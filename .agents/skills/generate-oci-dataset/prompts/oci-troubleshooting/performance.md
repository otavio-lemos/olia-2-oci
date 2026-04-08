# Prompt Template: oci-troubleshooting/performance

## Context

Generate examples about troubleshooting OCI performance issues.

## Topics

- Instance performance (CPU, memory)
- Shape sizing
- Storage bottlenecks (IOPS, throughput)
- Network bandwidth
- Database performance

## Difficulty Distribution

- beginner (20%): Basic performance checks
- intermediate (50%): Shape sizing, storage optimization
- advanced (30%): Complex performance tuning

## Quality Rules

- Include diagnostic commands (top, iostat, sar)
- Explain shape selection criteria
- Reference performance limits
- Tag mutable content with [MUTABLE]

## OCI Diagnostic CLI Syntax

Use these real OCI CLI commands for Performance troubleshooting:

```bash
# Instance shape info
oci compute instance get --instance-id ocid1.instance.oc1.<region>.<unique-id> --query "data.shape"
oci compute shape list --compartment-id ocid1.compartment.oc1.<region>.<unique-id> --availability-domain "AD1"

# Block Volume performance
oci bv volume get --volume-id ocid1.volume.oc1.<region>.<unique-id>
oci bv volume update --volume-id ocid1.volume.oc1.<region>.<unique-id> --vpus-per-gb <value>

# Volume performance metrics
oci monitoring metric-data get --compartment-id ocid1.compartment.oc1.<region>.<unique-id> \
  --metric-name "VolumeReadThroughput" \
  --resource-id ocid1.volume.oc1.<region>.<unique-id> \
  --interval "5m" \
  --timestamp-start "2025-01-01T00:00:00Z"

# Compute instance metrics
oci monitoring metric-data get --compartment-id ocid1.compartment.oc1.<region>.<unique-id> \
  --metric-name "CpuUtilization" \
  --resource-id ocid1.instance.oc1.<region>.<unique-id> \
  --interval "1m"

# Network bandwidth
oci network vnic get --vnic-id ocid1.vnic.oc1.<region>.<unique-id> --query "data.bandwidth-shape-name"

# Autonomous Database performance
oci database autonomous-database get --autonomous-database-id ocid1.autonomousdatabase.oc1.<region>.<unique-id> \
  --query "data.{ocpu:\"ocpu-count\",storage:\"data-storage-size-in-tbs\"}"
oci database autonomous-database update --autonomous-database-id ocid1.autonomousdatabase.oc1.<region>.<unique-id> \
  --ocpu-count <number>

# Database performance metrics
oci database autonomous-database get --autonomous-database-id ocid1.autonomousdatabase.oc1.<region>.<unique-id> \
  --query "data.service-configure-options"

# Shape resize
oci compute instance update --instance-id ocid1.instance.oc1.<region>.<unique-id> --shape "VM.Standard.E4.Flex" --shape-config "{\"ocpus\": 4, \"memory-in-gbs\": 64}"
```

## OCID Format

OCI resource identifiers follow this pattern:

```
ocid1.<resource-type>.<realm>.<region>.<unique-id>

Examples:
- ocid1.instance.oc1.sa-vinhedo-1.abcd1234...
- ocid1.volume.oc1.sa-vinhedo-1.abcd1234...
- ocid1.autonomousdatabase.oc1.sa-vinhedo-1.abcd1234...
- ocid1.vnic.oc1.sa-vinhedo-1.abcd1234...

Shape naming convention:
- Standard: VM.Standard2.X, VM.Standard.E4.X
- Flex: VM.Standard.E4.Flex (customizable OCPU/memory)
- Dense: VM.Dense2.X (storage optimized)
- HPC: VM.HPC2.X (high performance)
```

## Anti-Patterns

**NEVER generate:**

- ❌ Performance tuning without showing diagnostic commands
- ❌ Shape suggestions without checking availability in region
- ❌ Storage performance without mentioning VPUs [MUTABLE]
- ❌ "Scale up" without explaining cost implications [MUTABLE]
- ❌ Network issues without checking bandwidth shape limits
- ❌ Copy OCI documentation verbatim
- ❌ Suggest specific numbers without marking as [MUTABLE]
- ❌ OCPU/Storage scaling without mentioning limits [MUTABLE]
- ❌ Performance bottlenecks without considering application architecture
- ❌ Never recommend disabling auto-scaling for "consistency"

## Common Issues

- High CPU utilization
- Memory exhaustion
- IOPS/throughput limits reached
- Network bandwidth constraints
- Database query performance degradation

## Example Questions

- "Instância com alta utilização de CPU"
- "Storage lento, como aumentar IOPS?"
- "Qual shape usar para minha aplicação?"
- "Como monitorar performance do banco?"
- "Network bandwidth insufficient"