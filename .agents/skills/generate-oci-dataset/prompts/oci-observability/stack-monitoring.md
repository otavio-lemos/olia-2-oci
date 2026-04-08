# Prompt Template: oci-observability/stack-monitoring

## Context

Generate examples about OCI Stack Monitoring.

## Topics

- Stack Monitoring service
- Enterprise Manager integration
- Resource monitoring
- Custom metrics
- Alert rules

## Difficulty Distribution

- beginner (30%): Basic monitoring setup
- intermediate (50%): Custom metrics, alerts
- advanced (20%): Complex monitoring scenarios

## Quality Rules

- Include specific resource names
- Reference OCI documentation
- Tag mutable content with [MUTABLE]

## OCI CLI Syntax

### Monitoring Configuration

```bash
# Create monitor configuration
oci stack-monitoring monitor-config create --compartment-id <ocid> \
  --display-name "weblogic-monitor" \
  --monitor-type ORACLE_WEBSERVER

# List monitor configurations
oci stack-monitoring monitor-config list --compartment-id <ocid>

# Get monitor configuration
oci stack-monitoring monitor-config get \
  --monitor-config-id <ocid1.monconfig.oc1.<region>.<unique-id>>
```

### Metric Extension

```bash
# Create metric extension
oci stack-monitoring metric-extension create --compartment-id <ocid> \
  --display-name "jvm-memory-metric" \
  --metric-name "jvm_memory_used" \
  --metric-type COUNTER \
  --query "select * from jvm_metrics"

# List metric extensions
oci stack-monitoring metric-extension list --compartment-id <ocid>
```

### Alert Rule

```bash
# Create alert rule
oci stack-monitoring alert-rule create --compartment-id <ocid> \
  --display-name "high-memory-alert" \
  --metric-extensions-id <ocid1.metricext.oc1.<region>.<unique-id>> \
  --threshold "memory_usage > 80" \
  --severity CRITICAL

# List alert rules
oci stack-monitoring alert-rule list --compartment-id <ocid>

# Update alert rule
oci stack-monitoring alert-rule update \
  --alert-rule-id <ocid1.alertrule.oc1.<region>.<unique-id>> \
  --is-enabled true
```

### Resource Discovery

```bash
# List monitored resources
oci stack-monitoring resource list --compartment-id <ocid> \
  --monitor-id <ocid1.monitor.oc1.<region>.<unique-id>>

# Get resource metrics
oci stack-monitoring resource-metric list \
  --resource-id <ocid1.monitoredresource.oc1.<region>.<unique-id>>
```

## OCID Format

```
Monitor Config: ocid1.monconfig.oc1.<region>.<unique-id>
Metric Extension: ocid1.metricext.oc1.<region>.<unique-id>
Alert Rule: ocid1.alertrule.oc1.<region>.<unique-id>
Monitored Resource: ocid1.monitoredresource.oc1.<region>.<unique-id>
```

## Anti-Patterns

- NEVER create Stack Monitoring configurations without specifying monitor type
- NEVER use real OCIDs — always use placeholders like `<ocid1.monconfig.oc1.<region>.<unique-id>>`
- NEVER omit `--compartment-id` — required for all operations
- NEVER copy OCI documentation verbatim — generate original examples
- NEVER skip metric extension definition — custom metrics require proper definition
- NEVER create alerts without thresholds — always specify trigger conditions
- NEVER use generic metric names — use descriptive names like "jvm_heap_usage"
- NEVER use deprecated monitor types — use current Oracle types only
- NEVER omit Enterprise Manager credential configuration when required
- NEVER create alerts without notification destination — specify where alerts go
