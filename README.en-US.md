<!-- prettier-ignore -->
<div align="center">

# OCI Specialist LLM

Fine-tuning pipeline for an OCI specialist LLM using Apple Silicon, MLX, and LoRA.

[![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.12-blue?style=flat-square&logo=python&logoColor=white)](https://www.python.org)
[![MLX](https://img.shields.io/badge/MLX-Apple%20Silicon-orange?style=flat-square)](https://mlx.ai)
[![Dataset](https://img.shields.io/badge/Dataset-710_examples-green?style=flat-square)](docs/taxonomy.md)

</div>

> **Language**: [🇧🇷 PT-BR](README.md) | 🇺🇸 EN-US (secundário)

---

## Overview

This project builds an LLM specialized in Oracle Cloud Infrastructure (OCI). The pipeline prioritizes dataset quality, low cost, rigorous validation, and follows strict quality rules to ensure accurate and helpful responses.

The model is designed to assist with:
- Explaining OCI services, architecture, and best practices
- Troubleshooting OCI workloads
- Guiding migration from AWS, Azure, GCP, and on-premises to OCI
- Writing OCI Terraform configurations
- Providing security and IAM guidance

---

## Dataset

The dataset contains examples generated via MASTER_PROMPT. See `docs/taxonomy.md` for all topics.

| Category | Topics |
|----------|--------|
| OCI Core (compute, storage, networking, lb, database, container, serverless) | 20 |
| Security (iam-basics, policies, vault, encryption, cloud-guard, waf) | 9 |
| Migration (AWS/Azure/GCP/On-prem → OCI) | 14 |
| Terraform (provider, compute, storage, networking, lb, database, container, serverless, security, observability, devops, state) | 12 |
| Observability | 4 |
| Troubleshooting | 8 |
| DevOps | 4 |

> **Total: 71 topics × 10 examples = 710 examples**

### Data Format

Each example follows the OpenAI chat format:

```json
{
  "messages": [
    {"role": "system", "content": "You are an OCI specialist..."},
    {"role": "user", "content": "How do I configure..."},
    {"role": "assistant", "content": "## Solution\n\n### Steps..."}
  ],
  "metadata": {"category": "compute/instances", "difficulty": "intermediate", "source": "generated"}
}
```

---

## Quality Rules

We enforce strict quality rules to ensure dataset accuracy:

- **NEVER** copy OCI documentation verbatim
- **NEVER** invent non-existent Oracle services
- **NEVER** use prices or limits without marking as mutable
- **NEVER** create vague examples like "use best practices"
- **NEVER** generate architectural responses without steps, risks, or justifications

---

## Prerequisites

- **Apple Silicon Mac** (M1/M2/M3/M4) for MLX training
- **Python 3.12** (recommended via venv)

### Setup Virtual Environment

```bash
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## Quick Start

### Generate Curated Data

Use **MASTER_PROMPT** with any external LLM (Gemini, Claude, GPT):

```bash
# List available topics
python scripts/generate_prompt.py --list

# Generate prompt for a specific topic
python scripts/generate_prompt.py compute/instances

# Generate ALL prompts at once
python scripts/generate_prompt.py --all
```

The generated prompt should be sent to an LLM, and the result saved to `data/curated/[topic].jsonl`.

### Complete Pipeline

```bash
# 0. Activate virtual environment
source venv/bin/activate

# ========== 1. DATA PREPARATION ==========

# 1.1 Generate ALL prompts
python scripts/generate_prompt.py --all

# 1.2 In your LLM of choice, execute the prompt and save to data/curated/
 For each file in tmp/prompt_*.md:
   1. Execute tmp/prompt_*.md
   2. Save result to data/curated/[topic].jsonl
 Format: 1 file per topic (71 topics = 71 files), 10 examples per file

# 1.3 Concatenate all JSONL
cat data/curated/*.jsonl > data/all_curated.jsonl

# 1.4 Validate dataset
python3 scripts/validate_jsonl.py data/all_curated.jsonl --filter
mv data/all_curated_valid.jsonl data/all_curated.jsonl

# 1.5 Deduplicate
python3 scripts/dedupe_dataset.py data/all_curated.jsonl --remove

# 1.6 Create splits (train/valid/eval)
python3 scripts/build_dataset_fixed.py -i data/all_curated.jsonl -o data/

# ========== 2. TRAINING ==========

# ⚠️ NOTE: Validate variables in config/cycle-1.env before running
# 2.1 Load cycle configuration
source config/cycle-1.env

# 2.2 Fine-Tune LoRA
bash training/train_mlx.sh

# ========== 3. POST-TRAINING ==========

# 3.1 Export/Merge adapter
bash training/export_adapter.sh

# 3.2 Test inference
bash training/run_inference.sh

# 3.3 Evaluate
python scripts/evaluate_model.py outputs/adapters data/eval.jsonl outputs/benchmarks
```

### Cycle Configuration (`config/cycle-1.env`)

| Variable | Description | Default |
|----------|-------------|---------|
| `MODEL` | MLX base model (HuggingFace) | `mlx-community/Llama-3.2-3B-Instruct-4bit` |
| `TRAIN_DATA | Training data file | `data/train.jsonl` |
| `VALID_DATA` | Validation data file | `data/valid.jsonl` |
| `OUTPUT_DIR` | Folder to save LoRA adapters | `outputs/cycle-1` |
| `EPOCHS` | Number of training epochs | `2` |
| `BATCH_SIZE` | Batch size | `4` |
| `LEARNING_RATE` | Learning rate | `5e-5` |
| `LORA_RANK` | LoRA matrix rank (higher = more parameters) | `16` |
| `LORA_ALPHA` | LoRA scale (usually 2x rank) | `32` |
| `LORA_DROPOUT` | Dropout rate for regularization | `0.05` |
| `GRADIENT_ACCUMULATION` | Gradient steps before update | `2` |

> 💡 **Tip**: To create a new training cycle, copy `config/cycle-1.env` to `config/cycle-2.env` and adjust values.

> ⚠️ **Note**: This is a **local** training pipeline (LoRA with small dataset ~710 examples). For **production**, just increase the dataset to ~10k+ examples and follow the same steps - the rest of the pipeline remains identical.

### Pipeline Flow

```mermaid
flowchart LR
    subgraph DataPrep["1. Data Preparation"]
        DP1[Generate Prompts] --> DP2{Send to LLM}
        DP2 -->|Manual| DP3[Gemini/Claude/GPT]
        DP3 --> DP4[Save JSONL]
        DP4 --> DP5[Validate]
        DP5 --> DP6[Deduplicate]
        DP6 --> DP7[Create Splits]
        DP7 --> Train[train.jsonl]
        DP7 --> Valid[valid.jsonl]
        DP7 --> Eval[eval.jsonl]
    end
    
    subgraph Training["2. Training"]
        Train --> T1[Select Base Model]
        Valid --> T1
        T1 --> T2[Fine-Tune LoRA]
    end
    
    subgraph PostProcess["3. Post-Training"]
        T2 --> P1[Export/Merge Adapter]
        P1 --> P2[Test Inference]
        P2 --> P3[Evaluate with eval.jsonl]
    end
    
    P1 --> outputs/adapters
    P3 --> outputs/benchmarks
    
    style DP2 fill:#e1f5fe,stroke:#01579b
    style DP3 fill:#fff3e0,stroke:#e65100
    style DP4 fill:#fff3e0,stroke:#e65100
    style Train fill:#e8f5e9,stroke:#2e7d32
    style Valid fill:#e8f5e9,stroke:#2e7d32
    style Eval fill:#e8f5e9,stroke:#2e7d32
```

---
    
    I -.->|75%| L[train]
    I -.->|15%| M[valid]
    I -.->|10%| N[eval]
    
    style C fill:#e1f5fe,stroke:#01579b
    style D fill:#fff3e0,stroke:#e65100
    style E fill:#fff3e0,stroke:#e65100
```

---

## Project Structure

```
olia-2-oci/
├── AGENTS.md                      # Agent guidelines
├── README.md                      # Portuguese version (default)
├── README.en-US.md                # English version
├── CONTRIBUTING.md                # Contributing guide
├── docs/                          # Project documentation
│   ├── taxonomy.md               # Dataset topics
│   ├── quality-rules.md          # Quality rules
│   └── eval-rubric.md            # Evaluation criteria
├── scripts/                      # Pipeline scripts
│   ├── generate_prompt.py       # Generate prompts for LLM
│   ├── validate_jsonl.py         # Validate JSONL format
│   ├── dedupe_dataset.py         # Remove duplicates
│   ├── build_dataset_fixed.py    # Create train/valid/eval splits
│   └── evaluate_model.py         # Run benchmarks
├── .agents/skills/               # Data generation skills
│   └── generate-oci-dataset/
│       ├── MASTER_FORMAT.md
│       └── prompts/              # Prompts per topic
└── training/                     # MLX training scripts
    ├── train_mlx.sh
    └── run_inference.sh
```

---

## Pipeline

1. **Documentation** → Scope, taxonomy, quality rules
2. **Data Generation** → MASTER_PROMPT + external LLM → curated/
3. **Validation** → JSONL validator, deduplication
4. **Dataset Building** → train (~75%), valid (~15%), eval (~10%)
5. **Training** → MLX LoRA fine-tuning on Apple Silicon
6. **Evaluation** → Benchmark comparing base vs fine-tuned

---

## Outputs

After training:

- `outputs/adapters/` - Trained LoRA adapters
- `outputs/benchmarks/` - Evaluation reports
- `outputs/logs/` - Training logs
