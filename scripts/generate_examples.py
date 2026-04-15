#!/usr/bin/env python3
import json
import random

# Define possible values for metadata fields
categories = [
    "devops/resource-manager",
    "devops/terraform",
    "devops/ci-cd",
    "devops/vault",
    "devops/workspaces",
    "devops/drift",
    "devops/state-backend",
    "devops/modules",
    "devops/variables",
    "devops/outputs",
    "devops/approval",
    "devops/gitops",
    "devops/secrets",
    "devops/troubleshooting",
]

difficulties = ["beginner", "intermediate", "advanced"]
personas = [
    "infrastructure engineer",
    "cloud architect",
    "devops engineer",
    "platform engineer",
    "sre",
    "dba",
    "finops analyst",
    "security lead",
    "auditor",
]
intents = [
    "design",
    "troubleshoot",
    "optimize",
    "review",
    "recover",
    "migrate",
    "remediate",
    "standardize",
    "audit",
    "compare",
    "detect",
]
lifecycles = [
    "greenfield",
    "brownfield",
    "produção estável",
    "standardization",
    "desativação",
    "auditoria",
    "incidente",
    "expansão",
]

# Templates for questions and answers
templates = [
    {
        "question_pattern": "Sou {persona} na {company} e preciso {action} no projeto {project}, em {region}. Qual abordagem você recomenda?",
        "answer_pattern": "Para {topic}:\n\n1. **Passo 1**: {step1}\n2. **Passo 2**: {step2}\n3. **Passo 3**: {step3}\n4. **Passo 4**: {step4}\n\n**Dica**: {tip}\n\n**Referência**: {reference}",
    },
    {
        "question_pattern": "Como {persona} devo {action} usando OCI Resource Manager no ambiente {region}?",
        "answer_pattern": "Para {topic} com Resource Manager:\n\n1. **Configure o Stack**: {step1}\n2. **Defina variáveis**: {step2}\n3. **Execute o job**: {step3}\n4. **Monitore resultados**: {step4}\n\n**Observação**: [MUTABLE] limites podem variar. [CHECK DOCS] para valores atualizados.\n\n**Referência**: {reference}",
    },
]

companies = [
    "CloudNative Inc",
    "GameForge Studios",
    "TechCorp Brasil",
    "DataFlow Solutions",
    "BioResearch Labs",
    "SecureBank Corp",
    "InsureTech Plus",
    "FinServe Digital",
    "LegalDoc Manager",
    "HealthTech Systems",
    "EnergyGrid Monitor",
    "FoodChain Trace",
    "SmartCity IoT",
    "MediaStream Pro",
    "AutoDrive Systems",
    "TravelHub Platform",
    "EduPlatform Global",
    "AgriTech Innovations",
    "FinServe Digital",
    "RetailMax Online",
]

regions = [
    "us-phoenix-1",
    "us-ashburn-1",
    "eu-frankfurt-1",
    "ap-tokyo-1",
    "ap-mumbai-1",
    "ap-sydney-1",
    "me-jeddah-1",
    "sa-saopaulo-1",
    "ca-toronto-1",
    "uk-london-1",
    "ap-seoul-1",
    "ap-singapore-1",
    "il-jerusalem-1",
    "za-johannesburg-1",
]

actions = [
    "provisionar infraestrutura de forma declarativa",
    "construir pipelines de CI/CD com Terraform",
    "automatizar provisioning via CLI e pipelines",
    "gerenciar secrets com OCI Vault",
    "configurar workspaces no Resource Manager",
    "detectar drift no Resource Manager",
    "configurar state backend no Object Storage",
    "usar módulos Terraform",
    "gerenciar variáveis de ambiente",
    "exportar outputs entre stacks",
    "configurar approval manual para jobs",
    "versionar stacks com Git",
    "debugar falhas de apply",
    "monitorar jobs e manter stability",
]

projects = [
    "hybrid-cloud-integration",
    "api-gateway-deployment",
    "container-platform",
    "network-segmentation",
    "cost-optimization",
    "backup-strategy",
    "performance-tuning",
    "monitoring-overhaul",
    "identity-federation",
    "data-lake-modernization",
    "zero-trust-implementation",
    "multi-region-expansion",
    "database-consolidation",
    "ecommerce-migration",
    "disaster-recovery-setup",
    "security-hardening",
    "game-platform-scaling",
    "iot-device-management",
    "analytics-platform",
    "microservices-migration",
]

topics = [
    "criar um Stack do Resource Manager",
    "configurar detecção automática de drift",
    "gerenciar secrets com OCI Vault",
    "usar módulos Terraform",
    "configurar state backend",
    "definir variáveis de ambiente",
    "exportar outputs entre stacks",
    "configurar approval manual",
    "versionar stacks com Git",
    "debugar falhas de apply",
    "monitorar jobs de terraform",
    "gerenciar workspaces por ambiente",
    "resolver dependências circulares",
    "usar taint para forçar recreação",
    "importar recursos existentes",
    "limitar concorrência de jobs",
    "configurar notificações de job",
    "usar políticas de tagging",
    "otimizar performance de apply",
    "gerenciar drift detection schedule",
]

steps_options = [
    [
        "Acesse Resource Manager → Stacks e clique em Create Stack",
        "Selecione a origem: GitHub, Object Storage ou Manual",
        "Defina variáveis incluindo [MUTABLE] region e compartment_ocid",
        "Selecione ou crie workspace para o ambiente",
    ],
    [
        "Crie o Vault no compartment desejado",
        "Crie secrets para credenciais sensíveis",
        "Configure o provider OCI com secret_extraction_enabled = true",
        "Referencie secrets nos recursos Terraform usando data sources",
    ],
    [
        "Crie bucket no Object Storage com versioning habilitado",
        "Configure backend terraform com bucket e prefix",
        "Defina policies IAM para acesso ao bucket",
        "Migre state local para o backend remoto se necessário",
    ],
    [
        "Defina variáveis no arquivo variables.tf com descrições claras",
        "Marque variáveis sensíveis com sensitive = true",
        "Passe valores via CLI ou .tfvars por ambiente",
        "Valide variáveis com tflint antes do apply",
    ],
    [
        "Crie outputs para recursos que serão referenciados",
        "Marque outputs sensíveis conforme necessário",
        "Use data sources para referenciar outputs de outros stacks",
        "Exporte outputs para pipelines de CI/CD como variáveis",
    ],
    [
        "Crie policy IAM para grupo de approvers",
        "Marque job como requiring manual approval na criação",
        "Desenvolvedor submete plano que fica em WAITING_FOR_APPROVAL",
        "Approver revisa e aprova ou rejeita o job",
    ],
    [
        "Estruture repositório com main.tf, variables.tf, outputs.tf",
        "Organize ambientes em diretórios com terraform.tfvars",
        "Configure CI/CD com GitHub Actions ou GitLab CI",
        "Ignore .tfstate e .terraform no .gitignore",
    ],
    [
        "Verifique logs do job no Console ou via CLI",
        "Procure por mensagens de erro específicas",
        "Resolva problemas comuns como limites ou permissões",
        "Use TF_LOG=TRACE para debug detalhado se necessário",
    ],
]

tips_options = [
    "Use .tfvars para variáveis por ambiente (dev.tfvars, prod.tfvars)",
    "Nunca commite .tfstate no git - use backend remoto",
    "Pin versões de módulos para evitar breaking changes",
    "Sempre rode terraform plan antes de apply",
    "Use dependências explícitas apenas quando absolutamente necessário",
    "Isolese ambientes usando workspaces ou compartments separados",
    "Rotate secrets periodicamente e use versões do Vault",
    "Mantenha documentação atualizada junto com o código",
    "Implemente drift detection automático para ambientes de produção",
    "Use命名 conventions consistentes para resources e variáveis",
]

references = [
    "https://docs.oracle.com/en-us/iaas/Content/ResourceManager/Concepts/resourcemanager.htm",
    "https://docs.oracle.com/en-us/iaas/Content/KeyManagement/Concepts/vault.htm",
    "https://docs.oracle.com/en-us/iaas/Content/ResourceManager/Concepts/remotestates.htm",
    "https://docs.oracle.com/en-us/iaas/Content/ResourceManager/Concepts/workspaces.htm",
    "https://docs.oracle.com/en-us/iaas/Content/ResourceManager/Tasks/detectingdrift.htm",
    "https://docs.oracle.com/en-us/iaas/Content/ResourceManager/Tasks/rmusing.htm",
    "https://www.terraform.io/language/modules",
    "https://www.terraform.io/language/values/variables",
    "https://www.terraform.io/language/values/outputs",
    "https://www.terraform.io/intro/core-workflow",
]


def generate_example(idx):
    # Select random values
    category = random.choice(categories)
    difficulty = random.choice(difficulties)
    persona = random.choice(personas)
    intent = random.choice(intents)
    lifecycle = random.choice(lifecycles)
    company = random.choice(companies)
    region = random.choice(regions)
    action = random.choice(actions)
    project = random.choice(projects)
    topic = random.choice(topics)
    steps = random.choice(steps_options)
    tip = random.choice(tips_options)
    reference = random.choice(references)

    # Select template
    template = random.choice(templates)

    # Format question and answer
    question = template["question_pattern"].format(
        persona=persona, company=company, action=action, project=project, region=region
    )

    answer = template["answer_pattern"].format(
        topic=topic,
        step1=steps[0],
        step2=steps[1],
        step3=steps[2],
        step4=steps[3],
        tip=tip,
        reference=reference,
    )

    # Create metadata
    metadata = {
        "category": category,
        "difficulty": difficulty,
        "persona": persona,
        "intent": intent,
        "lifecycle": lifecycle,
    }

    return {"question": question, "answer": answer, "metadata": metadata}


def main():
    examples = []

    # Generate exactly 180 examples
    for i in range(180):
        example = generate_example(i)
        examples.append(example)

    # Write to file
    with open(
        "/Users/otaviolemos/ml/olia-2-oci/data/curated/devops-resource-manager.jsonl",
        "w",
    ) as f:
        for example in examples:
            f.write(json.dumps(example, ensure_ascii=False) + "\n")

    print(
        f"Generated {len(examples)} examples in /Users/otaviolemos/ml/olia-2-oci/data/curated/devops-resource-manager.jsonl"
    )


if __name__ == "__main__":
    main()
