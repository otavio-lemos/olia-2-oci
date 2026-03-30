<!-- prettier-ignore -->
<div align="center">

# OCI Specialist LLM

Fine-tuning pipeline for an OCI specialist LLM using Apple Silicon, MLX, and LoRA.

[![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.12-blue?style=flat-square&logo=python&logoColor=white)](https://www.python.org)
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
data/curated/      → human-reviewed examples (generated via MASTER_PROMPT)
data/TEMPLATE.jsonl → correct format example
```

## Dataset

Dataset contains examples generated via MASTER_PROMPT. See `docs/taxonomy.md` for all categories (43 categories available).

| Category | Examples Suggested |
|-----------|-------------------|
| oci-core/compute | 30 |
| oci-core/storage | 25 |
| oci-core/networking | 25 |
| oci-security/iam | 30 |
| oci-migration/* | ~160 |
| oci-terraform/* | ~70 |
| oci-troubleshooting/* | ~135 |

**Total recommended: 660-710 examples**

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
- **Python 3.12** (recommended via venv)

### Setup Virtual Environment

```bash
# Create venv with Python 3.12
python3.12 -m venv venv

# Activate
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Quick Start

### 0. Generate Curated Data

Use the **MASTER_PROMPT** with any external LLM (Gemini, GPT-4, Claude, Perplexity):

```
.agents/skills/generate-oci-dataset/MASTER_PROMPT.md
├── @docs/taxonomy.md                          ← choose category
├── @docs/quality-rules.md                     ← quality rules
└── .agents/skills/generate-oci-dataset/prompts/
    └── [category].md                         ← category-specific topics
```

> **Note**: The `@` references above are for you (the human) to know which files to include.
> When sending to the LLM, you must manually combine:
> - `.agents/skills/generate-oci-dataset/MASTER_PROMPT.md` (format instructions)
> - Relevant sections from `docs/taxonomy.md` (category and topics)
> - `docs/quality-rules.md` (quality rules)
> - The specific category prompt from `.agents/skills/generate-oci-dataset/prompts/[category].md`
>
> **Tip**: Generate one category at a time to stay within token limits.

#### Step by Step

1. **Choose a category** - see `docs/taxonomy.md`

2. **Read the category prompt**:
   ```bash
   cat .agents/skills/generate-oci-dataset/prompts/oci-core/compute.md
   ```

3. **Combine the prompt**:
   - `.agents/skills/generate-oci-dataset/MASTER_PROMPT.md` (format instructions)
   - Category from `docs/taxonomy.md`
   - Topics from category prompt
   - Rules from `docs/quality-rules.md`

4. **Send to an LLM** (Gemini, GPT-4, Claude)

5. **Save result** to `data/curated/[category]-[nnn].jsonl`

#### Usage Example

```bash
# 1. List available categories
cat docs/taxonomy.md | grep "^#### "

# 2. Read category prompt
cat .agents/skills/generate-oci-dataset/prompts/oci-core/compute.md

# 3. Read MASTER_PROMPT
cat .agents/skills/generate-oci-dataset/MASTER_PROMPT.md
```

4. Combine: MASTER_PROMPT + category + category prompt
5. Send to Gemini/GPT-4
6. Save to: `data/curated/oci-core/compute-001.jsonl`

#### File Structure

```
data/
├── curated/                    # Generated examples (one file = one example)
│   └── oci-core/compute-001.jsonl
└── TEMPLATE.jsonl             # Correct format example
```

#### Template (expected format)

```json
{"messages": [{"role": "system", "content": "You are an OCI specialist..."}, {"role": "user", "content": "Your question here"}, {"role": "assistant", "content": "Answer with steps, risks, alternatives, [MUTABLE] for prices, [CHECK DOCS] for limits"}], "metadata": {"category": "oci-core/compute", "difficulty": "beginner|intermediate|advanced", "source": "generated"}}
```

#### Available Categories (43 categories)

- **oci-core/** (8): compute, storage, networking, load-balancing, database, container, serverless, ai-ml
- **oci-security/** (5): iam, vault, encryption, cloud-guard, waf
- **oci-migration/** (9): aws-to-oci, azure-to-oci, gcp-to-oci, onprem-to-oci, database-migration, data-migration, storage-migration, oracle-to-oci, applications
- **oci-terraform/** (5): provider, resources, modules, best-practices, oke
- **oci-observability/** (4): logging, monitoring, stack-monitoring, apm
- **oci-troubleshooting/** (8): connectivity, performance, authentication, database, compute, storage, oke, functions-api-gateway
- **oci-devops/** (4): ci-cd, resource-manager, artifacts-registry, secrets

---

### 1. Activate Virtual Environment

```bash
source venv/bin/activate
```

### 2. Concatenate all curated files

```bash
# Creates a single file with all examples from curated/
cat data/curated/*.jsonl > data/all_curated.jsonl
```

### 3. Validate Dataset

```bash
python3 scripts/validate_jsonl.py data/all_curated.jsonl --filter
mv data/all_curated_valid.jsonl data/all_curated.jsonl
```

### 4. Deduplicate

```bash
python3 scripts/dedupe_dataset.py data/curated/ --remove
mv data/curated_deduped data/all_curated_clean.jsonl
```

### 5. Build Dataset Splits

The script reads `data/all_curated_clean.jsonl` and generates:

- `data/train.jsonl` (~75%)
- `data/valid.jsonl` (~15%)
- `data/eval.jsonl` (~10%)

```bash
python3 scripts/build_dataset_fixed.py -i data/all_curated_clean.jsonl -o data/
```

### 6. Train Model

```bash
source config/cycle-1.env && bash training/train_mlx.sh
```

Or with custom parameters:
```bash
MODEL="mlx-community/Llama-3.2-3B-Instruct-4bit" EPOCHS=2 bash training/train_mlx.sh
```

> **Note:** The training script sets `KMP_DUPLICATE_LIB_OK=TRUE` to handle OpenMP conflicts on macOS.

### 7. Run Inference

```bash
bash training/run_inference.sh
```

### 8. Evaluate

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
├── requirements.txt             # Python dependencies
├── docs/
│   ├── scope.md                # Model scope definition
│   ├── taxonomy.md             # Knowledge categories
│   ├── quality-rules.md        # Dataset quality rules
│   └── eval-rubric.md          # Evaluation criteria
├── data/
│   ├── curated/                # Human-reviewed examples (generated via MASTER_PROMPT)
│   └── TEMPLATE.jsonl          # Correct format example
├── scripts/
│   ├── validate_jsonl.py       # Validate JSONL format
│   ├── dedupe_dataset.py       # Remove duplicates
│   ├── build_dataset.py        # Build train/valid/eval splits
│   ├── split_dataset.py        # Split by category
│   └── evaluate_model.py        # Run benchmarks
├── .agents/skills/
│   └── generate-oci-dataset/   # Generation prompts
│       ├── MASTER_PROMPT.md
│       └── prompts/            # Prompts por categoria
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
2. **Data Generation** → Use MASTER_PROMPT com LLM externo → curated/[categoria].jsonl
3. **Validation** → JSONL validator, deduplication
4. **Dataset Building** → Build train/valid/eval splits
5. **Training** → MLX LoRA fine-tuning
6. **Evaluation** → Benchmark base vs fine-tuned

## License

This project is for educational and research purposes.
