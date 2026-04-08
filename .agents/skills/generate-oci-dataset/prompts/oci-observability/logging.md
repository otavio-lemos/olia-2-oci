# Prompt Template: oci-observability/logging

## Context

Generate examples about OCI Logging service.

## Topics

- Logging service
- Log groups
- Custom logs
- Log retention
- Log analysis

## Difficulty Distribution

- beginner (30%): Basic log setup
- intermediate (50%): Custom logs, retention
- advanced (20%): Advanced configurations

## Quality Rules

- Include specific OCI resource names
- Reference OCI documentation
- Tag mutable content with [MUTABLE]

## OCI CLI Syntax

### Log Group Commands

```bash
# Create log group
oci logging log-group create --compartment-id <ocid> \
  --display-name "app-logs-group" \
  --description "Application logs for production"

# List log groups
oci logging log-group list --compartment-id <ocid>

# Get log group
oci logging log-group get --log-group-id <ocid1.loggroup.oc1.<region>.<unique-id>>
```

### Log Commands

```bash
# Enable log
oci logging log create --log-group-id <ocid1.loggroup.oc1.<region>.<unique-id>> \
  --display-name "app-access-log" \
  --log-source-id <ocid1.instance.oc1.<region>.<unique-id>> \
  --log-type JSON

# List logs in group
oci logging log list --log-group-id <ocid1.loggroup.oc1.<region>.<unique-id>>

# Disable log
oci logging log delete --log-id <ocid1.log.oc1.<region>.<unique-id>>
```

### Log Search

```bash
# Search logs (using logs-query)
oci logging log-search search \
  --log-group-id <ocid1.loggroup.oc1.<region>.<unique-id>> \
  --time-start "2024-01-01T00:00:00Z" \
  --time-end "2024-01-02T00:00:00Z" \
  --search-query "message LIKE '%ERROR%'"
```

### Retention Management

```bash
# Update log retention (minimum 7 days, maximum 365 days)
oci logging log update --log-id <ocid1.log.oc1.<region>.<unique-id>> \
  --retention-duration-days 30
```

## OCID Format

```
Log Group: ocid1.loggroup.oc1.<region>.<unique-id>
Log: ocid1.log.oc1.<region>.<unique-id>
VCN: ocid1.vcn.oc1.<region>.<unique-id>
Instance: ocid1.instance.oc1.<region>.<unique-id>
```

## Anti-Patterns

- NEVER create logs without specifying a log group
- NEVER use real OCIDs — always use placeholders like `<ocid1.loggroup.oc1.<region>.<unique-id>>`
- NEVER omit `--compartment-id` — required for all operations
- NEVER set retention below 7 days or above 365 days
- NEVER copy OCI documentation verbatim — generate original examples
- NEVER skip enabling logs — disabled logs don't collect data
- NEVER use vague log names — use descriptive names like "prod-api-access-log"
- NEVER omit `--log-type` when creating logs — JSON or SYSLOG required
- NEVER query logs without time filters — always specify start/end time
- NEVER generate logs without retention policies — always specify retention duration
