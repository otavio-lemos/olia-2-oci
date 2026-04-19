# Research Log — RAG Evolution

## Resumo

Evolução do sistema RAG existente para integração com modelo fine-tuned OCI Specialist.

## Escopo

- Integração com LLM local (MLX/llama.cpp)
- Query rewriting e re-ranking
- melhoramento de orchestration com tools
- Observabilidade

## Pesquisa Realizada

### 1. Query Rewriting Patterns

**Fontes**:
- DEV Community: "Query Rewrite in RAG Systems" (2026)
- Medium: "RAG in 2025" (2025)
- RAG About It: "Query Rewriting Revolution" (2025)

**Descobertas**:
1. **Multi-Query Retrieval**: Gera 3-7 variações da query via LLM, executa retrieval em paralelo. Piora latência ~80-120ms mas melhora precision 25-50%.
2. **Query Decomposition**: Questões complexas são divididas em sub-queries
3. **Domain-aware Normalization**: Traduz terminologia usuário → linguagem do domínio
4. **HyDE (Hypothetical Document Embeddings)**: LLM gera resposta hipotética para buscar no índice

**Implicações para Design**:
- Implementar query rewriting como layer separado
- Usar cache para 70-80% das queries (pre-computed)
- Retrieval paralelo para múltiplas variações

### 2. LangGraph Tool Calling

**Fontes**:
- Abstract Algorithms: "LangGraph Tool Calling" (2026)
- SitePoint: "Tools-First Pattern" (2026)
- Crewship: "Building Agents with LangGraph" (2026)

**Descobertas**:
1. **@tool decorator** + **bind_tools()** + **ToolNode** + **tools_condition**: padrão completo
2. **Tools-first pattern**: Definir schemas Pydantic ANTES de escrever lógica
3. **Parallel execution**: ToolNode executa múltiplas tools em paralelo (reduz latência ~40%)
4. **Recursion limit**: Prevenir loops infinitos

**Implicações para Design**:
- Migrar de orchestrator mock para tools-first LangGraph
- Definir Pydantic schemas para todas as tools
- Usar create_react_agent como base

### 3. RAG Architecture 2025

**Fontes**:
- Medium: "RAG in 2025: From Quick Fix to Core Architecture" (2025)

**Descobertas**:
1. **Hybrid retrieval**: Dense (semantic) + Sparse (keyword) + Re-ranking
2. **Metadata-forward indexing**: Filtrar por source, date, authority
3. **Chunking por limites semânticos**: Seções, headings, não apenas tokens
4. **Prompt contracts**: Standardizar templates, citation requirements
5. **Guarded generation**: Verifiers que validam claims contra retrieved docs

**Implicações para Design**:
- Implementar chunking inteligente (não só overlap fixo)
- Adicionar metadata extraction automática
- Estruturar prompt com "no evidence, no answer"

## Decisões de Arquitetura

### Stack Confirmado
- **Framework**: LangGraph com @tool + ToolNode
- **LLM**: MLX/llama.cpp com streaming SSE
- **Query rewriting**: LLM-based com cache
- **Re-ranking**: Cross-Encoder (sentence-transformers)
- **Chunking**: Structure-aware (headings, seções)

### Riscos Identificados
1. **Latência**: Query rewriting adiciona 80-200ms → mitigado com cache
2. **Memory**: Contexto longo pode exceder window → chunking inteligente
3. **Tool loops**: Hallucination → recursion limit + tools-first

### Integrações Necessárias
1. API RAG → Servidor MLX/llama.cpp
2. Orchestrator → Tools-first pattern
3. UI → Streaming SSE real