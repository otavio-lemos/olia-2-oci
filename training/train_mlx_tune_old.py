#!/usr/bin/env python3
"""
training/train_mlx_tune.py
OCI Specialist LLM - MLX-Tune Training

Usa a CLI oficial mlx_lm.lora para treinamento (metodo testado pela Apple).

Uso:
    CYCLE=cycle-1 python training/train_mlx_tune.py
    CYCLE=cycle-2 python training/train_mlx_tune.py
    CYCLE=cycle-3 python training/train_mlx_tune.py
"""

import argparse
import csv
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


def load_cycle_config(cycle_name):
    env_file = Path(__file__).parent.parent / "config" / f"{cycle_name}.env"
    if not env_file.exists():
        print(f"ERROR: Config not found: {env_file}")
        sys.exit(1)

    config = {}
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                config[key.strip()] = value.strip().strip('"')
    return config


def load_dataset_jsonl(path):
    dataset = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                data = json.loads(line)
                dataset.append({"messages": data["messages"]})
    return dataset


class MetricsLogger:
    def __init__(self, cycle_name):
        self.cycle_name = cycle_name
        self.logs_dir = Path("outputs/logs") / cycle_name
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.logs_dir / "training.log"
        self.metrics_file = self.logs_dir / "metrics.csv"
        self.metrics = []
        self.all_lines = []

    def log(self, line):
        print(line, flush=True)
        self.all_lines.append(line)

    def record_metric(self, step, train_loss, val_loss=None, elapsed=None):
        self.metrics.append(
            {
                "step": step,
                "train_loss": train_loss,
                "val_loss": val_loss or "",
                "elapsed": elapsed or "",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

    def save(self, training_output=None):
        if training_output:
            self.all_lines.append("\n--- Training Output ---\n")
            self.all_lines.append(training_output)
            self.all_lines.append("\n--- End Training Output ---\n")

        with open(self.log_file, "w") as f:
            f.write("\n".join(self.all_lines) + "\n")
        if self.metrics:
            fieldnames = ["step", "train_loss", "val_loss", "elapsed", "timestamp"]
            with open(self.metrics_file, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
                writer.writeheader()
                writer.writerows(self.metrics)
            self.log(
                f"\n[metrics] Exported {len(self.metrics)} rows to {self.metrics_file}"
            )


def main():
    parser = argparse.ArgumentParser(description="MLX-Tune Training")
    parser.add_argument(
        "--fresh", action="store_true", help="Clear output directory and start fresh"
    )
    args = parser.parse_args()

    cycle = os.environ.get("CYCLE", "cycle-1")
    cfg = load_cycle_config(cycle)
    logger = MetricsLogger(cycle)

    # All params from .env
    model_name = cfg["MODEL"]
    train_data = cfg["TRAIN_DATA"]
    valid_data = cfg.get("VALID_DATA", "data/valid.jsonl")
    output_dir = cfg["OUTPUT_DIR"]
    prev_adapter = cfg.get("PREV_ADAPTER", "")
    iters = int(cfg["ITERS"])
    max_seq_length = int(cfg["MAX_SEQ_LENGTH"])
    batch_size = int(cfg["BATCH_SIZE"])
    lr = float(cfg["LEARNING_RATE"])
    rank = int(cfg["LORA_RANK"])
    alpha = int(cfg["LORA_ALPHA"])
    dropout = float(cfg["LORA_DROPOUT"])
    grad_accum = int(cfg["GRADIENT_ACCUMULATION"])
    val_batches = int(cfg.get("VAL_BATCHES", "5"))
    num_layers = int(cfg.get("NUM_LAYERS", "20"))
    weight_decay = float(cfg.get("WEIGHT_DECAY", "0.01"))
    warmup_steps = int(cfg.get("WARMUP_STEPS", "0"))
    logging_steps = int(cfg.get("LOGGING_STEPS", "10"))
    save_steps = int(cfg.get("SAVE_STEPS", "50"))
    seed = int(cfg.get("SEED", "42"))
    grad_checkpoint = cfg.get("GRADIENT_CHECKPOINTING", "false").lower() == "true"

    # Clean output directory if --fresh
    if args.fresh and Path(output_dir).exists():
        logger.log(f"[fresh] Cleaning output directory: {output_dir}")
        shutil.rmtree(output_dir)
        logger.log(f"[fresh] Directory cleaned. Starting fresh.")

    logger.log("=" * 60)
    logger.log("OCI Specialist LLM - MLX Training (mlx_lm.lora)")
    logger.log("=" * 60)
    logger.log(f"Cycle: {cycle}")
    logger.log(f"Model: {model_name}")
    logger.log(f"Train: {train_data}")
    logger.log(f"Output: {output_dir}")
    logger.log(f"Resume: {prev_adapter or '(none, training from scratch)'}")
    logger.log(f"Batch Size: {batch_size}")
    logger.log(f"Grad Accum: {grad_accum}")
    logger.log(f"Val Batches: {val_batches}")
    logger.log(f"Learning Rate: {lr}")
    logger.log(f"Weight Decay: {weight_decay}")
    logger.log(f"Warmup Steps: {warmup_steps}")
    logger.log(f"LoRA Rank: {rank}")
    logger.log(f"LoRA Alpha: {alpha}")
    logger.log(f"LoRA Dropout: {dropout}")
    logger.log(f"LoRA Layers: {num_layers}")
    logger.log(f"Iters: {iters}")
    logger.log(f"Max Seq Length: {max_seq_length}")
    logger.log(f"Logging Steps: {logging_steps}")
    logger.log(f"Save Steps: {save_steps}")
    logger.log(f"Seed: {seed}")
    logger.log(f"Grad Checkpoint: {grad_checkpoint}")
    logger.log("=" * 60)
    logger.log("")

    # Prepare data directory for mlx_lm format
    data_dir = Path(output_dir) / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    # Convert chat format to text format for mlx_lm
    try:
        from transformers import AutoTokenizer

        tokenizer = AutoTokenizer.from_pretrained(model_name)
    except Exception:
        logger.log("ERROR: Failed to load tokenizer")
        sys.exit(1)

    logger.log("Preparing dataset...")
    train_dataset = load_dataset_jsonl(train_data)
    with open(data_dir / "train.jsonl", "w") as f:
        for example in train_dataset:
            text = tokenizer.apply_chat_template(example["messages"], tokenize=False)
            f.write(json.dumps({"text": text}) + "\n")
    logger.log(f"  Train: {len(train_dataset)} examples")

    valid_dataset = load_dataset_jsonl(valid_data)
    with open(data_dir / "valid.jsonl", "w") as f:
        for example in valid_dataset:
            text = tokenizer.apply_chat_template(example["messages"], tokenize=False)
            f.write(json.dumps({"text": text}) + "\n")
    logger.log(f"  Valid: {len(valid_dataset)} examples")

    # Build mlx_lm.lora command
    cmd = [
        sys.executable,
        "-m",
        "mlx_lm",
        "lora",
        "--model",
        model_name,
        "--train",
        "--data",
        str(data_dir),
        "--iters",
        str(iters),
        "--learning-rate",
        str(lr),
        "--batch-size",
        str(batch_size),
        "--grad-accumulation-steps",
        str(grad_accum),
        "--num-layers",
        str(num_layers),
        "--adapter-path",
        str(Path(output_dir) / "adapters"),
        "--steps-per-report",
        str(logging_steps),
        "--save-every",
        str(save_steps),
        "--seed",
        str(seed),
    ]

    if grad_checkpoint:
        cmd.append("--grad-checkpoint")

    if prev_adapter and Path(prev_adapter).exists():
        adapter_file = Path(prev_adapter) / "adapters.safetensors"
        if adapter_file.exists():
            cmd.extend(["--resume-adapter-file", str(adapter_file)])
            logger.log(f"Resuming from: {adapter_file}")

    logger.log("")
    logger.log(f"Running: {' '.join(cmd)}")
    logger.log("")

    start_time = time.time()
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    output_lines = []
    all_metrics = []
    current_step = None
    for line in process.stdout:
        print(line, end="", flush=True)
        output_lines.append(line)

        if "Iter " in line and ": Train loss " in line:
            try:
                step_str = line.split("Iter ")[1].split(":")[0]
                current_step = int(step_str.strip())
                train_loss = float(line.split("Train loss ")[1].split(",")[0])
                all_metrics.append(
                    {"step": current_step, "train_loss": train_loss, "val_loss": None}
                )
            except (IndexError, ValueError):
                pass
        elif "Iter " in line and ": Val loss " in line:
            try:
                val_loss = float(line.split("Val loss ")[1].split(",")[0])
                if all_metrics and all_metrics[-1]["val_loss"] is None:
                    all_metrics[-1]["val_loss"] = val_loss
            except (IndexError, ValueError):
                pass

    process.wait()
    result = subprocess.CompletedProcess(
        args=cmd,
        returncode=process.returncode,
        stdout="".join(output_lines),
        stderr="",
    )
    elapsed = time.time() - start_time

    final_train_loss = all_metrics[-1]["train_loss"] if all_metrics else None
    final_val_loss = all_metrics[-1]["val_loss"] if all_metrics else None

    for m in all_metrics:
        is_last = m == all_metrics[-1]
        logger.record_metric(
            m["step"], m["train_loss"], m["val_loss"], elapsed if is_last else None
        )

    logger.log("")
    logger.log(f"  Training completed in {elapsed:.1f}s ({elapsed / 60:.1f} min)")

    # Save adapter config
    adapter_dir = Path(output_dir) / "adapters"
    if adapter_dir.exists():
        logger.log("[6/6] Adapters saved")
        logger.log(f"  Adapters saved to: {output_dir}")

    logger.log("")
    logger.log("=" * 60)
    logger.log("Training complete!")
    logger.log(f"Adapters: {output_dir}")
    logger.log(f"Logs: outputs/logs/{cycle}/")
    if final_train_loss is not None:
        logger.log("")
        logger.log("Final Metrics:")
        logger.log(f"  Train Loss: {final_train_loss:.3f}")
        logger.log(
            f"  Val Loss:   {final_val_loss:.3f}"
            if final_val_loss
            else "  Val Loss:   N/A"
        )
    logger.log("=" * 60)

    logger.save("".join(output_lines))

    if result.returncode != 0:
        sys.exit(result.returncode)


if __name__ == "__main__":
    main()
