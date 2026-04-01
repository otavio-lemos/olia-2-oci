#!/usr/bin/env python3
"""
OCI Specialist LLM - Data Generator - Parte 2
Gera categorias restantes de oci-core
"""

import json
from pathlib import Path

OUTPUT_DIR = Path("/Users/otaviolemos/ml/olia-2-oci/data/curated")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def create_example(system_prompt, user_question, assistant_answer, category, difficulty):
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
    output_file = OUTPUT_DIR / filename
    with open(output_file, 'w', encoding='utf-8') as f:
        for example in examples:
            f.write(json.dumps(example, ensure_ascii=False) + '\n')
    return output_file, len(examples)

# NETWORKING - VCN
def gen_networking_vcn():
    category = "networking/vcn"
    sp = "You are an OCI specialist with expertise in VCN networking. Provide technical guidance on VCN design, subnets, gateways, and routing."
    examples = []
    
    examples.append(create_example(sp, "Como criar uma VCN no OCI?",
        "Criando VCN:\n\n**Via Console:**\n1. Networking → Virtual Cloud Networks\n2. Create VCN\n3. Nome e compartment\n4. CIDR block (ex: 10.0.0.0/16)\n5. DNS label\n6. Create\n\n**Via CLI:**\n```bash\noci network vcn create --compartment-id <ocid> --cidr-block 10.0.0.0/16 --display-name my-vcn\n```\n\n**CIDR recommendations:**\n- /16 para VCN principal\n- /24 para subnets\n- Sobreposição com on-premises: evitar\n\nDocs: https://docs.oracle.com/en-us/iaas/Content/Network/Concepts/overview.htm", category, "beginner"))
    
    examples.append(create_example(sp, "Como criar subnets públicas e privadas?",
        "Criando subnets:\n\n**Subnet Pública:**\n```bash\noci network subnet create \\\n  --compartment-id <ocid> \\\n  --vcn-id <vcn-ocid> \\\n  --cidr-block 10.0.1.0/24 \\\n  --route-table-id <internet-gateway-rt> \\\n  --dhcp-options-id <dhcp-ocid>\n```\n\n**Subnet Privada:**\n```bash\noci network subnet create \\\n  --compartment-id <ocid> \\\n  --vcn-id <vcn-ocid> \\\n  --cidr-block 10.0.2.0/24 \\\n  --route-table-id <nat-gateway-rt>\n```\n\n**Diferença:** Pública tem rota para Internet Gateway, privada usa NAT Gateway", category, "beginner"))
    
    examples.append(create_example(sp, "Quando usar Internet Gateway vs NAT Gateway?",
        "Internet Gateway vs NAT Gateway:\n\n**Internet Gateway (IGW):**\n- Bidirecional (inbound + outbound)\n- Para instâncias com IP público\n- Load balancers públicos\n- Bastion hosts\n\n**NAT Gateway:**\n- Apenas outbound\n- Para instâncias sem IP público\n- Mais seguro (sem inbound)\n- Patching, updates\n\n**Use ambos:**\n- IGW para recursos públicos\n- NAT para recursos privados\n\n**Custo:** NAT Gateway tem custo por hora + GB", category, "intermediate"))
    
    examples.append(create_example(sp, "Como configurar routing table?",
        "Configurando routing table:\n\n**1. Crie route table:**\n```bash\noci network route-table create --compartment-id <ocid> --vcn-id <vcn-ocid>\n```\n\n**2. Adicione regras:**\n```bash\noci network route-table route-rule create \\\n  --rt-id <rt-ocid> \\\n  --destination 0.0.0.0/0 \\\n  --network-entity-id <gateway-ocid>\n```\n\n**Rotas comuns:**\n- 0.0.0.0/0 → Internet Gateway (público)\n- 0.0.0.0/0 → NAT Gateway (privado)\n- 10.0.0.0/8 → DRG (on-premises)\n\n**Best practice:** Route tables separadas por subnet type", category, "intermediate"))
    
    examples.append(create_example(sp, "Como planejar CIDR de VCN?",
        "Planejamento de CIDR:\n\n**1. Tamanho da VCN:**\n- /16 = 65,536 IPs (recomendado)\n- /20 = 4,096 IPs (mínimo)\n- /28 = 16 IPs (não recomendado)\n\n**2. Subnet sizing:**\n- /24 = 256 IPs (padrão)\n- /25 = 128 IPs\n- /26 = 64 IPs\n\n**3. Reserve espaço para:**\n- Crescimento futuro\n- Multiple ADs\n- DR/Backup\n\n**4. Evite sobreposição:**\n- On-premises networks\n- Outras VCNs\n- VPN connections\n\n**Exemplo:**\n```\nVCN: 10.0.0.0/16\n  Public: 10.0.0.0/24\n  Private App: 10.0.1.0/24\n  Private DB: 10.0.2.0/24\n```", category, "intermediate"))
    
    examples.append(create_example(sp, "Como conectar múltiplas VCNs?",
        "Conectando múltiplas VCNs:\n\n**Opção 1: VCN Peering (Local)**\n- Mesma região\n- Baixa latência\n- Tráfego pela backbone OCI\n\n**Opção 2: Remote VCN Peering**\n- Regiões diferentes\n- Via DRG\n- Mais caro\n\n**Opção 3: DRG (Dynamic Routing Gateway)**\n- Hub-and-spoke topology\n- Múltiplas VCNs conectadas\n- On-premises via VPN/FastConnect\n\n**Configuração:**\n```bash\noci network vcn-peering-connection create \\\n  --peer-vcn-id <vcn-ocid> \\\n  --vcn-id <source-vcn-ocid>\n```\n\n**Roteamento:** Adicione rotas nas route tables", category, "intermediate"))
    
    examples.append(create_example(sp, "Como usar DHCP options?",
        "DHCP Options:\n\n**Default DHCP:**\n- Criado automaticamente com VCN\n- Domain name: vcn.oraclevcn.com\n- Search domain: same\n\n**Custom DHCP:**\n```bash\noci network dhcp-options create \\\n  --compartment-id <ocid> \\\n  --vcn-id <vcn-ocid> \\\n  --options '{\"domainName\":\"mycompany.com\",\"searchDomainNames\":[\"mycompany.com\"]}'\n```\n\n**Use cases:**\n- Custom domain name\n- DNS personalizado\n- Compliance requirements\n\n**Nota:** Instâncias devem usar Oracle-provided DNS ou custom DNS servers", category, "intermediate"))
    
    examples.append(create_example(sp, "Como debugar problemas de conectividade na VCN?",
        "Debug de conectividade VCN:\n\n**1. Verifique route tables:**\n```bash\noci network route-table get --rt-id <ocid>\n```\n\n**2. Cheque security lists:**\n- Regras de ingress/egress\n- Portas necessárias abertas?\n\n**3. Verifique subnet tipo:**\n- Pública vs Privada\n- NAT Gateway funcionando?\n\n**4. Teste conectividade:**\n```bash\nping <destination>\ntelnet <host> <port>\n```\n\n**5. Use VCN Flow Logs:**\n- Enable no Console\n- Analise logs no Logging service\n\n**6. Network Path:**\n- Console → Networking → Network Path\n- Simula tráfego entre recursos", category, "advanced"))
    
    examples.append(create_example(sp, "Como implementar hub-and-spoke topology?",
        "Hub-and-spoke topology:\n\n**1. Crie VCN Hub:**\n- CIDR: 10.0.0.0/16\n- DRG attached\n- Transit routing enabled\n\n**2. Crie VCNs Spoke:**\n- CIDR: 10.1.0.0/16, 10.2.0.0/16\n- Peering com Hub\n\n**3. Configure DRG:**\n```bash\noci network drg create --compartment-id <ocid>\noci network drg-attachment create --drg-id <drg-ocid> --resource-type VCN --vcn-id <hub-vcn>\n```\n\n**4. Route tables:**\n- Spoke → Hub: 0.0.0.0/0\n- Hub → Spoke: rotas específicas\n\n**Vantagens:**\n- Centralized egress\n- Shared services\n- Simplified management\n\n**Trade-offs:**\n- Single point of failure (mitigue com DRG redundant)", category, "advanced"))
    
    examples.append(create_example(sp, "Como migrar VCN para outra região?",
        "Migrando VCN entre regiões:\n\n**Não há migração direta de VCN**\n\n**Abordagem:**\n\n**1. Terraform/CLI:**\n- Exporte configuração\n- Aplique na região destino\n\n**2. OCI Resource Mover:**\n- Move alguns recursos\n- Suporte limitado\n\n**3. Manual:**\n1. Crie VCN na região destino\n2. Recrie subnets, gateways, route tables\n3. Migre instâncias (custom images)\n4. Atualize DNS/load balancers\n5. Cutover\n\n**Downtime:** Necessário\n\n**Preparação:**\n- Documente toda configuração\n- Teste em staging primeiro\n- Tenha rollback plan", category, "advanced"))
    
    return examples

# NETWORKING - SECURITY
def gen_networking_security():
    category = "networking/security"
    sp = "You are an OCI specialist with expertise in network security. Provide technical guidance on security lists, NSGs, and ingress/egress rules."
    examples = []
    
    examples.append(create_example(sp, "Como criar Security List?",
        "Criando Security List:\n\n**Via Console:**\n1. VCN Details → Security Lists\n2. Create Security List\n3. Adicione ingress/egress rules\n4. Associate com subnets\n\n**Via CLI:**\n```bash\noci network security-list create \\\n  --compartment-id <ocid> \\\n  --vcn-id <vcn-ocid> \\\n  --display-name web-servers\n```\n\n**Ingress rules (exemplo):**\n- TCP 80, 443: 0.0.0.0/0 (web)\n- TCP 22: 10.0.0.0/8 (SSH interno)\n\n**Egress rules:**\n- All traffic: 0.0.0.0/0 (padrão)\n\n**Stateful:** Conexões de retorno automáticas\n\nDocs: https://docs.oracle.com/en-us/iaas/Content/Network/Concepts/overview.htm", category, "beginner"))
    
    examples.append(create_example(sp, "Qual diferença entre Security List e NSG?",
        "Security List vs NSG:\n\n**Security List:**\n- Nível de subnet\n- Todas instâncias na subnet herdam regras\n- Mais simples de gerenciar\n- Menos granular\n\n**Network Security Group (NSG):**\n- Nível de VNIC\n- Regras por instância/VNIC\n- Mais granular\n- Múltiplos NSGs por VNIC\n\n**Quando usar:**\n- Security List: regras comuns para toda subnet\n- NSG: regras específicas por workload\n\n**Best practice:** Use ambos\n- Security List: regras básicas\n- NSG: regras específicas da aplicação", category, "beginner"))
    
    examples.append(create_example(sp, "Como criar Network Security Group?",
        "Criando NSG:\n\n**1. Crie NSG:**\n```bash\noci network nsg create \\\n  --compartment-id <ocid> \\\n  --vcn-id <vcn-ocid> \\\n  --display-name web-nsg\n```\n\n**2. Adicione regras:**\n```bash\noci network nsg security-rule create \\\n  --nsg-id <nsg-ocid> \\\n  --direction INGRESS \\\n  --protocol 6 \\\n  --source 0.0.0.0/0 \\\n  --tcp-options '{\"destinationPortRange\":{\"min\":443,\"max\":443}}'\n```\n\n**3. Associate com VNICs:**\n- Console: Instance → VNICs → NSGs\n- Ou na criação da instância\n\n**Vantagem:** Mudança de regras afeta apenas VNICs associadas", category, "intermediate"))
    
    examples.append(create_example(sp, "Como configurar regras stateless?",
        "Regras stateless:\n\n**Stateful (padrão):**\n- Conexões de retorno automáticas\n- Mais seguro\n- Overhead mínimo\n\n**Stateless:**\n- Precisa definir ingress E egress\n- Mais performance (high throughput)\n- Mais complexo\n\n**Configuração:**\n```bash\noci network security-list create \\\n  --compartment-id <ocid> \\\n  --vcn-id <vcn-ocid> \\\n  --egress-security-rules '[{\"destination\":\"0.0.0.0/0\",\"protocol\":\"6\",\"isStateless\":true}]' \\\n  --ingress-security-rules '[{\"source\":\"0.0.0.0/0\",\"protocol\":\"6\",\"isStateless\":true}]'\n```\n\n**Use case:** HPC, big data workloads\n\n**Importante:** Defina ambas direções explicitamente", category, "intermediate"))
    
    examples.append(create_example(sp, "Como permitir acesso SSH seguro?",
        "SSH seguro:\n\n**1. Restrinja por IP:**\n```bash\n# Security rule\nSource: <seu-IP>/32\nPort: 22\n```\n\n**2. Use bastion host:**\n- Instância pública em subnet pública\n- SSH para bastion, depois para instâncias privadas\n- Bastion com MFA\n\n**3. OCI Bastion Service:**\n```bash\noci bastion bastion create \\\n  --compartment-id <ocid> \\\n  --target-vcn-id <vcn-ocid>\n```\n\n**4. SSH key best practices:**\n- Keys de 4096 bits\n- Rotação periódica\n- Sem password authentication\n\n**5. NSG para SSH:**\n- Apenas IPs específicos\n- Log de acesso habilitado", category, "intermediate"))
    
    examples.append(create_example(sp, "Como usar security rules para microsegmentação?",
        "Microsegmentação com NSGs:\n\n**1. Crie NSGs por camada:**\n- Web NSG: portas 80, 443\n- App NSG: porta 8080\n- DB NSG: porta 1521\n\n**2. Configure regras:**\n```\nWeb NSG:\n  Ingress: 80, 443 de 0.0.0.0/0\n  Egress: 8080 para App NSG\n\nApp NSG:\n  Ingress: 8080 de Web NSG\n  Egress: 1521 para DB NSG\n\nDB NSG:\n  Ingress: 1521 de App NSG\n  Egress: none\n```\n\n**3. Reference NSGs nas regras:**\n- Use NSG ID como source/destination\n\n**Benefícios:**\n- Least privilege\n- Contenção de breaches\n- Compliance", category, "intermediate"))
    
    examples.append(create_example(sp, "Como monitorar tráfego de rede?",
        "Monitoramento de tráfego:\n\n**1. VCN Flow Logs:**\n```bash\noci network vcn-flow-log create \\\n  --flow-log-type PATH_ANALYSIS \\\n  --resource-id <vcn-ocid>\n```\n\n**2. Logs capturam:**\n- Source/destination IP\n- Portas\n- Protocolo\n- Ação (allow/deny)\n\n**3. Envie para Logging:**\n- Log group dedicado\n- Retention configurável\n\n**4. Análise:**\n- Console → Logging → Search\n- Queries personalizadas\n- Alarms para tráfego anômalo\n\n**5. Integration:**\n- OCI Security Zones\n- Cloud Guard\n- SIEM externo\n\nDocs: https://docs.oracle.com/en-us/iaas/Content/Logging/overview.htm", category, "intermediate"))
    
    examples.append(create_example(sp, "Como proteger contra DDoS?",
        "Proteção DDoS:\n\n**OCI DDoS (automático):**\n- Habilitado por default\n- Camadas 3, 4, 7\n- Sem custo adicional\n\n**Best practices:**\n\n**1. Security Lists:**\n- Restrinja portas necessárias\n- Rate limiting\n\n**2. Load Balancer:**\n- Health checks\n- Rate limiting\n- WAF integration\n\n**3. WAF (Web Application Firewall):**\n```bash\noci waas waas-policy create \\\n  --compartment-id <ocid> \\\n  --cname \"example.com\"\n```\n\n**4. FastConnect:**\n- Maior capacidade\n- Dedicado\n\n**5. Monitoring:**\n- Alarms de tráfego\n- Anomaly detection\n\n**Durante ataque:**\n- Oracle SOC responde automaticamente\n- Service Request para suporte", category, "advanced"))
    
    examples.append(create_example(sp, "Como implementar zero trust network?",
        "Zero Trust Network:\n\n**Princípios:**\n- Never trust, always verify\n- Least privilege access\n- Microsegmentation\n\n**Implementação OCI:**\n\n**1. NSGs granulares:**\n- Regras por workload\n- Referencie NSGs (não CIDRs)\n\n**2. Private endpoints:**\n- Service Gateway\n- Private Link\n\n**3. Encryption:**\n- TLS em trânsito\n- Encryption em repouso\n\n**4. Identity:**\n- IAM policies\n- Dynamic groups\n- MFA obrigatório\n\n**5. Monitoring:**\n- Flow logs\n- Cloud Guard\n- Continuous compliance\n\n**6. Automation:**\n- Security Zones\n- Policy as code\n\n**Trade-offs:**\n- Mais complexo\n- Overhead de gerenciamento\n- Melhor segurança", category, "advanced"))
    
    examples.append(create_example(sp, "Como debugar regras de segurança?",
        "Debug de security rules:\n\n**1. Verifique regras aplicadas:**\n```bash\noci network security-list list --vcn-id <vcn-ocid>\noci network nsg list --vcn-id <vcn-ocid>\n```\n\n**2. Teste conectividade:**\n```bash\nnc -zv <host> <port>\ntelnet <host> <port>\n```\n\n**3. Verifique ordem de avaliação:**\n- NSGs e Security Lists são avaliados\n- Deny implícito no final\n\n**4. Flow logs:**\n- Enable VCN Flow Logs\n- Veja tráfego allow/deny\n\n**5. Common issues:**\n- Porta não aberta\n- CIDR errado\n- Stateful vs stateless\n- Rota faltando\n\n**6. Network Path:**\n- Console → Networking → Network Path\n- Simula tráfego e mostra onde bloqueia", category, "advanced"))
    
    return examples

# NETWORKING - CONNECTIVITY
def gen_networking_connectivity():
    category = "networking/connectivity"
    sp = "You are an OCI specialist with expertise in network connectivity. Provide technical guidance on DRG, VPN IPSec, FastConnect, and peering."
    examples = []
    
    examples.append(create_example(sp, "Como conectar on-premises ao OCI?",
        "Conectando on-premises ao OCI:\n\n**Opção 1: VPN IPSec**\n- Internet-based\n- Criptografado\n- Setup rápido\n- Até 1.5 Gbps\n\n**Opção 2: FastConnect**\n- Dedicated connection\n- Mais caro\n- Até 100 Gbps\n- Baixa latência\n\n**Opção 3: FastConnect Partner**\n- Via provider (Equinix, etc)\n- Menor custo que direto\n\n**Via Console:**\n1. Networking → Dynamic Routing Gateways\n2. Create DRG\n3. Attach to VCN\n4. Create IPSec Connection ou FastConnect\n\nDocs: https://docs.oracle.com/en-us/iaas/Content/Network/Concepts/overview.htm", category, "beginner"))
    
    examples.append(create_example(sp, "Como configurar VPN IPSec?",
        "Configurando VPN IPSec:\n\n**1. Crie DRG:**\n```bash\noci network drg create --compartment-id <ocid>\noci network drg-attachment create --drg-id <drg-ocid> --resource-type VCN\n```\n\n**2. Crie IPSec Connection:**\n```bash\noci network ipsec-connection create \\\n  --compartment-id <ocid> \\\n  --drg-id <drg-ocid> \\\n  --cpe-id <cpe-ocid> \\\n  --display-name onprem-vpn\n```\n\n**3. Configure on-premises:**\n- Oracle fornece informações de tunnel\n- IKE version: 2\n- Encryption: AES-256\n\n**4. Teste:**\n```bash\nping <remote-ip>\n```\n\n**Tunnels:** 2 por conexão (redundância)\n\n[CHECK DOCS] Limites de throughput variam", category, "intermediate"))
    
    examples.append(create_example(sp, "Qual diferença entre FastConnect e VPN?",
        "FastConnect vs VPN:\n\n**VPN IPSec:**\n- Via internet pública\n- Criptografado por default\n- Setup: minutos\n- Custo: baixo\n- Throughput: até 1.5 Gbps\n- SLA: 99.9%\n\n**FastConnect:**\n- Conexão dedicada\n- Opcionalmente criptografado\n- Setup: semanas (provisionamento)\n- Custo: alto\n- Throughput: 1-100 Gbps\n- SLA: 99.99%\n\n**Quando usar VPN:**\n- Dev/test\n- DR secondary\n- Baixo bandwidth\n\n**Quando usar FastConnect:**\n- Produção crítica\n- Grande volume de dados\n- Baixa latência requerida\n- Compliance", category, "intermediate"))
    
    examples.append(create_example(sp, "Como configurar FastConnect?",
        "Configurando FastConnect:\n\n**1. Crie DRG**\n\n**2. Provisione FastConnect:**\n- Console → Networking → FastConnect\n- Selecione provider\n- Defina bandwidth\n\n**3. Provider provisioning:**\n- Oracle fornece LOA-CFA\n- Provider instala cross-connect\n\n**4. Crie Virtual Circuit:**\n```bash\noci network virtual-circuit create \\\n  --compartment-id <ocid> \\\n  --drg-id <drg-ocid> \\\n  --type private\n```\n\n**5. Configure BGP:**\n- Oracle e customer edge\n- ASN configuration\n\n**Timeline:** 2-8 semanas\n\n[MUTABLE] Custos variam por bandwidth e provider", category, "intermediate"))
    
    examples.append(create_example(sp, "Como configurar VCN peering?",
        "VCN Peering:\n\n**Local Peering (mesma região):**\n\n**1. Crie peering:**\n```bash\noci network vcn-peering-connection create \\\n  --compartment-id <ocid> \\\n  --peer-vcn-id <vcn-ocid> \\\n  --vcn-id <source-vcn-ocid>\n```\n\n**2. Aceite peering no VCN destino**\n\n**3. Adicione rotas:**\n- Route table → Add route\n- Destination: peer VCN CIDR\n- Target: DRG ou peering\n\n**Remote Peering (regiões diferentes):**\n- Via DRG\n- Remote peering connection\n- Mais caro\n\n**Requisitos:**\n- CIDRs não sobrepostos\n- Mesma tenancy (ou diferentes com setup extra)", category, "intermediate"))
    
    examples.append(create_example(sp, "Como usar DRG para hub-and-spoke?",
        "DRG Hub-and-Spoke:\n\n**1. Crie DRG:**\n```bash\noci network drg create --compartment-id <ocid>\n```\n\n**2. Attach VCNs:**\n```bash\noci network drg-attachment create \\\n  --drg-id <drg-ocid> \\\n  --resource-type VCN \\\n  --vcn-id <spoke-vcn-ocid>\n```\n\n**3. Configure routing:**\n- Spoke route: 0.0.0.0/0 → DRG\n- Hub route: rotas específicas para spokes\n\n**4. Transit routing:**\n- Habilitar no DRG\n- Permite tráfego entre spokes via hub\n\n**Use cases:**\n- Centralized egress\n- Shared services (AD, DNS)\n- On-premises connectivity\n\n**Limites:** [CHECK DOCS] Número máximo de attachments", category, "intermediate"))
    
    examples.append(create_example(sp, "Como configurar redundant connectivity?",
        "Connectivity redundante:\n\n**1. Dual IPSec:**\n- 2 IPSec connections\n- Diferentes data centers Oracle\n- Active/Active ou Active/Standby\n\n**2. FastConnect + VPN:**\n- FastConnect primário\n- VPN backup\n- BGP para failover automático\n\n**3. Dual FastConnect:**\n- 2 connections em data centers diferentes\n- Maior custo\n- Maior disponibilidade\n\n**4. DRG redundancy:**\n- Múltiplos DRGs\n- Complexo de gerenciar\n\n**BGP configuration:**\n- ASN diferente por path\n- BGP community para preference\n- Failover automático\n\n**SLA:** 99.99% com redundant paths\n\n[MUTABLE] Custos variam por configuração", category, "intermediate"))
    
    examples.append(create_example(sp, "Como monitorar connectivity?",
        "Monitoramento de connectivity:\n\n**1. Metrics:**\n- BGP session status\n- Tunnel status\n- Bytes in/out\n- Packet loss\n\n**2. Console:**\n- Networking → DRG → Metrics\n- Networking → IPSec → Details\n\n**3. Alarms:**\n```bash\noci monitoring alarm create \\\n  --metric-name BgpSessionState \\\n  --threshold 0 \\\n  --severity critical\n```\n\n**4. Health checks:**\n- BFD (Bidirectional Forwarding Detection)\n- Fast failure detection\n\n**5. Logging:**\n- Flow logs\n- Audit logs\n\n**6. Notifications:**\n- OCI Notifications\n- PagerDuty integration\n\nDocs: https://docs.oracle.com/en-us/iaas/Content/Monitoring/overview.htm", category, "intermediate"))
    
    examples.append(create_example(sp, "Como otimizar performance de rede?",
        "Otimização de performance:\n\n**1. Escolha região próxima:**\n- Menor latência\n- Melhor experiência\n\n**2. Use FastConnect:**\n- Dedicated bandwidth\n- Sem internet congestion\n\n**3. MTU optimization:**\n- Jumbo frames (9000) para FastConnect\n- Padrao: 1500\n\n**4. BGP tuning:**\n- Adjust timers\n- ECMP para load balancing\n\n**5. VCN design:**\n- Subnets adequadas\n- Route tables otimizadas\n\n**6. Monitor:**\n- Latency metrics\n- Throughput\n- Packet loss\n\n**Baseline:**\n- Meça performance normal\n- Detecte anomalias rápido", category, "advanced"))
    
    examples.append(create_example(sp, "Como troubleshoot connectivity issues?",
        "Troubleshooting connectivity:\n\n**1. Verifique status:**\n```bash\noci network ipsec-connection get --id <ocid>\noci network virtual-circuit get --id <ocid>\n```\n\n**2. BGP sessions:**\n- Status up/down?\n- Routes being advertised?\n\n**3. Route tables:**\n- Rotas corretas?\n- Next hop certo?\n\n**4. Security:**\n- Security lists permitem tráfego?\n- NSGs configurados?\n\n**5. Testes:**\n```bash\nping <remote>\ntraceroute <remote>\n```\n\n**6. Logs:**\n- VCN Flow Logs\n- Customer edge logs\n\n**7. Oracle support:**\n- Service Request\n- Network team envolvido", category, "advanced"))
    
    return examples

if __name__ == "__main__":
    generators = {
        "networking-vcn": gen_networking_vcn,
        "networking-security": gen_networking_security,
        "networking-connectivity": gen_networking_connectivity,
    }
    
    for name, generator in generators.items():
        examples = generator()
        filename = f"{name}.jsonl"
        output_file, count = save_examples(examples, filename)
        print(f"Gerado: {output_file} ({count} exemplos)")
