import pytest
from rag.dense_retriever import create_dense_retriever
from rag.sparse_retriever import create_sparse_retriever
from rag.hybrid_retriever import create_hybrid_retriever, HybridRetrieverWithConfig
from langchain_core.documents import Document


def test_create_dense_retriever():
    docs = [Document(page_content="criar OCI compute instance", metadata={"id": 1})]
    retriever = create_dense_retriever(
        docs, embedding_model="sentence-transformers/all-MiniLM-L6-v2"
    )
    results = retriever.invoke("compute OCI")
    assert isinstance(results, list)


def test_create_sparse_retriever():
    docs = [Document(page_content="OCI compute instance shape", metadata={"id": 1})]
    retriever = create_sparse_retriever(docs)
    results = retriever.invoke("compute instance")
    assert isinstance(results, list)


def test_hybrid_retriever_rrf():
    docs = [Document(page_content="criar OCI compute instance", metadata={"id": 1})]
    dense = create_dense_retriever(docs)
    sparse = create_sparse_retriever(docs)
    hybrid = create_hybrid_retriever(dense, sparse, weights=[0.7, 0.3])
    results = hybrid.invoke("compute OCI")
    assert isinstance(results, list)


def test_hybrid_with_config():
    docs = [Document(page_content="test OCI", metadata={"id": 1})]
    dense = create_dense_retriever(docs)
    sparse = create_sparse_retriever(docs)
    hybrid = HybridRetrieverWithConfig(dense, sparse, config_name="migracao")
    config = hybrid.get_config()
    assert config["weights"] == [0.6, 0.4]
