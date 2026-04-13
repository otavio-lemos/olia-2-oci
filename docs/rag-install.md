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
pip install langgraph chainlit
```

### 3. Ingestão Base de Dados (Importante)
A arquitetura nova usa Lazy Loading e salva em disco. Você precisa gerar os índices **antes** de subir o servidor:

```bash
python scripts/update_rag.py
```
*(Isto gerará os arquivos `.faiss` e `.pkl` na pasta `data/`)*

### 4. Variáveis de ambiente (opcional)

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

```text
rag/
├── config.py          # Carrega config YAML
├── loaders.py         # Document loaders
├── splitter.py        # Text splitter
├── dense_retriever.py # FAISS + embeddings (persistido em disco)
├── sparse_retriever.py# BM25 (persistido em disco)
├── hybrid_retriever.py# RRF fusion + Cross Encoder
├── tools.py           # LangChain tools
├── api.py             # FastAPI service
├── app_chainlit.py    # UI Frontend Chainlit
├── orchestrator.py    # Máquina de estados LangGraph
└── demo.py            # Demo script
```