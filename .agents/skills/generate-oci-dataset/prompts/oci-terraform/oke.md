# Prompt Template: oci-terraform/oke

## Context

Generate examples about OCI OKE (Oracle Kubernetes Engine) with Terraform.

## Topics

- OKE cluster creation
- Node pools configuration
- OCI Kubernetes Engine resources
- Kubernetes manifests vs Terraform
- CNI configuration
- Add-ons
- OKE cluster scaling
- VCN integration for OKE

## Difficulty Distribution

- beginner (30%): Basic OKE creation
- intermediate (50%): Node pools, configuration
- advanced (20%): Advanced networking, add-ons, cluster upgrades

## Quality Rules

- Include OKE resource examples using `oci_container_cluster`
- Reference Container Engine documentation
- Tag mutable content with [MUTABLE]
- ALWAYS include provider block in examples

## Required Provider Syntax

```hcl
provider "oci" {
  tenancy_ocid     = var.tenancy_ocid
  user_ocid       = var.user_ocid
  fingerprint     = var.fingerprint
  private_key_path = var.private_key_path
  region           = var.region
}
```

## Required Resource Syntax

```hcl
resource "oci_container_cluster" "example" {
  compartment_id = var.compartment_ocid
  name           = "example-cluster"
  kubernetes_version = "v1.28.2"
  vcn_id          = oci_core_vcn.example.id
  endpoint_config {
    subnet_id = oci_core_subnet.example.id
  }
}

resource "oci_container_node_pool" "example" {
  cluster_id         = oci_container_cluster.example.id
  compartment_id     = var.compartment_ocid
  name               = "example-nodepool"
  kubernetes_version = "v1.28.2"
  node_shape         = "VM.Standard.E4.Flex"
  node_shape_config {
    ocpus   = 2
    memory_in_gbs = 16
  }
  node_count = 3
}
```

## Anti-Patterns

NEVER generate or include:
- **AWS resources**: `aws_eks_cluster`, `aws_eks_node_group`, `aws_instance`
- **GCP resources**: `google_container_cluster`, `google_container_node_pool`
- **Azure resources**: `azurerm_kubernetes_cluster`, `azurerm_kubernetes_node_pool`
- **Generic Kubernetes without provider**: Always use `oci_container_cluster` and `oci_container_node_pool`
- **EKS/GKE/AKS terminology**: Do not mention EKS, GKE, or AKS as alternatives
- **Cross-cloud patterns**: Do not suggest using Terraform modules from other clouds
- **Hardcoded OCIDs**: Always use variables for tenancy_ocid, compartment_ocid

## Example Questions

- "Criar cluster OKE com Terraform"
- "Configurar node pool com Terraform"
- "Adicionar cluster add-ons via Terraform"
- "Configurar endpoint OKE com subnet dedicada"
- "Escalar node pool automaticamente"
