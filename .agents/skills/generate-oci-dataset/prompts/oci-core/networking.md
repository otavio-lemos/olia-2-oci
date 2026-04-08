# Prompt Template: oci-core/networking

## Context

Generate examples about OCI Networking including VCN, subnets, Security Lists, NSGs, Route Tables, DRG, VPN, FastConnect, Load Balancing.

## Topics

- VCN design and CIDR blocks
- Subnets (public/private)
- Security Lists vs Network Security Groups
- Route Tables
- DRG (Dynamic Routing Gateway)
- VPN Connect
- FastConnect
- Load Balancing

## Difficulty Distribution

- beginner (30%): VCN creation, basic subnets
- intermediate (40%): Security rules, NSG, routing
- advanced (30%): Hybrid connectivity, DRG, complex architectures

## Quality Rules

- Always use correct OCI terminology (VCN, not "virtual network")
- Distinguish Security Lists from NSGs
- Explain when to use VPN vs FastConnect
- Include specific OCI resource names
- Tag mutable content with [MUTABLE]

---

## OCID Format

OCI resource identifiers follow this pattern:

```
ocid1.<resource_type>.oc1.<region>.<unique_id>
```

Common networking OCIDs:

| Resource | OCID Pattern | Example |
|----------|--------------|---------|
| VCN | `ocid1.vcn.oc1.<region>.<unique-id>` | `ocid1.vcn.oc1.sa-saopaulo-1.aaaaaaa...` |
| Subnet | `ocid1.subnet.oc1.<region>.<unique-id>` | `ocid1.subnet.oc1.sa-saopaulo-1.bbbbbbb...` |
| Security List | `ocid1.securitylist.oc1.<region>.<unique-id>` | `ocid1.securitylist.oc1.sa-saopaulo-1.ccccccc...` |
| Network Security Group | `ocid1.networksecuritygroup.oc1.<region>.<unique-id>` | `ocid1.networksecuritygroup.oc1.sa-saopaulo-1ddddddd...` |
| Route Table | `ocid1.routetable.oc1.<region>.<unique-id>` | `ocid1.routetable.oc1.sa-saopaulo-1.eeeeee...` |
| DRG | `ocid1.drg.oc1.<region>.<unique-id>` | `ocid1.drg.oc1.sa-saopaulo-1.fffffff...` |
| Load Balancer | `ocid1.loadbalancer.oc1.<region>.<unique-id>` | `ocid1.loadbalancer.oc1.sa-saopaulo-1.ggggggg...` |
| Internet Gateway | `ocid1.internetgateway.oc1.<region>.<unique-id>` | `ocid1.internetgateway.oc1.sa-saopaulo-1.hhhhhhh...` |
| Nat Gateway | `ocid1.natgateway.oc1.<region>.<unique-id>` | `ocid1.natgateway.oc1.sa-saopaulo-1.iiiiiii...` |
| Compartment | `ocid1.compartment.oc1.<region>.<unique-id>` | `ocid1.compartment.oc1.sa-saopaulo-1.jjjjjjj...` |

**Region codes**: `sa-saopaulo-1`, `us-ashburn-1`, `us-phoenix-1`, `eu-frankfurt-1`, `ap-tokyo-1`

---

## OCI CLI Syntax

### VCN Operations

```bash
# List VCNs
oci network vcn list --compartment-id $COMPARTMENT_ID

# Create VCN
oci network vcn create \
    --cidr-block 10.0.0.0/16 \
    --compartment-id $COMPARTMENT_ID \
    --display-name "my-vcn" \
    --dns-label "myvcn"

# Get VCN details
oci network vcn get --vcn-id $VCN_ID

# Delete VCN
oci network vcn delete --vcn-id $VCN_ID --force
```

### Subnet Operations

```bash
# List subnets
oci network subnet list --comnet-id $COMPARTMENT_ID --vcn-id $VCN_ID

# Create subnet
oci network subnet create \
    --compartment-id $COMPARTMENT_ID \
    --vcn-id $VCN_ID \
    --cidr-block 10.0.1.0/24 \
    --display-name "public-subnet" \
    --prohibit-public-ip-on-vlan false \
    --dns-label "publicsubnet"

# Get subnet details
oci network subnet get --subnet-id $SUBNET_ID
```

### Security List Operations

```bash
# Create security list with rules
oci network security-list create \
    --compartment-id $COMPARTMENT_ID \
    --vcn-id $VCN_ID \
    --display-name "web-security-list" \
    --egress-security-rules '[{"destination": "0.0.0.0/0", "protocol": "all", "is-stateless": false}]' \
    --ingress-security-rules '[{"source": "0.0.0.0/0", "protocol": "6", "port": {"min": 80, "max": 80}, "tcp-options": {"destination-port-range": {"min": 80, "max": 80}}}]'
```

### Network Security Group (NSG)

```bash
# Create NSG
oci network nsg create \
    --compartment-id $COMPARTMENT_ID \
    --vcn-id $VCN_ID \
    --display-name "app-nsg"

# Add NSG security rule
oci network nsg security-rules create \
    --nsg-id $NSG_ID \
    --security-rules '[{"direction": "INGRESS", "protocol": "6", "source": "10.0.0.0/16", "port": {"min": 443, "max": 443}}]'
```

### Route Table

```bash
# Create route table with DRG attachment
oci network route-table create \
    --compartment-id $COMPARTMENT_ID \
    --vcn-id $VCN_ID \
    --display-name "prod-route-table" \
    --route-rules '[{"destination": "0.0.0.0/0", "network-element-id": "$DRG_ID", "network-entity-type": "drg"}]'
```

### DRG

```bash
# Create DRG
oci network drg create \
    --compartment-id $COMPARTMENT_ID \
    --display-name "prod-drg"

# Attach VCN to DRG
oci network drg-attachment create \
    --drg-id $DRG_ID \
    --vcn-id $VCN_ID
```

### Load Balancer

```bash
# Create load balancer
oci lb load-balancer create \
    --compartment-id $COMPARTMENT_ID \
    --display-name "app-lb" \
    --subnet-ids '["$SUBNET_ID"]' \
    --shape "flexible" \
    --shape-details '{"minimum-bandwidth-in-mbps": 100, "maximum-bandwidth-in-mbps": 200}' \
    --scheme "IP_VERSION_2" \
    --type "Application"

# Add backend
oci lb backend create \
    --load-balancer-id $LB_ID \
    --backend-set-name "backend-set-1" \
    --ip-address "10.0.1.10" \
    --port 8080

# Add listener
oci lb listener create \
    --load-balancer-id $LB_ID \
    --default-backend-set-name "backend-set-1" \
    --port 443 \
    --protocol "HTTP"
```

--- Anti-Patterns

NEVER generate:

1. **Inaccurate OCIDs**: Never invent fake OCIDs. Use format `ocid1.<resource>.oc1.<region>.<32-char-hex>` - if uncertain, use placeholder like `$VCN_ID`

2. **Wrong CLI commands**: Never use `oci compute instance` for networking - use correct service: `oci network vcn`, `oci network subnet`, `oci lb`

3. **Security List confusion**: Never recommend Security Lists for stateful L7 rules that require tracking - use NSGs instead. Never recommend NSGs when Security Lists would suffice

4. **Non-existent services**: Never invent services like "VCN Peering Gateway" (use Remote Peering instead), "Private Endpoint" (use Private IP), or "Network Firewall"

5. **Incorrect CIDR**: Never use overlapping CIDRs (e.g., 10.0.0.0/8 and 10.0.1.0/24 in same VCN). Minimum /16 for VCN, /24 for subnets recommended

6. **VPN/FastConnect wrong choice**: Never suggest VPN for high-bandwidth (>250 Mbps) or latency-sensitive workloads - recommend FastConnect. Never suggest FastConnect for simple test/dev scenarios

7. **Missing ingress rule complement**: Never add only egress or only ingress rule without explaining stateful behavior in Security Lists (automatically returns traffic)

8. **VCN DNS confusion**: Never confuse VCN DNS resolver (for private resolved) with public DNS - VCN DNS only resolves within VCNCIDRs