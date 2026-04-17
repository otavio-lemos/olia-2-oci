#!/usr/bin/env python3
"""
training/train_mlx_tune.py
OCI Specialist LLM - MLX-Tune Training (SFTTrainer API)

Uses mlx-tune library with SFTTrainer API (Unsloth-compatible).
Supports: warmup, weight_decay, grad_clip, lr_scheduler.

Usage:
    bash training/run_cycles.sh --all                 # treina todos os ciclos
    bash training/run_cycles.sh --all --fresh       # limpa e treina todos os ciclos
"""

import argparse
import json
import os
import shutil
import signal
import sys
import time
import csv
from datetime import datetime, timezone
from pathlib import Path

from datasets import load_dataset, Dataset
from mlx_tune import FastLanguageModel, SFTTrainer, SFTConfig


def load_cycle_config(cycle_name):
    env_file = (
        Path(__file__).parent.parent
        / "outputs"
        / cycle_name
        / "config"
        / f"{cycle_name}.env"
    )
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


def load_and_prepare_dataset(path, tokenizer):
    """Load jsonl and apply chat template via high-performance HF map."""
    dataset = load_dataset("json", data_files=path, split="train")

    def format_chat(examples):
        texts = [
            tokenizer.apply_chat_template(msgs, tokenize=False)
            for msgs in examples["messages"]
        ]
        return {"text": texts}

    # Use HF Dataset mapping to parallelize and release memory automatically
    columns_to_remove = dataset.column_names
    dataset = dataset.map(
        format_chat,
        batched=True,
        num_proc=min(4, os.cpu_count() or 1),
        remove_columns=columns_to_remove,
        desc=f"Formatting {Path(path).name}",
    )
    return dataset


class MetricsLogger:
    def __init__(self, cycle_name):
        self.cycle_name = cycle_name
        self.logs_dir = Path("outputs") / cycle_name / "logs"
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

    def save_metrics(self):
        if self.metrics:
            fieldnames = ["step", "train_loss", "val_loss", "elapsed", "timestamp"]
            with open(self.metrics_file, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
                writer.writeheader()
                writer.writerows(self.metrics)


class TrainingCallback:
    def __init__(self, logger, total_steps, save_steps):
        self.logger = logger
        self.total_steps = total_steps
        self.save_steps = save_steps
        self.train_start = None

    def on_train_begin(self, args, control, logs=None):
        self.train_start = time.time()
        self.logger.log(f"Training started at step 1/{self.total_steps}")

    def on_step_end(self, args, control, logs=None):
        if logs:
            step = logs.get("step", 0)
            train_loss = logs.get("loss", logs.get("train_loss", 0))
            val_loss = logs.get("eval_loss")
            self.logger.log(
                f"Step {step}: loss={train_loss:.4f}"
                + (f", val_loss={val_loss:.4f}" if val_loss is not None else "")
            )
            self.logger.record_metric(
                step=step,
                train_loss=train_loss,
                val_loss=val_loss,
                elapsed=time.time() - self.train_start if self.train_start else None,
            )
            self.logger.save_metrics()


def main():
    parser = argparse.ArgumentParser(description="MLX-Tune Training")
    parser.add_argument(
        "--fresh", action="store_true", help="Clear output directory and start fresh"
    )
    args = parser.parse_args()

    cycle = os.environ.get("CYCLE", "cycle-1")
    cfg = load_cycle_config(cycle)
    logger = MetricsLogger(cycle)

    model_name = cfg["MODEL"]
    train_data = cfg["TRAIN_DATA"]
    valid_data = cfg.get("VALID_DATA", "data/valid.jsonl")
    iters = int(cfg["ITERS"])
    batch_size = int(cfg["BATCH_SIZE"])
    lr = float(cfg["LEARNING_RATE"])
    rank = int(cfg["LORA_RANK"])
    alpha = int(cfg["LORA_ALPHA"])
    dropout = float(cfg["LORA_DROPOUT"])
    target_modules = cfg.get(
        "TARGET_MODULES", "q_proj,k_proj,v_proj,o_proj,gate_proj,up_proj,down_proj"
    ).split(",")
    grad_accum = int(cfg["GRADIENT_ACCUMULATION"])
    num_layers = int(cfg.get("NUM_LAYERS", "32"))
    weight_decay = float(cfg.get("WEIGHT_DECAY", "0.01"))
    warmup_steps = int(cfg.get("WARMUP_STEPS", "0"))
    lr_scheduler = cfg.get("LR_SCHEDULER", "cosine")
    grad_clip = float(cfg.get("GRADIENT_CLIP_NORM", "1.0"))
    max_seq_length = int(cfg.get("MAX_SEQ_LENGTH", "2048"))
    seed = int(cfg.get("SEED", "42"))
    grad_checkpoint = cfg.get("GRADIENT_CHECKPOINTING", "false").lower() == "true"
    bf16 = cfg.get("BF16", "false").lower() == "true"
    output_dir = cfg["OUTPUT_DIR"]
    prev_adapter = cfg.get("PREV_ADAPTER", "")
    val_batches = int(cfg.get("VAL_BATCHES", "5"))
    logging_steps = int(cfg.get("LOGGING_STEPS", "10"))
    save_steps = int(cfg.get("SAVE_STEPS", "250"))
    eval_steps = int(cfg.get("EVAL_STEPS", "250"))

    output_path = Path(output_dir)
    if args.fresh and output_path.exists():
        logger.log(f"[fresh] Cleaning output directory: {output_path}")
        shutil.rmtree(output_path)
        logger.log(f"[fresh] Directory cleaned. Starting fresh.")
    output_path.mkdir(parents=True, exist_ok=True)

    adapter_path = output_path / "adapters"

    logger.log("=" * 60)
    logger.log("OCI Specialist LLM - MLX-Tune v2 (SFTTrainer API)")
    logger.log("=" * 60)
    logger.log(f"Cycle: {cycle}")
    logger.log(f"Model: {model_name}")
    logger.log(f"Train: {train_data}")
    logger.log(f"Output: {output_path}")
    logger.log(f"Resume: {prev_adapter or '(none, training from scratch)'}")
    logger.log(f"Batch Size: {batch_size}")
    logger.log(f"Grad Accum: {grad_accum}")
    logger.log(f"Learning Rate: {lr}")
    logger.log(f"Weight Decay: {weight_decay}")
    logger.log(f"Warmup Steps: {warmup_steps}")
    logger.log(f"LR Scheduler: {lr_scheduler}")
    logger.log(f"Grad Clip: {grad_clip}")
    logger.log(f"LoRA Rank: {rank}")
    logger.log(f"LoRA Alpha: {alpha}")
    logger.log(f"LoRA Layers: {num_layers}")
    logger.log(f"Iters: {iters}")
    logger.log(f"Max Seq Length: {max_seq_length}")
    logger.log(f"Seed: {seed}")
    logger.log(f"Grad Checkpoint: {grad_checkpoint}")
    logger.log(f"BF16: {bf16}")
    logger.log(f"Adapter Path: {adapter_path}")
    if prev_adapter and Path(prev_adapter).exists():
        logger.log(f"Resuming from: {prev_adapter}")
    logger.log("=" * 60)
    logger.log("")

    logger.log("Loading model...")
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name,
        max_seq_length=max_seq_length,
        load_in_4bit=True,
        trust_remote_code=True,
    )
    logger.log("Model loaded")

    # Load previous adapter weights if resuming
    if prev_adapter and Path(prev_adapter).exists():
        adapter_file = Path(prev_adapter) / "adapters.safetensors"
        if adapter_file.exists():
            logger.log(f"Loading adapter from: {prev_adapter}")
            model.load_adapter(str(prev_adapter))
            model.configure_lora(
                r=rank,
                lora_alpha=alpha,
                target_modules=target_modules,
                lora_dropout=dropout,
            )
            model._lora_applied = True  # Skip _apply_lora in SFTTrainer
            logger.log("Adapter loaded and LoRA configured (skipping _apply_lora)")
    else:
        model = FastLanguageModel.get_peft_model(
            model,
            r=rank,
            lora_alpha=alpha,
            target_modules=target_modules,
            lora_dropout=dropout,
            bias="none",
            use_gradient_checkpointing=grad_checkpoint,
        )

    logger.log("Loading and formatting datasets...")
    train_hf = load_and_prepare_dataset(train_data, tokenizer)
    valid_hf = load_and_prepare_dataset(valid_data, tokenizer)

    import gc
    import mlx.core as mx

    gc.collect()
    mx.clear_cache()

    logger.log(f"  Train: {len(train_hf)} examples")
    logger.log(f"  Valid: {len(valid_hf)} examples")

    sft_config = SFTConfig(
        output_dir=str(output_path),
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=val_batches,
        learning_rate=lr,
        warmup_steps=warmup_steps,
        weight_decay=weight_decay,
        max_grad_norm=grad_clip,
        max_steps=iters,
        gradient_accumulation_steps=grad_accum,
        lr_scheduler_type=lr_scheduler,
        eval_steps=eval_steps,
        save_steps=save_steps,
        logging_steps=logging_steps,
        logging_first_step=True,
        save_total_limit=3,
        report_to="none",
        seed=seed,
        data_seed=seed,
        num_layers=num_layers,
        grad_checkpoint=grad_checkpoint,
        bf16=bf16,
    )

    logger.log("Creating trainer...")
    callback = TrainingCallback(logger, iters, save_steps)
    trainer = SFTTrainer(
        model=model,
        train_dataset=train_hf,
        eval_dataset=valid_hf,
        tokenizer=tokenizer,
        args=sft_config,
        adapter_path="adapters",
        callbacks=[callback],
    )

    logger.log("")
    logger.log(f"Starting training for {iters} steps...")
    logger.log("")

    def save_on_interrupt(signum, frame):
        logger.log("\n[INTERRUPTED] Saving logs before exit...")
        logger.save()
        sys.exit(1)

    signal.signal(signal.SIGINT, save_on_interrupt)

    logger.log("Starting training...")
    start_time = time.time()

    # Train and capture metrics
    train_result = trainer.train()
    elapsed = time.time() - start_time

    # Extract training metrics
    if hasattr(train_result, "metrics"):
        metrics_dict = train_result.metrics
        train_loss = metrics_dict.get("train_loss", "N/A")
        logger.record_metric(step=iters, train_loss=train_loss, elapsed=elapsed)

    logger.save_metrics()

    logger.log("")
    logger.log(f"  Training completed in {elapsed:.1f}s ({elapsed / 60:.1f} min)")

    logger.save()
    logger.log("[METRICS] Logs saved!")

    adapter_file = Path(adapter_path) / "adapters.safetensors"
    if not adapter_file.exists():
        logger.log("[6/6] Saving adapter...")
        model.save_pretrained(str(adapter_path))
    else:
        logger.log("[6/6] Adapter already saved by trainer")

    logger.log(f"  Adapters saved to: {adapter_path}")
    logger.log("")
    logger.log("=" * 60)
    logger.log("Training complete!")
    logger.log(f"Adapters: {adapter_path}")
    logger.log(f"Logs: outputs/{cycle}/logs/")
    logger.log("=" * 60)

    logger.save()

    logger.log("")
    logger.log("Done!")


if __name__ == "__main__":
    main()
