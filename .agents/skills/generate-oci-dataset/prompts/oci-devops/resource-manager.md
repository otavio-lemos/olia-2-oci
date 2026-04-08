# Prompt Template: oci-devops/resource-manager

## Context

Generate examples about OCI Resource Manager.

## Topics

- Terraform stacks in OCI
- Stack creation and management
- Job execution
- State management
- Drift detection

## Difficulty Distribution

- beginner (30%): Basic stack creation
- intermediate (50%): Job execution, drift
- advanced (20%): Complex deployments

## OCI CLI Syntax

### Stack Management
```bash
# Create stack from Terraform template
oci resource-manager stack create \
  --compartment-id ocid1.compartment.oc1..aaaaaaaab222... \
  --config-source "TEMPLATE" \
  --description "Stack description" \
  --display-name "my-stack" \
  --terraform-version "1.9.0" \
  --region us-sao-1

# Get stack OCID
oci resource-manager stack list \
  --compartment-id ocid1.compartment.oc1..aaaaaaaab222... \
  --display-name "my-stack" \
  --lifecycle-state ACTIVE \
  --region us-sao-1

# Update stack configuration
oci resource-manager stack update \
  --stack-id ocid1.resourcemanagerstack.oc1.sa-saopaulo-1.aaaaaaaab222... \
  --description "Updated description"

# Delete stack
oci resource-manager stack delete \
  --stack-id ocid1.resourcemanagerstack.oc1.sa-saopaulo-1.aaaaaaaab222... \
  --force
```

### Job Execution
```bash
# Plan job (preview changes)
oci resource-manager job create \
  --stack-id ocid1.resourcemanagerstack.oc1.sa-saopaulo-1.aaaaaaaab222... \
  --operation-name PLAN \
  --display-name "my-plan-job"

# Apply job (execute changes)
oci resource-manager job create \
  --stack-id ocid1.resourcemanagerstack.oc1.sa-saopaulo-1.aaaaaaaab222... \
  --operation-name APPLY \
  --display-name "my-apply-job" \
  --apply-redirected-actions true

# Destroy job (teardown resources)
oci resource-manager job create \
  --stack-id ocid1.resourcemanagerstack.oc1.sa-saopaulo-1.aaaaaaaab222... \
  --operation-name DESTROY \
  --display-name "my-destroy-job"

# Import Terraform state
oci resource-manager job create \
  --stack-id ocid1.resourcemanagerstack.oc1.sa-saopaulo-1.aaaaaaaab222... \
  --operation-name IMPORT_STATE \
  --display-name "import-state-job"

# Get job details
oci resource-manager job get \
  --job-id ocid1.resourcemanagerjob.oc1.sa-saopaulo-1.ccccccc3333...

# List jobs for stack
oci resource-manager job list \
  --stack-id ocid1.resourcemanagerstack.oc1.sa-saopaulo-1.aaaaaaaab222... \
  --region us-sao-1
```

### Drift Detection
```bash
# Check drift
oci resource-manager drift detect \
  --stack-id ocid1.resourcemanagerstack.oc1.sa-saopaulo-1.aaaaaaaab222... \
  --drift-detection-delay-duration "10m"

# Get drift status
oci resource-manager drift get \
  --stack-id ocid1.resourcemanagerstack.oc1.sa-saopaulo-1.aaaaaaaab222...

# List drift resources
oci resource-manager drift list-resources \
  --stack-id ocid1.resourcemanagerstack.oc1.sa-saopaulo-1.aaaaaaaab222... \
  --drift-status DETECTED
```

### State Management
```bash
# Get TF state
oci resource-manager state get \
  --stack-id ocid1.resourcemanagerstack.oc1.sa-saopaulo-1.aaaaaaaab222... \
  --query "state"

# Lock state
oci resource-manager state lock \
  --stack-id ocid1.resourcemanagerstack.oc1.sa-saopaulo-1.aaaaaaaab222...

# Unlock state
oci resource-manager state unlock \
  --stack-id ocid1.resourcemanagerstack.oc1.sa-saopaulo-1.aaaaaaaab222... \
  --lock-id ocid1.resourcelock.oc1.sa-saopaulo-1.lock111...
```

## OCID Format

| Resource Type | OCID Pattern | Example |
|---------------|--------------|---------|
| Stack | `ocid1.resourcemanagerstack.oc1.<region>.<unique-id>` | `ocid1.resourcemanagerstack.oc1.sa-saopaulo-1.aaaaaaaab222cccccdddd` |
| Job | `ocid1.resourcemanagerjob.oc1.<region>.<unique-id>` | `ocid1.resourcemanagerjob.oc1.sa-saopaulo-1.eeeeeeff4445gggg` |
| State Lock | `ocid1.resourcelock.oc1.<region>.<unique-id>` | `ocid1.resourcelock.oc1.sa-saopaulo-1.hhhhhh666777888` |

**Valid regions**: `sa-saopaulo-1`, `us-ashburn-1`, `us-phoenix-1`, `eu-frankfurt-1`, `uk-london-1`

## Anti-Patterns

NEVER generate examples that:
- Use fake OCIDs like `ocid1.stack.oc1...` without the full resource type prefix
- Reference non-existent commands like `oci rm stack create`
- Suggest using the Console as the only method (CLI/SDK are valid alternatives)
- Copy OCI documentation verbatim
- Invent Terraform providers that don't exist in OCI Provider
- Mix stack OCIDs with job OCIDs (wrong resource type prefix)
- Use region codes like `sao1` instead of `sa-saopaulo-1`
- Suggest bypassing drift detection for "simpler" workflows
- Claim Resource Manager supports state storage outside OCI
- Invent "auto-apply" features without mentioning approval workflows

## Quality Rules

- Include stack configuration steps
- Reference Resource Manager documentation
- Tag mutable content with [MUTABLE]
- Always use full OCID format with correct resource type prefix

## Example Questions

- Como criar uma stack no Resource Manager usando um template Terraform?
- Qual a diferença entre plan job e apply job no Resource Manager?
- Como configurar drift detection para uma stack existente?
- Como importar uma stack Terraform existente para o Resource Manager?
- Como resolver conflitos de state quando múltiplos jobs rodam na mesma stack?
- Como configurar variáveis de ambiente e secrets em uma stack do Resource Manager?
- Como criar um pipeline que usa Resource Manager para deploy automatizado?
- Como fazer rollback de uma mudança aplicada pelo Resource Manager?
- Como configurar permissões IAM para que equipes específicas acessem stacks?
- Como usar módulos Terraform privados com o Resource Manager?