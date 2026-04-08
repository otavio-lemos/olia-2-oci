# Prompt Template: oci-security/encryption

## Context

Generate examples about OCI encryption services.

## Topics

- Volume encryption
- Object Storage encryption
- Customer-managed keys (CMK)
- BYOK (Bring Your Own Key)
- Encryption at rest

## Difficulty Distribution

- beginner (30%): Basic encryption concepts
- intermediate (50%): CMK configuration
- advanced (20%): BYOK, key rotation

## Quality Rules

- Distinguish between OCI-managed and customer-managed keys
- Include specific resource names
- Tag mutable content with [MUTABLE]

## OCI CLI Syntax

### Volume Encryption

```bash
# Create boot volume with encryption
oci bv boot-volume create --compartment-id ocid1.compartment.oc1..<unique-id> \
  --availability-domain 1:MELBOURNE-1-AD-1 \
  --display-name WebServerBoot \
  --size-in-gbs 50 \
  --image-id ocid1.image.oc1..<unique-id>

# Create block volume with custom encryption key
oci bv volume create --compartment-id ocid1.compartment.oc1..<unique-id> \
  --availability-domain 1:MELBOURNE-1-AD-1 \
  --display-name DataVolume \
  --size-in-gbs 100 \
  --kms-key-id ocid1.key.oc1..<unique-id>

# Attach volume with encryption
oci bv volume-attachment attach --instance-id ocid1.instance.oc1..<unique-id> \
  --volume-id ocid1.volume.oc1..<unique-id> \
  --attachment-type iscsi
```

### Object Storage Encryption

```bash
# Create bucket with customer-managed key
oci os bucket create --compartment-id ocid1.compartment.oc1..<unique-id> \
  --name encrypted-bucket \
  --kms-key-id ocid1.key.oc1..<unique-id> \
  --encryption-type CUSTOMER_MANAGED

# Update bucket to use CMK
oci os bucket update --bucket-name encrypted-bucket \
  --kms-key-id ocid1.key.oc1..<unique-id> \
  --encryption-type CUSTOMER_MANAGED

# Upload object (inherits bucket encryption)
oci os object put --bucket-name encrypted-bucket \
  --name sensitive-data.json \
  --file ./data.json
```

### Key Management for Encryption

```bash
# List encryption keys
oci kms key list --vault-id ocid1.vault.oc1..<unique-id> \
  --key-shape algorithm=AES

# Get key version
oci kms key-version get --key-id ocid1.key.oc1..<unique-id> \
  --version-number 1

# Enable key for encryption
oci kms key update --key-id ocid1.key.oc1..<unique-id> \
  --state ACTIVE
```

## OCID Format

```
Vault:         ocid1.vault.oc1..<unique-id>
Key:           ocid1.key.oc1..<unique-id>
Boot Volume:   ocid1.bootvolume.oc1..<unique-id>
Block Volume:  ocid1.volume.oc1..<unique-id>
Bucket:        ocid1.bucket.oc1..<unique-id>
Object:        objectName (no OCID, uses bucket name)
```

## Examples by Topic

### Volume Encryption with CMK

```bash
# Step 1: Create vault and key
oci kms vault create --compartment-id ocid1.compartment.oc1..aaaaaa \
  --display-name EncryptionVault --vault-type DEFAULT

oci kms key create --compartment-id ocid1.compartment.oc1..aaaaaa \
  --display-name VolumeKey --key-shape algorithm=AES key-length=256 \
  --vault-id ocid1.vault.oc1..aaaaaa

# Key OCID: ocid1.key.oc1..bbbbbb

# Step 2: Create volume with CMK
oci bv volume create --compartment-id ocid1.compartment.oc1..aaaaaa \
  --display-name EncryptedDataVolume \
  --size-in-gbs 500 \
  --kms-key-id ocid1.key.oc1..bbbbbb
```

### Object Storage with BYOK

```bash
# Create vault for BYOK (import key or generate in HSM)
oci kms vault create --compartment-id ocid1.compartment.oc1..aaaaaa \
  --display-name BYOKVault --vault-type DEFAULT

# Create key that will encrypt bucket data
oci kms key create --compartment-id ocid1.compartment.oc1..aaaaaa \
  --display-name BucketEncryptionKey \
  --key-shape algorithm=AES key-length=256 \
  --vault-id ocid1.vault.oc1..aaaaaa

# Create bucket with CMK
oci os bucket create --compartment-id ocid1.compartment.oc1..aaaaaa \
  --name secure-finance-data \
  --kms-key-id ocid1.key.oc1..bbbbbb \
  --encryption-type CUSTOMER_MANAGED
```

### IAM Policies for Encryption

```bash
# Policy for key usage
Allow group SecurityAdmins to use kms-key in compartment SecurityCompartment

# Policy for vault management
Allow group KeyAdmins to manage kms-key in compartment KeyManagement

# Allow compute service to use keys
Allow service instance to use kms-key in tenancy
```

## Anti-Patterns (Never generate)

1. ❌ Use OCI-managed key when CMK is required for compliance
2. ❌ Store encryption key in same vault as encrypted data
3. ❌ Delete customer-managed key (data becomes unrecoverable)
4. ❌ Mix up volume encryption vs object storage encryption (different services)
5. ❌ Use placeholder OCIDs: `ocid1.key.<region>.<id>` - correct is `ocid1.key.oc1..<unique-id>`
6. ❌ Forget that boot volumes can't use external CMKs (use block volumes instead)
7. ❌ Use BYOK without proper key import procedures
8. ❌ Create bucket without specifying encryption-type (defaults to OCI-managed)
9. ❌ Forget that bucket encryption is set at creation time
10. ❌ Recommend encryption at rest is optional - it's always enabled by default
11. ❌ Use "KMS" when correct service name is "Vault" in OCI
