# Prompt Template: oci-terraform/resources

## Context

Generate examples about OCI Terraform resources.

## Topics

- compute instance
- vcn, subnet
- iam policy
- object storage bucket
- block volume

## Difficulty Distribution

- beginner (30%): Basic resource creation
- intermediate (50%): Complex resources, dependencies
- advanced (20%): Modules, best practices

## Quality Rules

- Use correct Terraform resource names (oci_core_instance, not oci_instance)
- Include provider configuration
- Tag mutable content with [MUTABLE]
