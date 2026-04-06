# Próximas Melhorias do Projeto

## Análise Completa - Limitações e Melhorias

### 1. Geração template-based (依赖模板)
**Status atual:** `generate_diverse_v2.py` tem ~6000 linhas com templates hardcoded

**Soluções possíveis:**
- ✅ **Ja existe infra:** `sentence-transformers` já está em requirements.txt
- ✅ **Parcial:** factual_checker.py já valida shapes/regions/CLI
- ⚠️ **Difícil sem LLM externo:** Precisaria de um LLM para gerar dados genuínos — mas isso custaria dinheiro
- **Alternativa:** Expandir templates com mais variações (empresas, cenários, CLI options)

---

### 2. Scoring regex-based (评分依赖正则)
**Status atual:** `eval_scoring.py` usa ~50 regex patterns

**Soluções possíveis:**
- ✅ **Já implementado:** `scripts/quality/semantic_scorer.py` usa embeddings (paraphrase-MiniLM-L6-v2)
- ✅ **Factual checker:** `scripts/quality/factual_checker.py` já valida shapes/regions/cli
- **Melhoria:** Integrar esses módulos na avaliação principal

---

### 3. 100% single-turn (单轮对话)
**Status atual:** Dataset só tem system→user→assistant

**Soluções possíveis:**
- ⚠️ **Precisa novo script:** Não existe código para gerar conversas multi-turn
- **Alternativa:** Criar nova função em `generate_diverse_v2.py` para gerar diálogos de 2-5 turns
- **Complexidade:** Baixa —只需 adicionar campo `messages` com múltiplos user/assistant

---

### 4. Inference manual (手动推理)
**Status atual:** `run_inference.sh` usa 4 prompts hardcoded, sem output estruturado

**Soluções possíveis:**
- ✅ **Fácil:** Criar script que:
  - Leia prompts de arquivo JSONL
  - Execute inference
  - Salve respostas em JSONL para comparação
  - Gere relatório de diferenças

---

### 5. Semantic dedup (语义去重)
**Status atual:** `dedupe_dataset.py` usa character-level similarity (linha 62-63)

**Soluções possíveis:**
- ✅ **Já infraestrutura:** `semantic_scorer.py` existe e usa embeddings
- **Melhoria:** Modificar `dedupe_dataset.py` para usar embeddings ao invés de character-level

---

### 6. RAG layer (RAG图层)
**Status atual:** Não existe

**Soluções possíveis:**
- ⚠️ **Complexo:** Requer OCI documentation API ou vector DB
- **Alternativa simples:** Crawl documentação OCI → chunk → embedding → retrieval em tempo de inference

---

## Priorização Recomendada

| # | Item | Esforço | Impacto | Recommendation |
|---|------|---------|---------|----------------|
| 1 | Semantic dedup | **Baixo** | Alto | Modificar dedupe_dataset.py para usar semantic_scorer |
| 2 | Inference automation | **Baixo** | Médio | Novo script inference_runner.py com arquivo de prompts + output estruturado |
| 3 | Multi-turn data | **Médio** | Alto | Adicionar função em generate_diverse_v2.py |
| 4 | Semantic scoring na eval | **Médio** | Médio | Integrar semantic_scorer no pipeline de avaliação |
| 5 | RAG layer | **Alto** | Alto | Novo pipeline (crawl → embed → retrieve) |