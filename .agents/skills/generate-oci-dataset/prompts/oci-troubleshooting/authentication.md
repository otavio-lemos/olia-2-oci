# Prompt Template: oci-troubleshooting/authentication

## Context

Generate examples about troubleshooting OCI IAM and authentication issues.

## Topics

- IAM policy permission denied
- Dynamic Group evaluation issues
- MFA problems
- Federation failures (IdCS, Okta)
- Token expiration issues
- "NotAuthorized" errors
- Policy syntax errors

## Difficulty Distribution

- beginner (20%): Basic permission issues
- intermediate (50%): Policy debugging, dynamic groups
- advanced (30%): Federation, complex policy scenarios

## Quality Rules

- Provide step-by-step troubleshooting
- Include policy syntax examples
- Reference specific OCI resources
- Explain policy evaluation order

## OCI Diagnostic CLI Syntax

Use these real OCI CLI commands for IAM troubleshooting:

```bash
# User and group info
iam user get --user-id ocid1.user.oc1.<region>.<unique-id>
iam group list --compartment-id ocid1.compartment.oc1.<region>.<unique-id>

# Policy inspection
iam policy get --policy-id ocid1.policy.oc1.<region>.<unique-id>
iam policy list --compartment-id ocid1.compartment.oc1.<region>.<unique-id>

# Dynamic Group
iam dynamic-group get --dynamic-group-id ocid1.dynamicgroup.oc1.<region>.<unique-id>
iam dynamic-group list --compartment-id ocid1.compartment.oc1.<region>.<unique-id>

# Compartment access
iam compartment get --compartment-id ocid1.compartment.oc1.<region>.<unique-id>
iam compartment list --compartment-id ocid1.tenancy.oc1.<region>.<unique-id>

# API Key validation
iam user api-key list --user-id ocid1.user.oc1.<region>.<unique-id>
iam auth-token list --user-id ocid1.user.oc1.<region>.<unique-id>

# Service principal
iam service get --service-id ocid1.service.oc1.<region>.<unique-id>

# Session token
iam session-token create

# Simulate policy (check access)
iam policy simulate --statement "ALLOW group <group> TO <verb> <resource-type> IN compartment <compartment>"

# MFA status
iam user mfa-status get --user-id ocid1.user.oc1.<region>.<unique-id>

# Federation (IdCS/Okta)
iam identity-provider get --identity-provider-id ocid1.identityprovider.oc1.<region>.<unique-id>

# Credential report
iam credential-report get --user-id ocid1.user.oc1.<region>.<unique-id>
```

## OCID Format

OCI resource identifiers follow this pattern:

```
ocid1.<resource-type>.<realm>.<region>.<unique-id>

Examples:
- ocid1.user.oc1.sa-vinhedo-1.abcd1234...
- ocid1.group.oc1.sa-vinhedo-1.abcd1234...
- ocid1.policy.oc1.sa-vinhedo-1.abcd1234...
- ocid1.dynamicgroup.oc1.sa-vinhedo-1.abcd1234...
- ocid1.compartment.oc1.sa-vinhedo-1.abcd1234...
- ocid1.identityprovider.oc1.sa-vinhedo-1.abcd1234...

Policy format:
Allow <subject> to <verb> <resource-type> in <location> where <condition>
```

## Anti-Patterns

**NEVER generate:**

- ❌ Policy syntax without proper OCI verbs (GET, LIST, CREATE, UPDATE, DELETE, INSPECT)
- ❌ "NotAuthorized" errors without explaining the evaluation path
- ❌ Dynamic Group matching without showing matching rules
- ❌ MFA troubleshooting without mentioning recovery options
- ❌ Federation without mentioning IdCS/Okta specifics
- ❌ Copy OCI documentation verbatim
- ❌ "Just add to Admin group" without explaining security implications
- ❌ Policy conditions without mentioning supported operators
- ❌ Never suggest sharing credentials or bypassing auth

## Common Error Codes

- 403 NotAuthorized - insufficient permissions
- 404 NotAuthorizedOrNotFound - resource doesn't exist or no permission
- 401 Authentication failed - invalid credentials or token expired
- 409 NotAuthorizedOrResourceAlreadyExists - conflict in create operations

## Example Questions

- "Policy não funciona, usuário não acessa recurso"
- "Erro 403 ao tentar criar instância"
- "Dynamic Group não funciona para instância"
- "Token expirado, como renovar?"
- "MFA não funciona, como recuperar?"