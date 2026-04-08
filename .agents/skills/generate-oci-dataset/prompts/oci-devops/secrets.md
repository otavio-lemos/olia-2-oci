# Prompt Template: oci-devops/secrets

## Context

Generate examples about integrating OCI Vault with DevOps pipelines.

## Topics

- OCI Vault integration with DevOps
- Secret injection in pipelines
- Secure parameter storage
- Environment variables
- API key management

## Difficulty Distribution

- beginner (40%): Basic secret usage
- intermediate (40%): Pipeline integration
- advanced (20%): Advanced security patterns

## OCI CLI Syntax

### Vault Operations
```bash
# Create vault
oci vault vault create \
  --compartment-id ocid1.compartment.oc1..aaaaaaaab222... \
  --display-name "devops-vault" \
  --vault-type DEFAULT \
  --region us-sao-1

# List vaults
oci vault vault list \
  --compartment-id ocid1.compartment.oc1..aaaaaaaab222... \
  --lifecycle-state ACTIVE

# Get vault OCID
oci vault vault get \
  --vault-id ocid1.vault.oc1.sa-saopaulo-1.vvvvvv...
```

### Secret Management
```bash
# Create secret
oci vault secret create \
  --vault-id ocid1.vault.oc1.sa-saopaulo-1.vvvvvv... \
  --secret-name "db-password" \
  --secret-content " encrypted-content-here " \
  --secret-content-type BASE64 \
  --description "Database password for app" \
  --region us-sao-1

# Get secret OCID
oci vault secret list \
  --vault-id ocid1.vault.oc1.sa-saopaulo-1.vvvvvv... \
  --lifecycle-state ACTIVE

# Get secret value (requires read permission)
oci vault secret get-content \
  --secret-id ocid1.secret.oc1.sa-saopaulo-1.ssssss... \
  --region us-sao-1

# Update secret (new version)
oci vault secret update \
  --secret-id ocid1.secret.oc1.sa-saopaulo-1.ssssss... \
  --secret-content "new-encrypted-content" \
  --region us-sao-1

# Rotate secret
oci vault secret rotate \
  --secret-id ocid1.secret.oc1.sa-saopaulo-1.ssssss... \
  --secret-content "new-version-content" \
  --region us-sao-1
```

### Secrets in DevOps Pipeline
```bash
# Create DevOps secret (wraps Vault)
oci devops artifact create \
  --project-id ocid1.devopsproject.oc1.sa-saopaulo-1.aaaaaaaab222... \
  --display-name "db-password" \
  --artifact-type OCI_VAULT_SECRET \
  --artifact-ocid ocid1.secret.oc1.sa-saopaulo-1.ssssss... \
  --region us-sao-1

# Add as environment variable in deploy stage
# Via OCI Console UI - cannot set via CLI
# Add to deploy pipeline stage configuration:
# ${oci://vault://secret://ocid1.secret.oc1.sa-saopaulo-1.ssssss.@@}

# List secrets in DevOps
oci devops artifact list \
  --project-id ocid1.devopsproject.oc1.sa-saopaulo-1.aaaaaaaab222... \
  --artifact-type OCI_VAULT_SECRET
```

### Key Management
```bash
# Create key
oci vault key create \
  --vault-id ocid1.vault.oc1.sa-saopaulo-1.vvvvvv... \
  --display-name "signing-key" \
  --key-version-reference "1" \
  --region us-sao-1

# List keys
oci vault key list \
  --vault-id ocid1.vault.oc1.sa-saopaulo-1.vvvvvv... \
  --lifecycle-state ACTIVE

# Rotate key
oci vault key rotate \
  --key-id ocid1.key.oc1.sa-saopaulo-1.kkkkkk... \
  --key-version-reference "2" \
  --region us-sao-1
```

### Dynamic Group for Access
```bash
# Get dynamic group OCID
oci iam dynamic-group get \
  --dynamic-group-id ocid1.dynamicgroup.oc1.sa-saopaulo-1.dddddd...

# List dynamic groups
oci iam dynamic-group list \
  --compartment-id ocid1.compartment.oc1..aaaaaaaab222...
```

## OCID Format

| Resource Type | OCID Pattern | Example |
|---------------|--------------|---------|
| Vault | `ocid1.vault.oc1.<region>.<unique-id>` | `ocid1.vault.oc1.sa-saopaulo-1.vvvvvv111222333` |
| Secret | `ocid1.secret.oc1.<region>.<unique-id>` | `ocid1.secret.oc1.sa-saopaulo-1.ssssss444555666` |
| Key | `ocid1.key.oc1.<region>.<unique-id>` | `ocid1.key.oc1.sa-saopaulo-1.kkkkkk777888999` |
| Dynamic Group | `ocid1.dynamicgroup.oc1.<region>.<unique-id>` | `ocid1.dynamicgroup.oc1.sa-saopaulo-1.dddddd000111222` |
| Policy | `ocid1.policy.oc1.<region>.<unique-id>` | `ocid1.policy.oc1.sa-saopaulo-1.pppppp333444555` |

## IAM Policy for Vault Access

```bash
# Allow DevOps to read secrets
Allow dynamic-group <group-name> to read secret-content in compartment <compartment-name>

# Allow instance to access secrets
Allow dynamic-group <instance-group> to use secret-family in compartment <compartment-name>

# Full secret access
Allow any-user to read secrets in compartment <compartment-name>
```

## Anti-Patterns

NEVER generate examples that:
- Use fake OCIDs like `ocid1.key.oc1...` without full resource type prefix
- Use Vault secrets directly without dynamic groups/policies
- Suggest putting secrets in pipeline environment variables directly
- Copy secret values in plain text in logs or outputs
- Reference AWS Secrets Manager or Azure Key Vault in OCI context
- Use API key as secret type in OCI Vault
- Suggest "reading from env vars" without Vault integration
- Create policies without mentioning compartment scope
- Mix up Key OCID with Secret OCID
- Suggest key rotation without version management

## Quality Rules

- Include pipeline examples
- Reference Vault integration
- Emphasize security best practices
- Always include IAM policies for Vault access
- Use secret OCID references, not hardcoded values

## Example Questions

- Como configurar secrets do OCI Vault em um pipeline de deploy do DevOps?
- Como injetar credenciais de banco de dados armazenadas no Vault durante um build?
- Como rotacionar secrets no Vault sem quebrar pipelines em execução?
- Como usar dynamic groups para permitir que instâncias acessem secrets do Vault?
- Como configurar variáveis de ambiente sensíveis em um deploy para OKE usando Vault?
- Como resolver erros de permissão quando um pipeline não consegue ler secrets do Vault?
- Como armazenar e recuperar certificados SSL do Vault para uso em deployments?
- Como configurar acesso seguro a API keys de serviços externos via Vault no DevOps?
- Como auditar acesso a secrets no Vault para compliance?
- Como usar versionamento de secrets no Vault para rollback de credenciais?