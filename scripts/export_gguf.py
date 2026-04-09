#!/usr/bin/env python3
"""
scripts/export_gguf.py

Export MLX-trained LoRA adapter to GGUF format for Ollama/llama.cpp.

Usage:
    python scripts/export_gguf.py --cycle cycle-1 --quant q4,q5,q8
    python scripts/export_gguf.py --cycle cycle-1 --quant q4 --ollama
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

LLAMA_CPP_PATHS = [
    "/opt/homebrew/bin",
    "/usr/local/bin",
    str(Path.home() / "llama.cpp/build/bin"),
    str(Path(__file__).parent.parent / "llama.cpp" / "build" / "bin"),
]


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
    ]
    run_cmd(cmd)


def convert_to_gguf(merged_dir: str, output_file: str):
    print("\n=== Step 2: Converting to GGUF FP16 ===")
    convert_script = shutil.which("convert_hf_to_gguf.py")
    if not convert_script:
        convert_candidates = [
            Path("/opt/homebrew/bin/convert_hf_to_gguf.py"),
            Path("/usr/local/bin/convert_hf_to_gguf.py"),
            Path.home() / "llama.cpp/convert_hf_to_gguf.py",
            Path(__file__).parent.parent / "llama.cpp" / "convert_hf_to_gguf.py",
        ]
        for c in convert_candidates:
            if c.exists():
                convert_script = str(c)
                break
        if not convert_script:
            raise FileNotFoundError("convert_hf_to_gguf.py not found")

    cmd = [sys.executable, convert_script, merged_dir, "--outfile", output_file]
    run_cmd(cmd)


def quantize_model(input_file: str, output_file: str, quant_type: str):
    print(f"\n=== Step 3: Quantizing to {quant_type} ===")
    quantize_bin = find_llama_cpp_bin("llama-quantize")

    cmd = [quantize_bin, input_file, output_file, quant_type]
    run_cmd(cmd)


def create_ollama_modelfile(gguf_path: str, model_name: str, base_model: str) -> str:
    print("\n=== Step 4: Creating Ollama Modelfile ===")
    modelfile_content = f"""FROM {gguf_path}
PARAMETER temperature 0.1
PARAMETER top_p 0.9
PARAMETER top_k 40
SYSTEM You are an OCI (Oracle Cloud Infrastructure) specialist AI assistant.
"""
    modelfile_path = Path(gguf_path).parent / f"Modelfile-{model_name}"
    with open(modelfile_path, "w") as f:
        f.write(modelfile_content)
    print(f"Modelfile saved to: {modelfile_path}")
    return str(modelfile_path)


def import_to_ollama(gguf_path: str, model_name: str, modelfile_path: str):
    print("\n=== Step 5: Importing to Ollama ===")
    cmd = ["ollama", "create", f"oci-{model_name}", "-f", modelfile_path]
    try:
        run_cmd(cmd)
        print(f"Model imported: oci-{model_name}")
    except subprocess.CalledProcessError as e:
        print(f"WARNING: Failed to import to Ollama: {e}")
        print("You can manually import with: oci-{model_name} -f {modelfile_path}")


def main():
    parser = argparse.ArgumentParser(description="Export MLX LoRA to GGUF for Ollama")
    parser.add_argument("--cycle", required=True, help="Cycle name (e.g., cycle-1)")
    parser.add_argument(
        "--quant", default="q4", help="Quantization types (comma-separated): q4,q5,q8"
    )
    parser.add_argument(
        "--ollama", action="store_true", help="Import to Ollama after export"
    )
    parser.add_argument(
        "--skip-fuse",
        action="store_true",
        help="Skip fusion (use existing merged model)",
    )
    parser.add_argument(
        "--skip-convert", action="store_true", help="Skip HF->GGUF conversion"
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

    quant_types = [q.strip() for q in args.quant.split(",")]

    if not args.skip_fuse:
        fuse_model(str(base_model), str(adapter_dir), str(merged_dir))
    else:
        print(f"\n[SKIP] Using existing merged model: {merged_dir}")

    fp16_gguf = gguf_dir / "model-f16.gguf"

    if not args.skip_convert:
        convert_to_gguf(str(merged_dir), str(fp16_gguf))
    else:
        print(f"\n[SKIP] Using existing GGUF: {fp16_gguf}")

    if not fp16_gguf.exists():
        raise FileNotFoundError(f"FP16 GGUF not found: {fp16_gguf}")

    created_models = []

    for q in quant_types:
        quant_map = {
            "q4": "Q4_K_M",
            "q5": "Q5_K_M",
            "q8": "Q8_0",
            "f16": "F16",
        }
        quant_type = quant_map.get(q.lower(), q.upper())

        output_gguf = gguf_dir / f"model-{q}.gguf"

        if quant_type == "F16":
            shutil.copy(fp16_gguf, output_gguf)
            print(f"Copied FP16 to: {output_gguf}")
        else:
            quantize_model(str(fp16_gguf), str(output_gguf), quant_type)

        created_models.append(output_gguf)

        if args.ollama:
            modelfile = create_ollama_modelfile(
                str(output_gguf), f"{args.cycle}-{q}", base_model
            )
            import_to_ollama(str(output_gguf), f"{args.cycle}-{q}", modelfile)

    print("\n" + "=" * 50)
    print("EXPORT COMPLETE")
    print("=" * 50)
    print(f"Output directory: {gguf_dir}")
    print("Generated files:")
    for m in created_models:
        size_mb = m.stat().st_size / (1024 * 1024)
        print(f"  - {m.name} ({size_mb:.1f} MB)")

    if args.ollama:
        print("\nOllama models created:")
        for q in quant_types:
            print(f"  - oci-{args.cycle}-{q}")


if __name__ == "__main__":
    main()
