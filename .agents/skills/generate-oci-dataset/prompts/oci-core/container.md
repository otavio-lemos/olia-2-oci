# Prompt Template: oci-core/container

## Context

Generate examples about OCI Container services including OKE, Container Instances, and OCIR.

## Topics

- OKE cluster creation and management
- Node pools, worker nodes
- Container Instances
- OCIR (Container Registry)
- Deploy applications

## Difficulty Distribution

- beginner (30%): Basic OKE creation
- intermediate (50%): Deployments, services, ingress
- advanced (20%): GitOps, CNCF integration

## Quality Rules

- Use correct OCI terminology (OKE, not "Kubernetes OCI")
- Include kubectl commands
- Reference OCI documentation
- Tag mutable content with [MUTABLE]

## OCI CLI Syntax

Use these commands as reference:

```bash
# Create OKE Cluster
oci ce cluster create \
  --compartment-id ocid1.compartment.oc1.<region>.<unique-id> \
  --name "my-oke-cluster" \
  --kubernetes-version "v1.28.2" \
  --vcn-id ocid1.vcn.oc1.<region>.<unique-id> \
  --options '{"kubernetes-network-config": {"pods-cidr": "10.244.0.0/16", "services-cidr": "10.96.0.0/16"}}' \
  --type "OKE_VIRTUAL_MACHINE"

# Create Node Pool
oci ce node-pool create \
  --cluster-id ocid1.containercluster.oc1.<region>.<unique-id> \
  --compartment-id ocid1.compartment.oc1.<region>.<unique-id> \
  --name "pool-workers" \
  --kubernetes-version "v1.28.2" \
  --node-shape "VM.Standard.E4.Flex" \
  --node-shape-config '{"ocpus": 2, "memoryInGBs": 16}' \
  --quantity-per-subnet 3 \
  --subnet-ids '["ocid1.subnet.oc1.<region>.<unique-id>"]'

# Create Container Instance
oci container-instance container-instance create \
  --compartment-id ocid1.compartment.oc1.<region>.<unique-id> \
  --display-name "my-container" \
  --shape "CI.Standard3.Flex" \
  --shape-config '{"ocpus": 1, "memoryInGBs": 2}' \
  --containers '[{"name": "app", "image": "iad.ocir.io/<namespace>/my-image:latest", "command": ["python", "app.py"], "environment-vars": {"KEY": "value"}, "volume-mounts": [{"name": "data", "mount-path": "/data"}]}]' \
  --vnics '[{"subnet-id": "ocid1.subnet.oc1.<region>.<unique-id>"}]'

# Create OCIR Repository
oci artifacts container repository create \
  --compartment-id ocid1.compartment.oc1.<region>.<unique-id> \
  --display-name "my-repo" \
  --is-public false

# Push Image to OCIR
docker login iad.ocir.io
docker tag my-image:latest iad.ocir.io/<namespace>/my-repo/my-image:latest
docker push iad.ocir.io/<namespace>/my-repo/my-image:latest

# Get Cluster kubeconfig
oci ce cluster create-kubeconfig \
  --cluster-id ocid1.containercluster.oc1.<region>.<unique-id> \
  --file kubeconfig

# Scale Node Pool
oci ce node-pool update \
  --node-pool-id ocid1.nodepool.oc1.<region>.<unique-id> \
  --quantity-per-subnet 5
```

## OCID Format

Always use these patterns:

- Cluster: `ocid1.containercluster.oc1.<region>.<unique-id>`
- Node Pool: `ocid1.nodepool.oc1.<region>.<unique-id>`
- Container Instance: `ocid1.containerinstance.oc1.<region>.<unique-id>`
- OCIR Repository: `ocid1.containerrepository.oc1.<region>.<unique-id>`
- VCN: `ocid1.vcn.oc1.<region>.<unique-id>`
- Subnet: `ocid1.subnet.oc1.<region>.<unique-id>`
- Compartment: `ocid1.compartment.oc1.<region>.<unique-id>`

## Anti-Patterns

NEVER generate:
- Using "Kubernetes OCI" instead of "OKE" or "Oracle Kubernetes Engine"
- Creating clusters without specifying Kubernetes version
- Using non-flexible shapes for node pools in production
- Missing node pool in cluster setup
- Incorrect OCIR image naming convention: `<region>.ocir.io/<namespace>/<repo>:<tag>`
- Using `kubectl` without proper kubeconfig setup
- Creating Container Instances without VCN/subnet configuration
- Using public endpoint for production clusters without VPN
- Missing Ingress controller configuration for external traffic
- Not specifying proper security lists for pod networking
- Using outdated Kubernetes versions (always use current stable)

## Example Questions

- "Como criar um cluster OKE no OCI?"
- "Deployar aplicação no OKE usando kubectl"
- "Configurar OCIR para armazenar imagens Docker"