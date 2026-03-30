<!-- prettier-ignore -->
<div align="center">

# OCI Specialist LLM

Fine-tuning pipeline for an OCI specialist LLM using Apple Silicon, MLX, and LoRA.

[![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python&logoColor=white)](https://www.python.org)
[![MLX](https://img.shields.io/badge/MLX-Apple%20Silicon-orange?style=flat-square)](https://mlx.ai)

</div>

## Overview

This project builds a fine-tuned LLM specialized in Oracle Cloud Infrastructure (OCI). The pipeline prioritizes dataset quality, low cost, rigorous validation, and follows strict quality rules to ensure accurate and helpful responses.

> **Note**: This is a reference implementation for building an OCI specialist model. The current dataset is small (~500 examples) to keep training fast and cheap on Apple Silicon. For production use, you should scale the dataset to 10,000+ examples following the same quality rules and taxonomy structure.

The model is designed to assist with:
- Explaining OCI services, architecture, and best practices
- Troubleshooting OCI workloads
- Guiding migration from AWS, Azure, GCP, and on-premises to OCI
- Writing OCI Terraform configurations
- Providing security and IAM guidance

## Architecture

```
data/raw/        → sources collected (markdown, txt, json)
data/sanitized/  → normalized records
data/curated/    → human-reviewed examples
data/train.jsonl → training set
data/valid.jsonl → validation set
data/eval.jsonl  → evaluation set
```

## Dataset

The curated dataset contains **500+ unique examples** across 8 major categories:

| Category | Description |
|----------|-------------|
| Migration (AWS → OCI) | EC2 → Compute, S3 → Object Storage, RDS → Autonomous DB |
| Migration (Azure → OCI) | Azure VM → Compute, Blob → Object Storage, AKS → OKE |
| Migration (GCP → OCI) | Compute Engine → Compute, Cloud Storage → Object Storage |
| Migration (On-Prem → OCI) | VMware → Oracle Cloud VMware Solution |
| Terraform Provider | Configuration, authentication, multi-region |
| Terraform Resources | VCN, Compute, Block Volume, Object Storage |
| Troubleshooting (Connectivity) | Routing, firewall, DNS, VPN/FastConnect |
| Troubleshooting (Performance) | Shape sizing, storage bottlenecks, network latency |

### Data Format

Each example follows the OpenAI chat format:

```json
{
  "messages": [
    {"role": "system", "content": "You are an OCI specialist..."},
    {"role": "user", "content": "How do I configure..."},
    {"role": "assistant", "content": "## Solution\n\n### Steps..."}
  ],
  "metadata": {
    "category": "oci-core/networking/vcn",
    "difficulty": "intermediate",
    "source": "curated"
  }
}
```

## Quality Rules

We enforce strict quality rules to ensure dataset accuracy:

- **NEVER** copy OCI documentation verbatim
- **NEVER** invent non-existent Oracle services
- **NEVER** use prices or limits without marking as mutable
- **NEVER** create vague examples like "use best practices"
- **NEVER** generate architectural responses without steps, risks, or justifications

## Prerequisites

- **Apple Silicon Mac** (M1/M2/M3/M4) for MLX training
- **Python 3.10+**
- **MLX installed**: `pip install mlx mlx-lm`

## Quick Start

### 1. Validate Dataset

```bash
python scripts/validate_jsonl.py data/curated/
```

### 2. Deduplicate

```bash
python scripts/dedupe_dataset.py data/curated/ data/all_curated_clean.jsonl
```

### 3. Build Dataset Splits

```bash
python scripts/build_dataset.py data/all_curated_clean.jsonl data/
```

### 4. Train Model

```bash
export MODEL="mlx-community/Llama-3.2-3B-Instruct-4bit"
export EPOCHS=3
bash training/train_mlx.sh
```

### 5. Run Inference

```bash
bash training/run_inference.sh
```

### 6. Evaluate

```bash
python scripts/evaluate_model.py outputs/adapters data/eval.jsonl outputs/benchmarks
```

## Evaluation Rubric

The benchmark evaluates responses on:

| Criterion | Weight |
|-----------|--------|
| Technical Correctness | 1-5 |
| Depth of Knowledge | 1-5 |
| Structural Clarity | 1-5 |
| Hallucination | 1-5 |
| Clarity | 1-5 |
| Multi-Cloud Comparison | 1-5 |

**Minimum passing**: 3.5 overall average.

## Project Structure

```
olia-2-oci/
├── AGENTS.md                    # Agent guidelines
├── README.md                    # This file
├── docs/
│   ├── scope.md                # Model scope definition
│   ├── taxonomy.md             # Knowledge categories
│   ├── quality-rules.md        # Dataset quality rules
│   └── eval-rubric.md          # Evaluation criteria
├── data/
│   ├── raw/                    # Raw source materials
│   ├── sanitized/              # Normalized records
│   ├── curated/                # Human-reviewed examples
│   ├── train.jsonl             # Training data
│   ├── valid.jsonl             # Validation data
│   └── eval.jsonl              # Evaluation data
├── scripts/
│   ├── validate_jsonl.py       # Validate JSONL format
│   ├── dedupe_dataset.py       # Remove duplicates
│   ├── build_dataset.py        # Build train/valid/eval splits
│   ├── split_dataset.py        # Split by category
│   └── evaluate_model.py        # Run benchmarks
└── training/
    ├── train_mlx.sh            # MLX LoRA training
    ├── export_adapter.sh       # Export merged model
    └── run_inference.sh        # Test inference
```

## Output Artifacts

After training, the following artifacts are generated:

- `outputs/adapters/` - Trained LoRA adapters
- `outputs/benchmarks/` - Evaluation reports
- `outputs/logs/` - Training logs

## Pipeline Stages

1. **Documentation** → Scope, taxonomy, quality rules, eval rubric
2. **Data Collection** → Raw → Sanitized → Curated
3. **Validation** → JSONL validator, deduplication
4. **Dataset Building** → Build, split, export
5. **Training** → MLX LoRA fine-tuning
6. **Evaluation** → Benchmark base vs fine-tuned

## License

This project is for educational and research purposes.
