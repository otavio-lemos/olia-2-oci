"""Sparse retriever usando BM25 com persistência."""

from typing import List, Optional
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document
import pickle
import os

def create_sparse_retriever(
    documents: Optional[List[Document]] = None,
    k: int = 40,
    save_path: str = "data/bm25_retriever.pkl"
):
    """Cria ou carrega um sparse retriever com BM25 (com persistência)."""
    # Se não há documentos, tenta carregar do disco
    if not documents:
        if os.path.exists(save_path):
            with open(save_path, "rb") as f:
                retriever = pickle.load(f)
            retriever.k = k
            return retriever
        return None
        
    texts = [doc.page_content for doc in documents]
    metadatas = [doc.metadata for doc in documents]
    retriever = BM25Retriever.from_texts(texts, metadatas=metadatas)
    retriever.k = k
    
    # Salva para persistência
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    with open(save_path, "wb") as f:
        pickle.dump(retriever, f)
        
    return retriever
