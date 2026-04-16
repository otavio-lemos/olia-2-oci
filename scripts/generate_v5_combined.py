#!/usr/bin/env python3
"""Generate OCI training examples - combining best of both worlds:

- PT-BR responses with detailed phases (from old generate_diverse_v2.py)
- Real OCI CLI commands (from generate_e2e_diverse.py)
- 84 categories × 180 examples = 15,120 total
"""

import json
import random
import re
from pathlib import Path

random.seed(42)

EXAMPLES_PER_CATEGORY = 180

CATEGORIES = [
    # Compute (3)
    "compute/instances",
    "compute/scaling",
    "compute/custom-images",
    # Storage (3)
    "storage/block",
    "storage/object",
    "storage/file",
    # Networking (4)
    "networking/vcn",
    "networking/security",
    "networking/connectivity",
    "lb/load-balancer",
    # Database (7)
    "database/autonomous",
    "database/mysql",
    "database/postgresql",
    "database/nosql",
    "database/autonomous-json",
    "database/exadata",
    "database/exadata-cloud",
    # Container (2)
    "container/oke",
    "container/instances",
    # Serverless (2)
    "serverless/functions",
    "serverless/api-gateway",
    # Security (10)
    "security/iam-basics",
    "security/policies",
    "security/dynamic-groups",
    "security/federation",
    "security/vault-secrets",
    "security/vault-keys",
    "security/encryption",
    "security/cloud-guard",
    "security/waf",
    "security/zero-trust",
    "security/posture-management",
    # DevOps (4)
    "devops/ci-cd",
    "devops/resource-manager",
    "devops/artifacts",
    "devops/secrets",
    # Migration (12)
    "migration/aws-compute",
    "migration/aws-storage",
    "migration/aws-database",
    "migration/azure-compute",
    "migration/azure-storage",
    "migration/azure-database",
    "migration/gcp-compute",
    "migration/gcp-storage",
    "migration/gcp-database",
    "migration/onprem-compute",
    "migration/onprem-storage",
    "migration/onprem-vmware",
    "migration/onprem-database",
    "migration/data-transfer",
    # Terraform (12)
    "terraform/provider",
    "terraform/compute",
    "terraform/storage",
    "terraform/networking",
    "terraform/load-balancer",
    "terraform/database",
    "terraform/container",
    "terraform/serverless",
    "terraform/security",
    "terraform/observability",
    "terraform/devops",
    "terraform/state",
    # Observability (4)
    "observability/logging",
    "observability/monitoring",
    "observability/stack-monitoring",
    "observability/apm",
    # Troubleshooting (8)
    "troubleshooting/connectivity",
    "troubleshooting/performance",
    "troubleshooting/authentication",
    "troubleshooting/database",
    "troubleshooting/compute",
    "troubleshooting/storage",
    "troubleshooting/oke",
    "troubleshooting/functions",
    # Governance (8)
    "governance/landing-zone",
    "governance/compartments",
    "governance/tagging",
    "governance/budgets-cost",
    "governance/policies-guardrails",
    "governance/compliance",
    "governance/audit-readiness",
    "governance/resource-discovery",
    # FinOps (4)
    "finops/cost-optimization",
    "finops/showback-chargeback",
    "finops/rightsizing",
    "finops/storage-tiering",
    # Platform (2)
    "platform/backup-governance",
    "platform/sre-operations",
]

# =====================
# DATA LISTS
# =====================

SHAPES = [
    "VM.Standard.E4.Flex",
    "VM.Standard.A1.Flex",
    "VM.Optimized3.Flex",
    "BM.Standard.E5",
    "VM.GPU.A10.1",
    "VM.Standard3.Flex",
    "VM.DenseIO.E4.Flex",
]

REGIONS = [
    "sa-saopaulo-1",
    "us-ashburn-1",
    "us-phoenix-1",
    "eu-frankfurt-1",
    "uk-london-1",
    "ap-mumbai-1",
    "ap-tokyo-1",
    "ca-toronto-1",
    "ap-sydney-1",
]

COMPARTMENTS = [
    "production",
    "development",
    "staging",
    "sandbox",
    "shared-services",
    "networking",
    "security",
    "data-platform",
    "analytics",
    "devops",
]

COMPANIES = [
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

PROJECTS = [
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

INTENTS = [
    "create",
    "list",
    "get",
    "update",
    "delete",
    "manage",
]

PERSONAS = [
    "cloud architect",
    "platform engineer",
    "sre",
    "security lead",
    "dba",
    "finops analyst",
    "auditor",
    "devops engineer",
]

CONSTRAINTS = [
    "sem downtime",
    "sem IP público",
    "com budget limitado",
    "com auditoria em 30 dias",
    "ambiente legado",
    "equipe enxuta",
    "multi-região",
    "integração híbrida",
    "mínimo privilégio",
    "rollback em menos de 15 minutos",
]

LIFECYCLE_STAGES = [
    "greenfield",
    "brownfield",
    "produção estável",
    "incidente",
    "expansão",
    "auditoria",
    "migração",
    "desativação",
]

# CLI COMMANDS - Detailed for all intents including update/manage
CLI_COMMANDS = {
    "compute/instances": {
        "create": "oci compute instance launch --availability-domain {ad} --shape {shape} --shape-config 'ocpus={ocpus},memory={memory}' --subnet-id {subnet_id} --display-name {name} --compartment-id {compartment_id}",
        "list": "oci compute instance list --compartment-id {compartment_id} --lifecycle-state RUNNING",
        "get": "oci compute instance get --instance-id {instance_id}",
        "update": """# Update instance properties
oci compute instance update --instance-id {instance_id} --display-name {name}

# Resize (change shape)
oci compute instance update --instance-id {instance_id} --shape VM.Standard2.4 --preserve-boot-volume false --wait-for-state RUNNING

# Update boot volume
oci compute boot-volume update --boot-volume-id {volume_id} --size-in-gbs {size}""",
        "delete": "oci compute instance terminate --instance-id {instance_id} --preserve-boot-volume false",
        "manage": """# Start/Stop/Reset
oci compute instance action --instance-id {instance_id} --action START --wait-for-state RUNNING
oci compute instance action --instance-id {instance_id} --action STOP --wait-for-state STOPPED

# Get console output
oci compute instance get --instance-id {instance_id} --raw-output --query 'data."console-output".value' | base64 -d""",
    },
    "compute/scaling": {
        "create": "oci compute instance-pool create --compartment-id {compartment_id} --shape {shape} --size {size} --subnet-ids ['{subnet_id}'] --display-name {name}",
        "list": "oci compute instance-pool list --compartment-id {compartment_id}",
        "get": "oci compute instance-pool get --instance-pool-id {instance_pool_id}",
        "update": """# Update pool size
oci compute instance-pool update --instance-pool-id {instance_pool_id} --size {new_size}

# Update instance configuration
oci compute instance-configuration update --instance-configuration-id {config_id} --shape-config 'ocpus={ocpus},memory={memory}'""",
        "delete": "oci compute instance-pool delete --instance-pool-id {instance_pool_id} --force",
        "manage": """# Scale in/out
oci compute instance-pool update --instance-pool-id {instance_pool_id} --size {new_size}

# Attach/detach instances
oci compute instance-pool attach-instance --instance-pool-id {instance_pool_id} --instance-configuration-id {config_id}""",
    },
    "compute/custom-images": {
        "create": "oci compute image create --compartment-id {compartment_id} --instance-id {instance_id} --display-name {name}",
        "list": "oci compute image list --compartment-id {compartment_id} --operating-system 'Oracle Linux'",
        "get": "oci compute image get --image-id {image_id}",
        "update": "oci compute image update --image-id {image_id} --display-name {name}",
        "delete": "oci compute image delete --image-id {image_id} --force",
        "manage": "oci compute image get --image-id {image_id}",
    },
    "storage/block": {
        "create": "oci bv volume create --compartment-id {compartment_id} --availability-domain {ad} --size-in-gbs {size} --display-name {name}",
        "list": "oci bv volume list --compartment-id {compartment_id} --availability-domain {ad}",
        "get": "oci bv volume get --volume-id {volume_id}",
        "update": "oci bv volume update --volume-id {volume_id} --size-in-gbs {size}",
        "delete": "oci bv volume delete --volume-id {volume_id} --force",
        "attach": "oci bv volume-attachment attach --instance-id {instance_id} --volume-id {volume_id} --type {type}",
        "manage": "oci bv volume-attachment list --compartment-id {compartment_id}",
    },
    "storage/object": {
        "create": "oci os bucket create --name {bucket_name} --compartment-id {compartment_id} --storage-tier Standard",
        "list": "oci os bucket list --compartment-id {compartment_id}",
        "get": "oci os bucket get --bucket-name {bucket_name} --namespace-name {namespace}",
        "update": "oci os bucket update --bucket-name {bucket_name} --namespace-name {namespace}",
        "delete": "oci os bucket delete --bucket-name {bucket_name} --namespace-name {namespace} --force",
        "manage": "oci os object list --bucket-name {bucket_name} --namespace-name {namespace}",
    },
    "storage/file": {
        "create": "oci fs mount-target create --compartment-id {compartment_id} --subnet-id {subnet_id} --display-name {name}",
        "list": "oci fs mount-target list --compartment-id {compartment_id}",
        "get": "oci fs mount-target get --mount-target-id {mount_target_id}",
        "update": "oci fs mount-target update --mount-target-id {mount_target_id}",
        "delete": "oci fs mount-target delete --mount-target-id {mount_target_id} --force",
        "manage": "oci fs export list --mount-target-id {mount_target_id}",
    },
    "networking/vcn": {
        "create": "oci network vcn create --compartment-id {compartment_id} --cidr-blocks ['{cidr}'] --display-name {vcn_name}",
        "list": "oci network vcn list --compartment-id {compartment_id}",
        "get": "oci network vcn get --vcn-id {vcn_id}",
        "update": "oci network vcn update --vcn-id {vcn_id} --display-name {vcn_name}",
        "delete": "oci network vcn delete --vcn-id {vcn_id} --force",
        "manage": "oci network subnet list --vcn-id {vcn_id}",
    },
    "networking/security": {
        "create": "oci network security-list create --compartment-id {compartment_id} --vcn-id {vcn_id} --display-name {name}",
        "list": "oci network security-list list --vcn-id {vcn_id}",
        "get": "oci network security-list get --security-list-id {security_list_id}",
        "update": "oci network security-list update --security-list-id {security_list_id}",
        "delete": "oci network security-list delete --security-list-id {security_list_id} --force",
        "manage": "oci network security-rule list --security-list-id {security_list_id}",
    },
    "networking/connectivity": {
        "create": "oci network drg create --compartment-id {compartment_id} --display-name {name}",
        "list": "oci network drg list --compartment-id {compartment_id}",
        "get": "oci network drg get --drg-id {drg_id}",
        "update": "oci network drg update --drg-id {drg_id}",
        "delete": "oci network drg delete --drg-id {drg_id} --force",
        "manage": "oci network drg-attachment list --drg-id {drg_id}",
    },
    "lb/load-balancer": {
        "create": "oci lb load-balancer create --shape {shape} --subnet-ids ['{subnet_id}'] --display-name {name} --compartment-id {compartment_id}",
        "list": "oci lb load-balancer list --compartment-id {compartment_id}",
        "get": "oci lb load-balancer get --load-balancer-id {lb_id}",
        "update": "oci lb load-balancer update --load-balancer-id {lb_id} --display-name {name}",
        "delete": "oci lb load-balancer delete --load-balancer-id {lb_id} --force",
        "manage": "oci lb backend set list --load-balancer-id {lb_id}",
    },
    "database/autonomous": {
        "create": "oci db autonomous-database create --compartment-id {compartment_id} --cpu-core-count {cores} --storage-size-in-tbs {storage} --db-workload {workload} --license-type LICENSE_INCLUDED --display-name {name}",
        "list": "oci db autonomous-database list --compartment-id {compartment_id} --lifecycle-state AVAILABLE",
        "get": "oci db autonomous-database get --autonomous-database-id {adb_id}",
        "update": "oci db autonomous-database update --autonomous-database-id {adb_id} --cpu-core-count {cores}",
        "delete": "oci db autonomous-database delete --autonomous-database-id {adb_id} --force",
        "manage": "oci db autonomous-database get --autonomous-database-id {adb_id}",
    },
    "database/mysql": {
        "create": "oci db system create --compartment-id {compartment_id} --display-name {name} --shape {shape} --mysql-version {version} --admin-password {password}",
        "list": "oci db system list --compartment-id {compartment_id}",
        "get": "oci db system get --db-system-id {db_system_id}",
        "update": "oci db system update --db-system-id {db_system_id}",
        "delete": "oci db system delete --db-system-id {db_system_id} --force",
        "manage": "oci db system get --db-system-id {db_system_id}",
    },
    "database/postgresql": {
        "create": "oci db postgres instance create --compartment-id {compartment_id} --display-name {name} --shape {shape} --db-version {version}",
        "list": "oci db postgres instance list --compartment-id {compartment_id}",
        "get": "oci db postgres instance get --postgres-instance-id {postgres_id}",
        "update": "oci db postgres instance update --postgres-instance-id {postgres_id}",
        "delete": "oci db postgres instance delete --postgres-instance-id {postgres_id} --force",
        "manage": "oci db postgres instance get --postgres-instance-id {postgres_id}",
    },
    "database/nosql": {
        "create": "oci nosql table create --compartment-id {compartment_id} --name {table_name} --ddl 'CREATE TABLE {table_name} (id STRING PRIMARY KEY, data JSON)'",
        "list": "oci nosql table list --compartment-id {compartment_id}",
        "get": "oci nosql table get --table-name {table_name} --compartment-id {compartment_id}",
        "update": "oci nosql table update --table-name {table_name} --compartment-id {compartment_id}",
        "delete": "oci nosql table delete --table-name {table_name} --compartment-id {compartment_id} --force",
        "manage": "oci nosql table get --table-name {table_name} --compartment-id {compartment_id}",
    },
    "database/autonomous-json": {
        "create": "oci db autonomous-database create --compartment-id {compartment_id} --cpu-core-count {cores} --storage-size-in-tbs {storage} --db-workload JSON --display-name {name}",
        "list": "oci db autonomous-database list --compartment-id {compartment_id} --db-workload JSON",
        "get": "oci db autonomous-database get --autonomous-database-id {adb_id}",
        "update": "oci db autonomous-database update --autonomous-database-id {adb_id}",
        "delete": "oci db autonomous-database delete --autonomous-database-id {adb_id} --force",
        "manage": "oci db autonomous-database get --autonomous-database-id {adb_id}",
    },
    "database/exadata": {
        "create": "oci db exadata-infrastructure create --compartment-id {compartment_id} --display-name {name} --shape {shape} --availability-domain {ad}",
        "list": "oci db exadata-infrastructure list --compartment-id {compartment_id}",
        "get": "oci db exadata-infrastructure get --exadata-infrastructure-id {exadata_id}",
        "update": "oci db exadata-infrastructure update --exadata-infrastructure-id {exadata_id}",
        "delete": "oci db exadata-infrastructure delete --exadata-infrastructure-id {exadata_id} --force",
        "manage": "oci db cloud-exadata-cluster list --compartment-id {compartment_id}",
    },
    "database/exadata-cloud": {
        "create": "oci db cloud-exadata-cluster create --infrastructure-id {infra_id} --display-name {name} --compartment-id {compartment_id}",
        "list": "oci db cloud-exadata-cluster list --compartment-id {compartment_id}",
        "get": "oci db cloud-exadata-cluster get --cloud-exadata-cluster-id {cluster_id}",
        "update": "oci db cloud-exadata-cluster update --cloud-exadata-cluster-id {cluster_id}",
        "delete": "oci db cloud-exadata-cluster delete --cloud-exadata-cluster-id {cluster_id} --force",
        "manage": "oci db cloud-exadata-vm-cluster list --compartment-id {compartment_id}",
    },
    "migration/aws-compute": {
        "describe": """Para migrar instâncias EC2 para OCI Compute:

1. **Assessment**: Use OCI Migration Service para descubrir EC2s
2. **Planejamento**: Crie compartment dedicado para migração
3. **Execução**:
```bash
# Liste instâncias EC2 para identificar candidates
aws ec2 describe-instances --filters Name=instance-state-name,Values=running

# Crie instância OCI equivalente
oci compute instance launch --availability-domain {ad} --shape {shape} --subnet-id <subnet-ocid> --display-name <nome>
```

4. **Validação**: Teste performance e funcionaliade após migração""",
    },
    "migration/aws-storage": {
        "describe": """Para migrar EBS volumes para OCI Block Storage:

1. **Assessment**: Identifique volumes EBSAttached a EC2s
2. **Backup**: Crie snapshots EBS antes da migração
3. **Execução**:
```bash
# Crie snapshot EBS
aws ec2 create-snapshot --volume-id <vol-id>

# Crie volume OCI equivalent
oci bv volume create --compartment-id {compartment_id} --availability-domain {ad} --size-in-gbs <size> --display-name <nome>
```

4. **Migração de dados**: Use rsync ou ferramentas de transferência OCI""",
    },
    "migration/aws-database": {
        "describe": """Para migrar RDS para OCI Autonomous Database:

1. **Export**: Exporte dados RDS para S3 (dump SQL ou CSV)
2. **Provision**: Crie Autonomous Database em OCI:
```bash
oci db autonomous-database create --compartment-id {compartment_id} --cpu-core-count {cores} --storage-size-in-tbs {storage} --db-workload AUTONOMOUS_TRANSACTION_PROCESSING --display-name <nome>
```

3. **Import**: Use Data Pump para importar dados
4. **Validação**: Verifique integridade e performance""",
    },
    "migration/azure-compute": {
        "describe": """Para migrar Azure VMs para OCI Compute:

1. **Assessment**: Identifique VMs Azure para migração
2. **Planejamento**: Selecione shapes OCI equivalentes
3. **Execução**:
```bash
# Crie instância OCI
oci compute instance launch --availability-domain {ad} --shape {shape} --subnet-id <subnet-ocid> --display-name <nome> --compartment-id {compartment_id}
```

4. **Migração**: Use Azure Site Recovery ou migração manual""",
    },
    "migration/azure-storage": {
        "describe": """Para migrar Azure Blob para OCI Object Storage:

1. **Export**: Use AzCopy para exportar blobs para arquivo local
2. **Upload**: Carregue para OCI Object Storage:
```bash
oci os object put --bucket-name <bucket> --file-path <arquivo> --namespace-name {namespace}
```

3. **Validação**: Verifique integridade dos dados""",
    },
    "migration/azure-database": {
        "describe": """Para migrar Azure SQL para OCI Autonomous Database:

1. **Export**: Exporte Azure SQL para BACPAC
2. **Transfer**: Carregue arquivo para OCI Object Storage
3. **Import**: Use Data Pump para importar no Autonomous:
```bash
oci db autonomous-database create --compartment-id {compartment_id} --cpu-core-count {cores} --storage-size-in-tbs {storage} --display-name <nome>
```""",
    },
    "migration/gcp-compute": {
        "describe": """Para migrar GCE para OCI Compute:

1. **Assessment**: Use Migrate for Compute Engine (M4CE)
2. **Planejamento**: Configure conexão entre GCP e OCI
3. **Execução**:
```bash
oci compute instance launch --availability-domain {ad} --shape {shape} --subnet-id <subnet-ocid> --display-name <nome> --compartment-id {compartment_id}
```""",
    },
    "migration/gcp-storage": {
        "describe": """Para migrar GCS para OCI Object Storage:

1. **Export**: Use gsutil para exportar bucket GCS
2. **Upload**: Carregue para OCI:
```bash
oci os object put --bucket-name <bucket> --file-path <arquivo> --namespace-name {namespace}
```""",
    },
    "migration/gcp-database": {
        "describe": """Para migrar Cloud SQL para OCI Autonomous Database:

1. **Export**: Exporte Cloud SQL para SQL dump
2. **Provision**: Crie Autonomous Database:
```bash
oci db autonomous-database create --compartment-id {compartment_id} --cpu-core-count {cores} --storage-size-in-tbs {storage} --display-name <nome>
```

3. **Import**: Execute dump no Autonomous""",
    },
    "migration/onprem-compute": {
        "describe": """Para migrar VMs on-premises para OCI Compute:

1. **Assessment**: Inventário de VMs (VMware, Hyper-V, físico)
2. **Planejamento**: Selecione estratégia (lift-and-shift ou re-platform)
3. **Execução**:
```bash
# Crie instância OCI
oci compute instance launch --availability-domain {ad} --shape {shape} --subnet-id <subnet-ocid> --display-name <nome> --compartment-id {compartment_id}
```

4. **Migração**: Use OCI Migration Service ou manually""",
    },
    "migration/onprem-storage": {
        "describe": """Para migrar storage on-premises para OCI:

1. **Assessment**: Identifique dados críticos e حجم
2. **Transfer**: Use OCI Object Storage Multipart Upload ou Snowball
3. **Execução**:
```bash
oci os bucket create --name {bucket_name} --compartment-id {compartment_id} --storage-tier Standard
```""",
    },
    "migration/onprem-vmware": {
        "describe": """Para migrar VMware para OCI:

1. **Assessment**: Use OCI VMware Solution para评估
2. **Planejamento**: Configure OCI VMware Solution (SDDC)
3. **Migração**: Use VMware HCX para vMotion""",
    },
    "migration/onprem-database": {
        "describe": """Para migrar databases on-premises para OCI:

1. **Assessment**: Identifique banco de dados (Oracle, SQL Server, PostgreSQL)
2. **Export**: Crie export/full dump
3. **Provision**: Crie recurso OCI equivalente:
```bash
# Para Oracle
oci db system create --compartment-id {compartment_id} --display-name {name} --shape {shape} --mysql-version {version}
```""",
    },
    "migration/data-transfer": {
        "describe": """Para transfer de dados para OCI:

1. **Pequenos volumes** (< 10TB): Use internet com multipart upload
2. **Médios volumes** (10TB - 1PB): Use OCI Object Storage Transfer Appliance (Snowball Edge)
3. **Grandes volumes** (> 1PB): Use OCI Data Transfer Service
4. **CLI**:
```bash
oci os object put --bucket-name <bucket> --file-path <arquivo> --namespace-name {namespace}
```""",
    },
    # Container - MISSING CLI COMMANDS ADDED
    "container/oke": {
        "create": 'oci container cluster create --compartment-id {compartment_id} --name {name} --kubernetes-version {k8s_version} --vcn-id {vcn_id} --node-pool-details \'[{"size":2,"shape":"VM.Standard.E4.Flex","imageId":"Oracle-Linux-8"}]\'',
        "list": "oci container cluster list --compartment-id {compartment_id}",
        "get": "oci container cluster get --cluster-id {cluster_id}",
        "delete": "oci container cluster delete --cluster-id {cluster_id} --force",
        "update": "oci container cluster update --cluster-id {cluster_id} --kubernetes-version {k8s_version}",
        "manage": "kubectl get nodes && kubectl get pods -A",
    },
    "container/instances": {
        "create": 'oci container instance create --compartment-id {compartment_id} --display-name {name} --container-config \'[{"imageUrl":"{image}","cpu":1,"memory":2}]\' --shape VM.Standard.E4.Flex',
        "list": "oci container instance list --compartment-id {compartment_id}",
        "get": "oci container instance get --container-instance-id {instance_id}",
        "delete": "oci container instance delete --container-instance-id {instance_id} --force",
        "update": "oci container instance update --container-instance-id {instance_id} --display-name {name}",
        "manage": "oci container instance get --container-instance-id {instance_id}",
    },
    # Serverless - MISSING CLI COMMANDS ADDED
    "serverless/functions": {
        "create": "oci fn function create --application-id {app_id} --display-name {name} --image {image} --memory 256",
        "list": "oci fn function list --application-id {app_id}",
        "get": "oci fn function get --function-id {function_id}",
        "delete": "oci fn function delete --function-id {function_id} --force",
        "update": "oci fn function update --function-id {function_id} --image {image}",
        "manage": "oci fn invocation invoke --function-id {function_id} --body '{}'",
    },
    "serverless/api-gateway": {
        "create": "oci api-gateway gateway create --compartment-id {compartment_id} --display-name {name} --endpoint https://{domain}",
        "list": "oci api-gateway gateway list --compartment-id {compartment_id}",
        "get": "oci api-gateway gateway get --gateway-id {gateway_id}",
        "delete": "oci api-gateway gateway delete --gateway-id {gateway_id} --force",
        "update": "oci api-gateway gateway update --gateway-id {gateway_id} --display-name {name}",
        "manage": "oci api-gateway deployment list --gateway-id {gateway_id}",
    },
    # Governance - MISSING CLI COMMANDS ADDED
    "governance/compartments": {
        "create": "oci iam compartment create --compartment-id {tenancy_id} --name {name} --description {description}",
        "list": "oci iam compartment list --compartment-id {tenancy_id}",
        "get": "oci iam compartment get --compartment-id {compartment_id}",
        "delete": "oci iam compartment delete --compartment-id {compartment_id} --force",
        "update": "oci iam compartment update --compartment-id {compartment_id} --description {description}",
        "manage": "oci iam compartment list --compartment-id {tenancy_id}",
    },
    "governance/tagging": {
        "create": "oci iam tag-namespace create --compartment-id {compartment_id} --name {namespace_id}",
        "list": "oci iam tag-namespace list --compartment-id {compartment_id}",
        "get": "oci iam tag-namespace get --tag-namespace-id {namespace_id}",
        "delete": "oci iam tag-namespace delete --tag-namespace-id {namespace_id} --force",
        "update": "oci iam tag-namespace update --tag-namespace-id {namespace_id}",
        "manage": "oci iam tag list --compartment-id {compartment_id}",
    },
    "governance/policies-guardrails": {
        "create": "oci iam policy create --compartment-id {compartment_id} --name {policy_name} --statement {statement}",
        "list": "oci iam policy list --compartment-id {compartment_id}",
        "get": "oci iam policy get --policy-id {policy_id}",
        "delete": "oci iam policy delete --policy-id {policy_id} --force",
        "update": "oci iam policy update --policy-id {policy_id} --statement {statement}",
        "manage": "oci iam policy list --compartment-id {compartment_id}",
    },
    "governance/landing-zone": {
        "create": "oci iam compartment create --compartment-id {tenancy_id} --name landing-zone --description 'Landing Zone for enterprise'",
        "list": "oci iam compartment list --compartment-id {tenancy_id}",
        "get": "oci iam compartment get --compartment-id {compartment_id}",
        "delete": "oci iam compartment delete --compartment-id {compartment_id} --force",
        "update": "oci iam compartment update --compartment-id {compartment_id}",
        "manage": "oci iam policy list --compartment-id {compartment_id}",
    },
    # Observability - ADD MISSING
    "observability/logging": {
        "create": "oci logging log create --log-group-id {log_group_id} --display-name {name} --log-type CUSTOM",
        "list": "oci logging log list --log-group-id {log_group_id}",
        "get": "oci logging log get --log-id {log_id}",
        "delete": "oci logging log delete --log-id {log_id} --force",
        "update": "oci logging log update --log-id {log_id}",
        "manage": "oci logging search --log-group-id {log_group_id} --search-query 'search'",
    },
    "observability/monitoring": {
        "create": "oci monitoring alarm create --compartment-id {compartment_id} --display-name {name} --metric-name {metric} --threshold 80",
        "list": "oci monitoring alarm list --compartment-id {compartment_id}",
        "get": "oci monitoring alarm get --alarm-id {alarm_id}",
        "delete": "oci monitoring alarm delete --alarm-id {alarm_id} --force",
        "update": "oci monitoring alarm update --alarm-id {alarm_id} --threshold 90",
        "manage": "oci monitoring metric get --compartment-id {compartment_id} --metric-name {metric}",
    },
    # FinOps - ADD MISSING
    "finops/cost-optimization": {
        "create": 'oci usage budget create --compartment-id {compartment_id} --amount {amount} --alert-rules \'[{"type":"ACTUAL","threshold":80}]\'',
        "list": "oci usage budget list --compartment-id {compartment_id}",
        "get": "oci usage budget get --budget-id {budget_id}",
        "delete": "oci usage budget delete --budget-id {budget_id} --force",
        "update": "oci usage budget update --budget-id {budget_id} --amount {amount}",
        "manage": "oci usage cost-analysis query --compartment-id {compartment_id} --granularity MONTHLY",
    },
    # Platform - ADD MISSING
    "platform/backup-governance": {
        "create": "oci backup backup-job create --compartment-id {compartment_id} --target-id {instance_id} --backup-type FULL",
        "list": "oci backup backup-job list --compartment-id {compartment_id}",
        "get": "oci backup backup-job get --backup-job-id {backup_job_id}",
        "delete": "oci backup backup-job delete --backup-job-id {backup_job_id} --force",
        "update": "oci backup backup-job update --backup-job-id {backup_job_id}",
        "manage": "oci backup backup-repository list --compartment-id {compartment_id}",
    },
    # Security - MISSING CLI COMMANDS ADDED
    "security/iam-basics": {
        "create": "oci iam user create --compartment-id {compartment_id} --description {description} --email {email}",
        "list": "oci iam user list --compartment-id {compartment_id}",
        "get": "oci iam user get --user-id {user_id}",
        "update": "oci iam user update --user-id {user_id}",
        "delete": "oci iam user delete --user-id {user_id} --force",
        "manage": "oci iam group list --compartment-id {compartment_id}",
    },
    "security/policies": {
        "create": "oci iam policy create --compartment-id {compartment_id} --name {policy_name} --statement {statement}",
        "list": "oci iam policy list --compartment-id {compartment_id}",
        "get": "oci iam policy get --policy-id {policy_id}",
        "update": "oci iam policy update --policy-id {policy_id}",
        "delete": "oci iam policy delete --policy-id {policy_id} --force",
        "manage": "oci iam policy get --policy-id {policy_id}",
    },
    "security/dynamic-groups": {
        "create": "oci iam dynamic-group create --compartment-id {compartment_id} --matching-rule {rule}",
        "list": "oci iam dynamic-group list --compartment-id {compartment_id}",
        "get": "oci iam dynamic-group get --dynamic-group-id {dynamic_group_id}",
        "update": "oci iam dynamic-group update --dynamic-group-id {dynamic_group_id}",
        "delete": "oci iam dynamic-group delete --dynamic-group-id {dynamic_group_id} --force",
        "manage": "oci iam policy list --compartment-id {compartment_id}",
    },
    "security/vault-secrets": {
        "create": "oci vault secret create --vault-id {vault_id} --secret-name {name} --secret-content-file {file}",
        "list": "oci vault secret list --vault-id {vault_id}",
        "get": "oci vault secret get --secret-id {secret_id}",
        "update": "oci vault secret update --secret-id {secret_id}",
        "delete": "oci vault secret delete --secret-id {secret_id} --force",
        "manage": "oci vault secret get --secret-id {secret_id}",
    },
    "security/vault-keys": {
        "create": 'oci vault key create --compartment-id {compartment_id} --key-shape \'{"algorithm":"RSA"}\' --display-name {name}',
        "list": "oci vault key list --vault-id {vault_id}",
        "get": "oci vault key get --key-id {key_id}",
        "update": "oci vault key update --key-id {key_id}",
        "delete": "oci vault key delete --key-id {key_id} --force",
        "manage": "oci vault key get --key-id {key_id}",
    },
    "security/encryption": {
        "create": "oci vault vault create --compartment-id {compartment_id} --vault-type DEFAULT --display-name {name}",
        "list": "oci vault vault list --compartment-id {compartment_id}",
        "get": "oci vault vault get --vault-id {vault_id}",
        "update": "oci vault vault update --vault-id {vault_id}",
        "delete": "oci vault vault delete --vault-id {vault_id} --force",
        "manage": "oci vault key list --vault-id {vault_id}",
    },
    "security/cloud-guard": {
        "create": "oci cloud-guard detector create --compartment-id {compartment_id} --display-name {name}",
        "list": "oci cloud-guard detector list --compartment-id {compartment_id}",
        "get": "oci cloud-guard detector get --detector-id {detector_id}",
        "update": "oci cloud-guard detector update --detector-id {detector_id}",
        "delete": "oci cloud-guard detector delete --detector-id {detector_id} --force",
        "manage": "oci cloud-guard problem list --compartment-id {compartment_id}",
    },
    # DevOps - MISSING CLI COMMANDS ADDED
    "devops/ci-cd": {
        "create": "oci devops pipeline create --project-id {project_id} --display-name {name}",
        "list": "oci devops pipeline list --project-id {project_id}",
        "get": "oci devops pipeline get --pipeline-id {pipeline_id}",
        "update": "oci devops pipeline update --pipeline-id {pipeline_id}",
        "delete": "oci devops pipeline delete --pipeline-id {pipeline_id} --force",
        "manage": "oci devops pipeline list --project-id {project_id}",
    },
    "devops/artifacts": {
        "create": "oci devops artifact create --project-id {project_id} --display-name {name} --artifact-type DOCKER",
        "list": "oci devops artifact list --project-id {project_id}",
        "get": "oci devops artifact get --artifact-id {artifact_id}",
        "update": "oci devops artifact update --artifact-id {artifact_id}",
        "delete": "oci devops artifact delete --artifact-id {artifact_id} --force",
        "manage": "oci devops artifact list --project-id {project_id}",
    },
    "devops/secrets": {
        "create": "oci vault secret create --vault-id {vault_id} --secret-name {name} --secret-content {content}",
        "list": "oci vault secret list --vault-id {vault_id}",
        "get": "oci vault secret get --secret-id {secret_id}",
        "update": "oci vault secret update --secret-id {secret_id}",
        "delete": "oci vault secret delete --secret-id {secret_id} --force",
        "manage": "oci vault secret get --secret-id {secret_id}",
    },
    "devops/resource-manager": {
        "create": "oci resourcemanager stack create --compartment-id {compartment_id} --display-name {name}",
        "list": "oci resourcemanager stack list --compartment-id {compartment_id}",
        "get": "oci resourcemanager stack get --stack-id {stack_id}",
        "update": "oci resourcemanager stack update --stack-id {stack_id}",
        "delete": "oci resourcemanager stack delete --stack-id {stack_id} --force",
        "manage": "oci resourcemanager job list --stack-id {stack_id}",
    },
    "terraform/provider": {
        "create": """Configure provider OCI:

```hcl
provider "oci" {
  tenancy_ocid     = var.tenancy_ocid
  user_ocid       = var.user_ocid
  fingerprint     = var.fingerprint
  private_key     = var.private_key
  region          = var.region
}
```

Use instance principal para autenticação em produção.""",
        "list": "terraform init e terraform plan para validar configuração.",
    },
    "terraform/compute": {
        "create": """Crie recurso Compute Instance:

```hcl
resource "oci_compute_instance" "example" {
  compartment_id = var.compartment_id
  display_name   = "example-instance"
  shape          = "VM.Standard.E4.Flex"
  
  shape_config {
    ocpus         = 2
    memory_in_gbs = 16
  }
  
  source_details {
    source_type = "image"
    image_ocid  = "ocid1.image.oc1.sa-saopaulo-1.xxx"
  }
  
  subnet_id = "ocid1.subnet.oc1.sa-saopaulo-1.xxx"
}
```""",
    },
    "terraform/storage": {
        "create": """Crie recursos de storage:

```hcl
# Block Volume
resource "oci_blockstorage_volume" "example" {
  compartment_id = var.compartment_id
  display_name   = "example-volume"
  size_in_gbs    = 100
}

# Object Storage Bucket
resource "oci_objectstorage_bucket" "example" {
  compartment_id = var.compartment_id
  name           = "example-bucket"
  namespace      = var.namespace
  storage_tier   = "Standard"
}
```""",
    },
    "terraform/networking": {
        "create": """Crie recursos de networking:

```hcl
# VCN
resource "oci_core_vcn" "example" {
  compartment_id = var.compartment_id
  cidr_block     = "10.0.0.0/16"
  display_name   = "example-vcn"
}

# Subnet
resource "oci_core_subnet" "example" {
  compartment_id = var.compartment_id
  vcn_id         = oci_core_vcn.example.id
  cidr_block     = "10.0.1.0/24"
  display_name   = "example-subnet"
}
```""",
    },
    "terraform/load-balancer": {
        "create": """Crie Load Balancer:

```hcl
resource "oci_load_balancer" "example" {
  compartment_id = var.compartment_id
  display_name   = "example-lb"
  shape          = "100Mbps"
  subnet_ids     = [oci_core_subnet.example.id]
}

resource "oci_load_balancer_backendset" "example" {
  load_balancer_id = oci_load_balancer.example.id
  name             = "backend-set"
  health_checker {
    protocol = "HTTP"
    port     = 80
    url_path = "/health"
  }
}
```""",
    },
    "terraform/database": {
        "create": """Crie Autonomous Database:

```hcl
resource "oci_database_autonomous_database" "example" {
  compartment_id           = var.compartment_id
  display_name             = "example-adb"
  cpu_core_count           = 2
  storage_size_in_tbs      = 1
  db_workload              = "AUTONOMOUS_TRANSACTION_PROCESSING"
  license_type             = "LICENSE_INCLUDED"
}
```""",
    },
    "terraform/container": {
        "create": """Crie OKE Cluster:

```hcl
resource "oci_container_cluster" "example" {
  compartment_id     = var.compartment_id
  name              = "example-cluster"
  kubernetes_version = "v1.28.2"
  vcn_id            = oci_core_vcn.example.id
  
  options {
    service_lb_subnet_ids = [oci_core_subnet.example.id]
  }
}

resource "oci_container_node_pool" "example" {
  cluster_id = oci_container_cluster.example.id
  name       = "example-nodepool"
  node_shape = "VM.Standard.E4.Flex"
  node_count = 3
}
```""",
    },
    "terraform/serverless": {
        "create": """Crie OCI Functions:

```hcl
resource "oci_functions_application" "example" {
  compartment_id = var.compartment_id
  display_name    = "example-app"
  subnet_ids      = [oci_core_subnet.example.id]
}

resource "oci_functions_function" "example" {
  application_id = oci_functions_application.example.id
  display_name   = "example-function"
  image          = "example-image:latest"
  memory_in_mbs  = 256
}
```""",
    },
    "terraform/security": {
        "create": """Recursos de segurança:

```hcl
# IAM User
resource "oci_identity_user" "example" {
  compartment_id = var.compartment_id
  name          = "example-user"
  description   = "Example user"
}

# IAM Group
resource "oci_identity_group" "example" {
  compartment_id = var.compartment_id
  name          = "example-group"
  description   = "Example group"
}

# Policy
resource "oci_identity_policy" "example" {
  compartment_id = var.compartment_id
  name           = "example-policy"
  statements     = ["Allow group example-group to manage all-resources in compartment ${var.compartment_id}"]
}
```""",
    },
    "terraform/observability": {
        "create": """Recursos de observability:

```hcl
# Log Group
resource "oci_logging_log_group" "example" {
  compartment_id = var.compartment_id
  display_name   = "example-log-group"
}

# Alarm
resource "oci_monitoring_alarm" "example" {
  compartment_id  = var.compartment_id}
  display_name    = "example-alarm"
  metric_name     = "CpuUtilization"
  namespace       = "oci_compute"
  severity        = "CRITICAL"
  compartment_id  = var.compartment_id
}
```""",
    },
    "terraform/devops": {
        "create": """Recursos DevOps:

```hcl
# DevOps Project
resource "oci_devops_project" "example" {
  compartment_id = var.compartment_id
  display_name   = "example-project"
}

# Resource Manager Stack
resource "oci_resourcemanager_stack" "example" {
  compartment_id      = var.compartment_id}
  display_name        = "example-stack"
  terraform_version   = "1.0"
}
```""",
    },
    "terraform/state": {
        "configure": """Configure Remote State:

```hcl
terraform {
  backend "s3" {
    bucket         = "terraform-state"
    key            = "prod/terraform.tfstate"
    region         = "sa-saopaulo-1"
  }
}
```

Use OCI Object Storage para state.""",
    },
    "troubleshooting/connectivity": {
        "diagnose": """Diagnose conectividade VCN:

1. **Verifique VCN**: `oci network vcn get --vcn-id <vcn-ocid>`
2. **Check Subnets**: `oci network subnet list --vcn-id <vcn-ocid>`
3. **Verify Security Lists**: `oci network security-list list --vcn-id <vcn-ocid>`
4. **Teste连通性**:
```bash
# De instância
ping <destino>

# Trace route
traceroute <destino>

# Check NSG
oci network nsg rules list --network-security-group-id <nsg-ocid>
```""",
    },
    "troubleshooting/performance": {
        "diagnose": """Diagnose performance Compute:

1. **Check métricas**:
```bash
oci monitoring metric-data get --metric-name CpuUtilization --namespace oci_compute --resource-id <instance-ocid>
```

2. **Verifique shapes**: Shape tem recursos suficientes?
3. **Check block volumes**: IOPS atingindo limits?
4. **Analyze networking**: Latência de rede?

5. **Soluções**:
- Upscale shape (mais OCPUs/memory)
- Use block volume com mais IOPS
- Configure auto-scaling""",
    },
    "troubleshooting/authentication": {
        "diagnose": """Diagnose autenticação IAM:

1. **Verify user**:
```bash
oci iam user get --user-id <user-ocid>
```

2. **Check groups**:
```bash
oci iam group list --compartment-id <tenancy-ocid>
```

3. **Verify policies**:
```bash
oci iam policy list --compartment-id <compartment-ocid>
```

4. **Check API keys**:
```bash
oci iam user api-keys list --user-id <user-ocid>
```

5. **Soluções**:
- Adicione user ao group correto
- Crie/atualize policy com permissões
- Regenerate API keys""",
    },
    "troubleshooting/database": {
        "diagnose": """Diagnose Autonomous Database:

1. **Check status**:
```bash
oci db autonomous-database get --autonomous-database-id <adb-ocid>
```

2. **Verify connectivity**:
```bash
oci db autonomous-database wallet download --autonomous-database-id <adb-ocid> --password <password>
```

3. **Check metrics**:
```bash
oci monitoring metric-data get --metric-name CPUActivity --namespace oci_database --resource-id <adb-ocid>
```

4. **Soluções**:
- Restart Autonomous se necessário
- Scale up/down CPU/storage
- Use connection pooling""",
    },
    "troubleshooting/compute": {
        "diagnose": """Diagnose instância Compute:

1. **Check status**:
```bash
oci compute instance get --instance-id <instance-ocid>
```

2. **Get console output**:
```bash
oci compute instance get --instance-id <instance-ocid> --raw-output --query 'data."console-output".value' | base64 -d
```

3. **Check VNIC**:
```bash
oci network vnic get --vnic-id <vnic-ocid>
```

4. **Soluções**:
- Reboot/Stop/Start instância
- Reattach VNIC
- Recreate se necessário""",
    },
    "troubleshooting/storage": {
        "diagnose": """Diagnose storage performance:

1. **Check volumes**:
```bash
oci bv volume get --volume-id <volume-ocid>
```

2. **Check IOPS/throughput**:
```bash
oci bv volume metrics get --volume-id <volume-ocid>
```

3. **Verify limits**:
```bash
oci limits resource-availability get --service-name blockstorage --compartment-id <compartment-ocid>
```

4. **Soluções**:
- Use volume com mais IOPS
- Attach to faster shape
- Configure volume performance tier""",
    },
    "troubleshooting/oke": {
        "diagnose": """Diagnose OKE cluster:

1. **Check cluster**:
```bash
oci ce cluster get --cluster-id <cluster-ocid>
```

2. **Check node pools**:
```bash
oci ce node-pool list --cluster-id <cluster-ocid>
```

3. **Get cluster kubeconfig**:
```bash
oci ce cluster kubeconfig get --cluster-id <cluster-ocid> --file kubeconfig
```

4. **Check nodes**:
```bash
kubectl get nodes
kubectl describe node <node-name>
```

5. **Check events**:
```bash
kubectl get events --all-namespaces""",
    },
    "troubleshooting/functions": {
        "diagnose": """Diagnose OCI Functions:

1. **Check function**:
```bash
oci fn function get --function-id <function-ocid>
```

2. **Check invocation logs**:
```bash
oci logging log list --source-id <function-ocid> --log-group-id <log-group-ocid>
```

3. **Teste invoke**:
```bash
oci fn invocation invoke --function-id <function-ocid> --body '{}'
```

4. **Check application**:
```bash
oci fn application get --application-id <app-ocid>
```""",
    },
    "governance/landing-zone": {
        "create": """Crie Landing Zone OCI:

1. **Estrutura de compartments**:
```bash
oci iam compartment create --compartment-id <tenancy-ocid> --name production --description "Production compartment"
oci iam compartment create --compartment-id <tenancy-ocid> --name development --description "Development compartment"
oci iam compartment create --compartment-id <tenancy-ocid> --name sandbox --description "Sandbox compartment"
```

2. **Políticas base**: Alocar policies para cada compartment

3. **VCN central**: Criar VCN hub para connectivity

4. **Tagging namespace**: Criar tag namespace para cost tracking""",
    },
    "governance/policies-guardrails": {
        "create": """Crie políticas de compliance:

```bash
# Restringir regiões
oci iam policy create --compartment-id <tenancy-ocid> --name restrict-regions --statements ['Allow group admins to use resources in compartment id <compartment-ocid> where request.region in ["sa-saopaulo-1", "us-ashburn-1"]']

# Require tags
oci iam policy create --compartment-id <tenancy-ocid> --name require-tags --statements ['Allow group users to create any-resource in compartment id <compartment-ocid> where definedTags.namespace1.tag1 exists']

# Restringir shapes caros
oci iam policy create --compartment-id <tenancy-ocid> --name restrict-shapes --statements ['Deny group users to launch instance where shape in ["BM.GPU4.8", "VM.GPU.A10.2"]']
```""",
    },
    "governance/compliance": {
        "audit": """Execute auditoria de compliance:

1. **Ative Cloud Guard**:
```bash
oci cloud-guard detector create --compartment-id <tenancy-ocid> --display-name "primary-detector"
```

2. **Verifique auditing**:
```bash
oci logging log list --log-group-id <audit-group-id> --start-time <30-days-ago>
```

3. **Gere relatório**:
- Liste recursos por compartment
- Verifique políticas aplicadas
- Check tagging compliance

4. **Documente findings**: Use spreadsheet para tracking""",
    },
    "governance/audit-readiness": {
        "prepare": """Prepare OCI para auditoria:

1. **Configure audit retention** (default 90 dias):
```bash
oci logging log-group update --log-group-id <group-ocid> --retention-duration 365
```

2. **Ative export de logs**: Exporte para Object Storage para long-term retention

3. **Documente estrutura**:
- Tree de compartments
- Políticas aplicadas
- Recursos críticos

4. **Crie report de compliance**: Liste todos os recursos com tags""",
    },
    "governance/resource-discovery": {
        "scan": """Execute resource discovery:

```bash
# Listar todos os recursos por compartment
for comp in $(oci iam compartment list --compartment-id <tenancy-ocid> --query 'data[].id' | jq -r '.[]'); do
  echo "=== Compartment: $comp ==="
  oci compute instance list --compartment-id $comp
  oci db autonomous-database list --compartment-id $comp
  oci os bucket list --compartment-id $comp
done
```

Use para inventário e otimização de custos.""",
    },
    "finops/cost-optimization": {
        "analyze": """Analise custos OCI:

1. **Acesse Cost Analyzer**:
```bash
oci usage-api resource-aggregation get-usage --tenant-id <tenancy-ocid> --time-start <start> --time-end <end>
```

2. **Identifique padrões**:
- Recursos órfãos
- Shapes superdimensionados
- Unused block volumes

3. **Recomendações**:
- Delete recursos órfãos
- Rightsizing de instâncias
- Reserved Capacity para steady-state

4. **Configure budgets**:
```bash
oci budgets budget create --compartment-id <tenancy-ocid> --display-name "monthly-budget" --amount 10000
```""",
    },
    "finops/showback-chargeback": {
        "configure": """Configure showback/chargeback:

1. **Tagging por department**:
```bash
oci iam tag-definition create --tag-namespace-id <ns-ocid> --name "cost-center"
```

2. **Aplique tags** em todos os recursos

3. **Gere relatórios** por cost-center:
```bash
oci usage-api resource-aggregation get-usage --query "resources[?defined-tags.cost-center]"
```

4. **Configure budgets** por department""",
    },
    "finops/rightsizing": {
        "analyze": """Analise rightsizing:

1. **Collect métricas** de 30 dias:
```bash
oci monitoring metric-data get --metric-name CpuUtilization --namespace oci_compute --resource-id <instance-ocid>
```

2. **Identifique instância subutilizada**:
- CPU < 20% por mais de 30 dias
- Memory < 50% consistentemente

3. **Recomendações**:
- Downscale shape (E4.Flex 2 OCPU → 1 OCPU)
- Use burstable shapes para dev/test
- Spot instances para batch workloads

4. **Documente savings** estimate""",
    },
    "finops/storage-tiering": {
        "configure": """Configure storage tiering:

1. **Crie lifecycle policy**:
```bash
oci os object lifecycle-policy create --bucket-name <bucket> --items '[{"action": "ARCHIVE", "target": "object prefix", "days": 90}]'
```

2. **Configure tiering**:
- Standard: dados quentes
- Infrequent Access: dados frios (< 30 dias)
- Archive: dados velhos (> 90 dias)

3. **Monitore custos**:
- Compare custos antes/depois
- Documente economia""",
    },
    "platform/backup-governance": {
        "configure": """Configure backup policies:

1. **Block Volume Backup**:
```bash
oci bv volume-backup-policy create --compartment-id <compartment-ocid> --display-name "daily-backup"
```

2. **Database Backup**:
```bash
oci db autonomous-database update --autonomous-database-id <adb-ocid> --backup-preservation-days 30
```

3. **Object Storage**: versioning enabled

4. **Teste restore** periodicamente""",
    },
    "platform/sre-operations": {
        "configure": """Configure SRE practices:

1. **Monitoring**: Crie alarmes para SLIs:
```bash
oci monitoring alarm create --compartment-id <compartment-ocid> --display-name "high-cpu" --metric-name CpuUtilization --severity CRITICAL
```

2. **Logging**: Centralize logs:
```bash
oci logging log-group create --compartment-id <compartment-ocid> --display-name "central-logs"
```

3. **Incident response**: Crie runbooks para cenários comuns

4. **Post-mortems**: Documente incidentes e lições aprendidas""",
    },
}

# =====================
# RESPONSE TEMPLATES
# =====================

SYSTEM_PROMPTS = {
    "compute/instances": "Você é especialista em OCI Compute instances. Forneça orientação técnica sobre criação, shapes, acesso SSH e gestão de lifecycle.",
    "compute/scaling": "Você é especialista em OCI Compute scaling. Forneça orientação sobre instance pools, auto-scaling e planejamento de capacidade.",
    "compute/custom-images": "Você é especialista em OCI custom images. Forneça orientação sobre criação de imagens customizadas, boot volumes e templates.",
    "storage/block": "Você é especialista em OCI Block Storage. Forneça orientação sobre criação de volumes, attachment, performance tiers e backup.",
    "storage/object": "Você é especialista em OCI Object Storage. Forneça orientação sobre buckets, pre-authenticated requests e lifecycle policies.",
    "storage/file": "Você é especialista em OCI File Storage. Forneça orientação sobre NFS, mount targets e export options.",
    "networking/vcn": "Você é especialista em OCI VCN. Forneça orientação sobre design de VCN, CIDR blocks, subnets e gateways.",
    "networking/security": "Você é especialista em OCI network security. Forneça orientação sobre Security Lists e NSGs.",
    "networking/connectivity": "Você é especialista em OCI connectivity. Forneça orientação sobre DRG, VPN IPSec, FastConnect e VCN peering.",
    "lb/load-balancer": " Você é especialista em OCI Load Balancing. Forneça orientação sobre criação de load balancers, backend sets e health checks.",
    "database/autonomous": "Você é especialista em OCI Autonomous Database. Forneça orientação sobre ATP, ADW, wallet management e connection strings.",
    "database/mysql": "Você é especialista em OCI MySQL HeatWave. Forneça orientação sobre configuração, scaling e replicação.",
    "database/postgresql": "Você é especialista em OCI PostgreSQL. Forneça orientação sobre gestão de instâncias e HA.",
    "database/nosql": "Você é especialista em OCI NoSQL. Forneça orientação sobre criação de tabelas e operações CRUD.",
    "database/autonomous-json": "Você é especialista em OCI Autonomous JSON Database. Forneça orientação sobre document store e JSON collections.",
    "database/exadata": "Você é especialista em OCI Exadata. Forneça orientação sobre Exadata Cloud Service.",
    "database/exadata-cloud": "Você é especialista em OCI Exadata Cloud at Customer.",
    "container/oke": "Você é especialista em OCI OKE. Forneça orientação sobre criação de clusters, node pools e deployments.",
    "container/instances": "Você é especialista em OCI Container Instances. Forneça orientação sobre containers serverless.",
    "serverless/functions": "Você é especialista em OCI Functions. Forneça orientação sobre desenvolvimento de functions e triggers.",
    "serverless/api-gateway": "Você é especialista em OCI API Gateway. Forneça orientação sobre APIs e autenticação.",
    "security/iam-basics": "Você é especialista em OCI IAM. Forneça orientação sobre users, groups e authentication.",
    "security/policies": "Você é especialista em OCI policies. Forneça orientação sobre criação de políticas IAM.",
    "security/dynamic-groups": "Você é especialista em OCI dynamic groups. Forneça orientação sobre dynamic groups e matching rules.",
    "security/federation": "Você é especialista em OCI federation. Forneça orientação sobre IDP e SAML.",
    "security/vault-secrets": "Você é especialista em OCI Vault Secrets. Forneça orientação sobre gestão de secrets.",
    "security/vault-keys": "Você é especialista em OCI Vault Keys. Forneça orientação sobre gestão de chaves de criptografia.",
    "security/encryption": "Você é especialista em OCI encryption. Forneça orientação sobre encryption at rest e in transit.",
    "security/cloud-guard": "Você é especialista em OCI Cloud Guard. Forneça orientação sobre security posture.",
    "security/waf": "Você é especialista em OCI WAF. Forneça orientação sobre web application firewall.",
    "security/zero-trust": "Você é especialista em OCI zero-trust. Forneça orientação sobre implementação de zero-trust architecture.",
    "security/posture-management": "Você é especialista em OCI Posture Management. Forneça orientação sobre compliance e controls.",
    "devops/ci-cd": "Você é especialista em OCI DevOps. Forneça orientação sobre CI/CD pipelines e deployments.",
    "devops/resource-manager": "Você é especialista em OCI Resource Manager. Forneça orientação sobre Terraform stacks e jobs.",
    "devops/artifacts": "Você é especialista em OCI Artifacts. Forneça orientação sobre container registries e packages.",
    "devops/secrets": "Você é especialista em OCI Vault para DevOps. Forneça orientação sobre gestão de secrets em pipelines.",
    "migration/aws-compute": "Você é especialista em migração AWS para OCI. Forneça orientação sobre migração de EC2 para Compute.",
    "migration/aws-storage": "Você é especialista em migração AWS para OCI. Forneça orientação sobre migração de EBS para Block Storage.",
    "migration/aws-database": "Você é especialista em migração AWS para OCI. Forneça orientação sobre migração de RDS para Autonomous.",
    "migration/azure-compute": "Você é especialista em migração Azure para OCI. Forneça orientação sobre migração de Azure VMs.",
    "migration/azure-storage": "Você é especialista em migração Azure para OCI. Forneça orientação sobre migração de Blob Storage.",
    "migration/azure-database": "Você é especialista em migração Azure para OCI. Forneça orientação sobre migração de Azure SQL.",
    "migration/gcp-compute": "Você é especialista em migração GCP para OCI. Forneça orientação sobre migração de GCE.",
    "migration/gcp-storage": "Você é especialista em migração GCP para OCI. Forneça orientação sobre migração de GCS.",
    "migration/gcp-database": "Você é especialista em migração GCP para OCI. Forneça orientação sobre migração de Cloud SQL.",
    "migration/onprem-compute": "Você é especialista em migração On-Premises para OCI. Forneça orientação sobre migração de VMs.",
    "migration/onprem-storage": "Você é especialista em migração On-Premises para OCI. Forneça orientação sobre migração de storage.",
    "migration/onprem-vmware": "Você é especialista em migração VMware para OCI. Forneça orientação sobre VMware to OCI.",
    "migration/onprem-database": "Você é especialista em migração On-Premises para OCI. Forneça orientação sobre migração de databases.",
    "migration/data-transfer": "Você é especialista em data transfer para OCI. Forneça orientação sobre Snowball e importação.",
    "terraform/provider": "Você é especialista em Terraform para OCI. Forneça orientação sobre configuração do provider.",
    "terraform/compute": "Você é especialista em Terraform para OCI. Forneça orientação sobre recursos de Compute.",
    "terraform/storage": "Você é especialista em Terraform para OCI. Forneça orientação sobre recursos de Storage.",
    "terraform/networking": "Você é especialista em Terraform para OCI. Forneça orientação sobre recursos de Networking.",
    "terraform/load-balancer": "Você é especialista em Terraform para OCI. Forneça orientação sobre Load Balancer.",
    "terraform/database": "Você é especialista em Terraform para OCI. Forneça orientação sobre recursos de Database.",
    "terraform/container": "Você é especialista em Terraform para OCI. Forneça orientação sobre OKE e containers.",
    "terraform/serverless": "Você é especialista em Terraform para OCI. Forneça orientação sobre Functions.",
    "terraform/security": "Você é especialista em Terraform para OCI. Forneça orientação sobre recursos de security.",
    "terraform/observability": "Você é especialista em Terraform para OCI. Forneça orientação sobre logging e monitoring.",
    "terraform/devops": "Você é especialista em Terraform para OCI. Forneça orientação sobre DevOps resources.",
    "terraform/state": "Você é especialista em Terraform para OCI. Forneça orientação sobre remote state.",
    "observability/logging": "Você é especialista em OCI Logging. Forneça orientação sobre log groups e agentes.",
    "observability/monitoring": "Você é especialista em OCI Monitoring. Forneça orientação sobre alarms e métricas.",
    "observability/stack-monitoring": "Você é especialista em OCI Stack Monitoring. Forneça orientação sobre resource monitoring.",
    "observability/apm": "Você é especialista em OCI APM. Forneça orientação sobre application performance.",
    "troubleshooting/connectivity": "Você é especialista em troubleshooting OCI. Forneça orientação sobre problemas de conectividade.",
    "troubleshooting/performance": "Você é especialista em troubleshooting OCI. Forneça orientação sobre problemas de performance.",
    "troubleshooting/authentication": "Você é especialista em troubleshooting OCI. Forneça orientação sobre problemas de auth.",
    "troubleshooting/database": "Você é especialista em troubleshooting OCI. Forneça orientação sobre problemas de database.",
    "troubleshooting/compute": "Você é especialista em troubleshooting OCI. Forneça orientação sobre problemas de compute.",
    "troubleshooting/storage": "Você é especialista em troubleshooting OCI. Forneça orientação sobre problemas de storage.",
    "troubleshooting/oke": "Você é especialista em troubleshooting OCI. Forneça orientação sobre problemas de OKE.",
    "troubleshooting/functions": "Você é especialista em troubleshooting OCI. Forneça orientação sobre problemas de Functions.",
    "governance/landing-zone": "Você é especialista em OCI Landing Zone. Forneça orientação sobre design e implementação.",
    "governance/compartments": "Você é especialista em OCI compartments. Forneça orientação sobre hierarquia de compartments.",
    "governance/tagging": "Você é especialista em OCI Tagging. Forneça orientação sobre tag namespaces e definitions.",
    "governance/budgets-cost": "Você é especialista em OCI Budgets. Forneça orientação sobre controle de custos.",
    "governance/policies-guardrails": "Você é especialista em OCI Guardrails. Forneça orientação sobre policies e compliance.",
    "governance/compliance": "Você é especialista em OCI Compliance. Forneça orientação sobre auditoria e controls.",
    "governance/audit-readiness": "Você é especialista em OCI Audit Readiness. Forneça orientação sobre preparação para auditoria.",
    "governance/resource-discovery": "Você é especialista em OCI Resource Discovery. Forneça orientação sobre inventário de recursos.",
    "finops/cost-optimization": "Você é especialista em OCI FinOps. Forneça orientação sobre otimização de custos.",
    "finops/showback-chargeback": "Você é especialista em OCI FinOps. Forneça orientação sobre showback e chargeback.",
    "finops/rightsizing": "Você é especialista em OCI FinOps. Forneça orientação sobre rightsizing de recursos.",
    "finops/storage-tiering": "Você é especialista em OCI FinOps. Forneça orientação sobre storage tiering.",
    "platform/backup-governance": "Você é especialista em OCI Backup. Forneça orientação sobre políticas de backup.",
    "platform/sre-operations": "Você é especialista em OCI SRE. Forneça orientação sobre práticas de SRE.",
}


def generate_response(
    category, intent, idx, company, project, region, compartment, constraint, lifecycle
):
    """Generate detailed response with CLI and phases."""
    subcat = category.split("/")[-1]
    cli_template = CLI_COMMANDS.get(category, {}).get(intent, "")

    # Replace placeholders with realistic values
    params = {
        "ad": random.choice(["AD-1", "AD-2", "AD-3"]),
        "shape": random.choice(SHAPES),
        "ocpus": random.choice([2, 4, 8]),
        "memory": random.choice([16, 32, 64]),
        "subnet_id": "ocid1.subnet.oc1.sa-saopaulo-1.xxx",
        "compartment_id": f"ocid1.compartment.oc1..{compartment}",
        "name": f"{subcat}-{project[:5]}-{idx % 100}",
        "instance_id": "ocid1.instance.oc1.sa-saopaulo-1.xxx",
        "rule": "any instance.id != ''",
        "vcn_id": "ocid1.vcn.oc1.sa-saopaulo-1.xxx",
        "cidr": "10.0.0.0/16",
        "bucket_name": f"{project}-bucket",
        "namespace": "namespace-str",
        "storage": random.choice([1, 2, 4]),
        "cores": random.choice([2, 4, 8]),
        "workload": "AUTONOMOUS_TRANSACTION_PROCESSING",
        "k8s_version": "v1.28.2",
        "cluster_id": "ocid1.cluster.oc1.sa-saopaulo-1.xxx",
        "vault_id": "ocid1.vault.oc1.sa-saopaulo-1.xxx",
        "policy_name": f"{project}-policy",
        "statement": f"Allow group {project}-admins to manage all-resources in compartment {compartment}",
        "tenancy_id": "ocid1.tenancy.oc1..xxx",
        "amount": random.choice([1000, 5000, 10000]),
        "tf_version": "1.0.x",
        "app_id": "ocid1.application.oc1.sa-saopaulo-1.xxx",
        "image": "container-image-registry",
        "metric": "CpuUtilization",
        "domain": f"{project}.example.com",
        "table_name": f"{project}_data",
        "version": "8.0",
        "type": "iscsi",
        "size": random.choice([2, 4, 8]),
        "instance_pool_id": "ocid1.instancepool.oc1.sa-saopaulo-1.xxx",
        "infra_id": "ocid1.exadatainfrastructure.oc1.sa-saopaulo-1.xxx",
        "namespace_id": "ocid1.tagnamespace.oc1.sa-saopaulo-1.xxx",
        "image_id": "ocid1.image.oc1.sa-saopaulo-1.xxx",
        "volume_id": "ocid1.volume.oc1.sa-saopaulo-1.xxx",
        "adb_id": "ocid1.autonomousdatabase.oc1.sa-saopaulo-1.xxx",
        "password": "SecurePass123!",
        "action": random.choice(["START", "STOP", "RESET"]),
        "username": f"user_{idx % 100}",
        "description": f"User for {project}",
        "rule": "any instance.id != ''",
        "content": "secret_content_base64",
        "namespace": "namespace-str",
        "vcn_name": f"vcn-{project[:5]}",
        "exadata_id": "ocid1.exadatainfrastructure.oc1.sa-saopaulo-1.xxx",
        "cluster_id": "ocid1.cluster.oc1.sa-saopaulo-1.xxx",
        "new_size": random.choice([1, 2, 3, 4, 5]),
        "config_id": "ocid1.instanceconfiguration.oc1.sa-saopaulo-1.xxx",
        "new_cidr": "10.0.1.0/16",
    }

    # Check if original template already has markdown code blocks (before formatting)
    original_has_code = cli_template and ("```" in cli_template)

    # Check if template has Python-style placeholders that we can format
    has_python_placeholders = False
    cli_command = cli_template  # default
    if cli_template:
        # Simple placeholders like {compartment_id}, {name}, not HCL {var.name}
        placeholders = re.findall(r"\{([a-z_][a-z_0-9]*)\}", cli_template)
        # Only format if all placeholders are in our params
        if placeholders and all(p in params for p in placeholders):
            has_python_placeholders = True
            try:
                cli_command = cli_template.format(**params)
            except KeyError:
                cli_command = cli_template  # fallback

    # If didn't format, use original
    if not has_python_placeholders:
        cli_command = (
            cli_template
            if cli_template
            else "Consulte a documentação OCI para esta operação."
        )

    # Wrap in bash code block ONLY if result doesn't already have any code blocks
    # (check both original and after formatting)
    result_has_code = cli_command and ("```" in cli_command)
    if cli_command and not result_has_code:
        cli_command = "```bash\n" + cli_command + "\n```"

    responses = {
        "create": f"""Vamos Provisionar {subcat} para {company}:

**Fase 1: Preparação**
- Acesse o serviço {category.split("/")[0].title()} no Console OCI
- Selecione o compartment `{compartment}` em `{region}`
- Verifique se você tem permissões IAM adequadas ( group {project}-admins )

**Fase 2: Configuração**
- Execute o comando OCI CLI:

{cli_command}

- Defina os parâmetros:
  - `display-name`: {project}-{subcat}-{idx % 100}
  - `compartment-id`: ocid1.compartment.oc1..{compartment}
  - Configure sesuai {constraint}

**Fase 3: Verificação**
- Aguarde o resource atingir estado AVAILABLE/RUNNING
- Use `oci {category.replace("/", " ").replace(" ", " ")} list --compartment-id <ocid>` para verificar
- Confirme que o resource está no compartment correto

**Fase 4: Pós-provisionamento**
- Configure tagging adequado (cost-center={project})
- Configure backup policy se aplicável
- Configure monitoring/alarms para {subcat}

**Dicas**:
- Para production, use shape com HA (BM.Standard.E5)
- Sempre defina lifecycle state no comando com --wait-for-state
- Use naming convention consistente: {{resource}}-{{project}}-{{env}}

**Referência**: https://docs.oracle.com/pt-br/iaas/Content/{category.split("/")[0].title()}/Home.htm""",
        "list": f"""Vamos Listar {subcat} para {company}:

**Fase 1: Identificação**
- Determine o compartment onde os recursos estão: `{compartment}`
- Identifique o lifecycle state desejado (RUNNING, AVAILABLE, etc)

**Fase 2: Execução**
- Execute o comando OCI CLI:

```bash
{cli_command}
```

- Parâmetros importantes:
  - `--compartment-id`: ocid1.compartment.oc1..{compartment}
  - `--lifecycle-state`: Filtrar por estado específico
  - Use `--limit` e `--page` para paginação

**Fase 3: Análise**
- Verifique a saída em JSON
- Identifique recursos órfãos ou não utilizados
- Documente recursos em spreadsheet para {project}

**Fase 4: Otimização**
- Identifique recursos que podem ser movidos para compartments mais econômicos
- Marque recursos órfãos para cleanup
- Configure alerts para novos recursos

**Dicas**:
- Use `jq` para filtrar saída: `| jq '.data[] | select(.lifecycle-state=="AVAILABLE")'`
- Configure audit para monitorar criação de recursos

**Referência**: https://docs.oracle.com/pt-br/iaas/Content/{category.split("/")[0].title()}/Home.htm""",
        "get": f"""Vamos Consultar {subcat} para {company}:

**Fase 1: Identificação do Resource**
- Obtenha o OCID do resource: ocid1.{subcat}.oc1.sa-saopaulo-1.xxx
- Confirma que o resource está no compartment `{compartment}`

**Fase 2: Consulta**
- Execute o comando OCI CLI:

```bash
{cli_command}
```

**Fase 3: Análise da Resposta**
- Verifique campos importantes:
  - `lifecycle-state`: Estado atual
  - `time-created`: Data de criação
  - `defined-tags`: Tags aplicadas
  - `freeform-tags`: Tags livres

**Fase 4: Ações**
- Documente o estado atual
- Identifique necessidade de updates
- Verifique compliance com políticas de {project}

**Dicas**:
- Use `--raw-output` para outputs específicos
- Salve saída em arquivo para auditoria: `> {subcat}_{idx}.json`

**Referência**: https://docs.oracle.com/pt-br/iaas/Content/{category.split("/")[0].title()}/Home.htm""",
        "update": f"""Vamos Atualizar {subcat} para {company} no projeto {project}:

**Contexto**: Ambiente {lifecycle} com constraint: {constraint}

**Fase 1: Planejamento**
- Identifique o resource: ocid1.{subcat}.oc1.sa-saopaulo-1.xxx
- Avalie impacto das alterações considerando {constraint}
- Programe manutenção durante {random.choice(["janela de manutenção", "horário de baixo uso", "período de rollout"])}

**Fase 2: Backup**
- Execute: `oci {category.replace("/", " ").split()[0]} get --id <ocid> > backup_{project}.json`
- Documente configuração atual
- Tenha plano de rollback

**Fase 3: Execução**
{cli_command if cli_command else f"```bash\noci {category.replace('/', ' ')} update --<resource-id> --display-name {name}\n```"}

**Fase 4: Validação**
- Execute: `oci {category.replace("/", " ").split()[0]} get --id <ocid>`
- Confirme que {lifecycle} está estável
- Atualize documentação de {project}

**Dicas**:
- Para {constraint}, use abordagem gradual (blue-green)
- Monitore custos pós-update em {project}
- Configure alertas para detectar regressões

**Referência**: https://docs.oracle.com/pt-br/iaas/Content/{category.split("/")[0].title()}/Home.htm""",
        "delete": f"""Vamos Remover {subcat} de {company}:

**Fase 1: Validação**
- Confirme que o resource pode ser removido
- Verifique dependências (outros recursos dependem?)
- Confirme que não há dados críticos

**Fase 2: Backup**
- Exporte dados se necessário
- Documente OCID para referência futura

**Fase 3: Remoção**
- Execute o comando OCI CLI:
```bash
oci {category.replace("/", " ")} delete --{subcat.replace("-", "-")}-id <ocid> --force
```

**Fase 4: Verificação**
- Confirme que resource foi removido
- Verifique custos associados
- Atualize documentação de {project}

**Dicas**:
- Use `--force` para evitar prompts
- Considere soft-delete (preserve por 30 dias)
- Sempre documente reason para delete

**Alerta**: Após delete, dados não podem ser recuperados!

**Referência**: https://docs.oracle.com/pt-br/iaas/Content/{category.split("/")[0].title()}/Home.htm""",
        "manage": f"""Vamos Gerenciar {subcat} para {company} no projeto {project}:

**Contexto**: Ambiente {lifecycle}, constraint: {constraint}

**Fase 1: Avaliação**
- Identifique o resource: ocid1.{subcat}.oc1.sa-saopaulo-1.xxx
- Determine ação necessária: {random.choice(["start/stop", "restart", "scale up/down", "resize", "backup", "restore"])}

**Fase 2: Planejamento**
- Programe janela de manutenção se necessário ({random.choice(["off-peak hours", "weekend", "maintenance window"])})
- Notifique stakeholders de {project}
- Tenha plano de rollback

**Fase 3: Execução**
{cli_command if cli_command else f"```bash\noci {category.replace('/', ' ')} action --<resource-id> --action {random.choice(['START', 'STOP', 'RESET', 'START', 'STOP'])}\n```"}

**Fase 4: Monitoramento**
- Monitore health do resource
- Verifique métricas post-action: `oci monitoring metric-data get --metric-name CpuUtilization --resource-id <ocid>`
- Documente ação tomada no runbook de {project}

**Dicas**:
- Para scale em {lifecycle}, considere auto-scaling policies
- Para stop/start, planeje custos de idle resources
- {random.choice(["Documente no Runbook", "Atualize dashboard", "Configure alertas"])}

**Referência**: https://docs.oracle.com/pt-br/iaas/Content/{category.split("/")[0].title()}/Home.htm""",
        "diagnose": f"""Vamos Diagnosticar {subcat} para {company} no projeto {project}:

**Contexto**: Ambiente {lifecycle}, constraint: {constraint}

**Fase 1: Coleta de Informações**
- Identifique o resource com problema: ocid1.{subcat}.oc1.sa-saopaulo-1.xxx
- Colete logs: `oci logging log list --source-id <resource-ocid>`
- Verifique métricas em Monitoring: `oci monitoring metric-data get --resource-id <ocid>`

{cli_command}

**Fase 2: Análise**
- Analise erros nos logs
- Compare com baseline de {project}
- Identifique root cause

**Fase 3: Remediation**
- Aplique correção necessária
- Teste a correção

**Fase 4: Prevenção**
- Configure alertas para detecção precoce em {project}
- Documente o problema e solução
- Atualise runbook de {project}

**Dicas**:
- Use Diagnostic Service se disponível
- Colete timestamps e screenshots de erros
- Para {constraint}, priorize correção rápida

**Referência**: https://docs.oracle.com/pt-br/iaas/Content/{category.split("/")[0].title()}/Home.htm""",
        "describe": f"""Vamos Planejar Migração de {subcat} para {company} no projeto {project}:

**Contexto**: Ambiente {lifecycle}, constraint: {constraint}

**Fase 1: Assessment**
- Inventory de recursos atuais em {project}
- Identifique dependências e relações
- Avalie complexidade e riscos para {constraint}

**Fase 2: Planejamento**
- Selecione estratégia de migração: {random.choice(["lift-and-shift", "re-platform", "re-architecture", "hybrid"])}
- Planeje timeline considerando {lifecycle}
- Identifique ferramentas necessárias

{cli_command}

**Fase 3: Execução**
- Execute migração em fases
- Valide cada etapa
- Mantenha sincronização durante cutover

**Fase 4: Validação**
- Teste funcionalidade pós-migração
- Verifique performance
- Configure monitoring para {project}

**Dicas**:
- Use OCI Migration Service quando disponível
- Preserve dados por 30 dias pós-migração
- Documente decisões em {project}

**Referência**: https://docs.oracle.com/pt-br/iaas/Content/Migration/overview.htm""",
        "analyze": f"""Vamos Analisar {subcat} para {company} no projeto {project}:

**Contexto**: Ambiente {lifecycle}, constraint: {constraint}

**Fase 1: Coleta de Dados**
- Acesse Cost Analyzer em {region}
- Selecione compartment `{compartment}`
- Configure período de análise (últimos 30 dias)

{cli_command}

**Fase 2: Identificação**
- Identifique padrões de uso em {project}
- Compare com budget de {project}: {random.choice(["R$1.000", "R$5.000", "R$10.000"])}
- Identifique oportunidades de otimização para {constraint}

**Fase 3: Recomendações**
- Proponha actions específicas
- Estime economias
- Priorize por impacto para {lifecycle}

**Fase 4: Implementação**
- Implemente otimizações
- Configure budgets/alerts para {project}
- Documente savings realizados

**Dicas**:
- Use Cost Estimation antes de criar recursos
- Configure budget alerts em 80% e 100%
- Revise mensalmente para {project}

**Referência**: https://docs.oracle.com/pt-br/iaas/Content/Cost/Overview.htm""",
    }

    return responses.get(intent, responses["create"])


def generate_question(
    category,
    idx,
    company,
    project,
    region,
    compartment,
    persona,
    intent,
    constraint,
    lifecycle,
):
    """Generate question based on parameters."""
    subcat = category.split("/")[-1]

    templates = [
        f"Sou {persona} na {company} e preciso {intent} {subcat} para o projeto {project}, em {compartment}/{region}. Qual abordagem você recomenda?",
        f"Como {persona} devo {intent} {subcat} usando OCI no ambiente {region} para o projeto {project}?",
        f"Sou responsável pelo {project} e preciso de ajuda para {intent} {subcat} considerando {constraint}. Pode ajudar?",
        f"Temos um ambiente {lifecycle} em {region} e preciso {intent} {subcat} para {company}. Quais são os passos?",
        f"Preciso {intent} {subcat} no compartment {compartment} para {project}. OCI CLI ou Terraform?",
        f"Como {persona}, qual a melhor prática para {intent} {subcat} considerando {constraint} no projeto {project}?",
    ]

    return templates[idx % len(templates)]


def generate_example(category, idx):
    """Generate one training example."""
    company = random.choice(COMPANIES)
    project = random.choice(PROJECTS)
    region = random.choice(REGIONS)
    compartment = random.choice(COMPARTMENTS)
    persona = random.choice(PERSONAS)
    constraint = random.choice(CONSTRAINTS)
    lifecycle = random.choice(LIFECYCLE_STAGES)

    intents = ["create", "list", "get", "update", "delete", "manage"]
    intent = intents[idx % len(intents)]

    # Special handling for migration/troubleshooting
    if "migration" in category:
        intent = "describe"
    elif "troubleshooting" in category:
        intent = "diagnose"
    elif "finops" in category:
        intent = "analyze"

    question = generate_question(
        category,
        idx,
        company,
        project,
        region,
        compartment,
        persona,
        intent,
        constraint,
        lifecycle,
    )
    answer = generate_response(
        category,
        intent,
        idx,
        company,
        project,
        region,
        compartment,
        constraint,
        lifecycle,
    )

    return {
        "messages": [
            {
                "role": "system",
                "content": SYSTEM_PROMPTS.get(
                    category, f"Você é especialista em OCI {category}."
                ),
            },
            {"role": "user", "content": question},
            {"role": "assistant", "content": answer},
        ],
        "metadata": {
            "category": category,
            "difficulty": "intermediate",
            "company": company,
            "project": project,
            "region": region,
            "compartment": compartment,
            "persona": persona,
            "intent": intent,
            "constraint": constraint,
            "lifecycle": lifecycle,
            "source": "generate_v5_combined",
        },
    }


def main():
    """Generate all training examples."""
    output_dir = Path("data/curated")
    output_dir.mkdir(parents=True, exist_ok=True)

    total = 0
    for category in CATEGORIES:
        examples = []
        for i in range(EXAMPLES_PER_CATEGORY):
            ex = generate_example(category, i)
            examples.append(ex)

        safe_name = category.replace("/", "-")
        output_file = output_dir / f"{safe_name}.jsonl"

        with open(output_file, "w", encoding="utf-8") as f:
            for ex in examples:
                f.write(json.dumps(ex, ensure_ascii=False) + "\n")

        print(f"✅ {category}: {len(examples)}")
        total += len(examples)

    print(f"\n🎯 Total: {total} examples em {len(CATEGORIES)} categorias")
    print(f"📁 Output: {output_dir}")


if __name__ == "__main__":
    main()
