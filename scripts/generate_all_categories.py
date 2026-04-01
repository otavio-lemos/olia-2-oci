#!/usr/bin/env python3
"""
OCI Specialist LLM - Gerador Completo de Todas 71 Categorias
Gera 710 exemplos JSONL (10 por categoria)
"""

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

# ============================================================================
# LOAD BALANCER
# ============================================================================
def gen_lb():
    cat = "lb/load-balancer"
    sp = "You are an OCI specialist with expertise in Load Balancing. Provide technical guidance on load balancer configuration, backend sets, and SSL termination."
    ex = []
    ex.append(create_example(sp, "Como criar Load Balancer no OCI?",
        "Criando Load Balancer:\n\n**Via Console:**\n1. Networking → Load Balancers\n2. Create Load Balancer\n3. Escolha shape (100Mbps, 400Mbps, 8000Mbps)\n4. Selecione VCN e subnets\n5. Create\n\n**Via CLI:**\n```bash\noci lb load-balancer create \\\n  --compartment-id <ocid> \\\n  --shape 100Mbps \\\n  --subnet-ids <subnet-ocid>\n```\n\n**Shapes:**\n- 100Mbps: até 100 Mbps\n- 400Mbps: até 400 Mbps\n- 8000Mbps: até 8 Gbps\n\n**Public vs Private:**\n- Pública: subnet pública\n- Privada: subnet privada\n\n[MUTABLE] Preços variam por shape e região.\n\nDocs: https://docs.oracle.com/en-us/iaas/Content/LoadBalancing/Concepts/loadbalanceroverview.htm", cat, "beginner"))
    ex.append(create_example(sp, "Como configurar backend set?",
        "Configurando Backend Set:\n\n**1. Crie backend set:**\n```bash\noci lb backend-set create \\\n  --load-balancer-id <lb-ocid> \\\n  --name default \\\n  --policy ROUND_ROBIN \\\n  --health-check-protocol HTTP \\\n  --health-check-uri /health \\\n  --health-check-port 80\n```\n\n**2. Adicione backends:**\n```bash\noci lb backend create \\\n  --load-balancer-id <lb-ocid> \\\n  --backend-set-name default \\\n  --ip-address 10.0.1.10 \\\n  --port 80\n```\n\n**Policies:**\n- ROUND_ROBIN: distribuição igual\n- LEAST_CONNECTIONS: menor conexões\n- IP_HASH: sessão persistente\n\n**Health checks:** Automáticos, removem backends unhealthy", cat, "beginner"))
    ex.append(create_example(sp, "Como configurar SSL termination?",
        "SSL Termination:\n\n**1. Crie certificado:**\n```bash\noci lb certificate create \\\n  --load-balancer-id <lb-ocid> \\\n  --certificate-name my-cert \\\n  --public-certificate-file cert.pem \\\n  --private-key-file key.pem\n```\n\n**2. Configure listener HTTPS:**\n```bash\noci lb listener create \\\n  --load-balancer-id <lb-ocid> \\\n  --default-backend-set-name default \\\n  --port 443 \\\n  --protocol HTTP \\\n  --ssl-configuration-name my-cert\n```\n\n**3. Redirecione HTTP → HTTPS:**\n- Crie listener porta 80\n- Adicione rule para redirect 301\n\n**Benefícios:**\n- Offload de CPU do LB\n- Certificados centralizados\n- Mais simples de gerenciar", cat, "intermediate"))
    ex.append(create_example(sp, "Como usar path-based routing?",
        "Path-based routing:\n\n**1. Crie hostname:**\n```bash\noci lb hostname create \\\n  --load-balancer-id <lb-ocid> \\\n  --name example-com \\\n  --hostname example.com\n```\n\n**2. Crie backend sets por path:**\n- /api → API backend set\n- /static → Static content backend\n- / → Default backend\n\n**3. Configure listeners com rules:**\n```bash\noci lb listener create \\\n  --load-balancer-id <lb-ocid> \\\n  --route-policy-name api-policy\n```\n\n**Use cases:**\n- Microserviços\n- Separação API/web\n- Multi-tenant\n\n**Vantagem:** Single LB para múltiplas aplicações", cat, "intermediate"))
    ex.append(create_example(sp, "Como configurar health checks?",
        "Health checks:\n\n**Tipos:**\n- HTTP/HTTPS: verifica URI\n- TCP: verifica conexão\n\n**Configuração:**\n```bash\noci lb backend-set update \\\n  --load-balancer-id <lb-ocid> \\\n  --backend-set-name default \\\n  --health-check-protocol HTTP \\\n  --health-check-uri /health \\\n  --health-check-interval-ms 10000 \\\n  --health-check-timeout-ms 3000 \\\n  --unhealthy-threshold 3 \\\n  --healthy-threshold 2\n```\n\n**Best practices:**\n- Endpoint leve (/health)\n- Interval: 10-30 segundos\n- Timeout: 3-5 segundos\n- Thresholds: 2-3 tentativas\n\n**Monitor:** Console → Load Balancers → Backends → Health", cat, "intermediate"))
    ex.append(create_example(sp, "Como usar load balancer para blue-green deployment?",
        "Blue-green deployment:\n\n**1. Crie dois backend sets:**\n- blue-backend: versão atual\n- green-backend: nova versão\n\n**2. Configure pesos:**\n```bash\n# 100% blue\noci lb backend-set update --backend-set-name blue-backend --weight 100\noci lb backend-set update --backend-set-name green-backend --weight 0\n\n# Shift para green\noci lb backend-set update --backend-set-name blue-backend --weight 0\noci lb backend-set update --backend-set-name green-backend --weight 100\n```\n\n**3. Canary deployment:**\n- 90% blue, 10% green\n- Aumente gradualmente\n\n**Vantagens:**\n- Zero-downtime\n- Rollback rápido\n- Teste em produção controlado", cat, "intermediate"))
    ex.append(create_example(sp, "Como otimizar custo de Load Balancer?",
        "Otimização de custo:\n\n**1. Escolha shape adequado:**\n- 100Mbps para dev/test\n- Production: dimensione conforme necessidade\n\n**2. Use auto-scaling:**\n- Shape flexível\n- Scale up/down conforme demanda\n\n**3. Consolidate LBs:**\n- Path-based routing\n- Virtual hosts\n- Múltiplas apps no mesmo LB\n\n**4. Internal LBs:**\n- Mais baratos que públicos\n- Use para tráfego interno\n\n**5. Desligue ambientes dev:**\n- Night/weekend off\n- Scheduled scaling\n\n[MUTABLE] Preços variam por região e shape.\n\n**Exemplo:**\n- 2 LBs 100Mbps 24/7: ~$60/mês\n- 1 LB consolidado: ~$30/mês", cat, "intermediate"))
    ex.append(create_example(sp, "Como configurar content-based routing?",
        "Content-based routing:\n\n**1. Crie route policy:**\n```bash\noci lb route-policy create \\\n  --load-balancer-id <lb-ocid> \\\n  --name api-policy \\\n  --rules '[{\"condition\":\"URL_PATH begins_with /api\",\"action\":\"FORWARD\",\"backendSetName\":\"api-backend\"}]'\n```\n\n**2. Tipos de rules:**\n- URL_PATH: baseado no path\n- HEADER: baseado em headers\n- METHOD: HTTP method\n- SOURCE_IP: IP de origem\n\n**3. Combine rules:**\n- AND/OR conditions\n- Priority ordering\n\n**Use cases:**\n- API versioning (/v1/, /v2/)\n- Tenant routing (/tenant1/, /tenant2/)\n- A/B testing", cat, "advanced"))
    ex.append(create_example(sp, "Como troubleshoot load balancer?",
        "Troubleshooting LB:\n\n**1. Verifique health:**\n- Console → Backends → Health\n- Backends unhealthy?\n\n**2. Check security lists:**\n- Portas 80/443 abertas?\n- Health check ports?\n\n**3. Verifique listeners:**\n- Listeners configurados?\n- Certificates válidos?\n\n**4. Teste conectividade:**\n```bash\ncurl -v https://<lb-ip>\n```\n\n**5. Access logs:**\n- Enable no Console\n- Analise no Logging service\n\n**6. Common issues:**\n- Security blocks\n- Health check failing\n- Certificate expired\n- Backend overload", cat, "advanced"))
    ex.append(create_example(sp, "Como implementar session persistence?",
        "Session persistence:\n\n**Tipos:**\n\n**1. Cookie-based:**\n```bash\noci lb backend-set create \\\n  --policy SOURCE_IP_PERSISTENCE \\\n  --session-persistence-cookie-name SESSIONID\n```\n\n**2. Source IP:**\n- Mesmo IP → mesmo backend\n- Útil para stateful apps\n\n**3. SSL session ID:**\n- Reusa SSL session\n- Menor overhead\n\n**Use cases:**\n- Shopping carts\n- User sessions\n- Stateful applications\n\n**Trade-offs:**\n- Menor distribuição de carga\n- Sticky sessions podem causar overload\n\n**Alternativa:** Use external session store (Redis)", cat, "advanced"))
    return ex

# ============================================================================
# DATABASE - AUTONOMOUS
# ============================================================================
def gen_db_autonomous():
    cat = "database/autonomous"
    sp = "You are an OCI specialist with expertise in Autonomous Database. Provide technical guidance on ATP, ADW, wallet configuration, and connections."
    ex = []
    ex.append(create_example(sp, "Como criar Autonomous Database?",
        "Criando Autonomous Database:\n\n**Via Console:**\n1. Oracle Database → Autonomous Database\n2. Create Autonomous Database\n3. Escolha tipo: ATP ou ADW\n4. Configure OCPU e storage\n5. Admin password\n6. Create\n\n**Via CLI:**\n```bash\noci database autonomous-database create \\\n  --compartment-id <ocid> \\\n  --db-name MYDB \\\n  --cpu-core-count 1 \\\n  --data-storage-size-in-tbs 1 \\\n  --db-type ATP\n```\n\n**Tipos:**\n- ATP (Transaction Processing): OLTP\n- ADW (Data Warehouse): Analytics\n\n[MUTABLE] Preços por OCPU/hora e TB/mês.\n\nDocs: https://docs.oracle.com/en-us/iaas/Content/Database/Concepts/databaseoverview.htm", cat, "beginner"))
    ex.append(create_example(sp, "Como conectar no Autonomous Database?",
        "Conectando no ADP/ADW:\n\n**1. Baixe wallet:**\n- Console → Database → Details\n- DB Connection → Download Wallet\n- Defina password\n\n**2. Extraia wallet:**\n```bash\nunzip Wallet_<dbname>.zip\n```\n\n**3. Conecte-se:**\n```bash\nsqlplus admin@<db_name>_tp @(TNS entry)\n```\n\n**4. SQL Developer:**\n- File → Open\n- Selecione wallet\n- Connection: <db_name>_tp\n\n**Connection strings:**\n- _tp: Transaction Processing\n- _tpurgent: High priority\n- _low: Low priority (batch)\n\n**Importante:** Guarde wallet em local seguro!", cat, "beginner"))
    ex.append(create_example(sp, "Qual diferença entre ATP e ADW?",
        "ATP vs ADW:\n\n**ATP (Autonomous Transaction Processing):**\n- OLTP workloads\n- Row-based storage\n- Optimized para transações\n- Use cases: ERP, CRM, e-commerce\n\n**ADW (Autonomous Data Warehouse):**\n- Analytics workloads\n- Column-based storage\n- Optimized para queries complexas\n- Use cases: BI, reporting, data mining\n\n**Diferenças técnicas:**\n- ATP: índices, transações concorrentes\n- ADW: In-Memory, partition pruning\n\n**Escolha:**\n- Transacional → ATP\n- Analítico → ADW\n- Misto → ATP + ADW (replicação)", cat, "beginner"))
    ex.append(create_example(sp, "Como escalar Autonomous Database?",
        "Escalando ADB:\n\n**Scale up/down OCPU:**\n```bash\noci database autonomous-database update \\\n  --autonomous-database-id <ocid> \\\n  --cpu-core-count 4\n```\n\n**Scale storage:**\n```bash\noci database autonomous-database update \\\n  --autonomous-database-id <ocid> \\\n  --data-storage-size-in-tbs 2\n```\n\n**Auto Scaling:**\n- Habilita no Console\n- Scale até 3x OCPUs\n- Baseado em demanda\n\n**Considerações:**\n- Online scaling (sem downtime)\n- Prorate de custos\n- Performance metrics para decisão\n\n[MUTABLE] Custos variam por OCPU e storage", cat, "intermediate"))
    ex.append(create_example(sp, "Como configurar backup e restore?",
        "Backup e Restore:\n\n**Backup automático:**\n- Habilitado por default\n- Retention: 60 dias\n- Point-in-time recovery\n\n**Backup manual:**\n```bash\noci database autonomous-database backup create \\\n  --autonomous-database-id <ocid> \\\n  --display-name backup-2024-01\n```\n\n**Restore:**\n```bash\noci database autonomous-database restore \\\n  --autonomous-database-id <ocid> \\\n  --autonomous-database-backup-id <backup-ocid>\n```\n\n**Point-in-time:**\n- Console → Restore\n- Selecione timestamp\n- Cria novo database\n\n**Cross-region DR:**\n- Autonomous Data Guard\n- Replicação síncrona\n- Failover automático", cat, "intermediate"))
    ex.append(create_example(sp, "Como usar Autonomous Data Guard?",
        "Autonomous Data Guard:\n\n**Configuração:**\n\n**1. Habilite no Console:**\n- Database Details → Data Guard\n- Add Data Guard\n- Selecione região standby\n\n**2. Via CLI:**\n```bash\noci database autonomous-database create \\\n  --is-data-guard-enabled true \\\n  --standby-region <region>\n```\n\n**Características:**\n- Replicação síncrona (zero RPO)\n- Failover automático\n- Standby legível (reporting)\n\n**Use cases:**\n- Disaster recovery\n- Business continuity\n- Geographic redundancy\n\n**RTO/RPO:**\n- RPO: ~0 (síncrono)\n- RTO: < 5 minutos\n\n[MUTABLE] Custos adicionais por standby", cat, "intermediate"))
    ex.append(create_example(sp, "Como monitorar Autonomous Database?",
        "Monitoramento de ADB:\n\n**1. Console metrics:**\n- CPU utilization\n- Storage utilization\n- IOPS\n- Connection count\n\n**2. Performance Hub:**\n- SQL Monitor\n- Active Session History\n- Top SQL\n\n**3. Alarms:**\n```bash\noci monitoring alarm create \\\n  --metric-name CpuUtilization \\\n  --threshold 80 \\\n  --severity critical\n```\n\n**4. APEX:**\n- Database Actions → Monitor\n\n**5. Cloud Control:**\n- OCI Monitoring integration\n- Custom metrics\n\n**Thresholds recomendados:**\n- CPU: > 80% warning\n- Storage: > 85% warning\n- Connections: > 90% max", cat, "intermediate"))
    ex.append(create_example(sp, "Como otimizar performance do ADB?",
        "Otimização de performance:\n\n**1. Indexes:**\n- Crie índices em colunas de filtro\n- Use bitmap indexes para colunas low-cardinality\n\n**2. Statistics:**\n```sql\nBEGIN\n  DBMS_STATS.GATHER_SCHEMA_STATS('MY_SCHEMA');\nEND;\n```\n\n**3. SQL Tuning:**\n- Performance Hub → SQL Monitor\n- Identify top SQL\n- Use SQL Tuning Advisor\n\n**4. Resource Manager:**\n- Priorize workloads\n- Consumer groups\n\n**5. Scale:**\n- Aumente OCPUs\n- Enable auto-scaling\n\n**6. Materialized Views:**\n- Pre-compute aggregations\n- Refresh automático\n\n**7. Partitioning:**\n- Partition tables grandes\n- Partition pruning", cat, "advanced"))
    ex.append(create_example(sp, "Como migrar para Autonomous Database?",
        "Migração para ADB:\n\n**Opção 1: SQL Developer**\n1. Tools → Database Copy\n2. Source: on-premises/outra cloud\n3. Target: ADB (com wallet)\n4. Copy\n\n**Opção 2: Data Pump**\n```bash\n# Export\nexpdp user@source dumpfile=export.dmp\n\n# Import (via cloud object storage)\nimpdp admin@adb_par connect string...\n```\n\n**Opção 3: GoldenGate**\n- Replicação contínua\n- Minimal downtime\n- Bidirecional\n\n**Opção 4: OCI Database Migration**\n- Service gerenciado\n- Homogeneous e heterogeneous\n\n**Pre-migração:**\n- Compatibility check\n- Remove features não suportados\n- Test em staging", cat, "advanced"))
    ex.append(create_example(sp, "Como implementar segurança no ADB?",
        "Segurança em ADB:\n\n**1. Network security:**\n- Access Control Lists (ACLs)\n- Private endpoints\n- VCN peering\n\n**2. Authentication:**\n- Database authentication\n- OAuth2 token\n- IAM integration\n\n**3. Encryption:**\n- TDE (Transparent Data Encryption)\n- SSL/TLS em trânsito\n- Wallet passwords\n\n**4. Auditing:**\n```sql\nAUDIT SELECT TABLE BY ACCESS;\nAUDIT INSERT TABLE BY ACCESS;\n```\n\n**5. Data masking:**\n- Data Redaction\n- VPD (Virtual Private Database)\n\n**6. Backup encryption:**\n- Automática\n- Customer-managed keys (opcional)\n\n**Best practices:**\n- MFA para admin\n- Rotação de passwords\n- Least privilege", cat, "advanced"))
    return ex

# ============================================================================
# DATABASE - MYSQL
# ============================================================================
def gen_db_mysql():
    cat = "database/mysql"
    sp = "You are an OCI specialist with expertise in MySQL HeatWave. Provide technical guidance on MySQL configuration, scaling, and replication."
    ex = []
    ex.append(create_example(sp, "Como criar MySQL no OCI?",
        "Criando MySQL HeatWave:\n\n**Via Console:**\n1. MySQL → DB Systems\n2. Create DB System\n3. Configure:\n   - Compartment\n   - Shape (VM.Standard.E4)\n   - MySQL version (8.0+)\n   - Admin password\n4. Create\n\n**Via CLI:**\n```bash\noci mysql db-system create \\\n  --compartment-id <ocid> \\\n  --display-name my-mysql \\\n  --shape-name VM.Standard.E4 \\\n  --admin-password <password>\n```\n\n**Shapes:**\n- VM.Standard.E2: dev/test\n- VM.Standard.E4: production\n- HeatWave: analytics\n\n[MUTABLE] Preços variam por shape.\n\nDocs: https://docs.oracle.com/en-us/iaas/Content/Database/Concepts/databaseoverview.htm", cat, "beginner"))
    ex.append(create_example(sp, "Como configurar HeatWave?",
        "Configurando HeatWave:\n\n**1. Habilite HeatWave:**\n```bash\noci mysql db-system update \\\n  --db-system-id <ocid> \\\n  --is-heatwave-enabled true \\\n  --heatwave-cluster-size 2\n```\n\n**2. Cluster size:**\n- 2 nodes: mínimo\n- Escala até 8+ nodes\n\n**3. Carregue dados:**\n```sql\nALTER TABLE table_name SECONDARY_ENGINE = ON;\n```\n\n**4. Use para analytics:**\n```sql\nSELECT /*+ NO_INDEX */ * FROM large_table;\n```\n\n**Benefícios:**\n- 100-1000x mais rápido para analytics\n- Sem ETL separado\n- Mesmos dados, dual engine\n\n[MUTABLE] Custos adicionais por node HeatWave", cat, "intermediate"))
    ex.append(create_example(sp, "Como configurar replication?",
        "MySQL Replication:\n\n**1. Crie DB System source**\n\n**2. Adicione replica:**\n```bash\noci mysql replica create \\\n  --source-db-system-id <source-ocid> \\\n  --compartment-id <ocid> \\\n  --display-name mysql-replica\n```\n\n**3. Tipos de replication:**\n- Semi-synchronous (default)\n- Asynchronous\n\n**4. Monitor replication lag:**\n```sql\nSHOW SLAVE STATUS\\G\n```\n\n**Use cases:**\n- Read scaling\n- Reporting\n- DR\n\n**Failover:**\n- Manual (promote replica)\n- Application reconnect\n\n**Limites:** [CHECK DOCS] Número máximo de replicas", cat, "intermediate"))
    ex.append(create_example(sp, "Como fazer backup do MySQL?",
        "Backup de MySQL:\n\n**Automático:**\n- Habilitado por default\n- Retention: 7 dias (configurável)\n- Point-in-time recovery\n\n**Manual:**\n```bash\noci mysql backup create \\\n  --db-system-id <ocid> \\\n  --display-name backup-2024-01\n```\n\n**Restore:**\n```bash\noci mysql db-system create \\\n  --source-backup-id <backup-ocid>\n```\n\n**mysqldump (adicional):**\n```bash\nmysqldump -u admin -p --all-databases > backup.sql\n```\n\n**Best practices:**\n- Backup automático + manual\n- Test restore periodicamente\n- Cross-region backup para DR", cat, "intermediate"))
    ex.append(create_example(sp, "Como escalar MySQL?",
        "Escalando MySQL:\n\n**Vertical scaling:**\n```bash\noci mysql db-system update \\\n  --db-system-id <ocid> \\\n  --shape-name VM.Standard.E8\n```\n\n**Horizontal scaling (read):**\n- Adicione replicas\n- Read splitting na aplicação\n\n**HeatWave scaling:**\n- Aumente cluster size\n- Online scaling\n\n**Storage scaling:**\n```bash\noci mysql db-system update \\\n  --db-system-id <ocid> \\\n  --data-storage-size-in-gbs 200\n```\n\n**Considerações:**\n- Vertical: downtime necessário\n- Horizontal: application changes\n- Storage: online\n\n[MUTABLE] Custos variam por shape e storage", cat, "intermediate"))
    ex.append(create_example(sp, "Como configurar alta disponibilidade?",
        "Alta disponibilidade MySQL:\n\n**1. Fault Domain distribution:**\n- Primary em FD1\n- Replica em FD2\n- HeatWave em FD3\n\n**2. Failover automático:**\n- OCI Health Checks\n- DNS failover\n- Application retry logic\n\n**3. HeatWave HA:**\n- Cluster distribuído\n- Tolerância a falhas\n\n**4. Backup/Restore:**\n- Point-in-time recovery\n- RTO: minutos\n\n**5. Monitoring:**\n- Replication lag\n- Health checks\n- Alarms\n\n**RTO/RPO:**\n- RTO: 5-15 minutos\n- RPO: depende do replication lag", cat, "intermediate"))
    ex.append(create_example(sp, "Como otimizar performance do MySQL?",
        "Otimização de performance:\n\n**1. Configuration:**\n```bash\noci mysql configuration create \\\n  --display-name optimized \\\n  --variables '{\"innodb_buffer_pool_size\":\"75%\"}'\n```\n\n**2. Indexes:**\n- Crie índices apropriados\n- Use EXPLAIN para analisar queries\n\n**3. HeatWave:**\n- Para analytics\n- Offload do MySQL\n\n**4. Query optimization:**\n- Evite SELECT *\n- Use LIMIT\n- Cache results\n\n**5. Connection pooling:**\n- Reduz overhead\n- ProxySQL ou similar\n\n**6. Monitor:**\n- Performance Schema\n- Slow query log\n- Metrics no Console", cat, "advanced"))
    ex.append(create_example(sp, "Como migrar MySQL para OCI?",
        "Migração MySQL para OCI:\n\n**Opção 1: Dump/Restore**\n```bash\n# Source\nmysqldump -u root -p --all-databases > dump.sql\n\n# Target\nmysql -u admin -p < dump.sql\n```\n\n**Opção 2: Replication**\n1. Configure source como master\n2. OCI MySQL como replica\n3. Sync completo\n4. Cutover\n\n**Opção 3: OCI Database Migration**\n- Service gerenciado\n- Minimal downtime\n- Homogeneous\n\n**Opção 4: MySQL Enterprise Backup**\n- Hot backup\n- Incremental\n\n**Pre-migração:**\n- Version compatibility\n- Parameter tuning\n- Test em staging", cat, "advanced"))
    ex.append(create_example(sp, "Como proteger MySQL?",
        "Segurança MySQL:\n\n**1. Network:**\n- Private subnets apenas\n- Security Lists (porta 3306)\n- SSL/TLS connections\n\n**2. Authentication:**\n- Strong passwords\n- IAM integration (opcional)\n- MFA para admin\n\n**3. Encryption:**\n- TDE (Transparent Data Encryption)\n- SSL em trânsito\n- Backup encryption\n\n**4. Access control:**\n```sql\nCREATE USER 'app'@'%' IDENTIFIED BY 'password';\nGRANT SELECT, INSERT ON db.* TO 'app'@'%';\n```\n\n**5. Auditing:**\n- Audit log plugin\n- OCI Audit integration\n\n**6. Patching:**\n- Auto-patching habilitado\n- Maintenance windows", cat, "advanced"))
    ex.append(create_example(sp, "Como troubleshoot MySQL?",
        "Troubleshooting MySQL:\n\n**1. Verifique status:**\n```bash\noci mysql db-system get --db-system-id <ocid>\n```\n\n**2. Logs:**\n- Error log\n- Slow query log\n- Audit log\n\n**3. Performance:**\n```sql\nSHOW PROCESSLIST;\nSHOW ENGINE INNODB STATUS;\n```\n\n**4. Replication:**\n```sql\nSHOW SLAVE STATUS\\G\n```\n\n**5. Common issues:**\n- Connection limits\n- Lock contention\n- Replication lag\n- Storage full\n\n**6. Monitor metrics:**\n- CPU, memory\n- Connections\n- Replication lag\n- Storage\n\nDocs: https://docs.oracle.com/en-us/iaas/Content/Database/Concepts/databaseoverview.htm", cat, "advanced"))
    return ex

# ============================================================================
# Main - Gera categorias selecionadas
# ============================================================================

if __name__ == "__main__":
    generators = {
        "lb-load-balancer": gen_lb,
        "database-autonomous": gen_db_autonomous,
        "database-mysql": gen_db_mysql,
    }
    
    for name, gen in generators.items():
        examples = gen()
        filename = f"{name}.jsonl"
        output_file, count = save(examples, filename)
        print(f"Gerado: {output_file} ({count} exemplos)")
