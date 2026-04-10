# OCI Specialist LLM

Fine-tuned Large Language Model for Oracle Cloud Infrastructure (OCI) using Apple Silicon, MLX, and LoRA.

[![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.12-blue?style=flat-square&logo=python&logoColor=white)](https://www.python.org)
[![MLX](https://img.shields.io/badge/MLX-Apple%20Silicon-orange?style=flat-square)](https://mlx.ai)
[![Model](https://img.shields.io/badge/Base%20Model-Meta--Llama--3.1--8B--Instruct--4bit-purple?style=flat-square)](https://huggingface.co/mlx-community/Meta-Llama-3.1-8B-Instruct-4bit)
[![Dataset](https://img.shields.io/badge/Dataset-6627_examples-green?style=flat-square)](docs/taxonomy.md)

> **Language**: Data and prompts in Brazilian Portuguese (PT-BR).

---

## Overview

This project trains a specialized LLM for Oracle Cloud Infrastructure using Apple's MLX framework on Apple Silicon. The pipeline covers dataset generation, validation, MLX LoRA fine-tuning, and evaluation.

```mermaid
flowchart TB
    subgraph GENERATION["Phase 1: Generation"]
        A["generate_diverse_v2.py"]
        A --> B["data/curated/<br/>71 JSONL files"]
    end

    subgraph PREPARATION["Phase 2: Preparation"]
        B --> C1["Concat<br/>all_curated.jsonl"]
        C1 --> C2["Validate<br/>validate_jsonl.py"]
        C2 --> C3["Clean<br/>clean_dataset.py"]
        C3 --> C4["Dedup<br/>dedupe_dataset.py"]
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
    end

    subgraph EVALUATION["Phase 5: Evaluation"]
        F --> H["scripts/unified_evaluation.py<br/>base vs FT"]
        H --> I["outputs/benchmarks/"]
    end

    subgraph INFERENCE["Phase 6: Inference"]
        F --> J1["run_inference_v2.py<br/>YAML structured"]
        F --> J2["Ollama<br/>local deployment"]
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
- **Multiple Export Formats**: Merge to base model or export to GGUF (Q4/Q5/Q8)
- **Local Inference**: Deploy with Ollama for offline inference

---

## Dataset

| Metric | Value |
|--------|-------|
| **Total** | 6,627 examples |
| **Categories** | 71 OCI topics |
| **Removed in cleaning** | 3,313 (generic templates, duplicates) |

### Split

| Split | Examples | % |
|-------|----------|---|
| Train | 4,956 | 74.8% |
| Valid | 978 | 14.7% |
| Eval | 632 | 9.5% |

### Categories

- **OCI Core** (compute, storage, networking, lb, database, container, serverless) - 20 topics
- **Security** (iam, policies, vault, encryption, cloud-guard, waf) - 9 topics
- **Migration** (AWS/Azure/GCP/On-prem → OCI) - 14 topics
- **Terraform** (provider, compute, storage, networking, etc) - 12 topics
- **Observability** - 4 topics
- **Troubleshooting** - 8 topics
- **DevOps** - 4 topics

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

# 2. Validate and prepare
bash scripts/prepare_data.sh

# 3. Build dataset splits
python scripts/build_dataset_fixed.py --input data/all_curated_clean.jsonl

# 4. Train (Cycle 1)
CYCLE=cycle-1 python training/train_mlx_tune.py --fresh

# 5. Export to GGUF
python scripts/merge_export.py --cycle cycle-1 --quant q4 --name oci-specialist
```

---

## Training

```bash
# Full training with all cycles
bash training/run_all_cycles.sh --fresh

# Single cycle
CYCLE=cycle-1 python training/train_mlx_tune.py --fresh
```

**Configuration**: See `config/cycle-1.env`

| Parameter | Value |
|-----------|-------|
| MODEL | mlx-community/Meta-Llama-3.1-8B-Instruct-4bit |
| LEARNING_RATE | 2e-4 |
| LORA_RANK | 8 |
| LORA_ALPHA | 16 |
| ITERS | 1250 |
| MAX_SEQ_LENGTH | 2048 |

---

## Evaluation

```bash
# Test mode (10 samples, ~2 min)
python scripts/unified_evaluation.py --mode test

# Full evaluation (325 samples, ~90 min)
python scripts/unified_evaluation.py --mode full
```

Outputs include:
- JSON results with detailed scoring
- Markdown comparison report
- Radar charts (metrics comparison)
- Category bar charts

---

## Inference

### MLX-LM (Online)

```bash
# Base model (no LoRA)
python scripts/run_inference_v2.py --config config/inference_prompts.yaml \
  --model mlx-community/Meta-Llama-3.1-8B-Instruct-4bit

# Fine-tuned model
python scripts/run_inference_v2.py --config config/inference_prompts.yaml \
  --adapter outputs/cycle-1/adapters
```

### Ollama (Offline)

```bash
# Create Modelfile
cat > ./outputs/cycle-1/gguf/Modelfile << 'EOF'
FROM ./oci-specialist-Q4_K_M.gguf
PARAMETER temperature 0.1
PARAMETER top_p 0.9
PARAMETER top_k 40
SYSTEM Você é um especialista em OCI (Oracle Cloud Infrastructure).
EOF

# Import to Ollama
ollama create oci-specialist -f ./outputs/cycle-1/gguf/Modelfile

# Test
echo "Liste 3 serviços do OCI" | ollama run oci-specialist
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
│   ├── curated/            # 71 topic files
│   ├── train.jsonl         # 2,583 examples
│   ├── valid.jsonl         # 495 examples
│   └── eval.jsonl          # 325 examples
├── docs/                   # Documentation
│   ├── taxonomy.md
│   ├── quality-rules.md
│   └── eval-rubric.md
├── scripts/                # Pipeline scripts
│   ├── generate_diverse_v2.py
│   ├── validate_jsonl.py
│   ├── clean_dataset.py
│   ├── build_dataset_fixed.py
│   ├── merge_export.py
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

1. **Single-turn only**: Dataset doesn't include multi-turn conversations.
2. **No RAG**: No real-time access to OCI documentation.

---

## Resources

- [MLX Documentation](https://mlx.ai)
- [MLX-LM GitHub](https://github.com/ml-explore/mlx-lm)
- [Oracle Cloud Infrastructure Docs](https://docs.oracle.com/en-us/iaas/Content/home.htm)
- [HuggingFace Model](https://huggingface.co/mlx-community/Meta-Llama-3.1-8B-Instruct-4bit)

---

## License

This project is licensed under the MIT License.
