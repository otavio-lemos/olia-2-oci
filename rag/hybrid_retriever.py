"""Hybrid retriever com RRF fusion e Cross-Encoder Re-ranking."""

from typing import List, Dict, Any, Optional
from langchain_core.documents import Document


class EnsembleRetriever:
    """Ensemble retriever with RRF fusion and optional Cross-Encoder Re-ranking."""

    def __init__(self, retrievers: List, weights: List[float], reranker_model: Optional[str] = None, reranker_top_k: int = 10):
        self.retrievers = retrievers
        self.weights = weights
        self.reranker_model = reranker_model
        self.reranker_top_k = reranker_top_k
        self.cross_encoder = None
        
        # Carregamento lazy do Cross-Encoder para não travar a inicialização
        if self.reranker_model:
            try:
                from sentence_transformers import CrossEncoder
                self.cross_encoder = CrossEncoder(self.reranker_model)
            except Exception as e:
                print(f"Failed to load cross-encoder {self.reranker_model}: {e}")

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
        sorted_docs = sorted(docs_scores.items(), key=lambda x: x[1], reverse=True)

        # Unique documents in order
        result_docs = []
        seen_ids = set()
        for doc_id, _ in sorted_docs:
            if doc_id in seen_ids:
                continue
            seen_ids.add(doc_id)
            for doc, _ in all_results:
                if id(doc) == doc_id:
                    result_docs.append(doc)
                    break

        # Re-ranking step using Cross-Encoder
        if self.cross_encoder and result_docs:
            try:
                # Prepare pairs of (query, document_text)
                pairs = [[query, doc.page_content] for doc in result_docs]
                scores = self.cross_encoder.predict(pairs)
                
                # Pair docs with new scores and sort
                scored_docs = list(zip(result_docs, scores))
                scored_docs.sort(key=lambda x: x[1], reverse=True)
                
                # Extract sorted docs
                result_docs = [doc for doc, score in scored_docs]
                return result_docs[:self.reranker_top_k]
            except Exception as e:
                print(f"Error during re-ranking: {e}")
                return result_docs[:k]

        return result_docs[:k]


class HybridRetrieverWithConfig:
    """Hybrid retriever que respeita config do YAML, incluindo Re-ranking."""

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
            reranking_config = config.get("re_ranking", {})

            self.GLOBAL_RERANKER = reranking_config.get("model") if reranking_config.get("enabled") else None
            self.GLOBAL_RERANKER_TOP_K = reranking_config.get("top_k", 10)

            self.STRATEGIES = {
                "default": {
                    "weights": [
                        config.get("fusion", {}).get("dense_weight", 0.7),
                        config.get("fusion", {}).get("sparse_weight", 0.3)
                    ],
                    "k": config.get("dense", {}).get("top_k", 20),
                    "re_ranking": reranking_config.get("enabled", False)
                }
            }

            for strategy_name, strategy_config in by_type.items():
                weights = [
                    strategy_config.get("fusion.dense_weight", self.STRATEGIES["default"]["weights"][0]),
                    strategy_config.get("fusion.sparse_weight", self.STRATEGIES["default"]["weights"][1]),
                ]
                k = strategy_config.get("dense.top_k", self.STRATEGIES["default"]["k"])
                re_ranking_enabled = strategy_config.get("re_ranking.enabled", self.STRATEGIES["default"]["re_ranking"])
                
                self.STRATEGIES[strategy_name] = {
                    "weights": weights, 
                    "k": k,
                    "re_ranking": re_ranking_enabled
                }
        except Exception:
            self.GLOBAL_RERANKER = None
            self.GLOBAL_RERANKER_TOP_K = 10
            self.STRATEGIES = {
                "default": {"weights": [0.7, 0.3], "k": 10, "re_ranking": False},
                "migracao": {"weights": [0.6, 0.4], "k": 10, "re_ranking": False},
                "configuracao": {"weights": [0.4, 0.6], "k": 10, "re_ranking": False},
                "troubleshooting": {"weights": [0.5, 0.5], "k": 10, "re_ranking": False},
            }

    def _build(self):
        strategy = self.STRATEGIES.get(self.config_name, self.STRATEGIES["default"])
        
        reranker_model = self.GLOBAL_RERANKER if strategy.get("re_ranking") else None
        
        self.retriever = EnsembleRetriever(
            retrievers=[self.dense, self.sparse],
            weights=strategy["weights"],
            reranker_model=reranker_model,
            reranker_top_k=self.GLOBAL_RERANKER_TOP_K
        )

    def set_strategy(self, strategy_name: str):
        """Muda estratégia."""
        self.config_name = strategy_name
        self._build()

    def invoke(self, query: str):
        return self.retriever.invoke(query, k=self.STRATEGIES.get(self.config_name, {}).get("k", 10))

    def get_config(self) -> Dict[str, Any]:
        return self.STRATEGIES.get(self.config_name, self.STRATEGIES["default"])


def create_hybrid_retriever(
    dense_retriever,
    sparse_retriever,
    weights: List[float] = [0.7, 0.3],
    k: int = 10,
    reranker_model: Optional[str] = None,
    reranker_top_k: int = 10
) -> EnsembleRetriever:
    """Cria hybrid retriever com weights e re-ranking opcional."""
    return EnsembleRetriever(
        retrievers=[dense_retriever, sparse_retriever],
        weights=weights,
        reranker_model=reranker_model,
        reranker_top_k=reranker_top_k
    )
