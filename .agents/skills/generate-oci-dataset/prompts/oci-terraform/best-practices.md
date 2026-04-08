# Prompt Template: oci-terraform/best-practices

## Context

Generate examples about OCI Terraform best practices.

## Topics

- State management (local vs remote)
- Remote state with OCI Object Storage
- Workspaces
- Sentinel policies (governance)
- Drift detection
- Code organization
- Terraform vs Resource Manager
- Variable management
- Output configuration

## Difficulty Distribution

- beginner (30%): Basic state management
- intermediate (50%): Remote state, workspaces
- advanced (20%): Sentinel, governance

## Quality Rules

- Include state configuration examples
- Reference OCI best practices
- Tag mutable content with [MUTABLE]
- ALWAYS include provider block in examples

## Required Remote State Syntax

```hcl
terraform {
  backend "s3" {
    bucket         = "terraform-state-bucket"
    key            = "project/terraform.tfstate"
    region         = "us-phoenix-1"
    # For OCI Object Storage, use oss backend instead:
    # backend "oss" {
    #   bucket = "terraform-state"
    #   prefix = "env:/"
    # }
  }
}

# OCI Object Storage Backend
terraform {
  backend "oci" {
    bucket   = "terraform-state-bucket"
    prefix   = "production/"
  }
}
```

## Required Workspace Syntax

```hcl
terraform {
  backend "oci" {
    bucket   = "terraform-state-bucket"
    prefix   = "workspace/"
  }
}

# Create workspace
resource "oci_resourcemanager_workspace" "example" {
  compartment_id = var.compartment_ocid
  display_name   = "example-workspace"
}
```

## Required Sentinel Syntax

```hcl
# Sentinel policy example for OCI
import "tfplan/v2" as tfplan

main = rule {
  all tfplan.resource_changes as _, rc {
    all rc.change.after as _, attr {
      if attr["compartment_id"] else false {
        attr["compartment_id"] == "ocid1.compartment.oc1..example"
      }
    }
  }
}
```

## Anti-Patterns

NEVER generate or include:
- **AWS S3 for remote state with OCI**: Use OCI Object Storage backend, not AWS S3
- **AWS workspaces**: Use OCI Resource Manager workspaces, not AWS workspaces
- **AWS Sentinel equivalent**: OCI uses different governance - do not mention AWS Config Rules
- **Local state for production**: Always use remote state for production
- **Hardcoded state bucket names**: Use variables for bucket names
- **Cross-cloud backend**: Do not use AWS, GCP, or Azure backends for OCI state
- **Missing state encryption**: OCI Object Storage supports encryption - ensure it's enabled
- **State files in version control**: Never commit .tfstate files to git
- **Sensitive values in plain text**: Use sensitive variables, never expose secrets in outputs

## Example Questions

- "Configurar remote state no OCI"
- "Usar workspaces no Terraform"
- "Implementar Sentinel policies no OCI"
- "Organizar código Terraform para OCI"
- "Detectar drift de recursos OCI"
- "Usar Resource Manager vs Terraform"
