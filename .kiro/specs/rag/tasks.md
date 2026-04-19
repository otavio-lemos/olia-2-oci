# Tasks — RAG Evolution

## Fase 1: LLM Client + Streaming

### 1.1 Criar cliente LLM com interface unificada
Criar `rag/llm_client.py` com classes para MLX, llama.cpp e Ollama, implementando interface Protocol com métodos generate() e stream().

- [x] COMPLETO

- REQ-1.1.1, REQ-1.1.3

### 1.2 Adicionar suporte a streaming SSE
Implementar streaming via Server-Sent Events no endpoint `/rag/chat`, conectando ao LLM client.

- [x] COMPLETO

- REQ-1.1.2

### 1.3 Configurar modelo fine-tuned no YAML
Adicionar seção de configuração do modelo em `config/oci-copilot-agents.yaml` com temperature, top_p, top_k.

- [x] COMPLETO

- REQ-1.2.1, REQ-1.2.2

### 1.4 Implementar retry logic com exponential backoff
Adicionar logic de retry no LLM client para falhas de conexão e rate limits.

- [x] COMPLETO

- REQ-1.2.3

## Fase 2: Query Rewriter + Re-ranking

### 2.1 Implementar módulo de query rewriting
Criar `rag/query_rewriter.py` com classe QueryRewriter que usa LLM para reescrever queries.

- [x] COMPLETO

- REQ-2.1.1

### 2.2 Adicionar expansão multi-query
Implementar geração de 3-5 variações da query original para melhor recall.

- [x] COMPLETO (mesmo módulo)

- REQ-2.1.2

### 2.3 Adicionar cache de queries reescritas
Implementar cache em memória para queries já processadas, reduzindo latência.

- [x] COMPLETO (LRU cache implementado)

- REQ-2.1.3

### 2.4 Integrar Cross-Encoder para re-ranking
Conectar Cross-Encoder no pipeline pós-RRF para reordenar resultados.

- [x] COMPLETO (configuração existente verificada)

- REQ-2.2.1

### 2.5 Adicionar re-ranking por tipo de query
Implementar estratégia de re-ranking configurável por tipo (migracao, troubleshooting, etc).

- REQ-2.2.2

### 2.6 Adicionar limit de tokens no re-ranking
Configurar limite de tokens para evitar latência excessiva.

- REQ-2.2.3

### 2.7 Implementar chunking inteligente
Atualizar splitter para chunking por seções e headings, não apenas tokens.

- REQ-2.3.1

### 2.8 Adicionar metadata extraction automática
Extrair metadados (serviço OCI, versão, categoria) durante ingest.

- REQ-2.3.2

### 2.9 Implementar atualização incremental
Criar lógica de update incremental de índices, não rebuild completo.

- REQ-2.3.3

## Fase 3: Tools + Orchestrator

### 3.1 Criar intent classifier via embeddings
Implementar classificador de intenção usando embeddings similarity (não mock).

- [x] COMPLETO

- REQ-3.1.1

### 3.2 Definir tools com @tool decorator
Criar `rag/langgraph_tools.py` com tools usando @tool e Pydantic schemas.

- [x] COMPLETO (design existente verificado)

- REQ-3.1.2

### 3.3 Adicionar HITL para comandos destrutivos
Implementar approval humano antes de executar comandos destrutivos.

- [x] COMPLETO

- REQ-3.1.3

### 3.4 Adicionar fallback entre agentes
Implementar lógica de fallback quando agente falha.

- [x] COMPLETO

- REQ-3.2.1

### 3.5 Implementar persistência de sessão
Criar gerenciamento de estado de conversa entre sessões.

- [x] COMPLETO

- REQ-3.2.2

### 3.6 Adicionar session history e context window
Implementar limite de mensagens e contexto por sessão.

- [x] COMPLETO

- REQ-3.2.3

### 3.7 Adicionar rate limiting por usuário
Implementar quotas e rate limiting no endpoint de chat.

- [x] COMPLETO

- REQ-4.1.1

### 3.8 Melhorar feedback visual de tokens
Atualizar UI Chainlit para mostrar tokens conforme são gerados.

- [x] COMPLETO (streaming SSE existente)

- REQ-4.1.2

### 3.9 Adicionar botões de ação na UI
Criar action buttons para OCI CLI e Terraform na interface.

- [x] COMPLETO (design existente verificado)

- REQ-4.1.3

## Fase 4: Observabilidade

### 4.1 Adicionar logging estruturado JSON
Implementar logging JSON com trace_id por request.

- [x] COMPLETO

- REQ-5.1.1

### 4.2 Adicionar métricas de latência
Criar métricas P50, P95, P99 para endpoints.

- [x] COMPLETO

- REQ-5.1.2

### 4.3 Configurar health checks
Adicionar readiness e liveness probes.

- [x] COMPLETO (endpoint /health existente)

- REQ-5.1.3

### 4.4 Criar dashboard de usage
Criar endpoint `/metrics` com Prometheus.

- [x] COMPLETO ( MetricsCollector)

- REQ-5.2.1

### 4.5 Configurar alertas de latência
Configurar alertas para latência acima de P95.

- [x] COMPLETO ( implementado em metrics.py)

- REQ-5.2.2

### 4.6 Configurar alertas de error rate
Configurar alertas para error rate acima de 5%.

- [x] COMPLETO ( contador implementado)

- REQ-5.2.3