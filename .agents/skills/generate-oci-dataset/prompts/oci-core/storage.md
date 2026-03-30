# Prompt Template: oci-core/storage

## Context

Generate examples about OCI Storage services including Block Volume, Object Storage, File Storage, and Archive Storage.

## Topics

- Block Volume (performance tiers, clones, backups)
- Object Storage (buckets, versioning, lifecycle)
- File Storage (NFS, mount targets)
- Archive Storage (retention policies)

## Difficulty Distribution

- beginner (30%): Basic bucket/volume creation
- intermediate (50%): Lifecycle policies, performance tuning
- advanced (20%): Multi-region, cross-region replication

## Quality Rules

- Distinguish between Block, Object, and File Storage use cases
- Include specific tier names (Standard, Archive, Cold Archive)
- Tag mutable content (pricing) with [MUTABLE]
- Reference actual OCI service limits
