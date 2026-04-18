# Refatorar merge_export.py - Renomear merged/ para safetensors/ + Corrigir bug

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Renomear diretório `merged/` para `safetensors/` e corrigir bug do glob que impede criação de modelos quantizados

**Architecture:** O merge_export.py atualmente gera modelos em subdiretórios (bf16, q4_k_m) mas tem bug na checagem que pula a criação. Também renomear diretório principal.

**Tech Stack:** Python, mlx_lm, safetensors

---

## Tarefas a Executar

### Task 1: Corrigir bug do glob no merge_export.py

**Files:**
- Modify: `scripts/merge_export.py:483-487`

- [ ] **Step 1: Identificar a linha problemática**

A linha 483-487 tem:
```python
if (
    safetensor_dir.exists()
    and (safetensor_dir / "model.safetensors").exists()
    or safetensor_dir.glob("model-*.safetensors")
):
```

- [ ] **Step 2: Substituir por versão corrigida**

```python
if safetensor_dir.exists() and (list(safetensor_dir.glob("model-*.safetensors")) or (safetensor_dir / "model.safetensors").exists()):
```

- [ ] **Step 3: Commitar**

```bash
git add scripts/merge_export.py
git commit -m "fix: corrige bug do glob que pulava criação de q4_k_m"
```

---

### Task 2: Renomear merged/ para safetensors/ no merge_export.py

**Files:**
- Modify: `scripts/merge_export.py:361-430`

- [ ] **Step 1: Mudar definição do diretório**

Linha ~361:
```python
# De:
merged_dir = cycle_output / "merged"

# Para:
safetensors_dir = cycle_output / "safetensors"
```

- [ ] **Step 2: Atualizar todas referências de merged_dir para safetensors_dir**

 grep para encontrar todas ocorrências e substituir:
- `merged_dir` → `safetensors_dir`
- `merged_path` → `safetensors_path`

Linhas aproximadamente: 377, 379, 380, 385, 387, 388, 391, 394, 430, 433, 480, 515, 516, 520, 526

- [ ] **Step 3: Commitar**

```bash
git add scripts/merge_export.py
git commit -m "refactor: renomeia merged_dir para safetensors_dir"
```

---

### Task 3: Atualizar unified_evaluation_v2.py para usar safetensors/

**Files:**
- Modify: `scripts/unified_evaluation_v2.py:1409-1428`

- [ ] **Step 1: Mudar caminho do diretório**

Linha ~1409:
```python
# De:
merged_path = project_root / output_dir_config / "merged"

# Para:
safetensors_path = project_root / output_dir_config / "safetensors"
```

- [ ] **Step 2: Atualizar referências subsequentes**

Todas ocorrências de `merged_path` para `safetensors_path` no bloco de detecção do modelo ft

- [ ] **Step 3: Commitar**

```bash
git add scripts/unified_evaluation_v2.py
git commit -m "refactor: atualiza para usar safetensors/ em vez de merged/"
```

---

### Task 4: Atualizar documentação README

**Files:**
- Modify: `README.md` e `README.en-US.md`

- [ ] **Step 1: Substituir caminhos em README.md**

De: `outputs/cycle-1/merged/`
Para: `outputs/cycle-1/safetensors/`

- [ ] **Step 2: Substituir caminhos em README.en-US.md**

Mesma substituição

- [ ] **Step 3: Commitar**

```bash
git add README.md README.en-US.md
git commit -m "docs: atualiza caminhos para safetensors/"
```

---

### Task 5: Renomear diretório existente (após as mudanças no código)

**Files:**
- Bash: `mv outputs/cycle-1/merged outputs/cycle-1/safetensors`

- [ ] **Step 1: Verificar se não há referências pendentes**

```bash
grep -r "outputs/cycle-1/merged" --include="*.py" --include="*.sh" --include="*.md"
```

- [ ] **Step 2: Renomear diretório**

```bash
mv outputs/cycle-1/merged outputs/cycle-1/safetensors
```

- [ ] **Step 3: Commitar**

```bash
git add -A
git commit -m "refactor: renomeia diretório merged para safetensors"
```

---

## Verificação Final

Após todas as tarefas:
1. `ls outputs/cycle-1/safetensors/` deve mostrar: `bf16/`, `q4_k_m/` (ou arquivos originais se não gerou ainda)
2. `python scripts/merge_export.py --cycle cycle-1 --quant q4` deve criar `safetensors/q4_k_m/` corretamente
3. `python scripts/unified_evaluation_v2.py --cycle cycle-1 --ft-model outputs/cycle-1/safetensors/q4_k_m` deve funcionar