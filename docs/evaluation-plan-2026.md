# Plano de Avaliação Consolidada - OCI Specialist LLM

## Deep Dive: Melhores Práticas de Avaliação (2026)

### Fontes Pesquisadas
- OpenAI Evaluation Best Practices
- DeepChecks LLM Evaluation Framework
- Sogeti: "Did my Fine-tuning work?"
- BenchLM.ai Guide
- ZenML Evaluation Guide
- Weights & Biases

### Princípios Fundamentais (2026)

1. **Avaliação = Processo, não uma única métrica**
   - Não usar apenas perplexity ou loss
   - Combinar métricas automatizadas + avaliação humana
   - Métricas únicas são insuficientes

2. **Pilares da Avaliação**
   - Métricas automatizadas (quick feedback)
   - Avaliação humana (qualidade real)
   - Critérios de qualidade definidos (rubricas)
   - A/B testing com usuários

3. **Tipos de Métricas Recomendadas**
   - **Automáticas**: BLEU, ROUGE, BERTScore, Semantic Similarity
   - **Linguísticas**: Precisão factual, completude, formatação
   - **Human-in-the-loop**: Rubricas estruturadas

4. **Armadilhas a Evitar**
   - Confiar apenas em métricas acadêmicas (perplexity, BLEU)
   - Não criar datasets que não refletem uso real
   - Ignorar viés de prompts

---

## Plano: Script Único de Avaliação

### Objetivo
Criar um script unificado `evaluate_oci.py` que consolide:

1. **evaluate_model.py** - base vs fine-tuned (loss, perplexity)
2. **eval_semantic.py** - similarity com embeddings  
3. **eval_scoring.py** - regex patterns para OCI

### Arquitetura Proposta

```
evaluate_oci.py
├── --base-model      # Modelo base (opcional)
├── --adapter-path    # Adapter LoRA
├── --merged-path    # Modelo mesclado
├── --eval-file      # data/eval.jsonl
├── --output-dir     # outputs/benchmarks/
└── --metrics        # all|semantic|regex|comparison
```

### Métricas a Implementar

| # | Métrica | Tipo | Descrição |
|---|---------|------|------------|
| 1 | Perplexity | Automática | Loss no eval set |
| 2 | Semantic Similarity | Embedding | cosine similarity com reference |
| 3 | OCI Regex Match | Pattern | Detecta termos OCI válidos |
| 4 | Factual Accuracy | Heurística | Shapes, regiões, serviços |
| 5 | Format Compliance | Heurística | JSON estruturado quando requerido |

### Fluxo de Execução

```
1. Carregar eval.jsonl
2. Para cada exemplo:
   a. Gerar resposta do modelo
   b. Calcular perplexity (se base disponível)
   c. Calcular semantic similarity com reference
   d. Executar regex patterns OCI
   e. Detectar factual errors (shapes, regions, CLI)
3. Agregar resultados por categoria
4. Gerar relatório JSON + markdown
```

### Features Relevantes do Novo Script

1. **Comparação base vs fine-tuned**
   - Same prompt, both models
   - Delta de similarity
   - Delta de factual accuracy

2. **Agregação por Categoria OCI**
   - compute, storage, networking, iam, etc.
   - Identifica onde fine-tuning melhorou/piorou

3. **Cache de Avaliação**
   - Evita regenerar respostas já computadas
   - speeds up repeated runs

4. **Relatório Markdown**
   - Summary table
   - Breakdown por categoria
   - Exemplos de melhores/piores respostas

---

## Próximos Passos

1. Criar `scripts/evaluate_oci.py` consolidado
2. Manter scripts antigos como deprecated
3. Atualizar README com novo comando único

---

## Referências

- OpenAI: "Evaluation best practices" (2026)
- DeepChecks: "LLM Evaluation Framework"
- BenchLM.ai: "Complete Guide to LLM Benchmarking"
- Sogeti: "Did my Fine-tuning work?"
- ZenML: "Evaluation for Finetuning"
