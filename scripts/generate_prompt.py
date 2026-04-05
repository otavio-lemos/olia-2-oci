#!/usr/bin/env python3
"""Generate prompt files for OCI dataset topics from taxonomy.

Usage:
    python scripts/generate_prompt.py --list          # List all topics
    python scripts/generate_prompt.py compute/instances  # Generate one topic
    python scripts/generate_prompt.py --all           # Generate all topics
"""

import argparse
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
TAXONOMY_FILE = PROJECT_ROOT / "docs" / "taxonomy.md"
TMP_DIR = PROJECT_ROOT / "tmp"

QUALITY_RULES = """# OCI Specialist LLM - Quality Rules

## Dataset Quality Rules (Rigid)

### Prohibited Content

1. **NEVER copy OCI documentation verbatim**
   - Paraphrase in your own words
   - Reorganize information structure
   - Add original examples

2. **NEVER invent non-existent Oracle services**
   - Only include real OCI services
   - Verify service names from official docs
   - No "OCI Magic Service" or similar

3. **NEVER use prices without marking as mutable**
   - Prices change frequently
   - Use: "As of 2024, pricing is approximately X" or [MUTABLE]
   - Never quote exact current prices

4. **NEVER use limits/quotas without marking**
   - Limits vary by region and tenancy
   - Use: "Check your specific limits in the console" or [CHECK DOCS]

5. **NEVER create vague examples**
   - Bad: "Use best practices for security"
   - Good: "Enable MFA for all users, use IAM groups for access control"

6. **NEVER skip steps in procedural answers**
   - Include all necessary steps
   - Explain prerequisite configurations

7. **NEVER skip risks/justifications in architecture**
   - Every architectural choice has trade-offs
   - Explain why the recommendation makes sense

### Required Content

1. **Always provide specific OCI resource names**
   - Use actual OCI resource identifiers
   - Reference correct service names

2. **Always mark mutable content**
   - [MUTABLE] for prices, limits, quotas
   - [CHECK DOCS] for version-dependent info

3. **Always use accurate OCI terminology**
   - Compartment, not "folder"
   - VCN, not "virtual network" (define on first use)
   - Policy, not "permission"
   - OKE (Oracle Kubernetes Engine), not "Kubernetes OCI"

4. **Always include multi-cloud context when relevant**
   - AWS/Azure/GCP equivalent concepts
   - Migration mapping guidance

5. **Always include documentation references**
   - Reference official OCI docs when relevant
   - Include doc links: https://docs.oracle.com/en-us/iaas/Content/...

### Response Templates

#### Good Response Example (Compute)
```
Para criar uma instância no OCI:

1. No Console, vá para Compute → Instances
2. Clique em "Create Instance"
3. Selecione o compartment desejado
4. Escolha o shape (VM.Standard2.4 para propósito geral)
5. Configure a subnet (pública ou privada)
6. Adicione SSH keys
7. Clique em "Create"

Shape recomendado:
- VM.Standard2.4: propósito geral
- VM.Standard.E4: AMD EPYC (custo-benefício)
- VM.Optimized3: memória otimizada
- VM.Standard.A1: ARM (Ampere A1, econômico)

Nota: [MUTABLE] Preços variam por região e shape.
```

#### Bad Response Example (Compute)
```
Para criar uma instância no OCI, basta usar o console e escolher
um shape bom. Use práticas recomendadas de segurança.
```

### Validation Checklist

- No copied documentation sentences
- No made-up services
- Prices marked as mutable or removed
- Limits marked to verify in console
- Answers have specific steps
- Architecture answers include trade-offs
- All OCI terms are correct
- Documentation references included when relevant

### Deduplication Rules

- Exact duplicate: remove one copy
- Near-duplicate (>90% similarity): merge or keep best
- Same question, different category: **NOT duplicate** - keep both
- Same question, same category: keep only one

### Category Detection

When generating examples, detect category from:
- `data/curated/[category]-[nnn].jsonl` filename
- Or metadata.category field

Example categories:
- oci-core/compute, oci-core/storage, oci-core/networking, oci-core/database
- oci-security/iam, oci-security/vault, oci-security/encryption
- oci-migration/aws-to-oci, oci-migration/azure-to-oci, oci-migration/gcp-to-oci
- oci-terraform/provider, oci-terraform/resources
- oci-troubleshooting/connectivity, oci-troubleshooting/performance

"""

SYSTEM_PROMPTS = {
    "compute/instances": "You are an OCI specialist with expertise in Compute instances. Provide technical guidance on instance creation, shape selection, SSH access, and lifecycle management.",
    "compute/scaling": "You are an OCI specialist with expertise in Compute scaling. Provide technical guidance on instance pools, auto-scaling, and capacity planning.",
    "compute/custom-images": "You are an OCI specialist with expertise in Compute custom images. Provide technical guidance on image creation, import/export, and instance configurations.",
    "storage/block": "You are an OCI specialist with expertise in Block Volumes. Provide technical guidance on volume creation, attachment, performance tiers, and backup strategies.",
    "storage/object": "You are an OCI specialist with expertise in Object Storage. Provide technical guidance on buckets, pre-authenticated requests, lifecycle policies, and versioning.",
    "storage/file": "You are an OCI specialist with expertise in File Storage. Provide technical guidance on NFS mount targets, export options, and backup strategies.",
    "networking/vcn": "You are an OCI specialist with expertise in VCN design. Provide technical guidance on CIDR blocks, subnets, Internet Gateway, and NAT Gateway.",
    "networking/security": "You are an OCI specialist with expertise in network security. Provide technical guidance on Security Lists, NSGs, and ingress/egress rules.",
    "networking/connectivity": "You are an OCI specialist with expertise in network connectivity. Provide technical guidance on DRG, VPN IPSec, FastConnect, and VCN peering.",
    "lb/load-balancer": "You are an OCI specialist with expertise in Load Balancing. Provide technical guidance on backend sets, listeners, SSL certificates, and health checks.",
    "database/autonomous": "You are an OCI specialist with expertise in Autonomous Database. Provide technical guidance on ATP, ADW, wallet, connection strings, and backup/restore.",
    "database/mysql": "You are an OCI specialist with expertise in OCI MySQL HeatWave. Provide technical guidance on configuration, scaling, backup, and replication.",
    "database/postgresql": "You are an OCI specialist with expertise in OCI PostgreSQL. Provide technical guidance on instance management, scaling, backup, and high availability.",
    "database/nosql": "You are an OCI specialist with expertise in Oracle NoSQL Database. Provide technical guidance on table creation, CRUD operations, TTL, and consistency.",
    "database/autonomous-json": "You are an OCI specialist with expertise in Autonomous JSON Database. Provide technical guidance on document store, MongoDB compatibility, and JSON collections.",
    "database/exadata": "You are an OCI specialist with expertise in Exadata Cloud Service. Provide technical guidance on infrastructure, DB systems, patching, and maintenance.",
    "container/oke": "You are an OCI specialist with expertise in OKE. Provide technical guidance on cluster creation, node pools, worker nodes, and kubectl deployment.",
    "container/instances": "You are an OCI specialist with expertise in OCI Container Instances. Provide technical guidance on container deployment, OCIR, and image management.",
    "serverless/functions": "You are an OCI specialist with expertise in OCI Functions. Provide technical guidance on function deployment, invocation, and monitoring.",
    "serverless/api-gateway": "You are an OCI specialist with expertise in API Gateway. Provide technical guidance on routes, integrations, authentication, and throttling.",
    "security/iam-basics": "You are an OCI specialist with expertise in IAM. Provide technical guidance on compartments, users, groups, authentication, and MFA.",
    "security/policies": "You are an OCI specialist with expertise in IAM policies. Provide technical guidance on policy syntax, statements, and common patterns.",
    "security/dynamic-groups": "You are an OCI specialist with expertise in Dynamic Groups. Provide technical guidance on rules, instance principal, and resource principal.",
    "security/federation": "You are an OCI specialist with expertise in federation. Provide technical guidance on IdCS, Okta, SAML, OAuth, and user provisioning.",
    "security/vault-secrets": "You are an OCI specialist with expertise in Vault secrets. Provide technical guidance on secret creation, retrieval, and rotation.",
    "security/vault-keys": "You are an OCI specialist with expertise in Vault keys. Provide technical guidance on key management, policies, import, and generation.",
    "security/encryption": "You are an OCI specialist with expertise in encryption. Provide technical guidance on volume encryption, BYOK, customer-managed keys, and HSM.",
    "security/cloud-guard": "You are an OCI specialist with expertise in Cloud Guard. Provide technical guidance on configuration, detector recipes, and responder rules.",
    "security/waf": "You are an OCI specialist with expertise in WAF. Provide technical guidance on access rules, rate limiting, and protection patterns.",
    "migration/aws-compute": "You are an OCI specialist with expertise in AWS to OCI migration. Provide technical guidance on EC2 to OCI Compute migration.",
    "migration/aws-storage": "You are an OCI specialist with expertise in AWS to OCI storage migration. Provide technical guidance on S3 to Object Storage migration.",
    "migration/aws-database": "You are an OCI specialist with expertise in AWS to OCI database migration. Provide technical guidance on RDS to OCI Database migration.",
    "migration/azure-compute": "You are an OCI specialist with expertise in Azure to OCI migration. Provide technical guidance on Azure VMs to OCI Compute migration.",
    "migration/azure-storage": "You are an OCI specialist with expertise in Azure to OCI storage migration. Provide technical guidance on Azure Blob to Object Storage migration.",
    "migration/azure-database": "You are an OCI specialist with expertise in Azure to OCI database migration. Provide technical guidance on Azure SQL to Autonomous Database migration.",
    "migration/gcp-compute": "You are an OCI specialist with expertise in GCP to OCI migration. Provide technical guidance on GCP Compute Engine to OCI Compute migration.",
    "migration/gcp-storage": "You are an OCI specialist with expertise in GCP to OCI storage migration. Provide technical guidance on GCP Cloud Storage to Object Storage migration.",
    "migration/gcp-database": "You are an OCI specialist with expertise in GCP to OCI database migration. Provide technical guidance on GCP Cloud SQL to OCI Database migration.",
    "migration/onprem-compute": "You are an OCI specialist with expertise in on-premises to OCI migration. Provide technical guidance on lift-and-shift VM migration.",
    "migration/onprem-storage": "You are an OCI specialist with expertise in on-premises to OCI storage migration. Provide technical guidance on NFS migration and data transfer.",
    "migration/onprem-vmware": "You are an OCI specialist with expertise in VMware to OCI migration. Provide technical guidance on VMware Cloud Foundation and hybrid connectivity.",
    "migration/onprem-database": "You are an OCI specialist with expertise in on-premises to OCI database migration. Provide technical guidance on ZDM and Database Migration Service.",
    "migration/data-transfer": "You are an OCI specialist with expertise in data transfer. Provide technical guidance on GoldenGate, Data Integration, and large-scale transfers.",
    "terraform/provider": "You are an OCI Terraform specialist with expertise in provider configuration. Provide technical guidance on authentication and provider settings.",
    "terraform/compute": "You are an OCI Terraform specialist with expertise in Compute resources. Provide technical guidance on instance, instance pool, and auto-scaling Terraform.",
    "terraform/storage": "You are an OCI Terraform specialist with expertise in storage resources. Provide technical guidance on block volume, object storage, and file storage Terraform.",
    "terraform/networking": "You are an OCI Terraform specialist with expertise in networking resources. Provide technical guidance on VCN, subnet, and gateway Terraform.",
    "terraform/load-balancer": "You are an OCI Terraform specialist with expertise in load balancer resources. Provide technical guidance on LB, backend sets, and listener Terraform.",
    "terraform/database": "You are an OCI Terraform specialist with expertise in database resources. Provide technical guidance on Autonomous, MySQL, PostgreSQL, and NoSQL Terraform.",
    "terraform/container": "You are an OCI Terraform specialist with expertise in container resources. Provide technical guidance on OKE, node pools, and OCIR Terraform.",
    "terraform/serverless": "You are an OCI Terraform specialist with expertise in serverless resources. Provide technical guidance on Functions and API Gateway Terraform.",
    "terraform/security": "You are an OCI Terraform specialist with expertise in security resources. Provide technical guidance on Vault, secrets, keys, and WAF Terraform.",
    "terraform/observability": "You are an OCI Terraform specialist with expertise in observability resources. Provide technical guidance on logging, monitoring, and APM Terraform.",
    "terraform/devops": "You are an OCI Terraform specialist with expertise in DevOps resources. Provide technical guidance on artifacts, OCIR, and Resource Manager Terraform.",
    "terraform/state": "You are an OCI Terraform specialist with expertise in state management. Provide technical guidance on remote state, state locking, and workspaces.",
    "observability/logging": "You are an OCI specialist with expertise in Logging. Provide technical guidance on log groups, custom logs, retention, and audit.",
    "observability/monitoring": "You are an OCI specialist with expertise in Monitoring. Provide technical guidance on metrics, alarms, notifications, and custom metrics.",
    "observability/stack-monitoring": "You are an OCI specialist with expertise in Stack Monitoring. Provide technical guidance on resource monitoring and database monitoring.",
    "observability/apm": "You are an OCI specialist with expertise in APM. Provide technical guidance on distributed tracing and performance diagnostics.",
    "troubleshooting/connectivity": "You are an OCI troubleshooting specialist with expertise in connectivity issues. Provide technical guidance on routing, DNS, and VPN problems.",
    "troubleshooting/performance": "You are an OCI troubleshooting specialist with expertise in performance issues. Provide technical guidance on CPU, memory, storage, and network bottlenecks.",
    "troubleshooting/authentication": "You are an OCI troubleshooting specialist with expertise in authentication issues. Provide technical guidance on policy permissions, MFA, and federation failures.",
    "troubleshooting/database": "You are an OCI troubleshooting specialist with expertise in database issues. Provide technical guidance on connection issues, TNS errors, and wallet problems.",
    "troubleshooting/compute": "You are an OCI troubleshooting specialist with expertise in Compute issues. Provide technical guidance on provisioning, boot volume, and SSH problems.",
    "troubleshooting/storage": "You are an OCI troubleshooting specialist with expertise in storage issues. Provide technical guidance on bucket access, upload failures, and performance.",
    "troubleshooting/oke": "You are an OCI troubleshooting specialist with expertise in OKE issues. Provide technical guidance on cluster creation, node pools, and worker nodes.",
    "troubleshooting/functions": "You are an OCI troubleshooting specialist with expertise in Functions issues. Provide technical guidance on invocation errors, API Gateway 502/504, and timeouts.",
    "devops/ci-cd": "You are an OCI DevOps specialist with expertise in CI/CD pipelines. Provide technical guidance on build pipelines, deploy pipelines, triggers, and artifacts.",
    "devops/resource-manager": "You are an OCI DevOps specialist with expertise in Resource Manager. Provide technical guidance on stacks, jobs, drift detection, and state management.",
    "devops/artifacts": "You are an OCI DevOps specialist with expertise in artifacts. Provide technical guidance on OCIR, Helm charts, image signing, and repository access.",
    "devops/secrets": "You are an OCI DevOps specialist with expertise in secrets management. Provide technical guidance on Vault secrets, pipeline injection, and rotation.",
}

DIVERSITY_REQUIREMENTS = {
    "compute": "Varie os exemplos entre:\n- Diferentes shapes (Ampere A1, Intel Xeon, AMD)\n- Diferentes cenários (web servers, databases, batch processing)\n- Diferentes personas (sysadmin, devops engineer, architect)\n- Diferentes problemas (provisioning, performance, cost optimization)",
    "storage": "Varie os exemplos entre:\n- Diferentes tipos de storage (block, object, file)\n- Diferentes cenários (backup, archive, shared storage)\n- Diferentes personas (DBA, sysadmin, data engineer)\n- Diferentes problemas (performance, access, cost optimization)",
    "networking": "Varie os exemplos entre:\n- Diferentes topologias de rede (hub-spoke, mesh)\n- Diferentes cenários (hybrid cloud, multi-region)\n- Diferentes personas (network engineer, security architect)\n- Diferentes problemas (connectivity, routing, security)",
    "lb": "Varie os exemplos entre:\n- Diferentes tipos de load balancer (regional, global)\n- Diferentes cenários (web apps, APIs, microservices)\n- Diferentes personas (DevOps, network engineer)\n- Diferentes problemas (health checks, SSL, backend failures)",
    "database": "Varie os exemplos entre:\n- Diferentes tipos de database (autonomous, MySQL, PostgreSQL, NoSQL)\n- Diferentes cenários (OLTP, OLAP, document store)\n- Diferentes personas (DBA, developer, data engineer)\n- Diferentes problemas (connection, performance, backup/restore)",
    "container": "Varie os exemplos entre:\n- Diferentes cenários (microservices, batch jobs, web apps)\n- Diferentes personas (DevOps, platform engineer, developer)\n- Diferentes problemas (deployment, scaling, networking)",
    "serverless": "Varie os exemplos entre:\n- Diferentes cenários (event-driven, APIs, data processing)\n- Diferentes personas (developer, DevOps, architect)\n- Diferentes problemas (cold starts, timeouts, integration)",
    "security": "Varie os exemplos entre:\n- Diferentes serviços de segurança (IAM, Vault, Cloud Guard, WAF)\n- Diferentes cenários (access control, encryption, threat detection)\n- Diferentes personas (security engineer, admin, auditor)\n- Diferentes problemas (permission denied, key rotation, false positives)",
    "migration": "Varie os exemplos entre:\n- Diferentes origens (AWS, Azure, GCP, on-premises)\n- Diferentes workloads (compute, storage, database)\n- Diferentes personas (migration specialist, architect, DBA)\n- Diferentes problemas (compatibility, performance, downtime)",
    "terraform": "Varie os exemplos entre:\n- Diferentes resources (compute, storage, networking, database)\n- Diferentes cenários (greenfield, import, migration)\n- Diferentes personas (DevOps, infrastructure engineer, architect)\n- Diferentes problemas (state management, dependencies, errors)",
    "observability": "Varie os exemplos entre:\n- Diferentes serviços (logging, monitoring, APM, stack monitoring)\n- Diferentes cenários (alerting, dashboards, troubleshooting)\n- Diferentes personas (SRE, DevOps, developer)\n- Diferentes problemas (missing metrics, log retention, trace correlation)",
    "troubleshooting": "Varie os exemplos entre:\n- Diferentes tipos de problema (connectivity, performance, auth, database)\n- Diferentes cenários (production outage, degraded performance, migration issues)\n- Diferentes personas (SRE, sysadmin, network engineer)\n- Diferentes metodologias de troubleshooting (bottom-up, top-down)",
    "devops": "Varie os exemplos entre:\n- Diferentes serviços (CI/CD, Resource Manager, Artifacts, Secrets)\n- Diferentes cenários (greenfield, migration, optimization)\n- Diferentes personas (DevOps engineer, developer, platform engineer)\n- Diferentes problemas (pipeline failures, state drift, artifact management)",
}


def parse_taxonomy(taxonomy_path: Path) -> list[dict]:
    """Parse taxonomy.md and extract all topics with their metadata."""
    content = taxonomy_path.read_text()
    topics = []

    pattern = re.compile(
        r"####\s+([\w/-]+)\s+\(\d+\)\s*\n"
        r"(.*?)"
        r"-\s+\*\*Docs\*\*:\s+(https?://\S+)",
        re.DOTALL,
    )

    for match in pattern.finditer(content):
        topic_name = match.group(1)
        description_text = match.group(2).strip()
        docs_url = match.group(3).strip()

        descriptions = [
            line.lstrip("- ").strip()
            for line in description_text.split("\n")
            if line.strip().startswith("-") and "**Docs**" not in line
        ]

        topics.append(
            {
                "name": topic_name,
                "descriptions": descriptions,
                "docs_url": docs_url,
            }
        )

    return topics


def generate_prompt(topic: dict) -> str:
    """Generate a complete prompt file for a topic."""
    name = topic["name"]
    descriptions = "\n".join(f"- {d}" for d in topic["descriptions"])
    docs_url = topic["docs_url"]

    group = name.split("/")[0]
    diversity = DIVERSITY_REQUIREMENTS.get(group, "")
    system_prompt = SYSTEM_PROMPTS.get(
        name,
        f"You are an OCI specialist with expertise in {name}. Provide technical guidance.",
    )

    prompt = f"""# OCI Dataset Generation - {name}

## QUALITY RULES (OBRIGATÓRIO - SIGA À RISCA)

{QUALITY_RULES}
---

## TOPIC: {name}

#### {name} (140)
{descriptions}
- **Docs**: {docs_url}


---

## SYSTEM PROMPT (para usar no JSONL)

{system_prompt}

---

## DIVERSITY REQUIREMENTS (OBRIGATÓRIO)

{diversity}

---

## SUAS REGRAS DE EXECUÇÃO

1. Você DEVE seguir OBRIGATORIAMENTE todas as regras em "QUALITY RULES" acima
2. Gere APENAS exemplos para o topic "{name}"
3. Use APENAS as informações presentes em "TOPIC: {name}"
4. Não invente informações que não estão nos docs OCI
5. Não use preços ou limites sem marcar [MUTABLE] ou [CHECK DOCS]
6. Cada exemplo DEVE ter um cenário diferente - NÃO repita o mesmo caso de uso
7. Varie os contextos: diferentes personas, diferentes níveis de complexidade, diferentes casos de uso reais

---

## OUTPUT FORMAT

Gere EXATAMENTE 140 exemplos em formato JSONL.

**UM objeto JSON por linha** - cada linha é um objeto JSON completo.

```
{{"messages": [...], "metadata": {{"category": "{name}", "difficulty": "beginner|intermediate|advanced", "source": "generated"}}}}
{{"messages": [...], "metadata": {{"category": "{name}", "difficulty": "beginner|intermediate|advanced", "source": "generated"}}}}
... (140 linhas total)
```

---

## JSONL RULES (CRÍTICO - SIGA EXATAMENTE)

1. **UM objeto JSON por linha** - sem arrays, sem wrapper, sem markdown
2. **Escape todas as aspas dentro de strings**: " (aspas) → \\" (backslash aspas)
3. **Escape newlines dentro de strings**: quebra de linha → \\n
4. **Escape backslashes**: \\ (backslash) → \\\\
5. **metadata é OBRIGATÓRIO** em cada objeto
6. **metadata deve ficar FORA do array messages!**

**ESTRUTURA CORRETA (faça exatamente assim!):**
```json
{{"messages": [
  {{"role": "system", "content": "..."}},
  {{"role": "user", "content": "..."}},
  {{"role": "assistant", "content": "..."}}
], "metadata": {{"category": "...", "difficulty": "...", "source": "generated"}}}}
```

**ESTRUTURA ERRADA (NUNCA faça assim!):**
```json
{{"messages": [
  {{"role": "system", "content": "..."}},
  {{"role": "user", "content": "..."}},
  {{"role": "assistant", "content": "..."}},
  {{"metadata": {{"category": "..."}}}}
]}}
```

⚠️ **ATENÇÃO**: O metadata DEVE ficar na mesma linha que o messages, como um sibling key, NUNCA dentro do array messages!

---

## DISTRIBUIÇÃO DE DIFICULDADE
- beginner: ~30% dos exemplos (42 exemplos)
- intermediate: ~50% dos exemplos (70 exemplos)
- advanced: ~20% dos exemplos (28 exemplos)

---

## EXEMPLO DE FORMATO DE RESPOSTA

```json
{{"messages": [
  {{"role": "system", "content": "You are an OCI specialist..."}},
  {{"role": "user", "content": "Como configurar..."}},
  {{"role": "assistant", "content": "Para configurar...\\n\\n1. Step one\\n2. Step two\\n\\n[MUTABLE] Note about prices."}}
], "metadata": {{"category": "example/topic", "difficulty": "intermediate", "source": "generated"}}}}
```

⚠️ **ERRO COMUM**: O metadata deve ficar FORA do array messages, não dentro!

---

## SUA TAREFA

Gere EXATAMENTE 140 exemplos diversos para o topic: **{name}**

- Mistura de dificuldades: 42 beginner, 70 intermediate, 28 advanced
- Cenários reais de OCI - cada exemplo com um caso de uso diferente
- Use Português (BR) para perguntas do usuário
- Formato JSONL, uma linha por exemplo
- SIGA TODAS as regras de qualidade acima
- NÃO repita cenários - cada exemplo deve ser único
"""
    return prompt


def list_topics(topics: list[dict]) -> None:
    """Print all available topics."""
    print(f"\nAvailable topics ({len(topics)} total):\n")
    current_group = ""
    for topic in topics:
        group = topic["name"].split("/")[0]
        if group != current_group:
            print(f"\n  [{group}]")
            current_group = group
        print(f"    {topic['name']}")
    print()


def main():
    parser = argparse.ArgumentParser(description="Generate OCI dataset prompts")
    parser.add_argument("topic", nargs="?", help="Topic name (e.g., compute/instances)")
    parser.add_argument("--list", action="store_true", help="List all available topics")
    parser.add_argument(
        "--all", action="store_true", help="Generate prompts for all topics"
    )
    args = parser.parse_args()

    if not TAXONOMY_FILE.exists():
        print(f"Error: Taxonomy file not found: {TAXONOMY_FILE}")
        sys.exit(1)

    topics = parse_taxonomy(TAXONOMY_FILE)

    if args.list:
        list_topics(topics)
        return

    if args.all:
        TMP_DIR.mkdir(parents=True, exist_ok=True)
        print(f"\nGenerating prompts for {len(topics)} topics...")
        for i, topic in enumerate(topics, 1):
            prompt = generate_prompt(topic)
            filename = f"prompt_{topic['name'].replace('/', '-')}.md"
            output_path = TMP_DIR / filename
            output_path.write_text(prompt)
            print(f"  [{i}/{len(topics)}] {topic['name']} -> {filename}")
        print(f"\nDone! {len(topics)} prompts saved to {TMP_DIR}/")
        return

    if args.topic:
        topic_name = args.topic
        matching = [t for t in topics if t["name"] == topic_name]
        if not matching:
            print(f"Error: Topic '{topic_name}' not found.")
            print("Use --list to see available topics.")
            sys.exit(1)

        topic = matching[0]
        prompt = generate_prompt(topic)
        TMP_DIR.mkdir(parents=True, exist_ok=True)
        filename = f"prompt_{topic['name'].replace('/', '-')}.md"
        output_path = TMP_DIR / filename
        output_path.write_text(prompt)
        print(f"Prompt generated: {output_path}")
        print(f"\nTo execute this prompt, use it with your LLM and save the output to:")
        print(f"  data/curated/{topic['name'].replace('/', '-')}.jsonl")
        return

    parser.print_help()


if __name__ == "__main__":
    main()
