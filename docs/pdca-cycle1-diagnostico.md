# PDCA Cycle 1 — Diagnóstico Completo do Projeto OCI Specialist LLM

**Data:** 2026-04-03
**Versão:** 1.0
**Backup:** `backup_pdca_20260403-140359/` (7.1GB)

---

## 1. RESUMO EXECUTIVO

O projeto possui 9,940 exemplos de alta qualidade em 71 categorias OCI, com treinamento LoRA parcialmente completo. Foram identificados **6 problemas críticos** e **4 problemas menores** que impedem progresso consistente.

---

## 2. AUDITORIA DO DATASET

### 2.1 Dataset Principal (`data/all_curated.jsonl`)

| Métrica | Valor | Status |
|---------|-------|--------|
| Total de exemplos | 9,940 | ✅ |
| Estrutura JSONL válida | 100% | ✅ |
| Categorias únicas | 71 | ✅ |
| Exemplos por categoria | 140 (uniforme) | ✅ |
| Duplicatas exatas | 0 | ✅ |
| Roles por mensagem | system + user + assistant | ✅ |

### 2.2 Distribuição de Dificuldades

| Dificuldade | all_curated | train | valid | eval |
|-------------|-------------|-------|-------|------|
| Beginner | 2,943 (29.6%) | 1,925 | 383 | 244 |
| Intermediate | 5,039 (50.7%) | 3,276 | 632 | 450 |
| Advanced | 1,958 (19.7%) | 1,302 | 272 | 164 |

### 2.3 PROBLEMA CRÍTICO #1: Splits Incompletos

| Arquivo | Exemplos | Esperado | Diferença |
|---------|----------|----------|-----------|
| all_curated.jsonl | 9,940 | 9,940 | 0 |
| train.jsonl | 6,503 | ~7,455 | -952 |
| valid.jsonl | 1,287 | ~1,491 | -204 |
| eval.jsonl | 858 | ~994 | -136 |
| **Soma dos splits** | **8,648** | **9,940** | **-1,292** |

**Causa raiz:** 1,292 exemplos (19 por categoria × 68 categorias) estão em `all_curated.jsonl` mas NÃO foram incluídos em nenhum split. Isso indica que o script de split (`scripts/build_dataset_fixed.py`) foi executado com uma versão anterior do dataset e não foi re-executado após a expansão para 9,940 exemplos.

**Impacto:** ~13% do dataset está sendo desperdiçado em todos os treinamentos.

### 2.4 Dataset V2 (`data/v2/`)

| Arquivo | Exemplos | Categorias | Notas |
|---------|----------|------------|-------|
| train.jsonl | 9,940 | 71 (140 cada) | Dataset completo como train |
| valid.jsonl | 858 | 71 (12-14 cada) | Subset como valid |
| test.jsonl | **NÃO EXISTE** | - | ❌ Faltando |

**Problema:** O dataset v2 usa todo o dataset como train, sem separação adequada. Não há test.jsonl para avaliação.

### 2.5 Arquivos Problemáticos

| Arquivo | Problema |
|---------|----------|
| `data/all_curated_clean.jsonl` | Contém log de validação (8 linhas de texto), NÃO é JSONL válido |
| `data/all_curated_filtered.jsonl` | 8,716 exemplos (versão filtrada, não usada) |

---

## 3. AUDITORIA DE TREINAMENTO

### 3.1 Histórico de Execuções

| Ciclo | Modelo | Rank | LR | Iters | Val Loss | Status |
|-------|--------|------|----|-------|----------|--------|
| cycle-1 | Llama-3.2-3B-4bit | 8 | 5e-5 | 200 | 0.163 | ✅ Completo |
| cycle-2 | resume c1 | 8 | 1e-5 | 100 | 0.119 | ✅ Completo |
| cycle-3 | resume c2 | 8 | 5e-6 | 50 | 0.114 | ✅ Completo |
| cycle-1-v2 | Llama-3.2-3B-4bit | 32 | 3e-5 | 2485 | ? | ✅ Completo |
| cycle-2-v2 | resume c1-v2 | 32 | 1e-5 | 1243 | ? | ✅ Completo |
| cycle-3-v2 | resume c2-v2 | 32 | 5e-6 | 622 | ? | ✅ Completo |
| cycle-1-v3 | Llama-3.2-3B-4bit | 32 | 3e-5 | 500 | 0.121@450 | ⚠️ Incompleto |
| cycle-2-v3 | - | 32 | 1e-5 | 250 | - | ❌ Não executado |
| cycle-3-v3 | - | 32 | 5e-6 | 125 | - | ❌ Não executado |

### 3.2 PROBLEMA CRÍTICO #2: Cycle-1-v3 Incompleto

- **Config .env:** `EPOCHS=3`, `ITERS` não definido (default do script: 2485)
- **Config .yaml:** `iters=500`
- **Log:** Parou em iter ~470 sem marcador de conclusão
- **Val loss em 450:** 0.121 (bom, mas pode melhorar)
- **Adapters:** Existem até `0000450_adapters.safetensors` (111MB cada)

**Causa raiz:** O treinamento foi interrompido prematuramente (possivelmente por timeout ou interrupção manual). O script `train_mlx_v2.sh` usa `.env` files, mas os `.yaml` configs existem e NÃO são utilizados pelo script atual.

### 3.3 PROBLEMA CRÍTICO #3: Incompatibilidade .env vs .yaml

| Arquivo | Formato | Usado pelo script? |
|---------|---------|-------------------|
| `config/cycle-*-v3.env` | Shell env | ✅ Sim (train_mlx_v2.sh) |
| `config/cycle-*-v3.yaml` | YAML config | ❌ NÃO (script não suporta) |

Os `.yaml` configs foram criados para uso com `mlx_lm.lora --config`, mas `train_mlx_v2.sh` monta argumentos manualmente e ignora os `.yaml` files.

### 3.4 PROBLEMA CRÍTICO #4: `train_mlx_v2.sh` não usa `--epochs`

O script `train_mlx_v2.sh`:
- Define `ITERS=${ITERS:-2485}` como default
- Os `.env` files definem `EPOCHS` mas o script **NÃO converte epochs para iters**
- `mlx_lm.lora` **NÃO aceita `--epochs`**, apenas `--iters`
- Se `ITERS` não está definido no `.env`, usa 2485 (que é ~1 epoch completo para 6,503 exemplos com batch=1, grad_accum=4)

**Cálculo correto de iters:**
- Dataset train: 6,503 exemplos
- Batch size: 1, Grad accumulation: 4 → effective batch = 4
- 1 epoch = 6,503 / 4 ≈ 1,626 iters
- Para 3 epochs: ~4,878 iters

### 3.5 PROBLEMA CRÍTICO #5: Dataset desatualizado nos configs

Os configs v3 (`cycle-*-v3.env`) usam `data/train.jsonl` (6,503 exemplos — incompleto).
Deveriam usar o dataset completo (9,940) com splits corrigidos.

### 3.6 PROBLEMA CRÍTICO #6: Sem avaliação no test set

- `data/eval.jsonl` existe (858 exemplos) mas não é usado como `test.jsonl`
- MLX LM espera `test.jsonl` para `--test`
- Não há script rodando avaliação automática pós-treinamento

---

## 4. AUDITORIA DE ARQUIVOS

### 4.1 Arquivos Órfãos (git deleted mas presentes no backup)

**Scripts deletados (25 arquivos):**
```
scripts/build_dataset.py, convert_to_chat.py, fix_all_escaping.py,
fix_double_backslash.py, fix_json_errors.py, fix_metadata.py,
fix_real_newlines.py, fix_truncated.py, fix_truncated_final.py,
gen_batch.py, generate_all_categories.py, generate_all_data.py,
generate_all_jsonl.py, generate_final_batch.py, generate_jsonl_batch.py,
generate_master.py, generate_migration_batch1.py, generate_migration_batch2.py,
generate_part2.py, generate_prompt.py, generate_remaining.py,
generate_security_batch.py, generate_security_batch2.py, split_dataset.py
```

**Training deletado:**
```
training/train_mlx.sh
```

### 4.2 Arquivos Não Trackados

| Arquivo/Dir | Descrição |
|-------------|-----------|
| `backup_full_validation/` | Backup antigo |
| `backup_pre_expansao/` | Backup antigo |
| `backup_pdca_20260403-140359/` | Backup atual (este PDCA) |
| `config/cycle-*-v2.env`, `cycle-*-v3.env`, `cycle-*-v3.yaml` | Configs novas |
| `data/v2/` | Dataset v2 (sem test split) |
| `data/all_curated_filtered.jsonl` | Dataset filtrado não usado |
| `outputs/` | Todos os adapters e logs |
| `scripts/generate_additional.py` | Novo gerador |
| `training/run_all_cycles_v2.sh` | Novo orquestrador |

### 4.3 Problemas Menores

| # | Problema | Severidade |
|---|----------|------------|
| M1 | `data/all_curated_clean.jsonl` é texto, não JSONL | Baixa |
| M2 | ~70 arquivos modificados sem commit | Baixa |
| M3 | Múltiplos backups ocupando ~15GB | Baixa |
| M4 | `run_all_cycles.sh` vs `run_all_cycles_v2.sh` sem clareza | Baixa |

---

## 5. MELHORES PRÁTICAS MLX LoRA (Referência Oficial)

Baseado na documentação oficial `ml-explore/mlx-lm`:

### 5.1 Parâmetros Recomendados

| Parâmetro | Default MLX | Nosso v1 | Nosso v3 | Recomendação |
|-----------|-------------|----------|----------|--------------|
| LoRA rank | 8 | 8 | 32 | ✅ 32 para dataset grande |
| LoRA alpha | - | 16 | 64 | ✅ alpha = 2× rank |
| LoRA dropout | 0.0 | 0.05 | 0.05 | ✅ Bom |
| Num layers | 16 | 16 | 16 | ✅ OK |
| Batch size | 4 | 1 | 1 | ⚠️ Poderia ser 2 |
| Grad accum | 1 | 4 | 4 | ✅ Effective batch = 4 |
| Max seq len | 2048 | 1024 | 1024 | ⚠️ Poderia ser 2048 |
| LR | 1e-5 | 5e-5→5e-6 | 3e-5→5e-6 | ✅ LR decay strategy OK |

### 5.2 Fórmula de Iters

```
iters_per_epoch = ceil(len(train_data) / (batch_size × grad_accumulation))
```

Para nosso dataset:
- **Atual (6,503):** 6,503 / 4 = 1,626 iters/epoch
- **Corrigido (9,940):** 9,940 / 4 = 2,485 iters/epoch

### 5.3 LR Schedule Recomendado

Para multi-cycle training:
1. **Cycle 1:** LR mais alto (3e-5), 1-2 epochs completas
2. **Cycle 2:** LR médio (1e-5), 0.5-1 epoch
3. **Cycle 3:** LR baixo (5e-6), 0.25-0.5 epoch

O MLX LM suporta `lr_schedule` via YAML config com `cosine_decay` e `warmup`.

---

## 6. PLANO DE CORREÇÃO (DO)

### Fase 1: Corrigir Dataset (Prioridade ALTA)
1. **Rebuild dos splits** com 100% dos 9,940 exemplos (75/15/10 estratificado)
2. **Renomear** `data/all_curated_clean.jsonl` (arquivo corrompido)
3. **Criar** `data/test.jsonl` apontando para eval.jsonl

### Fase 2: Corrigir Configs de Treinamento (Prioridade ALTA)
4. **Unificar** configs: remover .yaml não usados ou migrar script para YAML
5. **Corrigir** ITERS nos .env files baseado no dataset corrigido
6. **Criar** `run_all_cycles_v3.sh` orquestrador limpo

### Fase 3: Re-treinar com Dataset Corrigido (Prioridade ALTA)
7. **Cycle 1-v3:** LR=3e-5, iters=2485 (1 epoch), rank=32
8. **Cycle 2-v3:** Resume, LR=1e-5, iters=1243 (0.5 epoch)
9. **Cycle 3-v3:** Resume, LR=5e-6, iters=622 (0.25 epoch)

### Fase 4: Avaliação e Validação (Prioridade MÉDIA)
10. **Avaliar** modelo no test set (eval.jsonl)
11. **Comparar** base vs fine-tuned
12. **Gerar** relatório de benchmark

### Fase 5: Limpeza (Prioridade BAIXA)
13. **Commit** organizado
14. **Remover** backups antigos
15. **Documentar** estrutura final

---

## 7. REFERÊNCIAS

- MLX LoRA Docs: https://github.com/ml-explore/mlx-lm/blob/main/mlx_lm/LORA.md
- MLX Example Config: https://github.com/ml-explore/mlx-lm/blob/main/mlx_lm/examples/lora_config.yaml
- Awni's LoRA Notebook: https://gist.github.com/awni/773e2a12079da40a1cbc566686c84c8f
- mlx-lm version: 0.31.1
- mlx version: 0.31.1
