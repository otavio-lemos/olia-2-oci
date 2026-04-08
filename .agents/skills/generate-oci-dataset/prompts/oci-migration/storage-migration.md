# Prompt Template: oci-migration/storage-migration

## Context

Generate examples about OCI storage migration tools and techniques.

## Topics

- OCI Object Storage Sync
- s5cmd tool for fast transfers
- Storage Gateway
- File Storage migration
- Large data transfer best practices
- Transfer pricing and optimization

## Difficulty Distribution

- beginner (30%): Basic storage concepts
- intermediate (50%): Transfer tools configuration
- advanced (20%): Large scale migrations

## Quality Rules

- Include s5cmd command examples
- Reference transfer speeds and limits
- Tag mutable content with [MUTABLE]

---

## OCI CLI Syntax Section

When generating examples, include actual OCI CLI commands:

### Object Storage Operations

```bash
# List buckets
oci os bucket list \
  --namespace-name $NAMESPACE_NAME \
  --compartment-id $COMPARTMENT_ID

# Create bucket with lifecycle policy
oci os bucket create \
  --name "migration-bucket" \
  --namespace-name $NAMESPACE_NAME \
  --compartment-id $COMPARTMENT_ID \
  --public-access-type "NoPublicAccess" \
  --object-lifecycle-policy '[{"action": "ARCHIVE", "days": 180}]'

# Enable versioning
oci os bucket update \
  --bucket-name "migration-bucket" \
  --namespace-name $NAMESPACE_NAME \
  --versioning "Enabled"

# List objects in bucket
oci os object list \
  --bucket-name "migration-bucket" \
  --namespace-name $NAMESPACE_NAME

# Upload single object
oci os object put \
  --namespace-name $NAMESPACE_NAME \
  --bucket-name "migration-bucket" \
  --file "/path/to/data.tar.gz" \
  --object-name "backup/data.tar.gz"

# Upload with multipart
oci os object put \
  --namespace-name $NAMESPACE_NAME \
  --bucket-name "migration-bucket" \
  --file "/path/to/large-file.tar" \
  --part-size 128

# Download object
oci os object get \
  --namespace-name $NAMESPACE_NAME \
  --bucket-name "migration-bucket" \
  --name "backup/data.tar.gz" \
  --file "/tmp/data.tar.gz"
```

### Object Storage Multipart Upload (Large Files)

```bash
# Create multipart upload
oci os multipart create \
  --bucket-name "migration-bucket" \
  --namespace-name $NAMESPACE_NAME \
  --object-name "large-file.tar"

# Upload part
oci os multipart upload \
  --bucket-name "migration-bucket" \
  --namespace-name $NAMESPACE_NAME \
  --object-name "large-file.tar" \
  --upload-id "upload-id-from-create" \
  --part-number 1 \
  --file "/tmp/part1.bin"

# Complete multipart
oci os multipart complete \
  --bucket-name "migration-bucket" \
  --namespace-name $NAMESPACE_NAME \
  --object-name "large-file.tar" \
  --upload-id "upload-id-from-create" \
  --parts '[{"partNumber": 1, "etag": "etag1"}]'
```

### Pre-Authenticated Requests (PAR)

```bash
# Create PAR for downloads
oci os preauth-request create \
  --bucket-name "migration-bucket" \
  --namespace-name $NAMESPACE_NAME \
  --name "download-par" \
  --access-type "ObjectRead" \
  --time-expires "2025-12-31T23:59:59Z"

# Create PAR for uploads
oci os preauth-request create \
  --bucket-name "migration-bucket" \
  --namespace-name $NAMESPACE_NAME \
  --name "upload-par" \
  --access-type "ObjectWrite" \
  --time-expires "2025-12-31T23:59:59Z"

# Create PAR for namespace access
oci os preauth-request create \
  --bucket-name "migration-bucket" \
  --namespace-name $NAMESPACE_NAME \
  --name "list-par" \
  --access-type "AnyObjectRead" \
  --time-expires "2025-12-31T23:59:59Z"
```

### Storage Gateway

```bash
# List storage gateways
oci storage-gateway gateway list --compartment-id $COMPARTMENT_ID

# Create storage gateway
oci storage-gateway gateway create \
  --display-name "migration-gateway" \
  --compartment-id $COMPARTMENT_ID \
  --gateway-type "FILE" \
  --capacity 100TB

# Get gateway details
oci storage-gateway gateway get --gateway-id $GATEWAY_OCID

# List NFS exports
oci storage-gateway nfs-export list --gateway-id $GATEWAY_OCID

# Create NFS export
oci storage-gateway nfs-export create \
  --gateway-id $GATEWAY_OCID \
  --source "/export/path" \
  --client-list '["10.0.0.0/24"]'
```

### File Storage

```bash
# List file systems
oci fs file-system list --compartment-id $COMPARTMENT_ID

# Create file system
oci fs file-system create \
  --display-name "migration-fs" \
  --compartment-id $COMPARTMENT_ID \
  --availability-domain "US-ASHBURN-AD-1" \
  --size 100GB

# Create mount target
oci fs mount-target create \
  --file-system-id $FS_OCID \
  --subnet-id $SUBNET_OCID \
  --display-name "mount-target"

# Get mount command
oci fs mount-target get \
  --mount-target-id $MT_OCID

# Create export
oci fs export create \
  --file-system-id $FS_OCID \
  --mount-target-id $MT_OCID \
  --path "/migration"
```

### Cross-Region Copy

```bash
# Copy object within same region
oci os object put \
  --namespace-name $NAMESPACE_NAME \
  --bucket-name "dest-bucket" \
  --source-uri "https://source-bucket.example.com/file.txt"

# Copy from another OCI tenancy
oci os object put \
  --namespace-name $NAMESPACE_NAME \
  --bucket-name "dest-bucket" \
  --source-uri "https://source-namespace.s3.amazonaws.com/file.txt" \
  --objects-to-copy '[{"name": "file.txt", "source_uri": "https://source.s3.amazonaws.com/file.txt"}]'
```

---

## s5cmd for Fast Transfers

s5cmd is a S3-compatible CLI tool optimized for OCI Object Storage transfers:

```bash
# Install s5cmd
brew install s5cmd  # macOS
# or
go install github.com/peak/s5cmd@latest

# Configure s5cmd for OCI
export S3_ENDPOINT=https://objectstorage.$REGION.oraclecloud.com
export AWS_ACCESS_KEY_ID=$OCI_ACCESS_KEY
export AWS_SECRET_ACCESS_KEY=$OCI_SECRET_KEY
export AWS_REGION=$REGION

# Copy local file to bucket
s5cmd cp /path/to/file.txt s3://migration-bucket/

# Copy with parallel threads
s5cmd cp --jobs 10 /path/to/files/* s3://migration-bucket/

# Sync directory
s5cmd sync /local/folder/ s3://migration-bucket/

# Copy from S3-compatible source
s5cmd cp s3://source-bucket/file.txt s3://migration-bucket/

# List objects
s5cmd ls s3://migration-bucket/
```

### s5cmd Best Practices

| Parameter | Recommendation |
|-----------|----------------|
| --jobs | 10-20 for high bandwidth |
| --part-size | 100MB for large files |
| --storage-class | STANDARD for frequent access |
| --parallel | Enable for multi-file transfers |

---

## Anti-Patterns Section

**NEVER generate the following in OCI examples:**

### Other Cloud Storage Commands (DO NOT USE)

```bash
# WRONG - AWS S3 CLI
aws s3 cp file.txt s3://bucket/
aws s3 sync ./data s3://bucket/
aws s3 mb s3://bucket-name

# WRONG - Azure CLI
az storage blob upload
az storage file upload
az storage account create

# WRONG - GCP gsutil
gsutil cp file.txt gs://bucket/
gsutil rsync ./data gs://bucket/
```

### Common Anti-Patterns

1. **Never use AWS S3 CLI** - Use OCI CLI or s5cmd with OCI endpoints
2. **Never use Azure AzCopy** - Use OCI native tools or s5cmd
3. **Never use GCP gsutil** - Use OCI CLI or s5cmd
4. **Never use S3 URI format for OCI** - Use OCI namespace format
5. **Never skip multipart for large files** - Files > 5GB require multipart
6. **Never use public buckets** - Use proper IAM and PARs
7. **Never ignore transfer pricing** - Tag all costs with [MUTABLE]
8. **Never suggest using other cloud's Data Transfer Service** - Use OCI Transfer Appliance
9. **Never use Glacier terminology** - Use Archive Storage tier
10. **Never skip pre-authenticated requests** - Essential for secure transfers

### OCID Format Requirements

```bash
# Correct OCID format for storage
ocid1.bucket.oc1.iad.xxx...
ocid1.object.oc1.iad.xxx...
ocid1.filesystem.oc1.iad.xxx...
ocid1.mounttarget.oc1.iad.xxx...
ocid1.storagegateway.oc1.iad.xxx...

# Namespace
# Get namespace: oci os ns get
# Format: namespace string (not OCID)
```

---

## Migration Best Practices

### Large Data Transfer Checklist

1. [ ] Create destination bucket with lifecycle policy
2. [ ] Enable versioning for critical data
3. [ ] Use s5cmd with parallel jobs for speed
4. [ ] Implement multipart for files > 100MB
5. [ ] Set up pre-authenticated requests for secure access
6. [ ] Use Transfer Appliance for >20TB [MUTABLE]
7. [ ] Monitor progress with Object Storage metrics
8. [ ] Validate checksums after transfer

### Transfer Speed Optimization

| Data Size | Recommended Tool | Expected Speed |
|-----------|------------------|----------------|
| < 1 TB | OCI CLI + s5cmd | ~100 Mbps |
| 1-20 TB | s5cmd parallel | ~500 Mbps |
| > 20 TB | Transfer Appliance | [MUTABLE] varies |

---

## Example Workflow

```bash
# 1. Get namespace
NAMESPACE=$(oci os ns get --raw-output)

# 2. Create bucket
oci os bucket create \
  --name "migration-bucket" \
  --namespace-name $NAMESPACE \
  --compartment-id $COMPARTMENT_ID

# 3. Upload with s5cmd
export S3_ENDPOINT=https://objectstorage.us-ashburn-1.oraclecloud.com
s5cmd cp --jobs 20 /data/* s3://migration-bucket/

# 4. Verify upload
oci os object list --bucket-name migration-bucket --namespace-name $NAMESPACE
```