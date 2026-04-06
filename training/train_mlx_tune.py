#!/usr/bin/env python3
"""
training/train_mlx_tune.py
OCI Specialist LLM - MLX-Tune Training

Todos os parametros vem do config/cycle-N.env. Zero hardcode.

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
import sys
import time
import types
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

    def record_metric(self, step, train_loss, val_loss=None):
        self.metrics.append(
            {
                "step": step,
                "train_loss": train_loss,
                "val_loss": val_loss or "",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

    def save(self):
        with open(self.log_file, "w") as f:
            f.write("\n".join(self.all_lines) + "\n")
        if self.metrics:
            fieldnames = ["step", "train_loss", "val_loss", "timestamp"]
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
    lr_scheduler = cfg.get("LR_SCHEDULER", "cosine")
    weight_decay = float(cfg.get("WEIGHT_DECAY", "0.01"))
    warmup_steps = int(cfg.get("WARMUP_STEPS", "0"))
    logging_steps = int(cfg.get("LOGGING_STEPS", "10"))
    save_steps = int(cfg.get("SAVE_STEPS", "50"))
    seed = int(cfg.get("SEED", "42"))

    # Clean output directory if --fresh
    if args.fresh and Path(output_dir).exists():
        logger.log(f"[fresh] Cleaning output directory: {output_dir}")
        shutil.rmtree(output_dir)
        logger.log(f"[fresh] Directory cleaned. Starting fresh.")

    logger.log("=" * 60)
    logger.log("OCI Specialist LLM - MLX-Tune Training")
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
    logger.log(f"LR Scheduler: {lr_scheduler}")
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
    logger.log("=" * 60)
    logger.log("")

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    try:
        from mlx_tune import FastLanguageModel, SFTTrainer, SFTConfig
    except ImportError as e:
        logger.log(f"ERROR: Failed to import mlx_tune: {e}")
        logger.log("Run: pip install mlx-tune")
        sys.exit(1)

    # 1. Load model
    logger.log("[1/6] Loading model...")
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=model_name,
        max_seq_length=max_seq_length,
        load_in_4bit=True,
    )
    logger.log(f"  Model loaded: {model_name}")

    # 2. Resume previous adapter
    if prev_adapter and Path(prev_adapter).exists():
        logger.log(f"[2/6] Resuming from: {prev_adapter}")
        adapter_path = (
            str(Path(prev_adapter) / "adapters.safetensors")
            if Path(prev_adapter).is_dir()
            else str(prev_adapter)
        )
        if Path(adapter_path).exists():
            model.load_adapter(adapter_path)
            logger.log(f"  Previous adapter loaded: {adapter_path}")
        else:
            logger.log(
                f"  WARNING: Adapter not found: {adapter_path}, training from scratch"
            )
    else:
        logger.log("[2/6] No previous adapter - training from scratch")

    # 3. LoRA
    logger.log("[3/6] Configuring LoRA...")
    model = FastLanguageModel.get_peft_model(
        model,
        r=rank,
        target_modules=[
            "q_proj",
            "k_proj",
            "v_proj",
            "o_proj",
            "gate_proj",
            "up_proj",
            "down_proj",
        ],
        lora_alpha=alpha,
        lora_dropout=dropout,
        bias="none",
        use_gradient_checkpointing=True,
    )
    logger.log(
        f"  LoRA: r={rank}, alpha={alpha}, dropout={dropout}, layers={num_layers}"
    )

    # 4. Dataset
    logger.log("[4/6] Loading dataset...")
    train_dataset = load_dataset_jsonl(train_data)
    logger.log(f"  Loaded {len(train_dataset)} examples")

    # 5. Trainer
    logger.log("[5/6] Starting training...")
    logger.log("")

    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=train_dataset,
        args=SFTConfig(
            output_dir=output_dir,
            per_device_train_batch_size=batch_size,
            gradient_accumulation_steps=grad_accum,
            learning_rate=lr,
            max_steps=iters,
            logging_steps=logging_steps,
            save_steps=save_steps,
            lr_scheduler_type=lr_scheduler,
            weight_decay=weight_decay,
            warmup_steps=warmup_steps,
        ),
    )

    # Patch val_batches from config (mlx-tune hardcodes 25)
    original_train_native = trainer._train_native

    def patched_train_native():
        from mlx_lm.tuner.trainer import TrainingArgs, train as mlx_train
        from mlx_lm.tuner.datasets import CacheDataset, load_dataset as mlx_load_dataset
        import mlx.core as mx
        from mlx import nn

        data_dir = trainer._prepare_training_data()
        lr_schedule = trainer._get_lr_schedule()

        # Create optimizer manually (mlx_tune changed API)
        learning_rate = trainer.learning_rate
        weight_decay = trainer.weight_decay

        actual_model = (
            trainer.model.model if hasattr(trainer.model, "model") else trainer.model
        )

        # Get trainable parameters from LoRA layers
        trainable_params = list(actual_model.parameters())

        print(f"  Trainable parameters: {len(trainable_params)}")

        # Create optimizer for LoRA parameters
        optimizer = nn.optim.Adam(learning_rate=learning_rate)
        adapter_file = str(trainer.adapter_path / "adapters.safetensors")
        training_args = TrainingArgs(
            batch_size=trainer.batch_size,
            iters=trainer.iters,
            val_batches=val_batches,
            steps_per_report=trainer.logging_steps,
            steps_per_eval=max(trainer.save_steps, 100),
            steps_per_save=trainer.save_steps,
            max_seq_length=trainer.max_seq_length,
            adapter_file=adapter_file,
            grad_checkpoint=trainer._should_use_grad_checkpoint(),
        )
        dataset_args = types.SimpleNamespace(
            data=data_dir,
            train=True,
            test=False,
            hf_dataset=None,
            mask_prompt=getattr(trainer, "_train_on_responses_only", False),
        )
        train_set, valid_set, _ = mlx_load_dataset(
            args=dataset_args, tokenizer=trainer.tokenizer
        )
        train_set = CacheDataset(train_set)
        valid_set = CacheDataset(valid_set)
        logger.log(f"  Val batches: {val_batches} (from config)")

        mlx_train(
            model=actual_model,
            optimizer=optimizer,
            train_dataset=train_set,
            val_dataset=valid_set,
            args=training_args,
        )
        trainer._save_adapter_config()
        logger.log("\n" + "=" * 60)
        logger.log("Training Complete!")
        logger.log("=" * 60)
        logger.log(f"  Adapters saved to: {trainer.adapter_path}")
        return {"status": "success", "adapter_path": str(trainer.adapter_path)}

    trainer._train_native = patched_train_native

    start_time = time.time()
    trainer.train()
    elapsed = time.time() - start_time

    logger.log("")
    logger.log(f"  Training completed in {elapsed:.1f}s ({elapsed / 60:.1f} min)")

    # 6. Save
    logger.log("[6/6] Saving adapters...")
    model.save_pretrained(output_dir)
    logger.log(f"  Adapters saved to: {output_dir}")

    logger.log("")
    logger.log("=" * 60)
    logger.log("Training complete!")
    logger.log(f"Adapters: {output_dir}")
    logger.log(f"Logs: outputs/logs/{cycle}/")
    logger.log("=" * 60)

    logger.save()


if __name__ == "__main__":
    main()
