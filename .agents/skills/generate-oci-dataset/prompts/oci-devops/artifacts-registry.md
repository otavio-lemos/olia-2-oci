# Prompt Template: oci-devops/artifacts-registry

## Context

Generate examples about OCI Artifacts and Container Registry.

## Topics

- OCI Artifacts service
- Container Registry (OCIR)
- Generic artifacts
- Image signing
- Access control
- Helm charts storage

## Difficulty Distribution

- beginner (30%): Basic registry usage
- intermediate (50%): Image management, access control
- advanced (20%): Signing, automation

## OCI CLI Syntax

### Container Registry (OCIR)
```bash
# List repositories
oci artifacts container repository list \
  --compartment-id ocid1.compartment.oc1..aaaaaaaab222... \
  --region us-sao-1

# List images in repository
oci artifacts container image list \
  --repository-id ocid1.artifactsrepository.oc1.sa-saopaulo-1.rrrrrrrr... \
  --region us-sao-1

# Get image details
oci artifacts container image get \
  --image-id ocid1.artifactscontainerimage.oc1.sa-saopaulo-1.iiiiii... \
  --region us-sao-1

# Delete image
oci artifacts container image delete \
  --image-id ocid1.artifactscontainerimage.oc1.sa-saopaulo-1.iiiiii... \
  --force

# Set lifecycle state (restore)
oci artifacts container image update \
  --image-id ocid1.artifactscontainerimage.oc1.sa-saopaulo-1.iiiiii... \
  --lifecycle-state AVAILABLE

# Create repository
oci artifacts container repository create \
  --compartment-id ocid1.compartment.oc1..aaaaaaaab222... \
  --display-name "myrepo" \
  --region us-sao-1

# Set lifecycle policy
oci artifacts container repository set-lifecycle-policy \
  --repository-id ocid1.artifactsrepository.oc1.sa-saopaulo-1.rrrrrrrr... \
  --policy-statements '[{"rules": [{"maxCount": 10, "filter": ".*"}]}]'
```

### Generic Artifacts
```bash
# Upload generic artifact
oci artifacts generic artifact upload \
  --compartment-id ocid1.compartment.oc1..aaaaaaaab222... \
  --artifact-type "HELM_CHART" \
  --display-name "mychart" \
  --version "1.0.0" \
  --content file:///path/to/chart.tgz \
  --region us-sao-1

# Download generic artifact
oci artifacts generic artifact download \
  --artifact-id ocid1.artifactsgenericartifact.oc1.sa-saopaulo-1.ggaaaa... \
  --region us-sao-1

# List generic artifacts
oci artifacts generic artifact list \
  --compartment-id ocid1.compartment.oc1..aaaaaaaab222... \
  --artifact-type "HELM_CHART" \
  --region us-sao-1
```

### Image Signing (OCD)
```bash
# Sign container image
oci artifacts container image sign \
  --image-id ocid1.artifactscontainerimage.oc1.sa-saopaulo-1.iiiiii... \
  --signing-key-id ocid1.key.oc1.sa-saopaulo-1.kkkkkk... \
  --region us-sao-1

# Verify image signature
oci artifacts container image verify \
  --image-id ocid1.artifactscontainerimage.oc1.sa-saopaulo-1.iiiiii... \
  --signing-key-id ocid1.key.oc1.sa-saopaulo-1.kkkkkk... \
  --region us-sao-1

# List signers
oci artifacts container image list-signers \
  --image-id ocid1.artifactscontainerimage.oc1.sa-saopaulo-1.iiiiii... \
  --region us-sao-1
```

### Docker Login/Push/Pull (not OCI CLI)
```bash
# Authenticate to OCIR (run via Docker CLI, not oci)
docker login myregistry.ocir.io \
  -u 'ocid1.user.oc1..aaaaaaaab222...' \
  -p '~/.oci/api_key.pem'  # or auth token

# Tag image
docker tag myapp:latest myregistry.ocir.io/myproject/myapp:v1.0.0

# Push image
docker push myregistry.ocir.io/myproject/myapp:v1.0.0

# Pull image
docker pull myregistry.ocir.io/myproject/myapp:v1.0.0
```

## OCID Format

| Resource Type | OCID Pattern | Example |
|---------------|--------------|---------|
| Repository | `ocid1.artifactsrepository.oc1.<region>.<unique-id>` | `ocid1.artifactsrepository.oc1.sa-saopaulo-1.rrrrrrrrsssssss` |
| Container Image | `ocid1.artifactscontainerimage.oc1.<region>.<unique-id>` | `ocid1.artifactscontainerimage.oc1.sa-saopaulo-1.iiiiii555666777` |
| Generic Artifact | `ocid1.artifactsgenericartifact.oc1.<region>.<unique-id>` | `ocid1.artifactsgenericartifact.oc1.sa-saopaulo-1.ggaaaa888999000` |

**Registry URL format**: `<registry>.ocir.io/<tenancy>/<repo>[:tag|@digest]`

**Valid registries**:
- `ioke.io` (Ashburn)
- `saopaulo.ocir.io` (São Paulo)
- `frankfurt.ocir.io`
- `phoenix.ocir.io`

**Auth token format**: `<tenancy-name>/<username>/<token>` (e.g., `mytenancy/admin/mytoken123`)

## Anti-Patterns

NEVER generate examples that:
- Use fake OCIDs like `ocid1.ocir.oc1...` (wrong format)
- Use `oci ocir` commands (OCIR is part of `oci artifacts`)
- Suggest using password instead of auth tokens for Docker login
- Mix up repository OCID with image OCID
- Use the wrong registry for a region
- Reference "Docker Hub" as primary registry in OCI context
- Use `kubernetes.io` as artifact type
- Claim OCIR supports private repos without proper IAM policies
- Suggest bypassing image scanning for "speed"
- Use `latest` tag in production pipelines

## Quality Rules

- Include OCIR examples
- Reference artifact types
- Tag mutable content with [MUTABLE]
- Use correct CLI command structure (`oci artifacts container`)
- Specify auth token format for Docker authentication

## Example Questions

- Como configurar o OCIR para armazenar imagens Docker de um pipeline CI/CD?
- Como fazer push de uma imagem Docker para o OCIR usando token de autenticação?
- Como configurar políticas de retenção e lifecycle para imagens no OCIR?
- Como usar OCI Artifacts para armazenar e distribuir Helm charts?
- Como configurar assinatura de imagens Docker no OCIR para segurança?
- Como resolver erros de autenticação quando um pipeline não consegue fazer push para o OCIR?
- Como configurar access control no OCIR usando IAM policies e dynamic groups?
- Como integrar o OCIR com OKE para deploy automatizado de containers?
- Como armazenar artifacts genéricos (JAR, ZIP, TAR) no OCI Artifacts?
- Como automatizar limpeza de imagens antigas no OCIR usando lifecycle policies?