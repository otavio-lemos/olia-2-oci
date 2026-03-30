# OCI Specialist LLM - Taxonomy

## Category Hierarchy

### oci-core (Priority: High)

#### oci-core/compute (30 examples suggested)
- Instances, shapes, HPC
- Instance pools, auto-scaling
- Custom images, boot volumes
- Example questions: "Como criar instância com shape Ampere A1?", "Configurar instance pool com auto-scaling"
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Compute/Concepts/computeoverview.htm

#### oci-core/storage (25 examples suggested)
- Block Volume
- Object Storage
- File Storage
- Archive Storage
- Example questions: "Como criar bucket com versioning?", "Migrar dados para Object Storage"
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Storage/Concepts/storageoverview.htm

#### oci-core/networking (25 examples suggested)
- VCN design
- Subnets (public/private)
- Security Lists
- Network Security Groups
- Route Tables
- DRG, VPN, FastConnect
- Example questions: "Como configurar NSG para permitir HTTP?", "Conectar VCN on-premises via FastConnect"
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Network/Concepts/overview.htm

#### oci-core/load-balancing (20 examples suggested)
- Load Balancer (HTTP, TCP, SSL)
- Backend sets, listeners
- SSL certificates
- Health checks
- Path routing
- Example questions: "Como configurar Load Balancer para aplicação web?", "Configurar SSL no Load Balancer"
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/LoadBalancing/Concepts/loadbalanceroverview.htm

#### oci-core/database (20 examples suggested)
- Autonomous Database (ATP, ADW)
- MySQL HeatWave
- PostgreSQL
- Exadata
- Example questions: "Como criar Autonomous Database?", "Configurar backup automático"
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Database/Concepts/databaseoverview.htm

#### oci-core/container (15 examples suggested)
- OKE (Oracle Kubernetes Engine)
- Container Instances
- Registry (OCIR)
- Example questions: "Como criar cluster OKE?", "Deployar aplicação no OKE"
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/ContEng/Concepts/contengoverview.htm

#### oci-core/serverless (10 examples suggested)
- OCI Functions
- API Gateway
- Example questions: "Como criar function com OCI Functions?", "Configurar API Gateway"
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Functions/Con/functionsoverview.htm

#### oci-core/ai-ml (10 examples suggested)
- OCI AI Services
- Data Science
- Model deployment
- Example questions: "Como usar OCI Vision?", "Deployar modelo no OCI Data Science"
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/AI/overview.htm

### oci-security (Priority: High)

#### oci-security/iam (30 examples suggested)
- Compartments
- Policies
- Groups
- Users
- Dynamic Groups
- Authentication (MFA)
- Federation (IdCS, Okta)
- Example questions: "Policy para permitir criação de instâncias apenas em compartment dev", "Configurar MFA para usuários"
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Identity/Concepts/overview.htm

#### oci-security/vault (20 examples suggested)
- Secrets
- Keys
- HSM
- Secret rotation
- Example questions: "Como criar secret para API key?", "Configurar rotação automática de secrets"
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/KeyManagement/Concepts/keyoverview.htm

#### oci-security/encryption (20 examples suggested)
- Volume encryption
- Object Storage encryption
- Customer-managed keys (CMK)
- BYOK (Bring Your Own Key)
- Example questions: "Como usar Vault para criptografar Block Volume?", "Configurar BYOK"
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/SecurityEncryption/overview.htm

#### oci-security/cloud-guard (15 examples suggested)
- Cloud Guard security posture
- Detector recipes
- Responder rules
- Security scores
- Target configurations
- Example questions: "Configurar Cloud Guard para detectar vulnerabilidades", "Review de security do OCI"
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/CloudGuard/concepts/cloudguardoverview.htm

#### oci-security/waf (10 examples suggested)
- Web Application Firewall
- Access rules
- Rate limiting
- IP blocking
- SQL injection protection
- Example questions: "Configurar WAF para API", "Proteger aplicação contra ataques"
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/WAF/Concepts/overview.htm

### oci-migration (Priority: High)

#### oci-migration/aws-to-oci (20 examples suggested)
- EC2 → OCI Compute
- S3 → Object Storage
- RDS → Autonomous DB
- VPC → VCN mapping
- IAM role mapping
- EKS → OKE
- Example questions: "Mapear VPC AWS para VCN OCI", "Migrar RDS MySQL para Autonomous Database"
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Migration/overview.htm

#### oci-migration/azure-to-oci (20 examples suggested)
- Azure VMs → OCI Compute
- Azure Blob → Object Storage
- Azure SQL → Autonomous DB
- VNet → VCN mapping
- AKS → OKE
- Example questions: "Mapear VNet Azure para VCN", "Migrar Azure Blob para OCI Object Storage"
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Migration/overview.htm

#### oci-migration/gcp-to-oci (20 examples suggested)
- Compute Engine → OCI Compute
- Cloud Storage → Object Storage
- Cloud SQL → Autonomous DB
- VPC → VCN mapping
- GKE → OKE
- Example questions: "Mapear GCP VPC para VCN OCI", "Migrar Cloud Storage para Object Storage"
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Migration/overview.htm

#### oci-migration/onprem-to-oci (20 examples suggested)
- VMware → OCI (VMware Cloud Foundation)
- Lift-and-shift patterns
- Hybrid connectivity (FastConnect, VPN)
- Oracle Cloud Migrations service
- Data migration tools
- Example questions: "Conectar datacenter on-premises via FastConnect", "Migração lift-and-shift de VMs via OCI Cloud Migrations"
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/cloud-migration/home.htm

#### oci-migration/database-migration (20 examples suggested)
- OCI Database Migration Service
- Online vs Offline migration
- Zero Downtime Migration (ZDM)
- Oracle → Autonomous DB migration
- MySQL → OCI MySQL migration
- Example questions: "Migrar banco Oracle on-premises para Autonomous DB", "Configurar Zero Downtime Migration"
- **Docs**: https://docs.oracle.com/en-us/iaas/database-migration/doc/overview.html

#### oci-migration/data-migration (15 examples suggested)
- OCI GoldenGate for data replication
- Data Integration service
- Object Storage data transfer
- Storage Gateway
- Example questions: "Configurar replicação com GoldenGate", "Migrar dados com OCI Data Integration"
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Integration/overview.htm

#### oci-migration/storage-migration (15 examples suggested)
- OCI Object Storage Sync
- s5cmd tool
- Storage Gateway
- File Storage migration
- Large data transfer
- Example questions: "Migrar grande volume de dados para Object Storage", "Usar s5cmd para upload"
- **Docs**: https://docs.oracle.com/en/learn/migr-ocistorage-p1/

#### oci-migration/oracle-to-oci (15 examples suggested)
- Oracle Cloud Classic → OCI migration
- Oracle E-Business Suite → OCI
- PeopleSoft → OCI
- JD Edwards → OCI
- Oracle Fusion → OCI
- Example questions: "Migrar EBS para OCI", "Mover Oracle Cloud Classic para OCI"
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/cloud-migration/home.htm

#### oci-migration/applications (15 examples suggested)
- Oracle Integration migration
- Oracle Process Automation migration
- SaaS migration patterns
- Application re-platforming
- Example questions: "Migrar Oracle Integration para OCI", "Mover aplicações SaaS para OCI"
- **Docs**: https://docs.oracle.com/en/cloud/paas/application-integration/oracle-integration-oci/

### oci-terraform (Priority: Medium)

#### oci-terraform/provider (10 examples suggested)
- Provider configuration
- Authentication (API key, instance principal, resource principal)
- Region configuration
- Provider version management
- Example questions: "Configurar provider OCI com API key", "Autenticação via instance principal"
- **Docs**: https://registry.terraform.io/providers/oracle/oci/latest/docs

#### oci-terraform/resources (30 examples suggested)
- Compute: instance, instance pool, custom image
- Networking: vcn, subnet, security list, NSG, load balancer
- IAM: policy, group, user, dynamic group
- Storage: object storage bucket, block volume, file system
- Database: autonomous database, mysql, database
- Example questions: "Criar instância com Terraform", "Criar VCN com subnets via Terraform"
- **Docs**: https://registry.terraform.io/providers/oracle/oci/latest/docs

#### oci-terraform/modules (15 examples suggested)
- Oracle official modules
- Module usage and composition
- Reusable infrastructure patterns
- Network modules (vcn, subnets)
- Compute modules (instance, instance pool)
- Example questions: "Usar módulos oficiais OCI Terraform", "Criar VCN com módulo Oracle"
- **Docs**: https://github.com/oracle-terraform-modules

#### oci-terraform/best-practices (15 examples suggested)
- State management (local vs remote)
- Remote state with OCI Object Storage
- Workspaces
- Sentinel policies
- Drift detection
- Code organization
- Example questions: "Configurar remote state no OCI", "Usar workspaces no Terraform"
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/dev/terraform/supported-services.htm

#### oci-terraform/oke (15 examples suggested)
- OKE cluster creation
- Node pools
- OCI Kubernetes Engine resources
- Kubernetes manifests vs Terraform
- CNI configuration
- Example questions: "Criar cluster OKE com Terraform", "Configurar node pool com Terraform"
- **Docs**: https://registry.terraform.io/providers/oracle/oci/latest/docs/container_engine.html

### oci-observability (Priority: Medium)

#### oci-observability/logging (15 examples)
- Logging service
- Log groups
- Custom logs
- Log retention
- Audit logs
- Service logs (Compute, Network, Database)
- Example questions: "Configurar logging para instância", "Criar log group customizado"
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Logging/overview.htm

#### oci-observability/monitoring (15 examples)
- Metrics
- Alarms
- Notifications
- Alarm destinations (email, Slack, PagerDuty)
- Custom metrics
- Example questions: "Criar alarme para CPU > 80%", "Configurar notificação via OCI Notifications"
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Monitoring/overview.htm

#### oci-observability/stack-monitoring (10 examples)
- Stack Monitoring
- Enterprise Manager
- Resource monitoring
- Database monitoring
- Exadata monitoring
- Example questions: "Configurar Stack Monitoring para banco de dados", "Monitorar infraestrutura OCI"
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/StackMonitoring/overview.htm

#### oci-observability/apm (10 examples)
- Application Performance Monitoring (APM)
- Distributed tracing
- Performance diagnostics
- Service maps
- Example questions: "Configurar APM para aplicação", "Debugar performance com tracing"
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/apm/overview.htm

### oci-troubleshooting (Priority: High)

#### oci-troubleshooting/connectivity (25 examples suggested)
- Instance not accessible from internet
- Routing issues (route table problems)
- Security List / NSG blocking traffic
- DNS problems (internal/external)
- VPN/FastConnect connectivity issues
- MTU issues
- Example questions: "Instância não acessível pela internet", "Problemas de DNS interno", "VPN IPSec não conecta"
- **Docs**: https://docs.oracle.com/en/learn/oci-ntw-troubleshoot-1/index.html

#### oci-troubleshooting/performance (20 examples suggested)
- Instance performance (CPU, memory)
- Shape sizing issues
- Storage bottlenecks (IOPS, throughput)
- Network latency
- Database performance
- Example questions: "Instance muito lenta, como diagnosticar?", "Performance de storage ruim"
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Compute/Concepts/computeoverview.htm

#### oci-troubleshooting/authentication (20 examples suggested)
- IAM policy permission denied
- Dynamic Group issues
- MFA problems
- Federation failures
- Token expiration issues
- "NotAuthorized" errors
- Example questions: "Policy não funciona, usuário não acessa recurso", "Erro 403 NotAuthorized"
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Identity/Concepts/overview.htm

#### oci-troubleshooting/database (20 examples suggested)
- Autonomous Database connection issues
- Connection string problems
- Wallet file issues
- TNS errors
- Performance issues in ADB
- Example questions: "Não consigo conectar no Autonomous Database", "Erro TNS: listener"
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Database/Concepts/databaseoverview.htm

#### oci-troubleshooting/compute (15 examples suggested)
- Instance stuck in provisioning
- Boot volume issues
- Shape allocation failures
- SSH key problems
- Instance lifecycle errors
- Example questions: "Instância travada em provisioning", "Não consigo fazer SSH na instância"
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Compute/known-issues.htm

#### oci-troubleshooting/storage (15 examples suggested)
- Bucket access issues
- Object upload/download failures
- Performance issues
- Replication problems
- Lifecycle policy issues
- Example questions: "Bucket não acessível", "Upload de arquivo muito lento"
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Storage/Concepts/storageoverview.htm

#### oci-troubleshooting/oke (10 examples suggested)
- OKE cluster creation failures
- Node pool issues
- Worker node not joining
- CNI plugin problems
- Storage mount issues
- Example questions: "Worker node não junta no cluster", "PVC não monta no OKE"
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/ContEng/Concepts/contengoverview.htm

#### oci-troubleshooting/functions-api-gateway (10 examples suggested)
- Function invocation errors
- API Gateway 502/504 errors
- Timeout issues
- Cold start problems
- Example questions: "Function retorna erro 500", "API Gateway retorna 502 Bad Gateway"
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Functions/Con/functionsoverview.htm

### oci-devops (Priority: Medium)

#### oci-devops/ci-cd (20 examples)
- OCI DevOps service
- Build pipelines
- Deploy pipelines
- Artifacts registry
- Container registry (OCIR)
- GitHub Actions integration
- Example questions: "Configurar CI/CD com OCI DevOps", "Deploy automático via OCI DevOps"
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/DevOps/Concepts/devopsoverview.htm

#### oci-devops/resource-manager (15 examples)
- Resource Manager
- Terraform stacks
- Job execution
- Drift detection
- State management
- Example questions: "Usar Resource Manager para deploy", "Importar Terraform no OCI"
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/ResourceManager/Con/resourcemanager.htm

#### oci-devops/artifacts-registry (10 examples)
- OCI Artifacts service
- Container Registry (OCIR)
- Generic artifacts
- Image signing
- Access control
- Example questions: "Configurar OCIR para armazenar imagens", "Usar Artifacts service"
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/Artifacts/Concepts/artifactsoverview.htm

#### oci-devops/secrets (10 examples)
- OCI Vault integration with DevOps
- Secret injection in pipelines
- Secure parameter storage
- Example questions: "Usar Vault secrets no pipeline", "Injetar API key no deployment"
- **Docs**: https://docs.oracle.com/en-us/iaas/Content/KeyManagement/Concepts/keyoverview.htm

## Difficulty Levels

- **beginner**: Basic concepts, service overview (30%)
- **intermediate**: Implementation, configuration (50%)
- **advanced**: Architecture design, migration, troubleshooting (20%)

## Total Examples Guide

Basic execution (local training): 660-710 examples
- oci-core/*: ~155 examples
- oci-security/*: ~95 examples
- oci-migration/*: ~160 examples
- oci-terraform/*: ~70 examples
- oci-observability/*: ~50 examples
- oci-troubleshooting/*: ~135 examples
- oci-devops/*: ~55 examples
