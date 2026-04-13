"""Document loaders para OCI."""

from typing import List, Iterator
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.documents import Document


class OCIDocsLoader(WebBaseLoader):
    """Loader para docs Oracle OCI."""

    def __init__(self, urls: List[str] = None):
        super().__init__(web_paths=urls or [])

    def load_with_metadata(self, metadata: dict) -> List[Document]:
        """Carrega docs com metadados enrichidos."""
        docs = self.load()
        for doc in docs:
            doc.metadata.update(metadata)
            doc.metadata.setdefault("source", "oracle_docs")
        return docs


class OCIWebLoader:
    """Loader para múltiplas URLs OCI."""

    def __init__(self, urls: List[str]):
        self.urls = urls

    def load(self) -> List[Document]:
        docs = []
        for url in self.urls:
            try:
                loader = OCIDocsLoader(urls=[url])
                docs.extend(
                    loader.load_with_metadata({"url": url, "doc_type": "oracle_docs"})
                )
            except Exception as e:
                print(f"Error loading {url}: {e}")
        return docs


# Default URLs para documentação OCI
DEFAULT_OCI_URLS = [
    "https://docs.oracle.com/en-us/iaas/Content/Compute/containers/overview.htm",
    "https://docs.oracle.com/en-us/iaas/Content/Network/VCNs/comprehensiv-overview.htm",
]


def load_oracle_docs(urls: List[str] = None, domain: str = "general") -> List[Document]:
    """Helper para carregar docs Oracle."""
    if not urls:
        urls = DEFAULT_OCI_URLS
    loader = OCIWebLoader(urls)
    docs = loader.load()
    for doc in docs:
        doc.metadata["domain"] = domain
    return docs
