#!/usr/bin/env python3
"""Regenerate migration-azure-compute.jsonl with high-quality pattern - specific to Azure→OCI mapping."""

import json

MAPPINGS = {
    "vm": {
        "azure": "VM instances",
        "oci": "OCI Compute",
        "desc": "Azure VMs são compute virtualizado. OCI Compute oferece VMs e Bare Metal com shapes flexíveis.",
    },
    "availability sets": {
        "azure": "Availability Sets",
        "oci": "Fault Domains + Availability Domains",
        "desc": "Azure Availability Sets fornecem isolamento de falhas dentro de um datacenter. OCI equivalent são Fault Domains (FDs) - grupos de hardware independentes dentro de um Availability Domain.",
    },
    "scale sets": {
        "azure": "Scale Sets",
        "oci": "Instance Pools + Auto Scaling",
        "desc": "Azure Scale Sets permitem VMs idênticas com auto-scaling. OCI usa Instance Pools para distribuição e Auto Scaling service para elasticidade.",
    },
    "managed disks": {
        "azure": "Managed Disks",
        "oci": "Block Volumes",
        "desc": "Azure Managed Disks são storage persistente Gerenciado. OCI Block Volumes oferecem performance configurável (VL, HP, FP) com backups automáticos.",
    },
    "vnet": {
        "azure": "VNETs",
        "oci": "VCNs",
        "desc": "Azure Virtual Networks isolam recursos. OCI Virtual Cloud Networks (VCNs) oferecem modelo similar com subnets, gateways e security lists.",
    },
    "nsg": {
        "azure": "NSGs",
        "oci": "Security Lists",
        "desc": "Azure Network Security Groups controlam tráfego. OCI Security Lists definem regras stateless para subnets em uma VCN.",
    },
    "spot": {
        "azure": "Spot VMs",
        "oci": "Preemptible Instances",
        "desc": "Azure Spot VMs oferecem desconto significativo com possibilidade de preempt. OCI Preemptible tem modelo similar com discount até 90%.",
    },
    "dedicated hosts": {
        "azure": "Dedicated Hosts",
        "oci": "Dedicated Compute Hosts",
        "desc": "Azure Dedicated Hosts fornecem server isolado físico. OCI Dedicated Compute Host oferece isolamento total para compliance.",
    },
    "vm images": {
        "azure": "VM images",
        "oci": "Custom Images",
        "desc": "Azure VM images generalized para reuse. OCI Custom Images permite criar templates de boot volumes para deploy rápido.",
    },
    "vm extensions": {
        "azure": "VM Extensions",
        "oci": "Cloud-Init",
        "desc": "Azure VM Extensions configuram pós-provisionamento. OCI suporta cloud-init para configuração declarativa de instâncias.",
    },
}


def extract_topic(question: str) -> tuple:
    """Extract Azure topic and difficulty from question."""
    q = question.lower()

    if any(kw in q for kw in ["troubleshoot", "incidente", "optimize", "advanced"]):
        difficulty = "advanced"
    elif any(kw in q for kw in ["migrate", "config", "setup", "implement"]):
        difficulty = "intermediate"
    else:
        difficulty = "beginner"

    topic = "vm"
    for k in MAPPINGS:
        if k in q:
            topic = k
            break

    return topic, difficulty


def generate_answer(question: str, meta: dict) -> str:
    """Generate high-quality answer based on question and metadata."""
    topic, _ = extract_topic(question)
    mapping = MAPPINGS.get(topic, MAPPINGS["vm"])
    difficulty = meta.get("difficulty", "intermediate")
    persona = meta.get("persona", "cloud architect")
    intent = meta.get("intent", "migrate")

    persona_intros = {
        "cloud architect": "Como cloud architect, considere a arquitetura completa",
        "platform engineer": "Do ponto de vista de engenharia de plataforma",
        "sre": "Para garantia de disponibilidade e performance",
        "dba": "Para considerações de dados e storage",
        "security lead": "Para controles de segurança",
        "finops analyst": "Para análise de custos e otimização",
        "auditor": "Para compliance e auditoria",
    }

    intro = persona_intros.get(persona, persona_intros["cloud architect"])

    if intent == "migrate":
        answer = f"""**Migração {mapping["azure"]} → {mapping["oci"]}**

{intro}:

1. **Análise**: Documente todos os {mapping["azure"]} no Azure (configurações, networking, dependências).

2. **Mapeamento**:
{mapping["desc"]}

3. **Provisionamento OCI** via CLI:
```bash
oci compute instance launch \\
    --compartment-id <COMPARTMENT_OCID> \\
    --shape VM.Standard.E4.Flex \\
    --subnet-id <SUBNET_OCID> \\
    --availability-domain AD-1
```

4. **Migração de Dados**: Use Object Storage como staging. Para grandes volumes, use Data Transfer Service.

5. **Validação**: Teste funcionalidade e performance antes do cutover.

**Nota**: [MUTABLE] Custos de {mapping["oci"]} variam por região. Verifique em https://www.oracle.com/cloud/pricing/.
**Doc**: https://docs.oracle.com/en-us/iaas/Content/Compute/Concepts/computeoverview.htm"""

    elif intent == "compare":
        answer = f"""**Comparativo {mapping["azure"]} vs {mapping["oci"]}**

| Aspecto | {mapping["azure"]} (Azure) | {mapping["oci"]} (OCI) |
|--------|---------------------------|-------------------|
| Gerenciamento | Managed | Block/Self-managed |
| Scaling | Scale Sets | Instance Pools |
| Alta Disponibilidade | Availability Sets | Fault Domains |
| Rede | VNET/Subnet | VCN/Subnet |

**CLI Equivalent**:
```bash
oci compute instance launch \\
    --compartment-id <OCID> \\
    --shape VM.Standard.E4.Flex \\
    --shape-config '{{"ocpus": 2, "memoryInGBs": 16}}'
```

**Dica**: OCI Shapes Flexíveis permitem dimensionamento granular de CPU e memória.

**Nota**: [MUTABLE] Limits de serviço variam por região - verifique no Console."""

    elif intent == "troubleshoot":
        answer = f"""**Troubleshooting: {mapping["azure"]} → {mapping["oci"]}**

1. **Diagnóstico**: Verifique o status no OCI Console ou via CLI:
```bash
oci compute instance list --compartment-id <OCID> --lifecycle-state RUNNING
```

2. **Logs**: Use OCI Logging:
```bash
oci logging log get --log-id <LOG_OCID>
```

3. **Network**: Verify VCN e Security Lists:
```bash
oci network vcn list --compartment-id <OCID>
```

**Common Issues**:
- Instance não conecta → Check subnet routing e security lists
- Performance lenta → Verify shape size e tenant limits
- Boot falha → Check boot volume e image

**Doc**: https://docs.oracle.com/en-us/iaas/Content/Logging/"""

    elif intent == "audit":
        answer = f"""**Auditoria: {mapping["azure"]} → {mapping["oci"]}**

Para compliance e auditoria:

1. **Inventário**:
```bash
oci compute instance list --compartment-id <OCID>
```

2. **Tags** para chargeback:
```bash
oci compute instance update \\
    --instance-id <OCID> \\
    --freeform-tags 'environment=prod,cost-center=12345'
```

3. **Auditoria**:
```bash
oci audit event list --compartment-id <OCID>
```

**Políticas IAM Required**:
```json
{{
  "statement": [
    "Allow group Auditors to inspect all-resources in compartment"
  ]
}}
```

**Doc**: https://docs.oracle.com/en-us/iaas/Content/Logging/"""

    else:
        answer = f"""**Migração {mapping["azure"]} → {mapping["oci"]}**

{intro}:

1. **Setup Inicial**: Configure compartment e VCN:
```bash
oci iam compartment create --name migration --compartment-id root
oci network vcn create --cidr-block 10.0.0.0/16
```

2. **Provisionamento**:
```bash
oci compute instance launch \\
    --compartment-id <OCID> \\
    --shape VM.Standard.E4.Flex
```

3. **Validação**: Teste conectividade e aplicação.

**Melhores Práticas**:
- Use tags para organização
- Configure monitoring alerts
- Implemente backup automatizado

**Nota**: [MUTABLE] Verifique pricing em https://www.oracle.com/cloud/pricing/"""

    return answer


def main():
    input_file = (
        "/Users/otaviolemos/ml/olia-2-oci/data/curated/migration-azure-compute.jsonl"
    )
    output_file = (
        "/Users/otaviolemos/ml/olia-2-oci/data/curated/migration-azure-compute.jsonl"
    )

    with open(input_file, "r") as f:
        lines = f.readlines()

    results = []
    for i, line in enumerate(lines):
        data = json.loads(line)

        # Extract question - handle different formats
        if "messages" in data and len(data.get("messages", [])) >= 3:
            question = data["messages"][1]["content"]
            meta_input = data.get("metadata", {})
        elif "question" in data:
            question = data.get("question", "")
            meta_input = data.get("metadata", {})
        else:
            continue

        # Extract topic
        topic, inferred_difficulty = extract_topic(question)
        q_lower = question.lower()

        # Use or infer persona
        persona = meta_input.get("persona", "")
        if not persona:
            if "cloud architect" in q_lower:
                persona = "cloud architect"
            elif "platform engineer" in q_lower:
                persona = "platform engineer"
            elif "sre" in q_lower:
                persona = "sre"
            elif "dba" in q_lower:
                persona = "dba"
            elif "security" in q_lower:
                persona = "security lead"
            elif "finops" in q_lower:
                persona = "finops analyst"
            elif "auditor" in q_lower:
                persona = "auditor"
            else:
                persona = "cloud architect"

        # Use or infer difficulty
        difficulty = meta_input.get("difficulty", inferred_difficulty)

        # Use or infer lifecycle
        lifecycle = meta_input.get("lifecycle_stage", "")
        if not lifecycle:
            if "greenfield" in q_lower:
                lifecycle = "greenfield"
            elif "brownfield" in q_lower or "expansão" in q_lower:
                lifecycle = "brownfield"
            elif "incidente" in q_lower:
                lifecycle = "incidente"
            elif "auditoria" in q_lower:
                lifecycle = "auditoria"
            elif "produção estável" in q_lower:
                lifecycle = "produção estável"
            elif "desativação" in q_lower:
                lifecycle = "desativação"
            else:
                lifecycle = "greenfield"

        # Use or infer intent
        intent = meta_input.get("intent", "")
        if not intent:
            if "migrar" in q_lower and "para" in q_lower:
                intent = "migrate"
            elif "mapear" in q_lower or "compar" in q_lower:
                intent = "compare"
            elif "validar" in q_lower or "revis" in q_lower:
                intent = "review"
            elif "troubleshoot" in q_lower or "resolve" in q_lower:
                intent = "troubleshoot"
            elif "disaster" in q_lower or "recovery" in q_lower:
                intent = "recover"
            elif "audit" in q_lower:
                intent = "audit"
            elif "security" in q_lower:
                intent = "remediate"
            else:
                intent = "migrate"

        # Build metadata
        metadata = {
            "category": "migration/azure-compute",
            "difficulty": difficulty,
            "persona": persona,
            "intent": intent,
            "lifecycle": lifecycle,
        }

        # Generate answer
        new_answer = generate_answer(question, metadata)

        result = {"question": question, "answer": new_answer, "metadata": metadata}
        results.append(result)

        if (i + 1) % 50 == 0:
            print(f"Processed {i + 1} lines...")

    # Write output
    with open(output_file, "w") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"Done! Generated {len(results)} high-quality examples")
    print(f"Output: {output_file}")


if __name__ == "__main__":
    main()
