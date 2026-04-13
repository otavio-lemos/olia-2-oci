#!/usr/bin/env python3
"""Generate OCI training examples - VERSION 3 (Evolved)

Key improvements over v2:
1. Hash-based value selection (no repetition from idx % len)
2. Real OCI CLI commands with full parameters
3. Real Terraform resources (oci_core_*, oci_database_*, etc)
4. Long responses (500+ words, 5+ sections)
5. 2x examples for problematic categories (terraform, troubleshooting)
6. Actual diagnostic scenarios with real metrics

Usage:
    python scripts/generate_v3.py
"""

import json
import hashlib
import random
from pathlib import Path
from collections import Counter

random.seed(42)

# =============================================================================
# CATEGORIES - Extended coverage with priority weights
# =============================================================================

CATEGORIES = {
    # Core OCI (baseline - 200 examples each)
    "compute/instances": {"weight": 1, "examples": 200},
    "compute/scaling": {"weight": 1, "examples": 200},
    "compute/custom-images": {"weight": 1, "examples": 200},
    "storage/block": {"weight": 1, "examples": 200},
    "storage/object": {"weight": 1, "examples": 200},
    "storage/file": {"weight": 1, "examples": 200},
    "networking/vcn": {"weight": 1, "examples": 200},
    "networking/security": {"weight": 1, "examples": 200},
    "networking/connectivity": {"weight": 1, "examples": 200},
    "lb/load-balancer": {"weight": 1, "examples": 200},
    # Database
    "database/autonomous": {"weight": 1, "examples": 200},
    "database/mysql": {"weight": 1, "examples": 200},
    "database/postgresql": {"weight": 1, "examples": 200},
    "database/nosql": {"weight": 1, "examples": 200},
    "database/autonomous-json": {"weight": 1, "examples": 200},
    "database/exadata": {"weight": 1, "examples": 200},
    # Container
    "container/oke": {"weight": 1, "examples": 200},
    "container/instances": {"weight": 1, "examples": 200},
    # Serverless
    "serverless/functions": {"weight": 1, "examples": 200},
    "serverless/api-gateway": {"weight": 1, "examples": 200},
    # Security
    "security/iam-basics": {"weight": 1, "examples": 200},
    "security/policies": {"weight": 1, "examples": 250},  # 250 - complex topic
    "security/dynamic-groups": {"weight": 1, "examples": 200},
    "security/federation": {"weight": 1, "examples": 200},
    "security/vault-secrets": {"weight": 1, "examples": 200},
    "security/vault-keys": {"weight": 1, "examples": 200},
    "security/encryption": {"weight": 1, "examples": 200},
    "security/cloud-guard": {"weight": 1, "examples": 200},
    "security/waf": {"weight": 1, "examples": 200},
    "security/zero-trust": {"weight": 1, "examples": 250},  # 250 - complex
    "security/posture-management": {"weight": 1, "examples": 200},
    # DevOps
    "devops/ci-cd": {"weight": 1, "examples": 200},
    "devops/resource-manager": {"weight": 1, "examples": 200},
    "devops/artifacts": {"weight": 1, "examples": 200},
    "devops/secrets": {"weight": 1, "examples": 200},
    # Observability
    "observability/logging": {"weight": 1, "examples": 200},
    "observability/monitoring": {"weight": 1, "examples": 200},
    "observability/apm": {"weight": 1, "examples": 200},
    "observability/stack-monitoring": {"weight": 1, "examples": 200},
    # Migration
    "migration/aws-compute": {"weight": 1, "examples": 200},
    "migration/aws-storage": {"weight": 1, "examples": 200},
    "migration/aws-database": {"weight": 1, "examples": 200},
    "migration/azure-compute": {"weight": 1, "examples": 200},
    "migration/azure-storage": {"weight": 1, "examples": 200},
    "migration/azure-database": {"weight": 1, "examples": 200},
    "migration/gcp-compute": {"weight": 1, "examples": 200},
    "migration/gcp-storage": {"weight": 1, "examples": 200},
    "migration/gcp-database": {"weight": 1, "examples": 200},
    "migration/onprem-compute": {"weight": 1, "examples": 200},
    "migration/onprem-storage": {"weight": 1, "examples": 200},
    "migration/onprem-database": {"weight": 1, "examples": 200},
    "migration/onprem-vmware": {"weight": 1, "examples": 200},
    "migration/data-transfer": {"weight": 1, "examples": 200},
    # FinOps
    "finops/cost-optimization": {"weight": 1, "examples": 200},
    "finops/rightsizing": {"weight": 1, "examples": 200},
    "finops/showback-chargeback": {"weight": 1, "examples": 200},
    "finops/storage-tiering": {"weight": 1, "examples": 200},
    # Governance (higher weight - 250 examples)
    "governance/landing-zone": {"weight": 1.5, "examples": 250},
    "governance/compartments": {"weight": 1.5, "examples": 250},
    "governance/tagging": {"weight": 1.5, "examples": 250},
    "governance/budgets-cost": {"weight": 1.5, "examples": 250},
    "governance/policies-guardrails": {"weight": 1.5, "examples": 250},
    "governance/compliance": {"weight": 1.5, "examples": 250},
    "governance/audit-readiness": {"weight": 1.5, "examples": 250},
    "governance/resource-discovery": {"weight": 1.5, "examples": 250},
    # Terraform - 2x examples (REGREASED in benchmark!)
    "terraform/provider": {"weight": 2.0, "examples": 300},
    "terraform/compute": {"weight": 2.0, "examples": 300},
    "terraform/storage": {"weight": 2.0, "examples": 300},
    "terraform/networking": {"weight": 2.0, "examples": 300},
    "terraform/load-balancer": {"weight": 2.0, "examples": 300},
    "terraform/database": {"weight": 2.0, "examples": 300},
    "terraform/container": {"weight": 2.0, "examples": 300},
    "terraform/serverless": {"weight": 2.0, "examples": 300},
    "terraform/security": {"weight": 2.0, "examples": 300},
    "terraform/observability": {"weight": 2.0, "examples": 300},
    "terraform/devops": {"weight": 2.0, "examples": 300},
    "terraform/state": {"weight": 2.0, "examples": 300},
    # Troubleshooting - 2x examples (REGREASED in benchmark!)
    "troubleshooting/performance": {"weight": 2.0, "examples": 350},
    "troubleshooting/storage": {"weight": 2.0, "examples": 350},
    "troubleshooting/authentication": {"weight": 2.0, "examples": 350},
    "troubleshooting/connectivity": {"weight": 1.5, "examples": 250},
    "troubleshooting/compute": {"weight": 1.5, "examples": 250},
    "troubleshooting/database": {"weight": 1.5, "examples": 250},
    "troubleshooting/oke": {"weight": 1.5, "examples": 250},
    "troubleshooting/functions": {"weight": 1.5, "examples": 250},
    # Platform
    "platform/backup-governance": {"weight": 1, "examples": 200},
    "platform/sre-operations": {"weight": 1, "examples": 200},
}

# =============================================================================
# SYSTEM PROMPTS - Detailed and specific
# =============================================================================

SYSTEM_PROMPTS = {
    "compute/instances": """You are an OCI Compute specialist. Provide technical guidance on:
- Instance lifecycle (launch, stop, start, terminate)
- Shape selection (VM.Standard, BM.Standard, GPU)
- SSH access, bastion hosts, cloud-init
- Instance metadata, tags, fault domains
- Boot volume management, custom images
Use real OCI CLI commands: oci compute instance launch, oci compute instance get, etc.""",
    "compute/scaling": """You are an OCI Compute scaling specialist. Provide technical guidance on:
- Instance pools, auto-scaling configurations
- Capacity planning, placement configurations
- Load balancing integration
- Regional vs zonal considerations
Use: oci autoscaling auto-scaling-configuration create, etc.""",
    "storage/block": """You are an OCI Block Storage specialist. Provide technical guidance on:
- Block volume creation, attachment, performance tiers
- Volume backups, clones, performance metrics
- NVMe vs regular performance
- Volume groups, backup policies
Use: oci bv volume create, oci bv volume-attachment create, etc.""",
    "storage/object": """You are an OCI Object Storage specialist. Provide technical guidance on:
- Bucket lifecycle policies, versioning
- Pre-authenticated requests (PARs)
- Multipart upload, storage tiers (Standard, Infrequent, Archive)
- Cross-region replication, access logging
Use: oci os bucket create, oci os object put, oci os preauth-request create, etc.""",
    "storage/file": """You are an OCI File Storage specialist. Provide technical guidance on:
- File system creation, mount targets
- NFSv3 and NFSv4.1 protocols
- Export options, security lists
- Snapshots, replication
Use: oci fs file-system create, oci fs mount-target create, etc.""",
    "networking/vcn": """You are an OCI Networking specialist. Provide technical guidance on:
- VCN design, CIDR blocks, RFC 1918
- Subnets (public/private), security lists
- Internet Gateway, NAT Gateway, Service Gateway
- VCN topology, hub-spoke, peering
Use: oci network vcn create, oci network subnet create, oci network route-table create, etc.""",
    "networking/security": """You are an OCI Network Security specialist. Provide technical guidance on:
- Security Lists vs Network Security Groups (NSGs)
- Ingress/egress rules, stateful vs stateless
- Security list evaluation order
- Private endpoints, security partner integrations
Use: oci network security-list create, oci network nsg create, etc.""",
    "networking/connectivity": """You are an OCI Connectivity specialist. Provide technical guidance on:
- DRG (Dynamic Routing Gateway), VCN attachments
- VPN IPSec, FastConnect, site-to-site VPN
- Remote peering, VCN-to-VCN connectivity
- Transit routing patterns
Use: oci network drg create, oci network drg-attachment create, etc.""",
    "lb/load-balancer": """You are an OCI Load Balancing specialist. Provide technical guidance on:
- Load balancer shapes (flexible, 10Gbps, 100Gbps)
- Backend sets, health checks, SSL/TLS
- Path-based routing, rule actions
- WAF integration, logging
Use: oci lb load-balancer create, oci lb backend-set create, etc.""",
    "database/autonomous": """You are an OCI Autonomous Database specialist. Provide technical guidance on:
- ATP, ADW, APEX configuration
- Wallet management, connection strings
- Auto scaling, CPU/IO auto scaling
- Dedicated vs shared infrastructure
Use: oci db autonomous-database create, oci db autonomous-database start/stop, etc.""",
    "database/mysql": """You are an OCI MySQL HeatWave specialist. Provide technical guidance on:
- DB System creation, shape selection
- HeatWave analytics, MySQL Shell
- Replicas, backup/restore
- Configuration parameters
Use: oci mysql db-system create, oci mysql db-system start, etc.""",
    "database/postgresql": """You are an OCI PostgreSQL specialist. Provide technical guidance on:
- DB System creation, versions
- High availability, read replicas
- Backup and restore
- Extensions, configuration
Use: oci database db-system create, oci database db-system update, etc.""",
    "terraform/provider": """You are an OCI Terraform specialist. CRITICAL: Always use the official terraform-provider-oci resources.
Resource naming: oci_core_*, oci_database_*, oci_objectstorage_*, etc.
NEVER use oci_* without the service prefix (e.g., oci_instance is WRONG, oci_core_instance is CORRECT).
Provider config: provider oci with tenancy_ocid, user_id, fingerprint, private_key_path.
Use: terraform init, terraform plan, terraform apply, terraform import.""",
    "terraform/compute": """You are an OCI Terraform Compute specialist. CRITICAL: Use ONLY official resources:
- oci_core_instance (NOT oci_instance)
- oci_core_instance_pool
- oci_core_boot_volume_attachment
- oci_autoscaling_instance_configuration
- oci_core_compute_image_capability_schema
NEVER make up resource names. Use terraform.io/docs/providers/oci/r/.""",
    "terraform/networking": """You are an OCI Terraform Networking specialist. CRITICAL resources:
- oci_core_vcn, oci_core_subnet, oci_core_route_table
- oci_core_security_list, oci_core_network_security_group
- oci_core_internet_gateway, oci_core_nat_gateway
- oci_core_drg, oci_core_local_peering_gateway
Always include proper provider block: provider oci { region = var.region }.""",
    "terraform/storage": """You are an OCI Terraform Storage specialist. CRITICAL resources:
- oci_core_volume (NOT oci_block_volume)
- oci_core_volume_group, oci_core_volume_attachment
- oci_objectstorage_bucket, oci_objectstorage_object
- oci_file_storage_file_system, oci_file_storage_mount_target
Check terraform.io/providers/oracle/oci/latest/docs for exact names.""",
    "terraform/database": """You are an OCI Terraform Database specialist. CRITICAL resources:
- oci_database_autonomous_database
- oci_database_db_system (for MySQL, PostgreSQL)
- oci_database_backup, oci_database_exadata_infrastructure
- oci_database_autonomous_exadata_infrastructure
NEVER use generic oci_database_* - use specific resource types.""",
    "terraform/serverless": """You are an OCI Terraform Serverless specialist. CRITICAL resources:
- oci_functions_function (NOT oci_fn_function)
- oci_functions_application
- oci_apigateway_gateway, oci_apigateway_deployment
- oci_apigateway_route
Use correct function configuration with invoke_endpoint, memory_in_mbs.""",
    "terraform/security": """You are an OCI Terraform Security specialist. CRITICAL resources:
- oci_identity_compartment, oci_identity_policy
- oci_identity_dynamic_group, oci_identity_user_group_membership
- oci_kms_vault, oci_kms_key, oci_kms_secret
- oci_logging_log_group, oci_events_rule
Policy syntax: "Allow group X to Y in compartment Z" - NOT SQL!""",
    "terraform/state": """You are an OCI Terraform State specialist. Provide guidance on:
- Remote state with oci_objectstorage_bucket
- State locking with OCI native support
- State import from existing resources
- State file best practices, workspaces
Use: terraform {
  backend "http" or "s3" compatible with OCI
}""",
    "terraform/container": """You are an OCI Terraform Container specialist. CRITICAL resources:
- oci_containerengine_cluster (NOT oci_oke_cluster)
- oci_containerengine_node_pool
- oci_containerengine_addon
- oci_container_instances_container_instance
Always configure kubeconfig output properly.""",
    "terraform/observability": """You are an OCI Terraform Observability specialist. CRITICAL resources:
- oci_logging_log_group, oci_logging_log
- oci_monitoring_alarm, oci_monitoring_metric_alarm
- oci_monitoring_dashboard, oci_monitoring_alert_rule
- oci_stackmonitoring_monitored_resource
Use correct metric namespaces: oci_computeagent, oci_blockstore, etc.""",
    "terraform/devops": """You are an OCI Terraform DevOps specialist. CRITICAL resources:
- oci_devops_project, oci_devops_pipeline
- oci_devops_deploy_pipeline, oci_devops_build_pipeline
- oci_devops_deploy_stage, oci_devops_build_run
- oci_devops_repository, oci_devops_trigger
Artifact registry: oci_devops_repository for OCIR, oci_objectstorage_bucket for general.""",
    "terraform/load-balancer": """You are an OCI Terraform Load Balancer specialist. CRITICAL resources:
- oci_load_balancer_load_balancer
- oci_load_balancer_backend_set
- oci_load_balancer_backend, oci_load_balancer_listener
- oci_load_balancer_hostname, oci_load_balancer_path_route_set
Include health_check_configuration, SSL certificates properly.""",
    "troubleshooting/performance": """You are an OCI Performance troubleshooting specialist. Provide detailed diagnostic guidance:
- CPU throttling, memory pressure, NVMe performance
- Monitoring metrics: oci_computeagent namespace
- Operations Insights, Performance Hub
- AWR/ASH reports for databases
Include REAL commands: oci monitoring metric-data query, oci monitoring alarm-history, etc.""",
    "troubleshooting/storage": """You are an OCI Storage troubleshooting specialist. Provide detailed diagnostic guidance:
- Block volume IOPS/throughput issues
- Object storage latency, bucket access problems
- File system mount issues, NFS errors
- Volume attachment state, quota exceeded
Real commands: oci bv volume get, oci os bucket get, oci fs mount-target get, etc.""",
    "troubleshooting/authentication": """You are an OCI IAM troubleshooting specialist. Provide detailed diagnostic guidance:
- Policy evaluation, permission denied errors
- Dynamic group matching, federation issues
- Instance principal, resource principal
- Audit logs for access denied events
Real commands: oci iam policy list, oci iam policy work-request, oci audit event list, etc.""",
    "troubleshooting/connectivity": """You are an OCI Connectivity troubleshooting specialist. Provide detailed diagnostic guidance:
- VCN routing issues, DNS resolution
- Security list blocking, NSG rules
- VPN tunnels, FastConnect BGP
- Load balancer health checks failing
Real commands: oci network vcn get, oci network route-table get, oci network connectivity-check, etc.""",
    "troubleshooting/compute": """You are an OCI Compute troubleshooting specialist. Provide detailed diagnostic guidance:
- Instance provisioning failures
- Boot volume issues, image compatibility
- SSH connectivity, Bastion access
- Auto-scaling not triggering
Real commands: oci compute instance get, oci compute instance-action, oci compute boot-volume-attachment list, etc.""",
    "troubleshooting/database": """You are an OCI Database troubleshooting specialist. Provide detailed diagnostic guidance:
- Connection failures, TNS errors
- ORA errors, quota exceeded
- Autonomous DB performance, wallet issues
- Backup/restore failures
Real commands: oci db autonomous-database get, oci db database get, etc.""",
    "troubleshooting/oke": """You are an OCI OKE troubleshooting specialist. Provide detailed diagnostic guidance:
- Node pool issues, worker node failures
- Cluster provisioning, CNI issues
- RBAC, kubectl access
- Add-on failures
Real commands: oci ce cluster get, oci ce node-pool get, kubectl get nodes, kubectl describe pods, etc.""",
    "troubleshooting/functions": """You are an OCI Functions troubleshooting specialist. Provide detailed diagnostic guidance:
- Function invocation failures, timeout issues
- Memory/CPU limits, concurrent executions
- API Gateway integration, trigger issues
- Logging and monitoring function invocations
Real commands: oci fn function invoke, oci fn function get, oci logging log list, etc.""",
}

# =============================================================================
# REAL OCI CLI COMMANDS - Complete with parameters
# =============================================================================

OCI_CLI_COMMANDS = {
    "compute/instances": [
        'oci compute instance launch --availability-domain "{ad}" --compartment-id $COMPARTMENT_ID --shape VM.Standard.E4.Flex --source-details \'{{"sourceType":"image","imageId":"{image_id}"}}\' --subnet-id $SUBNET_ID --display-name "prod-{idx}-instance" --shape-config \'{{"ocpus":{ocpus},"memoryInGBs":{memory}}}\'',
        "oci compute instance get --instance-id $INSTANCE_ID",
        "oci compute instance list --compartment-id $COMPARTMENT_ID --lifecycle-state RUNNING --sort-by DISPLAYNAME --limit 50",
        "oci compute instance-action --instance-id $INSTANCE_ID --action STOP",
        "oci compute ssh-authorized-key --instance-id $INSTANCE_ID --key file://~/.ssh/id_rsa.pub",
    ],
    "compute/scaling": [
        'oci autoscaling auto-scaling-configuration create --compartment-id $COMPARTMENT_ID --display-name "prod-autoscaling" --resource {resource_id} --policy \'{{"type":"threshold","capacity":{{"min":{min},"max":{max}}},"rule":{{"metricType":"CPU_UTILIZATION","threshold":{{"step":10,"upper":80}}}}}}}\'',
        "oci autoscaling auto-scaling-configuration get --auto-scaling-configuration-id $CONFIG_ID",
        'oci autoscaling auto-scaling-configuration update --auto-scaling-configuration-id $CONFIG_ID --policy \'{{"type":"threshold","capacity":{{"min":2,"max":10}}}}\'',
    ],
    "storage/block": [
        'oci bv volume create --availability-domain "{ad}" --compartment-id $COMPARTMENT_ID --size-in-gbs 100 --display-name "prod-data-{idx}" --vpus-per-gb 10 --backup-policy oracle-managed',
        "oci bv volume get --volume-id $VOLUME_ID",
        "oci bv volume-attachment create --instance-id $INSTANCE_ID --volume-id $VOLUME_ID --attachment-type iscsi --device /dev/oracleoci/oraclevdd",
        "oci bv volume-update --volume-id $VOLUME_ID --size-in-gbs 500 --vpus-per-gb 20",
    ],
    "storage/object": [
        'oci os bucket create --compartment-id $COMPARTMENT_ID --name "prod-data-{idx}" --storage-tier Standard --public-access-type NoPublicAccess',
        'oci os object put --bucket-name $BUCKET_NAME --file ./data.csv --name "data-{idx}.csv"',
        "oci os bucket get --bucket-name $BUCKET_NAME",
        'oci os preauth-request create --bucket-name $BUCKET_NAME --name "download-{idx}" --object-name "*.csv" --access-type ObjectRead --expiration-date "2025-12-31T23:59:59Z"',
        'oci os lifecycle-policy create --bucket-name $BUCKET_NAME --rules \'[{{"action":"ARCHIVE","objectNameFilter":{{"pattern":"logs/*"}},"target":"ARCHIVE_STORAGE"}}]\'',
    ],
    "storage/file": [
        'oci fs file-system create --availability-domain "{ad}" --compartment-id $COMPARTMENT_ID --display-name "prod-fs-{idx}" --freeform-tags "{{"Environment":"Production"}}"',
        'oci fs mount-target create --file-system-id $FS_ID --subnet-id $SUBNET_ID --display-name "prod-mt-{idx}"',
        'oci fs export create --file-system-id $FS_ID --mount-target-id $MT_ID --path /prodexports --export-options \'[{{"source":"0.0.0.0/0","access":"READ_WRITE","identitySquash":"NONE"}}]\'',
    ],
    "networking/vcn": [
        'oci network vcn create --compartment-id $COMPARTMENT_ID --cidr-blocks \'["10.{subnet}.0.0/16"]\' --display-name "prod-vcn-{idx}" --dns-label "prodvcn{idx}"',
        'oci network subnet create --vcn-id $VCN_ID --cidr-block 10.{subnet}.0.0/24 --availability-domain "{ad}" --display-name "prod-subnet-{idx}"',
        'oci network route-table create --vcn-id $VCN_ID --display-name "prod-rt-{idx}" --route-rules \'[{{"destination":"0.0.0.0/0","networkEntityId":"{igw_id}"}}]\'',
        'oci network internet-gateway create --vcn-id $VCN_ID --display-name "prod-igw-{idx}" --is-enabled true',
    ],
    "networking/security": [
        'oci network security-list create --vcn-id $VCN_ID --display-name "prod-ssl-{idx}" --egress-security-rules \'[{{"destination":"0.0.0.0/0","protocol":"all"}}]\' --ingress-security-rules \'[{{"source":"0.0.0.0/0","protocol":"tcp","tcpOptions":{{"destinationPortRange":{{"min":443,"max":443}}}}}}]\'',
        'oci network nsg create --vcn-id $VCN_ID --display-name "prod-nsg-{idx}"',
        "oci network nsg-rules add --nsg-id $NSG_ID --direction INGRESS --source 0.0.0.0/0 --protocol TCP --port 22",
    ],
    "networking/connectivity": [
        'oci network drg create --compartment-id $COMPARTMENT_ID --display-name "prod-drg-{idx}"',
        'oci network drg-attachment create --vcn-id $VCN_ID --drg-id $DRG_ID --display-name "prod-drg-att-{idx}"',
        'oci network drg-route-table create --drg-id $DRG_ID --display-name "prod-drg-rt-{idx}"',
    ],
    "lb/load-balancer": [
        'oci lb load-balancer create --compartment-id $COMPARTMENT_ID --display-name "prod-lb-{idx}" --shape-name 10Mbps --subnet-ids \'["{subnet_id}"]\'',
        'oci lb backend-set create --load-balancer-id $LB_ID --name "prod-bes-{idx}" --policy LEAST_CONNECTIONS --health-checker \'{{"protocol":"HTTP","port":80,"urlPath":"/health"}}\'',
        'oci lb backend create --backend-set-name "prod-bes-{idx}" --load-balancer-id $LB_ID --ip-address $BACKEND_IP --port 8080 --weight 10',
        'oci lb listener create --load-balancer-id $LB_ID --default-backend-set-name "prod-bes-{idx}" --port 443 --protocol HTTPS --ssl-certificate-name $CERT_NAME',
    ],
    "database/autonomous": [
        'oci db autonomous-database create --compartment-id $COMPARTMENT_ID --display-name "prod-adb-{idx}" --db-name "PRODDB" --cpu-core-count 2 --data-storage-size-in-tbs 1 --admin-password $ADMIN_PWD',
        "oci db autonomous-database get --autonomous-database-id $ADB_ID",
        "oci db autonomous-database start --autonomous-database-id $ADB_ID",
        "oci db autonomous-database update --autonomous-database-id $ADB_ID --cpu-core-count 4 --data-storage-size-in-tbs 2",
    ],
    "database/mysql": [
        'oci mysql db-system create --compartment-id $COMPARTMENT_ID --display-name "prod-mysql-{idx}" --mysql-version 8.0 --shape-name VM.Standard.E4.Flex --subnet-id $SUBNET_ID --admin-password $ADMIN_PWD --data-storage-size-in-gbs 256',
        "oci mysql db-system get --db-system-id $MYSQL_ID",
        "oci mysql db-system start --db-system-id $MYSQL_ID",
    ],
    "database/postgresql": [
        'oci database db-system create --compartment-id $COMPARTMENT_ID --display-name "prod-pg-{idx}" --postgres-version 15 --subnet-id $SUBNET_ID --hostname "prodpghost{idx}" --cpu-core-count 2 --db-home "prod-db-home-{idx}" --database "proddb" --admin-password $ADMIN_PWD',
        "oci database db-system get --db-system-id $PG_ID",
    ],
    # Terraform resource definitions
    "terraform/provider": [
        'provider "oci" {{tenancy_ocid = var.tenancy_ocid, user_ocid = var.user_ocid, fingerprint = var.fingerprint, private_key_path = var.private_key_path, region = var.region}}',
        'data "oci_identity_tenancy" "prod" {{tenancy_id = var.tenancy_ocid}}',
        'terraform {{required_providers {{oci = {{source = "oracle/oci", version = "~> 5.0"}}}}}}',
    ],
    "terraform/compute": [
        'resource "oci_core_instance" "prod_app" {{compartment_id = var.compartment_id, availability_domain = data.oci_identity_availability_domains.ads.availability_domains[0].name, shape = "VM.Standard.E4.Flex", source_details = {{source_id = var.image_id, source_type = "image"}}, subnet_id = oci_core_subnet.prod_subnet.id, metadata = {{"ssh_authorized_keys" = file(var.ssh_public_key)}}}}',
        'resource "oci_core_instance_pool" "prod_pool" {{compartment_id = var.compartment_id,placement_configs = [{{availability_domain = data.oci_identity_availability_domains.ads.availability_domains[0].name, primary_subnet_id = oci_core_subnet.prod_subnet.id}}],shape_config = {{memory_in_gbs = 16, ocpus = 2}},size = 3}}',
        'resource "oci_autoscaling_auto_scaling_configuration" "prod" {{compartment_id = var.compartment_id,resource = {{type = "instancePool",id = oci_core_instance_pool.prod_pool.id}},policies = [{{type = "threshold",capacity = {{max = 5,min = 1}},rules = [{{action = {{type = "CHANGE_COUNT_BY",value = 1}},metric = {{type = "CPU_UTILIZATION",threshold = {{comparison_operator = "GT",value = 70}}}}}}]}}]}}',
    ],
    "terraform/storage": [
        'resource "oci_core_volume" "prod_data" {{availability_domain = data.oci_identity_availability_domains.ads.availability_domains[0].name,compartment_id = var.compartment_id,name = "prod-data",size_in_gbs = 500,vpus_per_gb = 10}}',
        'resource "oci_objectstorage_bucket" "prod" {{compartment_id = var.compartment_id,name = "prod-data-bucket",storage_tier = "Standard",namespace = var.namespace}}',
        'resource "oci_file_storage_file_system" "prod" {{availability_domain = data.oci_identity_availability_domains.ads.availability_domains[0].name,compartment_id = var.compartment_id,name = "prod-fs"}}',
    ],
    "terraform/networking": [
        'resource "oci_core_vcn" "prod" {{cidr_blocks = ["10.0.0.0/16"],compartment_id = var.compartment_id,display_name = "prod-vcn",dns_label = "prodvcn"}}',
        'resource "oci_core_subnet" "prod_private" {{cidr_block = "10.0.1.0/24",compartment_id = var.compartment_id,display_name = "prod-private",route_table_id = oci_core_route_table.prod_rt.id,security_list_ids = [oci_core_security_list.prod_private.id],vcn_id = oci_core_vcn.prod.id}}',
        'resource "oci_core_route_table" "prod_rt" {{compartment_id = var.compartment_id,vcn_id = oci_core_vcn.prod.id,route_rules = [{{destination = "0.0.0.0/0",network_entity_id = oci_core_internet_gateway.prod_igw.id}}]}}',
        'resource "oci_core_security_list" "prod_private" {{compartment_id = var.compartment_id,vcn_id = oci_core_vcn.prod.id,egress_security_rules = [{{destination = "0.0.0.0/0",protocol = "all"}}],ingress_security_rules = [{{source = "10.0.0.0/16",protocol = "6",tcp_options = {{destination_port_range = {{max = 443,min = 443}}}}}}]}}',
    ],
    "terraform/database": [
        'resource "oci_database_autonomous_database" "prod_adb" {{admin_password = var.admin_password,compartment_id = var.compartment_id,cpu_core_count = 2,data_storage_size_in_tbs = 1,db_name = "PRODDB",display_name = "prod-adb"}}',
        'resource "oci_database_db_system" "prod_mysql" {{availability_domain = data.oci_identity_availability_domains.ads.availability_domains[0].name,compartment_id = var.compartment_id,display_name = "prod-mysql",mysql_version = "8.0",shape_name = "VM.Standard.E4.Flex",subnet_id = oci_core_subnet.prod_subnet.id,admin_password = var.admin_password,data_storage_size_in_gbs = 256}}',
    ],
    "terraform/serverless": [
        'resource "oci_functions_application" "prod" {{compartment_id = var.compartment_id,display_name = "prod-app",subnet_ids = [oci_core_subnet.prod_private.id]}}',
        'resource "oci_functions_function" "prod" {{application_id = oci_functions_application.prod.id,display_name = "prod-func",invoke_endpoint = oci_functions_function.prod.invoke_endpoint,memory_in_mbs = 256,timeout_in_seconds = 300}}',
        'resource "oci_apigateway_gateway" "prod" {{compartment_id = var.compartment_id,display_name = "prod-api",subnet_ids = [oci_core_subnet.prod_private.id]}}',
    ],
    "terraform/security": [
        'resource "oci_identity_policy" "prod_admin" {{compartment_id = var.compartment_id,description = "Admin policy for production",name = "prod-admin-policy",statements = ["Allow group ProdAdmins to manage all-resources in compartment Prod"]}}',
        'resource "oci_identity_dynamic_group" "prod_instances" {compartment_id = var.compartment_id,description = "Production instance principals",matching_rule = "ANY {instance.compartment_id = var.compartment_id}",name = "prod-instances-dg"}',
        'resource "oci_kms_vault" "prod" {{compartment_id = var.compartment_id,display_name = "prod-vault",vault_type = "DEFAULT"}}',
        'resource "oci_kms_key" "prod" {{compartment_id = var.compartment_id,display_name = "prod-key",vault_id = oci_kms_vault.prod.id}}',
    ],
    "terraform/load-balancer": [
        'resource "oci_load_balancer_load_balancer" "prod" {{compartment_id = var.compartment_id,display_name = "prod-lb",shape_name = "10Mbps",subnet_ids = [oci_core_subnet.prod_lb_subnet.id]}}',
        'resource "oci_load_balancer_backend_set" "prod" {{load_balancer_id = oci_load_balancer_load_balancer.prod.id,name = "prod-backend",policy = "LEAST_CONNECTIONS",health_checker = {{interval_ms = 10000,port = 80,protocol = "HTTP",url_path = "/health"}}}}',
        'resource "oci_load_balancer_listener" "prod" {{default_backend_set_name = "prod-backend",load_balancer_id = oci_load_balancer_load_balancer.prod.id,name = "prod-listener",port = 443,protocol = "HTTP"}}',
    ],
    "terraform/container": [
        'resource "oci_containerengine_cluster" "prod" {{compartment_id = var.compartment_id,display_name = "prod-oke",kubernetes_version = "v1.28.0",vcn_id = oci_core_vcn.prod.id,pods_cidr = "10.244.0.0/16",services_cidr = "10.96.0.0/16"}}',
        'resource "oci_containerengine_node_pool" "prod" {{cluster_id = oci_containerengine_cluster.prod.id,compartment_id = var.compartment_id,display_name = "prod-nodepool",kubernetes_version = "v1.28.0",node_shape = "VM.Standard.E4.Flex",node_metadata = {{"ssh_authorized_keys" = file(var.ssh_public_key)}},quantity_per_subnet = 2,subnet_ids = [oci_core_subnet.prod_k8s.id]}}',
    ],
    "terraform/observability": [
        'resource "oci_logging_log_group" "prod" {{compartment_id = var.compartment_id,display_name = "prod-logs"}}',
        'resource "oci_monitoring_alarm" "prod_cpu" {{compartment_id = var.compartment_id,display_name = "High CPU",metric_namespace = "oci_computeagent",metric_compartment_id = var.compartment_id,query = "CpuUtilization[5m].mean() > 80",severity = "CRITICAL"}}',
        'resource "oci_monitoring_dashboard" "prod" {{compartment_id = var.compartment_id,display_name = "Prod Dashboard"}}',
    ],
    "terraform/state": [
        'terraform {{backend "http" {{address = "oci-objectstorage-bucket-url",lock_address = "oci-objectstorage-bucket-url/lock"}}}}',
        'resource "oci_objectstorage_bucket" "terraform_state" {{compartment_id = var.compartment_id,name = "terraform-state-bucket",namespace = var.namespace}}',
        'data "oci_objectstorage_object" "state_file" {{bucket = "terraform-state-bucket",namespace = var.namespace,object = "prod/terraform.tfstate"}}',
    ],
}

# =============================================================================
# TROUBLESHOOTING SCENARIOS - Real diagnostic steps
# =============================================================================

TROUBLESHOOTING_SCENARIOS = {
    "troubleshooting/performance": [
        {
            "symptom": "CPU utilization consistently at 100% during business hours",
            "causes": [
                "Noisy neighbor on shared host",
                "Application memory leak",
                "Burst credits exhausted",
                "Process fork bomb",
            ],
            "diagnostics": [
                "oci monitoring metric-data query --namespace oci_computeagent --resourceId $INSTANCE_ID --query 'CpuUtilization[5m].max()'",
                "oci compute instance get --instance-id $INSTANCE_ID --query 'data.shapeConfig'",
                "oci monitoring alarm list --compartment-id $COMPARTMENT_ID --query 'data[?contains(display-name,\"CPU\")]'",
            ],
            "solutions": [
                "Resize to larger shape with more OCPUs",
                "Enable burst capacity with VM.Optimized3.Flex",
                "Implement auto-scaling with proper cooldown",
                "Review application for memory leaks",
            ],
            "verification": "oci monitoring metric-data query --namespace oci_computeagent --resourceId $INSTANCE_ID --query 'CpuUtilization[5m].mean()' --start-time 'now-1h'",
        },
        {
            "symptom": "Block volume IOPS significantly below provisioned performance",
            "causes": [
                "Volume attached to wrong type instance",
                "Encryption at rest enabled with HSM",
                "Shared infrastructure saturation",
                "NVMe not enabled",
            ],
            "diagnostics": [
                "oci bv volume get --volume-id $VOLUME_ID --query 'data'",
                "oci monitoring metric-data query --namespace oci_blockstore --resourceId $VOLUME_ID",
                "oci bv volume-attachment list --compartment-id $COMPARTMENT_ID --volume-id $VOLUME_ID",
            ],
            "solutions": [
                "Enable Higher Performance tier (60 IOPS/GB)",
                "Attach to GPU or BM shape with local NVMe",
                "Use volume groups for parallel I/O",
                "Configure application-level I/O queues",
            ],
            "verification": "oci bv volume get --volume-id $VOLUME_ID --query 'data.{state:lifecycle-state,perf:vpus-per-gb}'",
        },
    ],
    "troubleshooting/storage": [
        {
            "symptom": "Object storage bucket returning 403 Forbidden despite policy",
            "causes": [
                "PAR expired",
                "Bucket policy blocking",
                "Tenancy-level policy required",
                "IAM not propagated",
            ],
            "diagnostics": [
                "oci os bucket get --bucket-name $BUCKET_NAME",
                "oci os policy get --bucket-name $BUCKET_NAME",
                "oci iam policy list --compartment-id $COMPARTMENT_ID --query 'data[?contains(statement,\"object\")]'",
            ],
            "solutions": [
                "Update bucket policy to allow public access",
                "Create PAR with longer expiration",
                "Wait 5-10 minutes for IAM propagation",
                "Use service gateway for private access",
            ],
            "verification": "oci os object list --bucket-name $BUCKET_NAME --limit 1",
        },
        {
            "symptom": "Block volume showing 0 IOPS despite provisioned performance",
            "causes": [
                "Instance not in same AD as volume",
                "iSCSI not configured properly",
                "Multipath not enabled",
                "Volume still attaching",
            ],
            "diagnostics": [
                "oci bv volume-attachment list --compartment-id $COMPARTMENT_ID --instance-id $INSTANCE_ID",
                "oci bv volume get --volume-id $VOLUME_ID --query 'data.{state:lifecycle-state,attachment:attachments}'",
                "iscsiadm -m session",
            ],
            "solutions": [
                "Ensure volume in same AD as instance",
                "Run iscsiadm discovery and attach commands",
                "Enable multipathd service",
                "Wait for attachment state to become ATTACHED",
            ],
            "verification": "iostat -xn 2 | grep sd | head -5",
        },
    ],
    "troubleshooting/authentication": [
        {
            "symptom": "Policy allows action but audit log shows DENIED",
            "causes": [
                "Wildcard in wrong location",
                "Group membership not propagated",
                "Policy in wrong compartment",
                "Resource in different tenancy",
            ],
            "diagnostics": [
                "oci iam policy get --policy-id $POLICY_ID",
                "oci iam group list-member-groups --group-id $GROUP_ID",
                "oci audit event list --compartment-id $COMPARTMENT_ID --start-time '2025-01-01T00:00:00Z' --query 'data[?contains(message,\"DENIED\")]'",
                "oci iam work-request list --compartment-id $COMPARTMENT_ID",
            ],
            "solutions": [
                "Move policy to root compartment if resource is there",
                "Use compartment-level group membership",
                "Wait up to 10 minutes for policy propagation",
                "Test with explicit compartment in policy",
            ],
            "verification": "oci iam policy inspect --policy-id $POLICY_ID --query 'data.statement'",
        },
        {
            "symptom": "Dynamic group not matching instances as expected",
            "causes": [
                "Tag not set on instance",
                "Wrong matching rule syntax",
                "Instance not in correct compartment",
                "Rule using deprecated attribute",
            ],
            "diagnostics": [
                "oci iam dynamic-group get --dynamic-group-id $DG_ID",
                "oci compute instance get --instance-id $INSTANCE_ID --query 'data.{freeformTags:freeformTags,definedTags:definedTags}'",
                "oci iam dynamic-group list --compartment-id $COMPARTMENT_ID",
            ],
            "solutions": [
                "Fix matching rule: ALL {instance.compartmentId = 'ocid'}",
                "Set required defined tag on instance",
                "Use freeform tags instead of defined tags for dynamic groups",
                "Verify instance is in correct compartment",
            ],
            "verification": "oci iam dynamic-group list --compartment-id $COMPARTMENT_ID --query 'data[?contains(matchingRule,\"instance\")]'",
        },
    ],
    "troubleshooting/connectivity": [
        {
            "symptom": "VCN subnet cannot reach internet despite IGW attached",
            "causes": [
                "Route table missing IGW entry",
                "Security list blocking egress",
                "Stateful NAT required",
                "DNS resolver issue",
            ],
            "diagnostics": [
                "oci network route-table get --rt-id $RT_ID --query 'data.routeRules'",
                "oci network subnet get --subnet-id $SUBNET_ID --query 'data.securityListIds'",
                "oci network vcn get --vcn-id $VCN_ID --query 'data.defaultRouteTableId'",
                "nslookup google.com",
            ],
            "solutions": [
                "Add route: destination=0.0.0.0/0, target=IGW",
                "Update security list egress to 0.0.0.0/0 TCP/80/443",
                "Enable NAT Gateway if IGW not accessible",
                "Configure private DNS resolver",
            ],
            "verification": "curl -v https://www.google.com from instance in subnet",
        },
        {
            "symptom": "Load balancer health checks failing despite backend running",
            "causes": [
                "Health check port mismatch",
                "Security list blocking LB IP",
                "Backend not listening on correct path",
                "SSL certificate expired",
            ],
            "diagnostics": [
                "oci lb backend-set get --load-balancer-id $LB_ID --backend-set-name $BS_NAME --query 'data.healthChecker'",
                "oci lb backend list --load-balancer-id $LB_ID --backend-set-name $BS_NAME",
                "curl -v http://BACKEND_IP:PORT/health",
            ],
            "solutions": [
                "Update health checker to match backend endpoint",
                "Add LB IP range to security list ingress",
                "Enable HTTP health check on backend",
                "Renew SSL certificate if HTTPS",
            ],
            "verification": "oci lb health-checker-results get --load-balancer-id $LB_ID --backend-set-name $BS_NAME",
        },
    ],
    "troubleshooting/compute": [
        {
            "symptom": "Instance stuck in PROVISIONING state",
            "causes": [
                "Quota exceeded",
                "Image not found",
                "Subnet full",
                "Capacity not available in AD",
            ],
            "diagnostics": [
                "oci compute instance get --instance-id $INSTANCE_ID --query 'data'",
                "oci limits quota list --service-name compute --compartment-id $COMPARTMENT_ID",
                "oci compute shape list --compartment-id $COMPARTMENT_ID --shape VM.Standard.E4.Flex",
            ],
            "solutions": [
                "Request quota increase if at limit",
                "Try different availability domain",
                "Use different shape with available capacity",
                "Wait for capacity to free up",
            ],
            "verification": "oci compute instance get --instance-id $INSTANCE_ID --query 'data.{state:lifecycle-state}'",
        },
    ],
    "troubleshooting/database": [
        {
            "symptom": "Autonomous Database connection failing with TNS error",
            "causes": [
                "Wallet expired",
                "Wrong connection string",
                "IP not in ACL",
                "Database stopped",
            ],
            "diagnostics": [
                "oci db autonomous-database get --autonomous-database-id $ADB_ID --query 'data.{state:lifecycle-state,dbVersion:db-version}'",
                "oci db autonomous-database get-connection-strings --autonomous-database-id $ADB_ID",
                "openssl s_client -connect hostname:443",
            ],
            "solutions": [
                "Download fresh wallet from OCI Console",
                "Update sqlnet.ora with correct wallet path",
                "Verify wallet is not expired (usually 90 days)",
                "Check if DB is in AVAILABLE state",
            ],
            "verification": "sqlplus admin/WalletPassword123@high",
        },
    ],
    "troubleshooting/oke": [
        {
            "symptom": "OKE node pool showing all nodes in NotReady state",
            "causes": [
                "CNI plugin failure",
                "Kubelet not starting",
                "Security list blocking VCN",
                "Memory/CPU pressure",
            ],
            "diagnostics": [
                "kubectl get nodes -o wide",
                "kubectl describe node NODE_NAME",
                "oci ce node-pool get --node-pool-id $NP_ID --query 'data.nodes'",
                "kubectl logs -n kube-system kube-proxy-*",
            ],
            "solutions": [
                "Check VCN security lists allow node communication",
                "Restart kubelet: sudo systemctl restart kubelet",
                "Scale down non-critical workloads",
                "Recreate node pool if persistent issues",
            ],
            "verification": "kubectl get nodes, kubectl top nodes",
        },
    ],
    "troubleshooting/functions": [
        {
            "symptom": "Function invocation returning 500 Internal Server Error",
            "causes": [
                "Function timeout",
                "Memory limit exceeded",
                "Dependency missing",
                "Cold start failure",
            ],
            "diagnostics": [
                "oci fn invocation get --function-ocid $FN_ID --invoke-endpoint $ENDPOINT",
                "oci logging log list --log-name fn-$FN_ID",
                "oci fn function get --function-id $FN_ID",
            ],
            "solutions": [
                "Increase function timeout (max 300s)",
                "Increase memory (256MB to 1GB)",
                "Reduce function package size",
                "Use function provisioned concurrency",
            ],
            "verification": "oci fn function invoke --function-id $FN_ID --file response.json",
        },
    ],
}

# =============================================================================
# HELPER FUNCTIONS - Hash-based selection (no repetition!)
# =============================================================================


def hash_select(text: str, options: list) -> tuple:
    """Select value based on hash of text - deterministic but varied."""
    h = int(hashlib.md5(text.encode()).hexdigest(), 16)
    idx = h % len(options)
    return options[idx], idx


def get_hash_value(base: str, key: str, options: list) -> str:
    """Get a value based on hash of base+key combination."""
    text = f"{base}:{key}"
    h = int(hashlib.md5(text.encode()).hexdigest(), 16)
    return options[h % len(options)]


# =============================================================================
# QUESTION TEMPLATES - Varying by category
# =============================================================================

QUESTION_TEMPLATES = {
    "compute/instances": [
        "How do I launch a {shape} instance with {ocpus} OCPUs in {region}?",
        "What's the best practice for SSH access to {shape} instances in a private subnet?",
        "How to configure cloud-init to install packages on instance boot?",
        "How to migrate from {shape} to VM.Optimized3.Flex without downtime?",
        "How to set up instance principal for OCI API access?",
        "What's the difference between bare metal and VM shapes for {workload}?",
        "How to configure fault domain distribution for high availability?",
        "How to create a custom image from a running instance?",
    ],
    "terraform/compute": [
        "How to create {shape} instance with terraform using oci_core_instance?",
        "How to configure auto-scaling for instance pool with terraform?",
        "How to import existing OCI instance into terraform state?",
        "How to set up instance pool with multiple availability domains?",
        "How to configure spot instances to reduce costs with terraform?",
        "How to use data source to get latest Oracle Linux image?",
        "How to configure detailed logging for compute resources?",
        "How to set up instance principal with terraform?",
    ],
    "terraform/networking": [
        "How to create VCN with public and private subnets using terraform?",
        "How to configure security list rules with terraform oci_core_security_list?",
        "How to set up NAT Gateway for private subnet internet access?",
        "How to create DRG and attach multiple VCNs with terraform?",
        "How to configure VCN peering with oci_core_local_peering_gateway?",
        "How to set up VPN IPSec connection with terraform?",
        "How to configure network security groups instead of security lists?",
        "How to create load balancer subnets in different ADs?",
    ],
    "terraform/storage": [
        "How to create block volume with terraform oci_core_volume?",
        "How to attach block volume to instance using terraform?",
        "How to configure object storage bucket with lifecycle policy?",
        "How to create file system with mount target using terraform?",
        "How to enable encryption at rest for volumes with terraform?",
        "How to set up cross-region object replication?",
        "How to create pre-authenticated request for bucket access?",
        "How to configure volume backup policy with terraform?",
    ],
    "terraform/database": [
        "How to create Autonomous Database with terraform oci_database_autonomous_database?",
        "How to configure MySQL DB System with terraform?",
        "How to set up read replica for Autonomous Database?",
        "How to configure backup policy for DB System?",
        "How to create database wallet with terraform?",
        "How to enable auto-scaling for Autonomous Database?",
        "How to configure private endpoint for database access?",
        "How to set up database migration with terraform?",
    ],
    "terraform/serverless": [
        "How to create Functions application with terraform?",
        "How to deploy function using oci_functions_function resource?",
        "How to configure API Gateway with terraform?",
        "How to set up function with VCN access using terraform?",
        "How to configure custom domains for API Gateway?",
        "How to set up function logging with terraform?",
        "How to configure function memory and timeout with terraform?",
        "How to use terraform to manage function triggers?",
    ],
    "terraform/security": [
        "How to create compartment structure with terraform?",
        "How to create policy with terraform oci_identity_policy?",
        "How to configure dynamic group for instance principals?",
        "How to set up Vault with keys using terraform?",
        "How to create secrets in Vault with terraform?",
        "How to configure Cloud Guard with terraform?",
        "How to set up encryption with customer-managed keys?",
        "How to create user group and assign policies with terraform?",
    ],
    "troubleshooting/performance": [
        "Instance CPU at 100% during business hours - how to diagnose?",
        "Block volume IOPS below provisioned - what's causing this?",
        "Database query performance degraded after data growth - troubleshooting steps?",
        "Application response time increasing over 24 hours - how to investigate?",
        "Auto-scaling not triggering despite high CPU - diagnostic steps?",
        "Memory exhaustion on container workloads - how to identify root cause?",
        "Network throughput dropping unexpectedly - how to diagnose?",
        "Performance baseline changed without code changes - what to check?",
    ],
    "troubleshooting/storage": [
        "Block volume showing 0 IOPS despite provisioned performance - why?",
        "Object storage bucket returning 403 Forbidden - how to fix?",
        "File system mount timeout after network interruption - troubleshooting?",
        "Storage quota showing incorrect values - diagnostic steps?",
        "Volume attachment failing with 'already attached' error - how to resolve?",
        "Bucket lifecycle policy not transitioning objects - what to check?",
        "Cannot delete object storage bucket - permission denied - fix?",
        "Block volume performance degraded after 30 days - why?",
    ],
    "troubleshooting/authentication": [
        "Policy allows action but audit shows DENIED - how to debug?",
        "Dynamic group not matching instances as expected - troubleshooting?",
        "Federated user login failing with SAML error - diagnostic steps?",
        "Service account API calls returning 401 - how to fix?",
        "Instance principal not working from another service - why?",
        "Group membership change not taking effect - propagation time?",
        "Cross-compartment access failing with 'not in allowed compartments' - fix?",
        "Resource principal session token expiring early - how to extend?",
    ],
}

# =============================================================================
# RESPONSE GENERATORS - Long, detailed, with real commands
# =============================================================================


def generate_response(category: str, question: str) -> str:
    """Generate detailed response with real OCI commands."""

    # Hash-based selections for variety
    region = get_hash_value(
        question,
        "region",
        [
            "sa-saopaulo-1",
            "us-ashburn-1",
            "us-phoenix-1",
            "eu-frankfurt-1",
            "uk-london-1",
        ],
    )
    ad = get_hash_value(question, "ad", ["AD-1", "AD-2", "AD-3"])
    shape = get_hash_value(
        question,
        "shape",
        ["VM.Standard.E4.Flex", "VM.Optimized3.Flex", "BM.Standard.E5"],
    )
    ocpus = get_hash_value(question, "ocpus", ["2", "4", "8", "16"])

    if category.startswith("troubleshooting/"):
        return generate_troubleshooting_response(category, question, region, ad, shape)
    elif category.startswith("terraform/"):
        return generate_terraform_response(category, question, region, ad, shape, ocpus)
    else:
        return generate_standard_response(category, question, region, ad, shape, ocpus)


def generate_troubleshooting_response(
    category: str, question: str, region: str, ad: str, shape: str
) -> str:
    """Generate detailed troubleshooting response with real diagnostics."""

    scenarios = TROUBLESHOOTING_SCENARIOS.get(
        category, TROUBLESHOOTING_SCENARIOS["troubleshooting/performance"]
    )
    scenario = scenarios[
        int(hashlib.md5(question.encode()).hexdigest(), 16) % len(scenarios)
    ]

    # Get relevant CLI commands
    service_key = category.replace("troubleshooting/", "")
    cli_commands = (
        OCI_CLI_COMMANDS.get(f"{service_key}/instances", [])[:3]
        if service_key != "performance"
        else []
    )

    # Generate detailed response
    response = f"""## Diagnóstico: {scenario["symptom"]}

### 1. Coleta de Dados Inicial

Execute os seguintes comandos para diagnosticar o problema:

**Verificar estado atual:**
```bash
# Listar recursos afetados
{cli_commands[0] if cli_commands else "oci compute instance list --compartment-id $COMPARTMENT_ID --region " + region}

# Verificar métricas de performance
oci monitoring metric-data query \\
  --namespace oci_computeagent \\
  --resourceId $RESOURCE_ID \\
  --query 'CpuUtilization[5m].mean()' \\
  --start-time 'now-1h' \\
  --region {region}

# Verificar alarmes ativos
oci monitoring alarm list \\
  --compartment-id $COMPARTMENT_ID \\
  --lifecycle-state FIRES \\
  --region {region}
```

### 2. Análise de Causas Raiz

**Possíveis causas identificadas:**

"""

    for i, cause in enumerate(scenario["causes"], 1):
        response += f"{i}. **{cause}**\n"

    response += f"""
### 3. Comandos de Diagnóstico Específicos

```bash
# Comando 1: Verificação detalhada
{scenario["diagnostics"][0]}

# Comando 2: Logs de audit
oci audit event list \\
  --compartment-id $COMPARTMENT_ID \\
  --start-time 'now-24h' \\
  --query 'data[?contains(message,"ERROR")]'

# Comando 3: Status do recurso
{scenario["diagnostics"][1] if len(scenario["diagnostics"]) > 1 else scenario["diagnostics"][0]}
```

### 4. Solução Passo a Passo

**Recomendação principal:** {scenario["solutions"][0]}

**Passos de implementação:**

"""

    for i, solution in enumerate(scenario["solutions"], 1):
        response += f"{i}. {solution}\n"

    response += f"""
### 5. Comandos de Verificação

```bash
# Verificar se o problema foi resolvido
{scenario["verification"]}

# Monitorar por 24 horas
oci monitoring alarm-history \\
  --alarm-id $ALARM_ID \\
  --start-time 'now-24h'
```

### 6. Prevenção

- Configurar alarmes proativos antes do próximo incidente
- Implementar runbook de auto-remediação
- Revisar dimensionamento do recurso
- Habilitar Logging integrado para diagnóstico rápido

### 7. Referências

- [OCI Monitoring Documentation](https://docs.oracle.com/en-us/iaas/Content/Monitoring/Concepts/monitoringoverview.htm)
- [OCI Audit Documentation](https://docs.oracle.com/en-us/iaas/Content/Audit/Concepts/auditoverview.htm)
"""

    return response


def generate_terraform_response(
    category: str, question: str, region: str, ad: str, shape: str, ocpus: str
) -> str:
    """Generate detailed terraform response with correct resource names."""

    # Get terraform commands for this category
    tf_commands = OCI_CLI_COMMANDS.get(
        category, OCI_CLI_COMMANDS.get("terraform/provider", [])
    )
    tf_code = tf_commands[0] if tf_commands else ""

    response = f"""## Terraform: {question}

### 1. Visão Geral

Este guia demonstra como implementar a solução usando Terraform com os recursos oficiais da OCI.

### 2. Provider Configuration

```hcl
# versions.tf
terraform {{
  required_version = ">= 1.0"
  required_providers {{
    oci = {{
      source  = "oracle/oci"
      version = "~> 5.0"
    }}
  }}
}}

# provider.tf
provider "oci" {{
  tenancy_ocid     = var.tenancy_ocid
  user_ocid        = var.user_ocid
  fingerprint      = var.fingerprint
  private_key_path = var.private_key_path
  region           = var.region
}}
```

### 3. Variáveis

```hcl
# variables.tf
variable "tenancy_ocid" {{ description = "OCI Tenancy OCID" }}
variable "compartment_id" {{ description = "Compartment OCID" }}
variable "region" {{ default = "{region}" }}
```

### 4. Recursos Principais

"""

    # Add specific terraform resource based on category
    if category == "terraform/compute":
        response += f"""```hcl
# main.tf - Compute Instance
resource "oci_core_instance" "prod_app" {{
  compartment_id = var.compartment_id
  availability_domain = data.oci_identity_availability_domains.ads.availability_domains[0].name
  shape = "{shape}"
  
  source_details {{
    source_id   = var.image_id
    source_type = "image"
  }}
  
  create_vnic_details {{
    subnet_id = oci_core_subnet.prod_subnet.id
    nsg_ids    = [oci_core_network_security_group.prod_nsg.id]
  }}
  
  metadata = {{
    "ssh_authorized_keys" = file("~/.ssh/id_rsa.pub")
    "user_data"           = base64encode(file("cloud-init.yaml"))
  }}
}}

resource "oci_core_instance_pool" "prod_pool" {{
  compartment_id = var.compartment_id
  
  placement_configs {{
    availability_domain = data.oci_identity_availability_domains.ads.availability_domains[0].name
    primary_subnet_id   = oci_core_subnet.prod_subnet.id
  }}
  
  shape           = "{shape}"
  size            = 3
  
  shape_config {{
    ocpus         = {ocpus}
    memory_in_gbs = 16
  }}
}}
```
"""
    elif category == "terraform/networking":
        response += f"""```hcl
# main.tf - VCN and Networking
resource "oci_core_vcn" "prod" {{
  cidr_blocks     = ["10.0.0.0/16"]
  compartment_id  = var.compartment_id
  display_name    = "prod-vcn"
  dns_label       = "prodvcn"
}}

resource "oci_core_subnet" "prod_private" {{
  cidr_block              = "10.0.1.0/24"
  compartment_id          = var.compartment_id
  display_name            = "prod-private"
  route_table_id          = oci_core_route_table.prod_rt.id
  security_list_ids       = [oci_core_security_list.prod_private.id]
  vcn_id                  = oci_core_vcn.prod.id
  prohibit_public_ip_on_vnic = true
}}

resource "oci_core_internet_gateway" "prod_igw" {{
  compartment_id = var.compartment_id
  vcn_id         = oci_core_vcn.prod.id
  enabled        = true
}}

resource "oci_core_nat_gateway" "prod_nat" {{
  compartment_id = var.compartment_id
  vcn_id         = oci_core_vcn.prod.id
}}

resource "oci_core_route_table" "prod_rt" {{
  vcn_id         = oci_core_vcn.prod.id
  route_rules {{
    destination       = "0.0.0.0/0"
    network_entity_id = oci_core_nat_gateway.prod_nat.id
  }}
}}
```
"""
    elif category == "terraform/database":
        response += f"""```hcl
# main.tf - Database Resources
resource "oci_database_autonomous_database" "prod_adb" {{
  compartment_id           = var.compartment_id
  display_name            = "prod-adb"
  db_name                 = "PRODDB"
  cpu_core_count          = 2
  data_storage_size_in_tbs = 1
  admin_password          = var.admin_password
  db_workload             = "OLTP"
  is_auto_scaling_enabled = true
}}

resource "oci_database_db_system" "prod_mysql" {{
  availability_domain = data.oci_identity_availability_domains.ads.availability_domains[0].name
  compartment_id     = var.compartment_id
  display_name       = "prod-mysql"
  mysql_version      = "8.0"
  shape_name         = "{shape}"
  subnet_id          = oci_core_subnet.prod_private.id
  admin_password     = var.admin_password
  
  data_storage_size_in_gbs = 256
  
  maintenance_window {{
    day_of_week = "SUNDAY"
    hour_of_day = 2
  }}
}}
```
"""
    else:
        # Generic terraform resource example
        response += f"""```hcl
# main.tf - Generic Resource
resource "oci_core_instance" "prod" {{
  compartment_id      = var.compartment_id
  availability_domain = "{ad}"
  shape              = "{shape}"
  
  source_details {{
    source_id   = var.image_id
    source_type = "image"
  }}
  
  create_vnic_details {{
    subnet_id = oci_core_subnet.prod_subnet.id
  }}
}}
```

### 5. Outputs

```hcl
output "instance_id" {{
  value = oci_core_instance.prod_app.id
}}

output "instance_private_ip" {{
  value = oci_core_instance.prod_app.private_ip
}}
```
"""

    response += """
### 6. Comandos de Execução

```bash
# Inicializar Terraform
terraform init

# Validar configuração
terraform validate

# Visualizar plano
terraform plan -var-file="prod.tfvars"

# Aplicar recursos
terraform apply -var-file="prod.tfvars"

# Importar recursos existentes
terraform import oci_core_instance.prod ocid1.instance.oc1.xxx
```

### 7. Boas Práticas

1. **Use workspaces** para separar ambientes (dev, staging, prod)
2. **Remote state** com OCI Object Storage para colaboração
3. **State locking** habilitado automaticamente com OCI native
4. **Use módulos** para recursos reutilizáveis
5. **Versionamento** do código Terraform em git

### 8. Referências

- [OCI Terraform Provider Documentation](https://registry.terraform.io/providers/oracle/oci/latest/docs)
- [Terraform Best Practices](https://www.terraform.io/docs/cloud/guides/recommended-practices/index.html)
"""

    return response


def generate_standard_response(
    category: str, question: str, region: str, ad: str, shape: str, ocpus: str
) -> str:
    """Generate standard detailed response for non-troubleshooting, non-terraform categories."""

    # Get CLI commands
    cli_commands = OCI_CLI_COMMANDS.get(category, [])
    cli_example = (
        cli_commands[0]
        if cli_commands
        else f"oci {category.split('/')[0]} list --compartment-id $COMPARTMENT_ID"
    )

    response = f"""## {question}

### 1. Visão Geral

Este guia técnico fornece passos detalhados para implementar a solução solicitada no Oracle Cloud Infrastructure.

### 2. Pré-requisitos

- OCI CLI instalado e configurado (`oci setup config`)
- Permissões IAM necessárias (grupo com policy apropriada)
- Compartment criado ou acesso a compartment existente
- VCN configurada com subnet para recursos private (se aplicável)

### 3. Preparação do Ambiente

```bash
# Configurar OCI CLI se necessário
oci setup config

# Definir variáveis de ambiente
export COMPARTMENT_ID="ocid1.compartment.oc1.xxx"
export REGION="{region}"

# Verificar conexão
oci iam region list
```

### 4. Implementação Passo a Passo

#### Passo 1: Verificar Recursos Existentes

```bash
# Listar recursos atuais
{cli_example}

# Verificar limites de serviço
oci limits quota list --service-name compute --compartment-id $COMPARTMENT_ID
```

#### Passo 2: Criar Recursos

```bash
# Exemplo de criação (ajuste parâmetros conforme necessário)
{cli_example.replace("list", "create").replace("--compartment-id $COMPARTMENT_ID", '--compartment-id $COMPARTMENT_ID --display-name "my-resource"')}
```

#### Passo 3: Configurar Acesso e Segurança

```bash
# Configurar políticas IAM
oci iam policy create \\
  --compartment-id $COMPARTMENT_ID \\
  --name "allow-group-access" \\
  --statements '["Allow group Developers to manage instance in compartment Dev"]'

# Configurar security lists ou NSGs
oci network security-list create \\
  --vcn-id $VCN_ID \\
  --display-name "my-security-list" \\
  --egress-security-rules '[{{"destination":"0.0.0.0/0","protocol":"all"}}]' \\
  --ingress-security-rules '[{{"source":"0.0.0.0/0","protocol":"tcp","tcpOptions":{{"destinationPortRange":{{"min":443,"max":443}}}}}}]'
```

#### Passo 4: Configurar Monitoramento

```bash
# Criar alarm para monitorar recurso
oci monitoring alarm create \\
  --compartment-id $COMPARTMENT_ID \\
  --display-name "High CPU Alert" \\
  --namespace "oci_computeagent" \\
  --query "CpuUtilization[5m].mean() > 80" \\
  --severity CRITICAL \\
  --destinations '["ocid1.onpremnotificationtopic.oc1.xxx"]'
```

### 5. Verificação e Validação

```bash
# Verificar recurso criado
oci compute instance list --compartment-id $COMPARTMENT_ID --lifecycle-state RUNNING

# Verificar logs
oci logging log list --compartment-id $COMPARTMENT_ID

# Verificar métricas
oci monitoring metric-data query \\
  --namespace oci_computeagent \\
  --query 'CpuUtilization[1m].mean()' \\
  --start-time 'now-1h'
```

### 6. Troubleshooting Comum

| Problema | Solução |
|----------|---------|
| Recurso não cria | Verificar quotas com `oci limits quota list` |
| Permissão negada | Verificar policies com `oci iam policy list` |
| Timeout | Verificar VCN e security lists |
| Custo alto | Revisar com `oci usageapi schedule-run` |

### 7. Limpeza (Opcional)

```bash
# Deletar recursos quando não mais necessários
oci compute instance terminate --instance-id $INSTANCE_ID --preserve-boot-volume false
```

### 8. Referências

- [OCI Documentation](https://docs.oracle.com/en-us/iaas/Content/home.htm)
- [OCI CLI Reference](https://docs.oracle.com/en-us/iaas/Content/API/SDKDocs/cliinstall.htm)
"""

    return response


# =============================================================================
# MAIN GENERATION FUNCTION
# =============================================================================


def generate_example(category: str, idx: int) -> dict:
    """Generate a single training example."""

    # Get question template based on category
    templates = QUESTION_TEMPLATES.get(
        category,
        QUESTION_TEMPLATES.get(
            category.split("/")[0],
            [
                f"How to configure {category.split('/')[1]} in OCI?",
                f"Best practices for {category.split('/')[1]} on Oracle Cloud?",
                f"Step-by-step guide for {category.split('/')[1]} implementation?",
            ],
        ),
    )

    # Use hash to select template (no repetition!)
    question_template = templates[
        int(hashlib.md5(f"{category}:{idx}".encode()).hexdigest(), 16) % len(templates)
    ]

    # Generate question with varied values
    question = question_template.format(
        shape=get_hash_value(
            category,
            f"q{idx}",
            ["VM.Standard.E4.Flex", "VM.Optimized3.Flex", "BM.Standard.E5"],
        ),
        ocpus=get_hash_value(category, f"q{idx}", ["2", "4", "8", "16"]),
        region=get_hash_value(
            category, f"q{idx}", ["sa-saopaulo-1", "us-ashburn-1", "us-phoenix-1"]
        ),
        workload=get_hash_value(
            category,
            f"q{idx}",
            ["web applications", "data processing", "machine learning"],
        ),
    )

    # Generate response
    response = generate_response(category, question)

    # Get system prompt
    system_prompt = SYSTEM_PROMPTS.get(
        category, f"You are an OCI specialist for {category}."
    )

    # Determine difficulty
    difficulty = ["beginner", "intermediate", "advanced"][
        int(hashlib.md5(f"{category}:{idx}:diff".encode()).hexdigest(), 16) % 3
    ]

    return {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question},
            {"role": "assistant", "content": response},
        ],
        "metadata": {
            "category": category,
            "difficulty": difficulty,
            "source": "generated-v3",
            "intent": "troubleshoot"
            if category.startswith("troubleshooting/")
            else "implement",
        },
    }


def main():
    print("=" * 60)
    print("OCI Specialist - Generate v3 (Evolved)")
    print("=" * 60)

    output_dir = Path("data/curated")
    output_dir.mkdir(parents=True, exist_ok=True)

    all_examples = []
    stats = Counter()

    for category, config in CATEGORIES.items():
        num_examples = config["examples"]
        print(f"\nGenerating {num_examples} examples for {category}...")

        examples = []
        for i in range(num_examples):
            example = generate_example(category, i)
            examples.append(example)
            all_examples.append(example)

        stats[category] = len(examples)
        print(f"  -> Generated {len(examples)} examples")

    # Write individual category files
    print("\nWriting category files...")
    by_category = {}
    for ex in all_examples:
        cat = ex["metadata"]["category"]
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(ex)

    for cat, cat_examples in by_category.items():
        safe_name = cat.replace("/", "-")
        fpath = output_dir / f"{safe_name}.jsonl"
        with open(fpath, "w", encoding="utf-8") as f:
            for ex in cat_examples:
                f.write(json.dumps(ex, ensure_ascii=False) + "\n")
        print(f"  Written: {fpath} ({len(cat_examples)} examples)")

    # Write combined file
    all_path = Path("data/all_curated_v3.jsonl")
    with open(all_path, "w", encoding="utf-8") as f:
        for ex in all_examples:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")

    # Summary
    print(f"\n{'=' * 60}")
    print("GENERATION COMPLETE")
    print(f"{'=' * 60}")
    print(f"Total examples: {len(all_examples)}")
    print(f"Categories: {len(stats)}")
    print(f"Output: {all_path}")

    # Category breakdown
    print(f"\nCategory breakdown:")
    for cat, count in sorted(stats.items()):
        print(f"  {cat}: {count}")


if __name__ == "__main__":
    main()
