"""FastAPI service para RAG."""

import os
from contextlib import asynccontextmanager
from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from rag.config import load_rag_config

try:
    from rag.loaders import load_oracle_docs
    from rag.splitter import split_with_metadata
    from rag.dense_retriever import create_dense_retriever
    from rag.sparse_retriever import create_sparse_retriever
    from rag.hybrid_retriever import HybridRetrieverWithConfig

    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False
    HybridRetrieverWithConfig = None

RETRIEVER: Optional[HybridRetrieverWithConfig] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global RETRIEVER
    if not RAG_AVAILABLE:
        print("RAG components not available.")
        yield
        return
    try:
        dense = create_dense_retriever(documents=None)
        sparse = create_sparse_retriever(documents=None)
        if dense and sparse:
            RETRIEVER = HybridRetrieverWithConfig(dense, sparse)
            print("Successfully loaded persisted RAG indices.")
    except Exception as e:
        print(f"No persisted RAG indices found or failed to load: {e}")
    yield


app = FastAPI(title="OCI Copilot RAG Service", lifespan=lifespan)


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
        raise HTTPException(503, "RAG not initialized. Ingest data first.")

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
async def ingest_documents(
    urls: list = None, domain: str = "general", incremental: bool = True
):
    """Ingere documentos e persiste no disco.

    Se incremental=True (default), apenas adiciona docs novos baseados em URL.
    Se incremental=False, faz rebuild completo do índice.
    """
    docs = load_oracle_docs(urls, domain)
    chunks = split_with_metadata(docs)

    indexed_urls = set()
    existing_chunks = []

    if incremental:
        try:
            from rag.dense_retriever import load_existing_index

            existing = load_existing_index()
            if existing:
                existing_chunks = list(existing)
                indexed_urls = {
                    doc.metadata.get("url")
                    for doc in existing_chunks
                    if doc.metadata.get("url")
                }
        except Exception:
            pass

    new_chunks = [c for c in chunks if c.metadata.get("url") not in indexed_urls]

    if not new_chunks:
        return {"indexed": 0, "message": "No new documents"}

    all_chunks = existing_chunks + new_chunks

    dense = create_dense_retriever(all_chunks)
    sparse = create_sparse_retriever(all_chunks)

    global RETRIEVER
    RETRIEVER = HybridRetrieverWithConfig(dense, sparse)

    return {"indexed": len(new_chunks), "total": len(all_chunks)}


class ChatMessage(BaseModel):
    role: str = "user"
    content: str
    timestamp: str | None = None


class ChatRequest(BaseModel):
    messages: list[ChatMessage] = []
    query: str
    session_id: str | None = None
    temperature: float = 0.1
    max_tokens: int = 2048
    strategy: str | None = None


class StreamChunk(BaseModel):
    token: str = ""
    done: bool = False
    citations: list[dict] = []


@app.post("/rag/chat")
async def chat(request: ChatRequest):
    """Chat endpoint com streaming SSE."""
    from rag.llm_client import streaming_format, MLXClient
    from fastapi.responses import StreamingResponse
    import asyncio

    context_docs = []
    if RETRIEVER and RAG_AVAILABLE:
        context_docs = RETRIEVER.invoke(request.query)[:5]

    client = MLXClient()

    async def event_stream():
        try:
            citations = [
                {"content": d.page_content[:200], "metadata": d.metadata}
                for d in context_docs
            ]
            yield streaming_format(f"Citations: {len(citations)} docs", done=False)

            stream = client.stream(request.query, context_docs)
            async for token in stream:
                yield streaming_format(token, done=False)

            yield streaming_format("", done=True)
        finally:
            await client.close()

    return StreamingResponse(event_stream(), media_type="text/event-stream")
