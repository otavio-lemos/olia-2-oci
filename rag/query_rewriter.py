"""Query Rewriter - Expande e reescreve queries para melhor recall."""

from typing import TypedDict, Protocol, Any
from collections import OrderedDict


class QueryExpansion(TypedDict):
    """Resultado da expansão de query."""

    original: str
    expanded: list[str]
    intent: str
    entities: list[str]


class QueryRewriter(Protocol):
    """Interface para reescrita de queries."""

    async def rewrite(self, query: str, intent: str | None = None) -> QueryExpansion:
        """Reescreve e expande query."""
        ...

    async def expand(self, query: str, num_variations: int = 5) -> list[str]:
        """Gera variações da query."""
        ...


class QueryRewriterImpl:
    """Implementação de QueryRewriter usando LLM."""

    def __init__(self, llm_client: Any = None, cache_size: int = 100):
        self.llm_client = llm_client
        self._cache: OrderedDict[str, QueryExpansion] = OrderedDict()
        self._cache_size = cache_size

    async def rewrite(self, query: str, intent: str | None = None) -> QueryExpansion:
        """Reescreve e expande query."""
        # Check cache
        if query in self._cache:
            return self._cache[query]

        # Determine intent if not provided
        intent = intent or await self._classify_intent(query)

        # Generate enhanced query using LLM
        prompt = self._build_rewrite_prompt(query, intent)
        enhanced = await self._generate(prompt)

        # Parse result
        result = QueryExpansion(
            original=query,
            expanded=[enhanced],
            intent=intent,
            entities=await self._extract_entities(enhanced),
        )

        # Add to cache
        self._add_to_cache(query, result)

        return result

    async def expand(self, query: str, num_variations: int = 5) -> list[str]:
        """Gera variações da query."""
        # Check cache for variations
        cache_key = f"{query}:expand:{num_variations}"
        if cache_key in self._cache:
            cached = self._cache[cache_key]
            return cached["expanded"]

        base_expansion = await self.rewrite(query)

        prompt = self._build_expand_prompt(query, num_variations)
        variations_text = await self._generate(prompt)

        # Parse variations
        variations = [v.strip() for v in variations_text.split("\n") if v.strip()]
        variations = variations[:num_variations]

        if not variations:
            variations = base_expansion["expanded"]

        result = QueryExpansion(
            original=query,
            expanded=variations,
            intent=base_expansion["intent"],
            entities=base_expansion["entities"],
        )

        self._add_to_cache(cache_key, result)
        return variations

    async def _classify_intent(self, query: str) -> str:
        """Classifica intenção da query."""
        query_lower = query.lower()

        if any(w in query_lower for w in ["criar", "criar", "deploy", "criar"]):
            return "execucao"
        if any(w in query_lower for w in ["migrar", "migração"]):
            return "migracao"
        if any(w in query_lower for w in ["erro", "problema", "falha"]):
            return "troubleshooting"
        if any(w in query_lower for w in ["custo", "preço", "preço"]):
            return "finops"
        if any(w in query_lower for w in ["arquitetura", "desenhar"]):
            return "arquitetura"

        return "descoberta"

    async def _extract_entities(self, text: str) -> list[str]:
        """Extrai entidades (serviços OCI) do texto."""
        services = [
            "compute",
            "instance",
            "autonomous",
            "database",
            "functions",
            "oke",
            "kubernetes",
            "v cn",
            "object storage",
            "block volume",
            "load balancer",
            "api gateway",
            "vault",
            "resource manager",
        ]
        found = [s for s in services if s in text.lower()]
        return found

    def _build_rewrite_prompt(self, query: str, intent: str) -> str:
        """Constrói prompt para reescrita."""
        return f"""Reescreva a query para melhorar a busca em documentação OCI.

Query original: {query}
Intenção: {intent}

Reescreva de forma mais técnica e específica para OCI:"""

    def _build_expand_prompt(self, query: str, num: int) -> str:
        """Constrói prompt para expansão."""
        return f"""Gere {num} variações da query para busca em documentação OCI.

Query: {query}

Liste cada variação em uma linha:"""

    async def _generate(self, prompt: str) -> str:
        """Chama LLM para gerar."""
        if self.llm_client:
            return await self.llm_client.generate(prompt, [])
        # Fallback: return original
        return prompt

    def _add_to_cache(self, key: str, value: QueryExpansion) -> None:
        """Adiciona ao cache com LRU eviction."""
        if len(self._cache) >= self._cache_size:
            self._cache.popitem(last=False)
        self._cache[key] = value

    def clear_cache(self) -> None:
        """Limpa cache."""
        self._cache.clear()


def create_query_rewriter(llm_client: Any = None) -> QueryRewriterImpl:
    """Factory para criar QueryRewriter."""
    return QueryRewriterImpl(llm_client=llm_client)
