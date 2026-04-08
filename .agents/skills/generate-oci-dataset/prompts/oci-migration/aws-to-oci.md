# Prompt Template: oci-migration/aws-to-oci

## Context

Generate examples about migrating from AWS to OCI.

## Topics

- EC2 → OCI Compute mapping
- S3 → Object Storage mapping
- RDS → Autonomous Database mapping
- VPC → VCN mapping
- IAM role mapping
- EKS → OKE mapping
- RDS → OCI Database

## Difficulty Distribution

- beginner (30%): Basic service mapping
- intermediate (40%): Network migration, IAM mapping
- advanced (30%): Complex migrations, hybrid architectures

## Quality Rules

- Always include AWS → OCI mapping
- Explain differences between services
- Include specific OCI service names
- Mention migration strategies (lift-and-shift, re-architect)
- Tag mutable content with [MUTABLE]

---

## OCI CLI Syntax Section

When generating examples, include actual OCI CLI commands:

### Compute (EC2 → OCI Compute)

```bash
# List compute instances
oci compute instance list --compartment-id $COMPARTMENT_ID

# Create instance from image
oci compute instance launch \
  --display-name "prod-web-server" \
  --compartment-id $COMPARTMENT_ID \
  --availability-domain "US-ASHBURN-AD-1" \
  --image-id ocid1.image.oc1.iad.xxx \
  --shape VM.Standard.E4.Flex \
  --subnet-id ocid1.subnet.oc1.iad.xxx

# Get instance details
oci compute instance get --instance-id $INSTANCE_ID
```

### Object Storage (S3 → OCI Object Storage)

```bash
# List buckets
oci os bucket list --namespace-name $NAMESPACE_NAME --compartment-id $COMPARTMENT_ID

# Create bucket
oci os bucket create \
  --name "migration-bucket" \
  --namespace-name $NAMESPACE_NAME \
  --compartment-id $COMPARTMENT_ID \
  --public-access-type "NoPublicAccess"

# Upload object
oci os object put \
  --namespace-name $NAMESPACE_NAME \
  --bucket-name "migration-bucket" \
  --file "/path/to/file.tar.gz" \
  --name "backup/file.tar.gz"

# Copy object (cross-region)
oci os object put \
  --namespace-name $NAMESPACE_NAME \
  --bucket-name "dest-bucket" \
  --source-uri "https://source-bucket.s3.amazonaws.com/file.txt"
```

### Database (RDS → OCI Autonomous Database)

```bash
# List autonomous databases
oci db autonomous-database list --compartment-id $COMPARTMENT_ID

# Create Autonomous Database
oci db autonomous-database create \
  --display-name "prod-db" \
  --compartment-id $COMPARTMENT_ID \
  --db-name "PRODDB" \
  --cpu-core-count 2 \
  --storage-size-in-tbs 1 \
  --license-model "LICENSE_INCLUDED"

# Restore database
oci db autonomous-database restore \
  --autonomous-database-id $DB_OCID \
  --timestamp "2024-01-15T00:00:00Z"
```

### Networking (VPC → VCN)

```bash
# List VCNs
oci network vcn list --compartment-id $COMPARTMENT_ID

# Create VCN
oci network vcn create \
  --display-name "prod-vcn" \
  --compartment-id $COMPARTMENT_ID \
  --cidr-block "10.0.0.0/16"

# Create subnet
oci network subnet create \
  --display-name "web-subnet" \
  --compartment-id $COMPARTMENT_ID \
  --vcn-id $VCN_OCID \
  --cidr-block "10.0.1.0/24" \
  --security-list-ids '["ocid1.securitylist.oc1.xxx"]'

# List security lists
oci network security-list list --vcn-id $VCN_OCID

# Create security rule
oci network security-list update \
  --security-list-id $SECURITY_LIST_OCID \
  --egress-security-rules '[{"destination": "0.0.0.0/0", "protocol": "6", "tcp-options": {"destinationPortRange": {"max": 443, "min": 443}}}]'
```

### Container (EKS → OKE)

```bash
# List OKE clusters
oci ce cluster list --compartment-id $COMPARTMENT_ID

# Get kubeconfig
oci ce cluster get-kubeconfig \
  --cluster-id $CLUSTER_OCID \
  --file "$HOME/.kube/config"

# Create node pool
oci ce node-pool create \
  --display-name "prod-nodepool" \
  --cluster-id $CLUSTER_OCID \
  --compartment-id $COMPARTMENT_ID \
  --node-shape VM.Standard.E4.Flex \
  --node-source-source-type "Image" \
  --node-image-id ocid1.image.oc1.iad.xxx \
  --size 3
```

### IAM (IAM Role → OCI IAM)

```bash
# List dynamic groups
iam dynamic-group list --compartment-id $COMPARTMENT_ID

# Create policy
iam policy create \
  --compartment-id $COMPARTMENT_ID \
  --name "compute-admin" \
  --statements '["Allow group compute-admins to manage instances in compartment prod"]'

# List users
iam user list --compartment-id $COMPARTMENT_ID
```

---

## Cloud-to-OCI Mapping Section

| AWS Service | OCI Equivalent | Notes |
|-------------|----------------|-------|
| EC2 | OCI Compute (Virtual Machines) | Shapes, not instance types |
| EC2 Auto Scaling | OCI Instance Pool + Instance Configuration | Different architecture |
| RDS | Autonomous Database (ATP/ADW) or DB Systems | MySQL, PostgreSQL, Oracle supported |
| S3 | OCI Object Storage | Namespace = S3 bucket name |
| Glacier | OCI Archive Storage | Tiered storage |
| VPC | VCN (Virtual Cloud Network) | Regional, not global |
| Subnet | OCI Subnet | Regional |
| Security Group | OCI Security List + NSG | Different model |
| IAM Role | OCI Dynamic Group + Policy | Instance principal |
| EKS | OKE (Oracle Kubernetes Engine) | Fully managed K8s |
| Lambda | OCI Functions | Fn Project based |
| CloudFront | OCI CDN | Different provider |
| Route 53 | OCI DNS | Zone management |
| ELB | OCI Load Balancer | Regional |
| CloudWatch | OCI Monitoring + Logging | Different service |
| CloudFormation | Resource Manager (Terraform) | IaC approach |
| EBS | Block Volume | Attach to compute |
| EFS | File Storage | NFS mount |
| SES | Email Delivery | Different service |

---

## Anti-Patterns Section

**NEVER generate the following in OCI examples:**

### AWS Commands (DO NOT USE)

```bash
# WRONG - AWS CLI commands
aws ec2 describe-instances
aws s3 cp file.txt s3://bucket/
aws rds describe-db-instances
aws eks create-cluster
aws iam get-role
aws lambda invoke

# NEVER mention in OCI context
aws configure
aws sts assume-role
```

### Azure Commands

```bash
# WRONG - Azure CLI commands
az vm list
az storage account create
az sql db show
az aks create
az group show

# NEVER mention in OCI context
az login
az account set
```

### GCP Commands

```bash
# WRONG - gcloud commands
gcloud compute instances list
gcloud storage buckets list
gcloud sql instances list
gcloud container clusters create

# NEVER mention in OCI context
gcloud auth login
gcloud config set project
```

### Common Anti-Patterns

1. **Never mention AWS/Azure/GCP service names** - Don't say "like AWS S3", say "OCI Object Storage"
2. **Never suggest using cloud-native migration tools from other clouds** - Use OCI native tools
3. **Never use other cloud's IAM terminology** - Use OCI IAM terms (compartments, policies, dynamic groups)
4. **Never suggest cross-cloud networking** - VCNs are regional, not global like AWS global VPC
5. **Never mix pricing models** - Don't compare prices directly, use [MUTABLE] tag
6. **Never suggest using Terraform with AWS provider** - Must use OCI provider
7. **Never use Kubernetes terms from other clouds** - Use OKE, not EKS/GKE
8. **Never reference region names from other clouds** - Use OCI region identifiers (us-ashburn-1, etc.)
9. **Never use S3 bucket ARN format** - Use OCI Object Storage namespace format
10. **Never use EC2 instance type naming** - Use OCI shapes (VM.Standard.E4.Flex)

### OCID Format Requirements

Always use proper OCID format in examples:

```bash
# Correct OCID format
ocid1.instance.oc1.iad.abcd1234...
ocid1.bucket.oc1.iad.xyz...
ocid1.vcn.oc1.iad.xyz...
ocid1.autonomousdatabase.oc1.iad.xyz...

# NEVER use
ocid1... (incomplete)
ocid1.* (wildcard)
resource-id (non-OCID format)
```