# OCI Specialist LLM

[🇺🇸 English](README.en-US.md) | [🇧🇷 Português](README.md)

Large Language Model (LLM) fine-tuned for Oracle Cloud Infrastructure (OCI) using Apple Silicon, MLX, and LoRA.

[![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.12-blue?style=flat-square&logo=python&logoColor=white)](https://www.python.org)
[![MLX](https://img.shields.io/badge/MLX-Apple%20Silicon-orange?style=flat-square)](https://mlx.ai)
[![MLX-Tune](https://img.shields.io/badge/Finetune-MLX--Tune-blue?style=flat-square)](https://github.com/Aaronipher/mlx-tune)
[![Model](https://img.shields.io/badge/Base%20Model-Qwen2.5--Coder--7B--Instruct--4bit-purple?style=flat-square)](https://huggingface.co/mlx-community/Qwen2.5-Coder-7B-Instruct-4bit)
[![Dataset](https://img.shields.io/badge/Dataset-10299_examples-green?style=flat-square)](docs/taxonomy.md)
[![LangGraph](https://img.shields.io/badge/Orchestration-LangGraph-black?style=flat-square&logo=langchain)](https://python.langchain.com/docs/langgraph)
[![Chainlit](https://img.shields.io/badge/UI-Chainlit-orange?style=flat-square)](https://chainlit.io)
[![FastAPI](https://img.shields.io/badge/API-FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![FAISS](https://img.shields.io/badge/Dense-FAISS-76b900?style=flat-square)](https://github.com/facebookresearch/faiss)
[![BM25](https://img.shields.io/badge/Sparse-BM25-007acc?style=flat-square)](https://github.com/dorianbrown/rank_bm25)
[![Rerank](https://img.shields.io/badge/Rerank-Cross--Encoder-red?style=flat-square)](https://www.sbert.net/docs/pretrained_models.html#cross-encoders)
[![Hugging Face](https://img.shields.io/badge/%F0%9F%A4%97-Hugging%20Face-yellow?style=flat-square)](https://huggingface.co)

---

> **Language**: Data and prompts in Brazilian Portuguese (PT-BR).

### 🚀 Core Stack & Components
- **Base LLM**: [Qwen 2.5 Coder 7B Instruct](https://huggingface.co/Qwen/Qwen2.5-Coder-7B-Instruct) (4-bit).
- **Agent Orchestration**: [LangGraph](https://python.langchain.com/docs/langgraph) (Multi-Agent State Machine).
- **Agents Framework**: [LangChain](https://langchain.com) (Chain of Thought).
- **OCI Copilot Interface**: [Chainlit](https://chainlit.io) (Interactive UI with HITL).
- **Training**: [MLX-Tune](https://github.com/Aaronipher/mlx-tune) (SFTTrainer API).
- **Inference**: [MLX Framework](https://mlx.ai) (Apple Silicon Native).
- **RAG Dense**: [FAISS](https://github.com/facebookresearch/faiss) (Semantic Search).
- **RAG Sparse**: [Rank-BM25](https://github.com/dorianbrown/rank_bm25) (Lexical Search).
- **RAG Re-ranking**: [Sentence-Transformers](https://sbert.net) (Cross-Encoder).
- **RAG Fusion**: Reciprocal Rank Fusion (RRF).
- **Backend API**: [FastAPI](https://fastapi.tiangolo.com).
- **Embeddings**: [Hugging Face](https://huggingface.co) (all-MiniLM-L6-v2).
- **Hardware**: Optimized for Apple Silicon (M3 Pro 18GB).
- **Development**: Python 3.12.

---

## Overview

This project trains a specialized LLM for Oracle Cloud Infrastructure using Apple's MLX framework on Apple Silicon. The pipeline covers dataset generation, validation, fine-tuning via MLX LoRA, weight fusion (Merge), and integration with a RAG layer (OCI Copilot).

```mermaid
flowchart TD
    subgraph GENERATION["1. Generation & Preparation"]
        A1["generate_e2e_diverse.py\n(CLI real, 87 cats)"] --> A2["prepare_data.sh"]
        A2 --> A3["train.jsonl / valid.jsonl"]
    end

    subgraph TRAINING["2. Training & Merge"]
        B1["train_mlx_tune.py"] --> B2["LoRA Adapters"]
        B2 --> B3["Merge & Export (GGUF)"]
    end

    subgraph RAG["3. OCI Copilot (RAG)"]
        C1["update_rag.py (Offline)"] --> C2["FAISS / BM25 Indices"]
        C2 --> C3["FastAPI Backend"]
    end

    subgraph UI["4. Interface & Agents"]
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

## Features

- **LoRA Fine-tuning**: Low-rank adaptation with **Qwen 2.5 Coder 7B Instruct** (4-bit) base model.
- **M3 Pro Optimized**: Hyper-optimized configurations for 18GB RAM, using **native BF16** and zero disk Swap.
- **Advanced Hybrid RAG**: Semantic (FAISS) + Lexical (BM25) search with local persistence and **Offline Ingestion**.
- **Semantic Re-ranking**: Use of **Cross-Encoders** to validate the relevance of retrieved documents.
- **Multi-Agent System**: Orchestration via **LangGraph** (Router, Discovery, Architecture, Execution).
- **OCI Copilot Interface**: UI built with **Chainlit**, supporting file attachments, token streaming, and **Human-in-the-loop** for safe CLI commands.
- **Merge & Export**: Pipeline to fuse LoRA adapters into the base model and export to GGUF format (local quantization).
- **Automated Evaluation**: Benchmark pipeline to measure technical accuracy, hallucination, and depth.

---

## Dataset

| Metric | Value |
|--------|-------|
| **Total Generated** | 15,660 examples (87 categories × 180) |
| **After Clean/Dedup** | 10,299 examples |
| **Train** | 7,724 examples (75%) |
| **Valid** | 1,544 examples (15%) |
| **Eval** | 1,031 examples (10%) |
| **Categories** | 87 OCI topics |

### Split

| Split | Examples | % |
|-------|----------|---|
| Train | 7,724 | 75% |
| Valid | 1,544 | 15% |
| Eval | 1,031 | 10% |
| Eval | 2,133 | 10% |

---

## Training

Training uses the MLX-Tune framework, optimized for maximum performance on Apple Silicon M3 Pro.

> [!IMPORTANT]
> **All commands below must be executed from the project root directory.**

### 0. Cloning the Repository

```bash
git clone https://github.com/otavio-lemos/olia-2-oci.git
cd olia-2-oci
```

### 1. Environment Setup

```bash
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Execution

```bash
# Run the consolidated training cycle
bash training/run_all_cycles.sh --fresh
```

### 3. Weight Fusion (Merge) & Export

After training, you must merge the LoRA adapters with the base model and export to GGUF format (compatible with llama.cpp/Ollama).

```bash
# Merge and export to GGUF Q4
python scripts/merge_export.py --cycle cycle-1 --quant q4 --name oci-specialist
```

### Optimized Configuration (`config/cycle-1.env`)

<details>
<summary><b>Click to view Full .env Configuration (26 parameters)</b></summary>
<sub>

| Parameter | Value | Description |
|-----------|-------|-------------|
| **MODEL** | `mlx-community/Qwen2.5-Coder-7B-Instruct-4bit` | Optimized base model |
| **TRAIN_DATA** | `data/train.jsonl` | Training dataset |
| **VALID_DATA** | `data/valid.jsonl` | Validation dataset |
| **OUTPUT_DIR** | `outputs/cycle-1` | Output directory |
| **PREV_ADAPTER** | `""` | Previous adapter (if any) |
| **BATCH_SIZE** | 1 | Batch size per iteration |
| **LEARNING_RATE** | 2e-4 | Learning rate |
| **LORA_RANK** | 16 | LoRA Rank |
| **LORA_ALPHA** | 32 | LoRA Alpha |
| **NUM_LAYERS** | 28 | Number of LoRA layers (100%) |
| **TARGET_MODULES** | `"q_proj,k_proj,v_proj,o_proj,gate_proj,up_proj,down_proj"` | Target modules |
| **ITERS** | 4000 | Total iterations |
| **MAX_SEQ_LENGTH** | 768 | Maximum sequence length |
| **VAL_BATCHES** | 5 | Validation batches |
| **EVAL_STEPS** | 250 | Steps between evaluations |
| **LOGGING_STEPS** | 1 | Steps between logging |
| **SAVE_STEPS** | 500 | Steps between saves |
| **WARMUP_STEPS** | 320 | Warmup steps |
| **GRADIENT_CHECKPOINTING**| false | Gradient checkpointing |
| **LR_SCHEDULER** | `cosine` | LR scheduler |
| **WEIGHT_DECAY** | 0.01 | Weight decay |
| **SEED** | 42 | Random seed |
| **GRAD_CLIP_NORM** | 1.0 | Gradient clip norm |
| **BF16** | true | Native M3 acceleration |

</sub>
</details>

---

## Evaluation

The evaluation pipeline compares the fine-tuned model against the base model using:
- **Automatic scoring**: Correctness, Depth, Structure, Hallucination, Clarity
- **Semantic similarity**: Sentence Transformers (MiniLM-L6-v2)
- **Self-Judge (optional)**: LLM-as-Judge using the model itself for self-evaluation

```bash
# Quick Test (10 samples, ~2 min)
python scripts/unified_evaluation.py --cycle cycle-1 --mode small --fresh

# Recommended Evaluation (200 stratified samples, ~30 min)
python scripts/unified_evaluation.py --cycle cycle-1 --mode medium --fresh

# Full Evaluation (2133 samples, ~4-6 hours)
python scripts/unified_evaluation.py --cycle cycle-1 --mode full --fresh

# Evaluation with Self-Judge (LLM-as-Judge using the model itself)
python scripts/unified_evaluation.py --cycle cycle-1 --mode medium --self-judge --judge-lang en
```

### Evaluation Parameters

| Parameter | Description |
|-----------|-------------|
| `--mode small/test` | 10 samples (1 per category) |
| `--mode medium` | 200 samples (stratified) |
| `--mode full` | All samples (~2100) |
| `--self-judge` | Enable LLM-as-Judge (doubles execution time) |
| `--judge-lang pt\|en` | Judge rubric language (default: en) |
| `--judge-tokens` | Max tokens for judge response (default: 256) |
| `--max-tokens` | Max tokens for model response (default: 256) |
| `--fresh` | Clear output directory before running |

### Summary of Results (200 Samples Evaluation)

| Metric | Base Model | Fine-Tuned (Cycle 1) | Delta |
|--------|-------------|------------|-------|
| technical_correctness | 3.40 | 3.40 | +0.00 |
| depth | 2.60 | 2.60 | +0.00 |
| structure | 4.00 | 4.44 | +0.45 |
| hallucination | 3.58 | 4.68 | +1.10 |
| clarity | 3.50 | 3.37 | -0.13 |
| **Overall** | **3.42** | **3.70** | **+0.28** |

Results: [benchmark](#benchmark)

---

## RAG (Retrieval-Augmented Generation)

OCI Copilot uses a persistent RAG layer to access real-time facts from Oracle documentation.

### 1. RAG Setup

```bash
python3.12 -m venv venv-rag
source venv-rag/bin/activate
pip install -r requirements-rag.txt
```

### 2. Offline Ingestion (Mandatory)
To save RAM during chat, indices must be generated offline:
```bash
python scripts/update_rag.py
```

### 3. Orchestration and Agents
The agent ecosystem is orchestrated via **LangGraph** and served via **FastAPI** and **Chainlit**.

**Start Backend API (RAG Indices):**
```bash
uvicorn rag.api:app --host 0.0.0.0 --port 8000
```

**Start Orchestrator and UI (Copilot Interface):**
```bash
chainlit run rag/app_chainlit.py -w
```

---

## Inference and UI

After training and merge, use the official **Chainlit** interface to interact with the Copilot.

### 1. Start RAG Backend
```bash
uvicorn rag.api:app --port 8000
```

### 2. Start Visual Interface
```bash
chainlit run rag/app_chainlit.py -w
```
Access at: `http://localhost:8000` (or configured port).

---

## Benchmark

### How to Evaluate
To generate new benchmark reports, follow the instructions in the [Evaluation](#evaluation) section.

### Metrics Comparison
![Comparison Chart](outputs/cycle-1/benchmarks/comparison_chart_20260416_101519.png)

### Performance by Category
![Category Chart](outputs/cycle-1/benchmarks/category_chart_20260416_101519.png)

### Summary of Results

| Metric | Base Model | Fine-Tuned | Delta |
|--------|-------------|------------|-------|
| technical_correctness | 3.40 | 3.40 | +0.00 |
| depth | 2.60 | 2.60 | +0.00 |
| structure | 4.00 | 4.44 | +0.45 |
| hallucination | 3.58 | 4.68 | +1.10 |
| clarity | 3.50 | 3.37 | -0.13 |
| **Overall** | **3.42** | **3.70** | **+0.28** |

### Top Gains by Topic (Top 5)
1. **Troubleshooting Connectivity**: +0.66
2. **Troubleshooting Storage**: +0.66
3. **FinOps Cost-Optimization**: +0.60
4. **DevOps Secrets**: +0.50
5. **Security Encryption**: +0.50

### Detailed Category Results (86 Topics)

<details>
<summary>Click to expand the performance by category table</summary>
<sub>

| # | Category | Base | FT | Delta |
|---|----------|------|----|-------|
| 1 | compute/custom-images | 3.59 | 3.63 | +0.05 |
| 2 | compute/instances | 3.56 | 3.60 | +0.05 |
| 3 | compute/scaling | 3.33 | 3.69 | +0.36 |
| 4 | container/instances | 3.29 | 3.61 | +0.32 |
| 5 | container/oke | 3.28 | 3.61 | +0.33 |
| 6 | database/autonomous | 3.37 | 3.68 | +0.30 |
| 7 | database/autonomous-json | 3.51 | 3.70 | +0.19 |
| 8 | database/exadata | 3.55 | 3.60 | +0.05 |
| 9 | database/exadata-cloud | 3.54 | 3.71 | +0.17 |
| 10 | database/mysql | 3.51 | 3.69 | +0.18 |
| 11 | database/nosql | 3.52 | 3.76 | +0.24 |
| 12 | database/postgresql | 3.55 | 3.66 | +0.11 |
| 13 | devops/artifacts | 3.31 | 3.67 | +0.37 |
| 14 | devops/ci-cd | 3.39 | 3.60 | +0.20 |
| 15 | devops/resource-manager | 3.55 | 3.76 | +0.21 |
| 16 | devops/secrets | 3.20 | 3.70 | +0.50 |
| 17 | finops/cost-optimization | 3.24 | 3.84 | +0.60 |
| 18 | finops/rightsizing | 3.47 | 3.79 | +0.31 |
| 19 | finops/showback-chargeback | 3.61 | 3.61 | +0.00 |
| 20 | finops/storage-tiering | 3.46 | 3.56 | +0.11 |
| 21 | governance/audit-readiness | 3.36 | 3.70 | +0.34 |
| 22 | governance/budgets-cost | 3.52 | 3.62 | +0.10 |
| 23 | governance/compartments | 3.37 | 3.70 | +0.33 |
| 24 | governance/compliance | 3.31 | 3.67 | +0.36 |
| 25 | governance/landing-zone | 3.47 | 3.67 | +0.21 |
| 26 | governance/policies-guardrails | 3.30 | 3.72 | +0.42 |
| 27 | governance/resource-discovery | 3.29 | 3.66 | +0.37 |
| 28 | governance/tagging | 3.42 | 3.62 | +0.20 |
| 29 | lb/load-balancer | 3.53 | 3.63 | +0.10 |
| 30 | migration/aws-database | 3.60 | 3.83 | +0.23 |
| 31 | migration/azure-compute | 3.37 | 3.65 | +0.28 |
| 32 | migration/azure-database | 3.50 | 3.81 | +0.31 |
| 33 | migration/azure-storage | 3.27 | 3.65 | +0.38 |
| 34 | migration/data-transfer | 3.16 | 3.68 | +0.52 |
| 35 | migration/gcp-compute | 3.37 | 3.81 | +0.44 |
| 36 | migration/gcp-database | 3.40 | 3.79 | +0.39 |
| 37 | migration/gcp-storage | 3.28 | 3.73 | +0.45 |
| 38 | migration/onprem-compute | 3.42 | 3.79 | +0.37 |
| 39 | migration/onprem-database | 3.45 | 3.75 | +0.30 |
| 40 | migration/onprem-storage | 3.49 | 3.78 | +0.29 |
| 41 | migration/onprem-vmware | 3.37 | 3.71 | +0.34 |
| 42 | networking/connectivity | 3.38 | 3.64 | +0.26 |
| 43 | networking/security | 3.53 | 3.75 | +0.21 |
| 44 | networking/vcn | 3.62 | 3.68 | +0.07 |
| 45 | observability/apm | 3.38 | 3.66 | +0.28 |
| 46 | observability/logging | 3.49 | 3.66 | +0.18 |
| 47 | observability/monitoring | 3.34 | 3.67 | +0.33 |
| 48 | observability/stack-monitoring | 3.45 | 3.70 | +0.25 |
| 49 | platform/backup-governance | 3.27 | 3.72 | +0.46 |
| 50 | platform/sre-operations | 3.35 | 3.65 | +0.30 |
| 51 | security/cloud-guard | 3.55 | 3.72 | +0.17 |
| 52 | security/dynamic-groups | 3.43 | 3.72 | +0.29 |
| 53 | security/encryption | 3.18 | 3.68 | +0.50 |
| 54 | security/federation | 3.44 | 3.61 | +0.17 |
| 55 | security/iam-basics | 3.29 | 3.61 | +0.32 |
| 56 | security/policies | 3.51 | 3.76 | +0.25 |
| 57 | security/posture-management | 3.29 | 3.76 | +0.47 |
| 58 | security/vault-keys | 3.56 | 3.71 | +0.15 |
| 59 | security/vault-secrets | 3.66 | 3.66 | +0.00 |
| 60 | security/waf | 3.31 | 3.71 | +0.40 |
| 61 | security/zero-trust | 3.50 | 3.59 | +0.09 |
| 62 | serverless/api-gateway | 3.33 | 3.66 | +0.33 |
| 63 | serverless/functions | 3.53 | 3.58 | +0.05 |
| 64 | storage/block | 3.49 | 3.70 | +0.21 |
| 65 | storage/file | 3.32 | 3.71 | +0.39 |
| 66 | storage/object | 3.43 | 3.69 | +0.26 |
| 67 | terraform/compute | 3.31 | 3.67 | +0.35 |
| 68 | terraform/container | 3.37 | 3.66 | +0.29 |
| 69 | terraform/database | 3.47 | 3.72 | +0.25 |
| 70 | terraform/devops | 3.35 | 3.61 | +0.26 |
| 71 | terraform/load-balancer | 3.47 | 3.62 | +0.14 |
| 72 | terraform/networking | 3.37 | 3.71 | +0.34 |
| 73 | terraform/observability | 3.23 | 3.75 | +0.52 |
| 74 | terraform/provider | 3.56 | 3.66 | +0.10 |
| 75 | terraform/security | 3.40 | 3.73 | +0.33 |
| 76 | terraform/serverless | 3.41 | 3.70 | +0.30 |
| 77 | terraform/state | 3.45 | 3.76 | +0.31 |
| 78 | terraform/storage | 3.27 | 3.69 | +0.42 |
| 79 | troubleshooting/authentication | 3.38 | 3.84 | +0.46 |
| 80 | troubleshooting/compute | 3.63 | 3.71 | +0.08 |
| 81 | troubleshooting/connectivity | 3.16 | 3.82 | +0.66 |
| 82 | troubleshooting/database | 3.52 | 3.77 | +0.25 |
| 83 | troubleshooting/functions | 3.31 | 3.80 | +0.49 |
| 84 | troubleshooting/oke | 3.63 | 3.82 | +0.18 |
| 85 | troubleshooting/performance | 3.43 | 3.72 | +0.29 |
| 86 | troubleshooting/storage | 3.19 | 3.85 | +0.66 |

</sub>
</details>

---

## Roadmap

The following improvements are planned:

1. **OpenRouter Integration**: Routing to frontier models (Claude/GPT-4) for complex tasks.
2. **Hugging Face Hub Export**: Publishing trained adapters and quantized models.

---

## Acknowledgments

This project was developed by integrating the following cutting-edge technologies:

- **Hardware**: Apple Silicon (M3 Pro) with Unified Memory.
- **Training and Inference**: [MLX Framework](https://mlx.ai) and [MLX-Tune](https://github.com/Aaronipher/mlx-tune).
- **Base Model**: [Qwen 2.5 Coder 7B Instruct](https://huggingface.co/Qwen/Qwen2.5-Coder-7B-Instruct) (Alibaba Cloud).
- **Agent Orchestration**: [LangGraph](https://python.langchain.com/docs/langgraph) and [LangChain](https://langchain.com).
- **User Interface**: [Chainlit](https://chainlit.io).
- **Backend Services**: [FastAPI](https://fastapi.tiangolo.com).
- **Search Engines (RAG Hybrid)**: [FAISS](https://github.com/facebookresearch/faiss) (Dense), [Rank-BM25](https://github.com/dorianbrown/rank_bm25) (Sparse) and [Sentence-Transformers](https://sbert.net) (Cross-Encoder Re-ranking).
- **Embeddings**: [Hugging Face](https://huggingface.co) and [Sentence-Transformers](https://sbert.net).
- **Development**: [Python 3.12](https://www.python.org).
- **Data**: Synthesized and validated specifically for Oracle Cloud Infrastructure (OCI) scenarios.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
