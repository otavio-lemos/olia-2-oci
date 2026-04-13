#!/usr/bin/env python3
"""Prepare Cycle 2 dataset: merge, clean, deduplicate, split.

Combines cycle-1 and cycle-2 examples, then generates train/valid/eval splits.
"""

import json
import random
from pathlib import Path
from collections import defaultdict

random.seed(42)


def load_jsonl(path: Path) -> list:
    """Load JSONL file."""
    examples = []
    with open(path) as f:
        for line in f:
            if line.strip():
                examples.append(json.loads(line))
    return examples


def save_jsonl(examples: list, path: Path):
    """Save to JSONL."""
    with open(path, "w") as f:
        for ex in examples:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")


def main():
    """Merge and prepare dataset."""

    print("📂 Loading cycle-1...")
    c1_dir = Path("data/curated")
    c1_examples = []
    for f in c1_dir.glob("governance*.jsonl"):
        c1_examples.extend(load_jsonl(f))
    for f in c1_dir.glob("terraform*.jsonl"):
        c1_examples.extend(load_jsonl(f))
    print(f"  Cycle-1: {len(c1_examples)} examples")

    print("📂 Loading cycle-2...")
    c2_dir = Path("data/curated_cycle2")
    c2_examples = []
    for f in c2_dir.glob("*.jsonl"):
        c2_examples.extend(load_jsonl(f))
    print(f"  Cycle-2: {len(c2_examples)} examples")

    print("📦 Merging...")
    all_examples = c1_examples + c2_examples
    print(f"  Combined: {len(all_examples)} examples")

    print("🔄 Shuffling...")
    random.shuffle(all_examples)

    print("✂️ Splitting...")
    n = len(all_examples)
    train_end = int(n * 0.75)
    valid_end = int(n * 0.90)

    train = all_examples[:train_end]
    valid = all_examples[train_end:valid_end]
    eval_ = all_examples[valid_end:]

    print(f"  Train: {len(train)} (75%)")
    print(f"  Valid: {len(valid)} (15%)")
    print(f"  Eval: {len(eval_)} (10%)")

    print("💾 Saving...")
    data_dir = Path("data")

    save_jsonl(train, data_dir / "train_cycle2.jsonl")
    save_jsonl(valid, data_dir / "valid_cycle2.jsonl")
    save_jsonl(eval_, data_dir / "eval_cycle2.jsonl")

    print("✅ Cycle 2 dataset ready!")
    print(f"  data/train_cycle2.jsonl")
    print(f"  data/valid_cycle2.jsonl")
    print(f"  data/eval_cycle2.jsonl")


if __name__ == "__main__":
    main()
