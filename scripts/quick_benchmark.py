#!/usr/bin/env python3
"""Quick benchmark - 50 samples, max 512 tokens, fast evaluation."""

import json
import time
from pathlib import Path
from datetime import datetime
import random

import mlx.core as mx
from mlx_lm import load, generate
from mlx_lm.sample_utils import make_sampler


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Quick benchmark")
    parser.add_argument("--model", default="outputs/merged-model", help="Path to model")
    parser.add_argument("--eval-file", default="data/eval.jsonl", help="Eval JSONL")
    parser.add_argument(
        "--output", default="outputs/benchmarks/quick", help="Output dir"
    )
    parser.add_argument("--samples", type=int, default=50, help="Number of samples")
    parser.add_argument(
        "--max-tokens", type=int, default=512, help="Max tokens to generate"
    )
    args = parser.parse_args()

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("QUICK BENCHMARK")
    print("=" * 60)
    print(f"Model: {args.model}")
    print(f"Samples: {args.samples}")
    print(f"Max tokens: {args.max_tokens}")
    print("=" * 60)

    with open(args.eval_file, "r", encoding="utf-8") as f:
        all_data = [json.loads(line) for line in f]

    random.seed(42)
    eval_data = random.sample(all_data, min(args.samples, len(all_data)))
    print(f"Loaded {len(eval_data)} samples from {len(all_data)} total\n")

    print("Loading model...")
    model, tokenizer = load(path_or_hf_repo=args.model)
    sampler = make_sampler(temp=0.3, top_p=0.9, min_p=0.0, top_k=50)
    print("Model loaded.\n")

    results = []
    times = []

    for i, example in enumerate(eval_data):
        messages = example.get("messages", [])
        system_msg = ""
        for msg in messages:
            if msg.get("role") == "system":
                system_msg = msg.get("content", "")
                break

        user_msg = ""
        for msg in messages:
            if msg.get("role") == "user":
                user_msg = msg.get("content", "")
                break

        category = example.get("metadata", {}).get("category", "unknown")
        difficulty = example.get("metadata", {}).get("difficulty", "unknown")
        reference = ""
        for msg in messages:
            if msg.get("role") == "assistant":
                reference = msg.get("content", "")
                break

        start = time.time()
        print(
            f"[{i + 1}/{len(eval_data)}] {category} ({difficulty})...",
            end=" ",
            flush=True,
        )

        prompt_tokens = tokenizer.apply_chat_template(
            [
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg},
            ],
            add_generation_prompt=True,
        )

        try:
            response = generate(
                model,
                tokenizer,
                prompt=prompt_tokens,
                max_tokens=args.max_tokens,
                sampler=sampler,
                verbose=False,
            )
        except Exception as e:
            print(f"ERROR: {e}")
            response = f"Error: {e}"

        elapsed = time.time() - start
        times.append(elapsed)
        avg_time = sum(times) / len(times)
        remaining = len(eval_data) - (i + 1)
        eta = int(avg_time * remaining / 60)
        print(f"{elapsed:.1f}s | ETA: {eta}min")

        results.append(
            {
                "question": user_msg,
                "response": response,
                "reference": reference[:500],
                "category": category,
                "difficulty": difficulty,
                "tokens_generated": len(tokenizer.encode(response)),
                "time_seconds": elapsed,
            }
        )

        if (i + 1) % 10 == 0:
            with open(output_dir / "quick_results.json", "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, ensure_ascii=False)

    with open(output_dir / "quick_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    avg_tokens = sum(r["tokens_generated"] for r in results) / len(results)
    avg_time = sum(times) / len(times)
    total_time = sum(times)

    report = f"""# Quick Benchmark Results

**Date:** {datetime.now().strftime("%Y-%m-%d %H:%M")}
**Model:** {args.model}
**Samples:** {len(results)}/{args.samples}
**Max tokens:** 512
**Temperature:** 0.3

## Stats

| Metric | Value |
|--------|-------|
| Total time | {total_time / 60:.1f} min |
| Avg time/example | {avg_time:.1f}s |
| Avg tokens generated | {avg_tokens:.0f} |

## Categories

"""
    categories = {}
    for r in results:
        cat = r["category"]
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(r)

    for cat in sorted(categories.keys(), key=lambda x: -len(categories[x])):
        report += f"- **{cat}**: {len(categories[cat])} examples\n"

    with open(output_dir / "quick_report.md", "w", encoding="utf-8") as f:
        f.write(report)

    print(f"\n{'=' * 60}")
    print(f"DONE in {total_time / 60:.1f} min")
    print(f"Results: {output_dir}/quick_results.json")
    print(f"Report: {output_dir}/quick_report.md")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
