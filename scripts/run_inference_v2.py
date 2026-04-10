#!/usr/bin/env python3
"""
scripts/run_inference_v2.py

Inference estruturado com prompts em YAML e output JSON.

Usage:
    # Modo 1: Base model (sem LoRA)
    python scripts/run_inference_v2.py --config config/inference_prompts.yaml --model mlx-community/Meta-Llama-3.1-8B-Instruct-4bit

    # Modo 2: Base + LoRA adapter (fine-tuned)
    python scripts/run_inference_v2.py --config config/inference_prompts.yaml --adapter outputs/cycle-1/adapters
"""

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path

import yaml

from mlx_lm import load, generate
from mlx_lm.sample_utils import make_sampler


class InferenceRunner:
    def __init__(
        self,
        config_path: str,
        model_path: str = "",
        adapter_path: str = "",
        base_only: bool = False,
    ):
        self.config_path = config_path
        self.model_path = model_path
        self.adapter_path = adapter_path
        self.base_only = base_only
        self.model = None
        self.tokenizer = None
        self.sampler = None
        self.results = []

    def load_config(self) -> dict:
        with open(self.config_path) as f:
            return yaml.safe_load(f)

    def load_model(self, model_id: str):
        print(f"Loading model: {model_id}")
        if self.adapter_path:
            print(f"  With adapter: {self.adapter_path}")
            self.model, self.tokenizer = load(
                path_or_hf_repo=model_id,
                adapter_path=self.adapter_path,
            )
        else:
            self.model, self.tokenizer = load(path_or_hf_repo=model_id)

        config = self.load_config()
        sampling = config.get("sampling", {})
        self.sampler = make_sampler(
            temp=sampling.get("temperature", 0.1),
            top_p=sampling.get("top_p", 0.9),
            top_k=sampling.get("top_k", 40),
        )
        print("Model loaded successfully")

    def generate(self, prompt: str, system_prompt: str, max_tokens: int) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        prompt_tokens = self.tokenizer.apply_chat_template(
            messages, add_generation_prompt=True
        )

        response = generate(
            self.model,
            self.tokenizer,
            prompt=prompt_tokens,
            max_tokens=max_tokens,
            sampler=self.sampler,
            verbose=False,
        )
        return response

    def run(self):
        config = self.load_config()
        prompts = config.get("prompts", [])
        system_prompt = config.get("system_prompt", "")

        model_id = self.model_path or "mlx-community/Meta-Llama-3.1-8B-Instruct-4bit"
        self.load_model(model_id)

        print(f"\nRunning {len(prompts)} prompts...\n")

        for i, p in enumerate(prompts, 1):
            prompt_id = p.get("id", f"prompt-{i}")
            category = p.get("category", "unknown")
            prompt_text = p["prompt"]
            max_tokens = p.get("max_tokens", 512)

            print(f"[{i}/{len(prompts)}] {prompt_id} ({category})")
            start = time.time()
            response = self.generate(prompt_text, system_prompt, max_tokens)
            elapsed = time.time() - start

            result = {
                "prompt_id": prompt_id,
                "category": category,
                "difficulty": p.get("difficulty", "unknown"),
                "prompt": prompt_text,
                "response": response,
                "metrics": {
                    "elapsed_seconds": round(elapsed, 2),
                    "tokens_generated": len(response.split()),
                    "model": model_id,
                    "adapter": self.adapter_path if self.adapter_path else None,
                },
                "timestamp": datetime.now().isoformat(),
            }
            self.results.append(result)
            print(f"  ✓ {elapsed:.1f}s, ~{len(response.split())} tokens")

        self.save_results(config)

    def save_results(self, config: dict):
        output_config = config.get("output", {})
        save_path = output_config.get("save_to", "outputs/inference_results.json")
        output_dir = Path(save_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)

        with open(save_path, "w") as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

        print(f"\nResults saved to: {save_path}")

        summary = {
            "total_prompts": len(self.results),
            "total_time": sum(r["metrics"]["elapsed_seconds"] for r in self.results),
            "avg_time": sum(r["metrics"]["elapsed_seconds"] for r in self.results)
            / len(self.results),
            "model": self.results[0]["metrics"]["model"] if self.results else None,
            "adapter": self.results[0]["metrics"]["adapter"] if self.results else None,
        }
        print(
            f"\nSummary: {summary['total_prompts']} prompts, {summary['total_time']:.1f}s total, {summary['avg_time']:.1f}s avg"
        )

        if output_config.get("include_metrics", True):
            metrics_path = (
                str(Path(save_path).with_suffix("")).replace("results", "metrics")
                + ".json"
            )
            with open(metrics_path, "w") as f:
                json.dump(summary, f, indent=2)
            print(f"Metrics saved to: {metrics_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Structured inference runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Modo 1: Base model (sem LoRA)
  python scripts/run_inference_v2.py --config config/inference_prompts.yaml --model mlx-community/Meta-Llama-3.1-8B-Instruct-4bit

  # Modo 2: Base + LoRA adapter (fine-tuned)
  python scripts/run_inference_v2.py --config config/inference_prompts.yaml --adapter outputs/cycle-1/adapters
        """,
    )
    parser.add_argument(
        "--config", required=True, help="Prompts config file (required)"
    )
    parser.add_argument(
        "--model",
        default="",
        help="Base model ou merged model path. Use APENAS um: --model ou --adapter.",
    )
    parser.add_argument(
        "--adapter",
        default="",
        help="LoRA adapter path. Use APENAS um: --model ou --adapter.",
    )
    args = parser.parse_args()

    if args.model and args.adapter:
        parser.error("Use apenas --model OU --adapter, não ambos.")

    if not args.model and not args.adapter:
        parser.error("Especifique --model (base/merged) OU --adapter (LoRA).")

    runner = InferenceRunner(
        config_path=args.config,
        model_path=args.model,
        adapter_path=args.adapter,
    )
    runner.run()


if __name__ == "__main__":
    main()
