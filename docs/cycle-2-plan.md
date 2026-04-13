# Ciclo 2 - Plano de Ação

## Contexto

O **Cycle 1** foi completado com sucesso, mas a avaliação mostrou áreas que precisam de melhoria:

### Resultados Cycle 1 (200 amostras)

| Métrica | Base | FT | Delta |
|--------|------|----|-------|
| technical_correctness | 3.40 | 3.40 | +0.00 |
| depth | 2.60 | 2.60 | +0.00 |
| structure | 3.93 | 4.23 | **+0.30** |
| hallucination | 3.25 | 3.87 | **+0.62** |
| **clarity** | 3.49 | 3.19 | **-0.30** |
| overall | 3.33 | 3.46 | +0.12 |

### Áreas com Regressão (Top 5)

| # | Categoria | Delta |
|---|-----------|-------|
| 1 | `troubleshooting/performance` | -0.31 |
| 2 | `terraform/networking` | -0.27 |
| 3 | `governance/tagging` | -0.22 |
| 4 | `terraform/compute` | -0.21 |
| 5 | `terraform/serverless` | -0.19 |

---

## Fases do Ciclo 2

### Fase A: Auditoria do Dataset (Semanas 1-2)

| # | Task | Size | Files | Urgency | Risk | ROI | Blast | LOE | Depends On |
|---|---|------|------|---------|------|-----|-------|-----|------------|
| A1 | Identificar exemplos problemáticos em Terraform/Governance | M | data/curated/ | H | M | H | Dataset | 8h | - |
| A2 | Revisar clareza das respostas (tom burocrático → conversacional) | M | data/curated/ | H | M | H | Dataset | 6h | A1 |
| A3 | Substituir perguntas genéricas por cenários arquiteturais | M | data/curated/ | M | M | M | Dataset | 6h | A2 |

### Fase B: Geração de Novos Exemplos (Semanas 2-3)

| # | Task | Size | Files | Urgency | Risk | ROI | Blast | LOE | Depends On |
|---|---|------|------|---------|------|-----|-------|-----|------------|
| B1 | Gerar novos exemplos para categorias com regressão | M | scripts/ | H | L | H | Generation | 4h | A3 |
| B2 | Aplicar novo tom (engenheiro sênior explicando) | M | scripts/ | H | L | H | Generation | 2h | B1 |
| B3 | Usar RAG para validar factualidade | S | rag/ | M | L | M | RAG | 2h | B1 |

### Fase C: Preparação e Limpeza (Semana 3)

| # | Task | Size | Files | Urgency | Risk | ROI | Blast | LOE | Depends On |
|---|---|------|------|---------|------|-----|-------|-----|------------|
| C1 | Validar novos exemplos (validate_jsonl.py) | S | scripts/ | H | L | H | Pipeline | 1h | B2 |
| C2 | Limpar e desduplicar (clean_dataset.py + dedupe_embedding.py) | M | scripts/ | H | L | H | Pipeline | 2h | C1 |
| C3 | Gerar splits (build_dataset_fixed.py) | S | scripts/ | M | L | H | Pipeline | 1h | C2 |

### Fase D: Treinamento (Semana 4)

| # | Task | Size | Files | Urgency | Risk | ROI | Blast | LOE | Depends On |
|---|---|------|------|---------|------|-----|-------|-----|------------|
| D1 | Atualizar config (cycle-2.env): LORA_RANK 8→16, LORA_ALPHA 16→32 | S | config/ | H | M | H | Training | 1h | C3 |
| D2 | Treinar Cycle 2 (training/run_all_cycles.sh --fresh) | L | training/ | H | M | H | Training | 4h | D1 |
| D3 | Exportar para GGUF (scripts/merge_export.py) | M | outputs/ | M | L | M | Export | 1h | D2 |

### Fase E: Avaliação (Semana 5)

| # | Task | Size | Files | Urgency | Risk | ROI | Blast | LOE | Depends On |
|---|---|------|------|---------|------|-----|-------|-----|------------|
| E1 | Avaliação média (200 amostras) vs Cycle 1 | M | scripts/ | H | L | H | Evaluation | 1h | D3 |
| E2 | Comparar métricas (base vs cycle-1 vs cycle-2) | M | outputs/ | H | L | H | Evaluation | 1h | E1 |
| E3 | Análise de categorias específicas | M | outputs/ | M | L | M | Evaluation | 2h | E2 |

---

## Scripts Relevantes

| Script | Uso |
|--------|-----|
| `scripts/generate_diverse_v2.py` | Gerar novos exemplos |
| `scripts/validate_jsonl.py` | Validar JSONL |
| `scripts/clean_dataset.py` | Limpar dataset |
| `scripts/dedupe_embedding.py` | Desduplicar |
| `scripts/build_dataset_fixed.py` | Gerar splits |
| `training/train_mlx_tune.py` | Treinar |
| `scripts/unified_evaluation.py` | Avaliar |
| `rag/api.py` | RAG para validação factual |

---

## Configuração Cycle 2

| Parâmetro | Cycle 1 | Cycle 2 (Proposto) |
|-----------|---------|---------------------|
| MODEL | mlx-community/Meta-Llama-3.1-8B-Instruct-4bit | same |
| LEARNING_RATE | 2e-4 | 1.5e-4 (mais baixo para mais iters) |
| LORA_RANK | 8 | **16** |
| LORA_ALPHA | 16 | **32** |
| LORA_DROPOUT | 0.05 | 0.05 |
| NUM_LAYERS | 16 | 16 |
| ITERS | 3618 | ~5000 (mais iters para rank maior) |
| MAX_SEQ_LENGTH | 2048 | 2048 |

---

## Critérios de Sucesso

| Métrica | Target Cycle 2 |
|--------|----------------|
| technical_correctness | ≥ 3.50 (+0.10) |
| depth | ≥ 2.80 (+0.20) |
| structure | ≥ 4.30 (+0.07) |
| hallucination | ≥ 3.90 (+0.03) |
| **clarity** | ≥ 3.40 (+0.21) |
| **overall** | ≥ 3.60 (+0.14) |

---

## Riscos

| Risco | Likelihood | Impact | Mitigação |
|------|------------|--------|------------|
| Novos exemplos piores que originais | Low | High | Validar com RAG antes de usar |
| Tempo de treinamento maior | Medium | Medium | Usar gradient_checkpointing |
| Regressão em categorias boas | Low | High | Manter 80% examples cycle-1 |

---

## Rollback

| Fase | Cenário | Ação |
|------|---------|------|
| A-C | Exemplos piores | Manter dataset cycle-1, não mesclar |
| D | Treinamento falha | Usar config cycle-1 |
| E | Regressão global | Manrer ciclo 1, não fazer merge |

---

## Executar

```bash
# Geração
python scripts/generate_diverse_v2.py

# Preparação
bash scripts/prepare_data.sh

# Treinamento
CYCLE=cycle-2 bash training/run_all_cycles.sh --fresh

# Avaliação
python scripts/unified_evaluation.py --cycle cycle-2 --mode medium --fresh
```