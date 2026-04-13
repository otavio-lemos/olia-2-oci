import pytest
from rag.splitter import create_oci_splitter, split_with_metadata
from langchain_core.documents import Document


def test_split_with_metadata():
    splitter = create_oci_splitter()
    docs = [
        Document(
            page_content="# Criar instância\n\n1. Login\n2. Selecionar compartment\n3. Criar instance",
            metadata={"domain": "compute"},
        )
    ]
    chunks = splitter.split_documents(docs)
    assert len(chunks) > 0
    assert chunks[0].metadata.get("domain") == "compute"
