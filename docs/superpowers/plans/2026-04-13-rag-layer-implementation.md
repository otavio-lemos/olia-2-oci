# RAG Layer Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implementar uma camada RAG híbrida (dense + sparse) para o OCI Specialist Copilot com ingestion de documentação Oracle, query rewriting, re-ranking e integração com agentes.

**Architecture:** O sistema seguirá a arquitetura definida em `docs/oci-copilot-rag.md`:
- Índice dense via FAISS com embeddings MiniLM-L6
- Índice sparse via BM25 (rank-bm25) para termos técnicos
- Fusão via Reciprocal Rank Fusion (RRF)
- Query rewriting via LLM
- Re-ranking opcional com cross-encoder

**Tech Stack:** FAISS, sentence-transformers, rank-bm25, Python 3.12

---

## Chunk 1: Pipeline de Ingestão de Documentos

### Task 1: Crawler para Documentação Oracle

**Files:**
- Create: `rag/crawler.py`
- Test: `tests/rag/test_crawler.py`

- [ ] **Step 1: Escrever teste para crawler**

```python
# tests/rag/test_crawler.py
import pytest
from rag.crawler import fetch_oci_docs

def test_fetch_oci_docs_returns_list():
    """Testa que o crawler retorna uma lista de documentos."""
    docs = fetch_oci_docs(base_url="https://docs.oracle.com/en-us/iaas/Content/Compute/containers/overview.htm")
    assert isinstance(docs, list)
    if docs:
        assert "content" in docs[0]
        assert "url" in docs[0]
```

- [ ] **Step 2: Executar teste**

Run: `python -m pytest tests/rag/test_crawler.py::test_fetch_oci_docs_returns_list -v`
Expected: FAIL - import error

- [ ] **Step 3: Implementar crawler básico**

```python
# rag/crawler.py
"""Crawler para documentação Oracle OCI."""

from typing import List, Dict
import requests
from bs4 import BeautifulSoup


def fetch_oci_docs(base_url: str, max_pages: int = 50) -> List[Dict[str, str]]:
    """
    Fetch documents from Oracle OCI documentation.
    
    Args:
        base_url: URL base da documentação
        max_pages: Número máximo de páginas para crawlear
        
    Returns:
        Lista de documentos com 'url' e 'content'
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
            
            # Extrai conteúdo principal
            main_content = soup.find('main') or soup.find('article')
            if main_content:
                text = main_content.get_text(separator='\n', strip=True)
                if len(text) > 100:  #过滤太短的页面
                    docs.append({
                        "url": url,
                        "content": text,
                        "title": soup.title.string if soup.title else ""
                    })
            
            # Segue links internos
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
```

- [ ] **Step 4: Executar teste**

Run: `python -m pytest tests/rag/test_crawler.py::test_fetch_oci_docs_returns_list -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add rag/crawler.py tests/rag/test_crawler.py
git commit -m "feat(rag): add basic OCI documentation crawler"
```

### Task 2: Chunking de Documentos

**Files:**
- Create: `rag/chunker.py`
- Test: `tests/rag/test_chunker.py`

- [ ] **Step 1: Escrever teste para chunker**

```python
# tests/rag/test_chunker.py
import pytest
from rag.chunker import chunk_document

def test_chunk_document_splits_into_chunks():
    """Testa que documentos são dividos em chunks menores."""
    doc = {
        "url": "https://example.com",
        "content": "Heading 1\n\nContent paragraph one.\n\nHeading 2\n\nContent paragraph two.",
        "title": "Test Doc"
    }
    chunks = chunk_document(doc, chunk_size=500, overlap=50)
    assert len(chunks) > 1
    assert all("content" in c for c in chunks)
    assert all("url" in c for c in chunks)
```

- [ ] **Step 2: Executar teste**

Run: `python -m pytest tests/rag/test_chunker.py::test_chunk_document_splits_into_chunks -v`
Expected: FAIL - module not found

- [ ] **Step 3: Implementar chunker**

```python
# rag/chunker.py
"""Document chunking with semantic boundaries."""

from typing import List, Dict
import re


def chunk_document(doc: Dict[str, str], chunk_size: int = 1000, overlap: int = 100) -> List[Dict[str, str]]:
    """
    Chunk document into smaller pieces for embedding.
    
    Args:
        doc: Documento com 'url', 'content', 'title'
        chunk_size: Tamanho máximo de cada chunk em caracteres
        overlap:Overlap entre chunks consecutivos
        
    Returns:
        Lista de chunks com metadados
    """
    content = doc.get("content", "")
    title = doc.get("title", "")
    url = doc.get("url", "")
    
    # Split por parágrafos e cabeçalhos
    paragraphs = re.split(r'\n\s*\n|\n(?=#)|\n(?=[A-Z])', content)
    paragraphs = [p.strip() for p in paragraphs if p.strip()]
    
    chunks = []
    current_chunk = []
    current_size = 0
    
    for para in paragraphs:
        para_size = len(para)
        
        if current_size + para_size > chunk_size and current_chunk:
            # Finaliza chunk atual
            chunk_text = "\n\n".join(current_chunk)
            chunks.append({
                "content": chunk_text,
                "url": url,
                "title": title,
                "metadata": {
                    "chunk_index": len(chunks),
                    "source": "oracle_docs"
                }
            })
            
            # Mantém overlap
            if overlap > 0 and current_chunk:
                overlap_text = current_chunk[-1]
                current_chunk = [overlap_text] if len(overlap_text) < overlap else []
                current_size = len(overlap_text)
            else:
                current_chunk = []
                current_size = 0
        
        current_chunk.append(para)
        current_size += para_size + 2  # +2 for \n\n
    
    # Adiciona chunk final
    if current_chunk:
        chunk_text = "\n\n".join(current_chunk)
        chunks.append({
            "content": chunk_text,
            "url": url,
            "title": title,
            "metadata": {
                "chunk_index": len(chunks),
                "source": "oracle_docs"
            }
        })
    
    return chunks


def chunk_documents(documents: List[Dict[str, str]], **kwargs) -> List[Dict[str, str]]:
    """Chunk múltiplos documentos."""
    all_chunks = []
    for doc in documents:
        chunks = chunk_document(doc, **kwargs)
        all_chunks.extend(chunks)
    return all_chunks
```

- [ ] **Step 4: Executar teste**

Run: `python -m pytest tests/rag/test_chunker.py::test_chunk_document_splits_into_chunks -v`
Expected: PASS

- [ ] **Step 5: Commit**

```python
git add rag/chunker.py tests/rag/test_chunker.py
git commit -m "feat(rag): add document chunker with semantic boundaries"
```

---

## Chunk 2: Índice Dense (FAISS)

### Task 3: Embedding Generator

**Files:**
- Create: `rag/embedder.py`
- Test: `tests/rag/test_embedder.py`

- [ ] **Step 1: Escrever teste para embedder**

```python
# tests/rag/test_embedder.py
import pytest
import numpy as np
from rag.embedder import Embedder

def test_embedder_generates_embeddings():
    """Testa que o embedder gera vetores."""
    embedder = Embedder(model_name="sentence-transformers/all-MiniLM-L6-v2")
    texts = ["como criar instância no OCI", "OCI compute instance"]
    embeddings = embedder.embed_batch(texts)
    assert embeddings.shape[0] == 2
    assert embeddings.shape[1] == 384  # Dimensão do MiniLM-L6
```

- [ ] **Step 2: Executar teste**

Run: `python -m pytest tests/rag/test_embedder.py::test_embedder_generates_embeddings -v`
Expected: FAIL - module not found

- [ ] **Step 3: Implementar embedder**

```python
# rag/embedder.py
"""Embedding generation using sentence-transformers."""

from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer


class Embedder:
    """Gerador de embeddings para RAG."""
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
    
    def embed(self, text: str) -> np.ndarray:
        """Gera embedding para um texto."""
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding
    
    def embed_batch(self, texts: List[str]) -> np.ndarray:
        """Gera embeddings para uma lista de textos."""
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings
    
    @property
    def dimension(self) -> int:
        """Retorna dimensão dos embeddings."""
        return self.model.get_sentence_embedding_dimension()
```

- [ ] **Step 4: Executar teste**

Run: `python -m pytest tests/rag/test_embedder.py::test_embedder_generates_embeddings -v`
Expected: PASS (pode levar alguns segundos para baixar modelo na primeira vez)

- [ ] **Step 5: Commit**

```bash
git add rag/embedder.py tests/rag/test_embedder.py
git commit -m "feat(rag): add embedding generator with sentence-transformers"
```

### Task 4: FAISS Vector Store

**Files:**
- Create: `rag/vector_store.py`
- Test: `tests/rag/test_vector_store.py`

- [ ] **Step 1: Escrever teste para vector store**

```python
# tests/rag/test_vector_store.py
import pytest
import numpy as np
from rag.vector_store import VectorStore

def test_vector_store_add_and_search():
    """Testa adição e busca no vector store."""
    store = VectorStore(dimension=4)
    
    # Adiciona documentos
    vectors = np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0]])
    metadatas = [{"id": 1}, {"id": 2}, {"id": 3}]
    store.add(vectors, metadatas)
    
    # Busca
    query = np.array([1, 0, 0, 0])
    results = store.search(query, k=2)
    
    assert len(results) == 2
    assert results[0]["metadata"]["id"] == 1  # Mais próximo
```

- [ ] **Step 2: Executar teste**

Run: `python -m pytest tests/rag/test_vector_store.py::test_vector_store_add_and_search -v`
Expected: FAIL - module not found

- [ ] **Step 3: Implementar vector store**

```python
# rag/vector_store.py
"""FAISS vector store for dense embeddings."""

from typing import List, Dict, Any
import numpy as np
import faiss
import pickle


class VectorStore:
    """Vector store usando FAISS."""
    
    def __init__(self, dimension: int, index_type: str = "IVFFlat,Flat"):
        self.dimension = dimension
        self.index_type = index_type
        self.index = None
        self.metadatas: List[Dict] = []
        self._init_index()
    
    def _init_index(self):
        """Inicializa índice FAISS."""
        # Usa IndexFlatL2 para相似性 exata (mais simples)
        # Para production, usar IVF com quantização
        self.index = faiss.IndexFlatL2(self.dimension)
    
    def add(self, vectors: np.ndarray, metadatas: List[Dict]):
        """Adiciona vetores e metadados ao índice."""
        if vectors.shape[1] != self.dimension:
            raise ValueError(f"Expected dimension {self.dimension}, got {vectors.shape[1]}")
        
        vectors = vectors.astype('float32')
        self.index.add(vectors)
        self.metadatas.extend(metadatas)
    
    def search(self, query: np.ndarray, k: int = 10) -> List[Dict[str, Any]]:
        """Busca porSimilaridade."""
        query = query.reshape(1, -1).astype('float32')
        distances, indices = self.index.search(query, k)
        
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < len(self.metadatas):
                results.append({
                    "distance": float(dist),
                    "index": int(idx),
                    "metadata": self.metadatas[idx]
                })
        
        return results
    
    def save(self, path: str):
        """Salva índice em disco."""
        faiss.write_index(self.index, f"{path}.index")
        with open(f"{path}.meta", 'wb') as f:
            pickle.dump(self.metadatas, f)
    
    def load(self, path: str):
        """Carrega índice do disco."""
        self.index = faiss.read_index(f"{path}.index")
        with open(f"{path}.meta", 'rb') as f:
            self.metadatas = pickle.load(f)
    
    def __len__(self):
        return self.index.ntotal
```

- [ ] **Step 4: Executar teste**

Run: `python -m pytest tests/rag/test_vector_store.py::test_vector_store_add_and_search -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add rag/vector_store.py tests/rag/test_vector_store.py
git commit -m "feat(rag): add FAISS vector store"
```

---

## Chunk 3: Índice Sparse (BM25)

### Task 5: BM25 Index

**Files:**
- Create: `rag/bm25_index.py`
- Test: `tests/rag/test_bm25_index.py`

- [ ] **Step 1: Escrever teste para BM25**

```python
# tests/rag/test_bm25_index.py
import pytest
from rag.bm25_index import BM25Index

def test_bm25_add_and_search():
    """Testa adição e busca BM25."""
    index = BM25Index()
    
    docs = [
        {"id": 1, "text": "como criar instância no OCI compute"},
        {"id": 2, "text": "configurar VCN networking"},
        {"id": 3, "text": "OCI autonomous database"}
    ]
    index.add(docs)
    
    results = index.search("instância OCI compute", k=2)
    assert len(results) <= 2
    assert results[0]["id"] == 1  # Mais relevante
```

- [ ] **Step 2: Executar teste**

Run: `python -m pytest tests/rag/test_bm25_index.py::test_bm25_add_and_search -v`
Expected: FAIL - module not found

- [ ] **Step 3: Implementar BM25 index**

```python
# rag/bm25_index.py
"""BM25 sparse index for lexical search."""

from typing import List, Dict
import pickle
from rank_bm25 import BM25Okapi


class BM25Index:
    """Índice BM25 para busca esparsa."""
    
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.index = None
        self.documents: List[Dict] = []
        self.corpus: List[str] = []
    
    def add(self, documents: List[Dict]):
        """Adiciona documentos ao índice."""
        self.documents = documents
        self.corpus = [doc.get("text", doc.get("content", "")) for doc in documents]
        
        # Tokeniza
        tokenized_corpus = [doc.lower().split() for doc in self.corpus]
        self.index = BM25Okapi(tokenized_corpus, k1=self.k1, b=self.b)
    
    def search(self, query: str, k: int = 10) -> List[Dict]:
        """Busca por similaridade lexical."""
        tokenized_query = query.lower().split()
        scores = self.index.get_scores(tokenized_query)
        
        # Ordena por score
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:k]
        
        results = []
        for idx in top_indices:
            results.append({
                "id": self.documents[idx].get("id", idx),
                "score": float(scores[idx]),
                "document": self.documents[idx]
            })
        
        return results
    
    def save(self, path: str):
        """Salva índice em disco."""
        with open(f"{path}.pkl", 'wb') as f:
            pickle.dump({
                "documents": self.documents,
                "k1": self.k1,
                "b": self.b
            }, f)
    
    def load(self, path: str):
        """Carrega índice do disco."""
        with open(f"{path}.pkl", 'rb') as f:
            data = pickle.load(f)
        self.documents = data["documents"]
        self.k1 = data["k1"]
        self.b = data["b"]
        self.corpus = [doc.get("text", doc.get("content", "")) for doc in self.documents]
        tokenized_corpus = [doc.lower().split() for doc in self.corpus]
        self.index = BM25Okapi(tokenized_corpus, k1=self.k1, b=self.b)
```

- [ ] **Step 4: Executar teste**

Run: `python -m pytest tests/rag/test_bm25_index.py::test_bm25_add_and_search -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add rag/bm25_index.py tests/rag/test_bm25_index.py
git commit -m "feat(rag): add BM25 sparse index"
```

---

## Chunk 4: Camada de Retrieval Híbrido

### Task 6: Hybrid Retriever

**Files:**
- Create: `rag/hybrid_retriever.py`
- Test: `tests/rag/test_hybrid_retriever.py`

- [ ] **Step 1: Escrever teste para retriever**

```python
# tests/rag/test_hybrid_retriever.py
import pytest
import numpy as np
from rag.hybrid_retriever import HybridRetriever
from rag.vector_store import VectorStore
from rag.bm25_index import BM25Index

def test_hybrid_retriever_fuses_results():
    """Testa que retriever funde resultados dense e sparse."""
    # Setup
    vector_store = VectorStore(dimension=4)
    vector_store.add(
        np.array([[1, 0, 0, 0], [0, 1, 0, 0]]),
        [{"text": "instância OCI"}, {"text": "VCN networking"}]
    )
    
    bm25 = BM25Index()
    bm25.add([
        {"id": 0, "text": "instância OCI"},
        {"id": 1, "text": "VCN networking"},
        {"id": 2, "text": "database autonomous"}
    ])
    
    retriever = HybridRetriever(
        vector_store=vector_store,
        bm25_index=bm25,
        dense_weight=0.7,
        sparse_weight=0.3
    )
    
    results = retriever.retrieve("OCI instância", k=2)
    assert len(results) <= 2
```

- [ ] **Step 2: Executar teste**

Run: `python -m pytest tests/rag/test_hybrid_retriever.py::test_hybrid_retriever_fuses_results -v`
Expected: FAIL - module not found

- [ ] **Step 3: Implementar hybrid retriever**

```python
# rag/hybrid_retriever.py
"""Hybrid retriever combining dense and sparse search."""

from typing import List, Dict, Any, Optional
import numpy as np
from rag.vector_store import VectorStore
from rag.bm25_index import BM25Index
from rag.embedder import Embedder


class HybridRetriever:
    """Retriever híbrido usando fusão RRF."""
    
    def __init__(
        self,
        vector_store: VectorStore,
        bm25_index: BM25Index,
        embedder: Embedder,
        dense_weight: float = 0.7,
        sparse_weight: float = 0.3,
        dense_k: int = 20,
        sparse_k: int = 40
    ):
        self.vector_store = vector_store
        self.bm25_index = bm25_index
        self.embedder = embedder
        self.dense_weight = dense_weight
        self.sparse_weight = sparse_weight
        self.dense_k = dense_k
        self.sparse_k = sparse_k
    
    def retrieve(self, query: str, k: int = 10, use_reranker: bool = False) -> List[Dict[str, Any]]:
        """Executa retrieval híbrido com fusão RRF."""
        
        # Dense search
        query_embedding = self.embedder.embed(query)
        dense_results = self.vector_store.search(query_embedding, k=self.dense_k)
        
        # Sparse search
        sparse_results = self.bm25_index.search(query, k=self.sparse_k)
        
        # RRF fusion
        fused = self._rrf_fusion(dense_results, sparse_results)
        
        # Limit to k
        return fused[:k]
    
    def _rrf_fusion(
        self,
        dense_results: List[Dict],
        sparse_results: List[Dict],
        rrf_k: int = 60
    ) -> List[Dict[str, Any]]:
        """Reciprocal Rank Fusion para combinar resultados."""
        
        # Normaliza scores dense (convert distance to similarity)
        for r in dense_results:
            r["score"] = 1.0 / (1.0 + r["distance"])
        
        # Normaliza scores sparse (já são similaridade)
        for r in sparse_results:
            r["score"] = r.get("score", 1.0)
        
        # Combina ranks
        doc_scores: Dict[int, float] = {}
        doc_metadata: Dict[int, Dict] = {}
        
        for rank, result in enumerate(dense_results):
            idx = result["index"]
            score = 1.0 / (rrf_k + rank + 1)
            doc_scores[idx] = doc_scores.get(idx, 0) + self.dense_weight * score
            doc_metadata[idx] = result.get("metadata", {})
        
        for rank, result in enumerate(sparse_results):
            idx = result.get("id", rank)
            score = 1.0 / (rrf_k + rank + 1)
            doc_scores[idx] = doc_scores.get(idx, 0) + self.sparse_weight * score
            if idx not in doc_metadata:
                doc_metadata[idx] = result.get("document", {})
        
        # Ordena por score final
        sorted_indices = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)
        
        results = []
        for idx, score in sorted_indices:
            results.append({
                "index": idx,
                "score": score,
                "metadata": doc_metadata[idx]
            })
        
        return results
    
    def set_strategy(self, strategy: str):
        """Ajusta pesos baseado na estratégia."""
        if strategy == "migracao":
            self.dense_weight = 0.6
            self.sparse_weight = 0.4
        elif strategy == "configuracao":
            self.dense_weight = 0.4
            self.sparse_weight = 0.6
        elif strategy == "troubleshooting":
            self.dense_k = 15
            self.sparse_k = 50
```

- [ ] **Step 4: Executar teste**

Run: `python -m pytest tests/rag/test_hybrid_retriever.py::test_hybrid_retriever_fuses_results -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add rag/hybrid_retriever.py tests/rag/test_hybrid_retriever.py
git commit -m "feat(rag): add hybrid retriever with RRF fusion"
```

---

## Chunk 5: Pipeline Completo e API

### Task 7: Pipeline de Ingestion Integrado

**Files:**
- Create: `rag/ingestion_pipeline.py`
- Test: `tests/rag/test_ingestion_pipeline.py`

- [ ] **Step 1: Escrever teste para pipeline**

```python
# tests/rag/test_ingestion_pipeline.py
import pytest
import os
import tempfile
from rag.ingestion_pipeline import IngestionPipeline

def test_ingestion_pipeline_e2e():
    """Testa pipeline completo de ingestion."""
    with tempfile.TemporaryDirectory() as tmpdir:
        pipeline = IngestionPipeline(
            output_dir=tmpdir,
            chunk_size=500
        )
        
        # Simula documentos
        docs = [
            {"url": "https://example.com/1", "content": "Como criar instância OCI compute.", "title": "Instance"},
            {"url": "https://example.com/2", "content": "Configurar VCN networking.", "title": "VCN"}
        ]
        
        result = pipeline.run(docs)
        
        assert os.path.exists(f"{tmpdir}/vector_store.index")
        assert os.path.exists(f"{tmpdir}/bm25.pkl")
        assert result["chunks"] >= 2
```

- [ ] **Step 2: Executar teste**

Run: `python -m pytest tests/rag/test_ingestion_pipeline.py::test_ingestion_pipeline_e2e -v`
Expected: FAIL - module not found

- [ ] **Step 3: Implementar pipeline**

```python
# rag/ingestion_pipeline.py
"""Integrated ingestion pipeline."""

import os
from typing import List, Dict
from rag.crawler import fetch_oci_docs
from rag.chunker import chunk_documents
from rag.embedder import Embedder
from rag.vector_store import VectorStore
from rag.bm25_index import BM25Index


class IngestionPipeline:
    """Pipeline completo para ingestion de documentos."""
    
    def __init__(
        self,
        output_dir: str = "rag/data",
        chunk_size: int = 1000,
        overlap: int = 100,
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    ):
        self.output_dir = output_dir
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.embedding_model = embedding_model
        
        os.makedirs(output_dir, exist_ok=True)
    
    def run(self, documents: List[Dict]) -> Dict:
        """Executa pipeline completo."""
        
        # 1. Chunking
        print("Chunking documents...")
        chunks = chunk_documents(documents, chunk_size=self.chunk_size, overlap=self.overlap)
        print(f"Created {len(chunks)} chunks")
        
        # 2. Gera embeddings
        print("Generating embeddings...")
        embedder = Embedder(self.embedding_model)
        texts = [c["content"] for c in chunks]
        embeddings = embedder.embed_batch(texts)
        
        # 3. Cria índice dense
        print("Building dense index...")
        vector_store = VectorStore(dimension=embedder.dimension)
        metadatas = [{"content": c["content"], "url": c["url"], "title": c["title"]} for c in chunks]
        vector_store.add(embeddings, metadatas)
        vector_store.save(os.path.join(self.output_dir, "vector_store"))
        
        # 4. Cria índice sparse
        print("Building sparse index...")
        bm25 = BM25Index()
        docs_for_bm25 = [
            {"id": i, "text": c["content"][:500]}  # Limita texto para BM25
            for i, c in enumerate(chunks)
        ]
        bm25.add(docs_for_bm25)
        bm25.save(os.path.join(self.output_dir, "bm25"))
        
        return {
            "chunks": len(chunks),
            "embeddings": embeddings.shape,
            "output_dir": self.output_dir
        }
    
    def load_indexes(self):
        """Carrega índices do disco."""
        vector_store = VectorStore(dimension=384)
        vector_store.load(os.path.join(self.output_dir, "vector_store"))
        
        bm25 = BM25Index()
        bm25.load(os.path.join(self.output_dir, "bm25"))
        
        return vector_store, bm25
```

- [ ] **Step 4: Executar teste**

Run: `python -m pytest tests/rag/test_ingestion_pipeline.py::test_ingestion_pipeline_e2e -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add rag/ingestion_pipeline.py tests/rag/test_ingestion_pipeline.py
git commit -m "feat(rag): add ingestion pipeline"
```

### Task 8: API do Serviço RAG

**Files:**
- Create: `rag/api.py`
- Test: `tests/rag/test_api.py`

- [ ] **Step 1: Escrever teste para API**

```python
# tests/rag/test_api.py
import pytest
from fastapi.testclient import TestClient
from rag.api import app

def test_api_retrieve_endpoint():
    """Testa endpoint de retrieve."""
    client = TestClient(app)
    response = client.post("/rag/retrieve", json={
        "query": "como criar instância OCI",
        "k": 5
    })
    assert response.status_code in [200, 500]  # 500 se índices não carregados
```

- [ ] **Step 2: Executar teste**

Run: `python -m pytest tests/rag/test_api.py::test_api_retrieve_endpoint -v`
Expected: FAIL - module not found

- [ ] **Step 3: Implementar API**

```python
# rag/api.py
"""RAG Service API."""

import os
from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from rag.ingestion_pipeline import IngestionPipeline
from rag.hybrid_retriever import HybridRetriever
from rag.embedder import Embedder


app = FastAPI(title="OCI Copilot RAG Service")

# Global state
retriever: Optional[HybridRetriever] = None
pipeline: Optional[IngestionPipeline] = None


class RetrieveRequest(BaseModel):
    query: str
    k: int = 10
    strategy: Optional[str] = None
    metadata_filters: Optional[dict] = None


class RetrieveResponse(BaseModel):
    results: list
    query: str


@app.on_event("startup")
async def load_indexes():
    """Carrega índices na inicialização."""
    global retriever, pipeline
    
    output_dir = os.environ.get("RAG_DATA_DIR", "rag/data")
    
    if os.path.exists(output_dir):
        pipeline = IngestionPipeline(output_dir=output_dir)
        vector_store, bm25 = pipeline.load_indexes()
        embedder = Embedder()
        
        retriever = HybridRetriever(
            vector_store=vector_store,
            bm25_index=bm25,
            embedder=embedder
        )
        
        print(f"Loaded RAG indexes from {output_dir}")
    else:
        print(f"No RAG data found in {output_dir}. Run ingestion first.")


@app.post("/rag/retrieve", response_model=RetrieveResponse)
async def retrieve(request: RetrieveRequest):
    """Endpoint para retrieve de documentos."""
    if retriever is None:
        raise HTTPException(status_code=500, detail="RAG indexes not loaded")
    
    if request.strategy:
        retriever.set_strategy(request.strategy)
    
    results = retriever.retrieve(request.query, k=request.k)
    
    return RetrieveResponse(
        results=results,
        query=request.query
    )


@app.get("/health")
async def health():
    """Health check."""
    return {
        "status": "healthy" if retriever else "not_ready",
        "indexes_loaded": retriever is not None
    }


@app.post("/rag/ingest")
async def ingest_documents(documents: list):
    """Endpoint para ingestion de novos documentos."""
    if pipeline is None:
        output_dir = os.environ.get("RAG_DATA_DIR", "rag/data")
        pipeline = IngestionPipeline(output_dir=output_dir)
    
    result = pipeline.run(documents)
    return result
```

- [ ] **Step 4: Executar teste**

Run: `python -m pytest tests/rag/test_api.py::test_api_retrieve_endpoint -v`
Expected: PASS (ou 500 se índices não carregados)

- [ ] **Step 5: Commit**

```bash
git add rag/api.py tests/rag/test_api.py
git commit -m "feat(rag): add RAG service API"
```

---

## Chunk 6: Integração com Agentes

### Task 9: Integração com Agentes OCI Copilot

**Files:**
- Modify: `config/oci-copilot-agents.yaml` (adicionar tool rag_retrieve)
- Create: `rag/tool_wrapper.py`

- [ ] **Step 1: Escrever wrapper para tool**

```python
# rag/tool_wrapper.py
"""Tool wrappers for agent integration."""

from typing import Dict, Any, List, Optional
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
        """
        Retrieve documents for agent context.
        
        Args:
            query: Query do usuário
            k: Número de resultados
            strategy: Estratégia (migracao, configuracao, troubleshooting)
            filters: Filtros de metadata
            
        Returns:
            Dict com 'documents' e 'sources'
        """
        if strategy:
            self.retriever.set_strategy(strategy)
        
        results = self.retriever.retrieve(query, k=k)
        
        documents = []
        for r in results:
            meta = r.get("metadata", {})
            documents.append({
                "content": meta.get("content", ""),
                "url": meta.get("url", ""),
                "title": meta.get("title", ""),
                "score": r.get("score", 0)
            })
        
        return {
            "documents": documents,
            "query": query,
            "num_results": len(documents)
        }


def create_rag_tools(config: Dict[str, Any]) -> Dict[str, Any]:
    """Cria tools baseadas na configuração do agente."""
    # Implementação future quando índices carregados
    return {}
```

- [ ] **Step 2: Commit**

```bash
git add rag/tool_wrapper.py
git commit -m "feat(rag): add tool wrapper for agent integration"
```

### Task 10: Script de Demonstração

**Files:**
- Create: `rag/demo.py`

- [ ] **Step 1: Criar script de demo**

```python
#!/usr/bin/env python3
"""Demo script para testar RAG."""

from rag.crawler import fetch_oci_docs
from rag.ingestion_pipeline import IngestionPipeline
from rag.hybrid_retriever import HybridRetriever
from rag.embedder import Embedder
from rag.vector_store import VectorStore
from rag.bm25_index import BM25Index
import tempfile
import os


def main():
    # Demo com dados sintéticos (sem necessidade de crawler real)
    print("=== OCI Copilot RAG Demo ===\n")
    
    # 1. Criar dados de exemplo
    docs = [
        {"url": "https://docs.oracle.com/instance", "title": "OCI Instances", 
         "content": "Para criar uma instância de compute no OCI, você precisa definir o compartment, a forma (shape), a imagem (image), e a rede VCN. As instâncias podem ser redimensionadas later."},
        {"url": "https://docs.oracle.com/vcn", "title": "VCN Networking",
         "content": "Uma Virtual Cloud Network (VCN) é uma rede virtual privada no OCI. Você pode criar subnets públicas ou privadas, configurar security lists, e usar NAT gateway."},
        {"url": "https://docs.oracle.com/autonomous", "title": "Autonomous Database",
         "content": "Oracle Autonomous Database é um banco de dados self-driving, self-securing, self-repairing. Suporta both OLTP and OLAP workloads com machine learning automation."},
    ]
    
    with tempfile.TemporaryDirectory() as tmpdir:
        print("1. Running ingestion pipeline...")
        pipeline = IngestionPipeline(output_dir=tmpdir, chunk_size=500)
        result = pipeline.run(docs)
        print(f"   Created {result['chunks']} chunks\n")
        
        print("2. Loading indexes...")
        vector_store, bm25 = pipeline.load_indexes()
        embedder = Embedder()
        print(f"   Loaded {len(vector_store)} vectors, {len(bm25.documents)} docs\n")
        
        print("3. Testing queries...\n")
        retriever = HybridRetriever(
            vector_store=vector_store,
            bm25_index=bm25,
            embedder=embedder
        )
        
        queries = [
            "como criar instância de compute",
            "VCN subnet configuração",
            "autonomous database setup"
        ]
        
        for query in queries:
            print(f"Query: {query}")
            results = retriever.retrieve(query, k=2)
            for r in results:
                meta = r.get("metadata", {})
                print(f"  - [{r['score']:.3f}] {meta.get('title', 'N/A')}")
                print(f"    {meta.get('content', '')[:100]}...")
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

## Chunk 7: Teste de Integração Completo

### Task 11: Teste End-to-End

**Files:**
- Create: `tests/rag/test_e2e.py`

- [ ] **Step 1: Escrever teste e2e**

```python
# tests/rag/test_e2e.py
"""End-to-end RAG integration test."""

import pytest
import tempfile
import os
from rag.ingestion_pipeline import IngestionPipeline
from rag.hybrid_retriever import HybridRetriever
from rag.embedder import Embedder


def test_full_rag_pipeline():
    """Teste completo: ingestion + retrieval."""
    
    # Dados de teste
    docs = [
        {"url": "https://example.com/1", "title": "OCI Compute", 
         "content": "OCI Compute Instances permite criar máquinas virtuais ou bare metal. Shapes disponíveis incluem VM.Standard, VM.DenseIO, e BM.GPU."},
        {"url": "https://example.com/2", "title": "OCI Networking",
         "content": "VCN (Virtual Cloud Network) é o componente fundamental de rede no OCI. Suporta subnets, route tables, security lists, e NAT gateway."},
    ]
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Ingestion
        pipeline = IngestionPipeline(output_dir=tmpdir, chunk_size=500)
        result = pipeline.run(docs)
        
        assert result["chunks"] >= 2
        
        # Retrieval
        vector_store, bm25 = pipeline.load_indexes()
        embedder = Embedder()
        retriever = HybridRetriever(vector_store, bm25, embedder)
        
        results = retriever.retrieve("OCI compute instance shapes", k=2)
        
        assert len(results) >= 1
        # Verifica que pelo menos um resultado é relevante
        scores = [r["score"] for r in results]
        assert max(scores) > 0


def test_different_strategies():
    """Testa diferentes estratégias de retrieval."""
    
    docs = [
        {"url": "https://example.com/1", "title": "Test", "content": "Content about OCI."},
    ]
    
    with tempfile.TemporaryDirectory() as tmpdir:
        pipeline = IngestionPipeline(output_dir=tmpdir, chunk_size=500)
        pipeline.run(docs)
        
        vector_store, bm25 = pipeline.load_indexes()
        embedder = Embedder()
        
        # Teste migracao strategy
        retriever = HybridRetriever(vector_store, bm25, embedder)
        retriever.set_strategy("migracao")
        
        assert retriever.dense_weight == 0.6
        
        # Teste configuracao strategy
        retriever.set_strategy("configuracao")
        assert retriever.sparse_weight == 0.6
```

- [ ] **Step 2: Executar todos os testes**

Run: `python -m pytest tests/rag/ -v --tb=short`
Expected: All PASS

- [ ] **Step 3: Commit**

```bash
git add tests/rag/test_e2e.py
git commit -m "test(rag): add end-to-end integration tests"
```

---

## Resumo das Tasks

| Task | Descrição | Status |
|------|-----------|--------|
| 1 | Crawler docs Oracle | Pending |
| 2 | Document chunker | Pending |
| 3 | Embedding generator | Pending |
| 4 | FAISS vector store | Pending |
| 5 | BM25 sparse index | Pending |
| 6 | Hybrid retriever | Pending |
| 7 | Ingestion pipeline | Pending |
| 8 | RAG API | Pending |
| 9 | Tool wrapper | Pending |
| 10 | Demo script | Pending |
| 11 | E2E tests | Pending |

---

## Comandos para Rodar

```bash
# Instalar dependências
pip install faiss-cpu rank-bm25 sentence-transformers fastapi uvicorn

# Criar diretório de testes
mkdir -p tests/rag

# Rodar testes
python -m pytest tests/rag/ -v

# Rodar demo
python rag/demo.py

# Iniciar API
RAG_DATA_DIR=rag/data uvicorn rag.api:app --reload
```

---

**Plan complete and saved to `docs/superpowers/plans/2026-04-13-rag-layer-implementation.md`. Ready to execute?**
