"""Document loaders para OCI."""

import re
from typing import List
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.documents import Document

OCI_SERVICES = [
    "Compute",
    "Database",
    "Networking",
    "Storage",
    "Functions",
    "Kubernetes",
    "Functions",
    "Analytics",
    "Data Science",
    "AI",
    "Logging",
    "Monitoring",
    "Notifications",
    "Events",
    "Resource Manager",
    "IAM",
    "Security",
    "Key Vault",
    "Vault",
    "DNS",
    "Email",
    "Content",
    "Object Storage",
    "Block Storage",
    "File Storage",
    "Archive Storage",
    "Virtual Cloud Network",
    "VCN",
    "Load Balancer",
    "DNS",
    "FastConnect",
]


def extract_oci_metadata(doc: Document, base_metadata: dict) -> dict:
    """Extrai metadados automaticamente do documento."""
    metadata = base_metadata.copy()
    content = doc.page_content.lower()

    for service in OCI_SERVICES:
        if service.lower() in content:
            metadata["service"] = service
            break

    if "tutorial" in content or "how-to" in content:
        metadata["category"] = "how-to"
    elif "reference" in content:
        metadata["category"] = "reference"
    elif "concepts" in content or "overview" in content:
        metadata["category"] = "guide"

    version_match = re.search(r"(\d+\.\d+)", doc.page_content)
    if version_match:
        metadata["version"] = version_match.group(1)

    return metadata


class OCIDocsLoader(WebBaseLoader):
    """Loader para docs Oracle OCI."""

    def __init__(self, urls: List[str] = None):
        super().__init__(web_paths=urls or [])

    def load_with_metadata(self, metadata: dict) -> List[Document]:
        """Carrega docs com metadados enrichidos."""
        docs = self.load()
        for doc in docs:
            extracted = extract_oci_metadata(doc, metadata)
            doc.metadata.update(extracted)
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
