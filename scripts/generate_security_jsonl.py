#!/usr/bin/env python3
"""
OCI Dataset Generator - Generates curated JSONL files with OCI examples.
Each file: 180 examples (30% beginner, 50% intermediate, 20% advanced)
Questions in Portuguese (PT-BR)
"""

import json
import random
import uuid

random.seed(42)

PERSONAS = [
    "cloud architect",
    "platform engineer",
    "sre",
    "security lead",
    "devops engineer",
    "dba",
    "finops analyst",
    "auditor",
]

LIFECYCLES = [
    "greenfield",
    "brownfield",
    "produção estável",
    "incidente",
    "expansão",
    "auditoria",
    "migração",
    "desativação",
]

INTENTS = [
    "design",
    "compare",
    "troubleshoot",
    "remediate",
    "audit",
    "optimize",
    "migrate",
    "standardize",
    "review",
    "recover",
]

COMPANIES = [
    "TechCorp Brasil",
    "DataFlow Solutions",
    "CloudShop BR",
    "FinTech Brasil",
    "HealthTech SA",
    "LogiTech Corp",
    "RetailBr E-commerce",
    "EduTech Brasil",
    "StartUp Inovacao",
    "MegaCorp Tecnologia",
    "BankBr Finance",
    "SecureNet",
    "DevTeam Brasil",
    "OpsCenter BR",
    "DataCenter Solutions",
    "AgroTech Brasil",
]

WAF_TOPICS = {
    "beginner": [
        (
            "PROTEÇÃO OWASP",
            "ativa proteção contra SQL Injection, XSS e outras vulnerabilidades OWASP Top 10",
            "beginner",
        ),
        (
            "GEO-BLOCKING",
            "bloqueia acesso por país de origem (ex: block China, Russia)",
            "beginner",
        ),
        (
            "PROTEÇÃO DDoS",
            "mitigação de ataques de negação de serviço na borda Oracle",
            "beginner",
        ),
        ("MONITORAMENTO", "configura alertas para detecção de anomalias", "beginner"),
        (
            "ACesso VIA CONSOLE",
            "cria primeira política WAF pelo console OCI",
            "beginner",
        ),
    ],
    "intermediate": [
        (
            "ACCESS RULES POR IP",
            "cria regras de acesso baseadas em IP source (allow/block)",
            "intermediate",
        ),
        (
            "RATE LIMITING",
            "limita requests por IP para evitar abuso de API",
            "intermediate",
        ),
        (
            "BOT MANAGEMENT",
            "detecta e bloqueia bots maliciosos (scrapers, scanners)",
            "intermediate",
        ),
        (
            "WAF + LOAD BALANCER",
            "associa WAF regional a um Load Balancer existente",
            "intermediate",
        ),
        (
            "DIAGNÓSTICO FALSOS POSITIVOS",
            "analisa logs para identificar regras que bloqueiam tráfego legítimo",
            "intermediate",
        ),
        (
            "EXCLUSION RULES",
            "cria exceções para URLs específicas em regras de proteção",
            "intermediate",
        ),
    ],
    "advanced": [
        (
            "CUSTOM RULES AVANÇADAS",
            "cria regras customizadas com expressões regex para padrões específicos",
            "advanced",
        ),
        (
            "WAF REGIONAL VS EDGE",
            "decide entre WAF edge (global) vs regional (LB attached)",
            "advanced",
        ),
        (
            "CACHE DE RESPOSTAS",
            "configura caching para reduzir latência de API",
            "advanced",
        ),
        (
            "CANARY DEPLOYMENT",
            "testa novas regras em produção com tráfego limitado",
            "advanced",
        ),
    ],
}


def generate_waf_examples():
    examples = []
    for i in range(180):
        if i < 54:
            topic, desc, difficulty = random.choice(WAF_TOPICS["beginner"])
        elif i < 144:
            topic, desc, difficulty = random.choice(WAF_TOPICS["intermediate"])
        else:
            topic, desc, difficulty = random.choice(WAF_TOPICS["advanced"])

        persona = random.choice(PERSONAS)
        company = random.choice(COMPANIES)
        lifecycle = random.choice(LIFECYCLES)
        intent = random.choice(INTENTS)

        question = f"Como {persona} da {company}, preciso configurar {topic.lower()} no OCI WAF. {desc}. Como devo proceder?"

        answers = {
            "beginner": f"""Para configurar {topic.lower()} no OCI WAF:

**Passos via Console OCI:**
1. Acesse Identity & Security → Web Application Firewall
2. Clique em Create Policy e defina nome e domínio
3. Configure as regras de proteção conforme necessidade
4. Clique em Publish Changes para ativar

**Comandos CLI úteis:**
```bash
oci waas waas-policy list --compartment-id $COMPARTMENT_ID
oci waas waas-policy get --waas-policy-id $WAF_OCID
```

**Dica**: Sempre teste novas regras em modo "Log Only" antes de bloquear.

[MUTABLE] Custo: WAF ~$50/mês por política ativa + $0.000003 por request.
[CHECK DOCS] Limite de 50 regras por política.

**Referência**: https://docs.oracle.com/en-us/iaas/Content/WAF/Concepts/overview.htm""",
            "intermediate": f"""Para configurar {topic.lower()} no OCI WAF:

**Via Console:**
1. Vá em Identity & Security → Web Application Firewall → sua política
2. Acesse a seção de configuração (Access Control / Protection Rules)
3. Crie a regra com as condições necessárias
4. Publish Changes para aplicar

**Via OCI CLI:**
```bash
oci waas waas-policy update --waas-policy-id $WAF_OCID \\
    --rules '[{{"action": "BLOCK", "ruleType": "..."}}]' \\
    --wait-for-state SUCCEEDED
```

**Importante**: Para rate limiting, configure threshold (ex: 100 req/min por IP).

[MUTABLE] Custo: stesso acima + custos de logging adicional se habilitado.
[CHECK DOCS] Verifique limites de rate: max 10000 req/min, burst 500.

**Referência**: https://docs.oracle.com/en-us/iaas/Content/WAF/Concepts/overview.htm""",
            "advanced": f"""Para implementar {topic.lower()} no OCI WAF:

**Arquitetura Recomendada:**
1. Avalie se precisa Edge WAF (global) ou Regional WAF (LB attached)
2. Para Edge: configure CNAME no seu DNS para apontar para WAF
3. Para Regional: associe Policy ao OCID do Load Balancer

**CLI Completo:**
```bash
# Criar policy edge
oci waas waas-policy create \\
    --compartment-id $COMPARTMENT_ID \\
    --display-name "production-waf" \\
    --domain "app.$company.com.br" \\
    --origins '[{{"label": "primary", "uri": "https://backend.internal"}}]'

# Adicionar regra customizada
oci waas waas-policy update \\
    --waas-policy-id $WAF_OCID \\
    --protection-rules '[{{"key": "CUSTOM_RULE", "action": "BLOCK"}}]'
```

**Trade-offs**: Edge WAF oferece proteção global mas latência adicional; Regional é mais rápido mas menos distribuído.

[MUTABLE] Custos: Edge ~$75/mês, Regional ~$50/mês.
[CHECK DOCS] Limite de 200 regras customizadas por política.

**Referência**: https://docs.oracle.com/en-us/iaas/Content/WAF/Concepts/overview.htm""",
        }

        answer = answers[difficulty]

        examples.append(
            {
                "question": question,
                "answer": answer,
                "metadata": {
                    "category": "security/waf",
                    "difficulty": difficulty,
                    "persona": persona,
                    "intent": intent,
                    "lifecycle": lifecycle,
                },
            }
        )

    return examples


def generate_zero_trust_examples():
    """Zero Trust Architecture examples"""
    topics = [
        ("criar VCN com subnets privadas", "beginner"),
        ("configurar Bastion para acesso seguro", "intermediate"),
        ("implementar Private Endpoint para serviços", "intermediate"),
        ("Network Security Groups (NSG) configuracao", "intermediate"),
        ("Private Access Channel para OCI services", "intermediate"),
        ("seguranca em camada com security lists", "beginner"),
        ("acesso sem VPN via Bastion SSH", "beginner"),
        ("isolamento de workloads com compartments", "intermediate"),
        ("design de microsegmentacao", "advanced"),
        ("ZTNA implementation com IDCS", "advanced"),
        ("acesso a OCI APIs sem expor internet", "intermediate"),
        ("failover seguro entre regioes", "advanced"),
    ]

    examples = []
    for i in range(180):
        topic, base_difficulty = topics[i % len(topics)]
        difficulty = (
            base_difficulty
            if i < 144
            else random.choice(["beginner", "intermediate", "advanced"])
        )

        persona = random.choice(PERSONAS)
        company = random.choice(COMPANIES)
        lifecycle = random.choice(LIFECYCLES)
        intent = random.choice(INTENTS)

        question = f"Como {persona} na {company}, preciso implementar {topic}. Quais sao os passos?"

        answer = f"""Para implementar {topic} no contexto Zero Trust OCI:

**Arquitettura:**
1. Crie VCN dedicada para workloads sensiveis
2. Use subnets privadas com security lists restritivas
3. Implemente NSGs para controle granular
4. Configure Bastion para acesso administrativo

**OCI CLI:**
```bash
oci network vcn create --compartment-id [OCID] --cidr-block "10.0.0.0/16"
oci network subnet create --vcn-id [VCN_OCID] --cidr-block "10.0.1.0/24"
oci network nsg create --compartment-id [OCID] --vcn-id [VCN_OCID]
```

[MUTABLE] Custos: Bastion baseado em horas de conexao, VCN gratuita dentro de limites.
[CHECK DOCS] Limites de NSGs por VCN e regras por NSG.

**Referência**: https://docs.oracle.com/en-us/iaas/Content/Security/Reference/security.htm"""

        examples.append(
            {
                "question": question,
                "answer": answer,
                "metadata": {
                    "category": "security/zero-trust",
                    "difficulty": difficulty,
                    "persona": persona,
                    "intent": intent,
                    "lifecycle": lifecycle,
                },
            }
        )

    return examples


def generate_posture_management_examples():
    """Cloud Guard Posture Management examples"""
    topics = [
        ("ativar Cloud Guard na tenancy", "beginner"),
        ("configurar detector recipes", "intermediate"),
        ("criarSecurity Zone para recursos sensiveis", "intermediate"),
        ("remediacao automatica de findings", "intermediate"),
        ("configurar responder rules", "intermediate"),
        ("integrar com SIEM via logs", "intermediate"),
        ("design de detector customizado", "advanced"),
        ("relatorios de conformidade SOC2", "beginner"),
        ("baseline de seguranca inicial", "beginner"),
        ("monitoramento continuo de postura", "intermediate"),
        ("correcao de vulnerabilidades em compute", "advanced"),
        ("alertas para mudancas de seguranca", "intermediate"),
    ]

    examples = []
    for i in range(180):
        topic, base_difficulty = topics[i % len(topics)]
        difficulty = (
            base_difficulty
            if i < 144
            else random.choice(["beginner", "intermediate", "advanced"])
        )

        persona = random.choice(PERSONAS)
        company = random.choice(COMPANIES)
        lifecycle = random.choice(LIFECYCLES)
        intent = random.choice(INTENTS)

        question = f"Como {persona} na {company}, preciso configurar {topic}. Qual a abordagem recomendada?"

        answer = f"""Para configurar {topic} com Cloud Guard:

**Procedimento:**
1. Ative Cloud Guard no compartment raiz da tenancy
2. Configure targets (compartments a serem monitorados)
3. Selecione detector recipes apropriados
4. Defina responder rules para automacao

**OCI CLI:**
```bash
oci cloud-guard cloud-guard-target create --compartment-id [OCID] \
    --target-type COMPARTMENT --target-id [TARGET_OCID]
oci cloud-guard detector-recipe list --compartment-id [OCID]
```

[MUTABLE] Custos: Cloud Guard cobrado por recursos monitorados.
[CHECK DOCS] Limites de recipes e rules por tenancy.

**Referência**: https://docs.oracle.com/en-us/iaas/Content/CloudGuard/concepts/cloudguardoverview.htm"""

        examples.append(
            {
                "question": question,
                "answer": answer,
                "metadata": {
                    "category": "security/posture-management",
                    "difficulty": difficulty,
                    "persona": persona,
                    "intent": intent,
                    "lifecycle": lifecycle,
                },
            }
        )

    return examples


def generate_api_gateway_examples():
    """API Gateway examples"""
    topics = [
        ("criar API Gateway para microsservicos", "beginner"),
        ("definir rotas e backends", "intermediate"),
        ("autenticacao JWT no API Gateway", "intermediate"),
        ("rate limiting por cliente", "intermediate"),
        ("integrar com OCI Functions", "intermediate"),
        ("certificado SSL para dominio customizado", "beginner"),
        ("transformacao de requests/responses", "advanced"),
        ("cache de respostas", "intermediate"),
        ("CORS configuration", "beginner"),
        ("logs e monitoramento de APIs", "beginner"),
        ("versao de APIs com canary deploy", "advanced"),
        ("autenticacao com API Keys", "intermediate"),
    ]

    examples = []
    for i in range(180):
        topic, base_difficulty = topics[i % len(topics)]
        difficulty = (
            base_difficulty
            if i < 144
            else random.choice(["beginner", "intermediate", "advanced"])
        )

        persona = random.choice(PERSONAS)
        company = random.choice(COMPANIES)
        lifecycle = random.choice(LIFECYCLES)
        intent = random.choice(INTENTS)

        question = f"Como {persona} na {company}, preciso configurar {topic} no OCI API Gateway. Como faco isso?"

        answer = f"""Para configurar {topic} no OCI API Gateway:

**Via Console:**
1. Identity & Security → API Gateway → Create Gateway
2. Defina as rotas e integracoes necessarias
3. Configure autenticacao e throttling
4. Implemente logging para monitoramento

**OCI CLI:**
```bash
oci api-gateway gateway create --compartment-id [OCID] \
    --display-name "my-gateway" --endpoint-type "PUBLIC"
oci api-gateway deployment create --gateway-id [GATEWAY_OCID] \
    --path-prefix "/api" --logging-level "INFO"
```

[MUTABLE] Custos: Cobrado por hora do gateway e chamadas de API.
[CHECK DOCS] Limites de rotas por deployment e rate limits.

**Referência**: https://docs.oracle.com/en-us/iaas/Content/ApiGateway/Concepts/apigatewayoverview.htm"""

        examples.append(
            {
                "question": question,
                "answer": answer,
                "metadata": {
                    "category": "serverless/api-gateway",
                    "difficulty": difficulty,
                    "persona": persona,
                    "intent": intent,
                    "lifecycle": lifecycle,
                },
            }
        )

    return examples


def generate_secrets_examples():
    """Vault Secrets examples"""
    topics = [
        ("criar Vault e secrets", "beginner"),
        ("recuperar secret via CLI", "beginner"),
        ("rotacao automatica de secrets", "intermediate"),
        ("polices de acesso a Vault", "intermediate"),
        ("integrar secrets em Functions", "intermediate"),
        ("importar secrets de sistemas externos", "advanced"),
        ("versionamento de secrets", "beginner"),
        ("secret com expiration date", "intermediate"),
        ("uso de secrets em Container Instances", "intermediate"),
        ("auditoria de acesso a secrets", "intermediate"),
        ("migracao de HashiCorp Vault para OCI", "advanced"),
        ("secret no Terraform OCI provider", "intermediate"),
    ]

    examples = []
    for i in range(180):
        topic, base_difficulty = topics[i % len(topics)]
        difficulty = (
            base_difficulty
            if i < 144
            else random.choice(["beginner", "intermediate", "advanced"])
        )

        persona = random.choice(PERSONAS)
        company = random.choice(COMPANIES)
        lifecycle = random.choice(LIFECYCLES)
        intent = random.choice(INTENTS)

        question = f"Como {persona} na {company}, preciso gerenciar {topic} no OCI Vault. Quais sao os passos?"

        answer = f"""Para gerenciar {topic} no OCI Vault:

**Procedimento:**
1. Crie um Vault no compartment apropriado
2. Defina policies de acesso (IAM)
3. Crie secrets com versionamento
4. Use a API/CLI para recuperacao segura

**OCI CLI:**
```bash
oci vault secret create --vault-id [VAULT_OCID] \
    --secret-name "db-password" --secret-content "..."
oci vault secret get --secret-id [SECRET_OCID]
```

[MUTABLE] Custos: Vault possui taxa base + custos por secret/version.
[CHECK DOCS] Limites de secrets por vault e retencao de versoes.

**Referência**: https://docs.oracle.com/en-us/iaas/Content/KeyManagement/Concepts/keyoverview.htm"""

        examples.append(
            {
                "question": question,
                "answer": answer,
                "metadata": {
                    "category": "security/secrets",
                    "difficulty": difficulty,
                    "persona": persona,
                    "intent": intent,
                    "lifecycle": lifecycle,
                },
            }
        )

    return examples


def write_jsonl(examples, filepath):
    """Write examples to JSONL file"""
    with open(filepath, "w", encoding="utf-8") as f:
        for ex in examples:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")
    print(f"Wrote {len(examples)} examples to {filepath}")


def main():
    random.seed(42)

    base_dir = "/Users/otaviolemos/ml/olia-2-oci/data/curated"

    files = [
        ("security-waf.jsonl", generate_waf_examples),
        ("security-zero-trust.jsonl", generate_zero_trust_examples),
        ("security-posture-management.jsonl", generate_posture_management_examples),
        ("serverless-api-gateway.jsonl", generate_api_gateway_examples),
        ("security-secrets.jsonl", generate_secrets_examples),
    ]

    for filename, generator in files:
        examples = generator()
        filepath = f"{base_dir}/{filename}"
        write_jsonl(examples, filepath)

        # Verify difficulty distribution
        beginner = sum(1 for e in examples if e["metadata"]["difficulty"] == "beginner")
        intermediate = sum(
            1 for e in examples if e["metadata"]["difficulty"] == "intermediate"
        )
        advanced = sum(1 for e in examples if e["metadata"]["difficulty"] == "advanced")
        print(
            f"  Difficulty: beginner={beginner} ({beginner / 180 * 100:.1f}%), intermediate={intermediate} ({intermediate / 180 * 100:.1f}%), advanced={advanced} ({advanced / 180 * 100:.1f}%)"
        )


if __name__ == "__main__":
    main()
