# OCI Dataset Generation - devops/secrets

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

## TOPIC: devops/secrets

#### devops/secrets (140)
- Vault secret creation and management
- Pipeline secret injection
- Parameter store configuration
- Secret rotation and lifecycle
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/KeyManagement/Concepts/keyoverview.htm


---

## SYSTEM PROMPT (para usar no JSONL)

You are an OCI DevOps specialist with expertise in secrets management. Provide technical guidance on Vault secrets, pipeline injection, and rotation.

---

## DIVERSITY REQUIREMENTS (OBRIGATÓRIO)

Varie os exemplos entre:
- Diferentes serviços (CI/CD, Resource Manager, Artifacts, Secrets)
- Diferentes cenários (greenfield, migration, optimization)
- Diferentes personas (DevOps engineer, developer, platform engineer)
- Diferentes problemas (pipeline failures, state drift, artifact management)


---

## OCI CLI Syntax

### Vault Operations
```bash
# Create vault
oci vault vault create \
  --compartment-id ocid1.compartment.oc1..aaaaaaaab222... \
  --display-name "devops-vault" \
  --vault-type DEFAULT \
  --region us-sao-1

# List vaults
oci vault vault list \
  --compartment-id ocid1.compartment.oc1..aaaaaaaab222... \
  --lifecycle-state ACTIVE

# Get vault OCID
oci vault vault get \
  --vault-id ocid1.vault.oc1.sa-saopaulo-1.vvvvvv...
```

### Secret Management
```bash
# Create secret
oci vault secret create \
  --vault-id ocid1.vault.oc1.sa-saopaulo-1.vvvvvv... \
  --secret-name "db-password" \
  --secret-content " encrypted-content-here " \
  --secret-content-type BASE64 \
  --description "Database password for app" \
  --region us-sao-1

# Get secret OCID
oci vault secret list \
  --vault-id ocid1.vault.oc1.sa-saopaulo-1.vvvvvv... \
  --lifecycle-state ACTIVE

# Get secret value (requires read permission)
oci vault secret get-content \
  --secret-id ocid1.secret.oc1.sa-saopaulo-1.ssssss... \
  --region us-sao-1

# Update secret (new version)
oci vault secret update \
  --secret-id ocid1.secret.oc1.sa-saopaulo-1.ssssss... \
  --secret-content "new-encrypted-content" \
  --region us-sao-1

# Rotate secret
oci vault secret rotate \
  --secret-id ocid1.secret.oc1.sa-saopaulo-1.ssssss... \
  --secret-content "new-version-content" \
  --region us-sao-1
```

### Secrets in DevOps Pipeline
```bash
# Create DevOps secret (wraps Vault)
oci devops artifact create \
  --project-id ocid1.devopsproject.oc1.sa-saopaulo-1.aaaaaaaab222... \
  --display-name "db-password" \
  --artifact-type OCI_VAULT_SECRET \
  --artifact-ocid ocid1.secret.oc1.sa-saopaulo-1.ssssss... \
  --region us-sao-1

# Add as environment variable in deploy stage
# Via OCI Console UI - cannot set via CLI
# Add to deploy pipeline stage configuration:
# ${oci://vault://secret://ocid1.secret.oc1.sa-saopaulo-1.ssssss.@@}

# List secrets in DevOps
oci devops artifact list \
  --project-id ocid1.devopsproject.oc1.sa-saopaulo-1.aaaaaaaab222... \
  --artifact-type OCI_VAULT_SECRET
```

### Key Management
```bash
# Create key
oci vault key create \
  --vault-id ocid1.vault.oc1.sa-saopaulo-1.vvvvvv... \
  --display-name "signing-key" \
  --key-version-reference "1" \
  --region us-sao-1

# List keys
oci vault key list \
  --vault-id ocid1.vault.oc1.sa-saopaulo-1.vvvvvv... \
  --lifecycle-state ACTIVE

# Rotate key
oci vault key rotate \
  --key-id ocid1.key.oc1.sa-saopaulo-1.kkkkkk... \
  --key-version-reference "2" \
  --region us-sao-1
```

### Dynamic Group for Access
```bash
# Get dynamic group OCID
oci iam dynamic-group get \
  --dynamic-group-id ocid1.dynamicgroup.oc1.sa-saopaulo-1.dddddd...

# List dynamic groups
oci iam dynamic-group list \
  --compartment-id ocid1.compartment.oc1..aaaaaaaab222...
```


## Anti-Patterns

NEVER generate examples that:
- Use fake OCIDs like `ocid1.key.oc1...` without full resource type prefix
- Use Vault secrets directly without dynamic groups/policies
- Suggest putting secrets in pipeline environment variables directly
- Copy secret values in plain text in logs or outputs
- Reference AWS Secrets Manager or Azure Key Vault in OCI context
- Use API key as secret type in OCI Vault
- Suggest "reading from env vars" without Vault integration
- Create policies without mentioning compartment scope
- Mix up Key OCID with Secret OCID
- Suggest key rotation without version management



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
2. Gere APENAS exemplos para o topic "devops/secrets"
3. Use APENAS as informações presentes em "TOPIC: devops/secrets"
4. Não invente informações que não estão nos docs OCI
5. Não use preços ou limites sem marcar [MUTABLE] ou [CHECK DOCS]
6. Cada exemplo DEVE ter um cenário diferente - NÃO repita o mesmo caso de uso
7. Varie os contextos: diferentes personas, diferentes níveis de complexidade, diferentes casos de uso reais

---

## OUTPUT FORMAT

Gere EXATAMENTE 140 exemplos em formato JSONL.

**UM objeto JSON por linha** - cada linha é um objeto JSON completo.

```
{"messages": [...], "metadata": {"category": "devops/secrets", "difficulty": "beginner|intermediate|advanced", "source": "generated"}}
{"messages": [...], "metadata": {"category": "devops/secrets", "difficulty": "beginner|intermediate|advanced", "source": "generated"}}
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

Gere EXATAMENTE 140 exemplos diversos para o topic: **devops/secrets**

- Mistura de dificuldades: 42 beginner, 70 intermediate, 28 advanced
- Cenários reais de OCI - cada exemplo com um caso de uso diferente
- Use Português (BR) para perguntas do usuário
- Formato JSONL, uma linha por exemplo
- SIGA TODAS as regras de qualidade acima
- NÃO repita cenários - cada exemplo deve ser único
