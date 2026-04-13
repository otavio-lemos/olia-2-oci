# OCI Copilot – Documentação de Implantação da Camada de RAG

Este documento descreve como implantar e operar a camada de Retrieval-Augmented Generation (RAG) do OCI Copilot, alinhada com a configuração em `config/oci-copilot-agents.yaml`.[cite:80] O objetivo é fornecer um guia de ponta a ponta: desde a ingestão de documentos até a integração com os agentes e workflows do copilot.

---

## 1. Visão geral da arquitetura de RAG

A camada de RAG do OCI Copilot segue um modelo **híbrido + agentic**:

- **Híbrido (dense + sparse)**:
  - Índice vetorial para recuperação semântica (perguntas em linguagem natural, equivalência de serviços, padrões de migração).[cite:51][cite:66]
  - Índice esparso (BM25/FTS) para recuperação lexical precisa (nomes de serviços, flags de CLI, parâmetros Terraform, códigos de erro).[cite:51][cite:68]
  - Fusão via **Reciprocal Rank Fusion (RRF)**, com pesos configuráveis para denso/esparso.[cite:65][cite:68]
- **Re‑ranking semântico**: modelo cross‑encoder opcional que reordena os top‑K documentos mais relevantes.[cite:54][cite:65]
- **Query rewriting**: o próprio LLM especialista reescreve a query para maximizar a qualidade do retrieval, adicionando termos técnicos e nomes de serviços relevantes.[cite:52][cite:59]
- **Agentic RAG**: os agentes (migracao, arquitetura, configuracao, etc.) consomem a camada de RAG via uma tool `rag_retrieve`, respeitando filtros de metadados e estratégias específicas por tipo de fluxo.[cite:72][cite:76]

Toda a parametrização dessa arquitetura está centralizada em `rag` dentro de `config/oci-copilot-agents.yaml`.[cite:80]

---

## 2. Fontes de dados e ingestão

### 2.1 Fontes de documentos

As principais fontes que devem ser ingeridas no índice de RAG são:

- **Documentação oficial de OCI** (Content home, serviços específicos, guias de migração, whitepapers, best practices).[cite:60][cite:58]
- **Guias de migração multi‑cloud → OCI** (AWS/Azure/GCP/On‑prem), incluindo blogs e tutoriais da Oracle.[cite:60]
- **Exemplos oficiais de Terraform do provider OCI** (módulos e snippets).[cite:55]
- **Referência de CLI** para `oci` (man pages, exemplos de uso).[cite:55]
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
   - Evitar chunking cego por tokens; usar heurísticas baseadas em títulos, seções e listas.[cite:52][cite:32]
3. **Enriquecimento de metadados**
   - Atribuir metadados coerentes com o YAML:
     - `domain` (architecture, migration, security, governance, networking, finops, troubleshooting, observability, operations, devops, etc.).
     - `cloud_provider` (aws, azure, gcp, onprem, oci).
     - `doc_type` (reference, how-to, example, best-practices, runbook).
     - `service` (compute, vcn, oke, autonomous, object-storage, etc.).
   - Esse enriquecimento é crítico para filtros como os usados por agentes `migracao`, `configuracao_seg`, `finops`.[cite:52][cite:33][cite:80]
4. **Indexação sparse**
   - Enviar cada chunk para o índice BM25 (Elasticsearch/OpenSearch/Meilisearch ou Postgres FTS), definindo campos full‑text e campos de metadados.
5. **Indexação dense**
   - Gerar embeddings com o modelo `oci-specialist-embedding-v1` e indexar em um banco vetorial (FAISS, Qdrant, PGVector, etc.), guardando os mesmos metadados.[cite:52][cite:66]

O pipeline deve ser agendado (por exemplo, cron/Job em Kubernetes) para rodar periodicamente e capturar atualizações na documentação, especialmente para serviços em rápida evolução.[cite:52]

---

## 3. Índices dense e sparse

### 3.1 Índice dense

Configuração padronizada (conforme YAML):

- Modelo de embedding: `oci-specialist-embedding-v1`.[cite:80]
- Nome do índice: `oci_docs_dense_index`.[cite:80]
- Top‑K padrão: 20 documentos antes da fusão.[cite:80]

Boas práticas:
- Garantir que o modelo de embedding seja treinado/ajustado para linguagem técnica de cloud (PT‑BR/EN) para maximizar recall semântico.[cite:52][cite:66]
- Armazenar apenas IDs e metadados leves no índice vetorial; o texto completo pode ficar em um storage separado, referenciado por ID.[cite:66]

### 3.2 Índice sparse

Configuração (YAML):

- Engine: `elasticsearch` (ou equivalente).[cite:80]
- Índice: `oci_docs_sparse_index`.[cite:80]
- Top‑K padrão: 40 documentos antes da fusão.[cite:80]

Boas práticas:
- Mapear campos com analyzers consistentes, preservando tokens técnicos (nomes de recursos, flags, códigos).[cite:68][cite:71]
- Habilitar filtros e facetas pelos mesmos metadados dos embeddings (domain, cloud_provider, doc_type, service).

---

## 4. Estratégia de retrieval híbrido

### 4.1 Fluxo de consulta

Para cada chamada à tool `rag_retrieve`, o fluxo é:

1. **Query rewriting (opcional)**
   - O LLM reescreve a query original em uma forma otimizada para retrieval, usando o `system_prompt` definido em `rag.query_rewriting.system_prompt`.[cite:80]
2. **Aplicação de filtros de metadados**
   - Com base no agente e no tipo de workflow, selecionar filtros de `domain`, `cloud_provider`, `doc_type`, etc., conforme `metadata_filters` do agente em `config/oci-copilot-agents.yaml`.[cite:80]
3. **Busca dense**
   - Rodar a query reescrita no índice `oci_docs_dense_index` com `top_k` configurado (padrão 20, 30 para migração).[cite:80]
4. **Busca sparse**
   - Rodar a mesma query (ou eventualmente versão não reescrita) no índice `oci_docs_sparse_index` com `top_k` configurado (padrão 40, 60 para migração).[cite:80]
5. **Fusão (RRF)**
   - Combinar os resultados com método `rrf` (Reciprocal Rank Fusion), pesando `dense_weight` e `sparse_weight` conforme YAML (por exemplo, 0.7/0.3 global, 0.6/0.4 para migração, 0.4/0.6 para configuração).[cite:65][cite:68][cite:80]
6. **Re‑ranking (opcional)**
   - Se `re_ranking.enabled` for `true`, aplicar o modelo `oci-migration-cross-encoder-v1` sobre os top‑K para reordená‑los (especialmente útil em migração e troubleshooting).[cite:54][cite:65][cite:80]
7. **Retorno para o agente**
   - Entregar ao agente N documentos (por exemplo, top 10) com texto e metadados, para serem usados no contexto do LLM.

### 4.2 Overrides por tipo

O bloco `rag.by_type` no YAML permite overrides por scenario:[cite:80]

- `migracao`:
  - `dense.top_k` maior (30) e `sparse.top_k` maior (60) para garantir abrangência em migrações complexas.
  - Peso um pouco maior para dense (0.6) para priorizar semântica.[cite:80][cite:52]
- `configuracao`:
  - Peso maior para sparse (0.6), já que muitos pedidos são sobre parâmetros e flags exatas.[cite:71][cite:80]
- `troubleshooting`:
  - `re_ranking.enabled: true` e top‑K ajustado para trazer mais casos de incidentes relevantes.[cite:54][cite:80]

---

## 5. Integração com agentes e workflows

Cada agente no YAML declara:
- **tools** incluindo `rag_retrieve`.
- **rag_strategy** (dense/hybrid).
- **metadata_filters** (domain, cloud_provider, doc_type) que ajustam o escopo da busca.[cite:80]

Exemplos:

- Agente `migracao`:
  - `rag_strategy: hybrid`, filtros `domain: ["migration"]` e `cloud_provider` origem.[cite:80]
  - Usa RAG para buscar padrões e guias de migração específicos (ex.: RDS → Autonomous, EKS → OKE).[cite:52][cite:60]
- Agente `configuracao_seg`:
  - Focado em `domain: ["security", "governance", "networking"]`, ponderando mais sparse para pegar políticas/flags exatas.[cite:71][cite:80]
- Agente `finops`:
  - Filtros `domain: ["finops", "cost-optimization"]`, com queries que podem combinar docs de boas práticas e APIs de pricing.[cite:52][cite:60]

Os workflows (migracao, arquitetura, configuracao, etc.) definem a ordem em que esses agentes são chamados, e cada chamada pode envolver múltiplos ciclos de RAG dependendo da complexidade da tarefa.[cite:72][cite:76][cite:80]

---

## 6. Implantação da infraestrutura

### 6.1 Ambiente de desenvolvimento local

Componentes mínimos para dev:

- **Vector DB** (Qdrant/PGVector/FAISS via serviço) com índice `oci_docs_dense_index`.
- **Motor de busca sparse** (Elasticsearch/OpenSearch/Meilisearch/Postgres FTS) com índice `oci_docs_sparse_index`.[cite:68][cite:71]
- **Serviço de RAG** (microserviço em Python/Go) que:
  - Carrega `config/oci-copilot-agents.yaml` na inicialização.[cite:80]
  - Expõe um endpoint HTTP/JSON `/rag/retrieve` usado pelos agentes.
- **LLM servidor** (MLX-LM / Ollama / llama.cpp) com o modelo fine‑tuned oci‑specialist.

Sugestão: docker‑compose com serviços `rag-service`, `vector-db`, `search-db`, `llm-server`.

### 6.2 Ambiente de produção (exemplo em OCI)

- Deploy do **RAG Service** em OKE ou OKE Autonômico.
- **Vector DB** e **sparse engine** gerenciados (ou auto‑gerenciados) em OCI ou em infra escolhida pelo projeto.
- Rede com segurança adequada (VCN, NSGs, LB) e acesso controlado a fontes de dados.
- Observabilidade via OCI Logging/Monitoring para métricas de latência, taxas de acerto, erros de indexação, etc.[cite:58][cite:55]

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
- Métricas como NDCG, Recall@K e precisão top‑K para comparar configurações de pesos e modelos.[cite:52][cite:54]

### 7.3 Evolução da configuração

- Ajustar `dense_weight`, `sparse_weight`, `top_k` e políticas de re‑ranking com base em análise de logs e avaliação offline.[cite:65][cite:68]
- Evoluir o modelo de embeddings e de re‑ranking conforme necessário.
- Expandir fontes de dados (novos serviços de OCI, novos playbooks internos) sem mudar a API de RAG.

---

## 8. Resumo

Com essa arquitetura, a camada de RAG do OCI Copilot passa a ser um serviço bem definido, configurado via `config/oci-copilot-agents.yaml`, suportando retrieval híbrido, re‑ranking, query rewriting e uso intensivo de metadados.[cite:51][cite:52][cite:80]
Essa camada é consumida pelos agentes especializados de migração, arquitetura, configuração, FinOps, troubleshooting e outros, permitindo fluxos agentic complexos com base sólida em documentação oficial e conhecimento estruturado de OCI.[cite:72][cite:76]
