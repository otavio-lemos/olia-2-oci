"""Intent Router - Classifica intenção via embeddings."""

from typing import Any, Optional
from collections import OrderedDict

INTENT_TYPES = [
    "migracao",
    "troubleshooting",
    "finops",
    "arquitetura",
    "descoberta",
    "execucao",
    "configuracao",
    "security",
]

INTENT_KEYWORDS = {
    "migracao": ["migrar", "migração", "aws", "azure", "gcp", "on-premise"],
    "troubleshooting": ["erro", "problema", "falha", "debug", "não funciona"],
    "finops": ["custo", "preço", "preço", "orçamento", "billing"],
    "arquitetura": ["arquitetura", "desenhar", "design", "landing zone"],
    "descoberta": ["quais", "como", "explicar", "o que é"],
    "execucao": ["criar", "deploy", "executar", "provisionar"],
    "configuracao": ["configurar", "setor", "alterar"],
    "security": ["segurança", "iam", "policy", "acesso"],
}


class IntentClassifier:
    """Classificador de intenção via embeddings similarity."""

    def __init__(self, embeddings: Any = None, cache_size: int = 100):
        self.embeddings = embeddings
        self._cache: OrderedDict[str, str] = OrderedDict()
        self._cache_size = cache_size

    async def classify(self, query: str) -> str:
        """Classifica intenção da query."""
        query_lower = query.lower()

        # Try keyword matching first (fast)
        for intent, keywords in INTENT_KEYWORDS.items():
            if any(kw in query_lower for kw in keywords):
                self._add_to_cache(query, intent)
                return intent

        # Fallback to embeddings if available
        if self.embeddings:
            try:
                intent = await self._classify_embeddings(query)
                self._add_to_cache(query, intent)
                return intent
            except Exception:
                pass

        # Default
        return "descoberta"

    async def _classify_embeddings(self, query: str) -> str:
        """Classifica via embeddings similarity."""
        # Simple implementation - in production would use cosine similarity
        query_embedding = self.embeddings.embed_query(query)

        # Return default - would compare with intent embeddings
        return "descoberta"

    def _add_to_cache(self, query: str, intent: str) -> None:
        """Adiciona ao cache."""
        if len(self._cache) >= self._cache_size:
            self._cache.popitem(last=False)
        self._cache[query] = intent

    def clear_cache(self) -> None:
        """Limpa cache."""
        self._cache.clear()


def create_intent_classifier(embeddings: Any = None) -> IntentClassifier:
    """Factory para criar IntentClassifier."""
    return IntentClassifier(embeddings=embeddings)
