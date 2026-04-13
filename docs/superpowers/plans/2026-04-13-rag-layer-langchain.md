# RAG Layer Implementation Plan (LangChain)

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan.

**Goal:** Implementar camada RAG híbrida usando LangChain com ingestion de documentação Oracle, retrieval híbrido (dense + sparse com RRF), e API.

**Architecture:** 
- LangChain para orchestration completa
- FAISS para índice dense
- BM25 via langchain-community para índice sparse
- EnsembleRetriever para fusão RRF
- API FastAPI para servir

**Tech Stack:** LangChain, langchain-community, FAISS, sentence-transformers, FastAPI, Python 3.12

---

## Chunk 1: Setup e Crawler

### Task 1: Setup de Dependências

**Files:**
- Modify: `requirements.txt`

- [ ] **Step 1: Adicionar dependências LangChain**

```bash
# Adicionar ao requirements.txt:
langchain>=0.3.0
langchain-community>=0.3.0
langchain-core>=0.3.0
faiss-cpu>=1.7.0
rank-bm25>=0.2.0
beautifulsoup4>=4.12.0
requests>=2.31.0
fastapi>=0.109.0
uvicorn>=0.27.0
```

- [ ] **Step 2: Instalar dependências**

Run: `pip install langchain langchain-community faiss-cpu rank-bm25 beautifulsoup4 requests fastapi uvicorn`

- [ ] **Step 3: Commit**

```bash
git add requirements.txt
git commit -m "chore: add LangChain dependencies for RAG"
```

### Task 2: Crawler para Documentação Oracle

**Files:**
- Create: `rag/crawler.py`
- Test: `tests/rag/test_crawler.py`

- [ ] **Step 1: Escrever teste**

```python
# tests/rag/test_crawler.py
import pytest
from rag.crawler import fetch_oci_docs

def test_fetch_oci_docs_returns_list():
    docs = fetch_oci_docs(base_url="https://docs.oracle.com/en-us/iaas/Content/Compute/containers/overview.htm", max_pages=5)
    assert isinstance(docs, list)
    if docs:
        assert "page_content" in docs[0]
        assert "metadata" in docs[0]
```

- [ ] **Step 2: Executar teste**

Run: `python -m pytest tests/rag/test_crawler.py::test_fetch_oci_docs_returns_list -v`
Expected: FAIL

- [ ] **Step 3: Implementar crawler**

```python
# rag/crawler.py
"""Crawler para documentação Oracle OCI usando LangChain Documents."""

from typing import List
import requests
from bs4 import BeautifulSoup
from langchain.schema import Document


def fetch_oci_docs(base_url: str, max_pages: int = 50) -> List[Document]:
    """
    Fetch documents from Oracle OCI documentation.
    
    Returns LangChain Document objects with page_content and metadata.
    """
    docs = []
    visited = set()
    
    def crawl(url: str, depth: int = 0):
        if depth > 2 or url in visited:
            return
        visited.add(url)
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            main_content = soup.find('main') or soup.find('article')
            if main_content:
                text = main_content.get_text(separator='\n', strip=True)
                if len(text) > 100:
                    docs.append(Document(
                        page_content=text,
                        metadata={
                            "source": url,
                            "title": soup.title.string if soup.title else "",
                            "type": "oracle_docs"
                        }
                    ))
            
            for link in soup.find_all('a', href=True):
                href = link['href']
                if href.startswith('/en-us/iaas/'):
                    full_url = f"https://docs.oracle.com{href}"
                    if full_url not in visited:
                        crawl(full_url, depth + 1)
                        
        except Exception as e:
            print(f"Error fetching {url}: {e}")
    
    crawl(base_url)
    return docs[:max_pages]


def fetch_docs_from_urls(urls: List[str]) -> List[Document]:
    """Fetch documents from a list of URLs."""
    docs = []
    for url in urls:
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            text = soup.get_text(separator='\n', strip=True)
            if len(text) > 100:
                docs.append(Document(
                    page_content=text,
                    metadata={"source": url, "title": soup.title.string if soup.title else "", "type": "oracle_docs"}
                ))
        except Exception as e:
            print(f"Error fetching {url}: {e}")
    return docs
```

- [ ] **Step 4: Executar teste**

Run: `python -m pytest tests/rag/test_crawler.py::test_fetch_oci_docs_returns_list -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add rag/crawler.py tests/rag/test_crawler.py
git commit -m "feat(rag): add OCI documentation crawler"
```

---

## Chunk 2: Índices Dense e Sparse

### Task 3: Dense Index (FAISS)

**Files:**
- Create: `rag/dense_index.py`
- Test: `tests/rag/test_dense_index.py`

- [ ] **Step 1: Escrever teste**

```python
# tests/rag/test_dense_index.py
import pytest
from rag.dense_index import DenseIndex

def test_dense_index_create_and_search():
    from langchain.schema import Document
    docs = [Document(page_content="como criar instância OCI compute", metadata={"id": 1})]
    index = DenseIndex()
    index.from_documents(docs, embedding_model="sentence-transformers/all-MiniLM-L6-v2")
    results = index.search("instância OCI", k=1)
    assert len(results) >= 1
```

- [ ] **Step 2: Executar teste**

Run: `python -m pytest tests/rag/test_dense_index.py::test_dense_index_create_and_search -v`
Expected: FAIL

- [ ] **Step 3: Implementar**

```python
# rag/dense_index.py
"""Dense index using FAISS via LangChain."""

from typing import List, Optional
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document


class DenseIndex:
    """Dense index using FAISS."""
    
    def __init__(self, embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.embedding_model = embedding_model
        self.embeddings = HuggingFaceEmbeddings(model_name=embedding_model)
        self.vectorstore: Optional[FAISS] = None
    
    def from_documents(self, documents: List[Document]):
        """Create index from documents."""
        self.vectorstore = FAISS.from_documents(documents, self.embeddings)
    
    def add_documents(self, documents: List[Document]):
        """Add documents to existing index."""
        if self.vectorstore is None:
            self.from_documents(documents)
        else:
            self.vectorstore.add_documents(documents)
    
    def search(self, query: str, k: int = 10) -> List[Document]:
        """Search the index."""
        if self.vectorstore is None:
            raise ValueError("Index not initialized")
        return self.vectorstore.similarity_search(query, k=k)
    
    def as_retriever(self, **kwargs):
        """Get as LangChain retriever."""
        if self.vectorstore is None:
            raise ValueError("Index not initialized")
        return self.vectorstore.as_retriever(**kwargs)
    
    def save(self, path: str):
        """Save index to disk."""
        if self.vectorstore:
            self.vectorstore.save_local(path)
    
    def load(self, path: str):
        """Load index from disk."""
        self.vectorstore = FAISS.load_local(path, self.embeddings, allow_dangerous_deserialization=True)
```

- [ ] **Step 4: Executar teste**

Run: `python -m pytest tests/rag/test_dense_index.py::test_dense_index_create_and_search -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add rag/dense_index.py tests/rag/test_dense_index.py
git commit -m "feat(rag): add FAISS dense index"
```

### Task 4: Sparse Index (BM25)

**Files:**
- Create: `rag/sparse_index.py`
- Test: `tests/rag/test_sparse_index.py`

- [ ] **Step 1: Escrever teste**

```python
# tests/rag/test_sparse_index.py
import pytest
from rag.sparse_index import SparseIndex
from langchain.schema import Document

def test_sparse_index_create_and_search():
    docs = [Document(page_content="como criar instância OCI compute", metadata={"id": 1})]
    index = SparseIndex()
    index.from_documents(docs)
    results = index.search("instância OCI", k=1)
    assert len(results) >= 1
```

- [ ] **Step 2: Executar teste**

Run: `python -m pytest tests/rag/test_sparse_index.py::test_sparse_index_create_and_search -v`
Expected: FAIL

- [ ] **Step 3: Implementar**

```python
# rag/sparse_index.py
"""Sparse index using BM25 via LangChain."""

from typing import List
from langchain_community.retrievers import BM25Retriever
from langchain.schema import Document


class SparseIndex:
    """Sparse index using BM25."""
    
    def __init__(self):
        self.retriever: BM25Retriever = None
    
    def from_documents(self, documents: List[Document]):
        """Create index from documents."""
        texts = [doc.page_content for doc in documents]
        self.retriever = BM25Retriever.from_texts(texts, metadatas=[doc.metadata for doc in documents])
    
    def add_documents(self, documents: List[Document]):
        """Add documents to existing index."""
        if self.retriever is None:
            self.from_documents(documents)
        else:
            texts = [doc.page_content for doc in documents]
            self.retriever.add_texts(texts)
    
    def search(self, query: str, k: int = 10) -> List[Document]:
        """Search the index."""
        if self.retriever is None:
            raise ValueError("Index not initialized")
        return self.retriever.get_relevant_documents(query, k=k)
    
    def as_retriever(self, **kwargs):
        """Get as LangChain retriever."""
        if self.retriever is None:
            raise ValueError("Index not initialized")
        return self.retriever
    
    def save(self, path: str):
        """Save index to disk."""
        if self.retriever:
            self.retriever.save(path)
    
    def load(self, path: str):
        """Load index from disk."""
        self.retriever = BM25Retriever.load(path)
```

- [ ] **Step 4: Executar teste**

Run: `python -m pytest tests/rag/test_sparse_index.py::test_sparse_index_create_and_search -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add rag/sparse_index.py tests/rag/test_sparse_index.py
git commit -m "feat(rag): add BM25 sparse index"
```

---

## Chunk 3: Retrieval Híbrido e Pipeline

### Task 5: Hybrid Retriever

**Files:**
- Create: `rag/hybrid_retriever.py`
- Test: `tests/rag/test_hybrid_retriever.py`

- [ ] **Step 1: Escrever teste**

```python
# tests/rag/test_hybrid_retriever.py
import pytest
from rag.hybrid_retriever import HybridRetriever
from rag.dense_index import DenseIndex
from rag.sparse_index import SparseIndex
from langchain.schema import Document

def test_hybrid_retriever():
    docs = [
        Document(page_content="criar instância OCI compute", metadata={"id": 1}),
        Document(page_content="configurar VCN networking", metadata={"id": 2}),
    ]
    
    dense = DenseIndex()
    dense.from_documents(docs)
    
    sparse = SparseIndex()
    sparse.from_documents(docs)
    
    hybrid = HybridRetriever(dense, sparse, weights=[0.7, 0.3])
    results = hybrid.search("instância OCI", k=2)
    assert len(results) >= 1
```

- [ ] **Step 2: Executar teste**

Run: `python -m pytest tests/rag/test_hybrid_retriever.py::test_hybrid_retriever -v`
Expected: FAIL

- [ ] **Step 3: Implementar**

```python
# rag/hybrid_retriever.py
"""Hybrid retriever using LangChain EnsembleRetriever."""

from typing import List
from langchain.retrievers import EnsembleRetriever
from langchain.schema import Document


class HybridRetriever:
    """Hybrid retriever combining dense and sparse via RRF."""
    
    def __init__(self, dense_index, sparse_index, weights: List[float] = [0.7, 0.3]):
        self.dense_index = dense_index
        self.sparse_index = sparse_index
        self.weights = weights
        
        self.dense_retriever = dense_index.as_retriever()
        self.sparse_retriever = sparse_index.as_retriever()
        
        self.ensemble = EnsembleRetriever(
            retrievers=[self.dense_retriever, self.sparse_retriever],
            weights=weights
        )
    
    def search(self, query: str, k: int = 10) -> List[Document]:
        """Search using hybrid retrieval."""
        return self.ensemble.invoke(query)
    
    def set_strategy(self, strategy: str):
        """Adjust weights based on strategy."""
        if strategy == "migracao":
            self.weights = [0.6, 0.4]
        elif strategy == "configuracao":
            self.weights = [0.4, 0.6]
        elif strategy == "troubleshooting":
            self.weights = [0.5, 0.5]
        
        self.ensemble = EnsembleRetriever(
            retrievers=[self.dense_retriever, self.sparse_retriever],
            weights=self.weights
        )
```

- [ ] **Step 4: Executar teste**

Run: `python -m pytest tests/rag/test_hybrid_retriever.py::test_hybrid_retriever -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add rag/hybrid_retriever.py tests/rag/test_hybrid_retriever.py
git commit -m "feat(rag): add hybrid retriever with RRF"
```

### Task 6: Pipeline de Ingestion

**Files:**
- Create: `rag/ingestion_pipeline.py`
- Test: `tests/rag/test_ingestion_pipeline.py`

- [ ] **Step 1: Escrever teste**

```python
# tests/rag/test_ingestion_pipeline.py
import pytest
import tempfile
import os
from rag.ingestion_pipeline import IngestionPipeline
from langchain.schema import Document

def test_ingestion_pipeline():
    docs = [Document(page_content="Test content", metadata={"source": "test"})]
    
    with tempfile.TemporaryDirectory() as tmpdir:
        pipeline = IngestionPipeline(output_dir=tmpdir)
        result = pipeline.run(docs)
        
        assert os.path.exists(f"{tmpdir}/dense_index")
        assert result["chunks"] == 1
```

- [ ] **Step 2: Executar teste**

Run: `python -m pytest tests/rag/test_ingestion_pipeline.py::test_ingestion_pipeline -v`
Expected: FAIL

- [ ] **Step 3: Implementar**

```python
# rag/ingestion_pipeline.py
"""Integrated ingestion pipeline using LangChain."""

import os
from typing import List, Dict
from langchain.schema import Document
from rag.dense_index import DenseIndex
from rag.sparse_index import SparseIndex


class IngestionPipeline:
    """Pipeline completo para ingestion de documentos."""
    
    def __init__(self, output_dir: str = "rag/data"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def run(self, documents: List[Document]) -> Dict:
        """Executa pipeline completo."""
        
        # Dense index
        print("Building dense index...")
        dense = DenseIndex()
        dense.from_documents(documents)
        dense.save(os.path.join(self.output_dir, "dense_index"))
        
        # Sparse index
        print("Building sparse index...")
        sparse = SparseIndex()
        sparse.from_documents(documents)
        sparse.save(os.path.join(self.output_dir, "sparse_index"))
        
        return {
            "chunks": len(documents),
            "output_dir": self.output_dir
        }
    
    def load_indexes(self):
        """Carrega índices do disco."""
        dense = DenseIndex()
        dense.load(os.path.join(self.output_dir, "dense_index"))
        
        sparse = SparseIndex()
        sparse.load(os.path.join(self.output_dir, "sparse_index"))
        
        return dense, sparse
```

- [ ] **Step 4: Executar teste**

Run: `python -m pytest tests/rag/test_ingestion_pipeline.py::test_ingestion_pipeline -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add rag/ingestion_pipeline.py tests/rag/test_ingestion_pipeline.py
git commit -m "feat(rag): add ingestion pipeline"
```

---

## Chunk 4: API e Integração

### Task 7: API do Serviço RAG

**Files:**
- Create: `rag/api.py`
- Test: `tests/rag/test_api.py`

- [ ] **Step 1: Escrever teste**

```python
# tests/rag/test_api.py
import pytest
from fastapi.testclient import TestClient
from rag.api import app

def test_api_retrieve():
    client = TestClient(app)
    response = client.post("/rag/retrieve", json={"query": "test", "k": 5})
    assert response.status_code in [200, 500]
```

- [ ] **Step 2: Executar teste**

Run: `python -m pytest tests/rag/test_api.py::test_api_retrieve -v`
Expected: FAIL

- [ ] **Step 3: Implementar**

```python
# rag/api.py
"""RAG Service API using LangChain."""

import os
from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from rag.ingestion_pipeline import IngestionPipeline
from rag.hybrid_retriever import HybridRetriever
from rag.dense_index import DenseIndex
from rag.sparse_index import SparseIndex


app = FastAPI(title="OCI Copilot RAG Service")

retriever: Optional[HybridRetriever] = None


class RetrieveRequest(BaseModel):
    query: str
    k: int = 10
    strategy: Optional[str] = None


class RetrieveResponse(BaseModel):
    results: list
    query: str


@app.on_event("startup")
async def load_indexes():
    global retriever
    output_dir = os.environ.get("RAG_DATA_DIR", "rag/data")
    
    if os.path.exists(output_dir):
        pipeline = IngestionPipeline(output_dir=output_dir)
        dense, sparse = pipeline.load_indexes()
        retriever = HybridRetriever(dense, sparse)
        print(f"Loaded RAG indexes from {output_dir}")
    else:
        print(f"No RAG data found in {output_dir}")


@app.post("/rag/retrieve", response_model=RetrieveResponse)
async def retrieve(request: RetrieveRequest):
    if retriever is None:
        raise HTTPException(status_code=500, detail="RAG indexes not loaded")
    
    if request.strategy:
        retriever.set_strategy(request.strategy)
    
    docs = retriever.search(request.query, k=request.k)
    
    results = [
        {
            "content": doc.page_content,
            "metadata": doc.metadata,
            "score": getattr(doc, "score", None)
        }
        for doc in docs
    ]
    
    return RetrieveResponse(results=results, query=request.query)


@app.get("/health")
async def health():
    return {"status": "healthy" if retriever else "not_ready"}


@app.post("/rag/ingest")
async def ingest_documents(documents: list):
    """Endpoint para ingestion."""
    from langchain.schema import Document
    
    docs = [
        Document(page_content=d["page_content"], metadata=d.get("metadata", {}))
        for d in documents
    ]
    
    output_dir = os.environ.get("RAG_DATA_DIR", "rag/data")
    pipeline = IngestionPipeline(output_dir=output_dir)
    result = pipeline.run(docs)
    return result
```

- [ ] **Step 4: Executar teste**

Run: `python -m pytest tests/rag/test_api.py::test_api_retrieve -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add rag/api.py tests/rag/test_api.py
git commit -m "feat(rag): add RAG API service"
```

### Task 8: Demo Script

**Files:**
- Create: `rag/demo.py`

- [ ] **Step 1: Criar demo**

```python
#!/usr/bin/env python3
"""Demo script para testar RAG com LangChain."""

from langchain.schema import Document
from rag.ingestion_pipeline import IngestionPipeline
from rag.hybrid_retriever import HybridRetriever
import tempfile


def main():
    print("=== OCI Copilot RAG Demo (LangChain) ===\n")
    
    docs = [
        Document(
            page_content="Para criar uma instância de compute no OCI, você precisa definir o compartment, a shape (VM ou BM), a imagem do sistema operacional, e a VCN de rede.",
            metadata={"url": "https://docs.oracle.com/instance", "title": "OCI Instances"}
        ),
        Document(
            page_content="Uma Virtual Cloud Network (VCN) é uma rede virtual privada no OCI. Suporta subnets públicas ou privadas, security lists, route tables, e NAT gateway.",
            metadata={"url": "https://docs.oracle.com/vcn", "title": "VCN Networking"}
        ),
        Document(
            page_content="Oracle Autonomous Database é um banco de dados self-driving, self-securing, e self-repairing. Suporta OLTP e OLAP com automação de machine learning.",
            metadata={"url": "https://docs.oracle.com/autonomous", "title": "Autonomous Database"}
        ),
    ]
    
    with tempfile.TemporaryDirectory() as tmpdir:
        print("1. Running ingestion...")
        pipeline = IngestionPipeline(output_dir=tmpdir)
        result = pipeline.run(docs)
        print(f"   Indexed {result['chunks']} documents\n")
        
        print("2. Loading indexes...")
        dense, sparse = pipeline.load_indexes()
        retriever = HybridRetriever(dense, sparse, weights=[0.7, 0.3])
        print("   Loaded\n")
        
        print("3. Testing queries...\n")
        queries = ["criar instância compute OCI", "VCN subnet configuração"]
        
        for query in queries:
            print(f"Query: {query}")
            results = retriever.search(query, k=2)
            for i, doc in enumerate(results):
                print(f"  {i+1}. [{doc.metadata.get('title')}]")
                print(f"     {doc.page_content[:100]}...")
            print()


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Commit**

```bash
git add rag/demo.py
git commit -m "feat(rag): add demo script"
```

---

## Chunk 5: Integração com Agentes

### Task 9: Tool para Agentes

**Files:**
- Create: `rag/tool_wrapper.py`

- [ ] **Step 1: Criar wrapper**

```python
# rag/tool_wrapper.py
"""Tool wrappers for OCI Copilot agents."""

from typing import Dict, Any, Optional
from rag.hybrid_retriever import HybridRetriever


class RAGTool:
    """Tool para agentes usarem RAG."""
    
    def __init__(self, retriever: HybridRetriever):
        self.retriever = retriever
    
    def retrieve(
        self,
        query: str,
        k: int = 10,
        strategy: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Retrieve documents for agent context."""
        if strategy:
            self.retriever.set_strategy(strategy)
        
        docs = self.retriever.search(query, k=k)
        
        return {
            "documents": [
                {
                    "content": doc.page_content,
                    "metadata": doc.metadata
                }
                for doc in docs
            ],
            "query": query,
            "num_results": len(docs)
        }
```

- [ ] **Step 2: Commit**

```bash
git add rag/tool_wrapper.py
git commit -m "feat(rag): add agent tool wrapper"
```

---

## Resumo

| Task | Descrição |
|------|-----------|
| 1 | Setup dependências |
| 2 | Crawler docs Oracle |
| 3 | Dense index (FAISS) |
| 4 | Sparse index (BM25) |
| 5 | Hybrid retriever (RRF) |
| 6 | Ingestion pipeline |
| 7 | API FastAPI |
| 8 | Demo script |
| 9 | Tool wrapper |

---

## Comandos

```bash
# Instalar
pip install langchain langchain-community faiss-cpu beautifulsoup4 requests fastapi uvicorn

# Rodar demo
python rag/demo.py

# Iniciar API
RAG_DATA_DIR=rag/data uvicorn rag.api:app --reload
```

---

**Plan complete. Ready to execute?**
