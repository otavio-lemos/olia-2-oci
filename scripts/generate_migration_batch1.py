#!/usr/bin/env python3
"""
Generate JSONL files for OCI Migration categories (14 files).
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

# ============ MIGRATION AWS COMPUTE ============
def generate_migration_aws_compute():
    examples = []
    system = "You are an OCI migration specialist with expertise in AWS to OCI migrations. Provide technical guidance on compute migration, EC2 to Compute mapping, and best practices."
    cat = "migration/aws-compute"
    
    # Beginner (3)
    examples.append(create_example("migration-aws-compute", cat, "beginner",
        "Como mapear EC2 para OCI Compute?",
        "Mapeamento EC2 → OCI Compute:\n\n**Instance types:**\n- EC2 t3/t4g → VM.Standard.E4.Flex (burstable)\n- EC2 m5 → VM.Standard.E4.Flex (general purpose)\n- EC2 c5 → VM.Optimized3 (compute optimized)\n- EC2 r5 → VM.Optimized3 (memory optimized)\n\n**Shape examples:**\n- t3.medium (2 vCPU, 4GB) → VM.Standard.E4.Flex (1 OCPU, 4GB)\n- m5.large (2 vCPU, 8GB) → VM.Standard.E4.Flex (1 OCPU, 8GB)\n- c5.xlarge (4 vCPU, 8GB) → VM.Optimized3 (2 OCPUs, 8GB)\n\n**Diferenças:**\n- OCI: OCPUs (físicas) vs AWS: vCPUs (hyperthreading)\n- 1 OCPU OCI ≈ 2 vCPUs AWS\n\n**Pricing:** [MUTABLE] OCI geralmente 30-50% mais econômico\n\nDocs: https://docs.oracle.com/en-us/iaas/Content/Migration/", system))
    
    examples.append(create_example("migration-aws-compute", cat, "beginner",
        "Quais ferramentas para migrar EC2?",
        "Ferramentas de migração EC2 → OCI:\n\n**1. Oracle Cloud Mover:**\n- Migração online (replicação contínua)\n- Minimal downtime\n- Suporta Windows e Linux\n\n**2. Custom Images:**\n- Exporte EC2 como AMI\n- Converta para VMDK/OVA\n- Importe no OCI\n\n**3. Third-party:**\n- CloudEndure (AWS)\n- Zerto\n- Veeam\n\n**4. Manual:**\n- Snapshot do volume\n- Upload para Object Storage\n- Importe como Custom Image\n\n**Recomendação:**\n- Produção: Cloud Mover (menor downtime)\n- Dev/Test: Custom Images\n\n[CHECK DOCS] Verifique compatibilidade de OS.", system))
    
    examples.append(create_example("migration-aws-compute", cat, "beginner",
        "Qual o processo de migração lift-and-shift?",
        "Processo lift-and-shift:\n\n**1. Discovery:**\n- Inventário de instâncias EC2\n- Dependências\n- Performance baseline\n\n**2. Planning:**\n- Mapeie shapes equivalentes\n- Planeje network (VCN)\n- Estime custos\n\n**3. Replication:**\n- Instale agente Cloud Mover\n- Replicação inicial\n- Sync contínuo\n\n**4. Cutover:**\n- Agende janela\n- Stop EC2\n- Start OCI\n- Valide\n\n**5. Post-migration:**\n- Instale Oracle Cloud Agent\n- Configure monitoring\n- Otimize shape\n\n**Timeline:** 1-2 semanas por workload", system))
    
    # Intermediate (5)
    examples.append(create_example("migration-aws-compute", cat, "intermediate",
        "Como usar Oracle Cloud Mover?",
        "Oracle Cloud Mover:\n\n**1. Pré-requisitos:**\n- OCI tenancy\n- VCN configurada\n- IAM policies\n\n**2. Instale agente (EC2):**\n```bash\n# Download\nwget https://cloudmover.oraclecloud.com/installer.sh\n\n# Instale\nsudo bash installer.sh --tenant <ocid>\n```\n\n**3. Configure replication:**\n- Console → Migration → Discovery\n- Add source (AWS)\n- Configure credentials\n\n**4. Inicie replicação:**\n- Replicação inicial (pode levar horas)\n- Sync contínuo (delta)\n\n**5. Cutover:**\n- 'Launch Migration'\n- OCI instâncias criadas\n- DNS update\n- Stop AWS\n\n**Downtime:** Tipicamente <1 hora", system))
    
    examples.append(create_example("migration-aws-compute", cat, "intermediate",
        "Como migrar Auto Scaling Groups?",
        "Migrando Auto Scaling Groups:\n\n**1. Exporte configuração AWS:**\n```bash\naws autoscaling describe-auto-scaling-groups \\\n  --auto-scaling-group-names my-asg\n```\n\n**2. Mapeie para OCI:**\n- ASG → Instance Pool\n- Launch Configuration → Instance Configuration\n- Scaling Policies → OCI Scaling Policies\n\n**3. Crie Instance Configuration:**\n```bash\noci compute instance-configuration create \\\n  --compartment-id <ocid> \\\n  --display-name web-config \\\n  --instance-details '{\"shape\": \"VM.Standard.E4.Flex\"}'\n```\n\n**4. Crie Instance Pool:**\n```bash\noci compute instance-pool create \\\n  --compartment-id <ocid> \\\n  --instance-configuration-id <config-ocid> \\\n  --size 3\n```\n\n**5. Configure Auto-scaling:**\n- Metrics: CPU, memory\n- Policies: scale up/down\n\n**Load Balancer:** Update backend set", system))
    
    examples.append(create_example("migration-aws-compute", cat, "intermediate",
        "Como lidar com diferenças de networking?",
        "Diferenças de networking:\n\n**VPC (AWS) → VCN (OCI):**\n- Similar conceito\n- VCN é regional (como VPC)\n- Subnets também\n\n**Security Groups → Security Lists:**\n- AWS: stateful, por instância\n- OCI: stateless, por subnet\n- Mapeie rules\n\n**NACLs → Security Lists:**\n- Função similar\n- OCI combina inbound/outbound\n\n**Elastic IP → Public IP:**\n- Ephemeral: muda se stop/start\n- Reserved: mantém (como EIP)\n\n**NAT Gateway:** Similar\n\n**VPC Peering → VCN Peering:**\n- Regional ou inter-region\n\n**Direct Connect → FastConnect:**\n- Conexão dedicada\n\n**Ação:** Recrie network topology no OCI antes de migrar instâncias", system))
    
    examples.append(create_example("migration-aws-compute", cat, "intermediate",
        "Como migrar instâncias Windows?",
        "Migrando instâncias Windows:\n\n**1. Pré-requisitos:**\n- License mobility (SA)\n- Ou use BYOL no OCI\n\n**2. Cloud Mover:**\n```bash\n# Instale agente Windows\n# Download installer.exe\n# Execute como Administrator\n```\n\n**3. Drivers:**\n- Oracle Cloud Agent (Windows)\n- Paravirtual drivers\n- Network/storage drivers\n\n**4. Activation:**\n- KMS server\n- Ou MA KMS da Oracle\n\n**5. Post-migration:**\n- Update drivers\n- Configure Cloud Agent\n- Teste RDP\n\n**Licensing:**\n- BYOL: use suas licenças\n- License Included: Oracle cobra\n\n**Downtime:** Similar a Linux", system))
    
    examples.append(create_example("migration-aws-compute", cat, "intermediate",
        "Como validar migração?",
        "Validação de migração:\n\n**1. Connectivity:**\n```bash\n# Ping\ntest-connection <ip-oci>\n\n# Portas\nTest-NetConnection <ip> -Port 80\n\n# SSH/RDP\nssh opc@<ip-oci>\n```\n\n**2. Performance:**\n- Compare CPU, memory, disk\n- Baseline AWS vs OCI\n- Use Monitoring\n\n**3. Aplicações:**\n- Smoke tests\n- Teste funcional\n- Load testing\n\n**4. Dados:**\n- checksum de arquivos\n- Row counts (database)\n- Integridade\n\n**5. DNS:**\n- Update records\n- TTL baixo antes\n- Valide resolução\n\n**Checklist:**\n- [ ] Instância running\n- [ ] Network OK\n- [ ] Apps funcionando\n- [ ] Performance aceitável\n- [ ] Monitoring ativo", system))
    
    # Advanced (2)
    examples.append(create_example("migration-aws-compute", cat, "advanced",
        "Como migrar com mínimo downtime?",
        "Migração com mínimo downtime:\n\n**1. Replicação contínua:**\n- Cloud Mover\n- Sync inicial + deltas\n- RPO: minutos\n\n**2. DNS preparation:**\n```dns\n; Reduza TTL dias antes\nTTL 300 (5 minutos)\n```\n\n**3. Cutover procedure:**\n```bash\n# 1. Stop aplicações (AWS)\n# Drena conexões ativas\n\n# 2. Sync final (Cloud Mover)\n# Últimos deltas\n\n# 3. Valide OCI\n# Smoke tests\n\n# 4. Update DNS\n# Aponte para OCI\n\n# 5. Start aplicações (OCI)\n\n# 6. Monitore\n```\n\n**4. Rollback:**\n- Mantenha AWS rodando\n- DNS reversível\n- Teste rollback antes\n\n**Downtime típico:** 15-60 minutos\n\n**Zero-downtime:**\n- Blue-green deployment\n- Load Balancer em ambas\n- Traffic shifting gradual", system))
    
    examples.append(create_example("migration-aws-compute", cat, "advanced",
        "Como otimizar custos pós-migração?",
        "Otimização de custos pós-migração:\n\n**1. Right-sizing:**\n```bash\n# Analise utilização\noci monitoring metrics list \\\n  --namespace oci_computeagent \\\n  --metric-name CpuUtilization\n\n# Se média <30%, reduza shape\n```\n\n**2. Instance pools:**\n- Melhor utilization\n- Scaling automático\n\n**3. ARM migration:**\n- x86 → ARM (Ampere A1)\n- Até 80% mais econômico\n- Teste compatibilidade\n\n**4. Reserved instances:**\n- 1 ou 3 anos\n- Até 60% desconto\n\n**5. Shutdown automático:**\n- Dev/Test à noite\n- Automation com Functions\n\n**6. Storage:**\n- Archive para Object Storage\n- Backup policies\n\n**ROI típico:** 30-50% redução vs AWS", system))
    
    return examples

# ============ MIGRATION AWS STORAGE ============
def generate_migration_aws_storage():
    examples = []
    system = "You are an OCI migration specialist with expertise in AWS to OCI migrations. Provide technical guidance on storage migration, S3/EBS to Object/Block Storage."
    cat = "migration/aws-storage"
    
    # Beginner (3)
    examples.append(create_example("migration-aws-storage", cat, "beginner",
        "Como mapear S3 para Object Storage?",
        "Mapeamento S3 → Object Storage:\n\n**Conceitos:**\n- S3 Bucket → Object Storage Bucket\n- S3 Object → Object Storage Object\n- S3 Key → Object Storage Object Name\n\n**APIs:**\n- S3 API compatível\n- Use AWS SDK ou OCI SDK\n\n**Storage tiers:**\n- S3 Standard → Standard\n- S3 IA → Infrequent Access\n- S3 Glacier → Archive\n\n**Features:**\n- Versioning: similar\n- Lifecycle policies: similar\n- Encryption: similar\n\n**Diferenças:**\n- Namespaces no OCI (global)\n- Preços: [MUTABLE] OCI mais econômico\n\n**Endpoint:**\n```\nhttps://<namespace>.compat.objectstorage.<region>.oraclecloud.com\n```\n\nDocs: https://docs.oracle.com/en-us/iaas/Content/Object/", system))
    
    examples.append(create_example("migration-aws-storage", cat, "beginner",
        "Como mapear EBS para Block Storage?",
        "Mapeamento EBS → Block Storage:\n\n**Tipos:**\n- EBS gp2/gp3 → Block Volume Balanced\n- EBS io1/io2 → Block Volume Higher Performance\n- EBS st1 → (use File Storage para throughput)\n- EBS sc1 → (use Archive)\n\n**Sizes:**\n- EBS: 1GB - 16TB\n- Block Volume: 50GB - 32TB\n\n**Performance:**\n- gp3: 3000 IOPS → Balanced: 7500 IOPS\n- io2: 64000 IOPS → Higher Perf: 60000 IOPS\n\n**Features:**\n- Snapshots: similar\n- Encryption: similar\n- Attachment: similar\n\n**Diferenças:**\n- OCI: volumes mais performáticos\n- Multi-attach: ambos suportam\n\n**Pricing:** [MUTABLE] Comparable ou OCI mais barato", system))
    
    examples.append(create_example("migration-aws-storage", cat, "beginner",
        "Quais ferramentas para migrar dados?",
        "Ferramentas de migração de dados:\n\n**S3 → Object Storage:**\n\n**1. OCI Data Transfer:**\n- Online (network)\n- Offline (appliance)\n- Grande volume\n\n**2. Rclone:**\n```bash\n# Configure S3 e OCI remotes\nrclone copy s3:bucket oci:bucket\n```\n\n**3. OCI CLI:**\n```bash\noci os object bulk-download \\\n  --namespace <ns> \\\n  --bucket-name <bucket>\n```\n\n**4. Third-party:**\n- Cyberduck\n- Mountain Duck\n- CloudBerry\n\n**EBS → Block Volume:**\n- Snapshot → Image → Volume\n- Ou rsync para novo volume\n\n**Recomendação:**\n- <1TB: Rclone/CLI\n- >1TB: Data Transfer Service", system))
    
    # Intermediate (5)
    examples.append(create_example("migration-aws-storage", cat, "intermediate",
        "Como usar S3-compatible API do OCI?",
        "Usando S3-compatible API:\n\n**Configuração:**\n```ini\n# ~/.aws/config\n[default]\nregion = us-ashburn-1\n\n# ~/.aws/credentials\n[default]\naws_access_key_id = <oci-access-key>\naws_secret_access_key = <oci-secret-key>\nendpoint_url = https://<namespace>.compat.objectstorage.us-ashburn-1.oraclecloud.com\n```\n\n**AWS SDK (Python):**\n```python\nimport boto3\n\ns3 = boto3.client('s3',\n    endpoint_url='https://<namespace>.compat.objectstorage.us-ashburn-1.oraclecloud.com',\n    aws_access_key_id='<access-key>',\n    aws_secret_access_key='<secret-key>'\n)\n\n# List buckets\nbuckets = s3.list_buckets()\n\n# Upload\ns3.upload_file('file.txt', 'bucket', 'object.txt')\n```\n\n**Vantagem:** Reuse código existente\n\n**Limitações:** Algumas features S3 não suportadas", system))
    
    examples.append(create_example("migration-aws-storage", cat, "intermediate",
        "Como migrar S3 com Data Transfer?",
        "Data Transfer para S3:\n\n**Online (network):**\n\n**1. Crie job:**\n```bash\noci data-transfer job create \\\n  --compartment-id <ocid> \\\n  --display-name s3-migration \\\n  --transfer-type IMPORT \\\n  --source-type AWS_S3\n```\n\n**2. Configure source:**\n- AWS bucket\n- Credentials\n- Prefix/filters\n\n**3. Transfer:**\n- Automático via network\n- Monitor no Console\n\n**Offline (appliance):**\n\n**1. Request appliance:**\n- Oracle envia dispositivo\n\n**2. Copie dados:**\n- Mount appliance\n- rsync/cp dados\n\n**3. Return appliance:**\n- Oracle importa para Object Storage\n\n**Use offline quando:**\n- >10TB\n- Network limitada\n- Segurança exige\n\n[MUTABLE] Custos de transferência variam.", system))
    
    examples.append(create_example("migration-aws-storage", cat, "intermediate",
        "Como migrar EBS snapshots?",
        "Migrando EBS Snapshots:\n\n**Opção 1: Via instância:**\n```bash\n# 1. Crie volume do snapshot (AWS)\naws ec2 create-volume --snapshot-id snap-xxx\n\n# 2. Attach em instância\naws ec2 attach-volume ...\n\n# 3. Mount e copie\nmount /dev/xvdf /mnt\nrsync -av /mnt/ user@oci:/data\n\n# 4. Crie Block Volume (OCI)\noci bv volume create ...\n```\n\n**Opção 2: Export/Import:**\n```bash\n# 1. Exporte snapshot S3\naws ec2 export-snapshot ...\n\n# 2. Download VMDK\naws s3 cp s3://...\n\n# 3. Upload OCI Object Storage\noci os object put ...\n\n# 4. Importe como Custom Image\noci compute image import ...\n```\n\n**Opção 3: Third-party:**\n- CloudEndure\n- Zerto\n- Replicação contínua", system))
    
    examples.append(create_example("migration-aws-storage", cat, "intermediate",
        "Como configurar lifecycle policies?",
        "Lifecycle policies:\n\n**S3 → OCI:**\n\n**AWS:**\n```json\n{\n  \"Rules\": [{\n    \"ID\": \"Archive\",\n    \"Status\": \"Enabled\",\n    \"Transitions\": [{\n      \"Days\": 90,\n      \"StorageClass\": \"GLACIER\"\n    }]\n  }]\n}\n```\n\n**OCI:**\n```bash\noci os bucket put-lifecycle-policy \\\n  --namespace <ns> \\\n  --bucket-name <bucket> \\\n  --lifecycle-policy '{\n    \"rules\": [{\n      \"name\": \"Archive\",\n      \"action\": \"ARCHIVE_STORAGE_TIER\",\n      \"timeAmount\": 90,\n      \"timeUnit\": \"DAYS\"\n    }]\n  }'\n```\n\n**Actions OCI:**\n- ARCHIVE_STORAGE_TIER\n- DELETE\n- CHANGE_STORAGE_TIER\n\n**Tiers:**\n- Standard → Infrequent → Archive\n\n**Economia:** Archive ~70% mais barato", system))
    
    examples.append(create_example("migration-aws-storage", cat, "intermediate",
        "Como validar integridade na migração?",
        "Validando integridade:\n\n**1. Checksums:**\n```bash\n# AWS\naws s3api list-objects-v2 --bucket my-bucket \\\n  --query 'Contents[].{Key:Key,ETag:ETag}'\n\n# OCI\noci os object list --namespace <ns> --bucket <bucket> \\\n  --query 'data[].{Key:name,MD5:md5}'\n```\n\n**2. Compare counts:**\n```bash\n# Object count\naws s3 ls s3://bucket --recursive | wc -l\noci os object list --namespace <ns> --bucket <bucket> | jq '.data | length'\n```\n\n**3. Sample validation:**\n```bash\n# Download de ambos\naws s3 cp s3://bucket/file.txt /tmp/aws.txt\noci os object get --namespace <ns> --bucket <bucket> --name file.txt --file /tmp/oci.txt\n\n# Compare\ndiff /tmp/aws.txt /tmp/oci.txt\n```\n\n**4. Automated:**\n- Scripts de validação\n- Third-party tools\n- Checksums pré e pós", system))
    
    # Advanced (2)
    examples.append(create_example("migration-aws-storage", cat, "advanced",
        "Como migrar petabytes de dados?",
        "Migração de petabytes:\n\n**1. Estratégia:**\n- Offline (Data Transfer Appliance)\n- Parallel transfers\n- Incremental sync\n\n**2. Data Transfer Appliance:**\n```bash\n# Request appliance\noci data-transfer job create \\\n  --transfer-type IMPORT \\\n  --is-offline true \\\n  --transfer-appliance-shape \"100TB\"\n\n# Oracle envia dispositivo\n# Copie dados (até 100TB)\n# Return shipping label\n```\n\n**3. Parallel transfers:**\n```bash\n# Múltiplas threads\nrclone copy s3:bucket oci:bucket --transfers=32 --checkers=64\n\n# Ou múltiplas instâncias\neach instance copies subset of data\n```\n\n**4. Incremental:**\n- Initial: offline\n- Delta: online\n- Cutover: sync final\n\n**Timeline:**\n- 100TB offline: 1-2 semanas\n- Delta: horas\n\n**Custo:** [MUTABLE] Avalie vs network transfer", system))
    
    examples.append(create_example("migration-aws-storage", cat, "advanced",
        "Como implementar multi-cloud storage?",
        "Storage multi-cloud:\n\n**Cenário:** Dados em AWS + OCI\n\n**1. Replicação:**\n```python\nimport boto3\nimport oci\n\n# Upload em ambos\ns3 = boto3.client('s3')\nos_client = oci.object_storage.ObjectStorageClient()\n\ndef upload_both(key, data):\n    s3.put_object(Bucket='aws-bucket', Key=key, Body=data)\n    os_client.put_object(namespace='ns', bucket_name='oci-bucket', object_name=key, object_content=data)\n```\n\n**2. Failover:**\n- Primary: AWS\n- Secondary: OCI\n- DNS failover\n\n**3. Active-active:**\n- Read de ambos (latency-based)\n- Write em ambos (async)\n\n**4. Ferramentas:**\n- Rclone (sync)\n- Custom scripts\n- Third-party (Nasuni, Panzura)\n\n**Use cases:**\n- DR\n- Compliance (data residency)\n- Latency optimization", system))
    
    return examples

# Continue with more migration categories...
# (AWS Database, Azure, GCP, On-premises, Data Transfer)

def generate_migration_aws_database():
    examples = []
    system = "You are an OCI migration specialist with expertise in AWS to OCI database migrations. Provide technical guidance on RDS to Oracle DB, MySQL, PostgreSQL migration."
    cat = "migration/aws-database"
    
    # Beginner (3)
    examples.append(create_example("migration-aws-database", cat, "beginner",
        "Como mapear RDS para OCI Database?",
        "Mapeamento RDS → OCI Database:\n\n**RDS Oracle → OCI:**\n- RDS Oracle → Autonomous Database\n- RDS Oracle → DB System (Exadata)\n\n**RDS MySQL → OCI:**\n- RDS MySQL → MySQL HeatWave\n- RDS MySQL → MySQL em Compute\n\n**RDS PostgreSQL → OCI:**\n- RDS PostgreSQL → PostgreSQL em Compute\n- RDS PostgreSQL → Autonomous JSON (se JSON-heavy)\n\n**RDS SQL Server → OCI:**\n- RDS SQL Server → SQL Server em Compute\n\n**Aurora → OCI:**\n- Aurora MySQL → MySQL HeatWave\n- Aurora PostgreSQL → PostgreSQL em Compute\n\n**Diferenças:**\n- OCI: mais opções Oracle\n- AWS: mais managed services\n\n[MUTABLE] Preços variam por serviço.", system))
    
    examples.append(create_example("migration-aws-database", cat, "beginner",
        "Quais ferramentas para migrar databases?",
        "Ferramentas de migração de database:\n\n**Oracle:**\n- Data Pump (export/import)\n- Data Guard (replicação)\n- GoldenGate (CDC)\n- RMAN (backup/restore)\n\n**MySQL:**\n- mysqldump\n- MySQL Shell (dump/load)\n- MySQL Enterprise Backup\n- Third-party: pt-tools\n\n**PostgreSQL:**\n- pg_dump/pg_restore\n- pglogical (replication)\n- Logical replication\n\n**Multi-engine:**\n- AWS DMS → OCI (custom)\n- Striped (third-party)\n\n**Recomendação:**\n- Small (<100GB): dump/load\n- Medium: replication\n- Large: GoldenGate/DMS\n\n**Downtime:**\n- Dump: horas\n- Replication: minutos", system))
    
    examples.append(create_example("migration-aws-database", cat, "beginner",
        "O que é MySQL HeatWave?",
        "MySQL HeatWave:\n\n**O que é:**\n- MySQL compatível com Oracle Cloud\n- In-memory query accelerator\n- Analytics em tempo real\n\n**Features:**\n- 100% MySQL compatible\n- HeatWave: in-memory column store\n- OLTP + OLAP no mesmo banco\n\n**Performance:**\n- HeatWave: 100-1000x queries analytics\n- Sem ETL necessário\n\n**Casos de uso:**\n- Aplicações MySQL existentes\n- Analytics em tempo real\n- Substituir RDS MySQL + Redshift\n\n**Migração:**\n- mysqldump → HeatWave\n- Replication: MySQL native\n\n[MUTABLE] Preços por node.", system))
    
    # Intermediate (5)
    examples.append(create_example("migration-aws-database", cat, "intermediate",
        "Como migrar RDS Oracle para Autonomous?",
        "RDS Oracle → Autonomous Database:\n\n**1. Export (RDS):**\n```sql\n-- Data Pump export\nexpdp system/password \\\n  DIRECTORY=rds-datapump-dir \\\n  DUMPFILE=export.dmp \\\n  FULL=Y\n```\n\n**2. Copy para OCI:**\n```bash\naws s3 cp s3://rds-bucket/export.dmp .\noci os object put --namespace <ns> --bucket <bucket> --file export.dmp\n```\n\n**3. Import (Autonomous):**\n```sql\n-- No Autonomous\nBEGIN\n  DBMS_CLOUD.COPY_DATA(\n    table_name => 'MY_TABLE',\n    credential_name => 'OBJ_STORE_CRED',\n    file_uri_list => 'https://.../export.dmp'\n  );\nEND;\n```\n\n**4. Ou use Data Pump:**\n```bash\nimpdp admin/password@adb \\\n  dumpfile=export.dmp \\\n  directory=DATA_PUMP_DIR\n```\n\n**Downtime:** Horas para dump/import", system))
    
    examples.append(create_example("migration-aws-database", cat, "intermediate",
        "Como usar Data Guard para migração?",
        "Data Guard para migração:\n\n**Cenário:** RDS Oracle → OCI DB System\n\n**1. Configure RDS como Primary:**\n```sql\n-- RDS\nALTER DATABASE ARCHIVELOG;\nALTER DATABASE FORCE LOGGING;\n```\n\n**2. Crie Standby no OCI:**\n```sql\n-- OCI\nDUPLICATE DATABASE FROM ACTIVE DATABASE\n  FOR STANDBY\n  FROM PRIMARY\n  DOFILE_CONVERT ...\n```\n\n**3. Replicação:**\n- Redo transport automático\n- Apply no standby\n- Lag: segundos\n\n**4. Cutover:**\n```sql\n-- Failover\nALTER DATABASE COMMIT TO SWITCHOVER TO STANDBY;\n```\n\n**5. Pós-cutover:**\n- OCI vira primary\n- Apps reconectam\n\n**Vantagem:** Downtime mínimo (<5 min)\n\n**Requisito:** Mesma versão Oracle", system))
    
    examples.append(create_example("migration-aws-database", cat, "intermediate",
        "Como migrar MySQL com replication?",
        "MySQL replication migration:\n\n**1. Configure source (RDS):**\n```sql\n-- RDS MySQL\nCALL mysql.rds_set_external_master_gtid_mode('ON');\n\n-- Crie replication user\nCREATE USER 'repl'@'%' IDENTIFIED BY 'password';\nGRANT REPLICATION SLAVE ON *.* TO 'repl'@'%';\n```\n\n**2. Configure target (OCI):**\n```sql\n-- OCI MySQL\nCHANGE MASTER TO\n  MASTER_HOST='<rds-endpoint>',\n  MASTER_USER='repl',\n  MASTER_PASSWORD='password',\n  MASTER_AUTO_POSITION=1;\n\nSTART SLAVE;\n```\n\n**3. Monitore:**\n```sql\nSHOW SLAVE STATUS\\G\n-- Seconds_Behind_Master: 0 = synced\n```\n\n**4. Cutover:**\n```sql\n-- Stop writes (RDS)\n-- Wait sync\n-- STOP SLAVE (OCI)\n-- SET GLOBAL read_only=0;\n-- Apps conectam no OCI\n```\n\n**Downtime:** Minutos", system))
    
    examples.append(create_example("migration-aws-database", cat, "intermediate",
        "Como validar migração de database?",
        "Validação de migração:\n\n**1. Schema comparison:**\n```bash\n# Export schemas\nmysqldump -h rds --no-data > aws-schema.sql\nmysqldump -h oci --no-data > oci-schema.sql\n\n# Compare\ndiff aws-schema.sql oci-schema.sql\n```\n\n**2. Row counts:**\n```sql\n-- AWS\nSELECT table_name, table_rows \nFROM information_schema.tables \nWHERE table_schema = 'mydb';\n\n-- OCI\n-- Mesma query, compare resultados\n```\n\n**3. Data validation:**\n```sql\n-- Sample checksum\nSELECT MD5(GROUP_CONCAT(id ORDER BY id)) \nFROM my_table;\n```\n\n**4. Performance:**\n- Run queries idênticas\n- Compare explain plans\n- Benchmark tools\n\n**5. Application tests:**\n- Smoke tests\n- Integration tests\n- Load tests\n\n**Tools:**\n- pt-table-checksum (Percona)\n- Custom scripts", system))
    
    examples.append(create_example("migration-aws-database", cat, "intermediate",
        "Como lidar com diferenças de engine?",
        "Diferenças de engine:\n\n**RDS MySQL → OCI MySQL:**\n- Quase 100% compatível\n- Versões podem diferir\n- Teste features específicas\n\n**RDS PostgreSQL → OCI PostgreSQL:**\n- Extensions podem faltar\n- Version differences\n- Teste custom code\n\n**Aurora → OCI:**\n- Aurora features não existem no OCI\n- Reescreva se usar Aurora-specific\n\n**SQL Server:**\n- Licensing (BYOL vs License Included)\n- Features enterprise\n\n**Mitigação:**\n1. Inventário de features usadas\n2. Teste em staging\n3. Refatore se necessário\n4. Documente workarounds\n\n**Common issues:**\n- Stored procedures\n- Triggers\n- Custom extensions\n- Version-specific syntax", system))
    
    # Advanced (2)
    examples.append(create_example("migration-aws-database", cat, "advanced",
        "Como migrar com GoldenGate?",
        "GoldenGate para migração:\n\n**Cenário:** Migração zero-downtime\n\n**1. Configure Extract (AWS):**\n```bash\n# AWS (source)\nADD EXTRACT ext1, TRANLOG, BEGIN NOW\nADD EXTTRAIL /gg/trail/ext1, EXTRACT ext1\n```\n\n**2. Configure Replicat (OCI):**\n```bash\n# OCI (target)\nADD REPLICAT rep1, EXTTRAIL /gg/trail/ext1\n```\n\n**3. Mapeamento:**\n```bash\nTABLE rds_schema.*;\nTARGET oci_schema.*;\n```\n\n**4. Inicie replicação:**\n```bash\nSTART EXTRACT ext1\nSTART REPLICAT rep1\n```\n\n**5. Cutover:**\n- Stop writes (AWS)\n- Wait lag = 0\n- Stop replicat\n- Apps conectam OCI\n\n**Vantagem:** Downtime segundos\n\n**Custo:** [MUTABLE] GoldenGate é licenciado", system))
    
    examples.append(create_example("migration-aws-database", cat, "advanced",
        "Como migrar database grande (>1TB)?",
        "Migração de database grande:\n\n**Estratégia:**\n- Full backup + CDC\n- Ou replication contínua\n\n**1. Full backup inicial:**\n```bash\n# RDS\nmysqldump --single-transaction --quick \\\n  --master-data=2 > full.sql\n\n# Ou physical backup\nxtrabackup --backup --target-dir=/backup\n```\n\n**2. Restore no OCI:**\n```bash\n# OCI\nmysql < full.sql\n# Ou\nxtrabackup --prepare --target-dir=/backup\nxtrabackup --copy-back\n```\n\n**3. CDC (replication):**\n```sql\n-- Configure replication do ponto do backup\nCHANGE MASTER TO\n  MASTER_LOG_FILE='mysql-bin.000123',\n  MASTER_LOG_POS=456789;\nSTART SLAVE;\n```\n\n**4. Sync:**\n- Replication catches up\n- Lag → 0\n\n**5. Cutover:**\n- Janela agendada\n- Downtime mínimo\n\n**Timeline:**\n- Full: dias\n- CDC: contínuo\n- Cutover: horas", system))
    
    return examples

# Main execution
def main():
    generators = {
        "migration-aws-compute": generate_migration_aws_compute,
        "migration-aws-storage": generate_migration_aws_storage,
        "migration-aws-database": generate_migration_aws_database,
    }
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    for category, generator in generators.items():
        examples = generator()
        write_jsonl(f"{category}.jsonl", examples)
    
    print(f"\nTotal: {len(generators)} files generated")

if __name__ == "__main__":
    main()
