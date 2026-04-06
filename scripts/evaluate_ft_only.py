#!/usr/bin/env python3
"""Evaluate only the fine-tuned model against reference answers."""

import json
import re
import sys
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any

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


def format_eta(seconds_per_item: float, remaining: int) -> str:
    if remaining <= 0 or seconds_per_item <= 0:
        return "calculating..."
    total_seconds = int(seconds_per_item * remaining)
    return str(timedelta(seconds=total_seconds))


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
    cross_cloud_patterns = [
        r"provider\s+[\"']?aws[\"']?",
        r"resource\s+[\"']?aws_",
        r"resource\s+[\"']?azurerm_",
        r"aws_instance",
        r"aws_lb",
        r"aws_vpc",
        r"aws_security_group",
        r"aws_s3",
        r"aws_iam",
        r"azurerm_network_security_group",
        r"azurerm_virtual_network",
        r"azurerm_subnet",
        r"azurerm_public_ip",
        r"\bEC2\b",
        r"\bCloudWatch\b",
        r"AWS Management Console",
        r"Azure Portal",
    ]
    has_cross_cloud = any(re.search(p, response) for p in cross_cloud_patterns)
    if has_fake:
        score -= 2.0
    if has_cross_cloud:
        score -= 2.5
    if has_real:
        score += 1.0
    terraform_cats = [
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
    ]
    if category in terraform_cats:
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
    cross_cloud_patterns = [
        (r"provider\s+[\"']?aws[\"']?", 2.0),
        (r"resource\s+[\"']?aws_", 2.0),
        (r"resource\s+[\"']?azurerm_", 2.0),
        (r"aws_instance", 2.0),
        (r"aws_lb", 2.0),
        (r"aws_vpc", 2.0),
        (r"aws_security_group", 2.0),
        (r"aws_s3", 2.0),
        (r"aws_iam", 2.0),
        (r"azurerm_network_security_group", 2.0),
        (r"azurerm_virtual_network", 2.0),
        (r"azurerm_subnet", 2.0),
        (r"azurerm_public_ip", 2.0),
        (r"EC2", 1.5),
        (r"CloudWatch", 1.0),
        (r"AWS Management Console", 1.5),
        (r"AWS Console", 1.0),
        (r"Amazon Web Services", 1.0),
        (r"Azure Portal", 1.0),
        (r"Azure Resource Manager", 1.0),
    ]
    for pattern, penalty in hallucination_patterns:
        if re.search(pattern, response, re.IGNORECASE):
            score -= penalty
    for pattern, penalty in cross_cloud_patterns:
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
            path_or_hf_repo="mlx-community/Llama-3.2-3B-Instruct-4bit",
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
**Base:** mlx-community/Llama-3.2-3B-Instruct-4bit
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
