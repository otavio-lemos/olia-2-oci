# OCI Specialist LLM - Agent Guidelines

## Project Overview

This project builds a fine-tuned LLM specialist in Oracle Cloud Infrastructure (OCI) using Apple Silicon, MLX, and LoRA. The pipeline prioritizes dataset quality, low cost, rigorous validation, and a future RAG layer.

## Tech Stack

- **Hardware**: Apple Silicon (M1/M2/M3/M4)
- **Framework**: MLX for fine-tuning
- **Method**: LoRA (Low-Rank Adaptation)
- **Format**: JSONL chat format

## Pipeline Stages

1. **Documentation** → scope, taxonomy, quality rules, eval rubric
2. **Data Collection** → raw → sanitized → curated
3. **Validation** → JSONL validator, deduplication
4. **Dataset Building** → build, split, export
5. **Training** → MLX LoRA fine-tuning
6. **Evaluation** → benchmark base vs fine-tuned

## Data Flow

```
data/raw/        → sources collected (markdown, txt, json)
data/sanitized/  → normalized records
data/curated/    → human-reviewed examples
data/train.jsonl → training set
data/valid.jsonl → validation set
data/eval.jsonl  → evaluation set
```

## Quality Rules (Rigid)

- **NEVER** copy OCI documentation verbatim
- **NEVER** invent non-existent Oracle services
- **NEVER** use prices or limits without marking as mutable content
- **NEVER** create vague examples like "use best practices"
- **NEVER** generate architectural responses without steps, risks, or justifications
- **NEVER** mix training and evaluation data
- **ALWAYS** validate JSONL before export
- **ALWAYS** generate quality reports
- **ALWAYS** review examples by category before consolidating

## JSONL Format

```json
{
  "messages": [
    {"role": "system", "content": "You are an OCI specialist..."},
    {"role": "user", "content": "How do I..."},
    {"role": "assistant", "content": "To do this..."}
  ],
  "metadata": {
    "category": "oci-core/networking/vcn",
    "difficulty": "intermediate",
    "source": "generated"
  }
}
```

## Prohibited Content

- Literal documentation copies
- Made-up OCI services or features
- Unmarked mutable content (prices, limits, quotas)
- Generic advice without specific steps
- Responses without justification in architectural scenarios

## Output Artifacts

- `outputs/adapters/` - trained LoRA adapters
- `outputs/benchmarks/` - evaluation reports
- `outputs/logs/` - training logs

## Provider Strategy

- **OpenCode Zen**: Critical project engineering and review
- **OpenRouter**: Volume generation and brainstorming
- **Kilo Gateway**: Testing with other models

## Checkpoints

1. Scope and taxonomy approval
2. Quality rules approval
3. Validation scripts review
4. First 50 examples review
5. Benchmark review
6. Short training run
7. Base vs fine-tuned comparison
