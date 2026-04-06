#!/usr/bin/env python3
"""Evaluate only the fine-tuned model against reference answers."""

import json
import time
from pathlib import Path
from datetime import datetime

import mlx.core as mx
from mlx_lm import load, generate
from mlx_lm.sample_utils import make_sampler

from eval_scoring import (
    load_eval_data,
    get_user_prompt,
    get_reference_answer,
    evaluate_response,
)


def format_eta(seconds_per_item: float, remaining: int) -> str:
    if remaining <= 0 or seconds_per_item <= 0:
        return "calculating..."
    total_seconds = int(seconds_per_item * remaining)
    from datetime import timedelta

    return str(timedelta(seconds=total_seconds))


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Evaluate fine-tuned model")
    parser.add_argument("ft_model_path", help="Path to FT model or adapter")
    parser.add_argument("eval_file", help="Path to eval.jsonl")
    parser.add_argument(
        "output_dir", nargs="?", default="outputs/benchmarks", help="Output directory"
    )
    parser.add_argument(
        "--fresh",
        action="store_true",
        help="Clear checkpoint and start fresh",
    )
    args = parser.parse_args()

    ft_model_dir = args.ft_model_path
    eval_file = Path(args.eval_file)
    output_dir = Path(args.output_dir)
    fresh = args.fresh

    ft_model_path = Path(ft_model_dir)
    if ft_model_path.is_dir() and (ft_model_path / "model.safetensors").exists():
        merged_model_path = str(ft_model_path)
        adapter_path = None
        print(f"Detected merged model: {merged_model_path}")
    elif ft_model_path.is_dir() and (ft_model_path / "adapters.safetensors").exists():
        adapter_path = str(ft_model_path)
        merged_model_path = None
    else:
        adapter_path = ft_model_dir
        merged_model_path = None

    eval_data = load_eval_data(eval_file)
    print(f"Loaded {len(eval_data)} eval examples")
    print(f"FT model: {merged_model_path or adapter_path}")

    checkpoint_path = output_dir / "eval-ft-checkpoint.json"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Clear checkpoint if --fresh
    if fresh and checkpoint_path.exists():
        checkpoint_path.unlink()
        print(f"Cleared checkpoint: {checkpoint_path}")

    # Load checkpoint
    if checkpoint_path.exists():
        with open(checkpoint_path, "r", encoding="utf-8") as f:
            ckpt = json.load(f)
        results = ckpt.get("results", [])
        completed = ckpt.get("completed", 0)
        print(f"Resuming from checkpoint: {completed}/{len(eval_data)}")
    else:
        results = []
        completed = 0

    # Load model
    print("\nLoading model...")
    if merged_model_path:
        model, tokenizer = load(path_or_hf_repo=merged_model_path)
    else:
        model, tokenizer = load(
            path_or_hf_repo="mlx-community/Meta-Llama-3.1-8B-Instruct-4bit",
            adapter_path=adapter_path,
        )
    sampler = make_sampler(temp=0.5, top_p=0.9, min_p=0.0, top_k=50)
    print("Model loaded. Starting evaluation...\n")

    eval_times = []

    for i in range(completed, len(eval_data)):
        example = eval_data[i]
        question = get_user_prompt(example)
        reference = get_reference_answer(example)
        category = example.get("metadata", {}).get("category", "unknown")
        difficulty = example.get("metadata", {}).get("difficulty", "unknown")
        system_msg = ""
        for msg in example.get("messages", []):
            if msg.get("role") == "system":
                system_msg = msg.get("content", "")
                break

        item_start = time.time()
        print(f"[{i + 1}/{len(eval_data)}] {category} ({difficulty})...")

        messages = []
        if system_msg:
            messages.append({"role": "system", "content": system_msg})
        messages.append({"role": "user", "content": question})

        prompt_tokens = tokenizer.apply_chat_template(
            messages, add_generation_prompt=True
        )

        try:
            response = generate(
                model,
                tokenizer,
                prompt=prompt_tokens,
                max_tokens=2048,
                sampler=sampler,
                verbose=False,
            )
        except Exception as e:
            print(f"  ERROR: {e}")
            response = f"Error: {e}"

        scores = evaluate_response(response, reference, category)

        results.append(
            {
                "question": question,
                "response": response,
                "scores": scores,
                "category": category,
                "difficulty": difficulty,
            }
        )

        item_time = time.time() - item_start
        eval_times.append(item_time)
        avg_time = sum(eval_times) / len(eval_times)
        remaining = len(eval_data) - (i + 1)
        eta = format_eta(avg_time, remaining)
        print(f"  Done in {item_time:.1f}s | Avg: {avg_time:.1f}s | ETA: {eta}")

        if (i + 1) % 50 == 0 or (i + 1) == len(eval_data):
            with open(checkpoint_path, "w", encoding="utf-8") as f:
                json.dump(
                    {"results": results, "completed": i + 1},
                    f,
                    indent=2,
                    ensure_ascii=False,
                )
            pct = (i + 1) / len(eval_data) * 100
            print(f"  Checkpoint saved at {i + 1}/{len(eval_data)} ({pct:.1f}%)")

    # Generate report
    n = len(results)
    avg_scores = {}
    for metric in [
        "technical_correctness",
        "depth",
        "structure",
        "hallucination",
        "clarity",
        "overall",
    ]:
        avg_scores[metric] = sum(r["scores"][metric] for r in results) / n

    categories = {}
    for r in results:
        cat = r.get("category", "unknown")
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(r["scores"]["overall"])

    report = f"""# OCI Specialist LLM - Fine-Tuned Model Evaluation

**Date:** {datetime.now().strftime("%Y-%m-%d %H:%M")}
**Model:** outputs/merged-model (cycle-3-v3, LoRA rank=8, alpha=16)
**Base:** mlx-community/Meta-Llama-3.1-8B-Instruct-4bit
**Examples:** {n}/{len(eval_data)} ({n / len(eval_data) * 100:.1f}%)
**Categories:** {len(categories)}

## Overall Scores

| Metric | Score |
|--------|-------|
| **Overall** | **{avg_scores["overall"]:.2f}/5** |
| Technical Correctness | {avg_scores["technical_correctness"]:.2f} |
| Depth | {avg_scores["depth"]:.2f} |
| Structure | {avg_scores["structure"]:.2f} |
| Hallucination (5=none) | {avg_scores["hallucination"]:.2f} |
| Clarity | {avg_scores["clarity"]:.2f} |

## By Category

| Category | Score | Count |
|----------|-------|-------|
"""
    for cat in sorted(categories.keys()):
        cat_avg = sum(categories[cat]) / len(categories[cat])
        report += f"| {cat} | {cat_avg:.2f} | {len(categories[cat])} |\n"

    report += f"""
## By Difficulty

"""
    difficulties = {}
    for r in results:
        diff = r.get("difficulty", "unknown")
        if diff not in difficulties:
            difficulties[diff] = []
        difficulties[diff].append(r["scores"]["overall"])

    report += "| Difficulty | Score | Count |\n|------------|-------|-------|\n"
    for diff in ["beginner", "intermediate", "advanced"]:
        if diff in difficulties:
            d_avg = sum(difficulties[diff]) / len(difficulties[diff])
            report += f"| {diff} | {d_avg:.2f} | {len(difficulties[diff])} |\n"

    # Score distribution
    ranges = [(1, 2), (2, 3), (3, 4), (4, 5)]
    report += f"""
## Score Distribution

| Score Range | Count |
|-------------|-------|
"""
    for low, high in ranges:
        count = sum(1 for r in results if low <= r["scores"]["overall"] < high)
        report += f"| {low:.0f}-{high:.0f} | {count} |\n"

    output_path = output_dir / f"eval-ft-{datetime.now().strftime('%Y%m%d-%H%M%S')}.md"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)

    # Save final results
    final_path = output_dir / "eval-ft-results-final.json"
    with open(final_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\nReport: {output_path}")
    print(f"Results: {final_path}")
    print(f"Overall: {avg_scores['overall']:.2f}/5")


if __name__ == "__main__":
    main()
