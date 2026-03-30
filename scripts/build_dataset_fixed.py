#!/usr/bin/env python3
"""Build train/valid/eval from single JSONL or directory of JSON files."""

import json
import sys
import random
from pathlib import Path
from typing import List, Dict, Any
from collections import defaultdict

SYSTEM_PROMPT = """Você é um arquiteto especialista em OCI, migração multicloud e modernização on-premises. Seja técnico, objetivo e não invente serviços inexistentes."""

CATEGORY_MAP = {
    "oci-core-compute": "oci-core/compute",
    "oci-core-storage": "oci-core/storage",
    "oci-core-networking": "oci-core/networking",
    "oci-core-database": "oci-core/database",
    "oci-security-iam": "oci-security/iam",
    "oci-security-vault": "oci-security/vault",
    "oci-security-encryption": "oci-security/encryption",
    "oci-migration-aws-to-oci": "oci-migration/aws-to-oci",
    "oci-migration-azure-to-oci": "oci-migration/azure-to-oci",
    "oci-migration-gcp-to-oci": "oci-migration/gcp-to-oci",
    "oci-migration-onprem-to-oci": "oci-migration/onprem-to-oci",
    "oci-terraform-provider": "oci-terraform/provider",
    "oci-terraform-resources": "oci-terraform/resources",
    "oci-troubleshooting-connectivity": "oci-troubleshooting/connectivity",
    "oci-troubleshooting-performance": "oci-troubleshooting/performance",
}


def extract_category_from_filename(filename: str) -> str:
    """Extract category from JSONL filename like 'oci-migration-aws-to-oci-033.jsonl'."""
    name = Path(filename).stem
    for prefix, category in CATEGORY_MAP.items():
        if name.startswith(prefix):
            return category
    return "unknown"


def load_examples(input_path: Path) -> List[Dict[str, Any]]:
    """Load from single JSONL OR directory of JSON files."""
    examples = []

    if input_path.is_file() and input_path.suffix == ".jsonl":
        category = extract_category_from_filename(input_path.name)
        with open(input_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    ex = json.loads(line.strip())
                    if isinstance(ex, dict):
                        if "metadata" not in ex:
                            ex["metadata"] = {}
                        if (
                            "category" not in ex["metadata"]
                            or ex["metadata"]["category"] == "unknown"
                        ):
                            ex["metadata"]["category"] = category
                        examples.append(ex)
                except json.JSONDecodeError:
                    continue
    elif input_path.is_dir():
        for json_file in input_path.rglob("*.jsonl"):
            if json_file.name == "all_unique.jsonl":
                continue
            category = extract_category_from_filename(json_file.name)
            with open(json_file, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        ex = json.loads(line.strip())
                        if isinstance(ex, dict):
                            if "metadata" not in ex:
                                ex["metadata"] = {}
                            if (
                                "category" not in ex["metadata"]
                                or ex["metadata"]["category"] == "unknown"
                            ):
                                ex["metadata"]["category"] = category
                            examples.append(ex)
                    except json.JSONDecodeError:
                        continue
    else:
        raise ValueError(f"Input must be JSONL file or directory: {input_path}")

    print(f"✅ Loaded {len(examples)} examples from {input_path}")
    return examples


def ensure_chat_format(example: Dict[str, Any]) -> Dict[str, Any]:
    """Ensure chat format with system prompt."""
    if "messages" in example:
        # Already chat format
        messages = example["messages"]
    else:
        # Convert legacy format
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        if "question" in example or "prompt" in example:
            user_content = example.get("question", example.get("prompt", ""))
            messages.append({"role": "user", "content": user_content})
        if "answer" in example or "response" in example:
            assistant_content = example.get("answer", example.get("response", ""))
            messages.append({"role": "assistant", "content": assistant_content})

    metadata = example.get("metadata", {})
    return {"messages": messages, "metadata": metadata}


def balanced_split(
    examples: List[Dict[str, Any]], ratios: Dict[str, float]
) -> Dict[str, List]:
    """Stratified split by category."""
    categories = defaultdict(list)
    for ex in examples:
        cat = ex.get("metadata", {}).get("category", "unknown")
        categories[cat].append(ex)

    splits = {k: [] for k in ratios}
    total_ratios = sum(ratios.values())

    for cat_examples in categories.values():
        random.shuffle(cat_examples)
        n = len(cat_examples)

        start = 0
        for split_name, ratio in ratios.items():
            end = start + int(n * ratio / total_ratios)
            splits[split_name].extend(cat_examples[start:end])
            start = end

    return splits


def save_jsonl(examples: List[Dict], filepath: Path):
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        for ex in examples:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input", "-i", required=True, help="JSONL file or curated dir"
    )
    parser.add_argument("--output", "-o", default="data/", help="Output directory")
    parser.add_argument("--train-ratio", type=float, default=0.75)
    parser.add_argument("--valid-ratio", type=float, default=0.15)
    parser.add_argument("--eval-ratio", type=float, default=0.10)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    print("🚀 Building OCI specialist dataset...")

    # Load
    examples = load_examples(Path(args.input))
    chat_examples = [ensure_chat_format(ex) for ex in examples]

    # Split
    ratios = {
        "train": args.train_ratio,
        "valid": args.valid_ratio,
        "eval": args.eval_ratio,
    }
    splits = balanced_split(chat_examples, ratios)

    # Save
    output_dir = Path(args.output)
    save_jsonl(splits["train"], output_dir / "train.jsonl")
    save_jsonl(splits["valid"], output_dir / "valid.jsonl")
    save_jsonl(splits["eval"], output_dir / "eval.jsonl")

    print("\n✅ Dataset splits criados:")
    print(f"   📚 train.jsonl: {len(splits['train'])} exemplos")
    print(f"   ✅ valid.jsonl: {len(splits['valid'])} exemplos")
    print(f"   🧪 eval.jsonl:  {len(splits['eval'])} exemplos")


if __name__ == "__main__":
    main()
