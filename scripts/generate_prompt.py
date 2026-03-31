#!/usr/bin/env python3
"""
Gerar prompts prontos para uso na geração de dados OCI.

Uso:
    python scripts/generate_prompt.py --all
    python scripts/generate_prompt.py compute/instances
    python scripts/generate_prompt.py --list
"""

import sys
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
TMP_DIR = PROJECT_ROOT / "tmp"
TMP_DIR.mkdir(exist_ok=True)

QUALITY_RULES_PATH = PROJECT_ROOT / "docs/quality-rules.md"
TAXONOMY_PATH = PROJECT_ROOT / "docs/taxonomy.md"

SYSTEM_PROMPTS = {
    "compute/instances": "You are an OCI specialist with expertise in Compute instances. Provide technical guidance on instance creation, shape selection, SSH access, and lifecycle management.",
    "compute/scaling": "You are an OCI specialist with expertise in Compute scaling. Provide technical guidance on instance pools, auto-scaling, and capacity planning.",
    "compute/custom-images": "You are an OCI specialist with expertise in Compute custom images. Provide technical guidance on custom image creation, boot volumes, and instance templates.",
    "storage/block": "You are an OCI specialist with expertise in Block Volume. Provide technical guidance on block storage creation, attachment, performance tiers, and backups.",
    "storage/object": "You are an OCI specialist with expertise in Object Storage. Provide technical guidance on buckets, pre-authenticated requests, lifecycle policies, and versioning.",
    "storage/file": "You are an OCI specialist with expertise in File Storage. Provide technical guidance on NFS mounts, export options, and file system management.",
    "networking/vcn": "You are an OCI specialist with expertise in VCN networking. Provide technical guidance on VCN design, subnets, internet gateway, and NAT gateway.",
    "networking/security": "You are an OCI specialist with expertise in network security. Provide technical guidance on Security Lists, NSGs, and firewall rules.",
    "networking/connectivity": "You are an OCI specialist with expertise in hybrid connectivity. Provide technical guidance on DRG, VPN IPSec, FastConnect, and VCN peering.",
    "lb/load-balancer": "You are an OCI specialist with expertise in Load Balancing. Provide technical guidance on Load Balancer configuration, backend sets, SSL certificates, and health checks.",
    "database/autonomous": "You are an OCI specialist with expertise in Autonomous Database. Provide technical guidance on ATP/ADW creation, wallet management, connection strings, and backups.",
    "database/autonomous-json": "You are an OCI specialist with expertise in Autonomous JSON Database. Provide technical guidance on document stores, JSON collections, and MongoDB compatibility.",
    "database/mysql": "You are an OCI specialist with expertise in OCI MySQL. Provide technical guidance on MySQL HeatWave, configuration, scaling, and replication.",
    "database/postgresql": "You are an OCI specialist with expertise in OCI PostgreSQL. Provide technical guidance on PostgreSQL instances, scaling, and high availability.",
    "database/nosql": "You are an OCI specialist with expertise in Oracle NoSQL Database. Provide technical guidance on table creation, CRUD operations, and consistency.",
    "database/exadata": "You are an OCI specialist with expertise in Exadata Cloud Service. Provide technical guidance on Exadata infrastructure, DB systems, and maintenance.",
    "container/oke": "You are an OCI specialist with expertise in OKE. Provide technical guidance on Kubernetes cluster creation, node pools, and deployments.",
    "container/instances": "You are an OCI specialist with expertise in Container Instances. Provide technical guidance on container deployment and OCIR registry management.",
    "serverless/functions": "You are an OCI specialist with expertise in OCI Functions. Provide technical guidance on function creation, deployment, and invocation.",
    "serverless/api-gateway": "You are an OCI specialist with expertise in API Gateway. Provide technical guidance on API creation, routes, integrations, and authentication.",
    "security/iam-basics": "You are an OCI security specialist with expertise in IAM basics. Provide technical guidance on compartments, users, groups, and authentication.",
    "security/policies": "You are an OCI security specialist with expertise in policies. Provide technical guidance on policy syntax, statements, and common patterns.",
    "security/dynamic-groups": "You are an OCI security specialist with expertise in Dynamic Groups. Provide technical guidance on dynamic group rules, instance principal, and resource principal.",
    "security/federation": "You are an OCI security specialist with expertise in federation. Provide technical guidance on IdCS, Okta, SAML, and OAuth integration.",
    "security/vault-secrets": "You are an OCI security specialist with expertise in Vault secrets. Provide technical guidance on secret creation, retrieval, and rotation.",
    "security/vault-keys": "You are an OCI security specialist with expertise in Vault keys. Provide technical guidance on key creation, encryption, and key policies.",
    "security/encryption": "You are an OCI security specialist with expertise in encryption. Provide technical guidance on volume encryption, BYOK, and customer-managed keys.",
    "security/cloud-guard": "You are an OCI security specialist with expertise in Cloud Guard. Provide technical guidance on security posture, detector recipes, and responder rules.",
    "security/waf": "You are an OCI security specialist with expertise in WAF. Provide technical guidance on Web Application Firewall configuration, access rules, and protection.",
    "migration/aws-compute": "You are an OCI specialist with expertise in AWS to OCI migration. Provide technical guidance on EC2 to OCI Compute migration.",
    "migration/aws-storage": "You are an OCI specialist with expertise in AWS to OCI migration. Provide technical guidance on S3 to Object Storage migration.",
    "migration/aws-database": "You are an OCI specialist with expertise in AWS to OCI migration. Provide technical guidance on RDS to Autonomous Database migration.",
    "migration/azure-compute": "You are an OCI specialist with expertise in Azure to OCI migration. Provide technical guidance on Azure VMs to OCI Compute migration.",
    "migration/azure-database": "You are an OCI specialist with expertise in Azure to OCI migration. Provide technical guidance on Azure SQL to Autonomous Database migration.",
    "migration/gcp-compute": "You are an OCI specialist with expertise in GCP to OCI migration. Provide technical guidance on GCP Compute Engine to OCI Compute migration.",
    "migration/gcp-storage": "You are an OCI specialist with expertise in GCP to OCI migration. Provide technical guidance on GCP Cloud Storage to OCI Object Storage migration.",
    "migration/gcp-database": "You are an OCI specialist with expertise in GCP to OCI migration. Provide technical guidance on GCP Cloud SQL to OCI Database migration.",
    "migration/onprem-compute": "You are an OCI specialist with expertise in on-premises to OCI migration. Provide technical guidance on VM migration to OCI Compute.",
    "migration/onprem-storage": "You are an OCI specialist with expertise in on-premises to OCI migration. Provide technical guidance on file storage migration to OCI.",
    "migration/onprem-vmware": "You are an OCI specialist with expertise in on-premises to OCI migration. Provide technical guidance on VMware migration and lift-and-shift patterns.",
    "migration/onprem-database": "You are an OCI specialist with expertise in on-premises to OCI migration. Provide technical guidance on Oracle to Autonomous Database migration and ZDM.",
    "migration/data-transfer": "You are an OCI specialist with expertise in data migration. Provide technical guidance on GoldenGate, Data Integration, and large-scale data transfers.",
    "terraform/provider": "You are an OCI Terraform specialist with expertise in provider configuration. Provide technical guidance on authentication and provider settings.",
    "terraform/compute": "You are an OCI Terraform specialist with expertise in compute resources. Provide technical guidance on instance, instance pool, custom images, and auto-scaling.",
    "terraform/storage": "You are an OCI Terraform specialist with expertise in storage resources. Provide technical guidance on block volume, object storage, and file storage.",
    "terraform/networking": "You are an OCI Terraform specialist with expertise in networking resources. Provide technical guidance on VCN, subnet, security lists, and gateways.",
    "terraform/load-balancer": "You are an OCI Terraform specialist with expertise in load balancer resources. Provide technical guidance on load balancer, backend sets, and SSL certificates.",
    "terraform/database": "You are an OCI Terraform specialist with expertise in database resources. Provide technical guidance on Autonomous Database, MySQL, PostgreSQL, NoSQL, and Exadata.",
    "terraform/container": "You are an OCI Terraform specialist with expertise in container resources. Provide technical guidance on OKE clusters, node pools, and container instances.",
    "terraform/serverless": "You are an OCI Terraform specialist with expertise in serverless resources. Provide technical guidance on Functions and API Gateway.",
    "terraform/security": "You are an OCI Terraform specialist with expertise in security resources. Provide technical guidance on Vault, Cloud Guard, WAF, and encryption.",
    "terraform/observability": "You are an OCI Terraform specialist with expertise in observability resources. Provide technical guidance on logging, monitoring, and APM.",
    "terraform/devops": "You are an OCI Terraform specialist with expertise in DevOps resources. Provide technical guidance on DevOps, artifacts, and Resource Manager.",
    "terraform/state": "You are an OCI Terraform specialist with expertise in state management. Provide technical guidance on remote state and workspaces.",
    "observability/logging": "You are an OCI specialist with expertise in Logging. Provide technical guidance on log groups, custom logs, and audit logs.",
    "observability/monitoring": "You are an OCI specialist with expertise in Monitoring. Provide technical guidance on metrics, alarms, and notifications.",
    "observability/stack-monitoring": "You are an OCI specialist with expertise in Stack Monitoring. Provide technical guidance on enterprise monitoring and resource monitoring.",
    "observability/apm": "You are an OCI specialist with expertise in APM. Provide technical guidance on distributed tracing and performance diagnostics.",
    "troubleshooting/connectivity": "You are an OCI troubleshooting specialist with expertise in connectivity. Provide diagnostic guidance on network accessibility, routing, and DNS issues.",
    "troubleshooting/performance": "You are an OCI troubleshooting specialist with expertise in performance. Provide diagnostic guidance on CPU, memory, storage, and network performance.",
    "troubleshooting/authentication": "You are an OCI troubleshooting specialist with expertise in authentication. Provide diagnostic guidance on IAM policies, MFA, and federation issues.",
    "troubleshooting/database": "You are an OCI troubleshooting specialist with expertise in database. Provide diagnostic guidance on connection issues, TNS errors, and wallet problems.",
    "troubleshooting/compute": "You are an OCI troubleshooting specialist with expertise in compute. Provide diagnostic guidance on provisioning, boot volumes, and SSH issues.",
    "troubleshooting/storage": "You are an OCI troubleshooting specialist with expertise in storage. Provide diagnostic guidance on bucket access and performance issues.",
    "troubleshooting/oke": "You are an OCI troubleshooting specialist with expertise in OKE. Provide diagnostic guidance on cluster, node pool, and worker node issues.",
    "troubleshooting/functions": "You are an OCI troubleshooting specialist with expertise in Functions. Provide diagnostic guidance on invocation errors and API Gateway issues.",
    "devops/ci-cd": "You are an OCI DevOps specialist with expertise in CI/CD. Provide technical guidance on build pipelines, deploy pipelines, and artifacts.",
    "devops/resource-manager": "You are an OCI DevOps specialist with expertise in Resource Manager. Provide technical guidance on Terraform stacks and drift detection.",
    "devops/artifacts": "You are an OCI DevOps specialist with expertise in Artifacts. Provide technical guidance on OCIR and container registry.",
    "devops/secrets": "You are an OCI DevOps specialist with expertise in secrets. Provide technical guidance on Vault integration and secret injection.",
}

# =============================================================================
# EXAMPLE QUESTIONS - 10 perguntas diversas por tópico (71 topics total)
# Baseado em: Self-Instruct, Persona-based variation, Evol-Instruct patterns
# =============================================================================
EXAMPLE_QUESTIONS = {
    # === OCI CORE ===
    "compute/instances": [
        "Como criar uma instância VM.Standard.E4.Flex no OCI usando o console?",
        "Qual a diferença entre shapes Ampere A1 e Intel Xeon no OCI Compute?",
        "Como configurar acesso SSH com chave pública em uma instância OCI?",
        "Como redimensionar uma instância de VM.Standard.E2 para VM.Standard.E4?",
        "Como parar e iniciar uma instância sem perder dados do boot volume?",
        "Como criar múltiplas instâncias usando instance configuration?",
        "Como resolver erro de 'Out of Host Capacity' ao criar instâncias?",
        "Como configurar cloud-init para automatizar setup pós-criação?",
        "Como attaching secondary VNICs em uma instância existente?",
        "Como fazer backup e restore de boot volumes no OCI?",
    ],
    "compute/scaling": [
        "Como criar um instance pool no OCI Compute?",
        "Como configurar auto-scaling baseado em utilização de CPU?",
        "Qual a diferença entre instance pool e instance configuration?",
        "Como integrar instance pool com Load Balancer?",
        "Como configurar scaling policies com métricas customizadas?",
        "Como resolver instâncias não sendo provisionadas no instance pool?",
        "Como configurar health checker para auto-scaling?",
        "Como limitar o número máximo de instâncias no auto-scaling?",
        "Como migrar workload de instance pool para outro shape?",
        "Como monitorar custos de instance pools com auto-scaling?",
    ],
    "compute/custom-images": [
        "Como criar uma custom image a partir de uma instância existente?",
        "Como importar uma imagem VMDK do VMware para o OCI?",
        "Como exportar uma custom image para Object Storage?",
        "Como criar uma imagem com aplicações pré-configuradas?",
        "Como compartilhar custom images entre compartments?",
        "Como atualizar custom images sem downtime?",
        "Como validar uma custom image antes de usar em produção?",
        "Como criar launch template usando custom image?",
        "Como gerenciar ciclo de vida de custom images?",
        "Como converter imagem QCOW2 para formato compatível com OCI?",
    ],
    "storage/block": [
        "Como criar e attachar um Block Volume em uma instância OCI?",
        "Qual a diferença entre performance tiers VP e BP?",
        "Como configurar backup automático de Block Volumes?",
        "Como clonar um Block Volume existente?",
        "Como migrar Block Volume entre availability domains?",
        "Como resolver performance baixa em Block Volumes?",
        "Como configurar encryption com customer-managed keys?",
        "Como fazer resize de Block Volume sem downtime?",
        "Como monitorar IOPS e throughput de Block Volumes?",
        "Como restaurar Block Volume a partir de backup?",
    ],
    "storage/object": [
        "Como criar um bucket no OCI Object Storage?",
        "Como configurar lifecycle policies para expirar objetos antigos?",
        "Como criar pre-authenticated requests para acesso temporário?",
        "Como habilitar versioning em um bucket?",
        "Como configurar replicação entre regiões?",
        "Como fazer upload de arquivos grandes com multipart?",
        "Como restringir acesso público a um bucket?",
        "Como configurar Object Storage como backend de static website?",
        "Como monitorar custos de Object Storage?",
        "Como migrar dados de S3 para OCI Object Storage?",
    ],
    "storage/file": [
        "Como criar um File Storage no OCI?",
        "Como montar um filesystem NFS em instâncias Linux?",
        "Como configurar export options para controle de acesso?",
        "Como fazer backup de File Storage?",
        "Como resolver problemas de mount NFS?",
        "Como configurar acesso de múltiplas instâncias ao mesmo filesystem?",
        "Como monitorar performance de File Storage?",
        "Como migrar dados de NFS on-premises para OCI File Storage?",
        "Como configurar snapshot automático?",
        "Como resolver erro de 'permission denied' no mount NFS?",
    ],
    "networking/vcn": [
        "Como criar uma VCN com subnets públicas e privadas?",
        "Qual a diferença entre Internet Gateway e NAT Gateway?",
        "Como configurar route tables para subnets privadas?",
        "Como criar VCN com CIDR /16 e planejar subnets?",
        "Como configurar DNS custom em uma VCN?",
        "Como resolver problemas de conectividade entre subnets?",
        "Como migrar workloads para uma nova VCN?",
        "Como configurar service gateway para acessar OCI services?",
        "Como planejar sobreposição de CIDRs em VCNs?",
        "Como monitorar tráfego de rede na VCN?",
    ],
    "networking/security": [
        "Como criar Security Lists com regras de ingress e egress?",
        "Qual a diferença entre Security Lists e Network Security Groups?",
        "Como configurar regras stateless vs stateful?",
        "Como resolver problemas de acesso bloqueado por Security List?",
        "Como configurar NSG para um load balancer?",
        "Como auditar regras de segurança de uma VCN?",
        "Como configurar acesso SSH apenas de IPs específicos?",
        "Como criar regras de egress para atualizações de sistema?",
        "Como migrar de Security Lists para NSGs?",
        "Como troubleshootar conectividade entre NSGs?",
    ],
    "networking/connectivity": [
        "Como criar um VPN IPSec entre on-premises e OCI?",
        "Como configurar FastConnect para conexão dedicada?",
        "Como fazer VCN peering local entre duas VCNs?",
        "Como configurar DRG para hub de conectividade?",
        "Como resolver problemas de roteamento no DRG?",
        "Como configurar remote VCN peering entre regiões?",
        "Como troubleshootar túnel VPN IPSec?",
        "Como configurar BGP no FastConnect?",
        "Como planejar conectividade hybrid cloud?",
        "Como monitorar latência e disponibilidade do FastConnect?",
    ],
    "lb/load-balancer": [
        "Como criar um Load Balancer no OCI?",
        "Como configurar backend set com health checks?",
        "Como adicionar certificado SSL ao Load Balancer?",
        "Como configurar path-based routing?",
        "Como resolver backend servers em status 'Warning'?",
        "Como configurar session persistence?",
        "Como migrar Load Balancer entre subnets?",
        "Como configurar SSL termination no Load Balancer?",
        "Como monitorar métricas do Load Balancer?",
        "Como configurar load balancer para aplicação WebSocket?",
    ],
    # === DATABASE ===
    "database/autonomous": [
        "Como criar um Autonomous Database no OCI?",
        "Como configurar wallet para conexão com ADB?",
        "Como fazer backup e restore de Autonomous Database?",
        "Como escalar CPU e storage de um ADB?",
        "Como configurar acesso seguro com ACL?",
        "Como conectar aplicação Java ao Autonomous Database?",
        "Como resolver erro de conexão com wallet expirado?",
        "Como configurar auto-scaling no ADB?",
        "Como migrar banco Oracle on-premises para ADB?",
        "Como monitorar performance do Autonomous Database?",
    ],
    "database/autonomous-json": [
        "Como criar uma coleção JSON no Autonomous Database?",
        "Como executar queries em documentos JSON no ADB?",
        "Como configurar compatibilidade com MongoDB?",
        "Como fazer CRUD operations em JSON collections?",
        "Como criar índices em campos JSON?",
        "Como migrar dados do MongoDB para ADB JSON?",
        "Como validar schema de documentos JSON?",
        "Como fazer agregações em JSON collections?",
        "Como configurar acesso a JSON collections via REST?",
        "Como troubleshootar performance de queries JSON?",
    ],
    "database/mysql": [
        "Como criar uma instância MySQL HeatWave no OCI?",
        "Como configurar HeatWave cluster para analytics?",
        "Como fazer backup automatizado do MySQL?",
        "Como configurar read replicas no MySQL?",
        "Como migrar MySQL on-premises para OCI?",
        "Como resolver problemas de conexão ao MySQL?",
        "Como configurar high availability no MySQL?",
        "Como monitorar performance do MySQL HeatWave?",
        "Como escalar verticalmente uma instância MySQL?",
        "Como configurar point-in-time recovery?",
    ],
    "database/postgresql": [
        "Como criar uma instância PostgreSQL no OCI?",
        "Como configurar backup automático do PostgreSQL?",
        "Como fazer restore de um backup do PostgreSQL?",
        "Como configurar read replicas no PostgreSQL?",
        "Como migrar PostgreSQL on-premises para OCI?",
        "Como configurar high availability no PostgreSQL?",
        "Como resolver problemas de conexão ao PostgreSQL?",
        "Como monitorar métricas do PostgreSQL no OCI?",
        "Como escalar storage de uma instância PostgreSQL?",
        "Como configurar extensions no PostgreSQL do OCI?",
    ],
    "database/nosql": [
        "Como criar uma tabela no Oracle NoSQL Database?",
        "Como configurar throughput para uma tabela NoSQL?",
        "Como executar operações CRUD no NoSQL?",
        "Como configurar TTL em tabelas NoSQL?",
        "Como escolher entre consistência absoluta e eventual?",
        "Como migrar dados do DynamoDB para Oracle NoSQL?",
        "Como monitorar performance do NoSQL Database?",
        "Como configurar índices secundários?",
        "Como fazer backup de tabelas NoSQL?",
        "Como troubleshootar erros de throttling?",
    ],
    "database/exadata": [
        "Como provisionar Exadata Cloud Service no OCI?",
        "Como configurar database homes no Exadata?",
        "Como aplicar patches no Exadata Cloud?",
        "Como fazer backup de databases no Exadata?",
        "Como migrar Oracle on-premises para Exadata Cloud?",
        "Como configurar Oracle RAC no Exadata?",
        "Como monitorar performance do Exadata?",
        "Como resolver problemas de storage no Exadata?",
        "Como configurar Data Guard no Exadata Cloud?",
        "Como escalar recursos do Exadata Cloud?",
    ],
    # === CONTAINER ===
    "container/oke": [
        "Como criar um cluster OKE no OCI?",
        "Como configurar node pools no OKE?",
        "Como fazer deploy de aplicação no OKE?",
        "Como configurar kubectl para acessar o cluster?",
        "Como integrar OKE com OCI Load Balancer?",
        "Como configurar autoscaling de pods no OKE?",
        "Como resolver problemas de provisioning de nodes?",
        "Como configurar networking no OKE com Flannel?",
        "Como fazer upgrade de versão do Kubernetes no OKE?",
        "Como monitorar saúde do cluster OKE?",
    ],
    "container/instances": [
        "Como criar uma Container Instance no OCI?",
        "Como fazer push de imagem para o OCIR?",
        "Como configurar Container Instance com variáveis de ambiente?",
        "Como conectar Container Instance a uma VCN?",
        "Como resolver erro de pull de imagem no OCIR?",
        "Como configurar health checks em Container Instances?",
        "Como fazer scaling de Container Instances?",
        "Como montar volumes em Container Instances?",
        "Como configurar logging para Container Instances?",
        "Como troubleshootar Container Instance em estado failed?",
    ],
    # === SERVERLESS ===
    "serverless/functions": [
        "Como criar uma Function no OCI Functions?",
        "Como fazer deploy de function usando Fn Project?",
        "Como invocar uma function via HTTP?",
        "Como configurar variáveis de ambiente em functions?",
        "Como conectar function a um banco de dados?",
        "Como resolver timeout em OCI Functions?",
        "Como configurar logging para functions?",
        "Como fazer versionamento de functions?",
        "Como monitorar métricas de OCI Functions?",
        "Como troubleshootar erro de cold start?",
    ],
    "serverless/api-gateway": [
        "Como criar um API Gateway no OCI?",
        "Como configurar routes para OCI Functions?",
        "Como configurar autenticação no API Gateway?",
        "Como configurar rate limiting no API Gateway?",
        "Como integrar API Gateway com backend HTTP?",
        "Como resolver erro 502 do API Gateway?",
        "Como configurar CORS no API Gateway?",
        "Como fazer versionamento de APIs?",
        "Como monitorar métricas do API Gateway?",
        "Como configurar request/response transformation?",
    ],
    # === SECURITY ===
    "security/iam-basics": [
        "Como criar um compartment no OCI?",
        "Como adicionar usuários e grupos no IAM?",
        "Como configurar MFA para usuários?",
        "Como criar e gerenciar API keys?",
        "Como configurar console access para usuários?",
        "Como resolver erro de 'not authorized'?",
        "Como auditar atividades de usuários?",
        "Como configurar password policies?",
        "Como criar auth tokens para Docker?",
        "Como troubleshootar problemas de autenticação?",
    ],
    "security/policies": [
        "Como criar uma IAM policy no OCI?",
        "Qual a sintaxe de uma policy statement?",
        "Como criar policy para acesso a Object Storage?",
        "Como configurar policy em nível de compartment?",
        "Como usar condições em policy statements?",
        "Como resolver conflitos de policies?",
        "Como criar policy para acesso cross-compartment?",
        "Como auditar policies existentes?",
        "Como configurar policy para gerenciamento de instâncias?",
        "Como troubleshootar policy não funcionando?",
    ],
    "security/dynamic-groups": [
        "Como criar um Dynamic Group no OCI?",
        "Como configurar instance principal com Dynamic Groups?",
        "Como usar resource principal em funções?",
        "Como criar rules para Dynamic Groups?",
        "Como resolver erro de matching rules?",
        "Como configurar acesso de instâncias a Object Storage?",
        "Como troubleshootar Dynamic Group não funcionando?",
        "Como auditar Dynamic Groups existentes?",
        "Como configurar Dynamic Group para OKE workers?",
        "Como migrar de user credentials para instance principal?",
    ],
    "security/federation": [
        "Como configurar federation com IdCS?",
        "Como integrar OCI com Okta via SAML?",
        "Como configurar OAuth para aplicações?",
        "Como resolver erros de autenticação SAML?",
        "Como configurar user provisioning automático?",
        "Como troubleshootar federation com Azure AD?",
        "Como configurar SSO para console OCI?",
        "Como mapear grupos externos para compartments?",
        "Como auditar acessos via federation?",
        "Como configurar token lifetime para federation?",
    ],
    "security/vault-secrets": [
        "Como criar um secret no OCI Vault?",
        "Como recuperar um secret via OCI CLI?",
        "Como configurar rotação automática de secrets?",
        "Como integrar Vault com aplicações?",
        "Como resolver erro de acesso ao Vault?",
        "Como configurar Dynamic Group para acesso a secrets?",
        "Como versionar secrets no Vault?",
        "Como auditar acesso a secrets?",
        "Como migrar secrets de outro provider para OCI Vault?",
        "Como troubleshootar secret não encontrado?",
    ],
    "security/vault-keys": [
        "Como criar uma encryption key no OCI Vault?",
        "Como configurar key policies?",
        "Como importar key externa (BYOK)?",
        "Como rotacionar encryption keys?",
        "Como resolver erro de key disabled?",
        "Como configurar HSM para keys?",
        "Como auditar uso de keys?",
        "Como fazer backup de keys?",
        "Como troubleshootar erro de encrypt/decrypt?",
        "Como configurar key delegation?",
    ],
    "security/encryption": [
        "Como configurar encryption em Block Volumes?",
        "Como usar customer-managed keys para storage?",
        "Como configurar BYOK no OCI?",
        "Como resolver erro de key não encontrada?",
        "Como auditar encryption em recursos?",
        "Como migrar de Oracle-managed para customer-managed keys?",
        "Como configurar encryption em Object Storage?",
        "Como troubleshootar problemas de decrypt?",
        "Como configurar envelope encryption?",
        "Como verificar compliance de encryption?",
    ],
    "security/cloud-guard": [
        "Como configurar Cloud Guard no OCI?",
        "Como criar detector recipes customizadas?",
        "Como configurar responder rules?",
        "Como resolver security scores baixos?",
        "Como monitorar security posture?",
        "Como configurar notificações do Cloud Guard?",
        "Como troubleshootar detector não disparando?",
        "Como auditar responder actions?",
        "Como configurar Cloud Guard para múltiplos compartments?",
        "Como integrar Cloud Guard com OCI Logging?",
    ],
    "security/waf": [
        "Como configurar Web Application Firewall no OCI?",
        "Como criar access rules no WAF?",
        "Como configurar rate limiting no WAF?",
        "Como proteger contra SQL injection?",
        "Como resolver falsos positivos no WAF?",
        "Como configurar protection rules?",
        "Como monitorar ameaças bloqueadas?",
        "Como configurar WAF para múltiplos domínios?",
        "Como troubleshootar tráfego bloqueado?",
        "Como configurar bot management no WAF?",
    ],
    # === MIGRATION ===
    "migration/aws-compute": [
        "Como migrar instâncias EC2 para OCI Compute?",
        "Como mapear AWS instance types para OCI shapes?",
        "Como usar OCI Application Migration Service?",
        "Como migrar security groups para Security Lists?",
        "Como resolver incompatibilidade de AMI no OCI?",
        "Como planejar cutover de EC2 para OCI?",
        "Como migrar auto-scaling groups para instance pools?",
        "Como troubleshootar instância não bootando após migração?",
        "Como validar performance pós-migração?",
        "Como migrar user data scripts para cloud-init?",
    ],
    "migration/aws-storage": [
        "Como migrar dados de S3 para OCI Object Storage?",
        "Como usar s5cmd para transferência de dados?",
        "Como configurar replicação de S3 para OCI?",
        "Como migrar EBS snapshots para OCI Block Volumes?",
        "Como resolver erros de transferência de grandes volumes?",
        "Como validar integridade de dados migrados?",
        "Como migrar lifecycle policies do S3?",
        "Como troubleshootar permissões de acesso pós-migração?",
        "Como estimar tempo de migração?",
        "Como migrar pre-signed URLs para PARs?",
    ],
    "migration/aws-database": [
        "Como migrar RDS MySQL para OCI MySQL?",
        "Como migrar RDS PostgreSQL para OCI PostgreSQL?",
        "Como usar Database Migration Service para AWS?",
        "Como migrar Oracle RDS para Autonomous Database?",
        "Como resolver incompatibilidade de engine versions?",
        "Como migrar backups e snapshots de RDS?",
        "Como configurar replicação durante migração?",
        "Como validar dados após migração?",
        "Como troubleshootar erros de conexão pós-migração?",
        "Como planejar downtime mínimo na migração?",
    ],
    "migration/azure-compute": [
        "Como migrar Azure VMs para OCI Compute?",
        "Como mapear Azure VM sizes para OCI shapes?",
        "Como migrar managed disks para Block Volumes?",
        "Como resolver incompatibilidade de VHD?",
        "Como migrar Azure availability sets para instance pools?",
        "Como planejar cutover de Azure para OCI?",
        "Como migrar network security groups para OCI?",
        "Como troubleshootar VM não bootando após migração?",
        "Como validar performance pós-migração?",
        "Como migrar Azure extensions para cloud-init?",
    ],
    "migration/azure-database": [
        "Como migrar Azure SQL para Autonomous Database?",
        "Como usar Database Migration Service para Azure?",
        "Como resolver incompatibilidade de collation?",
        "Como migrar backups do Azure SQL?",
        "Como configurar replicação durante migração?",
        "Como validar dados após migração?",
        "Como troubleshootar erros de conexão pós-migração?",
        "Como migrar stored procedures e functions?",
        "Como planejar downtime mínimo?",
        "Como migrar Azure Database for PostgreSQL para OCI?",
    ],
    "migration/azure-storage": [
        "Como migrar Azure Blob Storage para OCI Object Storage?",
        "Como usar AzCopy para transferência para OCI?",
        "Como migrar containers e blobs?",
        "Como resolver erros de transferência?",
        "Como validar integridade de dados migrados?",
        "Como migrar lifecycle policies do Azure?",
        "Como troubleshootar permissões pós-migração?",
        "Como estimar tempo de migração?",
        "Como migrar SAS tokens para PARs?",
        "Como migrar Azure Files para OCI File Storage?",
    ],
    "migration/gcp-compute": [
        "Como migrar GCP Compute Engine para OCI?",
        "Como mapear GCP machine types para OCI shapes?",
        "Como migrar persistent disks para Block Volumes?",
        "Como resolver incompatibilidade de imagens?",
        "Como migrar GCP instance groups para instance pools?",
        "Como planejar cutover de GCP para OCI?",
        "Como migrar firewall rules para Security Lists?",
        "Como troubleshootar VM não bootando?",
        "Como validar performance pós-migração?",
        "Como migrar startup scripts para cloud-init?",
    ],
    "migration/gcp-storage": [
        "Como migrar GCP Cloud Storage para OCI Object Storage?",
        "Como usar gsutil para transferência para OCI?",
        "Como migrar buckets e objetos?",
        "Como resolver erros de transferência?",
        "Como validar integridade de dados migrados?",
        "Como migrar lifecycle policies?",
        "Como troubleshootar permissões pós-migração?",
        "Como estimar tempo de migração?",
        "Como migrar signed URLs para PARs?",
        "Como migrar GCP persistent disks para OCI?",
    ],
    "migration/gcp-database": [
        "Como migrar Cloud SQL MySQL para OCI MySQL?",
        "Como migrar Cloud SQL PostgreSQL para OCI PostgreSQL?",
        "Como resolver incompatibilidade de versões?",
        "Como migrar backups do Cloud SQL?",
        "Como configurar replicação durante migração?",
        "Como validar dados após migração?",
        "Como troubleshootar erros de conexão?",
        "Como planejar downtime mínimo?",
        "Como migrar Cloud Spanner para OCI NoSQL?",
        "Como migrar stored procedures?",
    ],
    "migration/onprem-compute": [
        "Como migrar VMs VMware para OCI Compute?",
        "Como usar OCI Application Migration Service?",
        "Como converter VMDK para formato OCI?",
        "Como planejar lift-and-shift?",
        "Como resolver incompatibilidade de hardware virtual?",
        "Como migrar configurações de rede?",
        "Como troubleshootar VM não bootando?",
        "Como validar performance pós-migração?",
        "Como planejar cutover com mínimo downtime?",
        "Como migrar scripts de automação?",
    ],
    "migration/onprem-storage": [
        "Como migrar NFS on-premises para OCI File Storage?",
        "Como usar OCI Data Transfer Service?",
        "Como migrar grandes volumes de dados?",
        "Como resolver problemas de transferência?",
        "Como validar integridade de dados?",
        "Como planejar transferência com mínimo impacto?",
        "Como troubleshootar mount points?",
        "Como migrar permissões de arquivos?",
        "Como estimar tempo de migração?",
        "Como configurar sync contínuo durante migração?",
    ],
    "migration/onprem-vmware": [
        "Como migrar VMware para OCI usando VMware Cloud?",
        "Como configurar HCX para migração?",
        "Como planejar lift-and-shift de VMware?",
        "Como resolver incompatibilidade de versões?",
        "Como migrar vCenter para OCI?",
        "Como troubleshootar migração falhando?",
        "Como planejar cutover?",
        "Como validar performance pós-migração?",
        "Como configurar conectividade hybrid?",
        "Como migrar templates e golden images?",
    ],
    "migration/onprem-database": [
        "Como migrar Oracle on-premises para Autonomous Database?",
        "Como usar Zero Downtime Migration (ZDM)?",
        "Como configurar Database Migration Service?",
        "Como resolver incompatibilidade de versões do Oracle?",
        "Como migrar backups e archives?",
        "Como validar dados após migração?",
        "Como troubleshootar erros de conexão?",
        "Como planejar downtime mínimo?",
        "Como migrar stored procedures e packages?",
        "Como configurar Data Guard pós-migração?",
    ],
    "migration/data-transfer": [
        "Como configurar GoldenGate para replicação de dados?",
        "Como usar OCI Data Integration para ETL?",
        "Como transferir petabytes de dados para OCI?",
        "Como usar OCI Data Transfer com discos físicos?",
        "Como configurar replicação contínua?",
        "Como resolver erros de sync no GoldenGate?",
        "Como monitorar progresso de transferência?",
        "Como troubleshootar latência de replicação?",
        "Como validar dados após transferência?",
        "Como planejar cutover de dados?",
    ],
    # === TERRAFORM ===
    "terraform/provider": [
        "Como configurar o provider OCI no Terraform?",
        "Como autenticar com API key no Terraform?",
        "Como usar instance principal com Terraform?",
        "Como configurar múltiplas regiões no provider?",
        "Como resolver erro de autenticação do provider?",
        "Como configurar tenancy e compartment defaults?",
        "Como usar variáveis de ambiente para credenciais?",
        "Como troubleshootar erro de 'not authenticated'?",
        "Como configurar provider version pinning?",
        "Como migrar de API key para instance principal?",
    ],
    "terraform/compute": [
        "Como criar instância OCI com Terraform?",
        "Como configurar instance pool com Terraform?",
        "Como criar custom image resource no Terraform?",
        "Como configurar auto-scaling com Terraform?",
        "Como resolver erro de shape não disponível?",
        "Como gerenciar múltiplas instâncias com count?",
        "Como configurar cloud-init via Terraform?",
        "Como troubleshootar provisioning falhando?",
        "Como importar instância existente para state?",
        "Como configurar boot volume via Terraform?",
    ],
    "terraform/storage": [
        "Como criar Block Volume com Terraform?",
        "Como criar bucket Object Storage com Terraform?",
        "Como configurar File Storage com Terraform?",
        "Como attachar volume a instância via Terraform?",
        "Como resolver erro de compartment quota?",
        "Como configurar backup policies via Terraform?",
        "Como gerenciar lifecycle rules com Terraform?",
        "Como troubleshootar volume não attachando?",
        "Como importar storage existente para state?",
        "Como configurar encryption com Terraform?",
    ],
    "terraform/networking": [
        "Como criar VCN com Terraform?",
        "Como configurar subnets e route tables?",
        "Como criar Security Lists com Terraform?",
        "Como configurar Internet Gateway e NAT?",
        "Como resolver erro de CIDR overlap?",
        "Como criar NSGs com Terraform?",
        "Como configurar VCN peering via Terraform?",
        "Como troubleshootar roteamento?",
        "Como importar VCN existente para state?",
        "Como configurar DNS no Terraform?",
    ],
    "terraform/load-balancer": [
        "Como criar Load Balancer com Terraform?",
        "Como configurar backend sets e listeners?",
        "Como adicionar certificado SSL via Terraform?",
        "Como resolver erro de subnet insuficiente?",
        "Como configurar health checks com Terraform?",
        "Como troubleshootar backend em warning?",
        "Como importar LB existente para state?",
        "Como configurar path-based routing?",
        "Como configurar SSL termination?",
        "Como gerenciar múltiplos backends?",
    ],
    "terraform/database": [
        "Como criar Autonomous Database com Terraform?",
        "Como configurar MySQL HeatWave com Terraform?",
        "Como criar PostgreSQL com Terraform?",
        "Como resolver erro de quota de database?",
        "Como configurar backup policies via Terraform?",
        "Como troubleshootar provisioning falhando?",
        "Como importar database existente para state?",
        "Como configurar wallet via Terraform?",
        "Como configurar networking para database?",
        "Como gerenciar múltiplas databases?",
    ],
    "terraform/container": [
        "Como criar cluster OKE com Terraform?",
        "Como configurar node pools via Terraform?",
        "Como criar Container Instance com Terraform?",
        "Como resolver erro de quota de OKE?",
        "Como configurar networking para OKE?",
        "Como troubleshootar node pool falhando?",
        "Como importar cluster existente para state?",
        "Como configurar add-ons do OKE?",
        "Como gerenciar versões do Kubernetes?",
        "Como configurar OCIR com Terraform?",
    ],
    "terraform/serverless": [
        "Como criar OCI Functions com Terraform?",
        "Como configurar API Gateway com Terraform?",
        "Como resolver erro de deploy de function?",
        "Como configurar application para functions?",
        "Como troubleshootar function não invocando?",
        "Como importar resources existentes para state?",
        "Como configurar routes do API Gateway?",
        "Como configurar autenticação no API Gateway?",
        "Como gerenciar versões de functions?",
        "Como configurar logging para serverless?",
    ],
    "terraform/security": [
        "Como criar Vault com Terraform?",
        "Como configurar secrets e keys via Terraform?",
        "Como criar Cloud Guard resources com Terraform?",
        "Como configurar WAF com Terraform?",
        "Como resolver erro de permissão do Vault?",
        "Como troubleshootar secret não criado?",
        "Como importar security resources para state?",
        "Como configurar encryption com Terraform?",
        "Como gerenciar policies de segurança?",
        "Como configurar dynamic groups com Terraform?",
    ],
    "terraform/observability": [
        "Como configurar Logging com Terraform?",
        "Como criar alarms de Monitoring com Terraform?",
        "Como configurar APM com Terraform?",
        "Como resolver erro de log group não criado?",
        "Como troubleshootar alarm não disparando?",
        "Como importar observability resources?",
        "Como configurar notificações com Terraform?",
        "Como criar métricas customizadas?",
        "Como gerenciar retention policies?",
        "Como configurar Stack Monitoring?",
    ],
    "terraform/devops": [
        "Como criar DevOps project com Terraform?",
        "Como configurar artifacts com Terraform?",
        "Como criar Resource Manager stack com Terraform?",
        "Como resolver erro de permissão do DevOps?",
        "Como troubleshootar pipeline falhando?",
        "Como importar DevOps resources para state?",
        "Como configurar connection com repositórios?",
        "Como gerenciar environments de deploy?",
        "Como configurar triggers de pipeline?",
        "Como integrar com OCIR via Terraform?",
    ],
    "terraform/state": [
        "Como configurar remote state no Object Storage?",
        "Como configurar state locking?",
        "Como usar workspaces no Terraform?",
        "Como resolver conflito de state?",
        "Como troubleshootar state corrompido?",
        "Como migrar de local para remote state?",
        "Como importar resources existentes?",
        "Como fazer backup do state?",
        "Como configurar state sharing entre times?",
        "Como troubleshootar erro de locking?",
    ],
    # === OBSERVABILITY ===
    "observability/logging": [
        "Como criar log groups no OCI Logging?",
        "Como configurar custom logs de aplicações?",
        "Como habilitar audit logs?",
        "Como configurar retention policies?",
        "Como resolver logs não aparecendo?",
        "Como troubleshootar log service não funcionando?",
        "Como configurar log parsing?",
        "Como integrar com OCI Monitoring?",
        "Como exportar logs para Object Storage?",
        "Como monitorar custos de Logging?",
    ],
    "observability/monitoring": [
        "Como criar alarms no OCI Monitoring?",
        "Como configurar métricas customizadas?",
        "Como configurar notificações de alarm?",
        "Como resolver alarm não disparando?",
        "Como troubleshootar métricas não coletadas?",
        "Como configurar dashboard de monitoring?",
        "Como integrar com OCI Notifications?",
        "Como monitorar métricas de instâncias?",
        "Como configurar alertas de threshold?",
        "Como exportar métricas para análise?",
    ],
    "observability/stack-monitoring": [
        "Como configurar Stack Monitoring no OCI?",
        "Como adicionar resources para monitoramento?",
        "Como configurar monitoring de databases?",
        "Como resolver agente não conectado?",
        "Como troubleshootar métricas não coletadas?",
        "Como configurar monitoring de middleware?",
        "Como integrar com OCI Monitoring?",
        "Como criar dashboards customizados?",
        "Como configurar alertas de Stack Monitoring?",
        "Como monitorar múltiplos compartments?",
    ],
    "observability/apm": [
        "Como configurar APM no OCI?",
        "Como instrumentar aplicações para tracing?",
        "Como configurar distributed tracing?",
        "Como resolver traces não aparecendo?",
        "Como troubleshootar performance diagnostics?",
        "Como configurar APM domains?",
        "Como monitorar microservices com APM?",
        "Como integrar APM com Logging?",
        "Como configurar alertas de performance?",
        "Como analisar traces de aplicações Java?",
    ],
    # === TROUBLESHOOTING ===
    "troubleshooting/connectivity": [
        "Como diagnosticar instância inacessível via SSH?",
        "Como troubleshootar problemas de roteamento?",
        "Como resolver erros de DNS no OCI?",
        "Como diagnosticar VPN IPSec caída?",
        "Como troubleshootar FastConnect com problemas?",
        "Como resolver connectivity entre VCNs?",
        "Como diagnosticar problemas de security lists?",
        "Como troubleshootar NAT Gateway não funcionando?",
        "Como resolver problemas de load balancer health checks?",
        "Como diagnosticar latency de rede?",
    ],
    "troubleshooting/performance": [
        "Como diagnosticar CPU alta em instâncias?",
        "Como troubleshootar problemas de memória?",
        "Como resolver IOPS baixos em Block Volumes?",
        "Como diagnosticar network latency?",
        "Como troubleshootar database lenta?",
        "Como resolver throttling de API?",
        "Como diagnosticar bottlenecks de storage?",
        "Como troubleshootar load balancer lento?",
        "Como resolver problemas de throughput de rede?",
        "Como monitorar performance de OKE?",
    ],
    "troubleshooting/authentication": [
        "Como resolver erro 'not authorized' no OCI?",
        "Como troubleshootar problemas de MFA?",
        "Como diagnosticar federation failures?",
        "Como resolver problemas de dynamic groups?",
        "Como troubleshootar API key inválida?",
        "Como resolver erros de policy syntax?",
        "Como diagnosticar problemas de SSO?",
        "Como troubleshootar token expirado?",
        "Como resolver problemas de compartment access?",
        "Como diagnosticar problemas de instance principal?",
    ],
    "troubleshooting/database": [
        "Como resolver erros de conexão ao database?",
        "Como troubleshootar erros TNS?",
        "Como diagnosticar problemas de wallet?",
        "Como resolver database não iniciando?",
        "Como troubleshootar replication falhando?",
        "Como diagnosticar problemas de backup?",
        "Como resolver erros de storage cheio?",
        "Como troubleshootar performance lenta?",
        "Como diagnosticar problemas de high availability?",
        "Como resolver erros de autenticação do database?",
    ],
    "troubleshooting/compute": [
        "Como resolver falha de provisioning de instância?",
        "Como troubleshootar boot volume corrompido?",
        "Como diagnosticar problemas de SSH key?",
        "Como resolver instância em estado 'Stopping'?",
        "Como troubleshootar cloud-init falhando?",
        "Como diagnosticar problemas de shape availability?",
        "Como resolver problemas de secondary VNIC?",
        "Como troubleshootar instância sem rede?",
        "Como diagnosticar problemas de console connection?",
        "Como resolver erros de quota de compute?",
    ],
    "troubleshooting/storage": [
        "Como resolver erro de acesso a bucket?",
        "Como troubleshootar upload failures?",
        "Como diagnosticar performance baixa de storage?",
        "Como resolver problemas de mount NFS?",
        "Como troubleshootar erros de permissão?",
        "Como diagnosticar problemas de backup?",
        "Como resolver erros de quota de storage?",
        "Como troubleshootar versioning não funcionando?",
        "Como diagnosticar problemas de lifecycle policies?",
        "Como resolver problemas de replicação?",
    ],
    "troubleshooting/oke": [
        "Como resolver falha de criação de cluster OKE?",
        "Como troubleshootar node pool não provisionando?",
        "Como diagnosticar worker nodes em erro?",
        "Como resolver problemas de networking no OKE?",
        "Como troubleshootar pods em CrashLoopBackOff?",
        "Como diagnosticar problemas de load balancer no OKE?",
        "Como resolver erros de pull de imagem?",
        "Como troubleshootar problemas de storage no OKE?",
        "Como diagnosticar problemas de upgrade de versão?",
        "Como resolver problemas de autoscaling no OKE?",
    ],
    "troubleshooting/functions": [
        "Como resolver erro de invocação de function?",
        "Como troubleshootar API Gateway 502/504?",
        "Como diagnosticar timeout em functions?",
        "Como resolver problemas de cold start?",
        "Como troubleshootar erros de permissão?",
        "Como diagnosticar problemas de logging?",
        "Como resolver erros de memória insuficiente?",
        "Como troubleshootar problemas de deploy?",
        "Como diagnosticar problemas de variáveis de ambiente?",
        "Como resolver problemas de integração com services?",
    ],
    # === DEVOPS ===
    "devops/ci-cd": [
        "Como criar um pipeline CI/CD básico no OCI DevOps para uma aplicação Node.js?",
        "Qual a diferença entre build pipeline e deploy pipeline no OCI DevOps?",
        "Como configurar um estágio de build que executa testes unitários e gera artefatos Docker?",
        "Como integrar o OCI DevOps com um repositório GitHub para trigger automático de builds?",
        "Como configurar variáveis de ambiente e secrets em um pipeline de deploy?",
        "Como criar um pipeline de deploy canário usando OCI DevOps e Load Balancer?",
        "Como resolver erros de permissão quando o build pipeline tenta acessar o Object Storage?",
        "Como configurar notificações por email quando um pipeline falha ou tem sucesso?",
        "Como criar um pipeline multi-stage com aprovação manual antes do deploy em produção?",
        "Como fazer rollback automático quando health checks falham após um deploy?",
    ],
    "devops/resource-manager": [
        "Como criar uma stack no Resource Manager usando um template Terraform?",
        "Qual a diferença entre plan job e apply job no Resource Manager?",
        "Como configurar drift detection para uma stack existente?",
        "Como importar uma stack Terraform existente para o Resource Manager?",
        "Como resolver conflitos de state quando múltiplos jobs rodam na mesma stack?",
        "Como configurar variáveis de ambiente e secrets em uma stack do Resource Manager?",
        "Como criar um pipeline que usa Resource Manager para deploy automatizado?",
        "Como fazer rollback de uma mudança aplicada pelo Resource Manager?",
        "Como configurar permissões IAM para que equipes específicas acessem stacks?",
        "Como usar módulos Terraform privados com o Resource Manager?",
    ],
    "devops/artifacts": [
        "Como configurar o OCIR para armazenar imagens Docker de um pipeline CI/CD?",
        "Como fazer push de uma imagem Docker para o OCIR usando token de autenticação?",
        "Como configurar políticas de retenção e lifecycle para imagens no OCIR?",
        "Como usar OCI Artifacts para armazenar e distribuir Helm charts?",
        "Como configurar assinatura de imagens Docker no OCIR para segurança?",
        "Como resolver erros de autenticação quando um pipeline não consegue fazer push para o OCIR?",
        "Como configurar access control no OCIR usando IAM policies e dynamic groups?",
        "Como integrar o OCIR com OKE para deploy automatizado de containers?",
        "Como armazenar artifacts genéricos (JAR, ZIP, TAR) no OCI Artifacts?",
        "Como automatizar limpeza de imagens antigas no OCIR usando lifecycle policies?",
    ],
    "devops/secrets": [
        "Como configurar secrets do OCI Vault em um pipeline de deploy do DevOps?",
        "Como injetar credenciais de banco de dados armazenadas no Vault durante um build?",
        "Como rotacionar secrets no Vault sem quebrar pipelines em execução?",
        "Como usar dynamic groups para permitir que instâncias acessem secrets do Vault?",
        "Como configurar variáveis de ambiente sensíveis em um deploy para OKE usando Vault?",
        "Como resolver erros de permissão quando um pipeline não consegue ler secrets do Vault?",
        "Como armazenar e recuperar certificados SSL do Vault para uso em deployments?",
        "Como configurar acesso seguro a API keys de serviços externos via Vault no DevOps?",
        "Como auditar acesso a secrets no Vault para compliance?",
        "Como usar versionamento de secrets no Vault para rollback de credenciais?",
    ],
}


def get_example_questions(topic: str) -> str:
    """Get example questions for a topic from embedded dictionary."""
    questions = EXAMPLE_QUESTIONS.get(topic, [])
    if not questions:
        return ""

    result = "## EXAMPLE QUESTIONS (para inspiração - gere questões originais)\n\n"
    for q in questions:
        result += f"- {q}\n"
    result += "\n"
    return result


def get_topics_from_taxonomy(taxonomy_path: Path) -> list:
    """Extract all topics from taxonomy."""
    content = taxonomy_path.read_text()
    topics = []
    for line in content.split("\n"):
        if line.startswith("#### "):
            topic = line.replace("#### ", "").strip()
            topic = re.sub(r"\s*\(\d+\)\s*$", "", topic)
            topics.append(topic)
    return topics


def get_topic_from_taxonomy(taxonomy_path: Path, topic: str) -> str:
    """Extract topic section from taxonomy."""
    content = taxonomy_path.read_text()
    topic_clean = re.sub(r"\s*\(\d+\)\s*$", "", topic)
    lines = content.split("\n")
    in_topic = False
    topic_lines = []
    for line in lines:
        if line.startswith("#### "):
            if in_topic:
                break
            line_clean = re.sub(r"\s*\(\d+\)\s*$", "", line)
            if topic_clean in line_clean:
                in_topic = True
                topic_lines.append(line)
        elif in_topic:
            if line.startswith("### ") or line.startswith("## "):
                break
            topic_lines.append(line)
    return "\n".join(topic_lines)


def generate_prompt(topic: str) -> str:
    """Generate the complete prompt for a topic."""
    quality_rules = QUALITY_RULES_PATH.read_text()
    topic_info = get_topic_from_taxonomy(TAXONOMY_PATH, topic)
    system_prompt = SYSTEM_PROMPTS.get(topic, "You are an OCI specialist.")
    example_questions = get_example_questions(topic)

    # Build diversity section based on topic category
    category = topic.split("/")[0]
    diversity_guidance = _get_diversity_guidance(category, topic)

    prompt = f"""# OCI Dataset Generation - {topic}

## QUALITY RULES (OBRIGATÓRIO - SIGA À RISCA)

{quality_rules}

---

## TOPIC: {topic}

{topic_info}

---

## SYSTEM PROMPT (para usar no JSONL)

{system_prompt}

---

{example_questions}---

## DIVERSITY REQUIREMENTS (OBRIGATÓRIO)

{diversity_guidance}

---

## SUAS REGRAS DE EXECUÇÃO

1. Você DEVE seguir OBRIGATORIAMENTE todas as regras em "QUALITY RULES" acima
2. Gere APENAS exemplos para o topic "{topic}"
3. Use APENAS as informações presentes em "TOPIC: {topic}"
4. Não invente informações que não estão nos docs OCI
5. Não use preços ou limites sem marcar [MUTABLE] ou [CHECK DOCS]
6. Se EXAMPLE QUESTIONS estiver presente, use como INSPIRAÇÃO para criar questões DIVERSAS e ORIGINAIS (não copie verbatim)
7. Cada exemplo DEVE ter um cenário diferente - NÃO repita o mesmo caso de uso
8. Varie os contextos: diferentes personas, diferentes níveis de complexidade, diferentes casos de uso reais

---

## OUTPUT FORMAT

Gere EXATAMENTE 10 exemplos em formato JSONL.

**UM objeto JSON por linha** - cada linha é um objeto JSON completo.

```
{{"messages": [...], "metadata": {{"category": "{topic}", "difficulty": "beginner|intermediate|advanced", "source": "generated"}}}}
{{"messages": [...], "metadata": {{"category": "{topic}", "difficulty": "beginner|intermediate|advanced", "source": "generated"}}}}
... (10 linhas total)
```

---

## JSONL RULES (CRÍTICO - SIGA EXATAMENTE)

1. **UM objeto JSON por linha** - sem arrays, sem wrapper, sem markdown
2. **Escape todas as aspas dentro de strings**: " (aspas) → \\" (backslash aspas)
3. **Escape newlines dentro de strings**: quebra de linha → \\n
4. **Escape backslashes**: \\ (backslash) → \\\\
5. **metadata é OBRIGATÓRIO** em cada objeto
6. **metadata deve ficar FORA do array messages!**

**ESTRUTURA CORRETA (faça exatamente assim!):**
```json
{{"messages": [
  {{"role": "system", "content": "..."}},
  {{"role": "user", "content": "..."}},
  {{"role": "assistant", "content": "..."}}
], "metadata": {{"category": "...", "difficulty": "...", "source": "generated"}}}}
```

**ESTRUTURA ERRADA (NUNCA faça assim!):**
```json
{{"messages": [
  {{"role": "system", "content": "..."}},
  {{"role": "user", "content": "..."}},
  {{"role": "assistant", "content": "..."}},
  {{"metadata": {{"category": "..."}}}}
]}}
```

⚠️ **ATENÇÃO**: O metadata DEVE ficar na mesma linha que o messages, como um sibling key, NUNCA dentro do array messages!

---

## DISTRIBUIÇÃO DE DIFICULDADE
- beginner: ~30% dos exemplos (3 exemplos)
- intermediate: ~50% dos exemplos (5 exemplos)
- advanced: ~20% dos exemplos (2 exemplos)

---

## EXEMPLO DE FORMATO DE RESPOSTA

```json
{{"messages": [
  {{"role": "system", "content": "You are an OCI specialist..."}},
  {{"role": "user", "content": "Como configurar..."}},
  {{"role": "assistant", "content": "Para configurar...\\n\\n1. Step one\\n2. Step two\\n\\n[MUTABLE] Note about prices."}}
], "metadata": {{"category": "example/topic", "difficulty": "intermediate", "source": "generated"}}}}
```

⚠️ **ERRO COMUM**: O metadata deve ficar FORA do array messages, não dentro!

---

## SUA TAREFA

Gere EXATAMENTE 10 exemplos diversos para o topic: **{topic}**

- Mistura de dificuldades: 3 beginner, 5 intermediate, 2 advanced
- Cenários reais de OCI - cada exemplo com um caso de uso diferente
- Use Português (BR) para perguntas do usuário
- Formato JSONL, uma linha por exemplo
- SIGA TODAS as regras de qualidade acima
- NÃO repita cenários - cada exemplo deve ser único
"""
    return prompt


def _get_diversity_guidance(category: str, topic: str) -> str:
    """Get diversity guidance based on topic category."""
    guidance = {
        "compute": """Varie os exemplos entre:
- Diferentes shapes (Ampere A1, Intel Xeon, AMD)
- Diferentes cenários (web servers, databases, batch processing)
- Diferentes personas (sysadmin, devops engineer, architect)
- Diferentes problemas (provisioning, performance, cost optimization)""",
        "storage": """Varie os exemplos entre:
- Diferentes tipos de storage (block, object, file)
- Diferentes casos de uso (backup, archive, active data)
- Diferentes personas (DBA, developer, data engineer)
- Diferentes problemas (performance, cost, security)""",
        "networking": """Varie os exemplos entre:
- Diferentes componentes (VCN, subnets, gateways, DRG)
- Diferentes cenários (single-tier, multi-tier, hybrid)
- Diferentes personas (network engineer, architect, security admin)
- Diferentes problemas (connectivity, security, performance)""",
        "database": """Varie os exemplos entre:
- Diferentes engines (Autonomous, MySQL, PostgreSQL, NoSQL)
- Diferentes casos de uso (OLTP, analytics, document store)
- Diferentes personas (DBA, developer, data architect)
- Diferentes problemas (performance, availability, migration)""",
        "container": """Varie os exemplos entre:
- Diferentes componentes (OKE, Container Instances, OCIR)
- Diferentes cenários (microservices, batch jobs, web apps)
- Diferentes personas (DevOps, SRE, developer)
- Diferentes problemas (deployment, scaling, networking)""",
        "serverless": """Varie os exemplos entre:
- Diferentes services (Functions, API Gateway)
- Diferentes casos de uso (event-driven, REST APIs, webhooks)
- Diferentes personas (developer, architect, DevOps)
- Diferentes problemas (performance, integration, debugging)""",
        "security": """Varie os exemplos entre:
- Diferentes componentes (IAM, Vault, Cloud Guard, WAF)
- Diferentes cenários (access control, encryption, compliance)
- Diferentes personas (security admin, auditor, developer)
- Diferentes problemas (authorization, authentication, monitoring)""",
        "migration": """Varie os exemplos entre:
- Diferentes origens (AWS, Azure, GCP, on-premises)
- Diferentes workloads (compute, storage, database)
- Diferentes personas (migration specialist, architect, DBA)
- Diferentes problemas (compatibility, performance, downtime)""",
        "terraform": """Varie os exemplos entre:
- Diferentes resources (compute, storage, networking, database)
- Diferentes cenários (greenfield, import, migration)
- Diferentes personas (DevOps, infrastructure engineer, architect)
- Diferentes problemas (state management, dependencies, errors)""",
        "observability": """Varie os exemplos entre:
- Diferentes services (Logging, Monitoring, APM, Stack Monitoring)
- Diferentes casos de uso (troubleshooting, alerting, compliance)
- Diferentes personas (SRE, developer, operations)
- Diferentes problemas (missing data, false alerts, performance)""",
        "troubleshooting": """Varie os exemplos entre:
- Diferentes sintomas (errors, timeouts, performance degradation)
- Diferentes componentes afetados (compute, network, storage, database)
- Diferentes personas (support engineer, SRE, developer)
- Diferentes níveis de severidade (critical, warning, informational)""",
        "devops": """Varie os exemplos entre:
- Diferentes componentes (CI/CD, Resource Manager, Artifacts, Secrets)
- Diferentes cenários (build, deploy, test, monitor)
- Diferentes personas (DevOps engineer, developer, release manager)
- Diferentes problemas (failures, performance, security)""",
        "lb": """Varie os exemplos entre:
- Diferentes configurações (HTTP, TCP, SSL)
- Diferentes cenários (web apps, APIs, microservices)
- Diferentes personas (network engineer, architect, developer)
- Diferentes problemas (health checks, SSL, routing)""",
    }
    return guidance.get(
        category,
        "Varie os exemplos entre diferentes cenários, personas e problemas para garantir diversidade.",
    )


def list_topics():
    """Lista todos os topics disponíveis."""
    topics = get_topics_from_taxonomy(TAXONOMY_PATH)
    print(f"\nTopics disponíveis ({len(topics)} total):\n")
    for topic in topics:
        print(f"  - {topic}")
    print(f"\nUso:")
    print(f"  python scripts/generate_prompt.py compute/instances")
    print(f"  python scripts/generate_prompt.py --all")


def generate_all_prompts():
    """Gera prompts para todos os topics."""
    topics = get_topics_from_taxonomy(TAXONOMY_PATH)
    print(f"\nGerando prompts para {len(topics)} topics...\n")
    for i, topic in enumerate(topics, 1):
        print(f"[{i}/{len(topics)}] {topic}...", end=" ")
        prompt = generate_prompt(topic)
        output_file = TMP_DIR / f"prompt_{topic.replace('/', '-')}.md"
        output_file.write_text(prompt)
        print(f"✓ salvo em {output_file.name}")
    print(f"\n✅ Todos os prompts gerados em: {TMP_DIR}/")
    print(f"\nSaída: 1 arquivo por topic em data/curated/[topic].jsonl")


def main():
    if len(sys.argv) == 1 or sys.argv[1] == "--all":
        generate_all_prompts()
    elif sys.argv[1] == "--list":
        list_topics()
    elif sys.argv[1] == "--help":
        print(__doc__)
    else:
        # Handle multiple topics
        topics = [arg for arg in sys.argv[1:] if not arg.startswith("--")]
        if not topics:
            print(__doc__)
            return

        for topic in topics:
            print(f"Gerando prompt para topic: {topic}\n")
            prompt = generate_prompt(topic)
            output_file = TMP_DIR / f"prompt_{topic.replace('/', '-')}.md"
            output_file.write_text(prompt)
            print(f"Prompt salvo em: {output_file}")
            print(f"\n{'=' * 60}\n")
            print(prompt)


if __name__ == "__main__":
    main()
