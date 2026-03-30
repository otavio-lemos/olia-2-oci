#!/usr/bin/env python3
"""Build train/valid/eval JSONL files from curated examples."""

import json
import sys
import random
from pathlib import Path
from typing import List, Dict, Any


SYSTEM_PROMPT = """You are an Oracle Cloud Infrastructure (OCI) specialist. You provide accurate, practical guidance on OCI services, architecture, migration, and troubleshooting. Always be specific, cite OCI resource names, and explain trade-offs when recommending architectures."""


def load_curated_examples(curated_dir: Path) -> List[Dict[str, Any]]:
    examples = []

    for json_file in curated_dir.rglob("*.json"):
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                examples.extend(data)
            else:
                examples.append(data)

    return examples


def convert_to_chat_format(example: Dict[str, Any]) -> Dict[str, Any]:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    user_content = example.get("question", example.get("prompt", ""))
    messages.append({"role": "user", "content": user_content})

    assistant_content = example.get("answer", example.get("response", ""))
    messages.append({"role": "assistant", "content": assistant_content})

    metadata = {
        "category": example.get("category", "unknown"),
        "difficulty": example.get("difficulty", "intermediate"),
        "source": example.get("source", "generated"),
    }

    return {"messages": messages, "metadata": metadata}


def split_dataset(
    examples: List[Dict[str, Any]],
    train_ratio: float = 0.8,
    valid_ratio: float = 0.1,
    eval_ratio: float = 0.1,
) -> Dict[str, List[Dict[str, Any]]]:
    random.seed(42)

    categories = {}
    for ex in examples:
        cat = ex.get("metadata", {}).get("category", "unknown")
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(ex)

    train, valid, eval_ = [], [], []

    for cat, cat_examples in categories.items():
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
    curated_dir = Path("data/curated")
    output_dir = Path("data")

    if len(sys.argv) > 1:
        curated_dir = Path(sys.argv[1])
    if len(sys.argv) > 2:
        output_dir = Path(sys.argv[2])

    print(f"Loading curated examples from {curated_dir}...")
    raw_examples = load_curated_examples(curated_dir)
    print(f"Loaded {len(raw_examples)} examples")

    chat_examples = [convert_to_chat_format(ex) for ex in raw_examples]

    splits = split_dataset(chat_examples)

    save_jsonl(splits["train"], output_dir / "train.jsonl")
    save_jsonl(splits["valid"], output_dir / "valid.jsonl")
    save_jsonl(splits["eval"], output_dir / "eval.jsonl")

    print(f"\nDataset split complete:")
    print(f"  train.jsonl: {len(splits['train'])} examples")
    print(f"  valid.jsonl: {len(splits['valid'])} examples")
    print(f"  eval.jsonl: {len(splits['eval'])} examples")


if __name__ == "__main__":
    main()
