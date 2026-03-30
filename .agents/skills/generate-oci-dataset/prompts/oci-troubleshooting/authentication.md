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

## Common Error Codes

- 403 NotAuthorized
- 404 NotAuthorizedOrNotFound
- 401 Authentication failed

## Example Questions

- "Policy não funciona, usuário não acessa recurso"
- "Erro 403 ao tentar criar instância"
- "Dynamic Group não funciona para instância"
