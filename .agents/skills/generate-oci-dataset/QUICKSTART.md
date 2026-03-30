# Quick Start - Gerar Dataset OCI

## Passo a Passo

### 1. Escolha uma categoria
Liste as categorias disponíveis:
```bash
ls .agents/skills/generate-oci-dataset/prompts/
```

### 2. Leia o prompt da categoria
```bash
cat .agents/skills/generate-oci-dataset/prompts/oci-core/compute.md
```

### 3. Copie o MASTER_PROMPT
```bash
cat .agents/skills/generate-oci-dataset/MASTER_PROMPT.md
```

### 4. Monte o prompt
Combine:
- MASTER_PROMPT (instruções de formato)
- Tópicos da categoria
- Exemplos de perguntas

### 5. Envie para LLM
Use Gemini, GPT-4, Claude, ou Perplexity.

### 6. Salve o resultado
```
data/curated/[categoria]-[nnn].jsonl
```

### 7. Valide
```bash
python3 scripts/validate_jsonl.py data/all_curated.jsonl --filter
```

---

## Estrutura de Arquivos

```
.agents/skills/generate-oci-dataset/
├── MASTER_PROMPT.md      # ← Use isto como base
├── SKILL.md              # Instruções gerais
└── prompts/              # Prompts por categoria
    ├── oci-core/
    ├── oci-security/
    ├── oci-migration/
    └── ...
```

---

## Exemplo Prático

**Categoria**: `oci-core/networking`

**Ação**: 
1. Abra `MASTER_PROMPT.md`
2. Copie o conteúdo
3. Adicione os tópicos de `prompts/oci-core/networking.md`
4. Envie para o Gemini
5. Salve em `data/curated/oci-core/networking-001.jsonl`
