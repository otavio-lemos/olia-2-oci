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
- **Sistema Multi-Agentes**: Orquestração via **LangGraph** (Router, Descoberta, Arquitetura, Execução).
- **Interface OCI Copilot**: UI construída com **Chainlit**, suportando anexos de arquivos, streaming de tokens e **Human-in-the-loop** para segurança em comandos CLI.
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
# Avaliação Rápida (10 amostras, ~2 min) - modelo específico obrigatório
python scripts/unified_evaluation_v2.py --cycle cycle-1 --ft-model outputs/cycle-1/safetensors/q4 --mode small --fresh

# Avaliação Completa (2133 amostras, ~4-6 horas)
python scripts/unified_evaluation_v2.py --cycle cycle-1 --ft-model outputs/cycle-1/safetensors/q4 --mode full --fresh

# Avaliação com Judge (LLM-as-Judge usando modelo diferente)
python scripts/unified_evaluation_v2.py --cycle cycle-1 --ft-model outputs/cycle-1/safetensors/q4 --mode medium --external-judge --judge-lang pt --judge-tokens 768 --max-tokens 768
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

### Resumo dos Resultados (Avaliação 200 amostras)

| Métrica | Modelo Base | Fine-Tuned (Cycle 1) | Delta |
|--------|-------------|------------|-------|
| technical_correctness | 3.67 | 4.51 | +0.84 |
| depth | 3.11 | 3.93 | +0.82 |
| structure | 3.47 | 4.45 | +0.98 |
| hallucination | 3.23 | 3.95 | +0.72 |
| clarity | 3.07 | 3.06 | -0.01 |
| **Overall** | **3.31** | **3.98** | **+0.67** |

### Avaliação Externa (Llama 3.1 8B Judge)

| Métrica | Modelo Base | Fine-Tuned | Delta |
|--------|-------------|------------|-------|
| technical_correctness | 3.94 | 4.29 | +0.35 |
| depth | 4.04 | 4.58 | +0.54 |
| structure | 3.91 | 4.46 | +0.55 |
| hallucination | 4.17 | 4.33 | +0.16 |
| clarity | 3.97 | 4.36 | +0.39 |
| **Overall** | **4.01** | **4.40** | **+0.40** |

### Como avaliar
Para gerar novos relatórios, utilize os comandos detalhados na seção [Avaliação](#avaliação).

### Comparação de Métricas
![Gráfico de Comparação](outputs/cycle-1/benchmarks/comparison_chart_20260418_220044.png)

### Performance por Categoria
![Gráfico de Categorias](outputs/cycle-1/benchmarks/category_chart_20260418_220044.png)

### Principais Ganhos por Tópico (Top 5)
1. **governance/tagging**: +2.20
2. **security/posture-management**: +2.24
3. **terraform/state**: +2.00
4. **security/waf**: +1.84
5. **troubleshooting/functions**: +1.86

### Resultados Detalhados por Categoria (88 Tópicos)

<details>
<summary>Clique para expandir a tabela de performance por categoria</summary>
<sub>

| # | Categoria | Base | FT | Delta |
|---|---------|------|----|-------|
| 1 | compute/custom-images | 2.59 | 3.81 | +1.22 |
| 2 | compute/instances | 2.91 | 4.34 | +1.43 |
| 3 | compute/scaling | 3.56 | 4.45 | +0.89 |
| 4 | container/instances | 2.08 | 3.90 | +1.82 |
| 5 | container/oke | 2.77 | 3.38 | +0.61 |
| 6 | database/autonomous | 2.72 | 3.31 | +0.60 |
| 7 | database/autonomous-json | 4.17 | 4.00 | -0.17 |
| 8 | database/exadata | 3.68 | 3.78 | +0.09 |
| 9 | database/exadata-cloud | 2.43 | 4.14 | +1.71 |
| 10 | database/mysql | 3.77 | 4.21 | +0.44 |
| 11 | database/nosql | 2.83 | 4.12 | +1.29 |
| 12 | database/postgresql | 2.06 | 3.64 | +1.58 |
| 13 | devops/artifacts | 3.95 | 3.94 | -0.01 |
| 14 | devops/ci-cd | 2.99 | 4.34 | +1.34 |
| 15 | devops/resource-manager | 3.84 | 4.02 | +0.18 |
| 16 | devops/secrets | 3.72 | 4.07 | +0.35 |
| 17 | finops/cost-optimization | 3.76 | 4.01 | +0.25 |
| 18 | finops/rightsizing | 3.78 | 4.04 | +0.26 |
| 19 | finops/showback-chargeback | 3.88 | 4.39 | +0.51 |
| 20 | finops/storage-tiering | 4.09 | 4.37 | +0.27 |
| 21 | governance/audit-readiness | 2.99 | 4.38 | +1.39 |
| 22 | governance/budgets-cost | 3.24 | 3.79 | +0.55 |
| 23 | governance/compartments | 2.98 | 4.13 | +1.16 |
| 24 | governance/compliance | 2.21 | 2.74 | +0.53 |
| 25 | governance/landing-zone | 3.37 | 4.28 | +0.91 |
| 26 | governance/policies-guardrails | 4.16 | 4.27 | +0.10 |
| 27 | governance/resource-discovery | 2.92 | 3.91 | +0.99 |
| 28 | governance/tagging | 1.78 | 3.98 | +2.20 |
| 29 | lb/load-balancer | 3.89 | 4.21 | +0.32 |
| 30 | migration/aws-compute | 4.00 | 3.95 | -0.06 |
| 31 | migration/aws-database | 4.22 | 4.18 | -0.03 |
| 32 | migration/aws-storage | 4.31 | 4.48 | +0.17 |
| 33 | migration/azure-compute | 3.12 | 4.07 | +0.94 |
| 34 | migration/azure-database | 3.63 | 4.28 | +0.65 |
| 35 | migration/azure-storage | 3.43 | 4.39 | +0.97 |
| 36 | migration/data-transfer | 2.67 | 3.92 | +1.25 |
| 37 | migration/gcp-compute | 3.97 | 4.18 | +0.21 |
| 38 | migration/gcp-database | 3.85 | 4.12 | +0.27 |
| 39 | migration/gcp-storage | 3.00 | 4.29 | +1.29 |
| 40 | migration/onprem-compute | 2.89 | 4.04 | +1.15 |
| 41 | migration/onprem-database | 3.93 | 4.03 | +0.11 |
| 42 | migration/onprem-storage | 2.69 | 4.27 | +1.57 |
| 43 | migration/onprem-vmware | 4.04 | 3.82 | -0.22 |
| 44 | networking/connectivity | 3.39 | 4.13 | +0.74 |
| 45 | networking/security | 3.82 | 3.52 | -0.31 |
| 46 | networking/vcn | 2.68 | 3.62 | +0.94 |
| 47 | observability/apm | 4.15 | 3.68 | -0.47 |
| 48 | observability/logging | 3.80 | 4.35 | +0.54 |
| 49 | observability/monitoring | 4.04 | 3.89 | -0.15 |
| 50 | observability/stack-monitoring | 2.71 | 4.10 | +1.39 |
| 51 | platform/backup-governance | 4.11 | 4.42 | +0.31 |
| 52 | platform/sre-operations | 3.72 | 4.11 | +0.40 |
| 53 | security/cloud-guard | 2.73 | 4.31 | +1.58 |
| 54 | security/dynamic-groups | 3.27 | 3.94 | +0.67 |
| 55 | security/encryption | 3.96 | 3.91 | -0.05 |
| 56 | security/federation | 3.94 | 4.08 | +0.14 |
| 57 | security/iam-basics | 2.67 | 3.96 | +1.29 |
| 58 | security/policies | 3.95 | 2.69 | -1.26 |
| 59 | security/posture-management | 1.92 | 4.17 | +2.24 |
| 60 | security/vault-keys | 4.17 | 4.00 | -0.17 |
| 61 | security/vault-secrets | 2.94 | 3.95 | +1.01 |
| 62 | security/waf | 2.17 | 4.01 | +1.84 |
| 63 | security/zero-trust | 3.50 | 3.85 | +0.36 |
| 64 | serverless/api-gateway | 3.59 | 3.63 | +0.04 |
| 65 | serverless/functions | 2.93 | 3.59 | +0.66 |
| 66 | storage/block | 3.94 | 4.11 | +0.17 |
| 67 | storage/file | 2.87 | 3.88 | +1.00 |
| 68 | storage/object | 2.04 | 3.05 | +1.00 |
| 69 | terraform/compute | 3.65 | 4.02 | +0.37 |
| 70 | terraform/container | 3.19 | 4.17 | +0.98 |
| 71 | terraform/database | 3.24 | 3.80 | +0.56 |
| 72 | terraform/devops | 2.83 | 4.15 | +1.32 |
| 73 | terraform/load-balancer | 2.95 | 4.00 | +1.05 |
| 74 | terraform/networking | 4.29 | 4.13 | -0.16 |
| 75 | terraform/observability | 2.65 | 3.60 | +0.96 |
| 76 | terraform/provider | 3.81 | 3.31 | -0.50 |
| 77 | terraform/security | 2.75 | 4.11 | +1.36 |
| 78 | terraform/serverless | 4.22 | 4.32 | +0.10 |
| 79 | terraform/state | 1.95 | 3.95 | +2.00 |
| 80 | terraform/storage | 3.51 | 4.11 | +0.60 |
| 81 | troubleshooting/authentication | 3.11 | 4.31 | +1.20 |
| 82 | troubleshooting/compute | 3.42 | 3.39 | -0.03 |
| 83 | troubleshooting/connectivity | 3.73 | 4.04 | +0.31 |
| 84 | troubleshooting/database | 3.34 | 3.61 | +0.27 |
| 85 | troubleshooting/functions | 1.98 | 3.84 | +1.86 |
| 86 | troubleshooting/oke | 3.51 | 4.07 | +0.57 |
| 87 | troubleshooting/performance | 2.63 | 3.37 | +0.74 |
| 88 | troubleshooting/storage | 3.64 | 4.13 | +0.48 |

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
| **Modelo (GGUF Q4)** | https://huggingface.co/otavio-lemos/oci-copilot-jr |
| **Dataset** | https://huggingface.co/datasets/otavio-lemos/oci-copilot-jr-dataset |

### Arquivos do Modelo
- `model-Q4_K_M.gguf` - Versão quantizada Q4 (4.6GB)
- `model-fp16.gguf` - Versão FP16 (~15GB)
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

