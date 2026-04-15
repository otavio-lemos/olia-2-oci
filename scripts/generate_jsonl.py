#!/usr/bin/env python3
import json
import random

random.seed(42)

companies = [
    "TechCorp Brasil",
    "DataFlow Solutions",
    "CloudNative Inc",
    "LogiTrack Logistics",
    "FinServe Digital",
    "RetailMax Online",
    "HealthTech Systems",
    "EduPlatform Global",
    "AgriTech Innovations",
    "SecureBank Corp",
    "TravelHub Platform",
    "SmartCity IoT",
    "BioResearch Labs",
    "AutoDrive Systems",
    "GameForge Studios",
    "MediaStream Pro",
    "LegalDoc Manager",
    "InsureTech Plus",
    "FoodChain Trace",
    "FinanceHub Corp",
]

regions = [
    "sa-saopaulo-1",
    "us-ashburn-1",
    "us-phoenix-1",
    "eu-frankfurt-1",
    "uk-london-1",
    "ap-sydney-1",
    "ap-tokyo-1",
    "ap-mumbai-1",
    "ca-toronto-1",
    "me-jeddah-1",
]

personas = [
    "cloud architect",
    "platform engineer",
    "sre",
    "security lead",
    "dba",
    "finops analyst",
    "auditor",
    "devops engineer",
]
intents = [
    "design",
    "compare",
    "troubleshoot",
    "remediate",
    "optimize",
    "audit",
    "review",
    "migrate",
    "recover",
    "standardize",
]
lifecycles = [
    "greenfield",
    "brownfield",
    "produção estável",
    "migração",
    "expansão",
    "desativação",
    "incidente",
    "auditoria",
]


def generate_examples(category, qa_by_difficulty):
    examples = []
    for difficulty in ["beginner", "intermediate", "advanced"]:
        count = {"beginner": 54, "intermediate": 90, "advanced": 36}[difficulty]
        qa_pairs = qa_by_difficulty[difficulty]
        for i in range(count):
            company = random.choice(companies)
            region = random.choice(regions)
            persona = random.choice(personas)
            intent = random.choice(intents)
            lifecycle = random.choice(lifecycles)

            q, a = random.choice(qa_pairs)
            question = (
                f"{q} para {company} no projeto {lifecycle}, considerando {intent}."
            )

            examples.append(
                {
                    "question": question,
                    "answer": a,
                    "metadata": {
                        "category": category,
                        "difficulty": difficulty,
                        "persona": persona,
                        "intent": intent,
                        "lifecycle": lifecycle,
                    },
                }
            )
    return examples


# LB Load Balancer
lb_qa = {
    "beginner": [
        (
            "Como configurar listener para APPLICATION?",
            "Para configurar via Console:\n1. Load Balancer → Backend Sets → Create\n2. Defina nome e policy\n3. Configure health check básico\n4. Adicione backends\n\n[MUTABLE] Custo: $25/mês para Starter shape.",
        ),
        (
            "Como verificar status do Load Balancer?",
            "Verifique o status com:\n```bash\noci lb load-balancer get --load-balancer-id <OCID>\n```\n\nEstados: ACTIVE, FAILED, DELETED",
        ),
        (
            "Qual shape de Load Balancer escolher?",
            "Shapes disponíveis:\n- Flexible Starter: 10 Mbps ($25/mês)\n- Flexible: 10-10000 Mbps\n- Dedicated: Hardware dedicado\n\n[CHECK DOCS] Limites em docs.oracle.com.",
        ),
        (
            "Como criar backend set básico?",
            "Backend Set agrupa backends com mesma config:\n1. Policy: ROUND_ROBIN, LEAST_CONNECTIONS\n2. Health check\n3. Session persistence\n\n[MUTABLE] Máximo 100 backends por set.",
        ),
        (
            "Como configurar health check simples?",
            'Health check básico:\n```json\n{\n  "protocol": "HTTP",\n  "port": 80,\n  "url-path": "/health",\n  "interval-in-millis": 10000,\n  "timeout-in-millis": 3000\n}\n```',
        ),
        (
            "O que é SSL termination?",
            "SSL Termination descriptografa tráfego no LB:\n- Reduz carga nos backends\n- Gerenciamento centralizado\n\n[CHECK DOCS] PCI-DSS requer configuração específica.",
        ),
        (
            "Como adicionar certificado?",
            'Adicione certificado:\n```bash\noci lb certificate create --load-balancer-id <LB_OCID> --certificate-name "meu-cert" --public-certificate-file file://cert.pem\n```',
        ),
    ],
    "intermediate": [
        (
            "Como criar Load Balancer via OCI CLI?",
            'Crie o Load Balancer:\n```bash\noci lb load-balancer create --compartment-id <OCID> --display-name "meu-lb" --shape-name "flexible" --shape-details \'{"max-bandwidth-in-mbps": 100}\' --subnet-ids \'[<SUBNET_OCID>]\'\n```',
        ),
        (
            "Como configurar backend set com múltiplos backends?",
            'Crie backend set:\n```bash\noci lb backend-set create --load-balancer-id <LB_OCID> --name "backend-web" --policy "ROUND_ROBIN" --health-checks \'[{"protocol": "HTTP", "port": 80, "url-path": "/health"}]\'\n```',
        ),
        (
            "Como configurar path-based routing?",
            'Path-based routing usa regras:\n```json\n{\n  "condition": "path_starts_with",\n  "paths": ["/api/*"],\n  "backend-set-name": "backend-api"\n}\n```\n\n[CHECK DOCS] Limite de regras por LB.',
        ),
        (
            "Como configurar session persistence?",
            "Session persistence mantém usuário no mesmo backend:\n1. Cookie-based: LB insere cookie\n2. SSL Session ID: mantém conexão\n\n[MUTABLE] Custo adicional pode aplicar.",
        ),
        (
            "Como migrar para OCI Load Balancer?",
            "Migração step-by-step:\n1. Crie LB no OCI\n2. Configure backends\n3. Teste com traffic 10%\n4. Aumente gradualmente\n5. Descomissione fonte",
        ),
        (
            "Como configurar health check com timeoutcustom?",
            'Health check avançado:\n```json\n{\n  "protocol": "HTTP",\n  "port": 443,\n  "url-path": "/health",\n  "interval-in-millis": 5000,\n  "timeout-in-millis": 2000,\n  "unhealthy-threshold": 3,\n  "healthy-threshold": 3\n}\n```',
        ),
        (
            "Como resolver problemas de conectividade?",
            "Troubleshooting:\n1. Verifique status do LB\n2. Check health dos backends\n3. Verifique Security Lists\n4. Teste conectividade direta\n5. Check logs de audit",
        ),
    ],
    "advanced": [
        (
            "Como configurar Load Balancer para alta disponibilidade entre regiões?",
            "HA multi-região:\n1. Crie LB em cada região\n2. Configure DNS com failover\n3. Sincronize backends\n4. Teste failover\n\n[CHECK DOCS] SLA 99.99% requer configuração específica.",
        ),
        (
            "Como configurar multi-region failover?",
            "Configure DR:\n1. Primary LB em região A\n2. Standby em região B\n3. DNS health check\n4. Failover automático\n\n[MUTABLE] Custo de egress entre regiões.",
        ),
        (
            "Como integrar com auto scaling?",
            "Auto scaling integration:\n1. Crie Instance Pool\n2. Configure autoscaling\n3. Associe ao LB\n4. Escala automático",
        ),
        (
            "Como implementar zero-downtime migration?",
            "Zero-downtime migration:\n1. Blue-green deployment\n2. Weighted DNS (10%→100%)\n3. Health validation\n4. Cutover progressivo\n5. Rollback procedure ready",
        ),
        (
            "Como implementar disaster recovery?",
            "Disaster recovery:\n1. RPO < 5 min\n2. RTO < 15 min\n3. Multi-AD deployment\n4. Cross-region replicate\n\n[CHECK DOCS] Backup policies em docs.oracle.com.",
        ),
        (
            "Como otimizar custos?",
            "Cost optimization:\n1. Use Flexible shape\n2. Right-size bandwidth\n3. Reserved capacity\n4. Monitor usage\n\n[MUTABLE] Flexible: ~$0.007/Mbps/hour.",
        ),
    ],
}

# Migration AWS Compute
compute_qa = {
    "beginner": [
        (
            "Qual shape de Compute escolher para workloads pequenos?",
            "Shapes para workloads pequenos:\n- VM.Standard.E2.1.Micro: Always Free\n- VM.Standard.E2.1.Small: 1 OCPU, 8GB\n\n[CHECK DOCS] Limites em docs.oracle.com.",
        ),
        (
            "Como criar instância via OCI CLI?",
            'Crie instância:\n```bash\noci compute instance launch --image-id <IMAGE_OCID> --shape "VM.Standard.E4.Flex" --subnet-id <SUBNET_OCID>\n```',
        ),
        (
            "Qual a diferença entre VM e Bare Metal?",
            "VM: virtualizado, menor custo\nBare Metal: hardware dedicado, maior performance\n\n[MUTABLE] Bare Metal ~2x VM.",
        ),
        (
            "Como configurar SSH keys?",
            "Configure SSH key:\n```bash\noci compute instance launch ... --ssh-authorized-keys-file ~/.ssh/id_rsa.pub\n```",
        ),
        (
            "O que é Always Free eligible?",
            "Always Free:\n- VM.Standard.E2.1.Micro\n- 2 instâncias por conta\n- 8GB storage\n\n[CHECK DOCS] Limites em docs.oracle.com.",
        ),
        (
            "Como listar imagens disponíveis?",
            'Liste imagens:\n```bash\noci compute image list --compartment-id <OCID> --operating-system "Oracle Linux"\n```',
        ),
        (
            "Como fazer attach de volume?",
            "Attach volume:\n```bash\noci compute volume attachment attach --instance-id <INSTANCE_OCID> --volume-id <VOLUME_OCID>\n```",
        ),
    ],
    "intermediate": [
        (
            "Como migrar EC2 t3.small para OCI?",
            "Mapeamento EC2 → OCI:\n| EC2 | OCI |\n| t3.small | VM.Standard.E4.Flex |\n| m5.large | VM.Standard.E4.Flex (2 OCPUs) |\n\n[CHECK DOCS] Docs em docs.oracle.com.",
        ),
        (
            "Como migrar EBS para Block Volume?",
            "Migre EBS para Block Volume:\n1. Identifique EBS volumes\n2. Crie Block Volume\n3. Attach à instância\n4. Transfira dados\n\n[MUTABLE] $0.029/GB/mês.",
        ),
        (
            "Como converter user data para cloud-init?",
            "Converta user data para cloud-init:\n```bash\n#cloud-config\npackages:\n  - httpd\nruncmd:\n  - systemctl start httpd\n```",
        ),
        (
            "Como criar Instance Pool?",
            "Crie Instance Pool:\n```bash\noci compute instance-pool create --compartment-id <OCID> --instance-configuration-id <CONFIG_OCID> --size 3\n```",
        ),
        (
            "Como configurar autoscaling?",
            "Configure autoscaling:\n```bash\noci autoscaling configuration create --resource-type instance-pool --resource-id <POOL_OCID> --policy-details '{\"CPU_UTILIZATION\": 70}'\n```",
        ),
        (
            "Como migrar Security Groups para NSGs?",
            "Migre Security Groups para NSGs:\n1. Crie NSG na VCN\n2. Migrar regras\n3. Associate à subnet\n\n[MUTABLE] Custo: $0/NSG.",
        ),
        (
            "Como criar VCN com subnets?",
            'Crie VCN:\n```bash\noci network vcn create --cidr-block "10.0.0.0/16" --compartment-id <OCID>\n```',
        ),
    ],
    "advanced": [
        (
            "Como implementar zero-downtime migration?",
            "Zero-downtime:\n1. Blue-green deployment\n2. Weighted DNS\n3. Health check\n4. Progressive cutover\n5. Rollback ready\n\n[CHECK DOCS] Docs em docs.oracle.com.",
        ),
        (
            "Como configurar multi-region disaster recovery?",
            "Multi-region DR:\n1. Primary em região A\n2. Standby em região B\n3. Data Guard\n4. DNS failover\n\n[MUTABLE] Custo cross-region egress.",
        ),
        (
            "Como integrar com auto scaling para HA?",
            "HA com auto scaling:\n1. Instance Pool em múltiplos ADs\n2. Load Balancer integration\n3. Health checks\n4. Scale policies\n\n[CHECK DOCS] SLA 99.99%.",
        ),
        (
            "Como migrar Auto Scaling Groups para Instance Pools?",
            "Migre ASG para Instance Pool:\n1. Instance Configuration\n2. Instance Pool\n3. Autoscaling config\n4. Scaling policies\n\n[CHECK DOCS] Docs em docs.oracle.com.",
        ),
        (
            "Como implementar blue-green deployment?",
            "Blue-green:\n1. Deploy green environment\n2. Teste com tráfico\n3. Switch DNS\n4. Validate\n5. Cleanup old\n\n[MUTABLE] Custo adicional temporário.",
        ),
        (
            "Como otimizar custos com preemptible?",
            "Preemptible optimization:\n1. Use preemptible para batch\n2. Mixed instance types\n3. Implement checkpoint\n4. Handle interruption\n\n[MUTABLE] até 90% desconto.",
        ),
        (
            "Como configurar encrypted volumes?",
            "Encrypted volumes:\n1. Create Vault\n2. Generate key\n3. Enable encryption\n4. Attach to instance\n\n[CHECK DOCS] Key management em docs.",
        ),
    ],
}

# Migration AWS Database
database_qa = {
    "beginner": [
        (
            "Qual database OCI escolher para migração RDS?",
            "Opções de Database OCI:\n- Autonomous Transaction Processing\n- Autonomous Data Warehouse\n- Base de dados MySQL\n- PostgreSQL\n\n[CHECK DOCS] Comparação em docs.oracle.com.",
        ),
        (
            "Como criar Autonomous Database?",
            'Crie Autonomous Database:\n```bash\noci db autonomous-database create --compartment-id <OCID> --db-name "mydb" --db-workload "TP" --display-name "meu-db"\n```',
        ),
        (
            "O que é Autonomous Transaction Processing?",
            "ATP: transações OLTP\nADW: analytics\nAJ: JSON documents\n\n[CHECK DOCS] Workload types em docs.oracle.com.",
        ),
        (
            "Como conectar no database?",
            "Connection string em Console:\nDatabase → Autonomous → Connection Strings\n\nUse wallet para TLS.",
        ),
        (
            "Quais tipos de storage disponíveis?",
            "Storage options:\n- Auto-scaling: até 128TB\n- Provisioned: fixo\n\n[MUTABLE] $0.00056/OCPU/hour.",
        ),
        (
            "Como configurar backup automático?",
            "Configure backup:\n1. Autonomous Database → Backup\n2. Enable auto backup\n3. Set retention\n\n[CHECK DOCS] Retention: 1-90 dias.",
        ),
        (
            "O que é Always Free database?",
            "Always Free:\n- 2 Autónomas databases\n- 25GB storage\n- 1 OCPU\n\n[CHECK DOCS] Limites em docs.oracle.com.",
        ),
    ],
    "intermediate": [
        (
            "Como migrar RDS PostgreSQL para OCI?",
            "Migração RDS PostgreSQL:\n1. Export do RDS\n2. Create Autonomous\n3. Import via SQL\n4. Validate\n\n[CHECK DOCS] Tools em docs.oracle.com.",
        ),
        (
            "Como configurar Data Guard?",
            "Configure Data Guard:\n```bash\noci db data-guard-association create --autonomous-database-id <PRIMARY_OCID> --peer-autonomous-database-id <STANDBY_OCID>\n```",
        ),
        (
            "Como migrar com DMS?",
            "DMS migration:\n1. Create migration hub\n2. Configure source/target\n3. Migrate\n4. Validate\n\n[CHECK DOCS] Documentação em docs.oracle.com.",
        ),
        (
            "Como configurar encryption?",
            "Encryption:\n1. Use Vault\n2. Generate key\n3. Enable at rest\n\n[CHECK DOCS] Key management em docs.",
        ),
        (
            "Como criar connection string?",
            "Connection string:\n1. Console → Connect\n2. Download wallet\n3. Configure client\n\n[MUTABLE] Wallet: $0.",
        ),
        (
            "Como configurar monitoring?",
            "Configure monitoring:\n1. Monitoring → Metrics\n2. Create alarm\n3. Set threshold\n\n[CHECK DOCS] Metrics em docs.oracle.com.",
        ),
        (
            "Como migrar stored procedures?",
            "Stored procedures:\n- Migre manualmente\n- Use TRANSLATE function\n- Teste extensivamente\n\n[CHECK DOCS] PL/SQL em docs.oracle.com.",
        ),
    ],
    "advanced": [
        (
            "Como implementar zero-downtime migration?",
            "Zero-downtime migration:\n1. DMS with CDC\n2. Blue-green\n3. Validate\n4. Switch\n\n[CHECK DOCS] DMS em docs.oracle.com.",
        ),
        (
            "Como configurar multi-region DR?",
            "Multi-region DR:\n1. Primary region\n2. Standby region\n3. Data Guard\n4. DNS failover\n\n[MUTABLE] Custo cross-region.",
        ),
        (
            "Como migrar Aurora para Exadata?",
            "Migre Aurora para Exadata:\n1. Export data\n2. Import to Exadata\n3. Test performance\n4. Switch\n\n[CHECK DOCS] Exadata em docs.oracle.com.",
        ),
        (
            "Como configurar auto scaling?",
            "Auto scaling:\n1. Elastic pool\n2. Configure min/max\n3. Auto scaling policy\n\n[CHECK DOCS] Pools em docs.oracle.com.",
        ),
        (
            "Como implementar zero data loss?",
            "Zero data loss:\n1. Sync_mode\n2. Lag threshold\n3. Validate\n\n[CHECK DOCS] Data Guard em docs.oracle.com.",
        ),
        (
            "Como migrar para Autonomous JSON?",
            "Migre para Autonomous JSON:\n1. Export JSON\n2. Import to AJ\n3. Validate\n4. Switch\n\n[CHECK DOCS] AJ em docs.oracle.com.",
        ),
        (
            "Como configurar HA com Data Guard?",
            "HA config:\n1. Primary + Standby\n2. Enable Data Guard\n3. Configure protection mode\n4. Test failover\n\n[CHECK DOCS] Protection modes em docs.",
        ),
    ],
}

# Migration AWS Storage
storage_qa = {
    "beginner": [
        (
            "Como criar bucket no Object Storage?",
            'Crie bucket:\n```bash\noci os bucket create --compartment-id <OCID> --name "meu-bucket"\n```',
        ),
        (
            "Qual a diferença entre Standard e Archive?",
            "Storage tiers:\n- Standard: acesso frequente\n- Archive: longo prazo\n- Infrequent: pouco acesso\n\n[MUTABLE] Archive: ~$0.0006/GB.",
        ),
        (
            "Como fazer upload de arquivo?",
            'Upload arquivo:\n```bash\noci os object put --bucket-name <BUCKET> --file /path/to/file --object-name "nome"\n```',
        ),
        (
            "Como criar pre-authenticated URL?",
            "Pre-authenticated URL:\n```bash\noci os pre-authenticated-request create --bucket-name <BUCKET> --object-name <OBJ>\n```",
        ),
        (
            "O que é Object Storage tiering?",
            "Tiering automatic:\n- Configure lifecycle rules\n- Move para Archive após N dias\n\n[CHECK DOCS] Rules em docs.oracle.com.",
        ),
        (
            "Como listar objetos?",
            "Liste objetos:\n```bash\noci os object list --bucket-name <BUCKET>\n```",
        ),
        (
            "Como configurar retenção?",
            "Retention rules:\n- Define retenção\n- Impede delete\n\n[CHECK DOCS] WORM em docs.oracle.com.",
        ),
    ],
    "intermediate": [
        (
            "Como migrar dados do S3 para OCI?",
            "Migre S3 → OCI:\n1. Configure credenciais\n2. Use rclone\n3. Validate checksums\n\n[CHECK DOCS] Docs em docs.oracle.com.",
        ),
        (
            "Como usar rclone para migração?",
            "rclone config:\n```bash\n[oci]\ntype = s3\nprovider = OCI\naccess_key_id = <KEY>\nsecret_access_key = <SECRET>\nendpoint = https://<REGION>.objectstorage.oraclecloud.com\nlocation_constraint = <REGION>\n```",
        ),
        (
            "Como configurar lifecycle rules?",
            'Lifecycle rules:\n```bash\noci os bucket update --bucket-name <BUCKET> --lifecycle-policy \'[{"action": "MOVE_TO_ARCHIVE", "days": 30}]\'\n```',
        ),
        (
            "Como configurar versioning?",
            "Versioning:\n```bash\noci os bucket update --bucket-name <BUCKET> --versioning ENABLE\n```",
        ),
        (
            "Como migrar Glacier para Archive?",
            "Glacier → Archive:\n1. Restore do Glacier\n2. Move para OCI Archive\n3. Validate\n\n[MUTABLE] Archive ~85% mais barato.",
        ),
        (
            "Como configurar replication?",
            "Configure replication:\n1. Create target bucket\n2. Create policy\n3. Enable\n\n[CHECK DOCS] Custo egress.",
        ),
        (
            "Como configurar encryption?",
            "Encryption:\n- AES-256 default\n- Vault key option\n\n[CHECK DOCS] Key em docs.oracle.com.",
        ),
    ],
    "advanced": [
        (
            "Como implementar zero-downtime migration?",
            "Zero-downtime:\n1. Sync incremental\n2. Validate\n3. Cutover\n4. Verify\n\n[CHECK DOCS] rclone com --fast-check.",
        ),
        (
            "Como configurar cross-region replication?",
            "Cross-region replication:\n1. Create policy\n2. Configure target\n3. Enable\n4. Monitor\n\n[MUTABLE] Custo egress entre regiões.",
        ),
        (
            "Como validar integridade após migração?",
            "Validate integridade:\n```bash\nrclone check s3:bucket oci:bucket --checksum\n```",
        ),
        (
            "Como implementar disaster recovery?",
            "Disaster recovery:\n1. Replicate para secondary\n2. DNS failover\n3. Teste\n\n[CHECK DOCS] RTO/RPO em docs.",
        ),
        (
            "Como configurar event notifications?",
            "Events config:\n1. Create rule\n2. Attach to bucket\n3. Action: Functions\n\n[CHECK DOCS] Events em docs.oracle.com.",
        ),
        (
            "Como otimizar custos com tiering?",
            "Cost optimization:\n1. Analyze access patterns\n2. Configure lifecycle\n3. Archive cold data\n\n[MUTABLE] Archive: ~$0.0006/GB.",
        ),
        (
            "Como configurar WORM storage?",
            "WORM storage:\n1. Enable retention\n2. Configure período\n3. Impede sobrescrita\n\n[CHECK DOCS] Compliance em docs.",
        ),
    ],
}

if __name__ == "__main__":
    lb_examples = generate_examples("lb/load-balancer", lb_qa)
    compute_examples = generate_examples("migration/aws-compute", compute_qa)
    database_examples = generate_examples("migration/aws-database", database_qa)
    storage_examples = generate_examples("migration/aws-storage", storage_qa)

    output_dir = "/Users/otaviolemos/ml/olia-2-oci/data/curated"

    with open(f"{output_dir}/lb-load-balancer.jsonl", "w") as f:
        for ex in lb_examples:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")

    with open(f"{output_dir}/migration-aws-compute.jsonl", "w") as f:
        for ex in compute_examples:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")

    with open(f"{output_dir}/migration-aws-database.jsonl", "w") as f:
        for ex in database_examples:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")

    with open(f"{output_dir}/migration-aws-storage.jsonl", "w") as f:
        for ex in storage_examples:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")

    print("Generated:")
    print(f"- lb-load-balancer.jsonl: {len(lb_examples)} examples")
    print(f"- migration-aws-compute.jsonl: {len(compute_examples)} examples")
    print(f"- migration-aws-database.jsonl: {len(database_examples)} examples")
    print(f"- migration-aws-storage.jsonl: {len(storage_examples)} examples")

    for name, examples in [
        ("lb-load-balancer", lb_examples),
        ("migration-aws-compute", compute_examples),
        ("migration-aws-database", database_examples),
        ("migration-aws-storage", storage_examples),
    ]:
        d_count = {"beginner": 0, "intermediate": 0, "advanced": 0}
        for ex in examples:
            d_count[ex["metadata"]["difficulty"]] += 1
        print(
            f"{name}: beginner={d_count['beginner']}, intermediate={d_count['intermediate']}, advanced={d_count['advanced']}"
        )
