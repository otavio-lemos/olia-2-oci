#!/usr/bin/env python3
"""
training/train_mlx_tune.py
OCI Specialist LLM - MLX-Tune Training

Todos os parametros vem do config/cycle-N.env. Zero hardcode.

Fixes aplicados:
- grad_accumulation_steps passado corretamente para TrainingArgs
- gradient clipping via monkey-patch no optimizer step
- clear_cache_threshold para evitar OOM em M3 Pro 18GB

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


def patch_mlx_tune_training(
    grad_clip_norm: float = 0.0, clear_cache_threshold: int = 0
):
    """
    Monkey-patch mlx_tune's _train_native to fix:
    1. grad_accumulation_steps not passed to TrainingArgs
    2. clear_cache_threshold for memory management
    3. gradient clipping (if grad_clip_norm > 0)
    """
    import mlx.core as mx
    import mlx.nn as nn
    from mlx.optimizers import AdamW
    from functools import partial
    from mlx.nn.utils import average_gradients
    from mlx.utils import tree_flatten, tree_map
    from mlx_lm.tuner.trainer import (
        TrainingArgs,
        CacheDataset,
        iterate_batches,
        evaluate,
        grad_checkpoint,
        default_loss,
    )

    def _patched_train_native(self):
        """Patched version of SFTTrainer._train_native with fixes."""
        print("\n[Using Native MLX Training (Patched)]")

        # Step 1: Apply LoRA to model if not already done
        if hasattr(self.model, "_apply_lora") and not self.model._lora_applied:
            print("\nApplying LoRA adapters...")
            self.model._apply_lora(num_layers=self.num_layers)

        # Step 2: Set adapter path on model for later saving
        if hasattr(self.model, "set_adapter_path"):
            self.model.set_adapter_path(str(self.adapter_path))

        # Step 3: Prepare training data
        data_dir = self._prepare_training_data()

        # Step 4: Create learning rate schedule
        lr_schedule = self._get_lr_schedule()

        # Step 5: Create optimizer
        optimizer = AdamW(
            learning_rate=lr_schedule,
            weight_decay=self.weight_decay,
        )

        # Step 6: Create training args - FIX: pass grad_accumulation_steps
        adapter_file = str(self.adapter_path / "adapters.safetensors")
        training_args = TrainingArgs(
            batch_size=self.batch_size,
            iters=self.iters,
            val_batches=25,
            steps_per_report=self.logging_steps,
            steps_per_eval=max(self.save_steps, 100),
            steps_per_save=self.save_steps,
            max_seq_length=self.max_seq_length,
            adapter_file=adapter_file,
            grad_checkpoint=self._should_use_grad_checkpoint(),
            grad_accumulation_steps=self.gradient_accumulation_steps,
        )

        print(f"\nTraining configuration:")
        print(f"  Iterations: {self.iters}")
        print(f"  Batch size: {self.batch_size}")
        print(f"  Grad accumulation: {self.gradient_accumulation_steps}")
        print(f"  Learning rate: {self.learning_rate}")
        print(f"  LR scheduler: {self.lr_scheduler_type}")
        print(f"  Grad checkpoint: {training_args.grad_checkpoint}")
        if grad_clip_norm > 0:
            print(f"  Grad clip norm: {grad_clip_norm}")
        if clear_cache_threshold > 0:
            print(f"  Clear cache threshold: {clear_cache_threshold / 1e9:.1f} GB")
        print(f"  Adapter file: {adapter_file}")
        print()

        # Step 7: Load datasets
        mask_prompt = getattr(self, "_train_on_responses_only", False)
        if mask_prompt:
            print("  Response-only training enabled (mask_prompt=True)")

        import mlx_lm
        from mlx_lm.tuner.datasets import (
            load_dataset as mlx_load_dataset,
            CacheDataset as MLXCacheDataset,
        )

        dataset_args = types.SimpleNamespace(
            data=data_dir,
            train=True,
            test=False,
            hf_dataset=None,
            mask_prompt=mask_prompt,
        )

        try:
            train_set, valid_set, _ = mlx_load_dataset(
                args=dataset_args,
                tokenizer=self.tokenizer,
            )
            train_set = MLXCacheDataset(train_set)
            valid_set = MLXCacheDataset(valid_set)
            print(
                f"Loaded {len(train_set)} training samples, {len(valid_set)} validation samples"
            )
        except Exception as e:
            print(f"Error loading dataset: {e}")
            print("Falling back to subprocess training...")
            return self._train_subprocess()

        # Step 8: Get the actual model
        actual_model = self.model.model if hasattr(self.model, "model") else self.model

        # Step 9: Custom training loop with gradient clipping
        print("Starting training loop...")

        if mx.metal.is_available():
            mx.set_wired_limit(mx.device_info()["max_recommended_working_set_size"])

        world = mx.distributed.init()
        world_size = world.size()
        rank = world.rank()

        if training_args.grad_checkpoint:
            grad_checkpoint(actual_model.layers[0])

        loss_value_and_grad = nn.value_and_grad(actual_model, default_loss)

        grad_accum_steps = training_args.grad_accumulation_steps
        state = [actual_model.state, optimizer.state, mx.random.state]

        @partial(mx.compile, inputs=state, outputs=state)
        def step(batch, prev_grad, do_update):
            (lvalue, toks), grad = loss_value_and_grad(actual_model, *batch)

            if prev_grad is not None:
                grad = tree_map(lambda x, y: x + y, grad, prev_grad)

            if do_update:
                grad = average_gradients(grad)
                if grad_accum_steps > 1:
                    grad = tree_map(lambda x: x / grad_accum_steps, grad)

                # FIX: Gradient clipping
                if grad_clip_norm > 0:
                    grad = tree_map(
                        lambda g: mx.clip(g, -grad_clip_norm, grad_clip_norm), grad
                    )

                optimizer.update(actual_model, grad)
                grad = None

            return lvalue, toks, grad

        actual_model.train()
        losses = 0
        n_tokens = 0
        steps = 0
        trained_tokens = 0
        train_time = 0
        grad_accum = None

        for it, batch in zip(
            range(1, training_args.iters + 1),
            iterate_batches(
                dataset=train_set,
                batch_size=training_args.batch_size,
                max_seq_length=training_args.max_seq_length,
                loop=True,
                comm_group=world,
            ),
        ):
            tic = time.perf_counter()

            # Validation
            if valid_set and (
                it == 1
                or it % training_args.steps_per_eval == 0
                or it == training_args.iters
            ):
                tic = time.perf_counter()
                val_loss = evaluate(
                    model=actual_model,
                    dataset=valid_set,
                    loss=default_loss,
                    batch_size=training_args.batch_size,
                    num_batches=training_args.val_batches,
                    max_seq_length=training_args.max_seq_length,
                    iterate_batches=iterate_batches,
                )
                actual_model.train()
                val_time = time.perf_counter() - tic
                if rank == 0:
                    print(
                        f"Iter {it}: Val loss {val_loss:.3f}, Val took {val_time:.3f}s",
                        flush=True,
                    )
                tic = time.perf_counter()

            lvalue, toks, grad_accum = step(
                batch,
                grad_accum,
                it % grad_accum_steps == 0,
            )

            losses += lvalue
            n_tokens += toks
            steps += 1
            mx.eval(state, losses, n_tokens, grad_accum)

            if clear_cache_threshold > 0:
                if mx.get_cache_memory() > clear_cache_threshold:
                    mx.clear_cache()

            train_time += time.perf_counter() - tic

            # Report training loss
            if it % training_args.steps_per_report == 0 or it == training_args.iters:
                train_loss = mx.distributed.all_sum(losses, stream=mx.cpu).item()
                train_loss /= steps * world_size
                n_tokens = mx.distributed.all_sum(n_tokens, stream=mx.cpu).item()
                learning_rate = optimizer.learning_rate.item()
                it_sec = training_args.steps_per_report / train_time
                tokens_sec = float(n_tokens) / train_time
                trained_tokens += n_tokens
                peak_mem = mx.get_peak_memory() / 1e9
                if rank == 0:
                    print(
                        f"Iter {it}: Train loss {train_loss:.3f}, "
                        f"Learning Rate {learning_rate:.3e}, "
                        f"It/sec {it_sec:.3f}, "
                        f"Tokens/sec {tokens_sec:.3f}, "
                        f"Trained Tokens {trained_tokens}, "
                        f"Peak mem {peak_mem:.3f} GB",
                        flush=True,
                    )
                losses = 0
                n_tokens = 0
                steps = 0
                train_time = 0

            # Save adapter weights
            if it % training_args.steps_per_save == 0 and rank == 0:
                adapter_weights = dict(
                    tree_flatten(actual_model.trainable_parameters())
                )
                mx.save_safetensors(str(training_args.adapter_file), adapter_weights)
                checkpoint = (
                    Path(training_args.adapter_file).parent
                    / f"{it:07d}_adapters.safetensors"
                )
                mx.save_safetensors(str(checkpoint), adapter_weights)
                print(
                    f"Iter {it}: Saved adapter weights to "
                    f"{training_args.adapter_file} and {checkpoint}."
                )

        # Save final weights
        if rank == 0:
            adapter_weights = dict(tree_flatten(actual_model.trainable_parameters()))
            mx.save_safetensors(str(training_args.adapter_file), adapter_weights)
            print(f"Saved final weights to {training_args.adapter_file}.")

        # Save adapter_config.json
        self._save_adapter_config()

        print("\n" + "=" * 70)
        print("Training Complete!")
        print("=" * 70)
        print(f"  Adapters saved to: {self.adapter_path}")

        return {"status": "success", "adapter_path": str(self.adapter_path)}

    # Apply the patch
    from mlx_tune import SFTTrainer

    SFTTrainer._train_native = _patched_train_native
    print(
        f"[patch] Applied MLX-Tune training fixes (grad_accum={True}, grad_clip={grad_clip_norm}, cache={clear_cache_threshold})"
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
    grad_checkpoint = cfg.get("GRADIENT_CHECKPOINTING", "false").lower() == "true"
    grad_clip_norm = float(cfg.get("GRADIENT_CLIP_NORM", "1.0"))
    clear_cache_gb = float(cfg.get("CLEAR_CACHE_GB", "5"))
    clear_cache_threshold = int(clear_cache_gb * 1e9)

    # Clean output directory if --fresh
    if args.fresh and Path(output_dir).exists():
        logger.log(f"[fresh] Cleaning output directory: {output_dir}")
        shutil.rmtree(output_dir)
        logger.log(f"[fresh] Directory cleaned. Starting fresh.")

    logger.log("=" * 60)
    logger.log("OCI Specialist LLM - MLX-Tune Training (Patched)")
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
    logger.log(f"Grad Checkpoint: {grad_checkpoint}")
    logger.log(f"Grad Clip Norm: {grad_clip_norm}")
    logger.log(f"Clear Cache: {clear_cache_gb} GB")
    logger.log("=" * 60)
    logger.log("")

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    try:
        from mlx_tune import FastLanguageModel, SFTTrainer, SFTConfig
    except ImportError as e:
        logger.log(f"ERROR: Failed to import mlx_tune: {e}")
        logger.log("Run: pip install mlx-tune")
        sys.exit(1)

    # Apply patches BEFORE creating trainer
    patch_mlx_tune_training(
        grad_clip_norm=grad_clip_norm,
        clear_cache_threshold=clear_cache_threshold,
    )

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
        adapter_path = str(prev_adapter)
        if not Path(adapter_path).exists():
            adapter_path = str(Path(prev_adapter) / "adapters.safetensors")
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
    if prev_adapter and Path(prev_adapter).exists():
        logger.log(
            f"  Using existing LoRA from previous adapter (skipping get_peft_model)"
        )
    else:
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
            gradient_checkpointing=grad_checkpoint,
            max_seq_length=max_seq_length,
            packing=False,
            use_native_training=True,
        ),
    )

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
