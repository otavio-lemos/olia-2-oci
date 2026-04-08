# Prompt Template: oci-troubleshooting/connectivity

## Context

Generate examples about troubleshooting OCI connectivity issues.

## Topics

- Instance not accessible from internet
- Routing issues
- Security List / NSG problems
- DNS issues
- VPN/FastConnect problems
- MTU issues

## Difficulty Distribution

- beginner (20%): Basic connectivity checks
- intermediate (50%): Firewall rules, routing
- advanced (30%): Complex hybrid connectivity

## Quality Rules

- Provide step-by-step troubleshooting
- Include diagnostic commands (ping, traceroute, curl)
- Reference specific OCI resources
- Explain common causes

## OCI Diagnostic CLI Syntax

Use these real OCI CLI commands for connectivity troubleshooting:

```bash
# VCN and Subnet inspection
oci network vcn get --vcn-id ocid1.vcn.oc1.<region>.<unique-id>
oci network subnet get --subnet-id ocid1.subnet.oc1.<region>.<unique-id>

# Security List rules
oci network security-list get --security-list-id ocid1.securitylist.oc1.<region>.<unique-id>
oci network security-list rules list --security-list-id ocid1.securitylist.oc1.<region>.<unique-id>

# NSG (Network Security Group)
oci network nsg get --nsg-id ocid1.nsg.oc1.<region>.<unique-id>
oci network nsg rules list --nsg-id ocid1.nsg.oc1.<region>.<unique-id>

# Routing tables
oci network route-table get --rt-id ocid1.routetable.oc1.<region>.<unique-id>

# Internet Gateway
oci network igw get --igw-id ocid1.internetgateway.oc1.<region>.<unique-id>

# NAT Gateway
oci network nat-gateway get --nat-gateway-id ocid1.natgateway.oc1.<region>.<unique-id>

# DRG (Dynamic Routing Gateway)
oci network drg get --drg-id ocid1.drg.oc1.<region>.<unique-id>

# Local Peering Gateway
oci network lpg get --lpg-id ocid1.localpeeringgateway.oc1.<region>.<unique-id>

# Instance VNIC info
oci compute instance get --instance-id ocid1.instance.oc1.<region>.<unique-id>
oci compute vnic list --instance-id ocid1.instance.oc1.<region>.<unique-id>

# IPSec VPN
oci network ipsec-connection get --ipsc-id ocid1.ipsecconnection.oc1.<region>.<unique-id>

# FastConnect
oci network virtual-circuit get --virtual-circuit-id ocid1.virtualcircuit.oc1.<region>.<unique-id>
```

## OCID Format

OCI resource identifiers follow this pattern:

```
ocid1.<resource-type>.<realm>.<region>.<unique-id>

Examples:
- ocid1.vcn.oc1.sa-vinhedo-1.abcd1234...
- ocid1.subnet.oc1.sa-vinhedo-1.abcd1234...
- ocid1.instance.oc1.sa-vinhedo-1.abcd1234...
- ocid1.securitylist.oc1.sa-vinhedo-1.abcd1234...
- ocid1.nsg.oc1.sa-vinhedo-1.abcd1234...
- ocid1.internetgateway.oc1.sa-vinhedo-1.abcd1234...

Key patterns:
- realm: sa-vinhedo-1, sa-saopaulo-1, us-ashburn-1, etc.
- resource-type: vcn, subnet, instance, securitylist, nsg, etc.
- unique-id: 32+ char alphanumeric string
```

## Anti-Patterns

**NEVER generate:**

- ❌ Generic "check firewall" without specifying Security List or NSG rules
- ❌ "Use public subnet" without explaining security implications
- ❌ Routing advice without referencing specific route tables or VCN topology
- ❌ VPN troubleshooting without mentioning IPSec or FastConnect specifics
- ❌ DNS resolution advice without mentioning OCI DNS or DNS proxy
- ❌ Copy OCI documentation verbatim
- ❌ Invent non-existent OCI services or features
- ❌ Suggest modifications without explaining impact
- ❌ Provide IP addresses without noting they are mutable
- ❌ Performance tuning without considering shape/instance type

## Common Issues

- Instance not accessible from internet (check IGW, Security List, NSG)
- Routing issues (check route table, DRG attachments)
- Security List / NSG problems (verify ingress/egress rules)
- DNS issues (check DNS resolver, VCN DNS configuration)
- VPN/FastConnect problems (check tunnel status, BGP session)
- MTU issues (verify path MTU, VCN MTU settings)

## Example Questions

- "Instância não acessível pela internet"
- "Problemas de roteamento entre VCNs"
- "Security List não permite conexão"
- "DNS não resolve nomes internos"
- "VPN IPSec não estabelece túnel"