#!/usr/bin/env python3
"""Semantic evaluation wrapper - extends eval_scoring with embedding-based similarity."""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Any

from eval_scoring import (
    load_eval_data,
    get_user_prompt,
    get_reference_answer,
    evaluate_response,
)


class SemanticEvaluator:
    def __init__(
        self, model_name: str = "sentence-transformers/paraphrase-MiniLM-L6-v2"
    ):
        self.model_name = model_name
        self.model = None
        self.embedding_cache = {}

    def load_model(self):
        """Lazy load embedding model."""
        if self.model is None:
            try:
                from sentence_transformers import SentenceTransformer

                self.model = SentenceTransformer(self.model_name)
                print(f"Loaded embedding model: {self.model_name}")
            except ImportError:
                print(
                    "Warning: sentence-transformers not installed. Install with: pip install sentence-transformers"
                )
                self.model = None
                return False
        return True

    def get_embedding(self, text: str):
        """Get embedding for text with caching."""
        if text in self.embedding_cache:
            return self.embedding_cache[text]

        if self.model is None:
            return None

        embedding = self.model.encode(text, convert_to_numpy=True)
        self.embedding_cache[text] = embedding
        return embedding

    def cosine_similarity(self, a, b):
        """Calculate cosine similarity between two embeddings."""
        import numpy as np

        a = a / (np.linalg.norm(a) + 1e-8)
        b = b / (np.linalg.norm(b) + 1e-8)
        return float(np.dot(a, b))

    def semantic_score(self, response: str, reference: str) -> float:
        """Calculate semantic similarity score (0-1)."""
        resp_emb = self.get_embedding(response)
        ref_emb = self.get_embedding(reference)

        if resp_emb is None or ref_emb is None:
            return 0.5

        return self.cosine_similarity(resp_emb, ref_emb)

    def evaluate_with_semantic(
        self, response: str, reference: str, category: str
    ) -> Dict[str, Any]:
        """Evaluate response with both regex and semantic scoring."""
        base_scores = evaluate_response(response, reference, category)

        sem_score = self.semantic_score(response, reference)

        base_scores["semantic_similarity"] = round(sem_score, 3)
        base_scores["semantic_weight"] = 0.3
        base_scores["overall_adjusted"] = base_scores["overall"] * 0.7 + sem_score * 0.3

        return base_scores


def main():
    parser = argparse.ArgumentParser(
        description="Evaluate with semantic similarity scoring"
    )
    parser.add_argument("eval_file", help="Path to eval.jsonl")
    parser.add_argument(
        "--model",
        default="sentence-transformers/paraphrase-MiniLM-L6-v2",
        help="Embedding model",
    )
    parser.add_argument(
        "--output", default="outputs/benchmarks/semantic_eval.json", help="Output file"
    )
    args = parser.parse_args()

    evaluator = SemanticEvaluator(model_name=args.model)
    if not evaluator.load_model():
        print("Falling back to regex-only scoring")
        sys.exit(1)

    eval_data = load_eval_data(Path(args.eval_file))

    results = []
    for i, example in enumerate(eval_data, 1):
        user_prompt = get_user_prompt(example)
        reference = get_reference_answer(example)
        category = example.get("metadata", {}).get("category", "unknown")

        response = example.get("generated_response", "")
        if not response:
            print(f"Skipping example {i}: no generated_response")
            continue

        scores = evaluator.evaluate_with_semantic(response, reference, category)

        results.append(
            {
                "prompt_id": i,
                "category": category,
                "scores": scores,
            }
        )

        print(
            f"[{i}/{len(eval_data)}] {category}: overall={scores['overall']:.2f}, semantic={scores['semantic_similarity']:.2f}"
        )

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)

    avg_semantic = sum(r["scores"]["semantic_similarity"] for r in results) / len(
        results
    )
    avg_overall = sum(r["scores"]["overall"] for r in results) / len(results)
    avg_adjusted = sum(r["scores"]["overall_adjusted"] for r in results) / len(results)

    print(f"\nResults saved to: {output_path}")
    print(f"Average semantic similarity: {avg_semantic:.3f}")
    print(f"Average overall (regex): {avg_overall:.3f}")
    print(f"Average overall (adjusted): {avg_adjusted:.3f}")


if __name__ == "__main__":
    main()
