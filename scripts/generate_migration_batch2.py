#!/usr/bin/env python3
"""
Generate remaining Migration JSONL files (11 files).
"""

import json
import os

OUTPUT_DIR = "/Users/otaviolemos/ml/olia-2-oci/data/curated"

def create_example(category, cat_path, difficulty, question, answer, system_prompt):
    return {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question},
            {"role": "assistant", "content": answer}
        ],
        "metadata": {"category": cat_path, "difficulty": difficulty, "source": "generated"}
    }

def write_jsonl(filename, examples):
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        for example in examples:
            f.write(json.dumps(example, ensure_ascii=False) + '\n')
    print(f"Generated: {filepath} ({len(examples)} examples)")

# ============ MIGRATION AZURE COMPUTE ============
def generate_migration_azure_compute():
    examples = []
    system = "You are an OCI migration specialist with expertise in Azure to OCI migrations. Provide technical guidance on Azure VM to OCI Compute migration."
    cat = "migration/azure-compute"
    
    examples.append(create_example("migration-azure-compute", cat, "beginner",
        "Como mapear Azure VMs para OCI Compute?",
        "Mapeamento Azure VMs → OCI Compute:\n\n**Series mapping:**\n- Azure B-series → VM.Standard.E4.Flex (burstable)\n- Azure D-series → VM.Standard.E4.Flex (general purpose)\n- Azure F-series → VM.Optimized3 (compute optimized)\n- Azure E-series → VM.Optimized3 (memory optimized)\n\n**Examples:**\n- Standard_B2s (2 vCPU, 4GB) → VM.Standard.E4.Flex (1 OCPU, 4GB)\n- Standard_D2s_v3 (2 vCPU, 8GB) → VM.Standard.E4.Flex (1 OCPU, 8GB)\n- Standard_F4s (4 vCPU, 8GB) → VM.Optimized3 (2 OCPUs, 8GB)\n\n**Diferenças:**\n- OCI: OCPUs (físicas) vs Azure: vCPUs (hyperthreading)\n- 1 OCPU OCI ≈ 2 vCPUs Azure\n\n**Pricing:** [MUTABLE] OCI geralmente 30-50% mais econômico", system))
    
    examples.append(create_example("migration-azure-compute", cat, "beginner",
        "Quais ferramentas para migrar Azure VMs?",
        "Ferramentas de migração Azure → OCI:\n\n**1. Oracle Cloud Mover:**\n- Migração online\n- Replicação contínua\n- Windows e Linux\n\n**2. Custom Images:**\n- Exporte VHD do Azure\n- Upload para Object Storage\n- Importe como Custom Image\n\n**3. Third-party:**\n- Zerto\n- Veeam\n- Carbonite\n\n**4. Manual:**\n```bash\n# Download VHD\naz storage blob download ...\n\n# Upload OCI\noci os object put ...\n\n# Import\noci compute image import ...\n```\n\n**Recomendação:**\n- Produção: Cloud Mover\n- Dev/Test: Custom Images", system))
    
    examples.append(create_example("migration-azure-compute", cat, "beginner",
        "Como exportar VHD do Azure?",
        "Exportando VHD do Azure:\n\n**1. Prepare VM:**\n```bash\n# Linux\nsudo waagent -deprovision+user\n\n# Windows\nsysprep /generalize /shutdown\n```\n\n**2. Generalize:**\n```bash\naz vm generalize --resource-group <rg> --name <vm-name>\n```\n\n**3. Capture image:**\n```bash\naz image create \\\n  --resource-group <rg> \\\n  --name my-image \\\n  --source <vm-name>\n```\n\n**4. Copy VHD:**\n```bash\naz storage blob copy start \\\n  --destination-bucket <oci-bucket> \\\n  --source-uri <vhd-uri>\n```\n\n**5. Ou download local:**\n```bash\naz storage blob download \\\n  --container-name <container> \\\n  --name <vhd-name> \\\n  --file /path/to/image.vhd\n```\n\n**Formato:** VHD (fixed) ou VMDK", system))
    
    examples.append(create_example("migration-azure-compute", cat, "intermediate",
        "Como importar imagem no OCI?",
        "Importando imagem no OCI:\n\n**1. Upload VHD para Object Storage:**\n```bash\noci os object put \\\n  --namespace <namespace> \\\n  --bucket-name <bucket> \\\n  --file image.vhd \\\n  --name images/my-image.vhd\n```\n\n**2. Importe como Custom Image:**\n```bash\noci compute image import \\\n  --compartment-id <ocid> \\\n  --display-name \"Azure-Imported\" \\\n  --source-type OBJECT_STORAGE \\\n  --source-uri 'https://objectstorage.us-ashburn-1.oraclecloud.com/n/<ns>/b/<bucket>/o/images/my-image.vhd' \\\n  --launch-mode PARAVIRTUALIZED\n```\n\n**3. Launch modes:**\n- PARAVIRTUALIZED: compatibilidade máxima\n- NATIVE: performance máxima\n\n**4. Valide:**\n```bash\noci compute image get --image-id <ocid>\n# Aguarde state = AVAILABLE\n```\n\n**5. Crie instância:**\n```bash\noci compute instance create --image-id <ocid> ...\n```", system))
    
    examples.append(create_example("migration-azure-compute", cat, "intermediate",
        "Como migrar Availability Sets?",
        "Migrando Availability Sets:\n\n**Azure → OCI:**\n- Availability Set → Instance Pool\n- Update/Fault Domains → ADs\n\n**1. Crie Instance Configuration:**\n```bash\noci compute instance-configuration create \\\n  --compartment-id <ocid> \\\n  --display-name web-config \\\n  --instance-details '{\"shape\": \"VM.Standard.E4.Flex\"}'\n```\n\n**2. Crie Instance Pool:**\n```bash\noci compute instance-pool create \\\n  --compartment-id <ocid> \\\n  --instance-configuration-id <config-ocid> \\\n  --size 3 \\\n  --placement-configurations '[{\"availabilityDomain\":\"<AD>\",\"primarySubnetId\":\"<subnet-ocid>\"}]'\n```\n\n**3. Multi-AD:**\n- OCI: 3 ADs por região\n- Distribua instâncias\n- Similar a Azure Fault Domains\n\n**Load Balancer:**\n- Backend set → Instance Pool\n- Health checks", system))
    
    examples.append(create_example("migration-azure-compute", cat, "intermediate",
        "Como migrar VM Scale Sets?",
        "Migrando VM Scale Sets:\n\n**Azure VMSS → OCI Instance Pool + Auto-scaling:**\n\n**1. Exporte configuração:**\n```bash\naz vmss show \\\n  --resource-group <rg> \\\n  --name <vmss-name>\n```\n\n**2. Crie Instance Configuration:**\n```bash\noci compute instance-configuration create \\\n  --compartment-id <ocid> \\\n  --display-name vmss-migrated \\\n  --instance-details '{\"shape\": \"VM.Standard.E4.Flex\"}'\n```\n\n**3. Crie Instance Pool:**\n```bash\noci compute instance-pool create \\\n  --compartment-id <ocid> \\\n  --instance-configuration-id <config-ocid> \\\n  --size 2\n```\n\n**4. Configure Auto-scaling:**\n```bash\noci compute instance-pool create-instance-pool-auto-scaling-policy \\\n  --instance-pool-id <ocid> \\\n  --display-name scale-up \\\n  --policy-type metric \\\n  --metric-definition '{\"metricType\":\"CPU_UTILIZATION\",\"threshold\":70}'\n```\n\n**5. Load Balancer:**\n- Attach backend set", system))
    
    examples.append(create_example("migration-azure-compute", cat, "intermediate",
        "Como lidar com Azure Managed Disks?",
        "Azure Managed Disks → OCI:\n\n**Tipos:**\n- Premium SSD → Block Volume Higher Performance\n- Standard SSD → Block Volume Balanced\n- Standard HDD → Block Volume (lower cost)\n\n**Migração:**\n\n**1. Exporte VHD:**\n```bash\n# Grant access\naz disk grant-access \\\n  --resource-group <rg> \\\n  --name <disk-name> \\\n  --access-level Read \\\n  --duration-in-seconds 3600\n\n# Get SAS URL\naz disk show --query sasUri\n\n# Download\naz storage blob copy start --source-uri <sas-url>\n```\n\n**2. Upload OCI:**\n```bash\noci os object put --file disk.vhd ...\n```\n\n**3. Importe como Custom Image:**\n```bash\noci compute image import ...\n```\n\n**4. Ou crie Block Volume:**\n```bash\noci bv volume create --size <size>\noci bv volume-attach ...\n```\n\n**Performance:** Mapeie conforme tipo de disco", system))
    
    examples.append(create_example("migration-azure-compute", cat, "intermediate",
        "Como migrar Azure Networking para VCN?",
        "Azure Networking → OCI VCN:\n\n**Mapeamento:**\n- VNet → VCN\n- Subnet → Subnet\n- NSG → Security List\n- UDR → Route Table\n- VNet Peering → VCN Peering\n- ExpressRoute → FastConnect\n\n**1. Crie VCN:**\n```bash\noci network vcn create \\\n  --compartment-id <ocid> \\\n  --cidr-block \"10.0.0.0/16\"\n```\n\n**2. Subnets:**\n```bash\noci network subnet create \\\n  --vcn-id <vcn-ocid> \\\n  --cidr-block \"10.0.1.0/24\"\n```\n\n**3. Security Lists:**\n```bash\noci network security-list create \\\n  --vcn-id <vcn-ocid> \\\n  --ingress-security-rules '[{\"cidrBlock\":\"0.0.0.0/0\",\"tcpOptions\":{\"destinationPortRange\":{\"min\":80,\"max\":80}}}]'\n```\n\n**4. Gateways:**\n- Internet Gateway\n- NAT Gateway\n- Service Gateway\n- DRG (para on-premises)", system))
    
    examples.append(create_example("migration-azure-compute", cat, "advanced",
        "Como migrar com Azure Site Recovery?",
        "Azure Site Recovery → OCI:\n\n**Cenário:** Replicação contínua\n\n**1. Exporte do ASR:**\n```bash\naz recovery-services replication protected-item list \\\n  --vault-name <vault> \\\n  --resource-group <rg>\n```\n\n**2. Configure OCI target:**\n- VCN pronta\n- IAM policies\n- Object Storage para staging\n\n**3. Use Cloud Mover:**\n```bash\n# Instale agente (Azure VM)\n# Configure replication\n# Inicie sync\n```\n\n**4. Ou manual:**\n- Snapshot disks\n- Copy para OCI\n- Import images\n- Recrie VMs\n\n**5. Cutover:**\n- Test failover primeiro\n- Agende janela\n- DNS update\n- Valide\n\n**Downtime:** Depende do método (minutos a horas)", system))
    
    examples.append(create_example("migration-azure-compute", cat, "advanced",
        "Como migrar Azure AD para OCI IAM?",
        "Azure AD → OCI IAM:\n\n**Federação:**\n\n**1. No Azure AD:**\n- Enterprise Application\n- SAML SSO\n- Download metadata\n\n**2. No OCI:**\n```bash\noci iam identity-provider create \\\n  --compartment-id <tenancy-ocid> \\\n  --name AzureAD \\\n  --protocol-type SAML2 \\\n  --metadata-url <azure-metadata-url>\n```\n\n**3. Mapeie grupos:**\n```\nAzure AD \"OCI-Admins\" → OCI Group \"Admins\"\n```\n\n**4. Policies:**\n```\nAllow group Admins to manage all-resources in tenancy\n```\n\n**5. Test SSO:**\n- Users logam via Azure AD\n- Tokens SAML válidos\n\n**Benefícios:**\n- SSO centralizado\n- MFA no Azure AD\n- Offboarding automático", system))
    
    return examples

# ============ MIGRATION AZURE STORAGE ============
def generate_migration_azure_storage():
    examples = []
    system = "You are an OCI migration specialist with expertise in Azure to OCI migrations. Provide technical guidance on Azure Storage to OCI Storage migration."
    cat = "migration/azure-storage"
    
    examples.append(create_example("migration-azure-storage", cat, "beginner",
        "Como mapear Azure Storage para OCI?",
        "Mapeamento Azure Storage → OCI:\n\n**Blob Storage → Object Storage:**\n- Blob Container → Bucket\n- Block Blob → Standard Object\n- Page Blob → (use Block Volume)\n- Append Blob → Object Storage\n\n**Blob tiers:**\n- Hot → Standard\n- Cool → Infrequent Access\n- Archive → Archive\n\n**Azure Files → File Storage:**\n- File Share → File System\n- SMB/NFS → NFS\n\n**Azure Disks → Block Volumes:**\n- Managed Disk → Block Volume\n- Unmanaged Disk → Object Storage + Image\n\n**Diferenças:**\n- OCI: namespaces globais\n- APIs diferentes (S3-compatible no OCI)\n\n[MUTABLE] Preços variam por tier.", system))
    
    examples.append(create_example("migration-azure-storage", cat, "beginner",
        "Quais ferramentas para migrar Blob Storage?",
        "Ferramentas Blob Storage → Object Storage:\n\n**1. OCI Data Transfer:**\n- Online (network)\n- Offline (appliance)\n- Grande volume\n\n**2. AzCopy + OCI CLI:**\n```bash\n# Download do Azure\nazcopy copy 'https://<account>.blob.core.windows.net/<container>?<sas>' /tmp/data\n\n# Upload para OCI\noci os object bulk-upload --namespace <ns> --bucket <bucket> --src-dir /tmp/data\n```\n\n**3. Rclone:**\n```bash\n# Configure Azure e OCI remotes\nrclone copy azure:container oci:bucket\n```\n\n**4. Third-party:**\n- CloudBerry\n- Cyberduck\n- Storage Gateway\n\n**Recomendação:**\n- <1TB: Rclone/AzCopy\n- >1TB: Data Transfer Service", system))
    
    examples.append(create_example("migration-azure-storage", cat, "beginner",
        "Como copiar dados do Azure Blob?",
        "Copiando do Azure Blob:\n\n**AzCopy:**\n```bash\n# Instale azcopy\n# https://docs.microsoft.com/azure/storage/common/storage-use-azcopy\n\n# Copy blob único\nazcopy copy \\\n  'https://<account>.blob.core.windows.net/<container>/file.txt?<sas>' \\\n  '/tmp/file.txt'\n\n# Copy container inteiro\nazcopy copy \\\n  'https://<account>.blob.core.windows.net/<container>?<sas>' \\\n  '/tmp/data' \\\n  --recursive\n```\n\n**Azure CLI:**\n```bash\naz storage blob download-batch \\\n  --source <container> \\\n  --destination /tmp/data \\\n  --account-name <account>\n```\n\n**SDK Python:**\n```python\nfrom azure.storage.blob import BlobServiceClient\n\nblob_service = BlobServiceClient(account_url, credential=sas)\ncontainer = blob_service.get_container_client('container')\n\nfor blob in container.list_blobs():\n    data = container.download_blob(blob.name).readall()\n    # Save ou upload para OCI\n```\n\n**Próximo:** Upload para OCI Object Storage", system))
    
    examples.append(create_example("migration-azure-storage", cat, "intermediate",
        "Como migrar Azure Files para File Storage?",
        "Azure Files → OCI File Storage:\n\n**1. Mount Azure Files:**\n```bash\n# Linux\nmount -t cifs //<account>.file.core.windows.net/<share> /mnt/azure \\\n  -o username=<account>,password=<key>\n```\n\n**2. Mount OCI File Storage:**\n```bash\n# OCI\nmount -t nfs <export-ip>:/<export-path> /mnt/oci\n```\n\n**3. Copy dados:**\n```bash\nrsync -av /mnt/azure/ /mnt/oci/\n```\n\n**4. Ou use azcopy + OCI CLI:**\n```bash\n# Download Azure\nazcopy copy 'https://<account>.file.core.windows.net/<share>?<sas>' /tmp/data --recursive\n\n# Upload OCI\noci file-storage file-system create ...\nmount e export\noci os object bulk-upload ...\n```\n\n**Diferenças:**\n- Azure: SMB + NFS\n- OCI: NFS apenas\n\n**Post-migration:**\n- Update mount points\n- Teste acesso", system))
    
    examples.append(create_example("migration-azure-storage", cat, "intermediate",
        "Como migrar Managed Disks?",
        "Migrando Managed Disks:\n\n**1. Exporte VHD:**\n```bash\n# Grant access\naz disk grant-access \\\n  --resource-group <rg> \\\n  --name <disk-name> \\\n  --access-level Read \\\n  --duration-in-seconds 3600\n\n# Get SAS URI\nsas_uri=$(az disk show --query sasUri -o tsv)\n```\n\n**2. Download:**\n```bash\naz storage blob copy start \\\n  --destination-bucket <oci-bucket> \\\n  --source-uri $sas_uri\n```\n\n**3. Upload OCI:**\n```bash\noci os object put \\\n  --namespace <ns> \\\n  --bucket <bucket> \\\n  --file disk.vhd\n```\n\n**4. Importe como Image:**\n```bash\noci compute image import \\\n  --source-type OBJECT_STORAGE \\\n  --source-uri 'https://...'\n```\n\n**5. Ou crie Block Volume:**\n```bash\noci bv volume create --size <size>\noci bv volume-attach --instance-id <id> --volume-id <vol-id>\n```\n\n**Performance:** Escolha tier adequado", system))
    
    examples.append(create_example("migration-azure-storage", cat, "intermediate",
        "Como configurar lifecycle policies?",
        "Lifecycle policies OCI:\n\n**Azure → OCI:**\n\n**Azure:**\n```json\n{\n  \"rules\": [{\n    \"name\": \"cool-tier\",\n    \"type\": \"Lifecycle\",\n    \"definition\": {\n      \"filters\": {\"blobTypes\": [\"blockBlob\"]},\n      \"actions\": {\"tierToCool\": {\"daysAfterModificationGreaterThan\": 30}}\n    }\n  }]\n}\n```\n\n**OCI:**\n```bash\noci os bucket put-lifecycle-policy \\\n  --namespace <ns> \\\n  --bucket-name <bucket> \\\n  --lifecycle-policy '{\n    \"rules\": [{\n      \"name\": \"cool-tier\",\n      \"action\": \"CHANGE_STORAGE_TIER\",\n      \"timeAmount\": 30,\n      \"timeUnit\": \"DAYS\",\n      \"storageTier\": \"INFREQUENT_ACCESS\"\n    }]\n  }'\n```\n\n**Tiers OCI:**\n- STANDARD\n- INFREQUENT_ACCESS\n- ARCHIVE\n\n**Actions:**\n- CHANGE_STORAGE_TIER\n- ARCHIVE_STORAGE_TIER\n- DELETE", system))
    
    examples.append(create_example("migration-azure-storage", cat, "intermediate",
        "Como validar integridade?",
        "Validando integridade:\n\n**1. Object counts:**\n```bash\n# Azure\naz storage blob list --container-name <container> | jq length\n\n# OCI\noci os object list --namespace <ns> --bucket <bucket> | jq '.data | length'\n```\n\n**2. Checksums:**\n```bash\n# Azure - MD5 de cada blob\naz storage blob list --container-name <container> \\\n  --query '[].{name:name, md5:properties.contentMd5}'\n\n# OCI - MD5 de cada object\noci os object list --namespace <ns> --bucket <bucket> \\\n  --query 'data[].{name:name, md5:md5}'\n```\n\n**3. Sample validation:**\n```bash\n# Download ambos\naz storage blob download ...\noci os object get ...\n\n# Compare\nmd5sum azure_file.txt oci_file.txt\n```\n\n**4. Automated script:**\n- Compare counts\n- Validate checksums\n- Report discrepancies", system))
    
    examples.append(create_example("migration-azure-storage", cat, "intermediate",
        "Como migrar com mínimo downtime?",
        "Migração com mínimo downtime:\n\n**1. Replicação inicial:**\n- Copy bulk de dados\n- Pode levar horas/dias\n\n**2. Sync contínuo:**\n```bash\n# rsync incremental\nrsync -av --delete /mnt/azure/ /mnt/oci/\n\n# Ou agende\n*/5 * * * * rsync -av /mnt/azure/ /mnt/oci/\n```\n\n**3. Cutover:**\n```bash\n# 1. Stop aplicações (write)\n# 2. Sync final\nrsync -av --delete /mnt/azure/ /mnt/oci/\n\n# 3. Valide\n# 4. Update configs\n# 5. Start aplicações (OCI)\n```\n\n**4. Rollback:**\n- Mantenha Azure\n- DNS reversível\n- Teste rollback\n\n**Downtime:** Tipicamente 15-60 minutos", system))
    
    examples.append(create_example("migration-azure-storage", cat, "advanced",
        "Como migrar petabytes do Azure?",
        "Migração de petabytes:\n\n**1. Data Transfer Appliance:**\n```bash\noci data-transfer job create \\\n  --transfer-type IMPORT \\\n  --is-offline true \\\n  --transfer-appliance-shape \"100TB\"\n```\n\n**2. Processo:**\n- Oracle envia appliance\n- Copie dados do Azure\n```bash\nazcopy copy 'https://...' /mnt/appliance/ --recursive\n```\n- Return shipping\n- Oracle importa para OCI\n\n**3. Parallel transfers:**\n```bash\n# Múltiplas threads\nrclone copy azure: oci: --transfers=64 --checkers=128\n\n# Múltiplas instâncias\n# Cada uma copia subset\n```\n\n**4. Incremental:**\n- Initial: offline\n- Delta: online\n- Cutover: sync final\n\n**Timeline:**\n- 100TB offline: 1-2 semanas\n- Delta: horas", system))
    
    examples.append(create_example("migration-azure-storage", cat, "advanced",
        "Como integrar Azure + OCI storage?",
        "Storage híbrido Azure + OCI:\n\n**Cenário:** Dados em ambos clouds\n\n**1. Replicação:**\n```python\nfrom azure.storage.blob import BlobServiceClient\nimport oci\n\nazure = BlobServiceClient(account_url, credential=credential)\nos_client = oci.object_storage.ObjectStorageClient()\n\ndef replicate(blob_name):\n    # Download Azure\n    azure_blob = azure.get_blob_client(blob_name)\n    data = azure_blob.download_blob().readall()\n    \n    # Upload OCI\n    os_client.put_object(\n        namespace=ns,\n        bucket_name=bucket,\n        object_name=blob_name,\n        object_content=data\n    )\n```\n\n**2. Failover:**\n- Primary: Azure\n- DR: OCI\n- DNS failover\n\n**3. Active-active:**\n- Read: latency-based\n- Write: async replicate\n\n**Use cases:**\n- DR\n- Compliance\n- Latency", system))
    
    return examples

# ============ MIGRATION AZURE DATABASE ============
def generate_migration_azure_database():
    examples = []
    system = "You are an OCI migration specialist with expertise in Azure to OCI database migrations. Provide technical guidance on Azure SQL, MySQL, PostgreSQL to OCI."
    cat = "migration/azure-database"
    
    examples.append(create_example("migration-azure-database", cat, "beginner",
        "Como mapear Azure SQL para OCI?",
        "Mapeamento Azure SQL → OCI:\n\n**Azure SQL Database → OCI:**\n- Azure SQL → Oracle Database (com migração)\n- Azure SQL → SQL Server em Compute\n- Azure SQL → MySQL (se compatível)\n\n**Azure Database for MySQL → OCI:**\n- MySQL HeatWave\n- MySQL em Compute\n\n**Azure Database for PostgreSQL → OCI:**\n- PostgreSQL em Compute\n- Autonomous JSON (se JSON-heavy)\n\n**Cosmos DB → OCI:**\n- NoSQL Database\n- Autonomous JSON\n\n**Diferenças:**\n- OCI: foco em Oracle DB\n- Azure: PaaS mais maduro\n\n**Migração SQL Server:**\n- Backup/restore\n- Log shipping\n- Always On", system))
    
    examples.append(create_example("migration-azure-database", cat, "beginner",
        "Como migrar Azure SQL Database?",
        "Migrando Azure SQL Database:\n\n**Opção 1: BACPAC export:**\n```bash\n# Export do Azure\naz sql db export \\\n  --storage-key-type StorageAccessKey \\\n  --storage-key <key> \\\n  --storage-uri 'https://<account>.blob.core.windows.net/<container>/db.bacpac' \\\n  --admin-user <user> \\\n  --admin-password <password> \\\n  --name <db-name>\n\n# Download\naz storage blob download ...\n\n# Import no OCI (SQL Server)\nsqlpackage /i:db.bacpac /tsn:<server> /td:db\n```\n\n**Opção 2: Transactional Replication:**\n- Configure publisher (Azure)\n- Configure subscriber (OCI)\n- Sync contínuo\n\n**Opção 3: Log Shipping:**\n- Backup logs\n- Copy para OCI\n- Restore\n\n**Downtime:** BACPAC: horas, Replication: minutos", system))
    
    examples.append(create_example("migration-azure-database", cat, "beginner",
        "Como migrar Azure MySQL?",
        "Migrando Azure MySQL:\n\n**1. mysqldump:**\n```bash\n# Export\nmysqldump -h <azure-host> -u admin -p \\\n  --single-transaction \\\n  --all-databases > dump.sql\n\n# Import\nmysql -h <oci-host> -u admin -p < dump.sql\n```\n\n**2. MySQL Shell:**\n```bash\n# Dump\nmysqldump --mysqlx -h <azure-host> -u admin -p \\\n  --all-databases > dump.sql\n\n# Load\nmysqlsh <oci-host> < dump.sql\n```\n\n**3. Replication:**\n```sql\n-- Azure (source)\nCREATE USER 'repl'@'%' IDENTIFIED BY 'password';\nGRANT REPLICATION SLAVE ON *.* TO 'repl'@'%';\n\n-- OCI (target)\nCHANGE MASTER TO MASTER_HOST='<azure-host>', ...;\nSTART SLAVE;\n```\n\n**HeatWave:** Migre para MySQL HeatWave para analytics", system))
    
    examples.append(create_example("migration-azure-database", cat, "intermediate",
        "Como usar Azure DMS para OCI?",
        "Azure DMS → OCI:\n\n**Cenário:** Usando Azure Database Migration Service\n\n**1. Configure DMS:**\n- Crie DMS resource\n- Setup source (Azure SQL)\n- Setup target (OCI)\n\n**2. Online migration:**\n```bash\n# DMS configuration\n{\n  \"source\": {\n    \"type\": \"AzureSql\",\n    \"connectionString\": \"Server=...\"\n  },\n  \"target\": {\n    \"type\": \"SqlServer\",\n    \"connectionString\": \"Server=<oci-ip>...\"\n  }\n}\n```\n\n**3. Migration workflow:**\n- Full load inicial\n- CDC (change data capture)\n- Sync contínuo\n\n**4. Cutover:**\n- Stop writes (Azure)\n- Apply pending\n- Start OCI\n\n**Limitação:** DMS é Azure-focused\n- Pode precisar de custom solutions para OCI", system))
    
    examples.append(create_example("migration-azure-database", cat, "intermediate",
        "Como migrar PostgreSQL?",
        "Migrando PostgreSQL:\n\n**1. pg_dump:**\n```bash\n# Export\npg_dump -h <azure-host> -U admin -d mydb > dump.sql\n\n# Import\npsql -h <oci-host> -U admin -d mydb < dump.sql\n```\n\n**2. Logical Replication:**\n```sql\n-- Azure (publisher)\nCREATE PUBLICATION mypub FOR ALL TABLES;\n\n-- OCI (subscriber)\nCREATE SUBSCRIPTION mysub \\\n  CONNECTION 'host=<azure-host> dbname=mydb user=repl' \\\n  PUBLICATION mypub;\n```\n\n**3. pglogical:**\n```sql\n-- Instale extensão\nCREATE EXTENSION pglogical;\n\n-- Configure replication\nSELECT pglogical.create_subscription(...);\n```\n\n**4. DMS alternativo:**\n- pgloader\n- SymmetricDS\n- Custom scripts\n\n**Downtime:**\n- pg_dump: horas\n- Replication: minutos", system))
    
    examples.append(create_example("migration-azure-database", cat, "intermediate",
        "Como migrar Cosmos DB?",
        "Migrando Cosmos DB:\n\n**Cosmos DB (SQL API) → OCI:**\n\n**1. Export data:**\n```python\nfrom azure.cosmos import CosmosClient\nimport json\n\nclient = CosmosClient(url, credential)\ncontainer = client.get_database_client('db').get_container_client('container')\n\nitems = list(container.read_all_items())\n\nwith open('data.json', 'w') as f:\n    json.dump(items, f)\n```\n\n**2. Import no OCI:**\n```python\nimport oci\nimport json\n\nnosql = oci.nosql.NosqlClient()\n\nwith open('data.json') as f:\n    data = json.load(f)\n    for item in data:\n        nosql.put_row(\n            table_name='my_table',\n            row=item\n        )\n```\n\n**3. Ou Autonomous JSON:**\n```python\n# SODA API\nfrom soda import *\n\ncollection = db.createCollection('cosmos_data')\nfor item in data:\n    collection.insertOne(item)\n```\n\n**Schema:** Pode precisar transformação", system))
    
    examples.append(create_example("migration-azure-database", cat, "intermediate",
        "Como validar migração de database?",
        "Validação de migração:\n\n**1. Schema comparison:**\n```bash\n# Export schemas\npg_dump -s -h <azure> > azure-schema.sql\npg_dump -s -h <oci> > oci-schema.sql\n\n# Compare\ndiff azure-schema.sql oci-schema.sql\n```\n\n**2. Row counts:**\n```sql\n-- Azure\nSELECT schemaname, tablename, n_live_tup \nFROM pg_stat_user_tables;\n\n-- OCI\n-- Mesma query, compare\n```\n\n**3. Data validation:**\n```sql\n-- Sample checksum\nSELECT md5(string_agg(id::text, ',')) \nFROM my_table;\n```\n\n**4. Performance:**\n- Run queries idênticas\n- Compare explain plans\n- pg_stat_statements\n\n**5. Application tests:**\n- Smoke tests\n- Integration tests\n- Load tests\n\n**Tools:**\n- pg_comparator\n- Custom scripts", system))
    
    examples.append(create_example("migration-azure-database", cat, "intermediate",
        "Como migrar com Always On?",
        "SQL Server Always On:\n\n**Cenário:** Azure SQL Managed Instance → OCI SQL Server\n\n**1. Configure Always On:**\n```sql\n-- Azure (primary)\nCREATE AVAILABILITY GROUP [AG1]\nWITH (AUTOMATED_BACKUP_PREFERENCE = SECONDARY)\nFOR DATABASE [MyDB]\nREPLICA ON \n  N'<azure-instance>' WITH (...),\n  N'<oci-instance>' WITH (...);\n```\n\n**2. Configure listener:**\n```sql\n-- DNS listener\nALTER AVAILABILITY GROUP [AG1]\nADD LISTENER 'ag-listener' (...);\n```\n\n**3. Replication:**\n- Synchronous (baixa latência)\n- Asynchronous (alta latência)\n\n**4. Failover:**\n```sql\nALTER AVAILABILITY GROUP [AG1] FAILOVER;\n```\n\n**5. Apps:**\n- Conectam ao listener\n- Transparent failover\n\n**Downtime:** Segundos (automático)", system))
    
    examples.append(create_example("migration-azure-database", cat, "advanced",
        "Como migrar database grande (>1TB)?",
        "Migração de database grande:\n\n**Estratégia:**\n- Full backup + CDC\n- Ou replication contínua\n\n**1. Full backup:**\n```sql\n-- Azure SQL\nBACKUP DATABASE [MyDB] \nTO URL = 'https://<storage>.blob.core.windows.net/backup/mydb.bak'\n```\n\n**2. Copy para OCI:**\n```bash\naz storage blob copy start ...\n```\n\n**3. Restore OCI:**\n```sql\n-- OCI SQL Server\nRESTORE DATABASE [MyDB] \nFROM DISK = '/backup/mydb.bak'\nWITH NORECOVERY;\n```\n\n**4. CDC (replication):**\n```sql\n-- Configure replication\n-- Transaction log shipping\n-- Ou Always On\n```\n\n**5. Sync:**\n- Apply logs\n- Lag → 0\n\n**6. Cutover:**\n- Janela agendada\n- Downtime mínimo\n\n**Timeline:**\n- Full: dias\n- CDC: contínuo\n- Cutover: horas", system))
    
    examples.append(create_example("migration-azure-database", cat, "advanced",
        "Como migrar para Autonomous Database?",
        "Migrando para Autonomous Database:\n\n**Azure SQL → Autonomous:**\n\n**1. Schema migration:**\n- T-SQL → PL/SQL (pode precisar refatoração)\n- Ou use Oracle SQL Developer\n\n**2. Data migration:**\n```bash\n# Export Azure SQL\naz sql db export --storage-uri ... --file db.bacpac\n\n# Convert (se necessário)\n# Oracle SQL Developer Migration Wizard\n\n# Import Autonomous\nimpdp admin/password@adb \\\n  dumpfile=db.dmp \\\n  directory=DATA_PUMP_DIR\n```\n\n**3. Ou Data Pump:**\n```sql\n-- Autonomous\nBEGIN\n  DBMS_CLOUD.COPY_DATA(\n    table_name => 'MY_TABLE',\n    credential_name => 'AZURE_CRED',\n    source_uri => 'https://<azure>.blob.core.windows.net/data.csv'\n  );\nEND;\n```\n\n**4. Valide:**\n- Objects\n- Data\n- Performance\n\n**Benefícios:**\n- Autonomous (auto-tuning)\n- Menos administração\n- Scaling fácil", system))
    
    return examples

# ============ MIGRATION GCP COMPUTE ============
def generate_migration_gcp_compute():
    examples = []
    system = "You are an OCI migration specialist with expertise in GCP to OCI migrations. Provide technical guidance on GCP Compute Engine to OCI Compute migration."
    cat = "migration/gcp-compute"
    
    examples.append(create_example("migration-gcp-compute", cat, "beginner",
        "Como mapear GCP Compute para OCI?",
        "Mapeamento GCP Compute → OCI:\n\n**Machine types:**\n- GCP e2-micro → VM.Standard.E4.Flex (burstable)\n- GCP e2-medium → VM.Standard.E4.Flex (general purpose)\n- GCP c2-standard → VM.Optimized3 (compute optimized)\n- GCP m2-ultramem → VM.Optimized3 (memory optimized)\n\n**Examples:**\n- e2-medium (2 vCPU, 4GB) → VM.Standard.E4.Flex (1 OCPU, 4GB)\n- n2-standard-2 (2 vCPU, 8GB) → VM.Standard.E4.Flex (1 OCPU, 8GB)\n- c2-standard-4 (4 vCPU, 16GB) → VM.Optimized3 (2 OCPUs, 16GB)\n\n**Diferenças:**\n- OCI: OCPUs (físicas) vs GCP: vCPUs\n- 1 OCPU OCI ≈ 2 vCPUs GCP\n\n**Pricing:** [MUTABLE] OCI geralmente 30-50% mais econômico", system))
    
    examples.append(create_example("migration-gcp-compute", cat, "beginner",
        "Quais ferramentas para migrar GCP VMs?",
        "Ferramentas de migração GCP → OCI:\n\n**1. Oracle Cloud Mover:**\n- Migração online\n- Replicação contínua\n- Windows e Linux\n\n**2. Custom Images:**\n- Exporte image do GCP\n- Upload para Object Storage\n- Importe como Custom Image\n\n**3. Third-party:**\n- Zerto\n- Veeam\n- CloudEndure\n\n**4. Manual:**\n```bash\n# Export GCP image\ngcloud compute images export ...\n\n# Upload OCI\noci os object put ...\n\n# Import\noci compute image import ...\n```\n\n**Recomendação:**\n- Produção: Cloud Mover\n- Dev/Test: Custom Images", system))
    
    examples.append(create_example("migration-gcp-compute", cat, "beginner",
        "Como exportar imagem do GCP?",
        "Exportando imagem do GCP:\n\n**1. Crie image da instância:**\n```bash\ngcloud compute images create my-image \\\n  --source-disk <disk-name> \\\n  --family <family>\n```\n\n**2. Exporte para Cloud Storage:**\n```bash\ngcloud compute images export my-image \\\n  --destination-uri gs://<bucket>/images/my-image.tar.gz \\\n  --export-format tar.gz\n```\n\n**3. Download local:**\n```bash\ngsutil cp gs://<bucket>/images/my-image.tar.gz .\ntar -xzf my-image.tar.gz\n```\n\n**4. Ou direto para OCI:**\n```bash\n# Download e upload\ngsutil cp gs://<bucket>/images/my-image.tar.gz .\ntar -xzf my-image.tar.gz\noci os object put --file disk.raw ...\n```\n\n**Formato:** RAW ou VMDK\n\n**Próximo:** Import no OCI", system))
    
    examples.append(create_example("migration-gcp-compute", cat, "intermediate",
        "Como importar imagem no OCI?",
        "Importando imagem no OCI:\n\n**1. Upload para Object Storage:**\n```bash\noci os object put \\\n  --namespace <namespace> \\\n  --bucket-name <bucket> \\\n  --file disk.raw \\\n  --name images/gcp-image.raw\n```\n\n**2. Importe como Custom Image:**\n```bash\noci compute image import \\\n  --compartment-id <ocid> \\\n  --display-name \"GCP-Imported\" \\\n  --source-type OBJECT_STORAGE \\\n  --source-uri 'https://objectstorage.../images/gcp-image.raw' \\\n  --launch-mode PARAVIRTUALIZED\n```\n\n**3. Launch modes:**\n- PARAVIRTUALIZED: compatibilidade\n- NATIVE: performance\n\n**4. Aguarde:**\n```bash\noci compute image get --image-id <ocid>\n# state = AVAILABLE\n```\n\n**5. Crie instância:**\n```bash\noci compute instance create --image-id <ocid> ...\n```\n\n**Drivers:** Instale Oracle Cloud Agent", system))
    
    examples.append(create_example("migration-gcp-compute", cat, "intermediate",
        "Como migrar Instance Groups?",
        "Migrando Instance Groups:\n\n**GCP MIG → OCI Instance Pool:**\n\n**1. Exporte configuração:**\n```bash\ngcloud compute instance-groups managed describe <group-name>\n```\n\n**2. Crie Instance Configuration:**\n```bash\noci compute instance-configuration create \\\n  --compartment-id <ocid> \\\n  --display-name mig-config \\\n  --instance-details '{\"shape\": \"VM.Standard.E4.Flex\"}'\n```\n\n**3. Crie Instance Pool:**\n```bash\noci compute instance-pool create \\\n  --compartment-id <ocid> \\\n  --instance-configuration-id <config-ocid> \\\n  --size 3\n```\n\n**4. Auto-scaling:**\n```bash\noci compute instance-pool create-instance-pool-auto-scaling-policy \\\n  --instance-pool-id <ocid> \\\n  --display-name scale-up \\\n  --metric-definition '{\"metricType\":\"CPU_UTILIZATION\",\"threshold\":70}'\n```\n\n**5. Load Balancer:**\n- Backend set → Instance Pool", system))
    
    examples.append(create_example("migration-gcp-compute", cat, "intermediate",
        "Como migrar GCP Networking?",
        "GCP Networking → OCI VCN:\n\n**Mapeamento:**\n- VPC → VCN\n- Subnet → Subnet\n- Firewall Rules → Security Lists\n- Routes → Route Tables\n- VPC Peering → VCN Peering\n- Cloud Interconnect → FastConnect\n\n**1. Crie VCN:**\n```bash\noci network vcn create \\\n  --compartment-id <ocid> \\\n  --cidr-block \"10.0.0.0/16\"\n```\n\n**2. Subnets:**\n```bash\noci network subnet create \\\n  --vcn-id <vcn-ocid> \\\n  --cidr-block \"10.0.1.0/24\"\n```\n\n**3. Security Lists:**\n```bash\noci network security-list create \\\n  --vcn-id <vcn-ocid> \\\n  --ingress-security-rules '[{\"cidrBlock\":\"0.0.0.0/0\",\"tcpOptions\":{\"destinationPortRange\":{\"min\":80,\"max\":80}}}]'\n```\n\n**4. Gateways:**\n- Internet Gateway\n- NAT Gateway\n- DRG", system))
    
    examples.append(create_example("migration-gcp-compute", cat, "intermediate",
        "Como migrar Persistent Disks?",
        "Migrando Persistent Disks:\n\n**1. Crie snapshot:**\n```bash\ngcloud compute disks snapshot <disk-name> \\\n  --snapshot-names <snapshot-name>\n```\n\n**2. Exporte para Cloud Storage:**\n```bash\ngcloud compute images create temp-image \\\n  --source-snapshot <snapshot-name>\n\ngcloud compute images export temp-image \\\n  --destination-uri gs://<bucket>/disk.tar.gz\n```\n\n**3. Download:**\n```bash\ngsutil cp gs://<bucket>/disk.tar.gz .\ntar -xzf disk.tar.gz\n```\n\n**4. Upload OCI:**\n```bash\noci os object put --file disk.raw ...\n```\n\n**5. Importe:**\n```bash\noci compute image import \\\n  --source-type OBJECT_STORAGE \\\n  --source-uri 'https://...'\n```\n\n**Tipos:**\n- pd-standard → Block Volume Balanced\n- pd-ssd → Block Volume Higher Performance", system))
    
    examples.append(create_example("migration-gcp-compute", cat, "intermediate",
        "Como validar migração?",
        "Validação de migração:\n\n**1. Connectivity:**\n```bash\n# Ping\ntest-connection <ip-oci>\n\n# SSH\nssh opc@<ip-oci>\n```\n\n**2. Performance:**\n- Compare CPU, memory, disk\n- Use Monitoring\n\n**3. Aplicações:**\n- Smoke tests\n- Functional tests\n- Load tests\n\n**4. Dados:**\n- checksum de arquivos\n- Row counts\n- Integridade\n\n**5. DNS:**\n- Update records\n- TTL baixo antes\n- Valide resolução\n\n**Checklist:**\n- [ ] Instância running\n- [ ] Network OK\n- [ ] Apps funcionando\n- [ ] Performance aceitável\n- [ ] Monitoring ativo", system))
    
    examples.append(create_example("migration-gcp-compute", cat, "advanced",
        "Como migrar com mínimo downtime?",
        "Migração com mínimo downtime:\n\n**1. Replicação contínua:**\n- Cloud Mover\n- Sync inicial + deltas\n\n**2. DNS preparation:**\n```dns\n; Reduza TTL\nTTL 300 (5 minutos)\n```\n\n**3. Cutover:**\n```bash\n# 1. Stop apps (GCP)\n# 2. Sync final\n# 3. Valide OCI\n# 4. Update DNS\n# 5. Start apps (OCI)\n# 6. Monitore\n```\n\n**4. Rollback:**\n- Mantenha GCP\n- DNS reversível\n\n**Downtime típico:** 15-60 minutos\n\n**Zero-downtime:**\n- Blue-green\n- Load Balancer em ambos\n- Traffic shifting", system))
    
    examples.append(create_example("migration-gcp-compute", cat, "advanced",
        "Como migrar GKE para OKE?",
        "Migrando GKE → OKE:\n\n**1. Exporte manifests:**\n```bash\nkubectl get all --all-namespaces -o yaml > gke-resources.yaml\n```\n\n**2. Ajuste para OKE:**\n- StorageClass names\n- LoadBalancer annotations\n- Ingress configuration\n\n**3. Crie OKE cluster:**\n```bash\noci ce cluster create \\\n  --compartment-id <ocid> \\\n  --name migrated-cluster \\\n  --kubernetes-version v1.28.5\n```\n\n**4. Apply manifests:**\n```bash\nkubectl apply -f oci-resources.yaml\n```\n\n**5. Migre dados:**\n- PVs: rsync\n- ConfigMaps/Secrets: recrie\n\n**6. Traffic:**\n- Update DNS\n- Ou use service mesh\n\n**Ferramentas:**\n- Velero (backup/restore)\n- Helm charts", system))
    
    return examples

# Main execution
def main():
    generators = {
        "migration-azure-compute": generate_migration_azure_compute,
        "migration-azure-storage": generate_migration_azure_storage,
        "migration-azure-database": generate_migration_azure_database,
        "migration-gcp-compute": generate_migration_gcp_compute,
    }
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    for category, generator in generators.items():
        examples = generator()
        write_jsonl(f"{category}.jsonl", examples)
    
    print(f"\nTotal: {len(generators)} files generated")

if __name__ == "__main__":
    main()
