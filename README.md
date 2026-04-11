# OCI Specialist LLM

Fine-tuned Large Language Model for Oracle Cloud Infrastructure (OCI) using Apple Silicon, MLX, and LoRA.

[![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.12-blue?style=flat-square&logo=python&logoColor=white)](https://www.python.org)
[![MLX](https://img.shields.io/badge/MLX-Apple%20Silicon-orange?style=flat-square)](https://mlx.ai)
[![Model](https://img.shields.io/badge/Base%20Model-Meta--Llama--3.1--8B--Instruct--4bit-purple?style=flat-square)](https://huggingface.co/mlx-community/Meta-Llama-3.1-8B-Instruct-4bit)
[![Dataset](https://img.shields.io/badge/Dataset-19294_examples-green?style=flat-square)](docs/taxonomy.md)

> **Language**: Data and prompts in Brazilian Portuguese (PT-BR).

---

## Overview

This project trains a specialized LLM for Oracle Cloud Infrastructure using Apple's MLX framework on Apple Silicon. The pipeline covers dataset generation, validation, MLX LoRA fine-tuning, and evaluation.

```mermaid
flowchart LR
    subgraph GENERATION["Phase 1: Generation"]
        A["generate_diverse_v2.py"]
        A --> B["data/curated/<br/>87 JSONL files"]
    end

    subgraph PREPARATION["Phase 2: Preparation"]
        B --> C1["Concat<br/>all_curated.jsonl"]
        C1 --> C2["Validate<br/>validate_jsonl.py"]
        C2 --> C3["Clean<br/>clean_dataset.py"]
        C3 --> C4["Dedup<br/>dedupe_embedding.py"]
        C4 --> C5["Split<br/>build_dataset_fixed.py"]
        C5 --> D["train.jsonl<br/>valid.jsonl<br/>eval.jsonl"]
    end

    subgraph TRAINING["Phase 3: Training"]
        D --> E["train_mlx_tune.py"]
        E --> F["outputs/cycle-1/adapters/<br/>adapters.safetensors"]
    end

    subgraph EXPORT["Phase 4: Export"]
        F --> G1["mlx_lm fuse<br/>→ merged-model"]
        F --> G2["merge_export.py<br/>→ GGUF (Q4/Q5/Q8)"]
        F --> G3["convert_hf_to_gguf.py<br/>→ llama.cpp GGUF"]
    end

    subgraph EVALUATION["Phase 5: Evaluation"]
        F --> H["scripts/unified_evaluation.py<br/>base vs FT"]
        H --> I["outputs/benchmarks/"]
    end

    subgraph INFERENCE["Phase 6: Inference"]
        F --> J1["run_inference_v2.py<br/>MLX-LM"]
        F --> J2["Ollama<br/>local deployment"]
        F --> J3["llama.cpp<br/>CLI inference"]
    end

    style GENERATION fill:#e1f5fe
    style PREPARATION fill:#fff3e0
    style TRAINING fill:#e8f5e9
    style EXPORT fill:#f3e5f5
    style EVALUATION fill:#ffebee
    style INFERENCE fill:#e0f2f1
```

**Tech Stack**: Python 3.12, MLX 0.31.1, MLX-LM 0.31.1, MLX-Tune 0.4.18, JSONL chat format.

---

## Features

- **LoRA Fine-tuning**: Low-rank adaptation with 4-bit quantized base model
- **Apple Silicon Optimized**: Runs natively on M1/M2/M3/M4/M5 Macs
- **Comprehensive Evaluation**: Automated scoring with semantic similarity
- **Multiple Export Formats**: Merge to base model, GGUF (Q4/Q5/Q8), or llama.cpp GGUF
- **Local Inference**: Deploy with Ollama or llama.cpp for offline inference
- **Richer Metadata**: Intent, persona, constraint, and lifecycle stage for RAG

---

## Dataset

| Metric | Value |
|--------|-------|
| **Total Generated** | 21,750 examples (87 categories × 250) |
| **After Clean/Dedup** | 19,294 examples |
| **Train** | 14,470 examples (75%) |
| **Valid** | 2,894 examples (15%) |
| **Eval** | 1,930 examples (10%) |
| **Categories** | 87 OCI topics |
| **Metadata** | intent, persona, constraint, lifecycle_stage |

### Split

| Split | Examples | % |
|-------|----------|---|
| Train | 14,470 | 75% |
| Valid | 2,894 | 15% |
| Eval | 1,930 | 10% |

### Categories

- **OCI Core** (compute, storage, networking, lb, database, container, serverless) - 20 topics
- **Security** (iam, policies, vault, encryption, cloud-guard, waf, zero-trust, posture-management) - 10 topics
- **Migration** (AWS/Azure/GCP/On-prem → OCI) - 14 topics
- **Terraform** (provider, compute, storage, networking, etc) - 12 topics
- **Observability** (logging, monitoring, stack-monitoring, apm) - 4 topics
- **Troubleshooting** (connectivity, performance, authentication, database, compute, storage, oke, functions) - 8 topics
- **DevOps** (ci-cd, resource-manager, artifacts, secrets) - 4 topics
- **Governance** (landing-zone, compartments, tagging, budgets-cost, policies-guardrails, compliance, audit-readiness, resource-discovery) - 8 topics
- **FinOps** (cost-optimization, showback-chargeback, rightsizing, storage-tiering) - 4 topics
- **Platform** (backup-governance, sre-operations) - 2 topics

---

## Getting Started

### Prerequisites

- Apple Silicon Mac (M1/M2/M3/M4/M5)
- Python 3.12

```bash
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Quick Start

```bash
# 1. Generate dataset
python scripts/generate_diverse_v2.py

# 2. Validate, clean, deduplicate and build splits
bash scripts/prepare_data.sh

# 3. Train (Cycle 1)
bash training/run_all_cycles.sh --fresh

# 4. Export to GGUF
python scripts/merge_export.py --cycle cycle-1 --quant q4 --name oci-specialist
```

---

## Training

```bash
# Train with single cycle (recommended)
bash training/run_all_cycles.sh --fresh
```

**Configuration**: See `config/cycle-1.env`

| Parameter | Value |
|-----------|-------|
| MODEL | mlx-community/Meta-Llama-3.1-8B-Instruct-4bit |
| LEARNING_RATE | 2e-4 |
| LORA_RANK | 8 |
| LORA_ALPHA | 16 |
| LORA_DROPOUT | 0.05 |
| NUM_LAYERS | 16 |
| GRADIENT_CHECKPOINTING | true |
| GRADIENT_ACCUMULATION | 4 |
| WARMUP_STEPS | 300 |
| ITERS | 3618 |
| MAX_SEQ_LENGTH | 2048 |
| WEIGHT_DECAY | 0.01 |
| LR_SCHEDULER | cosine |

---

## Evaluation

```bash
# Small mode (10 samples de categorias diferentes, ~5 min)
python scripts/unified_evaluation.py --cycle cycle-1 --mode small

# Medium evaluation (200 samples stratified, ~30-40 min) - RECOMMENDED
python scripts/unified_evaluation.py --cycle cycle-1 --mode medium

# Full evaluation (1930 samples, ~4-6 hours)
python scripts/unified_evaluation.py --cycle cycle-1 --mode full

# Add --fresh to clear previous results
python scripts/unified_evaluation.py --cycle cycle-1 --mode medium --fresh
```

Outputs include:
- JSON results with detailed scoring
- Markdown comparison report
- Radar charts (metrics comparison)
- Category bar charts

---

## Inference

> All methods use the fine-tuned model and expose an OpenAI-compatible API or built-in UI on `http://localhost:8080`.

### MLX-LM — API Server (Apple Silicon)

```bash
# Start server with fine-tuned LoRA adapters
mlx_lm.server \
  --model mlx-community/Meta-Llama-3.1-8B-Instruct-4bit \
  --adapter outputs/cycle-1/adapters \
  --port 8080
```

Connect via **Open WebUI** (GUI):

```bash
docker run -d -p 3000:8080 \
  -e OPENAI_API_BASE_URL=http://host.docker.internal:8080/v1 \
  -e OPENAI_API_KEY=ignore \
  ghcr.io/open-webui/open-webui:main
# Open: http://localhost:3000
```

Or via **CLI**:

```bash
curl http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"oci-specialist","messages":[{"role":"user","content":"Liste 3 serviços do OCI"}]}'
```

### Ollama — Local Server + WebUI

```bash
# 1. Create and import model (one-time)
cat > ./outputs/cycle-1/gguf/Modelfile << 'EOF'
FROM ./oci-specialist-Q4_K_M.gguf
PARAMETER temperature 0.1
PARAMETER top_p 0.9
PARAMETER top_k 40
SYSTEM Você é um especialista em OCI (Oracle Cloud Infrastructure).
EOF

ollama create oci-specialist -f ./outputs/cycle-1/gguf/Modelfile

# 2. Connect Open WebUI
docker run -d -p 3000:8080 \
  --add-host=host.docker.internal:host-gateway \
  -e OLLAMA_BASE_URL=http://host.docker.internal:11434 \
  ghcr.io/open-webui/open-webui:main
# Open: http://localhost:3000

# Or interactive CLI
ollama run oci-specialist
```

### llama.cpp — HTTP Server + Built-in WebUI

```bash
# Build llama.cpp
git clone https://github.com/ggerganov/llama.cpp.git
cd llama.cpp
make -j

# Start server with fine-tuned GGUF
./llama-server \
  -m ../outputs/cycle-1/gguf/oci-specialist-Q4_K_M.gguf \
  --host 0.0.0.0 --port 8080 --ctx-size 4096

# WebUI:  http://localhost:8080
# API:    http://localhost:8080/v1
```

> [!NOTE]
> The model is ~4.7GB when exported to GGUF Q4 format.

---

## Project Structure

```
├── config/                  # Configuration files
│   ├── cycle-1.env         # Training config
│   ├── inference_prompts.yaml
│   └── gguf.env
├── data/                    # Datasets
│   ├── curated/            # 87 topic files
│   ├── train.jsonl         # 14,470 examples
│   ├── valid.jsonl         # 2,894 examples
│   └── eval.jsonl          # 1,930 examples
├── docs/                   # Documentation
│   ├── taxonomy.md
│   ├── quality-rules.md
│   └── eval-rubric.md
├── scripts/                # Pipeline scripts
│   ├── generate_diverse_v2.py
│   ├── validate_jsonl.py
│   ├── clean_dataset.py
│   ├── dedupe_embedding.py
│   ├── build_dataset_fixed.py
│   ├── merge_export.py
│   ├── convert_hf_to_gguf.py
│   ├── unified_evaluation.py
│   └── run_inference_v2.py
├── training/               # Training scripts
│   ├── train_mlx_tune.py
│   └── run_all_cycles.sh
├── outputs/                # Generated outputs
│   └── cycle-1/
│       ├── adapters/      # LoRA adapters
│       └── gguf/          # Exported models
└── venv/                   # Python virtual environment
```

---

## Limitations

1. **No RAG**: No real-time access to OCI documentation.

---

## Resources

- [MLX Documentation](https://mlx.ai)
- [MLX-LM GitHub](https://github.com/ml-explore/mlx-lm)
- [llama.cpp](https://github.com/ggerganov/llama.cpp)
- [Oracle Cloud Infrastructure Docs](https://docs.oracle.com/en-us/iaas/Content/home.htm)
- [HuggingFace Model](https://huggingface.co/mlx-community/Meta-Llama-3.1-8B-Instruct-4bit)

---

## License

This project is licensed under the MIT License.
