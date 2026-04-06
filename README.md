# OCI Specialist LLM

Fine-tuning pipeline para um LLM especialista em Oracle Cloud Infrastructure (OCI) usando Apple Silicon, MLX e LoRA.

[![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.12-blue?style=flat-square&logo=python&logoColor=white)](https://www.python.org)
[![MLX](https://img.shields.io/badge/MLX-Apple%20Silicon-orange?style=flat-square)](https://mlx.ai)
[![Model](https://img.shields.io/badge/Base%20Model-Llama--3.2--3B--Instruct--4bit-purple?style=flat-square)](https://huggingface.co/mlx-community/Llama-3.2-3B-Instruct-4bit)
[![Dataset](https://img.shields.io/badge/Dataset-9940_examples-green?style=flat-square)](docs/taxonomy.md)

> **Idioma**: Todos os dados de treinamento e prompts estão em PT-BR.

---

## Visão Geral

Pipeline completo para fine-tuning de LLM em OCI: geração de dataset sintético, validação, treinamento multi-cycle com MLX LoRA, e avaliação com scoring rubrics.

**Arquitetura de dados:**

```
generate_diverse_v2.py → data/curated/ → validate → dedup → split → train/valid/eval.jsonl
                                                                        ↓
train_mlx_v2.sh (3 cycles) → outputs/cycle-{1,2,3}/ → export_adapter.sh → merged-model/
                                                                          ↓
evaluate_model.py / evaluate_ft_only.py → outputs/benchmarks/
```

**Stack:** Python 3.12, MLX (Apple Silicon), LoRA, `mlx-lm`, JSONL chat format.

---

## Resultados

### Treinamento Atual (Dataset com 15 estruturas, MAX_SEQ_LENGTH=2048)

| Ciclo | LR | Iters | Val Loss | Train Loss | Modo |
|-------|-----|-------|----------|------------|------|
| cycle-1 | 3e-5 | 2450 | 0.073 | 0.062 | Do zero |
| cycle-2 | 1e-5 | 2450 | 0.057 | 0.049 | Resume cycle-1 |
| cycle-3 | 5e-6 | 50 | 0.053 | 0.039 | Resume cycle-2 |

> Val loss decrescente ao longo dos ciclos indica convergência consistente. Cycle-3 usa LR mais baixo (5e-6) para fine-tuning final.

**Adapter final:** `outputs/cycle-3/adapters.safetensors`
**Modelo fundido:** `outputs/merged-model/` (~1.8GB)
**Avaliação FT:** **4.09/5** (994/994 exemplos, 5 dimensões de scoring)

---

## Dataset

### Estatísticas

| Métrica | Valor |
|---------|-------|
| Total | 9,940 exemplos |
| Categorias | 71 topics OCI |
| Por categoria | 140 exemplos |
| Estruturas de resposta | 15 (mapeadas por categoria) |
| Duplicatas | 0 (exatas + próximas, threshold 0.95) |
| Validação SDK | 9 modelos com campos validados |

### Splits

| Split | Exemplos | % | Uso |
|-------|----------|---|-----|
| Train | 7,455 | 75.0% | Fine-tuning |
| Valid | 1,491 | 15.0% | Val loss por ciclo |
| Eval | 994 | 10.0% | Benchmark pós-treino |

### Dificuldade (Train)

| Nível | Count | % |
|-------|-------|---|
| Beginner | 2,182 | 29.3% |
| Intermediate | 3,783 | 50.7% |
| Advanced | 1,490 | 20.0% |

### Categorias por Grupo

| Grupo | Topics | Exemplos |
|-------|--------|----------|
| OCI Core | 21 | 2,940 |
| Migration | 14 | 1,960 |
| Terraform | 12 | 1,680 |
| Security | 9 | 1,260 |
| Troubleshooting | 8 | 1,120 |
| Observability | 4 | 560 |
| DevOps | 4 | 560 |

### Formato dos Exemplos

```json
{
  "messages": [
    {"role": "system", "content": "Você é um arquiteto especialista em OCI..."},
    {"role": "user", "content": "Como criar uma VCN com subnets privadas?"},
    {"role": "assistant", "content": "## Solução\n\n### Passos:\n1. ..."}
  ],
  "metadata": {
    "category": "networking/vcn",
    "difficulty": "intermediate",
    "source": "generated",
    "structure": "step_by_step"
  }
}
```

### Geração de Dados

O dataset é gerado programaticamente por `scripts/generate_diverse_v2.py` (6,144 linhas). Não há chamadas a APIs de LLM externas — todo conteúdo é gerado a partir de templates com substituição de variáveis.

**15 estruturas de resposta:** step_by_step, troubleshooting, code_first, architecture, terraform, python_sdk, best_practices, cost_analysis, security_audit, performance_tuning, disaster_recovery, monitoring_alerting, integration, migration, comparison.

**Mapeamento:** Cada categoria recebe 5-7 estruturas relevantes via `CATEGORY_RESPONSE_MAP`. Ex: `compute/instances` usa step_by_step, troubleshooting, code_first, best_practices, cost_analysis, performance_tuning, disaster_recovery.

**Diversidade:** 20 empresas, 20 projetos, 10 regiões, 9 shapes, 8 OCPUs, 6 storage sizes, 10 compartments, 3 ADs — combinados via `idx` para variação contextual.

**Lookups validados:**
- `OCI_CLI_COMMANDS`: comandos CRUD por categoria (create, list, get, update, delete)
- `OCI_PYTHON_SDK`: client class, métodos, modelo por categoria
- `OCI_TERRAFORM_RESOURCES`: resources e data sources por categoria
- `SDK_MODEL_FIELDS`: campos required/optional por modelo SDK (9 recursos)

**Validação pós-geração:** `validate_example()` verifica presença de keywords do tópico nos primeiros 300 chars, ausência de contaminação cross-cloud (exceto migration), e tamanho mínimo de 200 chars.

---

## Pipeline

### 1. Geração de Dados

```bash
python scripts/generate_diverse_v2.py
```

**Entrada:** Nenhuma (self-contained, usa constantes hardcoded).
**Saída:** `data/curated/*.jsonl` (71 arquivos) + `data/all_curated.jsonl` (combinado).
**Seed:** `random.seed(42)` para reprodutibilidade.

### 2. Validação e Deduplicação

```bash
# Validação estrutural (roles, formato chat, limites de tamanho)
python scripts/validate_jsonl.py data/all_curated.jsonl

# Deduplicação (exata + near-duplicate com threshold 0.95, sobrescreve o arquivo original)
python scripts/dedupe_dataset.py data/all_curated.jsonl --remove
cp data/all_curated.jsonl data/all_curated_clean.jsonl
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
# Todos os ciclos
bash training/run_all_cycles.sh

# Ciclo individual
CYCLE=cycle-1 bash training/train_mlx_v2.sh
```

**Fluxo por ciclo:** `config/cycle-N.env` → gera YAML → `mlx_lm lora` → `outputs/cycle-N/adapters.safetensors`.

**Resume:** Cycle 2+ usa `--resume-adapter-file` do ciclo anterior.

**Logging:** `log_metrics.py` captura stdout do treinamento, parseia `Iter N: Train/Val loss`, exporta CSV.

### 5. Export e Inferência

```bash
# Fundir adapter com base model
ADAPTER_DIR=outputs/cycle-3 bash training/export_adapter.sh

# Testar inferência (4 prompts hardcoded, fallback: merged → adapter → base)
bash training/run_inference.sh
```

### 6. Avaliação

```bash
# Base vs FT (completo, 994 exemplos do eval split, --fresh limpa cache)
python scripts/evaluate_model.py "mlx-community/Llama-3.2-3B-Instruct-4bit" "outputs/merged-model" data/eval.jsonl outputs/benchmarks
python scripts/evaluate_model.py --fresh "mlx-community/Llama-3.2-3B-Instruct-4bit" "outputs/merged-model" data/eval.jsonl outputs/benchmarks  # limpa cache

# FT only (rápido, 994 exemplos do eval split, --fresh limpa checkpoint)
python scripts/evaluate_ft_only.py outputs/merged-model data/eval.jsonl outputs/benchmarks
python scripts/evaluate_ft_only.py --fresh outputs/merged-model data/eval.jsonl outputs/benchmarks  # limpa checkpoint
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

---

## Configuração

### Parâmetros por Ciclo

| Variável | cycle-1 | cycle-2 | cycle-3 |
|----------|---------|---------|---------|
| `LEARNING_RATE` | 3e-5 | 1e-5 | 5e-6 |
| `LORA_RANK` | 16 | 16 | 16 |
| `LORA_ALPHA` | 32 | 32 | 32 |
| `ITERS` | 2450 | 2450 | 500 |
| `MAX_SEQ_LENGTH` | 2048 | 2048 | 2048 |
| `PREV_ADAPTER` | — | cycle-1 | cycle-2 |

**Comuns:** `BATCH_SIZE=1`, `GRADIENT_ACCUMULATION=4`, `LORA_DROPOUT=0.05`, `EPOCHS=2` (não usado — mlx_lm é iteration-based).

### Configuração Completa (`config/cycle-1.env`)

| Variável | Descrição | Valor |
|----------|-----------|-------|
| `MODEL` | Base model HuggingFace | `mlx-community/Llama-3.2-3B-Instruct-4bit` |
| `TRAIN_DATA` | Dataset de treino | `data/train.jsonl` |
| `VALID_DATA` | Dataset de validação | `data/valid.jsonl` |
| `OUTPUT_DIR` | Pasta do adapter | `outputs/cycle-1` |
| `LEARNING_RATE` | Taxa de aprendizado | `3e-5` |
| `LORA_RANK` | Rank da matriz LoRA | `16` |
| `LORA_ALPHA` | Escala LoRA | `32` |
| `LORA_DROPOUT` | Dropout rate | `0.05` |
| `ITERS` | Iterações de treino | `200` |
| `MAX_SEQ_LENGTH` | Tamanho máximo de sequência | `2048` |
| `BATCH_SIZE` | Batch size | `1` |
| `GRADIENT_ACCUMULATION` | Steps antes do update | `4` |

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
│   ├── cycle-1.env               # LR=3e-5, rank=16, iters=2450
│   ├── cycle-2.env               # LR=1e-5, rank=16, iters=2450, resume
│   └── cycle-3.env               # LR=5e-6, rank=16, iters=500, resume
├── data/
│   ├── curated/                  # 71 arquivos × 140 exemplos
│   ├── all_curated.jsonl         # Combinado (9,940)
│   ├── all_curated_clean.jsonl   # Validado + deduplicado
│   ├── train.jsonl               # 7,455 (75%)
│   ├── valid.jsonl               # 1,491 (15%)
│   └── eval.jsonl                # 994 (10%)
├── scripts/
│   ├── generate_diverse_v2.py    # Gerador principal (6,144 linhas)
│   ├── generate_prompt.py        # Prompts a partir da taxonomy
│   ├── validate_jsonl.py         # Validação estrutural
│   ├── dedupe_dataset.py         # Deduplicação exata + near
│   ├── build_dataset_fixed.py    # Split estratificado
│   ├── evaluate_model.py         # Eval base vs FT
│   └── evaluate_ft_only.py       # Eval FT apenas
├── training/
│   ├── train_mlx_v2.sh           # Treino individual com logging
│   ├── run_all_cycles.sh         # Orquestrador multi-cycle
│   ├── export_adapter.sh         # mlx_lm fuse
│   ├── run_inference.sh          # Teste de inferência
│   └── log_metrics.py            # Parser de métricas → CSV
└── outputs/
    ├── cycle-{1,2,3}/            # Adapters por ciclo
    ├── merged-model/             # Modelo fundido (~1.8GB)
    ├── logs/                     # logs + metrics.csv por ciclo
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
4. **Código duplicado:** `evaluate_model.py` e `evaluate_ft_only.py` compartilham ~300 linhas de scoring idêntico.
5. **LoRA rank change:** Cycle-3 usa rank=8 com resume de rank=16. Pode haver mismatch dimensional.
6. **Sem validação de metadata:** `validate_jsonl.py` não verifica campos `metadata.category`, `metadata.difficulty`, `metadata.source`.
7. **Inference manual:** `run_inference.sh` usa 4 prompts hardcoded sem captura ou comparação automática de resultados.

---

## Melhorias Futuras

1. **Multi-turn data:** Gerar 20-30% de exemplos com 2-5 turns para conversas longas.
2. **Shared eval module:** Extrair scoring functions de `evaluate_model.py` e `evaluate_ft_only.py` para módulo compartilhado.
3. **RAG layer:** Documentação OCI em tempo real para precisão factual.
4. **Modelo maior:** Llama-3.1-8B para raciocínio arquitetural.
5. **Avaliação humana:** Review de respostas geradas para qualidade semântica.
6. **Semantic dedup:** Embedding-based similarity ao invés de character-level.
