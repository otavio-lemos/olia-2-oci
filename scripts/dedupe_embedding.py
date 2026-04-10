#!/usr/bin/env python3
"""
scripts/dedupe_embedding.py

Deduplicação baseada em embeddings usando sentence-transformers.
PER BUCKET: compare only within semantic buckets (category + intent + difficulty).
SEPARATE EMBEDDINGS: question and answer embedded separately.

Usage:
    python scripts/dedupe_embedding.py --input data/all_curated_clean.jsonl --output data/deduplicated.jsonl --threshold 0.975
    python scripts/dedupe_embedding.py --input data/all_curated_clean.jsonl --output data/deduplicated.jsonl --threshold 0.96 --model paraphrase-MiniLM-L6-v2
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple
from collections import defaultdict

import numpy as np


class EmbeddingDeduplicator:
    def __init__(
        self,
        model_name: str = "sentence-transformers/paraphrase-MiniLM-L6-v2",
        threshold: float = 0.975,
        question_threshold: float = 0.97,
        answer_threshold: float = 0.96,
    ):
        self.model_name = model_name
        self.threshold = threshold
        self.question_threshold = question_threshold
        self.answer_threshold = answer_threshold
        self.model = None
        self.examples = []
        self.question_embeddings = []
        self.answer_embeddings = []

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

    def get_question_text(self, example: Dict[str, Any]) -> str:
        """Extract question text for embedding."""
        messages = example.get("messages", [])
        for msg in messages:
            if msg.get("role") == "user":
                return msg.get("content", "")
        return ""

    def get_answer_text(self, example: Dict[str, Any]) -> str:
        """Extract answer text for embedding."""
        messages = example.get("messages", [])
        for msg in messages:
            if msg.get("role") == "assistant":
                return msg.get("content", "")
        return ""

    def get_bucket_key(self, example: Dict[str, Any]) -> str:
        """Create bucket key for semantic deduplication."""
        meta = example.get("metadata", {})
        cat = meta.get("category", "unknown")
        intent = meta.get("intent", "unknown")
        diff = meta.get("difficulty", "unknown")
        return f"{cat}|{intent}|{diff}"

    def compute_embeddings(self, examples: List[Dict[str, Any]]):
        """Compute separate embeddings for questions and answers."""
        questions = [self.get_question_text(e) for e in examples]
        answers = [self.get_answer_text(e) for e in examples]

        print(f"Computing question embeddings for {len(questions)} examples...")
        self.question_embeddings = self.model.encode(questions, convert_to_numpy=True)

        print(f"Computing answer embeddings for {len(answers)} examples...")
        self.answer_embeddings = self.model.encode(answers, convert_to_numpy=True)

        self.examples = examples
        print(f"Computed embeddings for {len(examples)} examples")

    def find_duplicates_per_bucket(self) -> List[Tuple[int, int]]:
        """Find duplicate pairs per bucket - compare only within semantic buckets."""
        buckets = defaultdict(list)
        for idx, ex in enumerate(self.examples):
            key = self.get_bucket_key(ex)
            buckets[key].append(idx)

        all_duplicates = []

        for bucket_key, indices in buckets.items():
            if len(indices) < 2:
                continue

            print(f"Processing bucket '{bucket_key}' with {len(indices)} examples...")

            q_embs = self.question_embeddings[indices]
            a_embs = self.answer_embeddings[indices]

            q_norms = np.linalg.norm(q_embs, axis=1, keepdims=True) + 1e-8
            q_normalized = q_embs / q_norms

            a_norms = np.linalg.norm(a_embs, axis=1, keepdims=True) + 1e-8
            a_normalized = a_embs / a_norms

            q_sim = np.dot(q_normalized, q_normalized.T)
            a_sim = np.dot(a_normalized, a_normalized.T)

            for i in range(len(indices)):
                for j in range(i + 1, len(indices)):
                    orig_i = indices[i]
                    orig_j = indices[j]

                    q_sim_ij = q_sim[i, j]
                    a_sim_ij = a_sim[i, j]

                    is_dup = (
                        q_sim_ij >= self.question_threshold
                        and a_sim_ij >= self.answer_threshold
                    )

                    if is_dup:
                        avg_sim = (q_sim_ij + a_sim_ij) / 2
                        all_duplicates.append((orig_i, orig_j, avg_sim))

        print(f"Found {len(all_duplicates)} duplicate pairs across all buckets")
        return all_duplicates

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
        duplicates = self.find_duplicates_per_bucket()
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
    parser = argparse.ArgumentParser(
        description="Deduplication using embeddings - per bucket"
    )
    parser.add_argument("--input", required=True, help="Input JSONL file")
    parser.add_argument("--output", required=True, help="Output JSONL file")
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.975,
        help="Combined similarity threshold (0-1)",
    )
    parser.add_argument(
        "--question-threshold",
        type=float,
        default=0.97,
        help="Question similarity threshold (0-1)",
    )
    parser.add_argument(
        "--answer-threshold",
        type=float,
        default=0.96,
        help="Answer similarity threshold (0-1)",
    )
    parser.add_argument(
        "--model",
        default="sentence-transformers/paraphrase-MiniLM-L6-v2",
        help="Embedding model",
    )
    args = parser.parse_args()

    dedup = EmbeddingDeduplicator(
        model_name=args.model,
        threshold=args.threshold,
        question_threshold=args.question_threshold,
        answer_threshold=args.answer_threshold,
    )
    dedup.run(args.input, args.output)


if __name__ == "__main__":
    main()
