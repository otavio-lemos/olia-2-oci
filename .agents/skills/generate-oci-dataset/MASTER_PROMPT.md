# Master Prompt para Geração de Dataset OCI

Use este master prompt com qualquer LLM online (Gemini, GPT-4, Claude, Perplexity).

## Como Usar

1. Escolha uma categoria do @docs/taxonomy.md
2. Leia o prompt da categoria em `.agents/skills/generate-oci-dataset/prompts/[categoria].md`
3. Monte o prompt final com as referências abaixo
4. Envie para o LLM
5. Salve em `data/curated/[categoria]-[nnn].jsonl`

---

## Master Prompt

```
Você é um especialista em Oracle Cloud Infrastructure (OCI) e deve gerar exemplos de training para um modelo de LLM fino-tuned.

## Contexto

Consulte:
- @docs/taxonomy.md - para ver a categoria e seus tópicos
- @docs/quality-rules.md - para regras de qualidade obrigatórias

## Categoria a Gerar

[INSIRA A CATEGORIA AQUI - ex: oci-core/compute]

## Prompt Específico da Categoria

[LEIA O ARQUIVO .agents/skills/generate-oci-dataset/prompts/[categoria].md E INSIRA O CONTEÚDO AQUI]
Exemplo: .agents/skills/generate-oci-dataset/prompts/oci-core/compute.md
```

---

## Estrutura de Referências

```
.agents/skills/generate-oci-dataset/MASTER_PROMPT.md (este arquivo)
├── @docs/taxonomy.md                          ← categorias, links docs
├── @docs/quality-rules.md                     ← regras de qualidade
└── .agents/skills/generate-oci-dataset/prompts/
    ├── oci-core/compute.md
    ├── oci-core/storage.md
    └── ...
```

---

## Fluxo de Geração

1. **Escolha categoria** → @docs/taxonomy.md
2. **Leia prompt específico** → .agents/skills/generate-oci-dataset/prompts/[categoria].md
3. **Monte prompt** → MASTER_PROMPT + categoria + prompt específico
4. **Envie para LLM**
5. **Salve resultado** → data/curated/[categoria]-[nnn].jsonl
6. **Valide** → validate_jsonl.py --filter
