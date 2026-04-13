# RAG Layer - Como Utilizar

## Quick Start

```python
from rag.tools import create_rag_tool
from rag.loaders import load_oci_docs

# Carregar documentos
docs = load_oci_docs("./data/docs")

# Criar RAG tool
rag_tool = create_rag_tool(docs)

# Usar como tool LangChain
result = rag_tool.invoke("Como migrar de AWS para OCI?")
print(result)
```

## API FastAPI

```bash
# Iniciar servidor
python -m rag.api

# Testar endpoint
curl -X POST "http://localhost:8000/rag" \
  -H "Content-Type: application/json" \
  -d '{"query": "Como criar instance no OCI?", "strategy": "migracao"}'
```

## Estratégias de Retrieval

| Estratégia | Descrição | Pesos (dense, sparse) |
|------------|-----------|---------------------|
| `default` | Hybrid padrão | [0.7, 0.3] |
| `migracao` | Para migração | [0.6, 0.4] |
| `configuracao` | Para config | [0.4, 0.6] |
| `troubleshooting` | Para problemas | [0.5, 0.5] |

## Demo

```bash
python -m rag.demo
```

## Configuração

Editar `config/oci-copilot-agents.yaml` para personalizar estratégias.