import pytest
from rag.tools import create_rag_tool, RAGTool


def test_create_rag_tool():
    class MockRetriever:
        def invoke(self, query):
            return []

        def set_strategy(self, strategy):
            pass

    tool = create_rag_tool(MockRetriever(), agent_config={"rag_strategy": "hybrid"})
    assert tool.name == "rag_retrieve"


def test_rag_tool_invoke():
    class MockDoc:
        page_content = "test content"
        metadata = {"title": "Test"}

    class MockRetriever:
        def invoke(self, query):
            return [MockDoc()]

        def set_strategy(self, strategy):
            pass

    tool = create_rag_tool(MockRetriever(), agent_config={})
    result = tool.invoke("test query")
    assert "test content" in result
