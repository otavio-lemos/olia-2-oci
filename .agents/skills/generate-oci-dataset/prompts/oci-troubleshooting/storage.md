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

## Common Issues

- 403 Access Denied for bucket
- Upload fails with timeout
- Block Volume not attaching to instance
- NFS mount timeout
- Performance limits reached

## Example Questions

- "Bucket não acessível mesmo com policy"
- "Upload de arquivo muito lento"
- "Block Volume não anexa à instância"
