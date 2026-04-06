# OCI Specialist LLM - Relatório Final de Validação

**Data:** 2026-04-05
**Escopo:** Validação completa do pipeline — prompts, dataset, dedup, treinamento, reporting, inferência, long context

---

## Resumo Executivo

| Área | Status | Nota |
|------|--------|------|
| Prompts (71 arquivos) | ✅ PASS (corrigido) | Todos dizem "140 exemplos" agora |
| Dataset JSONL (9,940 exemplos) | ✅ PASS | Formato válido, 71 categorias, 140 cada |
| Validação JSONL | ✅ PASS | 9,940/9,940 válidos, 0 erros |
| Deduplicação | ✅ PASS | Exata + near-duplicate (threshold 0.95) |
| Dataset splits | ✅ PASS | 7,455/1,491/994 (75/15/10%) |
| Treinamento pipeline | ⚠️ CORRIGIDO | ITERS e MAX_SEQ_LENGTH adicionados aos configs |
| Reporting/Eval | ⚠️ CORRIGIDO | max_tokens 1024→2048, métricas atualizadas |
| Inferência | ⚠️ CORRIGIDO | max_tokens 512→2048, adapter default cycle-2 |
| Long Context | ⚠️ LIMITAÇÃO | Modelo suporta 128K mas treino usa 4096, dataset 100% single-turn |
| Cross-cloud detection | ✅ PASS | AWS/Azure patterns detectados e penalizados |

---

## Issues Encontradas e Corrigidas

### CRÍTICAS (Corrigidas)

| # | Issue | Arquivo | Correção |
|---|-------|---------|----------|
| 1 | `ITERS` não definido nos configs | config/cycle-{1,2,3}.env | Adicionado ITERS=200/100/50 |
| 2 | `MAX_SEQ_LENGTH` não definido | config/cycle-{1,2,3}.env | Adicionado MAX_SEQ_LENGTH=4096 |
| 3 | export_adapter.sh default para cycle-3 inexistente | training/export_adapter.sh | Default mudado para outputs/cycle-2 |
| 4 | max_tokens=512 muito baixo para inferência | training/run_inference.sh | Aumentado para 2048 |
| 5 | max_tokens=1024 limita respostas complexas | scripts/evaluate_ft_only.py | Aumentado para 2048 |
| 6 | Métricas de treino hardcoded nos reports | scripts/evaluate_model.py | Adicionado cycle-3-v3 (0.039/0.053) |
| 7 | Descrição do modelo hardcoded | scripts/evaluate_ft_only.py | Atualizado para cycle-3-v3, rank=8 |
| 8 | 70/71 prompts diziam "10 exemplos" | tmp/prompt_*.md | Corrigido para "140 exemplos" |

### ALTA (Conhecidas, requerem ação futura)

| # | Issue | Impacto | Recomendação |
|---|-------|---------|--------------|
| 9 | Dataset 100% single-turn | Modelo não aprende conversas multi-turn | Gerar 20-30% de exemplos multi-turn |
| 10 | Apenas 7 templates de resposta cycling | Baixa diversidade estrutural | Expandir para 20+ templates topic-specific |
| 11 | SDK models com campos hallucinados | CreateSecretDetails tem availability_domain/shape | Corrigir geração de código Python SDK |
| 12 | Terraform missing required attributes | oci_core_vcn sem cidr_block | Adicionar validação de resources TF |
| 13 | cycle-3 nunca executado (só v3 logs) | outputs/cycle-3/ não existe | Executar cycle-3 com novos configs ou atualizar pipeline |

### MÉDIA (Baixo impacto)

| # | Issue | Impacto |
|---|-------|---------|
| 14 | Eval incompleto (900/994) | 94 exemplos faltando na avaliação FT |
| 15 | System prompts curtos (~150 chars) | Sem instruções para manutenção de contexto |
| 16 | Exemplos de resposta nos prompts são sempre sobre compute | Irrelevante para topics não-compute |

---

## Estado Atual do Pipeline

### Configurações de Treinamento (Corrigidas)

| Parâmetro | cycle-1 | cycle-2 | cycle-3 |
|-----------|---------|---------|---------|
| LEARNING_RATE | 3e-5 | 1e-5 | 5e-6 |
| ITERS | 200 | 100 | 50 |
| LORA_RANK | 16 | 16 | 8 |
| LORA_ALPHA | 32 | 32 | 16 |
| MAX_SEQ_LENGTH | 4096 | 4096 | 4096 |
| PREV_ADAPTER | — | cycle-1 | cycle-2 |

### Resultados de Treinamento (v3 real)

| Ciclo | Iters | Val Loss | Train Loss |
|-------|-------|----------|------------|
| cycle-1-v3 | 1,864 | 0.074 | 0.073 |
| cycle-2-v3 | 932 | 0.057 | 0.056 |
| cycle-3-v3 | 466 | **0.053** | **0.039** |

### Dataset

| Métrica | Valor |
|---------|-------|
| Total | 9,940 exemplos |
| Categorias | 71 topics OCI |
| Exemplos/categoria | 140 |
| Train | 7,455 (75.0%) |
| Valid | 1,491 (15.0%) |
| Eval | 994 (10.0%) |
| Dificuldade | 29.3% beginner, 50.7% intermediate, 20.0% advanced |
| Duplicatas | 0 |
| Comandos CLI falsos | 0 |
| SDK classes falsas | 0 |
| TF resources falsos | 0 |

### Modelo

| Propriedade | Valor |
|-------------|-------|
| Base | mlx-community/Llama-3.2-3B-Instruct-4bit |
| Context window | 128K (RoPE scaling 32x) |
| Training seq length | 4096 (corrigido de 1024) |
| Merged model | outputs/merged-model/ (1.8GB) |
| Melhor adapter | outputs/cycle-2/adapters.safetensors |

---

## Capacidade de Longas Conversas OCI

### Limitações Atuais

| Fator | Status | Detalhe |
|-------|--------|---------|
| Context window do modelo | ✅ 128K | Suporta conversas muito longas |
| Training sequence length | ⚠️ 4096 | Melhorou de 1024, mas ainda abaixo do capacity |
| Dataset multi-turn | ❌ 0% | Apenas single-turn (system→user→assistant) |
| max_tokens inferência | ✅ 2048 | Corrigido de 512 |
| max_tokens avaliação | ✅ 2048 | Corrigido de 1024 |
| Chat template | ✅ Multi-turn | Template Llama 3 suporta N turns |
| System prompts | ⚠️ Curtos | ~150 chars, sem instruções de contexto |

### Recomendações para Long Context

1. **Aumentar MAX_SEQ_LENGTH para 8192** no próximo ciclo de treino (Apple Silicon aguenta)
2. **Gerar 20-30% de exemplos multi-turn** simulando diálogos reais de suporte OCI
3. **Expandir system prompts** com instruções de manutenção de contexto
4. **Aumentar LoRA rank para 32** no cycle-3 para melhor capacidade de raciocínio

---

## Verificações Automatizadas Executadas

```
✅ validate_jsonl.py data/all_curated_clean.jsonl → 9,940/9,940 válidos
✅ validate_jsonl.py data/eval.jsonl → 994/994 válidos
✅ py_compile em todos os scripts Python → OK
✅ bash -n em todos os scripts shell → OK
✅ 71 prompts existem e correspondem a 71 categorias
✅ 71 arquivos curated com 140 exemplos cada
✅ Splits: 7,455 + 1,491 + 994 = 9,940
✅ AWS/Azure detection implementada nos 2 evaluators
✅ Cross-cloud patterns: 19 patterns com penalidades 1.0-2.5
```

---

## Próximos Passos Recomendados

1. **Regerar dataset com diversidade real** — resolver problema dos 7 templates cycling
2. **Corrigir SDK models hallucinados** — campos inexistentes em CreateSecretDetails, CreateVcnDetails
3. **Adicionar multi-turn ao dataset** — diálogos de 2-5 turns
4. **Executar cycle-3 com novos configs** — ITERS=50, MAX_SEQ_LENGTH=4096, rank=8
5. **Completar avaliação FT** — 94 exemplos restantes (900→994)
6. **Re-fundir modelo com cycle-3** — quando cycle-3 estiver completo
