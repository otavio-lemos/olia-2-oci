#!/usr/bin/env python3
"""Dynamic batch sizing based on sequence length distribution."""

import json
from pathlib import Path
from typing import Dict, Any
from collections import defaultdict


class DynamicBatcher:
    """Auto-tune batch size based on sequence length histogram."""

    def __init__(self, max_memory: int = 18 * 1024 * 1024 * 1024):
        self.max_memory = max_memory
        self.length_buckets = defaultdict(int)

    def analyze_dataset(self, data_path: Path) -> Dict[str, Any]:
        """Analyze sequence length distribution."""
        lengths = []

        with open(data_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    ex = json.loads(line)
                    user_content = ""
                    for msg in ex.get("messages", []):
                        if msg.get("role") == "user":
                            user_content = msg.get("content", "")
                            break
                    if user_content:
                        length = len(user_content)
                        lengths.append(length)
                        bucket = (length // 512) * 512
                        self.length_buckets[bucket] += 1

        if not lengths:
            return {"error": "No data found"}

        lengths_sorted = sorted(lengths)
        avg_length = sum(lengths) / len(lengths)
        p50 = lengths_sorted[len(lengths) // 2]
        p90 = lengths_sorted[int(len(lengths) * 0.9)]
        p99 = lengths_sorted[int(len(lengths) * 0.99)]

        return {
            "total": len(lengths),
            "avg_length": round(avg_length, 1),
            "p50_length": p50,
            "p90_length": p90,
            "p99_length": p99,
            "buckets": dict(self.length_buckets),
            "recommended_batch_size": self._recommend_batch_size(p99),
        }

    def _recommend_batch_size(self, p99_length: int) -> int:
        """Recommend batch size based on P99 length."""
        if p99_length < 1024:
            return 4
        elif p99_length < 2048:
            return 2
        else:
            return 1


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Dynamic batch sizing analysis")
    parser.add_argument("--input", required=True, help="Path to JSONL data file")
    parser.add_argument(
        "--recommend", action="store_true", help="Show recommended batch size"
    )
    args = parser.parse_args()

    batcher = DynamicBatcher()
    result = batcher.analyze_dataset(Path(args.input))

    print("=== Sequence Length Analysis ===")
    print(f"Total examples: {result.get('total', 0)}")
    print(f"Average length: {result.get('avg_length', 0)} chars")
    print(f"P50 (median): {result.get('p50_length', 0)} chars")
    print(f"P90: {result.get('p90_length', 0)} chars")
    print(f"P99: {result.get('p99_length', 0)} chars")

    if args.recommend:
        print(f"\n=== Recommended Batch Size ===")
        print(f"Batch size: {result.get('recommended_batch_size', 1)}")
        print("\nRecommendation logic:")
        print("  - P99 < 1024 chars: batch_size = 4")
        print("  - P99 < 2048 chars: batch_size = 2")
        print("  - P99 >= 2048 chars: batch_size = 1")


if __name__ == "__main__":
    main()
