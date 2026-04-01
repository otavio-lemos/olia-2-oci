#!/usr/bin/env python3
"""Generate 10k OCI training examples following exact patterns from existing 495 examples."""

import json
import random
import hashlib
from pathlib import Path

random.seed(42)

SYSTEM_PROMPTS = {
    "compute/instances": "You are an OCI specialist with expertise in Compute instances. Provide technical guidance on instance creation, shape selection, SSH access, and lifecycle management.",
    "compute/scaling": "You are an OCI specialist with expertise in Compute scaling. Provide technical guidance on instance pools, auto-scaling, and capacity planning.",
    "compute/custom-images": "You are an OCI specialist with expertise in Compute custom images. Provide technical guidance on custom image creation, boot volumes, and instance templates.",
    "storage/block": "You are an OCI specialist with expertise in Block Storage. Provide technical guidance on block volume creation, attachment, performance tiers, and backup strategies.",
    "storage/object": "You are an OCI specialist with expertise in Object Storage. Provide technical guidance on buckets, pre-authenticated requests, lifecycle policies, and versioning.",
    "storage/file": "You are an OCI specialist with expertise in File Storage. Provide technical guidance on NFS, mount targets, export options, and backup strategies.",
    "networking/vcn": "You are an OCI specialist with expertise in Virtual Cloud Networks. Provide technical guidance on VCN design, CIDR blocks, subnets, and gateways.",
    "networking/security": "You are an OCI specialist with expertise in network security. Provide technical guidance on Security Lists, Network Security Groups, and ingress/egress rules.",
    "networking/connectivity": "You are an OCI specialist with expertise in network connectivity. Provide technical guidance on DRG, VPN IPSec, FastConnect, and VCN peering.",
    "lb/load-balancer": "You are an OCI specialist with expertise in Load Balancing. Provide technical guidance on load balancer creation, backend sets, listeners, and health checks.",
    "database/autonomous": "You are an OCI specialist with expertise in Autonomous Database. Provide technical guidance on ATP, ADW, wallet management, and connection strings.",
    "database/mysql": "You are an OCI specialist with expertise in MySQL HeatWave. Provide technical guidance on MySQL configuration, scaling, and replication.",
    "database/postgresql": "You are an OCI specialist with expertise in OCI PostgreSQL. Provide technical guidance on instance management, scaling, and high availability.",
    "database/nosql": "You are an OCI specialist with expertise in Oracle NoSQL Database. Provide technical guidance on table creation, CRUD operations, and TTL.",
    "database/autonomous-json": "You are an OCI specialist with expertise in Autonomous JSON Database. Provide technical guidance on document store, MongoDB compatibility, and JSON collections.",
    "database/exadata": "You are an OCI specialist with expertise in Exadata Cloud Service. Provide technical guidance on infrastructure, DB systems, and patching.",
    "container/oke": "You are an OCI specialist with expertise in OKE. Provide technical guidance on cluster creation, node pools, and Kubernetes deployments.",
    "container/instances": "You are an OCI specialist with expertise in OCI Container Instances. Provide technical guidance on container deployment, OCIR, and image management.",
    "serverless/functions": "You are an OCI specialist with expertise in OCI Functions. Provide technical guidance on function deployment, invocation, and monitoring.",
    "serverless/api-gateway": "You are an OCI specialist with expertise in API Gateway. Provide technical guidance on routes, integrations, authentication, and throttling.",
    "security/iam-basics": "You are an OCI security specialist with expertise in IAM. Provide technical guidance on compartments, users, groups, and authentication.",
    "security/policies": "You are an OCI security specialist with expertise in IAM policies. Provide technical guidance on policy syntax, resource vs tenancy-level policies.",
    "security/dynamic-groups": "You are an OCI security specialist with expertise in Dynamic Groups. Provide technical guidance on dynamic group rules and instance principal.",
    "security/federation": "You are an OCI security specialist with expertise in federation. Provide technical guidance on IdCS, Okta, SAML, and OAuth.",
    "security/vault-secrets": "You are an OCI security specialist with expertise in Vault secrets. Provide technical guidance on secret creation, retrieval, and rotation.",
    "security/vault-keys": "You are an OCI security specialist with expertise in Vault keys. Provide technical guidance on key management, encryption, and key policies.",
    "security/encryption": "You are an OCI security specialist with expertise in encryption. Provide technical guidance on volume encryption, BYOK, and HSM integration.",
    "security/cloud-guard": "You are an OCI security specialist with expertise in Cloud Guard. Provide technical guidance on detector recipes and responder rules.",
    "security/waf": "You are an OCI security specialist with expertise in WAF. Provide technical guidance on Web Application Firewall, access rules, and rate limiting.",
    "migration/aws-compute": "You are an OCI specialist with expertise in AWS to OCI migration. Provide technical guidance on EC2 to Compute migration and shape mapping.",
    "migration/aws-storage": "You are an OCI specialist with expertise in AWS to OCI migration. Provide technical guidance on S3 to Object Storage migration.",
    "migration/aws-database": "You are an OCI specialist with expertise in AWS to OCI migration. Provide technical guidance on RDS to OCI Database migration.",
    "migration/azure-compute": "You are an OCI specialist with expertise in Azure to OCI migration. Provide technical guidance on Azure VMs to OCI Compute migration.",
    "migration/azure-storage": "You are an OCI specialist with expertise in Azure to OCI migration. Provide technical guidance on Azure Blob to Object Storage migration.",
    "migration/azure-database": "You are an OCI specialist with expertise in Azure to OCI migration. Provide technical guidance on Azure SQL to Autonomous Database migration.",
    "migration/gcp-compute": "You are an OCI specialist with expertise in GCP to OCI migration. Provide technical guidance on GCP Compute Engine to OCI Compute migration.",
    "migration/gcp-storage": "You are an OCI specialist with expertise in GCP to OCI migration. Provide technical guidance on GCP Cloud Storage to Object Storage migration.",
    "migration/gcp-database": "You are an OCI specialist with expertise in GCP to OCI migration. Provide technical guidance on GCP Cloud SQL to OCI Database migration.",
    "migration/onprem-compute": "You are an OCI specialist with expertise in on-premises to OCI migration. Provide technical guidance on lift-and-shift and cutover planning.",
    "migration/onprem-storage": "You are an OCI specialist with expertise in on-premises to OCI migration. Provide technical guidance on file storage and data transfer.",
    "migration/onprem-vmware": "You are an OCI specialist with expertise in VMware to OCI migration. Provide technical guidance on VMware Cloud Foundation and hybrid connectivity.",
    "migration/onprem-database": "You are an OCI specialist with expertise in on-premises to OCI migration. Provide technical guidance on Oracle to Autonomous Database migration.",
    "migration/data-transfer": "You are an OCI specialist with expertise in data transfer. Provide technical guidance on GoldenGate, Data Integration, and large-scale transfers.",
    "terraform/provider": "You are an OCI Terraform specialist. Provide technical guidance on provider configuration, authentication, and region setup.",
    "terraform/compute": "You are an OCI Terraform specialist. Provide technical guidance on Terraform resources for Compute, instance pools, and auto-scaling.",
    "terraform/storage": "You are an OCI Terraform specialist. Provide technical guidance on Terraform resources for Block Volume, Object Storage, and File Storage.",
    "terraform/networking": "You are an OCI Terraform specialist. Provide technical guidance on Terraform resources for VCN, subnets, and security configurations.",
    "terraform/load-balancer": "You are an OCI Terraform specialist. Provide technical guidance on Terraform resources for Load Balancer, backend sets, and listeners.",
    "terraform/database": "You are an OCI Terraform specialist. Provide technical guidance on Terraform resources for Autonomous Database, MySQL, and PostgreSQL.",
    "terraform/container": "You are an OCI Terraform specialist. Provide technical guidance on Terraform resources for OKE, node pools, and container instances.",
    "terraform/serverless": "You are an OCI Terraform specialist. Provide technical guidance on Terraform resources for Functions and API Gateway.",
    "terraform/security": "You are an OCI Terraform specialist. Provide technical guidance on Terraform resources for Vault, secrets, keys, and Cloud Guard.",
    "terraform/observability": "You are an OCI Terraform specialist. Provide technical guidance on Terraform resources for Logging, Monitoring, and Alarms.",
    "terraform/devops": "You are an OCI Terraform specialist. Provide technical guidance on Terraform resources for DevOps, artifacts, and Resource Manager.",
    "terraform/state": "You are an OCI Terraform specialist. Provide technical guidance on Terraform remote state, state locking, and workspaces.",
    "observability/logging": "You are an OCI specialist with expertise in Logging. Provide technical guidance on log groups, custom logs, and audit logs.",
    "observability/monitoring": "You are an OCI specialist with expertise in Monitoring. Provide technical guidance on metrics, alarms, and notifications.",
    "observability/stack-monitoring": "You are an OCI specialist with expertise in Stack Monitoring. Provide technical guidance on resource monitoring and database monitoring.",
    "observability/apm": "You are an OCI specialist with expertise in APM. Provide technical guidance on distributed tracing and performance diagnostics.",
    "troubleshooting/connectivity": "You are an OCI troubleshooting specialist with expertise in connectivity. Provide diagnostic guidance on routing, DNS, and VPN issues.",
    "troubleshooting/performance": "You are an OCI troubleshooting specialist with expertise in performance. Provide diagnostic guidance on CPU, memory, storage, and network performance.",
    "troubleshooting/authentication": "You are an OCI troubleshooting specialist with expertise in authentication. Provide diagnostic guidance on policy permissions and federation.",
    "troubleshooting/database": "You are an OCI troubleshooting specialist with expertise in database. Provide diagnostic guidance on connection issues and TNS errors.",
    "troubleshooting/compute": "You are an OCI troubleshooting specialist with expertise in Compute. Provide diagnostic guidance on provisioning, boot volume, and SSH issues.",
    "troubleshooting/storage": "You are an OCI troubleshooting specialist with expertise in storage. Provide diagnostic guidance on bucket access and performance issues.",
    "troubleshooting/oke": "You are an OCI troubleshooting specialist with expertise in OKE. Provide diagnostic guidance on cluster, node pool, and worker node issues.",
    "troubleshooting/functions": "You are an OCI troubleshooting specialist with expertise in Functions. Provide diagnostic guidance on function invocation and API Gateway errors.",
    "devops/ci-cd": "You are an OCI DevOps specialist. Provide technical guidance on build pipelines, deploy pipelines, and CI/CD automation.",
    "devops/resource-manager": "You are an OCI DevOps specialist. Provide technical guidance on Resource Manager stacks, jobs, and drift detection.",
    "devops/artifacts": "You are an OCI DevOps specialist. Provide technical guidance on OCIR, artifacts service, and image management.",
    "devops/secrets": "You are an OCI DevOps specialist. Provide technical guidance on Vault secrets, pipeline secret injection, and rotation.",
}

DOC_LINKS = {
    "compute/instances": "https://docs.oracle.com/en-us/iaas/Content/Compute/Concepts/computeoverview.htm",
    "compute/scaling": "https://docs.oracle.com/en-us/iaas/Content/Compute/Concepts/computeoverview.htm",
    "compute/custom-images": "https://docs.oracle.com/en-us/iaas/Content/Compute/Tasks/managingcustomimages.htm",
    "storage/block": "https://docs.oracle.com/en-us/iaas/Content/Block/Concepts/blockvolumeperformance.htm",
    "storage/object": "https://docs.oracle.com/en-us/iaas/Content/Object/Concepts/objectstorageoverview.htm",
    "storage/file": "https://docs.oracle.com/en-us/iaas/Content/File/Concepts/filestorageoverview.htm",
    "networking/vcn": "https://docs.oracle.com/en-us/iaas/Content/Network/Concepts/overview.htm",
    "networking/security": "https://docs.oracle.com/en-us/iaas/Content/Network/Concepts/overview.htm",
    "networking/connectivity": "https://docs.oracle.com/en-us/iaas/Content/Network/Concepts/overview.htm",
    "lb/load-balancer": "https://docs.oracle.com/en-us/iaas/Content/LoadBalancing/Concepts/loadbalanceroverview.htm",
    "database/autonomous": "https://docs.oracle.com/en-us/iaas/Content/Database/Concepts/databaseoverview.htm",
    "database/mysql": "https://docs.oracle.com/en-us/iaas/Content/MySQL/Concepts/overview.htm",
    "database/postgresql": "https://docs.oracle.com/en-us/iaas/Content/Database/Concepts/databaseoverview.htm",
    "database/nosql": "https://docs.oracle.com/en-us/iaas/Content/nosql/-nosql.htm",
    "database/autonomous-json": "https://docs.oracle.com/en-us/iaas/Content/Database/Concepts/databaseoverview.htm",
    "database/exadata": "https://docs.oracle.com/en-us/iaas/Content/Database/Concepts/databaseoverview.htm",
    "container/oke": "https://docs.oracle.com/en-us/iaas/Content/ContEng/Concepts/contengoverview.htm",
    "container/instances": "https://docs.oracle.com/en-us/iaas/Content/ContEng/Concepts/contengoverview.htm",
    "serverless/functions": "https://docs.oracle.com/en-us/iaas/Content/Functions/Con/functionsoverview.htm",
    "serverless/api-gateway": "https://docs.oracle.com/en-us/iaas/Content/ApiGateway/Concepts/apigatewayoverview.htm",
    "security/iam-basics": "https://docs.oracle.com/en-us/iaas/Content/Identity/Concepts/overview.htm",
    "security/policies": "https://docs.oracle.com/en-us/iaas/Content/Identity/Concepts/overview.htm",
    "security/dynamic-groups": "https://docs.oracle.com/en-us/iaas/Content/Identity/Concepts/overview.htm",
    "security/federation": "https://docs.oracle.com/en-us/iaas/Content/Identity/Concepts/overview.htm",
    "security/vault-secrets": "https://docs.oracle.com/en-us/iaas/Content/KeyManagement/Concepts/keyoverview.htm",
    "security/vault-keys": "https://docs.oracle.com/en-us/iaas/Content/KeyManagement/Concepts/keyoverview.htm",
    "security/encryption": "https://docs.oracle.com/en-us/iaas/Content/SecurityEncryption/overview.htm",
    "security/cloud-guard": "https://docs.oracle.com/en-us/iaas/Content/CloudGuard/concepts/cloudguardoverview.htm",
    "security/waf": "https://docs.oracle.com/en-us/iaas/Content/WAF/Concepts/overview.htm",
    "migration/aws-compute": "https://docs.oracle.com/en-us/iaas/Content/Migration/overview.htm",
    "migration/aws-storage": "https://docs.oracle.com/en-us/iaas/Content/Migration/overview.htm",
    "migration/aws-database": "https://docs.oracle.com/en-us/iaas/Content/Migration/overview.htm",
    "migration/azure-compute": "https://docs.oracle.com/en-us/iaas/Content/Migration/overview.htm",
    "migration/azure-storage": "https://docs.oracle.com/en-us/iaas/Content/Migration/overview.htm",
    "migration/azure-database": "https://docs.oracle.com/en-us/iaas/Content/Migration/overview.htm",
    "migration/gcp-compute": "https://docs.oracle.com/en-us/iaas/Content/Migration/overview.htm",
    "migration/gcp-storage": "https://docs.oracle.com/en-us/iaas/Content/Migration/overview.htm",
    "migration/gcp-database": "https://docs.oracle.com/en-us/iaas/Content/Migration/overview.htm",
    "migration/onprem-compute": "https://docs.oracle.com/en-us/iaas/Content/Migration/overview.htm",
    "migration/onprem-storage": "https://docs.oracle.com/en-us/iaas/Content/Storage/Concepts/storageoverview.htm",
    "migration/onprem-vmware": "https://docs.oracle.com/en-us/iaas/Content/cloud-migration/home.htm",
    "migration/onprem-database": "https://docs.oracle.com/en-us/iaas/Content/Migration/overview.htm",
    "migration/data-transfer": "https://docs.oracle.com/en-us/iaas/Content/Integration/overview.htm",
    "terraform/provider": "https://registry.terraform.io/providers/oracle/oci/latest/docs",
    "terraform/compute": "https://registry.terraform.io/providers/oracle/oci/latest/docs",
    "terraform/storage": "https://registry.terraform.io/providers/oracle/oci/latest/docs",
    "terraform/networking": "https://registry.terraform.io/providers/oracle/oci/latest/docs",
    "terraform/load-balancer": "https://registry.terraform.io/providers/oracle/oci/latest/docs",
    "terraform/database": "https://registry.terraform.io/providers/oracle/oci/latest/docs",
    "terraform/container": "https://registry.terraform.io/providers/oracle/oci/latest/docs",
    "terraform/serverless": "https://registry.terraform.io/providers/oracle/oci/latest/docs",
    "terraform/security": "https://registry.terraform.io/providers/oracle/oci/latest/docs",
    "terraform/observability": "https://registry.terraform.io/providers/oracle/oci/latest/docs",
    "terraform/devops": "https://registry.terraform.io/providers/oracle/oci/latest/docs",
    "terraform/state": "https://registry.terraform.io/providers/oracle/oci/latest/docs",
    "observability/logging": "https://docs.oracle.com/en-us/iaas/Content/Logging/overview.htm",
    "observability/monitoring": "https://docs.oracle.com/en-us/iaas/Content/Monitoring/overview.htm",
    "observability/stack-monitoring": "https://docs.oracle.com/en-us/iaas/Content/StackMonitoring/overview.htm",
    "observability/apm": "https://docs.oracle.com/en-us/iaas/Content/apm/overview.htm",
    "troubleshooting/connectivity": "https://docs.oracle.com/en/learn/oci-ntw-troubleshoot-1/index.html",
    "troubleshooting/performance": "https://docs.oracle.com/en-us/iaas/Content/Compute/Concepts/computeoverview.htm",
    "troubleshooting/authentication": "https://docs.oracle.com/en-us/iaas/Content/Identity/Concepts/overview.htm",
    "troubleshooting/database": "https://docs.oracle.com/en-us/iaas/Content/Database/Concepts/databaseoverview.htm",
    "troubleshooting/compute": "https://docs.oracle.com/en-us/iaas/Content/Compute/known-issues.htm",
    "troubleshooting/storage": "https://docs.oracle.com/en-us/iaas/Content/Storage/Concepts/storageoverview.htm",
    "troubleshooting/oke": "https://docs.oracle.com/en-us/iaas/Content/ContEng/Concepts/contengoverview.htm",
    "troubleshooting/functions": "https://docs.oracle.com/en-us/iaas/Content/Functions/Con/functionsoverview.htm",
    "devops/ci-cd": "https://docs.oracle.com/en-us/iaas/Content/DevOps/Concepts/devopsoverview.htm",
    "devops/resource-manager": "https://docs.oracle.com/en-us/iaas/Content/ResourceManager/Con/resourcemanager.htm",
    "devops/artifacts": "https://docs.oracle.com/en-us/iaas/Content/Artifacts/Concepts/artifactsoverview.htm",
    "devops/secrets": "https://docs.oracle.com/en-us/iaas/Content/KeyManagement/Concepts/keyoverview.htm",
}

SHAPES = [
    "VM.Standard.E4.Flex",
    "VM.Standard.A1.Flex",
    "VM.Optimized3.Flex",
    "BM.Standard.E5",
    "VM.GPU.A10.1",
    "VM.Standard3.Flex",
]
WORKLOADS = [
    "web servers",
    "batch processing",
    "machine learning",
    "databases",
    "microservices",
    "CI/CD runners",
    "data analytics",
    "high-performance computing",
]
REGIONS = [
    "sa-saopaulo-1",
    "us-ashburn-1",
    "us-phoenix-1",
    "eu-frankfurt-1",
    "uk-london-1",
    "ap-mumbai-1",
]
COMPS = ["production", "development", "staging", "sandbox", "shared-services"]


def hcat(s):
    return hashlib.md5(s.encode()).hexdigest()[:8]


def gen_answer(cat, q, diff):
    doc = DOC_LINKS.get(cat, "https://docs.oracle.com/en-us/iaas/Content/")
    s = random.choice(SHAPES)
    r = random.choice(REGIONS)
    c = random.choice(COMPS)
    n = random.randint(1, 999)

    if cat.startswith("terraform/"):
        return f"""Para usar Terraform com OCI:

**1. Provider configuration:**
```hcl
terraform {{
  required_providers {{
    oci = {{
      source  = "oracle/oci"
      version = "~> 5.0"
    }}
  }}
}}

provider "oci" {{
  region               = "{r}"
  tenancy_ocid         = var.tenancy_ocid
  user_ocid            = var.user_ocid
  fingerprint          = var.fingerprint
  private_key_path     = var.private_key_path
}}
```

**2. Variables (variables.tf):**
```hcl
variable "tenancy_ocid" {{}}
variable "user_ocid" {{}}
variable "fingerprint" {{}}
variable "private_key_path" {{}}
variable "compartment_ocid" {{
  description = "Compartment OCID"
  type        = string
}}
```

**3. Resources:**
```hcl
resource "oci_core_vcn" "main" {{
  compartment_id = var.compartment_ocid
  display_name   = "vcn-{c}"
  cidr_block     = "10.0.0.0/16"
  dns_label      = "vcn{n:02d}"
}}

resource "oci_core_subnet" "public" {{
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.main.id
  cidr_block     = "10.0.1.0/24"
  display_name   = "public-subnet"
  dns_label      = "pub{n:02d}"
}}
```

**4. Execução:**
```bash
terraform init
terraform plan -var-file="terraform.tfvars"
terraform apply -var-file="terraform.tfvars"
```

**5. Remote state no OCI Object Storage:**
```hcl
terraform {{
  backend "s3" {{
    bucket   = "terraform-state"
    key      = "{c}/terraform.tfstate"
    region   = "{r}"
    endpoint = "https://{r}.objectstorage.oci.oraclecloud.com"
  }}
}}
```

**Boas práticas:**
- Use modules para reutilização
- Pin provider versions
- Nunca commite state files
- Use workspaces para multi-environment

Doc: {doc}"""

    elif cat.startswith("troubleshooting/"):
        return f"""Para diagnosticar e resolver problemas no OCI:

**1. Coleta de informações:**
```bash
# Verifique o estado do recurso
oci <service> <resource> get --id <ocid> \\
  --query "data.{{state:'lifecycle-state', name:'display-name'}}"

# Verifique eventos recentes
oci audit event list \\
  --compartment-id <ocid> \\
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%SZ) \\
  --end-time $(date -u +%Y-%m-%dT%H:%M:%SZ)
```

**2. Diagnóstico por camada:**

**a) Rede:**
```bash
# Verificar conectividade
ping <target-ip>
traceroute <target-ip>

# Network Path Check
oci network path-check create \\
  --source-id <vnic-ocid> \\
  --destination-id <target-vnic-ocid>
```

**b) Security:**
- Verifique Security Lists e NSGs
- Confirme route tables
- Verifique IAM policies

**c) Resource:**
```bash
# Verificar métricas
oci <service> <resource> list-measurements \\
  --id <ocid> \\
  --metric-names CPUUTILIZATION
```

**3. Causas comuns:**
- Permissões IAM insuficientes → revise policies
- Security rules bloqueando tráfego → verifique ingress/egress
- Capacity indisponível → tente outro AD ou shape
- Quota excedida → solicite aumento

**4. Ferramentas de diagnóstico:**
- OCI Console → Resource → Metrics
- Log Explorer para logs de serviço
- Cloud Console connection para instâncias sem SSH
- [CHECK DOCS] Consulte status.oraclecloud.com para incidentes

Doc: {doc}"""

    elif cat.startswith("migration/"):
        return f"""Para migração para OCI:

**1. Assessment e planejamento:**
- Inventarie recursos existentes
- Mapeie serviços source → OCI equivalentes
- Defina estratégia: lift-and-shift, replatform, ou refactor
- Estime custos OCI com Pricing Calculator

**2. Preparação do ambiente OCI:**
```bash
# Criar VCN
oci network vcn create \\
  --compartment-id <ocid> \\
  --display-name "migration-vcn" \\
  --cidr-block "10.0.0.0/16"

# Criar compartment para migração
oci iam compartment create \\
  --compartment-id <tenancy-ocid> \\
  --name "migration-{c}" \\
  --description "Compartment for migration"
```

**3. Migração de dados:**
```bash
# Object Storage
oci os bucket create \\
  --compartment-id <ocid> \\
  --name "migration-data"

# Use OCI Migration Service
# Console → Migration → Object Storage Migration
```

**4. Migração de compute:**
- Converta imagens de VM para formato OCI
- Importe como custom images
- Configure networking e security
- Teste antes do cutover

**5. Migração de database:**
- Use Database Migration Service
- Ou GoldenGate para migração com mínimo downtime
- Console → Database → Migration

**6. Cutover e validação:**
- Redirecione DNS para OCI
- Valide funcionalidade
- Monitore performance
- [MUTABLE] Compare custos pós-migração

**Mapeamento de serviços:**
| Source | OCI |
|--------|-----|
| EC2/VMs/Compute Engine | OCI Compute |
| S3/Blob/GCS | Object Storage |
| RDS/Cloud SQL | Autonomous/MySQL/PostgreSQL |
| VPC/VNet/VPC | VCN |

Doc: {doc}"""

    elif cat.startswith("security/"):
        if "criar" in q.lower():
            return f"""Para criar recursos de segurança no OCI:

**Via Console:**
1. Identity & Security → selecione o serviço
2. Selecione o compartment: `{c}`
3. Clique em "Create"
4. Configure conforme o serviço:
   - **Name**: nome descritivo
   - **Compartment**: `{c}`
   - Parâmetros específicos do serviço
5. Clique em "Create"

**Via CLI:**
```bash
# Exemplo: criar Dynamic Group
oci iam dynamic-group create \\
  --compartment-id <tenancy-ocid> \\
  --name "app-servers-{c}" \\
  --description "Dynamic group for {c} servers" \\
  --matching-rule "ALL {{instance.compartment.id = '<compartment-ocid>'}}"

# Exemplo: criar policy
oci iam policy create \\
  --compartment-id <tenancy-ocid> \\
  --name "{c}-policy" \\
  --statements '[
    "Allow dynamic-group app-servers-{c} to manage instances in compartment {c}"
  ]'
```

**Princípios de segurança:**
- Least privilege: dê apenas permissões necessárias
- Use Dynamic Groups para workloads (não user credentials)
- Habilite MFA para todos os usuários
- Configure Cloud Guard para monitoramento contínuo

**Estrutura IAM recomendada:**
```
Tenancy
├── Compartments (por projeto/ambiente)
│   ├── Users/Groups
│   ├── Policies
│   └── Resources
└── Dynamic Groups (para workloads)
```

Doc: {doc}"""
        elif "configurar" in q.lower():
            return f"""Para configurar segurança no OCI:

**1. IAM Policies:**
```
# Sintaxe básica
Allow group <group-name> to <verb> <resource-type> in compartment <compartment-name>

# Exemplos comuns
Allow group admins to manage all-resources in tenancy
Allow group developers to manage instances in compartment development
Allow dynamic-group app-servers to read buckets in compartment production
```

**2. Dynamic Groups:**
```bash
# Regras de matching
# Instâncias em um compartment:
ALL {{instance.compartment.id = '<ocid>'}}

# Instâncias com tag específica:
ALL {{instance.compartment.id = '<ocid>', tag.app-tier.value = 'frontend'}}

# Resource principal para Functions:
resource.type = 'fnfunc', resource.compartment.id = '<ocid>'
```

**3. Vault e Secrets:**
```bash
# Criar secret
oci vault secret create-base64 \\
  --compartment-id <ocid> \\
  --vault-id <vault-ocid> \\
  --key-id <key-ocid> \\
  --secret-name "db-password" \\
  --secret-content-content $(echo -n "MyP@ssw0rd" | base64)
```

**Boas práticas:**
- Revise políticas regularmente
- Use break-glass accounts para emergência
- Configure Cloud Guard para detecção automática

Doc: {doc}"""
        else:
            return f"""Para gerenciar segurança no OCI:

**Identity & Security → selecione o serviço:**
- IAM: usuários, grupos, policies
- Vaults: secrets e keys
- Cloud Guard: detecção de ameaças
- WAF: proteção de aplicações web

**Via CLI:**
```bash
# Listar policies
oci iam policy list --compartment-id <ocid>

# Listar dynamic groups
oci iam dynamic-group list --compartment-id <tenancy-ocid>

# Listar secrets
oci vault secret list --compartment-id <ocid>
```

**Auditoria:**
```bash
# Eventos de segurança recentes
oci audit event list \\
  --compartment-id <ocid> \\
  --start-time $(date -u -d '24 hours ago' +%Y-%m-%dT%H:%M:%SZ) \\
  --query "data[?contains('identity.', 'user')]"
```

**Compliance:**
- Cloud Guard verifica CIS benchmarks automaticamente
- Configure detector recipes para regras customizadas
- Responder rules para auto-remediation

Doc: {doc}"""

    elif cat.startswith("observability/"):
        return f"""Para configurar observabilidade no OCI:

**1. Logging:**
```bash
# Criar Log Group
oci logging log-group create \\
  --compartment-id <ocid> \\
  --display-name "{c}-logs"

# Criar Service Log (VCN Flow Logs)
oci logging log create \\
  --compartment-id <ocid> \\
  --log-group-id <log-group-ocid> \\
  --display-name "vcn-flow-logs" \\
  --log-type SERVICE \\
  --is-enabled true \\
  --configuration '{{"source": {{"category": "flowlogs", "resource": "<vcn-ocid>", "sourceType": "OCISERVICE"}}}}' \\
  --retention-duration 30
```

**2. Monitoring e Alarms:**
```bash
# Criar alarm de CPU
oci monitoring alarm create \\
  --compartment-id <ocid> \\
  --display-name "high-cpu-{c}" \\
  --is-enabled true \\
  --metric-compartment-id <ocid> \\
  --namespace oci_computeagent \\
  --metric-name CpuUtilization \\
  --statistic AVG \\
  --interval 5m \\
  --threshold 80 \\
  --pending-duration PT5M \\
  --severity CRITICAL \\
  --destinations '[{{"serviceType": "ONS", "topicId": "<topic-ocid>"}}]'
```

**3. Notifications:**
```bash
# Criar tópico
oci ons topic create \\
  --compartment-id <ocid> \\
  --name "{c}-alerts"

# Adicionar subscription (email)
oci ons subscription create \\
  --topic-id <topic-ocid> \\
  --protocol EMAIL \\
  --endpoint "admin@example.com"
```

**Métricas disponíveis:**
- Compute: CPU, Memory, Disk, Network
- Block Volume: IOPS, Throughput, Latency
- Load Balancer: Request Count, Latency, Errors
- Database: CPU, Storage, Connections

[MUTABLE] Custos de ingestão de logs variam por volume.

Doc: {doc}"""

    elif cat.startswith("devops/"):
        return f"""Para configurar DevOps no OCI:

**1. Criar DevOps Project:**
```bash
oci devops project create \\
  --compartment-id <ocid> \\
  --name "{c}-devops-project" \\
  --description "DevOps project for {c}"
```

**2. Build Pipeline:**
```bash
oci devops build-pipeline create \\
  --project-id <project-ocid> \\
  --display-name "build-pipeline" \\
  --build-pipeline-stages '[{{
    "buildPipelineStageType": "BUILD",
    "buildSourceCollection": {{
      "items": [{{
        "connectionType": "DEVOPS_CODE_REPOSITORY",
        "repositoryUrl": "<repository-url>",
        "branch": "main"
      }}]
    }},
    "buildSpecFile": "build_spec.yaml",
    "image": "OL7_X86_64_STANDARD_10"
  }}]'
```

**3. Deploy Pipeline:**
```bash
oci devops deploy-pipeline create \\
  --project-id <project-ocid> \\
  --display-name "deploy-pipeline" \\
  --deploy-pipeline-stages '[{{
    "deployPipelineStageType": "DEPLOY",
    "deployEnvironmentId": "<environment-ocid>"
  }}]'
```

**4. Build Spec (build_spec.yaml):**
```yaml
version: 0.1
component: build
timeoutInSeconds: 3600
steps:
  - type: Command
    name: "Install dependencies"
    command: npm install
  - type: Command
    name: "Run tests"
    command: npm test
  - type: Command
    name: "Build"
    command: npm run build
```

**Boas práticas:**
- Use approval stages para produção
- Configure notificações para pipeline events
- Integre com OCI Registry para container images
- Use secrets do Vault para credenciais

Doc: {doc}"""

    elif cat.startswith("serverless/"):
        return f"""Para configurar serverless no OCI:

**1. OCI Functions:**
```bash
# Criar Functions Application
oci fn application create \\
  --compartment-id <ocid> \\
  --display-name "{c}-app" \\
  --subnet-ids '["<subnet-ocid>"]' \\
  --config '{{"LOG_LEVEL": "INFO"}}'

# Deploy function
fn deploy --app {c}-app
```

**2. Function code (Python):**
```python
import io
import json
from fdk import response

def handler(ctx, data: io.BytesIO = None):
    body = json.loads(data.getvalue().decode("utf-8")) if data else {{}}
    return response.Response(
        ctx,
        response_data=json.dumps({{"message": "Hello from OCI Functions", "input": body}}),
        headers={{"Content-Type": "application/json"}}
    )
```

**3. API Gateway:**
```bash
# Criar API Gateway
oci api-gateway gateway create \\
  --compartment-id <ocid> \\
  --display-name "{c}-api-gw" \\
  --subnet-id <subnet-ocid> \\
  --specification '{{
    "routes": [{{
      "path": "/hello",
      "methods": ["GET"],
      "backend": {{
        "type": "ORACLE_FUNCTIONS_BACKEND",
        "functionId": "<function-ocid>"
      }}
    }}]
  }}'
```

**Configurações recomendadas:**
- Timeout: 30s (default), máximo 300s
- Memory: 128MB a 2048MB
- Use VCN private para acesso a recursos internos

[MUTABLE] Preços baseados em invocações e GB-seconds.

Doc: {doc}"""

    elif cat.startswith("container/"):
        return f"""Para configurar containers no OCI:

**1. OKE Cluster:**
```bash
# Criar cluster
oci ce cluster create \\
  --compartment-id <ocid> \\
  --name "{c}-oke-cluster" \\
  --kubernetes-version "v1.29.0" \\
  --vcn-id <vcn-ocid> \\
  --endpoint-config '{{"isPublicIpEnabled": true, "subnetId": "<subnet-ocid>"}}'

# Criar node pool
oci ce node-pool create \\
  --compartment-id <ocid> \\
  --cluster-id <cluster-ocid> \\
  --name "node-pool-1" \\
  --kubernetes-version "v1.29.0" \\
  --node-shape "{s}" \\
  --node-config-details '{{"size": 3, "placementConfigs": [{{"availabilityDomain": "AD-1", "subnetId": "<subnet-ocid>"}}]}}'
```

**2. Conectar com kubectl:**
```bash
oci ce cluster create-kubeconfig \\
  --cluster-id <cluster-ocid> \\
  --file $HOME/.kube/config \\
  --region {r} \\
  --token-version 2.0.0

kubectl get nodes
```

**3. OCIR (Container Registry):**
```bash
# Login
docker login -u '<tenancy>/<username>' {r}.ocir.io

# Push image
docker tag myapp:latest {r}.ocir.io/<tenancy>/myapp:latest
docker push {r}.ocir.io/<tenancy>/myapp:latest
```

**4. Deploy application:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
    spec:
      containers:
      - name: myapp
        image: {r}.ocir.io/<tenancy>/myapp:latest
        ports:
        - containerPort: 8080
```

Doc: {doc}"""

    elif cat.startswith("database/"):
        if "criar" in q.lower():
            return f"""Para criar um database no OCI:

**Via Console:**
1. Oracle Database → selecione o tipo de database
2. Selecione o compartment: `{c}`
3. Clique em "Create"
4. Configure:
   - **Compartment**: `{c}`
   - **Display Name**: `db-{n:03d}`
   - **Workload Type**: Transactional ou Data Warehouse
   - **OCPUs**: comece com 1-2 (auto-scaling disponível)
   - **Storage**: 1TB (auto-scaling até 128TB)
   - **Admin Password**: defina senha forte
   - **Network**: escolha public ou private endpoint
5. Clique em "Create"

**Via CLI:**
```bash
oci db autonomous-database create \\
  --compartment-id <ocid> \\
  --display-name "adb-{n:03d}" \\
  --cpu-core-count 1 \\
  --data-storage-size-in-tbs 1 \\
  --admin-password "<strong-password>" \\
  --db-workload OLTP \\
  --is-auto-scaling-enabled true \\
  --wait-for-state AVAILABLE
```

**Tipos de database no OCI:**
- **Autonomous Database (ATP)**: OLTP, uso geral
- **Autonomous Data Warehouse (ADW)**: analytics
- **MySQL HeatWave**: MySQL gerenciado com analytics
- **OCI PostgreSQL**: PostgreSQL gerenciado
- **Oracle NoSQL**: database NoSQL de baixa latência

**Conexão:**
```bash
# Download do wallet
oci db autonomous-database generate-wallet \\
  --autonomous-database-id <ocid> \\
  --file wallet.zip \\
  --password "<wallet-password>"
```

[MUTABLE] Preços variam por OCPU e storage.

Doc: {doc}"""
        elif "configurar" in q.lower():
            return f"""Para configurar databases no OCI:

**1. Configuração de conexão:**
```bash
# Download wallet para Autonomous Database
oci db autonomous-database generate-wallet \\
  --autonomous-database-id <ocid> \\
  --file wallet.zip

# Configure connection string
# JDBC: jdbc:oracle:thin:@<db-name>_tp?TNS_ADMIN=/path/to/wallet
# Python: cx_Oracle.connect(user="<user>", password="<pass>", dsn="<tp-connect>")
```

**2. Configuração de networking:**
```bash
# Private endpoint (recomendado para produção)
oci db autonomous-database update \\
  --autonomous-database-id <ocid> \\
  --subnet-id <private-subnet-ocid>
```

**3. Auto-scaling:**
```bash
oci db autonomous-database update \\
  --autonomous-database-id <ocid> \\
  --is-auto-scaling-enabled true
```

**Boas práticas:**
- Use private endpoints em produção
- Habilite auto-scaling para workloads variáveis
- Configure backups automáticos (padrão)
- Use Database Actions para administração web

Doc: {doc}"""
        else:
            return f"""Para gerenciar databases no OCI:

**Operações via Console:**
1. Oracle Database → selecione o database
2. Operações disponíveis:
   - Scale (OCPUs e Storage)
   - Start/Stop
   - Backup/Restore
   - Clone
   - Generate Wallet

**Via CLI:**
```bash
# Scale up
oci db autonomous-database update \\
  --autonomous-database-id <ocid> \\
  --cpu-core-count 4 \\
  --data-storage-size-in-tbs 2

# Criar backup manual
oci db autonomous-database backup \\
  --autonomous-database-id <ocid> \\
  --display-name "manual-backup-$(date +%Y%m%d)"

# Listar backups
oci db autonomous-database backup list \\
  --autonomous-database-id <ocid>
```

**Monitoring:**
- Performance Hub para análise em tempo real
- AWR reports para análise histórica
- OCI Monitoring para métricas e alarms

[MUTABLE] Preços variam por OCPU e storage.

Doc: {doc}"""

    elif cat.startswith("storage/"):
        if "criar" in q.lower():
            return f"""Para criar recursos de Storage no OCI:

**Via Console:**
1. Storage → selecione o tipo de storage
2. Selecione o compartment: `{c}`
3. Clique em "Create"
4. Configure os parâmetros:
   - **Name**: nome descritivo (ex: `data-bucket-{n:03d}`)
   - **Compartment**: `{c}`
   - **Region**: `{r}`
5. Clique em "Create"

**Via CLI:**
```bash
# Object Storage
oci os bucket create \\
  --compartment-id <ocid> \\
  --name "data-bucket-{n:03d}" \\
  --storage-tier Standard

# Block Volume
oci bv volume create \\
  --compartment-id <ocid> \\
  --display-name "data-volume-{n:03d}" \\
  --size-in-gbs 100 \\
  --vpus-per-gb 10
```

**Tipos de storage disponíveis:**
- **Object Storage**: dados não estruturados, backups, archives
- **Block Volume**: discos para instâncias, databases
- **File Storage**: NFS compartilhado

**Boas práticas:**
- Use lifecycle policies para gerenciar custos
- Habilite versionamento para dados críticos
- Configure encryption (padrão no OCI)

[MUTABLE] Preços variam por storage tier e região.

Doc: {doc}"""
        elif "configurar" in q.lower():
            return f"""Para configurar storage no OCI:

**1. Object Storage configuration:**
```bash
# Configurar lifecycle policy
oci os object-lifecycle-policy put \\
  --namespace-name <namespace> \\
  --bucket-name <bucket> \\
  --items '[{{
    "name": "archive-old-objects",
    "action": "ARCHIVE",
    "time-amount": 90,
    "time-unit": "DAYS"
  }}]'

# Configurar versionamento
oci os bucket update \\
  --namespace-name <namespace> \\
  --bucket-name <bucket> \\
  --versioning Enabled
```

**2. Block Volume configuration:**
```bash
# Ajustar performance (VPUs)
oci bv volume update \\
  --volume-id <ocid> \\
  --vpus-per-gb 20

# Anexar a instância (paravirtualized)
oci compute volume-attachment attach \\
  --instance-id <instance-ocid> \\
  --volume-id <volume-ocid> \\
  --type paravirtualized
```

**3. File Storage configuration:**
```bash
# Criar mount target
oci fs mount-target create \\
  --compartment-id <ocid> \\
  --availability-domain <ad> \\
  --display-name "mt-{c}" \\
  --subnet-id <subnet-ocid>
```

**Considerações:**
- Block Volumes: ajuste VPUs conforme necessidade de IOPS
- Object Storage: use tiering para otimizar custos
- File Storage: configure export options para access control

Doc: {doc}"""
        else:
            return f"""Para gerenciar Storage no OCI:

**Operações via Console:**
1. Storage → selecione o tipo (Object, Block, File)
2. Selecione o recurso desejado
3. Use as opções disponíveis:
   - Create backup/clone
   - Edit configuration
   - View metrics
   - Manage access

**Operações via CLI:**
```bash
# Listar buckets
oci os bucket list --compartment-id <ocid>

# Listar volumes
oci bv volume list --compartment-id <ocid>

# Listar mount targets
oci fs mount-target list --compartment-id <ocid>
```

**Gerenciamento de custos:**
- Use Object Storage tiering (Standard → Infrequent → Archive)
- Configure lifecycle policies para automação
- Monitore usage com OCI Cost Analysis

**Segurança:**
- Encryption at rest é padrão
- Use customer-managed keys para controle adicional
- Configure IAM policies granulares

[MUTABLE] Preços e limites variam por região.

Doc: {doc}"""

    elif cat.startswith("networking/"):
        if "criar" in q.lower():
            return f"""Para criar recursos de rede no OCI:

**Via Console:**
1. Networking → Virtual Cloud Networks
2. Selecione o compartment: `{c}`
3. Clique em "Start VCN Wizard" ou "Create VCN"
4. Configure:
   - **Name**: `vcn-{c}-{n:03d}`
   - **CIDR Block**: `10.{random.randint(0, 255)}.0.0/16`
   - **DNS Resolution**: habilitado
   - **DNS Label**: `vcn{n:02d}`
5. Configure subnets (pública e privada)
6. Clique em "Create"

**Via CLI:**
```bash
# Criar VCN
oci network vcn create \\
  --compartment-id <ocid> \\
  --display-name "vcn-{c}" \\
  --cidr-block "10.0.0.0/16" \\
  --dns-label "vcn{n:02d}"

# Criar subnet pública
oci network subnet create \\
  --compartment-id <ocid> \\
  --vcn-id <vcn-ocid> \\
  --display-name "public-subnet" \\
  --cidr-block "10.0.1.0/24" \\
  --prohibit-public-ip-on-vnic false

# Criar Internet Gateway
oci network internet-gateway create \\
  --compartment-id <ocid> \\
  --vcn-id <vcn-ocid> \\
  --display-name "igw" \\
  --is-enabled true
```

**Componentes essenciais:**
- **VCN**: rede virtual isolada
- **Subnets**: pública (com IP público) ou privada
- **Internet Gateway**: acesso à internet
- **NAT Gateway**: saída para internet sem IP público
- **Service Gateway**: acesso a serviços OCI (Object Storage)

Doc: {doc}"""
        elif "configurar" in q.lower():
            return f"""Para configurar recursos de rede no OCI:

**1. Route Tables:**
```bash
oci network route-table create \\
  --compartment-id <ocid> \\
  --vcn-id <vcn-ocid> \\
  --display-name "public-rt" \\
  --route-rules '[{{
    "destination": "0.0.0.0/0",
    "networkEntityId": "<igw-ocid>"
  }}]'
```

**2. Security Lists:**
```bash
oci network security-list create \\
  --compartment-id <ocid> \\
  --vcn-id <vcn-ocid> \\
  --display-name "web-servers" \\
  --ingress-security-rules '[{{
    "protocol": "6",
    "source": "0.0.0.0/0",
    "tcpOptions": {{"destinationPortRange": {{"min": 443, "max": 443}}}}
  }}]'
```

**3. Network Security Groups:**
```bash
# Criar NSG
oci network nsg create \\
  --compartment-id <ocid> \\
  --vcn-id <vcn-ocid> \\
  --display-name "app-nsg"

# Adicionar regra
oci network nsg rules add \\
  --nsg-id <nsg-ocid> \\
  --security-rules '[{{
    "direction": "INGRESS",
    "protocol": "6",
    "source": "10.0.0.0/16",
    "tcpOptions": {{"destinationPortRange": {{"min": 8080, "max": 8080}}}}
  }}]'
```

**Boas práticas:**
- Use NSGs para granularidade (preferred sobre Security Lists)
- Aplique princípio de least privilege
- Documente todas as regras de rede

Doc: {doc}"""
        else:
            return f"""Para gerenciar recursos de rede no OCI:

**Via Console:**
1. Networking → Virtual Cloud Networks
2. Selecione a VCN desejada
3. Gerencie componentes:
   - Subnets, Gateways, Route Tables
   - Security Lists, NSGs
   - DHCP Options, DNS

**Via CLI:**
```bash
# Listar VCNs
oci network vcn list --compartment-id <ocid>

# Verificar subnets
oci network subnet list --vcn-id <vcn-ocid>

# Verificar gateways
oci network internet-gateway list --vcn-id <vcn-ocid>
```

**Considerações:**
- VCNs são regionais (não cross-region)
- Use VCN peering para conectar VCNs
- DRG para conectividade hybrid e cross-region

Doc: {doc}"""

    elif cat.startswith("lb/"):
        return f"""Para configurar Load Balancer no OCI:

**Via Console:**
1. Networking → Load Balancers
2. Selecione o compartment: `{c}`
3. Clique em "Create Load Balancer"
4. Configure:
   - **Name**: `lb-{c}-{n:03d}`
   - **Visibility**: Public ou Private
   - **Shape**: Flexible (recomendado)
   - **Minimum/Maximum bandwidth**: 10Mbps / 100Mbps
   - **Subnets**: selecione subnet pública
5. Configure Backend Set:
   - **Name**: `backend-{c}`
   - **Policy**: Round Robin ou Least Connections
   - **Health Check**: HTTP/HTTPS com path `/health`
   - **Backends**: adicione instâncias
6. Configure Listener:
   - **Name**: `listener-http`
   - **Port**: 80 (ou 443 para HTTPS)
   - **Protocol**: HTTP (ou HTTPS)

**Via CLI:**
```bash
oci lb load-balancer create \\
  --compartment-id <ocid> \\
  --display-name "lb-{c}" \\
  --shape-name flexible \\
  --shape-details '{{"minimumBandwidthInMbps": 10, "maximumBandwidthInMbps": 100}}' \\
  --subnet-ids '["<subnet-ocid>"]'

oci lb backend-set create \\
  --load-balancer-id <lb-ocid> \\
  --name "backend-{c}" \\
  --policy "ROUND_ROBIN" \\
  --health-checker '{{"protocol": "HTTP", "port": 80, "urlPath": "/health"}}'

oci lb backend add \\
  --load-balancer-id <lb-ocid> \\
  --backend-set-name "backend-{c}" \\
  --ip-address "<backend-ip>" \\
  --port 80
```

**Boas práticas:**
- Use Flexible shape para auto-scaling
- Configure health checks adequados
- Use SSL termination no LB
- [MUTABLE] Preços baseados em bandwidth e horas de uso

Doc: {doc}"""

    elif cat.startswith("compute/"):
        if "criar" in q.lower() or "criação" in q.lower() or "criando" in q.lower():
            return f"""Para criar recursos de Compute no OCI:

**Via Console:**
1. Acesse o Console OCI e navegue até Compute → Instances
2. Selecione o compartment: `{c}`
3. Clique em "Create Instance"
4. Configure:
   - **Name**: defina um nome descritivo (ex: `web-server-{n:03d}`)
   - **Compartment**: selecione `{c}`
   - **Placement**: escolha a Availability Domain
   - **Image**: Oracle Linux 8/9 ou Ubuntu 22.04
   - **Shape**: selecione `{s}`
   - **Networking**: configure VCN e subnet
   - **SSH Keys**: adicione sua chave pública SSH
5. Clique em "Create"

**Via CLI:**
```bash
oci compute instance launch \\
  --compartment-id <ocid> \\
  --display-name "web-server-{n:03d}" \\
  --shape "{s}" \\
  --subnet-id <subnet-ocid> \\
  --assign-public-ip true \\
  --ssh-authorized-keys-file ~/.ssh/id_rsa.pub \\
  --wait-for-state RUNNING
```

**Configurações recomendadas:**
- Boot volume: mínimo 50GB (padrão)
- VCN: use subnet privada para workloads de produção
- Tags: adicione tags para organização e custos

**Equivalentes multi-cloud:**
- AWS: EC2 instances
- Azure: Virtual Machines
- GCP: Compute Engine

[MUTABLE] Preços e limites variam por região e shape. Verifique no Console.

Doc: {doc}"""
        elif "configurar" in q.lower() or "configuração" in q.lower():
            return f"""Para configurar recursos de Compute no OCI:

**1. Configuração inicial via Console:**
- Compute → Instances → selecione a instância
- Clique em "Edit" para modificar configurações
- Ajuste shape, networking e tags conforme necessário

**2. Configuração via CLI:**
```bash
# Atualizar configuração da instância
oci compute instance update \\
  --instance-id <ocid> \\
  --defined-tags '{{"operations": {{"environment": "{c}"}}}}'

# Configurar VNIC
oci compute vnic-attachment list \\
  --instance-id <ocid> \\
  --query "data[].{{id:id, subnet:'subnet-id'}}"
```

**3. Configuração de cloud-init:**
```yaml
#cloud-config
package_update: true
packages:
  - nginx
  - git
runcmd:
  - systemctl enable nginx
  - systemctl start nginx
  - echo "Hello from OCI" > /var/www/html/index.html
```

**Boas práticas:**
- Use instance configuration para consistência
- Configure Oracle Cloud Agent para métricas avançadas
- Habilite monitoring básico (gratuito)

**Considerações:**
- Algumas configurações requerem stop/start da instância
- Shape changes podem exigir compatibilidade de image

Doc: {doc}"""
        else:
            return f"""Para gerenciar recursos de Compute no OCI:

**Via Console:**
1. Compute → Instances → selecione a instância desejada
2. Use "More Actions" para operações de lifecycle:
   - Start/Stop/Reboot
   - Create Custom Image
   - Attach/Detach Block Volumes
   - Edit configuration

**Via CLI:**
```bash
# Listar instâncias
oci compute instance list \\
  --compartment-id <ocid> \\
  --lifecycle-state RUNNING

# Ação na instância
oci compute instance action \\
  --instance-id <ocid> \\
  --action SOFTSTOP

# Verificar métricas
oci compute instance list-measurements \\
  --instance-id <ocid> \\
  --metric-names CPUUTILIZATION
```

**Operações comuns:**
- **Resize**: altere o shape via Console ou CLI
- **Backup**: crie boot volume backup antes de mudanças
- **Tags**: organize com freeform e defined tags
- **Monitoring**: ative Oracle Cloud Agent para métricas detalhadas

**Considerações importantes:**
- Stop/Start preserva dados do boot volume
- Terminate remove a instância permanentemente
- [MUTABLE] Billing para compute é por segundo (mínimo 1 minuto)

**Equivalentes multi-cloud:**
- AWS EC2 ≈ OCI Compute
- Azure VMs ≈ OCI Compute
- GCP Compute Engine ≈ OCI Compute

Doc: {doc}"""

    else:
        return f"""Para gerenciar recursos no OCI:

**Via Console:**
1. Navegue até o serviço correspondente
2. Selecione o compartment: `{c}`
3. Configure os parâmetros conforme necessidade
4. Clique em "Create" ou "Save"

**Via CLI:**
```bash
# Listar recursos
oci <service> <resource> list --compartment-id <ocid>

# Criar recurso
oci <service> <resource> create \\
  --compartment-id <ocid> \\
  --display-name "resource-{n:03d}"

# Verificar status
oci <service> <resource> get --id <ocid>
```

**Boas práticas:**
- Use compartments para isolamento lógico
- Configure tags para organização
- Habilite monitoring e logging
- Siga princípio de least privilege para IAM

**Considerações:**
- [MUTABLE] Preços e limites variam por região
- [CHECK DOCS] Verifique documentação para últimas atualizações

Doc: {doc}"""


def main():
    categories = list(SYSTEM_PROMPTS.keys())
    target_total = 10000
    per_cat = target_total // len(categories)  # ~140 per category

    examples = []
    total_generated = 0

    print(f"Generating {target_total} examples across {len(categories)} categories...")
    print(f"Target: ~{per_cat} examples per category")

    for cat in categories:
        sys_prompt = SYSTEM_PROMPTS[cat]
        doc = DOC_LINKS.get(cat, "https://docs.oracle.com/en-us/iaas/Content/")

        # Load existing questions to avoid duplicates
        existing_qs = set()

        for i in range(per_cat):
            # Difficulty distribution: 30% beginner, 50% intermediate, 20% advanced
            r = random.random()
            if r < 0.30:
                diff = "beginner"
            elif r < 0.80:
                diff = "intermediate"
            else:
                diff = "advanced"

            # Generate question from templates with variations
            q = _make_question(cat, diff, i, existing_qs)
            existing_qs.add(q)

            answer = gen_answer(cat, q, diff)

            example = {
                "messages": [
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": q},
                    {"role": "assistant", "content": answer},
                ],
                "metadata": {
                    "category": cat,
                    "difficulty": diff,
                    "source": "generated",
                },
            }
            examples.append(example)
            total_generated += 1

    print(f"\nTotal generated: {total_generated}")

    # Write to curated files
    out_dir = Path("data/curated")
    out_dir.mkdir(parents=True, exist_ok=True)

    # Group by category
    by_cat = {}
    for ex in examples:
        cat = ex["metadata"]["category"]
        if cat not in by_cat:
            by_cat[cat] = []
        by_cat[cat].append(ex)

    # Write individual files
    for cat, cat_examples in by_cat.items():
        safe_name = cat.replace("/", "-")
        fpath = out_dir / f"{safe_name}.jsonl"
        with open(fpath, "w", encoding="utf-8") as f:
            for ex in cat_examples:
                f.write(json.dumps(ex, ensure_ascii=False) + "\n")
        print(f"  {safe_name}: {len(cat_examples)} examples")

    # Write combined file
    all_path = Path("data/all_curated.jsonl")
    with open(all_path, "w", encoding="utf-8") as f:
        for ex in examples:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")
    print(f"\nCombined: {all_path} ({len(examples)} examples)")

    # Stats
    from collections import Counter

    cats = Counter(e["metadata"]["category"] for e in examples)
    diffs = Counter(e["metadata"]["difficulty"] for e in examples)
    print(f"\n=== Category distribution ===")
    for cat, cnt in sorted(cats.items()):
        print(f"  {cat}: {cnt}")
    print(f"\n=== Difficulty distribution ===")
    for d, cnt in sorted(diffs.items()):
        pct = cnt / len(examples) * 100
        print(f"  {d}: {cnt} ({pct:.1f}%)")
    print(f"\n=== Total: {len(examples)} ===")


def _make_question(cat, diff, idx, existing_qs):
    """Generate varied questions per category."""
    s = random.choice(SHAPES)
    r = random.choice(REGIONS)
    c = random.choice(COMPS)
    n = random.randint(1, 999)

    questions_by_cat = {
        "compute/instances": [
            f"Como criar uma instância no OCI com shape {s}?",
            f"Qual o melhor shape para {random.choice(WORKLOADS)} no OCI?",
            "Como configurar SSH para acessar instâncias OCI?",
            "Como parar e iniciar uma instância OCI sem perder dados?",
            "Como resolver o erro 'Out of Host Capacity' ao criar instâncias?",
            "Como criar múltiplas instâncias de forma consistente?",
            "Como migrar uma instância entre Availability Domains?",
            "Como configurar cloud-init para provisionamento automático?",
            "Como usar instance principal para acesso a outros serviços OCI?",
            "Como configurar tags para organizar instâncias OCI?",
            "Como criar uma instância com múltiplas VNICs?",
            "Como fazer resize de uma instância OCI para um shape maior?",
            "Como configurar boot volume customizado para uma instância?",
            "Como proteger instâncias contra terminação acidental?",
            "Como monitorar saúde de instâncias OCI?",
            "Como criar instâncias spot no OCI para reduzir custos?",
            "Como configurar dedicated hosts no OCI?",
            "Como usar capacity reservation para garantir capacidade?",
            "Como criar uma instância a partir de um boot volume backup?",
            "Como configurar GPU instances para machine learning no OCI?",
            f"Como criar uma instância Oracle Linux 9 no compartment {c}?",
            f"Qual a diferença entre VM.Standard.E4.Flex e {s}?",
            "Como conectar via SSH usando OCI Console?",
            "Como adicionar uma segunda VNIC a uma instância existente?",
            "Como configurar hostname customizado em uma instância?",
            "Como fazer backup do boot volume antes de mudanças?",
            "Como usar instance console connection para debug?",
            "Como configurar NTP em instâncias OCI?",
            "Como instalar Oracle Cloud Agent em instâncias existentes?",
            "Como configurar proxy em instâncias OCI?",
            "Como criar instâncias com Oracle Linux vs Ubuntu?",
            "Como gerenciar usuários em instâncias OCI?",
            "Como configurar firewall iptables em instâncias OCI?",
            "Como usar pre-emptible instances para workloads batch?",
            "Como configurar instâncias para alta disponibilidade?",
            f"Como criar uma instância na região {r}?",
            "Como resolver problemas de DNS em instâncias OCI?",
            "Como configurar swap em instâncias OCI?",
            "Como monitorar I/O de disco em instâncias?",
            "Como configurar log rotation em instâncias OCI?",
            "Como criar instâncias com custom boot volume size?",
            "Como usar instance metadata service?",
            "Como configurar instâncias para workloads de banco de dados?",
            "Como migrar instâncias entre regiões?",
            "Como configurar instâncias para web servers?",
            "Como usar OCI CLI para gerenciar instâncias?",
            "Como configurar instâncias para aplicações Java?",
            "Como otimizar instâncias para performance de rede?",
            "Como configurar instâncias para CI/CD runners?",
            "Como usar instâncias para desenvolvimento local?",
            f"Como criar uma instância BM.Standard.E5 para {random.choice(WORKLOADS)}?",
            "Como configurar instâncias para machine learning?",
            "Como gerenciar licenças de Windows em instâncias OCI?",
            "Como configurar instâncias para SAP workloads?",
            "Como usar instâncias para ambientes de teste?",
            "Como configurar instâncias para microservices?",
            "Como criar instâncias com IPv6?",
            "Como configurar instâncias para high-performance computing?",
            "Como usar instâncias para data analytics?",
            "Como configurar instâncias para streaming de dados?",
            "Como criar instâncias com boot volume encrypted?",
            "Como configurar instâncias para workloads de IA?",
            "Como usar instâncias para backup e disaster recovery?",
            "Como configurar instâncias para aplicações .NET?",
            "Como criar instâncias com Oracle Linux 8?",
            "Como configurar instâncias para workloads de IoT?",
            "Como usar instâncias para edge computing?",
            "Como configurar instâncias para workloads de gaming?",
            "Como criar instâncias com Ubuntu 22.04?",
            "Como configurar instâncias para workloads de vídeo?",
            "Como usar instâncias para renderização 3D?",
            "Como configurar instâncias para workloads de blockchain?",
            f"Como criar uma instância VM.Optimized3.Flex para {random.choice(WORKLOADS)}?",
            "Como configurar instâncias para workloads de email?",
            "Como usar instâncias para file servers?",
            "Como configurar instâncias para print servers?",
            "Como criar instâncias com CentOS?",
            "Como configurar instâncias para workloads de DNS?",
            "Como usar instâncias para DHCP servers?",
            "Como configurar instâncias para NTP servers?",
            "Como criar instâncias com Rocky Linux?",
            "Como configurar instâncias para workloads de LDAP?",
            "Como usar instâncias para certificate authorities?",
            "Como configurar instâncias para workloads de monitoring?",
            "Como criar instâncias com AlmaLinux?",
            "Como configurar instâncias para workloads de logging?",
            "Como usar instâncias para configuration management?",
            "Como configurar instâncias para workloads de backup?",
            f"Como criar uma instância VM.GPU.A10.1 para {random.choice(WORKLOADS)}?",
            "Como configurar instâncias para workloads de database?",
            "Como usar instâncias para application servers?",
            "Como configurar instâncias para workloads de cache?",
            "Como criar instâncias com SUSE Linux?",
            "Como configurar instâncias para workloads de messaging?",
            "Como usar instâncias para queue workers?",
            "Como configurar instâncias para workloads de search?",
            "Como criar instâncias com FreeBSD?",
            "Como configurar instâncias para workloads de analytics?",
            "Como usar instâncias para data warehouses?",
            "Como configurar instâncias para workloads de ETL?",
            f"Como criar uma instância VM.Standard3.Flex para {random.choice(WORKLOADS)}?",
            "Como configurar instâncias para workloads de API?",
            "Como usar instâncias para web scraping?",
            "Como configurar instâncias para workloads de crawling?",
            "Como criar instâncias com Debian?",
            "Como configurar instâncias para workloads de ML training?",
            "Como usar instâncias para model inference?",
            "Como configurar instâncias para workloads de computer vision?",
            "Como criar instâncias com Windows Server 2022?",
            "Como configurar instâncias para workloads de NLP?",
            "Como usar instâncias para recommendation engines?",
            "Como configurar instâncias para workloads de fraud detection?",
            f"Como criar uma instância para {random.choice(WORKLOADS)} com alta disponibilidade?",
            "Como configurar instâncias para workloads de real-time processing?",
            "Como usar instâncias para batch processing?",
            "Como configurar instâncias para workloads de stream processing?",
            "Como criar instâncias com Oracle Linux 9 minimal?",
            "Como configurar instâncias para workloads de data lake?",
            "Como usar instâncias para data pipeline orchestration?",
            "Como configurar instâncias para workloads de data quality?",
            "Como criar instâncias com RHEL 9?",
            "Como configurar instâncias para workloads de data governance?",
            "Como usar instâncias para master data management?",
            "Como configurar instâncias para workloads de data catalog?",
        ],
        "compute/scaling": [
            "Como criar um Instance Pool no OCI?",
            "Como configurar auto-scaling baseado em CPU?",
            "Como configurar auto-scaling baseado em métricas customizadas?",
            "Como fazer rolling update em um Instance Pool?",
            "Como configurar load balancer com Instance Pool?",
            "Qual a diferença entre Instance Pool e Instance Configuration?",
            "Como resolver falhas de provisioning em Instance Pool?",
            "Como configurar auto-scaling com schedule (horário)?",
            "Como distribuir instâncias entre múltiplos ADs?",
            "Como configurar health check para auto-scaling?",
            "Como monitorar custos de Instance Pools?",
            "Como usar placement groups com Instance Pools?",
            "Como configurar scale-in policies para reduzir custos?",
            "Como integrar Instance Pool com OCI DevOps?",
            "Como configurar auto-scaling para workloads batch?",
        ],
        "compute/custom-images": [
            "Como criar uma custom image a partir de uma instância existente?",
            "Como preparar uma instância antes de criar uma custom image?",
            "Como exportar uma custom image para Object Storage?",
            "Como compartilhar custom images entre compartments?",
            "Como importar uma imagem externa para o OCI?",
            "Como validar uma custom image antes de usar em produção?",
            "Como gerenciar o ciclo de vida de custom images?",
            "Como criar golden images com Packer para OCI?",
            "Como atualizar custom images sem causar downtime?",
            "Como converter imagens VMDK para OCI?",
            "Como criar imagens otimizadas para ARM/Ampere?",
            "Como automatizar a criação de imagens com OCI DevOps?",
            "Como fazer backup de custom images entre regiões?",
            "Como criar imagens com software pré-instalado?",
            "Como remover dados sensíveis antes de criar uma imagem?",
        ],
        "storage/block": [
            "Como criar e anexar um Block Volume a uma instância OCI?",
            "Como configurar performance tiers (VPUs) em Block Volume?",
            "Como fazer backup de Block Volumes?",
            "Como clonar um Block Volume?",
            "Como migrar Block Volumes entre regiões?",
            "Como monitorar performance de Block Volumes?",
            "Como resolver I/O errors em Block Volumes?",
            "Como configurar Block Volume boot para instâncias?",
            "Como fazer resize de um Block Volume sem downtime?",
            "Como usar Block Volume com múltiplas instâncias (read-only)?",
            "Como configurar encryption em Block Volumes?",
            "Como automatizar backups de Block Volumes?",
            "Como comparar Balanced vs Higher Performance vs Ultra High?",
            "Como montar um Block Volume no Linux?",
            "Como configurar iSCSI para Block Volumes?",
        ],
        "storage/object": [
            "Como criar um bucket no OCI Object Storage?",
            "Como configurar Pre-Authenticated Requests (PAR)?",
            "Como configurar lifecycle policies no Object Storage?",
            "Como habilitar versionamento em um bucket?",
            "Como replicar buckets entre regiões?",
            "Como configurar Object Lock (WORM)?",
            "Como migrar dados do S3 para OCI Object Storage?",
            "Como usar Object Storage como backend de website estático?",
            "Como configurar CORS para um bucket?",
            "Como monitorar custos do Object Storage?",
            "Como fazer upload de arquivos grandes (multipart)?",
            "Como configurar encryption no Object Storage?",
            "Como configurar tiering (Standard, Infrequent, Archive)?",
            "Como listar e gerenciar objetos via CLI?",
            "Como usar Object Storage com CloudFront equivalente?",
        ],
        "storage/file": [
            "Como criar um File Storage (NFS) no OCI?",
            "Como configurar mount targets e export sets?",
            "Como montar File Storage em instâncias Linux?",
            "Como configurar opções de export (access control)?",
            "Como fazer backup do File Storage?",
            "Como monitorar performance do File Storage?",
            "Como migrar NFS on-premises para OCI File Storage?",
            "Como configurar File Storage com OKE?",
            "Como resolver problemas de permissão no File Storage?",
            "Como comparar File Storage vs Block Volume para shared storage?",
            "Como configurar snapshot automático do File Storage?",
            "Como usar File Storage com múltiplos compartments?",
            "Como otimizar performance de I/O no File Storage?",
            "Como configurar File Storage para SAP workloads?",
            "Como monitorar quota de uso do File Storage?",
        ],
        "networking/vcn": [
            "Como criar uma VCN no OCI?",
            "Como planejar CIDR blocks para VCNs?",
            "Como configurar subnets públicas e privadas?",
            "Como configurar Internet Gateway?",
            "Como configurar NAT Gateway para subnets privadas?",
            "Como configurar Service Gateway para acesso a serviços OCI?",
            "Como fazer VCN peering local?",
            "Como fazer VCN peering remoto entre regiões?",
            "Como configurar route tables customizadas?",
            "Como migrar uma VCN para outro compartment?",
            "Como configurar DHCP options customizadas?",
            "Como resolver conflitos de CIDR em VCN peering?",
            "Como usar Transit Routing com DRG?",
            "Como configurar DNS customizado na VCN?",
            "Como planejar uma arquitetura multi-VCN?",
        ],
        "networking/security": [
            "Como configurar Security Lists no OCI?",
            "Como configurar Network Security Groups (NSG)?",
            "Qual a diferença entre Security Lists e NSGs?",
            "Como configurar regras stateful vs stateless?",
            "Como configurar regras de ingress para uma aplicação web?",
            "Como configurar regras de egress para limitar tráfego de saída?",
            "Como debugar regras de segurança que bloqueiam tráfego?",
            "Como configurar NSG para OKE?",
            "Como auditar regras de segurança da VCN?",
            "Como usar Network Security Groups com Load Balancer?",
            "Como configurar regras para ICMP (ping)?",
            "Como configurar security para bastion host?",
            "Como migrar Security Lists para NSGs?",
            "Como configurar regras mínimas de segurança (least privilege)?",
            "Como configurar WAF na frente de uma aplicação?",
        ],
        "networking/connectivity": [
            "Como configurar VPN IPSec no OCI?",
            "Como configurar FastConnect (dedicated connection)?",
            "Como configurar Dynamic Routing Gateway (DRG)?",
            "Como resolver problemas de conectividade VPN?",
            "Como configurar VCN peering entre regiões?",
            "Como configurar hub-and-spoke com DRG?",
            "Como migrar de VPN para FastConnect?",
            "Como configurar BGP para FastConnect?",
            "Como debugar problemas de roteamento na VCN?",
            "Como configurar connectivity para hybrid cloud?",
            "Como usar Network Path Check para diagnosticar problemas?",
            "Como configurar múltiplas VPNs para alta disponibilidade?",
            "Como configurar Private Access para serviços OCI?",
            "Como resolver DNS em ambiente hybrid?",
            "Como configurar connectivity para disaster recovery?",
        ],
        "lb/load-balancer": [
            "Como criar um Load Balancer no OCI?",
            "Como configurar backend sets e listeners?",
            "Como configurar SSL/TLS no Load Balancer?",
            "Como configurar health checks para backends?",
            "Como configurar Load Balancer flexível (auto-scaling)?",
            "Como configurar path-based routing?",
            "Como configurar session persistence?",
            "Como resolver 502 Bad Gateway no Load Balancer?",
            "Como configurar Load Balancer privado?",
            "Como monitorar métricas do Load Balancer?",
            "Como configurar SSL certificate management?",
            "Como configurar rule sets para redirect HTTP→HTTPS?",
            "Como fazer blue-green deployment com Load Balancer?",
            "Como configurar Load Balancer para gRPC?",
            "Como migrar de Network Load Balancer para Application Load Balancer?",
        ],
        "database/autonomous": [
            "Como criar um Autonomous Database no OCI?",
            "Como conectar ao Autonomous Database com wallet?",
            "Como configurar Autonomous JSON Database?",
            "Como fazer backup e restore do Autonomous Database?",
            "Como escalar OCPUs e storage do Autonomous Database?",
            "Como configurar Autonomous Data Guard (DR)?",
            "Como migrar Oracle on-premises para Autonomous Database?",
            "Como configurar Oracle Machine Learning no Autonomous?",
            "Como usar APEX com Autonomous Database?",
            "Como configurar cross-region replication?",
            "Como monitorar performance do Autonomous Database?",
            "Como configurar networking (public vs private endpoint)?",
            "Como usar Database Actions (SQL Developer Web)?",
            "Como configurar auto-scaling do Autonomous Database?",
            "Como resolver erros de conexão com wallet?",
        ],
        "database/mysql": [
            "Como criar um MySQL HeatWave no OCI?",
            "Como configurar MySQL HeatWave para analytics?",
            "Como fazer backup do MySQL HeatWave?",
            "Como configurar replication no MySQL?",
            "Como migrar MySQL on-premises para OCI?",
            "Como escalar MySQL HeatWave horizontalmente?",
            "Como configurar high availability para MySQL?",
            "Como monitorar performance do MySQL HeatWave?",
            "Como configurar MySQL com Terraform?",
            "Como resolver erros de conexão ao MySQL?",
            "Como configurar MySQL Database Service com private endpoint?",
            "Como fazer point-in-time recovery no MySQL?",
            "Como migrar de MySQL RDS para OCI MySQL?",
            "Como configurar MySQL shell para administração?",
            "Como usar MySQL HeatWave para machine learning?",
        ],
        "database/postgresql": [
            "Como criar um PostgreSQL no OCI?",
            "Como configurar high availability para PostgreSQL?",
            "Como fazer backup e restore do PostgreSQL OCI?",
            "Como escalar PostgreSQL no OCI?",
            "Como migrar PostgreSQL on-premises para OCI?",
            "Como configurar read replicas para PostgreSQL?",
            "Como monitorar performance do PostgreSQL OCI?",
            "Como configurar PostgreSQL com Terraform?",
            "Como resolver erros de conexão ao PostgreSQL?",
            "Como configurar PostgreSQL extensions no OCI?",
            "Como fazer upgrade de versão do PostgreSQL?",
            "Como configurar PostgreSQL private endpoint?",
            "Como migrar de RDS PostgreSQL para OCI?",
            "Como configurar logical replication no PostgreSQL OCI?",
            "Como otimizar queries no PostgreSQL OCI?",
        ],
        "database/nosql": [
            "Como criar uma tabela no Oracle NoSQL Database?",
            "Como configurar TTL (time-to-live) no NoSQL?",
            "Como fazer CRUD operations no Oracle NoSQL?",
            "Como configurar consistência no NoSQL Database?",
            "Como escalar o Oracle NoSQL Database?",
            "Como migrar DynamoDB para Oracle NoSQL?",
            "Como monitorar performance do NoSQL Database?",
            "Como configurar backups do NoSQL Database?",
            "Como usar NoSQL Database com aplicações Python?",
            "Como configurar NoSQL Database com Terraform?",
            "Como modelar dados no Oracle NoSQL?",
            "Como configurar indexes no NoSQL Database?",
            "Como resolver erros de throughput no NoSQL?",
            "Como usar NoSQL Database com serverless?",
            "Como comparar Oracle NoSQL com MongoDB?",
        ],
        "database/autonomous-json": [
            "Como criar uma Autonomous JSON Database no OCI?",
            "Como armazenar documentos JSON no Autonomous Database?",
            "Como conectar aplicações Node.js ao JSON Database?",
            "Como migrar MongoDB para Autonomous JSON Database?",
            "Como fazer queries em coleções JSON?",
            "Como configurar indexes para documentos JSON?",
            "Como usar SODA (Simple Oracle Document Access)?",
            "Como configurar Autonomous JSON com APEX?",
            "Como escalar JSON Database automaticamente?",
            "Como fazer backup de coleções JSON?",
            "Como validar schemas JSON no Autonomous Database?",
            "Como comparar JSON Database com MongoDB Atlas?",
            "Como configurar MongoDB compatibility mode?",
            "Como otimizar performance de queries JSON?",
            "Como usar JSON Database com microservices?",
        ],
        "database/exadata": [
            "Como provisionar Exadata Cloud Service no OCI?",
            "Como configurar Exadata Cloud@Customer?",
            "Como fazer patching do Exadata Cloud Service?",
            "Como migrar Oracle on-premises para Exadata Cloud?",
            "Como configurar Exadata Smart Scan?",
            "Como monitorar performance do Exadata?",
            "Como configurar backup do Exadata Cloud?",
            "Como usar Exadata com Data Guard?",
            "Como fazer scaling do Exadata Cloud?",
            "Como configurar networking para Exadata Cloud?",
            "Como comparar Exadata Cloud vs Autonomous Database?",
            "Como configurar RAC no Exadata Cloud?",
            "Como resolver problemas de performance no Exadata?",
            "Como configurar Exadata para SAP?",
            "Como gerenciar maintenance windows do Exadata?",
        ],
        "container/oke": [
            "Como criar um cluster OKE no OCI?",
            "Como configurar node pools no OKE?",
            "Como conectar ao OKE com kubectl?",
            "Como configurar Load Balancer para serviços OKE?",
            "Como configurar auto-scaling de pods no OKE?",
            "Como configurar persistent volumes no OKE?",
            "Como usar OCI Registry (OCIR) com OKE?",
            "Como configurar networking (Flannel vs NPN) no OKE?",
            "Como fazer upgrade de versão do Kubernetes no OKE?",
            "Como configurar RBAC no OKE?",
            "Como monitorar OKE com OCI Monitoring?",
            "Como configurar OKE com private nodes?",
            "Como usar Helm charts com OKE?",
            "Como configurar OKE para workloads GPU?",
            "Como fazer backup de workloads OKE?",
        ],
        "container/instances": [
            "Como criar uma Container Instance no OCI?",
            "Como configurar Container Registry (OCIR)?",
            "Como fazer push de imagens para OCIR?",
            "Como configurar Container Instance com variáveis de ambiente?",
            "Como configurar networking para Container Instances?",
            "Como usar Container Instances como alternativa ao OKE?",
            "Como configurar Container Instance com volumes?",
            "Como monitorar Container Instances?",
            "Como configurar auto-scaling para Container Instances?",
            "Como migrar Docker Compose para Container Instances?",
            "Como configurar Container Instance com secrets?",
            "Como usar Container Instances com OCI Functions?",
            "Como configurar logging para Container Instances?",
            "Como resolver erros de pull de imagem no OCIR?",
            "Como configurar Container Instance para workloads batch?",
        ],
        "serverless/functions": [
            "Como criar uma Function no OCI?",
            "Como configurar Fn Project para OCI Functions?",
            "Como invocar OCI Functions via API?",
            "Como configurar OCI Functions com Python?",
            "Como configurar OCI Functions com Node.js?",
            "Como configurar OCI Functions com Java?",
            "Como monitorar OCI Functions?",
            "Como configurar OCI Functions com eventos?",
            "Como resolver timeout em OCI Functions?",
            "Como configurar OCI Functions com VCN private?",
            "Como usar OCI Functions como webhooks?",
            "Como configurar OCI Functions com Object Storage triggers?",
            "Como otimizar cold start em OCI Functions?",
            "Como configurar OCI Functions com API Gateway?",
            "Como fazer deployment automatizado de Functions?",
        ],
        "serverless/api-gateway": [
            "Como criar um API Gateway no OCI?",
            "Como configurar routes no API Gateway?",
            "Como configurar autenticação no API Gateway?",
            "Como configurar rate limiting no API Gateway?",
            "Como configurar CORS no API Gateway?",
            "Como integrar API Gateway com OCI Functions?",
            "Como configurar API Gateway com backend HTTP?",
            "Como monitorar métricas do API Gateway?",
            "Como configurar API Gateway privado?",
            "Como configurar versionamento de APIs?",
            "Como configurar API Gateway com OAuth?",
            "Como migrar API Gateway de outro cloud para OCI?",
            "Como configurar request/response transformations?",
            "Como configurar API Gateway com mutual TLS?",
            "Como resolver 502/504 errors no API Gateway?",
        ],
        "security/iam-basics": [
            "Como criar usuários e grupos no OCI IAM?",
            "Como configurar MFA para usuários OCI?",
            "Como organizar recursos com Compartments?",
            "Como criar e gerenciar API keys?",
            "Como configurar auth tokens para OCI CLI?",
            "Como migrar usuários entre compartments?",
            "Como configurar IAM para multi-tenancy?",
            "Como auditar acesso de usuários no OCI?",
            "Como configurar Console domain customizado?",
            "Como desabilitar usuários sem remover permissões?",
            "Como configurar IAM Identity Domains?",
            "Como gerenciar lifecycle de usuários IAM?",
            "Como configurar break-glass accounts?",
            "Como configurar SSO para OCI Console?",
            "Como resolver erros de acesso denied?",
        ],
        "security/policies": [
            "Como criar uma IAM Policy no OCI?",
            "Como escrever policy statements corretamente?",
            "Qual a diferença entre policy no compartment vs tenancy?",
            "Como dar acesso de leitura a um compartment?",
            "Como dar acesso de administração a um compartment?",
            "Como configurar cross-compartment policies?",
            "Como debugar políticas que não funcionam?",
            "Como configurar least privilege com policies?",
            "Como usar condições em policy statements?",
            "Como criar policies para grupos específicos?",
            "Como configurar policies para Object Storage granular?",
            "Como auditar e revisar políticas existentes?",
            "Como configurar policies para multi-region?",
            "Como criar policies para serviços gerenciados?",
            "Como resolver 'not authorized' errors?",
        ],
        "security/dynamic-groups": [
            "Como criar um Dynamic Group no OCI?",
            "Como configurar instance principal com Dynamic Groups?",
            "Como usar resource principal com Dynamic Groups?",
            "Como criar regras de matching para Dynamic Groups?",
            "Como configurar Dynamic Groups para OKE?",
            "Como configurar Dynamic Groups para Functions?",
            "Como debugar Dynamic Groups que não funcionam?",
            "Como usar Dynamic Groups para acesso cross-compartment?",
            "Como configurar Dynamic Groups com tags?",
            "Como migrar de user credentials para instance principal?",
            "Como configurar Dynamic Groups para Terraform?",
            "Como auditar Dynamic Groups existentes?",
            "Como configurar Dynamic Groups para CI/CD pipelines?",
            "Como usar matching rules com ALL/ANY?",
            "Como resolver erros de resource principal?",
        ],
        "security/federation": [
            "Como configurar SAML federation com OCI?",
            "Como integrar Okta com OCI IAM?",
            "Como configurar OAuth para aplicações OCI?",
            "Como configurar Azure AD federation com OCI?",
            "Como configurar Google Workspace federation?",
            "Como configurar SSO com ADFS?",
            "Como resolver erros de SAML assertion?",
            "Como configurar SCIM para provisioning automático?",
            "Como configurar Identity Domains no OCI?",
            "Como migrar de IAM clássico para Identity Domains?",
            "Como configurar MFA com federation?",
            "Como configurar session timeout para federation?",
            "Como debugar problemas de SSO?",
            "Como configurar trusted identity providers?",
            "Como configurar attribute mapping para SAML?",
        ],
        "security/vault-secrets": [
            "Como criar um Vault no OCI?",
            "Como criar e gerenciar secrets no OCI Vault?",
            "Como rotacionar secrets automaticamente?",
            "Como acessar secrets de uma instância OCI?",
            "Como integrar Vault com OCI Functions?",
            "Como configurar Vault com Terraform?",
            "Como resolver erros de acesso ao Vault?",
            "Como auditar acesso a secrets?",
            "Como configurar Vault em múltiplas regiões?",
            "Como migrar secrets de outro gerenciador para OCI Vault?",
            "Como usar secrets com Kubernetes/OKE?",
            "Como configurar Vault com BYOK?",
            "Como versionar secrets no OCI Vault?",
            "Como configurar políticas de acesso ao Vault?",
            "Como fazer backup de secrets?",
        ],
        "security/vault-keys": [
            "Como criar encryption keys no OCI Vault?",
            "Como configurar BYOK (Bring Your Own Key)?",
            "Como importar keys externas para o OCI Vault?",
            "Como rotacionar encryption keys?",
            "Como configurar key policies e acesso?",
            "Como usar keys para encrypt/decrypt via API?",
            "Como configurar HSM para OCI Vault?",
            "Como resolver erros de key access?",
            "Como auditar uso de encryption keys?",
            "Como configurar key versioning?",
            "Como configurar Vault para compliance?",
            "Como comparar software vs HSM keys?",
            "Como configurar cross-region key replication?",
            "Como desativar e agendar deleção de keys?",
            "Como usar keys com Object Storage encryption?",
        ],
        "security/encryption": [
            "Como configurar encryption at rest no OCI?",
            "Como configurar encryption in transit?",
            "Como usar customer-managed keys (BYOK)?",
            "Como configurar encryption para Block Volumes?",
            "Como configurar encryption para Object Storage?",
            "Como configurar encryption para databases?",
            "Como auditar configurações de encryption?",
            "Como configurar envelope encryption?",
            "Como migrar de Oracle-managed para customer-managed keys?",
            "Como configurar encryption para backups?",
            "Como resolver problemas de encryption?",
            "Como configurar compliance de encryption?",
            "Como usar OCI Vault com aplicações customizadas?",
            "Como configurar encryption para File Storage?",
            "Como verificar se dados estão encryptados?",
        ],
        "security/cloud-guard": [
            "Como configurar Cloud Guard no OCI?",
            "Como configurar detector recipes?",
            "Como configurar responder rules?",
            "Como resolver security findings do Cloud Guard?",
            "Como configurar Cloud Guard para múltiplos compartments?",
            "Como criar custom detector recipes?",
            "Como integrar Cloud Guard com OCI Logging?",
            "Como configurar auto-remediation com Cloud Guard?",
            "Como monitorar compliance com Cloud Guard?",
            "Como configurar Cloud Guard para CIS benchmarks?",
            "Como resolver falsos positivos no Cloud Guard?",
            "Como configurar alertas para Cloud Guard findings?",
            "Como usar Cloud Guard para auditoria contínua?",
            "Como configurar Cloud Guard para workloads específicos?",
            "Como exportar findings do Cloud Guard?",
        ],
        "security/waf": [
            "Como configurar Web Application Firewall no OCI?",
            "Como configurar access rules no WAF?",
            "Como configurar rate limiting no WAF?",
            "Como configurar protection patterns no WAF?",
            "Como configurar WAF com Load Balancer?",
            "Como configurar WAF para APIs?",
            "Como configurar bot management no WAF?",
            "Como resolver falsos positivos no WAF?",
            "Como monitorar métricas do WAF?",
            "Como configurar WAF com custom domains?",
            "Como configurar WAF para proteger contra SQL injection?",
            "Como configurar WAF para proteger contra XSS?",
            "Como configurar WAF com Origin Shield?",
            "Como migrar de outro WAF para OCI WAF?",
            "Como configurar WAF logging e análise?",
        ],
        "migration/aws-compute": [
            "Como migrar EC2 para OCI Compute?",
            "Como mapear AWS shapes para OCI shapes?",
            "Como usar OCI Application Migration Service?",
            "Como migrar auto-scaling groups para OCI?",
            "Como migrar EC2 com custom images?",
            "Como resolver incompatibilidades de OS na migração?",
            "Como migrar workloads Windows do AWS para OCI?",
            "Como planejar cutover de EC2 para OCI?",
            "Como migrar security groups para Security Lists?",
            "Como migrar IAM roles para OCI Dynamic Groups?",
            "Como comparar custos AWS vs OCI Compute?",
            "Como migrar Elastic IPs para OCI public IPs?",
            "Como migrar EBS volumes para OCI Block Volumes?",
            "Como validar migração de EC2 para OCI?",
            "Como migrar instâncias com data replication?",
        ],
        "migration/aws-storage": [
            "Como migrar S3 para OCI Object Storage?",
            "Como usar OCI Migration Service para S3?",
            "Como migrar EBS para OCI Block Volumes?",
            "Como usar rclone para migrar S3 para OCI?",
            "Como migrar EFS para OCI File Storage?",
            "Como migrar dados com OCI Data Transfer (offline)?",
            "Como configurar replicação S3 → OCI durante migração?",
            "Como migrar S3 lifecycle policies?",
            "Como validar integridade após migração de storage?",
            "Como migrar S3 Pre-Signed URLs para OCI PARs?",
            "Como migrar Glacier para OCI Archive Storage?",
            "Como configurar S3-compatible API no OCI?",
            "Como migrar grandes volumes de dados (>10TB)?",
            "Como minimizar downtime na migração de storage?",
            "Como comparar custos S3 vs OCI Object Storage?",
        ],
        "migration/aws-database": [
            "Como migrar RDS MySQL para OCI MySQL HeatWave?",
            "Como migrar RDS PostgreSQL para OCI PostgreSQL?",
            "Como migrar RDS Oracle para Autonomous Database?",
            "Como usar OCI Database Migration Service?",
            "Como migrar DynamoDB para Oracle NoSQL?",
            "Como migrar ElastiCache para OCI?",
            "Como configurar GoldenGate para migração de database?",
            "Como validar dados após migração de database?",
            "Como migrar database com mínimo downtime?",
            "Como migrar database schemas e stored procedures?",
            "Como resolver incompatibilidades de versão na migração?",
            "Como migrar backups de RDS para OCI?",
            "Como configurar replication durante migração?",
            "Como migrar database connections e endpoints?",
            "Como comparar custos RDS vs OCI Database?",
        ],
        "migration/azure-compute": [
            "Como migrar Azure VMs para OCI Compute?",
            "Como mapear Azure VM sizes para OCI shapes?",
            "Como migrar Azure Availability Sets para OCI?",
            "Como migrar Azure Managed Disks para OCI Block Volumes?",
            "Como migrar Azure Virtual Networks para OCI VCNs?",
            "Como migrar workloads Windows do Azure para OCI?",
            "Como migrar Azure Scale Sets para OCI Instance Pools?",
            "Como planejar cutover de Azure para OCI?",
            "Como migrar Azure NSGs para OCI Security Lists?",
            "Como migrar Azure AD integration para OCI IAM?",
            "Como comparar custos Azure vs OCI Compute?",
            "Como migrar Azure Resource Manager templates para Terraform?",
            "Como migrar Azure VMs com custom images?",
            "Como validar migração de Azure para OCI?",
            "Como migrar Azure Load Balancer para OCI LB?",
        ],
        "migration/azure-storage": [
            "Como migrar Azure Blob Storage para OCI Object Storage?",
            "Como usar AzCopy equivalente no OCI?",
            "Como migrar Azure Files para OCI File Storage?",
            "Como migrar Azure Disk Storage para OCI Block Volumes?",
            "Como migrar Azure Storage lifecycle policies?",
            "Como migrar Azure Archive Storage para OCI Archive?",
            "Como configurar replicação Azure → OCI durante migração?",
            "Como validar integridade após migração de storage?",
            "Como migrar grandes volumes de dados do Azure?",
            "Como migrar Azure SAS tokens para OCI PARs?",
            "Como minimizar downtime na migração de storage Azure?",
            "Como comparar custos Azure Storage vs OCI?",
            "Como migrar Azure Table Storage para OCI NoSQL?",
            "Como migrar Azure Queue Storage para OCI Streaming?",
            "Como migrar Azure Storage accounts entre subscriptions?",
        ],
        "migration/azure-database": [
            "Como migrar Azure SQL para Autonomous Database?",
            "Como migrar Azure Database for MySQL para OCI MySQL?",
            "Como migrar Azure Database for PostgreSQL para OCI PostgreSQL?",
            "Como usar Database Migration Service do OCI para Azure?",
            "Como migrar Azure Cosmos DB para Oracle NoSQL?",
            "Como migrar Azure Cache for Redis para OCI?",
            "Como configurar GoldenGate para migração Azure → OCI?",
            "Como validar dados após migração de database Azure?",
            "Como migrar database Azure com mínimo downtime?",
            "Como migrar stored procedures do SQL Server?",
            "Como resolver incompatibilidades T-SQL vs Oracle SQL?",
            "Como migrar backups de Azure database para OCI?",
            "Como configurar replication durante migração Azure?",
            "Como migrar database connections e connection strings?",
            "Como comparar custos Azure SQL vs Autonomous Database?",
        ],
        "migration/gcp-compute": [
            "Como migrar GCP Compute Engine para OCI Compute?",
            "Como mapear GCP machine types para OCI shapes?",
            "Como migrar GCP Managed Instance Groups para OCI?",
            "Como migrar GCP Persistent Disks para OCI Block Volumes?",
            "Como migrar GCP VPC para OCI VCN?",
            "Como migrar workloads Windows do GCP para OCI?",
            "Como planejar cutover de GCP para OCI?",
            "Como migrar GCP firewall rules para OCI Security Lists?",
            "Como migrar GCP service accounts para OCI Dynamic Groups?",
            "Como comparar custos GCP vs OCI Compute?",
            "Como migrar GCP Deployment Manager para Terraform?",
            "Como migrar GCP custom images para OCI?",
            "Como validar migração de GCP para OCI?",
            "Como migrar GCP Cloud Load Balancing para OCI LB?",
            "Como migrar GCP preemptible VMs para OCI spot?",
        ],
        "migration/gcp-storage": [
            "Como migrar GCP Cloud Storage para OCI Object Storage?",
            "Como migrar gsutil para OCI CLI?",
            "Como migrar GCP Filestore para OCI File Storage?",
            "Como migrar GCP Persistent Disks para OCI Block Volumes?",
            "Como migrar GCP Storage lifecycle policies?",
            "Como migrar GCP Coldline para OCI Archive?",
            "Como configurar replicação GCP → OCI durante migração?",
            "Como validar integridade após migração de storage GCP?",
            "Como migrar grandes volumes de dados do GCP?",
            "Como migrar GCP Signed URLs para OCI PARs?",
            "Como minimizar downtime na migração de storage GCP?",
            "Como comparar custos GCP Storage vs OCI?",
            "Como usar OCI Migration Service para GCP Storage?",
            "Como migrar GCP Nearline para OCI Infrequent Access?",
            "Como migrar GCP Storage buckets entre projects?",
        ],
        "migration/gcp-database": [
            "Como migrar GCP Cloud SQL MySQL para OCI MySQL?",
            "Como migrar GCP Cloud SQL PostgreSQL para OCI PostgreSQL?",
            "Como migrar GCP Spanner para OCI?",
            "Como migrar GCP Firestore para Oracle NoSQL?",
            "Como migrar GCP Memorystore para OCI?",
            "Como usar Database Migration Service para GCP?",
            "Como configurar GoldenGate para migração GCP → OCI?",
            "Como validar dados após migração de database GCP?",
            "Como migrar database GCP com mínimo downtime?",
            "Como resolver incompatibilidades de database na migração?",
            "Como migrar backups de GCP database para OCI?",
            "Como configurar replication durante migração GCP?",
            "Como migrar database connections e endpoints GCP?",
            "Como comparar custos GCP Cloud SQL vs OCI Database?",
            "Como migrar BigQuery para OCI?",
        ],
        "migration/onprem-compute": [
            "Como migrar VMs VMware on-premises para OCI Compute?",
            "Como fazer lift-and-shift de servidores físicos para OCI?",
            "Como avaliar workloads para migração on-premises → OCI?",
            "Como planejar cutover de migração on-premises?",
            "Como migrar servidores Windows on-premises para OCI?",
            "Como migrar servidores Linux on-premises para OCI?",
            "Como usar OCI Application Migration para on-premises?",
            "Como converter imagens VMWare (VMDK) para OCI?",
            "Como converter imagens Hyper-V (VHDX) para OCI?",
            "Como migrar clusters on-premises para OKE?",
            "Como planejar capacidade para migração on-premises?",
            "Como validar migração on-premises para OCI?",
            "Como migrar aplicações legacy para OCI?",
            "Como configurar hybrid cloud durante migração?",
            "Como fazer rollback de migração on-premises?",
        ],
        "migration/onprem-storage": [
            "Como migrar NFS on-premises para OCI File Storage?",
            "Como migrar SAN/NAS on-premises para OCI Block Volumes?",
            "Como usar OCI Data Transfer para grandes volumes?",
            "Como migrar arquivos on-premises para OCI Object Storage?",
            "Como configurar rsync para migração de dados?",
            "Como migrar backups on-premises para OCI?",
            "Como configurar FastConnect para migração de dados?",
            "Como validar integridade após migração de storage?",
            "Como migrar storage com mínimo downtime?",
            "Como usar Object Storage Gateway para migração híbrida?",
            "Como migrar tape archives para OCI Archive Storage?",
            "Como configurar replicação durante migração?",
            "Como migrar databases com storage on-premises?",
            "Como comparar custos storage on-premises vs OCI?",
            "Como migrar storage para disaster recovery?",
        ],
        "migration/onprem-vmware": [
            "Como migrar VMware vSphere para OCI?",
            "Como configurar VMware Cloud Foundation no OCI?",
            "Como usar HCX para migração VMware → OCI?",
            "Como configurar FastConnect para VMware Cloud?",
            "Como planejar migração VMware com mínimo downtime?",
            "Como migrar VMs VMware individualmente para OCI Compute?",
            "Como converter VMDK para OCI custom images?",
            "Como configurar networking para VMware Cloud OCI?",
            "Como migrar vSAN para OCI Block Volumes?",
            "Como configurar NSX-T para VMware Cloud OCI?",
            "Como resolver problemas de compatibilidade VMware → OCI?",
            "Como validar migração VMware para OCI?",
            "Como configurar backup para VMware Cloud OCI?",
            "Como migrar vCenter management para OCI?",
            "Como comparar custos VMware on-premises vs OCI?",
        ],
        "migration/onprem-database": [
            "Como migrar Oracle on-premises para Autonomous Database?",
            "Como usar Zero Downtime Migration (ZDM)?",
            "Como usar Data Pump para migração de database?",
            "Como migrar SQL Server para Autonomous Database?",
            "Como migrar MySQL on-premises para OCI MySQL?",
            "Como migrar PostgreSQL on-premises para OCI PostgreSQL?",
            "Como configurar GoldenGate para migração de database?",
            "Como validar dados após migração de database?",
            "Como resolver incompatibilidades de versão Oracle?",
            "Como migrar database com mínimo downtime?",
            "Como migrar stored procedures e triggers?",
            "Como migrar backups de database on-premises?",
            "Como configurar replication durante migração?",
            "Como migrar database connections e TNS names?",
            "Como comparar custos Oracle on-prem vs Autonomous?",
        ],
        "migration/data-transfer": [
            "Como usar GoldenGate para replicação de dados?",
            "Como usar OCI Data Integration para ETL?",
            "Como transferir grandes volumes de dados para OCI?",
            "Como usar OCI Data Transfer Service (offline)?",
            "Como configurar replication em tempo real com GoldenGate?",
            "Como migrar dados entre regiões OCI?",
            "Como configurar OCI Streaming para data pipelines?",
            "Como usar Object Storage para data lake?",
            "Como configurar Data Catalog para dados migrados?",
            "Como validar integridade de dados transferidos?",
            "Como otimizar transferência de dados com FastConnect?",
            "Como configurar monitoring para data transfer?",
            "Como usar OCI Data Flow para processamento Spark?",
            "Como configurar data pipelines com OCI Functions?",
            "Como resolver problemas de performance em data transfer?",
        ],
        "terraform/provider": [
            "Como configurar o provider OCI no Terraform?",
            "Como autenticar Terraform com API key?",
            "Como autenticar Terraform com instance principal?",
            "Como configurar múltiplas regiões no Terraform?",
            "Como configurar múltiplos compartments no Terraform?",
            "Como configurar Terraform variables para OCI?",
            "Como usar data sources no Terraform OCI?",
            "Como configurar provider version pinning?",
            "Como resolver erros de autenticação do Terraform?",
            "Como usar Terraform workspaces para multi-environment?",
            "Como configurar provider aliases para multi-region?",
            "Como debugar provider OCI do Terraform?",
            "Como configurar Terraform com OCI CLI config?",
            "Como usar Terraform modules para OCI?",
            "Como configurar Terraform para OCI Government Cloud?",
        ],
        "terraform/compute": [
            "Como criar instâncias OCI com Terraform?",
            "Como configurar Instance Pool com Terraform?",
            "Como configurar auto-scaling com Terraform?",
            "Como criar custom images com Terraform?",
            "Como configurar cloud-init com Terraform?",
            "Como criar múltiplas instâncias com count?",
            "Como criar instâncias com for_each?",
            "Como configurar block volume attachment com Terraform?",
            "Como configurar VNIC attachment com Terraform?",
            "Como criar Instance Configuration com Terraform?",
            "Como configurar dedicated hosts com Terraform?",
            "Como configurar capacity reservation com Terraform?",
            "Como criar instâncias GPU com Terraform?",
            "Como configurar Terraform para instâncias spot?",
            "Como gerenciar lifecycle de instâncias com Terraform?",
        ],
        "terraform/storage": [
            "Como criar Block Volumes com Terraform?",
            "Como criar Object Storage buckets com Terraform?",
            "Como criar File Storage com Terraform?",
            "Como configurar volume attachments com Terraform?",
            "Como configurar backup policies com Terraform?",
            "Como criar Object Storage lifecycle rules com Terraform?",
            "Como configurar versionamento de bucket com Terraform?",
            "Como criar Pre-Authenticated Requests com Terraform?",
            "Como configurar replication de bucket com Terraform?",
            "Como criar mount targets com Terraform?",
            "Como configurar export sets com Terraform?",
            "Como criar snapshots de Block Volume com Terraform?",
            "Como configurar encryption de storage com Terraform?",
            "Como criar Object Storage com S3 compatibility?",
            "Como gerenciar storage lifecycle com Terraform?",
        ],
        "terraform/networking": [
            "Como criar VCN com Terraform?",
            "Como criar subnets com Terraform?",
            "Como configurar Security Lists com Terraform?",
            "Como configurar NSGs com Terraform?",
            "Como criar Internet Gateway com Terraform?",
            "Como criar NAT Gateway com Terraform?",
            "Como criar Service Gateway com Terraform?",
            "Como configurar route tables com Terraform?",
            "Como configurar VCN peering com Terraform?",
            "Como criar DRG com Terraform?",
            "Como configurar VPN IPSec com Terraform?",
            "Como criar DHCP options com Terraform?",
            "Como configurar DNS com Terraform?",
            "Como criar Local Peering Gateway com Terraform?",
            "Como gerenciar networking lifecycle com Terraform?",
        ],
        "terraform/load-balancer": [
            "Como criar Load Balancer com Terraform?",
            "Como configurar backend sets com Terraform?",
            "Como configurar listeners com Terraform?",
            "Como configurar SSL certificates com Terraform?",
            "Como configurar health checks com Terraform?",
            "Como criar Network Load Balancer com Terraform?",
            "Como configurar path-based routing com Terraform?",
            "Como configurar session persistence com Terraform?",
            "Como criar Load Balancer flexível com Terraform?",
            "Como configurar rule sets com Terraform?",
            "Como configurar Load Balancer privado com Terraform?",
            "Como integrar LB com Instance Pool via Terraform?",
            "Como configurar hostname routing com Terraform?",
            "Como configurar Load Balancer policies com Terraform?",
            "Como gerenciar LB lifecycle com Terraform?",
        ],
        "terraform/database": [
            "Como criar Autonomous Database com Terraform?",
            "Como criar MySQL HeatWave com Terraform?",
            "Como criar PostgreSQL com Terraform?",
            "Como criar Oracle NoSQL com Terraform?",
            "Como configurar Database backup com Terraform?",
            "Como configurar Auto Scaling de database com Terraform?",
            "Como configurar Data Guard com Terraform?",
            "Como criar Exadata Cloud com Terraform?",
            "Como configurar wallet download com Terraform?",
            "Como configurar private endpoint para database com Terraform?",
            "Como criar database com Terraform e outputs de conexão?",
            "Como configurar database maintenance window com Terraform?",
            "Como criar read replicas com Terraform?",
            "Como configurar database encryption com Terraform?",
            "Como gerenciar database lifecycle com Terraform?",
        ],
        "terraform/container": [
            "Como criar cluster OKE com Terraform?",
            "Como configurar node pools com Terraform?",
            "Como criar Container Instances com Terraform?",
            "Como configurar OCIR com Terraform?",
            "Como configurar OKE networking com Terraform?",
            "Como configurar OKE com enhanced security?",
            "Como criar OKE com virtual nodes?",
            "Como configurar OKE addons com Terraform?",
            "Como configurar OKE auto-scaling com Terraform?",
            "Como criar OKE com private endpoint?",
            "Como configurar OKE persistent volumes com Terraform?",
            "Como configurar OKE load balancer com Terraform?",
            "Como criar OKE com KMS encryption?",
            "Como configurar OKE logging com Terraform?",
            "Como gerenciar OKE lifecycle com Terraform?",
        ],
        "terraform/serverless": [
            "Como criar OCI Functions com Terraform?",
            "Como criar API Gateway com Terraform?",
            "Como configurar Functions application com Terraform?",
            "Como configurar API Gateway routes com Terraform?",
            "Como configurar API Gateway authentication com Terraform?",
            "Como configurar Functions com VCN private?",
            "Como configurar API Gateway deployment com Terraform?",
            "Como configurar rate limiting com Terraform?",
            "Como configurar CORS com Terraform?",
            "Como criar API Gateway com custom domain?",
            "Como configurar Functions logging com Terraform?",
            "Como configurar API Gateway com request headers?",
            "Como integrar Functions com Object Storage via Terraform?",
            "Como configurar Functions com secrets via Terraform?",
            "Como gerenciar serverless lifecycle com Terraform?",
        ],
        "terraform/security": [
            "Como criar Vault com Terraform?",
            "Como criar secrets no Vault com Terraform?",
            "Como criar encryption keys com Terraform?",
            "Como configurar Cloud Guard com Terraform?",
            "Como configurar WAF com Terraform?",
            "Como criar Dynamic Groups com Terraform?",
            "Como criar IAM policies com Terraform?",
            "Como configurar Vault com HSM via Terraform?",
            "Como configurar encryption de resources com Terraform?",
            "Como criar compartments com Terraform?",
            "Como configurar IAM users e groups com Terraform?",
            "Como configurar Vault secret rotation com Terraform?",
            "Como configurar Cloud Guard detector recipes com Terraform?",
            "Como criar WAF policies com Terraform?",
            "Como gerenciar security lifecycle com Terraform?",
        ],
        "terraform/observability": [
            "Como configurar Logging com Terraform?",
            "Como configurar Monitoring alarms com Terraform?",
            "Como configurar Log Groups com Terraform?",
            "Como configurar Service Logs com Terraform?",
            "Como configurar Custom Logs com Terraform?",
            "Como configurar Notifications (ONS) com Terraform?",
            "Como configurar Dashboards com Terraform?",
            "Como configurar Service Connector Hub com Terraform?",
            "Como configurar APM com Terraform?",
            "Como configurar Stack Monitoring com Terraform?",
            "Como configurar alarm conditions com Terraform?",
            "Como configurar log retention com Terraform?",
            "Como integrar Logging com Object Storage via Terraform?",
            "Como configurar metric queries com Terraform?",
            "Como gerenciar observability lifecycle com Terraform?",
        ],
        "terraform/devops": [
            "Como criar DevOps project com Terraform?",
            "Como criar build pipeline com Terraform?",
            "Como criar deploy pipeline com Terraform?",
            "Como configurar DevOps artifacts com Terraform?",
            "Como configurar DevOps repositories com Terraform?",
            "Como integrar DevOps com OKE via Terraform?",
            "Como configurar DevOps triggers com Terraform?",
            "Como configurar DevOps environments com Terraform?",
            "Como criar Resource Manager stacks com Terraform?",
            "Como configurar DevOps connection com Terraform?",
            "Como configurar DevOps approvals com Terraform?",
            "Como integrar DevOps com Functions via Terraform?",
            "Como configurar DevOps notifications com Terraform?",
            "Como configurar DevOps secrets com Terraform?",
            "Como gerenciar DevOps lifecycle com Terraform?",
        ],
        "terraform/state": [
            "Como configurar remote state no OCI Object Storage?",
            "Como configurar state locking com OCI?",
            "Como configurar workspaces no Terraform OCI?",
            "Como migrar local state para remote state?",
            "Como configurar state backend com locking?",
            "Como resolver conflitos de state?",
            "Como importar resources existentes para o state?",
            "Como fazer state refactoring?",
            "Como configurar state versioning?",
            "Como proteger o state file?",
            "Como configurar state para multi-environment?",
            "Como debugar problemas de state?",
            "Como configurar state com encryption?",
            "Como fazer backup do state file?",
            "Como configurar state sharing entre equipes?",
        ],
        "observability/logging": [
            "Como criar log groups no OCI Logging?",
            "Como configurar service logs para VCN?",
            "Como configurar custom logs de aplicação?",
            "Como configurar audit logs no OCI?",
            "Como usar Log Explorer para buscar logs?",
            "Como configurar log retention policies?",
            "Como criar saved searches no Logging?",
            "Como configurar log parsing para extrair campos?",
            "Como integrar Logging com Object Storage?",
            "Como configurar log agent em instâncias?",
            "Como criar dashboards de logs?",
            "Como configurar alerts baseados em logs?",
            "Como exportar logs para ferramentas externas?",
            "Como configurar logging para OKE?",
            "Como resolver problemas de ingestão de logs?",
        ],
        "observability/monitoring": [
            "O que é OCI Monitoring e quais métricas estão disponíveis?",
            "Como configurar alarms de monitoring?",
            "Como configurar notificações para alarms?",
            "Como criar métricas customizadas?",
            "Como configurar monitoring para Block Volumes?",
            "Como configurar monitoring para Load Balancer?",
            "Como exportar métricas para Grafana?",
            "Como configurar dashboards de monitoring?",
            "Como configurar monitoring para databases?",
            "Como configurar Oracle Cloud Agent para métricas?",
            "Como configurar alarm thresholds recomendados?",
            "Como configurar monitoring para OKE?",
            "Como configurar monitoring multi-region?",
            "Como resolver problemas de métricas missing?",
            "Como configurar monitoring para Functions?",
        ],
        "observability/stack-monitoring": [
            "O que é Stack Monitoring no OCI?",
            "Como configurar Stack Monitoring para instâncias?",
            "Como configurar Stack Monitoring para databases?",
            "Como configurar Stack Monitoring para OKE?",
            "Como adicionar hosts externos ao Stack Monitoring?",
            "Como configurar monitoramento de middleware?",
            "Como configurar monitoramento de WebLogic?",
            "Como configurar monitoramento de Apache/Nginx?",
            "Como configurar monitoramento de MySQL?",
            "Como configurar monitoramento de Oracle Database?",
            "Como criar dashboards no Stack Monitoring?",
            "Como configurar alertas do Stack Monitoring?",
            "Como integrar Stack Monitoring com OCI Monitoring?",
            "Como resolver problemas de coleta de métricas?",
            "Como configurar Stack Monitoring para SAP?",
        ],
        "observability/apm": [
            "O que é APM no OCI?",
            "Como configurar APM Domains?",
            "Como instrumentar aplicações Java para APM?",
            "Como instrumentar aplicações Python para APM?",
            "Como instrumentar aplicações Node.js para APM?",
            "Como configurar distributed tracing?",
            "Como analisar traces no APM?",
            "Como configurar APM para microservices?",
            "Como configurar APM para APIs?",
            "Como configurar APM synthetics?",
            "Como integrar APM com OCI Logging?",
            "Como configurar APM alerts?",
            "Como usar APM para performance diagnostics?",
            "Como configurar APM para OKE?",
            "Como comparar APM com outras ferramentas?",
        ],
        "troubleshooting/connectivity": [
            "Não consigo acessar minha instância via SSH. Como diagnosticar?",
            "Minha instância não tem conectividade com internet. O que verificar?",
            "VPN IPSec não está estabelecendo. Como debugar?",
            "DNS não está resolvendo na VCN. Como resolver?",
            "FastConnect está com problemas. Como diagnosticar?",
            "VCN peering não está funcionando. O que verificar?",
            "Como usar Network Path Check para diagnosticar?",
            "Minha aplicação não está acessível externamente. O que fazer?",
            "Como diagnosticar problemas de roteamento na VCN?",
            "Como resolver problemas de NAT Gateway?",
            "Como diagnosticar problemas de Security Lists bloqueando tráfego?",
            "Como resolver problemas de connectivity entre ADs?",
            "Como diagnosticar problemas de DNS customizado?",
            "Como resolver problemas de connectivity para services OCI?",
            "Como diagnosticar problemas de load balancer connectivity?",
        ],
        "troubleshooting/performance": [
            "Minha instância está com CPU em 95%. Como diagnosticar?",
            "Estou tendo IOPS baixos no Block Volume. O que verificar?",
            "Minha aplicação está com latência alta. Como diagnosticar?",
            "Estou enfrentando API throttling. Como resolver?",
            "Como monitorar performance de OKE?",
            "Preciso otimizar performance do Autonomous Database. O que fazer?",
            "Meu servidor web está lento em picos. Como configurar auto-scaling?",
            "Como diagnosticar network latency entre ADs?",
            "Como resolver memory pressure em instâncias?",
            "Como diagnosticar storage bottlenecks?",
            "Como otimizar performance de Object Storage?",
            "Como resolver problemas de performance em Load Balancer?",
            "Como diagnosticar problemas de performance em OKE?",
            "Como otimizar queries lentas no MySQL HeatWave?",
            "Como resolver problemas de cold start em Functions?",
        ],
        "troubleshooting/authentication": [
            "Recebendo 'not authorized' ao acessar recursos. Como resolver?",
            "Minha policy IAM não está funcionando. Como debugar?",
            "MFA não está funcionando. Como resolver?",
            "API key não está autenticando. O que verificar?",
            "Dynamic Group não está funcionando. Como diagnosticar?",
            "Federation SSO não está funcionando. Como resolver?",
            "Instance principal não está autenticando. O que fazer?",
            "Resource principal não está funcionando. Como debugar?",
            "Auth token expirou. Como renovar?",
            "Como resolver erros de cross-compartment access?",
            "Como debugar problemas de SAML federation?",
            "Como resolver problemas de OAuth authentication?",
            "Como diagnosticar problemas de Vault access?",
            "Como resolver problemas de compartment access?",
            "Como debugar problemas de API signature?",
        ],
        "troubleshooting/database": [
            "Não consigo conectar ao Autonomous Database. Como resolver?",
            "Erro TNS: could not resolve connect identifier. O que fazer?",
            "Wallet do Autonomous Database não está funcionando. Como resolver?",
            "MySQL HeatWave não está iniciando. Como diagnosticar?",
            "PostgreSQL OCI está com conexões lentas. O que verificar?",
            "Como resolver erros de quota de database?",
            "Como diagnosticar problemas de replication de database?",
            "Como resolver problemas de backup de database?",
            "Como diagnosticar problemas de performance de database?",
            "Como resolver erros de conexão com private endpoint?",
            "Como diagnosticar problemas de Data Guard?",
            "Como resolver problemas de Exadata connectivity?",
            "Como diagnosticar problemas de NoSQL Database?",
            "Como resolver erros de maintenance window de database?",
            "Como diagnosticar problemas de Database Migration?",
        ],
        "troubleshooting/compute": [
            "Instância não está provisionando. Como diagnosticar?",
            "Instância não dá boot. O que verificar?",
            "SSH key não está funcionando. Como resolver?",
            "Instância está em estado 'STOPPED' e não inicia. O que fazer?",
            "Boot volume está corrompido. Como recuperar?",
            "Como recuperar acesso a instância sem SSH key?",
            "Instância está com problemas de cloud-init. Como debugar?",
            "Como diagnosticar problemas de VNIC em instâncias?",
            "Como resolver problemas de quota de compute?",
            "Como diagnosticar problemas de instance pool?",
            "Como resolver problemas de custom image?",
            "Como diagnosticar problemas de dedicated host?",
            "Como resolver problemas de capacity reservation?",
            "Como diagnosticar problemas de GPU instances?",
            "Como resolver problemas de instance lifecycle?",
        ],
        "troubleshooting/storage": [
            "Bucket Object Storage não está acessível. Como resolver?",
            "Upload para Object Storage está falhando. O que verificar?",
            "Block Volume está com I/O errors. Como recuperar dados?",
            "File Storage não está montando. Como diagnosticar?",
            "Replicação de bucket parou de funcionar. Como resolver?",
            "Como resolver problemas de permissão no Object Storage?",
            "Como diagnosticar problemas de performance de storage?",
            "Como resolver problemas de quota de storage?",
            "Como diagnosticar problemas de backup de storage?",
            "Como resolver problemas de versionamento de bucket?",
            "Como diagnosticar problemas de lifecycle policies?",
            "Como resolver problemas de PAR (Pre-Authenticated Requests)?",
            "Como diagnosticar problemas de encryption de storage?",
            "Como resolver problemas de Object Lock?",
            "Como diagnosticar problemas de File Storage export?",
        ],
        "troubleshooting/oke": [
            "Cluster OKE não está criando. Como diagnosticar?",
            "Node pool não está provisionando nodes. O que fazer?",
            "Worker nodes não estão registrados no cluster. Como resolver?",
            "Pods estão em CrashLoopBackOff. Como diagnosticar?",
            "Load Balancer do serviço OKE não está criando. Como resolver?",
            "Persistent Volume Claims não estão sendo bound. O que fazer?",
            "Como diagnosticar problemas de networking no OKE?",
            "Como resolver problemas de RBAC no OKE?",
            "Como diagnosticar problemas de upgrade de Kubernetes?",
            "Como resolver problemas de OKE com private nodes?",
            "Como diagnosticar problemas de OKE auto-scaling?",
            "Como resolver problemas de OCIR pull no OKE?",
            "Como diagnosticar problemas de OKE storage classes?",
            "Como resolver problemas de OKE ingress controller?",
            "Como diagnosticar problemas de OKE monitoring?",
        ],
        "troubleshooting/functions": [
            "Function não está invocando. Como diagnosticar?",
            "API Gateway retornando 502. Como resolver?",
            "API Gateway retornando 504 timeout. O que fazer?",
            "Function está com timeout. Como resolver?",
            "Function não está conseguindo acessar outros serviços OCI. O que verificar?",
            "Como diagnosticar problemas de cold start em Functions?",
            "Como resolver problemas de memória em Functions?",
            "Como diagnosticar problemas de logging em Functions?",
            "Como resolver problemas de deployment de Functions?",
            "Como diagnosticar problemas de VCN private com Functions?",
            "Como resolver problemas de autenticação em Functions?",
            "Como diagnosticar problemas de trigger de Functions?",
            "Como resolver problemas de concurrency em Functions?",
            "Como diagnosticar problemas de API Gateway CORS?",
            "Como resolver problemas de API Gateway rate limiting?",
        ],
        "devops/ci-cd": [
            "Como criar um build pipeline no OCI DevOps?",
            "Como criar um deploy pipeline no OCI DevOps?",
            "Como configurar triggers automáticos no DevOps?",
            "Como configurar artifacts entre build e deploy?",
            "Como configurar DevOps para deploy no OKE?",
            "Como configurar DevOps para deploy em instâncias?",
            "Como configurar DevOps para deploy de Functions?",
            "Como configurar aprovações no deploy pipeline?",
            "Como configurar DevOps com repositório GitHub?",
            "Como configurar DevOps com repositório GitLab?",
            "Como resolver falhas no build pipeline?",
            "Como configurar DevOps para blue-green deployment?",
            "Como configurar DevOps para canary deployment?",
            "Como monitorar pipelines do DevOps?",
            "Como configurar DevOps com Terraform?",
        ],
        "devops/resource-manager": [
            "Como criar stacks no Resource Manager?",
            "Como executar jobs no Resource Manager?",
            "Como configurar drift detection?",
            "Como configurar Resource Manager com Terraform?",
            "Como monitorar jobs do Resource Manager?",
            "Como configurar Resource Manager com DevOps?",
            "Como resolver falhas de jobs no Resource Manager?",
            "Como configurar variáveis de ambiente no Resource Manager?",
            "Como configurar Resource Manager para multi-environment?",
            "Como configurar Resource Manager com private endpoints?",
            "Como importar estado existente para Resource Manager?",
            "Como configurar Resource Manager schedules?",
            "Como configurar Resource Manager com modules?",
            "Como resolver conflitos de state no Resource Manager?",
            "Como configurar Resource Manager para equipes?",
        ],
        "devops/artifacts": [
            "Como criar repositórios no OCIR?",
            "Como fazer push de imagens Docker para OCIR?",
            "Como configurar DevOps artifacts?",
            "Como configurar image scanning no OCIR?",
            "Como configurar access policies para OCIR?",
            "Como configurar DevOps com Helm charts?",
            "Como configurar DevOps com generic artifacts?",
            "Como configurar OCIR com Terraform?",
            "Como migrar imagens de outro registry para OCIR?",
            "Como configurar OCIR com cross-region replication?",
            "Como configurar DevOps artifact management?",
            "Como configurar OCIR com KMS encryption?",
            "Como resolver problemas de pull de imagens do OCIR?",
            "Como configurar OCIR lifecycle policies?",
            "Como configurar DevOps com Maven artifacts?",
        ],
        "devops/secrets": [
            "Como configurar secrets no DevOps pipeline?",
            "Como usar Vault secrets em build pipelines?",
            "Como configurar parameter store no DevOps?",
            "Como configurar secret rotation automática?",
            "Como injetar secrets em deploy pipelines?",
            "Como configurar secrets para OKE deployments?",
            "Como configurar secrets para Functions deployments?",
            "Como auditar acesso a secrets no DevOps?",
            "Como configurar secrets multi-environment?",
            "Como resolver problemas de secrets expirados?",
            "Como configurar secrets com Terraform?",
            "Como configurar secrets para CI/CD externo?",
            "Como migrar secrets de outro gerenciador?",
            "Como configurar secrets para database credentials?",
            "Como configurar secrets para API keys?",
        ],
    }

    pool = questions_by_cat.get(cat, [f"Pergunta sobre {cat} - exemplo {idx + 1}?"])
    q = random.choice(pool)

    # Ensure uniqueness
    attempt = 0
    while q in existing_qs and attempt < 20:
        q = random.choice(pool)
        attempt += 1

    return q


if __name__ == "__main__":
    main()
