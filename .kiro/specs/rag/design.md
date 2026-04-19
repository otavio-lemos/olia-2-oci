# Technical Design — RAG Evolution

## Visão Geral do Documento

Este documento define a arquitetura técnica para evolução do sistema RAG existente, integrando o modelo fine-tuned OCI Specialist e melhorando a performance de retrieval e orchestration.

---

## 1. Arquitetura e Padrões

### 1.1 Arquitetura de Alto Nível

```mermaid
flowchart TD
    subgraph CLIENT["Client Layer"]
        UI[Chainlit UI]
        API[FastAPI]
    end

    subgraph RETRIEVAL["Retrieval Layer"]
        QR[Query Rewriter]
        IR[Intent Router]
        Dense[FAISS Dense]
        Sparse[BM25 Sparse]
        RRF[RRF Fusion]
        CrossR[Cross-Encoder Reranker]
    end

    subgraph ORCHESTRATION["Orchestration Layer"]
        Router[Router Agent]
        Tools[Tool Node]
        Agents[Specialist Agents]
    end

    subgraph LLM["Generation Layer"]
        LLM[MLX/llama.cpp]
        Stream[SSE Stream]
    end

    UI --> API
    API --> QR
    QR --> IR
    IR --> Dense
    IR --> Sparse
    Dense --> RRF
    Sparse --> RRF
    RRF --> CrossR
    CrossR --> Router
    Router --> Tools
    Tools --> Agents
    Agents --> LLM
    LLM --> Stream
    Stream --> UI

    style LLM fill:#e8f5e9
    style RETRIEVAL fill:#e3f2fd
    style ORCHESTRATION fill:#f3e5f5
```

### 1.2 Componentes e Responsabilidades

| Componente | Responsabilidade | Localização |
|-----------|-----------------|-------------|
| `QueryRewriter` | Expande/reescreve queries via LLM | `rag/query_rewriter.py` |
| `IntentRouter` | Classifica intenção e roteia estratégia | `rag/intent_router.py` |
| `HybridRetriever` | RRF fusion + re-ranking | `rag/hybrid_retriever.py` (existente) |
| `LangGraphAgent` | Tools-first orchestration | `rag/orchestrator.py` (evoluir) |
| `LLMClient` | Interface com MLX/llama.cpp | `rag/llm_client.py` (novo) |
| `StreamingHandler` | SSE para streaming de tokens | `rag/streaming.py` (novo) |

### 1.3 Fluxo de Execução

1. **Query Received**: Usuário envia mensagem via Chainlit UI
2. **Query Rewriting**: LLM gera 3-5 variações da query (cacheado)
3. **Intent Classification**: Router determina estratégia (hybrid, dense, sparse)
4. **Parallel Retrieval**: Executa dense + sparse em paralelo
5. **RRF Fusion**: Combina resultados com pesos configuráveis
6. **Re-ranking**: Cross-Encoder reordena top-K
7. **Tool Calling**: LangGraph determina se precisa de tools
8. **Generation**: LLM gera resposta com contexto
9. **Streaming**: Tokens enviados via SSE

---

## 2. Stack Tecnológico

### 2.1 Tecnologias Existentes

| Componente | Tecnologia Atual | Papel |
|-----------|---------------|-------|
| Retrieval | FAISS + BM25 | Dense + Sparse |
| Orchestration | LangGraph (mock) | Máquina de estados |
| API | FastAPI |Backend |
| UI | Chainlit | Interface |

### 2.2 Novas Integrações

| Componente | Tecnologia | Propósito |
|-----------|----------|----------|
| LLM Server | MLX ou llama.cpp | Inferência local |
| Query Rewrite | LLM (mesmo modelo) | Expansão de queries |
| Reranker | Cross-Encoder | Re-rank |
| Streaming | Server-Sent Events | Token streaming |

### 2.3 Align com Steering

O design respeita:
- **Stack Python 3.12**:alongy
- **Módulos em `rag/`**:alongy
- **Configuração em YAML**:alongy
- **Outputs timestamped**:alongy

---

## 3. Interfaces e Contratos

### 3.1 Interface LLM Client

```python
from typing import AsyncIterator

class LLMClient(Protocol):
    """Interface para provedores de LLM local."""
    
    async def generate(
        self,
        prompt: str,
        context: list[Document],
        system_prompt: str | None = None,
        temperature: float = 0.1,
        max_tokens: int = 2048,
    ) -> str:
        """Gera resposta síncrona."""
        ...
    
    async def stream(
        self,
        prompt: str,
        context: list[Document],
        system_prompt: str | None = None,
    ) -> AsyncIterator[str]:
        """Gera resposta com streaming de tokens."""
        ...
```

### 3.2 Interface Query Rewriter

```python
from typing import TypedDict

class QueryExpansion(TypedDict):
    """Resultado da expansão de query."""
    original: str
    expanded: list[str]
    intent: str
    entities: list[str]

class QueryRewriter(Protocol):
    """Interface para reescrita de queries."""
    
    async def rewrite(
        self,
        query: str,
        intent: str | None = None,
    ) -> QueryExpansion:
        """Reescreve e expande query."""
        ...
    
    async def expand(
        self,
        query: str,
        num_variations: int = 5,
    ) -> list[str]:
        """Gera variações da query."""
        ...
```

### 3.3 Interface Tool Definitions

```python
from langchain_core.tools import tool
from pydantic import BaseModel, Field

class RetrieveInput(BaseModel):
    """Schema para tool de retrieval."""
    query: str = Field(description="Query de busca")
    k: int = Field(default=10, description="Número de documentos")
    strategy: str | None = Field(default=None, description="Estratégia override")

@tool(args_schema=RetrieveInput)
def rag_retrieve(query: str, k: int = 10, strategy: str | None = None) -> list[dict]:
    """Recupera documentos relevantes do knowledge base OCI."""
    ...

@tool
def generate_terraform(resource: str, compartment_id: str) -> str:
    """Gera código Terraform para recurso OCI."""
    ...

@tool
def validate_terraform(code: str) -> dict:
    """Valida código Terraform com OCI CLI."""
    ...
```

### 3.4 API Endpoints

| Método | Endpoint | Descrição |
|--------|----------|----------|
| `POST` | `/rag/chat` | Chat com streaming SSE |
| `POST` | `/rag/query` | Query única (sync) |
| `GET` | `/health` | Health check |
| `GET` | `/metrics` | Métricas Prometheus |

---

### 3.5 Chat Endpoint Schemas

```python
from typing import Literal
from pydantic import BaseModel, Field

class ChatMessage(BaseModel):
    """Mensagem individual no chat."""
    role: Literal["user", "assistant", "system"] = Field(description="Papel da mensagem")
    content: str = Field(description="Conteúdo da mensagem")
    timestamp: str | None = Field(default=None, description="Timestamp ISO 8601")

class ChatRequest(BaseModel):
    """Request para endpoint de chat."""
    messages: list[ChatMessage] = Field(description="Histórico de mensagens")
    session_id: str | None = Field(default=None, description="Session ID para continuidade")
    temperature: float = Field(default=0.1, ge=0.0, le=2.0)
    max_tokens: int = Field(default=2048, ge=1, le=8192)
    strategy: str | None = Field(default=None, description="Estratégia RAG override")

class StreamChunk(BaseModel):
    """ Chunk enviado via SSE."""
    token: str = Field(description="Token gerado")
    done: bool = Field(description="Se é o último chunk")
    citations: list[dict] = Field(default_factory=list, description="Citações dos docs")

class ChatResponse(BaseModel):
    """Response final do chat."""
    session_id: str = Field(description="Session ID")
    citations: list[dict] = Field(description="Docs utilizados")
    total_tokens: int = Field(description="Total de tokens gerados")

### 3.6 Session Management

| Campo | Tipo | Descrição |
|-------|------|----------|
| `session_id` | str | UUID gerado no primeiro request |
| `history` | list[ChatMessage] | Últimas 10 mensagens |
| `context_docs` | list[Document] | Docs retrievados recently |
| `expires_at` | datetime | TTL = 30min inactivity |

---

## 4. Componentes a Implementar

### 4.1 Query Rewriter Module

**Arquivo**: `rag/query_rewriter.py`

| Função | Descrição |
|-------|----------|
| `QueryRewriter` | Classe principal com cache |
| `expand_query()` | Gera 3-5 variações |
| `classify_intent()` | Classifica tipo de query |
| `apply_hyde()` | HyDE para queries complexas |

### 4.2 LLM Client Module

**Arquivo**: `rag/llm_client.py`

| Função | Descrição |
|-------|----------|
| `MLXClient` | Client para MLX |
| `LlamaCppClient` | Client para llama.cpp |
| `OllamaClient` | Client para Ollama |
| `StreamingHandler` | Handler SSE |

### 4.3 Tools Definitions

**Estratégia de Migração**: Criar novo módulo `rag/langgraph_tools.py` para tools-first, manter `rag/tools.py` existente para compatibilidade.

**Arquivo novo**: `rag/langgraph_tools.py`

| Tool | Descrição | Args |
|------|----------|------|
| `rag_retrieve` | Recupera docs | query, k, strategy |
| `generate_terraform` | Gera TF | resource, compartment |
| `validate_tf` | Valida TF | code |
| `generate_oci_cli` | Gera CLI | command |
| `list_compartments` | Lista compartments | - |

**Nota de Migração**:
- `from rag.tools import RAGTool` → manter para backward compatibility
- `from rag.langgraph_tools import rag_retriever_tool` → novo @tool decorator

### 4.4 Orchestrator Evolution

**Arquivo**: `rag/orchestrator.py` (evoluir)

| Mudança | De | Para |
|--------|----|------|
| Router | Mock | Embedding similarity |
| Tools | Não definidas | Tools-first (@tool) |
| Execution | String matching | ToolNode + should_continue |
| Context | Não persistido | Session + history |

### 4.5 API Evolution

**Arquivo**: `rag/api.py` (evoluir)

| Endpoint |Mudança |
|----------|--------|
| `/rag/retrieve` | Manter |
| `/rag/ingest` | Manter |
| `/rag/chat` | Novo (SSE streaming) |
| `/health` | Adicionar liveness |

---

## 5. Observabilidade

### 5.1 Métricas

| Métrica | Tipo | Descrição |
|--------|------|----------|
| `rag.query.latency_p50` | Histogram | Latência P50 |
| `rag.query.latency_p95` | Histogram | Latência P95 |
| `rag.query.latency_p99` | Histogram | Latência P99 |
| `rag.retrieval.hits` | Counter | Docs retrieved |
| `rag.retrieval.latency` | Histogram | Tempo retrieval |
| `rag.llm.tokens` | Counter | Tokens gerados |
| `rag.errors` | Counter | Erros por tipo |

### 5.2 Logging

- **Formato**: JSON estruturado
- **Trace ID**: Por request (header `x-trace-id`)
- **Campos**: timestamp, level, trace_id, component, action, latency_ms

---

## 6. Rastreabilidade de Requisitos

| ID | Requisito | Componente |
|----|----------|-----------|
| REQ-1.1.1 | LLM Server Integration | `llm_client.py` |
| REQ-1.1.2 | Streaming SSE | `streaming.py` |
| REQ-1.1.3 | Multi-provider | `llm_client.py` |
| REQ-2.1.1 | Query rewriting | `query_rewriter.py` |
| REQ-2.1.2 | Multi-query | `query_rewriter.py` |
| REQ-2.2.1 | Re-ranking | `hybrid_retriever.py` |
| REQ-3.1.1 | Intent classifier | `intent_router.py` |
| REQ-3.1.2 | Tool calling | `tools.py` |
| REQ-5.1.1 | Structured logging | Middleware |

---

## 7. Riscos e Mitigações

| Risco | Probabilidade | Impacto | Mitigação |
|-------|--------------|---------|----------|
| Latência query rewrite | Alta | Médio | Cache 80% das queries |
| Tool loop infinito | Média | Alto | Recursion limit |
| Memory overflow | Média | Alto | Chunking inteligente |
| Model OOM | Baixa | Alto | Quantização Q4 |

---

## 8. Ordem de Implementação

1. **Fase 1**: LLM Client + Streaming (infraestrutura básica)
2. **Fase 2**: Query Rewriter (performance)
3. **Fase 3**: Tools + Orchestrator (funcionalidade)
4. **Fase 4**: Observabilidade (operações)