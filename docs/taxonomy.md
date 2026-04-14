# OCI Specialist LLM - Taxonomy

## Category Hierarchy (250 examples per topic)

### oci-core (Priority: High)

#### compute/instances (250)
- Instance creation, shapes (Ampere A1, VM.Standard)
- SSH access, boot volume management
- Instance lifecycle (start, stop, terminate)
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Compute/Concepts/computeoverview.htm

#### compute/scaling (250)
- Instance pools, auto-scaling
- Capacity planning, shape resizing
- Load balancing integration
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Compute/Concepts/computeoverview.htm

#### compute/custom-images (250)
- Custom images, boot volumes
- Image import/export
- Instance configuration templates
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Compute/Tasks/managingcustomimages.htm

#### storage/block (250)
- Block Volume creation, attachment
- Performance tiers (VP, BP)
- Volume backup, clone
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Block/Concepts/blockvolumeperformance.htm

#### storage/object (250)
- Object Storage buckets
- Pre-authenticated requests
- Lifecycle policies, versioning
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Object/Concepts/objectstorageoverview.htm

#### storage/file (250)
- File Storage (NFS)
- Mount targets, export options
- Backup strategies
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/File/Concepts/filestorageoverview.htm

#### networking/vcn (250)
- VCN design, CIDR blocks
- Subnets (public/private)
- Internet Gateway, NAT Gateway
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Network/Concepts/overview.htm

#### networking/security (250)
- Security Lists, NSG
- Stateful vs stateless
- Ingress/egress rules
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Network/Concepts/overview.htm

#### networking/connectivity (250)
- DRG, VPN IPSec, FastConnect
- Hybrid cloud connectivity
- Peering (local vs remote)
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Network/Concepts/overview.htm

#### lb/load-balancer (250)
- Load Balancer (HTTP, TCP, SSL)
- Backend sets, listeners
- SSL certificates, health checks
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/LoadBalancing/Concepts/loadbalanceroverview.htm

#### database/autonomous (250)
- Autonomous Database (ATP, ADW)
- Wallet, connection strings
- Backup, restore
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Database/Concepts/databaseoverview.htm

#### database/mysql (250)
- OCI MySQL HeatWave
- Configuration, scaling
- Backup, replication
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/MySQL/Concepts/overview.htm

#### database/postgresql (250)
- OCI PostgreSQL
- Instance management, scaling
- Backup, high availability
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Database/Concepts/databaseoverview.htm

#### database/nosql (250)
- Oracle NoSQL Database
- Table creation, CRUD operations
- TTL, consistency
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/NoSQL/Concepts/nosqloverview.htm

#### database/autonomous-json (250)
- Autonomous JSON Database
- Document store, MongoDB compatibility
- JSON collections, APEX
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Database/Concepts/databaseoverview.htm

#### database/exadata (250)
- Exadata Cloud Service
- Infrastructure, DB systems
- Patching, maintenance
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Database/Concepts/databaseoverview.htm

#### container/oke (250)
- OKE cluster creation
- Node pools, worker nodes
- kubectl, deployment
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/ContEng/Concepts/contengoverview.htm

#### container/instances (250)
- OCI Container Instances
- Container Registry (OCIR)
- Image management
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/ContEng/Concepts/contengoverview.htm

#### serverless/functions (250)
- OCI Functions
- Function deployment
- Invoke, monitoring
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Functions/Concepts/functionsoverview.htm

#### serverless/api-gateway (250)
- API Gateway
- Routes, integrations
- Authentication, throttling
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/ApiGateway/Concepts/apigatewayoverview.htm

---

### oci-security (Priority: High)

#### security/iam-basics (250)
- Compartments, users, groups
- Authentication, MFA
- Console access
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Identity/Concepts/overview.htm

#### security/policies (250)
- Policy syntax, statements (text-based: `Allow group X to Y in Z`)
- Resource vs tenancy-level
- Common patterns
- **CRITICAL**: OCI policies use TEXT syntax — NEVER SQL (CREATE POLICY, GRANT)
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Identity/Concepts/overview.htm

#### security/dynamic-groups (250)
- Dynamic Group rules
- Instance principal
- Resource principal
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Identity/Concepts/overview.htm

#### security/federation (250)
- IdCS, Okta federation
- SAML, OAuth
- User provisioning
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Identity/Concepts/overview.htm

#### security/vault-secrets (250)
- Secrets management
- Secret creation, retrieval
- Rotation
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/KeyManagement/Concepts/keyoverview.htm

#### security/vault-keys (250)
- Keys, encryption
- Key policies
- Import, generate
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/KeyManagement/Concepts/keyoverview.htm

#### security/encryption (250)
- Volume encryption
- BYOK, customer-managed keys
- HSM integration
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/SecurityEncryption/overview.htm

#### security/cloud-guard (250)
- Cloud Guard configuration
- Detector recipes
- Responder rules
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/CloudGuard/concepts/cloudguardoverview.htm

#### security/waf (250)
- Web Application Firewall
- Access rules, rate limiting
- Protection patterns
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/WAF/Concepts/overview.htm

#### security/zero-trust (250)
- Zero trust architecture on OCI
- Private access, bastion patterns
- Network segmentation, least privilege
- Identity-aware access, workload isolation
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Security/Reference/security.htm

#### security/posture-management (250)
- Cloud Guard posture continuous assessment
- Security Zones configuration
- Detector recipe tuning
- Remediation workflows, governance alignment
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/CloudGuard/concepts/cloudguardoverview.htm

---

### oci-migration (Priority: High)

#### migration/aws-compute (250)
- EC2 → OCI Compute
- Instance migration, shape mapping
- Migration tools (Mover, CLI)
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Migration/overview.htm

#### migration/aws-storage (250)
- S3 → Object Storage
- Bucket migration, replication
- Data transfer (s5cmd, OCI CLI)
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Migration/overview.htm

#### migration/aws-database (250)
- RDS (MySQL, PostgreSQL, Oracle) → OCI Database
- Migration strategies, connection management
- OCI Database Migration Service
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Migration/overview.htm

#### migration/azure-compute (250)
- Azure VMs → OCI Compute
- Migration assessment, cutover
- Azure to OCI mapping
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Migration/overview.htm

#### migration/azure-storage (250)
- Azure Blob → OCI Object Storage
- Storage migration, data transfer
- AzCopy → OCI CLI
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Migration/overview.htm

#### migration/azure-database (250)
- Azure SQL → Autonomous Database
- Migration approaches, validation
- DMS configuration
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Migration/overview.htm

#### migration/gcp-compute (250)
- GCP Compute Engine → OCI Compute
- Instance migration
- GCP to OCI mapping
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Migration/overview.htm

#### migration/gcp-storage (250)
- GCP Cloud Storage → OCI Object Storage
- Bucket migration, gsutil → OCI CLI
- Data transfer
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Migration/overview.htm

#### migration/gcp-database (250)
- GCP Cloud SQL (MySQL, PostgreSQL) → OCI Database
- Database migration
- Migration tools
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Migration/overview.htm

#### migration/onprem-compute (250)
- On-premises VMs → OCI Compute
- Lift-and-shift migration
- Assessment, cutover planning
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Migration/overview.htm

#### migration/onprem-storage (250)
- On-premises file storage → OCI File Storage
- NFS migration, data transfer
- Backup strategies
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Storage/Concepts/storageoverview.htm

#### migration/onprem-vmware (250)
- VMware → OCI (VMware Cloud Foundation)
- Lift-and-shift patterns
- Hybrid connectivity (FastConnect, VPN)
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/cloud-migration/home.htm

#### migration/onprem-database (250)
- Oracle on-premises → Autonomous Database
- ZDM (Zero Downtime Migration)
- OCI Database Migration Service
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Migration/overview.htm

#### migration/data-transfer (250)
- GoldenGate replication
- OCI Data Integration service
- Large-scale data transfers
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Integration/overview.htm

---

### oci-terraform (Priority: Medium)

#### terraform/provider (250)
- Provider configuration
- Authentication (API key, instance principal)
- Region, tenancy
- **Docs**: https://registry.terraform.io/providers/oracle/oci/latest/docs

#### terraform/compute (250)
- Instance, instance pool
- Custom images, boot volumes
- Auto-scaling resources
- **Docs**: https://registry.terraform.io/providers/oracle/oci/latest/docs

#### terraform/storage (250)
- Block volume, object storage bucket
- File storage, archive storage
- Volume attachments
- **Docs**: https://registry.terraform.io/providers/oracle/oci/latest/docs

#### terraform/networking (250)
- VCN, subnet
- Security list, NSG
- Internet Gateway, NAT Gateway
- **Docs**: https://registry.terraform.io/providers/oracle/oci/latest/docs

#### terraform/load-balancer (250)
- Load balancer resource
- Backend sets, listeners
- SSL certificates
- **Docs**: https://registry.terraform.io/providers/oracle/oci/latest/docs

#### terraform/database (250)
- Autonomous database, MySQL, PostgreSQL
- NoSQL, Exadata resources
- Database resources
- **Docs**: https://registry.terraform.io/providers/oracle/oci/latest/docs

#### terraform/container (250)
- OKE cluster, node pools
- Container instances
- OCIR registry
- **Docs**: https://registry.terraform.io/providers/oracle/oci/latest/docs

#### terraform/serverless (250)
- Functions, API Gateway
- Invoke configurations
- Serverless resources
- **Docs**: https://registry.terraform.io/providers/oracle/oci/latest/docs

#### terraform/security (250)
- Vault, secrets, keys
- Cloud Guard resources
- WAF, encryption
- **Docs**: https://registry.terraform.io/providers/oracle/oci/latest/docs

#### terraform/observability (250)
- Logging, monitoring resources
- Alarms, notifications
- APM configuration
- **Docs**: https://registry.terraform.io/providers/oracle/oci/latest/docs

#### terraform/devops (250)
- DevOps resources
- Artifacts, OCIR
- Resource Manager stacks
- **Docs**: https://registry.terraform.io/providers/oracle/oci/latest/docs

#### terraform/state (250)
- Remote state (Object Storage)
- State locking
- Workspaces
- **Docs**: https://registry.terraform.io/providers/oracle/oci/latest/docs

---

### oci-observability (Priority: Medium)

#### observability/logging (250)
- Logging service
- Log groups, custom logs
- Retention, audit
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Logging/overview.htm

#### observability/monitoring (250)
- Metrics, alarms
- Notifications
- Custom metrics
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Monitoring/overview.htm

#### observability/stack-monitoring (250)
- Stack Monitoring
- Resource monitoring
- Database monitoring
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/StackMonitoring/overview.htm

#### observability/apm (250)
- APM configuration
- Distributed tracing
- Performance diagnostics
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/apm/overview.htm

---

### oci-troubleshooting (Priority: High)

#### troubleshooting/connectivity (250)
- Instance not accessible
- Routing, DNS issues
- VPN/FastConnect problems
- **Docs**: https://docs.oracle.com/en/learn/oci-ntw-troubleshoot-1/index.html

#### troubleshooting/performance (250)
- CPU, memory issues
- Storage bottlenecks
- Network latency
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Compute/Concepts/computeoverview.htm

#### troubleshooting/authentication (250)
- Policy permission denied
- MFA issues
- Federation failures
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Identity/Concepts/overview.htm

#### troubleshooting/database (250)
- Connection issues
- TNS errors
- Wallet problems
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Database/Concepts/databaseoverview.htm

#### troubleshooting/compute (250)
- Provisioning issues
- Boot volume problems
- SSH/key issues
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Compute/known-issues.htm

#### troubleshooting/storage (250)
- Bucket access
- Upload failures
- Performance issues
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Storage/Concepts/storageoverview.htm

#### troubleshooting/oke (250)
- Cluster creation failures
- Node pool issues
- Worker node problems
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/ContEng/Concepts/contengoverview.htm

#### troubleshooting/functions (250)
- Function invocation errors
- API Gateway 502/504
- Timeout issues
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Functions/Concepts/functionsoverview.htm

---

### oci-devops (Priority: Medium)

#### devops/ci-cd (250)
- Build pipeline creation and configuration
- Deploy pipeline setup with environments
- Pipeline triggers (manual, automatic)
- Artifact management between stages
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/DevOps/Concepts/devopsoverview.htm

#### devops/resource-manager (250)
- Stack creation from Terraform configurations
- Job execution and monitoring
- Drift detection and remediation
- State management and versioning
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/ResourceManager/Concepts/resourcemanager.htm

#### devops/artifacts (250)
- OCIR (Container Registry) repositories
- Artifacts service for Helm charts, binaries
- Image signing and security scanning
- Repository access control and policies
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Artifacts/Concepts/artifactsoverview.htm

#### devops/secrets (250)
- Vault secret creation and management
- Pipeline secret injection
- Parameter store configuration
- Secret rotation and lifecycle
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/KeyManagement/Concepts/keyoverview.htm

---

### oci-governance (Priority: High)

#### governance/landing-zone (250)
- Tenancy structure and compartment hierarchy
- Network segmentation and IAM guardrails
- Tagging standards and enterprise operating model
- Multi-account governance patterns
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Identity/Concepts/overview.htm

#### governance/compartments (250)
- Compartment hierarchy and delegation
- Resource isolation and naming conventions
- Operational boundaries, cross-compartment access
- Compartment quotas and cost allocation
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Identity/Tasks/managingcompartments.htm

#### governance/tagging (250)
- Defined tags and tag namespaces
- Cost allocation via tags
- Tag enforcement and automation
- Free-form vs defined tag strategy
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Tagging/Concepts/taggingoverview.htm

#### governance/budgets-cost (250)
- Budget creation and alert thresholds
- Cost anomaly detection and forecasting
- Spending guardrails across compartments
- Cost analysis and reporting
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Billing/Concepts/budgetsoverview.htm

#### governance/policies-guardrails (250)
- Least privilege policy design
- Separation of duties enforcement
- Preventive controls and guardrails
- Enterprise IAM policy patterns
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Identity/Concepts/policies.htm

#### governance/compliance (250)
- Regulatory alignment (GDPR, SOC2, ISO 27001)
- Evidence collection and retention
- Encryption controls and access reviews
- Governance process documentation
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Security/Reference/security.htm

#### governance/audit-readiness (250)
- Audit evidence and logging coverage
- Traceability and change control
- Access review workflows
- Remediation tracking and reporting
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Audit/Concepts/auditoverview.htm

#### governance/resource-discovery (250)
- Resource search and inventory reporting
- Tagging-based discovery
- Cross-compartment resource visibility
- Governance dashboards and reporting
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Search/Concepts/queryoverview.htm

---

### oci-finops (Priority: High)

#### finops/cost-optimization (250)
- Rightsizing analysis and recommendations
- Storage tiering and waste reduction
- Autoscaling efficiency patterns
- Cost forecasting and budgeting
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Billing/Concepts/costoverview.htm

#### finops/showback-chargeback (250)
- Cost allocation via tagging
- Showback and chargeback reporting models
- Shared service cost distribution
- Financial accountability workflows
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Tagging/Concepts/taggingoverview.htm

#### finops/rightsizing (250)
- CPU and memory utilization analysis
- Idle resource identification
- Shape optimization recommendations
- Storage rightsizing
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Monitoring/overview.htm

#### finops/storage-tiering (250)
- Object Storage tier lifecycle policies (Standard → Infrequent → Archive)
- Block volume performance tier optimization
- Backup retention cost governance
- Storage cost reduction patterns
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Object/Concepts/objectstorageoverview.htm

---

### oci-platform (Priority: Medium)

#### platform/backup-governance (250)
- Backup policy creation and enforcement
- Retention standards and exception handling
- Backup ownership and accountability
- Backup testing and validation procedures
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Block/Concepts/blockvolumebackups.htm

#### platform/sre-operations (250)
- SLO definition and alerting setup
- Incident response runbooks
- Capacity review processes
- Operational governance and on-call practices
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Monitoring/overview.htm

---

## Difficulty Levels

- **beginner**: Basic concepts, service overview (30%)
- **intermediate**: Implementation, configuration (50%)
- **advanced**: Architecture design, migration, troubleshooting (20%)

## Metadata Dimensions

The generator enriches each example with the following contextual dimensions:

- **Intent**: design, compare, troubleshoot, remediate, audit, optimize, migrate, standardize, review, recover
- **Persona**: cloud architect, platform engineer, sre, security lead, dba, finops analyst, auditor, devops engineer
- **Constraint**: sem downtime, sem IP público, com budget limitado, com auditoria em 30 dias, ambiente legado, equipe enxuta, multi-região, integração híbrida, mínimo privilégio, rollback em menos de 15 minutos
- **Lifecycle Stage**: greenfield, brownfield, produção estável, incidente, expansão, auditoria, migração, desativação

## Total

- **84 categories × 250 examples = 21,000 examples total**
- Diversity: 30% beginner / 50% intermediate / 20% advanced
- Structural uniqueness guaranteed per category via scenario, code, response structure, and content variation
