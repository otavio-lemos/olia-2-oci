#!/usr/bin/env python3
"""
scripts/merge_export.py

Simplified merge + export pipeline for MLX LoRA adapters.

Usage:
    python scripts/merge_export.py --cycle cycle-1
    python scripts/merge_export.py --cycle cycle-1 --quant q4,q5,q8
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import torch
from safetensors import safe_open
from safetensors.torch import save_file

LLAMA_CPP_PATHS = [
    "/opt/homebrew/bin",
    "/usr/local/bin",
    str(Path.home() / "llama.cpp/build/bin"),
    str(Path(__file__).parent.parent / "llama.cpp" / "build" / "bin"),
]

QUANT_MAP = {
    "q4": "Q4_K_M",
    "q5": "Q5_K_M",
    "q8": "Q8_0",
    "f16": "F16",
}


def find_llama_cpp_bin(name: str) -> str:
    for p in LLAMA_CPP_PATHS:
        candidate = Path(p) / name
        if candidate.exists():
            return str(candidate)
    raise FileNotFoundError(f"{name} not found in {LLAMA_CPP_PATHS}")


def load_cycle_config(cycle_name: str) -> dict:
    env_file = Path(__file__).parent.parent / "config" / f"{cycle_name}.env"
    if not env_file.exists():
        raise FileNotFoundError(f"Config not found: {env_file}")

    config = {}
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                config[key.strip()] = value.strip().strip('"')
    return config


def run_cmd(cmd: list, cwd: str = None, env: dict = None):
    print(f"[CMD] {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"ERROR: {result.stderr}")
        raise subprocess.CalledProcessError(result.returncode, cmd, result.stderr)
    print(result.stdout)
    return result


def clean_quantized_model(merged_dir: Path) -> Path:
    import json
    from safetensors import safe_open

    print("\n=== Step 1.5: Checking model for quantized tensors ===")

    # Check if model is sharded (multiple safetensors files)
    index_path = merged_dir / "model.safetensors.index.json"
    if not index_path.exists():
        raise FileNotFoundError(f"Model index not found: {index_path}")

    with open(index_path) as f:
        index = json.load(f)

    tensors_to_remove = set()
    for key in index["weight_map"].keys():
        if ".biases" in key or ".scales" in key:
            tensors_to_remove.add(key)

    if not tensors_to_remove:
        print(
            "No quantized tensors found (dequantize worked!). Using merged model directly."
        )
        return merged_dir

    print(f"Removing {len(tensors_to_remove)} quantized tensors (biases/scales)")

    cleaned_dir = merged_dir.parent / "merged_clean"
    cleaned_dir.mkdir(parents=True, exist_ok=True)

    # Handle sharded safetensors
    safetensors_files = list(merged_dir.glob("model-*.safetensors"))

    if safetensors_files:
        # Sharded model - need to process each file
        new_weight_map = {}

        for sf in safetensors_files:
            with safe_open(sf, framework="pt") as f:
                new_tensors = {}
                for key in f.keys():
                    if key not in tensors_to_remove:
                        tensor = f.get_tensor(key)
                        if tensor.dtype in [torch.uint8, torch.uint16, torch.uint32]:
                            tensor = tensor.to(torch.float32)
                        new_tensors[key] = tensor

                save_file(new_tensors, cleaned_dir / sf.name)
                for key in new_tensors:
                    new_weight_map[key] = sf.name

        new_index = {
            "metadata": index.get("metadata", {}),
            "weight_map": new_weight_map,
        }
        with open(cleaned_dir / "model.safetensors.index.json", "w") as f:
            json.dump(new_index, f, indent=2)
    else:
        # Single file model
        with safe_open(merged_dir / "model.safetensors", framework="pt") as f:
            all_keys = list(f.keys())

            new_tensors = {}
            for key in all_keys:
                if key not in tensors_to_remove:
                    tensor = f.get_tensor(key)
                    if tensor.dtype in [torch.uint8, torch.uint16, torch.uint32]:
                        tensor = tensor.to(torch.float32)
                    new_tensors[key] = tensor

            save_file(new_tensors, cleaned_dir / "model.safetensors")

            new_weight_map = {}
            for key in new_tensors:
                new_weight_map[key] = "model.safetensors"

        new_index = {
            "metadata": index.get("metadata", {}),
            "weight_map": new_weight_map,
        }
        with open(cleaned_dir / "model.safetensors.index.json", "w") as f:
            json.dump(new_index, f, indent=2)

    # Copy config files
    for f in [
        "config.json",
        "tokenizer.json",
        "tokenizer_config.json",
        "chat_template.jinja",
    ]:
        src = merged_dir / f
        dst = cleaned_dir / f
        if src.exists():
            shutil.copy(src, dst)

    print(f"Cleaned model saved to: {cleaned_dir}")
    return cleaned_dir


def fuse_model(base_model: str, adapter_path: str, output_dir: str):
    print("\n=== Step 1: Fusing LoRA adapter with base model ===")
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    cmd = [
        sys.executable,
        "-m",
        "mlx_lm",
        "fuse",
        "--model",
        base_model,
        "--adapter-path",
        adapter_path,
        "--save-path",
        output_dir,
        "--dequantize",
    ]
    run_cmd(cmd)


def check_fp16_exists(fp16_path: Path) -> bool:
    if not fp16_path.exists():
        return False

    # Verify it's a valid GGUF file (check header)
    if fp16_path.stat().st_size < 1000:
        print(f"[WARN] GGUF file too small, will regenerate: {fp16_path}")
        return False

    try:
        with open(fp16_path, "rb") as f:
            header = f.read(4)
            if header != b"GGUF":
                print(f"[WARN] Invalid GGUF header, will regenerate: {fp16_path}")
                return False
    except Exception as e:
        print(f"[WARN] Error checking GGUF, will regenerate: {e}")
        return False

    print(f"[CHECK] Found valid FP16 GGUF: {fp16_path}")
    return True


def convert_to_gguf(merged_dir: str, output_file: str, quant_type: str = None):
    print("\n=== Step 2: Converting to GGUF ===")

    llama_cpp_dir = Path(__file__).parent.parent / "llama.cpp"
    convert_script = llama_cpp_dir / "convert_hf_to_gguf.py"

    if not convert_script.exists():
        raise FileNotFoundError(f"convert_hf_to_gguf.py not found: {convert_script}")

    cmd = [
        sys.executable,
        str(convert_script),
        merged_dir,
        "--outfile",
        output_file,
    ]

    if quant_type:
        cmd.extend(["--outtype", quant_type])

    run_cmd(cmd)


def quantize_model(input_file: str, output_file: str, quant_type: str):
    print(f"\n=== Step 3: Quantizing to {quant_type} ===")
    quantize_bin = find_llama_cpp_bin("llama-quantize")

    cmd = [quantize_bin, input_file, output_file, quant_type]
    run_cmd(cmd)


def create_ollama_modelfile(gguf_path: str, model_name: str) -> str:
    print("\n=== Creating Ollama Modelfile ===")
    modelfile_content = f"""FROM {gguf_path}
PARAMETER temperature 0.1
PARAMETER top_p 0.9
PARAMETER top_k 40
SYSTEM Você é um especialista em OCI (Oracle Cloud Infrastructure).
"""
    modelfile_path = Path(gguf_path).parent / f"Modelfile-{model_name}"
    with open(modelfile_path, "w") as f:
        f.write(modelfile_content)
    print(f"Modelfile saved to: {modelfile_path}")
    return str(modelfile_path)


def main():
    parser = argparse.ArgumentParser(description="Merge LoRA + export to GGUF")
    parser.add_argument("--cycle", required=True, help="Cycle name (e.g., cycle-1)")
    parser.add_argument(
        "--quant", default="q4", help="Quantization types (comma-separated): q4,q5,q8"
    )
    parser.add_argument(
        "--name",
        default=None,
        help="Output name for GGUF file (e.g., oci-specialist-q4)",
    )
    args = parser.parse_args()

    project_root = Path(__file__).parent.parent

    config = load_cycle_config(args.cycle)
    base_model = config.get("MODEL", "mlx-community/Meta-Llama-3.1-8B-Instruct-4bit")
    adapter_dir = (
        project_root / config.get("OUTPUT_DIR", f"outputs/{args.cycle}") / "adapters"
    )

    if not adapter_dir.exists():
        raise FileNotFoundError(f"Adapter not found: {adapter_dir}")

    cycle_output = project_root / "outputs" / args.cycle
    merged_dir = cycle_output / "merged"
    gguf_dir = cycle_output / "gguf"
    gguf_dir.mkdir(parents=True, exist_ok=True)

    # Determine output name
    if args.name:
        model_name = args.name
    else:
        model_name = f"{args.cycle}"

    quant_types = [q.strip().lower() for q in args.quant.split(",")]

    # Step 1: Merge (auto-detect)
    if (merged_dir / "model.safetensors").exists():
        print(f"[CHECK] Found existing merged model: {merged_dir}")

        # Clean quantized tensors (biases/scales) for GGUF compatibility
        cleaned_dir = merged_dir.parent / "merged_clean"
        if cleaned_dir.exists():
            print(f"[SKIP] Using existing cleaned model: {cleaned_dir}")
            use_dir = cleaned_dir
        else:
            use_dir = clean_quantized_model(merged_dir)
    else:
        fuse_model(str(base_model), str(adapter_dir), str(merged_dir))
        use_dir = clean_quantized_model(merged_dir)

    # Step 2: Convert to GGUF FP16
    fp16_gguf = gguf_dir / "model-f16.gguf"
    if check_fp16_exists(fp16_gguf):
        print("[SKIP] FP16 GGUF already exists")
    else:
        convert_to_gguf(str(use_dir), str(fp16_gguf))

    if not fp16_gguf.exists():
        raise FileNotFoundError(f"FP16 GGUF not found: {fp16_gguf}")

    # Step 3: Quantize
    print(f"\n=== Quantizing: {quant_types} ===")
    created_models = []

    for q in quant_types:
        quant_type = QUANT_MAP.get(q, q.upper())

        # Always append quant suffix to avoid overwriting
        output_gguf = gguf_dir / f"{model_name}-{q}.gguf"

        if output_gguf.exists():
            print(f"[SKIP] {output_gguf.name} already exists")
            created_models.append(output_gguf)
            continue

        # Verify FP16 is valid GGUF before quantizing
        if fp16_gguf.stat().st_size < 1000:
            raise ValueError(f"Invalid FP16 GGUF file: {fp16_gguf}")

        quantize_model(str(fp16_gguf), str(output_gguf), quant_type)
        created_models.append(output_gguf)

    # Summary
    print("\n" + "=" * 50)
    print("EXPORT COMPLETE")
    print("=" * 50)
    print(f"Adapter: {adapter_dir}")
    print(f"Merged: {merged_dir}")
    print(f"GGUF: {gguf_dir}")
    print("\nGenerated files:")
    for m in created_models:
        size_mb = m.stat().st_size / (1024 * 1024)
        print(f"  - {m.name} ({size_mb:.1f} MB)")


if __name__ == "__main__":
    main()
