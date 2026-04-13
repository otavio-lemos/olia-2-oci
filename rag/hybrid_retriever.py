"""Hybrid retriever com RRF fusion (custom implementation)."""

from typing import List, Dict, Any
from langchain_core.documents import Document


class EnsembleRetriever:
    """Ensemble retriever with RRF fusion."""

    def __init__(self, retrievers: List, weights: List[float]):
        self.retrievers = retrievers
        self.weights = weights

    def invoke(self, query: str, k: int = 10):
        # Get results from each retriever
        all_results = []
        docs_scores = {}

        for retriever, weight in zip(self.retrievers, self.weights):
            try:
                results = retriever.invoke(query)
                for rank, doc in enumerate(results):
                    doc_id = id(doc)
                    score = 1.0 / (rank + 1)  # RRF score
                    docs_scores[doc_id] = docs_scores.get(doc_id, 0) + weight * score
                    all_results.append((doc, score))
            except Exception as e:
                print(f"Error in retriever: {e}")

        # Sort by RRF score
        sorted_docs = sorted(docs_scores.items(), key=lambda x: x[1], reverse=True)[:k]

        # Return documents in order
        result_docs = []
        for doc_id, _ in sorted_docs:
            for doc, _ in all_results:
                if id(doc) == doc_id:
                    result_docs.append(doc)
                    break

        return result_docs[:k]


class HybridRetrieverWithConfig:
    """Hybrid retriever que respeita config do YAML."""

    def __init__(self, dense_retriever, sparse_retriever, config_name: str = "default"):
        self.dense = dense_retriever
        self.sparse = sparse_retriever
        self.config_name = config_name
        self._load_strategies_from_config()
        self._build()

    def _load_strategies_from_config(self):
        """Load strategies from YAML config."""
        try:
            from rag.config import get_rag_config

            config = get_rag_config()
            by_type = config.get("by_type", {})

            self.STRATEGIES = {"default": {"weights": [0.7, 0.3], "k": 10}}

            for strategy_name, strategy_config in by_type.items():
                weights = [
                    strategy_config.get("fusion.dense_weight", 0.7),
                    strategy_config.get("fusion.sparse_weight", 0.3),
                ]
                k = strategy_config.get("dense.top_k", 10)
                self.STRATEGIES[strategy_name] = {"weights": weights, "k": k}
        except Exception:
            self.STRATEGIES = {
                "default": {"weights": [0.7, 0.3], "k": 10},
                "migracao": {"weights": [0.6, 0.4], "k": 10},
                "configuracao": {"weights": [0.4, 0.6], "k": 10},
                "troubleshooting": {"weights": [0.5, 0.5], "k": 10},
            }

    def _build(self):
        strategy = self.STRATEGIES.get(self.config_name, self.STRATEGIES["default"])
        self.retriever = EnsembleRetriever(
            retrievers=[self.dense, self.sparse],
            weights=strategy["weights"],
        )

    def set_strategy(self, strategy_name: str):
        """Muda estratégia."""
        self.config_name = strategy_name
        self._build()

    def invoke(self, query: str):
        return self.retriever.invoke(query)

    def get_config(self) -> Dict[str, Any]:
        return self.STRATEGIES.get(self.config_name, self.STRATEGIES["default"])


def create_hybrid_retriever(
    dense_retriever,
    sparse_retriever,
    weights: List[float] = [0.7, 0.3],
    k: int = 10,
) -> EnsembleRetriever:
    """Cria hybrid retriever com weights."""
    return EnsembleRetriever(
        retrievers=[dense_retriever, sparse_retriever],
        weights=weights,
    )
