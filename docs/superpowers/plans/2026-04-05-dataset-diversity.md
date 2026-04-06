# Dataset Diversity & Quality Improvement Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Regenerate the OCI training dataset with 15 response structures (instead of 7 cycling), fix hallucinated SDK model fields, add post-generation validation, and rebuild all data splits.

**Architecture:** Modify `scripts/generate_diverse_v2.py` to add 7 new answer generator functions, create a category-to-structure mapping dict, fix the `OCI_PYTHON_SDK` lookup tables with resource-specific fields, add a post-generation validation pass, then regenerate all 9,940 examples and rebuild splits.

**Tech Stack:** Python 3.12, MLX ecosystem (for later training), JSONL data format

---

## File Structure

| File | Action | Responsibility |
|------|--------|----------------|
| `scripts/generate_diverse_v2.py` | Modify | Main generator — add 7 new answer functions, category mapping, SDK fix, validation |
| `data/curated/*.jsonl` | Regenerate | 71 category files (140 examples each) |
| `data/all_curated.jsonl` | Rebuild | Concatenated dataset |
| `data/all_curated_clean.jsonl` | Rebuild | Validated + deduplicated |
| `data/train.jsonl` | Rebuild | Training split (75%) |
| `data/valid.jsonl` | Rebuild | Validation split (15%) |
| `data/eval.jsonl` | Rebuild | Evaluation split (10%) |
| `docs/validation-report-2026-04-05.md` | Reference | Validation findings that drove these changes |

---

## Chunk 1: New Response Structures (7 new answer functions)

### Task 1: Add _answer_cost_analysis function

**Files:**
- Modify: `scripts/generate_diverse_v2.py` — insert after `_answer_best_practices` (~line 5155)

- [ ] **Step 1: Add _answer_cost_analysis function**

Insert after `_answer_best_practices` (before `_answer_iam_policy`):

```python
def _answer_cost_analysis(category: str, subcat: str, question: str, idx: int, scenario: str) -> str:
    """Generate cost analysis responses with OCI pricing considerations."""
    doc = DOC_LINKS.get(category, "https://docs.oracle.com/iaas/")
    comp = COMPS[idx % len(COMPS)]
    region = REGIONS[idx % len(REGIONS)]
    shape = SHAPES[idx % len(SHAPES)]

    # Category-specific cost breakdowns
    if subcat in ("instances", "scaling", "custom-images"):
        cost_content = f"""**Análise de Custos — Compute ({scenario})**

**Componentes de custo:**
1. **Compute OCPUs**: {shape} com {OCPUS[idx % len(OCPUS)]} OCPUs
2. **Boot Volume**: {STORAGE_SIZES[idx % len(STORAGE_SIZES)]} Block Volume
3. **Networking**: Data egress de {region}
4. **Licenciamento**: BYOL vs Pay-as-you-go

**Otimizações recomendadas:**
- Use shapes preemptíveis para workloads fault-tolerant (até 75% economia)
- Dimensione OCPUs com base em métricas reais (OCI Monitoring)
- Commitment de 1-3 anos para Universal Credits (desconto de 20-60%)
- Desligue instâncias de dev/test fora do horário comercial

**Estimativa mensal:** Consulte [OCI Pricing Calculator](https://www.oracle.com/cloud/costestimator.html) para valores atualizados.

**Referência:** [OCI Compute Pricing](https://www.oracle.com/cloud/compute/pricing/)"""
    elif subcat in ("block", "object", "file"):
        cost_content = f"""**Análise de Custos — Storage ({scenario})**

**Componentes de custo:**
1. **Provisionado vs utilizado**: Block Volume cobra pelo provisionado
2. **Tier de performance**: Higher IOPS = higher cost
3. **Data transfer**: Cross-region replication tem custo adicional
4. **Lifecycle policies**: Archive tier para dados raramente acessados

**Otimizações recomendadas:**
- Use Object Storage Standard para dados frequentemente acessados
- Mova para Archive/Infrequent Access após 30 dias
- Delete unattached Block Volumes (cobrança contínua)
- Compacte backups de Block Volume

**Referência:** [OCI Storage Pricing](https://www.oracle.com/cloud/storage/pricing/)"""
    elif subcat in ("autonomous", "mysql", "postgresql", "nosql", "exadata"):
        cost_content = f"""**Análise de Custos — Database ({scenario})**

**Componentes de custo:**
1. **OCPU/ECPU**: Processamento do banco
2. **Storage**: Database storage com backup automático
3. **Licenciamento**: Oracle Database (incluído no Autonomous)
4. **Cross-region DR**: Data Guard tem custo adicional

**Otimizações recomendadas:**
- Autonomous Database: ECPUs são mais eficientes para workloads variáveis
- Use Always Free Autonomous Database para dev/test
- Pause Autonomous Database quando não em uso
- MySQL HeatWave: inclua analytics sem ETL separado

**Referência:** [OCI Database Pricing](https://www.oracle.com/cloud/database/pricing/)"""
    else:
        cost_content = f"""**Análise de Custos — {subcat.replace("-", " ").title()} ({scenario})**

**Componentes de custo:**
1. **Recurso principal**: Based on usage/provisioned capacity
2. **Storage associado**: Volumes, backups, snapshots
3. **Networking**: Data transfer entre regiões e internet
4. **Serviços complementares**: Monitoring, Logging, Vault

**Otimizações recomendadas:**
- Use OCI Budgets para alertas de gasto
- Tag resources por projeto para chargeback
- Revise recursos não utilizados semanalmente
- Considere Universal Credits para descontos por commitment

**Referência:** [OCI Pricing Calculator](https://www.oracle.com/cloud/costestimator.html)"""

    return f"""{cost_content}

**Dicas de otimização:**
- Monitore utilização real antes de dimensionar
- Automatize start/stop de ambientes non-production
- Use OCI Cost Analysis reports mensalmente
- Avalie serverless (Functions, Autonomous) para workloads variáveis

Documentação: {doc}"""
```

- [ ] **Step 2: Verify syntax**

Run: `source venv/bin/activate && python -m py_compile scripts/generate_diverse_v2.py`
Expected: PASS (may show SyntaxWarning for backticks, which is pre-existing)

---

### Task 2: Add _answer_security_audit function

**Files:**
- Modify: `scripts/generate_diverse_v2.py` — insert after `_answer_cost_analysis`

- [ ] **Step 1: Add _answer_security_audit function**

```python
def _answer_security_audit(category: str, subcat: str, question: str, idx: int, scenario: str) -> str:
    """Generate security audit responses with OCI security best practices."""
    doc = DOC_LINKS.get(category, "https://docs.oracle.com/iaas/")
    comp = COMPS[idx % len(COMPS)]
    group_name = f"developers-{comp.replace('-', '')}"

    security_checks = f"""**Security Audit — {subcat.replace("-", " ").title()} ({scenario})**

**Checklist de Segurança:**

**1. Identity & Access Management**
- [ ] Policies com princípio de menor privilégio
- [ ] Grupos IAM organizados por função (não por pessoa)
- [ ] MFA habilitado para todos os usuários
- [ ] API keys rotacionadas a cada 90 dias
- [ ] Dynamic groups para workloads (não user credentials)

**2. Network Security**
- [ ] Security lists restritivas (deny by default)
- [ ] Network Security Groups por workload
- [ ] WAF habilitado para aplicações web públicas
- [ ] Private endpoints para serviços OCI
- [ ] Sem subnets públicas com acesso direto a databases

**3. Data Protection**
- [ ] Encryption em repouso (OCI Vault com chaves gerenciadas pelo cliente)
- [ ] Encryption em trânsito (TLS 1.2+)
- [ ] Backups automatizados e testados
- [ ] Cross-region replication para DR
- [ ] Object Storage com versionamento habilitado

**4. Monitoring & Compliance**
- [ ] OCI Cloud Guard habilitado
- [ ] Audit log ativado em todos os compartments
- [ ] Alarms para atividades suspeitas
- [ ] Revisão trimestral de acesso
- [ ] Compliance com regulamentações aplicáveis"""

    if subcat in ("vault-keys", "vault-secrets", "encryption"):
        security_checks += f"""

**IAM Policy recomendada:**
\`\`\`
Allow group {group_name} to manage vaults in compartment {comp}
Allow group {group_name} to manage keys in compartment {comp}
Allow group {group_name} to manage secrets in compartment {comp}
Allow service blockstorage to use secret-family in compartment {comp}
\`\`\`"""

    return f"""{security_checks}

**Ferramentas de verificação:**
- OCI Security Zones (bloqueia configurações inseguras)
- OCI Cloud Guard (detecta misconfigurations automaticamente)
- OCI Vulner Scanning (imagens de container e hosts)
- OCI Configuration Auditor (regras CIS Benchmark)

**Referências:**
- [OCI Security Best Practices](https://docs.oracle.com/iaas/Content/Security/Concepts/security.htm)
- [CIS Oracle Cloud Foundations Benchmark](https://www.cisecurity.org/benchmark/oracle_cloud)

Documentação: {doc}"""
```

- [ ] **Step 2: Verify syntax**

Run: `source venv/bin/activate && python -m py_compile scripts/generate_diverse_v2.py`
Expected: PASS

---

### Task 3: Add _answer_performance_tuning function

**Files:**
- Modify: `scripts/generate_diverse_v2.py` — insert after `_answer_security_audit`

- [ ] **Step 1: Add _answer_performance_tuning function**

```python
def _answer_performance_tuning(category: str, subcat: str, question: str, idx: int, scenario: str) -> str:
    """Generate performance tuning responses with OCI benchmarking guidance."""
    doc = DOC_LINKS.get(category, "https://docs.oracle.com/iaas/")
    shape = SHAPES[idx % len(SHAPES)]
    ocpus = OCPUS[idx % len(OCPUS)]

    if subcat in ("instances", "scaling"):
        perf_content = f"""**Performance Tuning — Compute ({scenario})**

**Métricas críticas:**
| Métrica | Threshold | Ação |
|---------|-----------|------|
| CPU Utilization | >80% sustained | Scale up ou adicionar instâncias |
| Memory | >85% | Verificar memory leaks, scale up |
| Network throughput | >70% da capacity | Considerar shape com mais bandwidth |
| Disk IOPS | >80% provisionadas | Aumentar performance tier do Block Volume |

**Otimizações de shape:**
- {shape}: {ocpus} OCPUs — ideal para workloads balanced
- Flexible shapes: ajuste OCPUs e memory independentemente
- Dense I/O: para workloads com alto IOPS local
- GPU: para ML inference e rendering

**Tuning de sistema operacional:**
- Kernel parameters: net.core.somaxconn, fs.file-max
- TCP: enable TCP BBR congestion control
- Storage: use paravirtualized attachment para latência menor
- Oracle Cloud Agent: habilitar todos os plugins"""
    elif subcat in ("block", "object", "file"):
        perf_content = f"""**Performance Tuning — Storage ({scenario})**

**Block Volume Performance Tiers:**
| Tier | IOPS/GB | Throughput/GB | Use Case |
|------|---------|---------------|----------|
| Balanced | 10 | 480KB/s | General purpose |
| Higher Performance | 20 | 960KB/s | Databases |
| Ultra High Performance | 75 | 3.6MB/s | High-throughput workloads |

**Otimizações:**
- Stripe múltiplos Block Volumes para IOPS agregados
- Use NVMe local em Dense I/O shapes para máximo throughput
- Object Storage: multipart upload para arquivos >100MB
- File Storage: ajuste throughput mode (elastic vs provisioned)
- Enable paravirtualized attachment para menor latência"""
    elif subcat in ("autonomous", "mysql", "postgresql"):
        perf_content = f"""**Performance Tuning — Database ({scenario})**

**Autonomous Database:**
- Auto scaling: 1-20x OCPUs baseado em carga
- Auto indexing: Oracle cria/drop índices automaticamente
- SQL Performance Analyzer: testa queries antes de deploy
- AWR reports: identifica bottlenecks

**MySQL HeatWave:**
- HeatWave cluster: in-memory analytics 400x mais rápido
- Auto parallel load: otimiza dados para HeatWave
- Query rewrite: otimiza queries automaticamente

**PostgreSQL:**
- Connection pooling: PgBouncer para >500 conexões
- Autovacuum tuning: baseado em write workload
- Shared buffers: 25% da RAM disponível"""
    else:
        perf_content = f"""**Performance Tuning — {subcat.replace("-", " ").title()} ({scenario})**

**Metodologia de benchmark:**
1. Establish baseline com métricas atuais
2. Identificar bottleneck (CPU, memory, I/O, network)
3. Aplicar otimização isolada
4. Re-medir e comparar
5. Documentar resultados

**Ferramentas OCI:**
- OCI Monitoring: métricas em tempo real
- OCI APM: application performance monitoring
- OCI Logging: logs estruturados para análise
- Service Connector Hub: pipeline de observabilidade"""

    return f"""{perf_content}

**Comandos de diagnóstico:**
\`\`\`bash
# Monitorar CPU e memory
oci monitoring metric-data summarize-metrics \\
  --compartment-id <ocid> \\
  --query-text "CpuUtilization[1m].maximum"

# Verificar throughput de Block Volume
oci bv volume-performance get --volume-id <ocid>
\`\`\`

**Referência:** [OCI Performance Best Practices](https://docs.oracle.com/iaas/Content/performance.htm)

Documentação: {doc}"""
```

- [ ] **Step 2: Verify syntax**

Run: `source venv/bin/activate && python -m py_compile scripts/generate_diverse_v2.py`
Expected: PASS

---

### Task 4: Add _answer_disaster_recovery function

**Files:**
- Modify: `scripts/generate_diverse_v2.py` — insert after `_answer_performance_tuning`

- [ ] **Step 1: Add _answer_disaster_recovery function**

```python
def _answer_disaster_recovery(category: str, subcat: str, question: str, idx: int, scenario: str) -> str:
    """Generate disaster recovery responses with OCI backup and failover guidance."""
    doc = DOC_LINKS.get(category, "https://docs.oracle.com/iaas/")
    region = REGIONS[idx % len(REGIONS)]
    comp = COMPS[idx % len(COMPS)]

    if subcat in ("instances", "scaling", "custom-images"):
        dr_content = f"""**Disaster Recovery — Compute ({scenario})**

**Estratégia de DR:**
| RPO | RTO | Estratégia | Custo |
|-----|-----|------------|-------|
| 24h | Horas | Backup + Restore | Baixo |
| 1h | Minutos | Cross-region replication | Médio |
| 0 | Segundos | Active-Active multi-region | Alto |

**Plano de recuperação:**
1. **Backup**: Custom images + boot volume backups em região secundária
2. **Replicação**: Cross-region copy de custom images
3. **Failover**: Instance pool em região secundária com auto-scaling
4. **DNS**: Steering policy para redirecionar tráfego

**Comandos de recuperação:**
\`\`\`bash
# Criar backup do boot volume
oci compute boot-volume backup create \\
  --boot-volume-id <ocid> \\
  --display-name "dr-backup-$(date +%Y%m%d)" \\
  --compartment-id {comp}

# Cross-region copy
oci compute boot-volume-backup copy \\
  --boot-volume-backup-id <ocid> \\
  --destination-region <secondary-region>
\`\`\`"""
    elif subcat in ("autonomous", "mysql", "postgresql", "exadata"):
        dr_content = f"""**Disaster Recovery — Database ({scenario})**

**Autonomous Database:**
- Autonomous Data Guard: standby cross-region automático
- RPO: 0 (sync replication), RTO: minutos
- Failover manual ou automático via OCI
- Backup automático: retém 60 dias

**MySQL HeatWave:**
- Point-in-time recovery: até 5 minutos
- Cross-region read replica para DR
- Automated backups: retém 35 dias

**Recovery procedure:**
1. Verificar status do primary database
2. Promover standby para primary (Data Guard)
3. Atualizar connection strings na aplicação
4. Validar integridade dos dados
5. Recriar standby na região original"""
    elif subcat in ("block", "object", "file"):
        dr_content = f"""**Disaster Recovery — Storage ({scenario})**

**Block Volume:**
- Volume groups para backup consistente
- Cross-region volume group backup
- Clone de backups para recovery testing

**Object Storage:**
- Cross-region replication (automática)
- Versioning para proteção contra deleção acidental
- Object lifecycle policies para gerenciamento de versões

**File Storage:**
- File system snapshots
- Replicação manual via rsync para região secundária
- Mount targets em múltiplas ADs para HA"""
    else:
        dr_content = f"""**Disaster Recovery — {subcat.replace("-", " ").title()} ({scenario})**

**Framework de DR:**
1. **Assess**: Identificar workloads críticos e RPO/RTO
2. **Protect**: Implementar backups e replicação
3. **Recover**: Documentar runbooks de recuperação
4. **Test**: Simular failover trimestralmente

**OCI DR Services:**
- OCI GoldenGate: replicação de dados em tempo real
- OCI Data Guard: database standby automático
- Cross-region replication: Object Storage, Block Volume
- Resource Manager: infraestrutura como código para rebuild"""

    return f"""{dr_content}

**Runbook de teste de DR:**
1. Notificar equipe de teste
2. Simular falha na região primária
3. Executar failover para região secundária
4. Validar aplicação e dados
5. Failback para região primária
6. Documentar lições aprendidas

**Métricas de sucesso:**
- RPO real ≤ RPO planejado
- RTO real ≤ RTO planejado
- Zero data loss para workloads críticos

Documentação: {doc}"""
```

- [ ] **Step 2: Verify syntax**

Run: `source venv/bin/activate && python -m py_compile scripts/generate_diverse_v2.py`
Expected: PASS

---

### Task 5: Add _answer_monitoring_alerting function

**Files:**
- Modify: `scripts/generate_diverse_v2.py` — insert after `_answer_disaster_recovery`

- [ ] **Step 1: Add _answer_monitoring_alerting function**

```python
def _answer_monitoring_alerting(category: str, subcat: str, question: str, idx: int, scenario: str) -> str:
    """Generate monitoring and alerting responses with OCI Monitoring service."""
    doc = DOC_LINKS.get(category, "https://docs.oracle.com/iaas/")
    comp = COMPS[idx % len(COMPS)]
    region = REGIONS[idx % len(REGIONS)]

    monitoring_content = f"""**Monitoring & Alerting — {subcat.replace("-", " ").title()} ({scenario})**

**Métricas essenciais:**
| Métrica | Namespace | Alarm Threshold | Severidade |
|---------|-----------|-----------------|------------|
| CPU Utilization | oci_computeagent | >80% por 5min | Warning |
| Memory Utilization | oci_computeagent | >85% por 5min | Critical |
| Disk Read/Write Ops | oci_blockstorage | >90% IOPS provisionadas | Warning |
| Network Bytes In/Out | oci_computeagent | >70% bandwidth | Warning |
| Database Connections | oci_database | >80% max connections | Critical |

**Configuração de alarmes:**
\`\`\`bash
# Criar alarme de CPU
oci monitoring alarm create \\
  --compartment-id {comp} \\
  --display-name "high-cpu-{comp}" \\
  --metric-compartment-id {comp} \\
  --namespace oci_computeagent \\
  --query "CpuUtilization[1m]{{resourceId = '<instance-ocid>'}}.mean > 80" \\
  --severity WARNING \\
  --destination-credentials "{{\\"topicId\\": \\"ocid1.onstopic..."}}" \\
  --body "CPU utilization exceeded 80% for 5 minutes" \\
  --repeat-notification-duration PT1H
\`\`\`

**Dashboard recomendado:**
1. **Infrastructure**: CPU, memory, disk, network por instância
2. **Database**: Connections, queries/sec, storage, replication lag
3. **Application**: Response time, error rate, throughput
4. **Cost**: Daily spend, budget alerts, anomaly detection"""

    return f"""{monitoring_content}

**Service Connector Hub — Pipeline de logs:**
1. OCI Logging → Object Storage (archive)
2. OCI Logging → OCI Functions (processamento)
3. OCI Monitoring → Notifications (PagerDuty, Slack)
4. OCI Audit → Streaming (análise em tempo real)

**Best practices:**
- Alarms com duration para evitar alertas de spike
- Escalar notifications por severidade (email → SMS → PagerDuty)
- Dashboards por equipe e por workload
- Revisar thresholds mensalmente baseado em baseline

**Referência:** [OCI Monitoring](https://docs.oracle.com/iaas/Content/monitoring/home.htm)

Documentação: {doc}"""
```

- [ ] **Step 2: Verify syntax**

Run: `source venv/bin/activate && python -m py_compile scripts/generate_diverse_v2.py`
Expected: PASS

---

### Task 6: Add _answer_integration_pattern function

**Files:**
- Modify: `scripts/generate_diverse_v2.py` — insert after `_answer_monitoring_alerting`

- [ ] **Step 1: Add _answer_integration_pattern function**

```python
def _answer_integration_pattern(category: str, subcat: str, question: str, idx: int, scenario: str) -> str:
    """Generate integration pattern responses showing how OCI services work together."""
    doc = DOC_LINKS.get(category, "https://docs.oracle.com/iaas/")
    comp = COMPS[idx % len(COMPS)]
    region = REGIONS[idx % len(REGIONS)]

    if subcat in ("functions", "api-gateway"):
        integration_content = f"""**Integration Pattern — Serverless ({scenario})**

**Arquitetura:**
\`\`\`
Internet → API Gateway → OCI Functions → OCI Services
                                    ↓
                    ┌───────────────┼───────────────┐
                    ↓               ↓               ↓
              Object Storage   Autonomous DB   OCI Vault
\`\`\`

**Fluxo de dados:**
1. Client faz request via API Gateway
2. API Gateway autentica e roteia para Function
3. Function processa, acessa serviços OCI via SDK
4. Response retornada ao client

**Exemplo de integração:**
\`\`\`python
import oci
from fdk import response

def handler(ctx, data: dict = None):
    # Access Object Storage
    object_storage = oci.object_storage.ObjectStorageClient(
        oci.config.from_file()
    )
    namespace = object_storage.get_namespace().data

    # Write result
    object_storage.put_object(
        namespace_name=namespace,
        bucket_name="results",
        object_name="output.json",
        put_object_body=oci.util.to_stream(data)
    )

    return response.Response(
        ctx, response_data={{"status": "success"}},
        headers={{"Content-Type": "application/json"}}
    )
\`\`\`"""
    elif subcat in ("logging", "monitoring", "apm", "stack-monitoring"):
        integration_content = f"""**Integration Pattern — Observability ({scenario})**

**Arquitetura de Observabilidade:**
\`\`\`
Applications → OCI Logging ──┐
                             ↓
Infrastructure → OCI Monitoring → Service Connector Hub
                             ↓
User Experience → OCI APM ───┘
            ↓
    OCI Notifications
            ↓
    PagerDuty / Slack / Email
\`\`\`

**Service Connector Hub flows:**
- Logs → Object Storage (compliance archive)
- Logs → Functions (real-time processing)
- Metrics → Notifications (alerting)
- Audit → Streaming (security analysis)"""
    elif subcat in ("devops", "ci-cd", "resource-manager"):
        integration_content = f"""**Integration Pattern — DevOps ({scenario})**

**CI/CD Pipeline:**
\`\`\`
Git Repo → OCI DevOps Build → OCIR → OKE / Compute
                ↓
        OCI DevOps Deploy
                ↓
        OCI Functions / Compute Instance Group
                ↓
        OCI Monitoring (health check)
\`\`\`

**Infrastructure as Code:**
- Terraform via OCI Resource Manager
- State management em Object Storage
- Plans automáticos em MRs
- Apply via pipeline aprovado"""
    else:
        integration_content = f"""**Integration Pattern — {subcat.replace("-", " ").title()} ({scenario})**

**Serviços OCI que integram com {subcat}:**
1. **OCI Vault**: Encryption keys e secrets management
2. **OCI Monitoring**: Métricas e alertas
3. **OCI Logging**: Logs estruturados
4. **OCI IAM**: Políticas de acesso
5. **OCI Notifications**: Alertas e eventos

**Padrão comum:**
\`\`\`
Recurso OCI → Events → Service Connector Hub → Destination
                                    ↓
                        ┌───────────┼───────────┐
                        ↓           ↓           ↓
                  Functions   Notifications  Streaming
\`\`\`"""

    return f"""{integration_content}

**Dynamic Groups para integração:**
\`\`\`
ALL {{resource.type = 'fnfunc', resource.compartment.id = '{comp}'}}
ALL {{resource.type = 'compute', resource.compartment.id = '{comp}'}}
\`\`\`

**Policies necessárias:**
\`\`\`
Allow dynamic-group {comp}-functions to manage objects in compartment {comp}
Allow dynamic-group {comp}-functions to use secret-family in compartment {comp}
\`\`\`

**Referência:** [OCI Integration Patterns](https://docs.oracle.com/iaas/Content/integration.htm)

Documentação: {doc}"""
```

- [ ] **Step 2: Verify syntax**

Run: `source venv/bin/activate && python -m py_compile scripts/generate_diverse_v2.py`
Expected: PASS

---

### Task 7: Add _answer_migration_guide function

**Files:**
- Modify: `scripts/generate_diverse_v2.py` — insert after `_answer_integration_pattern`

- [ ] **Step 1: Add _answer_migration_guide function**

```python
def _answer_migration_guide(category: str, subcat: str, question: str, idx: int, scenario: str) -> str:
    """Generate migration guide responses for cloud-to-OCI migrations."""
    doc = DOC_LINKS.get(category, "https://docs.oracle.com/iaas/")
    comp = COMPS[idx % len(COMPS)]
    region = REGIONS[idx % len(REGIONS)]

    # Determine source cloud from category
    if "aws" in category:
        source = "AWS"
        mappings = {
            "compute": ("EC2", "OCI Compute", "oci compute instance launch"),
            "storage": ("S3", "Object Storage", "oci os object put"),
            "database": ("RDS", "Autonomous Database", "oci db autonomous-database create"),
        }
    elif "azure" in category:
        source = "Azure"
        mappings = {
            "compute": ("Azure VM", "OCI Compute", "oci compute instance launch"),
            "storage": ("Blob Storage", "Object Storage", "oci os object put"),
            "database": ("Azure SQL", "Autonomous Database", "oci db autonomous-database create"),
        }
    elif "gcp" in category:
        source = "GCP"
        mappings = {
            "compute": ("GCE", "OCI Compute", "oci compute instance launch"),
            "storage": ("Cloud Storage", "Object Storage", "oci os object put"),
            "database": ("Cloud SQL", "Autonomous Database", "oci db autonomous-database create"),
        }
    elif "onprem" in category:
        source = "On-premises"
        mappings = {
            "compute": ("VMware/Hyper-V", "OCI Compute", "oci compute instance launch"),
            "storage": ("NAS/SAN", "File Storage/Block Volume", "oci file-storage export"),
            "database": ("Oracle on-prem", "Exadata Cloud", "oci db system launch"),
        }
    else:
        source = "Cloud provider"
        mappings = {
            "compute": ("VM instances", "OCI Compute", "oci compute instance launch"),
            "storage": ("Cloud storage", "Object Storage", "oci os object put"),
            "database": ("Managed database", "Autonomous Database", "oci db autonomous-database create"),
        }

    subcat_key = subcat.split("-")[-1] if "-" in subcat else subcat
    src_svc = mappings.get(subcat_key, mappings.get("compute", ("Service", "OCI Service", "oci command")))

    migration_content = f"""**Migration Guide — {source} → OCI ({scenario})**

**Mapeamento de serviços ({source} → OCI):**
| {source} | OCI | CLI Command |
|----------|-----|-------------|
| {src_svc[0]} | {src_svc[1]} | `{src_svc[2]}` |

**Fases da migração:**

**Fase 1: Assessment (1-2 semanas)**
- Inventariar workloads e dependências
- Classificar por criticidade e complexidade
- Definir estratégia: rehost, replatform, refactor
- Estimar custos OCI vs {source}

**Fase 2: Foundation (1-2 semanas)**
- Criar VCN, subnets, gateways
- Configurar IAM, compartments, policies
- Estabelecer conectividade (IPSec/FastConnect)
- Configurar monitoring e logging

**Fase 3: Migration (2-4 semanas)**
- Migrar dados primeiro (Database Migration Service)
- Migrar aplicações (lift-and-shift ou replatform)
- Validar funcionalidade e performance
- Executar cutover com mínimo downtime

**Fase 4: Optimization (contínuo)**
- Right-size resources baseado em métricas reais
- Implementar auto-scaling
- Otimizar custos com Universal Credits
- Documentar runbooks OCI"""

    return f"""{migration_content}

**Ferramentas de migração OCI:**
- **Database Migration Service**: Online migration com mínimo downtime
- **Data Transfer Service**: Appliance físico para grandes volumes
- **Object Storage Migration Service**: Migração direta entre clouds
- **VMware Solution**: Lift-and-shift de workloads VMware
- **oci-cli**: Automação de provisioning

**Checklist de cutover:**
- [ ] DNS atualizado para endpoints OCI
- [ ] SSL/TLS certificates instalados
- [ ] Health checks passando
- [ ] Monitoring e alertas ativos
- [ ] Backup configurado
- [ ] Runbook de rollback preparado

**Referência:** [OCI Migration Guide](https://docs.oracle.com/iaas/Content/migration.htm)

Documentação: {doc}"""
```

- [ ] **Step 2: Verify syntax**

Run: `source venv/bin/activate && python -m py_compile scripts/generate_diverse_v2.py`
Expected: PASS

---

## Chunk 2: Category-to-Structure Mapping + Dispatch Logic

### Task 8: Add CATEGORY_RESPONSE_MAP and update _generate_answer dispatch

**Files:**
- Modify: `scripts/generate_diverse_v2.py` — add mapping dict after constants (~line 1250), modify `_generate_answer` dispatch logic (~line 4053-4081)

- [ ] **Step 1: Add CATEGORY_RESPONSE_MAP**

Insert before `_generate_questions` function (~line 1254):

```python
# Maps each category to 5-7 relevant response structures
# Structures: step_by_step, troubleshooting, comparison, architecture,
#             code_first, terraform, python_sdk, best_practices,
#             cost_analysis, security_audit, performance_tuning,
#             disaster_recovery, monitoring_alerting, integration, migration
CATEGORY_RESPONSE_MAP = {
    # Compute
    "compute/instances": ["step_by_step", "troubleshooting", "code_first", "best_practices", "cost_analysis", "performance_tuning", "disaster_recovery"],
    "compute/scaling": ["step_by_step", "troubleshooting", "code_first", "best_practices", "cost_analysis", "performance_tuning", "monitoring_alerting"],
    "compute/custom-images": ["step_by_step", "troubleshooting", "code_first", "best_practices", "disaster_recovery", "cost_analysis"],
    # Storage
    "storage/block": ["step_by_step", "troubleshooting", "code_first", "best_practices", "cost_analysis", "performance_tuning", "disaster_recovery"],
    "storage/object": ["step_by_step", "troubleshooting", "code_first", "best_practices", "cost_analysis", "disaster_recovery", "integration"],
    "storage/file": ["step_by_step", "troubleshooting", "code_first", "best_practices", "cost_analysis", "performance_tuning"],
    # Networking
    "networking/vcn": ["step_by_step", "troubleshooting", "code_first", "architecture", "best_practices", "security_audit", "integration"],
    "networking/security": ["step_by_step", "troubleshooting", "code_first", "best_practices", "security_audit", "monitoring_alerting", "integration"],
    "networking/connectivity": ["step_by_step", "troubleshooting", "code_first", "architecture", "best_practices", "disaster_recovery"],
    # Load Balancer
    "lb/load-balancer": ["step_by_step", "troubleshooting", "code_first", "architecture", "best_practices", "performance_tuning", "disaster_recovery"],
    # Database
    "database/autonomous": ["step_by_step", "troubleshooting", "code_first", "best_practices", "cost_analysis", "disaster_recovery", "performance_tuning"],
    "database/mysql": ["step_by_step", "troubleshooting", "code_first", "best_practices", "cost_analysis", "disaster_recovery", "performance_tuning"],
    "database/postgresql": ["step_by_step", "troubleshooting", "code_first", "best_practices", "cost_analysis", "disaster_recovery", "performance_tuning"],
    "database/nosql": ["step_by_step", "troubleshooting", "code_first", "best_practices", "cost_analysis", "disaster_recovery"],
    "database/exadata": ["step_by_step", "troubleshooting", "code_first", "best_practices", "cost_analysis", "disaster_recovery", "performance_tuning"],
    # Container
    "container/oke": ["step_by_step", "troubleshooting", "code_first", "architecture", "best_practices", "monitoring_alerting", "integration"],
    "container/container-instances": ["step_by_step", "troubleshooting", "code_first", "best_practices", "cost_analysis", "integration"],
    # Serverless
    "serverless/functions": ["step_by_step", "troubleshooting", "code_first", "architecture", "best_practices", "integration", "cost_analysis"],
    "serverless/api-gateway": ["step_by_step", "troubleshooting", "code_first", "architecture", "best_practices", "integration", "security_audit"],
    # Security
    "security/iam-basics": ["step_by_step", "troubleshooting", "code_first", "best_practices", "security_audit", "integration"],
    "security/policies": ["step_by_step", "troubleshooting", "code_first", "best_practices", "security_audit", "integration"],
    "security/dynamic-groups": ["step_by_step", "troubleshooting", "code_first", "best_practices", "security_audit", "integration"],
    "security/vault-keys": ["step_by_step", "troubleshooting", "code_first", "best_practices", "security_audit", "disaster_recovery"],
    "security/vault-secrets": ["step_by_step", "troubleshooting", "code_first", "best_practices", "security_audit", "disaster_recovery"],
    "security/encryption": ["step_by_step", "troubleshooting", "code_first", "best_practices", "security_audit", "compliance"],
    "security/cloud-guard": ["step_by_step", "troubleshooting", "code_first", "best_practices", "security_audit", "monitoring_alerting"],
    "security/waf": ["step_by_step", "troubleshooting", "code_first", "architecture", "best_practices", "security_audit", "monitoring_alerting"],
    "security/federation": ["step_by_step", "troubleshooting", "code_first", "best_practices", "security_audit", "integration"],
    # Migration
    "migration/aws-compute": ["migration", "step_by_step", "code_first", "cost_analysis", "disaster_recovery"],
    "migration/aws-storage": ["migration", "step_by_step", "code_first", "cost_analysis", "disaster_recovery"],
    "migration/aws-database": ["migration", "step_by_step", "code_first", "cost_analysis", "disaster_recovery", "performance_tuning"],
    "migration/azure-compute": ["migration", "step_by_step", "code_first", "cost_analysis", "disaster_recovery"],
    "migration/azure-storage": ["migration", "step_by_step", "code_first", "cost_analysis", "disaster_recovery"],
    "migration/azure-database": ["migration", "step_by_step", "code_first", "cost_analysis", "disaster_recovery", "performance_tuning"],
    "migration/gcp-compute": ["migration", "step_by_step", "code_first", "cost_analysis", "disaster_recovery"],
    "migration/gcp-storage": ["migration", "step_by_step", "code_first", "cost_analysis", "disaster_recovery"],
    "migration/gcp-database": ["migration", "step_by_step", "code_first", "cost_analysis", "disaster_recovery", "performance_tuning"],
    "migration/onprem-compute": ["migration", "step_by_step", "code_first", "cost_analysis", "disaster_recovery"],
    "migration/onprem-storage": ["migration", "step_by_step", "code_first", "cost_analysis", "disaster_recovery"],
    "migration/onprem-database": ["migration", "step_by_step", "code_first", "cost_analysis", "disaster_recovery", "performance_tuning"],
    "migration/onprem-vmware": ["migration", "step_by_step", "code_first", "architecture", "cost_analysis", "disaster_recovery"],
    "migration/data-transfer": ["migration", "step_by_step", "code_first", "cost_analysis", "disaster_recovery"],
    # Terraform
    "terraform/provider": ["terraform", "step_by_step", "code_first", "best_practices", "security_audit"],
    "terraform/compute": ["terraform", "step_by_step", "code_first", "best_practices", "cost_analysis", "performance_tuning"],
    "terraform/storage": ["terraform", "step_by_step", "code_first", "best_practices", "cost_analysis", "disaster_recovery"],
    "terraform/networking": ["terraform", "step_by_step", "code_first", "architecture", "best_practices", "security_audit"],
    "terraform/load-balancer": ["terraform", "step_by_step", "code_first", "architecture", "best_practices", "performance_tuning"],
    "terraform/database": ["terraform", "step_by_step", "code_first", "best_practices", "cost_analysis", "disaster_recovery"],
    "terraform/container": ["terraform", "step_by_step", "code_first", "architecture", "best_practices", "integration"],
    "terraform/serverless": ["terraform", "step_by_step", "code_first", "architecture", "best_practices", "integration"],
    "terraform/security": ["terraform", "step_by_step", "code_first", "best_practices", "security_audit"],
    "terraform/observability": ["terraform", "step_by_step", "code_first", "best_practices", "monitoring_alerting"],
    "terraform/devops": ["terraform", "step_by_step", "code_first", "best_practices", "integration"],
    "terraform/state": ["terraform", "step_by_step", "code_first", "best_practices", "security_audit", "disaster_recovery"],
    # Observability
    "observability/logging": ["step_by_step", "troubleshooting", "code_first", "architecture", "best_practices", "integration", "monitoring_alerting"],
    "observability/monitoring": ["step_by_step", "troubleshooting", "code_first", "best_practices", "monitoring_alerting", "integration", "performance_tuning"],
    "observability/stack-monitoring": ["step_by_step", "troubleshooting", "code_first", "best_practices", "monitoring_alerting", "integration"],
    "observability/apm": ["step_by_step", "troubleshooting", "code_first", "best_practices", "monitoring_alerting", "performance_tuning", "integration"],
    # Troubleshooting
    "troubleshooting/compute": ["troubleshooting", "step_by_step", "code_first", "best_practices", "performance_tuning"],
    "troubleshooting/storage": ["troubleshooting", "step_by_step", "code_first", "best_practices", "performance_tuning"],
    "troubleshooting/connectivity": ["troubleshooting", "step_by_step", "code_first", "best_practices", "security_audit"],
    "troubleshooting/database": ["troubleshooting", "step_by_step", "code_first", "best_practices", "performance_tuning", "disaster_recovery"],
    "troubleshooting/authentication": ["troubleshooting", "step_by_step", "code_first", "best_practices", "security_audit"],
    "troubleshooting/performance": ["troubleshooting", "step_by_step", "code_first", "best_practices", "performance_tuning", "monitoring_alerting"],
    "troubleshooting/functions": ["troubleshooting", "step_by_step", "code_first", "best_practices", "integration"],
    "troubleshooting/oke": ["troubleshooting", "step_by_step", "code_first", "best_practices", "integration", "monitoring_alerting"],
    # DevOps
    "devops/ci-cd": ["step_by_step", "troubleshooting", "code_first", "architecture", "best_practices", "integration"],
    "devops/resource-manager": ["step_by_step", "troubleshooting", "code_first", "best_practices", "integration", "security_audit"],
    "devops/artifacts": ["step_by_step", "troubleshooting", "code_first", "best_practices", "integration"],
    "devops/secrets": ["step_by_step", "troubleshooting", "code_first", "best_practices", "security_audit", "integration"],
}

# Map structure names to dispatch functions
STRUCTURE_DISPATCH = {
    "step_by_step": "_answer_step_by_step",
    "troubleshooting": "_answer_troubleshooting",
    "comparison": "_answer_comparison_table",
    "architecture": "_answer_architecture_diagram",
    "code_first": "_answer_code_first",
    "terraform": "_answer_terraform",
    "python_sdk": "_answer_python_sdk",
    "best_practices": "_answer_best_practices",
    "cost_analysis": "_answer_cost_analysis",
    "security_audit": "_answer_security_audit",
    "performance_tuning": "_answer_performance_tuning",
    "disaster_recovery": "_answer_disaster_recovery",
    "monitoring_alerting": "_answer_monitoring_alerting",
    "integration": "_answer_integration_pattern",
    "migration": "_answer_migration_guide",
}
```

- [ ] **Step 2: Update _generate_answer dispatch logic**

Replace the dispatch logic in `_generate_answer` (~line 4053-4081):

```python
def _generate_answer(category: str, question: str, idx: int) -> str:
    """Generate answer with category-specific response structure."""
    subcat = category.split("/")[1] if "/" in category else category
    scenario = f"{COMPANIES[idx % len(COMPANIES)]} - {PROJECTS[idx % len(PROJECTS)]}"

    # Get category-specific structures
    structures = CATEGORY_RESPONSE_MAP.get(category, [
        "step_by_step", "troubleshooting", "code_first", "best_practices"
    ])

    # Cycle through structures for this category
    structure_name = structures[idx % len(structures)]

    # Dispatch to appropriate answer function
    dispatch_map = {
        "step_by_step": lambda: _answer_step_by_step(category, subcat, question, idx, scenario),
        "troubleshooting": lambda: _answer_troubleshooting(category, subcat, question, idx, scenario),
        "comparison": lambda: _answer_comparison_table(category, subcat, question, idx, scenario),
        "architecture": lambda: _answer_architecture_diagram(category, subcat, question, idx, scenario),
        "code_first": lambda: _answer_code_first(category, subcat, question, idx, scenario),
        "terraform": lambda: _answer_terraform(category, subcat, question, idx, scenario),
        "python_sdk": lambda: _answer_python_sdk(category, subcat, question, idx, scenario),
        "best_practices": lambda: _answer_best_practices(category, subcat, question, idx, scenario),
        "cost_analysis": lambda: _answer_cost_analysis(category, subcat, question, idx, scenario),
        "security_audit": lambda: _answer_security_audit(category, subcat, question, idx, scenario),
        "performance_tuning": lambda: _answer_performance_tuning(category, subcat, question, idx, scenario),
        "disaster_recovery": lambda: _answer_disaster_recovery(category, subcat, question, idx, scenario),
        "monitoring_alerting": lambda: _answer_monitoring_alerting(category, subcat, question, idx, scenario),
        "integration": lambda: _answer_integration_pattern(category, subcat, question, idx, scenario),
        "migration": lambda: _answer_migration_guide(category, subcat, question, idx, scenario),
    }

    return dispatch_map.get(structure_name, dispatch_map["step_by_step"])()
```

- [ ] **Step 3: Verify syntax**

Run: `source venv/bin/activate && python -m py_compile scripts/generate_diverse_v2.py`
Expected: PASS

- [ ] **Step 4: Test dispatch logic**

Run: `source venv/bin/activate && python -c "
from scripts.generate_diverse_v2 import _generate_answer, CATEGORY_RESPONSE_MAP
print(f'Categories mapped: {len(CATEGORY_RESPONSE_MAP)}')
# Test a few categories
for cat in ['compute/instances', 'security/vault-secrets', 'migration/aws-database', 'terraform/networking']:
    structures = CATEGORY_RESPONSE_MAP.get(cat, [])
    print(f'{cat}: {len(structures)} structures → {structures[:3]}...')
    # Test first structure
    answer = _generate_answer(cat, f'Test question for {cat}', 0)
    print(f'  Generated {len(answer)} chars')
print('All dispatch tests passed!')
"
Expected: Shows 71 categories mapped, each generating answers

---

## Chunk 3: SDK Model Fix + Post-Generation Validation

### Task 9: Fix OCI_PYTHON_SDK lookup tables with resource-specific fields

**Files:**
- Modify: `scripts/generate_diverse_v2.py` — update `_answer_python_sdk` function (~line 4943-4967) and add SDK_MODEL_FIELDS dict

- [ ] **Step 1: Add SDK_MODEL_FIELDS dict**

Insert after `OCI_TERRAFORM_RESOURCES` (~line 1250):

```python
# Resource-specific SDK model fields (validated against OCI Python SDK docs)
SDK_MODEL_FIELDS = {
    "compute/instances": {
        "model": "LaunchInstanceDetails",
        "required": ["compartment_id", "availability_domain", "shape", "source_details"],
        "optional": ["display_name", "freeform_tags", "defined_tags", "metadata", "extended_metadata"],
    },
    "storage/block": {
        "model": "CreateVolumeDetails",
        "required": ["compartment_id", "availability_domain"],
        "optional": ["display_name", "size_in_gbs", "vpus_per_gb", "freeform_tags", "backup_policy_id"],
    },
    "storage/object": {
        "model": "CreateBucketDetails",
        "required": ["compartment_id", "name"],
        "optional": ["display_name", "namespace", "public_access_type", "storage_tier", "freeform_tags", "versioning"],
    },
    "storage/file": {
        "model": "CreateFileSystemDetails",
        "required": ["compartment_id", "availability_domain"],
        "optional": ["display_name", "freeform_tags", "defined_tags"],
    },
    "networking/vcn": {
        "model": "CreateVcnDetails",
        "required": ["compartment_id", "cidr_blocks"],
        "optional": ["display_name", "dns_label", "freeform_tags", "is_ipv6enabled"],
    },
    "database/autonomous": {
        "model": "CreateAutonomousDatabaseDetails",
        "required": ["compartment_id", "cpu_core_count", "data_storage_size_in_tbs", "db_name", "admin_password"],
        "optional": ["display_name", "db_workload", "is_free_tier", "license_model", "freeform_tags"],
    },
    "database/mysql": {
        "model": "CreateDbSystemDetails",
        "required": ["compartment_id", "availability_domain", "shape_name", "subnet_id", "display_name"],
        "optional": ["description", "data_storage_size_in_gbs", "freeform_tags", "mysql_version"],
    },
    "security/vault-secrets": {
        "model": "CreateSecretDetails",
        "required": ["compartment_id", "vault_id", "key_id", "secret_content"],
        "optional": ["display_name", "description", "freeform_tags", "defined_tags"],
    },
    "security/vault-keys": {
        "model": "CreateKeyDetails",
        "required": ["compartment_id", "key_shape"],
        "optional": ["display_name", "freeform_tags", "defined_tags", "protection_mode"],
    },
}

def _get_sdk_fields(category: str) -> dict:
    """Get validated SDK model fields for a category."""
    return SDK_MODEL_FIELDS.get(category, {
        "model": "CreateResourceDetails",
        "required": ["compartment_id"],
        "optional": ["display_name", "freeform_tags"],
    })
```

- [ ] **Step 2: Update _answer_python_sdk to use SDK_MODEL_FIELDS**

Replace the `_answer_python_sdk` function body to use `_get_sdk_fields(category)` for generating accurate model fields instead of generic ones with hallucinated `availability_domain` and `shape`.

```python
def _answer_python_sdk(category: str, subcat: str, question: str, idx: int, scenario: str) -> str:
    """Generate Python SDK automation scripts with validated model fields."""
    doc = DOC_LINKS.get(category, "https://docs.oracle.com/iaas/Content/API/SDKDocs/pythonsdk.htm")
    sdk_info = OCI_PYTHON_SDK.get(category, {})
    client_class = sdk_info.get("client", "oci.core.ComputeClient")
    create_method = sdk_info.get("create_method", "launch_instance")
    list_method = sdk_info.get("list_method", "list_instances")
    get_method = sdk_info.get("get_method", "get_instance")
    delete_method = sdk_info.get("delete_method", "terminate_instance")

    fields = _get_sdk_fields(category)
    model_name = fields["model"]
    required_fields = fields["required"]
    optional_fields = fields["optional"][:3]

    # Build model instantiation with correct fields
    model_fields_lines = []
    for f in required_fields:
        if f == "compartment_id":
            model_fields_lines.append(f'    compartment_id=compartment_id,')
        elif f == "availability_domain":
            model_fields_lines.append(f'    availability_domain=ad,')
        elif f == "shape":
            model_fields_lines.append(f'    shape=shape,')
        elif f == "shape_name":
            model_fields_lines.append(f'    shape_name=shape,')
        elif f in ("cidr_blocks",):
            model_fields_lines.append(f'    cidr_blocks=["10.0.0.0/16"],')
        elif f in ("vault_id", "key_id"):
            model_fields_lines.append(f'    {f}="<ocid>",')
        elif f in ("secret_content",):
            model_fields_lines.append(f'    secret_content={{"content": "base64-encoded-value", "content_type": "BASE64"}},')
        elif f in ("key_shape",):
            model_fields_lines.append(f'    key_shape={{"algorithm": "AES", "length": 32}},')
        elif f in ("cpu_core_count", "data_storage_size_in_tbs"):
            model_fields_lines.append(f'    {f}=1,')
        elif f in ("db_name",):
            model_fields_lines.append(f'    {f}="mydb",')
        elif f in ("admin_password",):
            model_fields_lines.append(f'    {f}="<secure-password>",')
        elif f == "name":
            model_fields_lines.append(f'    name="my-resource",')
        elif f == "subnet_id":
            model_fields_lines.append(f'    subnet_id=subnet_id,')
        else:
            model_fields_lines.append(f'    {f}="<value>",')

    for f in optional_fields:
        if f == "display_name":
            model_fields_lines.append(f'    display_name="{scenario}",')
        elif f == "freeform_tags":
            model_fields_lines.append(f'    freeform_tags={{"project": "{PROJECTS[idx % len(PROJECTS)]}", "environment": "dev"}},')
        else:
            model_fields_lines.append(f'    {f}="<value>",')

    model_fields = "\n".join(model_fields_lines)

    return f"""**Automação Python SDK — {subcat.replace("-", " ").title()} ({scenario})**

**1. Instalação:**
\`\`\`bash
pip install oci
\`\`\`

**2. Script de criação:**
\`\`\`python
import oci

# Configuração
config = oci.config.from_file()
compartment_id = "<compartment-ocid>"
client = {client_class}(config)

# Criar recurso
{model_fields}
details = oci.{client_class.split('.')[-1].replace('Client', '')}.models.{model_name}(
{model_fields}
)
response = client.{create_method}(details)
resource = response.data
print(f"Created: {{resource.id}}")
\`\`\`

**3. Listar recursos:**
\`\`\`python
resources = client.{list_method}(compartment_id=compartment_id)
for r in resources.data:
    print(f"{{r.display_name}}: {{r.lifecycle_state}}")
\`\`\`

**4. Consultar recurso específico:**
\`\`\`python
resource = client.{get_method}(resource_id="<resource-ocid>")
print(f"{{resource.data.display_name}}: {{resource.data.lifecycle_state}}")
\`\`\`

**5. Remover recurso:**
\`\`\`python
client.{delete_method}(resource_id="<resource-ocid>")
\`\`\`

**Modelo SDK:** `{model_name}`
**Campos obrigatórios:** {', '.join(required_fields)}

Documentação: {doc}"""
```

- [ ] **Step 3: Verify syntax**

Run: `source venv/bin/activate && python -m py_compile scripts/generate_diverse_v2.py`
Expected: PASS

---

### Task 10: Add post-generation validation

**Files:**
- Modify: `scripts/generate_diverse_v2.py` — add validation function and call in main()

- [ ] **Step 1: Add validate_example function**

Insert before `main()`:

```python
def validate_example(example: dict, category: str) -> list:
    """Validate a generated example for topic relevance and correctness."""
    issues = []
    assistant_content = ""
    user_content = ""
    for msg in example.get("messages", []):
        if msg.get("role") == "assistant":
            assistant_content = msg.get("content", "")
        elif msg.get("role") == "user":
            user_content = msg.get("content", "")

    # Check 1: Topic relevance (category keywords in first 300 chars)
    subcat = category.split("/")[1] if "/" in category else category
    topic_keywords = subcat.replace("-", " ").split()
    first_300 = assistant_content[:300].lower()
    keyword_match = sum(1 for kw in topic_keywords if kw.lower() in first_300)
    if keyword_match == 0:
        issues.append(f"OFF_TOPIC: No topic keywords ({topic_keywords}) in first 300 chars")

    # Check 2: No AWS/Azure contamination (except migration categories)
    if "migration" not in category:
        cross_cloud = ["aws_", "azurerm_", "EC2", "CloudWatch", "AWS Management Console", "Azure Portal"]
        for pattern in cross_cloud:
            if pattern in assistant_content:
                issues.append(f"CROSS_CLOUD: Found '{pattern}' in non-migration category")

    # Check 3: No hallucinated SDK fields
    hallucinated_fields = ["availability_domain", "shape"]
    safe_categories = ["security/vault-secrets", "security/vault-keys", "networking/vcn", "networking/security", "storage/object"]
    if category in safe_categories:
        fields = _get_sdk_fields(category)
        for field in hallucinated_fields:
            if field not in fields.get("required", []) and field not in fields.get("optional", []):
                if f"{field}=" in assistant_content:
                    issues.append(f"HALLUCINATED_FIELD: '{field}' not valid for {fields['model']}")

    # Check 4: Minimum content length
    if len(assistant_content) < 200:
        issues.append(f"TOO_SHORT: Only {len(assistant_content)} chars")

    return issues
```

- [ ] **Step 2: Integrate validation in main()**

In the `main()` function, after building each example, add:

```python
# Validate example
issues = validate_example(example, cat)
if issues:
    validation_errors += 1
    if validation_errors <= 10:  # Print first 10
        print(f"  WARNING: {cat} example {i}: {'; '.join(issues)}")
```

Add counter initialization at start of main:
```python
validation_errors = 0
```

Add summary at end of main:
```python
print(f"\nValidation errors: {validation_errors}/{total}")
```

- [ ] **Step 3: Verify syntax**

Run: `source venv/bin/activate && python -m py_compile scripts/generate_diverse_v2.py`
Expected: PASS

---

## Chunk 4: Regenerate Dataset + Rebuild Splits

### Task 11: Regenerate all dataset files

**Files:**
- Run: `source venv/bin/activate && python scripts/generate_diverse_v2.py`

- [ ] **Step 1: Backup current dataset**

```bash
mkdir -p backup_pre_diversity_$(date +%Y%m%d-%H%M%S)
cp data/curated/*.jsonl backup_pre_diversity_*/
cp data/all_curated.jsonl backup_pre_diversity_*/
cp data/all_curated_clean.jsonl backup_pre_diversity_*/
cp data/train.jsonl backup_pre_diversity_*/
cp data/valid.jsonl backup_pre_diversity_*/
cp data/eval.jsonl backup_pre_diversity_*/
echo "Backup complete"
```

- [ ] **Step 2: Run regeneration**

```bash
source venv/bin/activate && python scripts/generate_diverse_v2.py
```

Expected output:
- 71 category files generated
- 9,940 total examples
- ~15+ unique response structures per category
- Validation errors: 0 (or very few)
- Difficulty distribution: ~30/50/20

- [ ] **Step 3: Verify output**

```bash
# Check file counts
ls data/curated/*.jsonl | wc -l  # Expected: 71
wc -l data/curated/*.jsonl | tail -1  # Expected: 9940 total

# Check uniqueness
source venv/bin/activate && python -c "
import json
from collections import Counter
cats = Counter()
diffs = Counter()
structures = Counter()
with open('data/all_curated.jsonl') as f:
    for line in f:
        d = json.loads(line)
        cats[d['metadata']['category']] += 1
        diffs[d['metadata']['difficulty']] += 1
        structures[d['metadata'].get('structure', 'unknown')] += 1
print(f'Categories: {len(cats)} (expected 71)')
print(f'Total: {sum(cats.values())} (expected 9940)')
print(f'Difficulty: {dict(diffs)}')
print(f'Structures: {dict(structures)}')
# Check each category has 140
bad = [k for k, v in cats.items() if v != 140]
print(f'Categories with != 140 examples: {bad}')
"
```

---

### Task 12: Rebuild dataset splits

**Files:**
- Run: `source venv/bin/activate && python scripts/validate_jsonl.py data/all_curated.jsonl`
- Run: `source venv/bin/activate && python scripts/dedupe_dataset.py data/all_curated.jsonl --remove`
- Run: `source venv/bin/activate && python scripts/build_dataset_fixed.py --input data/all_curated.jsonl`

- [ ] **Step 1: Validate regenerated dataset**

```bash
source venv/bin/activate && python scripts/validate_jsonl.py data/all_curated.jsonl
```
Expected: All 9,940 examples valid

- [ ] **Step 2: Deduplicate**

```bash
source venv/bin/activate && python scripts/dedupe_dataset.py data/all_curated.jsonl --remove
# Copy deduped output
cp data/all_curated_deduped.jsonl data/all_curated_clean.jsonl
```

- [ ] **Step 3: Build splits**

```bash
source venv/bin/activate && python scripts/build_dataset_fixed.py --input data/all_curated_clean.jsonl
```
Expected: train.jsonl (~7,455), valid.jsonl (~1,491), eval.jsonl (~994)

- [ ] **Step 4: Verify splits**

```bash
wc -l data/train.jsonl data/valid.jsonl data/eval.jsonl
# Expected: 7455 + 1491 + 994 = 9940
```

---

## Chunk 5: Update README + Commit

### Task 13: Update README with new dataset stats

**Files:**
- Modify: `README.md` — update Dataset section
- Modify: `README.en-US.md` — update Dataset section

- [ ] **Step 1: Update README.md Dataset section**

Update the dataset section to reflect:
- 15 response structures (instead of 7)
- Category-specific structure mapping
- SDK model field validation
- Post-generation validation

- [ ] **Step 2: Update README.en-US.md**

Same changes in English.

- [ ] **Step 3: Commit all changes**

```bash
git add scripts/generate_diverse_v2.py data/ README.md README.en-US.md
git commit -m "feat: regenerate dataset with 15 response structures, fix SDK hallucinations, add validation

- Added 7 new response structures: cost_analysis, security_audit, performance_tuning, disaster_recovery, monitoring_alerting, integration_pattern, migration_guide
- Added CATEGORY_RESPONSE_MAP: 5-7 structures per category (71 categories)
- Fixed SDK model fields: resource-specific required/optional fields
- Added post-generation validation (topic relevance, cross-cloud, hallucinated fields)
- Regenerated all 9,940 examples with diverse, topic-specific responses
- Updated README with new dataset statistics"
```

---

## Task 14: Update validation report

**Files:**
- Modify: `docs/validation-report-2026-04-05.md` — mark items 1, 2, 3 as resolved

- [ ] **Step 1: Update validation report**

Add a "Resolution" section noting which issues from the original validation have been addressed.

---

## Verification Commands (Final)

After all tasks complete, run:

```bash
# 1. Validate all JSONL
source venv/bin/activate && python scripts/validate_jsonl.py data/all_curated_clean.jsonl
source venv/bin/activate && python scripts/validate_jsonl.py data/eval.jsonl

# 2. Check structure diversity
source venv/bin/activate && python -c "
import json
from collections import Counter
structures = Counter()
with open('data/all_curated.jsonl') as f:
    for line in f:
        d = json.loads(line)
        structures[d['metadata'].get('structure', 'unknown')] += 1
for s, c in sorted(structures.items(), key=lambda x: -x[1]):
    print(f'{s}: {c} ({c/9940*100:.1f}%)')
"

# 3. Check no cross-cloud contamination
source venv/bin/activate && python -c "
import json
issues = 0
with open('data/all_curated_clean.jsonl') as f:
    for line in f:
        d = json.loads(line)
        cat = d['metadata']['category']
        if 'migration' not in cat:
            content = ''.join(m['content'] for m in d['messages'])
            for p in ['aws_instance', 'azurerm_', 'EC2']:
                if p in content:
                    issues += 1
                    print(f'  CROSS_CLOUD: {cat} contains {p}')
print(f'Cross-cloud issues: {issues}')
"

# 4. Verify splits
wc -l data/train.jsonl data/valid.jsonl data/eval.jsonl
```

---

## Risk Assessment

| Risk | Probability | Mitigation |
|------|-------------|------------|
| Generation takes too long | Medium | Script is local, no API calls — should complete in minutes |
| New structures produce invalid content | Low | Post-generation validation catches off-topic/hallucinated content |
| SDK fields still wrong for some categories | Medium | Added 10 categories with validated fields; others use generic fallback |
| Dedup removes too many examples | Low | Threshold 0.95 is conservative; new diversity should reduce duplicates |
| Memory issues on Apple Silicon | Low | Previous run completed successfully with 5451 lines; adding ~500 lines is negligible |
