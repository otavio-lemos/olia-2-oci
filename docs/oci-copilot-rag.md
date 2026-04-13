# OCI Copilot – Documentação de Implantação da Camada de RAG

Este documento descreve como implantar e operar a camada de Retrieval-Augmented Generation (RAG) do OCI Copilot, alinhada com a configuração em `config/oci-copilot-agents.yaml`. O objetivo é fornecer um guia de ponta a ponta: desde a ingestão de documentos até a integração com os agentes e workflows do copilot.

---

## 1. Visão geral da arquitetura de RAG

A camada de RAG do OCI Copilot segue um modelo **híbrido + agentic**:

- **Híbrido (dense + sparse)**:
  - Índice vetorial para recuperação semântica (perguntas em linguagem natural, equivalência de serviços, padrões de migração).
  - Índice esparso (BM25/FTS) para recuperação lexical precisa (nomes de serviços, flags de CLI, parâmetros Terraform, códigos de erro).
  - Fusão via **Reciprocal Rank Fusion (RRF)**, com pesos configuráveis para denso/esparso.
- **Re‑ranking semântico**: modelo cross‑encoder opcional que reordena os top‑K documentos mais relevantes.
- **Query rewriting**: o próprio LLM especialista reescreve a query para maximizar a qualidade do retrieval, adicionando termos técnicos e nomes de serviços relevantes.
- **Agentic RAG**: os agentes (migracao, arquitetura, configuracao, etc.) consomem a camada de RAG via uma tool `rag_retrieve`, respeitando filtros de metadados e estratégias específicas por tipo de fluxo.

Toda a parametrização dessa arquitetura está centralizada em `rag` dentro de `config/oci-copilot-agents.yaml`.

---

## 2. Fontes de dados e ingestão

### 2.1 Fontes de documentos

As principais fontes que devem ser ingeridas no índice de RAG são:

- **Documentação oficial de OCI** (Content home, serviços específicos, guias de migração, whitepapers, best practices).
- **Guias de migração multi‑cloud → OCI** (AWS/Azure/GCP/On‑prem), incluindo blogs e tutoriais da Oracle.
- **Exemplos oficiais de Terraform do provider OCI** (módulos e snippets).
- **Referência de CLI** para `oci` (man pages, exemplos de uso).
- **Blogs técnicos internos** e runbooks corporativos (quando aplicável).

### 2.2 Pipeline de ingestão

Passos recomendados para o pipeline de ingestão:

1. **Coleta**
   - Crawlers para docs web (HTML), download de PDFs, clone de repositórios com exemplos Terraform/CLI.
   - Normalização de encoding e remoção de markup irrelevante.
2. **Segmentação (chunking)**
   - Particionar documentos em unidades de conhecimento:
     - Blocos de how‑to (passos completos).
     - Blocos de referência (tabelas de parâmetros, opções, limites).
     - Blocos de padrões arquiteturais (diagramas, descrições textuais).
   - Evitar chunking cego por tokens; usar heurísticas baseadas em títulos, seções e listas.
3. **Enriquecimento de metadados**
   - Atribuir metadados coerentes com o YAML:
     - `domain` (architecture, migration, security, governance, networking, finops, troubleshooting, observability, operations, devops, etc.).
     - `cloud_provider` (aws, azure, gcp, onprem, oci).
     - `doc_type` (reference, how-to, example, best-practices, runbook).
     - `service` (compute, vcn, oke, autonomous, object-storage, etc.).
   - Esse enriquecimento é crítico para filtros como os usados por agentes `migracao`, `configuracao_seg`, `finops`.
4. **Indexação sparse**
   - Enviar cada chunk para o índice BM25 (Elasticsearch/OpenSearch/Meilisearch ou Postgres FTS), definindo campos full‑text e campos de metadados.
5. **Indexação dense**
   - Gerar embeddings com o modelo `oci-specialist-embedding-v1` e indexar em um banco vetorial (FAISS, Qdrant, PGVector, etc.), guardando os mesmos metadados.

O pipeline deve ser agendado (por exemplo, cron/Job em Kubernetes) para rodar periodicamente e capturar atualizações na documentação, especialmente para serviços em rápida evolução.

---

## 3. Índices dense e sparse

### 3.1 Índice dense

Configuração padronizada (conforme YAML):

- Modelo de embedding: `oci-specialist-embedding-v1`.
- Nome do índice: `oci_docs_dense_index`.
- Top‑K padrão: 20 documentos antes da fusão.

Boas práticas:
- Garantir que o modelo de embedding seja treinado/ajustado para linguagem técnica de cloud (PT‑BR/EN) para maximizar recall semântico.
- Armazenar apenas IDs e metadados leves no índice vetorial; o texto completo pode ficar em um storage separado, referenciado por ID.

### 3.2 Índice sparse

Configuração (YAML):

- Engine: `elasticsearch` (ou equivalente).
- Índice: `oci_docs_sparse_index`.
- Top‑K padrão: 40 documentos antes da fusão.

Boas práticas:
- Mapear campos com analyzers consistentes, preservando tokens técnicos (nomes de recursos, flags, códigos).
- Habilitar filtros e facetas pelos mesmos metadados dos embeddings (domain, cloud_provider, doc_type, service).

---

## 4. Estratégia de retrieval híbrido

### 4.1 Fluxo de consulta

Para cada chamada à tool `rag_retrieve`, o fluxo é:

1. **Query rewriting (opcional)**
   - O LLM reescreve a query original em uma forma otimizada para retrieval, usando o `system_prompt` definido em `rag.query_rewriting.system_prompt`.
2. **Aplicação de filtros de metadados**
   - Com base no agente e no tipo de workflow, selecionar filtros de `domain`, `cloud_provider`, `doc_type`, etc., conforme `metadata_filters` do agente em `config/oci-copilot-agents.yaml`.
3. **Busca dense**
   - Rodar a query reescrita no índice `oci_docs_dense_index` com `top_k` configurado (padrão 20, 30 para migração).
4. **Busca sparse**
   - Rodar a mesma query (ou eventualmente versão não reescrita) no índice `oci_docs_sparse_index` com `top_k` configurado (padrão 40, 60 para migração).
5. **Fusão (RRF)**
   - Combinar os resultados com método `rrf` (Reciprocal Rank Fusion), pesando `dense_weight` e `sparse_weight` conforme YAML (por exemplo, 0.7/0.3 global, 0.6/0.4 para migração, 0.4/0.6 para configuração).
6. **Re‑ranking (opcional)**
   - Se `re_ranking.enabled` for `true`, aplicar o modelo `oci-migration-cross-encoder-v1` sobre os top‑K para reordená‑los (especialmente útil em migração e troubleshooting).
7. **Retorno para o agente**
   - Entregar ao agente N documentos (por exemplo, top 10) com texto e metadados, para serem usados no contexto do LLM.

### 4.2 Overrides por tipo

O bloco `rag.by_type` no YAML permite overrides por scenario:

- `migracao`:
  - `dense.top_k` maior (30) e `sparse.top_k` maior (60) para garantir abrangência em migrações complexas.
  - Peso um pouco maior para dense (0.6) para priorizar semântica.
- `configuracao`:
  - Peso maior para sparse (0.6), já que muitos pedidos são sobre parâmetros e flags exatas.
- `troubleshooting`:
  - `re_ranking.enabled: true` e top‑K ajustado para trazer mais casos de incidentes relevantes.

---

## 5. Integração com agentes e workflows

Cada agente no YAML declara:
- **tools** incluindo `rag_retrieve`.
- **rag_strategy** (dense/hybrid).
- **metadata_filters** (domain, cloud_provider, doc_type) que ajustam o escopo da busca.

Exemplos:

- Agente `migracao`:
  - `rag_strategy: hybrid`, filtros `domain: ["migration"]` e `cloud_provider` origem.
  - Usa RAG para buscar padrões e guias de migração específicos (ex.: RDS → Autonomous, EKS → OKE).
- Agente `configuracao_seg`:
  - Focado em `domain: ["security", "governance", "networking"]`, ponderando mais sparse para pegar políticas/flags exatas.
- Agente `finops`:
  - Filtros `domain: ["finops", "cost-optimization"]`, com queries que podem combinar docs de boas práticas e APIs de pricing.

Os workflows (migracao, arquitetura, configuracao, etc.) definem a ordem em que esses agentes são chamados, e cada chamada pode envolver múltiplos ciclos de RAG dependendo da complexidade da tarefa.

---

## 6. Implantação da infraestrutura

### 6.1 Ambiente de desenvolvimento local (M3 Pro 18GB)

Componentes mínimos desenhados para respeitar a RAM local:

- **Vector DB e Sparse Engine Persistidos** (`.faiss` e `.pkl`) criados via Ingestão Offline (`scripts/update_rag.py`). Sem containers Docker pesados.
- **Serviço de RAG (Backend)** (`rag/api.py`):
  - Carrega `config/oci-copilot-agents.yaml` e os índices do disco usando FastAPI Lifespan.
  - Expõe endpoint HTTP/JSON `/rag/retrieve` em `localhost:8000`.
- **Frontend / UI do Copilot** (`rag/app_chainlit.py`):
  - Interface Chainlit com Human-In-The-Loop e Chain of Thought.
- **Orquestrador de Workflow** (`rag/orchestrator.py`):
  - Máquina de Estados **LangGraph** para transitar entre os agentes (Router -> Execucao, etc).
- **LLM servidor**: Inferência com `mlx_lm` ou `llama.cpp` apontando para o modelo fine‑tuned local (`oci-specialist-Q4_K_M.gguf`).

### 6.2 Ambiente de produção (exemplo em OCI)

- Deploy do **RAG Service** em OKE ou OKE Autonômico.
- **Vector DB** e **sparse engine** gerenciados (ou auto‑gerenciados) em OCI ou em infra escolhida pelo projeto.
- Rede com segurança adequada (VCN, NSGs, LB) e acesso controlado a fontes de dados.
- Observabilidade via OCI Logging/Monitoring para métricas de latência, taxas de acerto, erros de indexação, etc.

---

## 7. Observabilidade, qualidade e evolução

### 7.1 Logging e métricas

- Logar queries reescritas, filtros de metadados, documentos retornados (IDs) e scores.
- Métricas chave:
  - Taxa de cliques ou selects em docs retornados.
  - Latência por estágio (dense, sparse, fusão, re‑ranking).
  - Cobertura por domínio (quantos docs por domain/cloud_provider são utilizados).

### 7.2 Avaliação offline

- Conjunto de perguntas de referência por domínio (migration, architecture, config, troubleshooting etc.).
- Métricas como NDCG, Recall@K e precisão top‑K para comparar configurações de pesos e modelos.

### 7.3 Evolução da configuração

- Ajustar `dense_weight`, `sparse_weight`, `top_k` e políticas de re‑ranking com base em análise de logs e avaliação offline.
- Evoluir o modelo de embeddings e de re‑ranking conforme necessário.
- Expandir fontes de dados (novos serviços de OCI, novos playbooks internos) sem mudar a API de RAG.

---

## 8. Resumo

Com essa arquitetura, a camada de RAG do OCI Copilot passa a ser um serviço bem definido, configurado via `config/oci-copilot-agents.yaml`, suportando retrieval híbrido, re‑ranking, query rewriting e uso intensivo de metadados.
Essa camada é consumida pelos agentes especializados de migração, arquitetura, configuração, FinOps, troubleshooting e outros, permitindo fluxos agentic complexos com base sólida em documentação oficial e conhecimento estruturado de OCI.
