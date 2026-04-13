#!/usr/bin/env python3
"""Generate Cycle 2 OCI examples with IMPROVED CLARITY.

Focus categories: Terraform, Governance (regression areas from Cycle 1)
Target: clarity 3.19 -> 3.40+
"""

import json
import random
from pathlib import Path

random.seed(42)

TERRAFORM_GUIDES = {
    "terraform/networking": """Para networking com Terraform, você precisa:

1. Criar o VCN:
```hcl
resource "oci_core_vcn" "main" {
  compartment_id = var.compartment_id
  display_name = "vcn-projeto"
  cidr_blocks   = ["10.0.0.0/16"]
}
```

2. Subnets (pública e privada):
```hcl
resource "oci_core_subnet" "public" {
  compartment_id = var.compartment_id
  vcn_id        = oci_core_vcn.main.id
  display_name  = "public-subnet"
  cidr_block   = "10.0.1.0/24"
}
```

3. Internet Gateway para acesso externo.

Dica: Use tags para organização desde o início.""",
    "terraform/compute": """Para compute, você tem VM ou Bare Metal:

**VM (mais comum):**
```hcl
resource "oci_core_instance" "vm" {
  compartment_id = var.compartment_id
  display_name  = "vm-projeto"
  shape        = "VM.Standard.E4.Flex"
  create_vnic_details {
    subnet_id = oci_core_subnet.private.id
  }
}
```

**Bare Metal (workloads pesados):**
```hcl
resource "oci_core_instance" "bm" {
  compartment_id = var.compartment_id
  display_name  = "bm-projeto"
  shape        = "BM.Standard.E5"
  shape_config {
    ocpus = 32
    memory = 128
  }
}
```

Flex shapes são ideais para dev/test — você paga apenas o que usa.""",
    "terraform/storage": """Para storage:

**Block Volume:**
```hcl
resource "oci_core_volume" "data" {
  compartment_id = var.compartment_id
  display_name  = "volume-projeto"
  size_in_gbs  = 100
}
```

**Object Storage:**
```hcl
resource "oci_objectstorage_bucket" "main" {
  compartment_id = var.compartment_id
  name        = "bucket-projeto"
  namespace   = var.namespace
}
```

Object é mais barato para arquivos — use lifecycle policies para Archive.""",
}

GOVERNANCE_GUIDES = {
    "governance/tagging": """Tagging é essencial para custos:

```hcl
tags = {
  project     = var.project
  environment = var.environment
  managed_by  = "terraform"
}
```

Aplique em todos os recursos. Documente a convenção no wiki do projeto.""",
    "governance/compartments": """Estrutura recomendada:

```
root
├── production/
├── staging/
├── development/
└── sandbox/
```

Cada um com políticas específicas. Comece simples e refine conforme cresce.""",
}


def generate_example(
    category: str, company: str, project: str, region: str, comp: str
) -> dict:
    """Generate one example with conversational tone."""

    if category.startswith("terraform"):
        guide = TERRAFORM_GUIDES.get(category, TERRAFORM_GUIDES["terraform/networking"])
    else:
        guide = GOVERNANCE_GUIDES.get(category, "")
        if not guide:
            guide = GOVERNANCE_GUIDES["governance/tagging"]

    introductions = [
        f"Olá! Vou te explicar sobre {category.split('/')[-1]} para {company}.",
        f"Bom pergunta! Aqui está o que funciona bem:",
    ]
    intro = random.choice(introductions)

    steps = "Vamos passo a passo:\n\n"

    warnings = [
        "\n\n⚠️ Atenç��o: Valide na região de produção antes de aplicar.",
        "\n\n⚠️ Cuidado: Esse comando muda estado — faça backup.",
    ]
    warning = random.choice(warnings)

    response = f"""{intro}

{steps}{guide}{warning}"""

    cat_clean = category.replace("terraform/", "").replace("governance/", "")
    question = f"""Sou architect e preciso configurar {cat_clean} para {company} no projeto {project}, em {comp}/{region}. Como devo proceder?"""

    return {
        "messages": [
            {
                "role": "system",
                "content": "Você é especialista em OCI. Responda de forma clara e prática como um arquiteto sênior explicando para um colega. Evite linguagem burocrática.",
            },
            {"role": "user", "content": question},
            {"role": "assistant", "content": response},
        ],
        "metadata": {
            "category": category,
            "difficulty": "intermediate",
            "company": company,
            "project": project,
            "source": "cycle2-generated",
        },
    }


def main():
    """Generate Cycle 2 examples."""

    categories = [
        "terraform/networking",
        "terraform/compute",
        "terraform/storage",
        "governance/tagging",
        "governance/compartments",
    ]

    output_dir = Path("data/curated_cycle2")
    output_dir.mkdir(exist_ok=True)

    companies = ["TechCorp Brasil", "DataFlow Solutions", "CloudNative Inc"]
    projects = ["ecommerce-migration", "data-lake", "modernization"]
    regions = ["sa-saopaulo-1", "us-ashburn-1"]
    comps = ["production", "development"]

    examples_per_category = 100

    total = 0
    for category in categories:
        examples = []
        for _ in range(examples_per_category):
            ex = generate_example(
                category,
                random.choice(companies),
                random.choice(projects),
                random.choice(regions),
                random.choice(comps),
            )
            examples.append(ex)

        safe_name = category.replace("/", "-")
        output_file = output_dir / f"{safe_name}.jsonl"
        with open(output_file, "w", encoding="utf-8") as f:
            for ex in examples:
                f.write(json.dumps(ex, ensure_ascii=False) + "\n")

        print(f"✅ {category}: {len(examples)} -> {output_file}")
        total += len(examples)

    print(f"\n🎯 Total: {total} examples in {output_dir}/")


if __name__ == "__main__":
    main()
