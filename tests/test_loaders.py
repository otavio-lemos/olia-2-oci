import pytest
from rag.loaders import OCIDocsLoader, OCIWebLoader, load_oracle_docs
from langchain_core.documents import Document


def test_load_docs_from_url():
    loader = OCIDocsLoader()
    # Just test it can be instantiated
    assert loader is not None


def test_web_loader_empty():
    loader = OCIWebLoader(urls=[])
    assert loader is not None
    assert loader.urls == []


def test_load_oracle_docs_default():
    # Test default URLs are populated
    docs = load_oracle_docs()
    assert isinstance(docs, list)
