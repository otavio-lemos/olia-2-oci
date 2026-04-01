#!/usr/bin/env python3
"""Fix missing and incomplete JSONL files."""

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

# Migration GCP Storage
def generate_migration_gcp_storage():
    examples = []
    system = "You are an OCI migration specialist with expertise in GCP to OCI migrations."
    cat = "migration/gcp-storage"
    
    examples.append(create_example("migration-gcp-storage", cat, "beginner",
        "Como mapear GCS para Object Storage?",
        "Mapeamento GCS → Object Storage:\n\n**Conceitos:**\n- GCS Bucket → Object Storage Bucket\n- GCS Object → Object Storage Object\n- GCS Folder → Object prefix\n\n**Storage classes:**\n- GCS Standard → OCI Standard\n- GCS Nearline → OCI Infrequent Access\n- GCS Coldline → OCI Archive\n- GCS Archive → OCI Archive\n\n**APIs:**\n- GCS JSON API → OCI SDK\n- GCS XML API → S3-compatible API\n\n**Diferenças:**\n- OCI: namespaces (globais)\n- Preços: [MUTABLE] OCI mais econômico", system))
    
    examples.append(create_example("migration-gcp-storage", cat, "beginner",
        "Quais ferramentas para migrar GCS?",
        "Ferramentas GCS → Object Storage:\n\n**1. OCI Data Transfer:**\n- Online (network)\n- Offline (appliance)\n\n**2. gsutil + OCI CLI:**\n```bash\ngsutil -m cp -r gs://bucket/* /tmp/data/\noci os object bulk-upload --namespace <ns> --bucket <bucket> --src-dir /tmp/data\n```\n\n**3. Rclone:**\n```bash\nrclone copy gcs:bucket oci:bucket\n```\n\n**Recomendação:**\n- <1TB: gsutil + OCI CLI\n- >1TB: Data Transfer Service", system))
    
    examples.append(create_example("migration-gcp-storage", cat, "beginner",
        "Como copiar dados do GCS?",
        "Copiando do GCS:\n\n**gsutil:**\n```bash\n# Single object\ngsutil cp gs://bucket/file.txt /tmp/file.txt\n\n# Recursive\ngsutil -m cp -r gs://bucket /tmp/data\n\n# Parallel\ngsutil -m -o 'GSUtil:parallel_process_count=4' cp -r gs://bucket /tmp/data\n```\n\n**SDK Python:**\n```python\nfrom google.cloud import storage\nclient = storage.Client()\nbucket = client.bucket('my-bucket')\nfor blob in bucket.list_blobs():\n    blob.download_to_filename(f'/tmp/{blob.name}')\n```\n\n**Próximo:** Upload para OCI Object Storage", system))
    
    examples.append(create_example("migration-gcp-storage", cat, "intermediate",
        "Como usar gsutil com OCI?",
        "gsutil → OCI:\n\n**gsutil não suporta OCI nativamente**\n\n**Workaround:**\n\n**1. Download GCS:**\n```bash\ngsutil -m cp -r gs://bucket /tmp/data\n```\n\n**2. Upload OCI:**\n```bash\noci os object bulk-upload \\\n  --namespace <namespace> \\\n  --bucket-name <bucket> \\\n  --src-dir /tmp/data \\\n  --recursive\n```\n\n**3. Ou Rclone:**\n```ini\n[gcs]\ntype = google cloud storage\n\n[oci]\ntype = s3\nprovider = Other\nendpoint = https://<namespace>.compat.objectstorage.<region>.oraclecloud.com\n```\n\n```bash\nrclone copy gcs:bucket oci:bucket\n```", system))
    
    examples.append(create_example("migration-gcp-storage", cat, "intermediate",
        "Como configurar lifecycle policies?",
        "Lifecycle policies OCI:\n\n**GCS → OCI:**\n\n**GCS:**\n```json\n{\"rule\": [{\"action\": {\"type\": \"SetStorageClass\", \"storageClass\": \"NEARLINE\"}, \"condition\": {\"age\": 30}}]}\n```\n\n**OCI:**\n```bash\noci os bucket put-lifecycle-policy \\\n  --namespace <ns> \\\n  --bucket-name <bucket> \\\n  --lifecycle-policy '{\n    \"rules\": [{\n      \"name\": \"cool-tier\",\n      \"action\": \"CHANGE_STORAGE_TIER\",\n      \"timeAmount\": 30,\n      \"timeUnit\": \"DAYS\",\n      \"storageTier\": \"INFREQUENT_ACCESS\"\n    }]\n  }'\n```\n\n**Tiers OCI:**\n- STANDARD\n- INFREQUENT_ACCESS\n- ARCHIVE\n\n**Economia:** Archive ~70% mais barato", system))
    
    examples.append(create_example("migration-gcp-storage", cat, "intermediate",
        "Como validar integridade?",
        "Validando integridade:\n\n**1. Object counts:**\n```bash\ngsutil du -c gs://bucket | tail -1\noci os object list --namespace <ns> --bucket <bucket> | jq '.data | length'\n```\n\n**2. Checksums:**\n```bash\ngsutil ls -L gs://bucket/file | grep Hash\noci os object head --namespace <ns> --bucket <bucket> --name file | jq '.md5'\n```\n\n**3. Sample validation:**\n```bash\ngsutil cp gs://bucket/file /tmp/gcs.txt\noci os object get --namespace <ns> --bucket <bucket> --name file --file /tmp/oci.txt\ndiff /tmp/gcs.txt /tmp/oci.txt\n```\n\n**4. Automated:**\n- Scripts de validação\n- Compare counts + checksums", system))
    
    examples.append(create_example("migration-gcp-storage", cat, "intermediate",
        "Como migrar buckets grandes?",
        "Migrando buckets grandes:\n\n**1. Parallel transfer:**\n```bash\ngsutil -m cp -r gs://bucket /tmp/data\noci os object bulk-upload --src-dir /tmp/data --parallel-upload-count 10\n```\n\n**2. Múltiplas instâncias:**\n```bash\n# Instância 1: prefixos A-M\ngsutil -m cp gs://bucket/[a-m]* /tmp/data/\n\n# Instância 2: prefixos N-Z\ngsutil -m cp gs://bucket/[n-z]* /tmp/data/\n```\n\n**3. Data Transfer:**\n- Online: network direta\n- Offline: appliance (100TB)\n\n**Timeline:**\n- 10TB: 1-2 dias (network)\n- 100TB: offline appliance", system))
    
    examples.append(create_example("migration-gcp-storage", cat, "advanced",
        "Como migrar com Data Transfer?",
        "Data Transfer para GCS:\n\n**Online:**\n```bash\noci data-transfer job create \\\n  --compartment-id <ocid> \\\n  --transfer-type IMPORT \\\n  --source-type GOOGLE_CLOUD_STORAGE\n```\n\n**Configure:**\n- GCS bucket\n- Credentials (service account)\n- Prefix/filters\n\n**Offline (appliance):**\n```bash\noci data-transfer job create \\\n  --is-offline true \\\n  --transfer-appliance-shape \"100TB\"\n```\n\n**Processo:**\n1. Oracle envia appliance\n2. gsutil copy para appliance\n3. Return shipping\n4. Oracle importa para OCI\n\n[MUTABLE] Custos variam por volume/região", system))
    
    examples.append(create_example("migration-gcp-storage", cat, "advanced",
        "Como implementar multi-cloud storage?",
        "Storage multi-cloud GCP + OCI:\n\n**1. Replicação:**\n```python\nfrom google.cloud import storage\nimport oci\n\ngcs = storage.Client()\nos_client = oci.object_storage.ObjectStorageClient()\n\ndef replicate(blob_name):\n    blob = gcs.bucket('gcs-bucket').blob(blob_name)\n    data = blob.download_as_bytes()\n    os_client.put_object(\n        namespace='ns',\n        bucket_name='oci-bucket',\n        object_name=blob_name,\n        object_content=data\n    )\n```\n\n**2. Failover:**\n- Primary: GCS\n- DR: OCI\n- DNS failover\n\n**Use cases:**\n- DR\n- Compliance (data residency)\n- Latency optimization", system))
    
    return examples

# Migration GCP Database
def generate_migration_gcp_database():
    examples = []
    system = "You are an OCI migration specialist with expertise in GCP to OCI database migrations."
    cat = "migration/gcp-database"
    
    examples.append(create_example("migration-gcp-database", cat, "beginner",
        "Como mapear Cloud SQL para OCI?",
        "Mapeamento Cloud SQL → OCI:\n\n**Cloud SQL MySQL → OCI:**\n- MySQL HeatWave\n- MySQL em Compute\n\n**Cloud SQL PostgreSQL → OCI:**\n- PostgreSQL em Compute\n- Autonomous JSON\n\n**Cloud SQL SQL Server → OCI:**\n- SQL Server em Compute\n\n**Spanner → OCI:**\n- Autonomous Database (sharding)\n- NoSQL Database\n\n**Firestore → OCI:**\n- Autonomous JSON Database\n- NoSQL Database\n\n[MUTABLE] Preços variam por serviço.", system))
    
    examples.append(create_example("migration-gcp-database", cat, "beginner",
        "Como migrar Cloud SQL MySQL?",
        "Migrando Cloud SQL MySQL:\n\n**1. mysqldump:**\n```bash\nmysqldump -h <cloud-sql-ip> -u admin -p \\\n  --single-transaction \\\n  --all-databases > dump.sql\n\nmysql -h <oci-host> -u admin -p < dump.sql\n```\n\n**2. Replication:**\n```sql\n-- Cloud SQL (source)\nCREATE USER 'repl'@'%' IDENTIFIED BY 'password';\nGRANT REPLICATION SLAVE ON *.* TO 'repl'@'%';\n\n-- OCI (target)\nCHANGE MASTER TO MASTER_HOST='<cloud-sql-ip>', ...;\nSTART SLAVE;\n```\n\n**Downtime:** Dump: horas, Replication: minutos", system))
    
    examples.append(create_example("migration-gcp-database", cat, "beginner",
        "Como migrar Cloud SQL PostgreSQL?",
        "Migrando Cloud SQL PostgreSQL:\n\n**1. pg_dump:**\n```bash\npg_dump -h <cloud-sql-ip> -U admin -d mydb > dump.sql\npsql -h <oci-host> -U admin -d mydb < dump.sql\n```\n\n**2. Logical Replication:**\n```sql\n-- Cloud SQL (publisher)\nCREATE PUBLICATION mypub FOR ALL TABLES;\n\n-- OCI (subscriber)\nCREATE SUBSCRIPTION mysub \\\n  CONNECTION 'host=<cloud-sql-ip> dbname=mydb user=repl' \\\n  PUBLICATION mypub;\n```\n\n**Downtime:**\n- pg_dump: horas\n- Replication: minutos", system))
    
    examples.append(create_example("migration-gcp-database", cat, "intermediate",
        "Como migrar Spanner?",
        "Migrando Spanner:\n\n**Spanner → Autonomous Database:**\n\n**1. Export Spanner:**\n```bash\ngcloud spanner databases dump mydb > dump.sql\n```\n\n**2. Convert schema:**\n- Spanner SQL → Oracle SQL\n\n**3. Import Autonomous:**\n```bash\nimpdp admin/password@adb \\\n  dumpfile=dump.dmp \\\n  directory=DATA_PUMP_DIR\n```\n\n**Ou NoSQL Database:**\n- Export como JSON\n- Import no OCI NoSQL\n\n**Schema:** Pode precisar transformação significativa", system))
    
    examples.append(create_example("migration-gcp-database", cat, "intermediate",
        "Como migrar Firestore?",
        "Migrando Firestore → OCI:\n\n**Firestore → Autonomous JSON:**\n\n**1. Export Firestore:**\n```bash\ngcloud firestore export gs://bucket/export\n```\n\n**2. Download:**\n```bash\ngsutil cp -r gs://bucket/export .\n```\n\n**3. Convert para JSON:**\n```python\nfrom google.cloud import firestore\nclient = firestore.Client()\ncollection = client.collection('my_collection')\ndocs = collection.stream()\ndata = [doc.to_dict() for doc in docs]\n```\n\n**4. Import Autonomous JSON:**\n```python\nfrom soda import *\ndb = get_database()\ncollection = db.createCollection('firestore_data')\nfor item in data:\n    collection.insertOne(item)\n```\n\n**Schema:** Document-based, similar", system))
    
    examples.append(create_example("migration-gcp-database", cat, "intermediate",
        "Como validar migração de database?",
        "Validação de migração:\n\n**1. Schema comparison:**\n```bash\npg_dump -s -h <gcp> > gcp-schema.sql\npg_dump -s -h <oci> > oci-schema.sql\ndiff gcp-schema.sql oci-schema.sql\n```\n\n**2. Row counts:**\n```sql\nSELECT schemaname, tablename, n_live_tup FROM pg_stat_user_tables;\n```\n\n**3. Data validation:**\n```sql\nSELECT md5(string_agg(id::text, ',')) FROM my_table;\n```\n\n**4. Performance:**\n- Run queries idênticas\n- Compare explain plans\n\n**5. Application tests:**\n- Smoke tests\n- Integration tests\n- Load tests", system))
    
    examples.append(create_example("migration-gcp-database", cat, "intermediate",
        "Como migrar com Dataflow?",
        "Dataflow → OCI:\n\n**1. Dataflow job:**\n```python\nimport apache_beam as beam\n\nwith beam.Pipeline() as p:\n    (p\n     | 'Read GCP' >> beam.io.ReadFromBigQuery(...)\n     | 'Write OCI' >> beam.io.WriteToText('oci://bucket/output'))\n```\n\n**2. Ou Dataflow → GCS → OCI:**\n```python\nwith beam.Pipeline() as p:\n    (p\n     | 'Read' >> beam.io.Read(...)\n     | 'Write GCS' >> beam.io.WriteToGCS('gs://bucket/output'))\n\n# Depois copy para OCI\ngsutil cp gs://bucket/output/* .\noci os object bulk-upload ...\n```\n\n**Vantagem:** Processamento durante migração", system))
    
    examples.append(create_example("migration-gcp-database", cat, "advanced",
        "Como migrar database grande?",
        "Migração de database grande:\n\n**Estratégia:**\n- Full backup + CDC\n- Ou replication contínua\n\n**1. Full backup:**\n```bash\nmysqldump -h <cloud-sql-ip> --all-databases > full.sql\n```\n\n**2. Restore OCI:**\n```bash\nmysql -h <oci-host> < full.sql\n```\n\n**3. CDC (replication):**\n```sql\nCHANGE MASTER TO MASTER_HOST='<cloud-sql-ip>', ...;\nSTART SLAVE;\n```\n\n**4. Sync:**\n- Replication catches up\n- Lag → 0\n\n**5. Cutover:**\n- Janela agendada\n- Downtime mínimo\n\n**Timeline:**\n- Full: dias\n- CDC: contínuo\n- Cutover: horas", system))
    
    examples.append(create_example("migration-gcp-database", cat, "advanced",
        "Como migrar para MySQL HeatWave?",
        "Migrando para MySQL HeatWave:\n\n**Cloud SQL MySQL → HeatWave:**\n\n**1. Export:**\n```bash\nmysqldump -h <cloud-sql-ip> -u admin -p \\\n  --single-transaction \\\n  --all-databases > dump.sql\n```\n\n**2. Crie HeatWave:**\n```bash\noci mysql db-system create \\\n  --compartment-id <ocid> \\\n  --display-name heatwave-prod \\\n  --is-heatwave-cluster-attached true\n```\n\n**3. Import:**\n```bash\nmysql -h <heatwave-ip> -u admin -p < dump.sql\n```\n\n**4. Enable HeatWave:**\n```sql\nALTER TABLE my_table SECONDARY_ENGINE = RAPID;\n```\n\n**Benefícios:**\n- 100-1000x analytics\n- Sem ETL\n- MySQL compatible", system))
    
    return examples

# Fix incomplete files
def fix_incomplete_files():
    """Add missing examples to files with only 9 lines."""
    
    # Fix migration-onprem-compute
    system = "You are an OCI migration specialist with expertise in on-premises to OCI migrations."
    cat = "migration/onprem-compute"
    
    with open(os.path.join(OUTPUT_DIR, "migration-onprem-compute.jsonl"), 'a', encoding='utf-8') as f:
        example = create_example("migration-onprem-compute", cat, "advanced",
            "Como otimizar custos pós-migração?",
            "Otimização de custos pós-migração:\n\n**1. Right-sizing:**\n```bash\noci monitoring metrics list \\\n  --namespace oci_computeagent \\\n  --metric-name CpuUtilization\n```\n\n**2. Instance pools:**\n- Melhor utilization\n- Scaling automático\n\n**3. ARM migration:**\n- x86 → ARM (Ampere A1)\n- Até 80% mais econômico\n\n**4. Reserved instances:**\n- 1 ou 3 anos\n- Até 60% desconto\n\n**ROI típico:** 30-50% redução vs on-premises\n\n[MUTABLE] Preços variam por região.", system)
        f.write(json.dumps(example, ensure_ascii=False) + '\n')
    print("Fixed: migration-onprem-compute.jsonl")
    
    # Fix migration-onprem-storage
    system = "You are an OCI migration specialist with expertise in on-premises storage migrations."
    cat = "migration/onprem-storage"
    
    with open(os.path.join(OUTPUT_DIR, "migration-onprem-storage.jsonl"), 'a', encoding='utf-8') as f:
        example = create_example("migration-onprem-storage", cat, "advanced",
            "Como otimizar custos de storage?",
            "Otimização de custos de storage:\n\n**1. Lifecycle policies:**\n- Standard → IA (30 dias)\n- IA → Archive (90 dias)\n\n**2. Deduplication:**\n- Remova dados duplicados\n- Compacte arquivos\n\n**3. Compression:**\n- gzip antes de upload\n- Economiza storage e network\n\n**4. Tiering automático:**\n```bash\noci os bucket put-lifecycle-policy ...\n```\n\n**Economia:**\n- IA: 40% vs Standard\n- Archive: 70% vs Standard\n\n[MUTABLE] Preços variam por região.", system)
        f.write(json.dumps(example, ensure_ascii=False) + '\n')
    print("Fixed: migration-onprem-storage.jsonl")

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Generate missing GCP files
    write_jsonl("migration-gcp-storage.jsonl", generate_migration_gcp_storage())
    write_jsonl("migration-gcp-database.jsonl", generate_migration_gcp_database())
    
    # Fix incomplete files
    fix_incomplete_files()
    
    print("\nAll files completed!")

if __name__ == "__main__":
    main()
