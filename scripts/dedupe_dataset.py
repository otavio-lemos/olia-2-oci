#!/usr/bin/env python3
"""Deduplicate JSONL dataset with exact and near-duplicate detection."""

import json
import sys
from pathlib import Path
from typing import List, Dict, Any, Set
from collections import defaultdict


def normalize_text(text: str) -> str:
    return " ".join(text.lower().split())


def get_example_key(example: Dict[str, Any]) -> str:
    messages = example.get("messages", [])
    user_msgs = [m["content"] for m in messages if m.get("role") == "user"]
    user_text = normalize_text(" ".join(user_msgs[:1]))[:200]

    category = example.get("metadata", {}).get("category", "unknown")
    return f"{category}::{user_text}"


def find_exact_duplicates(examples: List[Dict[str, Any]]) -> Dict[str, List[int]]:
    seen = {}
    duplicates = defaultdict(list)

    for i, example in enumerate(examples):
        key = get_example_key(example)
        if key in seen:
            duplicates[key].append(i)
        else:
            seen[key] = i

    return {k: v for k, v in duplicates.items() if len(v) > 0}


def find_near_duplicates(
    examples: List[Dict[str, Any]], threshold: float = 0.9
) -> List[tuple]:
    near_dupes = []

    for i in range(len(examples)):
        key_i = get_example_key(examples[i])
        for j in range(i + 1, len(examples)):
            key_j = get_example_key(examples[j])

            len_min = min(len(key_i), len(key_j))
            if len_min == 0:
                continue

            matches = sum(1 for a, b in zip(key_i, key_j) if a == b)
            similarity = matches / len_min

            if similarity >= threshold:
                near_dupes.append((i, j, similarity))

    return near_dupes


def load_jsonl(filepath: Path) -> List[Dict[str, Any]]:
    examples = []

    with open(filepath, "r", encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            if line.strip():
                try:
                    examples.append(json.loads(line))
                except json.JSONDecodeError as e:
                    print(f"Skipping line {i}: {e}")
    return examples


def save_jsonl(examples: List[Dict[str, Any]], filepath: Path):
    with open(filepath, "w", encoding="utf-8") as f:
        for example in examples:
            f.write(json.dumps(example, ensure_ascii=False) + "\n")


def main():
    if len(sys.argv) < 2:
        print("Usage: python dedupe_dataset.py <file.jsonl> [--remove]")
        sys.exit(1)

    filepath = Path(sys.argv[1])
    remove = "--remove" in sys.argv

    if not filepath.exists():
        print(f"Error: File not found: {filepath}")
        sys.exit(1)

    examples = load_jsonl(filepath)
    print(f"Loaded {len(examples)} examples")

    exact_dupes = find_exact_duplicates(examples)
    print(f"\nExact duplicates found: {len(exact_dupes)}")
    for key, indices in list(exact_dupes.items())[:5]:
        print(f"  '{key[:50]}...': {len(indices)} copies")

    near_dupes = find_near_duplicates(examples)
    print(f"\nNear duplicates found: {len(near_dupes)}")
    for i, j, sim in near_dupes[:5]:
        print(f"  {i} <-> {j} (similarity: {sim:.2%})")

    if remove and (exact_dupes or near_dupes):
        indices_to_remove = set()
        for indices in exact_dupes.values():
            indices_to_remove.update(indices[1:])

        for i, j, _ in near_dupes:
            if i not in indices_to_remove:
                indices_to_remove.add(j)

        examples = [ex for i, ex in enumerate(examples) if i not in indices_to_remove]

        # Save in place (overwrite original)
        save_jsonl(examples, filepath)
        print(f"\nRemoved {len(indices_to_remove)} duplicates")
        print(f"Saved deduplicated file: {filepath}")

    if not remove:
        print("\nRun with --remove to deduplicate the file")


if __name__ == "__main__":
    main()
