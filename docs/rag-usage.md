# RAG Layer - Como Utilizar

A camada de RAG utiliza Lazy Loading em RAM para respeitar limites de hardware (como M3 Pro 18GB). A ingestão de dados agora é feita **Offline**.

## 1. Ingestão Offline (Batch)

Sempre rode o script de update para popular os bancos `.faiss` e `.pkl` no disco:

```bash
python scripts/update_rag.py
```

## 2. API FastAPI (Backend)

O backend agora carega os índices do disco usando o `lifespan` do FastAPI.

```bash
# Iniciar servidor
uvicorn rag.api:app --host 0.0.0.0 --port 8000

# Testar endpoint
curl -X POST "http://localhost:8000/rag/retrieve" \
  -H "Content-Type: application/json" \
  -d '{"query": "Como criar instance no OCI?", "strategy": "migracao"}'
```

## 3. Interface Visual (Frontend OCI Copilot)

A interface do Copilot é construída em **Chainlit** para suportar anexos de arquivo, streaming de resposta e botões de aprovação de execução (Human-In-The-Loop). 

*Certifique-se de que a API Backend (FastAPI) esteja rodando na porta 8000 em outro terminal.*

```bash
# Iniciar a UI (com Hot Reload)
chainlit run rag/app_chainlit.py -w
```
**Acesse via navegador em:** `http://localhost:8000` (A porta do Chainlit pode ser a 8000 também por padrão, ajustando a porta original se der conflito).

## Estratégias e Orquestração

O **LangGraph** (em `rag/orchestrator.py`) gerencia o estado da aplicação e usa as estratégias configuradas no YAML.

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

Editar `config/oci-copilot-agents.yaml` para personalizar estratégias, prompts de sistema e metadados.