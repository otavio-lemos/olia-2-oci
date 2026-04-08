# Prompt Template: oci-core/serverless

## Context

Generate examples about OCI serverless services including Functions and API Gateway.

## Topics

- OCI Functions (function creation, invocation)
- API Gateway
- Fn Project
- Cold starts

## Difficulty Distribution

- beginner (30%): Basic function creation
- intermediate (50%): API Gateway configuration
- advanced (20%): Performance tuning, integration

## Quality Rules

- Use correct OCI terminology
- Include function invocation examples
- Tag mutable content with [MUTABLE]

## OCI CLI Syntax

Use these commands as reference:

```bash
# Create Application
oci fn application create \
  --compartment-id ocid1.compartment.oc1.<region>.<unique-id> \
  --display-name "my-functions-app" \
  --subnet-ids '["ocid1.subnet.oc1.<region>.<unique-id>"]' \
  --config '{"ENV_VAR": "value"}'

# Create Function
oci fn function create \
  --application-id ocid1.functionapp.oc1.<region>.<unique-id> \
  --display-name "my-function" \
  --image "iad.ocir.io/<namespace>/my-function-image:latest" \
  --memory-mb 256 \
  --timeout-seconds 30 \
  --config '{"FN_INTENT": "http", "FN_ENDPOINT_TYPE": "detached"}'

# Update Function Configuration
oci fn function update \
  --function-id ocid1.function.oc1.<region>.<unique-id> \
  --config '{"NEW_CONFIG": "value"}'

# Invoke Function
oci fn function invoke \
  --function-id ocid1.function.oc1.<region>.<unique-id> \
  --invoke-body '{"key": "value"}' \
  --header 'Content-Type: application/json'

# List Functions
oci fn function list \
  --application-id ocid1.functionapp.oc1.<region>.<unique-id>

# Create API Gateway
oci apigateway gateway create \
  --compartment-id ocid1.compartment.oc1.<region>.<unique-id> \
  --display-name "my-api-gateway" \
  --subnet-ids '["ocid1.subnet.oc1.<region>.<unique-id>"]' \
  --endpoint-type "PUBLIC" \
  --certificate-ids '["ocid1.certificate.oc1.<region>.<unique-id>"]'

# Create Deployment (API Gateway)
oci apigateway deployment create \
  --gateway-id ocid1.apigateway.oc1.<region>.<unique-id> \
  --display-name "my-deployment" \
  --path-prefix "/api" \
  --specification '{"routes": [{"path": "/functions/{path}", "methods": ["GET", "POST"], "backend": {"type": "ORACLE_FUNCTIONS", "functionId": "ocid1.function.oc1.<region>.<unique-id>"}}]}'
```

## OCID Format

Always use these patterns:

- Application: `ocid1.functionapp.oc1.<region>.<unique-id>`
- Function: `ocid1.function.oc1.<region>.<unique-id>`
- API Gateway: `ocid1.apigateway.oc1.<region>.<unique-id>`
- Deployment: `ocid1.apigatewaydeployment.oc1.<region>.<unique-id>`
- Subnet: `ocid1.subnet.oc1.<region>.<unique-id>`
- Compartment: `ocid1.compartment.oc1.<region>.<unique-id>`
- Certificate: `ocid1.certificate.oc1.<region>.<unique-id>`

## Anti-Patterns

NEVER generate:
- Using `--function-id` instead of `--application-id` for function create
- Invalid memory values (must be: 128, 256, 512, 1024, 2048)
- Timeout exceeding 300 seconds
- Using private endpoint without proper VCN configuration
- Creating API Gateway without certificates for HTTPS
- Invalid route path patterns
- Mixing OCI Functions terminology with AWS Lambda
- Creating functions without specifying image
- Forgetting to set `FN_INTENT: http` for HTTP-triggered functions
- Invoking functions without proper authentication

## Example Questions

- "Como criar uma Function no OCI?"
- "Configurar API Gateway para invocar Function"
- "Como resolver cold start em Functions?"