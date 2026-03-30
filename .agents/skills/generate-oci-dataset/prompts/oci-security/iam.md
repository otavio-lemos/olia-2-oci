# Prompt Template: oci-security/iam

## Context

Generate examples about OCI IAM including compartments, policies, groups, users, dynamic groups, authentication, MFA.

## Topics

- Compartments (hierarchy, naming conventions)
- Policies (syntax, permissions, compartments vs tenancy)
- Groups and Users
- Dynamic Groups
- Federation (IDCS, Okta)
- MFA and authentication
- Service principals

## Difficulty Distribution

- beginner (30%): Basic compartment creation, user management
- intermediate (40%): Policy syntax, groups
- advanced (30%): Dynamic groups, federation, complex policy architectures

## Quality Rules

- Use correct terminology: compartment, policy, group (not "folder", "permission")
- Explain difference between tenancy-level and compartment-level policies
- Include real policy syntax examples
- Tag mutable content (limits, quotas) with [MUTABLE]
- Reference actual OCI service limits
