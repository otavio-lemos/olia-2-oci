# Prompt Template: oci-terraform/modules

## Context

Generate examples about OCI Terraform modules.

## Topics

- Oracle official modules
- Module usage and composition
- Reusable infrastructure patterns
- Network modules (vcn, subnets)
- Compute modules (instance, instance pool)
- Best practices for modules
- Module outputs and inputs
- Terragrunt with OCI

## Difficulty Distribution

- beginner (30%): Basic module usage
- intermediate (50%): Module composition
- advanced (20%): Custom module development

## Quality Rules

- Include module source examples using Oracle official modules
- Reference Oracle official modules from terraform-oci-modules
- Tag mutable content with [MUTABLE]
- ALWAYS include provider block in examples

## Required Module Syntax

```hcl
# Using Oracle Official VCN Module
module "vcn" {
  source  = "oracle/oci//modules/vcn"
  version = "5.0.0"
  
  compartment_id = var.compartment_ocid
  vcn_name       = "example-vcn"
  vcn_cidr       = "10.0.0.0/16"
}

# Using Oracle Official Subnets Module
module "subnets" {
  source  = "oracle/oci//modules/vcn-subnets"
  version = "5.0.0"
  
  compartment_id = var.compartment_ocid
  vcn_id         = module.vcn.vcn_id
  subnet_cidrs   = ["10.0.1.0/24", "10.0.2.0/24"]
}

# Using Oracle Official Compute Instance Module
module "instance" {
  source  = "oracle/oci//modules/instance"
  version = "5.0.0"
  
  compartment_id = var.compartment_ocid
  display_name   = "example-instance"
  shape          = "VM.Standard.E4.Flex"
  subnet_id      = module.subnets.subnets[0].id
}
```

## Oracle Official Modules List

- `oracle/oci//modules/vcn` - VCN creation
- `oracle/oci//modules/vcn-subnets` - Subnet management
- `oracle/oci//modules/instance` - Compute instance
- `oracle/oci//modules/instance-pool` - Instance pools
- `oracle/oci//modules/oke` - OKE cluster
- `oracle/oci//modules/object-storage` - Object Storage
- `oracle/oci//modules/database` - Database
- `oracle/oci//modules/load-balancer` - Load Balancer

## Anti-Patterns

NEVER generate or include:
- **AWS modules**: `terraform-aws-modules/vpc/aws`, `terraform-aws-modules/eks/aws`
- **GCP modules**: `terraform-google-modules/network/google`, `terraform-google-kubernetes-engine/google`
- **Azure modules**: `Azure/terraform-provider-azapi`, Azure official modules
- **Non-OCI modules**: Using modules from other cloud providers
- **Hardcoded module sources**: Always specify version
- **Outdated modules**: Always use recent versions (5.x for OCI modules)
- **Cross-cloud module composition**: Do not combine AWS modules with OCI resources
- **Missing provider in modules**: Always pass provider or ensure provider is inherited

## Example Questions

- "Usar módulos oficiais OCI Terraform"
- "Criar VCN com módulo Oracle"
- "Módulo para OKE cluster"
- "Criar instance pool com módulo"
- "Criar módulo custom para OCI"
