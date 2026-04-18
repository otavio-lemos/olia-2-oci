import json
import random
import re
from pathlib import Path

random.seed(42)

# --- CONFIGURAÇÕES ---
EXAMPLES_PER_CATEGORY = 150  # Mantém paridade com o projeto
MIN_TOKENS = 800
MAX_TOKENS = 1100

CATEGORIES = [
    "compute/instances", "compute/scaling", "compute/custom-images",
    "storage/block", "storage/object", "storage/file",
    "networking/vcn", "networking/security", "networking/connectivity", "lb/load-balancer",
    "database/autonomous", "database/mysql", "database/postgresql", "database/nosql",
    "database/autonomous-json", "database/exadata", "database/exadata-cloud",
    "container/oke", "container/instances",
    "serverless/functions", "serverless/api-gateway",
    "security/iam-basics", "security/policies", "security/dynamic-groups", "security/federation",
    "security/vault-secrets", "security/vault-keys", "security/encryption",
    "security/cloud-guard", "security/waf", "security/zero-trust", "security/posture-management",
    "devops/ci-cd", "devops/resource-manager", "devops/artifacts", "devops/secrets",
    "migration/aws-compute", "migration/aws-storage", "migration/aws-database",
    "migration/azure-compute", "migration/azure-storage", "migration/azure-database",
    "migration/gcp-compute", "migration/gcp-storage", "migration/gcp-database",
    "migration/onprem-compute", "migration/onprem-storage", "migration/onprem-vmware",
    "migration/onprem-database", "migration/data-transfer",
    "terraform/provider", "terraform/compute", "terraform/storage", "terraform/networking",
    "terraform/load-balancer", "terraform/database", "terraform/container", "terraform/serverless",
    "terraform/security", "terraform/observability", "terraform/devops", "terraform/state",
    "observability/logging", "observability/monitoring", "observability/stack-monitoring", "observability/apm",
    "troubleshooting/connectivity", "troubleshooting/performance", "troubleshooting/authentication",
    "troubleshooting/database", "troubleshooting/compute", "troubleshooting/storage",
    "troubleshooting/oke", "troubleshooting/functions",
    "governance/landing-zone", "governance/compartments", "governance/tagging", "governance/budgets-cost",
    "governance/policies-guardrails", "governance/compliance", "governance/audit-readiness", "governance/resource-discovery",
    "finops/cost-optimization", "finops/showback-chargeback", "finops/rightsizing", "finops/storage-tiering",
    "platform/backup-governance", "platform/sre-operations",
]

# --- DIVERSIDADE COMPLETA (v5/v6 levels) ---
SHAPES = ["VM.Standard.E4.Flex", "VM.Standard.A1.Flex", "VM.Optimized3.Flex", "BM.Standard.E5", "VM.GPU.A10.1", "VM.Standard3.Flex", "VM.DenseIO.E4.Flex"]
REGIONS = ["sa-saopaulo-1", "us-ashburn-1", "us-phoenix-1", "eu-frankfurt-1", "uk-london-1", "ap-mumbai-1", "ap-tokyo-1", "ca-toronto-1", "ap-sydney-1"]
COMPARTMENTS = ["production", "development", "staging", "sandbox", "shared-services", "networking", "security", "data-platform", "analytics", "devops"]
COMPANIES = [
    "TechCorp", "FinBank", "HealthVida", "EduNet", "AgroBR",
    "LogisMax", "RetailSul", "MidiaBR", "GovBR", "StartX",
    "IndusMax", "ServPlus", "CyberDef", "DataCloud", "FastPag",
    "EcoEnergia", "Mobilita", "ConstruBR", "AutoTech", "BioMed"
]
PROJECTS = [
    "migra-aws", "app-modern", "data-lake", "erp-cloud",
    "dr-site", "api-gateway", "hybrid-cloud", "sec-baseline",
    "bi-analytics", "gen-ai", "iot-tracking", "crm-consolida",
    "hr-platform", "supply-chain", "audit-2026", "exadata-move",
    "iac-pipeline", "observability", "sre-ops", "finops-cost"
]
PERSONAS = ["cloud architect", "platform engineer", "sre", "security lead", "dba", "finops analyst", "auditor", "devops engineer"]
CONSTRAINTS = ["sem downtime", "sem IP público", "com budget limitado", "com auditoria em 30 dias", "ambiente legado", "equipe enxuta", "multi-região", "integração híbrida", "mínimo privilégio", "rollback em menos de 15 minutos"]
LIFECYCLE_STAGES = ["greenfield", "brownfield", "produção estável", "incidente", "expansão", "auditoria", "migração", "desativação"]

INTENTS_PT = {
    "create": "criação (provisionamento)",
    "list": "listagem e auditoria",
    "get": "consulta de detalhes",
    "update": "atualização de configuração",
    "delete": "remoção",
    "manage": "gerenciamento",
    "diagnose": "diagnóstico e troubleshooting",
    "describe": "planejamento de migração",
    "analyze": "análise e otimização",
}

# --- CLI COMPLETO (v5 level — todos os intents, todas as categorias) ---
CLI_COMMANDS = {
    "compute/instances": {
        "create": "oci compute instance launch --availability-domain {ad} --shape {shape} --shape-config 'ocpus={ocpus},memory={memory}' --subnet-id {subnet_id} --display-name {name} --compartment-id {compartment_id}",
        "list": "oci compute instance list --compartment-id {compartment_id} --lifecycle-state RUNNING",
        "get": "oci compute instance get --instance-id {instance_id}",
        "update": "oci compute instance update --instance-id {instance_id} --display-name {name}\noci compute boot-volume update --boot-volume-id {volume_id} --size-in-gbs {size}",
        "delete": "oci compute instance terminate --instance-id {instance_id} --preserve-boot-volume false",
        "manage": "oci compute instance action --instance-id {instance_id} --action START --wait-for-state RUNNING\noci compute instance action --instance-id {instance_id} --action STOP --wait-for-state STOPPED",
    },
    "compute/scaling": {
        "create": "oci compute instance-pool create --compartment-id {compartment_id} --shape {shape} --size {size} --subnet-ids ['{subnet_id}'] --display-name {name}",
        "list": "oci compute instance-pool list --compartment-id {compartment_id}",
        "get": "oci compute instance-pool get --instance-pool-id {instance_pool_id}",
        "update": "oci compute instance-pool update --instance-pool-id {instance_pool_id} --size {new_size}\noci compute instance-configuration update --instance-configuration-id {config_id} --shape-config 'ocpus={ocpus},memory={memory}'",
        "delete": "oci compute instance-pool delete --instance-pool-id {instance_pool_id} --force",
        "manage": "oci compute instance-pool attach-instance --instance-pool-id {instance_pool_id} --instance-configuration-id {config_id}",
    },
    "compute/custom-images": {
        "create": "oci compute image create --compartment-id {compartment_id} --instance-id {instance_id} --display-name {name}",
        "list": "oci compute image list --compartment-id {compartment_id} --operating-system 'Oracle Linux'",
        "get": "oci compute image get --image-id {image_id}",
        "update": "oci compute image update --image-id {image_id} --display-name {name}",
        "delete": "oci compute image delete --image-id {image_id} --force",
        "manage": "oci compute image get --image-id {image_id}",
    },
    "storage/block": {
        "create": "oci bv volume create --compartment-id {compartment_id} --availability-domain {ad} --size-in-gbs {size} --display-name {name}",
        "list": "oci bv volume list --compartment-id {compartment_id} --availability-domain {ad}",
        "get": "oci bv volume get --volume-id {volume_id}",
        "update": "oci bv volume update --volume-id {volume_id} --size-in-gbs {size}",
        "delete": "oci bv volume delete --volume-id {volume_id} --force",
        "manage": "oci bv volume-attachment list --compartment-id {compartment_id}",
    },
    "storage/object": {
        "create": "oci os bucket create --name {bucket_name} --compartment-id {compartment_id} --storage-tier Standard",
        "list": "oci os bucket list --compartment-id {compartment_id}",
        "get": "oci os bucket get --bucket-name {bucket_name} --namespace-name {namespace}",
        "update": "oci os bucket update --bucket-name {bucket_name} --namespace-name {namespace}",
        "delete": "oci os bucket delete --bucket-name {bucket_name} --namespace-name {namespace} --force",
        "manage": "oci os object list --bucket-name {bucket_name} --namespace-name {namespace}",
    },
    "storage/file": {
        "create": "oci fs mount-target create --compartment-id {compartment_id} --subnet-id {subnet_id} --display-name {name}",
        "list": "oci fs mount-target list --compartment-id {compartment_id}",
        "get": "oci fs mount-target get --mount-target-id {mount_target_id}",
        "update": "oci fs mount-target update --mount-target-id {mount_target_id}",
        "delete": "oci fs mount-target delete --mount-target-id {mount_target_id} --force",
        "manage": "oci fs export list --mount-target-id {mount_target_id}",
    },
    "networking/vcn": {
        "create": "oci network vcn create --compartment-id {compartment_id} --cidr-blocks ['{cidr}'] --display-name {vcn_name}",
        "list": "oci network vcn list --compartment-id {compartment_id}",
        "get": "oci network vcn get --vcn-id {vcn_id}",
        "update": "oci network vcn update --vcn-id {vcn_id} --display-name {vcn_name}",
        "delete": "oci network vcn delete --vcn-id {vcn_id} --force",
        "manage": "oci network subnet list --vcn-id {vcn_id}",
    },
    "networking/security": {
        "create": "oci network security-list create --compartment-id {compartment_id} --vcn-id {vcn_id} --display-name {name}",
        "list": "oci network security-list list --vcn-id {vcn_id}",
        "get": "oci network security-list get --security-list-id {security_list_id}",
        "update": "oci network security-list update --security-list-id {security_list_id}",
        "delete": "oci network security-list delete --security-list-id {security_list_id} --force",
        "manage": "oci network security-rule list --security-list-id {security_list_id}",
    },
    "networking/connectivity": {
        "create": "oci network drg create --compartment-id {compartment_id} --display-name {name}",
        "list": "oci network drg list --compartment-id {compartment_id}",
        "get": "oci network drg get --drg-id {drg_id}",
        "update": "oci network drg update --drg-id {drg_id}",
        "delete": "oci network drg delete --drg-id {drg_id} --force",
        "manage": "oci network drg-attachment list --drg-id {drg_id}",
    },
    "lb/load-balancer": {
        "create": "oci lb load-balancer create --shape {shape} --subnet-ids ['{subnet_id}'] --display-name {name} --compartment-id {compartment_id}",
        "list": "oci lb load-balancer list --compartment-id {compartment_id}",
        "get": "oci lb load-balancer get --load-balancer-id {lb_id}",
        "update": "oci lb load-balancer update --load-balancer-id {lb_id} --display-name {name}",
        "delete": "oci lb load-balancer delete --load-balancer-id {lb_id} --force",
        "manage": "oci lb backend set list --load-balancer-id {lb_id}",
    },
    "database/autonomous": {
        "create": "oci db autonomous-database create --compartment-id {compartment_id} --cpu-core-count {cores} --storage-size-in-tbs {storage} --db-workload AUTONOMOUS_TRANSACTION_PROCESSING --display-name {name}",
        "list": "oci db autonomous-database list --compartment-id {compartment_id} --lifecycle-state AVAILABLE",
        "get": "oci db autonomous-database get --autonomous-database-id {adb_id}",
        "update": "oci db autonomous-database update --autonomous-database-id {adb_id} --cpu-core-count {cores}",
        "delete": "oci db autonomous-database delete --autonomous-database-id {adb_id} --force",
        "manage": "oci db autonomous-database get --autonomous-database-id {adb_id}",
    },
    "database/mysql": {
        "create": "oci db system create --compartment-id {compartment_id} --display-name {name} --shape {shape} --mysql-version {version} --admin-password {password}",
        "list": "oci db system list --compartment-id {compartment_id}",
        "get": "oci db system get --db-system-id {db_system_id}",
        "update": "oci db system update --db-system-id {db_system_id}",
        "delete": "oci db system delete --db-system-id {db_system_id} --force",
        "manage": "oci db system get --db-system-id {db_system_id}",
    },
    "database/postgresql": {
        "create": "oci db postgres instance create --compartment-id {compartment_id} --display-name {name} --shape {shape} --db-version {version}",
        "list": "oci db postgres instance list --compartment-id {compartment_id}",
        "get": "oci db postgres instance get --postgres-instance-id {postgres_id}",
        "update": "oci db postgres instance update --postgres-instance-id {postgres_id}",
        "delete": "oci db postgres instance delete --postgres-instance-id {postgres_id} --force",
        "manage": "oci db postgres instance get --postgres-instance-id {postgres_id}",
    },
    "database/nosql": {
        "create": "oci nosql table create --compartment-id {compartment_id} --name {table_name} --ddl 'CREATE TABLE {table_name} (id STRING PRIMARY KEY, data JSON)'",
        "list": "oci nosql table list --compartment-id {compartment_id}",
        "get": "oci nosql table get --table-name {table_name} --compartment-id {compartment_id}",
        "update": "oci nosql table update --table-name {table_name} --compartment-id {compartment_id}",
        "delete": "oci nosql table delete --table-name {table_name} --compartment-id {compartment_id} --force",
        "manage": "oci nosql table get --table-name {table_name} --compartment-id {compartment_id}",
    },
    "database/autonomous-json": {
        "create": "oci db autonomous-database create --compartment-id {compartment_id} --cpu-core-count {cores} --storage-size-in-tbs {storage} --db-workload JSON --display-name {name}",
        "list": "oci db autonomous-database list --compartment-id {compartment_id} --db-workload JSON",
        "get": "oci db autonomous-database get --autonomous-database-id {adb_id}",
        "update": "oci db autonomous-database update --autonomous-database-id {adb_id}",
        "delete": "oci db autonomous-database delete --autonomous-database-id {adb_id} --force",
        "manage": "oci db autonomous-database get --autonomous-database-id {adb_id}",
    },
    "database/exadata": {
        "create": "oci db exadata-infrastructure create --compartment-id {compartment_id} --display-name {name} --shape {shape} --availability-domain {ad}",
        "list": "oci db exadata-infrastructure list --compartment-id {compartment_id}",
        "get": "oci db exadata-infrastructure get --exadata-infrastructure-id {exadata_id}",
        "update": "oci db exadata-infrastructure update --exadata-infrastructure-id {exadata_id}",
        "delete": "oci db exadata-infrastructure delete --exadata-infrastructure-id {exadata_id} --force",
        "manage": "oci db cloud-exadata-cluster list --compartment-id {compartment_id}",
    },
    "database/exadata-cloud": {
        "create": "oci db cloud-exadata-cluster create --infrastructure-id {infra_id} --display-name {name} --compartment-id {compartment_id}",
        "list": "oci db cloud-exadata-cluster list --compartment-id {compartment_id}",
        "get": "oci db cloud-exadata-cluster get --cloud-exadata-cluster-id {cluster_id}",
        "update": "oci db cloud-exadata-cluster update --cloud-exadata-cluster-id {cluster_id}",
        "delete": "oci db cloud-exadata-cluster delete --cloud-exadata-cluster-id {cluster_id} --force",
        "manage": "oci db cloud-exadata-vm-cluster list --compartment-id {compartment_id}",
    },
    "container/oke": {
        "create": "oci ce cluster create --compartment-id {compartment_id} --name {name} --kubernetes-version {k8s_version} --vcn-id {vcn_id}",
        "list": "oci ce cluster list --compartment-id {compartment_id}",
        "get": "oci ce cluster get --cluster-id {cluster_id}",
        "delete": "oci ce cluster delete --cluster-id {cluster_id} --force",
        "update": "oci ce cluster update --cluster-id {cluster_id} --kubernetes-version {k8s_version}",
        "manage": "oci ce node-pool list --cluster-id {cluster_id}",
    },
    "container/instances": {
        "create": "oci container-instances container-instance create --compartment-id {compartment_id} --display-name {name} --shape VM.Standard.E4.Flex",
        "list": "oci container-instances container-instance list --compartment-id {compartment_id}",
        "get": "oci container-instances container-instance get --container-instance-id {instance_id}",
        "delete": "oci container-instances container-instance delete --container-instance-id {instance_id} --force",
        "update": "oci container-instances container-instance update --container-instance-id {instance_id} --display-name {name}",
        "manage": "oci container-instances container-instance get --container-instance-id {instance_id}",
    },
    "serverless/functions": {
        "create": "oci fn application create --compartment-id {compartment_id} --display-name {name} --subnet-ids '[\"{subnet_id}\"]'",
        "list": "oci fn application list --compartment-id {compartment_id}",
        "get": "oci fn application get --application-id {app_id}",
        "delete": "oci fn application delete --application-id {app_id} --force",
        "update": "oci fn application update --application-id {app_id} --syslog-url tcp://syslog.example.com",
        "manage": "oci fn function list --application-id {app_id}",
    },
    "serverless/api-gateway": {
        "create": "oci api-gateway gateway create --compartment-id {compartment_id} --display-name {name} --endpoint-type PUBLIC --subnet-id {subnet_id}",
        "list": "oci api-gateway gateway list --compartment-id {compartment_id}",
        "get": "oci api-gateway gateway get --gateway-id {gateway_id}",
        "delete": "oci api-gateway gateway delete --gateway-id {gateway_id} --force",
        "update": "oci api-gateway gateway update --gateway-id {gateway_id} --display-name {name}",
        "manage": "oci api-gateway deployment list --compartment-id {compartment_id}",
    },
    "security/iam-basics": {
        "create": "oci iam user create --compartment-id {compartment_id} --description {description} --name {name}",
        "list": "oci iam user list --compartment-id {compartment_id}",
        "get": "oci iam user get --user-id {user_id}",
        "update": "oci iam user update --user-id {user_id} --description {description}",
        "delete": "oci iam user delete --user-id {user_id} --force",
        "manage": "oci iam group list --compartment-id {compartment_id}",
    },
    "security/policies": {
        "create": "oci iam policy create --compartment-id {compartment_id} --name {policy_name} --statements '[\"{statement}\"]' --description {description}",
        "list": "oci iam policy list --compartment-id {compartment_id}",
        "get": "oci iam policy get --policy-id {policy_id}",
        "update": "oci iam policy update --policy-id {policy_id} --statements '[\"{statement}\"]'",
        "delete": "oci iam policy delete --policy-id {policy_id} --force",
        "manage": "oci iam policy list --compartment-id {compartment_id}",
    },
    "security/dynamic-groups": {
        "create": "oci iam dynamic-group create --compartment-id {compartment_id} --matching-rule '{rule}' --name {name} --description {description}",
        "list": "oci iam dynamic-group list --compartment-id {compartment_id}",
        "get": "oci iam dynamic-group get --dynamic-group-id {dynamic_group_id}",
        "update": "oci iam dynamic-group update --dynamic-group-id {dynamic_group_id} --matching-rule '{rule}'",
        "delete": "oci iam dynamic-group delete --dynamic-group-id {dynamic_group_id} --force",
        "manage": "oci iam dynamic-group list --compartment-id {compartment_id}",
    },
    "security/federation": {
        "create": "oci iam identity-provider create --compartment-id {tenancy_id} --name {name} --description {description} --product-type IDCS --metadata-url {endpoint}",
        "list": "oci iam identity-provider list --compartment-id {tenancy_id}",
        "get": "oci iam identity-provider get --identity-provider-id {user_id}",
        "update": "oci iam identity-provider update --identity-provider-id {user_id} --description {description}",
        "delete": "oci iam identity-provider delete --identity-provider-id {user_id} --force",
        "manage": "oci iam identity-provider group-mapping list --identity-provider-id {user_id}",
    },
    "security/vault-secrets": {
        "create": "oci vault secret create --compartment-id {compartment_id} --secret-name {name} --vault-id {vault_id} --key-id {key_id} --secret-content-content '{content}' --secret-content-content-type BASE64",
        "list": "oci vault secret list --compartment-id {compartment_id} --vault-id {vault_id}",
        "get": "oci vault secret get --secret-id {secret_id}",
        "update": "oci vault secret update --secret-id {secret_id} --secret-content-content '{content}' --secret-content-content-type BASE64",
        "delete": "oci vault secret delete --secret-id {secret_id} --force",
        "manage": "oci vault secret-version list --secret-id {secret_id}",
    },
    "security/vault-keys": {
        "create": "oci kms management key create --compartment-id {compartment_id} --endpoint {endpoint} --display-name {name} --key-shape '{shape}'",
        "list": "oci kms management key list --compartment-id {compartment_id} --endpoint {endpoint}",
        "get": "oci kms management key get --key-id {key_id} --endpoint {endpoint}",
        "update": "oci kms management key update --key-id {key_id} --endpoint {endpoint} --display-name {name}",
        "delete": "oci kms management key schedule-deletion --key-id {key_id} --endpoint {endpoint} --time-of-deletion {time}",
        "manage": "oci kms management key-version list --key-id {key_id} --endpoint {endpoint}",
    },
    "security/encryption": {
        "create": "oci vault vault create --compartment-id {compartment_id} --display-name {name} --vault-type DEFAULT",
        "list": "oci vault vault list --compartment-id {compartment_id}",
        "get": "oci vault vault get --vault-id {vault_id}",
        "update": "oci vault vault update --vault-id {vault_id} --display-name {name}",
        "delete": "oci vault vault schedule-deletion --vault-id {vault_id} --time-of-deletion {time}",
        "manage": "oci kms management key list --compartment-id {compartment_id} --endpoint {endpoint}",
    },
    "security/cloud-guard": {
        "create": "oci cloud-guard target create --compartment-id {compartment_id} --display-name {name} --target-resource-id {compartment_id} --target-resource-type COMPARTMENT",
        "list": "oci cloud-guard target list --compartment-id {compartment_id}",
        "get": "oci cloud-guard target get --target-id {target_id}",
        "update": "oci cloud-guard target update --target-id {target_id} --display-name {name}",
        "delete": "oci cloud-guard target delete --target-id {target_id} --force",
        "manage": "oci cloud-guard problem list --compartment-id {compartment_id}",
    },
    "security/waf": {
        "create": "oci waf web-app-firewall create --compartment-id {compartment_id} --backend-type LOAD_BALANCER --load-balancer-id {lb_id} --web-app-firewall-policy-id {policy_id} --display-name {name}",
        "list": "oci waf web-app-firewall list --compartment-id {compartment_id}",
        "get": "oci waf web-app-firewall get --web-app-firewall-id {target_id}",
        "update": "oci waf web-app-firewall update --web-app-firewall-id {target_id} --display-name {name}",
        "delete": "oci waf web-app-firewall delete --web-app-firewall-id {target_id} --force",
        "manage": "oci waf web-app-firewall-policy list --compartment-id {compartment_id}",
    },
    "security/zero-trust": {
        "create": "oci network-security-group create --compartment-id {compartment_id} --vcn-id {vcn_id} --display-name {name}",
        "list": "oci network-security-group list --compartment-id {compartment_id}",
        "get": "oci network-security-group get --network-security-group-id {security_list_id}",
        "update": "oci network-security-group update --network-security-group-id {security_list_id} --display-name {name}",
        "delete": "oci network-security-group delete --network-security-group-id {security_list_id} --force",
        "manage": "oci network-security-group security-rule list --network-security-group-id {security_list_id}",
    },
    "security/posture-management": {
        "create": "oci cloud-guard detector-recipe create --compartment-id {compartment_id} --display-name {name} --source-detector-recipe-id {detector_id}",
        "list": "oci cloud-guard detector-recipe list --compartment-id {compartment_id}",
        "get": "oci cloud-guard detector-recipe get --detector-recipe-id {detector_id}",
        "update": "oci cloud-guard detector-recipe update --detector-recipe-id {detector_id}",
        "delete": "oci cloud-guard detector-recipe delete --detector-recipe-id {detector_id} --force",
        "manage": "oci cloud-guard problem list --compartment-id {compartment_id}",
    },
    "devops/ci-cd": {
        "create": "oci devops build-pipeline create --project-id {project_id} --display-name {name} --description {description}",
        "list": "oci devops build-pipeline list --project-id {project_id}",
        "get": "oci devops build-pipeline get --build-pipeline-id {pipeline_id}",
        "update": "oci devops build-pipeline update --build-pipeline-id {pipeline_id} --display-name {name}",
        "delete": "oci devops build-pipeline delete --build-pipeline-id {pipeline_id} --force",
        "manage": "oci devops build-pipeline-stage list --build-pipeline-id {pipeline_id}",
    },
    "devops/artifacts": {
        "create": "oci artifacts container repository create --compartment-id {compartment_id} --display-name {name} --is-immutable false --is-public false",
        "list": "oci artifacts container repository list --compartment-id {compartment_id}",
        "get": "oci artifacts container repository get --repository-id {repo_id}",
        "update": "oci artifacts container repository update --repository-id {repo_id} --is-immutable true",
        "delete": "oci artifacts container repository delete --repository-id {repo_id} --force",
        "manage": "oci artifacts container image list --compartment-id {compartment_id} --repository-id {repo_id}",
    },
    "devops/secrets": {
        "create": "oci vault secret create --compartment-id {compartment_id} --secret-name {name} --vault-id {vault_id} --key-id {key_id} --secret-content-content '{content}' --secret-content-content-type BASE64",
        "list": "oci vault secret list --compartment-id {compartment_id} --vault-id {vault_id}",
        "get": "oci vault secret get --secret-id {secret_id}",
        "update": "oci vault secret update --secret-id {secret_id} --secret-content-content '{content}' --secret-content-content-type BASE64",
        "delete": "oci vault secret delete --secret-id {secret_id} --force",
        "manage": "oci vault secret-version list --secret-id {secret_id}",
    },
    "devops/resource-manager": {
        "create": "oci resource-manager stack create --compartment-id {compartment_id} --config-source {config_source} --display-name {name}",
        "list": "oci resource-manager stack list --compartment-id {compartment_id}",
        "get": "oci resource-manager stack get --stack-id {stack_id}",
        "update": "oci resource-manager stack update --stack-id {stack_id} --display-name {name}",
        "delete": "oci resource-manager stack delete --stack-id {stack_id} --force",
        "manage": "oci resource-manager job create --stack-id {stack_id} --operation PLAN",
    },
    "governance/compartments": {
        "create": "oci iam compartment create --compartment-id {tenancy_id} --name {name} --description {description}",
        "list": "oci iam compartment list --compartment-id {tenancy_id}",
        "get": "oci iam compartment get --compartment-id {compartment_id}",
        "delete": "oci iam compartment delete --compartment-id {compartment_id} --force",
        "update": "oci iam compartment update --compartment-id {compartment_id} --description {description}",
        "manage": "oci iam compartment list --compartment-id {tenancy_id}",
    },
    "governance/tagging": {
        "create": "oci iam tag-namespace create --compartment-id {compartment_id} --name {name} --description {description}",
        "list": "oci iam tag-namespace list --compartment-id {compartment_id}",
        "get": "oci iam tag-namespace get --tag-namespace-id {namespace_id}",
        "delete": "oci iam tag-namespace delete --tag-namespace-id {namespace_id} --force",
        "update": "oci iam tag-namespace update --tag-namespace-id {namespace_id} --is-retired true",
        "manage": "oci iam tag create --tag-namespace-id {namespace_id} --name {name} --description {description}",
    },
    "governance/landing-zone": {
        "create": "oci resource-manager stack create --compartment-id {compartment_id} --config-source {config_source} --display-name {name}",
        "list": "oci resource-manager stack list --compartment-id {compartment_id}",
        "get": "oci resource-manager stack get --stack-id {stack_id}",
        "update": "oci resource-manager stack update --stack-id {stack_id} --display-name {name}",
        "delete": "oci resource-manager stack delete --stack-id {stack_id} --force",
        "manage": "oci resource-manager job create --stack-id {stack_id} --operation APPLY",
    },
    "governance/budgets-cost": {
        "create": "oci budgets budget create --compartment-id {tenancy_id} --amount {amount} --budget-processing-period-start-offset 0 --description {description} --display-name {name} --reset-period MONTHLY --target-type COMPARTMENT --targets '[{\"compartmentId\":\"{compartment_id}\"}]'",
        "list": "oci budgets budget list --compartment-id {tenancy_id}",
        "get": "oci budgets budget get --budget-id {alarm_id}",
        "update": "oci budgets budget update --budget-id {alarm_id} --amount {amount}",
        "delete": "oci budgets budget delete --budget-id {alarm_id} --force",
        "manage": "oci budgets alert-rule list --budget-id {alarm_id}",
    },
    "governance/policies-guardrails": {
        "create": "oci iam policy create --compartment-id {compartment_id} --name {policy_name} --statements '[\"{statement}\"]' --description {description}",
        "list": "oci iam policy list --compartment-id {compartment_id}",
        "get": "oci iam policy get --policy-id {policy_id}",
        "delete": "oci iam policy delete --policy-id {policy_id} --force",
        "update": "oci iam policy update --policy-id {policy_id} --statements '[\"{statement}\"]'",
        "manage": "oci iam policy list --compartment-id {compartment_id}",
    },
    "governance/compliance": {
        "create": "oci cloud-guard target create --compartment-id {compartment_id} --display-name {name} --target-resource-id {compartment_id} --target-resource-type COMPARTMENT",
        "list": "oci cloud-guard target list --compartment-id {compartment_id}",
        "get": "oci cloud-guard target get --target-id {target_id}",
        "update": "oci cloud-guard target update --target-id {target_id}",
        "delete": "oci cloud-guard target delete --target-id {target_id} --force",
        "manage": "oci cloud-guard problem list --compartment-id {compartment_id}",
    },
    "governance/audit-readiness": {
        "create": "oci audit configuration update --compartment-id {tenancy_id} --retention-period-days 365",
        "list": "oci audit event list --compartment-id {compartment_id} --start-time {start_time} --end-time {end_time}",
        "get": "oci audit configuration get --compartment-id {tenancy_id}",
        "update": "oci audit configuration update --compartment-id {tenancy_id} --retention-period-days 365",
        "delete": "oci logging log-group delete --log-group-id {log_group_id} --force",
        "manage": "oci audit event list --compartment-id {compartment_id} --start-time {start_time}",
    },
    "governance/resource-discovery": {
        "create": "oci resource-search resource free-text-search --text '{name}' --compartment-id {compartment_id}",
        "list": "oci resource-search resource structured-search --query-text \"query all resources\"",
        "get": "oci resource-search resource structured-search --query-text \"query {name} resources\"",
        "update": "oci tagging tag bulk-edit --compartment-id {compartment_id}",
        "delete": "oci resource-search resource free-text-search --text 'DELETED' --compartment-id {compartment_id}",
        "manage": "oci resource-search resource structured-search --query-text \"query all resources where compartmentId = '{compartment_id}'\"",
    },
    "observability/logging": {
        "create": "oci logging log-group create --compartment-id {compartment_id} --display-name {name} --description {description}",
        "list": "oci logging log-group list --compartment-id {compartment_id}",
        "get": "oci logging log-group get --log-group-id {log_group_id}",
        "delete": "oci logging log-group delete --log-group-id {log_group_id} --force",
        "update": "oci logging log-group update --log-group-id {log_group_id} --display-name {name}",
        "manage": "oci logging log list --log-group-id {log_group_id}",
    },
    "observability/monitoring": {
        "create": "oci monitoring alarm create --compartment-id {compartment_id} --display-name {name} --metric-compartment-id {compartment_id} --namespace {namespace} --query-text '{query}' --severity CRITICAL --destinations '[\"{topic_id}\"]' --is-enabled true",
        "list": "oci monitoring alarm list --compartment-id {compartment_id}",
        "get": "oci monitoring alarm get --alarm-id {alarm_id}",
        "delete": "oci monitoring alarm delete --alarm-id {alarm_id} --force",
        "update": "oci monitoring alarm update --alarm-id {alarm_id} --display-name {name}",
        "manage": "oci monitoring metric-data post --compartment-id {compartment_id} --metric-data '{metric_data}'",
    },
    "observability/stack-monitoring": {
        "create": "oci stack-monitoring monitored-resource create --compartment-id {compartment_id} --display-name {name} --type HOST --resource-time-zone UTC",
        "list": "oci stack-monitoring monitored-resource list --compartment-id {compartment_id}",
        "get": "oci stack-monitoring monitored-resource get --monitored-resource-id {alarm_id}",
        "update": "oci stack-monitoring monitored-resource update --monitored-resource-id {alarm_id} --display-name {name}",
        "delete": "oci stack-monitoring monitored-resource delete --monitored-resource-id {alarm_id} --force",
        "manage": "oci stack-monitoring discovery-job list --compartment-id {compartment_id}",
    },
    "observability/apm": {
        "create": "oci apm-control-plane apm-domain create --compartment-id {compartment_id} --display-name {name} --is-free-tier false",
        "list": "oci apm-control-plane apm-domain list --compartment-id {compartment_id}",
        "get": "oci apm-control-plane apm-domain get --apm-domain-id {alarm_id}",
        "update": "oci apm-control-plane apm-domain update --apm-domain-id {alarm_id} --display-name {name}",
        "delete": "oci apm-control-plane apm-domain delete --apm-domain-id {alarm_id} --force",
        "manage": "oci apm-synthetics monitor list --apm-domain-id {alarm_id}",
    },
    "finops/cost-optimization": {
        "create": "oci usage-api query create --compartment-id {compartment_id} --query-definition '{query_definition}'",
        "list": "oci usage-api query list --compartment-id {compartment_id}",
        "get": "oci usage-api query get --query-id {query_id}",
        "delete": "oci usage-api query delete --query-id {query_id} --force",
        "update": "oci usage-api query update --query-id {query_id} --query-definition '{query_definition}'",
        "manage": "oci usage-api report request --tenant-id {tenancy_id} --time-usage-started {start_time} --time-usage-ended {end_time}",
        "analyze": "oci usage-api summarized-usages request --tenant-id {tenancy_id} --time-usage-started {start_time} --time-usage-ended {end_time} --granularity MONTHLY",
    },
    "finops/showback-chargeback": {
        "create": "oci usage-api query create --compartment-id {compartment_id} --query-definition '{query_definition}'",
        "list": "oci usage-api query list --compartment-id {compartment_id}",
        "get": "oci usage-api report request --tenant-id {tenancy_id} --time-usage-started {start_time} --time-usage-ended {end_time}",
        "update": "oci usage-api query update --query-id {query_id} --query-definition '{query_definition}'",
        "delete": "oci usage-api query delete --query-id {query_id} --force",
        "manage": "oci usage-api subscription list --compartment-id {compartment_id}",
        "analyze": "oci usage-api summarized-usages request --tenant-id {tenancy_id} --time-usage-started {start_time} --time-usage-ended {end_time} --granularity DAILY",
    },
    "finops/rightsizing": {
        "create": "oci optimizer recommendation list --compartment-id {compartment_id}",
        "list": "oci optimizer resource-action list --compartment-id {compartment_id} --recommendation-id {query_id}",
        "get": "oci optimizer resource-action get --resource-action-id {query_id}",
        "update": "oci optimizer resource-action update --resource-action-id {query_id} --status IMPLEMENTED",
        "delete": "oci optimizer resource-action update --resource-action-id {query_id} --status DISMISSED",
        "manage": "oci optimizer profile list --compartment-id {compartment_id}",
        "analyze": "oci optimizer recommendation list --compartment-id {compartment_id} --status OPEN",
    },
    "finops/storage-tiering": {
        "create": "oci os bucket create --name {bucket_name} --compartment-id {compartment_id} --storage-tier Archive",
        "list": "oci os bucket list --compartment-id {compartment_id}",
        "get": "oci os bucket get --bucket-name {bucket_name} --namespace-name {namespace}",
        "update": "oci os object-lifecycle-policy put --bucket-name {bucket_name} --namespace-name {namespace} --items '{schedules}'",
        "delete": "oci os bucket delete --bucket-name {bucket_name} --namespace-name {namespace} --force",
        "manage": "oci os object list --bucket-name {bucket_name} --namespace-name {namespace}",
        "analyze": "oci os bucket get --bucket-name {bucket_name} --namespace-name {namespace}",
    },
    "platform/backup-governance": {
        "create": "oci bv volume-backup-policy create --compartment-id {compartment_id} --display-name {name} --schedules '{schedules}'",
        "list": "oci bv volume-backup-policy list --compartment-id {compartment_id}",
        "get": "oci bv volume-backup-policy get --policy-id {policy_id}",
        "delete": "oci bv volume-backup-policy delete --policy-id {policy_id} --force",
        "update": "oci bv volume-backup-policy update --policy-id {policy_id} --display-name {name}",
        "manage": "oci bv volume-backup-policy-assignment create --asset-id {volume_id} --policy-id {policy_id}",
    },
    "platform/sre-operations": {
        "create": "oci monitoring alarm create --compartment-id {compartment_id} --display-name {name} --metric-compartment-id {compartment_id} --namespace oci_compute --query-text 'CpuUtilization[1m].mean() > 80' --severity CRITICAL --destinations '[\"{topic_id}\"]' --is-enabled true",
        "list": "oci monitoring alarm list --compartment-id {compartment_id}",
        "get": "oci monitoring alarm get --alarm-id {alarm_id}",
        "update": "oci monitoring alarm update --alarm-id {alarm_id} --display-name {name}",
        "delete": "oci monitoring alarm delete --alarm-id {alarm_id} --force",
        "manage": "oci ons subscription list --compartment-id {compartment_id}",
    },
}

SYSTEM_PROMPTS = {
    "compute/instances": "Você é um Cloud Architect especializado no Oracle Cloud Infrastructure (OCI). Sua responsabilidade é fornecer respostas precisas, profundas e extremamente técnicas sobre as Instâncias do Compute.",
    "database/autonomous": "Você é um Database Administrator (DBA) sênior focado em OCI Autonomous Database. Forneça respostas exaustivas abordando as nuances e as melhores práticas em Oracle Cloud.",
    "migration/aws-compute": "Você é um arquiteto de migrações focado em transições do provedor de nuvem legado para o OCI. Suas respostas devem enfatizar a equivalência no OCI de maneira clara e assertiva, sem mencionar o nome de concorrentes diretamente.",
    "terraform/compute": "Você é um DevOps Engineer especialista em Infraestrutura como Código (IaC). Forneça respostas profundas sobre Terraform no ambiente Oracle Cloud (OCI).",
}


def estimate_tokens(text):
    return int(len(text) / 3.4)


def build_params(category, idx, compartment, project, region):
    subcat = category.split("/")[-1]
    return {
        "ad": random.choice(["AD-1", "AD-2", "AD-3"]),
        "shape": random.choice(SHAPES),
        "ocpus": random.choice([2, 4, 8]),
        "memory": random.choice([16, 32, 64]),
        "subnet_id": "ocid1.subnet.oc1.sa-saopaulo-1.xxx",
        "compartment_id": f"ocid1.compartment.oc1..{compartment}",
        "name": f"{subcat}-{project[:5]}-{idx % 100}",
        "instance_id": "ocid1.instance.oc1.sa-saopaulo-1.xxx",
        "rule": "any instance.id != ''",
        "vcn_id": "ocid1.vcn.oc1.sa-saopaulo-1.xxx",
        "cidr": "10.0.0.0/16",
        "bucket_name": f"{project}-bucket",
        "namespace": "namespace-str",
        "storage": random.choice([1, 2, 4]),
        "cores": random.choice([2, 4, 8]),
        "workload": "AUTONOMOUS_TRANSACTION_PROCESSING",
        "k8s_version": "v1.28.2",
        "cluster_id": "ocid1.cluster.oc1.sa-saopaulo-1.xxx",
        "vault_id": "ocid1.vault.oc1.sa-saopaulo-1.xxx",
        "policy_name": f"{project}-policy",
        "statement": f"Allow group {project}-admins to manage all-resources in compartment {compartment}",
        "tenancy_id": "ocid1.tenancy.oc1..xxx",
        "amount": random.choice([1000, 5000, 10000]),
        "tf_version": "1.0.x",
        "app_id": "ocid1.application.oc1.sa-saopaulo-1.xxx",
        "image": "container-image-registry",
        "metric": "CpuUtilization",
        "domain": f"{project}.example.com",
        "table_name": f"{project}_data",
        "version": "8.0",
        "type": "iscsi",
        "size": random.choice([2, 4, 8]),
        "instance_pool_id": "ocid1.instancepool.oc1.sa-saopaulo-1.xxx",
        "infra_id": "ocid1.exadatainfrastructure.oc1.sa-saopaulo-1.xxx",
        "namespace_id": "ocid1.tagnamespace.oc1.sa-saopaulo-1.xxx",
        "image_id": "ocid1.image.oc1.sa-saopaulo-1.xxx",
        "volume_id": "ocid1.volume.oc1.sa-saopaulo-1.xxx",
        "adb_id": "ocid1.autonomousdatabase.oc1.sa-saopaulo-1.xxx",
        "password": "SecurePass123!",
        "action": random.choice(["START", "STOP", "RESET"]),
        "username": f"user_{idx % 100}",
        "description": f"Description for {project}",
        "content": "secret_content_base64",
        "vcn_name": f"vcn-{project[:5]}",
        "exadata_id": "ocid1.exadatainfrastructure.oc1.sa-saopaulo-1.xxx",
        "new_size": random.choice([1, 2, 3, 4, 5]),
        "config_id": "ocid1.instanceconfiguration.oc1.sa-saopaulo-1.xxx",
        "new_cidr": "10.0.1.0/16",
        "drg_id": "ocid1.drg.oc1.sa-saopaulo-1.xxx",
        "lb_id": "ocid1.loadbalancer.oc1.sa-saopaulo-1.xxx",
        "db_system_id": "ocid1.dbsystem.oc1.sa-saopaulo-1.xxx",
        "postgres_id": "ocid1.postgresinstance.oc1.sa-saopaulo-1.xxx",
        "gateway_id": "ocid1.apigateway.oc1.sa-saopaulo-1.xxx",
        "user_id": "ocid1.user.oc1.sa-saopaulo-1.xxx",
        "policy_id": "ocid1.policy.oc1.sa-saopaulo-1.xxx",
        "dynamic_group_id": "ocid1.dynamicgroup.oc1.sa-saopaulo-1.xxx",
        "secret_id": "ocid1.secret.oc1.sa-saopaulo-1.xxx",
        "key_id": "ocid1.key.oc1.sa-saopaulo-1.xxx",
        "endpoint": "https://vault.example.com",
        "time": "2026-12-31T23:59:59Z",
        "target_id": "ocid1.target.oc1.sa-saopaulo-1.xxx",
        "detector_id": "ocid1.detector.oc1.sa-saopaulo-1.xxx",
        "pipeline_id": "ocid1.pipeline.oc1.sa-saopaulo-1.xxx",
        "artifact_id": "ocid1.artifact.oc1.sa-saopaulo-1.xxx",
        "project_id": "ocid1.devopsproject.oc1.sa-saopaulo-1.xxx",
        "repo_id": "ocid1.repository.oc1.sa-saopaulo-1.xxx",
        "stack_id": "ocid1.stack.oc1.sa-saopaulo-1.xxx",
        "config_source": "https://github.com/example/repo",
        "log_group_id": "ocid1.loggroup.oc1.sa-saopaulo-1.xxx",
        "alarm_id": "ocid1.alarm.oc1.sa-saopaulo-1.xxx",
        "query_id": "ocid1.query.oc1.sa-saopaulo-1.xxx",
        "start_time": "2026-01-01T00:00:00Z",
        "end_time": "2026-01-31T23:59:59Z",
        "query_definition": "SELECT * FROM usage",
        "metric_data": "cpu_utilization=80",
        "query": "CpuUtilization[1m].mean() > 80",
        "topic_id": "ocid1.onstopic.oc1.sa-saopaulo-1.xxx",
        "mount_target_id": "ocid1.mounttarget.oc1.sa-saopaulo-1.xxx",
        "security_list_id": "ocid1.securitylist.oc1.sa-saopaulo-1.xxx",
        "function_id": "ocid1.function.oc1.sa-saopaulo-1.xxx",
        "schedules": '[{"backupType":"FULL","period":"DAILY","timeZone":"UTC"}]',
    }


def generate_cli_code(category, intent, params):
    cat_commands = CLI_COMMANDS.get(category, {})
    if intent in cat_commands:
        cmd = cat_commands[intent]
        try:
            return f"```bash\n{cmd.format(**params)}\n```"
        except Exception:
            return f"```bash\n{cmd}\n```"

    # Terraform Fallbacks
    if category.startswith("terraform/"):
        tf_code = "```hcl\n"
        tf_code += f"resource \"oci_{category.split('/')[-1]}_resource\" \"main\" {{\n"
        tf_code += f"  compartment_id = \"{params.get('compartment_id', 'ocid1.compartment.oc1..xxxx')}\"\n"
        tf_code += f"  display_name   = \"{params.get('name', 'example')}\"\n"
        tf_code += "}\n```"
        return tf_code

    # Migration Fallbacks
    if category.startswith("migration/"):
        return f"```bash\noci compute instance launch --availability-domain {params.get('ad', 'AD-1')} --shape {params.get('shape', 'VM.Standard.E4.Flex')} --subnet-id {params.get('subnet_id', 'ocid1.subnet.oc1..xxxx')} --compartment-id {params.get('compartment_id', 'ocid1.compartment.oc1..xxxx')} --display-name oci-migrated-resource\n```"

    # Troubleshooting Fallbacks
    if category.startswith("troubleshooting/"):
        subcat = category.split("/")[-1]
        return f"```bash\noci logging log-search search-logs --log-group-id {params.get('log_group_id', 'ocid1.loggroup.oc1..xxxx')} --search-query 'search \"{params.get('compartment_id', 'ocid1.compartment.oc1..xxxx')}/{subcat}\" | where severity = 'ERROR' | sort by datetime desc | limit 50'\n```"

    # Default fallback
    return f"```bash\noci {category.replace('/', ' ')} {intent} --compartment-id {params.get('compartment_id', 'ocid1.compartment.oc1..xxxx')}\n```"


def get_tech_context(subcat, project, lifecycle, company):
    reasons = [
        f"A implementação de {subcat} no projeto {project} visa mitigar gargalos de performance na fase de {lifecycle}.",
        f"Para a {company}, a resiliência de {subcat} é crítica para manter os SLAs no estágio {lifecycle}.",
        f"A estratégia adota {subcat} como pilar de escalabilidade durante a {lifecycle}.",
        f"O projeto {project} exige que {subcat} seja configurado com atenção redobrada ao compliance no ciclo de {lifecycle}.",
    ]
    return random.choice(reasons)


# ============================================================
#  10 TEMPLATES — v5 Quality + v6 Diversity
# ============================================================

# --- Templates 0-4: Estruturais Ricos (v5/v7 quality) ---

def template_analitico(d):
    """Template 0 — Analítico com Matriz de Riscos"""
    return f"""## Análise de Design: {d["intent_pt"].title()} de {d["subcat"]}
{get_tech_context(d["subcat"], d["project"], d["lifecycle"], d["company"])} Como {d["persona"]}, valide se o compartimento `{d["compartment"]}` possui políticas IAM com mínimo privilégio antes de qualquer operação.

### 1. Contexto de Negócio
A operação de {d["intent_pt"]} em {d["subcat"]} é uma decisão estratégica para {d["company"]} no projeto {d["project"]}. O ciclo de {d["lifecycle"]} exige atenção a compliance e custo. A região {d["region"]} foi selecionada por proximidade dos usuários e Service Limits adequados.

### 2. Matriz de Riscos
| Componente | Risco | Mitigação | Prioridade |
|:---|:---|:---|:---|
| Disponibilidade | Quotas em {d["region"]} | Validar Service Limits previamente | Alta |
| Segurança | Exposição indevida | NSG restritivo + Security Lists | Alta |
| Custo | Oversizing de recursos | Shapes otimizados para workload | Média |
| Compliance | Auditoria pendente | Tagging completo + Logging habilitado | Alta |
| Performance | Latência elevada | CDN + Edge Locations + caching L2 | Média |
| Networking | Configuração incorreta | Validar routes e gateways previamente | Alta |

### 3. Implementação
{d["cli"]}

A execução segue o padrão de idempotência — use `--wait-for-state` para operações síncronas e valide o retorno antes de avançar.

### 4. Trade-offs de Arquitetura
- **Vantagem**: A abordagem escolhida oferece escalabilidade horizontal sem redesign da arquitetura base.
- **Desvantagem**: O custo aumenta proporcionalmente com a carga; reserved instances mitigam isso para workloads previsíveis.
- **Alternativa**: Para ambientes de desenvolvimento, considere Free Tier ou Always Free resources disponíveis no OCI.
- **Decisão recomendada**: Em produção estável, reserve capacity por 1 ano para redução de custo de até 40%.

### 5. Validação Pós-Deploy
- [ ] Status reportado como 'AVAILABLE' ou 'ACTIVE' via CLI ou Console
- [ ] Logs de auditoria gerados e visíveis em OCI Audit Trail
- [ ] Tags aplicadas: cost-center={d["project"]}, environment={d["lifecycle"]}, owner={d["company"]}
- [ ] Monitoring configurado para métricas de CPU, memória, rede e disco
- [ ] Alertas de orçamento configurados via OCI Budgets com threshold de 80%
- [ ] Políticas de retention de logs configuradas para mínimo de 90 dias
- [ ] Backup automático validado com teste de restore bem-sucedido

### 6. Boas Práticas
- Use **Identity Domains** para gerenciamento centralizado de usuários e grupos.
- Configure **alertas de orçamento** via OCI Budgets com notificações email e ONS.
- Utilize **Service Limits** para controlar quotas por compartment e prevenir overspend.
- Implemente **tagging hierárquico** para chargeback/showback granular por equipe.
- Configure **VCN Flow Logs** para auditoria completa do tráfego de rede.
- Use **OCI Cloud Guard** para detecção contínua de configurações inseguras.
- Implemente **backup automatizado** com retenção mínima de 30 dias e teste periódico.
- Configure **Life Cycle Policies** para tiering automático e otimização de custos.

### 7. Referências
- docs.oracle.com/pt-br/iaas/Content/{d["category"].split("/")[0]}/Home.htm
- docs.oracle.com/pt-br/iaas/Content/General/Concepts/oci-api-overview.htm"""


def template_sre(d):
    """Template 1 — SRE/Operacional (~1000 tokens)"""
    return f"""# Protocolo Operacional: {d["subcat"]} ({d["intent_pt"]})
Ciclo: {d["lifecycle"]} | Empresa: {d["company"]} | Projeto: {d["project"]} | Região: {d["region"]}

## Contexto Operacional
{get_tech_context(d["subcat"], d["project"], d["lifecycle"], d["company"])} No regime de **{d["lifecycle"]}**, a latência na região `{d["region"]}` é monitorada continuamente. A equipe de SRE deve seguir os runbooks padronizados e reportar qualquer anomalia no canal de incident, acionando o protocolo de escalation se o impacto atingir nível P1.

## Pré-validação Obrigatória
Antes de executar qualquer operação, confirme:
- IAM: grupo `{d["project"]}-sre` tem permissão `manage {d["subcat"]}-family` no compartimento `{d["compartment"]}`
- Service Limits: capacidade disponível em `{d["region"]}` para o recurso solicitado
- Backup: snapshot ou backup recente existe e foi validado via restore test
- Janela: operação aprovada para o horário atual pelo Change Advisory Board

## Execução
{d["cli"]}

O comando acima deve ser executado após validação de dependências e confirmação de backup recente. Para operações críticas, execute em horário de menor utilização (janela de manutenção) e informe a equipe de plantão com antecedência mínima de 30 minutos.

## Métricas de Saúde
| Métrica | Target | Alerta | Ação |
|:---|:---|:---|:---|
| Uptime | 99.9% | < 99.5% | Acionar on-call |
| Latência P99 | < 200ms | > 500ms | Escalar recursos |
| Error rate | < 0.1% | > 1% | Rollback imediato |
| CPU Utilization | < 70% | > 85% | Auto-scale trigger |
| Capacidade disco | < 75% | > 90% | Expandir volume |

## Runbook de Operações
1. Confirmar pré-validação completa (IAM, limites, backup, janela)
2. Executar o comando acima com parâmetros validados
3. Verificar estado: `oci {d["category"].split("/")[0]} {d["subcat"]} list --compartment-id {d["params"]["compartment_id"]}`
4. Confirmar que todos os ADs estão healthy e métricas dentro do target
5. Configurar alarmes em OCI Monitoring para métricas críticas identificadas
6. Documentar execução no runbook e atualizar dashboard de alertas
7. Notificar stakeholders via canal de comunicação oficial da equipe

## Resiliência e HA
- Valide os **Service Limits** da região antes de escalar recursos horizontalmente.
- Em cenários de HA, a distribuição entre ADs é mandatória para SLA de 99.99%.
- Utilize **OCI Logging** para capturar falhas silenciosas e eventos de auditoria completos.
- Configure **health checks** com intervalos de 30 segundos no OCI Load Balancer.
- Implemente **circuit breaker** para prevenir cascade failures em microservices.
- Use **failover automático** via OCI Load Balancer com DNS switchover configurado.

## Procedimento de Rollback
Em caso de falha crítica ou SLA violado:
1. Acionar equipe de on-call com severity P1 imediatamente
2. Executar rollback para versão anterior do recurso se disponível
3. Restaurar de backup validado mais recente
4. Documentar timeline completo no post-mortem (blameless)
5. Agendar revisão da causa raiz em até 48 horas

## SLAs e Métricas de Sucesso
- Tempo de deploy: < 30 minutos dentro da janela de manutenção
- Uptime pós-deploy: 99.9% monitorado nas primeiras 72 horas
- Custo dentro do orçamento aprovado para o projeto {d["project"]}
- Zero incidentes de segurança relacionados à operação"""


def template_governance(d):
    """Template 2 — Governance/Compliance (~1000 tokens)"""
    return f"""## Framework de Governança: {d["subcat"]}
Empresa: {d["company"]} | Projeto: {d["project"]} | Compartimento: {d["compartment"]} | Região: {d["region"]}

### Políticas de IAM Requeridas
Configurações mínimas obrigatórias (mínimo privilégio):
```
Allow group {d["project"]}-admins to manage {d["subcat"]}-family in compartment {d["compartment"]}
Allow group {d["project"]}-devops to use {d["subcat"]}-family in compartment {d["compartment"]}
Allow group {d["project"]}-viewers to inspect {d["subcat"]}-family in compartment {d["compartment"]}
Allow group {d["project"]}-auditors to read {d["subcat"]}-family in tenancy
```
Para dynamic groups (instâncias de serviço), use matching rules baseadas em OCID ou tag do compartimento.

### Implementação
{d["cli"]}

### Auditoria de Segurança e Rastreabilidade
Todo evento de {d["intent_pt"]} é registrado no **OCI Audit Trail** (retenção mínima: 90 dias). Para LGPD/PCI-DSS/SOC2, configure retenção estendida em Object Storage:
```bash
oci logging log create --log-group-id {d["params"]["log_group_id"]} --display-name {d["project"]}-audit-log --log-type CUSTOM
```
Capturado: usuário, ação, IP de origem, timestamp e resultado.

### Checklist de Conformidade
| Item | Status | Evidência Requerida |
|:---|:---|:---|
| Tagging cost-center | [ ] | Tag namespace aplicada e validada |
| Tagging environment | [ ] | Lifecycle tag consistente com projeto |
| Tagging owner | [ ] | Email do responsável técnico |
| Logging habilitado | [ ] | OCI Audit Trail ativo e retendo dados |
| Monitoring ativo | [ ] | Métricas, alarmes e dashboards definidos |
| Alertas de budget | [ ] | OCI Budgets configurado com threshold |
| Backup policy | [ ] | Schedule definido, aplicado e testado |
| Retention policy | [ ] | Lifecycle rules configuradas no storage |
| Acesso revisado | [ ] | Revisão mensal de permissões IAM |

### Resource Manager (IaC)
Para automação via Terraform, utilize OCI Resource Manager com state remoto:
```hcl
resource "oci_core_{d["subcat"]}" "main" {{
  compartment_id = "{d["params"]["compartment_id"]}"
  display_name   = "{d["params"]["name"]}"
  freeform_tags  = {{ "cost-center" = "{d["project"]}", "env" = "{d["lifecycle"]}" }}
  # Configurações específicas do {d["subcat"]}
}}
```
Stacks versionadas em Git com CI/CD via OCI DevOps e aprovação obrigatória antes de apply em produção.

### Relatórios e Métricas de Governança
- Relatórios de compliance gerados mensalmente via OCI Usage API e exportados para OCI Analytics.
- **Usage Cost Reports** com alocação granular por tag de cost-center e projeto.
- **Chargeback Reports** automáticos para bilhetagem interna entre unidades de negócio.
- Dashboard executivo com visibilidade de compliance score e desvios identificados.

### Recomendações de Otimização de Custo
- Utilize **reserved capacity** com compromisso anual para economia de até 40% em workloads steady-state.
- Configure **auto-scaling** baseado em métricas de CPU/memória para resposta automática à demanda.
- Implemente **shutdown schedule** para ambientes de dev/test fora do horário comercial (economia de ~60%).
- Use **preemptible instances** para workloads batch tolerantes a interrupções com desconto significativo."""


def template_migration(d):
    """Template 3 — Migration/Equivalência (~1050 tokens)"""
    return f"""### Guia de Migração: {d["subcat"]} → OCI
Cenário: {d["lifecycle"]} | Região: {d["region"]} | Empresa: {d["company"]} | Projeto: {d["project"]}

## Análise Técnica Pré-Migração
{get_tech_context(d["subcat"], d["project"], d["lifecycle"], d["company"])} A migração de ambientes legado para OCI requer análise cuidadosa de equivalências de serviço, networking, security e custo. Ferramentas como OCI Migration Service e Cloud Readiness Assessments ajudam a identificar similaridades, gaps e riscos antes do início da migração formal.

## Implementação no OCI
{d["cli"]}

## Tabela de Equivalências de Serviço
| Categoria | On-Premise/Legacy | OCI Equivalent | Notas de Migração |
|:---|:---|:---|:---|
| Compute | VMware vSphere | OCI Compute | Shapes Flexíveis com OCPUs/memória ajustáveis |
| Storage | EMC VMAX | OCI Block Storage | Performance/Enterprise com replicação cross-region |
| Storage | NetApp NAS | OCI File Storage | NFS/ONTAP com snapshots integrados |
| Database | Oracle DB Enterprise | OCI Autonomous DB | ATP/JSON com patching automático |
| Network | Cisco ACI/Nexus | OCI Networking VCN | Security Lists + NSGs por recurso |
| LB | F5 BigIP | OCI Load Balancer | Regional com health checks configuráveis |
| Identity | MS Active Directory | OCI IAM Identity Domains | SAML/OIDC federation nativo |
| Monitoring | Nagios/Zabbix | OCI Monitoring + Logging | Metrics, Alarms, Log Analytics integrados |

## Ferramentas de Migração OCI
- **OCI Migration Service**: análise automatizada de workloads e geração de planos
- **Cloud Coach**: guias de melhores práticas e validação de arquitetura
- **Rclone/OCI Data Transfer**: transferência de dados em massa para Object Storage
- **Velero + OKE**: migração de workloads Kubernetes e backups de cluster

## Estratégia de Migração em Fases
1. **Assessment**: OCI Migration Service analisa workloads, dependências e TCO
2. **Planning**: Documente RPO/RTO, sizing de recursos e janelas de cutover
3. **Proof of Concept**: Deploy na região {d["region"]} com dados de teste
4. **Pilot**: Migração de workloads não-críticos com validação funcional completa
5. **Production**: Cutover com janela de manutenção aprovada e rollback testado
6. **Validation**: Testes de regressão, performance, disaster recovery e segurança

## Cutover Checklist
- [ ] Conectividade validada entre compartments e on-premise via FastConnect/VPN
- [ ] Integridade de dados verificada com checksums pós-transferência
- [ ] Teste de failback de disaster recovery executado com sucesso
- [ ] Documentação técnica e runbooks operacionais atualizados
- [ ] Equipe operacional treinada nas ferramentas e consoles OCI
- [ ] Monitoramento, alertas e dashboards configurados e validados
- [ ] Tagging completo aplicado: cost-center={d["project"]}, env={d["lifecycle"]}

## Pós-Migração e Otimização Contínua
1. Configure OCI Monitoring com alertas proativos de performance e disponibilidade
2. Ative OCI Cloud Guard para monitoramento de postura de segurança
3. Execute cleanup de recursos legado após período de validação de 30 dias
4. Otimize shapes com OCI Optimizer baseado em utilização real do primeiro mês
5. Revise custos mensalmente com OCI Cost Analysis filtrado por tag de projeto

**Referências**: docs.oracle.com/pt-br/iaas/Content/migration/overview.htm"""


def template_executive(d):
    """Template 4 — Resumo Executivo (~1000 tokens)"""
    return f"""## Resumo Executivo: {d["subcat"]} | {d["intent_pt"]}
**Projeto**: {d["project"]} | **Região**: {d["region"]} | **Empresa**: {d["company"]} | **Persona**: {d["persona"]}

### Contexto de Negócio
{get_tech_context(d["subcat"], d["project"], d["lifecycle"], d["company"])} A operação de {d["intent_pt"]} para {d["subcat"]} no projeto {d["project"]} é crítica para o ciclo de {d["lifecycle"]} de {d["company"]}.

### Implementação Técnica Proposta
{d["cli"]}

Implementação alinhada ao OCI Well-Architected Framework (resiliência, segurança, observabilidade).

### Benefícios Esperados
- **Resiliência**: Alta disponibilidade multi-AD com Service Limits adequados ao workload
- **Custo**: Shapes otimizados para o perfil real de utilização com auto-scaling
- **Compliance**: Conformidade com políticas corporativas de security e auditoria
- **Observability**: Monitoramento completo via OCI Monitoring, Logging e APM
- **Automação**: Deploy via IaC (Terraform/Resource Manager) para repeatability

### Arquitetura de Referência
- **Acesso**: IAM `{d["project"]}-admins`, mínimo privilégio por grupo
- **Rede**: VCN com subnets privadas, NSGs e Security Lists dedicados
- **Dados**: Replicação cross-region para DR + backup automatizado
- **Observability**: OCI Monitoring + alarmes ONS configurados

### Status Alvo Pós-Execução
- AVAILABLE / ACTIVE (para operações de criação e atualização de configuração)
- RUNNING (para recursos de compute e serviços em operação contínua)
- Conformant (para validações de security posture via Cloud Guard)

### Restrições e Parâmetros
| Campo | Valor |
|:---|:---|
| Tipo de Recurso | {d["subcat"]} |
| Operação Solicitada | {d["intent_pt"]} |
| Fase do Projeto | {d["lifecycle"]} |
| Restrição Crítica | {d["constraint"]} |
| Persona Responsável | {d["persona"]} |
| Região OCI | {d["region"]} |
| Compartimento | {d["compartment"]} |

### ROADMAP E CUSTOS
**Custo Base**: USD 200–500/mês para baseline inicial em `{d["region"]}`.
1. Deploy em staging (compartimento `{d["compartment"]}`)
2. Configurar dashboards e alertas
3. Deploy e validação em produção
4. Otimização nos 30 dias subsequentes

### Riscos e Mitigações
| Risco | Probabilidade | Impacto | Mitigação |
|:---|:---|:---|:---|
| Custo acima do budget | Média | Alto | OCI Budgets + alertas automáticos |
| Performance abaixo do SLA | Baixa | Alto | Load testing + right-sizing contínuo |
| Violação de segurança | Baixa | Crítico | Cloud Guard + Security Advisor |
| Falha de disponibilidade | Baixa | Alto | Multi-AD + backup + DR testado |"""


# --- Templates 5-9: Diversidade de Formato (v6 style + calibrado 850-1100 tokens) ---

def template_conciso(d):
    """Template 5 — Conciso Estruturado (~950 tokens)"""
    subcat0 = d["category"].split("/")[0]
    return f"""## {d["intent_pt"]} de {d["subcat"]} em OCI

**Empresa**: {d["company"]} | **Projeto**: {d["project"]} | **Ambiente**: {d["lifecycle"]} | **Região**: {d["region"]}

### Visão Geral
{get_tech_context(d["subcat"], d["project"], d["lifecycle"], d["company"])} A restrição de `{d["constraint"]}` é mandatória nesse contexto e deve ser validada e documentada antes da execução de qualquer comando.

### Pré-requisitos de IAM e Infraestrutura
- Grupo `{d["project"]}-admins` com permissão `manage {d["subcat"]}-family` no compartimento `{d["compartment"]}`
- Grupo `{d["project"]}-devops` com permissão `use {d["subcat"]}-family` para operações rotineiras
- Grupo `{d["project"]}-viewers` com permissão `inspect {d["subcat"]}-family` para auditoria
- Service Limits verificados na região `{d["region"]}` — abrir SR com antecedência se necessário
- VCN, subnets e NSGs configurados conforme padrão de segurança do projeto
- Backup ou snapshot do estado atual validado antes de qualquer mudança

### Comando de Execução
{d["cli"]}

### Validação Pós-Execução
- Use `--wait-for-state` disponível na maioria dos recursos para tracking síncrono
- Aplique tagging obrigatório: `cost-center={d["project"]}`, `env={d["lifecycle"]}`, `owner={d["company"]}`
- Verifique status final via CLI:
```bash
{d["list_cli"]}
```
- Confirme visibilidade nos dashboards de OCI Monitoring e ausência de alertas críticos
- Valide que eventos foram registrados no OCI Audit Trail (retenção mínima 90 dias)

### Configurações Recomendadas pela Oracle
- **Backup**: Configure backup automático com retenção mínima de 30 dias e teste mensal de restore
- **Auto-scaling**: Defina policies baseadas em CPU > 70% para resposta automática à carga
- **Security**: Habilite OCI WAF e Cloud Guard para detecção proativa de ameaças
- **Cost Control**: Configure OCI Budgets com alertas quando custo atingir 80% do limite aprovado
- **Compliance**: Execute scan mensal com OCI Security Advisor e corrija findings críticos

### Troubleshooting Rápido
| Erro | Causa | Solução |
|:---|:---|:---|
| AuthorizationFailed | IAM insuficiente | Revisar policy do grupo `{d["project"]}-admins` |
| LimitExceeded | Quota atingida | Verificar Service Limits e abrir SR |
| NotFound | OCID incorreto | Validar OCIDs com `oci ... list` |

### Resumo da Operação
| Parâmetro | Valor |
|:---|:---|
| Região | {d["region"]} |
| Compartimento | {d["compartment"]} |
| Fase do Ciclo | {d["lifecycle"]} |
| Tipo de Ação | {d["intent_pt"]} |
| Persona | {d["persona"]} |
| Restrição | {d["constraint"]} |

**Ref**: docs.oracle.com/pt-br/iaas/Content/{subcat0.title()}/"""


def template_qa(d):
    """Template 6 — Direto Q&A Técnico (~1000 tokens)"""
    subcat0 = d["category"].split("/")[0]
    return f"""## {d["subcat"]}: {d["intent_pt"]}

**Cenário**: {d["company"]} — projeto {d["project"]} em fase de {d["lifecycle"]}

**Contexto Técnico**: {get_tech_context(d["subcat"], d["project"], d["lifecycle"], d["company"])}

**Região**: {d["region"]} | **Compartimento**: {d["compartment"]} | **Restrição**: {d["constraint"]} | **Persona**: {d["persona"]}

### Solução OCI Recomendada

{d["cli"]}

### Premissas e Notas Técnicas Críticas
- **IAM Obrigatório**: grupo `{d["project"]}-admins` deve ter permissão `manage {d["subcat"]}-family` no compartimento `{d["compartment"]}`
- **Quotas**: verificar Service Limits para {d["subcat"]} na região `{d["region"]}` antes da execução — abrir SR com antecedência
- **Idempotência**: reexecutar o comando não deve criar recursos duplicados — nomes e tags garantem unicidade
- **Estado síncrono**: usar `--wait-for-state` quando disponível ou implementar polling manual a cada 30s
- **Tags obrigatórias**: `cost-center={d["project"]}`, `env={d["lifecycle"]}`, `team={d["persona"]}`, `owner={d["company"]}`
- **Networking**: confirmar subnets privadas, NSGs e Security Lists conforme padrão de segurança do projeto
- **Backup**: validar existência de snapshot ou backup recente antes de operações destrutivas ou de modificação

### Verificar Estado e Listar Recursos
```bash
# Verificar estado do recurso recém-criado ou modificado
{d["list_cli"]}

# Verificar logs de auditoria da operação
oci audit event list --compartment-id {d["params"]["compartment_id"]} --start-time {d["params"]["start_time"]}
```

### Troubleshooting Comum
| Problema | Causa Provável | Diagnóstico | Solução |
|:---|:---|:---|:---|
| AuthorizationFailed | IAM insuficiente | Verificar group membership | Revisar policies no compartimento pai |
| LimitExceeded | Quota atingida | `oci limits service list` | Abrir SR Oracle para aumento |
| Timeout na criação | Recurso assíncrono | Polling com `--wait-for-state` | Aumentar timeout para 10+ minutos |
| NetworkError | NSG/SL restritivo | VCN Flow Logs + audit | Revisar regras de ingress/egress |
| NotFound 404 | OCID incorreto | `oci ... list` para validar | Confirmar região e compartimento |

### Best Practices Aplicáveis no Projeto {d["project"]}
- Mantenha configurações versionadas em Git com code review via OCI DevOps
- Utilize tags padronizadas desde o primeiro recurso criado no compartimento
- Configure alertas de custo no OCI Budgets antes de provisionar recursos em produção
- Documente todos os OCIDs em vault seguro (OCI Vault Secrets) com rotação automática
- Revise permissões de IAM a cada 30 dias seguindo princípio do mínimo privilégio
- Ative OCI Cloud Guard para detecção contínua de misconfigurations e ameaças

**Documentação Oficial**: docs.oracle.com/pt-br/iaas/Content/{subcat0.title()}/"""


def template_stepbystep(d):
    """Template 7 — Passo-a-Passo Detalhado (~1000 tokens)"""
    subcat0 = d["category"].split("/")[0]
    return f"""# {d["intent_pt"]} de {d["subcat"]} — OCI Step-by-Step

**Cenário**: {d["company"]}, projeto {d["project"]}, ambiente {d["lifecycle"]}, persona: {d["persona"]}

**Restrição**: {d["constraint"]} | **Região**: {d["region"]} | **Compartimento**: {d["compartment"]}

---

### Passo 1: Verificar Pré-requisitos Completos
Antes de qualquer execução, confirme todos os itens abaixo:
- **IAM**: grupo `{d["project"]}-admins` configurado corretamente no compartimento `{d["compartment"]}`
- **IAM Serviços**: dynamic groups configurados para instâncias e serviços que precisam de acesso
- **Service Limits**: verificar quotas disponíveis em `{d["region"]}` para {d["subcat"]} — abrir SR se necessário
- **Networking**: subnets privadas, NSGs e Security Lists configurados conforme padrão de segurança
- **Backup**: confirmar existência de snapshot ou backup validado do estado atual
- **Compliance**: restrição `{d["constraint"]}` documentada e aprovada pelo time de security

### Passo 2: Executar Operação Principal
{d["cli"]}

### Passo 3: Validar Resultado da Operação
- Aguardar estado AVAILABLE/ACTIVE usando `--wait-for-state` (timeout recomendado: 10 minutos)
- Verificar listagem completa e confirmar presença do recurso:
```bash
{d["list_cli"]}
```
- Confirmar visibilidade no OCI Console na região `{d["region"]}`
- Validar que não há alertas críticos ativos no OCI Monitoring

### Passo 4: Aplicar Tagging Obrigatório
```bash
# freeform-tags obrigatórias conforme política corporativa:
# cost-center={d["project"]}, env={d["lifecycle"]}, owner={d["company"]}, team={d["persona"]}
{d["update_cli"]} --freeform-tags '{{"cost-center": "{d["project"]}", "env": "{d["lifecycle"]}"}}'
```

### Passo 5: Configurar Monitoramento e Alertas
- Adicionar recurso ao dashboard de OCI Monitoring existente do projeto
- Criar alarmes específicos para métricas críticas do serviço {d["subcat"]}
- Configurar notificações via OCI Notifications (email, Slack, PagerDuty)
- Validar que OCI Cloud Guard está monitorando o compartimento `{d["compartment"]}`

### Passo 6: Segurança e Compliance
- Executar scan de postura com OCI Security Advisor no compartimento
- Confirmar que nenhum recurso é acessível publicamente sem justificativa
- Validar que encryption at-rest e in-transit estão habilitados
- Confirmar ativação de OCI Audit Trail com retenção de 90+ dias

### Passo 7: Documentar e Encerrar
- Atualizar CMDB com novos OCIDs, configurações e dependências
- Registrar procedimento executado no runbook da equipe de SRE
- Comunicar conclusão a stakeholders do projeto {d["project"]} via canal oficial
- Arquivar evidências de execução: screenshots, logs e outputs no sistema de tickets

### Dicas e Ferramentas OCI
- Use **OCI Cloud Shell** para execução sem configuração local de CLI ou credenciais
- Configure **OCI Monitoring** com métricas customizadas para o perfil do workload
- Utilize **OCI Cost Analysis** com filtros por tag para tracking granular de custos
- Implemente **OCI Events** para automação de respostas a mudanças de lifecycle state

**Referência**: docs.oracle.com/pt-br/iaas/Content/{subcat0.title()}/"""


def template_minimal_cli(d):
    """Template 8 — CLI Focused com Checklist e Troubleshooting (~950 tokens)"""
    subcat0 = d["category"].split("/")[0]
    return f"""## {d["subcat"]}: {d["intent_pt"]}

**Região**: {d["region"]} | **Compartimento**: {d["compartment"]} | **Projeto**: {d["project"]} | **Fase**: {d["lifecycle"]}

### Contexto Técnico
{get_tech_context(d["subcat"], d["project"], d["lifecycle"], d["company"])} A restrição crítica `{d["constraint"]}` deve ser observada e validada em todas as etapas da execução, sem exceções.

### Políticas IAM Necessárias
Configurações mínimas de IAM antes da execução:
```
Allow group {d["project"]}-admins to manage {d["subcat"]}-family in compartment {d["compartment"]}
Allow group {d["project"]}-devops to use {d["subcat"]}-family in compartment {d["compartment"]}
```

### Comando Principal
{d["cli"]}

### Parâmetros Chave da Execução
- **IAM group**: `{d["project"]}-admins` → permissão `manage {d["subcat"]}-family` no compartimento `{d["compartment"]}`
- **Restrição operacional**: {d["constraint"]} — validar conformidade antes de executar
- **Estado atual do ambiente**: {d["lifecycle"]} — considerar impacto de downtime
- **Persona e responsabilidade**: {d["persona"]} é o responsável técnico pela operação
- **Compartment ID**: `{d["params"]["compartment_id"]}`

### Checklist Completo de Execução
- [ ] IAM verificado — policies aplicadas corretamente
- [ ] Service Limits verificados na região `{d["region"]}`
- [ ] Backup/snapshot realizado antes da operação
- [ ] Janela de manutenção aprovada pela equipe
- [ ] Comando executado com sucesso e retorno validado
- [ ] Estado AVAILABLE/ACTIVE confirmado via polling
- [ ] Tags aplicadas: cost-center={d["project"]}, env={d["lifecycle"]}
- [ ] Monitoramento verificado — métricas visíveis no dashboard
- [ ] Documentação atualizada no CMDB e runbook

### Validação de Estado
```bash
{d["list_cli"]}
```

### Rollback (se necessário)
Em caso de falha, executar procedimento de rollback documentado:
1. Identificar OCID do recurso com problema
2. Executar terminação ou reversão conforme tipo de recurso
3. Restaurar de backup ou snapshot mais recente disponível
4. Notificar equipe de SRE e registrar incidente

### Troubleshooting Pós-Execução
| Sintoma | Causa | Diagnóstico | Ação |
|:---|:---|:---|:---|
| Estado FAILED | Parâmetro inválido | Verificar logs de error | Corrigir e reexecutar |
| Sem métricas | Agent não instalado | Checar OCI Management Agent | Instalar agente via console |
| Custo inesperado | Shape errado | OCI Cost Analysis por tag | Ajustar shape ou schedule |
| Acesso negado | Política IAM | `oci iam policy list` | Revisar e aplicar policy correta |

### Boas Práticas Obrigatórias
- **Seguranç**: ative encryption at-rest e in-transit em todos os recursos de dados
- **FinOps**: revise custos mensalmente com OCI Cost Analysis e relatório por tag
- **Compliance**: retenção de 90 dias mínima no OCI Audit Trail para auditoria
- **DR**: valide backup mensal com restore drill documentado e aprovado
- **Automação**: use IaC (Terraform/Resource Manager) para garantir repeatability

**Ref**: docs.oracle.com/pt-br/iaas/Content/{subcat0.title()}/"""


def template_risk_focus(d):
    """Template 9 — Foco em Riscos com Controles detalhados (~900 tokens)"""
    return f"""## {d["intent_pt"]} — {d["subcat"]}

### Contexto de Risco
| Campo | Valor |
|:---|:---|
| Empresa | {d["company"]} |
| Projeto | {d["project"]} |
| Ciclo de Vida | {d["lifecycle"]} |
| Restrição Crítica | {d["constraint"]} |
| Região | {d["region"]} |
| Compartimento | {d["compartment"]} |

### Análise de Impacto Pré-Execução
{get_tech_context(d["subcat"], d["project"], d["lifecycle"], d["company"])} É essencial avaliar o impacto da operação de {d["intent_pt"]} antes da execução, especialmente em ambientes de {d["lifecycle"]} onde a tolerância a falhas é reduzida.

### Riscos Identificados e Mitigações
| Risco | Probabilidade | Impacto | Mitigação Recomendada |
|:---|:---|:---|:---|
| Falha de IAM | Alta | Bloqueante | Validar `{d["project"]}-admins` antes |
| Quota insuficiente | Média | Alto | Verificar Service Limits em {d["region"]} |
| Violação de rede | Baixa | Alto | NSG restritivo + Security Lists |
| Drift de custo | Média | Médio | Budget alerts + tagging |
| Indisponibilidade | Baixa | Crítico | Deploy multi-AD + health checks |
| Compliance gap | Baixa | Alto | Audit trail + Cloud Guard |

### Execução com Controles
{d["cli"]}

### Controles Pós-Execução
1. **Estado**: aguardar AVAILABLE/ACTIVE com `--wait-for-state`
2. **Auditoria**: confirmar eventos registrados no OCI Audit Trail
3. **Tags obrigatórias**: cost-center={d["project"]}, env={d["lifecycle"]}
4. **Monitoramento**: verificar métricas visíveis no OCI Monitoring
5. **Compliance**: executar scan com OCI Cloud Guard após criação
6. **Documentação**: atualizar CMDB e cronograma de revisão mensal

### Conformidade e Governança
- [ ] Tagging padronizado aplicado conforme política corporativa
- [ ] Logging habilitado e retendo dados por mínimo 90 dias
- [ ] Monitoramento ativo com alertas configurados
- [ ] Acesso restrito por IAM com mínimo privilégio
- [ ] Backup policy aplicada e testada com restore drill
- [ ] Relatório de compliance gerado e arquivado

### Ações de Contingência e Rollback
Se a operação falhar ou SLA for violado, execute sequencialmente:
```bash
# 1. Identificar causa raiz via audit trail
oci audit event list --compartment-id {d["params"]["compartment_id"]} --start-time {d["params"]["start_time"]}

# 2. Listar estado atual dos recursos do compartimento
oci resource-search resource structured-search --query-text "query all resources where compartmentId = '{d["params"]["compartment_id"]}'"
```
Acionar equipe de SRE com severity P1 se impacto em produção. Documentar timeline completo no post-mortem blameless em até 48 horas.

### Recomendações de Segurança e FinOps
- **Zero Trust**: nenhum recurso deve ter acesso público sem aprovação explícita documentada
- **Encryption**: habilite CMK (Customer Managed Keys) via OCI Vault para datos sensíveis
- **Cost Governance**: tag `cost-center={d["project"]}` obrigatória em todos os recursos criados
- **Rightsizing**: use OCI Optimizer mensalmente para identificar recursos superprovisionados
- **Audit**: todos os eventos de {d["intent_pt"]} ficam registrados no OCI Audit Trail por 90 dias

**Referência**: docs.oracle.com/pt-br/iaas/Content/{d["category"].split("/")[0]}/Home.htm"""


# Mapa dos 10 templates
TEMPLATES = [
    template_analitico,    # 0 — v5 quality
    template_sre,          # 1 — v5 quality
    template_governance,   # 2 — v5 quality
    template_migration,    # 3 — v5 quality
    template_executive,    # 4 — v5 quality
    template_conciso,      # 5 — v6 diversity
    template_qa,           # 6 — v6 diversity
    template_stepbystep,   # 7 — v6 diversity
    template_minimal_cli,  # 8 — v6 diversity
    template_risk_focus,   # 9 — v6 diversity
]


def generate_question(category, idx, company, project, region, compartment, persona, intent, constraint, lifecycle):
    """Questões ricas (v5 style) — 4 variantes por rotação"""
    subcat = category.split("/")[-1]
    intent_pt = INTENTS_PT.get(intent, intent)
    templates = [
        f"Atuando como {persona} na empresa {company}, minha missão é executar a tarefa de {intent_pt} para {subcat} no escopo do projeto {project} (região {region}, compartimento {compartment}). Como proceder?",
        f"Para o ambiente {lifecycle} do nosso projeto {project}, precisamos realizar: {intent_pt} de {subcat}. Quais as melhores estratégias e comandos no OCI considerando a restrição: {constraint}?",
        f"Gostaria de saber a recomendação oficial do OCI para a tarefa de {intent_pt} em {subcat}. Nossa empresa ({company}) possui o cenário {lifecycle} e precisamos garantir que respeitaremos o pré-requisito de {constraint}.",
        f"Dada a infraestrutura da {company} (compartimento {compartment}), detalhe o passo a passo seguro para {intent_pt} de {subcat} no projeto {project}.",
    ]
    return templates[idx % len(templates)]


def generate_example(category, idx):
    company = random.choice(COMPANIES)
    project = random.choice(PROJECTS)
    region = random.choice(REGIONS)
    compartment = random.choice(COMPARTMENTS)
    persona = random.choice(PERSONAS)
    constraint = random.choice(CONSTRAINTS)
    lifecycle = random.choice(LIFECYCLE_STAGES)

    # Intents especializados por domínio (v5/v6 logic)
    intents = ["create", "list", "get", "update", "delete", "manage"]
    intent = intents[idx % len(intents)]
    if "migration" in category:
        intent = "describe"
    elif "troubleshooting" in category:
        intent = "diagnose"
    elif "finops" in category:
        intent = "analyze"

    subcat = category.split("/")[-1]
    intent_pt = INTENTS_PT.get(intent, intent)

    params = build_params(category, idx, compartment, project, region)
    cli = generate_cli_code(category, intent, params)

    # Dados compartilhados entre templates
    d = {
        "category": category,
        "subcat": subcat,
        "intent": intent,
        "intent_pt": intent_pt,
        "company": company,
        "project": project,
        "region": region,
        "compartment": compartment,
        "persona": persona,
        "constraint": constraint,
        "lifecycle": lifecycle,
        "cli": cli,
        "list_cli": generate_cli_code(category, "list", params),
        "update_cli": generate_cli_code(category, "update", params),
        "params": params,
    }

    # Rotação entre os 10 templates (5 v5-quality + 5 v6-diversity)
    answer = TEMPLATES[idx % len(TEMPLATES)](d)
    
    # HARD CAP para respeitar estritamente o MAX_TOKENS
    while estimate_tokens(answer) > MAX_TOKENS:
        # Pica o final do texto até caber, evitando cortar no meio da tag final
        parts = answer.rsplit('\n', 1)
        if len(parts) == 2:
            answer = parts[0]
        else:
            answer = answer[:-50]

    question = generate_question(category, idx, company, project, region, compartment, persona, intent, constraint, lifecycle)

    sys_prompt = SYSTEM_PROMPTS.get(
        category,
        f"Você é um arquiteto e especialista experiente em OCI focado no domínio de {category}. Forneça orientações técnicas, profundas e definitivas."
    )

    return {
        "messages": [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": question},
            {"role": "assistant", "content": answer},
        ],
        "metadata": {
            "category": category,
            "difficulty": "intermediate",
            "company": company,
            "project": project,
            "region": region,
            "compartment": compartment,
            "persona": persona,
            "intent": intent,
            "constraint": constraint,
            "lifecycle": lifecycle,
            "source": "generate_v7_combined",
        },
    }


def main():
    output_dir = Path("data/curated")
    output_dir.mkdir(parents=True, exist_ok=True)

    total = 0
    token_stats = []

    for category in CATEGORIES:
        examples = [generate_example(category, i) for i in range(EXAMPLES_PER_CATEGORY)]

        # Estatísticas de tokens por categoria
        cat_tokens = []
        for ex in examples:
            text = " ".join(m["content"] for m in ex["messages"])
            t = estimate_tokens(text)
            cat_tokens.append(t)
            token_stats.append(t)

        safe_name = category.replace("/", "-")
        with open(output_dir / f"{safe_name}.jsonl", "w", encoding="utf-8") as f:
            for ex in examples:
                f.write(json.dumps(ex, ensure_ascii=False) + "\n")

        avg_t = sum(cat_tokens) // len(cat_tokens)
        print(f"✅ {category}: {len(examples)} ex | tokens avg={avg_t} min={min(cat_tokens)} max={max(cat_tokens)}")
        total += len(examples)

    # Sumário global
    if token_stats:
        below = sum(1 for t in token_stats if t < MIN_TOKENS)
        above = sum(1 for t in token_stats if t > MAX_TOKENS)
        print(f"\n🎯 Total: {total} exemplos em {len(CATEGORIES)} categorias")
        print(f"📊 Tokens: avg={sum(token_stats)//len(token_stats)} min={min(token_stats)} max={max(token_stats)}")
        print(f"⚠️  Fora do range [{MIN_TOKENS}-{MAX_TOKENS}]: {below} abaixo | {above} acima")
        print(f"📁 Output: {output_dir}")


if __name__ == "__main__":
    main()
