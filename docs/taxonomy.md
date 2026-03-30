# OCI Specialist LLM - Taxonomy

## Category Hierarchy

### oci-core (Priority: High)

#### oci-core/compute
- Instances, shapes, HPC
- Instance pools, auto-scaling
- Custom images, boot volumes

#### oci-core/storage
- Block Volume
- Object Storage
- File Storage
- Archive Storage

#### oci-core/networking
- VCN design
- Subnets (public/private)
- Security Lists
- Network Security Groups
- Route Tables
- DRG, VPN, FastConnect
- Load Balancing

#### oci-core/database
- Autonomous Database
- MySQL, PostgreSQL
- Exadata

### oci-security (Priority: High)

#### oci-security/iam
- Compartments
- Policies
- Groups
- Users
- Dynamic Groups
- Authentication (MFA)

#### oci-security/vault
- Secrets
- Keys
- HSM

#### oci-security/encryption
- Volume encryption
- Object Storage encryption
- Customer-managed keys

### oci-migration (Priority: High)

#### oci-migration/aws-to-oci
- EC2 → OCI Compute
- S3 → Object Storage
- RDS → Autonomous DB
- VPC → VCN mapping
- IAM role mapping

#### oci-migration/azure-to-oci
- Azure VMs → OCI Compute
- Azure Blob → Object Storage
- Azure SQL → Autonomous DB
- VNet → VCN mapping

#### oci-migration/onprem-to-oci
- VMware → OCI
- Lift-and-shift patterns
- Hybrid connectivity

### oci-terraform (Priority: Medium)

#### oci-terraform/provider
- Provider configuration
- Authentication

#### oci-terraform/resources
- compute instance
- vcn, subnet
- iam policy
- object storage bucket

### oci-troubleshooting (Priority: Medium)

#### oci-troubleshooting/connectivity
- Routing issues
- Firewall rules
- DNS problems

#### oci-troubleshooting/performance
- Shape sizing
- Storage bottlenecks
- Network latency

## Difficulty Levels

- **beginner**: Basic concepts, service overview
- **intermediate**: Implementation, configuration
- **advanced**: Architecture design, migration, troubleshooting
