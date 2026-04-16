# Dataset Quality Improvement Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Corrigir dataset gerado por `generate_v5_combined.py` para eliminar respostas duplicadas em intents "update" e "manage", aumentar diversidade, e verificar integridade de todas as categorias.

**Architecture:** Modificar script de geração para produzir respostas únicas baseadas em contexto (empresa, projeto, constraint, lifecycle). Adicionar CLI commands específicos para cada intent. Criar script de validação para verificar qualidade.

**Tech Stack:** Python 3, JSONL, CLI OCI

---

## Chunk 1: Análise e Diagnóstico

### Task 1: Mapear todas as categorias com problema de duplicação

**Files:**
- Analyze: `scripts/generate_v5_combined.py:1545-1720`
- Test: verificar manualmente

- [ ] **Step 1: Executar análise de unicidade por intent**

```python
import json
import os

def analyze_dataset(path):
    results = {}
    for fname in os.listdir(path):
        if not fname.endswith('.jsonl'):
            continue
        filepath = os.path.join(path, fname)
        intents = {}
        with open(filepath) as f:
            for line in f:
                d = json.loads(line)
                intent = d.get('metadata', {}).get('intent', 'unknown')
                content = d['messages'][-1]['content']
                if intent not in intents:
                    intents[intent] = set()
                intents[intent].add(content[:100])
        
        results[fname] = {k: len(v) for k, v in intents.items()}
    return results

results = analyze_dataset("data/curated_v5_dedup")
for fname, stats in results.items():
    if any(v == 1 for v in stats.values()):
        print(f"❌ {fname}: {stats}")
```

Run: `python3 analyze_duplicates.py`
Expected: Lista de categorias com intents having only 1 unique response

- [ ] **Step 2: Documentar categorias afetadas**

Salvar resultado em `docs/dataset-quality-report.md`

- [ ] **Step 3: Commit**

```bash
git add docs/dataset-quality-report.md
git commit -m "docs: add dataset quality analysis report"
```

---

## Chunk 2: Corrigir script generate_v5_combined.py

### Task 2: Adicionar CLI commands para update/manage

**Files:**
- Modify: `scripts/generate_v5_combined.py:1642-1720`
- Test: `scripts/generate_v5_combined.py`

- [ ] **Step 1: Adicionar CLI_COMMANDS para intent "update"**

Adicionar dicionário após CLI_COMMANDS existente (linha ~200):

```python
# CLI commands para intents de management
UPDATE_COMMANDS = {
    "compute/instances": """# Atualizar instância
oci compute instance update \
  --instance-id {instance_id} \
  --display-name "{name}-updated" \
  --shape-config "ocpus={ocpus},memory={memory}" \
  --wait-for-state RUNNING

# Resize (change shape)
oci compute instance update \
  --instance-id {instance_id} \
  --shape VM.Standard2.4 \
  --preserve-boot-volume false \
  --wait-for-state RUNNING

# Update boot volume
oci compute boot-volume update \
  --boot-volume-id {volume_id} \
  --size-in-gbs {size}""",

    "compute/scaling": """# Update instance pool
oci compute instance-pool update \
  --instance-pool-id {instance_pool_id} \
  --size {new_size} \
  --wait-for-state RUNNING

# Update autoscaling config
oci autoscaling policy update \
  --policy-id {policy_id} \
  --min-instance-count {min} \
  --max-instance-count {max}""",

    "database/autonomous": """# Update ADB
oci db autonomous-database update \
  --autonomous-database-id {adb_id} \
  --cpu-core-count {cores} \
  --storage-size-in-tbs {storage} \
  --db-name "{name}" \
  --wait-for-state AVAILABLE

# Update license
oci db autonomous-database update \
  --autonomous-database-id {adb_id} \
  --license-model INCLUDED""",

    "storage/block": """# Update volume
oci blockstorage volume update \
  --volume-id {volume_id} \
  --size-in-gbs {size} \
  --vpus-per-gb {vpus} \
  --wait-for-state AVAILABLE""",

    "storage/object": """# Update bucket
oci os bucket update \
  --namespace-name {namespace} \
  --bucket-name {bucket_name} \
  --public-access-type NoPublicAccess \
  -- versioning Enabled""",

    "networking/vcn": """# Update VCN
oci network vcn update \
  --vcn-id {vcn_id} \
  --display-name "{vcn_name}-updated" \
  --cidr-block {new_cidr}

# Update subnet
oci network subnet update \
  --subnet-id {subnet_id} \
  --display-name "{name}-updated" \
  --prohibit-public-ip-on-vnic true""",

    # ... adicionar para todas as categorias
}

# Adicionar no generate_response() para usar quando intent == "update"
```

- [ ] **Step 2: Adicionar CLI commands para intent "manage"**

```python
MANAGE_COMMANDS = {
    "compute/instances": """# Start/Stop/Reset
oci compute instance action \
  --instance-id {instance_id} \
  --action START \
  --wait-for-state RUNNING

oci compute instance action \
  --instance_id {instance_id} \
  --action STOP \
  --wait-for-state STOPPED

oci compute instance action \
  --instance_id {instance_id} \
  --action RESET

# Get console output
oci compute instance get \
  --instance-id {instance_id} \
  --raw-output --query 'data."console-output".value' | base64 -d""",

    "compute/scaling": """# Scale instance pool
oci compute instance-pool update \
  --instance-pool-id {instance_pool_id} \
  --size {new_size}

# Trigger scale
oci compute instance-pool attach-instance \
  --instance-pool-id {instance_pool_id} \
  --instance-configuration-id {config_id}""",

    "database/autonomous": """# Start/Stop ADB
oci db autonomous-database start \
  --autonomous-database-id {adb_id} \
  --wait-for-state RUNNING

oci db autonomous-database stop \
  --autonomous-database-id {adb_id} \
  --wait-for-state STOPPED

# Restart
oci db autonomous-database restart \
  --autonomous-database-id {adb_id} \
  --wait-for-state AVAILABLE""",

    "storage/block": """# Backup volume
oci blockstorage volume backup create \
  --volume-id {volume_id} \
  --display-name "{name}-backup"

# Restore
oci blockstorage volume backup restore \
  --backup-id {backup_id} \
  --volume-id {volume_id}""",

    # ... adicionar para todas as categorias
}
```

- [ ] **Step 3: Modificar generate_response() para usar os novos commands**

Modificar lines 1456-1720:

```python
def generate_response(
    category, intent, idx, company, project, region, compartment, constraint, lifecycle
):
    # ... existing code ...
    
    # Add new CLI sources
    if intent == "update":
        cli_template = UPDATE_COMMANDS.get(category, CLI_COMMANDS.get(category, {}).get("update", ""))
    elif intent == "manage":
        cli_template = MANAGE_COMMANDS.get(category, CLI_COMMANDS.get(category, {}).get("manage", ""))
    
    # ... rest of function
```

- [ ] **Step 4: Commit**

```bash
git add scripts/generate_v5_combined.py
git commit -m "fix: add CLI commands for update/manage intents"
```

### Task 3: Adicionar variação contextual nos templates

**Files:**
- Modify: `scripts/generate_v5_combined.py:1545-1720`

- [ ] **Step 1: Modificar templates para usar variáveis contextuais**

Cada template deve incorporar as variáveis: company, project, constraint, lifecycle

```python
# Exemplo: modificar template "update" para incluir variação
"update": f"""Vamos Atualizar {subcat} para {company} no projeto {project}:

**Contexto**: Ambiente {lifecycle} com constraint: {constraint}

**Fase 1: Planejamento**
- Identifique o resource no compartment `{compartment}`
- Avalie impacto das alterações considerando {constraint}
- Programe manutenção durante {random.choice(['janela de manutenção', 'horário de baixo uso', 'período de rollout'])}

**Fase 2: Backup**
- Execute: `oci {service} get --id <ocid> > backup_{project}.json`
- Documente configuração atual
- Tenha plano de rollback: `restore from backup if {constraint}`

**Fase 3: Execução**
{cli_command}

**Fase 4: Validação**
- Execute: `oci {service} get --id <ocid>`
- Confirme que {lifecycle} está estável
- Atualize documentação de {project}

**Dicas**:
- Para {constraint}, use abordagem gradual (blue-green)
- Monitore custos pós-update em {project}
- Configure alertas para detectar regressões

**Referência**: ...""",
```

- [ ] **Step 2: Commit**

```bash
git add scripts/generate_v5_combined.py
git commit -m "fix: add contextual variation to response templates"
```

### Task 4: Aumentar diversidade de templates

**Files:**
- Modify: `scripts/generate_v5_combined.py`

- [ ] **Step 1: Criar variações de templates por intent**

Adicionar 3-5 variações para cada intent:

```python
# Adicionar antes de generate_response()
TEMPLATE_VARIATIONS = {
    "create": [
        "verbose",   # Passo a passo detalhado
        "cli-first", # Foco em CLI
        "console-first", # Foco no console
        "terraform", # Incluir TF
    ],
    "update": [
        "conservative",   # Foco em backup/rollback
        "fast",          # Quick updates
        "production",    # Zero-downtime
        "cost-focused",  # Otimização de custos
    ],
    # ... etc
}
```

- [ ] **Step 2: Selecionar variação baseada no contexto**

```python
def select_variation(intent, constraint, lifecycle):
    variations = TEMPLATE_VARIATIONS.get(intent, ["default"])
    
    if "budget" in constraint.lower():
        return "cost-focused"
    elif lifecycle == "production":
        return "production"
    elif lifecycle == "greenfield":
        return "verbose"
    # ... mais regras
    
    return random.choice(variations)
```

- [ ] **Step 3: Aplicar variações nos templates**

Modificar generate_response() para usar variações.

- [ ] **Step 4: Commit**

```bash
git add scripts/generate_v5_combined.py
git commit -m "feat: add template variations for diversity"
```

---

## Chunk 3: Regeração e Validação

### Task 5: Regenerar dataset corrigido

**Files:**
- Run: `scripts/generate_v5_combined.py`
- Output: `data/curated_v6/`

- [ ] **Step 1: Executar script regenerado**

```bash
python3 scripts/generate_v5_combined.py
```

- [ ] **Step 2: Verificar estrutura do output**

```bash
ls -la data/curated_v6/ | wc -l
wc -l data/curated_v6/*.jsonl | tail -3
```

- [ ] **Step 3: Commit**

```bash
git add data/curated_v6/
git commit -m "data: regenerate dataset v6 with fixed responses"
```

### Task 6: Validar qualidade do novo dataset

**Files:**
- Create: `scripts/validate_dataset.py`
- Test: Executar validação

- [ ] **Step 1: Criar script de validação**

```python
#!/usr/bin/env python3
"""Validate dataset quality."""

import json
import os
from pathlib import Path
from collections import defaultdict

def validate_dataset(dataset_path):
    results = {
        "total_categories": 0,
        "total_examples": 0,
        "intents": defaultdict(lambda: {"unique": 0, "total": 0}),
        "issues": []
    }
    
    for fname in os.listdir(dataset_path):
        if not fname.endswith('.jsonl'):
            continue
            
        results["total_categories"] += 1
        filepath = os.path.join(dataset_path, fname)
        
        unique_responses = defaultdict(set)
        
        with open(filepath) as f:
            for line_num, line in enumerate(f, 1):
                try:
                    d = json.loads(line)
                    results["total_examples"] += 1
                    
                    intent = d.get('metadata', {}).get('intent', 'unknown')
                    content = d['messages'][-1]['content']
                    
                    unique_responses[intent].add(content)
                    results["intents"][intent]["total"] += 1
                    
                    # Check for issues
                    if len(content) < 100:
                        results["issues"].append(f"{fname}:{line_num} - resposta muito curta")
                    
                except json.JSONDecodeError as e:
                    results["issues"].append(f"{fname}:{line_num} - JSON inválido: {e}")
        
        # Count unique per intent
        for intent, contents in unique_responses.items():
            results["intents"][intent]["unique"] += len(contents)
    
    return results

if __name__ == "__main__":
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else "data/curated_v6"
    results = validate_dataset(path)
    
    print(f"\n=== Dataset Quality Report ===")
    print(f"Categorias: {results['total_categories']}")
    print(f"Exemplos: {results['total_examples']}")
    print(f"\nIntent Coverage:")
    for intent, stats in results['intents'].items():
        ratio = stats['unique'] / stats['total'] * 100 if stats['total'] > 0 else 0
        print(f"  {intent}: {stats['unique']} unique / {stats['total']} total ({ratio:.1f}%)")
    
    if results['issues']:
        print(f"\n⚠️ Issues: {len(results['issues'])}")
        for issue in results['issues'][:10]:
            print(f"  - {issue}")
    else:
        print(f"\n✅ Sem issues encontrados")
```

- [ ] **Step 2: Executar validação**

```bash
python3 scripts/validate_dataset.py data/curated_v6
```

Expected output:
- update unique >= 10
- manage unique >= 10
- Todas as categorias com CLI commands

- [ ] **Step 3: Commit**

```bash
git add scripts/validate_dataset.py
git commit -m "scripts: add dataset validation tool"
```

---

## Chunk 4: Verificação de todas as categorias

### Task 7: Verificar categorias individuais

**Files:**
- Run: `scripts/validate_dataset.py` com análise por categoria

- [ ] **Step 1: Executar verificação por categoria**

```python
# Add to validation script
def check_category_diversity(filepath):
    with open(filepath) as f:
        intents = defaultdict(list)
        for line in f:
            d = json.loads(line)
            intent = d.get('metadata', {}).get('intent', 'unknown')
            content = d['messages'][-1]['content'][:50]  # First 50 chars as fingerprint
            intents[intent].append(content)
    
    results = {}
    for intent, fingerprints in intents.items():
        unique = len(set(fingerprints))
        total = len(fingerprints)
        results[intent] = {"unique": unique, "total": total, "ratio": unique/total if total > 0 else 0}
    
    return results

# Run for each category
for cat in categories:
    filepath = f"data/curated_v6/{cat}.jsonl"
    results = check_category_diversity(filepath)
    if any(r["ratio"] < 0.3 for r in results.values()):
        print(f"❌ {cat}: {results}")
```

- [ ] **Step 2: Documentar resultados**

Salvar em `docs/dataset-category-report.md`

- [ ] **Step 3: Corrigir categorias com problemas**

Se alguma categoria tiver < 30% unique responses, adicionar mais templates específicos para ela.

- [ ] **Step 4: Commit**

```bash
git add docs/dataset-category-report.md
git commit -m "docs: add per-category quality report"
```

---

## Summary

| Task | Description | Files |
|------|-------------|-------|
| 1 | Analisar duplicação | scripts + docs |
| 2 | Adicionar CLI para update/manage | scripts/generate_v5_combined.py |
| 3 | Adicionar variação contextual | scripts/generate_v5_combined.py |
| 4 | Aumentar diversidade de templates | scripts/generate_v5_combined.py |
| 5 | Regenerar dataset | data/curated_v6/ |
| 6 | Validar qualidade | scripts/validate_dataset.py |
| 7 | Verificar categorias | docs/ |

**Dependencies:**
- Task 1 → Task 2 (know what to fix)
- Task 2 → Task 3 (add commands before variation)
- Task 3 → Task 4 (variation before diversity)
- Task 4 → Task 5 (regenerate with all fixes)
- Task 5 → Task 6 (validate new dataset)
- Task 6 → Task 7 (verify all categories)

**Estimated Time:**
- Chunk 1: 15 min
- Chunk 2: 45 min
- Chunk 3: 20 min
- Chunk 4: 15 min
- **Total: ~95 min**