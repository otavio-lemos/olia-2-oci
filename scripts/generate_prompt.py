#!/usr/bin/env python3
"""
Gerar prompts prontos para uso na geração de dados.

Uso:
    # Gerar TODOS os prompts
    python scripts/generate_prompt.py --all

    # Gerar prompt para topic específico
    python scripts/generate_prompt.py compute/instances

    # Listar topics disponíveis
    python scripts/generate_prompt.py --list

Saída:
    Um arquivo por topic contendo 10 exemplos em JSONL.
"""

import sys
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
TMP_DIR = PROJECT_ROOT / "tmp"
TMP_DIR.mkdir(exist_ok=True)

QUALITY_RULES_PATH = PROJECT_ROOT / "docs/quality-rules.md"
TAXONOMY_PATH = PROJECT_ROOT / "docs/taxonomy.md"

SYSTEM_PROMPTS = {
    "compute/instances": "You are an OCI specialist with expertise in Compute instances. Provide technical guidance on instance creation, shape selection, SSH access, and lifecycle management.",
    "compute/scaling": "You are an OCI specialist with expertise in Compute scaling. Provide technical guidance on instance pools, auto-scaling, and capacity planning.",
    "compute/custom-images": "You are an OCI specialist with expertise in Compute custom images. Provide technical guidance on custom image creation, boot volumes, and instance templates.",
    "storage/block": "You are an OCI specialist with expertise in Block Volume. Provide technical guidance on block storage creation, attachment, performance tiers, and backups.",
    "storage/object": "You are an OCI specialist with expertise in Object Storage. Provide technical guidance on buckets, pre-authenticated requests, lifecycle policies, and versioning.",
    "storage/file": "You are an OCI specialist with expertise in File Storage. Provide technical guidance on NFS mounts, export options, and file system management.",
    "networking/vcn": "You are an OCI specialist with expertise in VCN networking. Provide technical guidance on VCN design, subnets, internet gateway, and NAT gateway.",
    "networking/security": "You are an OCI specialist with expertise in network security. Provide technical guidance on Security Lists, NSGs, and firewall rules.",
    "networking/connectivity": "You are an OCI specialist with expertise in hybrid connectivity. Provide technical guidance on DRG, VPN IPSec, FastConnect, and VCN peering.",
    "lb/load-balancer": "You are an OCI specialist with expertise in Load Balancing. Provide technical guidance on Load Balancer configuration, backend sets, SSL certificates, and health checks.",
    "database/autonomous": "You are an OCI specialist with expertise in Autonomous Database. Provide technical guidance on ATP/ADW creation, wallet management, connection strings, and backups.",
    "database/autonomous-json": "You are an OCI specialist with expertise in Autonomous JSON Database. Provide technical guidance on document stores, JSON collections, and MongoDB compatibility.",
    "database/mysql": "You are an OCI specialist with expertise in OCI MySQL. Provide technical guidance on MySQL HeatWave, configuration, scaling, and replication.",
    "database/postgresql": "You are an OCI specialist with expertise in OCI PostgreSQL. Provide technical guidance on PostgreSQL instances, scaling, and high availability.",
    "database/nosql": "You are an OCI specialist with expertise in Oracle NoSQL Database. Provide technical guidance on table creation, CRUD operations, and consistency.",
    "database/exadata": "You are an OCI specialist with expertise in Exadata Cloud Service. Provide technical guidance on Exadata infrastructure, DB systems, and maintenance.",
    "container/oke": "You are an OCI specialist with expertise in OKE. Provide technical guidance on Kubernetes cluster creation, node pools, and deployments.",
    "container/instances": "You are an OCI specialist with expertise in Container Instances. Provide technical guidance on container deployment and OCIR registry management.",
    "serverless/functions": "You are an OCI specialist with expertise in OCI Functions. Provide technical guidance on function creation, deployment, and invocation.",
    "serverless/api-gateway": "You are an OCI specialist with expertise in API Gateway. Provide technical guidance on API creation, routes, integrations, and authentication.",
    "security/iam-basics": "You are an OCI security specialist with expertise in IAM basics. Provide technical guidance on compartments, users, groups, and authentication.",
    "security/policies": "You are an OCI security specialist with expertise in policies. Provide technical guidance on policy syntax, statements, and common patterns.",
    "security/dynamic-groups": "You are an OCI security specialist with expertise in Dynamic Groups. Provide technical guidance on dynamic group rules, instance principal, and resource principal.",
    "security/federation": "You are an OCI security specialist with expertise in federation. Provide technical guidance on IdCS, Okta, SAML, and OAuth integration.",
    "security/vault-secrets": "You are an OCI security specialist with expertise in Vault secrets. Provide technical guidance on secret creation, retrieval, and rotation.",
    "security/vault-keys": "You are an OCI security specialist with expertise in Vault keys. Provide technical guidance on key creation, encryption, and key policies.",
    "security/encryption": "You are an OCI security specialist with expertise in encryption. Provide technical guidance on volume encryption, BYOK, and customer-managed keys.",
    "security/cloud-guard": "You are an OCI security specialist with expertise in Cloud Guard. Provide technical guidance on security posture, detector recipes, and responder rules.",
    "security/waf": "You are an OCI security specialist with expertise in WAF. Provide technical guidance on Web Application Firewall configuration, access rules, and protection.",
    "migration/aws-compute": "You are an OCI specialist with expertise in AWS to OCI migration. Provide technical guidance on EC2 to OCI Compute migration.",
    "migration/aws-storage": "You are an OCI specialist with expertise in AWS to OCI migration. Provide technical guidance on S3 to Object Storage migration.",
    "migration/aws-database": "You are an OCI specialist with expertise in AWS to OCI migration. Provide technical guidance on RDS to Autonomous Database migration.",
    "migration/azure-compute": "You are an OCI specialist with expertise in Azure to OCI migration. Provide technical guidance on Azure VMs to OCI Compute migration.",
    "migration/azure-database": "You are an OCI specialist with expertise in Azure to OCI migration. Provide technical guidance on Azure SQL to Autonomous Database migration.",
    "migration/gcp-compute": "You are an OCI specialist with expertise in GCP to OCI migration. Provide technical guidance on GCP Compute Engine to OCI Compute migration.",
    "migration/gcp-storage": "You are an OCI specialist with expertise in GCP to OCI migration. Provide technical guidance on GCP Cloud Storage to OCI Object Storage migration.",
    "migration/gcp-database": "You are an OCI specialist with expertise in GCP to OCI migration. Provide technical guidance on GCP Cloud SQL to OCI Database migration.",
    "migration/onprem-compute": "You are an OCI specialist with expertise in on-premises to OCI migration. Provide technical guidance on VM migration to OCI Compute.",
    "migration/onprem-storage": "You are an OCI specialist with expertise in on-premises to OCI migration. Provide technical guidance on file storage migration to OCI.",
    "migration/onprem-vmware": "You are an OCI specialist with expertise in on-premises to OCI migration. Provide technical guidance on VMware migration and lift-and-shift patterns.",
    "migration/onprem-database": "You are an OCI specialist with expertise in on-premises to OCI migration. Provide technical guidance on Oracle to Autonomous Database migration and ZDM.",
    "migration/data-transfer": "You are an OCI specialist with expertise in data migration. Provide technical guidance on GoldenGate, Data Integration, and large-scale data transfers.",
    "terraform/provider": "You are an OCI Terraform specialist with expertise in provider configuration. Provide technical guidance on authentication and provider settings.",
    "terraform/compute": "You are an OCI Terraform specialist with expertise in compute resources. Provide technical guidance on instance, instance pool, custom images, and auto-scaling.",
    "terraform/storage": "You are an OCI Terraform specialist with expertise in storage resources. Provide technical guidance on block volume, object storage, and file storage.",
    "terraform/networking": "You are an OCI Terraform specialist with expertise in networking resources. Provide technical guidance on VCN, subnet, security lists, and gateways.",
    "terraform/load-balancer": "You are an OCI Terraform specialist with expertise in load balancer resources. Provide technical guidance on load balancer, backend sets, and SSL certificates.",
    "terraform/database": "You are an OCI Terraform specialist with expertise in database resources. Provide technical guidance on Autonomous Database, MySQL, PostgreSQL, NoSQL, and Exadata.",
    "terraform/container": "You are an OCI Terraform specialist with expertise in container resources. Provide technical guidance on OKE clusters, node pools, and container instances.",
    "terraform/serverless": "You are an OCI Terraform specialist with expertise in serverless resources. Provide technical guidance on Functions and API Gateway.",
    "terraform/security": "You are an OCI Terraform specialist with expertise in security resources. Provide technical guidance on Vault, Cloud Guard, WAF, and encryption.",
    "terraform/observability": "You are an OCI Terraform specialist with expertise in observability resources. Provide technical guidance on logging, monitoring, and APM.",
    "terraform/devops": "You are an OCI Terraform specialist with expertise in DevOps resources. Provide technical guidance on DevOps, artifacts, and Resource Manager.",
    "terraform/state": "You are an OCI Terraform specialist with expertise in state management. Provide technical guidance on remote state and workspaces.",
    "observability/logging": "You are an OCI specialist with expertise in Logging. Provide technical guidance on log groups, custom logs, and audit logs.",
    "observability/monitoring": "You are an OCI specialist with expertise in Monitoring. Provide technical guidance on metrics, alarms, and notifications.",
    "observability/stack-monitoring": "You are an OCI specialist with expertise in Stack Monitoring. Provide technical guidance on enterprise monitoring and resource monitoring.",
    "observability/apm": "You are an OCI specialist with expertise in APM. Provide technical guidance on distributed tracing and performance diagnostics.",
    "troubleshooting/connectivity": "You are an OCI troubleshooting specialist with expertise in connectivity. Provide diagnostic guidance on network accessibility, routing, and DNS issues.",
    "troubleshooting/performance": "You are an OCI troubleshooting specialist with expertise in performance. Provide diagnostic guidance on CPU, memory, storage, and network performance.",
    "troubleshooting/authentication": "You are an OCI troubleshooting specialist with expertise in authentication. Provide diagnostic guidance on IAM policies, MFA, and federation issues.",
    "troubleshooting/database": "You are an OCI troubleshooting specialist with expertise in database. Provide diagnostic guidance on connection issues, TNS errors, and wallet problems.",
    "troubleshooting/compute": "You are an OCI troubleshooting specialist with expertise in compute. Provide diagnostic guidance on provisioning, boot volumes, and SSH issues.",
    "troubleshooting/storage": "You are an OCI troubleshooting specialist with expertise in storage. Provide diagnostic guidance on bucket access and performance issues.",
    "troubleshooting/oke": "You are an OCI troubleshooting specialist with expertise in OKE. Provide diagnostic guidance on cluster, node pool, and worker node issues.",
    "troubleshooting/functions": "You are an OCI troubleshooting specialist with expertise in Functions. Provide diagnostic guidance on invocation errors and API Gateway issues.",
    "devops/ci-cd": "You are an OCI DevOps specialist with expertise in CI/CD. Provide technical guidance on build pipelines, deploy pipelines, and artifacts.",
    "devops/resource-manager": "You are an OCI DevOps specialist with expertise in Resource Manager. Provide technical guidance on Terraform stacks and drift detection.",
    "devops/artifacts": "You are an OCI DevOps specialist with expertise in Artifacts. Provide technical guidance on OCIR and container registry.",
    "devops/secrets": "You are an OCI DevOps specialist with expertise in secrets. Provide technical guidance on Vault integration and secret injection.",
}


def get_topics_from_taxonomy(taxonomy_path: Path) -> list:
    """Extract all topics from taxonomy."""
    content = taxonomy_path.read_text()
    topics = []
    for line in content.split("\n"):
        if line.startswith("#### "):
            topic = line.replace("#### ", "").strip()
            topic = re.sub(r"\s*\(\d+\)\s*$", "", topic)
            topics.append(topic)
    return topics


def get_topic_from_taxonomy(taxonomy_path: Path, topic: str) -> str:
    """Extract topic section from taxonomy."""
    content = taxonomy_path.read_text()
    topic_clean = re.sub(r"\s*\(\d+\)\s*$", "", topic)
    lines = content.split("\n")
    in_topic = False
    topic_lines = []
    for line in lines:
        if line.startswith("#### "):
            if in_topic:
                break
            line_clean = re.sub(r"\s*\(\d+\)\s*$", "", line)
            if topic_clean in line_clean:
                in_topic = True
                topic_lines.append(line)
        elif in_topic:
            if line.startswith("### ") or line.startswith("## "):
                break
            topic_lines.append(line)
    return "\n".join(topic_lines)


def generate_prompt(topic: str) -> str:
    """Generate the complete prompt for a topic."""
    quality_rules = QUALITY_RULES_PATH.read_text()
    topic_info = get_topic_from_taxonomy(TAXONOMY_PATH, topic)
    system_prompt = SYSTEM_PROMPTS.get(topic, "You are an OCI specialist.")

    prompt = f"""# OCI Dataset Generation - {topic}

## QUALITY RULES (OBRIGATÓRIO - SIGA À RISCA)

{quality_rules}

---

## TOPIC: {topic}

{topic_info}

---

## SYSTEM PROMPT (para usar no JSONL)

{system_prompt}

---

## SUAS REGRAS DE EXECUÇÃO

1. Você DEVE seguir OBRIGATORIAMENTE todas as regras em "QUALITY RULES" acima
2. Gere APENAS exemplos para o topic "{topic}"
3. Use APENAS as informações presentes em "TOPIC: {topic}"
4. Não invente informações que não estão nos docs OCI
5. Não use preços ou limites sem marcar [MUTABLE] ou [CHECK DOCS]

---

## OUTPUT FORMAT

Gere EXATAMENTE 10 exemplos em formato JSONL.

**UM objeto JSON por linha** - cada linha é um objeto JSON completo.

```
{{"messages": [...], "metadata": {{"category": "{topic}", "difficulty": "beginner|intermediate|advanced", "source": "generated"}}}}
{{"messages": [...], "metadata": {{"category": "{topic}", "difficulty": "beginner|intermediate|advanced", "source": "generated"}}}}
... (10 linhas total)
```

---

## JSONL RULES (CRÍTICO)

1. **UM objeto JSON por linha** - sem arrays, sem wrapper
2. **Escape todas as aspas dentro de strings**: " -> \\"
3. **Escape newlines dentro de strings**: newline real -> \\n
4. **Escape backslashes**: \\ -> \\\\
5. **metadata é OBRIGATÓRIO** em cada objeto
6. **metadata deve ficar FORA do array messages!**

**ESTRUTURA CORRETA:**
```json
{{"messages": [
  {{"role": "system", "content": "..."}},
  {{"role": "user", "content": "..."}},
  {{"role": "assistant", "content": "..."}}
], "metadata": {{"category": "...", "difficulty": "...", "source": "generated"}}}}
```

**ESTRUTURA ERRADA (não faça assim!):**
```json
{{"messages": [
  {{"role": "system", "content": "..."}},
  {{"role": "user", "content": "..."}},
  {{"role": "assistant", "content": "..."}},
  {{"metadata": {{"category": "..."}}}}  <-- ERRADO!
]
}}
```

---

## DISTRIBUIÇÃO DE DIFICULDADE
- beginner: ~30% dos exemplos
- intermediate: ~50% dos exemplos
- advanced: ~20% dos exemplos

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

Gere EXATAMENTE 10 exemplos diversos para o topic: **{topic}**

- Mistura de dificuldades beginner, intermediate, advanced
- Cenários reais de OCI
- Use Português (BR) para perguntas do usuário
- Formato JSONL, uma linha por exemplo
- SIGA TODAS as regras de qualidade acima
"""

    return prompt


def list_topics():
    """Lista todos os topics disponíveis."""
    topics = get_topics_from_taxonomy(TAXONOMY_PATH)
    print(f"\nTopics disponíveis ({len(topics)} total):\n")
    for topic in topics:
        print(f"  - {topic}")
    print(f"\nUso:")
    print(f"  python scripts/generate_prompt.py compute/instances")
    print(f"  python scripts/generate_prompt.py --all")


def generate_all_prompts():
    """Gera prompts para todos os topics."""
    topics = get_topics_from_taxonomy(TAXONOMY_PATH)
    print(f"\nGerando prompts para {len(topics)} topics...\n")
    for i, topic in enumerate(topics, 1):
        print(f"[{i}/{len(topics)}] {topic}...", end=" ")
        prompt = generate_prompt(topic)
        output_file = TMP_DIR / f"prompt_{topic.replace('/', '-')}.md"
        output_file.write_text(prompt)
        print(f"✓ salvo em {output_file.name}")
    print(f"\n✅ Todos os prompts gerados em: {TMP_DIR}/")
    print(f"\nSaída: 1 arquivo por topic em data/curated/[topic].jsonl")


def main():
    if len(sys.argv) == 1 or sys.argv[1] == "--all":
        generate_all_prompts()
    elif sys.argv[1] == "--list":
        list_topics()
    elif sys.argv[1] == "--help":
        print(__doc__)
    elif len(sys.argv) == 2:
        topic = sys.argv[1]
        print(f"Gerando prompt para topic: {topic}\n")
        prompt = generate_prompt(topic)
        output_file = TMP_DIR / f"prompt_{topic.replace('/', '-')}.md"
        output_file.write_text(prompt)
        print(f"Prompt salvo em: {output_file}")
        print(f"\n{'=' * 60}\n")
        print(prompt)
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
