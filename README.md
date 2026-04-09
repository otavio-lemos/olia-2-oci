# OCI Specialist LLM

Fine-tuning de LLM especialista em Oracle Cloud Infrastructure (OCI) usando Apple Silicon, MLX e LoRA.

[![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.12-blue?style=flat-square&logo=python&logoColor=white)](https://www.python.org)
[![MLX](https://img.shields.io/badge/MLX-Apple%20Silicon-orange?style=flat-square)](https://mlx.ai)
[![Model](https://img.shields.io/badge/Base%20Model-Meta--Llama--3.1--8B--Instruct--4bit-purple?style=flat-square)](https://huggingface.co/mlx-community/Meta-Llama-3.1-8B-Instruct-4bit)
[![Dataset](https://img.shields.io/badge/Dataset-3467_examples-green?style=flat-square)](docs/taxonomy.md)

> **Idioma**: Dados e prompts em PT-BR.

---

## Visão Geral

Pipeline completo: geração dataset → validação → treino MLX LoRA → avaliação.

```
generate_diverse_v2.py → data/curated/ (71 topics) → build_dataset_fixed.py → train/valid/eval.jsonl
                                                                                          ↓
CYCLE=cycle-1 python training/train_mlx_tune.py → outputs/cycle-1/adapters/
                                                                                          ↓
evaluate_model.py → outputs/benchmarks/
```

**Stack:** Python 3.12, MLX 0.31.1, MLX-LM 0.31.1, MLX-Tune 0.4.18, JSONL chat format.

---

## Dataset

| Métrica | Valor |
|---------|-------|
| **Total** | 3,467 exemplos |
| **Categorias** | 71 topics OCI |
| **Removidos na limpeza** | 6,473 (templates genéricos, duplicatas) |

### Split

| Split | Exemplos | % |
|-------|----------|---|
| Train | 2,583 | 74.5% |
| Valid | 495 | 14.3% |
| Eval | 325 | 9.4% |

### Categorias

- OCI Core (compute, storage, networking, lb, database, container, serverless) - 20 topics
- Security (iam, policies, vault, encryption, cloud-guard, waf) - 9 topics
- Migration (AWS/Azure/GCP/On-prem → OCI) - 14 topics
- Terraform (provider, compute, storage, networking, etc) - 12 topics
- Observability - 4 topics
- Troubleshooting - 8 topics
- DevOps - 4 topics

---

## Pipeline

### 1. Geração

```bash
python scripts/generate_diverse_v2.py
```

Saída: `data/curated/*.jsonl` (71 arquivos) + `data/all_curated.jsonl`

### 2. Validação e Limpeza

```bash
# Pipeline completo
bash scripts/prepare_data.sh

# Ou manual
python3 scripts/validate_jsonl.py data/all_curated.jsonl
python3 scripts/clean_dataset.py --input data/all_curated.jsonl --output data/all_curated_clean.jsonl --all
python3 scripts/dedupe_dataset.py data/all_curated_clean.jsonl --remove
```

### 3. Construção Dataset

```bash
python scripts/build_dataset_fixed.py --input data/all_curated_clean.jsonl
```

### 4. Treinamento

```bash
# Treino único
CYCLE=cycle-1 python training/train_mlx_tune.py

# Com clean
CYCLE=cycle-1 python training/train_mlx_tune.py --fresh
```

**Config:** `config/cycle-1.env`

| Parâmetro | Valor |
|-----------|-------|
| MODEL | mlx-community/Meta-Llama-3.1-8B-Instruct-4bit |
| LEARNING_RATE | 2e-4 |
| LORA_RANK | 8 |
| LORA_ALPHA | 16 |
| LORA_DROPOUT | 0.05 |
| ITERS | 2583 |
| BATCH_SIZE | 1 |
| GRADIENT_ACCUMULATION | 2 |
| MAX_SEQ_LENGTH | 2048 |
| NUM_LAYERS | 8 |
| WARMUP_STEPS | 200 |

### 5. Export

#### MLX Merge

```bash
python -m mlx_lm fuse --model "mlx-community/Meta-Llama-3.1-8B-Instruct-4bit" --adapter-path outputs/cycle-1/adapters --save-path outputs/merged-model
```

#### GGUF (Ollama/llama.cpp)

```bash
python scripts/export_gguf.py --cycle cycle-1 --quant q4 --ollama
python scripts/export_gguf.py --cycle cycle-1 --quant q4,q5,q8 --ollama
```

### 6. Avaliação

```bash
python scripts/evaluate_model.py --cycle cycle-1 outputs/cycle-1 data/eval.jsonl outputs/benchmarks
python scripts/evaluate_ft_only.py --cycle cycle-1 outputs/cycle-1 data/eval.jsonl outputs/benchmarks
```

---

## Estrutura

```
├── config/
│   └── cycle-1.env                    # Configuração do treino
├── data/
│   ├── curated/                       # 71 arquivos JSONL
│   ├── all_curated.jsonl              # Combinado
│   ├── all_curated_clean.jsonl        # Limpo
│   ├── train.jsonl                    # 2,583
│   ├── valid.jsonl                    # 495
│   └── eval.jsonl                     # 325
├── scripts/
│   ├── generate_diverse_v2.py         # Gerador
│   ├── validate_jsonl.py             # Validação estrutural
│   ├── clean_dataset.py              # Limpeza
│   ├── dedupe_dataset.py             # Deduplicação
│   ├── build_dataset_fixed.py        # Split estratificado
│   ├── export_gguf.py                 # Export GGUF
│   ├── evaluate_model.py             # Avaliação
│   └── evaluate_ft_only.py           # Avaliação FT
├── training/
│   ├── train_mlx_tune.py             # Treino principal
│   └── run_all_cycles.sh             # Orquestrador
└── outputs/
    └── cycle-1/                       # Adapter output
```

---

## Pré-requisitos

```bash
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

- Apple Silicon Mac (M1/M2/M3/M4)
- Python 3.12

---

## Limitações

1. **100% single-turn** - Dataset não tem conversas multi-turn.
2. **Scoring regex-based** - Avaliação usa regex, não embeddings. (existe `semantic_scorer.py` mas não integrado).
3. **Inference manual** - `run_inference.sh` com 4 prompts hardcoded, sem output estruturado.
4. **Deduplicação character-level** - `dedupe_dataset.py` usa similarity por caracter, não embeddings.
5. **Sem RAG** - Não há acesso à documentação OCI em tempo real.