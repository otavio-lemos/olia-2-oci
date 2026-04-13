"""Text splitters para OCI."""

from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter


def create_oci_splitter(chunk_size: int = 1000, chunk_overlap: int = 100):
    """Cria splitter otimizado para docs OCI."""
    return RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=[
            "\n## ",
            "\n### ",
            "\n\n",
            "\n",
            ". ",
            " ",
            "",
        ],
        keep_separator=True,
    )


def split_with_metadata(documents, **kwargs):
    """Split documents preservando metadados."""
    splitter = create_oci_splitter(**kwargs)
    return splitter.split_documents(documents)
