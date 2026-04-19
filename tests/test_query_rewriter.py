"""Testes para Task 2.1 - Query Rewriter module."""

import pytest
from unittest.mock import MagicMock, AsyncMock


class TestQueryRewriter:
    """Testes para QueryRewriter."""

    def test_query_rewriter_class_exists(self):
        """QueryRewriter deve existir."""
        from rag.query_rewriter import QueryRewriter

        assert QueryRewriter is not None

    def test_query_rewriter_has_rewrite_method(self):
        """Deve ter método rewrite."""
        from rag.query_rewriter import QueryRewriterImpl

        rewriter = QueryRewriterImpl(llm_client=MagicMock())
        assert hasattr(rewriter, "rewrite")

    def test_query_rewriter_has_expand_method(self):
        """Deve ter método expand."""
        from rag.query_rewriter import QueryRewriterImpl

        rewriter = QueryRewriterImpl(llm_client=MagicMock())
        assert hasattr(rewriter, "expand")

    @pytest.mark.asyncio
    async def test_rewrite_returns_expansion(self):
        """rewrite deve retornar QueryExpansion."""
        from rag.query_rewriter import QueryRewriterImpl

        mock_llm = MagicMock()
        mock_llm.generate = AsyncMock(return_value="enhanced query")

        rewriter = QueryRewriterImpl(llm_client=mock_llm)
        result = await rewriter.rewrite("how to create compute")

        assert "original" in result or "expanded" in result


class TestQueryExpansion:
    """Testes para tipo QueryExpansion."""

    def test_query_expansion_type(self):
        """TypedDict deve existir."""
        from rag.query_rewriter import QueryExpansion

        # Can create instance
        exp = QueryExpansion(
            original="test query",
            expanded=["variant1", "variant2"],
            intent="descoberta",
            entities=["compute"],
        )
        assert exp["original"] == "test query"
