# OCI Dataset Generation - observability/logging

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

## TOPIC: observability/logging

#### observability/logging (140)
- Logging service
- Log groups, custom logs
- Retention, audit
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Logging/overview.htm


---

## SYSTEM PROMPT (para usar no JSONL)

You are an OCI specialist with expertise in Logging. Provide technical guidance on log groups, custom logs, retention, and audit.

---

## DIVERSITY REQUIREMENTS (OBRIGATÓRIO)

Varie os exemplos entre:
- Diferentes serviços (logging, monitoring, APM, stack monitoring)
- Diferentes cenários (alerting, dashboards, troubleshooting)
- Diferentes personas (SRE, DevOps, developer)
- Diferentes problemas (missing metrics, log retention, trace correlation)


---

## OCI CLI Syntax

### Log Group Commands

```bash
# Create log group
oci logging log-group create --compartment-id <ocid> \
  --display-name "app-logs-group" \
  --description "Application logs for production"

# List log groups
oci logging log-group list --compartment-id <ocid>

# Get log group
oci logging log-group get --log-group-id <ocid1.loggroup.oc1.<region>.<unique-id>>
```

### Log Commands

```bash
# Enable log
oci logging log create --log-group-id <ocid1.loggroup.oc1.<region>.<unique-id>> \
  --display-name "app-access-log" \
  --log-source-id <ocid1.instance.oc1.<region>.<unique-id>> \
  --log-type JSON

# List logs in group
oci logging log list --log-group-id <ocid1.loggroup.oc1.<region>.<unique-id>>

# Disable log
oci logging log delete --log-id <ocid1.log.oc1.<region>.<unique-id>>
```

### Log Search

```bash
# Search logs (using logs-query)
oci logging log-search search \
  --log-group-id <ocid1.loggroup.oc1.<region>.<unique-id>> \
  --time-start "2024-01-01T00:00:00Z" \
  --time-end "2024-01-02T00:00:00Z" \
  --search-query "message LIKE '%ERROR%'"
```

### Retention Management

```bash
# Update log retention (minimum 7 days, maximum 365 days)
oci logging log update --log-id <ocid1.log.oc1.<region>.<unique-id>> \
  --retention-duration-days 30
```


## Anti-Patterns

- NEVER create logs without specifying a log group
- NEVER use real OCIDs — always use placeholders like `<ocid1.loggroup.oc1.<region>.<unique-id>>`
- NEVER omit `--compartment-id` — required for all operations
- NEVER set retention below 7 days or above 365 days
- NEVER copy OCI documentation verbatim — generate original examples
- NEVER skip enabling logs — disabled logs don't collect data
- NEVER use vague log names — use descriptive names like "prod-api-access-log"
- NEVER omit `--log-type` when creating logs — JSON or SYSLOG required
- NEVER query logs without time filters — always specify start/end time
- NEVER generate logs without retention policies — always specify retention duration



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
2. Gere APENAS exemplos para o topic "observability/logging"
3. Use APENAS as informações presentes em "TOPIC: observability/logging"
4. Não invente informações que não estão nos docs OCI
5. Não use preços ou limites sem marcar [MUTABLE] ou [CHECK DOCS]
6. Cada exemplo DEVE ter um cenário diferente - NÃO repita o mesmo caso de uso
7. Varie os contextos: diferentes personas, diferentes níveis de complexidade, diferentes casos de uso reais

---

## OUTPUT FORMAT

Gere EXATAMENTE 140 exemplos em formato JSONL.

**UM objeto JSON por linha** - cada linha é um objeto JSON completo.

```
{"messages": [...], "metadata": {"category": "observability/logging", "difficulty": "beginner|intermediate|advanced", "source": "generated"}}
{"messages": [...], "metadata": {"category": "observability/logging", "difficulty": "beginner|intermediate|advanced", "source": "generated"}}
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

Gere EXATAMENTE 140 exemplos diversos para o topic: **observability/logging**

- Mistura de dificuldades: 42 beginner, 70 intermediate, 28 advanced
- Cenários reais de OCI - cada exemplo com um caso de uso diferente
- Use Português (BR) para perguntas do usuário
- Formato JSONL, uma linha por exemplo
- SIGA TODAS as regras de qualidade acima
- NÃO repita cenários - cada exemplo deve ser único
