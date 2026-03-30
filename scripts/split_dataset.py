#!/usr/bin/env python3
"""Split curated dataset into train/valid/eval with balanced distribution."""

import json
import sys
import random
from pathlib import Path
from typing import List, Dict, Any


def load_jsonl(filepath: Path) -> List[Dict[str, Any]]:
    examples = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                examples.append(json.loads(line))
    return examples


def get_category(example: Dict[str, Any]) -> str:
    if "metadata" in example and "category" in example["metadata"]:
        return example["metadata"]["category"]
    messages = example.get("messages", [])
    for msg in messages:
        if msg.get("role") == "user":
            content = msg.get("content", "").lower()
            if "vcn" in content or "network" in content:
                return "oci-core/networking"
            if "iam" in content or "policy" in content:
                return "oci-security/iam"
            if "migration" in content or "aws" in content or "azure" in content:
                return "oci-migration"
            if "terraform" in content:
                return "oci-terraform"
    return "other"


def balance_by_category(
    examples: List[Dict[str, Any]], train_ratio: float = 0.8, valid_ratio: float = 0.1
) -> Dict[str, List[Dict[str, Any]]]:
    random.seed(42)

    by_category = {}
    for ex in examples:
        cat = get_category(ex)
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(ex)

    print(f"Categories found: {list(by_category.keys())}")
    for cat, cats in by_category.items():
        print(f"  {cat}: {len(cats)} examples")

    train, valid, eval_ = [], [], []

    for cat, cat_examples in by_category.items():
        random.shuffle(cat_examples)
        n = len(cat_examples)
        n_train = int(n * train_ratio)
        n_valid = int(n * valid_ratio)

        train.extend(cat_examples[:n_train])
        valid.extend(cat_examples[n_train : n_train + n_valid])
        eval_.extend(cat_examples[n_train + n_valid :])

    return {"train": train, "valid": valid, "eval": eval_}


def save_jsonl(examples: List[Dict[str, Any]], filepath: Path):
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        for example in examples:
            f.write(json.dumps(example, ensure_ascii=False) + "\n")


def main():
    if len(sys.argv) < 2:
        print("Usage: python split_dataset.py <input.jsonl> [output_dir]")
        sys.exit(1)

    input_file = Path(sys.argv[1])
    output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else input_file.parent

    examples = load_jsonl(input_file)
    print(f"Loaded {len(examples)} examples")

    splits = balance_by_category(examples)

    output_dir = Path(output_dir)
    save_jsonl(splits["train"], output_dir / "train.jsonl")
    save_jsonl(splits["valid"], output_dir / "valid.jsonl")
    save_jsonl(splits["eval"], output_dir / "eval.jsonl")

    print(f"\nSplit complete:")
    print(f"  train.jsonl: {len(splits['train'])}")
    print(f"  valid.jsonl: {len(splits['valid'])}")
    print(f"  eval.jsonl: {len(splits['eval'])}")


if __name__ == "__main__":
    main()
