# Prompt Template: oci-observability/apm

## Context

Generate examples about OCI Application Performance Monitoring (APM).

## Topics

- Application Performance Monitoring
- Distributed tracing
- Performance diagnostics
- Service maps
- Span analysis
- Performance baselines

## Difficulty Distribution

- beginner (30%): Basic APM setup
- intermediate (50%): Tracing configuration
- advanced (20%): Performance analysis

## Quality Rules

- Include tracing examples
- Reference APM documentation
- Tag mutable content with [MUTABLE]

## OCI CLI Syntax

### APM Domain Commands

```bash
# Create APM domain
oci apm-config domain create --compartment-id <ocid> \
  --display-name "production-apm" \
  --description "Production APM domain"

# List APM domains
oci apm-config domain list --compartment-id <ocid>

# Get APM domain
oci apm-config domain get --apm-domain-id <ocid1.apmsddk.oc1.<region>.<unique-id>>
```

### Data Keys

```bash
# List data keys
oci apm-config data-key list --apm-domain-id <ocid1.apmsddk.oc1.<region>.<unique-id>>

# Create data key
oci apm-config data-key create --apm-domain-id <ocid1.apmsddk.oc1.<region>.<unique-id>> \
  --display-name "production-key" \
  --key-type PUBLIC
```

### Span Filter

```bash
# Create span filter
oci apm-config span-filter create --apm-domain-id <ocid1.apmsddk.oc1.<region>.<unique-id>> \
  --display-name "error-filter" \
  --filter "span.kind == 'SERVER' AND error == true"
```

### Metric Archive

```bash
# Create metric archive
oci apm-analytics metric-archive create --apm-domain-id <ocid1.apmsddk.oc1.<region>.<unique-id>> \
  --display-name "daily-metrics" \
  --namespace "apm.custom.metrics"
```

## OCID Format

```
APM Domain: ocid1.apmsddk.oc1.<region>.<unique-id>
APM Metric: ocid1.apmmetric.oc1.<region>.<unique-id>
```

## Anti-Patterns

- NEVER create APM configurations without a valid APM domain
- NEVER use real OCIDs — always use placeholders like `<ocid1.apmsddk.oc1.<region>.<unique-id>>`
- NEVER omit `--compartment-id` — required for all operations
- NEVER copy OCI documentation verbatim — generate original examples
- NEVER use synthetic traces only — real tracing is preferred
- NEVER skip data key configuration — agents require valid keys
- NEVER create spans without proper span.kind — SERVER, CLIENT, PRODUCER, CONSUMER
- NEVER use vague filter names — use descriptive names like "payment-service-error-filter"
- NEVER omit span attributes — always include service.name, span.name, error.stack
- NEVER forget to configure APM agent — Java, Node.js, Python agents need proper setup
