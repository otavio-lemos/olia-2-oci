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
2. **Data Generation** → generate examples using prompts
3. **Data Collection** → raw → sanitized → curated
4. **Validation** → JSONL validator, deduplication
5. **Dataset Building** → build, split, export
6. **Training** → MLX LoRA fine-tuning
7. **Evaluation** → benchmark base vs fine-tuned

## Data Generation

### Process

1. Select category from `docs/taxonomy.md`
2. Use prompt template from `tmp/prompt_*.md`
3. Execute the prompt as specified in the file
4. Validate response against quality rules
5. Save to `data/curated/[topic]-[nnn].jsonl`

### Execution

Execute prompts exactly as requested in each `tmp/prompt_*.md` file:
- Generate 10 files per topic (001-010)
- 1 example per file in JSONL format
- Follow the output format specified in the prompt file

## Data Flow

```
data/curated/        → Generated examples (one file per example)
                      format: [category]-[nnn].jsonl
data/all_curated.jsonl → concatenated examples
data/all_curated_clean.jsonl → validated and deduplicated
data/train.jsonl     → training set (~75%)
data/valid.jsonl     → validation set (~15%)
data/eval.jsonl      → evaluation set (~10%)
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
    {"role": "system", "content": "Você é um arquiteto especialista em OCI..."},
    {"role": "user", "content": "Como criar instância no OCI?"},
    {"role": "assistant", "content": "Para criar uma instância..."}
  ],
  "metadata": {
    "category": "oci-core/compute",
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

- `data/curated/` - individual generated examples
- `outputs/adapters/` - trained LoRA adapters
- `outputs/benchmarks/` - evaluation reports
- `outputs/logs/` - training logs

## Provider Strategy

- **OpenCode Zen**: Critical project engineering and review
- **Prompt execution**: Prompts are executed as specified in each tmp/prompt_*.md file

## Checkpoints

1. Taxonomy and categories approval
2. Quality rules approval
3. Generation prompts review
4. First 50 examples review
5. Validation scripts review
6. Deduplication review
7. Benchmark review
8. Short training run
9. Base vs fine-tuned comparison
