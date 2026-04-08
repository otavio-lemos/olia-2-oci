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

## OCI Diagnostic CLI Syntax

Use these real OCI CLI commands for OKE troubleshooting:

```bash
# Cluster operations
oci ce cluster get --cluster-id ocid1.cluster.oc1.<region>.<unique-id>
oci ce cluster list --compartment-id ocid1.compartment.oc1.<region>.<unique-id>

# Node pool management
oci ce node-pool get --node-pool-id ocid1.nodepool.oc1.<region>.<unique-id>
oci ce node-pool list --cluster-id ocid1.cluster.oc1.<region>.<unique-id>

# Node pool scale/resize
oci ce node-pool update --node-pool-id ocid1.nodepool.oc1.<region>.<unique-id> --node-count 3

# Worker nodes (instances)
oci compute instance list --compartment-id ocid1.compartment.oc1.<region>.<unique-id> --display-name "oke-*"

# Cluster endpoint access
oci ce cluster kubeconfig get --cluster-id ocid1.cluster.oc1.<region>.<unique-id> --file /path/to/kubeconfig

# VCN and subnet for cluster
oci network vcn get --vcn-id ocid1.vcn.oc1.<region>.<unique-id>
oci network subnet get --subnet-id ocid1.subnet.oc1.<region>.<unique-id>

# Security lists (cluster node subnet)
oci network security-list get --security-list-id ocid1.securitylist.oc1.<region>.<unique-id>

# Load balancers (for services)
oci lb load-balancer list --compartment-id ocid1.compartment.oc1.<region>.<unique-id>

# OCI Service Account for IAM
iam dynamic-group list --compartment-id ocid1.compartment.oc1.<region>.<unique-id>

# Pod events (run in cluster context)
kubectl get events --all-namespaces
kubectl describe pod <pod-name> -n <namespace>

# Node status
kubectl get nodes
kubectl describe node <node-name>

# PVC status
kubectl get pvc -n <namespace>
kubectl describe pvc <pvc-name> -n <namespace>
```

## OCID Format

OCI resource identifiers follow this pattern:

```
ocid1.<resource-type>.<realm>.<region>.<unique-id>

Examples:
- ocid1.cluster.oc1.sa-vinhedo-1.abcd1234...
- ocid1.nodepool.oc1.sa-vinhedo-1.abcd1234...
- ocid1.vcn.oc1.sa-vinhedo-1.abcd1234...
- ocid1.subnet.oc1.sa-vinhedo-1.abcd1234...

Cluster endpoint format:
https://<cluster-ocid>.containers.oraclecloud.com

OKE node naming:
oke-<node-pool-ocid>-<node-number>
```

## Anti-Patterns

**NEVER generate:**

- ❌ Node pool issues without checking node lifecycle state
- ❌ "Worker not joining" without investigating CNI pod status
- ❌ PVC problems without checking OCI volume attachment
- ❌ Network issues without mentioning VCN security lists
- ❌ "Just delete and recreate cluster" without root cause analysis
- ❌ Copy OCI documentation verbatim
- ❌ Suggest kubectl commands without cluster context
- ❌ IAM integration without mentioning Dynamic Groups and Service Account
- ❌ Performance tuning without mentioning node shape and OCPU
- ❌ Never recommend disabling Kubernetes RBAC for "simplicity"

## Common Issues

- Node stuck in "Creating" state
- Worker nodes not joining cluster
- CNI pod failures (oci-cni-node-*)
- PVC stuck in "Pending" (check OCI volume, storage class)
- ImagePullBackOff errors
- Load balancer provisioning failures

## Example Questions

- "Worker node não junta no cluster OKE"
- "Pod fica em Pending, PVC não monta"
- "Como debugar pods no OKE?"
- "CNI pods em CrashLoopBackOff"
- "Service tipo LoadBalancer não cria"