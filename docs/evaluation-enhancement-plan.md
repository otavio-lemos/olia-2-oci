# Plano de Ação: Avaliação OCI Specialist LLM

## Contexto

Scripts atuais:
- `evaluate_model.py` → Base vs FT comparison (principal)
- `evaluate_ft_only.py` → redundante, remover
- `eval_semantic.py` → embeddings similarity
- `eval_scoring.py` → funções de scoring (5 dimensões)

Métricas atuais (escala 1-5):
- technical_correctness
- depth  
- structure
- hallucination (inverso - maiores = melhor)
- clarity
- overall (média)

---

## Tarefas

### 1. Remover scripts redundantes

```bash
# Remover evaluate_ft_only.py
rm scripts/evaluate_ft_only.py
```

Rationale: FT-only não serve pra nada. Não interessa avaliar FT sozinho - o que importa é mostrar que FT é melhor que base.

### 2. Dashboard HTML com visualização

Gráficos a incluir:
- Radar chart (5 dimensões - base vs FT)
- Bar chart comparativo por categoria
- Heatmap por dificuldade
- Histograma de distribuição de scores

Tecnologia: Chart.js (standalone, zero dependencias)

### 3. Melhorar relatórios

Adicionar ao `evaluate_model.py`:
- Tabela sumarizada no header do README
- Badge shields.io para Overall e Hallucination
- QR code/link pra dashboard

### 4. (Opcional) LLM-as-judge

Só se quiser avaliação automatizada de qualidade. Nem é necessário - as scoring functions já funcionam bem.

---

## Cronograma

| Tarefa | Esforço |
|--------|---------|
| Remover ft_only.py | 5min |
| Dashboard HTML | 4h |
| Melhorar relatórios | 2h |
| LLM-as-judge (opcional) | 4h |

---

## Métricas que importam

Para esse projeto Specifically, zero interesse em:
- Perplexity
- BLEU/ROUGE
- MMLU
- MT-Bench

São métricas genéricas que não medem a tarefa. O scoring atual com 5 dimensões já é o correto.

---

## Output Visual Esperado

```
┌─────────────────────────────────────────────┐
│  OCI Specialist LLM - Benchmark Results    │
├─────────────────────────────────────────────┤
│  Overall:  4.2/5  ▲ +0.8 vs base          │
│  Hallucination: 4.5/5  ▲ +0.9 vs base    │
└─────────────────────────────────────────────┘

[Bar Chart: Base vs FT por categoria]

[Radar Chart: 5 dimensões]
```

---

## Decisões

1. ** Dashboard com Chart.js?** Sim/Não
2. **LLM-as-judge?** Sim/Não 
3. **Badge shields.io?** Sim/Não

---

## Arquivo Atual

Ver `scripts/eval_scoring.py` para as scoring functions. Estão boas.