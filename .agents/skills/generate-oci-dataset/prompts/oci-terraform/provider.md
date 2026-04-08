# Prompt Template: oci-terraform/provider

## Context

Generate examples about OCI Terraform provider configuration.

## Topics

- Provider configuration
- Authentication (API key, instance principal, resource principal)
- Region configuration
- Tenancy OCID
- Provider version
- Multiple provider configurations
- Alias providers

## Difficulty Distribution

- beginner (40%): Basic provider setup
- intermediate (40%): Authentication methods
- advanced (20%): Advanced configuration, aliases

## Quality Rules

- Use correct Terraform provider resource names
- Include provider block examples with all required fields
- Tag mutable content with [MUTABLE]
- Reference Terraform OCI provider docs

## Required Provider Syntax

```hcl
provider "oci" {
  tenancy_ocid     = var.tenancy_ocid
  user_ocid       = var.user_ocid
  fingerprint     = var.fingerprint
  private_key_path = var.private_key_path
  region           = var.region
}

# Alternative: Instance Principal
provider "oci" {
  tenancy_ocid = var.tenancy_ocid
  region       = var.region
  auth = "InstancePrincipal"
}

# Alternative: Resource Principal
provider "oci" {
  tenancy_ocid = var.tenancy_ocid
  region       = var.region
  auth = "ResourcePrincipal"
}

# Alias for secondary region
provider "oci" "secondary" {
  tenancy_ocid     = var.tenancy_ocid
  user_ocid       = var.user_ocid
  fingerprint     = var.fingerprint
  private_key_path = var.private_key_path
  region           = "us-ashburn-1"
}
```

## Anti-Patterns

NEVER generate or include:
- **AWS provider**: `provider "aws"`
- **GCP provider**: `provider "google"`
- **Azure provider**: `provider "azurerm"`
- **Missing required fields**: Always include tenancy_ocid, user_ocid, fingerprint, private_key_path, region
- **Hardcoded credentials**: Never hardcode OCIDs, fingerprints, or private keys - use variables
- **Deprecated authentication**: Do not use user_password auth (deprecated)
- **Incorrect provider name**: Always use `provider "oci"` not `provider "oraclecloud"` or similar
- **Cross-cloud authentication patterns**: Do not mix AWS IAM roles with OCI provider

## Example Questions

- "Configurar provider OCI com API key"
- "Autenticação via instance principal"
- "Como usar provider com múltiplas regiões?"
- "Configurar provider com variáveis de ambiente"
- "Usar OCI provider com alias"
