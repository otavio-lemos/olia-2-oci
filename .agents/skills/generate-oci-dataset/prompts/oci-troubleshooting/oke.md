# Prompt Template: oci-troubleshooting/oke

## Context

Generate examples about troubleshooting OCI OKE (Kubernetes) issues.

## Topics

- OKE cluster creation failures
- Node pool issues
- Worker node not joining cluster
- CNI plugin problems
- Storage mount issues (PVC)
- OCI IAM integration with Kubernetes

## Difficulty Distribution

- beginner (20%): Basic cluster access
- intermediate (50%): Node pools, worker nodes
- advanced (30%): CNI, networking, storage

## Quality Rules

- Include kubectl commands
- Reference OKE documentation
- Explain worker node lifecycle

## Common Issues

- Node stuck in "Creating" state
- Worker nodes not joining cluster
- CNI pod failures
- PVC stuck in "Pending"
- ImagePullBackOff errors

## Example Questions

- "Worker node não junta no cluster OKE"
- "Pod fica em Pending, PVC não monta"
- "Como debugar pods no OKE?"
