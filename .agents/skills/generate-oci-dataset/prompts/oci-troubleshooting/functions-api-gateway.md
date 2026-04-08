# Prompt Template: oci-troubleshooting/functions-api-gateway

## Context

Generate examples about troubleshooting OCI Functions and API Gateway issues.

## Topics

- Function invocation errors
- API Gateway 502/504 errors
- Function timeout issues
- Cold start problems
- Authentication issues
- Request/response mapping

## Difficulty Distribution

- beginner (30%): Basic function invocation
- intermediate (50%): API Gateway configuration
- advanced (20%): Performance, cold start

## Quality Rules

- Include function invoke examples
- Reference API Gateway configuration
- Explain cold start behavior

## OCI Diagnostic CLI Syntax

Use these real OCI CLI commands for Functions/API Gateway troubleshooting:

```bash
# Function details
oci fn function get --function-id ocid1.func.oc1.<region>.<unique-id>
oci fn function list --application-id ocid1.application.oc1.<region>.<unique-id>

# Application info
oci fn application get --application-id ocid1.application.oc1.<region>.<unique-id>

# Function invoke
oci fn function invoke --function-id ocid1.func.oc1.<region>.<unique-id> --body '{"key": "value"}' \
  --endpoint "https://function-endpoint.oraclecloud.com"

# Function logs (via OCI Logging)
oci logging log list --log-group-id ocid1.loggroup.oc1.<region>.<unique-id> --source-type FUNCTION

# API Gateway
oci api-gateway gateway get --gateway-id ocid1.apigateway.oc1.<region>.<unique-id>
oci api-gateway gateway list --compartment-id ocid1.compartment.oc1.<region>.<unique-id>

# Deployment
oci api-gateway deployment get --deployment-id ocid1.deployment.oc1.<region>.<unique-id>

# API Gateway logs
oci logging log list --log-group-id ocid1.loggroup.oc1.<region>.<unique-id> \
  --source-type APIGATEWAY

# Function metrics
oci monitoring metric-data get --compartment-id ocid1.compartment.oc1.<region>.<unique-id> \
  --metric-name "FunctionInvokeDuration" \
  --resource-id ocid1.func.oc1.<region>.<unique-id>

# Invoke metrics
oci monitoring metric-data get --compartment-id ocid1.compartment.oc1.<region>.<unique-id> \
  --metric-name "FunctionInvocations" \
  --resource-id ocid1.func.oc1.<region>.<unique-id>

# VCN config for function (if using private endpoints)
oci network private-endpoint get --private-endpoint-id ocid1.privateendpoint.oc1.<region>.<unique-id>
```

## OCID Format

OCI resource identifiers follow this pattern:

```
ocid1.<resource-type>.<realm>.<region>.<unique-id>

Examples:
- ocid1.func.oc1.sa-vinhedo-1.abcd1234...
- ocid1.application.oc1.sa-vinhedo-1.abcd1234...
- ocid1.apigateway.oc1.sa-vinhedo-1.abcd1234...
- ocid1.deployment.oc1.sa-vinhedo-1.abcd1234...

Function invoke URL format:
https://<fn-app-ocid>.<region>.functions.oci.oraclecloud.com/<function-name>

API Gateway URL format:
https://<gateway-ocid>.<region>.apigateway.oci.oraclecloud.com/<path>
```

## Anti-Patterns

**NEVER generate:**

- ❌ Function errors without mentioning logs
- ❌ API Gateway 502 without checking backend function health
- ❌ Timeout issues without mentioning execution time limits [MUTABLE]
- ❌ Cold start without explaining container lifecycle
- ❌ "Just increase timeout" without understanding root cause
- ❌ Copy OCI documentation verbatim
- ❌ Authentication without mentioning OCI IAM policies for functions
- ❌ Request mapping without showing actual API Gateway config
- ❌ Performance tuning without mentioning memory allocation

## Common Issues

- Function returns 500 Internal Server Error
- API Gateway returns 502 Bad Gateway
- Function times out (max 30 seconds for sync, 300 for async)
- Cold start too slow (first invocation after idle)
- Invalid function response format
- Authentication failures (missing IAM policy)

## Example Questions

- "Function retorna erro 500"
- "API Gateway retorna 502 Bad Gateway"
- "Como debugar OCI Function?"
- "Function timeout após 30 segundos"
- "Cold start muito lento"