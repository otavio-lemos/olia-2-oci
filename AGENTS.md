# OCI Specialist LLM - Agent Guidelines

## Project Overview

This project builds a fine-tuned LLM specialist in Oracle Cloud Infrastructure (OCI) using Apple Silicon, MLX, and LoRA. The pipeline prioritizes dataset quality, low cost, rigorous validation, and a future RAG layer.

## Tech Stack

- **Hardware**: Apple Silicon M3 Pro (18GB unified memory)
- **Framework**: MLX-Tune 0.4.18 (wrapper sobre MLX-LM 0.31.1)
- **MLX Core**: 0.31.1
- **Method**: LoRA (Low-Rank Adaptation) with 4-bit quantized base model
- **Format**: JSONL chat format
- **Python**: 3.12 (venv: `venv/`)

### Dependencies (venv)
```
mlx==0.31.1
mlx-lm==0.31.1
mlx-tune==0.4.18
transformers==5.4.0
sentence-transformers==5.3.0
scikit-learn==1.8.0
```

## Pipeline Stages

1. **Documentation** → scope, taxonomy, quality rules, eval rubric
2. **Data Generation** → generate examples using prompts
3. **Data Collection** → raw → sanitized → curated
4. **Validation** → JSONL validator, deduplication
5. **Dataset Building** → build, split, export
6. **Training** → MLX-Tune LoRA fine-tuning (3 cycles progressive)
7. **Evaluation** → benchmark base vs fine-tuned

## Training Architecture

### MLX-Tune Training Script
- **Main script**: `training/train_mlx_tune.py`
- **Config**: `config/cycle-N.env` (via `CYCLE` env var)
- **API**: mlx-tune SFTTrainer (Unsloth-compatible)
- **Suporte nativo**:
  - Warmup steps
  - Weight decay
  - Gradient clipping (max_grad_norm)
  - LR schedulers (cosine, linear, etc)

### Como rodar treinamento
```bash
# Cycle 1 (do zero)
CYCLE=cycle-1 python training/train_mlx_tune.py --fresh

# Cycle 2 (resume do cycle 1)
CYCLE=cycle-2 python training/train_mlx_tune.py

# Cycle 3 (resume do cycle 2)
CYCLE=cycle-3 python training/train_mlx_tune.py
```

### Configuração por Ciclo

| Param | Cycle-1 | Cycle-2 | Cycle-3 |
|-------|---------|---------|---------|
| Base | scratch | resume c1 | resume c2 |
| LR | 2e-5 | 1e-5 | 5e-6 |
| Rank | 8 | 8 | 8 |
| Alpha | 16 | 16 | 16 |
| Dropout | 0.0 | 0.0 | 0.0 |
| Batch | 1 | 1 | 1 |
| Grad Accum | 2 | 2 | 2 |
| Layers | 8 | 8 | 8 |
| Iters | 250 | 125 | 75 |
| Max Seq | 2048 | 2048 | 2048 |
| Warmup | 25 (10%) | 12 (10%) | 8 (10%) |
| Weight Decay | 0.01 | 0.01 | 0.01 |
| Grad Clip | 1.0 | 0.5 | 0.5 |
| Clear Cache | 5GB | 5GB | 5GB |
| Logging | 5 | 5 | 5 |

### Performance Esperada (M3 Pro 18GB)
- **Peak memory**: ~6.5 GB
- **Velocidade**: ~85 tokens/sec, ~0.18 iters/sec
- **Cycle 1 (200 iters)**: ~21 minutos
- **Loss**: Val ~2.4 → ~0.24, Train ~2.2 → ~0.37

## Data Flow

```
data/curated/        → Generated examples (one file per topic, 140 examples each)
                      format: [topic].jsonl
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
- `outputs/cycle-N/` - trained LoRA adapters per cycle
- `outputs/benchmarks/` - evaluation reports
- `outputs/logs/` - training logs and metrics CSV

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
