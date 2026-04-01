#!/usr/bin/env python3
"""
OCI Specialist LLM - Data Generator Completo
Gera 710 exemplos JSONL para 71 tópicos (10 exemplos por tópico)
"""

import json
from pathlib import Path

OUTPUT_DIR = Path("/Users/otaviolemos/ml/olia-2-oci/data/curated")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def create_example(system_prompt, user_question, assistant_answer, category, difficulty):
    """Cria um exemplo JSONL válido."""
    return {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_question},
            {"role": "assistant", "content": assistant_answer}
        ],
        "metadata": {
            "category": category,
            "difficulty": difficulty,
            "source": "generated"
        }
    }

def save_examples(examples, filename):
    """Salva exemplos em arquivo JSONL."""
    output_file = OUTPUT_DIR / filename
    with open(output_file, 'w', encoding='utf-8') as f:
        for example in examples:
            f.write(json.dumps(example, ensure_ascii=False) + '\n')
    return output_file, len(examples)

# ============================================================================
# COMPUTE - INSTANCES
# ============================================================================
def gen_compute_instances():
    category = "compute/instances"
    sp = "You are an OCI specialist with expertise in Compute instances. Provide technical guidance on instance creation, shape selection, SSH access, and lifecycle management."
    examples = []
    
    # Beginner (3)
    examples.append(create_example(sp, "Como criar uma instância no OCI?",
        "Para criar uma instância no OCI:\n\n1. No Console, vá para Compute → Instances\n2. Clique em 'Create Instance'\n3. Selecione o compartment desejado\n4. Escolha o shape (VM.Standard.E4.Flex para propósito geral)\n5. Configure a VCN e subnet\n6. Adicione chaves SSH\n7. Clique em 'Create'\n\nShapes recomendados:\n- VM.Standard.E4.Flex: AMD EPYC (custo-benefício)\n- VM.Standard.A1.Flex: ARM Ampere (econômico)\n- VM.Optimized3: memória otimizada\n\n[MUTABLE] Preços variam por região e shape.\n\nDocs: https://docs.oracle.com/en-us/iaas/Content/Compute/Concepts/computeoverview.htm", category, "beginner"))
    
    examples.append(create_example(sp, "Qual shape usar para aplicação web?",
        "Para aplicações web de propósito geral:\n\n**Recomendado:** VM.Standard.E4.Flex\n- CPU AMD EPYC de 3ª geração\n- Bom custo-benefício\n- Escalável de 1 a 64 OCPUs\n\n**Alternativas:**\n- VM.Standard.A1.Flex: ARM Ampere, até 80% mais econômico\n- VM.Optimized3: para cargas de memória intensiva\n\nPara produção, considere:\n- Múltiplas instâncias em diferentes ADs\n- Load Balancer na frente\n- Auto-scaling baseado em CPU", category, "beginner"))
    
    examples.append(create_example(sp, "Como conectar via SSH na instância?",
        "Para conectar via SSH:\n\n1. Gere par de chaves:\n```bash\nssh-keygen -t rsa -b 4096 -f ~/.ssh/oci_key\n```\n\n2. No Console, adicione a chave pública na criação\n\n3. Conecte-se:\n```bash\nssh -i ~/.ssh/oci_key opc@<ip-publico>\n```\n\n**Usuários padrão:**\n- 'opc': Oracle Linux\n- 'ubuntu': Ubuntu\n- 'centos': CentOS\n\nVerifique se a Security List permite porta 22.", category, "beginner"))
    
    # Intermediate (5)
    examples.append(create_example(sp, "Como gerenciar ciclo de vida de instâncias?",
        "Gerenciamento de ciclo de vida:\n\n**Start/Stop via CLI:**\n```bash\noci compute instance action --instance-id <ocid> --action START\noci compute instance action --instance-id <ocid> --action STOP\n```\n\n**Tipos de Stop:**\n- Soft Stop: shutdown gracioso (60s timeout)\n- Hard Stop: desliga imediatamente\n\n**Terminate:**\n- Remove permanentemente\n- Boot volume pode ser preservado\n\n**Best Practices:**\n- Use stop/start para economizar\n- Crie backup antes de terminate\n- Use instance pools para produção\n\n[MUTABLE] Instâncias paradas cobram apenas armazenamento.", category, "intermediate"))
    
    examples.append(create_example(sp, "Como escolher a região correta?",
        "Critérios para escolher região:\n\n**1. Latência:** Região mais próxima dos usuários\n\n**2. Disponibilidade de Shape:** Nem todos shapes disponíveis em todas regiões\n\n**3. Compliance:** Dados sensíveis podem exigir região específica\n\n**4. Custo:** Preços variam por região\n\n**5. Disaster Recovery:** Considere multi-região para DR\n\n**Regiões principais:**\n- us-ashburn-1: US East (maior capacidade)\n- us-phoenix-1: US West\n- eu-frankfurt-1: Europa\n- ap-tokyo-1: Ásia\n\nDocs: https://docs.oracle.com/en-us/iaas/Content/General/Concepts/regions.htm", category, "intermediate"))
    
    examples.append(create_example(sp, "Como resolver instância em PROVISIONING?",
        "Troubleshooting para PROVISIONING travado:\n\n**1. Verifique quotas:**\n```bash\noci iam limit-definition list\noci compute shape list --compartment-id <ocid>\n```\n\n**2. Verifique logs de auditoria no Console**\n\n**3. Ações:**\n- Aguarde até 10 minutos\n- Tente em outro Availability Domain\n- Reduza quantidade de instâncias\n- Verifique IPs disponíveis na VCN\n\n**4. Se persistir:**\n- Abra Service Request\n- Tente shape alternativo\n\n[CHECK DOCS] Limites variam por tenancy.", category, "intermediate"))
    
    examples.append(create_example(sp, "Como usar instance pools?",
        "Instance pools para escala:\n\n**1. Crie Instance Configuration:**\n```bash\noci compute instance-configuration create --compartment-id <ocid> --display-name web-config\n```\n\n**2. Crie Instance Pool:**\n```bash\noci compute instance-pool create --compartment-id <ocid> --instance-configuration-id <config-ocid> --size 3\n```\n\n**3. Configure Auto-scaling:**\n- Policy baseada em métricas\n- Min/Max instances\n\n**Vantagens:**\n- Deploy consistente\n- Scaling automático\n- Tolerância a falhas\n\nDocs: https://docs.oracle.com/en-us/iaas/Content/Compute/Concepts/computeoverview.htm", category, "intermediate"))
    
    examples.append(create_example(sp, "Como proteger instâncias com IAM?",
        "Proteção IAM para instâncias:\n\n**1. Policies:**\n```\nAllow group ComputeAdmins to manage instance-family in compartment Prod\nAllow group Developers to read instance-family in compartment Dev\n```\n\n**2. Dynamic Groups:**\n```\nALL {instance.compartment.id = '<compartment-ocid>'}\n```\n\n**3. Instance Principal:**\n- Permite instância acessar outros serviços OCI\n- Sem necessidade de config file\n\n**4. Tagging:**\n- Tags para controle de acesso\n- Ex: Environment=Prod, Team=DevOps\n\nDocs: https://docs.oracle.com/en-us/iaas/Content/Identity/Concepts/overview.htm", category, "intermediate"))
    
    # Advanced (2)
    examples.append(create_example(sp, "Como migrar instância on-premises?",
        "Migração lift-and-shift:\n\n**Opção 1: Oracle Cloud Mover**\n1. Instale agente na VM source\n2. Replicação contínua\n3. Cutover com mínimo downtime\n\n**Opção 2: Custom Image**\n1. Exporte VM como OVA/VMDK\n2. Upload para Object Storage\n3. Importe como Custom Image:\n```bash\noci compute image import --source-type OBJECT_STORAGE --source-uri <uri>\n```\n4. Crie instância da imagem\n\n**Pós-migração:**\n- Instale Oracle Cloud Agent\n- Configure monitoring\n\n**Riscos:** Drivers incompatíveis, licensing\n\nDocs: https://docs.oracle.com/en-us/iaas/Content/Migration/overview.htm", category, "advanced"))
    
    examples.append(create_example(sp, "Como implementar alta disponibilidade?",
        "HA para instâncias:\n\n**1. Multi-AD Deployment:** Distribua instâncias em 3 ADs\n\n**2. Load Balancer:** Health checks e failover automático\n\n**3. Auto-scaling:**\n- Scale up quando CPU > 70%\n- Scale down quando CPU < 30%\n- Minimum 2 instâncias por AD\n\n**4. Boot Volume Backup:** Backup diário automatizado\n\n**5. Instance Configuration:** Template versionado\n\n**Trade-offs:**\n- Multi-AD aumenta latência entre nós\n- Custo 2-3x maior\n- Mais complexo de gerenciar", category, "advanced"))
    
    return examples

# ============================================================================
# COMPUTE - SCALING
# ============================================================================
def gen_compute_scaling():
    category = "compute/scaling"
    sp = "You are an OCI specialist with expertise in Compute scaling. Provide technical guidance on instance pools, auto-scaling, and capacity planning."
    examples = []
    
    examples.append(create_example(sp, "Como configurar auto-scaling no OCI?",
        "Configuração de auto-scaling:\n\n**1. Crie Instance Pool primeiro**\n\n**2. Crie Auto-scaling Policy:**\n```bash\noci compute instance-pool create-auto-scaling-policy --instance-pool-id <ocid> --policy-type metric --metric-definition '{\"metricType\":\"CPU_UTILIZATION\",\"threshold\":70}'\n```\n\n**3. Configure thresholds:**\n- Scale up: CPU > 70% por 5 min\n- Scale down: CPU < 30% por 10 min\n\n**4. Defina limites:**\n- Min instances: 2\n- Max instances: 10\n\n[MUTABLE] Limites máximos variam por quota.", category, "beginner"))
    
    examples.append(create_example(sp, "Qual diferença entre instance pool e instance?",
        "Diferenças principais:\n\n**Instance (única):** VM individual, gerenciamento manual, sem auto-scaling\n\n**Instance Pool:** Múltiplas instâncias idênticas, gerenciamento centralizado, auto-scaling integrado, HA nativo\n\n**Quando usar Pool:** Aplicações stateless, tráfego variável, HA requerido", category, "beginner"))
    
    examples.append(create_example(sp, "Como fazer scaling manual de instância?",
        "Scaling manual (shape change):\n\n**Via Console:** Stop → Edit → Change Shape → Start\n\n**Via CLI:**\n```bash\noci compute instance action --instance-id <ocid> --action STOP\noci compute instance update --instance-id <ocid> --shape VM.Standard.E4.Flex\noci compute instance action --instance-id <ocid> --action START\n```\n\n**Importante:** Downtime necessário, boot volume compatível", category, "beginner"))
    
    examples.append(create_example(sp, "Como planejar capacidade para produção?",
        "Planejamento de capacidade:\n\n**1. Baseline:** Monitore 2-4 semanas\n\n**2. Headroom:** Adicione 30-50% buffer\n\n**3. Multi-AD:** Divida entre 3 ADs\n\n**4. Auto-scaling:** Min 50%, Max 150% do pico\n\n**Fórmula:** Instances = (Pico CPU / CPU por instância) * 1.5 buffer\n\n[MUTABLE] Limites de quota podem restringir.", category, "intermediate"))
    
    examples.append(create_example(sp, "Como integrar load balancer com auto-scaling?",
        "Integração LB + Auto-scaling:\n\n**1. Crie Load Balancer**\n\n**2. Configure Backend Set com health check HTTP /health**\n\n**3. Instance Pool atualiza LB automaticamente**\n\n**Benefícios:** Zero-downtime deployments, health checks automáticos\n\nDocs: https://docs.oracle.com/en-us/iaas/Content/LoadBalancing/Concepts/loadbalanceroverview.htm", category, "intermediate"))
    
    examples.append(create_example(sp, "O que é scheduled scaling?",
        "Scheduled Scaling (escalonamento agendado):\n\n**Use cases:** Picos horários conhecidos, Black Friday, processamento batch\n\n**Configuração:**\n```bash\noci compute instance-pool create-scheduled-policy --schedule \"0 8 * * 1-5\" --target-size 10\n```\n\n**Vantagens:** Previsibilidade, custo otimizado, capacidade garantida", category, "intermediate"))
    
    examples.append(create_example(sp, "Como monitorar auto-scaling?",
        "Monitoramento de auto-scaling:\n\n**1. Metrics:** CPU_UTILIZATION, Instance count\n\n**2. Alarms:**\n```bash\noci monitoring alarm create --metric-name CPU_UTILIZATION --threshold 80\n```\n\n**3. Dashboard:** Console → Monitoring\n\n**4. Notifications:** Integre com PagerDuty/Opsgenie\n\nDocs: https://docs.oracle.com/en-us/iaas/Content/Monitoring/overview.htm", category, "intermediate"))
    
    examples.append(create_example(sp, "Como lidar com warm-up time?",
        "Warm-up time em auto-scaling:\n\n**Problema:** Instâncias novas levam 2-5 min para boot\n\n**Soluções:**\n1. Custom Image com app pré-instalado\n2. User Data scripts\n3. Cooldown: 300s entre scaling events\n4. Minimum instances para capacidade base\n5. Pre-warm com scheduled scaling", category, "intermediate"))
    
    examples.append(create_example(sp, "Como otimizar custo com scaling?",
        "Otimização de custo:\n\n**1. ARM Ampere:** 80% economia\n\n**2. Aggressive scale-down:** Threshold 30% CPU\n\n**3. Scheduled reduction:** Noites 50%, fins de semana 25%\n\n**4. Spot instances:** Até 90% desconto\n\n**Exemplo:** Sem otimização: $1000/mês, Com scaling: $400/mês (60% economia)\n\n[MUTABLE] Preços variam por região.", category, "advanced"))
    
    examples.append(create_example(sp, "Como debugar scaling que não funciona?",
        "Debug de auto-scaling:\n\n**1. Verifique policy**\n\n**2. Cheque métricas no Monitoring**\n\n**3. Verifique quotas**\n\n**4. Audit logs: scaling events registrados?**\n\n**5. Health checks passando?**\n\n**Common issues:** Quota excedida, threshold muito alto, cooldown muito longo", category, "advanced"))
    
    return examples

# ============================================================================
# COMPUTE - CUSTOM IMAGES
# ============================================================================
def gen_compute_custom_images():
    category = "compute/custom-images"
    sp = "You are an OCI specialist with expertise in Compute custom images. Provide technical guidance on custom image creation, boot volumes, and instance templates."
    examples = []
    
    examples.append(create_example(sp, "Como criar custom image no OCI?",
        "Criando custom image:\n\n**Opção 1: De instância existente**\n```bash\noci compute image create --compartment-id <ocid> --instance-id <ocid> --launch-mode NATIVE\n```\n\n**Opção 2: Import de Object Storage**\n```bash\noci compute image import --source-type OBJECT_STORAGE --source-uri oci://bucket/path/image.vmdk\n```\n\n**Formatos:** QCOW2, VMDK, VDI, RAW\n\n**Launch modes:** NATIVE (performance), EMULATED (compatibilidade)\n\nDocs: https://docs.oracle.com/en-us/iaas/Content/Compute/Concepts/computeoverview.htm", category, "beginner"))
    
    examples.append(create_example(sp, "Como exportar custom image?",
        "Exportando custom image:\n\n```bash\noci compute image export --image-id <ocid> --destination-type OBJECT_STORAGE --export-image-type QCOW2\n```\n\n**Formatos:** QCOW2, VMDK, RAW\n\n**Use cases:** Backup offline, migração on-premises, DR\n\n[MUTABLE] Custos de Object Storage aplicam-se.", category, "beginner"))
    
    examples.append(create_example(sp, "Como compartilhar imagem entre compartments?",
        "Compartilhando imagens:\n\n**1. Image Sharing via Console ou CLI**\n\n**2. Policy necessária:**\n```\nAllow group Developers to use images in compartment Dev\n```\n\n**3. Ao criar instância:** Selecione \"Shared Images\"\n\n**Limitações:** Mesmo realm, launch mode compatível", category, "beginner"))
    
    examples.append(create_example(sp, "Como gerenciar versões de imagem?",
        "Versionamento de imagens:\n\n**Naming convention:** app-web-v1.0.0-2024-01\n\n**Lifecycle:** Dev: diárias, Staging: semanais, Production: mensais\n\n**Cleanup:** Manter últimas 3 versões", category, "intermediate"))
    
    examples.append(create_example(sp, "Como preparar OS para custom image?",
        "Preparando OS:\n\n**Oracle Linux:**\n```bash\nyum install -y cloud-init\nrm -rf /var/log/*\nrm -f /etc/ssh/ssh_host_*\n```\n\n**Ubuntu:** apt install -y cloud-init && cloud-init clean\n\n**Windows:** Sysprep /generalize\n\n**Importante:** Não deixe dados sensíveis", category, "intermediate"))
    
    examples.append(create_example(sp, "Como usar instance configuration?",
        "Instance Configuration (template):\n\n```bash\noci compute instance-configuration create --compartment-id <ocid> --instance-details '{\"sourceDetails\":{\"sourceType\":\"image\"}}'\n```\n\n**Use com Instance Pool**\n\n**Vantagens:** Consistência, versionamento, deploy rápido", category, "intermediate"))
    
    examples.append(create_example(sp, "Como migrar VMWare para OCI?",
        "Migração VMware:\n\n**Opção 1: Oracle VM Migration** - Conecte vCenter ao OCI, replicação contínua\n\n**Opção 2: Manual:**\n1. Exporte como OVF/OVA\n2. Converta para QCOW2\n3. Upload e import\n\nDocs: https://docs.oracle.com/en-us/iaas/Content/cloud-migration/home.htm", category, "intermediate"))
    
    examples.append(create_example(sp, "Como testar custom image?",
        "Testando custom image:\n\n**1. Crie instância de teste**\n\n**2. Checklist:** SSH conecta, Cloud-init executou, Network funcional, Apps rodando\n\n**3. Valide em múltiplos shapes:** AMD, ARM, Intel", category, "intermediate"))
    
    examples.append(create_example(sp, "Como otimizar tamanho de imagem?",
        "Otimização de imagem:\n\n**Limpeza:**\n```bash\nyum clean all && rm -rf /tmp/*\ndd if=/dev/zero of=/EMPTY && rm /EMPTY\n```\n\n**Use camadas:** Imagem base + app\n\n**Economia:** 50-70% redução\n\n[MUTABLE] Custos de armazenamento variam.", category, "advanced"))
    
    examples.append(create_example(sp, "Como automatizar criação de imagens?",
        "Automação com pipelines:\n\n**Packer + CI/CD:**\n```yaml\nstages:\n  - build: packer build image.json\n  - test: ./test-image.sh\n  - publish: oci compute image create\n```\n\n**Schedule:** Nightly, monthly patches", category, "advanced"))
    
    return examples

# ============================================================================
# STORAGE - BLOCK
# ============================================================================
def gen_storage_block():
    category = "storage/block"
    sp = "You are an OCI specialist with expertise in Block Volume. Provide technical guidance on block storage creation, attachment, performance tiers, and backups."
    examples = []
    
    examples.append(create_example(sp, "Como criar Block Volume no OCI?",
        "Criando Block Volume:\n\n**Via Console:**\n1. Block Storage → Volumes → Create Volume\n2. Selecione compartment e AD\n3. Defina tamanho (50GB - 32TB)\n4. Selecione performance (VP ou BP)\n\n**Via CLI:**\n```bash\noci bv volume create --compartment-id <ocid> --size-in-gbs 100 --vpus-per-gb 10\n```\n\n**Performance tiers:** Balanced (10 VPU/GB), Higher (até 120 VPU/GB)\n\n[MUTABLE] Preços por GB e VPU variam.\n\nDocs: https://docs.oracle.com/en-us/iaas/Content/Storage/Concepts/storageoverview.htm", category, "beginner"))
    
    examples.append(create_example(sp, "Como attach volume em instância?",
        "Attach de Block Volume:\n\n**Via Console:** Volume Details → Attach → Selecione instância\n\n**Via CLI:**\n```bash\noci compute volume-attachment attach --instance-id <ocid> --volume-id <ocid> --type iscsi\n```\n\n**Dentro da instância (iSCSI):**\n```bash\niscsiadm -m discovery -t st -p <ip>:3260\niscsiadm -m node -L\nlsblk\nmkfs.ext4 /dev/sdb\nmount /dev/sdb /data\n```\n\n**Paravirtualized:** Mais simples, menos performance", category, "beginner"))
    
    examples.append(create_example(sp, "Como criar backup de volume?",
        "Backup de Block Volume:\n\n**Backup manual:**\n```bash\noci bv volume-backup create --volume-id <ocid> --type FULL\n```\n\n**Backup policy (automático):**\n```bash\noci bv volume-backup-policy create --schedule \"0 2 * * *\" --retention 7\n```\n\n**Tipos:** FULL (completo), INCREMENTAL (apenas mudanças)\n\n**Restore:**\n```bash\noci bv volume create --source-details '{\"type\":\"volumeBackup\",\"id\":\"<backup-ocid>\"}'\n```\n\n**Best practices:** Backup diário, retenção 7 diários + 4 semanais", category, "beginner"))
    
    examples.append(create_example(sp, "Como clonar volume?",
        "Clonando Block Volume:\n\n**Clone de volume:**\n```bash\noci bv volume create --source-details '{\"type\":\"volume\",\"id\":\"<source-ocid>\"}'\n```\n\n**Clone de backup:**\n```bash\noci bv volume create --source-details '{\"type\":\"volumeBackup\",\"id\":\"<backup-ocid>\"}'\n```\n\n**Características:** Instantâneo, mesmo tamanho, mesmo AD\n\n**Use cases:** Dev/Test, migration entre ADs, DR", category, "intermediate"))
    
    examples.append(create_example(sp, "Como expandir volume?",
        "Expandindo Block Volume:\n\n**1. Expanda no OCI:**\n```bash\noci bv volume update --volume-id <ocid> --size-in-gbs 200\n```\n\n**2. Dentro da instância:**\n```bash\ngrowpart /dev/sdb 1\nresize2fs /dev/sdb1  # ext4\nxfs_growfs /data     # xfs\n```\n\n**Limites:** Mínimo: tamanho atual, Máximo: 32TB\n\n**Importante:** Backup antes de expandir", category, "intermediate"))
    
    examples.append(create_example(sp, "Como otimizar performance de volume?",
        "Otimização de performance:\n\n**1. Ajuste VPU/GB:**\n```bash\noci bv volume update --volume-id <ocid> --vpus-per-gb 100\n```\n\n**2. Use paravirtualized attachment**\n\n**3. Stripe múltiplos volumes (RAID 0)**\n\n**4. Ajuste I/O scheduler:**\n```bash\necho deadline > /sys/block/sdb/queue/scheduler\n```\n\n**Trade-offs:** Mais VPU = mais custo", category, "intermediate"))
    
    examples.append(create_example(sp, "Como mover volume entre ADs?",
        "Mover volume entre ADs:\n\n**Método 1: Backup/Restore**\n```bash\noci bv volume-backup create --volume-id <source-ocid>\noci bv volume create --source-details '{\"type\":\"volumeBackup\",\"id\":\"<backup-ocid>\"}' --availability-domain <target-AD>\n```\n\n**Método 2: Clone cross-AD**\n\n**Passos:** Stop instância → Detach → Criar backup/clone → Attach no novo AD\n\n**Downtime:** Necessário\n\n**Alternativa:** File Storage (multi-AD)", category, "intermediate"))
    
    examples.append(create_example(sp, "Como monitorar Block Volume?",
        "Monitoramento de Block Volume:\n\n**1. Metrics:** ReadOps, WriteOps, ReadLatency, WriteLatency, QueueDepth\n\n**2. Console:** Block Storage → Volumes → Metrics\n\n**3. CLI:**\n```bash\noci monitoring metrics-data query --namespace oci_blockstorage --resource-id <volume-ocid>\n```\n\n**4. Alarms:**\n```bash\noci monitoring alarm create --metric-name WriteLatency --threshold 100\n```\n\n**Thresholds:** Latency > 50ms (warning)", category, "intermediate"))
    
    examples.append(create_example(sp, "Como proteger Block Volume?",
        "Proteção de Block Volume:\n\n**1. Encryption:** Automática (AES-256) ou customer-managed keys\n\n**2. Policies:**\n```\nAllow group StorageAdmins to manage volume-family in compartment Prod\n```\n\n**3. Backup policies:** Automático diário\n\n**4. Access control:** Security Lists (iSCSI porta 3260)\n\n**5. Audit:** Logs de operações", category, "advanced"))
    
    examples.append(create_example(sp, "Como resolver volume não attach?",
        "Troubleshooting volume attach:\n\n**1. Verifique status:**\n```bash\noci compute volume-attachment list --instance-id <ocid>\n```\n\n**2. Common issues:**\n- Volume em uso (detach primeiro)\n- AD incompatível (devem estar no mesmo AD)\n- Quota excedida\n- Security List (porta 3260)\n\n**3. Debug na instância:**\n```bash\ncat /etc/iscsi/initiatorname.iscsi\niscsiadm -m discovery -t st -p <target-ip>:3260\n```\n\n**4. Re-attach:** Detach → Attach", category, "advanced"))
    
    return examples

# ============================================================================
# STORAGE - OBJECT
# ============================================================================
def gen_storage_object():
    category = "storage/object"
    sp = "You are an OCI specialist with expertise in Object Storage. Provide technical guidance on buckets, pre-authenticated requests, lifecycle policies, and versioning."
    examples = []
    
    examples.append(create_example(sp, "Como criar bucket no Object Storage?",
        "Criando bucket:\n\n**Via Console:**\n1. Object Storage → Buckets → Create Bucket\n2. Nome (único globalmente)\n3. Compartment\n4. Storage tier: Standard ou Infrequent Access\n\n**Via CLI:**\n```bash\noci os bucket create --namespace <namespace> --compartment-id <ocid> --name my-bucket\n```\n\n**Tiers:** Standard (acesso frequente), IA (acesso < 1x/mês, mais barato)\n\n**Naming:** 3-63 caracteres, lowercase, números, hífen\n\n[MUTABLE] Preços variam por tier e região.\n\nDocs: https://docs.oracle.com/en-us/iaas/Content/Storage/Concepts/storageoverview.htm", category, "beginner"))
    
    examples.append(create_example(sp, "Como upload de arquivos?",
        "Upload para Object Storage:\n\n**Via Console:** Bucket → Upload → Drag & drop\n\n**Via CLI:**\n```bash\noci os object put --bucket-name my-bucket --name file.txt --file file.txt\n```\n\n**Upload grande (multipart):**\n```bash\noci os object put --bucket-name my-bucket --name large.zip --file large.zip --parallel-upload-count 10\n```\n\n**Limites:** Single: até 5GB, Multipart: até 50TB\n\n**Python SDK:**\n```python\nclient.put_object('namespace', 'bucket', 'key', open('file.txt','rb'))\n```", category, "beginner"))
    
    examples.append(create_example(sp, "Como criar Pre-Authenticated Request (PAR)?",
        "Criando PAR:\n\n**Via Console:** Bucket → Pre-Authenticated Requests → Create\n\n**Via CLI:**\n```bash\noci os preauth-request create --bucket-name my-bucket --access-type ObjectRead --time-expires 2024-12-31T23:59:59Z\n```\n\n**Tipos de acesso:** ObjectRead, ObjectWrite, Any\n\n**Use cases:** Download público, upload sem credenciais, integração externa\n\n**Security:** Defina expiration curto, revogue quando não usar", category, "beginner"))
    
    examples.append(create_example(sp, "Como configurar lifecycle policy?",
        "Lifecycle policy:\n\n**Via Console:** Bucket → Lifecycle Rules → Create Rule\n\n**Via CLI:**\n```bash\noci os bucket put-lifecycle-policy --bucket-name my-bucket --rules '[{\"name\":\"archive-old\",\"timeAmount\":30,\"timeUnit\":\"DAYS\",\"action\":\"ARCHIVE\",\"filter\":{\"prefix\":\"logs/\"}}]'\n```\n\n**Ações:** ARCHIVE (move para Archive tier), DELETE (remove)\n\n**Exemplo:** Delete temp após 7 dias, Archive logs após 30 dias\n\n**Economia:** Archive até 80% mais barato", category, "intermediate"))
    
    examples.append(create_example(sp, "Como habilitar versioning?",
        "Versionamento de objetos:\n\n**Habilitar:**\n```bash\noci os bucket update --bucket-name my-bucket --versioning ENABLED\n```\n\n**Listar versões:**\n```bash\noci os object list --bucket-name my-bucket --fields versionId\n```\n\n**Download versão específica:**\n```bash\noci os object get --name file.txt --version-id <version-id>\n```\n\n**Use cases:** Recuperação acidental, audit trail, rollback\n\n**Custos:** Paga por todas versões armazenadas", category, "intermediate"))
    
    examples.append(create_example(sp, "Como replicar buckets entre regiões?",
        "Replicação cross-region:\n\n**Configurar:**\n```bash\noci os bucket put-replication-policy --bucket-name my-bucket --destination-bucket-name replica --destination-region us-phoenix-1\n```\n\n**Tipos:** One-way, Two-way\n\n**Requisitos:**\n- Buckets em regiões diferentes\n- Versioning habilitado\n- Mesmo namespace\n\n**Use cases:** DR, compliance, baixa latência global", category, "intermediate"))
    
    examples.append(create_example(sp, "Como usar Object Storage para backup?",
        "Object Storage para backup:\n\n**1. Crie bucket dedicado**\n\n**2. Configure lifecycle para Archive**\n\n**3. Upload automatizado:**\n```bash\nrsync -av /data/ /mnt/oci_backup/\noci os object bulk-upload --bucket-name backup --src-dir /mnt/oci_backup/\n```\n\n**4. Enable versioning para proteção**\n\n**Vantagens:** Durabilidade 99.999999999%, custo baixo, escalável\n\n**Best practice:** 3-2-1 rule (3 cópias, 2 mídias, 1 offsite)", category, "intermediate"))
    
    examples.append(create_example(sp, "Como otimizar custos no Object Storage?",
        "Otimização de custos:\n\n**1. Use tiers corretamente:**\n- Standard: acesso frequente\n- IA: acesso < 1x/mês\n- Archive: raramente acessado\n\n**2. Lifecycle policies:** Archive automático após 30-90 dias\n\n**3. Compression:** Reduz tamanho antes do upload\n\n**4. Deduplication:** Evite dados duplicados\n\n**5. Delete objects não utilizados**\n\n**Economia típica:** 50-70% com tiering correto\n\n[MUTABLE] Preços variam por região.", category, "intermediate"))
    
    examples.append(create_example(sp, "Como proteger dados no Object Storage?",
        "Proteção de dados:\n\n**1. Encryption:** Automática (AES-256) ou customer-managed keys (Vault)\n\n**2. Policies:**\n```\nAllow group StorageAdmins to manage object-family in compartment Prod\n```\n\n**3. Versioning:** Proteção contra delete acidental\n\n**4. Retention rules:** Imutabilidade por período\n\n**5. Private endpoint:** Acesso sem internet\n\n**6. Audit logs:** Todas operações registradas", category, "advanced"))
    
    examples.append(create_example(sp, "Como migrar S3 para Object Storage?",
        "Migração S3 → Object Storage:\n\n**Opção 1: OCI CLI**\n```bash\naws s3 cp s3://source-bucket . --recursive\noci os object bulk-upload --bucket-name dest-bucket --src-dir .\n```\n\n**Opção 2: rclone**\n```bash\nrclone copy s3:source-bucket oci:dest-bucket\n```\n\n**Opção 3: OCI Data Transfer**\n- Appliance físico para TB/PB\n- Transferência offline segura\n\n**Pós-migração:** Valide checksums, atualize aplicações\n\nDocs: https://docs.oracle.com/en-us/iaas/Content/Migration/overview.htm", category, "advanced"))
    
    return examples

# ============================================================================
# STORAGE - FILE
# ============================================================================
def gen_storage_file():
    category = "storage/file"
    sp = "You are an OCI specialist with expertise in File Storage. Provide technical guidance on NFS file systems, mount targets, and export options."
    examples = []
    
    examples.append(create_example(sp, "Como criar File Storage no OCI?",
        "Criando File Storage:\n\n**Via Console:**\n1. File Storage → File Systems → Create File System\n2. Selecione compartment e AD\n3. Escolha VCN e subnet\n4. Create\n\n**Via CLI:**\n```bash\noci file-storage file-system create --compartment-id <ocid> --availability-domain <AD>\n```\n\n**Mount target:** Necessário para acesso NFS\n\n**Performance:** Escalável, até GB/s de throughput\n\n[MUTABLE] Preços por GB armazenado.\n\nDocs: https://docs.oracle.com/en-us/iaas/Content/Storage/Concepts/storageoverview.htm", category, "beginner"))
    
    examples.append(create_example(sp, "Como montar File Storage em instância?",
        "Montando File Storage:\n\n**1. Crie mount target no Console**\n\n**2. Na instância:**\n```bash\n# Instalar NFS client\nyum install -y nfs-utils\n\n# Criar diretório\nmkdir /mnt/oci-fs\n\n# Mount\nmount <mount-target-ip>:/<export-path> /mnt/oci-fs\n\n# Persistir no fstab\necho \"<ip>:/<path> /mnt/oci-fs nfs defaults 0 0\" >> /etc/fstab\n```\n\n**Security List:** Permita NFS (porta 2049)", category, "beginner"))
    
    examples.append(create_example(sp, "Como configurar export options?",
        "Export options (NFS):\n\n**Via Console:** Mount Target → Export Options → Add\n\n**Via CLI:**\n```bash\noci file-storage export create --file-system-id <ocid> --source \"0.0.0.0/0\" --access READ_WRITE\n```\n\n**Tipos de acesso:**\n- READ_WRITE: leitura e escrita\n- READ_ONLY: apenas leitura\n- ROOT_ONLY: root tem acesso\n\n**Security:** Restrinja por CIDR, use export options para controle", category, "beginner"))
    
    examples.append(create_example(sp, "Como fazer backup do File Storage?",
        "Backup de File Storage:\n\n**Snapshot manual:**\n```bash\noci file-storage snapshot create --file-system-id <ocid> --name backup-2024-01\n```\n\n**Snapshot policy (automático):**\n```bash\noci file-storage snapshot-policy create --file-system-id <ocid> --schedule \"0 2 * * *\"\n```\n\n**Restore:**\n```bash\noci file-storage snapshot restore --snapshot-id <ocid>\n```\n\n**Best practices:** Snapshot diário, retenção configurável", category, "intermediate"))
    
    examples.append(create_example(sp, "Como compartilhar File Storage entre múltiplas instâncias?",
        "Compartilhamento de File Storage:\n\n**1. Crie file system e mount target**\n\n**2. Configure export options para múltiplos CIDRs**\n\n**3. Monte em todas instâncias:**\n```bash\nmount <ip>:/<path> /mnt/shared\n```\n\n**4. Controle de acesso:**\n- NFS export options\n- POSIX permissions (chmod/chown)\n\n**Use cases:** Shared home directories, application data, content management", category, "intermediate"))
    
    examples.append(create_example(sp, "Como otimizar performance do File Storage?",
        "Otimização de performance:\n\n**1. Use múltiplos mount points** para paralelismo\n\n**2. Ajuste mount options:**\n```bash\nmount -o rsize=1048576,wsize=1048576,nfsvers=4.1\n```\n\n**3. Localize perto das instâncias** (mesmo AD quando possível)\n\n**4. Monitor throughput:**\n```bash\niostat -x 1\n```\n\n**5. Evite muitos arquivos pequenos**\n\n**Limites:** [CHECK DOCS] Performance varia por região", category, "intermediate"))
    
    examples.append(create_example(sp, "Como mover File Storage entre ADs?",
        "Mover File Storage entre ADs:\n\n**File Storage é específico do AD**\n\n**Para mover:**\n1. Crie novo file system no AD destino\n2. Copie dados:\n```bash\nrsync -av /mnt/source/ /mnt/dest/\n```\n3. Atualize mounts nas instâncias\n4. Delete antigo\n\n**Alternativa:** Use um file system por AD e replique dados\n\n**Downtime:** Necessário durante migração", category, "intermediate"))
    
    examples.append(create_example(sp, "Como monitorar File Storage?",
        "Monitoramento de File Storage:\n\n**1. Metrics:**\n- ReadBytes, WriteBytes\n- ReadOps, WriteOps\n- StorageUtilization\n\n**2. Console:** File Storage → Metrics\n\n**3. CLI:**\n```bash\noci monitoring metrics-data query --namespace oci_file_storage\n```\n\n**4. Alarms:**\n```bash\noci monitoring alarm create --metric-name StorageUtilization --threshold 80\n```\n\n**Thresholds:** Utilização > 80% (warning)", category, "intermediate"))
    
    examples.append(create_example(sp, "Como proteger File Storage?",
        "Proteção de File Storage:\n\n**1. Encryption:** Automática em repouso e trânsito\n\n**2. Network security:**\n- Security Lists (porta 2049)\n- NSGs para controle granular\n- Private endpoints\n\n**3. Export options:** Restrinja acesso por CIDR\n\n**4. Snapshots:** Proteção contra delete acidental\n\n**5. Policies IAM:** Controle de acesso\n\n**6. Audit:** Logs de operações", category, "advanced"))
    
    examples.append(create_example(sp, "Como usar File Storage para home directories?",
        "File Storage para home directories:\n\n**1. Crie file system dedicado**\n\n**2. Monte em todas instâncias:**\n```bash\nmount <ip>:/homes /home\n```\n\n**3. Configure LDAP/AD para autenticação centralizada**\n\n**4. Permissions:**\n```bash\nchmod 700 /home/username\nchown username:username /home/username\n```\n\n**Vantagens:** Dados persistentes, compartilhamento fácil, backup centralizado\n\n**Use cases:** Dev environments, HPC, VDI", category, "advanced"))
    
    return examples

# ============================================================================
# Main execution - gera todas as categorias
# ============================================================================

if __name__ == "__main__":
    generators = {
        "compute-instances": gen_compute_instances,
        "compute-scaling": gen_compute_scaling,
        "compute-custom-images": gen_compute_custom_images,
        "storage-block": gen_storage_block,
        "storage-object": gen_storage_object,
        "storage-file": gen_storage_file,
    }
    
    for name, generator in generators.items():
        examples = generator()
        filename = f"{name}.jsonl"
        output_file, count = save_examples(examples, filename)
        print(f"Gerado: {output_file} ({count} exemplos)")
