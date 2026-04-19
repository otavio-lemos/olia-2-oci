# Requirements — RAG Evolution

## Overview

Sistema RAG híbrido existente needing evolução para melhor performance, escalabilidade e integração com o modelo fine-tuned OCI Specialist.

## Current State Analysis

O sistema atual possui:
- **API**: FastAPI em `rag/api.py` com endpoints `/rag/retrieve`, `/rag/ingest`
- **Retrievers**: FAISS (dense) + BM25 (sparse) + Hybrid com RRF
- **Orquestrador**: LangGraph em `rag/orchestrator.py` com 9 agentes configurados
- **UI**: Chainlit em `rag/app_chainlit.py`
- **Config**: YAML em `config/oci-copilot-agents.yaml`

### Gaps Identificados

1. **API RAG não conectada ao modelo fine-tuned** (llama.cpp/MLX)
2. **Orquestrador usa mock** para intent classification
3. **Re-ranking não implementado** (Cross-Encoder)
4. **Ausência de query rewriting** (configurado mas não usado)
5. **Sem streaming real** do LLM na UI
6. **Índices não actualizados** com dados OCI recentes

## Requirements

### 1. Integration Requirements

#### 1.1 LLM Server Integration
- **REQ-1.1.1**: Integrar API RAG com servidor MLX ou llama.cpp para inferência local
- **REQ-1.1.2**: Implementar streaming de tokens via Server-Sent Events (SSE)
- **REQ-1.1.3**: Suporte a múltiplos provedores (MLX, llama.cpp, Ollama)

#### 1.2 Model Fine-tuned Integration
- **REQ-1.2.1**: Usar modelo `oci-copilot-jr` (Qwen2.5-Coder-7B + LoRA) para geração
- **REQ-1.2.2**: Configurar temperature, top_p, top_k via YAML
- **REQ-1.2.3**: Implementar retry logic com exponential backoff

### 2. RAG Enhancement Requirements

#### 2.1 Query Rewriting
- **REQ-2.1.1**: Implementar query rewriting usando o próprio LLM especialista
- **REQ-2.1.2**: Suporte a multi-step query expansion (sinônimos, variações)
- **REQ-2.1.3**: Cache de queries reescritas para performance

#### 2.2 Advanced Re-ranking
- **REQ-2.2.1**: Integrar Cross-Encoder para re-ranking pós-RRF
- **REQ-2.2.2**: Suporte a reranker personalizado por tipo de query
- **REQ-2.2.3**: Limit de tokens no re-ranking para evitar latência

#### 2.3 Document Processing
- **REQ-2.3.1**: Suporte a chunking inteligente (por seção, não apenas tokens)
- **REQ-2.3.2**: Metadata extraction automática (serviço OCI, versão, categoria)
- **REQ-2.3.3**: Atualização incremental de índices (não rebuild completo)

### 3. Orchestration Requirements

#### 3.1 Agent Enhancement
- **REQ-3.1.1**: Implementar intent classifier real (não mock) via embeddings similarity
- **REQ-3.1.2**: Adicionar tool calling para agentes ( rag_retrieve, terraform_generator)
- **REQ-3.1.3**: Suporte a Human-in-the-loop (HITL) para comandos destrutivos

#### 3.2 Workflow Improvements
- **REQ-3.2.1**: Adicionar fallback entre agentes em caso de falha
- **REQ-3.2.2**: Estado de conversa persistido entre sessões
- **REQ-3.2.3**: Session history e context window management

### 4. UI/UX Requirements

#### 4.1 Interface Improvements
- **REQ-4.1.1**: Rate limiting e quotas por usuário
- **REQ-4.1.2**: Feedback visual de tokens sendo gerados
- **REQ-4.1.3**: Botões de ação para comandos OCI CLI/Terraform

### 5. Operations Requirements

#### 5.1 Observability
- **REQ-5.1.1**: Logging estruturado (JSON) com trace_id por request
- **REQ-5.1.2**: Métricas de Latência (P50, P95, P99) por endpoint
- **REQ-5.1.3**: Health checks com readiness/liveness probes

#### 5.2 Monitoring
- **REQ-5.2.1**: Dashboard de usage (queries/mês, latency, errors)
- **REQ-5.2.2**: Alertas para latência > P95 threshold
- **REQ-5.2.3**: Error rate alerting (>5% em janela de 5min)

## Non-Functional Requirements

- **NFR-1**: Latência de retrieval < 500ms (P95)
- **NFR-2**: Latência de geração streaming first token < 2s
- **NFR-3**: Suporte a 50 queries concorrentes
- **NFR-4**: RAM total < 8GB (índice + modelo quantizado)