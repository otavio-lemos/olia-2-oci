#!/usr/bin/env python3
"""
Generate all 56 remaining JSONL files for OCI Specialist LLM dataset.
Each file contains exactly 10 examples with proper difficulty distribution.
"""

import json
import os

OUTPUT_DIR = "/Users/otaviolemos/ml/olia-2-oci/data/curated"

# System prompts for each category group
SYSTEM_PROMPTS = {
    "database": "You are an OCI specialist with expertise in database services. Provide technical guidance on database architecture, configuration, and management.",
    "database-exadata": "You are an OCI specialist with expertise in Exadata Cloud Service. Provide technical guidance on Exadata infrastructure, DB systems, and maintenance.",
    "container": "You are an OCI specialist with expertise in container services. Provide technical guidance on OKE, container instances, and orchestration.",
    "serverless": "You are an OCI specialist with expertise in serverless computing. Provide technical guidance on Functions, API Gateway, and event-driven architectures.",
    "security": "You are an OCI security specialist with expertise in OCI security services. Provide technical guidance on IAM, encryption, and security monitoring.",
    "security-iam": "You are an OCI security specialist with expertise in IAM. Provide technical guidance on users, groups, policies, and access control.",
    "security-vault": "You are an OCI security specialist with expertise in Vault service. Provide technical guidance on secrets management and key management.",
    "security-encryption": "You are an OCI security specialist with expertise in encryption. Provide technical guidance on encryption at rest, in transit, and key management.",
    "security-monitoring": "You are an OCI security specialist with expertise in security monitoring. Provide technical guidance on Cloud Guard, security zones, and threat detection.",
    "migration": "You are an OCI migration specialist with expertise in cloud migration. Provide technical guidance on migration strategies, tools, and best practices.",
    "migration-aws": "You are an OCI migration specialist with expertise in AWS to OCI migrations. Provide technical guidance on compute, storage, and database migration.",
    "migration-azure": "You are an OCI migration specialist with expertise in Azure to OCI migrations. Provide technical guidance on compute, storage, and database migration.",
    "migration-gcp": "You are an OCI migration specialist with expertise in GCP to OCI migrations. Provide technical guidance on compute, storage, and database migration.",
    "migration-onprem": "You are an OCI migration specialist with expertise in on-premises to OCI migrations. Provide technical guidance on lift-and-shift and modernization.",
    "terraform": "You are an OCI Terraform specialist with expertise in Infrastructure as Code. Provide technical guidance on Terraform provider, resources, and best practices.",
    "observability": "You are an OCI observability specialist with expertise in monitoring and logging. Provide technical guidance on OCI observability stack.",
    "troubleshooting": "You are an OCI troubleshooting specialist with expertise in diagnosing and resolving issues. Provide technical guidance on common OCI problems.",
    "devops": "You are an OCI DevOps specialist with expertise in CI/CD and automation. Provide technical guidance on OCI DevOps services and practices.",
}

# Category mappings
CATEGORY_MAP = {
    "database-autonomous-json": "database/autonomous-json",
    "database-exadata": "database/exadata",
    "container-instances": "container/instances",
    "serverless-functions": "serverless/functions",
    "serverless-api-gateway": "serverless/api-gateway",
    "security-iam-basics": "security/iam-basics",
    "security-policies": "security/policies",
    "security-dynamic-groups": "security/dynamic-groups",
    "security-federation": "security/federation",
    "security-vault-secrets": "security/vault-secrets",
    "security-vault-keys": "security/vault-keys",
    "security-encryption": "security/encryption",
    "security-cloud-guard": "security/cloud-guard",
    "security-waf": "security/waf",
    "migration-aws-compute": "migration/aws-compute",
    "migration-aws-storage": "migration/aws-storage",
    "migration-aws-database": "migration/aws-database",
    "migration-azure-compute": "migration/azure-compute",
    "migration-azure-storage": "migration/azure-storage",
    "migration-azure-database": "migration/azure-database",
    "migration-gcp-compute": "migration/gcp-compute",
    "migration-gcp-storage": "migration/gcp-storage",
    "migration-gcp-database": "migration/gcp-database",
    "migration-onprem-compute": "migration/onprem-compute",
    "migration-onprem-storage": "migration/onprem-storage",
    "migration-onprem-vmware": "migration/onprem-vmware",
    "migration-onprem-database": "migration/onprem-database",
    "migration-data-transfer": "migration/data-transfer",
    "terraform-provider": "terraform/provider",
    "terraform-compute": "terraform/compute",
    "terraform-storage": "terraform/storage",
    "terraform-networking": "terraform/networking",
    "terraform-load-balancer": "terraform/load-balancer",
    "terraform-database": "terraform/database",
    "terraform-container": "terraform/container",
    "terraform-serverless": "terraform/serverless",
    "terraform-security": "terraform/security",
    "terraform-observability": "terraform/observability",
    "terraform-devops": "terraform/devops",
    "terraform-state": "terraform/state",
    "observability-logging": "observability/logging",
    "observability-monitoring": "observability/monitoring",
    "observability-stack-monitoring": "observability/stack-monitoring",
    "observability-apm": "observability/apm",
    "troubleshooting-connectivity": "troubleshooting/connectivity",
    "troubleshooting-performance": "troubleshooting/performance",
    "troubleshooting-authentication": "troubleshooting/authentication",
    "troubleshooting-database": "troubleshooting/database",
    "troubleshooting-compute": "troubleshooting/compute",
    "troubleshooting-storage": "troubleshooting/storage",
    "troubleshooting-oke": "troubleshooting/oke",
    "troubleshooting-functions": "troubleshooting/functions",
    "devops-ci-cd": "devops/ci-cd",
    "devops-resource-manager": "devops/resource-manager",
    "devops-artifacts": "devops/artifacts",
    "devops-secrets": "devops/secrets",
}

def get_system_prompt(category):
    """Get appropriate system prompt for category."""
    if "database" in category:
        if "exadata" in category:
            return SYSTEM_PROMPTS["database-exadata"]
        if "autonomous" in category:
            return SYSTEM_PROMPTS["database"]
        return SYSTEM_PROMPTS["database"]
    if "container" in category:
        if "instances" in category:
            return SYSTEM_PROMPTS["container"]
        return SYSTEM_PROMPTS["container"]
    if "serverless" in category:
        return SYSTEM_PROMPTS["serverless"]
    if "security" in category:
        if "iam" in category:
            return SYSTEM_PROMPTS["security-iam"]
        if "vault" in category:
            return SYSTEM_PROMPTS["security-vault"]
        if "encryption" in category:
            return SYSTEM_PROMPTS["security-encryption"]
        if "cloud-guard" in category or "waf" in category:
            return SYSTEM_PROMPTS["security-monitoring"]
        return SYSTEM_PROMPTS["security"]
    if "migration" in category:
        if "aws" in category:
            return SYSTEM_PROMPTS["migration-aws"]
        if "azure" in category:
            return SYSTEM_PROMPTS["migration-azure"]
        if "gcp" in category:
            return SYSTEM_PROMPTS["migration-gcp"]
        if "onprem" in category:
            return SYSTEM_PROMPTS["migration-onprem"]
        return SYSTEM_PROMPTS["migration"]
    if "terraform" in category:
        return SYSTEM_PROMPTS["terraform"]
    if "observability" in category:
        return SYSTEM_PROMPTS["observability"]
    if "troubleshooting" in category:
        return SYSTEM_PROMPTS["troubleshooting"]
    if "devops" in category:
        return SYSTEM_PROMPTS["devops"]
    return SYSTEM_PROMPTS["database"]

def create_example(category, difficulty, question, answer):
    """Create a single JSONL example."""
    return {
        "messages": [
            {"role": "system", "content": get_system_prompt(category)},
            {"role": "user", "content": question},
            {"role": "assistant", "content": answer}
        ],
        "metadata": {
            "category": CATEGORY_MAP.get(category, category),
            "difficulty": difficulty,
            "source": "generated"
        }
    }

# Data generation functions for each category group
def generate_database_autonomous_json_examples():
    """Generate examples for database-autonomous-json."""
    examples = []
    
    # Beginner (3)
    examples.append(create_example("database-autonomous-json", "beginner",
        "O que é Autonomous JSON Database?",
        "Autonomous JSON Database é um serviço gerenciado da OCI otimizado para cargas de trabalho JSON e documentos.\n\n**Características principais:**\n- Armazenamento nativo JSON\n- Indexação automática\n- Escalabilidade elástica\n- Patching automático\n\n**Casos de uso:**\n- Aplicações NoSQL\n- Catálogos de produtos\n- Perfis de usuário\n- Conteúdo dinâmico\n\n[MUTABLE] Preços variam por OCPU e armazenamento."))
    
    examples.append(create_example("database-autonomous-json", "beginner",
        "Como criar um Autonomous JSON Database?",
        "Para criar um Autonomous JSON Database:\n\n1. No Console, vá para Oracle Database → Autonomous Database\n2. Clique em 'Create Autonomous Database'\n3. Selecione 'Autonomous JSON Database'\n4. Configure:\n   - Compartment\n   - Display name\n   - OCPU count (mínimo 1)\n   - Storage (mínimo 20 GB)\n5. Defina admin password\n6. Escolha rede (pública ou privada)\n7. Clique em 'Create'\n\n[CHECK DOCS] Limites de OCPU variam por tenancy."))
    
    examples.append(create_example("database-autonomous-json", "beginner",
        "Qual a diferença entre Autonomous JSON e Transaction Processing?",
        "Diferenças principais:\n\n**Autonomous JSON Database:**\n- Otimizado para JSON/documentos\n- SODA API (Simple Oracle Document Access)\n- Melhor para dados semi-estruturados\n- Indexação JSON automática\n\n**Autonomous Transaction Processing:**\n- Otimizado para transações OLTP\n- SQL tradicional\n- Melhor para dados relacionais\n- Controle manual de índices\n\nEscolha JSON para: catálogos, logs, conteúdo dinâmico\nEscolha TP para: sistemas transacionais, ERP, CRM"))
    
    # Intermediate (5)
    examples.append(create_example("database-autonomous-json", "intermediate",
        "Como inserir documentos JSON via SODA?",
        "Inserindo documentos via SODA Driver for Python:\n\n```python\nimport oracledb\n\n# Conexão\nconn = oracledb.connect(\n    user='admin',\n    password='***',\n    dsn='(description=...)'\n)\n\n# SODA Collection\ncollection = conn.getSodaDatabase().createCollection('products')\n\n# Inserir documento\ndoc = {\n    'name': 'Laptop',\n    'price': 999,\n    'specs': {'cpu': 'i7', 'ram': '16GB'}\n}\nresult = collection.insertOne(doc)\nprint(f'Document ID: {result.getKey()}')\n```\n\nSODA abstrai SQL e trabalha diretamente com JSON."))
    
    examples.append(create_example("database-autonomous-json", "intermediate",
        "Como consultar documentos JSON?",
        "Consultando com SODA e SQL:\n\n**Via SODA (Python):**\n```python\n# Find by field\nresults = collection.find().filter({'name': 'Laptop'}).getDocuments()\n\n# Find with operator\nresults = collection.find().filter({'price': {'$gt': 500}}).getDocuments()\n```\n\n**Via SQL:**\n```sql\n-- Usando JSON_TABLE\nSELECT j.name, j.price\nFROM products p,\nJSON_TABLE(p.json_document, '$'\nCOLUMNS (name VARCHAR2(100) PATH '$.name',\n         price NUMBER PATH '$.price')) j\nWHERE j.price > 500;\n```\n\nSODA é mais simples para operações básicas."))
    
    examples.append(create_example("database-autonomous-json", "intermediate",
        "Como criar índices em coleções JSON?",
        "Criando índices para performance:\n\n**Via SODA:**\n```python\n# Índice em campo simples\ncollection.createIndex({'name': 'price_idx',\n    'fields': [{'path': 'price', 'datatype': 'number'}]})\n\n# Índice composto\ncollection.createIndex({'name': 'category_price_idx',\n    'fields': [\n        {'path': 'category', 'datatype': 'string'},\n        {'path': 'price', 'datatype': 'number'}\n    ]})\n```\n\n**Via SQL:**\n```sql\nCREATE INDEX price_idx ON products (json_document)\nINDENT IS JSON INDEX ON (price NUMBER);\n```\n\n[CHECK DOCS] Verifique limites de índices por coleção."))
    
    examples.append(create_example("database-autonomous-json", "intermediate",
        "Como fazer backup do Autonomous JSON?",
        "Backup e recuperação:\n\n**Automático (padrão):**\n- Backups automáticos diários\n- Retenção de 60 dias\n- Point-in-time recovery\n\n**Manual via Console:**\n1. Database Details → More Actions\n2. 'Create Manual Backup'\n3. Aguarde conclusão\n\n**Via CLI:**\n```bash\noci db autonomous-database create-backup \\\n  --autonomous-database-id <ocid> \\\n  --type MANUAL\n```\n\n**Restore:**\n- Point-in-time via Console\n- Restore para novo timestamp\n\n[MUTABLE] Backup adicional pode ter custos."))
    
    examples.append(create_example("database-autonomous-json", "intermediate",
        "Como escalar OCPU e storage?",
        "Scaling elástico:\n\n**Via Console:**\n1. Database Details → Scale Resources\n2. Ajuste OCPU ou Storage\n3. Apply\n\n**Via CLI:**\n```bash\noci db autonomous-database update \\\n  --autonomous-database-id <ocid> \\\n  --cpu-count 8 \\\n  --storage-size-in-tbs 1\n```\n\n**Características:**\n- Scale up: imediato (segundos)\n- Scale down: imediato\n- Sem downtime\n- Cobrança proporcional\n\n**Auto-scaling:**\n- Até 3x OCPU base\n- Habilitar em Database Details\n\n[MUTABLE] Preços por OCPU/hora variam."))
    
    # Advanced (2)
    examples.append(create_example("database-autonomous-json", "advanced",
        "Como migrar MongoDB para Autonomous JSON?",
        "Migração MongoDB → Autonomous JSON:\n\n**1. Análise:**\n- Mapeie coleções → tabelas\n- Documentos → colunas JSON\n- Queries → SODA ou SQL\n\n**2. Extração:**\n```bash\n# MongoDB export\nmongodump --uri=\"mongodb://...\" --out=/backup\n```\n\n**3. Transformação:**\n- Converta BSON para JSON\n- Ajuste tipos de dados\n- Normalize IDs (_id → id)\n\n**4. Carga:**\n```python\n# Python SODA load\nfor doc in json_docs:\n    collection.insertOne(doc)\n```\n\n**5. Validação:**\n- Compare contagens\n- Teste queries críticas\n- Valide performance\n\n**Riscos:** Queries complexas podem precisar reescrita."))
    
    examples.append(create_example("database-autonomous-json", "advanced",
        "Como otimizar performance de queries JSON?",
        "Otimização de performance:\n\n**1. Índices estratégicos:**\n```python\n# Índice em campos frequentemente consultados\ncollection.createIndex({\n    'fields': [\n        {'path': 'status', 'datatype': 'string'},\n        {'path': 'created_at', 'datatype': 'date'}\n    ]\n})\n```\n\n**2. Evite full collection scan:**\n```python\n# RUIM: scan completo\nresults = collection.find().getDocuments()\n\n# BOM: com filtro\nresults = collection.find().filter({'status': 'active'}).getDocuments()\n```\n\n**3. Projection (traga só necessário):**\n```python\nresults = collection.find().fields({'name': 1, 'price': 1}).getDocuments()\n```\n\n**4. Monitoramento:**\n- Use Performance Hub\n- Identifique queries lentas\n- Ajuste índices conforme uso\n\n**Trade-offs:** Índices aceleram leitura, desaceleram escrita."))
    
    return examples

def generate_database_exadata_examples():
    """Generate examples for database-exadata."""
    examples = []
    
    # Beginner (3)
    examples.append(create_example("database-exadata", "beginner",
        "O que é Exadata Cloud Service?",
        "Exadata Cloud Service é a infraestrutura de banco de dados de alta performance da Oracle na nuvem.\n\n**Características:**\n- Hardware Exadata dedicado\n- Smart Scan para queries\n- Storage cells com flash\n- Rede RDMA de baixa latência\n\n**Tipos:**\n- Exadata Cloud Service (dedicado)\n- Exadata Cloud@Customer (no seu datacenter)\n- Autonomous Database on Exadata (compartilhado)\n\n**Casos de uso:**\n- Data warehouses grandes\n- OLTP de alta transação\n- Consolidação de databases\n\n[MUTABLE] Preços variam por configuração."))
    
    examples.append(create_example("database-exadata", "beginner",
        "Como provisionar um DB system no Exadata?",
        "Provisionando DB system:\n\n1. Console → Oracle Database → Exadata\n2. Selecione Exadata Infrastructure\n3. 'Create VM Cluster'\n4. Configure:\n   - VM Cluster name\n   - Shape (ex: Exadata.X9M)\n   - Número de nós\n   - Storage allocation\n5. Crie o DB System:\n   - Database name\n   - Edition (Enterprise/Standard)\n   - Admin credentials\n6. Review e Create\n\n[CHECK DOCS] Disponibilidade de shapes varia por região."))
    
    examples.append(create_example("database-exadata", "beginner",
        "Quais shapes de Exadata estão disponíveis?",
        "Shapes Exadata (exemplos):\n\n**X9M (3ª geração):**\n- Exadata.X9M-2: 2 nós, 56 OCPUs\n- Exadata.X9M-4: 4 nós, 112 OCPUs\n- Exadata.X9M-8: 8 nós, 224 OCPUs\n\n**X8M:**\n- Exadata.X8M-2: 2 nós\n- Exadata.X8M-8: 8 nós\n\n**Características X9M:**\n- Intel Xeon de 3ª geração\n- 3TB memory por nó\n- 100Gb RDMA network\n- Persistent memory\n\n[CHECK DOCS] Disponibilidade e preços variam por região."))
    
    # Intermediate (5)
    examples.append(create_example("database-exadata", "intermediate",
        "Como funciona Smart Scan no Exadata?",
        "Smart Scan é o recurso de aceleração do Exadata:\n\n**Como funciona:**\n1. Query é enviada para storage cells\n2. Storage filtra dados antes de enviar\n3. Só dados relevantes vão para database\n4. Reduz I/O e network traffic\n\n**Benefícios:**\n- Redução de 10-50x em I/O\n- Menos CPU no database server\n- Queries full scan mais rápidas\n\n**Requisitos:**\n- Direct path read\n- Full table/index scan\n- Storage Indexes compatíveis\n\n**Exemplo:**\n```sql\n-- Smart Scan ativado para:\nSELECT * FROM sales WHERE amount > 1000;\n-- Storage filtra antes de enviar\n```"))
    
    examples.append(create_example("database-exadata", "intermediate",
        "Como fazer patching no Exadata?",
        "Patching do Exadata:\n\n**Via Console:**\n1. Exadata Infrastructure → Patching\n2. 'Schedule Patching'\n3. Selecione patches\n4. Agende janela de manutenção\n5. Execute\n\n**Via CLI:**\n```bash\noci db exadata-infrastructure update \\\n  --exadata-infrastructure-id <ocid> \\\n  --is-updated true\n```\n\n**Tipos de patch:**\n- Database patch (RU/RUR)\n- Infrastructure patch\n- Firmware update\n\n**Janela típica:** 2-4 horas\n**Impacto:** Rolling update (sem downtime total)\n\n[CHECK DOCS] Verifique release notes antes de aplicar."))
    
    examples.append(create_example("database-exadata", "intermediate",
        "Como monitorar performance do Exadata?",
        "Monitoramento de performance:\n\n**Console:**\n- Exadata Infrastructure → Metrics\n- VM Cluster → Performance Hub\n- Storage cells → I/O stats\n\n**Métricas chave:**\n- Cell I/O latency\n- Smart Scan efficiency\n- RDMA network throughput\n- Flash cache hit ratio\n\n**SQL de monitoramento:**\n```sql\nSELECT metric_name, metric_value \nFROM v$cellmetric \nWHERE metric_name LIKE '%SMART%';\n```\n\n**Alertas:**\n- Configure thresholds no Console\n- Integre com OCI Monitoring\n- Notificações via Email/Slack"))
    
    examples.append(create_example("database-exadata", "intermediate",
        "Como configurar backup no Exadata?",
        "Configuração de backup:\n\n**Recovery Appliance (ZDLA):**\n1. Provisione ZDLA virtual machine\n2. Configure network para DB system\n3. RMAN registra no ZDLA:\n```sql\nCONFIGURE CONTROLFILE AUTOBACKUP ON;\nCONFIGURE BACKUP OPTIMIZATION ON;\n```\n\n**Object Storage:**\n```sql\n-- Backup direto para Object Storage\nBACKUP DATABASE TO 'oci://bucket@namespace/db_backup';\n```\n\n**Via Console:**\n- Database → Backup → Create Backup\n- Automático: configure Backup Schedule\n\n**Best Practice:**\n- Backup diário incremental\n- Full semanal\n- Retenção de 30-60 dias\n\n[MUTABLE] Storage de backup tem custo adicional."))
    
    examples.append(create_example("database-exadata", "intermediate",
        "Como escalar um VM Cluster?",
        "Scaling de VM Cluster:\n\n**Scale Up (mais recursos por nó):**\n1. Console → VM Cluster → Scale\n2. Selecione novo shape\n3. Apply (requer restart)\n\n**Scale Out (mais nós):**\n1. VM Cluster → Add Node\n2. Selecione quantidade\n3. Configure network\n4. Add ao cluster\n\n**Considerações:**\n- Scale Out: sem downtime (rolling)\n- Scale Up: requer restart\n- Storage escala separadamente\n\n**Via CLI:**\n```bash\noci db vm-cluster add-node \\\n  --vm-cluster-id <ocid> \\\n  --number-of-nodes 2\n```\n\n[CHECK DOCS] Verifique quotas antes de escalar."))
    
    # Advanced (2)
    examples.append(create_example("database-exadata", "advanced",
        "Como migrar RAC on-premises para Exadata Cloud?",
        "Migração RAC → Exadata Cloud:\n\n**1. Planejamento:**\n- Mapeie topology RAC atual\n- Dimensione Exadata equivalente\n- Planeje network (FastConnect)\n\n**2. Método - Data Guard:**\n```sql\n-- On-premises:\nCREATE STANDBY DATABASE \n  FROM PRIMARY \\\n  VIA 'oci_exadata_target';\n```\n\n**3. Configuração:**\n- Configure Exadata target\n- Setup Data Guard replication\n- Sync inicial (pode levar horas/dias)\n\n**4. Cutover:**\n```sql\n-- Failover planejado:\nALTER DATABASE COMMIT TO SWITCHOVER TO STANDBY;\n```\n\n**5. Pós-migração:**\n- Valide performance\n- Ajuste parâmetros\n- Teste failback\n\n**Riscos:** Downtime no cutover, compatibilidade de versão."))
    
    examples.append(create_example("database-exadata", "advanced",
        "Como otimizar workload misto (OLTP + DW) no Exadata?",
        "Otimização de workload misto:\n\n**1. Resource Manager:**\n```sql\n-- Crie consumer groups\nBEGIN\n  DBMS_RESOURCE_MANAGER.CREATE_CONSUMER_GROUP(\n    consumer_group => 'OLTP_GROUP',\n    comment => 'OLTP workload');\n  DBMS_RESOURCE_MANAGER.CREATE_CONSUMER_GROUP(\n    consumer_group => 'DW_GROUP',\n    comment => 'Data warehouse');\nEND;\n/```\n\n**2. I/O Resource Management:**\n- OLTP: prioridade em I/O aleatório\n- DW: prioridade em Smart Scan\n\n**3. Memory allocation:**\n- SGA maior para OLTP\n- PGA maior para DW\n\n**4. Time-based:**\n- OLTP durante dia (business hours)\n- DW à noite (batch window)\n\n**Trade-offs:** Complexidade de tuning, monitoramento contínuo necessário."))
    
    return examples

def generate_container_instances_examples():
    """Generate examples for container-instances."""
    examples = []
    
    # Beginner (3)
    examples.append(create_example("container-instances", "beginner",
        "O que é OCI Container Instances?",
        "OCI Container Instances é um serviço serverless para executar containers sem gerenciar infraestrutura.\n\n**Características:**\n- Sem necessidade de clusters\n- Pay per second de execução\n- Scaling automático\n- Isolamento por sandbox\n\n**Casos de uso:**\n- Jobs batch\n- Processamento assíncrono\n- Dev/test rápido\n- Burst de capacidade\n\n**Diferença para OKE:**\n- Container Instances: serverless, sem cluster\n- OKE: Kubernetes completo, mais controle\n\n[MUTABLE] Preços por vCPU e memória."))
    
    examples.append(create_example("container-instances", "beginner",
        "Como criar um container instance?",
        "Criando container instance:\n\n**Via Console:**\n1. Developer Services → Container Instances\n2. 'Create Container Instance'\n3. Configure:\n   - Compartment\n   - Image (OCI Registry ou Docker Hub)\n   - Shape (CPU/Memory)\n   - Network (VCN, subnet)\n4. Environment variables (opcional)\n5. Create\n\n**Via CLI:**\n```bash\noci container-instance container-instance create \\\n  --compartment-id <ocid> \\\n  --display-name my-app \\\n  --image \"nginx:latest\" \\\n  --shape OCI.CI.E4.Flex\n```\n\n[CHECK DOCS] Shapes disponíveis variam por região."))
    
    examples.append(create_example("container-instances", "beginner",
        "Qual o custo do Container Instances?",
        "Modelo de pricing:\n\n**Cobrança:**\n- Por vCPU/segundo\n- Por GB de memória/segundo\n- Mínimo de 1 segundo\n\n**Exemplo [MUTABLE]:**\n- Shape: 4 vCPU, 16GB RAM\n- 1 hora de execução ≈ $X\n- Comparado a VM: mais econômico para cargas intermitentes\n\n**Custos adicionais:**\n- Object Storage (imagens)\n- Network egress\n- Container Registry\n\n**Otimização:**\n- Use shapes adequados\n- Termine instâncias ociosas\n- Agende execuções em batch\n\n[CHECK DOCS] Consulte pricing calculator atual."))
    
    # Intermediate (5)
    examples.append(create_example("container-instances", "intermediate",
        "Como passar variáveis de ambiente?",
        "Variáveis de ambiente:\n\n**Via Console:**\n- Container Instance → Environment Variables\n- Adicione key-value pairs\n\n**Via CLI:**\n```bash\noci container-instance container-instance create \\\n  --compartment-id <ocid> \\\n  --environment-variables '[{\"name\":\"DB_HOST\",\"value\":\"db.example.com\"},{\"name\":\"DB_PORT\",\"value\":\"5432\"}]' \\\n  --display-name my-app\n```\n\n**Secrets (recomendado para sensíveis):**\n```bash\noci container-instance container-instance create \\\n  --environment-variables-from-vault '[{\"name\":\"DB_PASSWORD\",\"vault_id\":\"<ocid>\",\"secret_name\":\"db-pass\"}]'\n```\n\n**Best Practice:** Nunca hardcode secrets no código ou imagens."))
    
    examples.append(create_example("container-instances", "intermediate",
        "Como conectar container à VCN?",
        "Conectividade de rede:\n\n**Requisitos:**\n1. VCN com subnet\n2. Security List permitindo tráfego\n3. Route Table configurada\n\n**Configuração:**\n```bash\noci container-instance container-instance create \\\n  --compartment-id <ocid> \\\n  --subnet-id <subnet-ocid> \\\n  --display-name my-app \\\n  --image \"nginx:latest\"\n```\n\n**Security List:**\n- Ingress: portas necessárias (ex: 80, 443)\n- Egress: 0.0.0.0/0 para internet\n\n**IPs:**\n- IP privado da subnet\n- IP público (se subnet for pública)\n\n**DNS:**\n- Automático da VCN\n- Custom DNS via /etc/resolv.conf"))
    
    examples.append(create_example("container-instances", "intermediate",
        "Como montar volumes no container?",
        "Montando volumes:\n\n**Block Volume:**\n```bash\noci container-instance container-instance create \\\n  --compartment-id <ocid> \\\n  --volume-mounts '[{\"name\":\"data\",\"mountPath\":\"/data\",\"blockVolumeId\":\"<ocid>\"}]' \\\n  --display-name my-app\n```\n\n**File Storage:**\n```bash\noci container-instance container-instance create \\\n  --compartment-id <ocid> \\\n  --volume-mounts '[{\"name\":\"shared\",\"mountPath\":\"/shared\",\"fileSystemId\":\"<ocid>\"}]'\n```\n\n**Tipos suportados:**\n- Block Volume (leitura/escrita)\n- File Storage (compartilhado)\n- Object Storage (via mount, leitura)\n\n**Limites:** [CHECK DOCS] Verifique limites de IOPS por volume."))
    
    examples.append(create_example("container-instances", "intermediate",
        "Como executar jobs batch?",
        "Executando jobs batch:\n\n**Configuração:**\n```bash\noci container-instance container-instance create \\\n  --compartment-id <ocid> \\\n  --display-name batch-job \\\n  --image \"python:3.9\" \\\n  --command '[\"python\", \"/app/process.py\"]' \\\n  --restart-policy NEVER\n```\n\n**Restart policies:**\n- NEVER: job único\n- ON_FAILURE: retry automático\n- ALWAYS: serviço contínuo\n\n**Monitoramento:**\n```bash\n# Status do job\noci container-instance container-instance get \\\n  --container-instance-id <ocid>\n\n# Logs\noci container-instance container-instance-action get-logs \\\n  --container-instance-id <ocid>\n```\n\n**Melhor prática:** Use Object Storage para outputs."))
    
    examples.append(create_example("container-instances", "intermediate",
        "Como usar imagens do Container Registry?",
        "Usando OCI Container Registry:\n\n**1. Push da imagem:**\n```bash\n# Login\ndocker login <region>.ocir.io -u '<namespace>/<username>'\n\n# Tag\ndocker tag myapp:latest <region>.ocir.io/<namespace>/myapp:latest\n\n# Push\ndocker push <region>.ocir.io/<namespace>/myapp:latest\n```\n\n**2. Crie container instance:**\n```bash\noci container-instance container-instance create \\\n  --compartment-id <ocid> \\\n  --image \"<region>.ocir.io/<namespace>/myapp:latest\" \\\n  --image-pull-secret '<auth-token>'\n```\n\n**3. Auth Token:**\n- Console → User Settings → Auth Tokens\n- Generate Token\n- Use como senha no docker login\n\n**Best Practice:** Use tags versionadas, não 'latest'."))
    
    # Advanced (2)
    examples.append(create_example("container-instances", "advanced",
        "Como implementar auto-scaling com Container Instances?",
        "Auto-scaling pattern:\n\n**1. Com Events + Functions:**\n```yaml\n# Event Rule\n- source: oci.metrics\n- metric: cpu_utilization > 70%\n- action: invoke function\n```\n\n**2. Function cria nova instância:**\n```python\nimport oci\n\ndef handler(ctx, data):\n    ci_client = oci.container_instances.ContainerInstanceClient()\n    ci_client.create_container_instance({\n        'compartment_id': compartment,\n        'image': 'myapp:latest',\n        'shape': 'OCI.CI.E4.Flex'\n    })\n```\n\n**3. Cleanup (scale in):**\n- Monitor instâncias ociosas\n- Delete após timeout\n- Use tagging para tracking\n\n**Alternativa:** Use OKE com Horizontal Pod Autoscaler para scaling mais sofisticado."))
    
    examples.append(create_example("container-instances", "advanced",
        "Como migrar de ECS (AWS) para Container Instances?",
        "Migração ECS → Container Instances:\n\n**Mapeamento:**\n- ECS Task → Container Instance\n- ECS Service → Múltiplas instâncias + Load Balancer\n- ECS Fargate → Container Instances (serverless)\n\n**1. Exporte definições:**\n```json\n// ECS Task Definition\n{\n  \"containerDefinitions\": [{\n    \"image\": \"myapp:latest\",\n    \"cpu\": 1024,\n    \"memory\": 2048\n  }]\n}\n```\n\n**2. Converta para OCI:**\n```bash\noci container-instance container-instance create \\\n  --image \"myapp:latest\" \\\n  --shape OCI.CI.E4.Flex  # 4 vCPU, 16GB\n```\n\n**3. Load Balancer:**\n- Backend set → Container Instances\n- Health check configurado\n\n**Diferenças:**\n- ECS tem mais features de orchestration\n- Container Instances é mais simples\n- Para Kubernetes, use OKE"))
    
    return examples

def generate_serverless_functions_examples():
    """Generate examples for serverless-functions."""
    examples = []
    
    # Beginner (3)
    examples.append(create_example("serverless-functions", "beginner",
        "O que é OCI Functions?",
        "OCI Functions é um serviço serverless de Functions-as-a-Service (FaaS).\n\n**Características:**\n- Execução sob demanda\n- Scaling automático (0 a N)\n- Pay per execution\n- Baseado em Fn Project (open source)\n\n**Casos de uso:**\n- Processamento de eventos\n- Webhooks\n- Automação de infraestrutura\n- ETL leve\n\n**Componentes:**\n- Application: grupo de functions\n- Function: código executável\n- Invocation: execução da function\n\n[MUTABLE] Preços por milhão de invocações e GB-segundo."))
    
    examples.append(create_example("serverless-functions", "beginner",
        "Como criar minha primeira function?",
        "Criando primeira function:\n\n**Via Console:**\n1. Developer Services → Functions\n2. 'Create Application'\n3. Configure VCN e subnet\n4. 'Create Function' na aplicação\n5. Escolha runtime (Python, Node, Java)\n6. Upload do código ou editor inline\n7. Teste com 'Invoke'\n\n**Exemplo Python:**\n```python\ndef handler(ctx, data):\n    return {\n        'statusCode': 200,\n        'body': 'Hello from OCI Functions!'\n    }\n```\n\n**Endpoint:** HTTPS automático fornecido\n\n[CHECK DOCS] Runtimes suportados variam."))
    
    examples.append(create_example("serverless-functions", "beginner",
        "Quais linguagens são suportadas?",
        "Runtimes suportados:\n\n**Oficiais:**\n- Python 3.8, 3.9, 3.10\n- Node.js 14, 16, 18\n- Java 8, 11\n- Go 1.x\n\n**Custom (Docker):**\n- Qualquer linguagem via Docker image\n- Ruby, PHP, .NET, etc.\n- Controle total do ambiente\n\n**Exemplo custom:**\n```dockerfile\nFROM ruby:3.1\nCOPY function.rb /\nCMD [\"function.handle\"]\n```\n\n**Recomendação:** Use runtimes oficiais para simplicidade, custom para necessidades específicas.\n\n[CHECK DOCS] Versões atualizadas periodicamente."))
    
    # Intermediate (5)
    examples.append(create_example("serverless-functions", "intermediate",
        "Como invocar uma function via CLI?",
        "Invocando via CLI:\n\n**Invoke síncrono:**\n```bash\noci functions function invoke \\\n  --function-id <ocid> \\\n  --invoke-type SYNCHRONOUS \\\n  --invoke-body '{\"name\": \"John\"}' \\\n  --response-body-output-file -\n```\n\n**Invoke assíncrono:**\n```bash\noci functions function invoke \\\n  --function-id <ocid> \\\n  --invoke-type ASYNCHRONOUS \\\n  --invoke-body '{\"event\": \"process\"}'\n```\n\n**Via endpoint HTTPS:**\n```bash\ncurl -X POST https://<endpoint>/20180120/actions/<id>/actions/invoke \\\n  -H \"Authorization: Bearer <token>\" \\\n  -d '{\"data\": \"test\"}'\n```\n\n**Resposta:** JSON com statusCode e body."))
    
    examples.append(create_example("serverless-functions", "intermediate",
        "Como conectar function ao Vault para secrets?",
        "Usando secrets do Vault:\n\n**1. Crie secret no Vault:**\n```bash\noci vault secret create \\\n  --compartment-id <ocid> \\\n  --vault-id <ocid> \\\n  --secret-name db-password \\\n  --secret-content '{\"content\": \"mysecret\"}'\n```\n\n**2. Policy para function:**\n```\nAllow service fnfunc to read secret-family in compartment <comp>\n```\n\n**3. Código da function:**\n```python\nimport oci\n\ndef handler(ctx, data):\n    vault = oci.vault.VaultClient()\n    secret = vault.get_secret(secret_id='<ocid>')\n    password = secret.data.secret_content.content\n    # Use password\n```\n\n**Best Practice:** Nunca hardcode secrets no código."))
    
    examples.append(create_example("serverless-functions", "intermediate",
        "Como configurar triggers do Events Service?",
        "Configurando triggers:\n\n**1. Crie Rule no Events:**\n```bash\noci events rule create \\\n  --compartment-id <ocid> \\\n  --display-name \"object-created\" \\\n  --condition '{\"eventType\":\"com.oraclecloud.objectstorage.createobject\"}' \\\n  --actions '[{\"type\":\"FUNCTION\",\"functionId\":\"<ocid>\"}]'\n```\n\n**2. Exemplo - Object Storage:**\n```json\n{\n  \"eventType\": \"com.oraclecloud.objectstorage.createobject\",\n  \"compartmentId\": \"<ocid>\",\n  \"data\": {\n    \"namespace\": \"my-ns\",\n    \"bucketName\": \"uploads\",\n    \"objectName\": \"file.pdf\"\n  }\n}\n```\n\n**3. Function processa evento:**\n```python\ndef handler(ctx, data):\n    bucket = data['data']['bucketName']\n    object = data['data']['objectName']\n    # Process file\n```"))
    
    examples.append(create_example("serverless-functions", "intermediate",
        "Como fazer deploy de functions com Fn CLI?",
        "Deploy com Fn CLI:\n\n**1. Instale Fn CLI:**\n```bash\npip3 install fnproject-cli\n```\n\n**2. Inicie projeto:**\n```bash\nfn init --runtime python myfunc\ncd myfunc\n```\n\n**3. Estrutura:**\n```\nmyfunc/\n  func.py      # código\n  func.yaml    # configuração\n  requirements.txt\n```\n\n**4. Deploy:**\n```bash\nfn deploy --app myapp --registry <region>.ocir.io/<namespace>\n```\n\n**5. Invoke:**\n```bash\nfn invoke myapp myfunc\n```\n\n**Vantagem:** Versionamento e CI/CD mais fácil."))
    
    examples.append(create_example("serverless-functions", "intermediate",
        "Como monitorar e debugar functions?",
        "Monitoramento e debugging:\n\n**Logs no Logging:**\n```bash\noci logging log-entry list \\\n  --compartment-id <ocid> \\\n  --log-id <log-ocid>\n```\n\n**CloudWatch-style logs:**\n```python\nimport logging\nlogging.basicConfig(level=logging.INFO)\nlogger = logging.getLogger()\n\ndef handler(ctx, data):\n    logger.info(f\"Processing: {data}\")\n    logger.error(f\"Error occurred\")\n```\n\n**Metrics no Monitoring:**\n- Invocations count\n- Errors count\n- Duration (ms)\n- Concurrent executions\n\n**Tracing:**\n- Integre com OCI Resource Manager\n- Use correlation IDs\n- Distributed tracing com Jaeger\n\n**Debug local:**\n```bash\nfn invoke --body '{\"test\": true}' myapp myfunc\n```"))
    
    # Advanced (2)
    examples.append(create_example("serverless-functions", "advanced",
        "Como implementar retry e dead letter queue?",
        "Retry e DLQ pattern:\n\n**1. Retry na function:**\n```python\ndef handler(ctx, data):\n    max_retries = 3\n    for attempt in range(max_retries):\n        try:\n            return process(data)\n        except Exception as e:\n            if attempt == max_retries - 1:\n                # Send to DLQ\n                send_to_dlq(data, str(e))\n                raise\n            time.sleep(2 ** attempt)  # backoff\n```\n\n**2. DLQ com Queue Service:**\n```python\nimport oci\n\ndef send_to_dlq(data, error):\n    queue = oci.queue.QueueClient()\n    queue.put_message(\n        queue_id='<dlq-ocid>',\n        message={'body': data, 'error': error}\n    )\n```\n\n**3. Events para DLQ:**\n- Rule para falhas de function\n- Action: enviar para Queue\n\n**Processamento DLQ:**\n- Function separada processa DLQ\n- Alerta quando DLQ cresce\n- Retry manual após fix"))
    
    examples.append(create_example("serverless-functions", "advanced",
        "Como migrar AWS Lambda para OCI Functions?",
        "Migração Lambda → OCI Functions:\n\n**1. Mapeamento de conceitos:**\n- Lambda Function → OCI Function\n- Lambda Layer → Docker custom runtime\n- API Gateway → OCI API Gateway\n- EventBridge → OCI Events\n\n**2. Converta handler:**\n```python\n# AWS Lambda\ndef lambda_handler(event, context):\n    return {'statusCode': 200, 'body': 'OK'}\n\n# OCI Functions\ndef handler(ctx, data):\n    return {'statusCode': 200, 'body': 'OK'}\n```\n\n**3. IAM → Policies:**\n- Lambda execution role → Dynamic group + policies\n- resource.function-family → function-family\n\n**4. Environment variables:**\n- Mesma abordagem\n- Secrets → OCI Vault\n\n**Diferenças:**\n- Lambda tem mais integrações nativas\n- OCI Functions é mais simples\n- Custom Docker para parity total"))
    
    return examples

def generate_serverless_api_gateway_examples():
    """Generate examples for serverless-api-gateway."""
    examples = []
    
    # Beginner (3)
    examples.append(create_example("serverless-api-gateway", "beginner",
        "O que é OCI API Gateway?",
        "OCI API Gateway é um serviço gerenciado para criar, publicar e gerenciar APIs.\n\n**Características:**\n- RESTful APIs\n- Rate limiting\n- Authentication/Authorization\n- Transformação de requests\n- Logging e monitoring\n\n**Componentes:**\n- Gateway: endpoint público\n- Deployment: conjunto de routes\n- Route: mapeamento path → backend\n- Backend: Functions, HTTP, Load Balancer\n\n**Casos de uso:**\n- APIs para aplicações\n- Microserviços\n- Backend para mobile\n- Integração B2B\n\n[MUTABLE] Preços por gateway e requests."))
    
    examples.append(create_example("serverless-api-gateway", "beginner",
        "Como criar um API Gateway?",
        "Criando API Gateway:\n\n**Via Console:**\n1. Developer Services → API Gateway\n2. 'Create Gateway'\n3. Configure:\n   - Compartment\n   - Name\n   - VCN e subnet\n   - Type (public/private)\n4. Create\n\n**Via CLI:**\n```bash\noci api-gateway gateway create \\\n  --compartment-id <ocid> \\\n  --display-name my-api \\\n  --endpoint-type PUBLIC \\\n  --subnet-id <subnet-ocid>\n```\n\n**Endpoint:** URL pública automática fornecida\n\n**Próximos passos:** Criar deployment com routes"))
    
    examples.append(create_example("serverless-api-gateway", "beginner",
        "Como criar uma rota simples?",
        "Criando rota (route):\n\n**Via Console:**\n1. Gateway Details → Create Deployment\n2. Add Route:\n   - Path: /hello\n   - Method: GET\n   - Backend: HTTP Backend\n   - URL: https://myapp.com/api\n3. Create Deployment\n\n**Via SDK (Python):**\n```python\nfrom oci.apigateway.models import DeploymentDetails\n\ndeployment = DeploymentDetails(\n    display_name='v1',\n    routes=[{\n        'path': '/hello',\n        'methods': ['GET'],\n        'backend': {\n            'type': 'HTTP_BACKEND',\n            'url': 'https://myapp.com/api'\n        }\n    }]\n)\n```\n\n**Teste:** curl https://<gateway-url>/hello"))
    
    # Intermediate (5)
    examples.append(create_example("serverless-api-gateway", "intermediate",
        "Como integrar API Gateway com Functions?",
        "Integração com Functions:\n\n**Via Console:**\n1. Create Deployment → Add Route\n2. Backend Type: Oracle Functions\n3. Selecione Application e Function\n4. Create\n\n**Via CLI:**\n```bash\noci api-gateway deployment create \\\n  --gateway-id <gateway-ocid> \\\n  --specification '{\n    \"routes\": [{\n      \"path\": \"/process\",\n      \"methods\": [\"POST\"],\n      \"backend\": {\n        \"type\": \"ORACLE_FUNCTIONS_BACKEND\",\n        \"functionId\": \"<function-ocid>\"\n      }\n    }]\n  }'\n```\n\n**Policy necessária:**\n```\nAllow service apigateway to use fn-func in compartment <comp>\n```\n\n**Vantagem:** Serverless end-to-end, scaling automático."))
    
    examples.append(create_example("serverless-api-gateway", "intermediate",
        "Como configurar rate limiting?",
        "Configurando rate limiting:\n\n**Via Console:**\n1. Deployment → Rate Limiting\n2. Configure:\n   - Rate limit: requests por segundo\n   - Burst limit: pico permitido\n3. Apply\n\n**Via SDK:**\n```python\nrate_limits = {\n    'rateLimiting': {\n        'type': 'CLIENT_IP',\n        'rateInRequestsPerSecond': 100,\n        'burstLimitInRequests': 200\n    }\n}\n\ndeployment = DeploymentDetails(\n    display_name='v1',\n    rate_limiting=rate_limits,\n    routes=[...]\n)\n```\n\n**Tipos:**\n- CLIENT_IP: por IP de origem\n- GLOBAL: total do gateway\n\n**Use cases:**\n- Proteger backend de overload\n- Prevenir abuso\n- SLA enforcement"))
    
    examples.append(create_example("serverless-api-gateway", "intermediate",
        "Como adicionar autenticação JWT?",
        "Autenticação JWT:\n\n**Via Console:**\n1. Deployment → Authentication\n2. Type: JWT\n3. Configure:\n   - JWKS URI: https://auth.example.com/.well-known/jwks.json\n   - Audience: my-api\n   - Issuer: https://auth.example.com\n4. Save\n\n**Via SDK:**\n```python\nauth = {\n    'type': 'JWT',\n    'jwksUri': 'https://auth.example.com/.well-known/jwks.json',\n    'audience': 'my-api',\n    'issuer': 'https://auth.example.com'\n}\n```\n\n**Fluxo:**\n1. Client obtém token do IdP\n2. Request com Authorization: Bearer <token>\n3. Gateway valida JWT\n4. Backend recebe request válido\n\n**IdPs suportados:** Oracle IDCS, Auth0, Okta, Azure AD, etc."))
    
    examples.append(create_example("serverless-api-gateway", "intermediate",
        "Como fazer versionamento de API?",
        "Versionamento de API:\n\n**Estratégia 1 - Path:**\n```\nGET /v1/users\nGET /v2/users\n```\n\n**Deployments:**\n```python\n# v1 deployment\nroutes_v1 = [{'path': '/v1/users', ...}]\n\n# v2 deployment\nroutes_v2 = [{'path': '/v2/users', ...}]\n```\n\n**Estratégia 2 - Header:**\n```\nGET /users\nHeader: API-Version: 2\n```\n\n**Route matching:**\n```python\nroutes = [\n    {'path': '/v2/users', 'headerMatches': [{'name': 'API-Version', 'value': '2'}]},\n    {'path': '/v1/users'},  # default\n]\n```\n\n**Best Practice:**\n- Mantenha versões antigas por período definido\n- Documente breaking changes\n- Use deprecation headers"))
    
    examples.append(create_example("serverless-api-gateway", "intermediate",
        "Como configurar CORS?",
        "Configurando CORS:\n\n**Via Console:**\n1. Deployment → CORS\n2. Configure:\n   - Allowed Origins: https://app.example.com\n   - Allowed Methods: GET, POST, PUT\n   - Allowed Headers: Content-Type, Authorization\n   - Exposed Headers: X-Request-Id\n   - Max Age: 3600\n3. Save\n\n**Via SDK:**\n```python\ncors = {\n    'allowedOrigins': ['https://app.example.com'],\n    'allowedMethods': ['GET', 'POST', 'PUT', 'DELETE'],\n    'allowedHeaders': ['Content-Type', 'Authorization'],\n    'exposedHeaders': ['X-Request-Id'],\n    'maxAgeInSeconds': 3600\n}\n```\n\n**Wildcard (dev):**\n- allowedOrigins: ['*']\n- Não use em produção\n\n**Preflight:** Gateway responde OPTIONS automaticamente."))
    
    # Advanced (2)
    examples.append(create_example("serverless-api-gateway", "advanced",
        "Como implementar request/response transformation?",
        "Transformation com request/response policies:\n\n**Request Transformation:**\n```python\nrequest_policy = {\n    'type': 'REQUEST_POLICY',\n    'renameHeaders': [{'from': 'X-Old', 'to': 'X-New'}],\n    'addHeaders': [{'name': 'X-Gateway-Time', 'value': '$request.time'}],\n    'removeHeaders': ['X-Internal']\n}\n```\n\n**Response Transformation:**\n```python\nresponse_policy = {\n    'type': 'RESPONSE_POLICY',\n    'addHeaders': [{'name': 'X-API-Version', 'value': 'v2'}],\n    'bodyTransformation': {\n        'type': 'JSON',\n        'template': '{\"data\": $response.body, \"meta\": {\"version\": \"v2\"}}'\n    }\n}\n```\n\n**Use cases:**\n- Legacy → Modern API\n- Normalização de responses\n- Adicionar metadata\n- Masking de dados sensíveis\n\n**Limitações:** Transformações complexas podem precisar de Function intermediária."))
    
    examples.append(create_example("serverless-api-gateway", "advanced",
        "Como migrar AWS API Gateway para OCI?",
        "Migração API Gateway AWS → OCI:\n\n**1. Exporte API AWS:**\n```bash\naws apigateway get-rest-apis\naws apigateway get-resources --rest-api-id <id>\n```\n\n**2. Mapeamento:**\n- REST API → Gateway + Deployment\n- Resources → Routes\n- Integrations → Backends\n- Authorizers → Authentication policies\n- Usage Plans → Rate Limiting\n\n**3. Converta definição:**\n```yaml\n# AWS OpenAPI → OCI Specification\npaths:\n  /users:\n    get:\n      x-oci-backend:\n        type: ORACLE_FUNCTIONS_BACKEND\n        functionId: <ocid>\n```\n\n**4. IAM:**\n- AWS IAM → OCI Policies\n- Lambda permissions → Function policies\n\n**Diferenças:**\n- OCI é mais simples\n- Menos integrações nativas\n- Custom policies para casos complexos"))
    
    return examples

# Continue with more category generators...
# (To be continued with all 56 categories)

def generate_security_iam_basics_examples():
    """Generate examples for security-iam-basics."""
    examples = []
    
    # Beginner (3)
    examples.append(create_example("security-iam-basics", "beginner",
        "O que é IAM no OCI?",
        "IAM (Identity and Access Management) controla quem acessa quais recursos no OCI.\n\n**Componentes principais:**\n- Users: pessoas ou serviços\n- Groups: coleção de users\n- Compartments: isolamento lógico de recursos\n- Policies: regras de permissão\n- Dynamic Groups: grupos baseados em regras\n\n**Princípios:**\n- Least privilege (menor privilégio necessário)\n- Segregation of duties\n- Audit via CloudTrail\n\n**Diferença AWS:** IAM Users → OCI Users, IAM Roles → Dynamic Groups\n\nDocs: https://docs.oracle.com/en-us/iaas/Content/Identity/Concepts/overview.htm"))
    
    examples.append(create_example("security-iam-basics", "beginner",
        "Como criar um usuário?",
        "Criando usuário:\n\n**Via Console:**\n1. Identity & Security → Users\n2. 'Create User'\n3. Preencha:\n   - Name\n   - Email\n   - Description\n4. Add a grupos (opcional)\n5. Create\n\n**Via CLI:**\n```bash\noci iam user create \\\n  --compartment-id <tenancy-ocid> \\\n  --name joao.silva \\\n  --email joao@empresa.com \\\n  --description \"Desenvolvedor\"\n```\n\n**Próximos passos:**\n- Add a grupos\n- Configure credentials (password ou API keys)\n\n[CHECK DOCS] Limites de usuários por tenancy."))
    
    examples.append(create_example("security-iam-basics", "beginner",
        "O que são compartments?",
        "Compartments são containers lógicos para organizar recursos OCI.\n\n**Características:**\n- Isolamento lógico (não físico)\n- Hierarquia (compartments dentro de compartments)\n- Políticas podem ser por compartment\n- Facilita billing e governance\n\n**Exemplo de estrutura:**\n```\nTenancy\n├── Prod\n│   ├── Network\n│   ├── Compute\n│   └── Database\n├── Dev\n└── Shared\n```\n\n**Best Practices:**\n- Separe por ambiente (Prod/Dev/Test)\n- Separe por time/projeto\n- Use tags para cruzar compartments\n\n**Diferença AWS:** Similar a AWS Organizations OUs + Resource Groups"))
    
    # Intermediate (5)
    examples.append(create_example("security-iam-basics", "intermediate",
        "Como criar grupos e adicionar usuários?",
        "Gerenciando grupos:\n\n**Criar grupo:**\n```bash\noci iam group create \\\n  --compartment-id <tenancy-ocid> \\\n  --name Developers \\\n  --description \"Time de desenvolvimento\"\n```\n\n**Add usuário ao grupo:**\n```bash\noci iam user-add-to-group \\\n  --user-id <user-ocid> \\\n  --group-id <group-ocid>\n```\n\n**Listar membros:**\n```bash\noci iam group list-users --group-id <group-ocid>\n```\n\n**Remover:**\n```bash\noci iam user-remove-from-group \\\n  --user-id <user-ocid> \\\n  --group-id <group-ocid>\n```\n\n**Best Practice:** Grupos por função (Developers, Admins, DBAs), não por pessoa."))
    
    examples.append(create_example("security-iam-basics", "intermediate",
        "Como configurar MFA?",
        "Configurando MFA (Multi-Factor Authentication):\n\n**Para o próprio usuário:**\n1. Console → User Settings\n2. 'Generate MFA Secret'\n3. Scan QR code com app (Google Authenticator, Authy)\n4. Digite código de verificação\n5. Enable MFA\n\n**Forçar MFA para outros usuários (Policy):**\n```\nAllow group Admins to manage all-resources in tenancy\n  where request.auth.type='mfa'\n```\n\n**Via CLI:**\n```bash\noci iam user update \\\n  --user-id <ocid> \\\n  --is-mfa-activated true\n```\n\n**Best Practice:** MFA obrigatório para todos usuários com acesso privilegiado\n\n[CHECK DOCS] MFA não disponível para API keys."))
    
    examples.append(create_example("security-iam-basics", "intermediate",
        "Como gerar API keys?",
        "Gerando API keys para CLI/SDK:\n\n**1. Gere par de chaves:**\n```bash\nmkdir -p ~/.oci\nopenssl genrsa -out ~/.oci/oci_api_key.pem 2048\nchmod 600 ~/.oci/oci_api_key.pem\nopenssl rsa -pubout -in ~/.oci/oci_api_key.pem -out ~/.oci/oci_api_key_public.pem\n```\n\n**2. Console → User Settings → API Keys**\n3. 'Add API Key'\n4. Upload da chave pública\n5. Anote Key Fingerprint\n\n**3. Configure ~/.oci/config:**\n```ini\n[DEFAULT]\nuser=<user-ocid>\nfingerprint=<key-fingerprint>\ntenancy=<tenancy-ocid>\nregion=us-ashburn-1\nkey_file=~/.oci/oci_api_key.pem\n```\n\n**4. Teste:**\n```bash\noci iam user get --user-id <ocid>\n```"))
    
    examples.append(create_example("security-iam-basics", "intermediate",
        "Como auditar acesso com Audit Service?",
        "Auditoria com Audit Service:\n\n**O que é auditado:**\n- Todas as chamadas de API\n- Console actions\n- Mudanças em recursos\n- Acesso a dados sensíveis\n\n**Query de auditoria:**\n```bash\noci audit event list \\\n  --compartment-id <ocid> \\\n  --start-time \"2024-01-01T00:00:00Z\" \\\n  --end-time \"2024-01-31T23:59:59Z\"\n```\n\n**Filtros comuns:**\n```bash\n# Quem deletou instâncias?\noci audit event list --query \"?data.resourceName=='instance-delete'\"\n\n# Acesso de usuário específico\noci audit event list --query \"?data.identity.userPrincipalId=='<user-ocid>'\"\n```\n\n**Export:** Configure para Object Storage para retenção longa\n\nDocs: https://docs.oracle.com/en-us/iaas/Content/Audit/Concepts/auditoverview.htm"))
    
    examples.append(create_example("security-iam-basics", "intermediate",
        "Como usar tags para governança?",
        "Tags para governança:\n\n**Tipos de tags:**\n- Free-form: simples, sem schema\n- Defined: com schema e validação\n\n**Aplicar tags:**\n```bash\noci compute instance tag \\\n  --instance-id <ocid> \\\n  --defined-tags '{\"Production\":{\"Environment\": \"prod\"}}' \\\n  --freeform-tags '{\"Owner\": \"DevOps\", \"CostCenter\": \"12345\"}'\n```\n\n**Políticas baseadas em tags:**\n```\nAllow group Developers to manage instance-family in compartment Dev\n  where ALL {request.resource.tags.CostCenter = '12345'}\n```\n\n**Use cases:**\n- Cost allocation (CostCenter)\n- Ownership (Owner, Team)\n- Environment (Prod, Dev, Test)\n- Compliance (PCI, HIPAA)\n\n**Best Practice:** Defina tag schema antes de criar recursos."))
    
    # Advanced (2)
    examples.append(create_example("security-iam-basics", "advanced",
        "Como implementar least privilege?",
        "Implementando least privilege:\n\n**1. Analise acesso atual:**\n```bash\n# Quem acessou o quê\noci audit event list --compartment-id <ocid> | \\\n  jq '.data | {user: .identity.userPrincipalName, action: .eventName}'\n```\n\n**2. Crie políticas mínimas:**\n```bash\n# RUIM: muito permissivo\nAllow group Devs to manage all-resources in compartment Dev\n\n# BOM: específico\nAllow group Devs to read instance-family in compartment Dev\nAllow group Devs to manage volume-family in compartment Dev\nAllow group Devs to read virtual-network-family in compartment Dev\n```\n\n**3. Resource-specific:**\n```\nAllow group DBAs to manage db-systems in compartment Prod\n  where resource.id = '<specific-db-ocid>'\n```\n\n**4. Review periódico:**\n- Audit logs mensais\n- Remova acesso não usado\n- Documente exceções\n\n**Trade-off:** Mais granularidade = mais complexidade"))
    
    examples.append(create_example("security-iam-basics", "advanced",
        "Como federar com Azure AD?",
        "Federação com Azure AD:\n\n**1. No Azure AD:**\n- Crie Enterprise Application\n- Configure SAML\n- Download metadata XML\n\n**2. No OCI:**\n```bash\noci iam identity-provider create \\\n  --compartment-id <tenancy-ocid> \\\n  --name AzureAD \\\n  --protocol-type SAML2 \\\n  --metadata-url https://login.microsoftonline.com/<tenant>/federationmetadata/2007-06/federationmetadata.xml\n```\n\n**3. Mapeie grupos:**\n```\nAzure AD Group \"OCI-Admins\" → OCI Group \"Admins\"\n```\n\n**4. Policy no OCI:**\n```\nAllow group Admins to manage all-resources in tenancy\n```\n\n**5. Teste login:**\n- Users logam via Azure AD SSO\n- Tokens SAML válidos no OCI\n\n**Vantagens:**\n- SSO centralizado\n- Provisionamento automático\n- Offboarding no Azure remove acesso OCI"))
    
    return examples

def generate_security_policies_examples():
    """Generate examples for security-policies."""
    examples = []
    
    # Beginner (3)
    examples.append(create_example("security-policies", "beginner",
        "O que são policies no OCI?",
        "Policies são regras que definem quem pode fazer o quê no OCI.\n\n**Sintaxe:**\n```\nAllow <group> to <verb> <resource-type> in <location>\n```\n\n**Exemplos:**\n```\nAllow group Admins to manage all-resources in tenancy\nAllow group Developers to manage instance-family in compartment Dev\nAllow group DBAs to read database-family in compartment Prod\n```\n\n**Verbos:**\n- read: visualizar\n- use: usar (inspecionar + ações)\n- manage: CRUD completo\n\n**Recursos:**\n- instance-family: instâncias, images, volumes\n- virtual-network-family: VCNs, subnets, security lists\n- database-family: databases, backups\n\nDocs: https://docs.oracle.com/en-us/iaas/Content/Identity/Concepts/policies.htm"))
    
    examples.append(create_example("security-policies", "beginner",
        "Como criar uma policy?",
        "Criando policy:\n\n**Via Console:**\n1. Identity & Security → Policies\n2. 'Create Policy'\n3. Selecione compartment\n4. Digite statement:\n   ```\n   Allow group Developers to manage instance-family in compartment Dev\n   ```\n5. Create\n\n**Via CLI:**\n```bash\noci iam policy create \\\n  --compartment-id <compartment-ocid> \\\n  --name dev-compute-policy \\\n  --statements '[\"Allow group Developers to manage instance-family in compartment Dev\"]'\n```\n\n**Best Practices:**\n- Names descritivos\n- Statements em linhas separadas\n- Teste com usuário de teste\n\n[CHECK DOCS] Limites de policies por compartment."))
    
    examples.append(create_example("security-policies", "beginner",
        "Qual a diferença entre read, use e manage?",
        "Níveis de permissão:\n\n**READ:**\n- Listar recursos\n- Ver detalhes\n- Sem modificações\n```Allow group Auditors to read instance-family in tenancy```\n\n**USE:**\n- Tudo do READ +\n- Start/stop instâncias\n- Attach/detach volumes\n- Console access\n```Allow group Operators to use instance-family in compartment Prod```\n\n**MANAGE:**\n- Tudo do USE +\n- Create/delete\n- Update configurações\n```Allow group Admins to manage instance-family in compartment Dev```\n\n**Hierarquia:** manage > use > read\n\n**Use case:**\n- Devs: use (dev/test)\n- Ops: use (prod)\n- Admins: manage (tudo)"))
    
    # Intermediate (5)
    examples.append(create_example("security-policies", "intermediate",
        "Como escrever policy para VCN?",
        "Policies para VCN:\n\n**Leitura (network team):**\n```\nAllow group NetworkAdmins to read virtual-network-family in tenancy\n```\n\n**Gerenciamento completo:**\n```\nAllow group NetworkAdmins to manage virtual-network-family in compartment Shared\n```\n\n**Específico por recurso:**\n```\nAllow group NetworkAdmins to manage vcns in compartment Shared\nAllow group NetworkAdmins to manage subnets in compartment Shared\nAllow group NetworkAdmins to manage security-lists in compartment Shared\nAllow group NetworkAdmins to use virtual-network-family in compartment Prod\n```\n\n**Cross-compartment:**\n```\nAllow group NetworkAdmins to read virtual-network-family in compartment Prod\nAllow group NetworkAdmins to manage virtual-network-family in compartment Shared\n```\n\n**DRG (Dynamic Routing Gateway):**\n```\nAllow group NetworkAdmins to manage drg-family in tenancy\n```"))
    
    examples.append(create_example("security-policies", "intermediate",
        "Como permitir acesso a Object Storage?",
        "Policies para Object Storage:\n\n**Acesso a buckets específicos:**\n```\nAllow group AppTeam to read buckets in compartment Prod\n  where target.bucket.name='app-data'\nAllow group AppTeam to manage objects in compartment Prod\n  where target.bucket.name='app-data'\n```\n\n**Acesso por prefixo:**\n```\nAllow group DataTeam to manage objects in compartment Data\n  where target.object.name.startsWith('team-a/')\n```\n\n**Verbos:**\n- read: listar buckets, ver metadata\n- use: download de objetos\n- manage: CRUD completo (create/delete bucket, upload/delete objects)\n\n**Exemplo completo:**\n```\nAllow group BackupTeam to read buckets in tenancy\nAllow group BackupTeam to manage objects in tenancy\n  where target.object.name.startsWith('backups/')\n```\n\nDocs: https://docs.oracle.com/en-us/iaas/Content/Identity/Concepts/commonpolicies.htm#Object_Storage"))
    
    examples.append(create_example("security-policies", "intermediate",
        "Como criar policy para Load Balancer?",
        "Policies para Load Balancer:\n\n**Gerenciamento completo:**\n```\nAllow group LBAdmins to manage load-balancers in compartment Prod\n```\n\n**Apenas leitura:**\n```\nAllow group Auditors to read load-balancers in tenancy\n```\n\n**Específico:**\n```\nAllow group LBAdmins to manage load-balancers in compartment Prod\nAllow group LBAdmins to manage backend-sets in compartment Prod\nAllow group LBAdmins to manage certificates in compartment Prod\n```\n\n**Network resources relacionados:**\n```\nAllow group LBAdmins to use virtual-network-family in compartment Prod\n  where target.resource.type='subnet'\n```\n\n**Cross-compartment (LB em Shared, apps em Prod):**\n```\nAllow group LBAdmins to manage load-balancers in compartment Shared\nAllow group LBAdmins to read virtual-network-family in compartment Prod\n```"))
    
    examples.append(create_example("security-policies", "intermediate",
        "Como usar condições em policies?",
        "Condições em policies:\n\n**Por tag:**\n```\nAllow group Devs to manage instance-family in compartment Dev\n  where ALL {request.resource.tags.Environment = 'dev'}\n```\n\n**Por tempo:**\n```\nAllow group Contractors to use instance-family in compartment Dev\n  where request.time < '2024-12-31T23:59:59Z'\n```\n\n**Por MFA:**\n```\nAllow group Admins to manage all-resources in tenancy\n  where request.auth.type='mfa'\n```\n\n**Por IP:**\n```\nAllow group RemoteWorkers to use instance-family in compartment Prod\n  where request.source.ip='203.0.113.0/24'\n```\n\n**Combinando:**\n```\nAllow group Devs to manage instance-family in compartment Dev\n  where ALL {\n    request.resource.tags.Environment = 'dev',\n    request.auth.type = 'mfa'\n  }\n```\n\n**Operadores:** ALL (AND), ANY (OR)"))
    
    examples.append(create_example("security-policies", "intermediate",
        "Como debugar policy que não funciona?",
        "Debug de policies:\n\n**1. Policy Analyzer (Console):**\n- Identity → Policies → Policy Analyzer\n- Simule usuário + ação\n- Veja se policy permite/nega\n\n**2. Verifique hierarquia:**\n- Policies em múltiplos compartments?\n- Herança pode bloquear\n\n**3. Sintaxe:**\n```bash\n# Liste policies\noci iam policy list --compartment-id <ocid>\n\n# Ver statements\noci iam policy get --policy-id <ocid>\n```\n\n**4. Common issues:**\n- Group name errado\n- Compartment errado\n- Verbo insuficiente (read vs use)\n- Resource-type incorreto\n\n**5. Audit logs:**\n```bash\noci audit event list --query \"?data.resourceName=='<resource>'\"\n# Veja erro exato\n```\n\n**6. Teste com usuário do grupo afetado"))
    
    # Advanced (2)
    examples.append(create_example("security-policies", "advanced",
        "Como implementar políticas de tagging obrigatório?",
        "Tagging obrigatório com policies:\n\n**1. Crie tag schema:**\n```bash\noci iam tag-namespace create \\\n  --compartment-id <tenancy-ocid> \\\n  --name Production \\\n  --description \"Production tags\"\n\noci iam tag create \\\n  --tag-namespace-id <namespace-ocid> \\\n  --name CostCenter \\\n  --description \"Cost center code\"\n```\n\n**2. Policy para exigir tag:**\n```\nAllow group Admins to manage instance-family in tenancy\n  where ALL {request.resource.tags.Production.CostCenter = 'defined'}\n\nDeny group AllUsers to manage instance-family in tenancy\n  where ANY {request.resource.tags.Production.CostCenter = 'undefined'}\n```\n\n**3. Validação:**\n- Criação sem tag → negado\n- Criação com tag → permitido\n\n**Limitação:** Nem todos recursos suportam tag enforcement\n\n**Alternativa:** Automation via Functions para remediar recursos sem tag."))
    
    examples.append(create_example("security-policies", "advanced",
        "Como criar política multi-tenancy?",
        "Políticas multi-tenancy:\n\n**Cenário:** MSP gerencia múltiplas tenancies\n\n**1. Federation setup:**\n- Identity Provider central\n- Groups mapeados por tenancy\n\n**2. Policy por tenancy:**\n```\n# Tenancy A\nAllow group MSP-Admins to manage all-resources in tenancy\n  where request.tenant.name='TenantA'\n\n# Tenancy B\nAllow group MSP-Admins to manage all-resources in tenancy\n  where request.tenant.name='TenantB'\n```\n\n**3. Cross-tenancy access:**\n```\nAllow group CentralOps to read metrics in tenancy\n  where request.tenant.id in ['<tenancy-a>','<tenancy-b>']\n```\n\n**4. Resource isolation:**\n```\nAllow group TenantA-Devs to manage instance-family in tenancy\n  where ALL {\n    request.tenant.name = 'TenantA',\n    request.resource.compartment.name = 'TenantA-Prod'\n  }\n```\n\n**Best Practice:** Use Organizations + federation para escala"))
    
    return examples

# ... More generators for all 56 categories

# Main execution
def main():
    """Generate all JSONL files."""
    
    # Category generators mapping
    generators = {
        # OCI Core (5)
        "database-autonomous-json": generate_database_autonomous_json_examples,
        "database-exadata": generate_database_exadata_examples,
        "container-instances": generate_container_instances_examples,
        "serverless-functions": generate_serverless_functions_examples,
        "serverless-api-gateway": generate_serverless_api_gateway_examples,
        
        # OCI Security (9)
        "security-iam-basics": generate_security_iam_basics_examples,
        "security-policies": generate_security_policies_examples,
        # ... more will be added
    }
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    for category, generator in generators.items():
        filepath = os.path.join(OUTPUT_DIR, f"{category}.jsonl")
        examples = generator()
        
        with open(filepath, 'w') as f:
            for example in examples:
                f.write(json.dumps(example, ensure_ascii=False) + '\n')
        
        print(f"Generated: {filepath} ({len(examples)} examples)")
    
    print(f"\nTotal: {len(generators)} files generated")

if __name__ == "__main__":
    main()
