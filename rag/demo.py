#!/usr/bin/env python3
"""Demo script para testar RAG."""

from rag.loaders import load_oracle_docs
from rag.splitter import split_with_metadata
from rag.dense_retriever import create_dense_retriever
from rag.sparse_retriever import create_sparse_retriever
from rag.hybrid_retriever import HybridRetrieverWithConfig


def main():
    print("=== OCI Copilot RAG Demo (LangChain) ===\n")

    # 1. Load docs
    print("1. Loading docs...")
    docs = load_oracle_docs()
    print(f"   Loaded {len(docs)} docs\n")

    # 2. Split
    print("2. Splitting...")
    chunks = split_with_metadata(docs)
    print(f"   Created {len(chunks)} chunks\n")

    # 3. Create retrievers
    print("3. Creating retrievers...")
    dense = create_dense_retriever(chunks)
    sparse = create_sparse_retriever(chunks)
    hybrid = HybridRetrieverWithConfig(dense, sparse)
    print("   Done\n")

    # 4. Test queries
    print("4. Testing queries...\n")
    queries = [
        "criar instância compute OCI",
    ]

    for query in queries:
        print(f"Query: {query}")
        try:
            results = hybrid.invoke(query)
            for i, doc in enumerate(results[:3]):
                print(f"  {i + 1}. {doc.page_content[:100]}...")
        except Exception as e:
            print(f"  Error: {e}")
        print()


if __name__ == "__main__":
    main()
