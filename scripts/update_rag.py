#!/usr/bin/env python3
"""
Script de Ingestão Offline (Batch) para o OCI Copilot RAG.

Este script deve ser rodado periodicamente (ex: via cron) para baixar a documentação,
gerar os embeddings e índices BM25, e persistir os dados no disco (.faiss e .pkl).
Nunca faça ingestão pesada durante o fluxo de conversação da API em produção.
"""

import os
import sys
import time
from pathlib import Path

# Adiciona o diretório raiz ao PYTHONPATH para importar o pacote rag
sys.path.append(str(Path(__file__).resolve().parent.parent))

from rag.config import get_rag_config
from rag.loaders import load_oracle_docs, DEFAULT_OCI_URLS
from rag.splitter import split_with_metadata
from rag.dense_retriever import create_dense_retriever
from rag.sparse_retriever import create_sparse_retriever


def main():
    print("="*50)
    print("🚀 Iniciando Ingestão Offline RAG - OCI Copilot")
    print("="*50)

    # 1. Carregar URLs
    # Em produção, você pode puxar isso de um banco de dados ou arquivo JSON com milhares de links.
    urls_to_ingest = DEFAULT_OCI_URLS
    domain = "general"
    
    print(f"1️⃣  Carregando {len(urls_to_ingest)} documentos OCI base...")
    start_time = time.time()
    try:
        docs = load_oracle_docs(urls_to_ingest, domain)
        print(f"   ✓ {len(docs)} documentos carregados em {time.time() - start_time:.2f}s")
    except Exception as e:
        print(f"   ❌ Erro ao carregar documentos: {e}")
        sys.exit(1)

    # 2. Split (Chunking) com Metadados
    print("\n2️⃣  Realizando o chunking dos documentos...")
    start_time = time.time()
    chunks = split_with_metadata(docs)
    print(f"   ✓ {len(chunks)} chunks gerados em {time.time() - start_time:.2f}s")

    if not chunks:
        print("   ❌ Nenhum chunk gerado. Abortando ingestão.")
        sys.exit(1)

    # 3. Gerar e Persistir Índice Denso (FAISS)
    print("\n3️⃣  Gerando Embeddings e persistindo Índice Denso (FAISS)...")
    start_time = time.time()
    dense_index_path = "data/faiss_index"
    try:
        # A nova função create_dense_retriever já lida com a persistência no disco.
        create_dense_retriever(documents=chunks, index_path=dense_index_path)
        print(f"   ✓ Índice Denso FAISS salvo em '{dense_index_path}' em {time.time() - start_time:.2f}s")
    except Exception as e:
        print(f"   ❌ Erro ao criar índice FAISS: {e}")

    # 4. Gerar e Persistir Índice Esparso (BM25)
    print("\n4️⃣  Gerando e persistindo Índice Esparso (BM25)...")
    start_time = time.time()
    sparse_index_path = "data/bm25_retriever.pkl"
    try:
        # A nova função create_sparse_retriever já lida com a persistência via Pickle.
        create_sparse_retriever(documents=chunks, save_path=sparse_index_path)
        print(f"   ✓ Índice Esparso BM25 salvo em '{sparse_index_path}' em {time.time() - start_time:.2f}s")
    except Exception as e:
        print(f"   ❌ Erro ao criar índice BM25: {e}")

    print("\n" + "="*50)
    print("✅ Ingestão finalizada com sucesso! Os índices estão prontos para uso local.")
    print("="*50)


if __name__ == "__main__":
    main()
