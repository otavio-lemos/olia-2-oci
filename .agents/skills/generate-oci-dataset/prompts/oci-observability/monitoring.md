# Prompt Template: oci-observability/monitoring

## Context

Generate examples about OCI Monitoring service.

## Topics

- Metrics
- Alarms
- Notifications
- Alarm destinations

## Difficulty Distribution

- beginner (30%): Basic alarm creation
- intermediate (50%): Custom metrics, notifications
- advanced (20%): Complex alarm configurations

## Quality Rules

- Include specific OCI resource names
- Reference OCI documentation
- Tag mutable content with [MUTABLE]

## OCI CLI Syntax

### Alarm Commands

```bash
# Create alarm
oci monitoring alarm create --compartment-id <ocid> \
  --display-name "High CPU Alarm" \
  --metric-compartment-id <ocid> \
  --namespace "oci_compute" \
  --resource-group "INSTANCE_NAME" \
  --query "cpu_utilization > 80" \
  --severity CRITICAL \
  --notification-topic-id <ocid1.topic.oc1.<region>.<unique-id>>

# List alarms
oci monitoring alarm list --compartment-id <ocid> \
  --query "[?displayName=='High CPU Alarm']"

# Get alarm
oci monitoring alarm get --alarm-id <ocid1.alarm.oc1.<region>.<unique-id>>

# Update alarm
oci monitoring alarm update --alarm-id <ocid1.alarm.oc1.<region>.<unique-id>> \
  --severity WARNING

# Delete alarm
oci monitoring alarm delete --alarm-id <ocid1.alarm.oc1.<region>.<unique-id>>
```

### Metric Commands

```bash
# Post custom metric
oci monitoring metric post \
  --metric-details '{"datapoints":[{"timestamp":"2024-01-01T00:00:00Z","value":85.5}]}' \
  --namespace "custom_namespace" \
  --resource-id <ocid1.instance.oc1.<region>.<unique-id>> \
  --compartment-id <ocid>

# Query metrics
oci monitoring metric-data query \
  --compartment-id <ocid> \
  --namespace "oci_compute" \
  --query "cpu_utilization" \
  --start-time "2024-01-01T00:00:00Z" \
  --end-time "2024-01-02T00:00:00Z"
```

### Notification Commands

```bash
# Create topic
oci ons topic create --compartment-id <ocid> \
  --name "alarms-topic"

# Publish message
oci ons message publish --topic-id <ocid1.topic.oc1.<region>.<unique-id>> \
  --message '{"title":"Alarm","body":"CPU high"}'
```

## OCID Format

```
Alarm: ocid1.alarm.oc1.<region>.<unique-id>
Topic: ocid1.topic.oc1.<region>.<unique-id>
Metric: ocid1.metric.oc1.<region>.<unique-id>
Instance: ocid1.instance.oc1.<region>.<unique-id>
```

## Anti-Patterns

- NEVER use generic alarm names like "my alarm" — use descriptive names like "prod-webserver-cpu-alarm"
- NEVER omit `--compartment-id` — required for all operations
- NEVER use real OCIDs — always use placeholder `<ocid1.alarm.oc1.<region>.<unique-id>>`
- NEVER copy OCI documentation verbatim — generate original examples
- NEVER skip alarm destinations — always specify notification target
- NEVER use deprecated alarm states — use only ACTIVE, DELETED, DISABLED
- NEVER omit severity level — CRITICAL, ERROR, WARNING, INFO are valid values
- NEVER create alarms without query validation — queries must be syntactically correct
- NEVER use hardcoded thresholds without context — explain the reasoning
