"""Dense retriever usando FAISS e HuggingFace."""

from typing import List, Optional
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from rag.config import get_rag_config
import os

def get_embedding_model_name() -> str:
    """Obtém o modelo de embedding da configuração."""
    config = get_rag_config()
    return config.get("dense", {}).get("embedding_model", "sentence-transformers/all-MiniLM-L6-v2")

def create_dense_retriever(
    documents: Optional[List[Document]] = None,
    embedding_model: str = None,
    k: int = 20,
    index_path: str = "data/faiss_index"
):
    """Cria ou carrega um dense retriever com FAISS (com persistência)."""
    if not embedding_model:
        embedding_model = get_embedding_model_name()
        
    try:
        embeddings = HuggingFaceEmbeddings(model_name=embedding_model)
    except Exception as e:
        print(f"Warning: Failed to load embedding model '{embedding_model}': {e}")
        print("Falling back to 'sentence-transformers/all-MiniLM-L6-v2'")
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    
    # Se não há documentos, tenta carregar do disco (persistência)
    if not documents:
        if os.path.exists(index_path):
            vectorstore = FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)
            return vectorstore.as_retriever(search_kwargs={"k": k})
        return None
        
    vectorstore = FAISS.from_documents(documents, embeddings)
    
    # Salva para persistência
    os.makedirs(os.path.dirname(index_path), exist_ok=True)
    vectorstore.save_local(index_path)
    
    return vectorstore.as_retriever(search_kwargs={"k": k})
