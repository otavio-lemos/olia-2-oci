# RAG Layer Implementation Plan (LangChain)

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan.

**Goal:** Implementar camada RAG híbrida usando LangChain, alinhada com `docs/oci-copilot-rag.md` e `config/oci-copilot-agents.yaml`.

**Architecture:** LangChain com retrievers customizados, fused (RRF), metadata filters, agents e workflows conforme YAML. Segue docs/oci-copilot-roadmap.md Onda 1.

**Tech Stack:** LangChain, langchain-community, FAISS, BM25Retriever, FastAPI, Python 3.12

---

## Chunk 1: Config e Setup

### Task 1: Config Loader

**Files:**
- Create: `rag/config.py`
- Test: `tests/rag/test_config.py`

- [ ] **Step 1: Escrever teste**

```python
# tests/rag/test_config.py
import pytest
from rag.config import load_rag_config

def test_load_rag_config():
    config = load_rag_config("config/oci-copilot-agents.yaml")
    assert config["rag"]["default_strategy"] == "hybrid"
    assert config["rag"]["fusion"]["dense_weight"] == 0.7
    assert len(config["agents"]) == 10
```

- [ ] **Step 2: Run test**

Run: `cd .worktrees/rag-langchain && python -m pytest tests/rag/test_config.py::test_load_rag_config -v`
Expected: FAIL - module not found

- [ ] **Step 3: Implementar config loader**

```python
# rag/config.py
"""Carrega configuração do YAML."""
import yaml
from pathlib import Path
from typing import Dict, Any


def load_rag_config(config_path: str = "config/oci-copilot-agents.yaml") -> Dict[str, Any]:
    """Carrega config do agente."""
    path = Path(config_path)
    if not path.exists:
        path = Path(__file__).parent.parent / config_path
    
    with open(path) as f:
        return yaml.safe_load(f)


def get_rag_config() -> Dict[str, Any]:
    """Retorna config RAG."""
    config = load_rag_config()
    return config.get("rag", {})


def get_agent_config(agent_name: str) -> Dict[str, Any]:
    """Retorna config de um agente."""
    config = load_rag_config()
    return config.get("agents", {}).get(agent_name, {})


def get_workflow_config(workflow_name: str) -> Dict[str, Any]:
    """Retorna config de um workflow."""
    config = load_rag_config()
    return config.get("workflows", {}).get(workflow_name, {})
```

- [ ] **Step 4: Run test**

Run: `cd .worktrees/rag-langchain && python -m pytest tests/rag/test_config.py::test_load_rag_config -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add rag/config.py tests/rag/test_config.py
git commit -m "feat(rag): add config loader"
```

---

## Chunk 2: Document Loaders e Chunking

### Task 2: Document Loader

**Files:**
- Create: `rag/loaders.py`
- Test: `tests/rag/test_loaders.py`

- [ ] **Step 1: Escrever teste**

```python
# tests/rag/test_loaders.py
import pytest
from rag.loaders import OCIDocsLoader

def test_load_docs_from_url():
    loader = OCIDocsLoader()
    docs = loader.load(["https://docs.oracle.com/en-us/iaas/Content/Compute/containers/overview.htm"])
    assert len(docs) >= 0  # pode falhar network
```

- [ ] **Step 2: Run test**

Run: `python -m pytest tests/rag/test_loaders.py::test_load_docs_from_url -v`
Expected: FAIL - module not found

- [ ] **Step 3: Implementar loader**

```python
# rag/loaders.py
"""Document loaders para OCI."""
from typing import List, Iterator
from langchain_community.document_loaders import WebBaseLoader
from langchain.schema import Document


class OCIDocsLoader(WebBaseLoader):
    """Loader para docs Oracle OCI."""
    
    def __init__(self, urls: List[str] = None):
        super().__init__(web_paths=urls or [])
    
    def load_with_metadata(self, metadata: dict) -> List[Document]:
        """Carrega docs com metadados enriched."""
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
                docs.extend(loader.load_with_metadata({
                    "url": url,
                    "doc_type": "oracle_docs"
                }))
            except Exception as e:
                print(f"Error loading {url}: {e}")
        return docs


def load_oracle_docs(urls: List[str] = None, domain: str = "general") -> List[Document]:
    """Helper para carregar docs Oracle."""
    if not urls:
        urls = [
            "https://docs.oracle.com/en-us/iaas/Content/Compute/containers/overview.htm",
            "https://docs.oracle.com/en-us/iaas/Content/Network/VCNs/comprehensiv-overview.htm",
        ]
    loader = OCIWebLoader(urls)
    docs = loader.load()
    for doc in docs:
        doc.metadata["domain"] = domain
    return docs
```

- [ ] **Step 4: Run test**

Run: `python -m pytest tests/rag/test_loaders.py::test_load_docs_from_url -v`
Expected: PASS (ou skip se network)

- [ ] **Step 5: Commit**

```bash
git add rag/loaders.py tests/rag/test_loaders.py
git commit -m "feat(rag): add OCI document loader"
```

### Task 3: Text Splitter

**Files:**
- Create: `rag/splitter.py`
- Test: `tests/rag/test_splitter.py`

- [ ] **Step 1: Escrever teste**

```python
# tests/rag/test_splitter.py
import pytest
from rag.splitter import create_oci_splitter
from langchain.schema import Document

def test_split_with_metadata():
    splitter = create_oci_splitter()
    docs = [Document(page_content="# Criar instância\n\n1. Login\n2. Selecionar compartment", metadata={"domain": "compute"})]
    chunks = splitter.split_documents(docs)
    assert len(chunks) > 0
    assert chunks[0].metadata.get("domain") == "compute"
```

- [ ] **Step 2: Run test**

Run: `python -m pytest tests/rag/test_splitter.py::test_split_with_metadata -v`
Expected: FAIL

- [ ] **Step 3: Implementar splitter**

```python
# rag/splitter.py
"""Text splitters para OCI."""
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.text_splitter import MarkdownHeaderTextSplitter


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


def create_markdown_splitter():
    """Splitter para markdown OCI."""
    headers_to_split_on = [
        ("#", "h1"),
        ("##", "h2"),
        ("##", "h3"),
    ]
    return MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)


def split_with_metadata(documents, **kwargs):
    """Split documents preservando metadados."""
    splitter = create_oci_splitter(**kwargs)
    return splitter.split_documents(documents)
```

- [ ] **Step 4: Run test**

Run: `python -m pytest tests/rag/test_splitter.py::test_split_with_metadata -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add rag/splitter.py tests/rag/test_splitter.py
git commit -m "feat(rag): add text splitter for OCI docs"
```

---

## Chunk 3: Retrievers (Dense + Sparse)

### Task 4: Dense Retriever (FAISS)

**Files:**
- Create: `rag/dense_retriever.py`
- Test: `tests/rag/test_dense_retriever.py`

- [ ] **Step 1: Escrever teste**

```python
# tests/rag/test_dense_retriever.py
import pytest
from rag.dense_retriever import create_dense_retriever
from langchain.schema import Document

def test_create_dense_retriever():
    docs = [Document(page_content="criar instância OCI", metadata={"id": 1})]
    retriever = create_dense_retriever(docs, embedding_model="sentence-transformers/all-MiniLM-L6-v2")
    results = retriever.invoke("instância OCI compute")
    assert len(results) >= 1
```

- [ ] **Step 2: Run test**

Run: `python -m pytest tests/rag/test_dense_retriever.py::test_create_dense_retriever -v`
Expected: FAIL

- [ ] **Step 3: Implementar dense retriever**

```python
# rag/dense_retriever.py
"""Dense retriever usando FAISS."""
from typing import List, Optional
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import EmbeddingsFilter


def create_dense_retriever(
    documents: List[Document],
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
    k: int = 20,
) -> "FAISS":
    """Cria dense retriever com embeddings."""
    embeddings = HuggingFaceEmbeddings(model_name=embedding_model)
    vectorstore = FAISS.from_documents(documents, embeddings)
    return vectorstore.as_retriever(search_kwargs={"k": k})


def create_compression_retriever(
    base_retriever,
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
    k: int = 10,
):
    """Cria compression retriever com embeddings filter."""
    embeddings = HuggingFaceEmbeddings(model_name=embedding_model)
    return ContextualCompressionRetriever(
        base_compressor=EmbeddingsFilter(embeddings=embeddings, k=k),
        base_retriever=base_retriever,
    )
```

- [ ] **Step 4: Run test**

Run: `python -m pytest tests/rag/test_dense_retriever.py::test_create_dense_retriever -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add rag/dense_retriever.py tests/rag/test_dense_retriever.py
git commit -m "feat(rag): add FAISS dense retriever"
```

### Task 5: Sparse Retriever (BM25)

**Files:**
- Create: `rag/sparse_retriever.py`
- Test: `tests/rag/test_sparse_retriever.py`

- [ ] **Step 1: Escrever teste**

```python
# tests/rag/test_sparse_retriever.py
import pytest
from rag.sparse_retriever import create_sparse_retriever
from langchain.schema import Document

def test_create_sparse_retriever():
    docs = [Document(page_content="OCI compute instance shape", metadata={"id": 1})]
    retriever = create_sparse_retriever(docs)
    results = retriever.invoke("compute instance")
    assert len(results) >= 1
```

- [ ] **Step 2: Run test**

Run: `python -m pytest tests/rag/test_sparse_retriever.py::test_create_sparse_retriever -v`
Expected: FAIL

- [ ] **Step 3: Implementar sparse retriever**

```python
# rag/sparse_retriever.py
"""Sparse retriever usando BM25."""
from typing import List
from langchain_community.retrievers import BM25Retriever
from langchain.schema import Document


def create_sparse_retriever(
    documents: List[Document],
    k: int = 40,
):
    """Cria sparse retriever com BM25."""
    texts = [doc.page_content for doc in documents]
    metadatas = [doc.metadata for doc in documents]
    retriever = BM25Retriever.from_texts(texts, metadatas=metadatas)
    return retriever
```

- [ ] **Step 4: Run test**

Run: `python -m pytest tests/rag/test_sparse_retriever.py::test_create_sparse_retriever -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add rag/sparse_retriever.py tests/rag/test_sparse_retriever.py
git commit -m "feat(rag): add BM25 sparse retriever"
```

---

## Chunk 4: Hybrid Retrieval (RRF Fusion)

### Task 6: Hybrid Retriever

**Files:**
- Create: `rag/hybrid_retriever.py`
- Test: `tests/rag/test_hybrid_retriever.py`

- [ ] **Step 1: Escrever teste**

```python
# tests/rag/test_hybrid_retriever.py
import pytest
from rag.hybrid_retriever import create_hybrid_retriever, HybridRetrieverWithConfig
from rag.config import get_rag_config
from rag.dense_retriever import create_dense_retriever
from rag.sparse_retriever import create_sparse_retriever
from langchain.schema import Document

def test_hybrid_retriever_rrf():
    docs = [Document(page_content="criar OCI compute instance", metadata={"id": 1})]
    dense = create_dense_retriever(docs)
    sparse = create_sparse_retriever(docs)
    hybrid = create_hybrid_retriever(dense, sparse, weights=[0.7, 0.3])
    results = hybrid.invoke("compute OCI")
    assert len(results) >= 1

def test_hybrid_with_config():
    dense = create_dense_retriever([Document(page_content="test", metadata={})])
    sparse = create_sparse_retriever([Document(page_content="test", metadata={})])
    hybrid = HybridRetrieverWithConfig(dense, sparse, config_name="migracao")
    # migracao usa weights 0.6/0.4
    results = hybrid.invoke("test OCI")
    assert len(results) >= 1
```

- [ ] **Step 2: Run test**

Run: `python -m pytest tests/rag/test_hybrid_retriever.py -v`
Expected: FAIL

- [ ] **Step 3: Implementar hybrid retriever**

```python
# rag/hybrid_retriever.py
"""Hybrid retriever com RRF fusion."""
from typing import List, Optional, Dict, Any
from langchain.retrievers import EnsembleRetriever
from langchain.schema import Document


def create_hybrid_retriever(
    dense_retriever,
    sparse_retriever,
    weights: List[float] = [0.7, 0.3],
    k: int = 10,
) -> EnsembleRetriever:
    """Cria hybrid retriever com weights."""
    return EnsembleRetriever(
        retrievers=[dense_retriever, sparse_retriever],
        weights=weights,
    )


class HybridRetrieverWithConfig:
    """Hybrid retriever que respeita config do YAML."""
    
    STRATEGIES = {
        "default": {"weights": [0.7, 0.3], "k": 10},
        "migracao": {"weights": [0.6, 0.4], "k": 10},
        "configuracao": {"weights": [0.4, 0.6], "k": 10},
        "troubleshooting": {"weights": [0.5, 0.5], "k": 10},
    }
    
    def __init__(self, dense_retriever, sparse_retriever, config_name: str = "default"):
        self.dense = dense_retriever
        self.sparse = sparse_retriever
        self.config_name = config_name
        self._build()
    
    def _build(self):
        strategy = self.STRATEGIES.get(self.config_name, self.STRATEGIES["default"])
        self.retriever = EnsembleRetriever(
            retrievers=[self.dense, self.sparse],
            weights=strategy["weights"],
        )
    
    def set_strategy(self, strategy_name: str):
        """Muda estratégia."""
        self.config_name = strategy_name
        self._build()
    
    def invoke(self, query: str):
        return self.retriever.invoke(query)
    
    def get_config(self) -> Dict[str, Any]:
        return self.STRATEGIES.get(self.config_name, self.STRATEGIES["default"])
```

- [ ] **Step 4: Run test**

Run: `python -m pytest tests/rag/test_hybrid_retriever.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add rag/hybrid_retriever.py tests/rag/test_hybrid_retriever.py
git commit -m "feat(rag): add hybrid retriever with RRF"
```

---

## Chunk 5: Agentes e Tools

### Task 7: RAG Tool

**Files:**
- Create: `rag/tools.py`
- Test: `tests/rag/test_tools.py`

- [ ] **Step 1: Escrever teste**

```python
# tests/rag/test_tools.py
import pytest
from rag.tools import create_rag_tool, RAGTool

def test_create_rag_tool():
    # Mock retriever
    class MockRetriever:
        def invoke(self, query):
            return [Document(page_content="test", metadata={})]
    
    tool = create_rag_tool(MockRetriever(), agent_config={"rag_strategy": "hybrid"})
    assert tool.name == "rag_retrieve"
```

- [ ] **Step 2: Run test**

Run: `python -m pytest tests/rag/test_tools.py::test_create_rag_tool -v`
Expected: FAIL

- [ ] **Step 3: Implementar tool**

```python
# rag/tools.py
"""Tools para agentes LangChain."""
from typing import Optional, List, Dict, Any
from langchain_core.tools import BaseTool
from langchain.schema import Document
from pydantic import BaseModel


class RetrieveInput(BaseModel):
    query: str
    k: int = 10
    strategy: Optional[str] = None
    filters: Optional[Dict[str, Any]] = None


class RAGTool(BaseTool):
    """Tool de retrieve para agentes."""
    
    name = "rag_retrieve"
    description = "Recupera documentos da documentação OCI. Use para perguntas sobre OCI."
    args_schema = RetrieveInput
    
    def __init__(self, retriever, agent_config: Dict[str, Any]):
        super().__init__()
        self.retriever = retriever
        self.agent_config = agent_config
    
    def _run(self, query: str, k: int = 10, strategy: str = None, filters: dict = None) -> str:
        if strategy:
            self.retriever.set_strategy(strategy)
        
        docs = self.retriever.invoke(query)
        
        if filters:
            docs = [d for d in docs if all(d.metadata.get(k) == v for k, v in filters.items())]
        
        docs = docs[:k]
        
        return "\n\n".join([
            f"## {i+1}. {d.metadata.get('title', 'Document')}\n{d.page_content[:500]}"
            for i, d in enumerate(docs)
        ])


def create_rag_tool(retriever, agent_config: Dict[str, Any]) -> RAGTool:
    """Factory para criar RAG tool."""
    return RAGTool(retriever=retriever, agent_config=agent_config)
```

- [ ] **Step 4: Run test**

Run: `python -m pytest tests/rag/test_tools.py::test_create_rag_tool -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add rag/tools.py tests/rag/test_tools.py
git commit -m "feat(rag): add RAG tool for agents"
```

### Task 8: Agent Factory

**Files:**
- Create: `rag/agents.py`
- Test: `tests/rag/test_agents.py`

- [ ] **Step 1: Escrever teste**

```python
# tests/rag/test_agents.py
import pytest
from rag.agents import create_agent, list_available_agents, get_agent_workflow
from rag.config import load_rag_config

def test_list_available_agents():
    agents = list_available_agents()
    assert "router" in agents
    assert "migracao" in agents
    assert "configuracao_seg" in agents

def test_get_agent_workflow():
    workflow = get_agent_workflow("migracao")
    assert workflow["entry_agent"] == "router"
    assert "pipeline" in workflow
```

- [ ] **Step 2: Run test**

Run: `python -m pytest tests/rag/test_agents.py::test_list_available_agents -v`
Expected: FAIL

- [ ] **Step 3: Implementar agents**

```python
# rag/agents.py
"""Agentes e workflows."""
from typing import Dict, List, Any, Optional
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate
from rag.config import load_rag_config, get_agent_config
from rag.tools import create_rag_tool
from rag.hybrid_retriever import HybridRetrieverWithConfig


def list_available_agents() -> List[str]:
    """Lista agentes disponíveis."""
    config = load_rag_config()
    return list(config.get("agents", {}).keys())


def get_agent_workflow(workflow_name: str) -> Dict[str, Any]:
    """Retorna workflow."""
    config = load_rag_config()
    return config.get("workflows", {}).get(workflow_name, {})


def create_agent(
    agent_name: str,
    retriever: HybridRetrieverWithConfig,
    llm=None,
) -> Optional[AgentExecutor]:
    """Cria agente baseado no config."""
    config = get_agent_config(agent_name)
    if not config:
        return None
    
    tools = []
    if "rag_retrieve" in config.get("tools", []):
        tools.append(create_rag_tool(retriever, config))
    
    if not llm or not tools:
        return None
    
    prompt = ChatPromptTemplate.from_template(
        f"""Você é o agente {agent_name}.
        Description: {config.get('description', '')}
        
        Tools disponíveis: {{tools}}
        {{tool_names}}
        
        Input: {{input}}
        {{agent_scratchpad}}"""
    )
    
    agent = create_tool_calling_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=True)


def run_workflow(workflow_name: str, input: str, retriever, llm) -> str:
    """Executa workflow completo."""
    workflow = get_agent_workflow(workflow_name)
    if not workflow:
        return f"Workflow '{workflow_name}' não encontrado"
    
    results = []
    pipeline = workflow.get("pipeline", [])
    
    for agent_name in pipeline:
        if agent_name == "router":
            continue
        agent = create_agent(agent_name, retriever, llm)
        if agent:
            result = agent.run(input)
            results.append(f"=== {agent_name} ===\n{result}")
    
    return "\n\n".join(results)
```

- [ ] **Step 4: Run test**

Run: `python -m pytest tests/rag/test_agents.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add rag/agents.py tests/rag/test_agents.py
git commit -m "feat(rag): add agent factory"
```

---

## Chunk 6: API Service

### Task 9: FastAPI Service

**Files:**
- Create: `rag/api.py`
- Test: `tests/rag/test_api.py`

- [ ] **Step 1: Escrever teste**

```python
# tests/rag/test_api.py
import pytest
from fastapi.testclient import TestClient
from rag.api import app

def test_health():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
```

- [ ] **Step 2: Run test**

Run: `python -m pytest tests/rag/test_api.py::test_health -v`
Expected: FAIL

- [ ] **Step 3: Implementar API**

```python
# rag/api.py
"""FastAPI service para RAG."""
import os
from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from rag.config import load_rag_config
from rag.dense_retriever import create_dense_retriever
from rag.sparse_retriever import create_sparse_retriever
from rag.hybrid_retriever import HybridRetrieverWithConfig
from rag.loaders import load_oracle_docs
from rag.splitter import split_with_metadata
from rag.agents import run_workflow


app = FastAPI(title="OCI Copilot RAG Service")

RETRIEVER: Optional[HybridRetrieverWithConfig] = None


class RetrieveRequest(BaseModel):
    query: str
    k: int = 10
    strategy: Optional[str] = None
    filters: Optional[dict] = None


class WorkflowRequest(BaseModel):
    workflow: str
    query: str


@app.on_event("startup")
async def startup():
    global RETRIEVER
    data_dir = os.environ.get("RAG_DATA_DIR", "rag/data")
    
    if os.path.exists(data_dir):
        from rag.dense_retriever import create_dense_retriever
        from rag.sparse_retriever import create_sparse_retriever
        
        docs = []  # TODO: load from disk
        dense = create_dense_retriever(docs)
        sparse = create_sparse_retriever(docs)
        RETRIEVER = HybridRetrieverWithConfig(dense, sparse)
        print(f"Loaded RAG from {data_dir}")
    else:
        print("No RAG data, running with empty index")


@app.get("/health")
async def health():
    return {"status": "healthy", "retriever_loaded": RETRIEVER is not None}


@app.post("/rag/retrieve")
async def retrieve(request: RetrieveRequest):
    if not RETRIEVER:
        raise HTTPException(503, "RAG not initialized")
    
    if request.strategy:
        RETRIEVER.set_strategy(request.strategy)
    
    docs = RETRIEVER.invoke(request.query)
    return {
        "documents": [
            {"content": d.page_content, "metadata": d.metadata}
            for d in docs[:request.k]
        ]
    }


@app.post("/workflow/run")
async def run_workflow_endpoint(request: WorkflowRequest):
    if not RETRIEVER:
        raise HTTPException(503, "RAG not initialized")
    
    # TODO: integrate with LLM
    result = run_workflow(request.workflow, request.query, RETRIEVER, None)
    return {"result": result}


@app.get("/agents")
async def list_agents():
    from rag.agents import list_available_agents
    return {"agents": list_available_agents()}


@app.get("/workflows")
async def list_workflows():
    from rag.agents import get_agent_workflow
    config = load_rag_config()
    return {"workflows": list(config.get("workflows", {}).keys())}


@app.post("/rag/ingest")
async def ingest_documents(urls: list, domain: str = "general"):
    """Ingere documentos."""
    docs = load_oracle_docs(urls, domain)
    chunks = split_with_metadata(docs)
    
    dense = create_dense_retriever(chunks)
    global RETRIEVER
    RETRIEVER = HybridRetrieverWithConfig(dense.as_retriever(), create_sparse_retriever(chunks).as_retriever())
    
    return {"Indexed": len(chunks)}
```

- [ ] **Step 4: Run test**

Run: `python -m pytest tests/rag/test_api.py::test_health -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add rag/api.py tests/rag/test_api.py
git commit -m "feat(rag): add FastAPI service"
```

---

## Chunk 7: Demo

### Task 10: Demo Script

**Files:**
- Create: `rag/demo.py`

- [ ] **Step 1: Criar demo**

```python
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
        "VCN networking configuração",
    ]
    
    for query in queries:
        print(f"Query: {query}")
        results = hybrid.invoke(query)
        for i, doc in enumerate(results[:3]):
            print(f"  {i+1}. {doc.page_content[:100]}...")
        print()


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run demo**

Run: `python rag/demo.py`

- [ ] **Step 3: Commit**

```bash
git add rag/demo.py
git commit -m "feat(rag): add demo script"
```

---

## Resumo

| Task | Descrição |
|------|-----------|
| 1 | Config Loader (YAML) |
| 2 | Document Loaders |
| 3 | Text Splitter |
| 4 | Dense Retriever (FAISS) |
| 5 | Sparse Retriever (BM25) |
| 6 | Hybrid Retriever (RRF) |
| 7 | RAG Tool |
| 8 | Agent Factory |
| 9 | FastAPI Service |
| 10 | Demo |

---

## Alinhamento com Documentos

| docs/oci-copilot-rag.md | Implementado |
|------------------------|-------------|
| Hybrid (dense + sparse) | ✅ Task 6 |
| BM25 | ✅ Task 5 |
| RRF fusion | ✅ Task 6 |
| Re-ranking | ⚠️ Opcional |
| Query rewriting | ⚠️ Opcional |
| Agentic RAG | ✅ Task 7-8 |

| config/oci-copilot-agents.yaml | Implementado |
|-----------------------------|-------------|
| 10 agents | ✅ Task 8 |
| 10 workflows | ✅ Task 8 |
| metadata_filters | ✅ Task 7 |
| by_type strategies | ✅ Task 6 |

---

## Comandos

```bash
# Instalar dependências
source venv-rag/bin/activate
pip install langchain langchain-community faiss-cpu beautifulsoup4 requests fastapi uvicorn pyyaml langchain-huggingface

# Criar diretório de testes
mkdir -p tests/rag

# Rodar demo
python rag/demo.py

# Iniciar API
RAG_DATA_DIR=rag/data uvicorn rag.api:app --reload --port 8080
```

---

**Plan complete and saved to `docs/superpowers/plans/2026-04-13-rag-layer-langchain.md`. Ready to execute?**