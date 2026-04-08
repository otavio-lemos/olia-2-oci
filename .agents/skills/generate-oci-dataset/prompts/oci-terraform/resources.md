# Prompt Template: oci-terraform/resources

## Context

Generate examples about OCI Terraform resources.

## Topics

- compute instance (oci_core_instance)
- vcn, subnet (oci_core_vcn, oci_core_subnet)
- iam policy (oci_identity_policy)
- object storage bucket (oci_objectstorage_bucket)
- block volume (oci_core_volume)
- database (oci_database_db_system)
- load balancer (oci_load_balancer_load_balancer)
- KMS vault and keys (oci_kms_vault, oci_kms_key)

## Difficulty Distribution

- beginner (30%): Basic resource creation
- intermediate (50%): Complex resources, dependencies
- advanced (20%): Modules, best practices

## Quality Rules

- Use correct Terraform resource names (oci_core_instance, not oci_instance)
- Include provider configuration
- Tag mutable content with [MUTABLE]
- ALWAYS include provider block in examples

## Required Resource Syntax - Compute

```hcl
resource "oci_core_instance" "example" {
  compartment_id = var.compartment_ocid
  display_name   = "example-instance"
  shape          = "VM.Standard.E4.Flex"
  shape_config {
    ocpus   = 2
    memory_in_gbs = 16
  }
  source_details {
    source_type = "image"
    image_ocid  = var.image_ocid
  }
  subnet_id = oci_core_subnet.example.id
}
```

## Required Resource Syntax - VCN

```hcl
resource "oci_core_vcn" "example" {
  compartment_id = var.compartment_ocid
  display_name   = "example-vcn"
  cidr_block    = "10.0.0.0/16"
}

resource "oci_core_subnet" "example" {
  compartment_id = var.compartment_ocid
  display_name   = "example-subnet"
  vcn_id         = oci_core_vcn.example.id
  cidr_block    = "10.0.1.0/24"
}
```

## Required Resource Syntax - Object Storage

```hcl
resource "oci_objectstorage_bucket" "example" {
  compartment_id = var.compartment_ocid
  name           = "example-bucket"
  namespace      = var.namespace
  compartment_id = var.compartment_ocid
}
```

## Required Resource Syntax - Database

```hcl
resource "oci_database_db_system" "example" {
  compartment_id     = var.compartment_ocid
  display_name       = "example-db"
  availability_domain = var.availability_domain
  shape              = "VM.Standard.E4.Flex"
  db_home {
    database_version = "19c"
    db_system_image_id = var.db_system_image_id
  }
  cpu_core_count = 2
  memory_size_in_gbs = 32
  storage_size_in_gbs = 256
  subnet_id = oci_core_subnet.example.id
}
```

## Anti-Patterns

NEVER generate or include:
- **AWS resources**: `aws_instance`, `aws_vpc`, `aws_subnet`, `aws_s3_bucket`, `aws_db_instance`, `aws_lb`
- **GCP resources**: `google_compute_instance`, `google_vpc`, `google_storage_bucket`, `google_sql_database_instance`
- **Azure resources**: `azurerm_virtual_machine`, `azurerm_virtual_network`, `azurerm_storage_account`, `azurerm_sql_database`
- **Wrong OCI resource names**: `oci_instance` (wrong), `oci_vcn` (wrong), `oci_subnet` (wrong) - must use `oci_core_*`
- **Incorrect database resource**: `oci_database_instance` (wrong) - use `oci_database_db_system`
- **Hardcoded OCIDs**: Always use variables for all OCIDs
- **Cross-cloud resource references**: Do not reference resources from other clouds in dependencies

## Example Questions

- "Criar instância compute com Terraform"
- "Criar VCN com subnets públicas e privadas"
- "Criar bucket Object Storage"
- "Criar política IAM para acesso a recursos"
- "Configurar block volume para instância"
