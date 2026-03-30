# OCI Specialist LLM - Scope (v1)

## Objectives

Build a fine-tuned LLM that serves as an expert in Oracle Cloud Infrastructure, capable of:
- Explaining OCI services, architecture, and best practices
- Troubleshooting OCI workloads
- Guiding migration from AWS, Azure, and on-premises to OCI
- Writing OCI Terraform configurations
- Providing security and IAM guidance

## What Goes Into Fine-Tuning (v1)

Core knowledge that should be embedded in the model:
- OCI core services (Compute, Storage, Networking, IAM, Database)
- OCI networking concepts (VCN, Subnets, Security Lists, Route Tables, DRG)
- OCI security (IAM policies, vault, encryption)
- OCI migration patterns (AWS→OCI, Azure→OCI, on-prem→OCI)
- OCI troubleshooting common issues
- OCI Terraform resource definitions

## What Stays for RAG (Future v2)

Information that requires real-time updates:
- Current pricing and quotas
- New service announcements
- Region availability
- Service-specific limits that change frequently
- Latest API versions

## Version Scope

### v1 Focus
- OCI Core Services
- IAM and Security
- Networking (VCN, VPN, FastConnect)
- Compute shapes and optimization
- Block/Object Storage
- Migration patterns
- Basic troubleshooting

### v2 (Future)
- AI/ML services on OCI
- OCI Cloud Guard details
- OCI Observability suite
- Complete migration guides
- Advanced troubleshooting
