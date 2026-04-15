import json
import random
import os

random.seed(42)


def generate_examples(file_name, topics, num_examples=180):
    beginner = int(num_examples * 0.30)
    intermediate = int(num_examples * 0.50)
    advanced = num_examples - beginner - intermediate

    difficulties = (
        ["beginner"] * beginner
        + ["intermediate"] * intermediate
        + ["advanced"] * advanced
    )
    random.shuffle(difficulties)

    personas = [
        "cloud architect",
        "devops engineer",
        "dba",
        "platform engineer",
        "sre",
        "security lead",
        "finops analyst",
        "auditor",
    ]
    intents = [
        "design",
        "migrate",
        "troubleshoot",
        "optimize",
        "audit",
        "recover",
        "standardize",
        "compare",
        "review",
        "remediate",
    ]
    lifecycles = [
        "greenfield",
        "brownfield",
        "production",
        "staging",
        "development",
        "migration",
        "expansao",
        "desativacao",
        "incidente",
        "auditoria",
    ]

    examples = []

    for i in range(num_examples):
        difficulty = difficulties[i]
        persona = random.choice(personas)
        intent = random.choice(intents)
        lifecycle = random.choice(lifecycles)

        if file_name == "migration-onprem-compute":
            topic = random.choice(topics)
            question = generate_migration_compute_question(topic)
            answer = generate_migration_compute_answer(topic, difficulty)
            category = "migration/onprem-compute"
        elif file_name == "migration-onprem-database":
            topic = random.choice(topics)
            question = generate_migration_database_question(topic)
            answer = generate_migration_database_answer(topic, difficulty)
            category = "migration/onprem-database"
        elif file_name == "migration-onprem-storage":
            topic = random.choice(topics)
            question = generate_migration_storage_question(topic)
            answer = generate_migration_storage_answer(topic, difficulty)
            category = "migration/onprem-storage"
        elif file_name == "migration-onprem-vmware":
            topic = random.choice(topics)
            question = generate_migration_vmware_question(topic)
            answer = generate_migration_vmware_answer(topic, difficulty)
            category = "migration/onprem-vmware"
        elif file_name == "observability-apm":
            topic = random.choice(topics)
            question = generate_apm_question(topic)
            answer = generate_apm_answer(topic, difficulty)
            category = "observability/apm"

        example = {
            "question": question,
            "answer": answer,
            "metadata": {
                "category": category,
                "difficulty": difficulty,
                "persona": persona,
                "intent": intent,
                "lifecycle": lifecycle,
            },
        }
        examples.append(example)

    return examples


def generate_migration_compute_question(topic):
    scenarios = [
        "Como migrar " + topic + " do data center on-premises para OCI Compute?",
        "Preciso migrar 10 servidores " + topic + " para OCI. Quais os passos?",
        "Qual estrategia para migrar " + topic + " do nosso data center para OCI?",
        "Como fazer lift-and-shift de " + topic + " para OCI?",
        "Temos servidor "
        + topic
        + " rodando em data center on-premises. Como fazer a migracao?",
        "Como migrar VM " + topic + " do VMware para OCI sem refatorar aplicacao?",
        "Preciso migrar servidor " + topic + " do Hyper-V. Como comecar?",
        "Qual a melhor forma de migrar " + topic + " para OCI Compute?",
        "Migrar " + topic + ": quais pre-requisitos de compatibilidade?",
        "Como avaliar " + topic + " antes de migrar para OCI?",
    ]
    return random.choice(scenarios)


def generate_migration_compute_answer(topic, difficulty):
    if difficulty == "beginner":
        return (
            """Para migrar """
            + topic
            + """ para OCI Compute, siga estes passos:

## 1. Avaliacao Inicial

- Liste todos os servidores que serao migrados
- Verifique o sistema operacional (Oracle Linux, Ubuntu, CentOS, Windows sao suportados)
- Documente os requisitos de CPU, memoria e armazenamento

## 2. Preparacao no OCI

- Crie a VCN com subnets apropriadas
- Configure Security Lists para liberar as portas necessarias
- Crie o compartment para isolar os recursos

## 3. Migracao

- Use Custom Image para migrar VMs individuais
- Para multiplas VMs, considere OCI Migration Service
- Use `oci compute instance launch` para criar instancias

## 4. Pos-Migracao

- Valide a aplicacao e conectividade
- Configure backups com Block Volume Backups
- Configure monitoring com OCI Monitoring

**Nota**: [MUTABLE] Verifique os precos na calculadora OCI.
**Doc de referencia**: https://docs.oracle.com/en-us/iaas/Content/Compute/Tasks/computemoving.htm"""
        )

    elif difficulty == "intermediate":
        return (
            """Para migrar """
            + topic
            + """ para OCI Compute com abordagem estruturada:

## 1. Inventario e Analise

- Documente: SO, versao, dependencias, rede, armazenamento
- Use Oracle Migration Assessment para dimensionamento
- Mapeie portas necessarias e dependencias de rede
- Identifique shape adequado (VM.Standard.E4.Flex para x86)

## 2. Estrategia de Migracao

| Metodo | Quando Usar |
|--------|-------------|
| Custom Image | VMs individuais |
| Migration Service | Multiplas VMs |
| CLI/API | Automacao |
| Rsync/SCP | Dados apenas |

## 3. Execucao via CLI

```bash
oci compute image list --compartment-id <ocid> --query 'data[?operating-system==Oracle Linux].{name:display-name,id:id}'

oci compute instance launch --compartment-id <ocid> --display-name migrated-"""
            + topic
            + """ --shape VM.Standard.E4.Flex --subnet-id <subnet-ocid> --image-id <image-ocid> --shape-config '{"ocpus": 2, "memoryInGBs": 4}'
```

## 4. Validacao

- Teste funcional completo
- Valide conectividade de rede
- Configure alertas de monitoramento

**Nota**: [MUTABLE] Custos variam por shape e regiao.
**Doc de referencia**: https://docs.oracle.com/en-us/iaas/Content/Compute/Tasks/computemoving.htm"""
        )

    else:
        return (
            """Migracao enterprise de """
            + topic
            + """ para OCI Compute:

## Fase 1: Assessment Completo

```bash
oci compute instance list --compartment-id <ocid> --all
oci limits list-services --compartment-id <ocid>
oci limits value list --service-name compute --compartment-id <ocid>
```

## Fase 2: Design de Migracao

1. **Rede**: Configure VCN com subnets para App, DB, Mgmt
2. **Seguranca**: Use Security Lists e Network Security Groups
3. **Backup**: Configure Object Storage para long-term retention
4. **DR**: Configure standby em segunda regiao

## Fase 3: Implementacao

```bash
oci compute image create --compartment-id <ocid> --display-name custom-"""
            + topic
            + """-image --image-source-via-object-storage-uri <uri>

oci compute instance launch --compartment-id <ocid> --display-name prod-"""
            + topic
            + """ --shape VM.Standard.E4.Flex --subnet-id <subnet-ocid> --image-id <image-ocid> --shape-config '{"ocpus": 4, "memoryInGBs": 16}' --metadata '{"ssh_authorized_keys": "<pub-key>"}' --extended-metadata '{"user_data": "<cloud-init>"}'

oci bv backup policy create --compartment-id <ocid> --display-name backup-"""
            + topic
            + """ --backup-type FULL --schedule '{"timeOfDay": "02:00"}' --retention-days 30
```

## Fase 4: Cutover

1. Configure DNS cutover
2. Valide aplicacao com testes de regressao
3. Monitore metricas de performance
4. Documente no CMDB

**Nota**: [CHECK DOCS] Verifique limites de servico por regiao.
**Doc de referencia**: https://docs.oracle.com/en-us/iaas/Content/Compute/Tasks/computemoving.htm"""
        )


def generate_migration_database_question(topic):
    scenarios = [
        "Como migrar banco de dados " + topic + " para OCI?",
        "Preciso migrar "
        + topic
        + " do Oracle Exadata para Autonomous Database. Como fazer?",
        "Qual estrategia para migrar " + topic + " on-premises para OCI Database?",
        "Como fazer migracao do " + topic + " para OCI sem downtime?",
        "Temos " + topic + " rodando em servidor fisico. Como migrar para OCI?",
        "Migrar " + topic + ": quais ferramentas OCI usar?",
        "Como migrar " + topic + " com minima interrupcao?",
        "Qual a melhor forma de migrar " + topic + " para Autonomous Database?",
    ]
    return random.choice(scenarios)


def generate_migration_database_answer(topic, difficulty):
    if difficulty == "beginner":
        return (
            """Para migrar banco de dados """
            + topic
            + """ para OCI Database:

## 1. Avaliacao

- Identifique o banco de dados atual (Oracle, PostgreSQL, MySQL)
- Verifique versao e edicao
- Documente tamanho do banco e requisitos de performance

## 2. Opcoes de Migracao

- **Lift-and-shift**: Migracao direta para VM
- **Refatorar**: Migrar para Autonomous Database
- **Replatform**: Ajustar para OCI Database Service

## 3. Preparacao OCI

- Crie o Autonomous Database no Console OCI
- Configure VCN e subnets
- Prepare credenciais

## 4. Migracao

- Use Data Pump para Oracle
- Use pg_dump/pg_restore para PostgreSQL
- Use mysqldump para MySQL

**Nota**: [MUTABLE] Verifique precos do Autonomous Database.
**Doc de referencia**: https://docs.oracle.com/en-us/iaas/Content/Database/Tasks/migratingoverview.htm"""
        )

    elif difficulty == "intermediate":
        return (
            """Migracao de """
            + topic
            + """ para OCI Database:

## 1. Analise de Compatibilidade

```bash
SELECT version();
SELECT datname, pg_size_pretty(pg_database_size(datname)) FROM pg_database;
```

## 2. Criar Autonomous Database

```bash
oci db autonomous-database create --compartment-id <ocid> --display-name migrated-"""
            + topic
            + """ --db-name <dbname> --cpu-core-count 2 --data-storage-size-in-tb 1 --db-workload OLTP --license-model BRING_YOUR_OWN_LICENSE
```

## 3. Migracao de Dados

**Para Oracle:**
```bash
expdp full=y directory=dpump_dir dumpfile=full.dmp
impdp full=y directory=dpump_dir dumpfile=full.dmp remap_schema=old:new table_exists_action=replace
```

**Para PostgreSQL:**
```bash
export PGPASSWORD=<password>
pg_dump -h <source> -U <user> -d <db> -f backup.sql
psql -h <oci-endpoint> -U <user> -d <db> -f backup.sql
```

## 4. Validacao

- Execute testes funcionais
- Valide performance
- Configure backup automatico

**Nota**: [MUTABLE] Precoss variam por CPU e storage.
**Doc de referencia**: https://docs.oracle.com/en-us/iaas/Content/Database/Tasks/migratingoverview.htm"""
        )

    else:
        return (
            """Migracao enterprise de """
            + topic
            + """ para OCI Database:

## Fase 1: Assessment Detalhado

```bash
echo "SELECT COUNT(*) FROM dba_objects WHERE status = 'INVALID';" | sqlplus / as sysdba
echo "SELECT * FROM dba_dependencies WHERE referenced_owner NOT IN (USER, 'SYS', 'SYSTEM');" | sqlplus / as sysdba
SELECT tablespace_name, ROUND(SUM(bytes)/1024/1024/1024, 2) GB FROM dba_data_files GROUP BY tablespace_name;
```

## Fase 2: Estrategia de Migracao

| Fase | Atividade | Ferramenta |
|------|-----------|------------|
| Pre-migracao | Analise compatibilidade | Oracle SQL Developer |
| Migracao | Export/Import | Data Pump |
| Migracao | Replication | GoldenGate |
| Validacao | Testes | SQL Developer |

## Fase 3: Execucao

```bash
oci db autonomous-database create --compartment-id <ocid> --display-name prod-"""
            + topic
            + """ --db-name <dbname> --cpu-core-count 4 --data-storage-size-in-tb 2 --db-workload OLTP --license-model INCLUDED --whitelisted-ips '["10.0.0.0/16"]' --auto-scaling-enabled true

oci db autonomous-database create-data-guard --autonomous-database-id <primary-ocid> --display-name prod-"""
            + topic
            + """-dg

oci db autonomous-database update --autonomous-database-id <ocid> --backup-config '{"backup-destination-type": ["OBJECT_STORAGE"], "object-storage-container": "oracle-db-backups"}'
```

## Fase 4: Cutover com Minima Interrupcao

1. Configure GoldenGate replication
2. Sincronize dados delta
3. Aplique cutover planejado
4. Valide aplicacao completa

**Nota**: [CHECK DOCS] Verifique limites de CPU e storage.
**Doc de referencia**: https://docs.oracle.com/en-us/iaas/Content/Database/Tasks/migratingoverview.htm"""
        )


def generate_migration_storage_question(topic):
    scenarios = [
        "Como migrar armazenamento " + topic + " para OCI?",
        "Preciso migrar dados do NAS para File Storage. Como fazer?",
        "Qual estrategia para migrar " + topic + " para OCI Block Volume?",
        "Como migrar dados SAN para OCI Storage?",
        "Temos storage " + topic + " on-premises. Como migrar para OCI?",
        "Migrar " + topic + ": quais opcoes de transferencia?",
    ]
    return random.choice(scenarios)


def generate_migration_storage_answer(topic, difficulty):
    if difficulty == "beginner":
        return (
            """Para migrar """
            + topic
            + """ para OCI Storage:

## 1. Avaliacao

- Identifique tipo de storage atual (NAS, SAN, local)
- Documente capacidade e requisitos de performance
- Liste protocolos usados (NFS, SMB, iSCSI)

## 2. Opcoes OCI

- **File Storage**: Para NFS/SMB
- **Block Volume**: Para iSCSI
- **Object Storage**: Para dados nao estruturados

## 3. Migracao

- Use OCI File Storage para compartilhamentos NFS
- Use OCI Block Volume para storage de bloco
- Configure mount points e acesso

**Nota**: [MUTABLE] Verifique precos de storage.
**Doc de referencia**: https://docs.oracle.com/en-us/iaas/Content/FileStorage/overview.htm"""
        )

    elif difficulty == "intermediate":
        return (
            """Migracao de """
            + topic
            + """ para OCI Storage:

## 1. Analise

```bash
df -h
ls -la <path>
du -sh <path>
```

## 2. Criar File Storage

```bash
oci fs file-system create --compartment-id <ocid> --display-name migrated-"""
            + topic
            + """ --availability-domain <ad>

oci fs mount-target create --compartment-id <ocid> --file-system-id <fs-ocid> --subnet-id <subnet-ocid> --display-name mt-"""
            + topic
            + """

oci fs mount-target list --file-system-id <fs-ocid> --query 'data[0]."export-path"'
```

## 3. Transferencia de Dados

```bash
rsync -avz /source/ <mount-target-ip>:/mount/

oci os object put --namespace <ns> --bucket-name <bucket> --file-path /local/file --object-name remote/file
```

## 4. Configuracao

- Configure snapshots
- Configure backup para Object Storage
- Monte em instancias

**Nota**: [MUTABLE] Precoss variam por tipo de storage.
**Doc de referencia**: https://docs.oracle.com/en-us/iaas/Content/FileStorage/overview.htm"""
        )

    else:
        return (
            """Migracao enterprise de """
            + topic
            + """ para OCI Storage:

## Fase 1: Assessment

```bash
iostat -x 5
find /data -type f | wc -l
du -sh /data/*
```

## Fase 2: Design

1. **File Storage**: Configure para NFS com alta disponibilidade
2. **Block Volume**: Configure para iSCSI com performance adequada
3. **Object Storage**: Configure lifecycle policies

## Fase 3: Implementacao

```bash
oci fs file-system create --compartment-id <ocid> --display-name prod-"""
            + topic
            + """ --availability-domain <ad> --metered-bytes <size>

oci fs mount-target create --compartment-id <ocid> --file-system-id <fs-ocid> --subnet-id <subnet-ocid> --display-name prod-mt-"""
            + topic
            + """ --nsg-ids '["<nsg-ocid>"]'

oci fs export create --file-system-id <fs-ocid> --mount-target-id <mt-ocid> --export-path /"""
            + topic
            + """ --options '{"access": "READ_WRITE", "requires": []}'

oci bv volume create --compartment-id <ocid> --display-name prod-"""
            + topic
            + """ --size-in-gbs 1024 --vpus-per-gb 10 --backup-policy-ids '["<backup-policy-ocid>"]'
```

## Fase 4: Transferencia e Validacao

1. Use parallella rsync para transferencia
2. Configure parallel file system
3. Valide performance com fio
4. Configure monitoring

**Nota**: [CHECK DOCS] Verifique limites de storage por regiao.
**Doc de referencia**: https://docs.oracle.com/en-us/iaas/Content/FileStorage/overview.htm"""
        )


def generate_migration_vmware_question(topic):
    scenarios = [
        "Como migrar ambiente VMware para OCI?",
        "Preciso migrar VMs do VMware para OCI usando HCX. Como fazer?",
        "Qual estrategia para migrar " + topic + " para AVS?",
        "Como usar OCI AVS para migracao VMware?",
        "Temos VMware on-premises. Como migrar para OCI?",
    ]
    return random.choice(scenarios)


def generate_migration_vmware_answer(topic, difficulty):
    if difficulty == "beginner":
        return (
            """Para migrar ambiente VMware """
            + topic
            + """ para OCI:

## 1. Avaliacao

- Documente inventario de VMs
- Identifique requisitos de CPU, memoria, storage
- Mapeie dependencias de rede

## 2. Opcoes de Migracao

- **OCI AVS**: VMware as a Service
- **HCX**: Hybrid Mobility
- **Lift-and-shift**: Compute Instance

## 3. Preparacao

- Configure OCI AVS ou migration service
- Prepare rede e conectividade

## 4. Migracao

- Use HCX para migracao ao vivo
- Configure rede no OCI

**Nota**: [MUTABLE] Verifique precos OCI AVS.
**Doc de referencia**: https://docs.oracle.com/en-us/iaas/Content/vmware/overview.htm"""
        )

    elif difficulty == "intermediate":
        return (
            """Migracao de VMware """
            + topic
            + """ para OCI:

## 1. Preparacao HCX

```bash
vmware -v
esxcli system version get
```

## 2. Configurar OCI AVS

```bash
oci avs sddc create --compartment-id <ocid> --display-name avs-"""
            + topic
            + """ --esxi-hosts <num-hosts> --vmware-vsan-num-hosts <num> --vmware-version vSphere-7.0

oci avs sddc list --compartment-id <ocid>
```

## 3. Configurar HCX

1. Deploy HCX Appliance no vCenter on-premises
2. Configure HCX Cloud Gateway
3. Configure Network Profile
4. Configure Compute Profile

## 4. Migracao

```bash
hcx migration create --source-vm <vm-id> --target-sddc <sddc-ocid> --migration-type BULK

hcx migration status --group-id <group-id>
```

**Nota**: [MUTABLE] Custos variam por host e configuracao.
**Doc de referencia**: https://docs.oracle.com/en-us/iaas/Content/vmware/overview.htm"""
        )

    else:
        return (
            """Migracao enterprise de VMware """
            + topic
            + """ para OCI:

## Fase 1: Assessment VMware

```bash
Get-VM | Select Name, NumCPU, MemoryGB, Harddisks | Export-Csv vm-inventory.csv
Get-VM | Get-NetworkAdapter
Get-VM | Get-Datastore
```

## Fase 2: Design AVS

1. **SDDC**: Configure clusters com ESXi
2. **Rede**: Configure NSX-T networking
3. **Storage**: Configure vSAN ou use Block Volume
4. **DR**: Configure vSphere Replication

## Fase 3: Implementacao

```bash
oci avs sddc create --compartment-id <ocid> --display-name prod-avs-"""
            + topic
            + """ --esxi-hosts 3 --vmware-vsan-num-hosts 3 --vmware-version vSphere-8.0 --network-config '{"vc": "10.0.0.0/22", "nsx": "10.0.4.0/23"}' --ssh-public-keys '["<key>"]'

oci avs hcx-enterprise enable --sddc-id <sddc-ocid>

oci avs network-profile create --sddc-id <sddc-ocid> --display-name prod-np-"""
            + topic
            + """ --vc-domain-config '{"dns": ["10.0.0.2"], "ntp": ["10.0.0.3"]}'
```

## Fase 4: Migracao em Lote

1. Configure Replication for critical VMs
2. Execute migracao em waves
3. Valide cada wave
4. Execute cutover final

**Nota**: [CHECK DOCS] Verifique limites AVS por regiao.
**Doc de referencia**: https://docs.oracle.com/en-us/iaas/Content/vmware/overview.htm"""
        )


def generate_apm_question(topic):
    scenarios = [
        "Como configurar APM para monitorar aplicacoes " + topic + "?",
        "Preciso configurar distributed tracing para " + topic + ". Como fazer?",
        "Qual estrategia para implementar APM no projeto " + topic + "?",
        "Como monitorar performance de " + topic + " com OCI APM?",
        "Como analisar latency de " + topic + " com APM?",
    ]
    return random.choice(scenarios)


def generate_apm_answer(topic, difficulty):
    if difficulty == "beginner":
        return (
            """Para configurar APM para """
            + topic
            + """:

## 1. Criar APM Domain

- Acesse o console OCI
- Navegue ate APM
- Crie um novo APM Domain
- Anote o endpoint de coleta

## 2. Instrumentar Aplicacao

- Adicione o agente APM ao seu codigo
- Configure o Application Specific Reporter
- Defina nome do servico

## 3. Visualizar Dados

- Acesse o APM Dashboard
- Visualize service maps
- Analise traces e spans

## 4. Configurar Alertas

- Crie alertas para latencia e erros
- Configure notificacoes

**Nota**: [MUTABLE] Verifique precos do APM.
**Doc de referencia**: https://docs.oracle.com/en-us/iaas/Content/apm/overview.htm"""
        )

    elif difficulty == "intermediate":
        return (
            """Configurar APM para """
            + topic
            + """:

## 1. Criar APM Domain via CLI

```bash
oci apm domain create --compartment-id <ocid> --display-name apm-"""
            + topic
            + """ --description "APM for """
            + topic
            + """"

oci apm domain get --apm-domain-id <domain-ocid> --query 'data."apm-url"'
```

## 2. Configurar Agent

```bash
export APM_ENDPOINT=<endpoint>
export APM_SECRET_KEY=<key>
export SERVICE_NAME="""
            + topic
            + """
```

## 3. Criar Span Filter

```bash
oci apm span-filter create --apm-domain-id <domain-ocid> --display-name filter-"""
            + topic
            + """ --filter-config '{"type": "SpanFilter", "config": "span.name = ' + "'" + topic + "'" + '"}'
```

## 4. Configurar Alertas

```bash
oci monitoring alarm create --compartment-id <ocid> --display-name apm-latency-"""
            + topic
            + """ --metric-compartment-id <ocid> --namespace oci_apm --query "apm.latency[1m].mean() > 1000" --severity WARNING
```

**Nota**: [MUTABLE] Custos variam por spans ingeridos.
**Doc de referencia**: https://docs.oracle.com/en-us/iaas/Content/apm/overview.htm"""
        )

    else:
        return (
            """Configuracao enterprise de APM para """
            + topic
            + """:

## Fase 1: Design de Observabilidade

```
+---------+     +---------+     +---------+
| Application |-->|   APM Agent |-->| APM Domain  |
+---------+     +---------+     +---------+
                                      |
                                      v
                    +---------+     +---------+
                    |  Dashboard  |<--|  Traces     |
                    +---------+     +---------+
```

## Fase 2: Implementacao

```bash
oci apm domain create --compartment-id <ocid> --display-name prod-apm-"""
            + topic
            + """ --description "Production APM for """
            + topic
            + """" --retention-period-days 30 --tags '{"environment": "production"}'

oci apm domain get --apm-domain-id <domain-ocid> --query 'data.{"url": "apm-url", "key": "public-key"}'

oci apm span-filter create --apm-domain-id <domain-ocid> --display-name prod-filter-"""
            + topic
            + """ --filter-config '{"type": "SpanFilter", "config": "span.name contains ' + "'" + topic + "'" + '"}'

oci apm metric-group create --apm-domain-id <domain-ocid> --display-name custom-metrics-"""
            + topic
            + """ --metrics-def '{"columns": [{"name": "latency", "type": "DOUBLE"}]}'
```

## Fase 3: Integracao

1. Configure APM agent em todas as instancias
2. Configure sampling strategy
3. Configure context propagation
4. Configure error tracking

## Fase 4: Dashboards e Alertas

```bash
oci monitoring alarm create --compartment-id <ocid> --display-name prod-latency-"""
            + topic
            + """ --metric-compartment-id <ocid> --namespace oci_apm --query "apm.latency[1m].p99() > 500" --severity CRITICAL --destination-credentials '{"topicId": "<topic-ocid>"}' --repeat-notification-duration PT30M

oci monitoring alarm create --compartment-id <ocid> --display-name prod-errors-"""
            + topic
            + """ --metric-compartment-id <ocid> --namespace oci_apm --query "apm.error.count[5m].sum() > 10" --severity CRITICAL
```

**Nota**: [CHECK DOCS] Verifique limites de spans por dominio.
**Doc de referencia**: https://docs.oracle.com/en-us/iaas/Content/apm/overview.htm"""
        )


# Generate all files
files_config = [
    (
        "migration-onprem-compute",
        ["VMs", "VMware ESXi", "Hyper-V", "bare metal", "vCenter"],
    ),
    (
        "migration-onprem-database",
        ["Oracle DB", "PostgreSQL", "MySQL", "SQL Server", "Autonomous"],
    ),
    (
        "migration-onprem-storage",
        ["NAS", "File Storage", "SAN", "Block Volume", "Object Storage"],
    ),
    ("migration-onprem-vmware", ["VMware", "HCX", "AVS", "vSphere", "NSX"]),
    ("observability-apm", ["APM", "Tracing", "Metrics", "Spans", "Service Maps"]),
]

output_dir = "/Users/otaviolemos/ml/olia-2-oci/data/curated"
os.makedirs(output_dir, exist_ok=True)

for file_name, topics in files_config:
    examples = generate_examples(file_name, topics)
    with open(f"{output_dir}/{file_name}.jsonl", "w", encoding="utf-8") as f:
        for ex in examples:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")
    print(f"Generated {file_name}: {len(examples)} examples")

print("All files generated successfully!")
