# Prompt Template: oci-core/database

## Context

Generate examples about OCI Database services including Autonomous Database, MySQL, PostgreSQL, and Exadata.

## Topics

- Autonomous Database (ATP, ADW)
- MySQL HeatWave
- PostgreSQL
- Exadata
- Backups, patching, scaling

## Difficulty Distribution

- beginner (30%): Basic database creation
- intermediate (50%): Backup strategies, scaling
- advanced (20%): Exadata, performance tuning

## Quality Rules

- Distinguish ATP vs ADW use cases
- Include specific OCI resource names
- Tag mutable content (pricing, limits) with [MUTABLE]

---

## OCID Format

OCI resource identifiers follow this pattern:

```
ocid1.<resource_type>.oc1.<region>.<unique_id>
```

Common database OCIDs:

| Resource | OCID Pattern | Example |
|----------|--------------|---------|
| Autonomous Database | `ocid1.autonomousdatabase.oc1.<region>.<unique-id>` | `ocid1.autonomousdatabase.oc1.sa-saopaulo-1.aaaaaaa...` |
| Autonomous Container Database | `ocid1.autonomouscontainerdatabase.oc1.<region>.<unique-id>` | `ocid1.autonomouscontainerdatabase.oc1.sa-saopaulo-1.bbbbbbb...` |
| Autonomous VM Cluster | `ocid1.autonomousvmcluster.oc1.<region>.<unique-id>` | `ocid1.autonomousvmcluster.oc1.sa-saopaulo-1.ccccccc...` |
| DB System | `ocid1.dbsystem.oc1.<region>.<unique-id>` | `ocid1.dbsystem.oc1.sa-saopaulo-1ddddddd...` |
| VM Cluster | `ocid1.vmcluster.oc1.<region>.<unique-id>` | `ocid1.vmcluster.oc1.sa-saopaulo-1.eeeeee...` |
| Exadata VM Cluster | `ocid1.exadatavmcluster.oc1.<region>.<unique-id>` | `ocid1.exadatavmcluster.oc1.sa-saopaulo-1.fffffff...` |
| MySQL DB System | `ocid1.mysqldbsystem.oc1.<region>.<unique-id>` | `ocid1.mysqldbsystem.oc1.sa-saopaulo-1.ggggggg...` |
| MySQL HeatWave Cluster | `ocid1.heatwavecluster.oc1.<region>.<unique-id>` | `ocid1.heatwavecluster.oc1.sa-saopaulo-1.hhhhhhh...` |
| PostgreSQL DB Instance | `ocid1postgresqldbinstance.oc1.<region>.<unique-id>` | `ocid1postgresqldbinstance.oc1.sa-saopaulo-1.iiiiiii...` |
| Database Backup | `ocid1.backup.oc1.<region>.<unique-id>` | `ocid1.backup.oc1.sa-saopaulo-1.jjjjjjj...` |
| Autonomous Backup | `ocid1.autonomousbackup.oc1.<region>.<unique-id>` | `ocid1.autonomousbackup.oc1.sa-saopaulo-1.kkkkkkk...` |

**Region codes**: `sa-saopaulo-1`, `us-ashburn-1`, `us-phoenix-1`, `eu-frankfurt-1`, `ap-tokyo-1`

---

## OCI CLI Syntax

### Autonomous Database (ATP/ADW)

```bash
# Create Autonomous Transaction Processing database
oci db autonomous-database create \
    --compartment-id $COMPARTMENT_ID \
    --display-name "atp-prod" \
    --db-name "atpprod" \
    --cpu-core-count 2 \
    --data-storage-size-in-tbs 1 \
    --license-model "LICENSE_INCLUDED" \
    --autonomous-maintenance-schedule-type "MONTHLY" \
    --auto-scaling-enabled true \
    --whitelisted-ips null

# Create Autonomous Data Warehouse
oci db autonomous-database create \
    --compartment-id $COMPARTMENT_ID \
    --display-name "adw-analytics" \
    --db-name "adwanalytics" \
    --cpu-core-count 4 \
    --data-storage-size-in-tbs 2 \
    --workload-type "DW" \
    --license-model "BRING_YOUR_OWN_LICENSE"

# Get Autonomous Database details
oci db autonomous-database get --autonomous-database-id $ADB_ID

# Scale CPU
oci db autonomous-database update \
    --autonomous-database-id $ADB_ID \
    --cpu-core-count 4

# Scale storage
oci db autonomous-database update \
    --autonomous-database-id $ADB_ID \
    --data-storage-size-in-tbs 2

# Stop/Start for cost savings
oci db autonomous-database stop --autonomous-database-id $ADB_ID
oci db autonomous-database start --autonomous-database-id $ADB_ID

# List Autonomous Databases
oci db autonomous-database list --compartment-id $COMPARTMENT_ID
```

### Autonomous Database Backups

```bash
# Create manual backup
oci db autonomous-database backup create \
    --autonomous-database-id $ADB_ID \
    --display-name "pre-migration-backup"

# Restore from backup
oci db autonomous-database restore \
    --autonomous-database-id $ADB_ID \
    --backup-id $BACKUP_ID

# List backups
oci db autonomous-database backup list --autonomous-database-id $ADB_ID
```

### MySQL HeatWave

```bash
# Create MySQL DB System
oci db-mysql db-system create \
    --compartment-id $COMPARTMENT_ID \
    --display-name "mysql-prod" \
    --availability-domain "aaaa:sa-saopaulo-1" \
    --shape-name "MySQL.VM2.Standard.E4" \
    --mysql-version "8.0" \
    --configuration-id "ocid1.mysqlconfig.oc1.sa-saopaulo-1.aaaaaaa..." \
    --admin-password "SecurePassword123!" \
    --data-storage-size-in-gbs 100

# Add HeatWave cluster
oci db-mysql heatwave-cluster create \
    --db-system-id $MYSQL_ID \
    --shape-name "MySQL.HeatWave.VM.Standard.E4" \
    --cluster-size 2

# List MySQL DB Systems
oci db-mysql db-system list --compartment-id $COMPARTMENT_ID
```

### PostgreSQL

```bash
# Create PostgreSQL DB Instance
oci db-postgresql instance create \
    --compartment-id $COMPARTMENT_ID \
    --display-name "postgres-prod" \
    --availability-domain "aaaa:sa-saopaulo-1" \
    --instance-type "Single" \
    --db-name "appdb" \
    --db-version "16" \
    --shape-name "VM.Standard2.4" \
    --storage-gb 100 \
    --admin-username "postgres" \
    --admin-password "SecurePassword123!"

# Get instance details
oci db-postgresql instance get --instance-id $PG_ID

# List PostgreSQL instances
oci db-postgresql instance list --compartment-id $COMPARTMENT_ID
```

### Exadata Cloud Service

```bash
# Create Exadata DB System (cloud autonomous)
oci db system create \
    --compartment-id $COMPARTMENT_ID \
    --display-name "exadata-prod" \
    --availability-domain "aaaa:sa-saopaulo-1" \
    --db-system-edition "EXADATA" \
    --cpu-core-count 8 \
    --data-storage-size-in-tbs 1 \
    --db-name "EXADB1" \
    --admin-password "SecurePassword123!" \
    --license-model "LICENSE_INCLUDED" \
    --version "19c"

# Create Exadata VM Cluster
oci db vm-cluster create \
    --compartment-id $COMPARTMENT_ID \
    --display-name "exadata-vm-cluster" \
    --exadata-infrastructure-id "$EXADATA_INFRA_ID" \
    --cpu-core-count 8 \
    --memory-size-in-gbs 120 \
    --db-version "19.25.0.0" \
    --license-model "BRING_YOUR_OWN_LICENSE"

# Scale up Exadata
oci db vm-cluster update \
    --vm-cluster-id "$EXADATA_VM_ID" \
    --cpu-core-count 12
```

### Database Patching

```bash
# List available patches
oci db patch list --compartment-id $COMPARTMENT_ID

# Apply patch to Autonomous Database
oci db autonomous-database patch apply \
    --autonomous-database-id $ADB_ID \
    --patch-id $PATCH_ID

# Patch DB System
oci db system patch \
    --db-system-id $DB_SYSTEM_ID \
    --action "APPLY" \
    --patch-id $PATCH_ID
```

---

## Anti-Patterns

NEVER generate:

1. **Inaccurate OCIDs**: Never invent fake OCIDs. Use format `ocid1.autonomousdatabase.oc1.<region>.<32-char-hex>` - if uncertain, use placeholder like `$ADB_ID`

2. **Wrong CLI service**: Never confuse `oci db autonomous-database` with `oci db-mysql` (MySQL) or `oci db-postgresql` (PostgreSQL) - these are separate services

3. **ATP vs ADW confusion**: Never recommend ATP for analytics workloads (use ADW) or ADW for high-concurrency OLTP (use ATP). Misunderstanding workload types is the #1 error

4. **BYOL licensing**: Never forget that "Bring Your Own License" requires existing Oracle DB licenses - cannot buy via OCI

5. **Autonomous maintenance without window**: Never skip explaining maintenance window and impact - applies patches automatically

6. **Exadata vs Cloud Exadata**: Never confuse Exadata Cloud Service (dedicated Exadata) with Cloud Exadata (Autonomous on Exadata infrastructure)

7. **HeatWave without MySQL**: Never add HeatWave cluster before MySQL DB System exists - HeatWave is a MySQL add-on

8. **PostgreSQL vs MySQL**: Never suggest PostgreSQL features (JSON, array types) don't exist or confuse the databases - they have different feature sets

9. **Scaling without limits**: Never ignore CPU core limits - autonomous databases have account-level core limits. [MUTABLE] tag for specific limits

10. **Backup without retention**: Never skip on-demand backup without understanding retention (Autonomous: 60 days default, use Manual for longer)

11. **Connection string confusion**: Never show wrong connection format - always use `(description=...` tnsnames style or dedicated endpoint for client connections