# RAG Layer - Instalação

## Pré-requisitos

- Python 3.12+
- macOS (Apple Silicon preferencial)
- M3 Pro recomendado (18GB RAM)

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

### 3. Nova Instalação de Dependências (Obrigatório)

O sistema agora incluye dependências adicionais para testing:

```bash
# pytest-asyncio é obrigatório para testes
pip install -r requirements-rag.txt
```

 Verifique que `requirements-rag.txt` inclui:
- `pytest-asyncio>=0.24.0`
- `python-multipart>=0.0.6`

### 4. Ingestão Base de Dados (Obrigatório)

A arquitetura usa Lazy Loading em disco. Gere os índices **antes** de subir o servidor:

```bash
python scripts/update_rag.py
```

Isto gerará os arquivos `.faiss` e `.pkl` na pasta `data/`.

### 5. Variáveis de ambiente (opcional)

```bash
export OCI_EMBEDDING_MODEL="sentence-transformers/all-MiniLM-L6-v2"
export OCI_DOCS_PATH="./data/docs"
```

## Testes

```bash
pytest tests/ -v
```

Todos os 55 testes devem passar.

## Estrutura Completa

```
rag/
├── api.py              # FastAPI com streaming SSE
├── llm_client.py       # MLX/llama.cpp/Ollama clients
├── query_rewriter.py   # Query expansion com cache
├── intent_router.py    # Intent classification
├── hitl.py            # Human-in-the-loop checker
├── session.py         # Session manager
├── rate_limit.py      # Rate limiter
├── logging_config.py # Structured JSON logging
├── metrics.py         # Metrics P50/P95/P99
├── config.py          # Carrega config YAML
├── loaders.py         # Document loaders
├── splitter.py         # Text splitter
├── dense_retriever.py # FAISS
├── sparse_retriever.py# BM25
├── hybrid_retriever.py# RRF fusion + Cross Encoder
├── tools.py           # LangChain tools
├── orchestrator.py   # LangGraph agent
├── app_chainlit.py   # Chainlit UI
└── demo.py           # Demo script
```

## Configuração

Edite `config/oci-copilot-agents.yaml`:

```yaml
llm:
  model_path: "outputs/cycle-1/gguf/oci-specialist-Q4_K_M.gguf"
  adapter_path: "outputs/cycle-1/adapters"
  temperature: 0.1
  top_p: 0.9
  top_k: 40
  max_tokens: 2048
  provider: "llama.cpp"
  streaming: true
```

## Endpoints

| Endpoint | Descrição |
|----------|-----------|
| `/rag/retrieve` | Retrieval híbrido |
| `/rag/chat` | Chat com streaming SSE |
| `/rag/ingest` | Ingestão de documentos |
| `/health` | Health check |
| `/workflows` | Lista workflows |