# Prompt Template: oci-troubleshooting/compute

## Context

Generate examples about troubleshooting OCI Compute issues.

## Topics

- Instance stuck in provisioning
- Boot volume issues
- Shape allocation failures
- SSH key problems
- Instance lifecycle errors
- Instance console access
- Termination protection

## Difficulty Distribution

- beginner (30%): SSH access, basic issues
- intermediate (50%): Provisioning, boot volumes
- advanced (20%): Complex lifecycle issues

## Quality Rules

- Include diagnostic steps
- Reference console access
- Explain common failure causes

## OCI Diagnostic CLI Syntax

Use these real OCI CLI commands for Compute troubleshooting:

```bash
# Instance details and status
oci compute instance get --instance-id ocid1.instance.oc1.<region>.<unique-id>

# Instance lifecycle state
oci compute instance list --compartment-id ocid1.compartment.oc1.<region>.<unique-id> --lifecycle-state RUNNING

# Boot volume attachment
oci compute volume-attachment list --instance-id ocid1.instance.oc1.<region>.<unique-id>
oci blockstorage volume get --volume-id ocid1.bootvolume.oc1.<region>.<unique-id>

# VNIC and network info
oci compute vnic list --instance-id ocid1.instance.oc1.<region>.<unique-id>
oci network vnic get --vnic-id ocid1.vnic.oc1.<region>.<unique-id>

# Console history (for troubleshooting stuck instances)
oci compute console-history capture --instance-id ocid1.instance.oc1.<region>.<unique-id>
oci compute console-history get --console-history-id ocid1.consolehistory.oc1.<region>.<unique-id>

# SSH key verification
oci compute instance list --compartment-id ocid1.compartment.oc1.<region>.<unique-id> --query "data[?\"display-name\"=='your-instance']"

# Shape availability
oci compute shape list --compartment-id ocid1.compartment.oc1.<region>.<unique-id> --availability-domain "AD1"

# Instance actions (lifecycle operations)
oci compute instance action --instance-id ocid1.instance.oc1.<region>.<unique-id> --action STOP
oci compute instance action --instance-id ocid1.instance.oc1.<region>.<unique-id> --action RESET

# Capacity reservation check
oci compute capacity-report get --capacity-report-id ocid1.capacityreport.oc1.<region>.<unique-id>

# Dedicated VM host
oci compute dedicated-vm-host get --dedicated-vm-host-id ocid1.dedicatedvmhost.oc1.<region>.<unique-id>
```

## OCID Format

OCI resource identifiers follow this pattern:

```
ocid1.<resource-type>.<realm>.<region>.<unique-id>

Examples:
- ocid1.instance.oc1.sa-vinhedo-1.abcd1234...
- ocid1.bootvolume.oc1.sa-vinhedo-1.abcd1234...
- ocid1.vnic.oc1.sa-vinhedo-1.abcd1234...
- ocid1.consolehistory.oc1.sa-vinhedo-1.abcd1234...
- ocid1.dedicatedvmhost.oc1.sa-vinhedo-1.abcd1234...

Key patterns:
- realm: sa-vinhedo-1, sa-saopaulo-1, us-ashburn-1, etc.
- resource-type: instance, bootvolume, vnic, consolehistory, dedicatedvmhost
- unique-id: 32+ char alphanumeric string
```

## Anti-Patterns

**NEVER generate:**

- ❌ "Reset the instance" without mentioning console history for diagnosis
- ❌ SSH troubleshooting without mentioning key formats (RSA, ED25519)
- ❌ Shape allocation advice without checking availability in AD/region
- ❌ Boot volume issues without checking volume state and attachment
- ❌ "Just terminate and recreate" without diagnosing root cause
- ❌ Copy OCI documentation verbatim
- ❌ Suggest shape changes without explaining why current shape failed
- ❌ Instance recovery without mentioning console access options
- ❌ Termination protection discussions without explaining how to disable

## Common Issues

- Instance stuck in "Provisioning" or "Starting"
- SSH connection refused (wrong key, port 22 blocked)
- Instance unreachable after reboot
- Shape unavailable in region
- Boot volume not attaching
- Console access needed for recovery

## Example Questions

- "Instância travada em provisioning"
- "Não consigo fazer SSH na instância"
- "Shape não disponível na região"
- "Boot volume não anexa"
- "Como acessar console da instância?"