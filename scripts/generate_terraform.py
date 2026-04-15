import json
import random

companies = [
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

projects = [
    "terraform-infrastructure",
    "cloud-migration",
    "infrastructure-as-code",
    "devops-automation",
    "ci-cd-pipeline",
    "infrastructure-refactoring",
    "cost-optimization",
    "security-hardening",
    "multi-region-expansion",
    "disaster-recovery",
    "compliance-audit",
    "hybrid-cloud-integration",
    "container-platform",
    "database-consolidation",
    "network-segmentation",
    "identity-federation",
    "performance-tuning",
    "monitoring-overhaul",
    "backup-strategy",
    "zero-trust-implementation",
    "api-gateway-deployment",
    "serverless-transformation",
    "microservices-refactor",
    "data-lake-modernization",
]

regions = [
    "sa-saopaulo-1",
    "us-ashburn-1",
    "us-phoenix-1",
    "eu-frankfurt-1",
    "uk-london-1",
    "ap-mumbai-1",
    "ap-tokyo-1",
    "ap-sydney-1",
    "ca-toronto-1",
    "me-jeddah-1",
]

personas = [
    "cloud architect",
    "platform engineer",
    "sre",
    "devops engineer",
    "finops analyst",
    "auditor",
    "security lead",
    "dba",
    "infrastructure engineer",
]

intents = [
    "design",
    "troubleshoot",
    "migrate",
    "standardize",
    "optimize",
    "compare",
    "review",
    "remediate",
    "audit",
    "configure",
]

lifecycles = [
    "greenfield",
    "brownfield",
    "produção estável",
    "expansão",
    "incidente",
    "auditoria",
    "standardize",
    "migration",
]

constraints = [
    "sem IP público",
    "multi-região",
    "com budget limitado",
    "mínimo privilégio",
    "integração híbrida",
    "sem downtime",
    "rollback em menos de 15 minutos",
    "com auditoria em 30 dias",
    "alta disponibilidade",
    "baixa latência",
]

difficulties = ["beginner", "intermediate", "advanced"]

compartments = [
    "production",
    "staging",
    "development",
    "security",
    "networking",
    "shared-services",
    "data-platform",
    "sandbox",
    "analytics",
    "devops",
]

shapes = [
    "VM.Standard.E4.Flex",
    "VM.Standard.A1.Flex",
    "VM.Optimized3.Flex",
    "VM.Standard3.Flex",
    "VM.DenseIO.E4.Flex",
    "BM.Standard.E5",
    "BM.GPU4.8",
    "VM.GPU.A10.1",
    "VM.Standard.E2.Micro",
]

random.seed(42)

examples = []
for i in range(250):
    company = random.choice(companies)
    project = random.choice(projects)
    region = random.choice(regions)
    persona = random.choice(personas)
    intent = random.choice(intents)
    lifecycle = random.choice(lifecycles)
    difficulty = random.choice(difficulties)
    compartment = random.choice(compartments)
    constraint = random.choice(constraints)
    shape = random.choice(shapes)

    question = f"Como {persona}, preciso configurar Terraform provider para {company} no projeto {project}, em {compartment}/{region}, considerando {constraint}. Qual abordagem você recomenda?"

    answer = f'''Para configurar o Terraform Provider para {company} no projeto {project}, siga os passos abaixo:

**1. Configuração do Provider:**
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
  region = "{region}"
}}
```

**2. Autenticação:**
O OCI Terraform Provider suporta múltiplos métodos de autenticação:
- **API Key** (recomendado): Configure em `~/.oci/config` ou via variáveis de ambiente
- **Instance Principal**: Use para execução em instâncias OCI com Dynamic Groups
- **Security Token**: Para cenários de federação

**3. Recursos exemplo:**
```hcl
resource "oci_core_instance" "main" {{
  compartment_id = var.compartment_ocid
  display_name   = "terraform-{project[:20]}-{i:03d}"
  shape          = "{shape}"
  
  tags = {{
    project     = "{company} - {project}"
    environment = "{compartment}"
    managed_by  = "terraform"
  }}
}}

variable "compartment_ocid" {{
  type        = string
  description = "OCID do compartment {compartment}"
}}
```

**4. Boas práticas de segurança:**
- Nunca exponha credenciais no código
- Use OCI Vault para secrets
- Aplique princípio de menor privilégio nas policies IAM
- Habilite audit logging para compliance

**5. Deploy:**
```bash
terraform init
terraform plan -var="compartment_ocid=<ocid>"
terraform apply -var="compartment_ocid=<ocid>" -auto-approve
```

**Nota:** [MUTABLE] Preços e limites de shapes variam por região. Verifique sempre o 'Service Limits' no console.

**Doc de referência:** https://registry.terraform.io/providers/oracle/oci/latest/docs'''

    example = {
        "question": question,
        "answer": answer,
        "metadata": {
            "category": "terraform/provider",
            "difficulty": difficulty,
            "persona": persona,
            "intent": intent,
            "lifecycle": lifecycle,
        },
    }
    examples.append(example)

with open(
    "/Users/otaviolemos/ml/olia-2-oci/data/curated/terraform-provider.jsonl", "w"
) as f:
    for example in examples:
        f.write(json.dumps(example, ensure_ascii=False) + "\n")

print(f"Generated {len(examples)} examples")
