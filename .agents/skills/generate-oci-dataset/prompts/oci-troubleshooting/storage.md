# Prompt Template: oci-troubleshooting/storage

## Context

Generate examples about troubleshooting OCI Storage issues.

## Topics

- Bucket access issues (public/private)
- Object upload/download failures
- Object Storage performance
- Block Volume attachment issues
- File Storage mount problems
- Lifecycle policy issues

## Difficulty Distribution

- beginner (30%): Basic bucket access
- intermediate (50%): Performance, attachments
- advanced (20%): Complex storage scenarios

## Quality Rules

- Include bucket policy examples
- Reference attachment procedures
- Tag mutable content with [MUTABLE]

## OCI Diagnostic CLI Syntax

Use these real OCI CLI commands for Storage troubleshooting:

```bash
# Object Storage Bucket
oci os bucket get --namespace-name <namespace> --bucket-name <bucket-name>
oci os bucket list --compartment-id ocid1.compartment.oc1.<region>.<unique-id>

# Object operations
oci os object put --namespace-name <namespace> --bucket-name <bucket-name> --file-path /path/to/file
oci os object get --namespace-name <namespace> --bucket-name <bucket-name> --name <object-name> --file-path /output/path

# Bucket policy
oci os bucket get --namespace-name <namespace> --bucket-name <bucket-name> --query "data.policy"

# Pre-authenticated requests
oci os preauth-request list --bucket-name <bucket-name> --namespace-name <namespace>
oci os preauth-request create --bucket-name <bucket-name> --namespace-name <namespace> --name "test-par" --object-name "*" --expiration 2025-12-31

# Block Volume
oci bv volume get --volume-id ocid1.volume.oc1.<region>.<unique-id>
oci bv volume list --compartment-id ocid1.compartment.oc1.<region>.<unique-id>

# Volume attachment
oci compute volume-attachment list --compartment-id ocid1.compartment.oc1.<region>.<unique-id> --instance-id ocid1.instance.oc1.<region>.<unique-id>
oci compute volume-attachment attach --instance-id ocid1.instance.oc1.<region>.<unique-id> --volume-id ocid1.volume.oc1.<region>.<unique-id> --attachment-type iscsi

# File Storage
oci fs file-system list --compartment-id ocid1.compartment.oc1.<region>.<unique-id>
oci fs export get --export-id ocid1.export.oc1.<region>.<unique-id>
oci fs mount-target get --mount-target-id ocid1.mounttarget.oc1.<region>.<unique-id>

# Volume performance (VPUs)
oci bv volume get --volume-id ocid1.volume.oc1.<region>.<unique-id> --query "data.volume-perf"

# Lifecycle policies
oci os object lifecycle-policy get --namespace-name <namespace> --bucket-name <bucket-name>
```

## OCID Format

OCI resource identifiers follow this pattern:

```
ocid1.<resource-type>.<realm>.<region>.<unique-id>

Examples:
- ocid1.volume.oc1.sa-vinhedo-1.abcd1234...
- ocid1.volumeattachment.oc1.sa-vinhedo-1.abcd1234...
- ocid1.filesystem.oc1.sa-vinhedo-1.abcd1234...
- ocid1.export.oc1.sa-vinhedo-1.abcd1234...
- ocid1.mounttarget.oc1.sa-vinhedo-1.abcd1234...

Namespace format: oci - <tenancy-ocid>
```

## Anti-Patterns

**NEVER generate:**

- ❌ "Make bucket public" without explaining security risks
- ❌ Access issues without mentioning IAM policy vs bucket policy
- ❌ Block Volume attachment without mentioning iSCSI/Paravirtualized
- ❌ File Storage mount without explaining security lists and export options
- ❌ Performance issues without mentioning VPUs [MUTABLE]
- ❌ Copy OCI documentation verbatim
- ❌ Suggest specific throughput numbers without marking as [MUTABLE]
- ❌ Upload failures without checking multipart upload options
- ❌ Never recommend disabling encryption for performance

## Common Issues

- 403 Access Denied for bucket (check IAM and bucket policy)
- Upload fails with timeout (check multipart threshold)
- Block Volume not attaching to instance (check attachment type, CHAP)
- NFS mount timeout (check security list, export options)
- Performance limits reached (check VPUs, throughput)

## Example Questions

- "Bucket não acessível mesmo com policy"
- "Upload de arquivo muito lento"
- "Block Volume não anexa à instância"
- "NFS mount timeout no File Storage"
- "Como configurar lifecycle policy?"