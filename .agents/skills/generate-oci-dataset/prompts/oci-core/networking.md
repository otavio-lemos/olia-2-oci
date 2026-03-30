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
