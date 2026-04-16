import json
import random
import re
from pathlib import Path

random.seed(42)

EXAMPLES_PER_CATEGORY = 180

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

SHAPES = ["VM.Standard.E4.Flex", "VM.Standard.A1.Flex", "VM.Optimized3.Flex", "BM.Standard.E5", "VM.GPU.A10.1", "VM.Standard3.Flex", "VM.DenseIO.E4.Flex"]
REGIONS = ["sa-saopaulo-1", "us-ashburn-1", "us-phoenix-1", "eu-frankfurt-1", "uk-london-1", "ap-mumbai-1", "ap-tokyo-1", "ca-toronto-1", "ap-sydney-1"]
COMPARTMENTS = ["production", "development", "staging", "sandbox", "shared-services", "networking", "security", "data-platform", "analytics", "devops"]
COMPANIES = ["TechCorp Brasil", "DataFlow Solutions", "CloudNative Inc", "FinServe Digital", "RetailMax Online", "HealthTech Systems", "EduPlatform Global", "LogiTrack Logistics", "MediaStream Pro", "AgriTech Innovations", "SecureBank Corp", "TravelHub Platform", "SmartCity IoT", "GameForge Studios", "BioResearch Labs", "AutoDrive Systems", "EnergyGrid Monitor", "FoodChain Trace", "LegalDoc Manager", "InsureTech Plus"]
PROJECTS = ["ecommerce-migration", "data-lake-modernization", "microservices-refactor", "disaster-recovery-setup", "compliance-audit", "cost-optimization", "performance-tuning", "security-hardening", "multi-region-expansion", "hybrid-cloud-integration", "ci-cd-pipeline", "monitoring-overhaul", "backup-strategy", "zero-trust-implementation", "api-gateway-deployment", "container-platform", "serverless-transformation", "database-consolidation", "network-segmentation", "identity-federation"]
INTENTS = ["create", "list", "get", "update", "delete", "manage"]
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
    "governance/policies-guardrails": {
        "create": "oci iam policy create --compartment-id {compartment_id} --name {policy_name} --statements '[\"{statement}\"]' --description {description}",
        "list": "oci iam policy list --compartment-id {compartment_id}",
        "get": "oci iam policy get --policy-id {policy_id}",
        "delete": "oci iam policy delete --policy-id {policy_id} --force",
        "update": "oci iam policy update --policy-id {policy_id} --statements '[\"{statement}\"]'",
        "manage": "oci iam policy list --compartment-id {compartment_id}",
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
    "finops/cost-optimization": {
        "create": "oci usage-api query create --compartment-id {compartment_id} --query-definition '{query_definition}'",
        "list": "oci usage-api query list --compartment-id {compartment_id}",
        "get": "oci usage-api query get --query-id {query_id}",
        "delete": "oci usage-api query delete --query-id {query_id} --force",
        "update": "oci usage-api query update --query-id {query_id} --query-definition '{query_definition}'",
        "manage": "oci usage-api report request --tenant-id {tenancy_id} --time-usage-started {start_time} --time-usage-ended {end_time}",
    },
    "platform/backup-governance": {
        "create": "oci bv volume-backup-policy create --compartment-id {compartment_id} --display-name {name} --schedules '{schedules}'",
        "list": "oci bv volume-backup-policy list --compartment-id {compartment_id}",
        "get": "oci bv volume-backup-policy get --policy-id {policy_id}",
        "delete": "oci bv volume-backup-policy delete --policy-id {policy_id} --force",
        "update": "oci bv volume-backup-policy update --policy-id {policy_id} --display-name {name}",
        "manage": "oci bv volume-backup-policy-assignment create --asset-id {volume_id} --policy-id {policy_id}",
    }
}

SYSTEM_PROMPTS = {
    "compute/instances": "Você é um Cloud Architect especializado no Oracle Cloud Infrastructure (OCI). Sua responsabilidade é fornecer respostas precisas, profundas e extremamente técnicas sobre as Instâncias do Compute.",
    "database/autonomous": "Você é um Database Administrator (DBA) sênior focado em OCI Autonomous Database. Forneça respostas exaustivas abordando as nuances e as melhores práticas em Oracle Cloud.",
    "migration/aws-compute": "Você é um arquiteto de migrações focado em transições do provedor de nuvem legado para o OCI. Suas respostas devem enfatizar a equivalência no OCI de maneira clara e assertiva, sem mencionar o nome de concorrentes diretamente.",
    "terraform/compute": "Você é um DevOps Engineer especialista em Infraestrutura como Código (IaC). Forneça respostas profundas sobre Terraform no ambiente Oracle Cloud (OCI)."
}

def generate_question(category, idx, company, project, region, compartment, persona, intent, constraint, lifecycle):
    subcat = category.split("/")[-1]
    intent_pt = INTENTS_PT.get(intent, intent)
    templates = [
        f"Atuando como {persona} na empresa {company}, minha missão é executar a tarefa de {intent_pt} para {subcat} no escopo do projeto {project} (região {region}, compartimento {compartment}). Como proceder?",
        f"Para o ambiente {lifecycle} do nosso projeto {project}, precisamos realizar: {intent_pt} de {subcat}. Quais as melhores estratégias e comandos no OCI considerando a restrição: {constraint}?",
        f"Gostaria de saber a recomendação oficial do OCI para a tarefa de {intent_pt} em {subcat}. Nossa empresa ({company}) possui o cenário {lifecycle} e precisamos garantir que respeitaremos o pré-requisito de {constraint}.",
        f"Dada a infraestrutura da {company} (compartimento {compartment}), detalhe o passo a passo seguro para {intent_pt} de {subcat} no projeto {project}.",
    ]
    return templates[idx % len(templates)]

def generate_cli_code(category, intent, params):
    subcat = category.split("/")[-1]
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
    
    # Migration Fallbacks (avoiding cross cloud references)
    if category.startswith("migration/"):
        return f"```bash\noci compute instance launch --availability-domain {params.get('ad', 'AD-1')} --shape {params.get('shape', 'VM.Standard.E4.Flex')} --subnet-id {params.get('subnet_id', 'ocid1.subnet.oc1..xxxx')} --compartment-id {params.get('compartment_id', 'ocid1.compartment.oc1..xxxx')} --display-name oci-migrated-resource\n```"

    # Default fallback
    return f"```bash\noci {category.replace('/', ' ')} {intent} --compartment-id {params.get('compartment_id', 'ocid1.compartment.oc1..xxxx')}\n```"

def generate_response(category, intent, idx, company, project, region, compartment, constraint, lifecycle):
    subcat = category.split("/")[-1]
    intent_pt = INTENTS_PT.get(intent, intent)
    
    params = {
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
        "namespace": "oci_compute",
        "topic_id": "ocid1.onstopic.oc1.sa-saopaulo-1.xxx",
        "mount_target_id": "ocid1.mounttarget.oc1.sa-saopaulo-1.xxx",
        "security_list_id": "ocid1.securitylist.oc1.sa-saopaulo-1.xxx",
        "function_id": "ocid1.function.oc1.sa-saopaulo-1.xxx",
        "schedules": '[{"backupType":"FULL","period":"DAILY","timeZone":"UTC"}]'
    }

    cli_command = generate_cli_code(category, intent, params)

    content = f"""Para a solicitação de {intent_pt} em relação a {subcat} na Oracle Cloud Infrastructure (OCI), considerando o cenário da empresa {company}, a abordagem recomendada é dividida em etapas claras. 

Neste contexto, é de suma importância observar as best practices (melhores práticas) e garantir que o ciclo de vida do ambiente ({lifecycle}) esteja alinhado à estratégia corporativa. Dessa forma, apresentamos as diretrizes técnicas exigidas, garantindo a alta disponibilidade e integridade do seu serviço.

### 1. Visão Geral e Pré-requisitos

Antes de iniciar qualquer operação através da OCI CLI ou Terraform, é imprescindível verificar os seguintes pré-requisitos fundamentais:
- Confirme que as permissões de IAM adequadas estão configuradas. Por exemplo, garanta que a política "Allow group {project}-admins to manage {subcat}-family in compartment {compartment}" foi corretamente aplicada.
- Certifique-se de que os limites (Service Limits) do tenant suportam esta operação, especialmente para novos recursos ou em situações de alta demanda na região `{region}`.
- Planeje os eventuais impactos no tráfego de rede e acesso, garantindo que o requisito imposto de `{constraint}` seja plenamente atendido.

### 2. Boas Práticas, Vantagens e Trade-offs

Ao administrar e evoluir a infraestrutura de {subcat}, deve-se pesar a vantagem da agilidade oferecida pela nuvem contra os desafios e o risco potencial de segurança ou custo excessivo.

- **Melhor Prática (Recomendação)**: Mantenha sempre um esquema de tags (Tagging) consistente nos recursos gerados, utilizando namespaces padronizados como `cost-center={project}`. Em resumo, isso facilita absurdamente a auditoria, rastreabilidade e visibilidade de custos a longo prazo.
- **Trade-off de Arquitetura**: Provisionar instâncias ou serviços excessivamente robustos e performáticos (por exemplo, shapes superiores) traz a vantagem clara de suportar cargas de pico sem gargalos. No entanto, a desvantagem inerente é o custo ocioso se a demanda real for inferior à projetada. 
- **Risco Identificado**: Uma configuração descuidada de portas ou permissões abertas no compartimento `{compartment}` pode expor partes da sua arquitetura à internet ou a intrusos. A mitigação fundamental recomendada é implementar regras estritas de NSG (Network Security Groups) e ativar a monitoria contínua usando os pilares fundamentais do OCI Cloud Guard desde o primeiro dia.

### 3. Procedimento Técnico e Implementação

Abaixo, fornecemos os detalhes exatos da execução do {intent_pt} via linha de comando ou script de automação de infraestrutura. Execute os comandos com cautela, assegurando-se de que o ambiente alvo está correto.

{cli_command}

Consequentemente, executando as instruções delineadas acima, o recurso de {subcat} será orquestrado conforme o padrão recomendado e validado pela Oracle. A OCI exige atenção redobrada à precisão dos identificadores (OCIDs) fornecidos.

### 4. Validação e Teste de Funcionalidade

Após o envio da requisição para a cloud, a etapa de validação é o próximo passo estritamente obrigatório. Veja que a execução de um comando muitas vezes é assíncrona, exigindo assim a confirmação objetiva de seu estado:

- Realize consultas periódicas de estado (polling) ou utilize flags nativas como `--wait-for-state` (quando disponível) para assegurar que a transição ocorreu com total êxito.
- Inspecione os logs de auditoria nativos e verifique se as métricas de performance estão condizentes com a baseline aceitável do projeto {project}.
- Valide também se os pontos de rede foram atribuídos adequadamente, permitindo conectividade com a aplicação consumidora.

### 5. Resumo da Configuração Aplicada

Para efeito de clareza, segue a tabela sumária do escopo onde a operação foi planejada:

| Parâmetro Crítico | Valor Configurado na Operação |
|-------------------|-------------------------------|
| **Região (Region)** | `{region}` |
| **Compartimento** | `{compartment}` |
| **Fase / Ciclo de Vida** | `{lifecycle}` |
| **Tipo de Ação** | `{intent_pt}` |

Portanto, seguindo religiosamente essa estrutura metodológica, o risco de indisponibilidade é drasticamente minimizado e as metas técnicas estabelecidas para a infraestrutura da {company} serão entregues com segurança e alta performance no Oracle Cloud Infrastructure.

**Referência Oficial (Doc):** https://docs.oracle.com/pt-br/iaas/Content/{category.split("/")[0].title()}/Home.htm"""
    return content

def generate_example(category, idx):
    company = random.choice(COMPANIES)
    project = random.choice(PROJECTS)
    region = random.choice(REGIONS)
    compartment = random.choice(COMPARTMENTS)
    persona = random.choice(PERSONAS)
    constraint = random.choice(CONSTRAINTS)
    lifecycle = random.choice(LIFECYCLE_STAGES)

    intents = ["create", "list", "get", "update", "delete", "manage"]
    intent = intents[idx % len(intents)]

    if "migration" in category:
        intent = "describe"
    elif "troubleshooting" in category:
        intent = "diagnose"
    elif "finops" in category:
        intent = "analyze"

    question = generate_question(category, idx, company, project, region, compartment, persona, intent, constraint, lifecycle)
    answer = generate_response(category, intent, idx, company, project, region, compartment, constraint, lifecycle)

    sys_prompt = SYSTEM_PROMPTS.get(category, f"Você é um arquiteto e especialista experiente em OCI focado no domínio de {category}. Forneça orientações técnicas, profundas e definitivas.")

    return {
        "messages": [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": question},
            {"role": "assistant", "content": answer}
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
            "source": "generate_v5_combined"
        }
    }

def main():
    output_dir = Path("data/curated")
    output_dir.mkdir(parents=True, exist_ok=True)

    total = 0
    for category in CATEGORIES:
        examples = []
        for i in range(EXAMPLES_PER_CATEGORY):
            ex = generate_example(category, i)
            examples.append(ex)

        safe_name = category.replace("/", "-")
        output_file = output_dir / f"{safe_name}.jsonl"

        with open(output_file, "w", encoding="utf-8") as f:
            for ex in examples:
                f.write(json.dumps(ex, ensure_ascii=False) + "\n")

        print(f"✅ {category}: {len(examples)}")
        total += len(examples)

    print(f"\n🎯 Total: {total} examples em {len(CATEGORIES)} categorias")
    print(f"📁 Output: {output_dir}")

if __name__ == "__main__":
    main()
