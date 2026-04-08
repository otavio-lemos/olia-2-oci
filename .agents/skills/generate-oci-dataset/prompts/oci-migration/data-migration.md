# Prompt Template: oci-migration/data-migration

## Context

Generate examples about OCI data migration and integration services.

## Topics

- OCI GoldenGate for data replication
- Data Integration service
- Object Storage data transfer
- Storage Gateway
- Data Flow

## Difficulty Distribution

- beginner (30%): Basic data transfer concepts
- intermediate (50%): GoldenGate, Data Integration
- advanced (20%): Complex replication scenarios

## Quality Rules

- Include GoldenGate configuration examples
- Reference Data Integration pipelines
- Tag mutable content with [MUTABLE]

---

## OCI CLI Syntax Section

When generating examples, include actual OCI CLI commands:

### OCI GoldenGate

```bash
# List GoldenGate deployments
oci goldengate deployment list --compartment-id $COMPARTMENT_ID

# Create GoldenGate deployment
oci goldengate deployment create \
  --display-name "prod-gg" \
  --compartment-id $COMPARTMENT_ID \
  --subnet-id $SUBNET_OCID \
  --deployment-type "OGG19" \
  --license-model "LICENSE_INCLUDED" \
  --cpu-core-count 2 \
  --storage-size-in-gbs 1024

# Get deployment connection info
oci goldengate deployment get \
  --deployment-id $GG_DEPLOYMENT_OCID

# Create GoldenGate connection (Oracle DB)
oci goldengate connection create \
  --display-name "oracle-source" \
  --compartment-id $COMPARTMENT_ID \
  --deployment-id $GG_DEPLOYMENT_OCID \
  --connection-type "ORACLE" \
  --connection-string "oracle://source.host:1521/SID"

# Create connection (MySQL)
oci goldengate connection create \
  --display-name "mysql-target" \
  --compartment-id $COMPARTMENT_ID \
  --deployment-id $GG_DEPLOYMENT_OCID \
  --connection-type "MYSQL" \
  --connection-string "mysql://mysql.host:3306/db"

# Create extract
oci goldengate extract create \
  --deployment-id $GG_DEPLOYMENT_OCID \
  --display-name "ext-orders" \
  --source-connection-id $CONNECTION_OCID \
  --extract-type "INTEGRATED" \
  --source-scn 1234567

# Create replicat
oci goldengate replicat create \
  --deployment-id $GG_DEPLOYMENT_OCID \
  --display-name "rep-orders" \
  --target-connection-id $TARGET_CONN_OCID \
  --replicat-type "INTEGRATED" \
  --checkpoint-table "CHECKPOINT"

# Start/stop extract
oci goldengate extract start --extract-id $EXTRACT_OCID
oci goldengate extract stop --extract-id $EXTRACT_OCID
```

### Data Integration

```bash
# List data flows
oci data-integration data-flow list --compartment-id $COMPARTMENT_ID

# Create data flow
oci data-integration data-flow create \
  --display-name "etl-pipeline" \
  --compartment-id $COMPARTMENT_ID \
  --project-id $PROJECT_OCID \
  --data-flow-type "DATA_LOADER"

# List tasks
oci data-integration task list --compartment-id $COMPARTMENT_ID

# Create task
oci data-integration task create \
  --display-name "data-copy-task" \
  --compartment-id $COMPARTMENT_ID \
  --task-type "INTEGRATION_TASK" \
  --source-connection-id $SOURCE_CONN_OCID \
  --target-connection-id $TARGET_CONN_OCID

# Run task
oci data-integration task run \
  --task-id $TASK_OCID

# Get task run status
oci data-integration task-run get \
  --task-run-id $TASK_RUN_OCID
```

### Data Flow (Spark-based)

```bash
# List Data Flow applications
oci dataflow application list --compartment-id $COMPARTMENT_ID

# Create Data Flow application
oci dataflow application create \
  --display-name "spark-etl" \
  --compartment-id $COMPARTMENT_ID \
  --spark-version "3.2.1" \
  --driver-shape "VM.Standard.E4.Flex" \
  --executor-shape "VM.Standard.E4.Flex" \
  --num-executors 4 \
  --file-uri "oci://bucket@namespace/etl-script.py"

# Get application logs
oci dataflow application get-logs \
  --application-id $APP_OCID

# Run application
oci dataflow application run \
  --application-id $APP_OCID
```

### Object Storage Data Transfer

```bash
# List buckets
oci os bucket list --namespace-name $NAMESPACE --compartment-id $COMPARTMENT_ID

# Create bucket for data staging
oci os bucket create \
  --name "data-staging" \
  --namespace-name $NAMESPACE \
  --compartment-id $COMPARTMENT_ID

# Upload data file
oci os object put \
  --namespace-name $NAMESPACE \
  --bucket-name "data-staging" \
  --file "/data/import.csv" \
  --object-name "raw/import.csv"

# Copy to another bucket
oci os object put \
  --namespace-name $NAMESPACE \
  --bucket-name "data-archive" \
  --source-uri "https://data-staging.s3.amazonaws.com/raw/import.csv"
```

### Storage Gateway

```bash
# List storage gateways
oci storage-gateway gateway list --compartment-id $COMPARTMENT_ID

# Create storage gateway
oci storage-gateway gateway create \
  --display-name "data-gateway" \
  --compartment-id $COMPARTMENT_ID \
  --gateway-type "FILE" \
  --capacity 50TB

# Get NFS mount details
oci storage-gateway gateway get-nfs-mount-info \
  --gateway-id $GATEWAY_OCID

# Create bucket for gateway backup
oci os bucket create \
  --name "gateway-backup" \
  --namespace-name $NAMESPACE \
  --compartment-id $COMPARTMENT_ID

# Configure gateway to Object Storage
oci storage-gateway bucket configuration create \
  --gateway-id $GATEWAY_OCID \
  --bucket-name "gateway-backup"
```

### Data Catalog

```bash
# List data catalogs
oci datacatalog catalog list --compartment-id $COMPARTMENT_ID

# Create data asset
oci datacatalog data-asset create \
  --catalog-id $CATALOG_OCID \
  --display-name "prod-db-asset" \
  --type "ORACLE_DATABASE" \
  --connection-string "oracle://host:1521/SID"

# Create data entity (table)
oci datacatalog entity create \
  --data-asset-id $ASSET_OCID \
  --display-name "orders_table" \
  --schema-name "sales"

# Search for data
oci datacatalog term list \
  --catalog-id $CATALOG_OCID \
  --name "customer"
```

---

## Cloud-to-OCI Mapping Section

| AWS Service | OCI Equivalent | Notes |
|-------------|----------------|-------|
| AWS DMS | OCI Database Migration Service | Oracle, MySQL, PostgreSQL |
| AWS Glue | OCI Data Integration | ETL pipelines |
| AWS Glue DataBrew | OCI Data Integration | Data preparation |
| AWS EMR | OCI Data Flow | Spark workloads |
| Kinesis | OCI Event Hub | Streaming |
| S3 Data Lake | Object Storage + Data Lake | Different approach |
| AWS Lake Formation | Data Catalog | Data governance |
| AWS Data Pipeline | Data Integration | Workflow orchestration |
| AWS Glue Catalog | OCI Data Catalog | Metadata management |

| Azure Service | OCI Equivalent | Notes |
|---------------|----------------|-------|
| Azure Data Factory | OCI Data Integration | Data pipelines |
| Azure Data Lake | Object Storage | Different storage model |
| Azure Databricks | OCI Data Flow + Notebook | Spark analytics |
| Azure Event Hub | OCI Event Hub | Streaming |
| Azure Migration | OCI Database Migration | Various sources |
| Azure Data Catalog | OCI Data Catalog | Metadata |

| GCP Service | OCI Equivalent | Notes |
|-------------|----------------|-------|
| Cloud Dataflow | OCI Data Flow | Spark/Beam |
| Cloud Data Fusion | OCI Data Integration | ETL/ELT |
| Cloud Pub/Sub | OCI Event Hub | Streaming |
| Cloud Storage | OCI Object Storage | Object storage |
| Dataform | OCI Data Integration | SQL pipelines |

---

## Anti-Patterns Section

**NEVER generate the following in OCI examples:**

### Other Cloud Data Commands (DO NOT USE)

```bash
# WRONG - AWS
aws dms create-replication-instance
aws glue create-job
aws emr create-cluster
aws s3 cp data s3://bucket/

# WRONG - Azure
az datafactory pipeline create
az databricks workspace create
az storage blob upload

# WRONG - GCP
gcloud dataflow jobs list
gcloud datafusion instance create
gcloud pubsub topics create
```

### Common Anti-Patterns

1. **Never use AWS Glue** - Use OCI Data Integration
2. **Never use AWS EMR** - Use OCI Data Flow
3. **Never use Azure Data Factory** - Use OCI Data Integration
4. **Never use GCP Dataflow** - Use OCI Data Flow
5. **Never use other cloud's GoldenGate** - Use OCI GoldenGate (OGG19)
6. **Never use AWS S3 for data staging** - Use OCI Object Storage
7. **Never use other cloud's DMS** - Use OCI Database Migration Service
8. **Never skip OCID format** - All resources use proper OCIDs
9. **Never suggest manual data transfer** - Use automation
10. **Never ignore data governance** - Use Data Catalog

### OCID Format Requirements

```bash
# Correct OCID format for data services
ocid1.goldengatedeployment.oc1.iad.xxx...
ocid1.goldengateconnection.oc1.iad.xxx...
ocid1.dataintegrationworkspace.oc1.iad.xxx...
ocid1.dataflowapplication.oc1.iad.xxx...
ocid1.datacatalog.oc1.iad.xxx...
ocid1.storagegateway.oc1.iad.xxx...
```

---

## Migration Patterns

### Data Replication Pattern

```bash
# 1. Create GoldenGate deployment
oci goldengate deployment create --display-name "replication" --cpu-core-count 2

# 2. Create source connection (Oracle)
oci goldengate connection create --connection-type "ORACLE" --connection-string "oracle://source:1521/SID"

# 3. Create target connection (OCI DB)
oci goldengate connection create --connection-type "AUTONOMOUS_DATABASE" --connection-string "adb://target"

# 4. Create extract
oci goldengate extract create --extract-type "INTEGRATED" --source-scn 123456

# 5. Create replicat
oci goldengate replicat create --replicat-type "INTEGRATED"

# 6. Start replication
oci goldengate extract start --extract-id $EXTRACT_OCID
```

### Data Pipeline Pattern

```bash
# 1. Create Data Integration workspace
oci data-integration workspace create --display-name "di-workspace"

# 2. Create connections
oci data-integration connection create --connection-type "ORACLE"
oci data-integration connection create --connection-type "OBJECT_STORAGE"

# 3. Create data flow
oci data-integration data-flow create --data-flow-type "DATA_LOADER"

# 4. Create and run task
oci data-integration task create --task-type "INTEGRATION_TASK"
oci data-integration task run --task-id $TASK_OCID
```

### Data Flow Pattern

```bash
# 1. Create Data Flow application
oci dataflow application create \
  --spark-version "3.2.1" \
  --driver-shape "VM.Standard.E4.Flex" \
  --executor-shape "VM.Standard.E4.Flex" \
  --num-executors 4

# 2. Run application
oci dataflow application run --application-id $APP_OCID

# 3. Check status
oci dataflow application get --application-id $APP_OCID
```