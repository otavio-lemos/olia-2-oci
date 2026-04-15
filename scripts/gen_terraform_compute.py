import json
import random

random.seed(42)

empresas = [
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
    "BioResearch Labs",
    "AutoDrive Systems",
    "EnergyGrid Monitor",
    "GameForge Studios",
    "FoodChain Trace",
    "LegalDoc Manager",
    "InsureTech Plus",
]

projetos = [
    "ecommerce-migration",
    "data-lake-modernization",
    "microservices-refactor",
    "disaster-recovery-setup",
    "compliance-audit",
    "cost-optimization",
    "performance-tuning",
    "security-hardening",
    "multi-region-expansion",
    "hybrid-cloud-integration",
    "ci-cd-pipeline",
    "monitoring-overhaul",
    "backup-strategy",
    "zero-trust-implementation",
    "api-gateway-deployment",
    "container-platform",
    "serverless-transformation",
    "database-consolidation",
    "network-segmentation",
    "identity-federation",
]

compartimentos = [
    "production",
    "development",
    "staging",
    "security",
    "analytics",
    "devops",
    "sandbox",
    "shared-services",
    "networking",
]
regioes = [
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
    "devops engineer",
    "sre",
    "dba",
    "security lead",
    "auditor",
    "finops analyst",
    "infrastructure engineer",
]
intents = [
    "design",
    "standardize",
    "troubleshoot",
    "migrate",
    "optimize",
    "audit",
    "review",
    "remediate",
    "compare",
    "recover",
]
lifecycles = [
    "greenfield",
    "brownfield",
    "expansão",
    "produção estável",
    "incidente",
    "migração",
    "desativação",
    "auditoria",
]
difficulties = ["beginner", "intermediate", "advanced"]

constraints = [
    "sem downtime",
    "sem IP público",
    "com budget limitado",
    "com auditoria em 30 dias",
    "mínimo privilégio",
    "equipe enxuta",
    "ambiente legado",
    "rollback em menos de 15 minutos",
    "integração híbrida",
    "multi-região",
]

perguntas_base = [
    "Como criar uma instância Compute com Terraform no OCI para {project}?",
    "Preciso configurar instance pool com auto-scaling via Terraform. Quais os recursos necessários?",
    "Como fazer deploy de compute com Terraform em {region} usando shape flex?",
    "Qual configuração Terraform para criar instance com boot volume encriptado?",
    "Como migrar instância compute existente para Terraform sem downtime?",
    "Problema ao executar terraform apply - instance não provisiona. Diagnóstico?",
    "Como configurar auto-scaling para instance pool via Terraform?",
    "Melhor prática para state remoto em Terraform com OCI?",
    "Como criar instance configuration com custom image via Terraform?",
    "Terraform retorna erro de limite de recursos. Como resolver?",
]

respostas_tecnicas = [
    r"""Recurso principal: `oci_core_instance`

```hcl
resource "oci_core_instance" "app_server" {
  compartment_id = var.compartment_id
  display_name   = "app-prod-001"
  shape          = "VM.Standard.E4.Flex"
  
  shape_config {
    ocpus         = 2
    memory_in_gbs = 16
  }
  
  source_details {
    image_id = var.oracle_linux_8_image_id
  }
  
  create_vnic_details {
    subnet_id        = oci_core_subnet.private_subnet.id
    assign_public_ip = false
    hostname_label   = "app-prod"
  }
  
  metadata = {
    ssh_authorized_keys = file(var.ssh_pub_key_path)
  }
  
  defined_tags = {
    "Environment" = "production"
    "Project"     = "PROJECT_PLACEHOLDER"
  }
}
```

**Variables:**
```hcl
variable "compartment_id" { description = "OCID do compartment" }
variable "oracle_linux_8_image_id" { description = "Image OCID para Oracle Linux 8" }
variable "ssh_pub_key_path" { description = "Caminho da chave pública SSH" }
```

**Considerações:**
- [MUTABLE] Shapes E4.Flex: preço varia por OCPU/GB. Verifique Pricing Calculator.
- Use `create_vnic_details` para controle total de rede.
- `defined_tags` facilita governança e chargeback.
- [CHECK DOCS] Limites de OCPUs por região: https://docs.oracle.com/iaas/Content/General/LimitsResources.htm""",
    r"""Recursos necessários para Instance Pool com Auto-Scaling:

```hcl
# 1. Instance Configuration
resource "oci_core_instance_configuration" "pool_config" {
  compartment_id = var.compartment_id
  display_name   = "app-pool-config"
  
  instance_details {
    instance_type = "compute"
    
    compute_details {
      shape          = "VM.Standard.E4.Flex"
      shape_config {
        ocpus         = 2
        memory_in_gbs = 16
      }
      source_details {
        image_id = var.oracle_linux_image_id
      }
    }
  }
}

# 2. Instance Pool
resource "oci_autoscaling_instance_pool" "app_pool" {
  compartment_id     = var.compartment_id
  instance_pool_name = "app-autoscaling-pool"
  
  placement_configuration {
    availability_domain = var.availability_domain
    fault_domains       = ["FAULT-DOMAIN-1", "FAULT-DOMAIN-2"]
  }
  
  instance_configuration_id = oci_core_instance_configuration.pool_config.id
  
  size = 3
  
  scaling_configuration {
    policy_type = "threshold"
    
    threshold_details {
      metric_type     = "CPU_UTILIZATION"
      threshold       = 70
      scale_in_threshold = 30
      duration_in_seconds = 300
    }
  }
}
```

**Dica:** Auto-scaling baseado em CPU é o mais comum. Para workloads com padrão previsível, considere schedule-based scaling.""",
    r"""Deploy em REGION_PLACEHOLDER com shape E4.Flex:

```hcl
provider "oci" {
  region = "REGION_PLACEHOLDER"
}

terraform {
  required_providers {
    oci = {
      source  = "oracle/oci"
      version = "~> 6.0"
    }
  }
}

data "oci_core_images" "oracle_linux" {
  compartment_id          = var.compartment_id
  operating_system        = "Oracle Linux"
  operating_system_version = "8"
  sort_by                 = "TIMECREATED"
  sort_order              = "DESC"
}

resource "oci_core_instance" "main" {
  compartment_id = var.compartment_id
  display_name   = "prod-PROJECT_PLACEHOLDER"
  shape          = "VM.Standard.E4.Flex"
  
  shape_config {
    ocpus         = 4
    memory_in_gbs = 32
  }
  
  source_details {
    image_id = data.oci_core_images.oracle_linux.images[0].id
  }
  
  create_vnic_details {
    subnet_id = oci_core_subnet.app_subnet.id
  }
}
```

**Região REGION_PLACEHOLDER:** Verifique disponibilidade de shapes na documentação. [MUTABLE] Preços por hora variam significativamente.""",
    r"""Boot volume encriptado com chave gerenciada OCI (default):

```hcl
resource "oci_core_instance" "secure_app" {
  compartment_id = var.compartment_id
  display_name   = "secure-app-001"
  shape          = "VM.Standard.E4.Flex"
  
  source_details {
    image_id = var.image_id
  }
  
  # Boot volume com encryption default (Oracle-managed)
  create_vnic_details {
    subnet_id = oci_core_subnet.private.id
  }
}
```

**Para encryption customizada (BYOK):**

```hcl
resource "oci_core_instance" "byok_app" {
  # ... config básica ...
  
  boot_volume_config_details {
    source_details {
      source_type = "image"
      image_id    = var.image_id
    }
    
    # Usar chave do Vault
    kms_key_id = oci_kms_key.byok_key.id
  }
}
```

**Nota:** Encryption em repouso é default e gratuita. BYOK requer Vault configurado.""",
    r"""Migração para Terraform sem downtime - estratégia:

**1. Importar recurso existente:**
```bash
terraform import oci_core_instance.existing <instance_ocid>
```

**2. Gerar configuração base:**
```bash
# Show atual do recurso
terraform state show oci_core_instance.existing
```

**3. Ajustar configuração para IaC:**

```hcl
resource "oci_core_instance" "app" {
  compartment_id = var.compartment_id
  display_name   = "app-migrated"
  shape          = "VM.Standard.E4.Flex"
  # Import mantém o IP existente se subnet não mudar
  
  lifecycle {
    # Preserve IP e metadata durante updates
    create_before_destroy = false
    update_strategy = "none"
  }
}
```

**4. Estratégia blue-green:**
- Criar nova instância via Terraform
- Migrar tráfego via Load Balancer
- Decomissionar antiga

**Cuidado:** `import` não gera código automaticamente. Analise o estado e crie a configuração manualmente.""",
    r"""Diagnóstico de falha no provisionamento:

**1. Verificar erro específico:**
```bash
terraform apply 2>&1 | grep -A5 "Error:"
```

**2. Causas comuns:**
- Limite de recursos atingido → `oci limits resource list`
- Shape indisponível na AD → usar outra AD ou shape alternativo
- Subnet sem espaço → criar nova subnet com CIDR maior
- SSH key mal formatada → formato OpenSSH obrigatório

**3. Debug detalhado:**
```hcl
provider "oci" {
  region = var.region
  
  # Habilitar debug
  #tenancy_ocid = var.tenancy_ocid
}
```

```bash
TF_LOG=DEBUG terraform apply
```

**4. Retry com exponential backoff:**
```hcl
resource "oci_core_instance" "app" {
  # ... config ...
  
  lifecycle {
    retry_on_create_failure = true
  }
}
```

[CHECK DOCS] Service Limits: https://docs.oracle.com/iaas/Content/General/LimitsResources.htm""",
    r"""Auto-scaling com OCI autoscaling:

```hcl
resource "oci_autoscaling_policy" "cpu_policy" {
  compartment_id     = oci_autoscaling_instance_pool.pool.compartment_id
  instance_pool_id   = oci_autoscaling_instance_pool.pool.id
  policy_type        = "threshold"
  
  display_name       = "scale-out-cpu"
  
  capacity {
    min       = 2
    max       = 10
    initial   = 3
  }
  
  rules {
    action     = "INCREASE"
    metric_type = "CPU_UTILIZATION"
    threshold  = 75
  }
  
  rules {
    action     = "DECREASE"
    metric_type = "CPU_UTILIZATION"
    threshold  = 25
  }
  
  execution_schedule {
    timezone = "UTC"
    # Não aplicável para threshold-based
  }
}
```

**Tipos de política:**
- **Threshold**: baseada em métricas (CPU, memory, network)
- **Schedule**: baseada em horário (útil para cargas previsíveis)
- **Prediction**: ML-based (requiere OCI Ops Insights)""",
    r"""Remote State com OCI Object Storage:

```hcl
terraform {
  backend "s3" {
    endpoint          = "https://objectstorage.REGION_PLACEHOLDER.oraclecloud.com"
    bucket            = "terraform-state"
    key               = "compute/prod/terraform.tfstate"
    
    skip_credentials_validation = true
    skip_metadata_api_check     = true
    
    region     = "REGION_PLACEHOLDER"
    tenancy    = var.tenancy_ocid
  }
}
```

**State Locking:**
```hcl
terraform {
  backend "s3" {
    # ... same config ...
    
    dynamodb_endpoint = "https://objectstorage.REGION_PLACEHOLDER.oraclecloud.com"
    dynamodb_table    = "terraform-lock"
  }
}
```

**Melhorias:**
- Habilite versionamento no bucket para audit trail
- Use lifecycle rules para expiration de state antigo
- Restrinja acesso com IAM policies""",
    r"""Instance Configuration com custom image:

```hcl
# Buscar custom image
data "oci_core_images" "custom_image" {
  compartment_id          = var.compartment_id
  image_filter            = "name:^my-custom-image-"
  sort_by                 = "TIMECREATED"
  sort_order              = "DESC"
}

resource "oci_core_instance_configuration" "custom_config" {
  compartment_id = var.compartment_id
  display_name   = "web-server-config"
  
  instance_details {
    instance_type = "compute"
    
    compute_details {
      shape = "VM.Standard.E4.Flex"
      
      shape_config {
        ocpus         = 2
        memory_in_gbs = 16
      }
      
      source_details {
        image_id = data.oci_core_images.custom_image.images[0].id
        boot_volume_size_in_gbs = 100
      }
      
      create_vnic_details {
        subnet_id      = oci_core_subnet.web_subnet.id
        assign_public_ip = true
      }
    }
  }
}
```

**Dica:** Custom images devem ser compatíveis com OCI. Use Oracle Linux ou imagens validadas.""",
    r"""Resolução de erro de limites:

**1. Verificar limites atuais:**
```bash
oci limits value list \
  --compartment-id $TENANCY_OCID \
  --service-name "compute" \
  --resource-name "standard-e4-core-ocpu"
```

**2. Identificar recursos não utilizados:**
```bash
oci compute instance list \
  --compartment-id $COMPARTMENT_OCID \
  --lifecycle-state "STOPPED" \
  --query "data[?\"shape\" contains 'E4'].{\"name\":\"display-name\",\"ocpus\":\"shape-config.ocpus\"}"
```

**3. Soluções:**
- **Cleanup**: Terminar instâncias stopped (elas ainda consomem limites em alguns casos)
- **Resize**: Downgrade de shapes não utilizados
- **Request Increase**: Solicitar aumento via console ou API

**Política de limits:**
- [MUTABLE] Limits podem ser aumentados mediante solicitação
- Some limits são regionais, outros são por tenancy
- Reserved IP e boot volumes afetam limites""",
]

examples = []
for i in range(250):
    projeto = projetos[i % len(projetos)]
    region = regioes[i % len(regioes)]
    persona = personas[i % len(personas)]
    intent = intents[i % len(intents)]
    lifecycle = lifecycles[i % len(lifecycles)]
    difficulty = difficulties[i % 3]
    constraint = constraints[i % len(constraints)] if i % 4 == 0 else None

    pergunta_base = perguntas_base[i % len(perguntas_base)]
    pergunta = pergunta_base.format(project=projeto, region=region)

    if constraint:
        pergunta += f" Restrição: {constraint}."

    resposta = respostas_tecnicas[i % len(respostas_tecnicas)]
    resposta = resposta.replace("PROJECT_PLACEHOLDER", projeto).replace(
        "REGION_PLACEHOLDER", region
    )

    metadata = {
        "category": "terraform/compute",
        "difficulty": difficulty,
        "persona": persona,
        "intent": intent,
        "lifecycle": lifecycle,
    }

    if constraint:
        metadata["constraint"] = constraint

    example = {"question": pergunta, "answer": resposta, "metadata": metadata}
    examples.append(example)

with open(
    "/Users/otaviolemos/ml/olia-2-oci/data/curated/terraform-compute.jsonl", "w"
) as f:
    for ex in examples:
        f.write(json.dumps(ex, ensure_ascii=False) + "\n")

print(f"Gerados {len(examples)} exemplos")
print(f"Primeiro exemplo:")
print(json.dumps(examples[0], ensure_ascii=False, indent=2))
print(f"\nÚltimo exemplo (index 249):")
print(json.dumps(examples[249], ensure_ascii=False, indent=2))
