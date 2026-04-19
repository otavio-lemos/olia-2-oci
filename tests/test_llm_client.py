"""Testes para LLM Client - TDD Task 1.1"""

import pytest
from unittest.mock import MagicMock


class TestLLMClientInterface:
    """Testes para interface Protocol do LLM Client."""

    def test_llm_protocol_has_generate_method(self):
        """Protocol deve ter método generate."""
        from rag.llm_client import LLMClient

        assert hasattr(LLMClient, "generate")

    def test_llm_protocol_has_stream_method(self):
        """Protocol deve ter método stream."""
        from rag.llm_client import LLMClient

        assert hasattr(LLMClient, "stream")


class TestMLXClient:
    """Testes para MLXClient."""

    @pytest.mark.asyncio
    async def test_mlx_generate_returns_string(self):
        """generate deve retornar string."""
        from rag.llm_client import MLXClient

        mock_model = MagicMock()
        mock_model.generate = MagicMock(return_value="test response")

        client = MLXClient(model=mock_model)
        result = await client.generate("prompt", [])

        assert isinstance(result, str)
        assert result == "test response"


class TestStreamingHandler:
    """Testes para StreamingHandler SSE."""

    def test_sse_format_correct(self):
        """SSE format deve ser válido."""
        from rag.llm_client import streaming_format

        result = streaming_format("test token", done=False)
        assert "data:" in result

    def test_sse_done_flag(self):
        """Done flag deve finalizar corretamente."""
        from rag.llm_client import streaming_format

        result = streaming_format("final", done=True)
        assert "final" in result
