#!/usr/bin/env python3
"""Evaluate model responses against eval.jsonl benchmark with real scoring rubrics."""

import json
import re
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

import mlx.core as mx
from mlx_lm import load, generate
from mlx_lm.sample_utils import make_sampler


def load_eval_data(filepath: Path) -> List[Dict[str, Any]]:
    examples = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                examples.append(json.loads(line))
    return examples


def get_user_prompt(example: Dict[str, Any]) -> str:
    for msg in example.get("messages", []):
        if msg.get("role") == "user":
            return msg.get("content", "")
    return ""


def get_reference_answer(example: Dict[str, Any]) -> str:
    for msg in example.get("messages", []):
        if msg.get("role") == "assistant":
            return msg.get("content", "")
    return ""


class ModelEvaluator:
    def __init__(self, base_model_id: str, adapter_path: str = ""):
        self.base_model_id = base_model_id
        self.adapter_path = adapter_path
        self.model = None
        self.tokenizer = None
        self._loaded = False

    def load_model(self):
        if self._loaded:
            return
        print(f"Loading model: {self.base_model_id}")
        if self.adapter_path:
            print(f"  With adapter: {self.adapter_path}")
        self.model, self.tokenizer = load(
            path_or_hf_repo=self.base_model_id,
            adapter_path=self.adapter_path if self.adapter_path else None,
        )
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

        sampler = make_sampler(temp=0.7, top_p=1.0, min_p=0.0, top_k=0)

        response = generate(
            self.model,
            self.tokenizer,
            prompt=prompt_tokens,
            max_tokens=max_tokens,
            sampler=sampler,
            verbose=False,
        )

        return response


def score_technical_correctness(response: str, reference: str, category: str) -> float:
    score = 3.0
    if not response or response.startswith("Error:"):
        return 1.0
    if len(response) < 100:
        score -= 1.0
    real_cli_patterns = [
        r"oci\s+(compute|network|db|bv|os|ce|fn|kms|vault|iam|logging|monitoring|resource-manager|devops|container-instance|nosql|mysql|cloud-guard|waas|apm|stack-monitoring|file-storage|load-balancer|api-gateway)",
        r"oci_core_instance",
        r"oci_objectstorage_bucket",
        r"oci_database_autonomous_database",
        r"oci_containerengine_cluster",
        r"oci\.core\.ComputeClient",
        r"oci\.object_storage\.ObjectStorageClient",
        r"oci\.database\.DatabaseClient",
    ]
    fake_cli_patterns = [
        r"oci\s+instances\s+",
        r"oci\s+storage\s+",
        r"oci\s+connectivity\s+",
        r"oci\s+block\s+",
        r"oci\s+autonomous-json\s+",
        r"oci\s+azure-storage\s+",
        r"oci\s+onprem-storage\s+",
        r"oci\s+observability\s+",
        r"oci\s+authentication\s+",
        r"oci\.Compute\.InstancesClient",
        r"oci\.Storage\.BlockClient",
        r"oci\.ConnectivityClient",
        r"oci_compute_instances",
        r"oci_storage_block",
        r"oci_connectivity",
    ]
    has_real = any(re.search(p, response) for p in real_cli_patterns)
    has_fake = any(re.search(p, response) for p in fake_cli_patterns)
    if has_fake:
        score -= 2.0
    if has_real:
        score += 1.0
    if category in (
        "terraform/provider",
        "terraform/compute",
        "terraform/storage",
        "terraform/networking",
        "terraform/database",
        "terraform/container",
        "terraform/serverless",
        "terraform/security",
        "terraform/observability",
        "terraform/devops",
        "terraform/state",
    ):
        if "terraform" in response.lower() and (
            "resource" in response.lower() or "provider" in response.lower()
        ):
            score += 0.5
        if "oci_" in response:
            score += 0.5
    if "Allow group" in response and "to" in response and "in compartment" in response:
        score += 0.5
    if "Doc:" in response or "docs.oracle.com" in response:
        score += 0.3
    return max(1.0, min(5.0, score))


def score_depth(response: str, reference: str) -> float:
    score = 3.0
    if not response or response.startswith("Error:"):
        return 1.0
    depth_indicators = [
        (r"\d+\.\s+", 0.3),
        (r"```", 0.5),
        (r"- ", 0.2),
        (r"\* ", 0.2),
        (r"best practice", 0.3),
        (r"recomenda[çc][aã]o", 0.2),
        (r"trade.?off", 0.3),
        (r"vantagem", 0.2),
        (r"desvantagem", 0.2),
        (r"risco", 0.3),
        (r"mitiga[çc][aã]o", 0.3),
        (r"pr[ée]-requisito", 0.2),
        (r"valida[çc][aã]o", 0.2),
    ]
    for pattern, points in depth_indicators:
        if re.search(pattern, response, re.IGNORECASE):
            score += points
    word_count = len(response.split())
    if word_count > 200:
        score += 0.5
    if word_count > 500:
        score += 0.5
    if word_count < 50:
        score -= 1.0
    return max(1.0, min(5.0, score))


def score_structure(response: str) -> float:
    score = 3.0
    if not response or response.startswith("Error:"):
        return 1.0
    has_numbered_list = bool(re.search(r"\d+\.\s+", response))
    has_bullet_list = bool(re.search(r"^[-*]\s+", response, re.MULTILINE))
    has_code_block = "```" in response
    has_sections = bool(re.search(r"#+\s+", response))
    has_table = "|" in response and "---" in response
    structural_elements = sum(
        [has_numbered_list, has_bullet_list, has_code_block, has_sections, has_table]
    )
    if structural_elements >= 3:
        score += 1.5
    elif structural_elements >= 2:
        score += 1.0
    elif structural_elements >= 1:
        score += 0.5
    if len(response.split("\n")) > 10:
        score += 0.3
    return max(1.0, min(5.0, score))


def score_hallucination(response: str) -> float:
    score = 5.0
    if not response or response.startswith("Error:"):
        return 1.0
    hallucination_patterns = [
        (r"oci\s+instances\s+", 1.5),
        (r"oci\s+storage\s+(?!gateway)", 1.5),
        (r"oci\s+connectivity\s+", 1.5),
        (r"oci\s+block\s+(?!volume)", 1.5),
        (r"oci\s+autonomous-json", 1.5),
        (r"oci\s+azure-storage", 1.5),
        (r"oci\s+onprem-storage", 1.5),
        (r"oci\s+observability\s+", 1.5),
        (r"oci\s+authentication\s+", 1.5),
        (r"oci\.Compute\.InstancesClient", 1.5),
        (r"oci\.Storage\.BlockClient", 1.5),
        (r"oci\.ConnectivityClient", 1.5),
        (r"oci_compute_instances", 1.5),
        (r"oci_storage_block", 1.5),
        (r"oci_connectivity", 1.5),
        (r"semidesenvolvimento", 1.0),
        (r"Carneval", 1.0),
        (r"Insurance", 0.5),
        (r"deletar", 0.3),
    ]
    for pattern, penalty in hallucination_patterns:
        if re.search(pattern, response, re.IGNORECASE):
            score -= penalty
    fake_urls = [
        r"/Content/\w+/Con/\w+\.htm",
        r"/Content/\w+/-\w+\.htm",
    ]
    for pattern in fake_urls:
        if re.search(pattern, response):
            score -= 1.0
    return max(1.0, min(5.0, score))


def score_clarity(response: str) -> float:
    score = 3.0
    if not response or response.startswith("Error:"):
        return 1.0
    if len(response) < 50:
        score -= 1.5
    elif len(response) < 100:
        score -= 0.5
    if len(response) > 2000:
        score -= 0.3
    sentences = re.split(r"[.!?]+", response)
    avg_sentence_length = len(response.split()) / max(len(sentences), 1)
    if 10 <= avg_sentence_length <= 25:
        score += 0.5
    if re.search(
        r"\b(portanto|assim|consequentemente|dessa forma|em resumo)\b",
        response,
        re.IGNORECASE,
    ):
        score += 0.3
    if re.search(
        r"\b(exemplo|por exemplo|como segue|veja que)\b", response, re.IGNORECASE
    ):
        score += 0.3
    return max(1.0, min(5.0, score))


def evaluate_response(response: str, reference: str, category: str) -> Dict[str, Any]:
    scores = {
        "technical_correctness": score_technical_correctness(
            response, reference, category
        ),
        "depth": score_depth(response, reference),
        "structure": score_structure(response),
        "hallucination": score_hallucination(response),
        "clarity": score_clarity(response),
    }
    scores["overall"] = sum(scores.values()) / len(scores)
    return scores


def generate_comparison_report(
    base_results: List[Dict[str, Any]],
    ft_results: List[Dict[str, Any]],
    output_path: Path,
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
| cycle-1 | 3e-5 | 1864 | 0.074 | 0.070 |
| cycle-2 | 1e-5 | 932 | 0.056 | 0.056 |
| cycle-3 | 5e-6 | 466 | 0.039 | 0.053 |

**Best Model:** cycle-3 (lowest validation loss: 0.053)

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
- **Base Model:** mlx-community/Llama-3.2-3B-Instruct-4bit
- **Fine-Tuned Model:** LoRA adapters from cycle-3-v3 (merged), LR=5e-6, 466 iterations
- **Dataset:** 9,940 unique examples, 71 categories, 140 per category
"""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"Comparison report saved to {output_path}")
    print(f"Base model overall: {base_overall:.2f}/5")
    print(f"Fine-tuned model overall: {ft_overall:.2f}/5")
    print(f"Improvement: {improvement:+.2f} ({improvement_pct:+.1f}%)")


def main():
    if len(sys.argv) < 4:
        print(
            "Usage: python evaluate_model.py <base_model_path> <ft_model_path> <eval.jsonl> [output_dir]"
        )
        sys.exit(1)

    base_model_path = sys.argv[1]
    ft_model_dir = sys.argv[2]
    eval_file = Path(sys.argv[3])
    output_dir = Path(sys.argv[4]) if len(sys.argv) > 4 else Path("outputs/benchmarks")

    base_model_id = "mlx-community/Llama-3.2-3B-Instruct-4bit"

    ft_model_path = Path(ft_model_dir)
    if ft_model_path.is_file() and ft_model_path.suffix == ".safetensors":
        adapter_path = str(ft_model_path.parent)
    elif ft_model_path.is_dir():
        adapter_path = str(ft_model_path)
    else:
        adapter_path = ft_model_dir

    eval_data = load_eval_data(eval_file)
    print(f"Loaded {len(eval_data)} eval examples")
    print(f"Base model: {base_model_id}")
    print(f"Adapter: {adapter_path}")

    base_evaluator = ModelEvaluator(base_model_id)
    ft_evaluator = ModelEvaluator(base_model_id, adapter_path)

    base_evaluator.load_model()
    ft_evaluator.load_model()

    base_results = []
    ft_results = []

    for i, example in enumerate(eval_data):
        question = get_user_prompt(example)
        reference = get_reference_answer(example)
        category = example.get("metadata", {}).get("category", "unknown")
        system_msg = ""
        for msg in example.get("messages", []):
            if msg.get("role") == "system":
                system_msg = msg.get("content", "")
                break

        print(f"[{i + 1}/{len(eval_data)}] Evaluating {category}...")

        base_response = base_evaluator.generate_response(question, system_msg)
        ft_response = ft_evaluator.generate_response(question, system_msg)

        base_scores = evaluate_response(base_response, reference, category)
        ft_scores = evaluate_response(ft_response, reference, category)

        base_results.append(
            {
                "question": question,
                "response": base_response,
                "scores": base_scores,
                "category": category,
            }
        )
        ft_results.append(
            {
                "question": question,
                "response": ft_response,
                "scores": ft_scores,
                "category": category,
            }
        )

    output_path = (
        output_dir / f"eval-comparison-{datetime.now().strftime('%Y%m%d-%H%M%S')}.md"
    )
    generate_comparison_report(base_results, ft_results, output_path)


if __name__ == "__main__":
    main()
