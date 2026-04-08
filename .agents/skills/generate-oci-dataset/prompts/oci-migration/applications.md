# Prompt Template: oci-migration/applications

## Context

Generate examples about migrating applications to OCI.

## Topics

- Oracle Integration migration
- Oracle Process Automation migration
- SaaS migration patterns
- Application re-platforming
- Container-based migrations
- Lift-and-shift vs re-architect

## Difficulty Distribution

- beginner (20%): Basic migration concepts
- intermediate (50%): Integration migrations
- advanced (30%): Complex application scenarios

## Quality Rules

- Include specific migration paths
- Reference OCI application services
- Tag mutable content with [MUTABLE]

---

## OCI CLI Syntax Section

When generating examples, include actual OCI CLI commands:

### OCI Integration (Oracle Integration)

```bash
# List integration instances
oci oic integration-instance list --compartment-id $COMPARTMENT_ID

# Create OIC instance
oci oic integration-instance create \
  --display-name "prod-oic" \
  --compartment-id $COMPARTMENT_ID \
  --integration-instance-type "STANDARD" \
  --pack-version "11.1.2.0.0" \
  --is-cvp-enabled false \
  --shape-type "DEVELOPMENT" \
  --message-packs 1

# Update OIC instance
oci oic integration-instance update \
  --integration-instance-id $OIC_OCID \
  --message-packs 5

# Get instance details
oci oic integration-instance get \
  --integration-instance-id $OIC_OCID

# Create integration
oci oic integration create \
  --integration-instance-id $OIC_OCID \
  --display-name "order-integration" \
  --integration-type "PROCESS" \
  --package-name "com.company.order"

# Activate integration
oci oic integration activate \
  --integration-instance-id $OIC_OCID \
  --integration-id $INTEGRATION_OCID
```

### Oracle Process Automation

```bash
# List process automation instances
oci opa process-automation-instance list --compartment-id $COMPARTMENT_ID

# Create OPA instance
oci opa process-automation-instance create \
  --display-name "prod-opa" \
  --compartment-id $COMPARTMENT_ID \
  --pack-version "23.04.0" \
  --shape-type "PRODUCTION"

# Get instance console URL
oci opa process-automation-instance get \
  --process-automation-instance-id $OPA_OCID

# Create process application
oci opa application create \
  --process-automation-instance-id $OPA_OCID \
  --display-name "approval-app"
```

### Container Registry

```bash
# List container repositories
oci artifacts container repository list --compartment-id $COMPARTMENT_ID

# Create repository
oci artifacts container repository create \
  --display-name "app-images" \
  --compartment-id $COMPARTMENT_ID \
  --repository-type "PRIVATE" \
  --visibility "PRIVATE"

# List container images
oci artifacts container image list \
  --repository-id $REPO_OCID

# Get image scan results
oci vulnerability scanning container image scan result get \
  --image-digest "sha256:abc123..."

# Tag and push image
docker tag myapp:latest $REGION.ocir.io/$TENANCY/app-images/myapp:latest
docker push $REGION.ocir.io/$TENANCY/app-images/myapp:latest
```

### OCI Container Engine for Kubernetes (OKE)

```bash
# List OKE clusters
oci ce cluster list --compartment-id $COMPARTMENT_ID

# Create OKE cluster (new VCN)
oci ce cluster create \
  --display-name "prod-cluster" \
  --compartment-id $COMPARTMENT_ID \
  --vcn-id $VCN_OCID \
  --kubernetes-version "v1.28.2" \
  --service-lb-subnet-ids '["ocid1.subnet.oc1.iad.xxx"]'

# Create OKE cluster (custom VCN)
oci ce cluster create \
  --display-name "custom-vcn-cluster" \
  --compartment-id $COMPARTMENT_ID \
  --vcn-id $VCN_OCID \
  --kubernetes-version "v1.28.2" \
  --endpoint-config '{"is_public_ip_enabled": true}'

# Get kubeconfig
oci ce cluster get-kubeconfig \
  --cluster-id $CLUSTER_OCID \
  --file "$HOME/.kube/config"

# Create node pool
oci ce node-pool create \
  --display-name "prod-nodepool" \
  --cluster-id $CLUSTER_OCID \
  --compartment-id $COMPARTMENT_ID \
  --node-shape VM.Standard.E4.Flex \
  --node-shape-config '{"ocpus": 2, "memoryInGBs": 16}' \
  --size 3

# Update node pool scaling
oci ce node-pool update \
  --node-pool-id $NODES_OCID \
  --size 5
```

### Functions

```bash
# List applications
oci fn application list --compartment-id $COMPARTMENT_ID

# Create application
oci fn application create \
  --display-name "image-processor" \
  --compartment-id $COMPARTMENT_ID \
  --subnet-ids '["ocid1.subnet.oc1.iad.xxx"]'

# Update application config
oci fn application update \
  --application-id $APP_OCID \
  --config '{"KEY": "VALUE"}'

# List functions
oci fn function list --application-id $APP_OCID

# Deploy function
oci fn function update \
  --function-id $FN_OCID \
  --image $REGION.ocir.io/$TENANCY/myfunc:latest \
  --memory-in-mbs 256

# Invoke function
oci fn invocation invoke \
  --function-id $FN_OCID \
  --body '{"action": "process"}'
```

### Resource Manager (Terraform)

```bash
# List stacks
oci resourcemanager stack list --compartment-id $COMPARTMENT_ID

# Create stack
oci resourcemanager stack create \
  --display-name "app-infrastructure" \
  --compartment-id $COMPARTMENT_ID \
  --config-source "ZIP" \
  --terraform-version "1.1" \
  --zip-file-base64-encoded "$(base64 -w0 terraform.zip)"

# Get terraform plan
oci resourcemanager stack plan \
  --stack-id $STACK_OCID

# Apply terraform
oci resourcemanager stack apply \
  --stack-id $STACK_OCID

# Get drift detection
oci resourcemanager stack drift-detection \
  --stack-id $STACK_OCID
```

### API Gateway

```bash
# List APIs
oci apigateway api list --compartment-id $COMPARTMENT_ID

# Create API
oci apigateway api create \
  --display-name "mobile-api" \
  --compartment-id $COMPARTMENT_ID \
  --type "REST" \
  --target-backend "http://backend:8080"

# Deploy API
oci apigateway deployment create \
  --api-id $API_OCID \
  --display-name "prod-deployment" \
  --path-prefix "/api/v1" \
  --specification "{...}"

# Create usage plan
oci apigateway usage-plan create \
  --display-name "premium-plan" \
  --compartment-id $COMPARTMENT_ID
```

---

## Migration Patterns

### Lift-and-Shift Pattern

Moving applications to OCI without code changes:

```bash
# 1. Assess current environment
# Identify: VMs, dependencies, networking

# 2. Create matching VCN
oci network vcn create --display-name "prod-vcn" --cidr-block "10.0.0.0/16"

# 3. Create subnets
oci network subnet create --display-name "app-subnet" --cidr-block "10.0.1.0/24"

# 4. Launch compute instances
oci compute instance launch --display-name "app-server" \
  --shape VM.Standard.E4.Flex \
  --image-id $CUSTOM_IMAGE_OCID

# 5. Attach block storage
oci bv attachment attach --instance-id $INSTANCE_OCID --volume-id $VOLUME_OCID
```

### Re-Architect Pattern

Modernizing applications for OCI:

```bash
# 1. Create OKE cluster
oci ce cluster create --display-name "prod-cluster" --kubernetes-version "v1.28"

# 2. Create container image repository
oci artifacts container repository create --display-name "app-images"

# 3. Push application image
docker push $REGION.ocir.io/$TENANCY/app-images/app:v1

# 4. Deploy to OKE
kubectl apply -f deployment.yaml

# 5. Create API Gateway
oci apigateway api create --display-name "app-api"

# 6. Create Functions for serverless
oci fn application create --display-name "api-handler"
```

### Container-Based Migration

```bash
# 1. Create OKE cluster
oci ce cluster create --display-name "prod-cluster"

# 2. Create registry
oci artifacts container repository create --display-name "production"

# 3. Build and push image
docker build -t myapp:latest .
docker tag myapp:latest $REGION.ocir.io/$TENANCY/production/myapp:v1
docker push $REGION.ocir.io/$TENANCY/production/myapp:v1

# 4. Create deployment YAML
# (application yaml with replicas, health checks, etc.)

# 5. Deploy
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# 6. Set up ingress
kubectl apply -f k8s/ingress.yaml
```

---

## Anti-Patterns Section

**NEVER generate the following in OCI examples:**

### Other Cloud Container Commands (DO NOT USE)

```bash
# WRONG - AWS EKS
aws eks create-cluster
aws ecr create-repository

# WRONG - Azure AKS
az aks create
az acr create

# WRONG - GCP GKE
gcloud container clusters create
gcloud container images list
```

### Common Anti-Patterns

1. **Never use EKS for OCI** - Use OKE
2. **Never use AKS for OCI** - Use OKE
3. **Never use GKE for OCI** - Use OKE
4. **Never use AWS ECR** - Use OCI Container Registry
5. **Never use Azure Container Registry** - Use OCI Container Registry
6. **Never use GCP Container Registry** - Use OCI Container Registry
7. **Never use Lambda terminology** - Use OCI Functions
8. **Never use Azure Functions terminology** - Use OCI Functions
9. **Never use Cloud Functions** - Use OCI Functions
10. **Never use other cloud's API Gateway** - Use OCI API Gateway

### OCID Format Requirements

```bash
# Correct OCID format for applications
ocid1.integrationinstance.oc1.iad.xxx...
ocid1.processautomationinstance.oc1.iad.xxx...
ocid1.cluster.oc1.iad.xxx...
ocid1.nodepool.oc1.iad.xxx...
ocid1.application.oc1.iad.xxx...
ocid1.function.oc1.iad.xxx...
ocid1.apigatewayapi.oc1.iad.xxx...
ocid1.containerrepository.oc1.iad.xxx...
ocid1.stack.oc1.iad.xxx...
```

---

## Oracle Integration Cloud Migration

### Migration from Oracle Integration Cloud (OIC) Classic

```bash
# 1. Export from OIC Classic
# Use: Integrations > Export > Download JAR

# 2. Create new OIC Gen 3 instance
oci oic integration-instance create \
  --display-name "prod-gen3" \
  --integration-instance-type "STANDARD" \
  --pack-version "23.04.0"

# 3. Import integrations
oci oic integration import \
  --integration-instance-id $OIC_OCID \
  --file "@exported-integration.jar"

# 4. Update connections
oci oic connection update \
  --integration-instance-id $OIC_OCID \
  --connection-id $CONN_OCID

# 5. Activate and test
oci oic integration activate --integration-id $INT_OCID
```

### Process Automation Migration

```bash
# 1. Export process applications
# Use: Process > Applications > Export

# 2. Create OPA instance
oci opa process-automation-instance create \
  --display-name "prod-opa" \
  --pack-version "23.04.0"

# 3. Import applications
oci opa application import \
  --process-automation-instance-id $OPA_OCID \
  --file "@exported-app.zip"

# 4. Configure connections
oci opa connection update --connection-id $CONN_OCID

# 5. Publish application
oci opa application publish --application-id $APP_OCID
```