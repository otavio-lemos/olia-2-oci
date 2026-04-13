"""Sparse retriever usando BM25."""

from typing import List
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document


def create_sparse_retriever(
    documents: List[Document],
    k: int = 40,
):
    """Cria sparse retriever com BM25."""
    if not documents:
        return None
    texts = [doc.page_content for doc in documents]
    metadatas = [doc.metadata for doc in documents]
    retriever = BM25Retriever.from_texts(texts, metadatas=metadatas)
    return retriever
