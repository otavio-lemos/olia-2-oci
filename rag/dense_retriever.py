"""Dense retriever usando FAISS."""

from typing import List
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document


def create_dense_retriever(
    documents: List[Document],
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
    k: int = 20,
):
    """Cria dense retriever com embeddings."""
    if not documents:
        return None
    embeddings = HuggingFaceEmbeddings(model_name=embedding_model)
    vectorstore = FAISS.from_documents(documents, embeddings)
    return vectorstore.as_retriever(search_kwargs={"k": k})
