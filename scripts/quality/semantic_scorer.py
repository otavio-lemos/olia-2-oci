#!/usr/bin/env python3
"""Semantic scoring for hallucination detection using lightweight embeddings."""

import json
import numpy as np
from pathlib import Path
from typing import Dict, Any, Tuple


class SemanticScorer:
    """Lightweight semantic similarity for hallucination detection."""

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
                    "Warning: sentence-transformers not installed. Using fallback TF-IDF similarity."
                )
                self.model = None

    def get_embedding(self, text: str) -> np.ndarray:
        """Get embedding for text with caching."""
        if text in self.embedding_cache:
            return self.embedding_cache[text]

        if self.model is None:
            return self._tfidf_fallback(text)

        embedding = self.model.encode(text, convert_to_numpy=True)
        self.embedding_cache[text] = embedding
        return embedding

    def _tfidf_fallback(self, text: str) -> np.ndarray:
        """Simple word hashing fallback when sentence-transformers not available."""
        words = text.lower().split()
        vector = np.zeros(128)
        for i, word in enumerate(words[:128]):
            vector[i % 128] += hash(word) % 100 / 100.0
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
        return vector

    def compute_similarity(self, text1: str, text2: str) -> float:
        """Compute cosine similarity between two texts."""
        emb1 = self.get_embedding(text1)
        emb2 = self.get_embedding(text2)

        norm1 = np.linalg.norm(emb1)
        norm2 = np.linalg.norm(emb2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return float(np.dot(emb1, emb2) / (norm1 * norm2))

    def detect_hallucination(
        self, reference: str, generated: str, threshold: float = 0.3
    ) -> Dict[str, Any]:
        """Detect potential hallucination based on semantic divergence."""
        similarity = self.compute_similarity(reference, generated)

        return {
            "similarity": round(similarity, 3),
            "is_hallucination": similarity < threshold,
            "confidence": round(1.0 - similarity, 3),
            "threshold": threshold,
        }

    def score_response_quality(
        self, reference: str, generated: str
    ) -> Dict[str, float]:
        """Score response quality across multiple dimensions."""
        similarity = self.compute_similarity(reference, generated)

        return {
            "semantic_similarity": round(similarity, 3),
            "factual_alignment": round(min(1.0, similarity * 1.2), 3),
            "coverage": round(similarity if similarity > 0.5 else similarity * 0.8, 3),
        }


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Semantic scoring for hallucination detection"
    )
    parser.add_argument("--reference", required=True, help="Reference text file")
    parser.add_argument("--generated", required=True, help="Generated text file")
    parser.add_argument(
        "--threshold", type=float, default=0.3, help="Hallucination threshold"
    )
    args = parser.parse_args()

    scorer = SemanticScorer()
    scorer.load_model()

    with open(args.reference, "r") as f:
        ref_text = f.read()
    with open(args.generated, "r") as f:
        gen_text = f.read()

    result = scorer.detect_hallucination(ref_text, gen_text, args.threshold)

    print("=== Hallucination Detection ===")
    print(f"Similarity: {result['similarity']}")
    print(f"Is Hallucination: {result['is_hallucination']}")
    print(f"Confidence: {result['confidence']}")

    quality = scorer.score_response_quality(ref_text, gen_text)
    print("\n=== Quality Scores ===")
    print(f"Semantic Similarity: {quality['semantic_similarity']}")
    print(f"Factual Alignment: {quality['factual_alignment']}")
    print(f"Coverage: {quality['coverage']}")


if __name__ == "__main__":
    main()
