#!/usr/bin/env python3
"""Evaluate model responses against eval.jsonl benchmark with real scoring rubrics."""

import json
import sys
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any

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
    return str(timedelta(seconds=total_seconds))


class ModelEvaluator:
    def __init__(
        self, base_model_id: str, adapter_path: str = "", merged_model_path: str = ""
    ):
        self.base_model_id = base_model_id
        self.adapter_path = adapter_path
        self.merged_model_path = merged_model_path
        self.model = None
        self.tokenizer = None
        self._loaded = False

    def load_model(self):
        if self._loaded:
            return
        if self.merged_model_path:
            print(f"Loading merged model: {self.merged_model_path}")
            self.model, self.tokenizer = load(path_or_hf_repo=self.merged_model_path)
        else:
            print(f"Loading model: {self.base_model_id}")
            if self.adapter_path:
                print(f"  With adapter: {self.adapter_path}")
            self.model, self.tokenizer = load(
                path_or_hf_repo=self.base_model_id,
                adapter_path=self.adapter_path if self.adapter_path else None,
            )
        self.sampler = make_sampler(temp=0.5, top_p=0.9, min_p=0.0, top_k=50)
        self._loaded = True
        print("Model loaded successfully")

    def generate_response(
        self, prompt: str, system_prompt: str = "", max_tokens: int = 1024
    ) -> str:
        if not self._loaded:
            self.load_model()

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


def generate_comparison_report(
    base_results: List[Dict[str, Any]],
    ft_results: List[Dict[str, Any]],
    output_path: Path,
    total_eval: int = 994,
):
    if not base_results or not ft_results:
        return

    n = len(base_results)
    base_avg = {}
    ft_avg = {}
    metrics = [
        "technical_correctness",
        "depth",
        "structure",
        "hallucination",
        "clarity",
        "overall",
    ]

    for m in metrics:
        base_avg[m] = sum(r["scores"].get(m, 0) for r in base_results) / n
        ft_avg[m] = sum(r["scores"].get(m, 0) for r in ft_results) / n

    base_overall = base_avg["overall"]
    ft_overall = ft_avg["overall"]
    improvement = ft_overall - base_overall
    improvement_pct = (improvement / base_overall * 100) if base_overall > 0 else 0

    categories = {}
    for br, fr in zip(base_results, ft_results):
        cat = br.get("category", "unknown")
        if cat not in categories:
            categories[cat] = {"base": [], "ft": []}
        categories[cat]["base"].append(br["scores"]["overall"])
        categories[cat]["ft"].append(fr["scores"]["overall"])

    report = f"""# OCI Specialist LLM - Model Comparison Report

**Date:** {datetime.now().strftime("%Y-%m-%d %H:%M")}
**Progress:** {n}/{total_eval} examples ({n / total_eval * 100:.1f}%)
**Evaluation Set:** {n} examples across {len(categories)} categories

## Executive Summary

| Metric | Base Model | Fine-Tuned Model | Improvement |
|--------|-----------|-----------------|-------------|
| **Overall Score** | **{base_overall:.2f}/5** | **{ft_overall:.2f}/5** | **{improvement:+.2f} ({improvement_pct:+.1f}%)** |
| Technical Correctness | {base_avg["technical_correctness"]:.2f} | {ft_avg["technical_correctness"]:.2f} | {ft_avg["technical_correctness"] - base_avg["technical_correctness"]:+.2f} |
| Depth | {base_avg["depth"]:.2f} | {ft_avg["depth"]:.2f} | {ft_avg["depth"] - base_avg["depth"]:+.2f} |
| Structure | {base_avg["structure"]:.2f} | {ft_avg["structure"]:.2f} | {ft_avg["structure"] - base_avg["structure"]:+.2f} |
| Hallucination (lower=better) | {base_avg["hallucination"]:.2f} | {ft_avg["hallucination"]:.2f} | {ft_avg["hallucination"] - base_avg["hallucination"]:+.2f} |
| Clarity | {base_avg["clarity"]:.2f} | {ft_avg["clarity"]:.2f} | {ft_avg["clarity"] - base_avg["clarity"]:+.2f} |

## Training Metrics

| Cycle | Learning Rate | Iterations | Train Loss | Val Loss |
|-------|--------------|------------|------------|----------|
| cycle-1 | 3e-5 | 2485 | 0.062 | 0.073 |
| cycle-2 | 1e-5 | 2485 | 0.049 | 0.057 |
| cycle-3 | 5e-6 | 466 | 0.039 | 0.053 |

**Best Model:** cycle-3-v3 (lowest validation loss: 0.053, minimal overfitting gap: 0.014)

## Category-by-Category Comparison

| Category | Base | Fine-Tuned | Delta |
|----------|------|------------|-------|
"""

    for cat in sorted(categories.keys()):
        cat_base = sum(categories[cat]["base"]) / len(categories[cat]["base"])
        cat_ft = sum(categories[cat]["ft"]) / len(categories[cat]["ft"])
        delta = cat_ft - cat_base
        report += f"| {cat} | {cat_base:.2f} | {cat_ft:.2f} | {delta:+.2f} |\n"

    report += f"""
## Score Distribution

| Score Range | Base Count | Fine-Tuned Count |
|-------------|-----------|-----------------|
"""

    ranges = [(1, 2), (2, 3), (3, 4), (4, 5)]
    for low, high in ranges:
        base_count = sum(
            1 for r in base_results if low <= r["scores"]["overall"] < high
        )
        ft_count = sum(1 for r in ft_results if low <= r["scores"]["overall"] < high)
        report += f"| {low:.0f}-{high:.0f} | {base_count} | {ft_count} |\n"

    report += f"""
## Key Findings

1. **Overall Improvement:** {improvement:+.2f} points ({improvement_pct:+.1f}%)
2. **Best Category Improvement:** {max(categories.keys(), key=lambda c: sum(categories[c]["ft"]) / len(categories[c]["ft"]) - sum(categories[c]["base"]) / len(categories[c]["base"]))} (+{max(sum(categories[c]["ft"]) / len(categories[c]["ft"]) - sum(categories[c]["base"]) / len(categories[c]["base"]) for c in categories):.2f})
3. **Worst Category:** {min(categories.keys(), key=lambda c: sum(categories[c]["ft"]) / len(categories[c]["ft"]))} ({min(sum(categories[c]["ft"]) / len(categories[c]["ft"]) for c in categories):.2f})

## Methodology

- **Scoring Rubric:** 6 criteria (1-5 scale): Technical Correctness, Depth, Structure, Hallucination (inverse), Clarity, Overall
- **Evaluation Set:** {n} examples from eval.jsonl, stratified across {len(categories)} OCI categories
- **Base Model:** mlx-community/Meta-Llama-3.1-8B-Instruct-4bit
- **Fine-Tuned Model:** LoRA adapters from cycle-2 (merged), LR=1e-5, 2485 iterations, rank=16
- **Dataset:** 9,940 unique examples, 71 categories, 140 per category
"""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"Comparison report saved to {output_path}")
    print(f"Base model overall: {base_overall:.2f}/5")
    print(f"Fine-tuned model overall: {ft_overall:.2f}/5")
    print(f"Improvement: {improvement:+.2f} ({improvement_pct:+.1f}%)")


def generate_difficulty_report(
    base_results: List[Dict[str, Any]],
    ft_results: List[Dict[str, Any]],
    output_dir: Path,
) -> Path:
    difficulties = {}
    for br, fr in zip(base_results, ft_results):
        diff = br.get("difficulty", "unknown")
        if diff not in difficulties:
            difficulties[diff] = {"base": [], "ft": []}
        difficulties[diff]["base"].append(br["scores"]["overall"])
        difficulties[diff]["ft"].append(fr["scores"]["overall"])

    n = len(base_results)
    base_avg = sum(r["scores"]["overall"] for r in base_results) / n
    ft_avg = sum(r["scores"]["overall"] for r in ft_results) / n

    report = f"""# OCI Specialist LLM - Difficulty Analysis Report

**Date:** {datetime.now().strftime("%Y-%m-%d %H:%M")}
**Total Examples:** {n}

## Overall

| Metric | Base | Fine-Tuned | Delta |
|--------|------|------------|-------|
| **Overall** | **{base_avg:.2f}/5** | **{ft_avg:.2f}/5** | **{ft_avg - base_avg:+.2f}** |

## By Difficulty

| Difficulty | Base | Fine-Tuned | Delta | Count |
|------------|------|------------|-------|-------|
"""
    for diff in ["beginner", "intermediate", "advanced"]:
        if diff in difficulties:
            d_base = sum(difficulties[diff]["base"]) / len(difficulties[diff]["base"])
            d_ft = sum(difficulties[diff]["ft"]) / len(difficulties[diff]["ft"])
            count = len(difficulties[diff]["base"])
            report += f"| {diff} | {d_base:.2f} | {d_ft:.2f} | {d_ft - d_base:+.2f} | {count} |\n"

    report += "\n## Hallucination Analysis\n\n"
    base_hall = sum(r["scores"]["hallucination"] for r in base_results) / n
    ft_hall = sum(r["scores"]["hallucination"] for r in ft_results) / n
    report += f"| Metric | Base | Fine-Tuned |\n|--------|------|------------|\n"
    report += f"| Hallucination Score | {base_hall:.2f} | {ft_hall:.2f} |\n"

    base_hall_count = sum(1 for r in base_results if r["scores"]["hallucination"] < 4.0)
    ft_hall_count = sum(1 for r in ft_results if r["scores"]["hallucination"] < 4.0)
    report += f"| Responses with hallucination | {base_hall_count} ({base_hall_count / n * 100:.1f}%) | {ft_hall_count} ({ft_hall_count / n * 100:.1f}%) |\n"

    report += "\n## Worst Performing Categories (Fine-Tuned)\n\n"
    cat_scores = {}
    for br, fr in zip(base_results, ft_results):
        cat = br.get("category", "unknown")
        if cat not in cat_scores:
            cat_scores[cat] = {"base": [], "ft": []}
        cat_scores[cat]["base"].append(br["scores"]["overall"])
        cat_scores[cat]["ft"].append(fr["scores"]["overall"])

    cat_avgs = [
        (
            cat,
            sum(scores["ft"]) / len(scores["ft"]),
            sum(scores["base"]) / len(scores["base"]),
        )
        for cat, scores in cat_scores.items()
    ]
    cat_avgs.sort(key=lambda x: x[1])

    report += "| Category | Base | Fine-Tuned | Delta | Count |\n|----------|------|------------|-------|-------|\n"
    for cat, ft_avg_cat, base_avg_cat in cat_avgs[:10]:
        count = len(cat_scores[cat]["ft"])
        report += f"| {cat} | {base_avg_cat:.2f} | {ft_avg_cat:.2f} | {ft_avg_cat - base_avg_cat:+.2f} | {count} |\n"

    report += "\n## Best Performing Categories (Fine-Tuned)\n\n"
    report += "| Category | Base | Fine-Tuned | Delta | Count |\n|----------|------|------------|-------|-------|\n"
    for cat, ft_avg_cat, base_avg_cat in cat_avgs[-10:]:
        count = len(cat_scores[cat]["ft"])
        report += f"| {cat} | {base_avg_cat:.2f} | {ft_avg_cat:.2f} | {ft_avg_cat - base_avg_cat:+.2f} | {count} |\n"

    output_path = (
        output_dir
        / f"difficulty-analysis-{datetime.now().strftime('%Y%m%d-%H%M%S')}.md"
    )
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)
    return output_path


def run_single_model_eval(
    evaluator: ModelEvaluator,
    eval_data: List[Dict[str, Any]],
    model_label: str,
    start_idx: int,
    checkpoint_path: Path,
    output_dir: Path,
    total_eval: int,
) -> List[Dict[str, Any]]:
    """Run evaluation for a single model (base or FT)."""
    results = []
    eval_times = []

    for i in range(start_idx, len(eval_data)):
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
        print(f"[{model_label} {i + 1}/{len(eval_data)}] {category} ({difficulty})...")

        try:
            response = evaluator.generate_response(question, system_msg)
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

        # Save partial results for checkpointing
        if (i + 1) % 50 == 0 or (i + 1) == len(eval_data):
            partial_results = {
                "base_results": results if model_label == "BASE" else [],
                "ft_results": results if model_label == "FT" else [],
                "completed": i + 1 if model_label == "FT" else 0,
                "base_completed": i + 1 if model_label == "BASE" else 0,
                "ft_completed": i + 1 if model_label == "FT" else 0,
            }
            # Save intermediate results
            interim_path = (
                output_dir / f"eval-{model_label.lower()}-results-{i + 1:05d}.json"
            )
            with open(interim_path, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            print(f"  Saved {model_label} results at {i + 1}/{len(eval_data)}")

    return results


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Evaluate model responses against eval.jsonl benchmark"
    )
    parser.add_argument("base_model_path", help="Base model ID or path")
    parser.add_argument(
        "ft_model_path", help="Fine-tuned model directory or adapter path"
    )
    parser.add_argument("eval_file", help="Evaluation JSONL file")
    parser.add_argument(
        "output_dir", nargs="?", default="outputs/benchmarks", help="Output directory"
    )
    parser.add_argument(
        "--fresh", action="store_true", help="Clear cached results before evaluating"
    )
    args = parser.parse_args()

    base_model_path = args.base_model_path
    ft_model_dir = args.ft_model_path
    eval_file = Path(args.eval_file)
    output_dir = Path(args.output_dir)
    fresh_mode = args.fresh

    ft_model_path = Path(ft_model_dir)
    if ft_model_path.is_dir() and (ft_model_path / "model.safetensors").exists():
        merged_model_path = str(ft_model_path)
        adapter_path = None
        print(f"Detected merged model: {merged_model_path}")
    elif ft_model_path.is_file() and ft_model_path.suffix == ".safetensors":
        adapter_path = str(ft_model_path.parent)
        merged_model_path = None
    elif ft_model_path.is_dir() and (ft_model_path / "adapters.safetensors").exists():
        adapter_path = str(ft_model_path)
        merged_model_path = None
    else:
        adapter_path = ft_model_dir
        merged_model_path = None

    eval_data = load_eval_data(eval_file)
    print(f"Loaded {len(eval_data)} eval examples")
    print(f"Base model: {base_model_path}")
    print(f"FT model: {merged_model_path or adapter_path}")

    checkpoint_path = output_dir / "eval-checkpoint.json"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Check for saved results from previous run
    base_results_path = output_dir / "eval-base-results-final.json"
    ft_results_path = output_dir / "eval-ft-results-final.json"

    base_results = None
    ft_results = None

    # Clear cache if --fresh flag is set
    if fresh_mode:
        if base_results_path.exists():
            print(f"Clearing cached base results: {base_results_path}")
            base_results_path.unlink()
        if ft_results_path.exists():
            print(f"Clearing cached FT results: {ft_results_path}")
            ft_results_path.unlink()
        print("Fresh evaluation mode enabled.\n")

    # Load base results if available
    if base_results_path.exists():
        print(f"Loading cached base results from {base_results_path}")
        with open(base_results_path, "r", encoding="utf-8") as f:
            base_results = json.load(f)
        print(f"  Loaded {len(base_results)} base results")

    # Load FT results if available
    if ft_results_path.exists():
        print(f"Loading cached FT results from {ft_results_path}")
        with open(ft_results_path, "r", encoding="utf-8") as f:
            ft_results = json.load(f)
        print(f"  Loaded {len(ft_results)} FT results")

    # Phase 1: Evaluate base model
    if base_results is None:
        print("\n" + "=" * 60)
        print("PHASE 1: Evaluating base model")
        print("=" * 60)
        base_evaluator = ModelEvaluator(base_model_path)
        base_evaluator.load_model()
        base_results = run_single_model_eval(
            base_evaluator,
            eval_data,
            "BASE",
            0,
            checkpoint_path,
            output_dir,
            len(eval_data),
        )
        # Save final base results
        with open(base_results_path, "w", encoding="utf-8") as f:
            json.dump(base_results, f, indent=2, ensure_ascii=False)
        print(f"\nBase results saved to {base_results_path}")
        # Free memory
        del base_evaluator
        import gc

        gc.collect()
    else:
        print(f"\nSkipping base model evaluation ({len(base_results)} results cached)")

    # Phase 2: Evaluate FT model
    if ft_results is None:
        print("\n" + "=" * 60)
        print("PHASE 2: Evaluating fine-tuned model")
        print("=" * 60)
        ft_evaluator = ModelEvaluator(
            base_model_path, adapter_path or "", merged_model_path or ""
        )
        ft_evaluator.load_model()
        ft_results = run_single_model_eval(
            ft_evaluator,
            eval_data,
            "FT",
            0,
            checkpoint_path,
            output_dir,
            len(eval_data),
        )
        # Save final FT results
        with open(ft_results_path, "w", encoding="utf-8") as f:
            json.dump(ft_results, f, indent=2, ensure_ascii=False)
        print(f"\nFT results saved to {ft_results_path}")
        del ft_evaluator
        import gc

        gc.collect()
    else:
        print(f"\nSkipping FT model evaluation ({len(ft_results)} results cached)")

    # Phase 3: Generate reports
    print("\n" + "=" * 60)
    print("PHASE 3: Generating reports")
    print("=" * 60)

    output_path = (
        output_dir / f"eval-comparison-{datetime.now().strftime('%Y%m%d-%H%M%S')}.md"
    )
    generate_comparison_report(base_results, ft_results, output_path, len(eval_data))

    difficulty_report = generate_difficulty_report(base_results, ft_results, output_dir)
    print(f"\nDifficulty report saved to {difficulty_report}")


if __name__ == "__main__":
    main()
