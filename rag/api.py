"""FastAPI service para RAG."""

import os
from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from rag.config import load_rag_config
from rag.loaders import load_oracle_docs
from rag.splitter import split_with_metadata
from rag.dense_retriever import create_dense_retriever
from rag.sparse_retriever import create_sparse_retriever
from rag.hybrid_retriever import HybridRetrieverWithConfig


app = FastAPI(title="OCI Copilot RAG Service")

RETRIEVER: Optional[HybridRetrieverWithConfig] = None


class RetrieveRequest(BaseModel):
    query: str
    k: int = 10
    strategy: Optional[str] = None


class WorkflowRequest(BaseModel):
    workflow: str
    query: str


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
            for d in docs[: request.k]
        ]
    }


@app.get("/agents")
async def list_agents():
    from rag.config import get_rag_config

    config = get_rag_config()
    # Not Implemented
    return {}


@app.get("/workflows")
async def list_workflows():
    config = load_rag_config()
    return {"workflows": list(config.get("workflows", {}).keys())}


@app.post("/rag/ingest")
async def ingest_documents(urls: list = None, domain: str = "general"):
    """Ingere documentos."""
    docs = load_oracle_docs(urls, domain)
    chunks = split_with_metadata(docs)

    dense = create_dense_retriever(chunks)
    sparse = create_sparse_retriever(chunks)

    global RETRIEVER
    RETRIEVER = HybridRetrieverWithConfig(dense, sparse)

    return {"Indexed": len(chunks)}
