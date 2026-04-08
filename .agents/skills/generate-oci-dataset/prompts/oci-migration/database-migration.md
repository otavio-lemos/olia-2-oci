# Prompt Template: oci-migration/database-migration

## Context

Generate examples about OCI Database Migration Service.

## Topics

- OCI Database Migration Service
- Online vs Offline migration
- Zero Downtime Migration (ZDM)
- Oracle → Autonomous DB migration
- MySQL → OCI MySQL migration
- Migration workflows

## Difficulty Distribution

- beginner (20%): Basic migration concepts
- intermediate (50%): Migration configuration
- advanced (30%): Zero Downtime Migration, complex scenarios

## Quality Rules

- Include Database Migration Service steps
- Explain online vs offline differences
- Reference ZDM workflow
- Tag mutable content with [MUTABLE]

---

## OCI CLI Syntax Section

When generating examples, include actual OCI CLI commands:

### Database Migration Service

```bash
# List database migrations
oci databasemigration migration list --compartment-id $COMPARTMENT_ID

# Create migration (online)
oci databasemigration migration create \
  --display-name "prod-db-migration" \
  --compartment-id $COMPARTMENT_ID \
  --source-database-type "ORACLE" \
  --source-connection-string "oracle://source.host:1521/SID" \
  --source-admin-credentials "username=admin,password=xxx" \
  --target-autonomous-database-id $ADB_OCID \
  --migration-type "ONLINE"

# Create migration (offline)
oci databasemigration migration create \
  --display-name "offline-migration" \
  --compartment-id $COMPARTMENT_ID \
  --source-database-type "ORACLE" \
  --source-connection-string "oracle://source.host:1521/SID" \
  --target-autonomous-database-id $ADB_OCID \
  --migration-type "OFFLINE"

# Start migration
oci databasemigration migration start \
  --migration-id $MIGRATION_OCID

# Get migration status
oci databasemigration migration get \
  --migration-id $MIGRATION_OCID

# Stop migration
oci databasemigration migration stop \
  --migration-id $MIGRATION_OCID
```

### Zero Downtime Migration (ZDM)

```bash
# List ZDM migration jobs
oci zdm-migration-job list --compartment-id $COMPARTMENT_ID

# Create ZDM physical migration
oci zdm-migration-job create \
  --display-name "zdm-prod" \
  --compartment-id $COMPARTMENT_ID \
  --source-db-system-id $EXACC_OCID \
  --target-autonomous-database-id $ADB_OCID \
  --migration-type "PHYSICAL"

# Create ZDM logical migration
oci zdm-migration-job create \
  --display-name "zdm-logical" \
  --compartment-id $COMPARTMENT_ID \
  --source-database-id $SOURCE_DB_OCID \
  --target-autonomous-database-id $ADB_OCID \
  --migration-type "LOGICAL"

# Get ZDM job details
oci zdm-migration-job get \
  --migration-job-id $ZDM_JOB_OCID

# Check ZDM phase
oci zdm-migration-job get-phase \
  --migration-job-id $ZDM_JOB_OCID
```

### Oracle to Autonomous DB

```bash
# List autonomous databases
oci db autonomous-database list --compartment-id $COMPARTMENT_ID

# Create target Autonomous Database
oci db autonomous-database create \
  --display-name "target-adb" \
  --compartment-id $COMPARTMENT_ID \
  --db-name "TARGETDB" \
  --cpu-core-count 4 \
  --storage-size-in-tbs 2 \
  --license-model "LICENSE_INCLUDED" \
  --db-workload "ATP"

# Get connection strings
oci db autonomous-database get-connection-strings \
  --autonomous-database-id $ADB_OCID

# Generate wallet for connection
oci db autonomous-database generate-wallet \
  --autonomous-database-id $ADB_OCID \
  --password "SecurePassword123" \
  --file "/path/to/wallet.zip"

# Update database for migration
oci db autonomous-database update \
  --autonomous-database-id $ADB_OCID \
  --auto-scaling-enabled true
```

### MySQL to OCI MySQL

```bash
# List OCI MySQL instances
oci mysql system list --compartment-id $COMPARTMENT_ID

# Create OCI MySQL instance
oci mysql system create \
  --display-name "prod-mysql" \
  --compartment-id $COMPARTMENT_ID \
  --shape-name MySQL.VM.Standard.E4 \
  --mysql-version "8.0" \
  --subnet-id $SUBNET_OCID \
  --admin-password "SecurePassword123"

# Create read replica
oci mysql read-replica create \
  --display-name "read-replica" \
  --mysql-system-id $MYSQL_OCID \
  --replica-source-type "MySQLSystem"

# Get backup list
oci mysql backup list --mysql-system-id $MYSQL_OCID

# Restore from backup
oci mysql system restore \
  --mysql-system-id $MYSQL_OCID \
  --backup-id $BACKUP_OCID
```

### DB Systems (Exadata, VM, BM)

```bash
# List DB systems
oci db system list --compartment-id $COMPARTMENT_ID

# Create Exadata DB System
oci db system create \
  --display-name "prod-exacc" \
  --compartment-id $COMPARTMENT_ID \
  --system-shape "EXACC" \
  --db-version "19c" \
  --cpu-core-count 8 \
  --storage-size-in-tbs 32

# Create VM DB System
oci db system create \
  --display-name "prod-vm" \
  --compartment-id $COMPARTMENT_ID \
  --system-shape "VM.Standard2.16" \
  --db-version "19c" \
  --cpu-core-count 16 \
  --storage-size-in-tbs 32

# Get database connection strings
oci db database get \
  --database-id $DB_OCID | jq '.connection_strings'

# Create data guard
oci db data-guard-association create \
  --database-id $DB_OCID \
  --creation-type "NewDatabase" \
  --peer-region "us-ashburn-1"
```

---

## Migration Type Comparison

### Online Migration

| Aspect | Description |
|--------|-------------|
| Downtime | Minimal (cutover window) |
| Data Sync | Continuous replication |
| Use Case | Production databases |
| Duration | Hours to days |
| Risk | Lower |
| OCI Tool | Database Migration Service (Online) |

### Offline Migration

| Aspect | Description |
|--------|-------------|
| Downtime | Full source downtime during migration |
| Data Sync | Single batch transfer |
| Use Case | Dev/Test, small databases |
| Duration | Hours |
| Risk | Higher (no continuous sync) |
| OCI Tool | Database Migration Service (Offline), Data Pump |

### Zero Downtime Migration (ZDM)

| Aspect | Description |
|--------|-------------|
| Downtime | Zero |
| Data Sync | GoldenGate-based replication |
| Use Case | Mission-critical production |
| Duration | Days to weeks (setup) |
| Risk | Minimal |
| OCI Tool | Zero Downtime Migration (ZDM) |

---

## Anti-Patterns Section

**NEVER generate the following in OCI examples:**

### Other Cloud Database Commands (DO NOT USE)

```bash
# WRONG - AWS RDS commands
aws rds describe-db-instances
aws rds create-db-instance
aws rds create-db-instance-read-replica

# WRONG - Azure SQL commands
az sql db show
az sql db create

# WRONG - GCP Cloud SQL commands
gcloud sql instances list
gcloud sql databases create
```

### Common Anti-Patterns

1. **Never suggest AWS DMS for OCI migration** - Use OCI Database Migration Service
2. **Never use Azure Database Migration Service** - Use OCI native tools
3. **Never use AWS RDS read replica** - Use OCI MySQL read replicas
4. **Never use GCP Cloud SQL** - Use Autonomous Database
5. **Never use Oracle Data Pump incorrectly** - Must target OCI Object Storage
6. **Never suggest GoldenGate cloud-to-cloud** - Use ZDM for Oracle migrations
7. **Never recommend using RMAN directly for migration** - Use Database Migration Service
8. **Never use other cloud backup restore** - Use OCI backup and restore
9. **Never suggest manual database creation** - Use Terraform or Resource Manager
10. **Never ignore OCID format** - All database resources use ocid1.db.* format

### OCID Format Requirements

```bash
# Correct OCID format for databases
ocid1.autonomousdatabase.oc1.iad.xxx...
ocid1.database.oc1.iad.xxx...
ocid1.dbsystem.oc1.iad.xxx...
ocid1.mysqlystem.oc1.iad.xxx...

# Migration service OCIDs
ocid1.migration.oc1.iad.xxx...
ocid1.zdmjob.oc1.iad.xxx...
```

---

## Migration Workflow Example

```bash
# Step 1: Create target Autonomous Database
oci db autonomous-database create \
  --display-name "prod-adb" \
  --compartment-id $COMPARTMENT_ID \
  --db-name "PRODDB" \
  --cpu-core-count 4

# Step 2: Create database migration
oci databasemigration migration create \
  --display-name "prod-migration" \
  --compartment-id $COMPARTMENT_ID \
  --source-database-type "ORACLE" \
  --target-autonomous-database-id $ADB_OCID \
  --migration-type "ONLINE"

# Step 3: Start migration
oci databasemigration migration start \
  --migration-id $MIGRATION_OCID

# Step 4: Monitor progress
oci databasemigration migration get \
  --migration-id $MIGRATION_OCID

# Step 5: Cutover
oci databasemigration migration cutover \
  --migration-id $MIGRATION_OCID
```