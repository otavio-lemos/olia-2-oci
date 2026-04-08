# Prompt Template: oci-security/vault

## Context

Generate examples about OCI Vault including secrets, keys, and HSM.

## Topics

- Vault creation and management
- Secrets (API keys, passwords, certificates)
- Keys (encryption, signing)
- HSM (Hardware Security Module)
- Secret rotation

## Difficulty Distribution

- beginner (30%): Basic vault/secret creation
- intermediate (50%): Key management, rotation
- advanced (20%): HSM, BYOK

## Quality Rules

- Distinguish between secrets and keys use cases
- Include specific resource names
- Tag mutable content with [MUTABLE]

## OCI CLI Syntax

### Vault Commands

```bash
# Create a vault
oci kms vault create --compartment-id ocid1.compartment.oc1..<unique-id> \
  --display-name ProductionVault --vault-type DEFAULT --wait-for-state ACTIVE

# List vaults
oci kms vault list --compartment-id ocid1.compartment.oc1..<unique-id>

# Get vault details
oci kms vault get --vault-id ocid1.vault.oc1..<unique-id>

# Create a key
oci kms key create --compartment-id ocid1.compartment.oc1..<unique-id> \
  --display-name MasterKey --key-shape algorithm=AES key-length=256 \
  --vault-id ocid1.vault.oc1..<unique-id>

# List keys
oci kms key list --vault-id ocid1.vault.oc1..<unique-id>

# Get key details
oci kms key get --key-id ocid1.key.oc1..<unique-id>

# Rotate a key
oci kms key rotate --key-id ocid1.key.oc1..<unique-id>
```

### Secret Commands

```bash
# Create a secret
oci vault secret create-base64 --secret-name "api-key-prod" \
  --vault-id ocid1.vault.oc1..<unique-id> \
  --key-id ocid1.key.oc1..<unique-id> \
  --secret-base64-encoded-content S2V5Q29udGVudA== \
  --description "Production API Key"

# List secrets
oci vault secret list --vault-id ocid1.vault.oc1..<unique-id>

# Get secret details
oci vault secret get --secret-id ocid1.secret.oc1..<unique-id>

# Get secret content
oci vault secret get-secret-content --secret-id ocid1.secret.oc1..<unique-id>

# Schedule secret deletion (for rotation)
oci vault secret schedule-secret-deletion --secret-id ocid1.secret.oc1..<unique-id>
```

### HSM Commands

```bash
# Create HSM vault (dedicated hardware security module)
oci kms vault create --compartment-id ocid1.compartment.oc1..<unique-id> \
  --display-name HSMVault --vault-type DEDICATED_HSM --wait-for-state ACTIVE

# List HSM keys
oci kms key list --vault-id ocid1.vault.oc1..<unique-id> \
  --key-shape algorithm=RSA
```

## OCID Format

OCI Vault resources use these OCID patterns:

```
Vault:         ocid1.vault.oc1..<unique-id>
Key:           ocid1.key.oc1..<unique-id>
Secret:        ocid1.secret.oc1..<unique-id>
```

Example full OCIDs:
```
ocid1.vault.oc1..aaaaaaaa1234567890abcdef1234567890abcdef1234567890abcdef
ocid1.key.oc1..bbbbbbbb1234567890abcdef1234567890abcdef1234567890abcdef
ocid1.secret.oc1..cccccccc1234567890abcdef1234567890abcdef1234567890abcdef
```

## Examples by Topic

### Creating a Vault and Key

```bash
# Create vault
oci kms vault create --compartment-id ocid1.compartment.oc1..aaaaaa \
  --display-name AppSecVault --vault-type DEFAULT

# Store OCID
VAULT_OCID="ocid1.vault.oc1..<unique-id>"

# Create encryption key
oci kms key create --compartment-id ocid1.compartment.oc1..aaaaaa \
  --display-name EncryptionKey --key-shape algorithm=AES key-length=256 \
  --vault-id $VAULT_OCID

# Key OCID format
ocid1.key.oc1..<unique-id>
```

### Storing a Secret

```bash
# Encode secret value
SECRET_BASE64=$(echo -n "my-api-key-12345" | base64)

# Create secret with key encryption
oci vault secret create-base64 --secret-name "db-password-prod" \
  --vault-id ocid1.vault.oc1..aaaaaa \
  --key-id ocid1.key.oc1..bbbbbb \
  --secret-base64-encoded-content $SECRET_BASE64 \
  --description "Production database password"

# OCID: ocid1.secret.oc1..<unique-id>
```

### Secret Rotation

```bash
# Create new secret version for rotation
oci vault secret create-base64 --secret-name "api-key-prod" \
  --vault-id ocid1.vault.oc1..aaaaaa \
  --key-id ocid1.key.oc1..bbbbbb \
  --secret-base64-encoded-content $(echo -n "new-api-key" | base64)

# Schedule old secret deletion (7 days)
oci vault secret schedule-secret-deletion --secret-id ocid1.secret.oc1..cccccc \
  --time-of-deletion "2024-12-01T00:00:00Z"
```

## Anti-Patterns (Never generate)

1. ❌ Use Vault for secrets vs keys - keys are for encryption, secrets are for storing sensitive data
2. ❌ Store encryption keys and encrypted data in same vault (use separate vaults)
3. ❌ Hardcode secrets in code - always use Vault secret OCIDs
4. ❌ Create secrets without encryption key
5. ❌ Use placeholder OCIDs like `ocid1.vault.<region>.<unique-id>` - use actual format: `ocid1.vault.oc1..<unique-id>`
6. ❌ Delete keys without understanding impact (data encrypted with key becomes unrecoverable)
7. ❌ Skip key rotation schedules - rotate keys [MUTABLE: every 1-2 years]
8. ❌ Use Vault without proper IAM policies
9. ❌ Store plain-text secrets (must use base64 encoding)
10. ❌ Describe Vault as "password manager" - it's for secrets and keys, not general credential storage
