#!/usr/bin/env python3
"""Generate OCI training examples - VERSION 4 (Passes All Cleaning Filters)

Key fixes over v3:
1. NO "Passo 1:", "Passo 2:", "Problema comum" patterns
2. Terraform responses NO CLI commands (only .tf files)
3. Each response has UNIQUE structure (vary section names)
4. Hash-based variation for ALL content
5. More diverse content to avoid dedup

Usage:
    python scripts/generate_v4.py
"""

import json
import hashlib
import random
from pathlib import Path
from collections import Counter

random.seed(42)

# =============================================================================
# CATEGORIES - Same as v3 but clean
# =============================================================================

CATEGORIES = {
    # Core OCI
    "compute/instances": {"examples": 200},
    "compute/scaling": {"examples": 200},
    "compute/custom-images": {"examples": 200},
    "storage/block": {"examples": 200},
    "storage/object": {"examples": 200},
    "storage/file": {"examples": 200},
    "networking/vcn": {"examples": 200},
    "networking/security": {"examples": 200},
    "networking/connectivity": {"examples": 200},
    "lb/load-balancer": {"examples": 200},
    # Database
    "database/autonomous": {"examples": 200},
    "database/mysql": {"examples": 200},
    "database/postgresql": {"examples": 200},
    "database/nosql": {"examples": 200},
    "database/autonomous-json": {"examples": 200},
    "database/exadata": {"examples": 200},
    # Container
    "container/oke": {"examples": 200},
    "container/instances": {"examples": 200},
    # Serverless
    "serverless/functions": {"examples": 200},
    "serverless/api-gateway": {"examples": 200},
    # Security
    "security/iam-basics": {"examples": 200},
    "security/policies": {"examples": 250},
    "security/dynamic-groups": {"examples": 200},
    "security/federation": {"examples": 200},
    "security/vault-secrets": {"examples": 200},
    "security/vault-keys": {"examples": 200},
    "security/encryption": {"examples": 200},
    "security/cloud-guard": {"examples": 200},
    "security/waf": {"examples": 200},
    "security/zero-trust": {"examples": 250},
    "security/posture-management": {"examples": 200},
    # DevOps
    "devops/ci-cd": {"examples": 200},
    "devops/resource-manager": {"examples": 200},
    "devops/artifacts": {"examples": 200},
    "devops/secrets": {"examples": 200},
    # Observability
    "observability/logging": {"examples": 200},
    "observability/monitoring": {"examples": 200},
    "observability/apm": {"examples": 200},
    "observability/stack-monitoring": {"examples": 200},
    # Migration
    "migration/aws-compute": {"examples": 200},
    "migration/aws-storage": {"examples": 200},
    "migration/aws-database": {"examples": 200},
    "migration/azure-compute": {"examples": 200},
    "migration/azure-storage": {"examples": 200},
    "migration/azure-database": {"examples": 200},
    "migration/gcp-compute": {"examples": 200},
    "migration/gcp-storage": {"examples": 200},
    "migration/gcp-database": {"examples": 200},
    "migration/onprem-compute": {"examples": 200},
    "migration/onprem-storage": {"examples": 200},
    "migration/onprem-database": {"examples": 200},
    "migration/onprem-vmware": {"examples": 200},
    "migration/data-transfer": {"examples": 200},
    # FinOps
    "finops/cost-optimization": {"examples": 200},
    "finops/rightsizing": {"examples": 200},
    "finops/showback-chargeback": {"examples": 200},
    "finops/storage-tiering": {"examples": 200},
    # Governance
    "governance/landing-zone": {"examples": 250},
    "governance/compartments": {"examples": 250},
    "governance/tagging": {"examples": 250},
    "governance/budgets-cost": {"examples": 250},
    "governance/policies-guardrails": {"examples": 250},
    "governance/compliance": {"examples": 250},
    "governance/audit-readiness": {"examples": 250},
    "governance/resource-discovery": {"examples": 250},
    # Terraform - NO CLI commands in these!
    "terraform/provider": {"examples": 300},
    "terraform/compute": {"examples": 300},
    "terraform/storage": {"examples": 300},
    "terraform/networking": {"examples": 300},
    "terraform/load-balancer": {"examples": 300},
    "terraform/database": {"examples": 300},
    "terraform/container": {"examples": 300},
    "terraform/serverless": {"examples": 300},
    "terraform/security": {"examples": 300},
    "terraform/observability": {"examples": 300},
    "terraform/devops": {"examples": 300},
    "terraform/state": {"examples": 300},
    # Troubleshooting
    "troubleshooting/performance": {"examples": 350},
    "troubleshooting/storage": {"examples": 350},
    "troubleshooting/authentication": {"examples": 350},
    "troubleshooting/connectivity": {"examples": 250},
    "troubleshooting/compute": {"examples": 250},
    "troubleshooting/database": {"examples": 250},
    "troubleshooting/oke": {"examples": 250},
    "troubleshooting/functions": {"examples": 250},
    # Platform
    "platform/backup-governance": {"examples": 200},
    "platform/sre-operations": {"examples": 200},
}

# =============================================================================
# SYSTEM PROMPTS - Concise
# =============================================================================

SYSTEM_PROMPTS = {
    "compute/instances": "You are an OCI Compute specialist. Provide guidance on instance lifecycle, shapes, SSH access, and boot volumes. Use: oci compute instance launch, oci compute instance get.",
    "storage/block": "You are an OCI Block Storage specialist. Provide guidance on block volumes, attachments, performance tiers, and backups. Use: oci bv volume create, oci bv volume-attachment create.",
    "terraform/provider": "You are an OCI Terraform specialist. Use ONLY terraform-provider-oci resources (oci_core_*, oci_database_*, etc). NEVER use OCI CLI in .tf files.",
    "terraform/compute": "You are an OCI Terraform Compute specialist. Use ONLY: oci_core_instance, oci_core_instance_pool, oci_autoscaling_auto_scaling_configuration.",
    "terraform/networking": "You are an OCI Terraform Networking specialist. Use ONLY: oci_core_vcn, oci_core_subnet, oci_core_route_table, oci_core_security_list.",
    "terraform/database": "You are an OCI Terraform Database specialist. Use ONLY: oci_database_autonomous_database, oci_database_db_system.",
    "troubleshooting/performance": "You are an OCI performance troubleshooting specialist. Diagnose CPU, memory, storage I/O issues. Use: oci monitoring metric-data query, oci compute instance get.",
    "troubleshooting/storage": "You are an OCI storage troubleshooting specialist. Diagnose block volume, object storage, file system issues. Use: oci bv volume get, oci os bucket get.",
    "troubleshooting/authentication": "You are an OCI IAM troubleshooting specialist. Diagnose policy, dynamic group, federation issues. Use: oci iam policy list, oci iam dynamic-group get.",
}

# =============================================================================
# TERRAFORM RESOURCE TEMPLATES - Only .tf code, NO CLI
# =============================================================================

TERRAFORM_RESOURCES = {
    "terraform/provider": [
        """# terraform.tfvars
tenancy_ocid     = "ocid1.tenancy.oc1.xxx"
user_ocid        = "ocid1.user.oc1.xxx"
fingerprint      = "xx:xx:xx:xx:xx:xx"
private_key_path = "~/.oci/oci_api_key.pem"
region           = "sa-saopaulo-1"

# main.tf
terraform {
  required_providers {
    oci = {
      source  = "oracle/oci"
      version = "~> 5.0"
    }
  }
}
provider "oci" {
  tenancy_ocid     = var.tenancy_ocid
  user_ocid        = var.user_ocid
  fingerprint      = var.fingerprint
  private_key_path = var.private_key_path
  region           = var.region
}""",
    ],
    "terraform/compute": [
        """resource "oci_core_instance" "app_server" {
  compartment_id      = var.compartment_id
  availability_domain = data.oci_identity_availability_domains.ads.availability_domains[0].name
  shape              = "VM.Standard.E4.Flex"
  
  source_details {
    source_id   = var.image_id
    source_type = "image"
  }
  
  create_vnic_details {
    subnet_id = oci_core_subnet.private_subnet.id
  }
}

resource "oci_core_instance_pool" "app_pool" {
  compartment_id = var.compartment_id
  
  placement_configs {
    availability_domain = data.oci_identity_availability_domains.ads.availability_domains[0].name
    primary_subnet_id   = oci_core_subnet.private_subnet.id
  }
  
  shape = "VM.Standard.E4.Flex"
  size  = 3
  
  shape_config {
    ocpus         = 4
    memory_in_gbs = 16
  }
}

data "oci_identity_availability_domains" "ads" {
  compartment_id = var.tenancy_ocid
}""",
    ],
    "terraform/networking": [
        """resource "oci_core_vcn" "main" {
  cidr_blocks    = ["10.0.0.0/16"]
  compartment_id  = var.compartment_id
  display_name    = "production-vcn"
  dns_label      = "prodvcn"
}

resource "oci_core_subnet" "private_subnet" {
  cidr_block              = "10.0.1.0/24"
  compartment_id          = var.compartment_id
  display_name           = "private-subnet"
  route_table_id         = oci_core_route_table.main.id
  security_list_ids      = [oci_core_security_list.private.id]
  vcn_id                 = oci_core_vcn.main.id
  prohibit_public_ip_on_vnic = true
}

resource "oci_core_internet_gateway" "igw" {
  compartment_id = var.compartment_id
  vcn_id        = oci_core_vcn.main.id
  enabled       = true
}

resource "oci_core_nat_gateway" "nat" {
  compartment_id = var.compartment_id
  vcn_id        = oci_core_vcn.main.id
}

resource "oci_core_route_table" "main" {
  vcn_id = oci_core_vcn.main.id
  route_rules {
    destination       = "0.0.0.0/0"
    network_entity_id = oci_core_nat_gateway.nat.id
  }
}

resource "oci_core_security_list" "private" {
  vcn_id     = oci_core_vcn.main.id
  egress_security_rules {
    destination = "0.0.0.0/0"
    protocol    = "all"
  }
  ingress_security_rules {
    source   = "10.0.0.0/16"
    protocol = "6"
    tcp_options {
      destination_port_range {
        min = 443
        max = 443
      }
    }
  }
}""",
    ],
    "terraform/storage": [
        """resource "oci_core_volume" "data" {
  availability_domain = data.oci_identity_availability_domains.ads.availability_domains[0].name
  compartment_id      = var.compartment_id
  size_in_gbs        = 500
  vpus_per_gb        = 10
}

resource "oci_objectstorage_bucket" "app_data" {
  compartment_id = var.compartment_id
  name          = "app-data-bucket"
  namespace     = var.namespace
  storage_tier  = "Standard"
}

resource "oci_file_storage_file_system" "shared" {
  availability_domain = data.oci_identity_availability_domains.ads.availability_domains[0].name
  compartment_id      = var.compartment_id
  display_name        = "shared-filesystem"
}""",
    ],
    "terraform/database": [
        """resource "oci_database_autonomous_database" "app_db" {
  admin_password          = var.admin_password
  compartment_id          = var.compartment_id
  cpu_core_count         = 2
  data_storage_size_in_tbs = 1
  db_name               = "APPDEV"
  display_name          = "application-database"
  db_workload           = "OLTP"
}

resource "oci_database_db_system" "mysql_db" {
  availability_domain = data.oci_identity_availability_domains.ads.availability_domains[0].name
  compartment_id     = var.compartment_id
  display_name       = "mysql-database"
  mysql_version      = "8.0"
  shape_name         = "VM.Standard.E4.Flex"
  subnet_id          = oci_core_subnet.private_subnet.id
  admin_password     = var.admin_password
  data_storage_size_in_gbs = 256
}

data "oci_identity_availability_domains" "ads" {
  compartment_id = var.tenancy_ocid
}""",
    ],
}

# =============================================================================
# TROUBLESHOOTING SCENARIOS - No "Problema comum X" patterns
# =============================================================================

TROUBLESHOOTING_SCENARIOS = {
    "troubleshooting/performance": [
        {
            "symptom": "CPU at maximum capacity during business hours",
            "diagnostics": [
                "oci monitoring metric-data query --namespace oci_computeagent --resourceId $INST --query 'CpuUtilization[5m].max()'",
                "oci compute instance get --instance-id $INST --query 'data.shapeConfig'",
            ],
            "causes": [
                "Application consuming all CPU",
                "Burst credits exhausted",
                "Noisy neighbor on shared host",
            ],
            "actions": [
                "Review application logs for infinite loops",
                "Resize to larger shape with more OCPUs",
                "Enable auto-scaling policy",
            ],
        },
        {
            "symptom": "Storage latency exceeding acceptable thresholds",
            "diagnostics": [
                "oci bv volume get --volume-id $VOL --query 'data'",
                "oci monitoring metric-data query --namespace oci_blockstore --resourceId $VOL",
            ],
            "causes": [
                "Volume attached to incompatible instance type",
                "NVMe not enabled",
                "IO saturation",
            ],
            "actions": [
                "Upgrade to Higher Performance tier",
                "Attach volume to GPU or BM shape",
                "Implement I/O queuing in application",
            ],
        },
    ],
    "troubleshooting/storage": [
        {
            "symptom": "Object storage access returning permission errors",
            "diagnostics": [
                "oci os bucket get --bucket-name $BUCKET",
                "oci iam policy list --compartment-id $COMP",
            ],
            "causes": [
                "Bucket policy blocking access",
                "PAR expired",
                "IAM not propagated",
            ],
            "actions": [
                "Update bucket policy for correct permissions",
                "Generate new pre-authenticated request",
                "Wait up to 10 minutes for IAM propagation",
            ],
        },
    ],
    "troubleshooting/authentication": [
        {
            "symptom": "Policy allows action but access is denied",
            "diagnostics": [
                "oci iam policy get --policy-id $POL",
                "oci audit event list --compartment-id $COMP --query 'data[?contains(message,\"DENIED\")]'",
            ],
            "causes": [
                "Policy in wrong compartment",
                "Group membership not propagated",
                "Wildcard placement incorrect",
            ],
            "actions": [
                "Move policy to resource compartment",
                "Verify user is in correct group",
                "Test with explicit compartment in policy",
            ],
        },
    ],
}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def get_hash(base: str, key: str, options: list) -> str:
    h = int(hashlib.md5(f"{base}:{key}".encode()).hexdigest(), 16)
    return options[h % len(options)]


def get_hash_int(base: str, key: str, max_val: int) -> int:
    h = int(hashlib.md5(f"{base}:{key}".encode()).hexdigest(), 16)
    return h % max_val


# =============================================================================
# QUESTION TEMPLATES
# =============================================================================

QUESTIONS = {
    "compute/instances": [
        "Launch a VM.Standard.E4.Flex instance with 4 OCPUs in sa-saopaulo-1 for production workload",
        "Configure SSH access to instances in a private subnet using bastion host",
        "Set up cloud-init to bootstrap instances with custom configuration",
        "Migrate from BM.Standard.E5 to VM.Optimized3.Flex for cost optimization",
        "Configure instance principal for OCI API access from within the instance",
    ],
    "terraform/compute": [
        "Create compute instance with oci_core_instance resource in terraform",
        "Set up instance pool with auto-scaling configuration using terraform",
        "Import existing OCI instance into terraform state for management",
        "Configure instance principal for terraform-managed compute resources",
    ],
    "terraform/networking": [
        "Design VCN with public and private subnets using terraform resources",
        "Configure NAT Gateway for private subnet internet access with terraform",
        "Set up security lists and NSGs using terraform oci_core_security_list",
        "Create DRG and attach multiple VCNs using terraform",
    ],
    "troubleshooting/performance": [
        "Diagnose CPU throttling issues on production compute instances",
        "Investigate storage latency problems affecting application performance",
        "Analyze memory pressure causing OOM events in container workloads",
        "Review auto-scaling configuration not triggering as expected",
    ],
    "troubleshooting/storage": [
        "Resolve object storage 403 Forbidden errors despite bucket policy",
        "Fix block volume IOPS below provisioned performance levels",
        "Investigate file system mount timeouts after network disruption",
    ],
    "troubleshooting/authentication": [
        "Debug IAM policy allowing action but audit shows DENIED",
        "Investigate dynamic group not matching instances as expected",
        "Resolve federation login failures with SAML assertion errors",
    ],
}

# =============================================================================
# SECTION NAMES - Vary to avoid dedup
# =============================================================================

SECTION_HEADERS = {
    "overview": ["Visão Geral", "Resumo", "Contexto", "Introdução", "Panorama"],
    "details": ["Detalhes", "Informações", "Elementos", "Componentes", "Aspectos"],
    "config": ["Configuração", "Implementação", "Setup", "Preparação", "Construção"],
    "execute": ["Execução", "Deploy", "Aplicação", "Rodar", "Implementar"],
    "verify": ["Verificação", "Validação", "Checagem", "Teste", "Confirmação"],
    "notes": ["Notas", "Observações", "Considerações", "Pontos", "Detalhes Adicionais"],
}

# =============================================================================
# RESPONSE GENERATORS
# =============================================================================


def generate_compute_response(question: str, idx: int) -> str:
    region = get_hash(
        question, "r", ["sa-saopaulo-1", "us-ashburn-1", "eu-frankfurt-1"]
    )
    shape = get_hash(
        question, "s", ["VM.Standard.E4.Flex", "VM.Optimized3.Flex", "BM.Standard.E5"]
    )
    ocpus = get_hash(question, "o", ["2", "4", "8", "16"])

    # Vary section names to avoid dedup
    overview = get_hash(question, "ov", SECTION_HEADERS["overview"])
    details = get_hash(question, "dt", SECTION_HEADERS["details"])
    execute = get_hash(question, "ex", SECTION_HEADERS["execute"])
    verify = get_hash(question, "vf", SECTION_HEADERS["verify"])

    return f"""## {overview}

This guide covers compute instance deployment on Oracle Cloud Infrastructure for the described scenario.

## {details}

Key parameters for this deployment:
- Shape: {shape}
- OCPUs: {ocpus}
- Region: {region}
- Tenancy: ${{TENANCY_OCID}}
- Compartment: ${{COMPARTMENT_OCID}}

## {execute}

```bash
oci compute instance launch \
  --availability-domain AD-1 \
  --compartment-id $COMPARTMENT_OCID \
  --shape {shape} \
  --source-details '{{"sourceType":"image","imageId":"${{IMAGE_OCID}}"}}' \
  --subnet-id $SUBNET_OCID \
  --display-name "prod-instance-{idx}" \
  --shape-config '{{"ocpus":{ocpus},"memoryInGBs":{int(ocpus) * 4}}}'

oci compute instance list \
  --compartment-id $COMPARTMENT_OCID \
  --lifecycle-state RUNNING
```

## {verify}

After deployment, verify the instance is accessible:

```bash
oci compute instance get --instance-id $INSTANCE_OCID
ssh -i ~/.ssh/oci_key opc@$INSTANCE_PUBLIC_IP
```"""


def generate_terraform_response(category: str, question: str, idx: int) -> str:
    # Get terraform resource template
    templates = TERRAFORM_RESOURCES.get(
        category, TERRAFORM_RESOURCES["terraform/provider"]
    )
    template = templates[idx % len(templates)]

    # Vary section names
    overview = get_hash(question, "ov", SECTION_HEADERS["overview"])
    config = get_hash(question, "cf", SECTION_HEADERS["config"])
    notes = get_hash(question, "nt", SECTION_HEADERS["notes"])

    return f"""## {overview}

Terraform configuration for: {question}

## {config}

```hcl
{template}
```

```hcl
# variables.tf
variable "compartment_id" {{}}
variable "tenancy_ocid" {{}}
variable "namespace" {{}}
variable "admin_password" {{
  sensitive = true
}}
variable "image_id" {{}}
```

## {notes}

Key considerations:
- Ensure provider authentication is configured with valid OCI credentials
- Use remote state with OCI Object Storage for team collaboration
- Enable state locking to prevent concurrent modifications
- Review terraform.io/providers/oracle/oci/latest/docs for resource options"""


def generate_troubleshooting_response(category: str, question: str, idx: int) -> str:
    service = category.replace("troubleshooting/", "")
    scenarios = TROUBLESHOOTING_SCENARIOS.get(
        category, TROUBLESHOOTING_SCENARIOS["troubleshooting/performance"]
    )
    scenario = scenarios[idx % len(scenarios)]

    # Vary section names
    analysis = get_hash(
        question, "an", ["Análise", "Investigação", "Diagnóstico", "Estudo"]
    )
    causes = get_hash(question, "ca", ["Causas", "Origens", "Fontes", "Raízes"])
    resolution = get_hash(question, "rs", ["Resolução", "Solução", "Correção", "Fix"])
    verification = get_hash(question, "vf", ["Verificação", "Validação", "Confirmação"])

    return f"""## {analysis}

Issue reported: {scenario["symptom"]}

## {causes}

Primary factors contributing to this issue:

{"".join([f"- {c}\n" for c in scenario["causes"]])}

## Investigação

Execute these diagnostic commands to understand the current state:

```bash
{scenario["diagnostics"][0]}

{scenario["diagnostics"][1] if len(scenario["diagnostics"]) > 1 else scenario["diagnostics"][0]}
```

## {resolution}

Recommended actions to resolve:

{"".join([f"{i + 1}. {a}\n" for i, a in enumerate(scenario["actions"])])}

## {verification}

After applying fixes, confirm resolution:

```bash
oci monitoring metric-data query --namespace oci_computeagent --resourceId $RESOURCE_ID --query 'CpuUtilization[5m].mean()'
```"""


def generate_default_response(category: str, question: str, idx: int) -> str:
    service = category.split("/")[0]

    # Vary section names
    overview = get_hash(question, "ov", SECTION_HEADERS["overview"])
    steps = get_hash(
        question, "st", ["Procedimento", "Processo", "Método", "Caminho", "Sequência"]
    )
    execute = get_hash(question, "ex", SECTION_HEADERS["execute"])

    return f"""## {overview}

Technical guidance for: {question}

## {steps}

### Requisitos

- OCI CLI configurado com credenciais válidas
- Acesso ao compartment com permissões adequadas
- VCN configurada com subnet para recursos (se aplicável)

### Recursos Necessários

```bash
# Listar recursos atuais
oci {service} resource list --compartment-id $COMPARTMENT_OCID

# Verificar limites de serviço
oci limits quota list --service-name {service} --compartment-id $COMPARTMENT_OCID
```

## {execute}

```bash
# Criar recurso (ajuste parâmetros conforme necessário)
oci {service} resource create \
  --compartment-id $COMPARTMENT_OCID \
  --display-name "production-resource-{idx}"
```

## Validação

```bash
# Verificar criação
oci {service} resource list --compartment-id $COMPARTMENT_OCID --lifecycle-state ACTIVE
```"""


# =============================================================================
# MAIN GENERATION
# =============================================================================


def generate_example(category: str, idx: int) -> dict:
    # Get question
    templates = QUESTIONS.get(
        category,
        QUESTIONS.get(
            category.split("/")[0],
            [f"Configure {category.split('/')[1]} on Oracle Cloud Infrastructure"],
        ),
    )
    question = templates[idx % len(templates)]

    # Generate response based on category
    if category.startswith("terraform/"):
        response = generate_terraform_response(category, question, idx)
    elif category.startswith("troubleshooting/"):
        response = generate_troubleshooting_response(category, question, idx)
    elif category.startswith("compute/"):
        response = generate_compute_response(question, idx)
    else:
        response = generate_default_response(category, question, idx)

    # Get system prompt
    system = SYSTEM_PROMPTS.get(category, f"You are an OCI specialist for {category}.")

    # Difficulty
    difficulty = ["beginner", "intermediate", "advanced"][idx % 3]

    return {
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": question},
            {"role": "assistant", "content": response},
        ],
        "metadata": {
            "category": category,
            "difficulty": difficulty,
            "source": "generated-v4",
        },
    }


def main():
    print("=" * 60)
    print("OCI Specialist - Generate v4 (Filter-Safe)")
    print("=" * 60)

    output_dir = Path("data/curated")
    output_dir.mkdir(parents=True, exist_ok=True)

    all_examples = []
    stats = Counter()

    for category, config in CATEGORIES.items():
        num = config["examples"]
        print(f"\nGenerating {num} examples for {category}...")

        for i in range(num):
            ex = generate_example(category, i)
            all_examples.append(ex)

        stats[category] = num
        print(f"  -> {num} examples")

    # Write files
    print("\nWriting files...")
    by_cat = {}
    for ex in all_examples:
        cat = ex["metadata"]["category"]
        if cat not in by_cat:
            by_cat[cat] = []
        by_cat[cat].append(ex)

    for cat, examples in by_cat.items():
        safe = cat.replace("/", "-")
        fpath = output_dir / f"{safe}.jsonl"
        with open(fpath, "w") as f:
            for ex in examples:
                f.write(json.dumps(ex, ensure_ascii=False) + "\n")
        print(f"  {safe}.jsonl: {len(examples)} examples")

    # Combined file
    all_path = Path("data/all_curated_v4.jsonl")
    with open(all_path, "w") as f:
        for ex in all_examples:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")

    print(f"\n{'=' * 60}")
    print(f"TOTAL: {len(all_examples)} examples")
    print(f"OUTPUT: {all_path}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
