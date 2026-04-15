#!/usr/bin/env python3
"""Generate high-quality OCI Terraform JSONL datasets."""

import json
import random
import os

random.seed(42)

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

difficulties = ["beginner", "intermediate", "advanced"]
difficulty_weights = [0.30, 0.50, 0.20]

# def get_difficulty():
#     return random.choices(difficulties, weights=difficulty_weights, k=1)[0]

topics = {
    "terraform-database": {
        "keywords": [
            "Autonomous Database",
            "MySQL",
            "PostgreSQL",
            "ATP",
            "ADB",
            "Oracle Database",
        ],
        "resource_types": [
            "oci_database_autonomous_database",
            "oci_mysql_mysql_db_system",
            "oci_database_postgresql_instance",
        ],
        "category": "Database",
    },
    "terraform-load-balancer": {
        "keywords": ["Load Balancer", "SSL", "Backend", "Listener", "Certificate"],
        "resource_types": [
            "oci_load_balancer_load_balancer",
            "oci_load_balancer_backendset",
            "oci_load_balancer_listener",
            "oci_load_balancer_certificate",
        ],
        "category": "Networking",
    },
    "terraform-networking": {
        "keywords": ["VCN", "Subnet", "Security List", "Route Table", "NAT Gateway"],
        "resource_types": [
            "oci_core_vcn",
            "oci_core_subnet",
            "oci_core_security_list",
            "oci_core_route_table",
            "oci_core_nat_gateway",
        ],
        "category": "Networking",
    },
    "terraform-observability": {
        "keywords": ["Monitoring", "Alerts", "Metrics", "Notifications"],
        "resource_types": [
            "oci_monitoring_metric",
            "oci_monitoring_alert",
            "oci_monitoring_alert_rule",
            "oci_events_rule",
            "oci_monitoring_dashboard",
        ],
        "category": "Observability",
    },
    "terraform-provider": {
        "keywords": ["Provider", "Authentication", "Config", "OCI"],
        "resource_types": ["provider oci"],
        "category": "Provider",
    },
    "terraform-security": {
        "keywords": ["Vault", "Keys", "Secrets", "KMS", "Encryption"],
        "resource_types": [
            "oci_vault_secret",
            "oci_kms_key",
            "oci_vault_vault",
            "oci_kms_key_version",
        ],
        "category": "Security",
    },
    "terraform-serverless": {
        "keywords": ["Functions", "API Gateway", "Fn", "Serverless"],
        "resource_types": [
            "oci_functions_function",
            "oci_apigateway_gateway",
            "oci_apigateway_deployment",
        ],
        "category": "Serverless",
    },
    "terraform-storage": {
        "keywords": [
            "Object Storage",
            "Block Storage",
            "File Storage",
            "Bucket",
            "OCFS",
        ],
        "resource_types": [
            "oci_objectstorage_bucket",
            "oci_core_volume",
            "oci_file_storage_file_system",
            "oci_objectstorage_object",
        ],
        "category": "Storage",
    },
}


def generate_question(
    topic, company, project, compartment, region, persona, intent, lifecycle, constraint
):
    return (
        f"Como {persona}, preciso {intent} {topic.lower()} para {company} no projeto {project}, "
        f"em {compartment}/{region}, considerando {constraint}. Qual abordagem você recomenda?"
    )


def generate_answer(topic_key, company, project, compartment, region, difficulty):
    topic = topics[topic_key]
    resource_type = topic["resource_types"][0]

    tf_code = get_terraform_code(topic_key, difficulty)
    cli_code = get_oci_cli_code(topic_key, difficulty)
    explanation = get_explanation(topic_key, difficulty)

    answer = f"""Para {topic["keywords"][0].lower()} para {company} no projeto {project}, siga os passos abaixo:

{explanation}

**Terraform HCL:**
```hcl
{tf_code}
```

**OCI CLI:**
```bash
{cli_code}
```

**Deploy:**
```bash
terraform init
terraform plan -var="compartment_ocid=<ocid>"
terraform apply -var="compartment_ocid=<ocid>" -auto-approve
```

**Nota:** [MUTABLE] Preços e limites variam por região. Verifique sempre o Service Limits no console.

**Doc de referência:** https://docs.oracle.com/"""

    return answer


def get_terraform_code(topic_key, difficulty):
    if topic_key == "terraform-database":
        return f"""resource "oci_database_autonomous_database" "main" {{
  compartment_id = var.compartment_ocid
  display_name   = "{project_name()}"
  
  db_name         = "adbdemo"
  db_version      = "19c"
  shape           = "VM.Standard.E4.Flex"
  ocpu_count      = {get_ocpu(difficulty)}
  storage_gb      = {get_storage(difficulty)}
  
  license_model   = "LICENSE_INCLUDED"
  database_edition = "ENTERPRISE_EDITION"
  
  freeform_tags = {{
    environment = "{env_name()}"
    managed_by  = "terraform"
  }}
  
  defined_tags = {{
    "project" = {{"name" = "{company_name()}"}}
  }}
}}

variable "compartment_ocid" {{
  type        = string
  description = "OCID do compartment"
}}"""

    elif topic_key == "terraform-load-balancer":
        return f"""resource "oci_load_balancer_load_balancer" "main" {{
  compartment_id = var.compartment_ocid
  display_name   = "{project_name()}"
  
  shape          = "flexible"
  shape_details {{
    minimum_bandwidth_in_mbps = "10"
    maximum_bandwidth_in_mbps = "100"
  }}
  
  subnet_ids      = [oci_core_subnet.public_subnet.id]
  is_private      = false
  
  freeform_tags = {{
    environment = "{env_name()}"
    managed_by  = "terraform"
  }}
}}

resource "oci_load_balancer_backendset" "backend" {{
  load_balancer_id = oci_load_balancer_load_balancer.main.id
  name             = "backend-set-{i3()}"
  
  health_check {{
    protocol       = "HTTP"
    port           = 80
    url_path       = "/health"
    interval_ms    = 30000
    timeout_ms     = 3000
    retries        = 3
  }}
  
  policy          = "ROUND_ROBIN"
}}"""

    elif topic_key == "terraform-networking":
        return f"""resource "oci_core_vcn" "main" {{
  compartment_id = var.compartment_ocid
  display_name   = "{project_name()}"
  
  cidr_block     = "10.0.0.0/16"
  dns_label      = "vcndemo"
  
  freeform_tags = {{
    environment = "{env_name()}"
    managed_by  = "terraform"
  }}
}}

resource "oci_core_subnet" "public_subnet" {{
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.main.id
  display_name   = "public-subnet"
  
  cidr_block    = "10.0.1.0/24"
  dns_label     = "public"
  availability_domain = "{ad_name()}"
  
  security_list_ids = [oci_core_security_list.public.id]
  route_table_id   = oci_core_route_table.public.id
}}

resource "oci_core_security_list" "public" {{
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.main.id
  display_name   = "public-security-list"
  
  egress_security_rules {{
    destination = "0.0.0.0/0"
    protocol    = "all"
  }}
  
  ingress_security_rules {{
    protocol  = "6"
    source    = "0.0.0.0/0"
    tcp_options {{
      min = 80
      max = 80
    }}
  }}
}}"""

    elif topic_key == "terraform-observability":
        return f"""resource "oci_monitoring_alert_rule" "main" {{
  compartment_id = var.compartment_ocid
  display_name   = "{project_name()}"
  
  metric_compartment_id = var.compartment_ocid
  namespace            = "oci_autonomous_database"
  metric_name           = "CpuUtilization"
  
  aggregation_interval = "300s"
  operator             = "GT"
  threshold            = "80"
  
  destinations = [oci_monitoring_topic.main.id]
  
  freeform_tags = {{
    environment = "{env_name()}"
    managed_by  = "terraform"
  }}
}}

resource "oci_monitoring_topic" "main" {{
  compartment_id = var.compartment_ocid
  display_name   = "alerts-topic"
  
  description = "Alertas de monitoramento para {company_name()}"
}}"""

    elif topic_key == "terraform-provider":
        return f"""terraform {{
  required_providers {{
    oci = {{
      source  = "oracle/oci"
      version = "~> 6.0"
    }}
  }}
}}

provider "oci" {{
  region = var.region
  
  fingerprint          = var.fingerprint
  private_key_path     = var.private_key_path
  tenant_id            = var.tenancy_ocid
  user_id              = var.user_ocid
}}

variable "compartment_ocid" {{
  type        = string
  description = "OCID do compartment"
}}

variable "region" {{
  type        = string
  default     = "sa-saopaulo-1"
}}"""

    elif topic_key == "terraform-security":
        return f"""resource "oci_vault_vault" "main" {{
  compartment_id = var.compartment_ocid
  display_name   = "{project_name()}"
  
  vault_type     = "PRIVATE"
  
  freeform_tags = {{
    environment = "{env_name()}"
    managed_by  = "terraform"
  }}
}}

resource "oci_kms_key" "main" {{
  compartment_id = var.compartment_ocid
  display_name   = "encryption-key"
  
  key_id         = oci_vault_vault.main.id
  key_shape {{
    algorithm = "AES"
    length    = 32
  }}
  
  protection_mode = "SOFTWARE"
  key_state       = "ENABLED"
}}

resource "oci_vault_secret" "main" {{
  compartment_id = var.compartment_ocid
  display_name   = "db-password"
  
  secret_content {{
    content_type = "BASE64"
    content      = base64encode(var.db_password)
  }}
  
  vault_id       = oci_vault_vault.main.id
  key_id         = oci_kms_key.main.id
  secret_rules {{
    secret_rule_type = "EXPIRATION"
    time_rule_type   = "ABSOLUTE"
    expire_after     = "P90D"
  }}
}}"""

    elif topic_key == "terraform-serverless":
        return f"""resource "oci_functions_application" "main" {{
  compartment_id = var.compartment_ocid
  display_name   = "{project_name()}"
  
  subnet_ids     = [oci_core_subnet.functions_subnet.id]
  
  freeform_tags = {{
    environment = "{env_name()}"
    managed_by  = "terraform"
  }}
}}

resource "oci_functions_function" "main" {{
  application_id = oci_functions_application.main.id
  display_name   = "hello-function"
  
  function_type = "HTTP"
  memory_in_mbs = 256
  
  source {{
    image_uri = "phx.ocir.io/${{var.tenancy_ocid}}/demo/functions/hello:latest"
  }}
  
  config = {{
    "MY_VAR" = "value"
  }}
}}

resource "oci_apigateway_gateway" "main" {{
  compartment_id = var.compartment_ocid
  display_name   = "{project_name()}"
  
  endpoint_type = "PUBLIC"
  subnet_ids    = [oci_core_subnet.api_subnet.id]
  
  freeform_tags = {{
    environment = "{env_name()}"
    managed_by  = "terraform"
  }}
}}"""

    elif topic_key == "terraform-storage":
        return f"""resource "oci_objectstorage_bucket" "main" {{
  compartment_id = var.compartment_ocid
  name           = "{project_name().replace("-", "_")}"
  
  namespace      = var.object_storage_namespace
  visibility     = "private"
  
  object_events_enabled = true
  versioning             = "Enabled"
  
  freeform_tags = {{
    environment = "{env_name()}"
    managed_by  = "terraform"
  }}
}}

resource "oci_core_volume" "main" {{
  compartment_id = var.compartment_ocid
  display_name   = "data-volume"
  
  availability_domain = "{ad_name()}"
  size_in_gbs         = {get_storage(difficulty)}
  
  volume_pool_id = null
  
  freeform_tags = {{
    environment = "{env_name()}"
    managed_by  = "terraform"
  }}
}}"""

    return "# Resource code here"


def get_oci_cli_code(topic_key, difficulty):
    if topic_key == "terraform-database":
        return f"""oci db autonomous-database create \\
  --compartment-id ${{var.compartment_ocid}} \\
  --display-name "{project_name()}" \\
  --db-name "adbdemo" \\
  --db-version "19c" \\
  --shape "VM.Standard.E4.Flex" \\
  --ocpu-count {get_ocpu(difficulty)} \\
  --storage-gb {get_storage(difficulty)} \\
  --license-model "LICENSE_INCLUDED" \\
  --wait-for-state AVAILABLE"""

    elif topic_key == "terraform-load-balancer":
        return f"""oci lb load-balancer create \\
  --compartment-id ${{var.compartment_ocid}} \\
  --display-name "{project_name()}" \\
  --shape "flexible" \\
  --minimum-bandwidth-in-mbps 10 \\
  --maximum-bandwidth-in-mbps 100 \\
  --subnet-ids '[${{oci_core_subnet.public_subnet.id}}]' \\
  --wait-for-state ACTIVE"""

    elif topic_key == "terraform-networking":
        return f"""oci network vcn create \\
  --compartment-id ${{var.compartment_ocid}} \\
  --display-name "{project_name()}" \\
  --cidr-block "10.0.0.0/16" \\
  --dns-label "vcndemo" \\
  --wait-for-state AVAILABLE

oci network subnet create \\
  --compartment-id ${{var.compartment_ocid}} \\
  --vcn-id ${{oci_core_vcn.main.id}} \\
  --display-name "public-subnet" \\
  --cidr-block "10.0.1.0/24" \\
  --dns-label "public" \\
  --availability-domain "{ad_name()}" \\
  --wait-for-state AVAILABLE"""

    elif topic_key == "terraform-observability":
        return f"""oci monitoring alert-rule create \\
  --compartment-id ${{var.compartment_ocid}} \\
  --display-name "{project_name()}" \\
  --metric-compartment-id ${{var.compartment_ocid}} \\
  --namespace "oci_autonomous_database" \\
  --metric-name "CpuUtilization" \\
  --aggregation-interval "300s" \\
  --operator "GT" \\
  --threshold 80 \\
  --destinations '[${{oci_monitoring_topic.main.id}}]' \\
  --wait-for-state ACTIVE"""

    elif topic_key == "terraform-security":
        return f"""oci vault vault create \\
  --compartment-id ${{var.compartment_ocid}} \\
  --display-name "{project_name()}" \\
  --vault-type "PRIVATE"

oci kms key create \\
  --compartment-id ${{var.compartment_ocid}} \\
  --display-name "encryption-key" \\
  --key-id ${{oci_vault_vault.main.id}} \\
  --key-shape '{{"algorithm": "AES", "length": 32}}' \\
  --protection-mode "SOFTWARE" \\
  --key-state "ENABLED"

oci vault secret create \\
  --compartment-id ${{var.compartment_ocid}} \\
  --display-name "db-password" \\
  --secret-content '{{"content_type": "BASE64", "content": "${{base64_password}}"}}' \\
  --vault-id ${{oci_vault_vault.main.id}} \\
  --key-id ${{oci_kms_key.main.id}}"""

    elif topic_key == "terraform-serverless":
        return f"""oci fn application create \\
  --compartment-id ${{var.compartment_ocid}} \\
  --display-name "{project_name()}" \\
  --subnet-ids '[${{oci_core_subnet.functions_subnet.id}}]'

oci fn function create \\
  --application-id ${{oci_functions_application.main.id}} \\
  --display-name "hello-function" \\
  --function-type "HTTP" \\
  --memory-in-mbs 256 \\
  --image-uri "phx.ocir.io/${{var.tenancy_ocid}}/demo/functions/hello:latest"

oci api-gateway gateway create \\
  --compartment-id ${{var.compartment_ocid}} \\
  --display-name "{project_name()}" \\
  --endpoint-type "PUBLIC" \\
  --subnet-ids '[${{oci_core_subnet.api_subnet.id}}]' \\
  --wait-for-state ACTIVE"""

    elif topic_key == "terraform-storage":
        return f"""oci os bucket create \\
  --compartment-id ${{var.compartment_ocid}} \\
  --name "{project_name().replace("-", "_")}" \\
  --namespace ${{var.object_storage_namespace}} \\
  --visibility "private" \\
  --object-events-enabled \\
  --versioning "Enabled"

oci bv volume create \\
  --compartment-id ${{var.compartment_ocid}} \\
  --display-name "data-volume" \\
  --availability-domain "{ad_name()}" \\
  --size-in-gbs {get_storage(difficulty)}"""

    else:
        return "# OCI CLI command here"


def get_explanation(topic_key, difficulty):
    explanations = {
        "beginner": "Este é um cenário de nível iniciante. Siga os passos básicos de configuração.",
        "intermediate": "Este cenário requer atenção especial à rede e segurança. Configure corretamente as políticas IAM.",
        "advanced": "Este é um cenário avançado que requer alta disponibilidade e disaster recovery configurado.",
    }
    return explanations.get(difficulty, "Siga os procedimentos padrão.")


def project_name():
    return f"project-{random.randint(100, 999)}"


def company_name():
    return random.choice(companies)


def env_name():
    return random.choice(compartments)


def ad_name():
    return f"AD{random.randint(1, 3)}"


def i3():
    return random.randint(100, 999)


def get_ocpu(difficulty):
    if difficulty == "beginner":
        return random.choice([1, 2])
    elif difficulty == "intermediate":
        return random.choice([4, 8])
    else:
        return random.choice([16, 32])


def get_storage(difficulty):
    if difficulty == "beginner":
        return random.choice([50, 100])
    elif difficulty == "intermediate":
        return random.choice([200, 300])
    else:
        return random.choice([500, 1000])


def generate_dataset(topic_key, num_examples=180):
    examples = []

    num_beginner = int(180 * 0.30)
    num_intermediate = int(180 * 0.50)
    num_advanced = 180 - num_beginner - num_intermediate

    beginner_pool = generate_pool("beginner", num_beginner)
    intermediate_pool = generate_pool("intermediate", num_intermediate)
    advanced_pool = generate_pool("advanced", num_advanced)

    all_items = beginner_pool + intermediate_pool + advanced_pool
    random.shuffle(all_items)

    for i, item in enumerate(all_items):
        (
            company,
            project,
            region,
            persona,
            intent,
            lifecycle,
            compartment,
            constraint,
        ) = item

        question = generate_question(
            topics[topic_key]["keywords"][0],
            company,
            project,
            compartment,
            region,
            persona,
            intent,
            lifecycle,
            constraint,
        )

        difficulty = (
            "beginner"
            if i < num_beginner
            else "intermediate"
            if i < num_beginner + num_intermediate
            else "advanced"
        )
        answer = generate_answer(
            topic_key, company, project, compartment, region, difficulty
        )

        example = {
            "question": question,
            "answer": answer,
            "metadata": {
                "category": topic_key.replace("-", "/"),
                "difficulty": difficulty,
                "persona": persona,
                "intent": intent,
                "lifecycle": lifecycle,
            },
        }
        examples.append(example)

    return examples


def generate_pool(difficulty, count):
    pool = []
    for _ in range(count):
        pool.append(
            (
                random.choice(companies),
                random.choice(projects),
                random.choice(regions),
                random.choice(personas),
                random.choice(intents),
                random.choice(lifecycles),
                random.choice(compartments),
                random.choice(constraints),
            )
        )
    return pool


def save_dataset(topic_key, examples):
    output_dir = "/Users/otaviolemos/ml/olia-2-oci/data/curated"
    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(output_dir, f"{topic_key}.jsonl")

    with open(output_path, "w", encoding="utf-8") as f:
        for example in examples:
            f.write(json.dumps(example, ensure_ascii=False) + "\n")

    return len(examples)


if __name__ == "__main__":
    topic_keys = [
        "terraform-database",
        "terraform-load-balancer",
        "terraform-networking",
        "terraform-observability",
        "terraform-provider",
        "terraform-security",
        "terraform-serverless",
        "terraform-storage",
    ]

    for topic_key in topic_keys:
        print(f"Generating {topic_key}...")
        examples = generate_dataset(topic_key, 180)
        count = save_dataset(topic_key, examples)
        print(f"  Saved {count} examples to {topic_key}.jsonl")

    print("\nDone!")
