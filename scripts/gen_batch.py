#!/usr/bin/env python3
import json
from pathlib import Path

OUTPUT_DIR = Path("/Users/otaviolemos/ml/olia-2-oci/data/curated")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def create_example(sp, q, a, cat, diff):
    return {
        "messages": [
            {"role": "system", "content": sp},
            {"role": "user", "content": q},
            {"role": "assistant", "content": a}
        ],
        "metadata": {"category": cat, "difficulty": diff, "source": "generated"}
    }

def save(examples, filename):
    output_file = OUTPUT_DIR / filename
    with open(output_file, 'w', encoding='utf-8') as f:
        for ex in examples:
            f.write(json.dumps(ex, ensure_ascii=False) + '\n')
    return output_file, len(examples)

def gen_postgresql():
    cat = "database/postgresql"
    sp = "You are an OCI specialist with expertise in PostgreSQL on OCI."
    ex = []
    ex.append(create_example(sp, "Como criar PostgreSQL no OCI?", "Criando PostgreSQL:\n\n**Via Console:**\n1. MySQL → DB Systems → Create\n2. Selecione PostgreSQL\n3. Configure shape e storage\n4. Create\n\n**Via CLI:**\n```bash\noci mysql db-system create --compartment-id <ocid> --display-name my-postgres\n```\n\n[MUTABLE] Preços variam por shape.", cat, "beginner"))
    ex.append(create_example(sp, "Como conectar no PostgreSQL?", "Conectando:\n\n```bash\npsql -h <host> -U admin -d postgres\n```\n\n**Security:** Porta 5432 aberta na Security List", cat, "beginner"))
    ex.append(create_example(sp, "Qual shape para PostgreSQL?", "Shapes:\n\n**Dev/Test:** VM.Standard.E2\n**Production:** VM.Standard.E4\n\n[MUTABLE] Preços variam.", cat, "beginner"))
    ex.append(create_example(sp, "Como configurar replication?", "Replication:\n\n```sql\nALTER SYSTEM SET wal_level = replica;\npg_basebackup -h primary -D /data -R\n```\n\n**Tipos:** Synchronous, Asynchronous", cat, "intermediate"))
    ex.append(create_example(sp, "Como fazer backup?", "Backup:\n\n```bash\npg_dump -U admin dbname > backup.sql\noci mysql backup create --db-system-id <ocid>\n```\n\n**Best practice:** Backup diário + WAL archiving", cat, "intermediate"))
    ex.append(create_example(sp, "Como escalar PostgreSQL?", "Escalando:\n\n**Vertical:** oci mysql db-system update --shape-name VM.Standard.E8\n**Horizontal:** Read replicas\n\n[MUTABLE] Custos variam.", cat, "intermediate"))
    ex.append(create_example(sp, "Como configurar HA?", "HA:\n\n**Primary-Standby** com streaming replication\n**Failover:** pg_ctl promote\n\n**RTO:** minutos, **RPO:** depende do lag", cat, "intermediate"))
    ex.append(create_example(sp, "Como monitorar?", "Monitoring:\n\n```sql\nSELECT * FROM pg_stat_activity;\n```\n\n**Tools:** pgAdmin, Prometheus, OCI Monitoring", cat, "intermediate"))
    ex.append(create_example(sp, "Como otimizar performance?", "Otimização:\n\n**Config:** shared_buffers = 25% RAM\n**Indexes:** B-tree, GIN\n**Query:** EXPLAIN ANALYZE", cat, "advanced"))
    ex.append(create_example(sp, "Como migrar para OCI?", "Migração:\n\n**Opções:** pg_dump, logical replication, OCI Database Migration\n\n**Pre-migração:** Test em staging", cat, "advanced"))
    return ex

def gen_nosql():
    cat = "database/nosql"
    sp = "You are an OCI specialist with expertise in Oracle NoSQL Database."
    ex = []
    ex.append(create_example(sp, "Como criar tabela NoSQL?", "Criando tabela:\n\n```bash\noci nosql table create --compartment-id <ocid> --name users\n```\n\n**Keys:** SIMPLE, COMPOSITE, MULTI\n\n[MUTABLE] Preços por capacidade.", cat, "beginner"))
    ex.append(create_example(sp, "Como inserir dados?", "Inserindo:\n\n```python\nimport oci\nclient = oci.nosql.NosqlClient(config)\nclient.row_put(table_name='users', value={'id': '1', 'name': 'John'})\n```\n\n**Batch:** client.multi_put(rows=[...])", cat, "beginner"))
    ex.append(create_example(sp, "Como consultar?", "Consultando:\n\n```python\nclient.get(table_name='users', key={'id': '1'})\nclient.query(table_name='users', statement='SELECT * FROM users WHERE age > 18')\n```", cat, "beginner"))
    ex.append(create_example(sp, "Como configurar TTL?", "TTL:\n\n```bash\noci nosql table create --name events --ttl '{\"duration\":30,\"unit\":\"DAYS\"}'\n```\n\n**Use cases:** Session data, cache", cat, "intermediate"))
    ex.append(create_example(sp, "Como fazer backup?", "Backup:\n\n```bash\noci nosql backup create --table-id <ocid>\n```\n\n**Restore:** oci nosql backup restore --backup-id <id>", cat, "intermediate"))
    ex.append(create_example(sp, "Como escalar?", "Escalando:\n\n```bash\noci nosql table update --table-id <ocid> --read-units 1000\n```\n\n**Storage:** Automático\n\n[MUTABLE] Custos por capacidade.", cat, "intermediate"))
    ex.append(create_example(sp, "Como modelar dados?", "Modelagem:\n\n**Padrões:**\n- One-to-many: embed\n- Time-series: partition por tempo\n- Catalog: arrays\n\n**Design:** Baseado em queries", cat, "intermediate"))
    ex.append(create_example(sp, "Como monitorar?", "Monitoring:\n\n**Metrics:** ReadUnits, WriteUnits, ThrottledRequests\n**Alarms:** oci monitoring alarm create", cat, "intermediate"))
    ex.append(create_example(sp, "Como otimizar?", "Otimização:\n\n**Indexes:** oci nosql index create\n**Batch:** multi_put, multi_delete\n**Capacity:** Ajuste baseado em metrics", cat, "advanced"))
    ex.append(create_example(sp, "Como migrar?", "Migração:\n\n**De SQL:** Modele, transforme, migre em batch\n**De MongoDB:** JSON compatible\n\n**Tools:** OCI Data Integration", cat, "advanced"))
    return ex

def gen_oke():
    cat = "container/oke"
    sp = "You are an OCI specialist with expertise in OKE."
    ex = []
    ex.append(create_example(sp, "Como criar cluster OKE?", "Criando OKE:\n\n**Console:** Kubernetes Clusters → Create\n**CLI:** oci ce cluster create --name my-cluster\n\n**Node pools:** VM.Standard.E4, VM.Standard.A1\n\n[MUTABLE] Preços variam.", cat, "beginner"))
    ex.append(create_example(sp, "Como conectar com kubectl?", "Conectando:\n\n**1.** Baixe kubeconfig do Console\n**2.** export KUBECONFIG=/path/to/kubeconfig.yaml\n**3.** kubectl get nodes\n\n**CLI:** oci ce cluster create-kubeconfig", cat, "beginner"))
    ex.append(create_example(sp, "Como criar node pool?", "Node pool:\n\n```bash\noci ce node-pool create --cluster-id <ocid> --name pool1 --shape VM.Standard.E4.Flex --node-count 3\n```\n\n**Auto-scaling:** minNodes, maxNodes", cat, "beginner"))
    ex.append(create_example(sp, "Como fazer deploy?", "Deploy:\n\n```yaml\napiVersion: apps/v1\nkind: Deployment\nmetadata:\n  name: nginx\nspec:\n  replicas: 3\n  template:\n    spec:\n      containers:\n      - name: nginx\n        image: nginx:latest\n```\n\n**Apply:** kubectl apply -f deployment.yaml", cat, "intermediate"))
    ex.append(create_example(sp, "Como configurar auto-scaling?", "Auto-scaling:\n\n**Cluster:** node pool com min/max\n**HPA:**\n```yaml\napiVersion: autoscaling/v2\nkind: HorizontalPodAutoscaler\nspec:\n  minReplicas: 2\n  maxReplicas: 10\n  metrics:\n  - type: Resource\n    resource:\n      name: cpu\n      target:\n        averageUtilization: 70\n```", cat, "intermediate"))
    ex.append(create_example(sp, "Como usar Helm?", "Helm:\n\n**Instalar:** curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash\n\n**Charts:**\n```bash\nhelm repo add stable https://charts.helm.sh/stable\nhelm install my-app ./chart\n```", cat, "intermediate"))
    ex.append(create_example(sp, "Como configurar monitoring?", "Monitoring:\n\n**OCI:** Metrics automáticas\n**Prometheus:** helm install prometheus-community/kube-prometheus-stack\n**Alarms:** oci monitoring alarm create", cat, "intermediate"))
    ex.append(create_example(sp, "Como configurar RBAC?", "RBAC:\n\n**IAM:** Allow group Developers to manage oke-cluster\n**Kubernetes:** ClusterRoleBinding\n\n**Namespace isolation:** ResourceQuota", cat, "intermediate"))
    ex.append(create_example(sp, "Como otimizar custos?", "Otimização:\n\n**ARM:** VM.Standard.A1 (80% economia)\n**Auto-scaling:** Scale down à noite\n**Spot:** Até 90% desconto\n**Right-size:** kubectl top pods\n\n[MUTABLE] Preços variam.", cat, "advanced"))
    ex.append(create_example(sp, "Como fazer upgrade?", "Upgrade:\n\n**Cluster:** oci ce cluster update --kubernetes-version v1.29.0\n**Node pools:** oci ce node-pool update\n\n**Sequência:** Cluster → Nodes → Apps\n\n**Best practice:** Test em staging primeiro", cat, "advanced"))
    return ex

if __name__ == "__main__":
    gens = {
        "database-postgresql": gen_postgresql,
        "database-nosql": gen_nosql,
        "container-oke": gen_oke,
    }
    for name, gen in gens.items():
        examples = gen()
        filename = f"{name}.jsonl"
        output_file, count = save(examples, filename)
        print(f"Gerado: {output_file} ({count} exemplos)")
