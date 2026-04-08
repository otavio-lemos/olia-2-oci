# Prompt Template: oci-core/load-balancing

## Context

Generate examples about OCI Load Balancing service.

## Topics

- Load Balancer (HTTP, TCP, SSL)
- Backend sets and servers
- Listeners
- SSL certificates
- Health checks
- Path routing policies

## Difficulty Distribution

- beginner (30%): Basic Load Balancer creation
- intermediate (50%): SSL configuration, health checks
- advanced (20%): Complex routing, performance tuning

## Quality Rules

- Distinguish between HTTP, TCP, and SSL listeners
- Include SSL certificate configuration
- Reference Load Balancer shapes
- Tag mutable content with [MUTABLE]

## OCI CLI Syntax

Use these commands as reference:

```bash
# Create Load Balancer
oci lb load-balancer create \
  --compartment-id ocid1.compartment.oc1.<region>.<unique-id> \
  --display-name "my-load-balancer" \
  --shape "flexible" \
  --shape-details '{"minimumBandwidthMbps": 100, "maximumBandwidthMbps": 300}' \
  --subnet-ids '["ocid1.subnet.oc1.<region>.<unique-id>"]' \
  --reserved-public-ip-id ocid1.publicip.oc1.<region>.<unique-id>

# Create Backend Set
oci lb backend-set create \
  --load-balancer-id ocid1.loadbalancer.oc1.<region>.<unique-id> \
  --name "backend-set-web" \
  --policy "ROUND_ROBIN" \
  --health-checker '{"protocol": "HTTP", "port": 80, "urlPath": "/health"}'

# Update Backend
oci lb backend update \
  --load-balancer-id ocid1.loadbalancer.oc1.<region>.<unique-id> \
  --backend-set-name "backend-set-web" \
  --ip-address "10.0.0.5" \
  --port 8080 \
  --target-id ocid1.instance.oc1.<region>.<unique-id>

# Create Listener
oci lb listener create \
  --load-balancer-id ocid1.loadbalancer.oc1.<region>.<unique-id> \
  --name "listener-https" \
  --default-backend-set-name "backend-set-web" \
  --protocol "HTTPS" \
  --port 443

# Upload SSL Certificate
oci lb certificate create \
  --load-balancer-id ocid1.loadbalancer.oc1.<region>.<unique-id> \
  --certificate-name "my-ssl-cert" \
  --public-certificate "$(cat cert.pem)" \
  --private-key "$(cat key.pem)" \
  --ca-certificate "$(cat ca.pem)"
```

## OCID Format

Always use these patterns:

- Load Balancer: `ocid1.loadbalancer.oc1.<region>.<unique-id>`
- Backend Set: `ocid1.loadbalancerbackendset.oc1.<region>.<unique-id>`
- Listener: `ocid1.loadbalancerlistener.oc1.<region>.<unique-id>`
- Certificate: `ocid1.loadbalancercertificate.oc1.<region>.<unique-id>`
- Subnet: `ocid1.subnet.oc1.<region>.<unique-id>`
- Compartment: `ocid1.compartment.oc1.<region>.<unique-id>`
- Reserved Public IP: `ocid1.publicip.oc1.<region>.<unique-id>`

## Anti-Patterns

NEVER generate:
- Commands without `--compartment-id` or `--load-balancer-id`
- Invalid listener protocols (use HTTP, HTTP2, TCP, UDP)
- SSL certificates without proper CA bundle chain
- Health checks without proper path for HTTP
- Mixing flexible and fixed shapes in same lb
- Missing backend servers in backend-set
- Using IP addresses instead of instance OCIDs for backends
- Creating listeners without associated backend-set

## Example Questions

- "Como criar Load Balancer para aplicação web?"
- "Configurar SSL certificate no Load Balancer"
- "Health check não funciona, como debugar?"