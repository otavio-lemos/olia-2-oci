# OCI Specialist LLM - Taxonomy

## Category Hierarchy (10 examples per topic)

### oci-core (Priority: High)

#### compute/instances (10)
- Instance creation, shapes (Ampere A1, VM.Standard)
- SSH access, boot volume management
- Instance lifecycle (start, stop, terminate)
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Compute/Concepts/computeoverview.htm

#### compute/scaling (10)
- Instance pools, auto-scaling
- Capacity planning, shape resizing
- Load balancing integration
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Compute/Concepts/computeoverview.htm

#### compute/custom-images (10)
- Custom images, boot volumes
- Image import/export
- Instance configuration templates
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Compute/Concepts/computeoverview.htm

#### storage/block (10)
- Block Volume creation, attachment
- Performance tiers (VP, BP)
- Volume backup, clone
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Storage/Concepts/storageoverview.htm

#### storage/object (10)
- Object Storage buckets
- Pre-authenticated requests
- Lifecycle policies, versioning
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Storage/Concepts/storageoverview.htm

#### storage/file (10)
- File Storage (NFS)
- Mount targets, export options
- Backup strategies
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Storage/Concepts/storageoverview.htm

#### networking/vcn (10)
- VCN design, CIDR blocks
- Subnets (public/private)
- Internet Gateway, NAT Gateway
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Network/Concepts/overview.htm

#### networking/security (10)
- Security Lists, NSG
- Stateful vs stateless
- Ingress/egress rules
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Network/Concepts/overview.htm

#### networking/connectivity (10)
- DRG, VPN IPSec, FastConnect
- Hybrid cloud connectivity
- Peering (local vs remote)
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Network/Concepts/overview.htm

#### lb/load-balancer (10)
- Load Balancer (HTTP, TCP, SSL)
- Backend sets, listeners
- SSL certificates, health checks
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/LoadBalancing/Concepts/loadbalanceroverview.htm

#### database/autonomous (10)
- Autonomous Database (ATP, ADW)
- Wallet, connection strings
- Backup, restore
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Database/Concepts/databaseoverview.htm

#### database/mysql (10)
- OCI MySQL HeatWave
- Configuration, scaling
- Backup, replication
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Database/Concepts/databaseoverview.htm

#### database/postgresql (10)
- OCI PostgreSQL
- Instance management, scaling
- Backup, high availability
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Database/Concepts/databaseoverview.htm

#### database/nosql (10)
- Oracle NoSQL Database
- Table creation, CRUD operations
- TTL, consistency
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/nosql/-nosql.htm

#### database/autonomous-json (10)
- Autonomous JSON Database
- Document store, MongoDB compatibility
- JSON collections, APEX
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Database/Concepts/databaseoverview.htm

#### database/exadata (10)
- Exadata Cloud Service
- Infrastructure, DB systems
- Patching, maintenance
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Database/Concepts/databaseoverview.htm

#### container/oke (10)
- OKE cluster creation
- Node pools, worker nodes
- kubectl, deployment
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/ContEng/Concepts/contengoverview.htm

#### container/instances (10)
- OCI Container Instances
- Container Registry (OCIR)
- Image management
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/ContEng/Concepts/contengoverview.htm

#### serverless/functions (10)
- OCI Functions
- Function deployment
- Invoke, monitoring
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Functions/Con/functionsoverview.htm

#### serverless/api-gateway (10)
- API Gateway
- Routes, integrations
- Authentication, throttling
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Functions/Con/functionsoverview.htm

---

### oci-security (Priority: High)

#### security/iam-basics (10)
- Compartments, users, groups
- Authentication, MFA
- Console access
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Identity/Concepts/overview.htm

#### security/policies (10)
- Policy syntax, statements
- Resource vs tenancy-level
- Common patterns
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Identity/Concepts/overview.htm

#### security/dynamic-groups (10)
- Dynamic Group rules
- Instance principal
- Resource principal
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Identity/Concepts/overview.htm

#### security/federation (10)
- IdCS, Okta federation
- SAML, OAuth
- User provisioning
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Identity/Concepts/overview.htm

#### security/vault-secrets (10)
- Secrets management
- Secret creation, retrieval
- Rotation
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/KeyManagement/Concepts/keyoverview.htm

#### security/vault-keys (10)
- Keys, encryption
- Key policies
- Import, generate
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/KeyManagement/Concepts/keyoverview.htm

#### security/encryption (10)
- Volume encryption
- BYOK, customer-managed keys
- HSM integration
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/SecurityEncryption/overview.htm

#### security/cloud-guard (10)
- Cloud Guard configuration
- Detector recipes
- Responder rules
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/CloudGuard/concepts/cloudguardoverview.htm

#### security/waf (10)
- Web Application Firewall
- Access rules, rate limiting
- Protection patterns
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/WAF/Concepts/overview.htm

---

### oci-migration (Priority: High)

#### migration/aws-compute (10)
- EC2 → OCI Compute
- Instance migration, shape mapping
- Migration tools (Mover, CLI)
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Migration/overview.htm

#### migration/aws-storage (10)
- S3 → Object Storage
- Bucket migration, replication
- Data transfer (s5cmd, OCI CLI)
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Migration/overview.htm

#### migration/aws-database (10)
- RDS (MySQL, PostgreSQL, Oracle) → OCI Database
- Migration strategies, connection management
- OCI Database Migration Service
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Migration/overview.htm

#### migration/azure-compute (10)
- Azure VMs → OCI Compute
- Migration assessment, cutover
- Azure to OCI mapping
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Migration/overview.htm

#### migration/azure-storage (10)
- Azure Blob → OCI Object Storage
- Storage migration, data transfer
- AzCopy → OCI CLI
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Migration/overview.htm

#### migration/azure-database (10)
- Azure SQL → Autonomous Database
- Migration approaches, validation
- DMS configuration
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Migration/overview.htm

#### migration/gcp-compute (10)
- GCP Compute Engine → OCI Compute
- Instance migration
- GCP to OCI mapping
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Migration/overview.htm

#### migration/gcp-storage (10)
- GCP Cloud Storage → OCI Object Storage
- Bucket migration, gsutil → OCI CLI
- Data transfer
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Migration/overview.htm

#### migration/gcp-database (10)
- GCP Cloud SQL (MySQL, PostgreSQL) → OCI Database
- Database migration
- Migration tools
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Migration/overview.htm

#### migration/onprem-compute (10)
- On-premises VMs → OCI Compute
- Lift-and-shift migration
- Assessment, cutover planning
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Migration/overview.htm

#### migration/onprem-storage (10)
- On-premises file storage → OCI File Storage
- NFS migration, data transfer
- Backup strategies
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Storage/Concepts/storageoverview.htm

#### migration/onprem-vmware (10)
- VMware → OCI (VMware Cloud Foundation)
- Lift-and-shift patterns
- Hybrid connectivity (FastConnect, VPN)
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/cloud-migration/home.htm

#### migration/onprem-database (10)
- Oracle on-premises → Autonomous Database
- ZDM (Zero Downtime Migration)
- OCI Database Migration Service
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Migration/overview.htm

#### migration/data-transfer (10)
- GoldenGate replication
- OCI Data Integration service
- Large-scale data transfers
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Integration/overview.htm

---

### oci-terraform (Priority: Medium)

#### terraform/provider (10)
- Provider configuration
- Authentication (API key, instance principal)
- Region, tenancy
- **Docs**: https://registry.terraform.io/providers/oracle/oci/latest/docs

#### terraform/compute (10)
- Instance, instance pool
- Custom images, boot volumes
- Auto-scaling resources
- **Docs**: https://registry.terraform.io/providers/oracle/oci/latest/docs

#### terraform/storage (10)
- Block volume, object storage bucket
- File storage, archive storage
- Volume attachments
- **Docs**: https://registry.terraform.io/providers/oracle/oci/latest/docs

#### terraform/networking (10)
- VCN, subnet
- Security list, NSG
- Internet Gateway, NAT Gateway
- **Docs**: https://registry.terraform.io/providers/oracle/oci/latest/docs

#### terraform/load-balancer (10)
- Load balancer resource
- Backend sets, listeners
- SSL certificates
- **Docs**: https://registry.terraform.io/providers/oracle/oci/latest/docs

#### terraform/database (10)
- Autonomous database, MySQL, PostgreSQL
- NoSQL, Exadata resources
- Database resources
- **Docs**: https://registry.terraform.io/providers/oracle/oci/latest/docs

#### terraform/container (10)
- OKE cluster, node pools
- Container instances
- OCIR registry
- **Docs**: https://registry.terraform.io/providers/oracle/oci/latest/docs

#### terraform/serverless (10)
- Functions, API Gateway
- Invoke configurations
- Serverless resources
- **Docs**: https://registry.terraform.io/providers/oracle/oci/latest/docs

#### terraform/security (10)
- Vault, secrets, keys
- Cloud Guard resources
- WAF, encryption
- **Docs**: https://registry.terraform.io/providers/oracle/oci/latest/docs

#### terraform/observability (10)
- Logging, monitoring resources
- Alarms, notifications
- APM configuration
- **Docs**: https://registry.terraform.io/providers/oracle/oci/latest/docs

#### terraform/devops (10)
- DevOps resources
- Artifacts, OCIR
- Resource Manager stacks
- **Docs**: https://registry.terraform.io/providers/oracle/oci/latest/docs

#### terraform/state (10)
- Remote state (Object Storage)
- State locking
- Workspaces
- **Docs**: https://registry.terraform.io/providers/oracle/oci/latest/docs

---

### oci-observability (Priority: Medium)

#### observability/logging (10)
- Logging service
- Log groups, custom logs
- Retention, audit
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Logging/overview.htm

#### observability/monitoring (10)
- Metrics, alarms
- Notifications
- Custom metrics
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Monitoring/overview.htm

#### observability/stack-monitoring (10)
- Stack Monitoring
- Resource monitoring
- Database monitoring
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/StackMonitoring/overview.htm

#### observability/apm (10)
- APM configuration
- Distributed tracing
- Performance diagnostics
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/apm/overview.htm

---

### oci-troubleshooting (Priority: High)

#### troubleshooting/connectivity (10)
- Instance not accessible
- Routing, DNS issues
- VPN/FastConnect problems
- **Docs**: https://docs.oracle.com/en/learn/oci-ntw-troubleshoot-1/index.html

#### troubleshooting/performance (10)
- CPU, memory issues
- Storage bottlenecks
- Network latency
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Compute/Concepts/computeoverview.htm

#### troubleshooting/authentication (10)
- Policy permission denied
- MFA issues
- Federation failures
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Identity/Concepts/overview.htm

#### troubleshooting/database (10)
- Connection issues
- TNS errors
- Wallet problems
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Database/Concepts/databaseoverview.htm

#### troubleshooting/compute (10)
- Provisioning issues
- Boot volume problems
- SSH/key issues
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Compute/known-issues.htm

#### troubleshooting/storage (10)
- Bucket access
- Upload failures
- Performance issues
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Storage/Concepts/storageoverview.htm

#### troubleshooting/oke (10)
- Cluster creation failures
- Node pool issues
- Worker node problems
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/ContEng/Concepts/contengoverview.htm

#### troubleshooting/functions (10)
- Function invocation errors
- API Gateway 502/504
- Timeout issues
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Functions/Con/functionsoverview.htm

---

### oci-devops (Priority: Medium)

#### devops/ci-cd (10)
- Build pipeline creation and configuration
- Deploy pipeline setup with environments
- Pipeline triggers (manual, automatic)
- Artifact management between stages
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/DevOps/Concepts/devopsoverview.htm

#### devops/resource-manager (10)
- Stack creation from Terraform configurations
- Job execution and monitoring
- Drift detection and remediation
- State management and versioning
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/ResourceManager/Con/resourcemanager.htm

#### devops/artifacts (10)
- OCIR (Container Registry) repositories
- Artifacts service for Helm charts, binaries
- Image signing and security scanning
- Repository access control and policies
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Artifacts/Concepts/artifactsoverview.htm

#### devops/secrets (10)
- Vault secret creation and management
- Pipeline secret injection
- Parameter store configuration
- Secret rotation and lifecycle
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/KeyManagement/Concepts/keyoverview.htm

---

## Difficulty Levels

- **beginner**: Basic concepts, service overview (30%)
- **intermediate**: Implementation, configuration (50%)
- **advanced**: Architecture design, migration, troubleshooting (20%)

## Total

- 71 topics × 10 examples = 710 examples total
