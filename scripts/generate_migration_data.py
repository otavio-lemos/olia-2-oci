import json
import random

random.seed(42)

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

personas = [
    "cloud architect",
    "platform engineer",
    "dba",
    "sre",
    "devops engineer",
    "security lead",
    "finops analyst",
    "auditor",
]

intent_patterns = [
    "design",
    "troubleshoot",
    "compare",
    "standardize",
    "optimize",
    "migrate",
    "recover",
    "audit",
]
lifecycle_patterns = [
    "greenfield",
    "produção estável",
    "brownfield",
    "incidente",
    "expansão",
    "desativação",
    "auditoria",
    "migração",
]
regions = [
    "sa-saopaulo-1",
    "us-ashburn-1",
    "us-phoenix-1",
    "eu-frankfurt-1",
    "uk-london-1",
    "ap-tokyo-1",
    "ap-sydney-1",
    "ca-toronto-1",
    "ap-mumbai-1",
    "me-jeddah-1",
]
difficulties = ["beginner", "intermediate", "advanced"]

db_types = [
    "Oracle Database",
    "MySQL",
    "PostgreSQL",
    "SQL Server",
    "MongoDB",
    "Cassandra",
    "MariaDB",
]
oci_db_services = [
    "Autonomous Database",
    "MySQL HeatWave",
    "PostgreSQL Database",
    "NoSQL Database",
]

migration_topics = [
    ("Oracle Database", "oracle", "Autonomous Database"),
    ("MySQL", "mysql", "MySQL HeatWave"),
    ("PostgreSQL", "postgresql", "PostgreSQL Database"),
    ("MongoDB", "mongodb", "NoSQL Database"),
    ("SQL Server", "sqlserver", "Autonomous Database"),
    ("MariaDB", "maria", "MySQL HeatWave"),
]

question_templates = [
    "Sou {persona} na {company} e preciso migrar {db_type} on-premises para {oci_service} no projeto {project}, em {environment}/{region}, considerando {constraint}. Qual abordagem você recomenda?",
    "Como {persona}, preciso de um comando OCI CLI para migrar {db_type} on-premises para {oci_service} no contexto de {project}, com cenário {lifecycle} e requisito de {constraint}.",
    "Ao migrar {db_type} on-premises para OCI, recebo o erro {error}. Como {persona} da {company}, como devo proceder para diagnosticar e resolver isso?",
    "Qual a diferença entre {db_type} on-premises e {oci_service} no OCI e quando usar cada um para o projeto {project} da {company}?",
    "Preciso projetar arquitetura de alta disponibilidade para {db_type} migrado para {oci_service}. Como devo distribuir os recursos para suportar falhas sem usar múltiplas regiões?",
    "O que define um recurso como elegível para migração de {db_type} no OCI e quais configurações estão incluídas atualmente?",
    "Sou {persona} e preciso realizar {operation} em {db_type} durante a migração para {oci_service}. Quais são os passos para garantir zero downtime?",
    "Como garantir que minha migração de {db_type} não contenha dados desatualizados ou configurações incorretas antes de aplicar em produção?",
    "Qual estratégia de cutover você recomenda para migrar {db_type} on-premises para {oci_service} com {constraint}?",
    "Preciso validar que a migração de {db_type} foi concluída com sucesso. Quais métricas e verificações devo executar?",
]

answer_templates = [
    """**Migration Guide — On-premises → OCI ({company} - {project})**

**Mapeamento de serviços (On-premises → OCI):**
| On-premises | OCI | CLI Command |
|----------|-----|-------------|
| {db_type} | {oci_service} | `oci db autonomous-database create` |

**Fases da migração:**

**Fase 1: Assessment (1-2 semanas)**
- Inventariar workloads e dependências
- Classificar por criticidade e complexidade
- Definir estratégia: rehost, replatform, refactor
- Estimar custos OCI vs On-premises

**Fase 2: Foundation (1-2 semanas)**
- Criar VCN, subnets, gateways
- Configurar IAM, compartments, policies
- Estabelecer conectividade (IPSec/FastConnect)
- Configurar monitoring e logging

**Fase 3: Migration (2-4 semanas)**
- Migrar dados primeiro (Database Migration Service)
- Migrar aplicações (lift-and-shift ou replatform)
- Validar funcionalidade e performance
- Executar cutover com mínimo downtime

**Fase 4: Optimization (contínuo)**
- Right-size resources baseado em métricas reais
- Implementar auto-scaling
- Otimizar custos com Universal Credits
- Documentar runbooks OCI

**Ferramentas de migração OCI:**
- **Database Migration Service**: Online migration com mínimo downtime
- **Data Transfer Service**: Appliance físico para grandes volumes
- **Object Storage Migration Service**: Migração direta entre clouds

**Nota:** [MUTABLE] Preços e limites de shapes variam por região. Verifique sempre o Service Limits no console.
**Doc de referência:** https://docs.oracle.com/en-us/iaas/Content/Database/overview.htm""",
    """Para migrar via CLI, use o comando `oci db autonomous-database create`. No OCI, Autonomous Database oferece escala automática e sem gerenciamento.

**Comando:**
```bash
oci db autonomous-database create \\
    --compartment-id $(oci iam compartment list \\
    --query "data[?name=='{environment}'].id | [0]") \\
    --display-name "{project}-migration" \\
    --region {region} \\
    --db-name "migrateddb" \\
    --cpu-core-count {ocpus} \\
    --storage-size-in-tbs {storage} \\
    --license-model {license} \\
    --wait-for-state AVAILABLE
```

**Pontos de atenção:**
- Autonomous Database é serverless: você não gerencia OS ou patches.
- [MUTABLE] O modelo de licença pode ser 'Included' (BYOL) ou 'License Included'.
- Para {constraint}, configure private endpoint com subnet privada e evite IP público.

**Dica**: Use --db-workload {workload_type} para otimizar para OLTP ou OLAP.""",
    """O erro '{error}' indica um problema na configuração ou limites do serviço.

**Passos para remediação:**
1. **Verificar Limites**: No console, vá em **Governance & Administration** → **Limits, Quotas, and Usage**.
2. **Filtrar**: Selecione o serviço 'Database' e procure pelo recurso específico.
3. **Analisar Uso**: Verifique se há bancos de dados parados que ainda consomem cota.
4. **Solicitar Aumento**: Se realmente precisar de mais, clique em 'Request a service limit increase'.

**Checklist de diagnóstico:**
- Verificar conectividade de rede (NAT Gateway, Service Gateway)
- Confirmar políticas IAM corretas para o serviço Database
- Validar credenciais de conexão (wallet, credentials)
- [CHECK DOCS] Monitorar eventos no OCI Events para erros de operação.

**Nota**: {db_type} on-premises pode ter configurações incompatíveis. Valide character set, timezone e parâmetros.""",
    """Embora ambos armazenam dados, os propósitos são distintos:

- **{db_type} on-premises**: Total controle de hardware, SO, patches. Você é responsável por backups, alta disponibilidade e tuning.
- **{oci_service}**: Fully managed. A Oracle gerencia patches, backups, HA automaticamente. Escalabilidade automática.

**Comparação rápida:**
- **TCO**: On-premises tem custos ocultos (energia, físicos, DBAs). OCI é OPEX puro.
- **HA**: OCI fornece Data Guard automático em standby regions.
- **Backup**: OCI tem backup automático com retenção configurável.

**Recomendação para {project}**: Use {oci_service} se sua equipe quer focar em aplicação, não administração. O custo é maior mas o tempo de DBAs diminui.

**Terminologia correta**: Use 'Autonomous Database' para Oracle, 'HeatWave' para MySQL Analytics.""",
    """Para alta disponibilidade dentro de uma única região OCI para {db_type} migrado, utilize **Autonomous Data Guard** ou réplicas cross-AD.

**Estratégia de Design:**
1. **Primary**: Crie Autonomous Database com Data Guard em standby automático.
2. **Distribuição em ADs**: Configure primary em AD-1 e standby em AD-2 (se disponível).
3. **Failover Automático**: O ADG detecta falha e promove standby em minutos.
4. **Application**: Use FCF (Fast Connect Failover) ou connection pool com múltiplos endpoints.

**Trade-off**: Cross-Region Data Guard oferece proteção contra regionais inteiras, mas tem latência maior.

**RPO/RTO para {project}:**
- RPO: Segundos (Sync mode) a minutos (Async mode)
- RTO: 3-5 minutos (Automatic failover)

**Nota**: [MUTABLE] Data Guard tem custo adicional por standby. Calcule antes de habilitar.""",
    """**Análise de Custos — Migração {db_type} ({company} - {project})**

**Componentes de custo:**
1. **Database**: Baseado em OCPUs e storage (Oracle) ou instâncias (MySQL/PostgreSQL).
2. **Storage**: Backup storage no Object Storage.
3. **Networking**: Data transfer entre regiões e internet.
4. **Serviços complementares**: Monitoring, Logging, Vault para wallets.

**Otimizações recomendadas:**
- Use Express Reviews para estimar custos antes
- Tag resources por projeto para chargeback
- Considere Universal Credits para descontos por commitment

**Referência**: [OCI Pricing Calculator](https://www.oracle.com/cloud/costestimator.html)

**Dicas de otimização:**
- Monitore utilização real antes de dimensionar
- Use Autonomous para workloads variáveis (escala automática)
- Avalie {oci_service} para workloads específicos""",
    """**Performance Tuning — {db_type} em OCI ({company} - {project})**

**Metodologia:**
1. Establish baseline com métricas atuais
2. Identificar bottleneck (CPU, I/O, network)
3. Aplicar otimização isolada
4. Re-medir e comparar
5. Documentar resultados

**Ferramentas OCI:**
- OCI Monitoring: métricas em tempo real
- OCI APM: application performance monitoring
- OCI Logging: logs estruturados para análise

**Comandos de diagnóstico:**
```bash
# Monitorar métricas de database
oci monitoring metric-data summarize-metrics \\
  --compartment-id <ocid> \\
  --query-text "CpuUtilization[1m].maximum"

# Verificar storage I/O
oci bv volume-performance get --volume-id <ocid>
```

**Referência**: [OCI Performance Best Practices](https://docs.oracle.com/iaas/Content/performance.htm)""",
]

errors = [
    "Service limit reached",
    "Invalid credential type",
    "Connection timeout",
    "Invalid subnet configuration",
    "License not supported",
    "Shape not available",
    "Network route not found",
]

constraints = [
    "sem downtime",
    "sem IP público",
    "com orçamento limitado",
    "ambiente legado",
    "com auditoria em 30 dias",
    "mínimo privilégio",
    "integração híbrida",
    "multi-região",
    "rollback em menos de 15 minutos",
    "equipe enxuta",
]

projects = [
    "ecommerce-migration",
    "data-lake-modernization",
    "microservices-refactor",
    "disaster-recovery-setup",
    "compliance-audit",
    "cost-optimization",
    "performance-tuning",
    "security-hardening",
    "multi-region-expansion",
    "hybrid-cloud-integration",
    "ci-cd-pipeline",
    "monitoring-overhaul",
    "backup-strategy",
    "zero-trust-implementation",
    "api-gateway-deployment",
    "container-platform",
    "serverless-transformation",
    "database-consolidation",
    "network-segmentation",
    "identity-federation",
]

operations = [
    "upgrade de versão",
    "aplicação de patch",
    "alteração de charset",
    "criação de índice",
    "reorganização de tabela",
    "backup completo",
]

environments = [
    "production",
    "development",
    "staging",
    "security",
    "shared-services",
    "analytics",
    "data-platform",
    "devops",
    "sandbox",
]

examples = []
for i in range(250):
    company = random.choice(companies)
    persona = random.choice(personas)
    region = random.choice(regions)
    difficulty = random.choice(difficulties)
    project = random.choice(projects)
    constraint = random.choice(constraints)
    lifecycle = random.choice(lifecycle_patterns)
    intent = random.choice(intent_patterns)
    db_type, db_keyword, oci_service = random.choice(migration_topics)
    error = random.choice(errors)
    environment = random.choice(environments)
    operation = random.choice(operations)

    ocpus = random.choice([2, 4, 8, 16])
    storage = random.choice([1, 2, 4])
    license = random.choice(["INCLUDED", "BRING_YOUR_FIRST_LICENSE"])
    workload_type = random.choice(["OLTP", "OLAP"])

    q_template = random.choice(question_templates)
    a_template = random.choice(answer_templates)

    question = q_template.format(
        persona=persona,
        company=company,
        project=project,
        environment=environment,
        region=region,
        constraint=constraint,
        db_type=db_type,
        oci_service=oci_service,
        error=error,
        lifecycle=lifecycle,
        operation=operation,
    )

    answer = a_template.format(
        company=company,
        project=project,
        environment=environment,
        region=region,
        constraint=constraint,
        db_type=db_type,
        oci_service=oci_service,
        ocpus=ocpus,
        storage=storage,
        license=license,
        workload_type=workload_type,
        error=error,
    )

    example = {
        "question": question,
        "answer": answer,
        "metadata": {
            "category": "migration/onprem-database",
            "difficulty": difficulty,
            "persona": persona,
            "intent": intent,
            "lifecycle": lifecycle,
        },
    }
    examples.append(example)

with open(
    "/Users/otaviolemos/ml/olia-2-oci/data/curated/migration-onprem-database.jsonl",
    "w",
    encoding="utf-8",
) as f:
    for ex in examples:
        f.write(json.dumps(ex, ensure_ascii=False) + "\n")

print(f"Generated {len(examples)} examples")
print("File saved to data/curated/migration-onprem-database.jsonl")
