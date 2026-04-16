#!/usr/bin/env python3
"""Validate dataset quality - check for duplicates, diversity, etc."""

import json
import os
import sys
from collections import defaultdict, Counter


def analyze_dataset(path):
    results = {}
    for fname in sorted(os.listdir(path)):
        if not fname.endswith(".jsonl"):
            continue
        filepath = os.path.join(path, fname)

        intents = defaultdict(list)
        with open(filepath) as f:
            for line in f:
                d = json.loads(line)
                intent = d.get("metadata", {}).get("intent", "unknown")
                content = d["messages"][-1]["content"]
                intents[intent].append(content)

        stats = {}
        issues = []
        for intent, contents in intents.items():
            total = len(contents)
            unique = len(set(contents))
            ratio = unique / total if total > 0 else 0

            stats[intent] = {"unique": unique, "total": total, "ratio": ratio}

            if total > 1 and ratio < 0.3:
                issues.append(f"{intent}: {unique}/{total} ({ratio * 100:.0f}%)")

        results[fname] = {"stats": stats, "issues": issues}

    return results


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "data/curated_v5"

    print(f"=== Dataset Quality Report ===")
    print(f"Path: {path}\n")

    results = analyze_dataset(path)

    total_issues = sum(len(r["issues"]) for r in results.values())
    categories_with_issues = sum(1 for r in results.values() if r["issues"])

    print(f"Total categories: {len(results)}")
    print(f"Categories with issues: {categories_with_issues}")
    print(f"Total issues: {total_issues}\n")

    if total_issues > 0:
        print("Categories with issues:")
        for fname, data in results.items():
            if data["issues"]:
                print(f"\n  {fname}:")
                for issue in data["issues"]:
                    print(f"    - {issue}")
        print("\n⚠️ ISSUES FOUND")
        sys.exit(1)
    else:
        print("✅ No issues found - all intents have good diversity!")

        # Show summary per intent
        intent_totals = defaultdict(lambda: {"unique": 0, "total": 0})
        for data in results.values():
            for intent, stat in data["stats"].items():
                intent_totals[intent]["unique"] += stat["unique"]
                intent_totals[intent]["total"] += stat["total"]

        print("\nIntent summary:")
        for intent, stats in sorted(intent_totals.items()):
            ratio = stats["unique"] / stats["total"] * 100 if stats["total"] > 0 else 0
            print(
                f"  {intent}: {stats['unique']} unique / {stats['total']} total ({ratio:.0f}%)"
            )

        sys.exit(0)


if __name__ == "__main__":
    main()
