# OCI Specialist Copilot – Visão e Roadmap Inicial

Este documento captura a visão e o roadmap iniciais para evoluir o projeto `olia-2-oci` de um modelo LLM especialista em OCI para um **OCI Specialist Copilot** completo.

## Objetivo

Transformar o LLM atual, já fine-tuned para OCI em PT-BR, em um copilot capaz de:
- Responder com alta correção técnica, profundidade e clareza sobre serviços e arquiteturas OCI.
- Navegar e usar documentação oficial e exemplos atualizados (RAG).
- Interagir com uma tenancy OCI real via ferramentas (CLI/SDK) em modo inicialmente somente leitura.
- Orquestrar agentes especializados (Arquitetura, DevOps, FinOps, Troubleshooting).
- Ser acessível por múltiplas superfícies (CLI, WebUI, extensões de IDE).

## Estado atual (resumo)

- LLM treinado sobre ~19k exemplos após limpeza, com 87 categorias cobrindo OCI core, segurança, migração, Terraform, observabilidade, troubleshooting, DevOps, governança, FinOps e plataforma.
- Métricas pós cycle-1 (200 amostras):
  - technical_correctness: estável.
  - depth: estável.
  - structure: melhora relevante.
  - hallucination: melhora relevante (menos alucinação).
  - clarity: queda (respostas mais burocráticas/menos naturais).
  - overall: leve ganho.
- Roadmap existente já prevê:
  - RAG com documentação oficial OCI.
  - Cycle-2 de fine-tuning (auditoria de dataset, ajustes de tom, mais profundidade, tuning de LoRA).
  - Publicação de adaptadores/modelos no Hugging Face.

## Principais lacunas para um copilot

1. **Conhecimento profundo e claro**
   - technical_correctness e depth ainda não evoluíram como esperado.
   - clarity caiu, o que reduz a usabilidade como copilot conversacional.

2. **Factualidade e atualização contínua**
   - Modelo não tem acesso em tempo real a documentação, preços, limites e parâmetros de CLI atualizados.

3. **Acesso ao ambiente real (tenancy)**
   - Hoje o modelo não “vê” recursos reais (compartimentos, VCNs, budgets, policies, métricas, logs).

4. **Orquestração de fluxo de trabalho**
   - Falta camada de agentes e planner para dividir responsabilidades por persona/área.

5. **Experiências de uso focadas em trabalho diário**
   - Falta CLI/IDE/flows guiados específicos para tarefas típicas de arquitetos/engenheiros OCI.

## Arquitetura lógica proposta

Quatro camadas principais:

1. **Modelo Especialista**
   - LLM fine-tuned em PT-BR para OCI, com dataset estruturado por categorias, intent, persona, constraint, lifecycle_stage.

2. **Camada de Conhecimento (RAG)**
   - Ingestor de documentação oficial OCI, exemplos de CLI/SDK, blogs, tutoriais.
   - Indexador vetorial + filtros por serviço/categoria/lifecycle_stage.
   - Recuperação condicionada a intent/persona para selecionar o contexto mais relevante.

3. **Camada de Ferramentas/Ações**
   - Wrappers sobre OCI CLI/SDK inicialmente read-only (listar recursos, budgets, policies, métricas, logs).
   - Geradores de artefatos (Terraform, policies IAM, scripts OCI CLI) sem aplicar mudanças.
   - Futuramente, ações de escrita controlada com aprovação humana.

4. **Camada de Orquestração e Experiências**
   - Agentes especializados (Arquitetura, DevOps, Governança/FinOps, Troubleshooting).
   - Planner/router central que decide quais agentes/tools usar, em que ordem.
   - Superfícies de uso: CLI `oci-copilot`, integração com WebUI, extensões de IDE (VS Code), flows guiados na web.

## Componentes futuros – por camada

### 1. Modelo especialista (short term)

- **Cycle-2 de fine-tuning**:
  - Auditoria forte em categorias que regrediram (Terraform, Governance, principalmente networking/compute/serverless e tagging).
  - Reescrita de exemplos para melhorar clarity sem perder densidade técnica (tom "engenheiro sênior explicando para colega").
  - Introdução de cenários arquiteturais end-to-end (migrações, landing zones, HA/DR multi-região, etc.) para aumentar depth.
  - Tuning de LoRA (ex.: LORA_RANK ↑, LORA_ALPHA ↑) para absorver mais conhecimento de domínio.

### 2. Camada de conhecimento (RAG)

- Ingestor baseado na taxonomia atual (87 categorias + metadados de intent/persona/lifecycle_stage).
- Indexação vetorial + filtro híbrido (keyword + embedding) por serviço/categoria.
- Query de RAG enriquecida com persona e lifecycle_stage para priorizar docs corretas para o contexto.
- Pipeline de refresh periódico (ex.: semanal) para capturar mudanças na documentação e novos serviços.

### 3. Ferramentas/Ações sobre OCI

**Fase 1 – Read-only (prioridade alta)**
- Tools para:
  - `list_compartments`, `list_vcns`, `list_subnets`, `list_instances`, `list_budgets`, `list_policies`.
  - Ler métricas e logs básicos (Monitoring/Logging) para suportar troubleshooting.

**Fase 2 – Geração de artefatos (sem aplicar)**
- Tools que recebem intenções estruturadas e geram:
  - Módulos/snippets Terraform opinados.
  - Policies IAM baseadas em objetivo (“somente leitura em logs deste compartimento”, etc.).
  - Scripts OCI CLI encadeados com flags corretas.

**Fase 3 – Ação controlada**
- Tools de escrita (criação de recursos em sandbox, aplicação de planos Terraform, etc.)
  - Sempre com aprovação humana explícita.
  - Escopo restrito (compartimentos específicos, policies bem definidas).
  - Logs de auditoria e mecanismos de rollback.

### 4. Orquestração e agentes

- Definir agentes baseados nas personas/categorias existentes:
  - **Arquitetura/Platform**: landing zones, VCN, bancos, HA/DR, backup-governance, sre-operations.
  - **DevOps/Infra as Code**: Terraform (todas as subcategorias), Resource Manager, CI/CD, secrets, artifacts.
  - **Governança/FinOps**: compartments, tagging, budgets-cost, compliance, policies-guardrails, cost-optimization, showback/chargeback, storage-tiering.
  - **Troubleshooting/Observability**: troubleshooting (compute, networking, OKE, functions, performance, storage) e observability (logging, monitoring, APM, stack-monitoring).
- Implementar um planner/router que:
  - Classifica intent/persona/lifecycle_stage da requisição.
  - Seleciona agentes e ferramentas relevantes.
  - Orquestra chamadas em sequência (ex.: arquitetura → FinOps → DevOps).

### 5. Experiências de usuário

- **CLI `oci-copilot`**:
  - REPL interativo em linguagem natural.
  - Comandos orientados a fluxo (ex.: "migrar app de AWS para OCI", "analisar VCN X", "otimizar custos deste compartimento").

- **Extensão VS Code**:
  - Foco em Terraform + policies IAM.
  - Geração, refino, explicação e correção em contexto de projeto.

- **UI Web opinada**:
  - Playbooks/fluxos pré-definidos (criar landing zone, otimizar custos, troubleshooting de performance em OKE, etc.).
  - Construída sobre a API compatível com OpenAI/MLX já exposta no projeto.

## Roadmap em ondas

**Onda 1 – Copilot de Conhecimento**
- Cycle-2 de fine-tuning (foco em technical_correctness, depth, clarity).
- RAG mínimo viável com docs oficiais e schema alinhado à taxonomia.
- Início da estrutura `copilot/` (módulos rag/, tools/, agents/, ui/).

**Onda 2 – Copilot de Observação**
- Tools read-only para inspecionar tenancy.
- Agents especializados e planner básico.
- CLI `oci-copilot` utilizando agentes + RAG + tools.

**Onda 3 – Copilot de Ação**
- Tools de escrita controlada (sandbox + aprovação).
- Extensões de IDE e flows web mais ricos.
- Observabilidade e auditoria de tool-calls em produção.
