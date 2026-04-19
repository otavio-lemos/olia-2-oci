# RAG Layer - Como Utilizar

A camada de RAG utiliza Lazy Loading em RAM para respeitar limites de hardware (como M3 Pro 18GB). A ingestão de dados agora é feita **Offline**.

## 1. Ingestão Offline (Batch)

Sempre rode o script de update para popular os bancos `.faiss` e `.pkl` no disco:

```bash
python scripts/update_rag.py
```

## 2. API FastAPI (Backend)

O backend carrega os índices do disco usando o `lifespan` do FastAPI.

```bash
# Iniciar servidor
uvicorn rag.api:app --host 0.0.0.0 --port 8000

# Testar endpoints
curl -X POST "http://localhost:8000/rag/retrieve" \
  -H "Content-Type: application/json" \
  -d '{"query": "Como criar instance no OCI?", "strategy": "migracao"}'

# Chat com streaming SSE
curl -X POST "http://localhost:8000/rag/chat" \
  -H "Content-Type: application/json" \
  -d '{"query": "Crie uma compute instance"}'
```

## 3. Interface Visual (Frontend OCI Copilot)

A interface do Copilot é construída em **Chainlit** com streaming, anexos de arquivo e botões de aprovação (HITL).

```bash
# Certifique-se que a API está rodando na porta 8000
chainlit run rag/app_chainlit.py --port 8001
```

Acesse: `http://localhost:8001`

## 4. Chat com Streaming SSE (Novo)

O novo endpoint `/rag/chat` suporta streaming de tokens em tempo real:

```python
import requests

response = requests.post(
    "http://localhost:8000/rag/chat",
    json={"query": "Como migrar para OCI?", "temperature": 0.1},
    stream=True
)

for line in response.iter_lines():
    if line:
        print(line.decode())
```

## 5. Session Management

O sistema agora suporta sessões persistidas:

```python
# Criar sessão
session_id = manager.create_session()

# Adicionar mensagem
manager.add_message(session_id, "user", "Olá")
manager.add_message(session_id, "assistant", "Olá! Como posso ajudar?")

# Histórico
history = manager.get_history(session_id, max_messages=10)
```

## 6. Rate Limiting

Rate limiting integrado por usuário:

```python
from rag.rate_limit import create_rate_limiter

limiter = create_rate_limiter(max_requests=10, window_seconds=60)

# Verifica se request é permitido
if limiter.check("user_id"):
    # Prossegue com request
    pass
```

## 7. HITL (Human-in-the-Loop)

Aprovaão humana para comandos destrutivos:

```python
from rag.hitl import create_hitl_checker

checker = create_hitl_checker()

# Verifica se comando requer aprovação
if checker.requires_approval("terminate instance --force"):
    # Pede confirmação ao usuário
    pass
```

## 8. Intent Classification

Classificação automática de intenção:

```python
from rag.intent_router import create_intent_classifier

classifier = create_intent_classifier()
intent = await classifier.classify("Como migrar meus 서버s?")

# Intenções: migracao, troubleshooting, finops, arquitetura, execucao
```

## 9. Query Rewriter

Expansão de query para melhor recall:

```python
from rag.query_rewriter import create_query_rewriter

rewriter = create_query_rewriter()
expansion = await rewriter.rewrite("create compute")

# Expande para múltiplas variações
variations = await rewriter.expand("create compute", num_variations=5)
```

## 10. Logging Estruturado

Logging JSON com trace_id:

```python
from rag.logging_config import JSONLogger, generate_trace_id

logger = JSONLogger()
trace_id = generate_trace_id()

logger.log("INFO", "query_exec", trace_id=trace_id, latency_ms=150)
```

## 11. Métricas

Coleta de métricas P50/P95/P99:

```python
from rag.metrics import get_metrics

metrics = get_metrics()
metrics.record_latency("rag.chat", 0.150)

p95 = metrics.get_percentile("rag.chat", 0.95)
```

## Estratégias e Orquestração

O **LangGraph** (em `rag/orchestrator.py`) gerencia o estado da aplicação:

| Estratégia | Descrição | Pesos (dense, sparse) |
|------------|-----------|---------------------|
| `default` | Hybrid padrão | [0.7, 0.3] |
| `migracao` | Para migração | [0.6, 0.4] |
| `configuracao` | Para config | [0.4, 0.6] |
| `troubleshooting` | Para problemas | [0.5, 0.5] |

## Demo CLI Rápido

```bash
python -m rag.demo
```

## Configuração

Edite `config/oci-copilot-agents.yaml` para personalizar estratégias, prompts de sistema e metadados.

## Testes

```bash
pytest tests/ -v
```

55 testes devem passar.