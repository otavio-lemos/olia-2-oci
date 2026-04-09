#!/usr/bin/env python3
"""
scripts/dedupe_embedding.py

Deduplicação baseada em embeddings usando sentence-transformers.

Usage:
    python scripts/dedupe_embedding.py --input data/all_curated_clean.jsonl --output data/deduplicated.jsonl --threshold 0.85
    python scripts/dedupe_embedding.py --input data/all_curated_clean.jsonl --output data/deduplicated.jsonl --threshold 0.9 --model paraphrase-MiniLM-L6-v2
"""

import argparse
import json
import hashlib
from pathlib import Path
from typing import Dict, Any, List, Tuple

import numpy as np


class EmbeddingDeduplicator:
    def __init__(
        self,
        model_name: str = "sentence-transformers/paraphrase-MiniLM-L6-v2",
        threshold: float = 0.85,
    ):
        self.model_name = model_name
        self.threshold = threshold
        self.model = None
        self.embeddings = []
        self.examples = []

    def load_model(self):
        """Load embedding model."""
        try:
            from sentence_transformers import SentenceTransformer

            self.model = SentenceTransformer(self.model_name)
            print(f"Loaded embedding model: {self.model_name}")
            return True
        except ImportError:
            print("Error: sentence-transformers not installed")
            print("Install with: pip install sentence-transformers")
            return False

    def get_text_for_embedding(self, example: Dict[str, Any]) -> str:
        """Extract text content for embedding."""
        messages = example.get("messages", [])
        parts = []
        for msg in messages:
            content = msg.get("content", "")
            if content:
                parts.append(content)
        return " ".join(parts)

    def compute_embeddings(self, examples: List[Dict[str, Any]]):
        """Compute embeddings for all examples."""
        texts = [self.get_text_for_embedding(e) for e in examples]
        self.embeddings = self.model.encode(texts, convert_to_numpy=True)
        self.examples = examples
        print(f"Computed embeddings for {len(texts)} examples")

    def cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Calculate cosine similarity."""
        a = a / (np.linalg.norm(a) + 1e-8)
        b = b / (np.linalg.norm(b) + 1e-8)
        return float(np.dot(a, b))

    def find_duplicates(self) -> List[Tuple[int, int]]:
        """Find duplicate pairs above threshold."""
        n = len(self.embeddings)
        duplicates = []

        for i in range(n):
            for j in range(i + 1, n):
                sim = self.cosine_similarity(self.embeddings[i], self.embeddings[j])
                if sim >= self.threshold:
                    duplicates.append((i, j, sim))

        print(f"Found {len(duplicates)} duplicate pairs (threshold={self.threshold})")
        return duplicates

    def remove_duplicates(self, duplicates: List[Tuple[int, int]]) -> List[int]:
        """Remove duplicates, keeping first occurrence."""
        to_remove = set()
        for i, j, sim in duplicates:
            if i not in to_remove and j not in to_remove:
                to_remove.add(j)

        kept_indices = [i for i in range(len(self.examples)) if i not in to_remove]
        print(
            f"Keeping {len(kept_indices)} of {len(self.examples)} examples ({len(to_remove)} removed)"
        )
        return kept_indices

    def run(self, input_path: str, output_path: str):
        """Run deduplication pipeline."""
        examples = []
        with open(input_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    examples.append(json.loads(line))

        print(f"Loaded {len(examples)} examples from {input_path}")

        if not self.load_model():
            sys.exit(1)

        self.compute_embeddings(examples)
        duplicates = self.find_duplicates()
        kept_indices = self.remove_duplicates(duplicates)

        kept_examples = [self.examples[i] for i in kept_indices]

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            for ex in kept_examples:
                f.write(json.dumps(ex, ensure_ascii=False) + "\n")

        print(f"Deduplicated dataset saved to: {output_path}")
        print(
            f"Original: {len(examples)}, Kept: {len(kept_examples)}, Removed: {len(examples) - len(kept_examples)}"
        )


def main():
    parser = argparse.ArgumentParser(description="Deduplication using embeddings")
    parser.add_argument("--input", required=True, help="Input JSONL file")
    parser.add_argument("--output", required=True, help="Output JSONL file")
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.85,
        help="Similarity threshold (0-1)",
    )
    parser.add_argument(
        "--model",
        default="sentence-transformers/paraphrase-MiniLM-L6-v2",
        help="Embedding model",
    )
    args = parser.parse_args()

    dedup = EmbeddingDeduplicator(model_name=args.model, threshold=args.threshold)
    dedup.run(args.input, args.output)


if __name__ == "__main__":
    import sys

    main()
