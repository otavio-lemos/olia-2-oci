"""Tools para agentes LangChain."""

from typing import Optional, List, Dict, Any, Callable


class RAGTool:
    """Tool de retrieve para agentes."""

    name: str = "rag_retrieve"
    description: str = (
        "Recupera documentos da documentação OCI. Use para perguntas sobre OCI."
    )

    def __init__(self, retriever, agent_config: Dict[str, Any]):
        self.retriever = retriever
        self.agent_config = agent_config

    def invoke(
        self, query: str, k: int = 10, strategy: str = None, filters: dict = None
    ) -> str:
        if strategy and hasattr(self.retriever, "set_strategy"):
            self.retriever.set_strategy(strategy)

        docs = self.retriever.invoke(query)

        if filters:
            docs = [
                d
                for d in docs
                if all(d.metadata.get(fk) == fv for fk, fv in filters.items())
            ]

        docs = docs[:k]

        return "\n\n".join(
            [
                f"## {i + 1}. {d.metadata.get('title', 'Document')}\n{d.page_content[:500]}"
                for i, d in enumerate(docs)
            ]
        )

    def __call__(self, query: str, k: int = 10) -> str:
        return self.invoke(query, k=k)


def create_rag_tool(retriever, agent_config: Dict[str, Any]) -> RAGTool:
    """Factory para criar RAG tool."""
    return RAGTool(retriever=retriever, agent_config=agent_config)
