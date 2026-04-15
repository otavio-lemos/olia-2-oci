import json
import random
from datetime import datetime

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

projects = [
    "ecommerce-migration",
    "data-lake-modernization",
    "microservices-refactor",
    "disaster-recovery-setup",
    "compliance-audit",
    "cost-optimization",
    "performance-tuning",
    "backup-strategy",
    "zero-trust-implementation",
    "api-gateway-deployment",
    "container-platform",
    "serverless-transformation",
    "database-consolidation",
    "network-segmentation",
    "identity-federation",
    "multi-region-expansion",
    "hybrid-cloud-integration",
    "ci-cd-pipeline",
    "monitoring-overhaul",
    "infrastructure-modernization",
]

compartments = [
    "production",
    "staging",
    "development",
    "sandbox",
    "shared-services",
    "devops",
    "security",
    "networking",
    "analytics",
    "data-platform",
]

regions = [
    "sa-saopaulo-1",
    "us-ashburn-1",
    "us-phoenix-1",
    "eu-frankfurt-1",
    "uk-london-1",
    "ap-tokyo-1",
    "ap-sydney-1",
    "ap-mumbai-1",
    "ca-toronto-1",
    "me-jeddah-1",
]

personas = [
    "cloud architect",
    "platform engineer",
    "sre",
    "devops engineer",
    "finops analyst",
    "dba",
    "auditor",
    "security lead",
]

difficulties = ["beginner", "intermediate", "advanced"]

lifecycles = [
    "greenfield",
    "brownfield",
    "migração",
    "expansão",
    "produção estável",
    "auditoria",
    "incidente",
    "desativação",
    "rollback",
]

intents = [
    "design",
    "compare",
    "troubleshoot",
    "review",
    "recover",
    "migrate",
    "audit",
    "optimize",
    "standardize",
    "remediate",
]

constraints = [
    "sem downtime",
    "sem IP público",
    "com budget limitado",
    "equipe enxuta",
    "multi-região",
    "mínimo privilégio",
    "ambiente legado",
    "rollback em menos de 15 minutos",
    "com auditoria em 30 dias",
    "integração híbrida",
]

topics = [
    "Log Groups",
    "Custom Logs",
    "Audit Logs",
    "Log Retention",
    "Log Export",
    "Log Search",
    "Log Parsing",
    "Logging Agents",
    "Log Compliance",
    "Log Security",
    "Log Alerting",
    "Log Integration",
    "Log Monitoring",
    "Log Cost Optimization",
    "Log Archiving",
    "Log Encryption",
    "Log Access Control",
    "Log Performance",
]


def generate_question(
    company, project, compartment, region, persona, intent, constraint, lifecycle, topic
):
    constraint_text = f", considerando {constraint}" if random.random() > 0.3 else ""
    lifecycle_text = f" ({lifecycle})" if random.random() > 0.5 else ""

    templates = [
        f"Como {persona} da {company}, preciso configurar {topic.lower()} para o projeto {project} no compartment {compartment} em {region}{constraint_text}. Qual abordagem você recomenda?",
        f"Sou {persona} e preciso configurar {topic} no projeto {company} em {region}, considerando {compartment}{constraint_text}. Qual a melhor forma?",
        f"No ambiente {compartment} da {company}, qual é a melhor forma de configurar {topic.lower()} para {project} quando o objetivo é {intent}{constraint_text}?",
        f"Estamos em cenário de {lifecycle} e eu atuo como {persona}. Como configurar {topic} para {project} em {region}{constraint_text}?",
        f"Qual desenho você sugere para configurar {topic} no projeto {company} considerando {intent}{constraint_text} e operação em {region}?",
    ]
    return random.choice(templates)


def generate_answer(topic, intent, difficulty, constraint):
    answers = []

    # Content based on topic
    topic_content = {
        "Log Groups": {
            "cli": """```bash
# Criar Log Group
oci logging log-group create \\
  --compartment-id <COMPARTMENT_OCID> \\
  --display-name "meu-log-group" \\
  --description "Log Group para produção" \\
  --region sa-saopaulo-1

# Listar Log Groups
oci logging log-group list \\
  --compartment-id <COMPARTMENT_OCID> \\
  --query "data[?\"lifecycle-state\"=='ACTIVE']"

# Obter detalhes
oci logging log-group get \\
  --log-group-id <LOG_GROUP_OCID>
```""",
            "concepts": "Log Groups são containers lógicos que organizam Custom Logs. Cada compartment pode ter múltiplos Log Groups. Recomendamos criar um Log Group por aplicação ou serviço para facilitar a gestão e controles de acesso.",
        },
        "Custom Logs": {
            "cli": """```bash
# Criar Custom Log
oci logging log create \\
  --log-group-id <LOG_GROUP_OCID> \\
  --display-name "meu-custom-log" \\
  --log-source-type OCI_LINUX \\
  --configuration '{"ingestion": {"source": {"type": "OCI_LINUX"}}, "archiving": {"isEnabled": false}}'

# Habilitar log source
oci logging log update \\
  --log-id <LOG_OCID> \\
  --configuration '{"ingestion": {"source": {"type": "OCI_LINUX"}}, "isEnabled": true}'
```""",
            "concepts": "Custom Logs coletam logs de aplicações, sistemas operacionais ou fontes externas. O OCI Logging suporta vários tipos de source: OCI_LINUX, OCI_WINDOWS, CUSTOM, e integrações como Kubernetes, Functions, etc.",
        },
        "Audit Logs": {
            "cli": """```bash
# Audit logs são automaticamente habilitados na tenancy
# Listar audit logs disponíveis
oci logging log list \\
  --compartment-id <TENANCY_OCID> \\
  --log-type AUDIT

# Consultar eventos de audit
oci audit event list \\
  --compartment-id <COMPARTMENT_OCID> \\
  --start-time "2024-01-01T00:00:00Z" \\
  --end-time "2024-01-02T00:00:00Z" \\
  --query "data[?request.action=='CREATE']"
```""",
            "concepts": "Audit Logs registram todas as chamadas de API no OCI. São automaticamente coletados em toda a tenancy e não podem ser desativados. Retention: 365 dias para eventos de escrita, 90 dias para leitura.",
        },
        "Log Retention": {
            "cli": """```bash
# Atualizar retention (requer Object Storage para archive)
oci logging log update \\
  --log-id <LOG_OCID> \\
  --configuration '{"archiving": {"isEnabled": true, "retention": 30}}'
```""",
            "concepts": "Retention padrão é 30 dias para logs ativos. Para compliance, configure archive para Object Storage com retenção de até 1 ano. [CHECK DOCS] Limite máximo: 365 dias para archive.",
        },
        "Log Export": {
            "cli": """```bash
# Exportar para Object Storage via Service Connector Hub
oci sch connector create \\
  --compartment-id <COMPARTMENT_OCID> \\
  --display-name "log-export-archive" \\
  --source-kind logging \\
  --target-kind object-storage \\
  --source-config '{"logSourceId": "<LOG_GROUP_OCID>"}' \\
  --target-config '{"bucketName": "log-archive", "namespace": "<TENANCY_NAME>"}'
```""",
            "concepts": "Use Service Connector Hub para exportar logs para Object Storage, Stream, ou Functions. Configure partitionamento por data para facilitar查询. [MUTABLE] Custos de Object Storage aplicam-se.",
        },
        "Log Search": {
            "cli": """```bash
# Pesquisar logs via CLI
oci logging search \\
  --compartment-id <COMPARTMENT_OCID> \\
  --search-query "logGroupId=<LOG_GROUP_OCID> | where level == 'ERROR' | sort by timestamp desc" \\
  --start-time "2024-01-01T00:00:00Z" \\
  --end-time "2024-01-02T00:00:00Z"
```""",
            "concepts": "Log Search permite consultas ad-hoc usando OCI Logging Query Language. Suporta filtros por nível, fonte, tempo e campos customizados. Busca últimos 30 dias.",
        },
        "Logging Agents": {
            "cli": """```bash
# Instalação do agente em instância
# 1. Criar Log Group para agente
# 2. Gerar token de autenticação
# 3. Instalar agente
curl -s "https://objectstorage.us-ashburn-1.oraclecloud.com/n/idcs_xxx" | bash -s -- --log-group-id <LOG_GROUP_OCID>
```""",
            "concepts": "OCI Logging Agent é um agente leve que coleta logs de VMs. Suporta Linux e Windows. Use para aplicações que não têm integração nativa com OCI.",
        },
        "Log Alerting": {
            "cli": """```bash
# Criar alarme baseado em log
oci monitoring alarm create \\
  --compartment-id <COMPARTMENT_OCID> \\
  --display-name "error-log-alert" \\
  --namespace oci_logging \\
  --query-text "search(\"<LOG_GROUP_OCID>\") | where level == 'ERROR' | count() > 10" \\
  --severity CRITICAL \\
  --destinations '["<TOPIC_OCID>"]' \\
  --repeat-notification-duration PT1H
```""",
            "concepts": "Alertas baseados em log monitoram padrões específicos. Configure thresholds apropriados para evitar falsos positivos. [CHECK DOCS] Limite: 50 alarmes por log group.",
        },
        "Log Compliance": {
            "concepts": "Para compliance (LGPD, SOX, etc.), implemente: retenção prolongada via archive, encryption em repouso, acesso restrito via IAM, e auditoria de acesso aos logs. Documente a política de retenção."
        },
        "Log Cost Optimization": {
            "concepts": "Otimize custos: desabilite logs não utilizados, configure archive para retention longo, use filtros para não capturar logs desnecessários, e implemente lifecycle policies. [MUTABLE] Custos: ~$0.50/GB/mês para logs ativos."
        },
    }

    topic_key = random.choice(list(topic_content.keys()))
    content = topic_content[topic_key]

    # Add specific guidance based on intent
    if intent == "troubleshoot":
        guidance = """
**Diagnóstico:**
1. Verifique o estado do Log Group: `oci logging log-group get --log-group-id <OCID>`
2. Liste os logs ativos: `oci logging log list --log-group-id <OCID>`
3. Check events de Audit para operações recentes
4. Verifique métricas de ingestion no Monitoring

**Problemas comuns:**
- Log não aparece: verifique se está habilitado (isEnabled: true)
- Performance lenta: use filtros de tempo mais específicos
- Custo alto: revue retention e archiving settings"""
    elif intent == "optimize":
        guidance = """
**Otimização recomendada:**
1. **Indexação**: Use campos estruturados para queries mais rápidas
2. **Retenção**: Configure archive para dados >30 dias
3. **Filtragem**: Aplique include/exclude filters para reduzir volume
4. **Agregação**: Considere agregar logs de múltiplas fontes

**Cost savings:**
- Reduza retention de ambientes não-produção
- Archive logs de compliance automaticamente
- Use Object Storage com lifecycle policies"""
    elif intent == "design":
        guidance = """
**Arquitetura recomendada:**
1. Crie Log Groups por domínio/aplicação
2. Use naming convention: `lg-{ambiente}-{projeto}-{servico}`
3. Configure tags para organização: `project`, `environment`, `team`
4. Implemente Service Connector para archiving
5. Configure alertas para erros críticos desde o início

**IAM Required:**
```
Allow group Developers to use log-groups in compartment development
Allow group Ops to manage log-groups in compartment production
Allow group Auditors to read log-groups in compartment shared-services
```"""
    elif intent == "migrate":
        guidance = """
**Migração de Logging:**
1. Mapeie estrutura atual de logs para OCI Log Groups
2. Configure Collection Agents na fonte
3. Valide que todos os logs estão sendo coletados
4. Atualize aplicações para enviar para OCI
5. Mantenha sistema anterior durante transição (30 dias)

**Timeline:**
- Week 1: Setup Log Groups e Agents
- Week 2: Coleta em paralelo
- Week 3: Validação e cutover
- Week 4: Decomission sistema anterior"""
    else:
        guidance = ""

    # Add constraint-specific guidance
    if "sem downtime" in constraint:
        guidance += (
            "\n\n**Sem downtime**: Configuração é automática e não impacta aplicações."
        )
    elif "budget limitado" in constraint:
        guidance += "\n\n**Budget limitado**: Comece com retention de 30 dias, habilite archive apenas para compliance."
    elif "equipe enxuta" in constraint:
        guidance += "\n\n**Equipe enxuta**: Use Terraform/Provider para IaC e automatize operacionais."

    # Build answer
    answer = f"{content.get('concepts', '')}\n\n"
    if content.get("cli"):
        answer += f"**Comandos OCI:**\n{content['cli']}\n\n"
    answer += guidance

    # Add warnings
    answer += """
\n**Avisos importantes:**
- [MUTABLE] Preços variam por região e configuração; consulte a calculadora OCI
- [CHECK DOCS] Limites podem variar por tenancy; verifique Service Limits
- Sempre valide em ambiente de teste antes de produção
"""

    return answer


# Generate 250 examples
examples = []
for i in range(250):
    company = random.choice(companies)
    project = random.choice(projects)
    compartment = random.choice(compartments)
    region = random.choice(regions)
    persona = random.choice(personas)
    difficulty = random.choice(difficulties)
    lifecycle = random.choice(lifecycles)
    intent = random.choice(intents)
    constraint = random.choice(constraints)
    topic = random.choice(topics)

    question = generate_question(
        company,
        project,
        compartment,
        region,
        persona,
        intent,
        constraint,
        lifecycle,
        topic,
    )
    answer = generate_answer(topic, intent, difficulty, constraint)

    example = {
        "question": question,
        "answer": answer,
        "metadata": {
            "category": "observability/logging",
            "difficulty": difficulty,
            "persona": persona,
            "intent": intent,
            "lifecycle": lifecycle,
        },
    }
    examples.append(example)

# Save to file
output_path = "data/curated/observability-logging.jsonl"
with open(output_path, "w", encoding="utf-8") as f:
    for ex in examples:
        f.write(json.dumps(ex, ensure_ascii=False) + "\n")

print(f"Generated {len(examples)} examples to {output_path}")
