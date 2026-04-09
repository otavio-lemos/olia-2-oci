# OCI Specialist LLM

Fine-tuning pipeline para um LLM especialista em Oracle Cloud Infrastructure (OCI) usando Apple Silicon, MLX e LoRA.

[![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.12-blue?style=flat-square&logo=python&logoColor=white)](https://www.python.org)
[![MLX](https://img.shields.io/badge/MLX-Apple%20Silicon-orange?style=flat-square)](https://mlx.ai)
[![Model](https://img.shields.io/badge/Base%20Model-Meta--Llama--3.1--8B--Instruct--4bit-purple?style=flat-square)](https://huggingface.co/mlx-community/Meta-Llama-3.1-8B-Instruct-4bit)
[![Dataset](https://img.shields.io/badge/Dataset-3467_examples-green?style=flat-square)](docs/taxonomy.md)
[![Training](https://img.shields.io/badge/Training-MLX--Tune%200.4.18-blue?style=flat-square)](https://github.com/ARahim3/mlx-tune)

> **Idioma**: Todos os dados de treinamento e prompts estão em PT-BR.

---

## Visão Geral

Pipeline completo para fine-tuning de LLM em OCI: geração de dataset sintético, validação, treinamento multi-cycle com MLX LoRA, e avaliação com scoring rubrics.

**Arquitetura de dados:**

```
generate_diverse_v2.py → data/curated/ → prepare_data.sh → train/valid/eval.jsonl
                                                                   ↓
training/run_all_cycles.sh (3 cycles) → outputs/cycle-{1,2,3}/ → export_adapter.sh → merged-model/
                                                                              ↓
evaluate_model.py / evaluate_ft_only.py → outputs/benchmarks/ → report_generator.py / comparison_dashboard.py
```

**Stack:** Python 3.12, MLX 0.31.1, MLX-LM 0.31.1, MLX-Tune 0.4.18 (Unsloth-compatible Python API), JSONL chat format.

---

## Resultados

### Treinamento Atual (Dataset com 3,467 exemplos, MAX_SEQ_LENGTH=2048, MLX-Tune Patched)

| Ciclo | LR | Iters | Val Loss | Train Loss | Peak Mem | Modo |
|-------|-----|-------|----------|------------|----------|------|
| cycle-1 | 2e-5 | 200 | 0.331 | 0.316 | 6.5 GB | Do zero |
| cycle-2 | 1e-5 | 100 | 0.254 | 0.152 | 6.5 GB | Resume cycle-1 |
| cycle-3 | 5e-6 | 50 | 0.259 | 0.099 | 6.5 GB | Resume cycle-2 |

> **Fixes aplicados:** `grad_accumulation_steps` corrigido no MLX-Tune, gradient clipping (norm=1.0), clear cache threshold (5GB), dataset loading corrigido.
> **Performance:** ~85 tokens/sec, ~0.18 iters/sec, Cycle 1 em ~21 minutos no M3 Pro 18GB.

**Adapter final:** `outputs/cycle-3/adapters/` (após todos os cycles)
**Avaliação FT:** Concluída (após cycle-3)

---

## Dataset

O dataset contém 3,467 exemplos únicos gerados com diversidade estrutural e validação rigorosa.

| Métrica | Valor |
|---------|-------|
| **Total de Exemplos** | 3,467 |
| **Categorias** | 71 topics OCI |
| **Exemplos Removidos na Limpeza** | 6,473 (templates genéricos, CLI errado, poluição de contexto, duplicatas) |
| **Comandos CLI Falsos** | 0 |
| **Classes SDK Falsas** | 0 |
| **Resources TF Falsos** | 0 |

### Split Distribution

| Split | Exemplos | Percentual |
|-------|----------|------------|
| Train | 2,583 | 74.5% |
| Valid | 495 | 14.3% |
| Eval | 325 | 9.4% |
| **Total** | **3,467** | **100.0%** |

### Difficulty Distribution (Train)

| Dificuldade | Count | Percentual |
|-------------|-------|------------|
| Beginner | 781 | 30.2% |
| Intermediate | 1,297 | 50.2% |
| Advanced | 505 | 19.6% |

### Categorias por Grupo

| Grupo | Topics | Exemplos |
|-------|--------|----------|
| OCI Core (compute, storage, networking, lb, database, container, serverless) | 20 | 1,036 |
| Security (iam-basics, policies, vault, encryption, cloud-guard, waf) | 9 | 423 |
| Migration (AWS/Azure/GCP/On-prem → OCI) | 14 | 683 |
| Terraform (provider, compute, storage, networking, lb, database, container, serverless, security, observability, devops, state) | 12 | 583 |
| Observability | 4 | 194 |
| Troubleshooting | 8 | 390 |
| DevOps | 4 | 198 |


---

## Pipeline

### 1. Geração de Dados

```bash
python scripts/generate_diverse_v2.py
```

**Entrada:** Nenhuma (self-contained, usa constantes hardcoded).
**Saída:** `data/curated/*.jsonl` (71 arquivos) + `data/all_curated.jsonl` (combinado).
**Seed:** `random.seed(42)` para reprodutibilidade.

### 2. Validação, Limpeza e Deduplicação

```bash
# Executa todo o pipeline de preparação (validate → clean → dedup → split)
bash scripts/prepare_data.sh

# Ou manualmente passo a passo:
# Validação estrutural (roles, formato chat, limites de tamanho)
python3 scripts/validate_jsonl.py data/all_curated.jsonl

# Limpeza de conteúdo (remove templates genéricos, CLI errado, poluição de contexto, shapes em respostas, adiciona acentos)
python3 scripts/clean_dataset.py --input data/all_curated.jsonl --output data/all_curated_clean.jsonl --all

# Deduplicação (exata + near-duplicate com threshold 0.95)
python3 scripts/dedupe_dataset.py data/all_curated_clean.jsonl --remove
if [ -f "data/all_curated_deduped.jsonl" ]; then
    cp data/all_curated_deduped.jsonl data/all_curated_clean.jsonl
fi
```

**validate_jsonl.py:** Verifica JSON parseável, roles válidos (system/user/assistant), primeiro message = system, último = assistant, assistant ≤ 8,192 chars, user ≤ 2,048 chars. Não valida metadata.

**dedupe_dataset.py:** Key = `{category}::{first 200 chars normalized}`. Near-duplicate usa similaridade character-level ≥ 0.95 dentro da mesma categoria. Mantém primeira ocorrência.

### 3. Construção do Dataset

```bash
python scripts/build_dataset_fixed.py --input data/all_curated_clean.jsonl
```

Split estratificado por categoria: 75% train, 15% valid, 10% eval. Seed 42.

### 4. Treinamento

```bash
# Todos os ciclos (do zero)
bash training/run_all_cycles.sh --fresh

# Todos os ciclos (resume do último state)
bash training/run_all_cycles.sh

# A partir de um ciclo específico
bash training/run_all_cycles.sh 2

# Ciclo individual
CYCLE=cycle-1 python training/train_mlx_tune.py
CYCLE=cycle-1 python training/train_mlx_tune.py --fresh  # limpa output e recomeça
```

**Fluxo por ciclo:** `config/cycle-N.env` → `train_mlx_tune.py` (Python API) → `outputs/cycle-N/adapters.safetensors`.

**Parâmetros do config:** Todos vêm do `.env` — zero hardcode. Suporta: MODEL, TRAIN_DATA, OUTPUT_DIR, PREV_ADAPTER, ITERS, MAX_SEQ_LENGTH, BATCH_SIZE, LEARNING_RATE, LORA_RANK, LORA_ALPHA, LORA_DROPOUT, GRADIENT_ACCUMULATION, VAL_BATCHES, NUM_LAYERS, LR_SCHEDULER, WEIGHT_DECAY, WARMUP_STEPS, LOGGING_STEPS, SAVE_STEPS, SEED.

**Resume:** Cycle 2+ usa `PREV_ADAPTER` do ciclo anterior (configurado no `.env`).

**Logging:** Métricas capturadas em `outputs/logs/{cycle}/training.log` e `metrics.csv`.

**`--fresh` flag:**
- `train_mlx_tune.py --fresh`: Remove o `OUTPUT_DIR` e recomeça do zero
- `run_all_cycles.sh --fresh`: Remove todos `outputs/cycle-{1,2,3}` antes de começar

**Rollback:** O script antigo `train_mlx_v2.sh` permanece no repo para fallback.

### Phase 2: Performance Tools (Opcional)

```bash
# Análise de sequence length e recomendação de batch size
python scripts/performance/dynamic_batcher.py --input data/train.jsonl --recommend

# Cache de respostas para avaliação mais rápida
python scripts/performance/eval_cache.py --stats
```

### 5. Export e Inferência

#### Opção 1: Export para MLX (padrão)

```bash
# Fundir adapter com base model (safetensors)
CYCLE=cycle-3 bash training/export_adapter.sh

# O script gera:
#   outputs/merged-model/ — modelo merged em formato MLX/safetensors

# Testar inferência (4 prompts hardcoded, fallback: merged → adapter → base)
bash training/run_inference.sh
```

#### Opção 2: Export para GGUF (Ollama/llama.cpp)

```bash
# Export para GGUF com quantização e importação para Ollama
python scripts/export_gguf.py --cycle cycle-1 --quant q4,q5,q8 --ollama

# Apenas Q4 (mais comum)
python scripts/export_gguf.py --cycle cycle-1 --quant q4 --ollama

# Skip fuse (usar merged model existente)
python scripts/export_gguf.py --cycle cycle-1 --skip-fuse

# O script gera em outputs/cycle-N/gguf/:
#   model-f16.gguf   — FP16 (~16GB para 8B)
#   model-q4.gguf    — Q4_K_M (~4.5GB, recomendado)
#   model-q5.gguf    — Q5_K_M (~5.3GB)
#   model-q8.gguf    — Q8_0 (~8GB)
#   Modelfile-oc*   — arquivo para Ollama
```

**Quantização recomendada:**
| Tipo | Tamanho (8B) | Qualidade |
|------|--------------|-----------|
| Q4_K_M | ~4.5 GB | Melhor custo-benefício |
| Q5_K_M | ~5.3 GB | Alta qualidade |
| Q8_0 | ~8 GB | Quase sem perda |

Para importar manualmente para Ollama:
```bash
ollama create oci-cycle-1 -f outputs/cycle-1/gguf/Modelfile-oc*
ollama run oci-cycle-1
```

### 6. Avaliação

```bash
# Base vs FT (completo, 325 exemplos do eval split, --fresh limpa cache)
python scripts/evaluate_model.py --cycle cycle-3 outputs/merged-model data/eval.jsonl outputs/benchmarks
python scripts/evaluate_model.py --fresh --cycle cycle-3 outputs/merged-model data/eval.jsonl outputs/benchmarks

# FT only (rápido, 325 exemplos do eval split, --fresh limpa checkpoint)
python scripts/evaluate_ft_only.py --cycle cycle-3 outputs/merged-model data/eval.jsonl outputs/benchmarks
python scripts/evaluate_ft_only.py --fresh --cycle cycle-3 outputs/merged-model data/eval.jsonl outputs/benchmarks

# Phase 2: Relatórios HTML automáticos
python scripts/reporting/report_generator.py --results outputs/benchmarks/eval-ft-results-final.json --output outputs/benchmarks/report.html

# Phase 2: Comparison dashboard (base vs FT)
python scripts/reporting/comparison_dashboard.py --base outputs/benchmarks/eval-base-results-final.json --ft outputs/benchmarks/eval-ft-results-final.json --output outputs/benchmarks/comparison.html
```

**5 dimensões de scoring (escala 1-5):**

| Dimensão | O que mede | Penalidades |
|----------|-----------|-------------|
| Technical Correctness | Padrões OCI reais (CLI/SDK/TF) | Fake CLI (-2.0), cross-cloud (-2.5) |
| Depth | Listas numeradas, code blocks, trade-offs, riscos | — |
| Structure | Seções, tabelas, código formatado | — |
| Hallucination | Comandos falsos, URLs inventadas, cross-cloud | Fake patterns (-1.0 a -1.5), cross-cloud (-1.0 a -2.0), fake URLs (-1.5) |
| Clarity | Balanceamento de sentenças, conectivos PT-BR, exemplos | — |

**Checkpoint:** Salva a cada 50 exemplos. Resume automático via `eval-ft-checkpoint.json`. Use `--fresh` para limpar checkpoint e recomeçar do zero.

**`--fresh` flag:**
- `evaluate_model.py --fresh`: Remove resultados cached (`eval-base-results-final.json`, `eval-ft-results-final.json`)
- `evaluate_ft_only.py --fresh`: Remove checkpoint (`eval-ft-checkpoint.json`)

### Phase 2: Quality Tools (Opcional)

```bash
# Scoring semântico para detecção de hallucination
python scripts/quality/semantic_scorer.py --reference ref.txt --generated gen.txt --threshold 0.3

# Verificação factual de respostas OCI (shapes, regions, CLI)
python scripts/quality/factual_checker.py --text "resposta a verificar"
```

---

## Configuração

### Parâmetros por Ciclo

| Variável | cycle-1 | cycle-2 | cycle-3 |
|----------|---------|---------|---------|
| `LEARNING_RATE` | 2e-5 | 1e-5 | 5e-6 |
| `LORA_RANK` | 8 | 8 | 8 |
| `LORA_ALPHA` | 16 | 16 | 16 |
| `LORA_DROPOUT` | 0.0 | 0.0 | 0.0 |
| `ITERS` | 200 | 100 | 50 |
| `MAX_SEQ_LENGTH` | 2048 | 2048 | 2048 |
| `BATCH_SIZE` | 1 | 1 | 1 |
| `GRADIENT_ACCUMULATION` | 2 | 2 | 2 |
| `NUM_LAYERS` | 8 | 8 | 8 |
| `WARMUP_STEPS` | 20 | 50 | 25 |
| `GRADIENT_CLIP_NORM` | 1.0 | 0.5 | 0.5 |
| `CLEAR_CACHE_GB` | 5 | 5 | 5 |
| `PREV_ADAPTER` | — | cycle-1 | cycle-2 |
| `VAL_BATCHES` | 5 | 5 | 5 |

**Comuns:** `LR_SCHEDULER=cosine`, `SEED=42`, `GRADIENT_CHECKPOINTING=true`, `LOGGING_STEPS=5`. Cycle-1 usa `WEIGHT_DECAY=0.01`, cycle-2/3 usam `0.001`.

### Configuração Completa (`config/cycle-1.env`)

| Variável | Descrição | Valor |
|----------|-----------|-------|
| `MODEL` | Base model HuggingFace | `mlx-community/Meta-Llama-3.1-8B-Instruct-4bit` |
| `TRAIN_DATA` | Dataset de treino | `data/train.jsonl` |
| `VALID_DATA` | Dataset de validação | `data/valid.jsonl` |
| `OUTPUT_DIR` | Pasta do adapter | `outputs/cycle-1` |
| `PREV_ADAPTER` | Adapter anterior (resume) | — |
| `EPOCHS` | Épocas de treino | `2` |
| `BATCH_SIZE` | Batch size | `1` |
| `LEARNING_RATE` | Taxa de aprendizado | `2e-5` |
| `LORA_RANK` | Rank da matriz LoRA | `8` |
| `LORA_ALPHA` | Escala LoRA | `16` |
| `LORA_DROPOUT` | Dropout rate | `0.0` |
| `GRADIENT_ACCUMULATION` | Steps antes do update | `2` |
| `NUM_LAYERS` | Camadas LoRA | `8` |
| `ITERS` | Iterações de treino | `200` |
| `MAX_SEQ_LENGTH` | Tamanho máximo de sequência | `2048` |
| `VAL_BATCHES` | Batches de validação | `5` |
| `LOGGING_STEPS` | Log a cada N steps | `5` |
| `SAVE_STEPS` | Save checkpoint a cada N steps | `50` |
| `WARMUP_STEPS` | Warmup steps | `20` |
| `GRADIENT_CHECKPOINTING` | Gradient checkpointing | `true` |
| `LR_SCHEDULER` | Tipo de scheduler | `cosine` |
| `WEIGHT_DECAY` | Regularização | `0.01` |
| `SEED` | Seed para reprodutibilidade | `42` |
| `GRADIENT_CLIP_NORM` | Max norm para gradient clipping | `1.0` |
| `CLEAR_CACHE_GB` | Threshold para clear cache (GB) | `5` |

---

## Estrutura do Projeto

```
olia-2-oci/
├── docs/
│   ├── taxonomy.md               # 72 categorias do dataset
│   ├── quality-rules.md          # Regras de qualidade
│   ├── eval-rubric.md            # Critérios de avaliação
│   └── scope.md                  # Escopo v1 vs v2
├── config/
│   ├── cycle-1.env               # LR=2e-5, rank=8, iters=200, do zero
│   ├── cycle-2.env               # LR=1e-5, rank=8, iters=100, resume
│   └── cycle-3.env               # LR=5e-6, rank=8, iters=50, resume
├── data/
│   ├── curated/                  # 71 arquivos × 140 exemplos
│   ├── all_curated.jsonl         # Combinado (9,940)
│   ├── all_curated_clean.jsonl   # Validado + deduplicado + limpo (3,467)
│   ├── train.jsonl               # 2,583 (74.5%)
│   ├── valid.jsonl               # 495 (14.3%)
│   └── eval.jsonl                # 325 (9.4%)
├── scripts/
│   ├── generate_diverse_v2.py    # Gerador principal (6,144 linhas)
│   ├── generate_prompt.py        # Prompts a partir da taxonomy
│   ├── validate_jsonl.py         # Validação estrutural
│   ├── clean_dataset.py         # Limpeza de conteúdo
│   ├── dedupe_dataset.py         # Deduplicação exata + near
│   ├── build_dataset_fixed.py    # Split estratificado
│   ├── prepare_data.sh           # Pipeline completo de preparação
│   ├── evaluate_model.py         # Eval base vs FT (--fresh limpa cache)
│   ├── evaluate_ft_only.py       # Eval FT apenas (--fresh limpa checkpoint)
│   ├── performance/              # Phase 2: Performance
│   │   ├── async_pipeline.py     # Pipeline async com prefetch
│   │   ├── dynamic_batcher.py   # Batch sizing dinâmico
│   │   └── eval_cache.py         # Cache de respostas
│   ├── quality/                  # Phase 2: Quality
│   │   ├── semantic_scorer.py   # Scoring semântico (embeddings)
│   │   └── factual_checker.py   # Validação factual OCI
│   └── reporting/                 # Phase 2: Reporting
│       ├── report_generator.py  # Relatórios HTML automáticos
│       └── comparison_dashboard.py  # Comparativo base vs FT
├── training/
│   ├── train_mlx_tune.py         # Treino principal (mlx-tune, Python API)
│   ├── train_mlx_v2.sh           # Legacy: treino com mlx-lm (rollback)
│   ├── run_all_cycles.sh         # Orquestrador multi-cycle (--fresh support)
│   ├── export_adapter.sh         # Merge adapter (save_pretrained_merged)
│   ├── run_inference.sh          # Teste de inferência
│   └── log_metrics.py            # Parser de métricas → CSV
└── outputs/
    ├── cycle-{1,2,3}/            # Adapters por ciclo + checkpoints
    ├── merged-model/             # Modelo fundido (~1.8GB)
    ├── logs/                     # training.log + metrics.csv por ciclo
    └── benchmarks/               # Relatórios de avaliação
```

---

## Pré-requisitos

- Apple Silicon Mac (M1/M2/M3/M4)
- Python 3.12

```bash
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## Limitações Conhecidas

1. **Geração template-based:** Dados são gerados programaticamente, não por LLM ou curadoria humana. Qualidade depende dos templates hardcoded.
2. **Scoring regex-based:** Avaliação usa pattern matching, não compreensão semântica. Scores são indicadores proxy.
3. **100% single-turn:** Dataset não contém conversas multi-turn. Modelo não aprendeu manutenção de contexto.
4. **Inference manual:** `run_inference.sh` usa 4 prompts hardcoded sem captura ou comparação automática de resultados.

---

## Melhorias Futuras

1. **Multi-turn data:** Gerar 20-30% de exemplos com 2-5 turns para conversas longas.
2. **RAG layer:** Documentação OCI em tempo real para precisão factual.
3. **Avaliação humana:** Review de respostas geradas para qualidade semântica.
4. **Semantic dedup:** Embedding-based similarity ao invés de character-level.
