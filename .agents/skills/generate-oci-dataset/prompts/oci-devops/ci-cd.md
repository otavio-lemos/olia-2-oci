# Prompt Template: oci-devops/ci-cd

## Context

Generate examples about OCI DevOps CI/CD pipelines.

## Topics

- OCI DevOps service
- Build pipelines
- Deploy pipelines
- Artifacts storage
- Container registry integration

## Difficulty Distribution

- beginner (30%): Basic pipeline creation
- intermediate (50%): Build and deploy stages
- advanced (20%): Complex pipelines, integration

## OCI CLI Syntax

### Project Management
```bash
# Create DevOps project
oci devops project create \
  --compartment-id ocid1.compartment.oc1..aaaaaaaab222... \
  --description "DevOps project for app" \
  --display-name "my-app-project" \
  --region us-sao-1

# List DevOps projects
oci devops project list \
  --compartment-id ocid1.compartment.oc1..aaaaaaaab222... \
  --lifecycle-state ACTIVE

# Get project OCID
oci devops project get \
  --project-id ocid1.devopsproject.oc1.sa-saopaulo-1.aaaaaaaab222...
```

### Build Pipeline
```bash
# Create build pipeline
oci devops build pipeline create \
  --project-id ocid1.devopsproject.oc1.sa-saopaulo-1.aaaaaaaab222... \
  --display-name "build-pipeline" \
  --description "Build and test application"

# Add build stage
oci devops build pipeline add-build-stage \
  --build-pipeline-id ocid1.devopsbuildpipeline.oc1.sa-saopaulo-1.bbbbbb333... \
  --stage-name "build-stage" \
  --build-source "https://github.com/owner/repo" \
  --build-type DOCKER \
  --primary-output-dir ./dist

# List build pipelines
oci devops build pipeline list \
  --project-id ocid1.devopsproject.oc1.sa-saopaulo-1.aaaaaaaab222...

# Start manual build
oci devops build pipeline run \
  --build-pipeline-id ocid1.devopsbuildpipeline.oc1.sa-saopaulo-1.bbbbbb333... \
  --display-name "manual-run"
```

### Deploy Pipeline
```bash
# Create deploy pipeline
oci devops deploy pipeline create \
  --project-id ocid1.devopsproject.oc1.sa-saopaulo-1.aaaaaaaab222... \
  --display-name "deploy-pipeline" \
  --description "Deploy to OKE"

# Add OKE deployment stage
oci devops deploy pipeline add-stage \
  --deploy-pipeline-id ocid1.devopsdeploypipeline.oc1.sa-saopaulo-1.ccccccc444... \
  --stage-name "deploy-to-oke" \
  --stage-type OKE \
  --oke-cluster-id ocid1.cluster.oc1.sa-saopaulo-1.kkkkkk555... \
  --oke-namespace production

# Add approval stage
oci devops deploy pipeline add-stage \
  --deploy-pipeline-id ocid1.devopsdeploypipeline.oc1.sa-saopaulo-1.ccccccc444... \
  --stage-name "approval-check" \
  --stage-type APPROVAL \
  --approval-stage-config "{\"approverGroup\": \"devops-approvers\"}"

# Deploy canary
oci devops deploy pipeline create-canary-deployment \
  --deploy-pipeline-id ocid1.devopsdeploypipeline.oc1.sa-saopaulo-1.ccccccc444... \
  --pipeline-stage-id ocid1.devopsdeploystage.oc1.sa-saopaulo-1.ssssss666... \
  --work-load OKE \
  --traffic-split-percent 10

# Trigger deployment
oci devops deploy pipeline trigger \
  --deploy-pipeline-id ocid1.devopsdeploypipeline.oc1.sa-saopaulo-1.ccccccc444... \
  --display-name "production-deploy"
```

### Artifacts and Trigger
```bash
# Link artifact to pipeline
oci devops artifact create \
  --project-id ocid1.devopsproject.oc1.sa-saopaulo-1.aaaaaaaab222... \
  --display-name "app-artifact" \
  --artifact-type DOCKER_IMAGE \
  --artifact-path "myregistry.ocir.io/myapp:1.0.0"

# Create trigger
oci devops trigger create \
  --project-id ocid1.devopsproject.oc1.sa-saopaulo-1.aaaaaaaab222... \
  --display-name "github-trigger" \
  --trigger-source GITHUB \
  --actions "[{\"buildPipelineId\": \"ocid1.devopsbuildpipeline...\"}]"
```

## OCID Format

| Resource Type | OCID Pattern | Example |
|---------------|--------------|---------|
| DevOps Project | `ocid1.devopsproject.oc1.<region>.<unique-id>` | `ocid1.devopsproject.oc1.sa-saopaulo-1.aaaaaaaab222cccccdddd` |
| Build Pipeline | `ocid1.devopsbuildpipeline.oc1.<region>.<unique-id>` | `ocid1.devopsbuildpipeline.oc1.sa-saopaulo-1.bbbbbb333cccc4444` |
| Deploy Pipeline | `ocid1.devopsdeploypipeline.oc1.<region>.<unique-id>` | `ocid1.devopsdeploypipeline.oc1.sa-saopaulo-1.ccccc666dddd7777` |
| Artifact | `ocid1.devopsartifact.oc1.<region>.<unique-id>` | `ocid1.devopsartifact.oc1.sa-saopaulo-1.eeeeee888ffff9999` |
| Trigger | `ocid1.devopstrigger.oc1.<region>.<unique-id>` | `ocid1.devopstrigger.oc1.sa-saopaulo-1.ggggg111hhhh2222` |

**Valid regions**: `sa-saopaulo-1`, `us-ashburn-1`, `us-phoenix-1`, `eu-frankfurt-1`

## Anti-Patterns

NEVER generate examples that:
- Use fake OCIDs like `ocid1.pipeline.oc1...` without full resource type
- Confuse build pipeline with deploy pipeline (different OCID types)
- Use CLI commands without required --project-id or --pipeline-id
- Reference "OCI CI/CD" instead of "OCI DevOps" (correct service name)
- Suggest using Jenkins or GitLab CI as the primary CI/CD tool in OCI context
- Use YAML syntax that doesn't match DevOps pipeline schema
- Claim DevOps supports on-premise deployments without OCI Connector
- Mix approval stages with build stages
- Reference "automatic rollback" without health check configuration
- Suggest manual approval via API without proper IAM permissions

## Quality Rules

- Include YAML pipeline examples
- Reference OCI DevOps documentation
- Tag mutable content with [MUTABLE]
- Always use correct OCID resource type prefix
- Use correct region format (e.g., `sa-saopaulo-1` not `sao1`)

## Example Questions

- Como criar um pipeline CI/CD básico no OCI DevOps para uma aplicação Node.js?
- Qual a diferença entre build pipeline e deploy pipeline no OCI DevOps?
- Como configurar um estágio de build que executa testes unitários e gera artefatos Docker?
- Como integrar o OCI DevOps com um repositório GitHub para trigger automático de builds?
- Como configurar variáveis de ambiente e secrets em um pipeline de deploy?
- Como criar um pipeline de deploy canário usando OCI DevOps e Load Balancer?
- Como resolver erros de permissão quando o build pipeline tenta acessar o Object Storage?
- Como configurar notificações por email quando um pipeline falha ou tem sucesso?
- Como criar um pipeline multi-stage com aprovação manual antes do deploy em produção?
- Como fazer rollback automático quando health checks falham após um deploy?