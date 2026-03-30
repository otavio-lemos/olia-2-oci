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
2. **Data Generation** → generate examples using online LLMs
3. **Data Collection** → raw → sanitized → curated
4. **Validation** → JSONL validator, deduplication
5. **Dataset Building** → build, split, export
6. **Training** → MLX LoRA fine-tuning
7. **Evaluation** → benchmark base vs fine-tuned

## Data Generation

### Process

1. Select category from `docs/taxonomy.md`
2. Use prompt template from `.agents/skills/generate-oci-dataset/prompts/`
3. Send to online LLM (Gemini, GPT-4, Claude)
4. Validate response against `docs/quality-rules.md`
5. Save to `data/curated/[category]-[nnn].jsonl`

### Providers for Generation

Recommended online LLMs:
- **Google Gemini 2.0 Flash** - fast, good quality
- **OpenAI GPT-4o** - excellent reasoning
- **Anthropic Claude 3.5** - clear explanations
- **Perplexity Sonar** - up-to-date knowledge

## Data Flow

```
data/curated/        → LLM-generated examples (one file per example)
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
- **Google Gemini**: Volume generation (fast, cost-effective)
- **OpenAI GPT-4o**: Quality generation (complex topics)
- **OpenRouter**: Testing with other models

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
