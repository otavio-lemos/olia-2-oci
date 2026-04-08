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

---

## OCID Format

OCI resource identifiers follow this pattern:

```
ocid1.<resource_type>.oc1.<region>.<unique_id>
```

Common compute OCIDs:

| Resource | OCID Pattern | Example |
|----------|--------------|---------|
| Instance | `ocid1.instance.oc1.<region>.<unique-id>` | `ocid1.instance.oc1.sa-saopaulo-1.aaaaaaa...` |
| Shape | Built-in | `VM.Standard2.4`, `VM.Standard.E4.Flex`, `VM.Optimized3.Flex`, `Ampere2.A1.Flex` |
| Instance Pool | `ocid1.instancepool.oc1.<region>.<unique-id>` | `ocid1.instancepool.oc1.sa-saopaulo-1.bbbbbbb...` |
| Instance Configuration | `ocid1.instanceconfiguration.oc1.<region>.<unique-id>` | `ocid1.instanceconfiguration.oc1.sa-saopaulo-1.ccccccc...` |
| Boot Volume | `ocid1.bootvolume.oc1.<region>.<unique-id>` | `ocid1.bootvolume.oc1.sa-saopaulo-1ddddddd...` |
| Boot Volume Backup | `ocid1.bootvolumebackup.oc1.<region>.<unique-id>` | `ocid1.bootvolumebackup.oc1.sa-saopaulo-1.eeeeee...` |
| Custom Image | `ocid1.image.oc1.<region>.<unique-id>` | `ocid1.image.oc1.sa-saopaulo-1.fffffff...` |
| Dedicated VM Host | `ocid1.dedicatedhost.oc1.<region>.<unique-id>` | `ocid1.dedicatedhost.oc1.sa-saopaulo-1.ggggggg...` |
| Compartment | `ocid1.compartment.oc1.<region>.<unique-id>` | `ocid1.compartment.oc1.sa-saopaulo-1.hhhhhhh...` |
| Subnet | `ocid1.subnet.oc1.<region>.<unique-id>` | `ocid1.subnet.oc1.sa-saopaulo-1.iiiiiii...` |

**Region codes**: `sa-saopaulo-1`, `us-ashburn-1`, `us-phoenix-1`, `eu-frankfurt-1`, `ap-tokyo-1`

---

## OCI CLI Syntax

### Instance Operations

```bash
# List available shapes
oci compute shape list --compartment-id $COMPARTMENT_ID --availability-domain $AD

# Launch instance
oci compute instance launch \
    --compartment-id $COMPARTMENT_ID \
    --display-name "web-server" \
    --availability-domain "aaaa:sa-saopaulo-1" \
    --shape "VM.Standard2.4.Flex" \
    --shape-config '{"memory-in-gbs": 16, "ocpus": 4}' \
    --source-boot-volume-id "$BOOT_VOLUME_ID" \
    --subnet-id $SUBNET_ID

# Or using image
oci compute instance launch \
    --compartment-id $COMPARTMENT_ID \
    --display-name "web-server" \
    --availability-domain "aaaa:sa-saopaulo-1" \
    --image-id "ocid1.image.oc1.sa-saopaulo-1.aaaaaaa..." \
    --shape "VM.Standard2.4.Flex" \
    --shape-config '{"memory-in-gbs": 16, "ocpus": 4}' \
    --subnet-id $SUBNET_ID

# Get instance details
oci compute instance get --instance-id $INSTANCE_ID

# List instances
oci compute instance list --compartment-id $COMPARTMENT_ID

# Stop instance
oci compute instance stop --instance-id $INSTANCE_ID --preserve-boot-volume true --force

# Start instance
oci compute instance start --instance-id $INSTANCE_ID

# Terminate instance
oci compute instance terminate --instance-id $INSTANCE_ID --preserve-boot-volume false --force
```

### Instance Pool Operations

```bash
# Create instance configuration
oci compute instance-configuration create \
    --compartment-id $COMPARTMENT_ID \
    --display-name "web-config" \
    --instance-details '{"instanceType": "compute", "compute": {"shape": "VM.Standard2.4.Flex", "shapeConfig": {"memoryInGBs": 16, "ocpus": 4}, "sourceDetails": {"imageId": "$IMAGE_ID", "sourceType": "image"}}' \
    --defined-tags '{"tag-namespace": {"key": "value"}}' \
    --freeform-tags '{"environment": "prod"}'

# Create instance pool
oci compute instance-pool create \
    --compartment-id $COMPARTMENT_ID \
    --display-name "web-pool" \
    --instance-configuration-id $INSTANCE_CONFIG_ID \
    --size 3 \
    --availability-domains '["aaaa:sa-saopaulo-1", "bbbb:sa-saopaulo-1"]'

# Get instance pool details
oci compute instance-pool get --instance-pool-id $POOL_ID

# List instance pools
oci compute instance-pool list --compartment-id $COMPARTMENT_ID
```

### Auto-Scaling

```bash
# Attach auto-scaling configuration
oci compute instance-pool attach-autoscaling-configuration \
    --instance-pool-id $POOL_ID \
    --autoscaling-configuration '{"cool-down-in-seconds": 300, "policy": {"policy-type": "threshold", "metric": "CPU_UTILIZATION", "threshold": {"operator": "GT", "value": 80}, "action": {"type": "INCREMENT", "value": 1}, "max": 10, "min": 3}}'
```

### Custom Image Operations

```bash
# Create custom image from instance
oci compute image create \
    --compartment-id $COMPARTMENT_ID \
    --instance-id $INSTANCE_ID \
    --display-name "web-server-image"

# Create image from boot volume
oci compute image create-from-boot-volume \
    --compartment-id $COMPARTMENT_ID \
    --boot-volume-id $BOOT_VOLUME_ID \
    --display-name "custom-image"

# Get image details
oci compute image get --image-id $IMAGE_ID

# List custom images
oci compute image list --compartment-id $COMPARTMENT_ID
```

### Boot Volume Operations

```bash
# List boot volumes
oci bv boot-volume list --compartment-id $COMPARTMENT_ID --availability-domain $AD

# Create boot volume
oci bv boot-volume create \
    --compartment-id $COMPARTMENT_ID \
    --availability-domain "aaaa:sa-saopaulo-1" \
    --size-in-gbs 50 \
    --shape "VM.Standard2.4" \
    --backup-policy-id "ocid1.bootvolumebackuppolicy.oc1..."

# Create boot volume backup
oci bv boot-volume-backup create \
    --boot-volume-id $BOOT_VOLUME_ID \
    --display-name "web-backup"

# Restore boot volume from backup
oci bv boot-volume restore \
    --boot-volume-id $BOOT_VOLUME_ID \
    --boot-volume-backup-id $BACKUP_ID
```

### HPC Instances

```bash
# Launch HPC instance
oci compute instance launch \
    --compartment-id $COMPARTMENT_ID \
    --display-name "hpc-cluster" \
    --availability-domain "aaaa:sa-saopaulo-1" \
    --shape "BM.HPC2.36" \
    --shape-config '{"memory-in-gbs": 384, "ocpus": 36}' \
    --source-boot-volume-id "$BOOT_VOLUME_ID" \
    --subnet-id $SUBNET_ID
```

---

## Anti-Patterns

NEVER generate:

1. **Inaccurate OCIDs**: Never invent fake OCIDs. Use format `ocid1.instance.oc1.<region>.<32-char-hex>` - if uncertain, use placeholder like `$INSTANCE_ID`

2. **Wrong shape family**: Never confuse AMD (VM.Standard2, VM.Optimized3) with Intel (VM.Standard.E4) or ARM (Ampere A1) - each has different use cases

3. **MissingFlex vs Fixed shapes**: Never omit `VM.Standard2.4.Flex` vs `VM.Standard2.4` difference - Flex allows custom OCPU/memory ratios

4. **OCPU vs Core confusion**: Never confuse OCI's OCPU (virtual CPU, equals 2 vCPUs) with physical cores. "4 OCPUs" = 2 physical cores = 4 vCPUs in legacy terms

5. **Incorrect CLI service**: Never use `oci bv` for compute images (use `oci compute image`) or confuse boot volume operations

6. **Auto-scaling without cooldown**: Never suggest auto-scaling without cooldown period - causes flapping (rapid scale up/down cycles)

7. **Instance pool without load balancer**: Never recommend instance pool for production without explaining need for load balancer distribution

8. **Custom image with sensitive data**: Never suggest creating custom image from instance with embedded credentials, keys, or sensitive data

9. **Wrong shape for workload**: Never recommend GPU shapes (BM.GPU4.8, BM.GPU3.8) for general compute, or Ampere for legacy Windows workloads requiring vTPM

10. **Termination without backup**: Never terminate instance without explaining boot volume data loss - always confirm backups exist