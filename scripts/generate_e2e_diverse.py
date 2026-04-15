#!/usr/bin/env python3
"""Evolve generate_diverse_v2.py - CLI real + intents alinhados preservando output structure.

Mantem:
- 84 categorias
- messages[] (system, user, assistant)
- metadata{} com category, difficulty, etc.

Adiciona:
- OCI CLI commands reais (da OCI_CLI_COMMANDS lookup)
- Intent alignment (create/list/manage → resposta correspondente)
- Remove "Fase 1/2/3/4" templates
"""

import json
import random
from pathlib import Path

random.seed(42)

EXAMPLES_PER_CATEGORY = 180

INTENTS = [
    ("create", "create new", "Create"),
    ("list", "list existing", "List"),
    ("manage", "manage lifecycle", "Manage"),
    ("configure", "configure settings", "Configure"),
]

CLI_TEMPLATE = """```bash
{cli} \\
  --compartment-id ${{ compartment_id }} \\{params}  --wait-for-state {state}
```

Replace placeholders with your OCIDs."""

CLI_COMMANDS = {
    "compute/instances": {
        "create": (
            "oci compute instance launch",
            "  --availability-domain AD-1\n  --shape VM.Standard.E4.Flex\n  --shape-config 'ocpus=2,memory=16'\n  --subnet-id ${{ subnet_id }}\n  --display-name ${{ name }}",
            "RUNNING",
        ),
        "list": (
            "oci compute instance list",
            "  --compartment-id ${{ compartment_id }}\n  --lifecycle-state RUNNING",
            "RUNNING",
        ),
        "get": (
            "oci compute instance get",
            "  --instance-id ${{ instance_id }}",
            "RUNNING",
        ),
        "manage": (
            "oci compute instance action",
            "  --instance-id ${{ instance_id }}\n  --action STOP",
            "STOPPED",
        ),
    },
    "database/autonomous": {
        "create": (
            "oci db autonomous-database create",
            "  --cpu-core-count 2\n  --storage-size-in-tbs 1\n  --db-workload AUTONOMOUS_TRANSACTION_PROCESSING\n  --license-type LICENSE_INCLUDED",
            "AVAILABLE",
        ),
        "list": (
            "oci db autonomous-database list",
            "  --compartment-id ${{ compartment_id }}\n  --lifecycle-state AVAILABLE",
            "AVAILABLE",
        ),
        "get": (
            "oci db autonomous-database get",
            "  --autonomous-database-id ${{ adb_id }}",
            "AVAILABLE",
        ),
    },
    "container/oke": {
        "create": (
            "oci ce cluster create",
            "  --vcn-id ${{ vcn_id }}\n  --kubernetes-version v1.28.2\n  --name ${{ cluster_name }}",
            "ACTIVE",
        ),
        "list": (
            "oci ce cluster list",
            "  --compartment-id ${{ compartment_id }}\n  --lifecycle-state ACTIVE",
            "ACTIVE",
        ),
    },
    "devops/secrets": {
        "create": (
            "oci vault secret create",
            "  --vault-id ${{ vault_id }}\n  --secret-name ${{ secret_name }}\n  --content-type BASE64\n  --secret-content ${{ content }}",
            "ACTIVE",
        ),
        "list": (
            "oci vault secret list",
            "  --vault-id ${{ vault_id }}\n  --lifecycle-state ACTIVE",
            "ACTIVE",
        ),
        "get": ("oci vault secret get", "  --secret-id ${{ secret_id }}", "ACTIVE"),
    },
    "lb/load-balancer": {
        "create": (
            "oci lb load-balancer create",
            "  --shape 100Mbps\n  --subnet-ids ['${{ subnet_id }}']\n  --display-name ${{ lb_name }}",
            "ACTIVE",
        ),
        "list": (
            "oci lb load-balancer list",
            "  --compartment-id ${{ compartment_id }}\n  --lifecycle-state ACTIVE",
            "ACTIVE",
        ),
    },
    "storage/object": {
        "create": (
            "oci os bucket create",
            "  --name ${{ bucket_name }}\n  --compartment-id ${{ compartment_id }}",
            "ACTIVE",
        ),
        "list": (
            "oci os bucket list",
            "  --namespace ${{ namespace }}\n  --compartment-id ${{ compartment_id }}",
            "ACTIVE",
        ),
    },
    "networking/vcn": {
        "create": (
            "oci network vcn create",
            "  --cidr-blocks ['10.0.0.0/16']\n  --display-name ${{ vcn_name }}",
            "AVAILABLE",
        ),
        "list": (
            "oci network vcn list",
            "  --compartment-id ${{ compartment_id }}\n  --lifecycle-state AVAILABLE",
            "AVAILABLE",
        ),
    },
}

CATEGORIES = [
    # Compute
    "compute/instances",
    "compute/scaling",
    "compute/custom-images",
    # Storage
    "storage/block",
    "storage/object",
    "storage/file",
    # Networking
    "networking/vcn",
    "networking/security",
    "networking/connectivity",
    "lb/load-balancer",
    # Database
    "database/autonomous",
    "database/mysql",
    "database/postgresql",
    "database/nosql",
    "database/autonomous-json",
    "database/exadata",
    # Container
    "container/oke",
    "container/instances",
    # Serverless
    "serverless/functions",
    "serverless/api-gateway",
    # Security
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
    # DevOps
    "devops/ci-cd",
    "devops/resource-manager",
    "devops/artifacts",
    "devops/secrets",
    # Migration
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
    # Terraform
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
    # Observability
    "observability/logging",
    "observability/monitoring",
    "observability/stack-monitoring",
    "observability/apm",
    # Troubleshooting
    "troubleshooting/connectivity",
    "troubleshooting/performance",
    "troubleshooting/authentication",
    "troubleshooting/database",
    "troubleshooting/compute",
    "troubleshooting/storage",
    "troubleshooting/oke",
    "troubleshooting/functions",
    # Governance
    "governance/landing-zone",
    "governance/compartments",
    "governance/tagging",
    "governance/budgets-cost",
    "governance/policies-guardrails",
    "governance/compliance",
    "governance/audit-readiness",
    "governance/resource-discovery",
    # FinOps
    "finops/cost-optimization",
    "finops/showback-chargeback",
    "finops/rightsizing",
    "finops/storage-tiering",
    # Platform
    "platform/backup-governance",
    "platform/sre-operations",
]

COMPANIES = [
    "TechCorp Brasil",
    "DataFlow Solutions",
    "CloudNative Inc",
    "FinServe Digital",
]
PROJECTS = ["ecommerce-migration", "data-lake", "modernization", "cost-optimization"]
REGIONS = ["sa-saopaulo-1", "us-ashburn-1", "eu-frankfurt-1"]
COMPARTMENTS = ["production", "development", "staging"]


def get_intent(idx, question_lower):
    """Detect intent from question."""
    if any(w in question_lower for w in ["create", "provision", "setup", "new"]):
        return INTENTS[0]
    elif any(w in question_lower for w in ["list", "show", "get all"]):
        return INTENTS[1]
    elif any(w in question_lower for w in ["manage", "update", "delete", "terminate"]):
        return INTENTS[2]
    elif any(w in question_lower for w in ["configure", "config", "setup"]):
        return INTENTS[3]
    return INTENTS[idx % 4]


def get_cli_for_category(category):
    """Get CLI commands for category."""
    return CLI_COMMANDS.get(category, CLI_COMMANDS.get("compute/instances"))


def generate_response(category, intent, idx):
    """Generate aligned response with real CLI."""
    cmds = get_cli_for_category(category)
    key = intent[0]

    cli_cmd, params, state = cmds.get(key, cmds.get("create", ("oci", "", "AVAILABLE")))

    response = f"""{intent[2]} {category.split("/")[-1]}:

{cli_cmd} \\
  --compartment-id <ocid> \\
{params}

Common issues:
- Check compartment permissions
- Verify resource limits
- Use --wait-for-state {state}

Replace <ocid> with actual OCIDs."""
    return response


def generate_example(category, idx):
    """Generate one example with intent-aligned responses."""
    company = random.choice(COMPANIES)
    project = random.choice(PROJECTS)
    region = random.choice(REGIONS)
    compartment = random.choice(COMPARTMENTS)

    intent = get_intent(idx, f"{company} {project}")

    subcat = category.split("/")[-1]

    question = f"I need to {intent[1]} {subcat} resources for {company} project {project} in {compartment}/{region}. What's the OCI CLI command?"

    response = generate_response(category, intent, idx)

    return {
        "messages": [
            {
                "role": "system",
                "content": f"You are an OCI specialist with expertise in {category}.",
            },
            {"role": "user", "content": question},
            {"role": "assistant", "content": response},
        ],
        "metadata": {
            "category": category,
            "difficulty": "intermediate",
            "company": company,
            "project": project,
            "source": "evolved-diverse-v1",
        },
    }


def main():
    """Generate evolved diverse examples."""
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

    print(f"\n🎯 Total: {total} evolved examples")


if __name__ == "__main__":
    main()
