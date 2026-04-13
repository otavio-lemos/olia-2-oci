# RAG Layer - Instalação

## Pré-requisitos

- Python 3.12+
- macOS (Apple Silicon preferencial)

## Instalação

### 1. Criar ambiente virtual

```bash
python -m venv venv-rag
source venv-rag/bin/activate
```

### 2. Instalar dependências

```bash
pip install -r requirements-rag.txt
```

### 3. Variáveis de ambiente (opcional)

```bash
export OCI_EMBEDDING_MODEL="sentence-transformers/all-MiniLM-L6-v2"
export OCI_DOCS_PATH="./data/docs"
```

## Testes

```bash
pytest tests/rag/ -v
```

Todos os 16 testes devem passar.

## Estrutura

```
rag/
├── config.py          # Carrega config YAML
├── loaders.py         # Document loaders
├── splitter.py       # Text splitter
├── dense_retriever.py # FAISS + embeddings
├── sparse_retriever.py# BM25
├── hybrid_retriever.py # RRF fusion
├── tools.py           # LangChain tools
├── api.py             # FastAPI service
└── demo.py            # Demo script
```