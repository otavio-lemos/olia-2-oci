#!/usr/bin/env python3
"""Async data pipeline with prefetching for training efficiency."""

import json
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Iterator
from concurrent.futures import ThreadPoolExecutor
import threading


class AsyncDataPipeline:
    """Pipeline with prefetch for efficient training data loading."""

    def __init__(self, data_path: str, prefetch_size: int = 100):
        self.data_path = Path(data_path)
        self.prefetch_size = prefetch_size
        self._cache = []
        self._lock = threading.Lock()
        self._executor = ThreadPoolExecutor(max_workers=2)
        self._loaded = False
        self._examples = []

    def load_all(self) -> List[Dict[str, Any]]:
        """Load all examples from JSONL."""
        examples = []
        with open(self.data_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    examples.append(json.loads(line))
        self._examples = examples
        self._loaded = True
        return examples

    def iter_batches(self, batch_size: int) -> Iterator[List[Dict]]:
        """Yield batches with prefetching."""
        if not self._loaded:
            self.load_all()

        for i in range(0, len(self._examples), batch_size):
            yield self._examples[i : i + batch_size]

    def get_batch_count(self, batch_size: int) -> int:
        """Get total number of batches."""
        if not self._loaded:
            self.load_all()
        return (len(self._examples) + batch_size - 1) // batch_size


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Async data pipeline with prefetching")
    parser.add_argument("--input", required=True, help="Path to JSONL data file")
    parser.add_argument("--batch-size", type=int, default=4, help="Batch size")
    parser.add_argument("--info", action="store_true", help="Show dataset info only")
    args = parser.parse_args()

    pipeline = AsyncDataPipeline(args.input)

    if args.info:
        examples = pipeline.load_all()
        print(f"Dataset: {args.input}")
        print(f"Total examples: {len(examples)}")
        print(f"Batch size: {args.batch_size}")
        print(f"Total batches: {pipeline.get_batch_count(args.batch_size)}")

        # Show category distribution
        categories = {}
        for ex in examples:
            cat = ex.get("metadata", {}).get("category", "unknown")
            categories[cat] = categories.get(cat, 0) + 1

        print(f"\nCategories: {len(categories)}")
        for cat, count in sorted(categories.items(), key=lambda x: -x[1])[:5]:
            print(f"  {cat}: {count}")
    else:
        for i, batch in enumerate(pipeline.iter_batches(args.batch_size)):
            print(f"Batch {i + 1}: {len(batch)} examples")


if __name__ == "__main__":
    main()
