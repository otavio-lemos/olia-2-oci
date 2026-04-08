# OCI Dataset Generation - devops/resource-manager

## QUALITY RULES (OBRIGATÓRIO - SIGA À RISCA)

# OCI Specialist LLM - Quality Rules

## Dataset Quality Rules (Rigid)

### Prohibited Content

1. **NEVER copy OCI documentation verbatim**
   - Paraphrase in your own words
   - Reorganize information structure
   - Add original examples

2. **NEVER invent non-existent Oracle services**
   - Only include real OCI services
   - Verify service names from official docs
   - No "OCI Magic Service" or similar

3. **NEVER use prices without marking as mutable**
   - Prices change frequently
   - Use: "As of 2024, pricing is approximately X" or [MUTABLE]
   - Never quote exact current prices

4. **NEVER use limits/quotas without marking**
   - Limits vary by region and tenancy
   - Use: "Check your specific limits in the console" or [CHECK DOCS]

5. **NEVER create vague examples**
   - Bad: "Use best practices for security"
   - Good: "Enable MFA for all users, use IAM groups for access control"

6. **NEVER skip steps in procedural answers**
   - Include all necessary steps
   - Explain prerequisite configurations

7. **NEVER skip risks/justifications in architecture**
   - Every architectural choice has trade-offs
   - Explain why the recommendation makes sense

### Required Content

1. **Always provide specific OCI resource names**
   - Use actual OCI resource identifiers
   - Reference correct service names

2. **Always mark mutable content**
   - [MUTABLE] for prices, limits, quotas
   - [CHECK DOCS] for version-dependent info

3. **Always use accurate OCI terminology**
   - Compartment, not "folder"
   - VCN, not "virtual network" (define on first use)
   - Policy, not "permission"
   - OKE (Oracle Kubernetes Engine), not "Kubernetes OCI"

4. **Always include multi-cloud context when relevant**
   - AWS/Azure/GCP equivalent concepts
   - Migration mapping guidance

5. **Always include documentation references**
   - Reference official OCI docs when relevant
   - Include doc links: https://docs.oracle.com/en-us/iaas/Content/...

### Response Templates

#### Good Response Example (Compute)
```
Para criar uma instância no OCI:

1. No Console, vá para Compute → Instances
2. Clique em "Create Instance"
3. Selecione o compartment desejado
4. Escolha o shape (VM.Standard2.4 para propósito geral)
5. Configure a subnet (pública ou privada)
6. Adicione SSH keys
7. Clique em "Create"

Shape recomendado:
- VM.Standard2.4: propósito geral
- VM.Standard.E4: AMD EPYC (custo-benefício)
- VM.Optimized3: memória otimizada
- VM.Standard.A1: ARM (Ampere A1, econômico)

Nota: [MUTABLE] Preços variam por região e shape.
```

#### Bad Response Example (Compute)
```
Para criar uma instância no OCI, basta usar o console e escolher
um shape bom. Use práticas recomendadas de segurança.
```

### Validation Checklist

- No copied documentation sentences
- No made-up services
- Prices marked as mutable or removed
- Limits marked to verify in console
- Answers have specific steps
- Architecture answers include trade-offs
- All OCI terms are correct
- Documentation references included when relevant

### Deduplication Rules

- Exact duplicate: remove one copy
- Near-duplicate (>90% similarity): merge or keep best
- Same question, different category: **NOT duplicate** - keep both
- Same question, same category: keep only one

### Category Detection

When generating examples, detect category from:
- `data/curated/[category]-[nnn].jsonl` filename
- Or metadata.category field

Example categories:
- oci-core/compute, oci-core/storage, oci-core/networking, oci-core/database
- oci-security/iam, oci-security/vault, oci-security/encryption
- oci-migration/aws-to-oci, oci-migration/azure-to-oci, oci-migration/gcp-to-oci
- oci-terraform/provider, oci-terraform/resources
- oci-troubleshooting/connectivity, oci-troubleshooting/performance


---

## TOPIC: devops/resource-manager

#### devops/resource-manager (140)
- Stack creation from Terraform configurations
- Job execution and monitoring
- Drift detection and remediation
- State management and versioning
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/ResourceManager/Con/resourcemanager.htm


---

## SYSTEM PROMPT (para usar no JSONL)

You are an OCI DevOps specialist with expertise in Resource Manager. Provide technical guidance on stacks, jobs, drift detection, and state management.

---

## DIVERSITY REQUIREMENTS (OBRIGATÓRIO)

Varie os exemplos entre:
- Diferentes serviços (CI/CD, Resource Manager, Artifacts, Secrets)
- Diferentes cenários (greenfield, migration, optimization)
- Diferentes personas (DevOps engineer, developer, platform engineer)
- Diferentes problemas (pipeline failures, state drift, artifact management)


---

## OCI CLI Syntax

### Stack Management
```bash
# Create stack from Terraform template
oci resource-manager stack create \
  --compartment-id ocid1.compartment.oc1..aaaaaaaab222... \
  --config-source "TEMPLATE" \
  --description "Stack description" \
  --display-name "my-stack" \
  --terraform-version "1.9.0" \
  --region us-sao-1

# Get stack OCID
oci resource-manager stack list \
  --compartment-id ocid1.compartment.oc1..aaaaaaaab222... \
  --display-name "my-stack" \
  --lifecycle-state ACTIVE \
  --region us-sao-1

# Update stack configuration
oci resource-manager stack update \
  --stack-id ocid1.resourcemanagerstack.oc1.sa-saopaulo-1.aaaaaaaab222... \
  --description "Updated description"

# Delete stack
oci resource-manager stack delete \
  --stack-id ocid1.resourcemanagerstack.oc1.sa-saopaulo-1.aaaaaaaab222... \
  --force
```

### Job Execution
```bash
# Plan job (preview changes)
oci resource-manager job create \
  --stack-id ocid1.resourcemanagerstack.oc1.sa-saopaulo-1.aaaaaaaab222... \
  --operation-name PLAN \
  --display-name "my-plan-job"

# Apply job (execute changes)
oci resource-manager job create \
  --stack-id ocid1.resourcemanagerstack.oc1.sa-saopaulo-1.aaaaaaaab222... \
  --operation-name APPLY \
  --display-name "my-apply-job" \
  --apply-redirected-actions true

# Destroy job (teardown resources)
oci resource-manager job create \
  --stack-id ocid1.resourcemanagerstack.oc1.sa-saopaulo-1.aaaaaaaab222... \
  --operation-name DESTROY \
  --display-name "my-destroy-job"

# Import Terraform state
oci resource-manager job create \
  --stack-id ocid1.resourcemanagerstack.oc1.sa-saopaulo-1.aaaaaaaab222... \
  --operation-name IMPORT_STATE \
  --display-name "import-state-job"

# Get job details
oci resource-manager job get \
  --job-id ocid1.resourcemanagerjob.oc1.sa-saopaulo-1.ccccccc3333...

# List jobs for stack
oci resource-manager job list \
  --stack-id ocid1.resourcemanagerstack.oc1.sa-saopaulo-1.aaaaaaaab222... \
  --region us-sao-1
```

### Drift Detection
```bash
# Check drift
oci resource-manager drift detect \
  --stack-id ocid1.resourcemanagerstack.oc1.sa-saopaulo-1.aaaaaaaab222... \
  --drift-detection-delay-duration "10m"

# Get drift status
oci resource-manager drift get \
  --stack-id ocid1.resourcemanagerstack.oc1.sa-saopaulo-1.aaaaaaaab222...

# List drift resources
oci resource-manager drift list-resources \
  --stack-id ocid1.resourcemanagerstack.oc1.sa-saopaulo-1.aaaaaaaab222... \
  --drift-status DETECTED
```

### State Management
```bash
# Get TF state
oci resource-manager state get \
  --stack-id ocid1.resourcemanagerstack.oc1.sa-saopaulo-1.aaaaaaaab222... \
  --query "state"

# Lock state
oci resource-manager state lock \
  --stack-id ocid1.resourcemanagerstack.oc1.sa-saopaulo-1.aaaaaaaab222...

# Unlock state
oci resource-manager state unlock \
  --stack-id ocid1.resourcemanagerstack.oc1.sa-saopaulo-1.aaaaaaaab222... \
  --lock-id ocid1.resourcelock.oc1.sa-saopaulo-1.lock111...
```


## Anti-Patterns

NEVER generate examples that:
- Use fake OCIDs like `ocid1.stack.oc1...` without the full resource type prefix
- Reference non-existent commands like `oci rm stack create`
- Suggest using the Console as the only method (CLI/SDK are valid alternatives)
- Copy OCI documentation verbatim
- Invent Terraform providers that don't exist in OCI Provider
- Mix stack OCIDs with job OCIDs (wrong resource type prefix)
- Use region codes like `sao1` instead of `sa-saopaulo-1`
- Suggest bypassing drift detection for "simpler" workflows
- Claim Resource Manager supports state storage outside OCI
- Invent "auto-apply" features without mentioning approval workflows



## Universal Anti-Patterns (Always Include)

1. ❌ Copiar documentação OCI literalmente
2. ❌ Inventar serviços Oracle inexistentes
3. ❌ Usar preços ou limites sem marcar [MUTABLE]
4. ❌ Criar exemplos vagos como "use best practices"
5. ❌ Respostas arquiteturais sem steps, risks, justification
6. ❌ OCID fictícios sem formato válido
7. ❌ Comandos CLI inventados



## Universal OCID Format Reference

```
ocid1.<resource>.<realm>.<region>.<unique-id>
ocid1.instance.oc1.iad.abcd1234...
ocid1.compartment.oc1..aaaa2222...
ocid1.user.oc1.iad.bbbb3333...
ocid1.group.oc1.iad.cccc4444...
ocid1.tenancy.oc1..dddd5555...
```


---

## SUAS REGRAS DE EXECUÇÃO

1. Você DEVE seguir OBRIGATORIAMENTE todas as regras em "QUALITY RULES" acima
2. Gere APENAS exemplos para o topic "devops/resource-manager"
3. Use APENAS as informações presentes em "TOPIC: devops/resource-manager"
4. Não invente informações que não estão nos docs OCI
5. Não use preços ou limites sem marcar [MUTABLE] ou [CHECK DOCS]
6. Cada exemplo DEVE ter um cenário diferente - NÃO repita o mesmo caso de uso
7. Varie os contextos: diferentes personas, diferentes níveis de complexidade, diferentes casos de uso reais

---

## OUTPUT FORMAT

Gere EXATAMENTE 140 exemplos em formato JSONL.

**UM objeto JSON por linha** - cada linha é um objeto JSON completo.

```
{"messages": [...], "metadata": {"category": "devops/resource-manager", "difficulty": "beginner|intermediate|advanced", "source": "generated"}}
{"messages": [...], "metadata": {"category": "devops/resource-manager", "difficulty": "beginner|intermediate|advanced", "source": "generated"}}
... (140 linhas total)
```

---

## JSONL RULES (CRÍTICO - SIGA EXATAMENTE)

1. **UM objeto JSON por linha** - sem arrays, sem wrapper, sem markdown
2. **Escape todas as aspas dentro de strings**: " (aspas) → \" (backslash aspas)
3. **Escape newlines dentro de strings**: quebra de linha → \n
4. **Escape backslashes**: \ (backslash) → \\
5. **metadata é OBRIGATÓRIO** em cada objeto
6. **metadata deve ficar FORA do array messages!**

**ESTRUTURA CORRETA (faça exatamente assim!):**
```json
{"messages": [
  {"role": "system", "content": "..."},
  {"role": "user", "content": "..."},
  {"role": "assistant", "content": "..."}
], "metadata": {"category": "...", "difficulty": "...", "source": "generated"}}
```

**ESTRUTURA ERRADA (NUNCA faça assim!):**
```json
{"messages": [
  {"role": "system", "content": "..."},
  {"role": "user", "content": "..."},
  {"role": "assistant", "content": "..."},
  {"metadata": {"category": "..."}}
]}
```

⚠️ **ATENÇÃO**: O metadata DEVE ficar na mesma linha que o messages, como um sibling key, NUNCA dentro do array messages!

---

## DISTRIBUIÇÃO DE DIFICULDADE
- beginner: ~30% dos exemplos (42 exemplos)
- intermediate: ~50% dos exemplos (70 exemplos)
- advanced: ~20% dos exemplos (28 exemplos)

---

## EXEMPLO DE FORMATO DE RESPOSTA

```json
{"messages": [
  {"role": "system", "content": "You are an OCI specialist..."},
  {"role": "user", "content": "Como configurar..."},
  {"role": "assistant", "content": "Para configurar...\n\n1. Step one\n2. Step two\n\n[MUTABLE] Note about prices."}
], "metadata": {"category": "example/topic", "difficulty": "intermediate", "source": "generated"}}
```

⚠️ **ERRO COMUM**: O metadata deve ficar FORA do array messages, não dentro!

---

## SUA TAREFA

Gere EXATAMENTE 140 exemplos diversos para o topic: **devops/resource-manager**

- Mistura de dificuldades: 42 beginner, 70 intermediate, 28 advanced
- Cenários reais de OCI - cada exemplo com um caso de uso diferente
- Use Português (BR) para perguntas do usuário
- Formato JSONL, uma linha por exemplo
- SIGA TODAS as regras de qualidade acima
- NÃO repita cenários - cada exemplo deve ser único
