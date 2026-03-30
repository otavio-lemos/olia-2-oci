# Prompt Template: oci-core/compute

## Context

Generate examples about OCI Compute service including instances, shapes, instance pools, auto-scaling, custom images, and boot volumes.

## Topics

- Instance creation and management
- Shape selection (VM.Standard2, VM.Standard.E4, VM.Optimized3, Ampere A1)
- Instance pools and auto-scaling
- Custom images
- Boot volumes
- HPC instances

## Difficulty Distribution

- beginner (30%): Basic instance creation, shape overview
- intermediate (50%): Instance pools, auto-scaling, custom images
- advanced (20%): HPC, performance tuning, multi-instance architectures

## Example Prompts

### Beginner
```
Como criar uma instância de compute no OCI?
```

### Intermediate
```
Como configurar um instance pool com auto-scaling no OCI?
```

### Advanced
```
Como criar uma arquitetura de alta disponibilidade com instance pool e load balancer?
```

## Quality Rules

- Always mention specific shape names
- Include console steps AND CLI/SDK where relevant
- Explain when to use each shape type
- Mention costs with [MUTABLE] tag
- Include performance considerations
