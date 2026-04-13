#!/usr/bin/env python3
"""Generate troubleshooting examples for categories that regressed in benchmarks.

Focus on:
- troubleshooting/performance (-0.31)
- troubleshooting/storage (-0.13)
- troubleshooting/authentication

Usage:
    python scripts/generate_troubleshooting.py
"""

import json
import random
import hashlib
from pathlib import Path

random.seed(42)

CATEGORIES = {
    "troubleshooting/performance": {
        "system": "You are an OCI troubleshooting specialist with expertise in performance diagnostics. Provide diagnostic guidance on CPU, memory, storage I/O, and network latency issues. Include OCI-specific tools like Monitoring, Operations Insights, and performance views.",
        "base_category": "compute/instances",
    },
    "troubleshooting/storage": {
        "system": "You are an OCI troubleshooting specialist with expertise in storage diagnostics. Provide diagnostic guidance on block volume performance, object storage access, file system latency, and storage quota issues. Include OCI-specific tools like block volume performance stats and storage metrics.",
        "base_category": "storage/block",
    },
    "troubleshooting/authentication": {
        "system": "You are an OCI troubleshooting specialist with expertise in IAM diagnostics. Provide diagnostic guidance on policy permission issues, authentication failures, federation problems, and dynamic group evaluation. Include OCI-specific IAM tools and policy debugging.",
        "base_category": "security/iam-basics",
    },
}

COMPANIES = [
    "TechCorp Brasil",
    "DataFlow Solutions",
    "CloudNative Inc",
    "FinServe Digital",
    "RetailMax Online",
    "HealthTech Systems",
    "EduPlatform Global",
    "LogiTrack Logistics",
]

SHAPES = [
    "VM.Standard.E4.Flex",
    "VM.Standard.A1.Flex",
    "VM.Optimized3.Flex",
    "BM.Standard.E5",
]
REGIONS = ["sa-saopaulo-1", "us-ashburn-1", "us-phoenix-1", "eu-frankfurt-1"]
COMPS = ["production", "development", "staging", "sandbox"]

OCI_CLI_COMMANDS = {
    "troubleshooting/performance": {
        "list_instances": "oci compute instance list --compartment-id {comp_id}",
        "get_metrics": "oci monitoring metric-data point-query --namespace oci_computeagent --resourceId {instance_id}",
        "list_alarms": "oci monitoring alarm list --compartment-id {comp_id}",
    },
    "troubleshooting/storage": {
        "list_volumes": "oci bv volume list --compartment-id {comp_id}",
        "get_volume_stats": "oci bv volume get --volume-id {volume_id}",
        "check_iops": "oci monitoring metric-data point-query --namespace oci_blockstore --resourceId {volume_id}",
    },
    "troubleshooting/authentication": {
        "list_policies": "oci iam policy list --compartment-id {comp_id}",
        "inspect_policy": "oci iam policy get --policy-id {policy_id}",
        "check_dynamic_groups": "oci iam dynamic-group get --dynamic-group-id {group_id}",
    },
}

SCENARIOS = {
    "troubleshooting/performance": [
        "CPU usage spike to 100% during business hours",
        "Memory exhaustion causing OOM kills on container workloads",
        "Storage latency exceeding 50ms consistently",
        "Network throughput dropping to 10% of expected bandwidth",
        "Application response time degrading over 24 hours",
        "Auto-scaling not triggering despite high CPU",
        "Instance boot time increasing from 2min to 10min",
        "Database query performance degrading after data growth",
        "Intermittent timeout errors during peak traffic",
        "Performance baseline suddenly changing without code changes",
    ],
    "troubleshooting/storage": [
        "Block volume showing 0 IOPS despite provisioned performance",
        "Object storage bucket returning 403 Forbidden",
        "File system mount timeout after network interruption",
        "Storage quota reached but usage shows lower values",
        "Volume attachment failing with 'already attached' error",
        "Bucket lifecycle policy not transitioning objects",
        "Cannot delete object storage bucket - permission denied",
        "Block volume performance degrading after 30 days",
        "Mount target becoming unreachable intermittently",
        "Pre-authenticated request expiring earlier than configured",
    ],
    "troubleshooting/authentication": [
        "User unable to access compartment despite policy assignment",
        "Dynamic group not matching instances as expected",
        "Federated user login failing with SAML assertion error",
        "Service account API calls returning 401 Unauthorized",
        "Policy allowing action but audit log shows DENIED",
        "Group membership change not taking effect immediately",
        "OCI CLI assume-role failing with credential expired",
        "Resource principal not recognized in another service",
        "MFA device not prompting during login",
        "Cross-compartment access failing with 'not in allowed compartments'",
    ],
}

DIAGNOSTIC_STEPS = {
    "troubleshooting/performance": [
        "Check instance monitoring metrics in OCI Console",
        "Review VCN flow logs for network issues",
        "Examine boot volume performance metrics",
        "Analyze compute agent metrics for CPU/memory pressure",
        "Review alarm history for threshold breaches",
        "Check for noisy neighbor issues on shared infrastructure",
        "Verify shape burst capacity usage",
        "Examine instance pool health and distribution",
    ],
    "troubleshooting/storage": [
        "Verify volume attachment state in OCI Console",
        "Check volume performance settings match workload needs",
        "Review bucket access logging for 403 errors",
        "Examine NFS mount options and export rules",
        "Verify VCN security list rules for storage endpoints",
        "Check service limits for block volume count",
        "Review lifecycle policy configuration",
        "Examine volume backup and restore status",
    ],
    "troubleshooting/authentication": [
        "Review effective policies using Policy Analyzer",
        "Check dynamic group matching rules syntax",
        "Verify SAML IdP metadata is current",
        "Examine audit logs for access Denied events",
        "Confirm user group membership in OCI Console",
        "Review resource principal session token validity",
        "Check for policy evaluation caching delays",
        "Verify compartment OCID in policy statements",
    ],
}

SOLUTIONS = {
    "troubleshooting/performance": [
        "Resize to a larger shape or enable burst capacity",
        "Implement horizontal auto-scaling with proper cooldown",
        "Enable Performance Hub for comprehensive analysis",
        "Configure enhanced monitoring with custom metrics",
        "Review and optimize application memory management",
        "Implement CDN for static content to reduce latency",
        "Use placement settings to avoid noisy neighbors",
        "Configure alarm-based auto-remediation",
    ],
    "troubleshooting/storage": [
        "Change volume performance tier to Higher Performance",
        "Enable volume backup policy for data protection",
        "Review and update bucket policies for correct permissions",
        "Recreate mount target with correct security rules",
        "Delete stale snapshots to free quota",
        "Configure VCN endpoints for private bucket access",
        "Update lifecycle policy rules",
        "Enable service connector hub for access logging",
    ],
    "troubleshooting/authentication": [
        "Add explicit compartment permissions to policy",
        "Fix dynamic group matching rule syntax",
        "Regenerate SAML certificate before expiration",
        "Use resource principal instead of user credentials",
        "Wait 5-10 minutes for IAM propagation",
        "Create policy without 'where' clauses for testing",
        "Use instance principal for compute resources",
        "Enable audit logging to track access patterns",
    ],
}


def generate_example(category: str, idx: int) -> dict:
    company = random.choice(COMPANIES)
    region = random.choice(REGIONS)
    comp = random.choice(COMPS)
    shape = random.choice(SHAPES)
    scenario = random.choice(SCENARIOS[category])

    diagnostic = random.sample(DIAGNOSTIC_STEPS[category], 3)
    solution = random.sample(SOLUTIONS[category], 3)

    cli_cmd = random.choice(list(OCI_CLI_COMMANDS[category].values()))

    difficulty = random.choices(
        ["beginner", "intermediate", "advanced"], weights=[0.2, 0.5, 0.3]
    )[0]

    system_content = CATEGORIES[category]["system"]

    user_content = f"""{company} ({comp}) in {region} is experiencing: {scenario}

Environment:
- Shape: {shape}
- Compartment: {comp}
- Region: {region}

Help diagnose this issue and provide resolution steps."""

    assistant_content = f"""## Diagnóstico

### 1. Verificação Inicial

Primeiro, colete dados do ambiente afetado:

```bash
# Listar recursos no compartimento
oci compute instance list --compartment-id $COMPARTMENT_OCID --region {region}

# Verificar métricas de performance
oci monitoring metric-data point-query \\
  --namespace oci_computeagent \\
  --resourceId $INSTANCE_OCID \\
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%SZ) \\
  --end-time $(date -u +%Y-%m-%dT%H:%M:%SZ)
```

### 2. Análise de Dados

Execute os seguintes comandos de verificação:

```bash
{cli_cmd.replace("{comp_id}", "$COMPARTMENT_OCID").replace("{instance_id}", "$INSTANCE_OCID")}
```

### 3. Diagnóstico Específico

{diagnostic[0]}

{diagnostic[1]}

{diagnostic[2]}

### 4. Solução

**Ação recomendada:**

{solution[0]}

**Passos de implementação:**

1. {solution[1]}
2. {solution[2]}

### 5. Verificação Pós-Correção

```bash
# Validar que o problema foi resolvido
oci monitoring alarm list --compartment-id $COMPARTMENT_OCID --query "data[?contains(display-name, '{scenario[:30]}')]"
```

### 6. Prevenção

- Configurar alarmes proativos
- Implementar auto-scaling appropriate
- Revisar dimensionamento periódico

Doc: {CATEGORIES[category]["system"].split("with expertise")[0].replace("You are an OCI specialist ", "https://docs.oracle.com/en-us/iaas/Content/")}
"""

    return {
        "messages": [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content},
            {"role": "assistant", "content": assistant_content},
        ],
        "metadata": {
            "category": category,
            "difficulty": difficulty,
            "source": "generated",
            "company": company,
            "region": region,
            "intent": "troubleshoot",
        },
    }


def main():
    output_dir = Path("data/curated")
    output_dir.mkdir(exist_ok=True)

    examples_per_category = 200

    for category in CATEGORIES:
        output_file = output_dir / f"{category.replace('/', '-')}.jsonl"
        examples = []

        for i in range(examples_per_category):
            example = generate_example(category, i)
            examples.append(example)

        with open(output_file, "w") as f:
            for ex in examples:
                f.write(json.dumps(ex, ensure_ascii=False) + "\n")

        print(f"Generated {len(examples)} examples for {category} -> {output_file}")

    total = examples_per_category * len(CATEGORIES)
    print(f"\nTotal: {total} troubleshooting examples generated")


if __name__ == "__main__":
    main()
