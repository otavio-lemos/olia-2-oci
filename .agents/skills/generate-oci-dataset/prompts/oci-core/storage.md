# Prompt Template: oci-core/storage

## Context

Generate examples about OCI Storage services including Block Volume, Object Storage, File Storage, and Archive Storage.

## Topics

- Block Volume (performance tiers, clones, backups)
- Object Storage (buckets, versioning, lifecycle)
- File Storage (NFS, mount targets)
- Archive Storage (retention policies)

## Difficulty Distribution

- beginner (30%): Basic bucket/volume creation
- intermediate (50%): Lifecycle policies, performance tuning
- advanced (20%): Multi-region, cross-region replication

## Quality Rules

- Distinguish between Block, Object, and File Storage use cases
- Include specific tier names (Standard, Archive, Cold Archive)
- Tag mutable content (pricing) with [MUTABLE]
- Reference actual OCI service limits

---

## OCID Format

OCI resource identifiers follow this pattern:

```
ocid1.<resource_type>.oc1.<region>.<unique_id>
```

Common storage OCIDs:

| Resource | OCID Pattern | Example |
|----------|--------------|---------|
| Block Volume | `ocid1.volume.oc1.<region>.<unique-id>` | `ocid1.volume.oc1.sa-saopaulo-1.aaaaaaa...` |
| Volume Backup | `ocid1.volumebackup.oc1.<region>.<unique-id>` | `ocid1.volumebackup.oc1.sa-saopaulo-1.bbbbbbb...` |
| Volume Group | `ocid1.volumegroup.oc1.<region>.<unique-id>` | `ocid1.volumegroup.oc1.sa-saopaulo-1.ccccccc...` |
| Object Storage Bucket | N/A (namespace-scoped) | `https://objectstorage.sa-saopaulo-1.oraclecloud.com/n/<namespace>/b/<bucket-name>/o/` |
| File Storage Mount Target | `ocid1.mounttarget.oc1.<region>.<unique-id>` | `ocid1.mounttarget.oc1.sa-saopaulo-1ddddddd...` |
| File System | `ocid1.filesystem.oc1.<region>.<unique-id>` | `ocid1.filesystem.oc1.sa-saopaulo-1.eeeeee...` |
| Archive Storage | N/A (tier within Object Storage) | Same as Object Storage bucket with tier |
| Bucket Replication Policy | `ocid1.replicationpolicy.oc1.<region>.<unique-id>` | `ocid1.replicationpolicy.oc1.sa-saopaulo-1.fffffff...` |

**Region codes**: `sa-saopaulo-1`, `us-ashburn-1`, `us-phoenix-1`, `eu-frankfurt-1`, `ap-tokyo-1`

---

## OCI CLI Syntax

### Block Volume Operations

```bash
# List volume types/configurations
oci bv volume-type list --compartment-id $COMPARTMENT_ID

# Create Block Volume
oci bv volume create \
    --compartment-id $COMPARTMENT_ID \
    --availability-domain "aaaa:sa-saopaulo-1" \
    --display-name "data-volume" \
    --size-in-gbs 100 \
    --vpus-per-gb 10 \
    --backup-policy-id "ocid1.volumebackuppolicy.oc1..."

# Get volume details
oci bv volume get --volume-id $VOLUME_ID

# Update volume (scale up)
oci bv volume update \
    --volume-id $VOLUME_ID \
    --size-in-gbs 200

# Create volume from backup (clone)
oci bv volume create-from-backup \
    --backup-id $BACKUP_ID \
    --display-name "restored-volume"

# List volumes
oci bv volume list --compartment-id $COMPARTMENT_ID
```

### Volume Backups

```bash
# Create volume backup
oci bv backup create \
    --volume-id $VOLUME_ID \
    --display-name "daily-backup" \
    --backup-type "INCREMENTAL"

# List backups
oci bv backup list --volume-id $VOLUME_ID

# Restore from backup
oci bv backup restore \
    --backup-id $BACKUP_ID \
    --volume-id $VOLUME_ID

# Create volume group backup
oci bv backup create \
    --volume-group-id $VOLUME_GROUP_ID \
    --display-name "group-backup"
```

### Object Storage

```bash
# Create bucket
oci os bucket create \
    --namespace $NAMESPACE \
    --name "app-data-bucket" \
    --compartment-id $COMPARTMENT_ID \
    --public-access-type "NoPublicAccess" \
    --storage-tier "Standard" \
    --versioning "Enabled" \
    --object-events-enabled true

# Get bucket details
oci os bucket get --namespace $NAMESPACE --bucket-name $BUCKET_NAME

# Update bucket
oci os bucket update \
    --namespace $NAMESPACE \
    --bucket-name $BUCKET_NAME \
    --versioning "Enabled"

# List buckets
oci os bucket list --compartment-id $COMPARTMENT_ID

# Upload object
oci os object put \
    --namespace $NAMESPACE \
    --bucket-name $BUCKET_NAME \
    --name "data/file.json" \
    --file-path /local/path/file.json \
    --metadata '{"department": "engineering"}'

# Download object
oci os object get \
    --namespace $NAMESPACE \
    --bucket-name $BUCKET_NAME \
    --name "data/file.json" \
    --file-path /local/output/file.json

# List objects
oci os object list \
    --namespace $NAMESPACE \
    --bucket-name $BUCKET_NAME \
    --prefix "data/"
```

### Lifecycle Policies

```bash
# Create lifecycle policy
oci os lifecycle-policy create \
    --namespace $NAMESPACE \
    --compartment-id $COMPARTMENT_ID \
    --display-name "archive-policy" \
    --items '[{"bucketName": "app-data-bucket", "objectNamePrefix": "logs/", "target-bucket": "archive-bucket", "action": "ARCHIVE", "days-value": 30}]'

# List lifecycle policies
oci os lifecycle-policy list --compartment-id $COMPARTMENT_ID

# Update lifecycle policy
oci os lifecycle-policy update \
    --lifecycle-policy-id $POLICY_ID \
    --items '[{"bucketName": "app-data-bucket", "objectNamePrefix": "logs/", "target-bucket": "archive-bucket", "action": "ARCHIVE", "days-value": 60}]'
```

### Cross-Region Replication

```bash
# Create replication policy
oci os replication-policy create \
    --namespace $NAMESPACE \
    --destination-region "us-ashburn-1" \
    --destination-bucket-name "replica-bucket-us" \
    --bucket-name $SOURCE_BUCKET \
    --compartment-id $COMPARTMENT_ID

# List replication policies
oci os replication-policy list \
    --namespace $NAMESPACE \
    --bucket-name $BUCKET_NAME
```

### Archive Storage

```bash
# Create bucket with Archive tier
oci os bucket create \
    --namespace $NAMESPACE \
    --name "archive-bucket" \
    --compartment-id $COMPARTMENT_ID \
    --storage-tier "Archive"

# Restore from archive
oci os object restore \
    --namespace $NAMESPACE \
    --bucket-name $BUCKET_NAME \
    --object-name "archive/backup-2024.tar" \
    --hours 24
```

### File Storage

```bash
# Create file system
oci fs file-system create \
    --compartment-id $COMPARTMENT_ID \
    --display-name "app-file-system" \
    --availability-domain "aaaa:sa-saopaulo-1" \
    --cidr-block 10.0.2.0/24

# Create mount target
oci fs mount-target create \
    --file-system-id $FS_ID \
    --display-name "mount-target" \
    --subnet-id $SUBNET_ID

# Get mount target details (includes export path)
oci fs mount-target get --mount-target-id $MT_ID

# Create export
oci fs export create \
    --file-system-id $FS_ID \
    --mount-target-id $MT_ID \
    --path "/appdata"

# List file systems
oci fs file-system list --compartment-id $COMPARTMENT_ID
```

---

## Anti-Patterns

NEVER generate:

1. **OCID confusion**: Block volumes use `ocid1.volume.oc1...`, File Storage uses `ocid1.filesystem.oc1...`, but Object Storage uses namespace-scoped names (no OCID for bucket)

2. **Wrong storage tier for workload**: Never use Archive tier for frequently accessed data (retrieval takes hours). Never use Standard for archival data (cost inefficient)

3. **Block vs Object vs File confusion**: Never recommend Block for file storage, Object for database storage, or File for unstructured data at scale

4. **Volume cloning without limits**: Never clone volumes across regions - cross-region clone is not supported. Must backup and restore

5. **Volume VPU confusion**: Never recommend lower VPUs (<10) if performance needed. Higher VPUs = better IOPS/throughput. Default is 10 for balanced

6. **Object Storage vs Archive same bucket**: Never mix standard and archive objects in one bucket - use lifecycle policies to move between tiers or separate buckets

7. **Mount target without free IP**: Never create mount target in subnet with insufficient IPs - /24 minimum recommended for File Storage

8. **Replication without permissions**: Never configure replication without ensuring destination compartment has proper policies

9. **Restore before archiving**: Never forget archive restoration can take 1-12 hours - plan ahead

10. **Object listing without pagination**: Never list large buckets without pagination - use `--limit` and `--page` for production