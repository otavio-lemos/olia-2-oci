# Prompt Template: oci-migration/azure-to-oci

## Context

Generate examples about migrating from Azure to OCI.

## Topics

- Azure VMs → OCI Compute
- Azure Blob → Object Storage
- Azure SQL → Autonomous Database
- VNet → VCN mapping
- Azure AD → OCI IAM mapping
- AKS → OKE

## Difficulty Distribution

- beginner (30%): Basic service mapping
- intermediate (40%): Network migration
- advanced (30%): Complex migrations

## Quality Rules

- Always include Azure → OCI mapping
- Explain differences between services
- Tag mutable content with [MUTABLE]

---

## OCI CLI Syntax Section

When generating examples, include actual OCI CLI commands:

### Compute (Azure VM → OCI Compute)

```bash
# List compute instances
oci compute instance list --compartment-id $COMPARTMENT_ID

# Create VM instance
oci compute instance launch \
  --display-name "prod-web-server" \
  --compartment-id $COMPARTMENT_ID \
  --availability-domain "US-ASHBURN-AD-1" \
  --image-id ocid1.image.oc1.iad.xxx \
  --shape VM.Standard.E4.Flex \
  --subnet-id ocid1.subnet.oc1.iad.xxx

# Resize instance (change shape)
oci compute instance update \
  --instance-id $INSTANCE_OCID \
  --shape VM.Standard.E5.Flex
```

### Object Storage (Azure Blob → OCI Object Storage)

```bash
# List buckets
oci os bucket list --namespace-name $NAMESPACE_NAME --compartment-id $COMPARTMENT_ID

# Create bucket with tiering
oci os bucket create \
  --name "migration-bucket" \
  --namespace-name $NAMESPACE_NAME \
  --compartment-id $COMPARTMENT_ID \
  --storage-tier "Standard"

# Upload object with multipart
oci os object put \
  --namespace-name $NAMESPACE_NAME \
  --bucket-name "migration-bucket" \
  --file "/path/to/large-file.tar.gz" \
  --part-size 100

# Generate pre-authenticated request
oci os preauth-request create \
  --bucket-name "migration-bucket" \
  --namespace-name $NAMESPACE_NAME \
  --name "download-link" \
  --access-type "ObjectRead" \
  --time-expires "2024-12-31T23:59:59Z"
```

### Database (Azure SQL → OCI Autonomous Database)

```bash
# List autonomous databases
oci db autonomous-database list --compartment-id $COMPARTMENT_ID

# Create Autonomous Transaction Processing
oci db autonomous-database create \
  --display-name "prod-atp" \
  --compartment-id $COMPARTMENT_ID \
  --db-name "PRODDB" \
  --cpu-core-count 2 \
  --storage-size-in-tbs 1 \
  --license-model "LICENSE_INCLUDED" \
  --db-workload "ATP"

# Create Autonomous Data Warehouse
oci db autonomous-database create \
  --display-name "prod-adw" \
  --compartment-id $COMPARTMENT_ID \
  --db-name "PRODADW" \
  --cpu-core-count 2 \
  --storage-size-in-tbs 1 \
  --db-workload "ADW"

# Connect with wallet
oci db autonomous-database generate-wallet \
  --autonomous-database-id $DB_OCID \
  --password "WalletPassword123" \
  --file "/path/to/wallet.zip"
```

### Networking (Azure VNet → OCI VCN)

```bash
# List VCNs
oci network vcn list --compartment-id $COMPARTMENT_ID

# Create VCN with CIDR
oci network vcn create \
  --display-name "prod-vcn" \
  --compartment-id $COMPARTMENT_ID \
  --cidr-block "172.16.0.0/16"

# Create subnet with service gateway
oci network subnet create \
  --display-name "app-subnet" \
  --compartment-id $COMPARTMENT_ID \
  --vcn-id $VCN_OCID \
  --cidr-block "172.16.1.0/24" \
  --prohibit-public-ip-on-vnic true

# Create NAT Gateway
oci network nat gateway create \
  --display-name "nat-gateway" \
  --compartment-id $COMPARTMENT_ID \
  --vcn-id $VCN_OCID

# Create Internet Gateway
oci network internet-gateway create \
  --display-name "igw" \
  --compartment-id $COMPARTMENT_ID \
  --vcn-id $VCN_OCID \
  --enabled true

# Create DRG for hybrid connectivity
oci network drg create \
  --display-name "hybrid-drg" \
  --compartment-id $COMPARTMENT_ID
```

### Container (Azure AKS → OCI OKE)

```bash
# List OKE clusters
oci ce cluster list --compartment-id $COMPARTMENT_ID

# Create OKE cluster
oci ce cluster create \
  --display-name "prod-cluster" \
  --compartment-id $COMPARTMENT_ID \
  --vcn-id $VCN_OCID \
  --kubernetes-version "v1.28.2" \
  --service-lb-subnet-ids '["ocid1.subnet.oc1.iad.xxx"]'

# Get kubeconfig
oci ce cluster get-kubeconfig \
  --cluster-id $CLUSTER_OCID \
  --file "$HOME/.kube/config"

# Create node pool with auto-scaling
oci ce node-pool create \
  --display-name "nodepool" \
  --cluster-id $CLUSTER_OCID \
  --compartment-id $COMPARTMENT_ID \
  --node-shape VM.Standard.E4.Flex \
  --size 3 \
  --min-size 1 \
  --max-size 10
```

### IAM (Azure AD → OCI IAM)

```bash
# List users
oci iam user list --compartment-id $COMPARTMENT_ID

# Create user
oci iam user create \
  --name "app-developer" \
  --description "Application developer" \
  --email "dev@company.com"

# Create group
oci iam group create \
  --name "developers" \
  --description "Development team"

# Add user to group
iam group add-user \
  --user-id $USER_OCID \
  --group-id $GROUP_OCID

# Create policy
oci iam policy create \
  --compartment-id $COMPARTMENT_ID \
  --name "dev-policy" \
  --statements '["Allow group developers to manage objects in compartment dev"]'

# Create dynamic group for instances
oci iam dynamic-group create \
  --name "compute-dynamic-group" \
  --matching-rule 'ANY {instance.compartment.id = "ocid1.compartment.oc1.xxx"}'
```

---

## Cloud-to-OCI Mapping Section

| Azure Service | OCI Equivalent | Notes |
|---------------|----------------|-------|
| Azure VM | OCI Compute (VM) | Flex shapes available |
| Azure VM Scale Sets | OCI Instance Pool | Different architecture |
| Azure Blob Storage | OCI Object Storage | Namespace per tenant |
| Azure Files | OCI File Storage | NFS mount |
| Azure SQL | Autonomous Database (ATP) | Auto-patching, auto-backup |
| Azure SQL Managed Instance | OCI Exadata DB System | Enterprise grade |
| Azure Cosmos DB | OCI MongoDB / MySQL | Different data models |
| Azure VNet | VCN (Virtual Cloud Network) | Regional |
| Azure Subnet | OCI Subnet | Regional |
| Azure NSG | OCI Security List + NSG | Two-tier model |
| Azure Private Endpoint | OCI Private Endpoint | Different implementation |
| Azure AD | OCI IAM | Tenancy-based |
| Azure RBAC | OCI IAM Policies | Compartment-based |
| Azure AKS | OCI OKE | Kubernetes managed |
| Azure Functions | OCI Functions | Fn Project based |
| Azure App Service | OCI Container Apps | Serverless containers |
| Azure CDN | OCI CDN | Different providers |
| Azure Application Gateway | OCI Load Balancer | Layer 7 support |
| Azure ExpressRoute | OCI FastConnect | Dedicated connection |
| Azure VPN Gateway | OCI VPN Connect | IPSec tunnel |
| Azure Monitor | OCI Monitoring | Metrics and alarms |
| Azure Log Analytics | OCI Logging | Log groups |

---

## Anti-Patterns Section

**NEVER generate the following in OCI examples:**

### Azure Commands (DO NOT USE)

```bash
# WRONG - Azure CLI commands
az vm list
az storage account create
az sql db show
az aks create
az group show
az ad user list

# NEVER mention in OCI context
az login
az account set
az account show
```

### AWS Commands

```bash
# WRONG - AWS CLI commands
aws ec2 describe-instances
aws s3 cp file.txt s3://bucket/
aws eks create-cluster

# NEVER mention in OCI context
aws configure
```

### GCP Commands

```bash
# WRONG - gcloud commands
gcloud compute instances list
gcloud container clusters create

# NEVER mention in OCI context
gcloud auth login
```

### Common Anti-Patterns

1. **Never mention Azure service names** - Don't say "like Azure Blob", say "OCI Object Storage"
2. **Never use Azure RBAC terminology** - Use OCI IAM policies and compartments
3. **Never suggest Azure Migrate for OCI** - Use OCI Database Migration Service, Data Transfer Service
4. **Never use Azure VNet peer** - Use OCI VCN local peering or remote peering
5. **Never compare Azure region names** - Use OCI region identifiers (us-ashburn-1, etc.)
6. **Never use Azure resource groups** - Use OCI compartments
7. **Never suggest Azure Functions** - Use OCI Functions
8. **Never use Azure ExpressRoute terminology** - Use OCI FastConnect
9. **Never use Azure AD app registration** - Use OCI dynamic groups and instance principal
10. **Never mix Azure and OCI pricing** - Tag all prices with [MUTABLE]

### OCID Format Requirements

Always use proper OCID format in examples:

```bash
# Correct OCID format
ocid1.instance.oc1.iad.abcd1234...
ocid1.bucket.oc1.iad.xyz...
ocid1.vcn.oc1.iad.xyz...
ocid1.autonomousdatabase.oc1.iad.xyz...
ocid1.compartment.oc1.xxx...

# NEVER use
ocid1... (incomplete)
ocid1.* (wildcard)
/subscriptions/xxx (Azure format)
/projects/xxx (GCP format)
```