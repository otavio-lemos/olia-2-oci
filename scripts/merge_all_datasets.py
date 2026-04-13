#!/usr/bin/env python3
"""Merge all training datasets into one unified dataset for single-cycle training.

Datasets:
- train.jsonl (14,470) - original curated
- train_cycle2.jsonl (4,125) - governance + terraform
- NEW: troubleshooting/*.jsonl (~600) - performance, storage, authentication

Usage:
    python scripts/merge_all_datasets.py
"""

import json
import random
from pathlib import Path
from collections import Counter

random.seed(42)


def load_jsonl(path: str) -> list:
    data = []
    with open(path, "r") as f:
        for line in f:
            if line.strip():
                data.append(json.loads(line))
    return data


def save_jsonl(data: list, path: str):
    with open(path, "w") as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
    print(f"Saved {len(data)} examples to {path}")


def analyze_categories(data: list) -> Counter:
    cats = [item.get("metadata", {}).get("category", "unknown") for item in data]
    return Counter(cats)


def main():
    base_dir = Path("data")
    curated_dir = base_dir / "curated"

    all_data = []
    sources = {}

    # 1. Original train data
    train_path = base_dir / "train.jsonl"
    if train_path.exists():
        train_data = load_jsonl(str(train_path))
        for item in train_data:
            item["metadata"]["source_dataset"] = "train"
        all_data.extend(train_data)
        sources["train.jsonl"] = len(train_data)
        print(f"Loaded train.jsonl: {len(train_data)} examples")

    # 2. Cycle 2 data
    cycle2_path = base_dir / "train_cycle2.jsonl"
    if cycle2_path.exists():
        cycle2_data = load_jsonl(str(cycle2_path))
        for item in cycle2_data:
            item["metadata"]["source_dataset"] = "cycle2"
        all_data.extend(cycle2_data)
        sources["train_cycle2.jsonl"] = len(cycle2_data)
        print(f"Loaded train_cycle2.jsonl: {len(cycle2_data)} examples")

    # 3. Troubleshooting data (new)
    troubleshooting_files = [
        "troubleshooting-performance.jsonl",
        "troubleshooting-storage.jsonl",
        "troubleshooting-authentication.jsonl",
    ]

    for tfile in troubleshooting_files:
        tpath = curated_dir / tfile
        if tpath.exists():
            tdata = load_jsonl(str(tpath))
            for item in tdata:
                item["metadata"]["source_dataset"] = "troubleshooting"
            all_data.extend(tdata)
            sources[tfile] = len(tdata)
            print(f"Loaded {tfile}: {len(tdata)} examples")
        else:
            print(f"WARNING: {tfile} not found - will skip")

    print(f"\n{'=' * 50}")
    print(f"Total before dedup: {len(all_data)} examples")

    # 4. Basic dedup by prompt hash
    seen_hashes = set()
    unique_data = []
    dupes = 0

    for item in all_data:
        prompt = item.get("messages", [{}])[1].get("content", "")[:500]
        h = hash(prompt)
        if h not in seen_hashes:
            seen_hashes.add(h)
            unique_data.append(item)
        else:
            dupes += 1

    print(f"Duplicates removed: {dupes}")
    print(f"Total after dedup: {len(unique_data)} examples")

    # 5. Analyze categories
    cats = analyze_categories(unique_data)
    print(f"\nCategory distribution ({len(cats)} categories):")
    for cat, count in sorted(cats.items()):
        print(f"  {cat}: {count}")

    # 6. Shuffle and split
    random.shuffle(unique_data)

    # 80/10/10 split
    total = len(unique_data)
    train_size = int(total * 0.8)
    valid_size = int(total * 0.1)

    train_data = unique_data[:train_size]
    valid_data = unique_data[train_size : train_size + valid_size]
    eval_data = unique_data[train_size + valid_size :]

    # 7. Save merged datasets
    save_jsonl(train_data, str(base_dir / "train_merged.jsonl"))
    save_jsonl(valid_data, str(base_dir / "valid_merged.jsonl"))
    save_jsonl(eval_data, str(base_dir / "eval_merged.jsonl"))

    # 8. Summary
    print(f"\n{'=' * 50}")
    print("MERGE COMPLETE")
    print(f"{'=' * 50}")
    print(f"Train: {len(train_data)} ({len(train_data) / total * 100:.1f}%)")
    print(f"Valid: {len(valid_data)} ({len(valid_data) / total * 100:.1f}%)")
    print(f"Eval:  {len(eval_data)} ({len(eval_data) / total * 100:.1f}%)")
    print(f"\nSources:")
    for src, cnt in sources.items():
        print(f"  {src}: {cnt}")
    print(
        f"  NEW troubleshooting: ~{sources.get('troubleshooting-performance.jsonl', 0) + sources.get('troubleshooting-storage.jsonl', 0) + sources.get('troubleshooting-authentication.jsonl', 0)}"
    )


if __name__ == "__main__":
    main()
