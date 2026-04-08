# Prompt Template: oci-migration/gcp-to-oci

## Context

Generate examples about migrating from GCP to OCI.

## Topics

- Compute Engine → OCI Compute
- Cloud Storage → Object Storage
- Cloud SQL → Autonomous Database
- VPC → VCN mapping
- IAM mapping
- GKE → OKE

## Difficulty Distribution

- beginner (30%): Basic service mapping
- intermediate (40%): Network migration
- advanced (30%): Complex migrations

## Quality Rules

- Always include GCP → OCI mapping
- Explain differences between services
- Tag mutable content with [MUTABLE]

---

## OCI CLI Syntax Section

When generating examples, include actual OCI CLI commands:

### Compute (GCP Compute Engine → OCI Compute)

```bash
# List compute instances
oci compute instance list --compartment-id $COMPARTMENT_ID

# Create instance with custom shape
oci compute instance launch \
  --display-name "prod-server" \
  --compartment-id $COMPARTMENT_ID \
  --availability-domain "US-ASHBURN-AD-1" \
  --image-id ocid1.image.oc1.iad.xxx \
  --shape VM.Standard.E4.Flex \
  --shape-config '{"ocpus": 2, "memoryInGBs": 16}' \
  --subnet-id ocid1.subnet.oc1.iad.xxx

# Create GPU instance
oci compute instance launch \
  --display-name "gpu-server" \
  --compartment-id $COMPARTMENT_ID \
  --shape VM.GPU3.8 \
  --image-id ocid1.image.oc1.iad.xxx

# List images
oci compute image list --compartment-id $COMPARTMENT_ID
```

### Object Storage (GCP Cloud Storage → OCI Object Storage)

```bash
# List buckets
oci os bucket list --namespace-name $NAMESPACE_NAME --compartment-id $COMPARTMENT_ID

# Create bucket with lifecycle policy
oci os bucket create \
  --name "migration-bucket" \
  --namespace-name $NAMESPACE_NAME \
  --compartment-id $COMPARTMENT_ID \
  --versioning "Enabled" \
  --object-lifecycle-policy '[{"action": "ARCHIVE", "days": 90}]'

# Upload object with encryption
oci os object put \
  --namespace-name $NAMESPACE_NAME \
  --bucket-name "migration-bucket" \
  --file "/path/to/data.tar.gz" \
  --encryption-key "base64-encoded-key"

# Create pre-authenticated request
oci os preauth-request create \
  --bucket-name "migration-bucket" \
  --namespace-name $NAMESPACE_NAME \
  --name "upload-par" \
  --access-type "ObjectWrite" \
  --time-expires "2024-12-31T23:59:59Z"

# Copy from URL (cross-cloud)
oci os object put \
  --namespace-name $NAMESPACE_NAME \
  --bucket-name "dest-bucket" \
  --source-uri "https://storage.googleapis.com/source-bucket/file.txt"
```

### Database (GCP Cloud SQL → OCI Autonomous Database)

```bash
# List autonomous databases
oci db autonomous-database list --compartment-id $COMPARTMENT_ID

# Create Autonomous Transaction Processing
oci db autonomous-database create \
  --display-name "prod-atp" \
  --compartment-id $COMPARTMENT_ID \
  --db-name "PRODDB" \
  --cpu-core-count 4 \
  --storage-size-in-tbs 2 \
  --license-model "BRING_YOUR_OWN_LICENSE" \
  --db-workload "ATP"

# Create dedicated infrastructure
oci db autonomous-database create \
  --display-name "dedicated-atp" \
  --compartment-id $COMPARTMENT_ID \
  --db-name "PRODDB" \
  --cpu-core-count 4 \
  --db-workload "ATP" \
  --dedicated-instance-domain "dedicated-domain"

# Enable auto-scaling
oci db autonomous-database update \
  --autonomous-database-id $DB_OCID \
  --auto-scaling-enabled true \
  --auto-scaling-max-cpu-core-count 8

# Generate connection string
oci db autonomous-database get \
  --autonomous-database-id $DB_OCID | jq '.["connection_strings"]'
```

### Networking (GCP VPC → OCI VCN)

```bash
# List VCNs
oci network vcn list --compartment-id $COMPARTMENT_ID

# Create VCN with multiple CIDR blocks
oci network vcn create \
  --display-name "prod-vcn" \
  --compartment-id $COMPARTMENT_ID \
  --cidr-block "192.168.0.0/16"

# Create subnet with route table
oci network subnet create \
  --display-name "private-subnet" \
  --compartment-id $COMPARTMENT_ID \
  --vcn-id $VCN_OCID \
  --cidr-block "192.168.1.0/24" \
  --route-table-id $ROUTE_TABLE_OCID

# Create route table
oci network route-table create \
  --display-name "private-rt" \
  --compartment-id $COMPARTMENT_ID \
  --vcn-id $VCN_OCID \
  --route-rules '[{"destination": "0.0.0.0/0", "network_entity_id": "ocid1.internetgateway.oc1.xxx"}]'

# Create private endpoint for database
oci network private-endpoint create \
  --display-name "db-pe" \
  --compartment-id $COMPARTMENT_ID \
  --vcn-id $VCN_OCID \
  --subnet-id $SUBNET_OCID \
  --target-db-ids '["ocid1.autonomousdatabase.oc1.xxx"]'

# Create service gateway for Object Storage access
oci network service-gateway create \
  --display-name "sgw" \
  --compartment-id $COMPARTMENT_ID \
  --vcn-id $VCN_OCID \
  --services '[{"service_id": "ocid1.service.oc1.iad.xxx"}]'
```

### Container (GCP GKE → OCI OKE)

```bash
# List OKE clusters
oci ce cluster list --compartment-id $COMPARTMENT_ID

# Create OKE cluster with private endpoints
oci ce cluster create \
  --display-name "prod-oke" \
  --compartment-id $COMPARTMENT_ID \
  --vcn-id $VCN_OCID \
  --kubernetes-version "v1.28.2" \
  --endpoint-config '{"is_public_ip_enabled": false, "subnet_id": "ocid1.subnet.oc1.iad.xxx"}' \
  --service-lb-subnet-ids '["ocid1.subnet.oc1.iad.xxx"]'

# Get kubeconfig
oci ce cluster get-kubeconfig \
  --cluster-id $CLUSTER_OCID \
  --file "$HOME/.kube/config"

# Create node pool with node labels
oci ce node-pool create \
  --display-name "prod-nodepool" \
  --cluster-id $CLUSTER_OCID \
  --compartment-id $COMPARTMENT_ID \
  --node-shape VM.Standard.E4.Flex \
  --size 3 \
  --node-labels '{"environment": "production"}'

# Add-ons for cluster
oci ce cluster create \
  --display-name "oke-with-addons" \
  --compartment-id $COMPARTMENT_ID \
  --vcn-id $VCN_OCID \
  --add-ons '{"kubernetes_network_policy": true, "kubeconfig_content_type": "text"}'
```

### IAM (GCP IAM → OCI IAM)

```bash
# List users
oci iam user list --compartment-id $COMPARTMENT_ID

# Create user
oci iam user create \
  --name "developer" \
  --description "Application developer" \
  --email "dev@company.com"

# Create group
oci iam group create \
  --name "app-developers" \
  --description "Application development team"

# Add user to group
iam group add-user \
  --user-id $USER_OCID \
  --group-id $GROUP_OCID

# Create policy with conditions
oci iam policy create \
  --compartment-id $COMPARTMENT_ID \
  --name "dev-policy" \
  --statements '["Allow group app-developers to manage instance-family in compartment dev where request.timestamp < \"2025-01-01T00:00:00Z\""]'

# Create dynamic group for compute
oci iam dynamic-group create \
  --name "compute-dynamic-group" \
  --matching-rule 'ANY {instance.compartment.id = "ocid1.compartment.oc1.xxx", instance.state = "RUNNING"}'

# List policies
oci iam policy list --compartment-id $COMPARTMENT_ID
```

---

## Cloud-to-OCI Mapping Section

| GCP Service | OCI Equivalent | Notes |
|-------------|----------------|-------|
| Compute Engine | OCI Compute | Flex shapes with custom CPU/memory |
| GCE Preemptible VM | OCI Preemptible Instances | Different pricing model |
| GKE | OCI OKE | Fully managed Kubernetes |
| Cloud Storage | OCI Object Storage | Namespace per tenant |
| Cloud Storage Nearline | OCI Object Storage Infrequent Access | Tiered storage |
| Cloud Storage Coldline | OCI Object Storage Archive | Long-term retention |
| Cloud SQL | Autonomous Database (ATP) | Auto-patching, auto-backup |
| Cloud Spanner | OCI Exadata Cloud Service | Distributed database |
| BigQuery | OCI Operations Insights | Different service |
| VPC Network | VCN (Virtual Cloud Network) | Regional |
| Shared VPC | OCI VCN with IAM | Compartment-based |
| Cloud IAM | OCI IAM | Policy-based |
| Cloud IAM Roles | OCI IAM Policies | Compartment-scoped |
| Cloud Load Balancing | OCI Load Balancer | Regional |
| Cloud CDN | OCI CDN | Different providers |
| Cloud NAT | OCI NAT Gateway | Same functionality |
| Cloud Router | OCI DRG + Route Table | Hybrid connectivity |
| Cloud Armor | OCI WAF | Web application firewall |
| Cloud Scheduler | OCI Scheduler | Cron-based jobs |
| Cloud Functions | OCI Functions | Fn Project based |
| Cloud Run | OCI Container Instances | Serverless containers |
| Cloud Monitoring | OCI Monitoring | Metrics and alarms |
| Cloud Logging | OCI Logging | Centralized logging |
| Cloud Armor | OCI WAF | Security |
| Apigee | OCI API Gateway | API management |

---

## Anti-Patterns Section

**NEVER generate the following in OCI examples:**

### GCP Commands (DO NOT USE)

```bash
# WRONG - gcloud commands
gcloud compute instances list
gcloud storage buckets list
gcloud sql instances list
gcloud container clusters create
gcloud iam service-accounts list

# NEVER mention in OCI context
gcloud auth login
gcloud config set project
gcloud projects list
```

### AWS Commands

```bash
# WRONG - AWS CLI commands
aws ec2 describe-instances
aws s3 ls

# NEVER mention in OCI context
aws configure
```

### Azure Commands

```bash
# WRONG - Azure CLI commands
az vm list
az storage account list

# NEVER mention in OCI context
az login
```

### Common Anti-Patterns

1. **Never mention GCP service names** - Don't say "like GKE", say "OCI OKE"
2. **Never use GCP project terminology** - Use OCI compartments
3. **Never use GCP IAM roles** - Use OCI IAM policies
4. **Never suggest Google Migrate for Compute Engine** - Use OCI native migration tools
5. **Never use GCP VPC global network** - OCI VCNs are regional
6. **Never reference GCP region names** - Use OCI region identifiers (us-ashburn-1, etc.)
7. **Never use Cloud SQL terminology** - Use Autonomous Database
8. **Never use preemptible instances pricing** - Use OCI preemptible or on-demand
9. **Never use BigQuery** - OCI has different analytics services
10. **Never use Apigee terminology** - Use OCI API Gateway

### OCID Format Requirements

Always use proper OCID format in examples:

```bash
# Correct OCID format
ocid1.instance.oc1.iad.abcd1234...
ocid1.bucket.oc1.iad.xyz...
ocid1.vcn.oc1.iad.xyz...
ocid1.autonomousdatabase.oc1.iad.xyz...
ocid1.cluster.oc1.iad.xyz...

# NEVER use
projects/my-project/... (GCP format)
projects/my-project/zones/us-central1/... (GCP format)
resource-id (non-OCID format)
ocid1... (incomplete)
```

---

## Migration Strategy Examples

### Lift-and-Shift (Direct Migration)

```bash
# 1. Create matching VCN
oci network vcn create --display-name "prod-vcn" --cidr-block "10.0.0.0/16"

# 2. Create subnets
oci network subnet create --display-name "web-subnet" --cidr-block "10.0.1.0/24"
oci network subnet create --display-name "db-subnet" --cidr-block "10.0.2.0/24"

# 3. Launch compute instances
oci compute instance launch --display-name "web-1" --shape VM.Standard.E4.Flex
```

### Re-Architect (Cloud-Native)

```bash
# 1. Create Autonomous Database
oci db autonomous-database create --db-name "PRODDB" --cpu-core-count 2

# 2. Create OKE cluster
oci ce cluster create --display-name "prod-cluster" --kubernetes-version "v1.28"

# 3. Deploy application containers
kubectl apply -f deployment.yaml
```