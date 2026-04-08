# Prompt Template: oci-migration/oracle-to-oci

## Context

Generate examples about migrating from Oracle Cloud Classic (OCC) to OCI.

## Topics

- Oracle Cloud Classic → OCI migration
- Oracle E-Business Suite (EBS) → OCI
- PeopleSoft → OCI
- JD Edwards → OCI
- Oracle Fusion Applications → OCI
- Migration strategies

## Difficulty Distribution

- beginner (20%): Basic migration concepts
- intermediate (50%): Application migration patterns
- advanced (30%): Complex enterprise migrations

## Quality Rules

- Include specific migration paths
- Reference Oracle migration tools
- Tag mutable content with [MUTABLE]

---

## OCI CLI Syntax Section

When generating examples, include actual OCI CLI commands:

### Compute Migration

```bash
# List existing instances
oci compute instance list --compartment-id $COMPARTMENT_ID

# Create replacement instance in OCI
oci compute instance launch \
  --display-name "prod-app-server" \
  --compartment-id $COMPARTMENT_ID \
  --availability-domain "US-ASHBURN-AD-1" \
  --image-id ocid1.image.oc1.iad.xxx \
  --shape VM.Standard.E4.Flex \
  --shape-config '{"ocpus": 4, "memoryInGBs": 32}' \
  --subnet-id ocid1.subnet.oc1.iad.xxx

# Create custom image from export
oci compute image import \
  --display-name "custom-ebs-image" \
  --compartment-id $COMPARTMENT_ID \
  --source-image-type "QCOW2" \
  --input-source-uri "https://objectstorage.us-ashburn-1.oraclecloud.com/n/namespace/b/custom-images/ebs.qcow2"

# Create instance from custom image
oci compute instance launch \
  --display-name "ebs-server" \
  --image-id $CUSTOM_IMAGE_OCID
```

### Database Migration

```bash
# Create Autonomous Database
oci db autonomous-database create \
  --display-name "ebs-prod-db" \
  --compartment-id $COMPARTMENT_ID \
  --db-name "EBSPROD" \
  --cpu-core-count 4 \
  --storage-size-in-tbs 2 \
  --license-model "LICENSE_INCLUDED" \
  --db-workload "ATP"

# Create Exadata DB System
oci db system create \
  --display-name "fusion-db" \
  --compartment-id $COMPARTMENT_ID \
  --system-shape "EXACC" \
  --db-version "19c" \
  --cpu-core-count 16 \
  --storage-size-in-tbs 64

# Generate wallet
oci db autonomous-database generate-wallet \
  --autonomous-database-id $ADB_OCID \
  --password "SecurePassword123" \
  --file "/path/to/wallet.zip"

# Database Migration Service
oci databasemigration migration create \
  --display-name "occ-migration" \
  --compartment-id $COMPARTMENT_ID \
  --source-database-type "ORACLE" \
  --target-autonomous-database-id $ADB_OCID \
  --migration-type "ONLINE"
```

### Networking

```bash
# Create VCN for migration
oci network vcn create \
  --display-name "migration-vcn" \
  --compartment-id $COMPARTMENT_ID \
  --cidr-block "10.0.0.0/16"

# Create subnets
oci network subnet create \
  --display-name "app-tier" \
  --compartment-id $COMPARTMENT_ID \
  --vcn-id $VCN_OCID \
  --cidr-block "10.0.1.0/24"

oci network subnet create \
  --display-name "db-tier" \
  --compartment-id $COMPARTMENT_ID \
  --vcn-id $VCN_OCID \
  --cidr-block "10.0.2.0/24"

# Create DRG for hybrid connectivity
oci network drg create \
  --display-name "migration-drg" \
  --compartment-id $COMPARTMENT_ID

# Attach DRG to VCN
oci network drg-attachment create \
  --drg-id $DRG_OCID \
  --vcn-id $VCN_OCID
```

### Oracle E-Business Suite Specific

```bash
# Create EBS-compatible database
oci db system create \
  --display-name "ebs-db" \
  --compartment-id $COMPARTMENT_ID \
  --system-shape "VM.Standard2.16" \
  --db-version "19c" \
  --cpu-core-count 16 \
  --storage-size-in-tbs 128

# Upload EBS R12 image
oci compute image create \
  --display-name "ebs-r12-image" \
  --compartment-id $COMPARTMENT_ID \
  --image-source-uri "https://objectstorage.region.oraclecloud.com/n/namespace/b/custom/ebs-r12.qcow2"

# Configure EBS applications tier
oci compute instance launch \
  --display-name "ebs-apps" \
  --image-id $EBS_IMAGE_OCID \
  --shape VM.Standard.E4.Flex

# Set up block storage for EBS data
oci bv volume create \
  --display-name "ebs-data" \
  --compartment-id $COMPARTMENT_ID \
  --availability-domain "US-ASHBURN-AD-1" \
  --size-in-gbs 1024

oci bv volume-attachment attach \
  --instance-id $INSTANCE_OCID \
  --volume-id $VOLUME_OCID
```

### PeopleSoft/ JD Edwards Specific

```bash
# Create PeopleSoft database on Exadata
oci db system create \
  --display-name "peoplesoft-db" \
  --compartment-id $COMPARTMENT_ID \
  --system-shape "EXACC" \
  --db-version "19c" \
  --cpu-core-count 8 \
  --storage-size-in-tbs 32

# Create app tier compute
oci compute instance launch \
  --display-name "psft-app" \
  --compartment-id $COMPARTMENT_ID \
  --shape VM.Standard.E4.Flex \
  --image-id ocid1.image.oc1.iad.xxx

# Configure shared file system for PS_HOME
oci fs file-system create \
  --display-name "psft-shared" \
  --compartment-id $COMPARTMENT_ID \
  --availability-domain "US-ASHBURN-AD-1" \
  --size 500GB

oci fs mount-target create \
  --file-system-id $FS_OCID \
  --subnet-id $SUBNET_OCID
```

### Fusion Applications Migration

```bash
# Create Fusion Database (Exadata)
oci db system create \
  --display-name "fusion-db-prod" \
  --compartment-id $COMPARTMENT_ID \
  --system-shape "EXACC" \
  --db-version "19c" \
  --cpu-core-count 24 \
  --storage-size-in-tbs 128

# Configure auto-scaling
oci db system update \
  --system-id $EXACC_OCID \
  --auto-scaling-enabled true \
  --auto-scaling-core-count 32

# Create identity domain
oci identity domain create \
  --display-name "fusion-idp" \
  --compartment-id $COMPARTMENT_ID

# Configure OCI IAM for Fusion
oci iam policy create \
  --compartment-id $COMPARTMENT_ID \
  --name "fusion-admin-policy" \
  --statements '["Allow group fusion-admins to manage all-resources in compartment fusion"]'
```

---

## Migration Strategies

### Lift-and-Shift (Quickest)

```bash
# 1. Export VM images from OCC
# 2. Import as custom images in OCI
oci compute image import \
  --display-name "legacy-app" \
  --compartment-id $COMPARTMENT_ID \
  --source-image-type "QCOW2" \
  --input-source-uri "https://objectstorage.region.oraclecloud.com/n/namespace/b/images/app.qcow2"

# 3. Launch instances from custom images
oci compute instance launch \
  --display-name "migrated-app" \
  --image-id $CUSTOM_IMAGE_OCID

# 4. Attach storage
oci bv volume-attachment attach --instance-id $INSTANCE_OCID --volume-id $VOLUME_OCID
```

### Re-Architect (Modernize)

```bash
# 1. Create OKE cluster
oci ce cluster create \
  --display-name "modern-app" \
  --compartment-id $COMPARTMENT_ID \
  --kubernetes-version "v1.28.2"

# 2. Create container registry
oci artifacts container repository create \
  --display-name "fusion-apps"

# 3. Deploy to OKE
kubectl apply -f kubernetes/deployment.yaml

# 4. Create API Gateway
oci apigateway api create \
  --display-name "app-api" \
  --compartment-id $COMPARTMENT_ID
```

### Hybrid Approach

```bash
# 1. Keep core database on Exadata
oci db system create --display-name "core-db" --system-shape "EXACC"

# 2. Migrate app tier to OKE
oci ce cluster create --display-name "app-cluster"

# 3. Connect via private endpoint
oci network private-endpoint create \
  --display-name "app-db-pe" \
  --vcn-id $VCN_OCID \
  --subnet-id $SUBNET_OCID \
  --target-db-ids '["ocid1.dbsystem.oc1.xxx"]'
```

---

## Oracle Cloud Classic → OCI Mapping

| OCC Service | OCI Equivalent | Notes |
|-------------|----------------|-------|
| OCI Compute Classic | OCI Compute | Different shapes |
| OCI DBaaS | Exadata/Autonomous | Migration tools available |
| OCI Storage Classic | Object Storage | Different API |
| OCI Network Classic | VCN + DRG | Regional |
| Oracle Identity Cloud | OCI IAM | Different architecture |
| Java Cloud Service | OCI Container Instances | Container-based |
| SOA Cloud Service | OCI Integration | Different service |
| Oracle Mobile Cloud | OCI Mobile | Different offering |

---

## Anti-Patterns Section

**NEVER generate the following in OCI examples:**

### Legacy Oracle Commands

```bash
# WRONG - OCC commands (do not use in OCI context)
opcctl status
oracle-cli compute instance list
dbaascli dbbackup list

# NEVER mention
opc (OPC user)
java cloud service console
```

### Other Cloud Migration Tools

```bash
# WRONG - AWS migration
aws sms connect

# WRONG - Azure migration
azmigrate assess

# WRONG - GCP migration
gcloud migrate center
```

### Common Anti-Patterns

1. **Never use OCC CLI** - Use OCI CLI
2. **Never use Oracle Cloud Infrastructure Classic** - Use OCI Gen 2/3
3. **Never use OPC user format** - Use IAM users/groups
4. **Never suggest legacy Java Cloud Service** - Use OKE or Container Instances
5. **Never use DBaaS CLI** - Use OCI DB commands
6. **Never use Storage Classic** - Use Object Storage
7. **Never ignore OCID format** - All resources use ocid1.* format
8. **Never suggest manual database export** - Use Database Migration Service
9. **Never use Oracle Cloud Console** - Refer to OCI Console
10. **Never mix OCC and OCI architectures** - VCNs are regional, not global

### OCID Format Requirements

```bash
# Correct OCID format
ocid1.instance.oc1.iad.xxx...
ocid1.dbsystem.oc1.iad.xxx...
ocid1.autonomousdatabase.oc1.iad.xxx...
ocid1.vcn.oc1.iad.xxx...
ocid1.subnet.oc1.iad.xxx...
ocid1.cluster.oc1.iad.xxx...

# NEVER use
ocid1.compartment.oc1..xxx (double dot)
opc://resource (OPC format)
/identity/domains/xxx (OCC format)
```

---

## EBS Migration Checklist

```bash
# Phase 1: Assessment
# - Document current EBS version
# - Identify customizations
# - Map dependencies

# Phase 2: Database Migration
# - Create target Exadata
# - Use Database Migration Service
# - Validate data integrity

# Phase 3: Application Tier
# - Export custom images
# - Import to OCI
# - Configure compute instances

# Phase 4: Integration
# - Configure networking
# - Set up Load Balancer
# - Configure DNS

# Phase 5: Validation
# - Test all workflows
# - Verify integrations
# - Performance testing [MUTABLE]
```

## PeopleSoft Migration Checklist

```bash
# Phase 1: Database
# - Export PeopleSoft DB
# - Create Exadata target
# - Import with Data Pump

# Phase 2: Application Servers
# - Create app tier compute
# - Configure PS_HOME on File Storage
# - Set up Process Scheduler

# Phase 3: Web Tier
# - Configure WebLogic on OCI
# - Set up OHS (Oracle HTTP Server)
# - Configure web entry points

# Phase 4: Integration
# - Connect to OCI integrations
# - Configure single sign-on
# - Test all interfaces
```

## Fusion Applications Migration

```bash
# 1. Request Oracle SaaS Migration Service
# Contact Oracle for guided migration

# 2. Identity Migration
oci identity domain create --display-name "fusion-domain"
oci iam group create --display-name "fusion-users"

# 3. Database Migration
oci db system create --display-name "fusion-db" --system-shape "EXACC"
oci databasemigration migration create

# 4. Application Deployment
# Oracle-managed migration
# Work with Oracle Support
```