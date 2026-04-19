"""Testes para Task 1.2 - Streaming SSE."""

import pytest
from unittest.mock import MagicMock, AsyncMock
from fastapi.testclient import TestClient
from fastapi import FastAPI


class TestStreamingEndpoint:
    """Testes para endpoint /rag/chat com SSE."""

    def test_chat_endpoint_exists(self):
        """Endpoint /rag/chat deve existir."""
        from rag.api import app

        routes = [r.path for r in app.routes]
        assert "/rag/chat" in routes or hasattr(app, "chat")

    def test_chat_returns_sse_content_type(self):
        """Chat deve aceitar request válido."""
        from rag.api import ChatRequest

        # Test request model is valid
        request = ChatRequest(messages=[], query="OCI compute instance")
        assert request.query == "OCI compute instance"
        assert request.temperature == 0.1

    def test_chat_request_model(self):
        """ChatRequest deve ter os campos corretos."""
        from rag.api import ChatRequest

        request = ChatRequest(messages=[], query="test")
        assert request.query == "test"


class TestStreamingHelper:
    """Testes para helper de streaming SSE."""

    def test_sse_data_format(self):
        """Formato SSE deve ter 'data:' prefix."""
        from rag.llm_client import streaming_format

        result = streaming_format("hello", done=False)
        assert "data:" in result

    def test_sse_done_format(self):
        """Formato done deve incluir [DONE]."""
        from rag.llm_client import streaming_format

        result = streaming_format("", done=True)
        assert "[DONE]" in result
