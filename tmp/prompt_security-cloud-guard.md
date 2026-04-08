# OCI Dataset Generation - security/cloud-guard

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

## TOPIC: security/cloud-guard

#### security/cloud-guard (140)
- Cloud Guard configuration
- Detector recipes
- Responder rules
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/CloudGuard/concepts/cloudguardoverview.htm


---

## SYSTEM PROMPT (para usar no JSONL)

You are an OCI specialist with expertise in Cloud Guard. Provide technical guidance on configuration, detector recipes, and responder rules.

---

## DIVERSITY REQUIREMENTS (OBRIGATÓRIO)

Varie os exemplos entre:
- Diferentes serviços de segurança (IAM, Vault, Cloud Guard, WAF)
- Diferentes cenários (access control, encryption, threat detection)
- Diferentes personas (security engineer, admin, auditor)
- Diferentes problemas (permission denied, key rotation, false positives)


---

## OCI CLI Syntax

### Cloud Guard Configuration

```bash
# Enable Cloud Guard
oci cloud-guard cloud-guard-cli-service summarize-tenancy-status \
  --registry-credential-id ocid1.credential.oc1..<unique-id>

# Create Cloud Guard configuration
oci cloud-guard configuration create-or-update --compartment-id ocid1.compartment.oc1..<unique-id> \
  --status ENABLED \
  --detector-recipe-id ocid1.detectorrecipe.oc1..<unique-id> \
  --responder-recipe-id ocid1.responderrecipe.oc1..<unique-id>

# Get configuration
oci cloud-guard configuration get --compartment-id ocid1.compartment.oc1..<unique-id>
```

### Target Management

```bash
# Create target (scope for Cloud Guard)
oci cloud-guard target create --compartment-id ocid1.compartment.oc1..<unique-id> \
  --display-name ProductionTargets \
  --target-resource-type COMPARTMENT \
  --target-resource-id ocid1.compartment.oc1..<unique-id> \
  --detector-recipe-id ocid1.detectorrecipe.oc1..<unique-id> \
  --responder-recipe-id ocid1.responderrecipe.oc1..<unique-id>

# List targets
oci cloud-guard target list --compartment-id ocid1.compartment.oc1..<unique-id>

# Update target
oci cloud-guard target update --target-id ocid1.target.oc1..<unique-id> \
  --display-name UpdatedTargets
```

### Detector Recipes

```bash
# List detector recipes
oci cloud-guard detector-recipe list --compartment-id ocid1.compartment.oc1..<unique-id>

# Create custom detector recipe
oci cloud-guard detector-recipe create --compartment-id ocid1.compartment.oc1..<unique-id> \
  --display-name CustomSecurityRecipe \
  --detector-rules '[{"detectorRuleId": "rule-id", "enabled": true, "riskLevel": "HIGH"}]'

# Get detector recipe details
oci cloud-guard detector-recipe get --detector-recipe-id ocid1.detectorrecipe.oc1..<unique-id>
```

### Responder Rules

```bash
# List responder recipes
oci cloud-guard responder-recipe list --compartment-id ocid1.compartment.oc1..<unique-id>

# Create custom responder rule
oci cloud-guard responder-rule create --compartment-id ocid1.compartment.oc1..<unique-id> \
  --display-name AutoRemediateS3 \
  --type AUTO_ACTER \
  --condition "problem[0].severity == HIGH" \
  --action "[{\"script\": \"remediate.sh\"}]"

# Enable responder
oci cloud-guard responder-rule update --responder-rule-id ocid1.responderrule.oc1..<unique-id> \
  --enabled true
```

### Security Findings

```bash
# List security findings
oci cloud-guard problem list --compartment-id ocid1.compartment.oc1..<unique-id> \
  --lifecycle-state ACTIVE

# Get finding details
oci cloud-guard problem get --problem-id ocid1.problem.oc1..<unique-id>

# Dismiss finding
oci cloud-guard problem update --problem-id ocid1.problem.oc1..<unique-id> \
  --lifecycle-state RESOLVED

# Get security score
oci cloud-guard security-score list-summaries --compartment-id ocid1.compartment.oc1..<unique-id>
```


## Anti-Patterns (Never generate)

1. ❌ Enable Cloud Guard without explaining it requires admin privileges in root compartment
2. ❌ Create targets without understanding scoping (can scan entire tenancy or specific compartments)
3. ❌ Use placeholder OCIDs: `ocid1.cloudguard.<region>.<id>` - correct is `ocid1.target.oc1..<unique-id>`
4. ❌ Enable all detector rules without testing (some may cause false positives)
5. ❌ Configure auto-responders without testing in non-production first
6. ❌ Ignore security score - it aggregates all findings [MUTABLE: recalculates every 24 hours]
7. ❌ Claim Cloud Guard replaces manual security audits
8. ❌ Enable responders without understanding the actions they perform
9. ❌ Mix up detector recipes vs responder recipes (detection vs action)
10. ❌ Forget that Cloud Guard findings can trigger events to other services
11. ❌ Configure targets on wrong compartment level
12. ❌ Dismiss findings without actual remediation



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
2. Gere APENAS exemplos para o topic "security/cloud-guard"
3. Use APENAS as informações presentes em "TOPIC: security/cloud-guard"
4. Não invente informações que não estão nos docs OCI
5. Não use preços ou limites sem marcar [MUTABLE] ou [CHECK DOCS]
6. Cada exemplo DEVE ter um cenário diferente - NÃO repita o mesmo caso de uso
7. Varie os contextos: diferentes personas, diferentes níveis de complexidade, diferentes casos de uso reais

---

## OUTPUT FORMAT

Gere EXATAMENTE 140 exemplos em formato JSONL.

**UM objeto JSON por linha** - cada linha é um objeto JSON completo.

```
{"messages": [...], "metadata": {"category": "security/cloud-guard", "difficulty": "beginner|intermediate|advanced", "source": "generated"}}
{"messages": [...], "metadata": {"category": "security/cloud-guard", "difficulty": "beginner|intermediate|advanced", "source": "generated"}}
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

Gere EXATAMENTE 140 exemplos diversos para o topic: **security/cloud-guard**

- Mistura de dificuldades: 42 beginner, 70 intermediate, 28 advanced
- Cenários reais de OCI - cada exemplo com um caso de uso diferente
- Use Português (BR) para perguntas do usuário
- Formato JSONL, uma linha por exemplo
- SIGA TODAS as regras de qualidade acima
- NÃO repita cenários - cada exemplo deve ser único
