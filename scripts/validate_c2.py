#!/usr/bin/env python3
"""Validate Cycle 2 JSONL examples."""

import json
import sys
from pathlib import Path


def validate_example(line_num: int, example: dict) -> list:
    """Validate single example."""
    errors = []
    if "messages" not in example:
        return [f"Line {line_num}: Missing messages"]
    msgs = example["messages"]
    if len(msgs) != 3:
        errors.append(f"Line {line_num}: Must have 3 messages")
    else:
        if msgs[0].get("role") != "system":
            errors.append(f"Line {line_num}: First must be system")
        if msgs[1].get("role") != "user":
            errors.append(f"Line {line_num}: Second must be user")
        if msgs[2].get("role") != "assistant":
            errors.append(f"Line {line_num}: Third must be assistant")
    if "metadata" not in example:
        errors.append(f"Line {line_num}: Missing metadata")
    return errors


def main():
    input_dir = Path("data/curated_cycle2")
    total = 0
    all_errors = 0
    for jsonl_file in input_dir.glob("*.jsonl"):
        file_errors = 0
        line_num = 0
        with open(jsonl_file) as f:
            for line in f:
                line_num += 1
                if not line.strip():
                    continue
                try:
                    ex = json.loads(line)
                    errs = validate_example(line_num, ex)
                    for e in errs:
                        print(e)
                        file_errors += 1
                except json.JSONDecodeError as e:
                    print(f"Line {line_num}: JSON error - {e}")
                    file_errors += 1
        print(f"✅ {jsonl_file.name}: {line_num} examples, {file_errors} errors")
        total += line_num
        all_errors += file_errors
    print(f"\n📊 Total: {total} examples, {all_errors} errors")
    sys.exit(1 if all_errors > 0 else 0)


if __name__ == "__main__":
    main()
