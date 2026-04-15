#!/usr/bin/env python3
import json

examples = []

topics = [
    ("Vault", "create", "beginner"),
    ("Secret", "list", "beginner"),
    ("Secret", "get", "beginner"),
    ("Secret", "update", "intermediate"),
    ("Secret", "delete", "intermediate"),
    ("Secret", "rotate", "intermediate"),
    ("Secret", "version", "intermediate"),
    ("Secret", "restore", "advanced"),
    ("Vault", "policy", "intermediate"),
    ("Secret", "inject", "intermediate"),
    ("Secret", "oci-cli", "intermediate"),
    ("Secret", "terraform", "advanced"),
    ("Secret", "rotation-policy", "advanced"),
    ("Secret", "monitoring", "beginner"),
    ("Secret", "troubleshoot", "intermediate"),
]

companies = [
    "TechCorp Brasil",
    "DataFlow Solutions",
    "CloudNative Inc",
    "FinServe Digital",
    "RetailMax Online",
    "HealthTech Systems",
    "EduPlatform Global",
    "LogiTrack Logistics",
    "MediaStream Pro",
    "AgriTech Innovations",
    "SecureBank Corp",
    "TravelHub Platform",
    "SmartCity IoT",
    "GameForge Studios",
    "BioResearch Labs",
    "AutoDrive Systems",
    "EnergyGrid Monitor",
    "FoodChain Trace",
    "LegalDoc Manager",
    "InsureTech Plus",
]

regions = [
    "sa-saopaulo-1",
    "us-ashburn-1",
    "eu-frankfurt-1",
    "uk-london-1",
    "ap-tokyo-1",
    "ap-sydney-1",
    "us-phoenix-1",
    "ap-mumbai-1",
    "ca-toronto-1",
    "me-jeddah-1",
]

personas = [
    "cloud architect",
    "platform engineer",
    "sre",
    "devops engineer",
    "security lead",
    "dba",
    "finops analyst",
    "auditor",
]

intents = [
    "design",
    "standardize",
    "troubleshoot",
    "optimize",
    "migrate",
    "audit",
    "compare",
    "recover",
    "remediate",
]

lifecycles = [
    "greenfield",
    "brownfield",
    "produção estável",
    "expansão",
    "incidente",
    "auditoria",
    "desativação",
]

constraints = [
    "sem downtime",
    "sem IP público",
    "com budget limitado",
    "com auditoria em 30 dias",
    "ambiente legado",
    "equipe enxuta",
    "mínimo privilégio",
    "multi-região",
    "rollback em menos de 15 minutos",
]


def generate_question(topic, action, company, region, constraint, lifecycle, persona):
    scenarios = {
        "create": f"Sou {persona} na {company} e preciso criar um secret no Vault para o projeto {topic.lower()}-project, em production/{region}. {constraint}. Qual abordagem você recomenda?",
        "list": f"Como {persona}, preciso listar todos os secrets do compartment devops na {region} para auditing. Qual comando uso?",
        "get": f"No ambiente {lifecycle} da {company}, qual é a melhor forma de recuperar um secret em {region} quando o objetivo é {action}?",
        "update": f"Como {persona}, preciso atualizar o valor de um secret Rotate-me no Vault da {region}. Como fazer isso via CLI?",
        "delete": f"Estamos em cenário de {lifecycle} e eu atuo como {persona}. Como agendar a deleção de um secret em {region} sem perder de vista compliance?",
        "rotate": f"Como {persona}, preciso configurar rotação automática para secrets de API keys na {company}. Quais os passos no OCI Vault?",
        "version": f"Preciso gerenciar múltiplas versões de secrets no Vault. Como versionar e restaurar uma versão anterior na {region}?",
        "restore": f"Um secret foi deletado acidentalmente. Como {persona}, preciso restaurar a versão anterior do secret na {region}. É possível?",
        "policy": f"Quais IAM policies preciso criar para que uma função OCI possa acessar secrets no compartment production da {region}?",
        "inject": f"No pipeline CI/CD da {company}, como injetar secrets do Vault em containers sem expon-los em variáveis de ambiente?",
        "oci-cli": f"Provide OCI CLI commands para gerenciar secrets via linha de comando na {region}. Quais os principais?",
        "terraform": f"Como gerenciar secrets via Terraform na {company} para o projeto {topic.lower()}-infra? Qual provider usar?",
        "rotation-policy": f"Qual a política de rotação recomendada para secrets de banco de dados em produção na {region}?",
        "monitoring": f"Como monitorar accessos a secrets no Vault da {region}? Preciso auditar quem acessou cada secret.",
        "troubleshoot": f"O minhas instâncias não conseguem ler secrets do Vault. Erro de permission denied. Como diagnosticar na {region}?",
    }
    return scenarios.get(
        action,
        f"Como {persona}, gerenciar secrets para {company} no projeto em {region}?",
    )


def generate_answer(action, topic, company, region, constraint, lifecycle, persona):
    answers = {
        "create": f"""Para criar um secret no OCI Vault via Console:

1. Vá em **Identity & Security** → **Vault**.
2. Selecione o Vault existente ou crie um novo (escolha 'Virtual Private' para maior segurança).
3. Clique em **Secrets** → **Create Secret**.
4. **Nome**: Use convenção `prod-db-password-app01`.
5. **Secret Contents**: Escolha o tipo (Plain Text ou Base64).
6. **Encryption Key**: Selecione a chave do Vault.
7. **Rotation** (opcional): Configure se precisa de rotação.

**Nota**: [MUTABLE] Verifique os limites de secrets por Vault na região.
**Doc**: https://docs.oracle.com/en-us/iaas/Content/KeyManagement/Concepts/secretoverview.htm""",
        "list": f"""Para listar secrets via OCI CLI:

```bash
oci vault secret list \
    --compartment-id ocid1.compartment.oc1..example \
    --vault-id ocid1.vault.oc1..example \
    --query "data[].{{name:\"secret-name\", state:\"lifecycle-state\"}}"
```

**Via Console**: Vault → Secrets → Lista filtrável.

**Dica**: Use filtros para secrets por tag ou status.""",
        "get": f"""Para retrieving um secret value:

```bash
oci vault secret get-content \
    --secret-id ocid1.secret.oc1..example
```

**Importante**: O conteúdo só fica disponível por 1 hora após retrieval. Use imediatamente.

**Auditoria**: Sempre log quem acessa via OCI Logging com `auditd`.
[MUTABLE] Verifique políticas IAM para acesso.""",
        "update": f"""Para atualizar um secret (nova versão):

```bash
oci vault secret update \
    --secret-id ocid1.secret.oc1..example \
    --secret-content-tuple '{{"secret-name": "meu-secret", "content": "novo-valor-base64"}}'
```

**Nota**: Isso cria uma nova versão. Versões são imutáveis.
**Boa prática**: Sempre rode um teste antes de atualizar produção.""",
        "delete": f"""Para agendar deleção (soft delete):

```bash
oci vault secret schedule-secret-deletion \
    --secret-id ocid1.secret.oc1..example \
    --deletion-timeout-duration-days 7
```

**Período de grace**: 7-14 dias (configurável).
**Auditoria**: O Audit log mantém registro mesmo após deleção.
**Restore**: Use `restore-secret` dentro do período de grace.""",
        "rotate": f"""Para configurar rotação automática:

1. No Console: Vault → Secret → **Configure Rotation**.
2. **Rotation Policy**:
   - **Time-based**: A cada X dias (7, 30, 90).
   - **Usage-based**: Após X retrievals.
3. **Endpoint**: URL de rotação (Oracle rotation endpoint ou custom).

**CLI**:
```bash
oci vault secret update \
    --secret-id ocid1.secret.oc1..example \
    --rotation-policy '{{"time-interval-in-days": 30}}'
```

[MUTABLE] Verifique custo por rotação.""",
        "version": f"""Para gerenciar versões:

```bash
# Listar versões
oci vault secret list-versions \
    --secret-id ocid1.secret.oc1..example

# Get versão específica
oci vault secret get-content \
    --secret-id ocid1.secret.oc1..example \
    --version-number 2
```

**Versões**: Cada update cria uma nova versão numerada.
**Restore**: Não possível diretamente, mas pode copiar content de volta.""",
        "restore": f"""Para restaurar um secret deletado:

```bash
oci vault secret restore \
    --secret-id ocid1.secret.oc1..example
```

**Condições**: 
- Deve estar no período de grace (7-14 dias).
- Não ter sido deletado permanentemente.

**Dica**: Configure alertas para deleções agendadas.""",
        "policy": f"""Para dar acesso a secrets para compute/function:

**Policy mínima**:
```
Allow dynamic-group [MY-DG] to read secret-family in compartment [MY-COMPARTMENT]
Allow dynamic-group [MY-DG] to use keys in compartment [MY-COMPARTMENT]
```

**Boa prática**: Least-privilege - só `read`, não `manage`.

**Doc**: https://docs.oracle.com/en-us/iaas/Content/Identity/Concepts/policygetstarted.htm""",
        "inject": f"""Para injeção segura em containers:

**OCI DevOps**: Use 'Deploy' → 'Configuration' → 'Secret Reference'.

**Patterns seguros**:
1. **Volume mount**: Secrets como arquivos (não env vars).
2. **Mount path**: `/run/secrets/my-secret`.
3. **Não exponha**: Use `tmpfs` para dados sensíveis.

**Docker Compose**:
```yaml
secrets:
  db_pass:
    external: true
```

**Nunca**: LOG secrets em plaintext!""",
        "oci-cli": f"""Comandos OCI CLI essenciais para Vault:

```bash
# Criar Vault
oci vault vault create --compartment-id ... --vault-type DEFAULT

# Criar Secret  
oci vault secret create --vault-id ... --secret-content ...

# Listar Secrets
oci vault secret list --vault-id ...

# Get Content
oci vault secret get-content --secret-id ...

# Rotação
oci vault secret update-rotation --secret-id ...

# Deleção
oci vault secret schedule-secret-deletion --secret-id ...
```

**Requisito**: OCI CLI configurado com API key.""",
        "terraform": """Para Terraform:

**Provider**:
```hcl
provider "oci" {
  region = var.region
}
```

**Resource**:
```hcl
resource "oci_vault_secret" "app_secret" {
  compartment_id = var.compartment_ocid
  vault_id     = oci_vault_vault.main.id
  secret_name = "prod-api-key"
  content     = "base64-encoded-secret"
}
```

**Data Source**:
```hcl
data "oci_vault_secret" "fetch" {
  secret_id = oci_vault_secret.app_secret.id
}
```

**Importante**: Não commite secrets no TF state!""",
        "rotation-policy": f"""**Política de rotação recomendada**:

| Tipo Secret | Intervalo | Método |
|------------|----------|--------|
| DB Passwords | 30 dias | Automatic (OCI) |
| API Keys | 90 dias | Manual |
| Tokens | 60 dias | Webhook |
| Certs | 365 dias | ACME/Let's Encrypt |

**Configuração**:
1. **Segregação**: Secrets por ambiente (dev/stg/prod).
2. **Alertas**: Notifique quando rotação falhar.
3. **Teste**: Valide secret após rotação.

**Referências**:
- [CHECK DOCS] NIST SP 800-118
- OCI Vault Rotation Docs""",
        "monitoring": f"""**Monitoramento de accessos**:

1. **OCI Audit**:
   - Habilite em todos compartments.
   - Filtrar `target.secret.oc1`.

2. **OCI Logging**:
   ```bash
   oci logging log get --log-id ... --source-type vault-secret
   ```

3. **Alertas**:
   - Access em horário estranho.
   - Múltiplos failures.

**Dashboards**: Use OCI Monitoring com métricas customizadas.
**Retenção**: [MUTABLE] 90-365 dias conforme compliance.""",
        "troubleshoot": f"""**Diagnóstico de access denied**:

1. **Verificar Policy**:
```bash
oci iam policy get --policy-id ...
```

2. **Dynamic Group membership**:
```bash
oci compute instance get --instance-id ... | jq '.agent-config'
```

3. **Secret state**:
```bash
oci vault secret get --secret-id ...
```

4. **Audit logs**:
```bash
oci audit event list --compartment-id ... --source service vault
```

**Common causes**:
- Policy faltando para dynamic-group.
- Secret em compartment errado.
- TTL expirado (1 hora).""",
    }
    return answers.get(action, f"Gerencie secrets na {region} para {company}.")


for i in range(250):
    topic_idx = i % len(topics)
    action = topics[topic_idx][1]
    diff = topics[topic_idx][2]

    example = {
        "question": generate_question(
            topics[topic_idx][0],
            action,
            companies[i % len(companies)],
            regions[i % len(regions)],
            constraints[i % len(constraints)],
            lifecycles[i % len(lifecycles)],
            personas[i % len(personas)],
        ),
        "answer": generate_answer(
            action,
            topics[topic_idx][0],
            companies[i % len(companies)],
            regions[i % len(regions)],
            constraints[i % len(constraints)],
            lifecycles[i % len(lifecycles)],
            personas[i % len(personas)],
        ),
        "metadata": {
            "category": "devops/secrets",
            "difficulty": diff,
            "persona": personas[i % len(personas)],
            "intent": intents[i % len(intents)],
            "lifecycle": lifecycles[i % len(lifecycles)],
        },
    }
    examples.append(example)

print(f"Generated {len(examples)} examples")

with open(
    "/Users/otaviolemos/ml/olia-2-oci/data/curated/devops-secrets.jsonl", "w"
) as f:
    for ex in examples:
        f.write(json.dumps(ex, ensure_ascii=False) + "\n")

print("Saved to devops-secrets.jsonl")
