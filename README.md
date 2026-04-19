# OCI Specialist LLM

[🇺🇸 English](README.en-US.md) | [🇧🇷 Português](README.md)

Large Language Model (LLM) fine-tuned para Oracle Cloud Infrastructure (OCI) usando Apple Silicon, MLX e LoRA.

[![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.12-blue?style=flat-square&logo=python&logoColor=white)](https://www.python.org)
[![MLX](https://img.shields.io/badge/MLX-Apple%20Silicon-orange?style=flat-square)](https://mlx.ai)
[![MLX-Tune](https://img.shields.io/badge/Finetune-MLX--Tune-blue?style=flat-square)](https://github.com/Aaronipher/mlx-tune)
[![Model](https://img.shields.io/badge/Base%20Model-Qwen2.5--Coder--7B--Instruct--4bit-purple?style=flat-square)](https://huggingface.co/mlx-community/Qwen2.5-Coder-7B-Instruct-4bit)
[![Dataset](https://img.shields.io/badge/Dataset-13196_examples-green?style=flat-square)](docs/taxonomy.md)
[![LangGraph](https://img.shields.io/badge/Orquestração-LangGraph-black?style=flat-square&logo=langchain)](https://python.langchain.com/docs/langgraph)
[![Chainlit](https://img.shields.io/badge/UI-Chainlit-orange?style=flat-square)](https://chainlit.io)
[![FastAPI](https://img.shields.io/badge/API-FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![FAISS](https://img.shields.io/badge/Dense-FAISS-76b900?style=flat-square)](https://github.com/facebookresearch/faiss)
[![BM25](https://img.shields.io/badge/Sparse-BM25-007acc?style=flat-square)](https://github.com/dorianbrown/rank_bm25)
[![Rerank](https://img.shields.io/badge/Rerank-Cross--Encoder-red?style=flat-square)](https://www.sbert.net/docs/pretrained_models.html#cross-encoders)
[![Hugging Face](https://img.shields.io/badge/%F0%9F%A4%97-Hugging%20Face-yellow?style=flat-square)](https://huggingface.co)

---

> **Idioma**: Dados e prompts em Português do Brasil (PT-BR).

### 🚀 Core Stack & Componentes
- **LLM Base**: [Qwen 2.5 Coder 7B Instruct](https://huggingface.co/Qwen/Qwen2.5-Coder-7B-Instruct) (4-bit).
- **Orquestração de Agentes**: [LangGraph](https://python.langchain.com/docs/langgraph) & [LangChain](https://langchain.com).
- **Interface OCI Copilot**: [Chainlit](https://chainlit.io) (Interactive UI com HITL).
- **Treinamento e Inferência**: [MLX Framework](https://mlx.ai) & [MLX-Tune](https://github.com/Aaronipher/mlx-tune).
- **RAG (Busca Híbrida)**: [FAISS](https://github.com/facebookresearch/faiss) (Dense) + [Rank-BM25](https://github.com/dorianbrown/rank_bm25) (Sparse).
- **Backend Service**: [FastAPI](https://fastapi.tiangolo.com) (RAG API).
- **Embeddings & Rerank**: [Hugging Face](https://huggingface.co) & [Sentence-Transformers](https://sbert.net).
- **Hardware**: Otimizado para Apple Silicon (M3 Pro 18GB).
- **Linguagem**: Python 3.12.

---

## Visão Geral

O processo de desenvolvimento do OCI Specialist LLM segue uma ordem rigorosa de pipeline para garantir a precisão técnica e a performance no Apple Silicon.

```mermaid
flowchart TD
    subgraph GENERATION["1. Geração & Preparação"]
        A1["generate_v7_combined.py\n(88 cats, 100% diversity)"] --> A2["prepare_data.sh"]
        A2 --> A3["train.jsonl / valid.jsonl"]
    end

    subgraph TRAINING["2. Treinamento & Merge"]
        B1["train_mlx_tune.py"] --> B2["LoRA Adapters"]
        B2 --> B3["Merge & Export (GGUF)"]
    end

    subgraph RAG["3. OCI Copilot (RAG)"]
        C1["update_rag.py (Offline)"] --> C2["FAISS / BM25 Indices"]
        C2 --> C3["FastAPI Backend"]
    end

    subgraph UI["4. Interface & Agentes"]
        D1["orchestrator.py (LangGraph)"] --> D2["app_chainlit.py (UI)"]
    end

    GENERATION --> TRAINING
    TRAINING --> UI
    RAG --> UI

    style GENERATION fill:#e1f5fe
    style TRAINING fill:#e8f5e9
    style RAG fill:#fff3e0
    style UI fill:#f3e5f5
```

---

## Funcionalidades

- **LoRA Fine-tuning**: Adaptação de baixo ranque com modelo base **Qwen 2.5 Coder 7B Instruct** (4-bit).
- **Otimizado para M3 Pro**: Configurações hiper-otimizadas para 18GB de RAM, usando **BF16 nativo** e sem Swap em disco.
- **RAG Híbrido Avançado**: Busca semântica (FAISS) + lexical (BM25) com persistência local e **Ingestão Offline**.
- **Query Rewriting**: Expansão automática de queries via LLM para melhor recall.
- **Multi-Query Expansion**: Geração de 3-5 variações da query original.
- **Cross-Encoder Re-ranking**: Reordenação de resultados pós-RRF.
- **Re-ranking por Tipo**: Estratégia configurável por tipo de query (migracao, troubleshooting, etc).
- **Chunking Inteligente**: Divisão por seções e headings, não apenas tokens.
- **Metadata Extraction**: Extração automática de serviço OCI, versão e categoria.
- **Atualização Incremental**: Indexação de novos docs sem rebuild completo.
- **Intent Classification via Embeddings**: Classificação de intenção real (não mock).
- **Tool Calling**: Agentes com tools via @tool decorator e Pydantic.
- **Session Management**: Sessões persistidas com histórico e context window.
- **Rate Limiting**: Controle de acesso por usuário via token bucket.
- **HITL**: Human-in-the-loop para comandos destrutivos.
- **Streaming SSE**: Tokens enviados em tempo real via Server-Sent Events.
- **Fallback Entre Agentes**: Redundância quando agente falha.
- **Logging Estruturado**: JSON logging com trace_id por request.
- **Métricas**: Latência P50/P95/P99 + health checks.
- **Sistema Multi-Agentes**: Orquestração via **LangGraph** (Router, Descoberta, Arquitetura, Execução, Troubleshooting, etc).
- **Interface OCI Copilot**: UI construída com **Chainlit**, suportando anexos de arquivos, streaming de tokens e **Human-in-the-loop** para segurança em comandos CLI.
- **Action Buttons**: Botões de ação para OCI CLI e Terraform na UI.
- **Merge & Export**: Pipeline para fundir adaptadores LoRA ao modelo base e exportar para GGUF (quantização local).
- **Avaliação Automatizada**: Pipeline de benchmark para medir precisão técnica, alucinação e profundidade.

---

## Dataset

| Métrica | Valor |
|--------|-------|
| **Total Gerado** | 13.200 exemplos (88 categorias × 150) |
| **Após Limpeza** | 14.940 exemplos |
| **Após Desduplicação** | 13.196 exemplos |
| **Treino (Train)** | 9.897 exemplos (75%) |
| **Validação (Valid)** | 1.979 exemplos (15%) |
| **Avaliação (Eval)** | 1.320 exemplos (10%) |
| **Categorias** | 88 tópicos do OCI |

---

## Instalação e Começando

> [!IMPORTANT]
> **Todos os comandos deste projeto devem ser executados obrigatoriamente na raiz do repositório.**
> **Lembre-se de ativar o ambiente virtual correto com `source venv/bin/activate` ou `source venv-rag/bin/activate` antes de executar qualquer comando.**

### 1. Clonagem do Repositório

```bash
git clone https://github.com/otavio-lemos/olia-2-oci.git
cd olia-2-oci
```

### 2. Ambiente de Treinamento (LLM)

```bash
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Ambiente OCI Copilot (RAG)

```bash
python3.12 -m venv venv-rag
source venv-rag/bin/activate
pip install -r requirements-rag.txt
```

---

## Preparação do Dataset

Pipeline para validar, limpar, desduplicar e gerar splits do dataset.

### Fluxo Completo

```mermaid
flowchart LR
    A1["generate_v7_combined.py\n(88 cats, 100% diversity)"] --> D["prepare_data.sh"]
    D --> E["validate_jsonl.py\n(estrutura)"]
    E --> F["clean_dataset.py\n(conteúdo)"]
    F --> G["dedupe_embedding.py\n(semântico)"]
    G --> H["build_dataset_fixed.py\n(splits)"]
    H --> I["train.jsonl\nvalid.jsonl\neval.jsonl"]
```

### Geração do Dataset

Gera exemplos usando templates com OCI CLI commands reais e intents variados. Rápido, sem custo, sem dependência de internet.

```bash
# Gerar dataset (88 categorias × 180 exemplos = 15,840)
python scripts/generate_v7_combined.py
```

### Passo Final — Validar, Limpar e Gerar Splits

Após gerar os exemplos, execute o pipeline de preparação:

```bash
# Validar, limpar, desduplicar e gerar splits (75/15/10%)
bash scripts/prepare_data.sh
```

### Scripts do Pipeline

| Script | Função | Entrada | Saída |
|--------|--------|---------|-------|
| `validate_jsonl.py` | Valida estrutura JSONL (schema messages) | `all_curated.jsonl` | `all_curated.jsonl` (ou falha) |
| `clean_dataset.py` | Remove templates genéricos, CLI incorretas, ruído | `all_curated.jsonl` | `all_curated_clean.jsonl` |
| `dedupe_embedding.py` | Desduplicação semântica por embeddings (threshold 0.97) | `all_curated_clean.jsonl` | `all_curated_semantic_dedup.jsonl` |
| `build_dataset_fixed.py` | Gera splits (75% train, 15% valid, 10% eval) | `all_curated_semantic_dedup.jsonl` | `train.jsonl`, `valid.jsonl`, `eval.jsonl` |

---

## Treinamento

O treinamento utiliza o framework MLX-Tune, focado na arquitetura do Apple Silicon.

### 1. Execução do Treino (Fine-Tuning)

> [!NOTE]
> Execute com o ambiente **venv** ativado: `source venv/bin/activate`

```bash
# Execute o ciclo consolidado de treinamento
bash training/run_cycles.sh --all --fresh
```

### 2. Fusão de Pesos (Merge) & Exportação

> [!NOTE]
> Execute com o ambiente **venv** ativado: `source venv/bin/activate`

Após gerar os adaptadores LoRA, fundir com o modelo base para uso em inferência.

```bash
# Merge e export para GGUF Q4
python scripts/merge_export.py --cycle cycle-1 --quant q4 --name oci-specialist
```

---

## Avaliação

O pipeline de avaliação compara o modelo fine-tuned contra o modelo base usando:
- **Scoring automático**: Correctness, Depth, Structure, Hallucination, Clarity
- **Similaridade semântica**: Sentence Transformers (MiniLM-L6-v2)
- **Judge (opcional)**: LLM-as-Judge usando modelo diferente (ex: Llama 3.1 8B) para avaliação imparcial

> [!NOTE]
> Execute com o ambiente **venv** ativado: `source venv/bin/activate`

### 1. Gerar Modelos Quantizados (Pré-requisito)

Antes de avaliar, gere os modelos quantizados com o merge_export:

```bash
# Gerar versões quantizadas do modelo mergeado
# Cria: safetensors/bf16/, safetensors/q4/
python scripts/merge_export.py --cycle cycle-1 --quant q4
```

### 2. Executar Avaliação

```bash
# Avaliação Rápida (10 amostras) - modelo específico obrigatório
python scripts/unified_evaluation_v4.py --cycle cycle-1 --ft-model outputs/cycle-1/safetensors/q4 --mode small --fresh

# Avaliação Completa (1320 amostras)
python scripts/unified_evaluation_v4.py --cycle cycle-1 --ft-model outputs/cycle-1/safetensors/q4 --mode full --fresh

# Avaliação com Judge (LLM-as-Judge usando modelo diferente)
python scripts/unified_evaluation_v4.py --cycle cycle-1 --ft-model outputs/cycle-1/safetensors/q4 --mode medium --external-judge --judge-lang pt --judge-tokens 800 --max-tokens 768
```

Resultados: ver [Benchmark](#benchmark)

---

## RAG (Retrieval-Augmented Generation)

O OCI Copilot utiliza uma camada de RAG persistente para acessar fatos da documentação Oracle.

### 1. Ingestão Offline (Obrigatória)
> [!NOTE]
> Execute com o ambiente **venv-rag** ativado: `source venv-rag/bin/activate`

Para economizar RAM durante o chat, os índices devem ser gerados offline:
```bash
python scripts/update_rag.py
```

### 2. Orquestração e Agentes
O ecossistema é orquestrado via **LangGraph** e servido via **FastAPI**.

**Subir API Backend (RAG Indices):**
> [!NOTE]
> Execute com o ambiente **venv-rag** ativado: `source venv-rag/bin/activate`

```bash
uvicorn rag.api:app --host 0.0.0.0 --port 8000
```

**Subir Orquestrador e UI (Interface Copilot):**
> [!NOTE]
> Execute com o ambiente **venv-rag** ativado: `source venv-rag/bin/activate`

```bash
chainlit run rag/app_chainlit.py --port 8001
```

---

## Inferência e UI

A inferência local é realizada utilizando o modelo após o processo de **Merge**.

### 1. Servidores de Inferência

#### MLX (Recomendado - Apple Silicon)
> [!TIP]
> Recomendado para Apple Silicon. Inferência local via MLX com LoRA adapter.

> [!NOTE]
> Execute com o ambiente **venv** ativado: `source venv/bin/activate`

```bash
mlx_lm.server --model mlx-community/Qwen2.5-Coder-7B-Instruct-4bit --adapter outputs/cycle-1/adapters
```

#### Ollama
```bash
# 1. Criar Modelfile
cat > ./outputs/cycle-1/gguf/Modelfile << 'EOF'
FROM ./oci-specialist-Q4_K_M.gguf
PARAMETER temperature 0.1
PARAMETER top_p 0.9
PARAMETER top_k 40
SYSTEM Você é um especialista em OCI (Oracle Cloud Infrastructure).
EOF

# 2. Criar modelo
ollama create oci-specialist -f ./outputs/cycle-1/gguf/Modelfile

# 3. Iniciar servidor em background
ollama serve &

# 4. Carregar modelo na memória
curl http://localhost:11434/api/generate -d '{"model": "oci-specialist", "keep_alive": -1}'
```

#### llama.cpp
```bash
llama-server -m outputs/cycle-1/gguf/oci-specialist-Q4_K_M.gguf --port 8080
```

### 2. OCI Copilot UI
> [!NOTE]
> Execute com o ambiente **venv-rag** ativado: `source venv-rag/bin/activate`

Com o backend RAG rodando, inicie a interface visual:
```bash
chainlit run rag/app_chainlit.py --port 8001
```

---

## Benchmark

### Avaliação com Judge Externo (mlx-community/Meta-Llama-3.1-8B-Instruct-4bit) - 200 amostras

| Métrica | Modelo Base | Fine-Tuned | Delta |
|--------|-------------|------------|-------|
| technical_correctness | 3.00 | 3.73 | +0.72 |
| depth | 3.06 | 3.82 | +0.76 |
| structure | 3.50 | 4.63 | +1.14 |
| hallucination | 3.62 | 4.46 | +0.84 |
| clarity | 3.20 | 3.98 | +0.77 |
| **Overall** | **3.27** | **4.12** | **+0.85** |

### Como avaliar
Para gerar novos relatórios, utilize os comandos detalhados na seção [Avaliação](#avaliação).

### Comparação de Métricas
![Gráfico de Comparação](outputs/cycle-1/benchmarks/comparison_chart_20260419_162359.png)

### Performance por Categoria
![Gráfico de Categorias](outputs/cycle-1/benchmarks/category_chart_20260419_162359.png)

### Principais Ganhos por Tópico (Top 5)
1. **storage/object**: +3.60
2. **troubleshooting/performance**: +3.80
3. **observability/apm**: +3.40
4. **security/dynamic-groups**: +3.40
5. **database/postgresql**: +3.40

### Resultados Detalhados por Categoria (88 Tópicos)

<details>
<summary>Clique para expandir a tabela de performance por categoria</summary>
<sub>

| # | Categoria | Base | FT | Delta |
---|---------|------|----|-------|
| 1 | compute/custom-images | 2.80 | 4.60 | +1.80 |
| 2 | compute/instances | 4.60 | 4.80 | +0.20 |
| 3 | compute/scaling | 4.40 | 4.20 | -0.20 |
| 4 | container/instances | 1.40 | 3.40 | +2.00 |
| 5 | container/oke | 2.60 | 5.00 | +2.40 |
| 6 | database/autonomous | 4.00 | 1.60 | -2.40 |
| 7 | database/autonomous-json | 1.20 | 3.40 | +2.20 |
| 8 | database/exadata | 4.00 | 5.00 | +1.00 |
| 9 | database/exadata-cloud | 4.60 | 3.20 | -1.40 |
| 10 | database/mysql | 4.20 | 3.60 | -0.60 |
| 11 | database/nosql | 1.60 | 4.20 | +2.60 |
| 12 | database/postgresql | 1.00 | 4.40 | +3.40 |
| 13 | devops/artifacts | 4.80 | 5.00 | +0.20 |
| 14 | devops/ci-cd | 4.40 | 4.60 | +0.20 |
| 15 | devops/resource-manager | 4.60 | 4.80 | +0.20 |
| 16 | devops/secrets | 1.60 | 4.20 | +2.60 |
| 17 | finops/cost-optimization | 4.60 | 5.00 | +0.40 |
| 18 | finops/rightsizing | 3.80 | 4.80 | +1.00 |
| 19 | finops/showback-chargeback | 4.60 | 4.80 | +0.20 |
| 20 | finops/storage-tiering | 4.40 | 3.80 | -0.60 |
| 21 | governance/audit-readiness | 3.80 | 4.80 | +1.00 |
| 22 | governance/budgets-cost | 2.40 | 5.00 | +2.60 |
| 23 | governance/compartments | 2.40 | 4.40 | +2.00 |
| 24 | governance/compliance | 1.00 | 3.60 | +2.60 |
| 25 | governance/landing-zone | 4.80 | 3.20 | -1.60 |
| 26 | governance/policies-guardrails | 4.40 | 4.60 | +0.20 |
| 27 | governance/resource-discovery | 1.40 | 4.40 | +3.00 |
| 28 | governance/tagging | 1.40 | 4.00 | +2.60 |
| 29 | lb/load-balancer | 5.00 | 4.60 | -0.40 |
| 30 | migration/aws-compute | 5.00 | 4.60 | -0.40 |
| 31 | migration/aws-database | 1.40 | 4.40 | +3.00 |
| 32 | migration/aws-storage | 2.40 | 2.00 | -0.40 |
| 33 | migration/azure-compute | 1.80 | 4.60 | +2.80 |
| 34 | migration/azure-database | 3.60 | 3.00 | -0.60 |
| 35 | migration/azure-storage | 0.80 | 2.60 | +1.80 |
| 36 | migration/data-transfer | 4.80 | 4.20 | -0.60 |
| 37 | migration/gcp-compute | 1.60 | 4.60 | +3.00 |
| 38 | migration/gcp-database | 2.40 | 3.40 | +1.00 |
| 39 | migration/gcp-storage | 3.00 | 1.40 | -1.60 |
| 40 | migration/onprem-compute | 2.80 | 5.00 | +2.20 |
| 41 | migration/onprem-database | 2.60 | 4.60 | +2.00 |
| 42 | migration/onprem-storage | 2.20 | 4.60 | +2.40 |
| 43 | migration/onprem-vmware | 4.40 | 4.60 | +0.20 |
| 44 | networking/connectivity | 2.20 | 4.40 | +2.20 |
| 45 | networking/security | 4.20 | 4.60 | +0.40 |
| 46 | networking/vcn | 2.40 | 2.40 | +0.00 |
| 47 | observability/apm | 1.60 | 5.00 | +3.40 |
| 48 | observability/logging | 4.60 | 4.60 | +0.00 |
| 49 | observability/monitoring | 4.60 | 3.00 | -1.60 |
| 50 | observability/stack-monitoring | 2.00 | 4.60 | +2.60 |
| 51 | platform/backup-governance | 2.80 | 4.60 | +1.80 |
| 52 | platform/sre-operations | 2.20 | 3.60 | +1.40 |
| 53 | security/cloud-guard | 4.60 | 4.60 | +0.00 |
| 54 | security/dynamic-groups | 1.40 | 4.80 | +3.40 |
| 55 | security/encryption | 4.60 | 4.60 | +0.00 |
| 56 | security/federation | 4.40 | 3.60 | -0.80 |
| 57 | security/iam-basics | 1.60 | 4.60 | +3.00 |
| 58 | security/policies | 1.80 | 3.40 | +1.60 |
| 59 | security/posture-management | 5.00 | 4.80 | -0.20 |
| 60 | security/vault-keys | 4.00 | 4.60 | +0.60 |
| 61 | security/vault-secrets | 3.20 | 4.60 | +1.40 |
| 62 | security/waf | 1.40 | 4.60 | +3.20 |
| 63 | security/zero-trust | 4.40 | 3.20 | -1.20 |
| 64 | serverless/api-gateway | 4.20 | 2.40 | -1.80 |
| 65 | serverless/functions | 4.40 | 4.60 | +0.20 |
| 66 | storage/block | 1.20 | 4.40 | +3.20 |
| 67 | storage/file | 2.40 | 2.60 | +0.20 |
| 68 | storage/object | 1.00 | 4.60 | +3.60 |
| 69 | terraform/compute | 4.40 | 3.40 | -1.00 |
| 70 | terraform/container | 2.60 | 4.40 | +1.80 |
| 71 | terraform/database | 5.00 | 3.40 | -1.60 |
| 72 | terraform/devops | 4.00 | 4.00 | +0.00 |
| 73 | terraform/load-balancer | 3.80 | 4.80 | +1.00 |
| 74 | terraform/networking | 2.20 | 4.40 | +2.20 |
| 75 | terraform/observability | 3.60 | 4.80 | +1.20 |
| 76 | terraform/provider | 2.00 | 2.60 | +0.60 |
| 77 | terraform/security | 3.40 | 4.60 | +1.20 |
| 78 | terraform/serverless | 4.00 | 4.60 | +0.60 |
| 79 | terraform/state | 4.60 | 3.80 | -0.80 |
| 80 | terraform/storage | 4.80 | 4.20 | -0.60 |
| 81 | troubleshooting/authentication | 2.00 | 4.60 | +2.60 |
| 82 | troubleshooting/compute | 4.60 | 4.40 | -0.20 |
| 83 | troubleshooting/connectivity | 4.20 | 4.40 | +0.20 |
| 84 | troubleshooting/database | 4.20 | 4.60 | +0.40 |
| 85 | troubleshooting/functions | 1.80 | 3.40 | +1.60 |
| 86 | troubleshooting/oke | 1.40 | 4.40 | +3.00 |
| 87 | troubleshooting/performance | 1.00 | 4.80 | +3.80 |
| 88 | troubleshooting/storage | 4.20 | 4.80 | +0.60 |

</sub>
</details>

---

## Roadmap

As seguintes melhorias estão planejadas:

1. **Integração com OpenRouter**: Roteamento para modelos de fronteira (Claude/GPT-4) em tarefas complexas.

---

## Hugging Face Hub

O modelo treinado e o dataset estão disponíveis no Hugging Face:

| Recurso | URL |
|---------|-----|
| **Safetensors** | https://huggingface.co/otavio-lemos/oci-copilot-jr-safetensors |
| **GGUF** | https://huggingface.co/otavio-lemos/oci-copilot-jr-gguf |
| **Dataset** | https://huggingface.co/datasets/otavio-lemos/oci-copilot-jr-dataset |

### Arquivos do Modelo (Safetensors)
- `adapters/` - LoRA adapters do Cycle 1
- `safetensors/bf16/` - Modelo em BF16
- `safetensors/q4/` - Modelo quantizado Q4

### Arquivos do Modelo (GGUF)
- `oci-specialist-Q4_K_M.gguf` - Versão quantizada Q4 (4.6GB)
- `oci-specialist-FP16.gguf` - Versão FP16 (~15GB)
- `eval_results.json` - Resultados da avaliação

### Dataset
- `train.jsonl` - 9.897 exemplos
- `valid.jsonl` - 1.979 exemplos  
- `eval.jsonl` - 1.320 exemplos

---

## Agradecimentos

Este projeto foi desenvolvido integrando as seguintes tecnologias de ponta:

- **Hardware**: Apple Silicon (M3 Pro) com Memória Unificada.
- **Treinamento e Inferência**: [MLX Framework](https://mlx.ai) e [MLX-Tune](https://github.com/Aaronipher/mlx-tune).
- **Modelo Base**: [Qwen 2.5 Coder 7B Instruct](https://huggingface.co/Qwen/Qwen2.5-Coder-7B-Instruct) (Alibaba Cloud).
- **Orquestração de Agentes**: [LangGraph](https://python.langchain.com/docs/langgraph) e [LangChain](https://langchain.com).
- **Interface do Usuário**: [Chainlit](https://chainlit.io).
- **Serviços de Backend**: [FastAPI](https://fastapi.tiangolo.com).
- **Motores de Busca (RAG Híbrida)**: [FAISS](https://github.com/facebookresearch/faiss) (Dense) e [Rank-BM25](https://github.com/dorianbrown/rank_bm25) (Sparse).
- **Embeddings e Re-ranking**: [Hugging Face](https://huggingface.co) e [Sentence-Transformers](https://sbert.net).
- **Desenvolvimento**: [Python 3.12](https://www.python.org).
- **Dados**: Sintetizados e validados especificamente para cenários de Oracle Cloud Infrastructure (OCI).

---

## Licença

Este projeto está licenciado sob a Licença MIT. Veja o arquivo [LICENSE](LICENSE) para detalhes.

