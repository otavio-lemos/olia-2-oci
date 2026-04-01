#!/usr/bin/env python3
"""
Generate all 56 remaining JSONL files for OCI Specialist LLM dataset.
Batch 1: database-exadata, container-instances, serverless-functions, serverless-api-gateway
"""

import json
import os

OUTPUT_DIR = "/Users/otaviolemos/ml/olia-2-oci/data/curated"

def create_example(category, cat_path, difficulty, question, answer, system_prompt):
    """Create a single JSONL example."""
    return {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question},
            {"role": "assistant", "content": answer}
        ],
        "metadata": {
            "category": cat_path,
            "difficulty": difficulty,
            "source": "generated"
        }
    }

def write_jsonl(filename, examples):
    """Write examples to JSONL file."""
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        for example in examples:
            f.write(json.dumps(example, ensure_ascii=False) + '\n')
    print(f"Generated: {filepath} ({len(examples)} examples)")

# ============ DATABASE EXADATA ============
def generate_database_exadata():
    examples = []
    system = "You are an OCI specialist with expertise in Exadata Cloud Service. Provide technical guidance on Exadata infrastructure, DB systems, patching, and maintenance."
    cat = "database/exadata"
    
    # Beginner (3)
    examples.append(create_example("database-exadata", cat, "beginner",
        "O que é Exadata Cloud Service?",
        "Exadata Cloud Service é a infraestrutura de banco de dados de alta performance da Oracle na nuvem.\n\n**Características principais:**\n- Hardware Exadata dedicado\n- Smart Scan para aceleração de queries\n- Storage cells com flash\n- Rede RDMA de baixa latência\n\n**Tipos de deployment:**\n- Exadata Cloud Service (dedicado na OCI)\n- Exadata Cloud@Customer (no seu datacenter)\n- Autonomous Database on Exadata (compartilhado)\n\n**Casos de uso:**\n- Data warehouses grandes\n- OLTP de alta transação\n- Consolidação de databases\n\n[MUTABLE] Preços variam por configuração e região.\n\nDocs: https://docs.oracle.com/en-us/iaas/Content/Database/Concepts/databaseoverview.htm", system))
    
    examples.append(create_example("database-exadata", cat, "beginner",
        "Como provisionar um DB system no Exadata?",
        "Provisionando DB system no Exadata:\n\n1. Console → Oracle Database → Exadata\n2. Selecione Exadata Infrastructure\n3. 'Create VM Cluster'\n4. Configure:\n   - VM Cluster name\n   - Shape (ex: Exadata.X9M)\n   - Número de nós\n   - Storage allocation\n5. Crie o DB System:\n   - Database name\n   - Edition (Enterprise/Standard)\n   - Admin credentials\n6. Review e Create\n\n**Pré-requisitos:**\n- VCN com subnet\n- DHCP options configurado\n- Security lists permitindo portas DB\n\n[CHECK DOCS] Disponibilidade de shapes varia por região.", system))
    
    examples.append(create_example("database-exadata", cat, "beginner",
        "Quais shapes de Exadata estão disponíveis?",
        "Shapes Exadata disponíveis (exemplos):\n\n**X9M (3ª geração):**\n- Exadata.X9M-2: 2 nós, 56 OCPUs total\n- Exadata.X9M-4: 4 nós, 112 OCPUs total\n- Exadata.X9M-8: 8 nós, 224 OCPUs total\n\n**X8M:**\n- Exadata.X8M-2: 2 nós\n- Exadata.X8M-8: 8 nós\n\n**Características X9M:**\n- Intel Xeon de 3ª geração\n- 3TB memory por nó\n- 100Gb RDMA network\n- Persistent memory (PMEM)\n\n**Storage:**\n- High capacity: mais espaço\n- High performance: mais IOPS\n\n[CHECK DOCS] Disponibilidade e preços variam por região.", system))
    
    # Intermediate (5)
    examples.append(create_example("database-exadata", cat, "intermediate",
        "Como funciona Smart Scan no Exadata?",
        "Smart Scan é o recurso de aceleração do Exadata:\n\n**Como funciona:**\n1. Query é enviada para storage cells\n2. Storage filtra dados antes de enviar\n3. Só dados relevantes vão para database server\n4. Reduz I/O e network traffic significativamente\n\n**Benefícios:**\n- Redução de 10-50x em I/O\n- Menos CPU no database server\n- Queries full scan mais rápidas\n\n**Requisitos para Smart Scan:**\n- Direct path read\n- Full table/index scan\n- Storage Indexes compatíveis\n\n**Exemplo:**\n```sql\n-- Smart Scan ativado para:\nSELECT * FROM sales WHERE amount > 1000;\n-- Storage filtra antes de enviar\n```\n\n**Monitoramento:**\n```sql\nSELECT name, value FROM v$sysstat \nWHERE name LIKE '%cell physical IO%';\n```", system))
    
    examples.append(create_example("database-exadata", cat, "intermediate",
        "Como fazer patching no Exadata?",
        "Patching do Exadata Cloud Service:\n\n**Via Console:**\n1. Exadata Infrastructure → Patching\n2. 'Schedule Patching'\n3. Selecione patches disponíveis\n4. Agende janela de manutenção\n5. Execute\n\n**Via CLI:**\n```bash\noci db exadata-infrastructure update \\\n  --exadata-infrastructure-id <ocid> \\\n  --is-updated true\n```\n\n**Tipos de patch:**\n- Database patch (RU/RUR - Quarterly)\n- Infrastructure patch (firmware)\n- Grid Infrastructure patch\n\n**Janela típica:** 2-4 horas\n**Impacto:** Rolling update (sem downtime total do cluster)\n\n**Best Practices:**\n- Teste em ambiente não-prod primeiro\n- Agende fora do horário comercial\n- Tenha backup recente\n\n[CHECK DOCS] Verifique release notes antes de aplicar.", system))
    
    examples.append(create_example("database-exadata", cat, "intermediate",
        "Como monitorar performance do Exadata?",
        "Monitoramento de performance do Exadata:\n\n**Console:**\n- Exadata Infrastructure → Metrics\n- VM Cluster → Performance Hub\n- Storage cells → I/O stats\n\n**Métricas chave:**\n- Cell I/O latency\n- Smart Scan efficiency\n- RDMA network throughput\n- Flash cache hit ratio\n- CPU utilization por nó\n\n**SQL de monitoramento:**\n```sql\nSELECT metric_name, metric_value \nFROM v$cellmetric \nWHERE metric_name LIKE '%SMART%';\n\n-- Flash cache\nSELECT name, value FROM v$sysstat \nWHERE name LIKE '%flash%';\n```\n\n**Alertas:**\n- Configure thresholds no Console\n- Integre com OCI Monitoring\n- Notificações via Email/Slack\n\n**Dashboard:** Performance Hub mostra wait events, SQL mais lentos, etc.", system))
    
    examples.append(create_example("database-exadata", cat, "intermediate",
        "Como configurar backup no Exadata?",
        "Configuração de backup no Exadata:\n\n**Recovery Appliance (ZDLA):**\n1. Provisione ZDLA virtual machine\n2. Configure network para DB system\n3. RMAN registra no ZDLA:\n```sql\nCONFIGURE CONTROLFILE AUTOBACKUP ON;\nCONFIGURE BACKUP OPTIMIZATION ON;\n```\n\n**Object Storage:**\n```sql\n-- Backup direto para Object Storage\nBACKUP DATABASE TO 'oci://bucket@namespace/db_backup';\n```\n\n**Via Console:**\n- Database → Backup → Create Backup\n- Automático: configure Backup Schedule\n\n**Best Practice:**\n- Backup diário incremental\n- Full semanal\n- Retenção de 30-60 dias\n- Teste restore periodicamente\n\n[MUTABLE] Storage de backup tem custo adicional.", system))
    
    examples.append(create_example("database-exadata", cat, "intermediate",
        "Como escalar um VM Cluster?",
        "Scaling de VM Cluster no Exadata:\n\n**Scale Up (mais recursos por nó):**\n1. Console → VM Cluster → Scale\n2. Selecione novo shape\n3. Apply (requer restart do nó)\n\n**Scale Out (mais nós):**\n1. VM Cluster → Add Node\n2. Selecione quantidade\n3. Configure network\n4. Add ao cluster\n\n**Considerações:**\n- Scale Out: rolling (sem downtime total)\n- Scale Up: requer restart do nó\n- Storage escala separadamente\n\n**Via CLI:**\n```bash\noci db vm-cluster add-node \\\n  --vm-cluster-id <ocid> \\\n  --number-of-nodes 2\n```\n\n**Limites:** [CHECK DOCS] Máximo de nós depende do shape\n\n**Custo:** Proporcional aos recursos adicionados", system))
    
    # Advanced (2)
    examples.append(create_example("database-exadata", cat, "advanced",
        "Como migrar RAC on-premises para Exadata Cloud?",
        "Migração RAC on-premises → Exadata Cloud:\n\n**1. Planejamento:**\n- Mapeie topology RAC atual\n- Dimensione Exadata equivalente\n- Planeje network (FastConnect ou VPN)\n- Verifique compatibilidade de versão\n\n**2. Método - Data Guard:**\n```sql\n-- On-premises:\nCREATE STANDBY DATABASE \n  FROM PRIMARY \n  VIA 'oci_exadata_target';\n```\n\n**3. Configuração:**\n- Provisione Exadata target\n- Setup Data Guard replication\n- Sync inicial (pode levar horas/dias)\n\n**4. Cutover:**\n```sql\n-- Failover planejado:\nALTER DATABASE COMMIT TO SWITCHOVER TO STANDBY;\n```\n\n**5. Pós-migração:**\n- Valide performance\n- Ajuste parâmetros\n- Teste failback\n\n**Riscos:**\n- Downtime no cutover (minimize com prática)\n- Compatibilidade de versão\n- Network latency durante sync\n\n**Alternativa:** Data Pump para migração offline", system))
    
    examples.append(create_example("database-exadata", cat, "advanced",
        "Como otimizar workload misto (OLTP + DW) no Exadata?",
        "Otimização de workload misto (OLTP + DW) no Exadata:\n\n**1. Database Resource Manager:**\n```sql\n-- Crie consumer groups\nBEGIN\n  DBMS_RESOURCE_MANAGER.CREATE_CONSUMER_GROUP(\n    consumer_group => 'OLTP_GROUP',\n    comment => 'OLTP workload');\n  DBMS_RESOURCE_MANAGER.CREATE_CONSUMER_GROUP(\n    consumer_group => 'DW_GROUP',\n    comment => 'Data warehouse');\nEND;\n/\n\n-- Crie plano\nBEGIN\n  DBMS_RESOURCE_MANAGER.CREATE_PLAN(plan => 'MIXED_PLAN');\n  DBMS_RESOURCE_MANAGER.CREATE_PLAN_DIRECTIVE(\n    plan => 'MIXED_PLAN',\n    group_or_subplan => 'OLTP_GROUP',\n    cpu_p1 => 60);\n  DBMS_RESOURCE_MANAGER.CREATE_PLAN_DIRECTIVE(\n    plan => 'MIXED_PLAN',\n    group_or_subplan => 'DW_GROUP',\n    cpu_p1 => 40);\nEND;\n/\n```\n\n**2. I/O Resource Management (IORM):**\n- OLTP: prioridade em I/O aleatório\n- DW: prioridade em Smart Scan\n\n**3. Memory allocation:**\n- SGA maior para OLTP (buffer cache)\n- PGA maior para DW (sort/hash)\n\n**4. Time-based:**\n- OLTP durante dia (business hours)\n- DW à noite (batch window)\n\n**Trade-offs:** Complexidade de tuning, monitoramento contínuo necessário", system))
    
    return examples

# ============ CONTAINER INSTANCES ============
def generate_container_instances():
    examples = []
    system = "You are an OCI specialist with expertise in container services. Provide technical guidance on Container Instances, OKE, and orchestration."
    cat = "container/instances"
    
    # Beginner (3)
    examples.append(create_example("container-instances", cat, "beginner",
        "O que é OCI Container Instances?",
        "OCI Container Instances é um serviço serverless para executar containers sem gerenciar infraestrutura.\n\n**Características principais:**\n- Sem necessidade de clusters ou nodes\n- Pay per second de execução\n- Scaling automático\n- Isolamento por sandbox\n\n**Casos de uso:**\n- Jobs batch e processamento assíncrono\n- Dev/test rápido de containers\n- Burst de capacidade complementar\n- APIs stateless simples\n\n**Diferença para OKE:**\n- Container Instances: serverless, sem cluster, mais simples\n- OKE: Kubernetes completo, mais controle e features\n\n**Diferença para AWS:** Similar ao AWS Fargate/ECS\n\n[MUTABLE] Preços por vCPU e memória consumidos.\n\nDocs: https://docs.oracle.com/en-us/iaas/Content/ContainerInstance/", system))
    
    examples.append(create_example("container-instances", cat, "beginner",
        "Como criar um container instance?",
        "Criando container instance:\n\n**Via Console:**\n1. Developer Services → Container Instances\n2. 'Create Container Instance'\n3. Configure:\n   - Compartment\n   - Image (OCI Registry ou Docker Hub)\n   - Shape (CPU/Memory)\n   - Network (VCN, subnet)\n4. Environment variables (opcional)\n5. Create\n\n**Via CLI:**\n```bash\noci container-instance container-instance create \\\n  --compartment-id <ocid> \\\n  --display-name my-app \\\n  --image \"nginx:latest\" \\\n  --shape OCI.CI.E4.Flex \\\n  --subnet-id <subnet-ocid>\n```\n\n**Shapes disponíveis:**\n- OCI.CI.E4.Flex: AMD EPYC (custo-benefício)\n- OCI.CI.A1.Flex: ARM Ampere (econômico)\n\n[CHECK DOCS] Shapes disponíveis variam por região.", system))
    
    examples.append(create_example("container-instances", cat, "beginner",
        "Qual o modelo de custo do Container Instances?",
        "Modelo de pricing do Container Instances:\n\n**Cobrança:**\n- Por vCPU/segundo\n- Por GB de memória/segundo\n- Mínimo de 1 segundo de execução\n\n**Exemplo [MUTABLE]:**\n- Shape: 4 vCPU, 16GB RAM\n- 1 hora de execução ≈ custo proporcional\n- Comparado a VM: mais econômico para cargas intermitentes\n\n**Custos adicionais:**\n- Object Storage (para imagens)\n- Network egress (saída de dados)\n- Container Registry (se usar OCI Registry)\n\n**Otimização de custos:**\n- Use shapes adequados à carga\n- Termine instâncias ociosas\n- Agende execuções em batch\n- Use ARM (A1) quando compatível\n\n[CHECK DOCS] Consulte pricing calculator atualizada.", system))
    
    # Intermediate (5)
    examples.append(create_example("container-instances", cat, "intermediate",
        "Como passar variáveis de ambiente e secrets?",
        "Variáveis de ambiente e secrets:\n\n**Variáveis simples (Console):**\n- Container Instance → Environment Variables\n- Adicione key-value pairs\n\n**Via CLI:**\n```bash\noci container-instance container-instance create \\\n  --compartment-id <ocid> \\\n  --environment-variables '[{\"name\":\"DB_HOST\",\"value\":\"db.example.com\"},{\"name\":\"DB_PORT\",\"value\":\"5432\"}]' \\\n  --display-name my-app\n```\n\n**Secrets (recomendado para dados sensíveis):**\n```bash\noci container-instance container-instance create \\\n  --environment-variables-from-vault '[{\"name\":\"DB_PASSWORD\",\"vaultId\":\"<ocid>\",\"secretName\":\"db-pass\"}]'\n```\n\n**Policy necessária:**\n```\nAllow service containerinstance to read secret-family in compartment <comp>\n```\n\n**Best Practice:**\n- Nunca hardcode secrets no código ou imagens\n- Use Vault para passwords, API keys, connection strings", system))
    
    examples.append(create_example("container-instances", cat, "intermediate",
        "Como conectar container à VCN e internet?",
        "Conectividade de rede:\n\n**Requisitos:**\n1. VCN com subnet configurada\n2. Security List permitindo tráfego necessário\n3. Route Table configurada\n\n**Configuração:**\n```bash\noci container-instance container-instance create \\\n  --compartment-id <ocid> \\\n  --subnet-id <subnet-ocid> \\\n  --display-name my-app \\\n  --image \"nginx:latest\"\n```\n\n**Security List:**\n- Ingress: portas necessárias (ex: 80, 443, 8080)\n- Egress: 0.0.0.0/0 para internet (se necessário)\n\n**IPs:**\n- IP privado: da subnet\n- IP público: se subnet for pública\n\n**DNS:**\n- Automático da VCN\n- Custom DNS via configuração\n\n**Para expor serviço:**\n- Use Load Balancer na frente\n- Ou API Gateway para HTTP", system))
    
    examples.append(create_example("container-instances", cat, "intermediate",
        "Como montar volumes no container?",
        "Montando volumes no Container Instances:\n\n**Block Volume:**\n```bash\noci container-instance container-instance create \\\n  --compartment-id <ocid> \\\n  --volume-mounts '[{\"name\":\"data\",\"mountPath\":\"/data\",\"blockVolumeId\":\"<ocid>\"}]' \\\n  --display-name my-app\n```\n\n**File Storage (compartilhado):**\n```bash\noci container-instance container-instance create \\\n  --volume-mounts '[{\"name\":\"shared\",\"mountPath\":\"/shared\",\"fileSystemId\":\"<ocid>\"}]'\n```\n\n**Tipos suportados:**\n- Block Volume: leitura/escrita, alta performance\n- File Storage: compartilhado entre containers\n- Object Storage: via mount (principalmente leitura)\n\n**Limites:** [CHECK DOCS] Verifique limites de IOPS por volume\n\n**Use cases:**\n- Block: banco de dados, arquivos grandes\n- File: compartilhamento entre containers\n- Object: assets estáticos", system))
    
    examples.append(create_example("container-instances", cat, "intermediate",
        "Como executar jobs batch com retry?",
        "Executando jobs batch:\n\n**Configuração básica:**\n```bash\noci container-instance container-instance create \\\n  --compartment-id <ocid> \\\n  --display-name batch-job \\\n  --image \"python:3.9\" \\\n  --command '[\"python\", \"/app/process.py\"]' \\\n  --restart-policy NEVER\n```\n\n**Restart policies:**\n- NEVER: job único (batch)\n- ON_FAILURE: retry automático\n- ALWAYS: serviço contínuo\n\n**Monitoramento:**\n```bash\n# Status do job\noci container-instance container-instance get \\\n  --container-instance-id <ocid>\n\n# Logs\noci container-instance container-instance-action get-logs \\\n  --container-instance-id <ocid>\n```\n\n**Melhor prática:**\n- Use Object Storage para outputs\n- Configure alertas de falha\n- Implemente retry no código para resiliência", system))
    
    examples.append(create_example("container-instances", cat, "intermediate",
        "Como usar imagens do OCI Container Registry?",
        "Usando OCI Container Registry (OCIR):\n\n**1. Push da imagem:**\n```bash\n# Login\ndocker login <region>.ocir.io -u '<namespace>/<username>'\n\n# Tag\ndocker tag myapp:latest <region>.ocir.io/<namespace>/myapp:latest\n\n# Push\ndocker push <region>.ocir.io/<namespace>/myapp:latest\n```\n\n**2. Crie Auth Token:**\n- Console → User Settings → Auth Tokens\n- Generate Token\n- Use como senha no docker login\n\n**3. Crie container instance:**\n```bash\noci container-instance container-instance create \\\n  --compartment-id <ocid> \\\n  --image \"<region>.ocir.io/<namespace>/myapp:latest\" \\\n  --image-pull-secret '<auth-token>'\n```\n\n**Best Practice:**\n- Use tags versionadas (v1.0, v1.1), não 'latest'\n- Scan imagens por vulnerabilidades\n- Use políticas de retenção", system))
    
    # Advanced (2)
    examples.append(create_example("container-instances", cat, "advanced",
        "Como implementar auto-scaling com Container Instances?",
        "Auto-scaling pattern com Container Instances:\n\n**1. Com Events + Functions:**\n```yaml\n# Event Rule\n- source: oci.metrics\n- metric: cpu_utilization > 70%\n- action: invoke function\n```\n\n**2. Function cria nova instância:**\n```python\nimport oci\n\ndef handler(ctx, data):\n    ci_client = oci.container_instances.ContainerInstanceClient()\n    ci_client.create_container_instance({\n        'compartment_id': compartment,\n        'image': 'myapp:latest',\n        'shape': 'OCI.CI.E4.Flex'\n    })\n```\n\n**3. Cleanup (scale in):**\n- Monitor instâncias ociosas\n- Delete após timeout configurado\n- Use tagging para tracking\n\n**Alternativa para scaling sofisticado:**\n- Use OKE com Horizontal Pod Autoscaler\n- Mais controle e métricas\n\n**Trade-offs:**\n- Container Instances: scaling mais lento (minutos)\n- OKE: scaling mais rápido (segundos)", system))
    
    examples.append(create_example("container-instances", cat, "advanced",
        "Como migrar de AWS ECS/Fargate para OCI?",
        "Migração ECS/Fargate → Container Instances:\n\n**1. Mapeamento de conceitos:**\n- ECS Task → Container Instance\n- ECS Service → Múltiplas instâncias + Load Balancer\n- ECS Fargate → Container Instances (serverless)\n- ECR → OCI Container Registry\n\n**2. Exporte definições ECS:**\n```json\n// ECS Task Definition\n{\n  \"containerDefinitions\": [{\n    \"image\": \"myapp:latest\",\n    \"cpu\": 1024,\n    \"memory\": 2048,\n    \"environment\": [...]\n  }]\n}\n```\n\n**3. Converta para OCI:**\n```bash\noci container-instance container-instance create \\\n  --image \"myapp:latest\" \\\n  --shape OCI.CI.E4.Flex  # 4 vCPU, 16GB\n```\n\n**4. Load Balancer:**\n- Backend set → Container Instances\n- Health check configurado\n\n**Diferenças:**\n- ECS tem mais features de orchestration\n- Container Instances é mais simples\n- Para Kubernetes, use OKE", system))
    
    return examples

# ============ SERVERLESS FUNCTIONS ============
def generate_serverless_functions():
    examples = []
    system = "You are an OCI specialist with expertise in serverless computing. Provide technical guidance on Functions, API Gateway, and event-driven architectures."
    cat = "serverless/functions"
    
    # Beginner (3)
    examples.append(create_example("serverless-functions", cat, "beginner",
        "O que é OCI Functions?",
        "OCI Functions é um serviço serverless de Functions-as-a-Service (FaaS).\n\n**Características principais:**\n- Execução sob demanda\n- Scaling automático (0 a N)\n- Pay per execution\n- Baseado em Fn Project (open source)\n\n**Casos de uso:**\n- Processamento de eventos (Object Storage, Events)\n- Webhooks e integrações\n- Automação de infraestrutura\n- ETL leve e transformação de dados\n- Backend para APIs\n\n**Componentes:**\n- Application: grupo de functions\n- Function: código executável\n- Invocation: execução da function\n\n**Diferença para AWS:** Similar ao AWS Lambda\n\n[MUTABLE] Preços por milhão de invocações e GB-segundo.\n\nDocs: https://docs.oracle.com/en-us/iaas/Content/Functions/", system))
    
    examples.append(create_example("serverless-functions", cat, "beginner",
        "Como criar minha primeira function?",
        "Criando primeira function:\n\n**Via Console:**\n1. Developer Services → Functions\n2. 'Create Application'\n3. Configure VCN e subnet\n4. 'Create Function' na aplicação\n5. Escolha runtime (Python, Node, Java)\n6. Upload do código ou editor inline\n7. Teste com 'Invoke'\n\n**Exemplo Python:**\n```python\ndef handler(ctx, data):\n    return {\n        'statusCode': 200,\n        'body': 'Hello from OCI Functions!'\n    }\n```\n\n**Endpoint:** HTTPS automático fornecido\n\n**Via CLI:**\n```bash\noci functions function create \\\n  --application-id <app-ocid> \\\n  --display-name hello \\\n  --image <region>.ocir.io/<namespace>/func-python:latest\n```\n\n[CHECK DOCS] Runtimes suportados variam.", system))
    
    examples.append(create_example("serverless-functions", cat, "beginner",
        "Quais linguagens são suportadas?",
        "Runtimes suportados no OCI Functions:\n\n**Oficiais:**\n- Python 3.8, 3.9, 3.10\n- Node.js 14, 16, 18\n- Java 8, 11\n- Go 1.x\n\n**Custom (Docker):**\n- Qualquer linguagem via Docker image\n- Ruby, PHP, .NET, Rust, etc.\n- Controle total do ambiente\n\n**Exemplo custom Dockerfile:**\n```dockerfile\nFROM ruby:3.1\nCOPY function.rb /\nCMD [\"function.handle\"]\n```\n\n**Recomendação:**\n- Use runtimes oficiais para simplicidade\n- Use custom Docker para necessidades específicas\n\n[CHECK DOCS] Versões atualizadas periodicamente, consulte docs.", system))
    
    # Intermediate (5)
    examples.append(create_example("serverless-functions", cat, "intermediate",
        "Como invocar uma function via CLI e SDK?",
        "Invocando functions:\n\n**Via CLI (síncrono):**\n```bash\noci functions function invoke \\\n  --function-id <ocid> \\\n  --invoke-type SYNCHRONOUS \\\n  --invoke-body '{\"name\": \"John\"}' \\\n  --response-body-output-file -\n```\n\n**Via CLI (assíncrono):**\n```bash\noci functions function invoke \\\n  --function-id <ocid> \\\n  --invoke-type ASYNCHRONOUS \\\n  --invoke-body '{\"event\": \"process\"}'\n```\n\n**Via endpoint HTTPS:**\n```bash\ncurl -X POST https://<endpoint>/20180120/actions/<id>/actions/invoke \\\n  -H \"Authorization: Bearer <token>\" \\\n  -d '{\"data\": \"test\"}'\n```\n\n**Via SDK Python:**\n```python\nimport oci\n\nclient = oci.functions.FunctionsInvocationClient()\nresponse = client.invoke_function(\n    function_id='<ocid>',\n    invoke_body='{}'\n)\nprint(response.data)\n```\n\n**Resposta:** JSON com statusCode e body", system))
    
    examples.append(create_example("serverless-functions", cat, "intermediate",
        "Como conectar function ao Vault para secrets?",
        "Usando secrets do Vault em Functions:\n\n**1. Crie secret no Vault:**\n```bash\noci vault secret create \\\n  --compartment-id <ocid> \\\n  --vault-id <ocid> \\\n  --secret-name db-password \\\n  --secret-content '{\"content\": \"mysecret\"}'\n```\n\n**2. Policy para function:**\n```\nAllow service fnfunc to read secret-family in compartment <comp>\n```\n\n**3. Código da function (Python):**\n```python\nimport oci\n\ndef handler(ctx, data):\n    vault = oci.vault.VaultClient()\n    secret = vault.get_secret(secret_id='<ocid>')\n    password = secret.data.secret_content.content\n    # Use password para conectar ao DB\n    return {'status': 'success'}\n```\n\n**Best Practice:**\n- Nunca hardcode secrets no código\n- Rotação automática de secrets\n- Use instance principal para auth", system))
    
    examples.append(create_example("serverless-functions", cat, "intermediate",
        "Como configurar triggers do Events Service?",
        "Configurando triggers com Events Service:\n\n**1. Crie Rule no Events:**\n```bash\noci events rule create \\\n  --compartment-id <ocid> \\\n  --display-name \"object-created\" \\\n  --condition '{\"eventType\":\"com.oraclecloud.objectstorage.createobject\"}' \\\n  --actions '[{\"type\":\"FUNCTION\",\"functionId\":\"<ocid>\"}]'\n```\n\n**2. Exemplo - Object Storage:**\n```json\n{\n  \"eventType\": \"com.oraclecloud.objectstorage.createobject\",\n  \"compartmentId\": \"<ocid>\",\n  \"data\": {\n    \"namespace\": \"my-ns\",\n    \"bucketName\": \"uploads\",\n    \"objectName\": \"file.pdf\"\n  }\n}\n```\n\n**3. Function processa evento:**\n```python\ndef handler(ctx, data):\n    bucket = data['data']['bucketName']\n    object_name = data['data']['objectName']\n    # Process file\n    return {'processed': f'{bucket}/{object_name}'}\n```\n\n**Outros eventos:** Compute, Database, Monitoring, etc.", system))
    
    examples.append(create_example("serverless-functions", cat, "intermediate",
        "Como fazer deploy com Fn CLI?",
        "Deploy de functions com Fn CLI:\n\n**1. Instale Fn CLI:**\n```bash\npip3 install fnproject-cli\n```\n\n**2. Inicie projeto:**\n```bash\nfn init --runtime python myfunc\ncd myfunc\n```\n\n**3. Estrutura do projeto:**\n```\nmyfunc/\n  func.py           # código da function\n  func.yaml         # configuração\n  requirements.txt  # dependências\n```\n\n**4. func.yaml:**\n```yaml\nschema_version: 0.0.1\nversion: 0.0.1\nruntime: python\ncmd: func.handler\n```\n\n**5. Deploy:**\n```bash\nfn deploy --app myapp --registry <region>.ocir.io/<namespace>\n```\n\n**6. Invoke:**\n```bash\nfn invoke myapp myfunc\n```\n\n**Vantagem:** Versionamento e CI/CD mais fácil", system))
    
    examples.append(create_example("serverless-functions", cat, "intermediate",
        "Como monitorar e debugar functions?",
        "Monitoramento e debugging:\n\n**Logs no Logging Service:**\n```bash\noci logging log-entry list \\\n  --compartment-id <ocid> \\\n  --log-id <log-ocid>\n```\n\n**Logging na function:**\n```python\nimport logging\nlogging.basicConfig(level=logging.INFO)\nlogger = logging.getLogger()\n\ndef handler(ctx, data):\n    logger.info(f\"Processing: {data}\")\n    logger.error(f\"Error occurred\")\n    return {'status': 'ok'}\n```\n\n**Metrics no Monitoring:**\n- Invocations count\n- Errors count\n- Duration (ms)\n- Concurrent executions\n\n**Tracing:**\n- Integre com OCI Resource Manager\n- Use correlation IDs\n- Distributed tracing com Jaeger\n\n**Debug local:**\n```bash\nfn invoke --body '{\"test\": true}' myapp myfunc\n```", system))
    
    # Advanced (2)
    examples.append(create_example("serverless-functions", cat, "advanced",
        "Como implementar retry e dead letter queue?",
        "Retry e Dead Letter Queue pattern:\n\n**1. Retry na function:**\n```python\ndef handler(ctx, data):\n    max_retries = 3\n    for attempt in range(max_retries):\n        try:\n            return process(data)\n        except Exception as e:\n            if attempt == max_retries - 1:\n                # Send to DLQ\n                send_to_dlq(data, str(e))\n                raise\n            time.sleep(2 ** attempt)  # exponential backoff\n```\n\n**2. DLQ com Queue Service:**\n```python\nimport oci\n\ndef send_to_dlq(data, error):\n    queue = oci.queue.QueueClient()\n    queue.put_message(\n        queue_id='<dlq-ocid>',\n        message={'body': data, 'error': error}\n    )\n```\n\n**3. Events para DLQ:**\n- Rule para falhas de function\n- Action: enviar para Queue\n\n**Processamento DLQ:**\n- Function separada processa DLQ\n- Alerta quando DLQ cresce\n- Retry manual após fix\n\n**Best Practice:** Monitore tamanho da DLQ", system))
    
    examples.append(create_example("serverless-functions", cat, "advanced",
        "Como migrar AWS Lambda para OCI Functions?",
        "Migração AWS Lambda → OCI Functions:\n\n**1. Mapeamento de conceitos:**\n- Lambda Function → OCI Function\n- Lambda Layer → Docker custom runtime\n- API Gateway → OCI API Gateway\n- EventBridge → OCI Events\n- SQS → OCI Queue\n\n**2. Converta handler:**\n```python\n# AWS Lambda\ndef lambda_handler(event, context):\n    return {'statusCode': 200, 'body': 'OK'}\n\n# OCI Functions\ndef handler(ctx, data):\n    return {'statusCode': 200, 'body': 'OK'}\n```\n\n**3. IAM → Policies:**\n- Lambda execution role → Dynamic group + policies\n- resource.function-family → function-family\n\n**4. Environment variables:**\n- Mesma abordagem\n- Secrets → OCI Vault\n\n**Diferenças:**\n- Lambda tem mais integrações nativas\n- OCI Functions é mais simples\n- Custom Docker para parity total\n\n**Ferramentas:** Use Fn CLI para deploy similar ao SAM", system))
    
    return examples

# ============ SERVERLESS API GATEWAY ============
def generate_serverless_api_gateway():
    examples = []
    system = "You are an OCI specialist with expertise in serverless computing and API management. Provide technical guidance on API Gateway, routes, and integrations."
    cat = "serverless/api-gateway"
    
    # Beginner (3)
    examples.append(create_example("serverless-api-gateway", cat, "beginner",
        "O que é OCI API Gateway?",
        "OCI API Gateway é um serviço gerenciado para criar, publicar e gerenciar APIs.\n\n**Características principais:**\n- RESTful APIs\n- Rate limiting\n- Authentication/Authorization\n- Transformação de requests\n- Logging e monitoring\n\n**Componentes:**\n- Gateway: endpoint público\n- Deployment: conjunto de routes\n- Route: mapeamento path → backend\n- Backend: Functions, HTTP, Load Balancer\n\n**Casos de uso:**\n- APIs para aplicações web/mobile\n- Microserviços\n- Backend para frontend (BFF)\n- Integração B2B\n\n**Diferença para AWS:** Similar ao AWS API Gateway\n\n[MUTABLE] Preços por gateway e requests.\n\nDocs: https://docs.oracle.com/en-us/iaas/Content/APIGateway/", system))
    
    examples.append(create_example("serverless-api-gateway", cat, "beginner",
        "Como criar um API Gateway?",
        "Criando API Gateway:\n\n**Via Console:**\n1. Developer Services → API Gateway\n2. 'Create Gateway'\n3. Configure:\n   - Compartment\n   - Name\n   - VCN e subnet\n   - Type (public/private)\n4. Create\n\n**Via CLI:**\n```bash\noci api-gateway gateway create \\\n  --compartment-id <ocid> \\\n  --display-name my-api \\\n  --endpoint-type PUBLIC \\\n  --subnet-id <subnet-ocid>\n```\n\n**Endpoint:** URL pública automática fornecida\nex: https://abc123.apigateway.us-ashburn-1.oci.customer-oci.com\n\n**Próximos passos:** Criar deployment com routes\n\n[CHECK DOCS] Limites de gateways por compartment", system))
    
    examples.append(create_example("serverless-api-gateway", cat, "beginner",
        "Como criar uma rota simples?",
        "Criando rota (route):\n\n**Via Console:**\n1. Gateway Details → Create Deployment\n2. Add Route:\n   - Path: /hello\n   - Method: GET\n   - Backend: HTTP Backend\n   - URL: https://myapp.com/api\n3. Create Deployment\n\n**Via SDK (Python):**\n```python\nfrom oci.apigateway.models import DeploymentDetails\n\ndeployment = DeploymentDetails(\n    display_name='v1',\n    routes=[{\n        'path': '/hello',\n        'methods': ['GET'],\n        'backend': {\n            'type': 'HTTP_BACKEND',\n            'url': 'https://myapp.com/api'\n        }\n    }]\n)\n```\n\n**Teste:**\n```bash\ncurl https://<gateway-url>/hello\n```\n\n**Backend types:** HTTP, Oracle Functions, Load Balancer, Stock Response", system))
    
    # Intermediate (5)
    examples.append(create_example("serverless-api-gateway", cat, "intermediate",
        "Como integrar API Gateway com Functions?",
        "Integração API Gateway + Functions:\n\n**Via Console:**\n1. Create Deployment → Add Route\n2. Backend Type: Oracle Functions\n3. Selecione Application e Function\n4. Create Deployment\n\n**Via CLI:**\n```bash\noci api-gateway deployment create \\\n  --gateway-id <gateway-ocid> \\\n  --specification '{\n    \"routes\": [{\n      \"path\": \"/process\",\n      \"methods\": [\"POST\"],\n      \"backend\": {\n        \"type\": \"ORACLE_FUNCTIONS_BACKEND\",\n        \"functionId\": \"<function-ocid>\"\n      }\n    }]\n  }'\n```\n\n**Policy necessária:**\n```\nAllow service apigateway to use fn-func in compartment <comp>\n```\n\n**Vantagem:** Serverless end-to-end, scaling automático\n\n**Exemplo completo:** API REST → API Gateway → Function → Database", system))
    
    examples.append(create_example("serverless-api-gateway", cat, "intermediate",
        "Como configurar rate limiting?",
        "Configurando rate limiting:\n\n**Via Console:**\n1. Deployment → Rate Limiting\n2. Configure:\n   - Rate limit: requests por segundo\n   - Burst limit: pico permitido\n3. Apply\n\n**Via SDK:**\n```python\nrate_limits = {\n    'rateLimiting': {\n        'type': 'CLIENT_IP',\n        'rateInRequestsPerSecond': 100,\n        'burstLimitInRequests': 200\n    }\n}\n\ndeployment = DeploymentDetails(\n    display_name='v1',\n    rate_limiting=rate_limits,\n    routes=[...]\n)\n```\n\n**Tipos:**\n- CLIENT_IP: por IP de origem\n- GLOBAL: total do gateway\n\n**Use cases:**\n- Proteger backend de overload\n- Prevenir abuso/DDoS\n- SLA enforcement\n- Tier de API (free vs premium)", system))
    
    examples.append(create_example("serverless-api-gateway", cat, "intermediate",
        "Como adicionar autenticação JWT?",
        "Autenticação JWT no API Gateway:\n\n**Via Console:**\n1. Deployment → Authentication\n2. Type: JWT\n3. Configure:\n   - JWKS URI: https://auth.example.com/.well-known/jwks.json\n   - Audience: my-api\n   - Issuer: https://auth.example.com\n4. Save\n\n**Via SDK:**\n```python\nauth = {\n    'type': 'JWT',\n    'jwksUri': 'https://auth.example.com/.well-known/jwks.json',\n    'audience': 'my-api',\n    'issuer': 'https://auth.example.com'\n}\n```\n\n**Fluxo:**\n1. Client obtém token do IdP\n2. Request com Authorization: Bearer <token>\n3. Gateway valida JWT\n4. Backend recebe request válido\n\n**IdPs suportados:** Oracle IDCS, Auth0, Okta, Azure AD, Keycloak", system))
    
    examples.append(create_example("serverless-api-gateway", cat, "intermediate",
        "Como fazer versionamento de API?",
        "Versionamento de API:\n\n**Estratégia 1 - Path (mais comum):**\n```\nGET /v1/users\nGET /v2/users\n```\n\n**Deployments:**\n```python\n# v1 deployment\nroutes_v1 = [{'path': '/v1/users', ...}]\n\n# v2 deployment\nroutes_v2 = [{'path': '/v2/users', ...}]\n```\n\n**Estratégia 2 - Header:**\n```\nGET /users\nHeader: API-Version: 2\n```\n\n**Route matching:**\n```python\nroutes = [\n    {'path': '/v2/users', 'headerMatches': [{'name': 'API-Version', 'value': '2'}]},\n    {'path': '/v1/users'},  # default\n]\n```\n\n**Best Practices:**\n- Mantenha versões antigas por período definido\n- Documente breaking changes\n- Use deprecation headers\n- Comunique mudanças com antecedência", system))
    
    examples.append(create_example("serverless-api-gateway", cat, "intermediate",
        "Como configurar CORS?",
        "Configurando CORS:\n\n**Via Console:**\n1. Deployment → CORS\n2. Configure:\n   - Allowed Origins: https://app.example.com\n   - Allowed Methods: GET, POST, PUT\n   - Allowed Headers: Content-Type, Authorization\n   - Exposed Headers: X-Request-Id\n   - Max Age: 3600\n3. Save\n\n**Via SDK:**\n```python\ncors = {\n    'allowedOrigins': ['https://app.example.com'],\n    'allowedMethods': ['GET', 'POST', 'PUT', 'DELETE'],\n    'allowedHeaders': ['Content-Type', 'Authorization'],\n    'exposedHeaders': ['X-Request-Id'],\n    'maxAgeInSeconds': 3600\n}\n```\n\n**Wildcard (dev/test):**\n- allowedOrigins: ['*']\n- Não use em produção\n\n**Preflight:** Gateway responde OPTIONS automaticamente", system))
    
    # Advanced (2)
    examples.append(create_example("serverless-api-gateway", cat, "advanced",
        "Como implementar request/response transformation?",
        "Transformation com policies:\n\n**Request Transformation:**\n```python\nrequest_policy = {\n    'type': 'REQUEST_POLICY',\n    'renameHeaders': [{'from': 'X-Old', 'to': 'X-New'}],\n    'addHeaders': [{'name': 'X-Gateway-Time', 'value': '$request.time'}],\n    'removeHeaders': ['X-Internal']\n}\n```\n\n**Response Transformation:**\n```python\nresponse_policy = {\n    'type': 'RESPONSE_POLICY',\n    'addHeaders': [{'name': 'X-API-Version', 'value': 'v2'}],\n    'bodyTransformation': {\n        'type': 'JSON',\n        'template': '{\"data\": $response.body, \"meta\": {\"version\": \"v2\"}}'\n    }\n```\n\n**Use cases:**\n- Legacy → Modern API\n- Normalização de responses\n- Adicionar metadata\n- Masking de dados sensíveis\n\n**Limitações:** Transformações complexas podem precisar de Function intermediária", system))
    
    examples.append(create_example("serverless-api-gateway", cat, "advanced",
        "Como migrar AWS API Gateway para OCI?",
        "Migração AWS API Gateway → OCI:\n\n**1. Exporte API AWS:**\n```bash\naws apigateway get-rest-apis\naws apigateway get-resources --rest-api-id <id>\naws apigateway get-export --rest-api-id <id> --export-type swagger\n```\n\n**2. Mapeamento:**\n- REST API → Gateway + Deployment\n- Resources → Routes\n- Integrations → Backends\n- Authorizers → Authentication policies\n- Usage Plans → Rate Limiting\n\n**3. Converta definição OpenAPI:**\n```yaml\n# AWS OpenAPI → OCI Specification\npaths:\n  /users:\n    get:\n      x-oci-backend:\n        type: ORACLE_FUNCTIONS_BACKEND\n        functionId: <ocid>\n```\n\n**4. IAM:**\n- AWS IAM → OCI Policies\n- Lambda permissions → Function policies\n\n**Diferenças:**\n- OCI é mais simples\n- Menos integrações nativas\n- Custom policies para casos complexos", system))
    
    return examples

# Main execution
def main():
    """Generate JSONL files for batch 1."""
    
    generators = {
        "database-exadata": generate_database_exadata,
        "container-instances": generate_container_instances,
        "serverless-functions": generate_serverless_functions,
        "serverless-api-gateway": generate_serverless_api_gateway,
    }
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    for category, generator in generators.items():
        examples = generator()
        write_jsonl(f"{category}.jsonl", examples)
    
    print(f"\nTotal: {len(generators)} files generated")

if __name__ == "__main__":
    main()
