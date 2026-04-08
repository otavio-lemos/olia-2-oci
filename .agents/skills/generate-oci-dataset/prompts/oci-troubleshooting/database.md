# Prompt Template: oci-troubleshooting/database

## Context

Generate examples about troubleshooting OCI Database issues.

## Topics

- Autonomous Database connection issues
- Connection string / wallet problems
- TNS errors
- ADB performance issues
- Database access from on-premises
- Connection pool issues

## Difficulty Distribution

- beginner (20%): Basic connection issues
- intermediate (50%): Wallet configuration, TNS
- advanced (30%): Performance tuning, complex connectivity

## Quality Rules

- Include wallet configuration steps
- Reference connection string formats
- Tag mutable content with [MUTABLE]

## OCI Diagnostic CLI Syntax

Use these real OCI CLI commands for Database troubleshooting:

```bash
# Autonomous Database (ADB)
oci database autonomous-database get --autonomous-database-id ocid1.autonomousdatabase.oc1.<region>.<unique-id>
oci database autonomous-database list --compartment-id ocid1.compartment.oc1.<region>.<unique-id>

# ADB connection strings
oci database autonomous-database get --autonomous-database-id ocid1.autonomousdatabase.oc1.<region>.<unique-id> --query "data.connection-strings"

# Database System (DBSystem)
oci database db-system get --db-system-id ocid1.dbsystem.oc1.<region>.<unique-id>
oci database db-system list --compartment-id ocid1.compartment.oc1.<region>.<unique-id>

# Database VM cluster
oci database vm-cluster get --vm-cluster-id ocid1.vmcluster.oc1.<region>.<unique-id>

# Exadata Infrastructure
oci database exadata-infrastructure get --exadata-infrastructure-id ocid1.exadatainfrastructure.oc1.<region>.<unique-id>

# Backup operations
oci database backup list --compartment-id ocid1.compartment.oc1.<region>.<unique-id> --database-id ocid1.autonomousdatabase.oc1.<region>.<unique-id>

# Patch status
oci database autonomous-database get --autonomous-database-id ocid1.autonomousdatabase.oc1.<region>.<unique-id> --query "data.maintenance-schedule-details"

# Connection diagnostics
oci database autonomous-database wallet download --autonomous-database-id ocid1.autonomousdatabase.oc1.<region>.<unique-id> --password "your-password"

# Resource utilization (metrics)
oci monitoring metric-data get --compartment-id ocid1.compartment.oc1.<region>.<unique-id> --metric-name "CpuUtilization" --resource-id ocid1.autonomousdatabase.oc1.<region>.<unique-id>
```

## OCID Format

OCI resource identifiers follow this pattern:

```
ocid1.<resource-type>.<realm>.<region>.<unique-id>

Examples:
- ocid1.autonomousdatabase.oc1.sa-vinhedo-1.abcd1234...
- ocid1.dbsystem.oc1.sa-vinhedo-1.abcd1234...
- ocid1.vmcluster.oc1.sa-vinhedo-1.abcd1234...
- ocid1.exadatainfrastructure.oc1.sa-vinhedo-1.abcd1234...

Connection string format:
- high: dbname.high.us-east-1.adb.oraclecloud.com:1522/dbname_high.adb.oraclecloud.com
- medium: dbname.medium.us-east-1.adb.oraclecloud.com:1522/dbname_medium.adb.oraclecloud.com
- low: dbname.low.us-east-1.adb.oraclecloud.com:1522/dbname_low.adb.oraclecloud.com

TNS format: (DESCRIPTION=(ADDRESS=(PROTOCOL=TCPS)(HOST=...)(PORT=1522))(CONNECT_DATA=(SERVICE_NAME=...)))
```

## Anti-Patterns

**NEVER generate:**

- ❌ TNS errors without explaining ORA error codes
- ❌ Wallet troubleshooting without mentioning download/refresh process
- ❌ Connection string issues without showing actual format
- ❌ Performance advice without mentioning OCPU/Storage scaling [MUTABLE]
- ❌ "Enable SSL" without explaining certificate requirements
- ❌ Copy OCI documentation verbatim
- ❌ Suggest specific IP addresses or ports without noting as [MUTABLE]
- ❌ Connection pool tuning without considering application needs
- ❌ Access from on-prem without mentioning required network setup (VPN/FastConnect)
- ❌ Never suggest disabling wallet security for "convenience"

## Common Issues

- ORA-12541: TNS:no listener
- ORA-12514: TNS:listener does not currently know of service
- Wallet file not found or corrupted
- SSL/TLS handshake failures
- Connection timeout from on-premises
- OCPU capacity exhausted [MUTABLE]

## Example Questions

- "Não consigo conectar no Autonomous Database"
- "Erro ORA-12514 ao conectar no banco"
- "Como configurar wallet para ADB?"
- "Conexão lenta no banco"
- "Wallet não funciona com SQL Developer"