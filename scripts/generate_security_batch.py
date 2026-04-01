#!/usr/bin/env python3
"""
Generate JSONL files for OCI Security categories (9 files).
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

# ============ SECURITY IAM BASICS ============
def generate_security_iam_basics():
    examples = []
    system = "You are an OCI security specialist with expertise in IAM. Provide technical guidance on compartments, users, groups, authentication, and access control."
    cat = "security/iam-basics"
    
    # Beginner (3)
    examples.append(create_example("security-iam-basics", cat, "beginner",
        "O que é IAM no OCI?",
        "IAM (Identity and Access Management) controla quem acessa quais recursos no OCI.\n\n**Componentes principais:**\n- Users: pessoas ou serviços\n- Groups: coleção de users\n- Compartments: isolamento lógico de recursos\n- Policies: regras de permissão\n- Dynamic Groups: grupos baseados em regras\n\n**Princípios:**\n- Least privilege (menor privilégio necessário)\n- Segregation of duties\n- Audit via Audit Service\n\n**Diferença AWS:** IAM Users → OCI Users, IAM Roles → Dynamic Groups\n\nDocs: https://docs.oracle.com/en-us/iaas/Content/Identity/Concepts/overview.htm", system))
    
    examples.append(create_example("security-iam-basics", cat, "beginner",
        "Como criar um usuário?",
        "Criando usuário:\n\n**Via Console:**\n1. Identity & Security → Users\n2. 'Create User'\n3. Preencha:\n   - Name\n   - Email\n   - Description\n4. Add a grupos (opcional)\n5. Create\n\n**Via CLI:**\n```bash\noci iam user create \\\n  --compartment-id <tenancy-ocid> \\\n  --name joao.silva \\\n  --email joao@empresa.com \\\n  --description \"Desenvolvedor\"\n```\n\n**Próximos passos:**\n- Add a grupos\n- Configure credentials (password ou API keys)\n\n[CHECK DOCS] Limites de usuários por tenancy.", system))
    
    examples.append(create_example("security-iam-basics", cat, "beginner",
        "O que são compartments?",
        "Compartments são containers lógicos para organizar recursos OCI.\n\n**Características:**\n- Isolamento lógico (não físico)\n- Hierarquia (compartments dentro de compartments)\n- Políticas podem ser por compartment\n- Facilita billing e governance\n\n**Exemplo de estrutura:**\n```\nTenancy\n├── Prod\n│   ├── Network\n│   ├── Compute\n│   └── Database\n├── Dev\n└── Shared\n```\n\n**Best Practices:**\n- Separe por ambiente (Prod/Dev/Test)\n- Separe por time/projeto\n- Use tags para cruzar compartments\n\n**Diferença AWS:** Similar a AWS Organizations OUs + Resource Groups", system))
    
    # Intermediate (5)
    examples.append(create_example("security-iam-basics", cat, "intermediate",
        "Como criar grupos e adicionar usuários?",
        "Gerenciando grupos:\n\n**Criar grupo:**\n```bash\noci iam group create \\\n  --compartment-id <tenancy-ocid> \\\n  --name Developers \\\n  --description \"Time de desenvolvimento\"\n```\n\n**Add usuário ao grupo:**\n```bash\noci iam user-add-to-group \\\n  --user-id <user-ocid> \\\n  --group-id <group-ocid>\n```\n\n**Listar membros:**\n```bash\noci iam group list-users --group-id <group-ocid>\n```\n\n**Remover:**\n```bash\noci iam user-remove-from-group \\\n  --user-id <user-ocid> \\\n  --group-id <group-ocid>\n```\n\n**Best Practice:** Grupos por função (Developers, Admins, DBAs), não por pessoa.", system))
    
    examples.append(create_example("security-iam-basics", cat, "intermediate",
        "Como configurar MFA?",
        "Configurando MFA (Multi-Factor Authentication):\n\n**Para o próprio usuário:**\n1. Console → User Settings\n2. 'Generate MFA Secret'\n3. Scan QR code com app (Google Authenticator, Authy)\n4. Digite código de verificação\n5. Enable MFA\n\n**Forçar MFA para outros usuários (Policy):**\n```\nAllow group Admins to manage all-resources in tenancy\n  where request.auth.type='mfa'\n```\n\n**Via CLI:**\n```bash\noci iam user update \\\n  --user-id <ocid> \\\n  --is-mfa-activated true\n```\n\n**Best Practice:** MFA obrigatório para todos usuários com acesso privilegiado\n\n[CHECK DOCS] MFA não disponível para API keys.", system))
    
    examples.append(create_example("security-iam-basics", cat, "intermediate",
        "Como gerar API keys para CLI/SDK?",
        "Gerando API keys:\n\n**1. Gere par de chaves:**\n```bash\nmkdir -p ~/.oci\nopenssl genrsa -out ~/.oci/oci_api_key.pem 2048\nchmod 600 ~/.oci/oci_api_key.pem\nopenssl rsa -pubout -in ~/.oci/oci_api_key.pem -out ~/.oci/oci_api_key_public.pem\n```\n\n**2. Console → User Settings → API Keys:**\n- 'Add API Key'\n- Upload da chave pública\n- Anote Key Fingerprint\n\n**3. Configure ~/.oci/config:**\n```ini\n[DEFAULT]\nuser=<user-ocid>\nfingerprint=<key-fingerprint>\ntenancy=<tenancy-ocid>\nregion=us-ashburn-1\nkey_file=~/.oci/oci_api_key.pem\n```\n\n**4. Teste:**\n```bash\noci iam user get --user-id <ocid>\n```", system))
    
    examples.append(create_example("security-iam-basics", cat, "intermediate",
        "Como auditar acesso com Audit Service?",
        "Auditoria com Audit Service:\n\n**O que é auditado:**\n- Todas as chamadas de API\n- Console actions\n- Mudanças em recursos\n- Acesso a dados sensíveis\n\n**Query de auditoria:**\n```bash\noci audit event list \\\n  --compartment-id <ocid> \\\n  --start-time \"2024-01-01T00:00:00Z\" \\\n  --end-time \"2024-01-31T23:59:59Z\"\n```\n\n**Filtros comuns:**\n```bash\n# Quem deletou instâncias?\noci audit event list --query \"?data.resourceName=='instance-delete'\"\n\n# Acesso de usuário específico\noci audit event list --query \"?data.identity.userPrincipalId=='<user-ocid>'\"\n```\n\n**Export:** Configure para Object Storage para retenção longa\n\nDocs: https://docs.oracle.com/en-us/iaas/Content/Audit/Concepts/auditoverview.htm", system))
    
    examples.append(create_example("security-iam-basics", cat, "intermediate",
        "Como usar tags para governança?",
        "Tags para governança:\n\n**Tipos de tags:**\n- Free-form: simples, sem schema\n- Defined: com schema e validação\n\n**Aplicar tags:**\n```bash\noci compute instance tag \\\n  --instance-id <ocid> \\\n  --defined-tags '{\"Production\":{\"Environment\": \"prod\"}}' \\\n  --freeform-tags '{\"Owner\": \"DevOps\", \"CostCenter\": \"12345\"}'\n```\n\n**Políticas baseadas em tags:**\n```\nAllow group Developers to manage instance-family in compartment Dev\n  where ALL {request.resource.tags.CostCenter = '12345'}\n```\n\n**Use cases:**\n- Cost allocation (CostCenter)\n- Ownership (Owner, Team)\n- Environment (Prod, Dev, Test)\n- Compliance (PCI, HIPAA)\n\n**Best Practice:** Defina tag schema antes de criar recursos.", system))
    
    # Advanced (2)
    examples.append(create_example("security-iam-basics", cat, "advanced",
        "Como implementar least privilege?",
        "Implementando least privilege:\n\n**1. Analise acesso atual:**\n```bash\noci audit event list --compartment-id <ocid> | \\\n  jq '.data | {user: .identity.userPrincipalName, action: .eventName}'\n```\n\n**2. Crie políticas mínimas:**\n```bash\n# RUIM: muito permissivo\nAllow group Devs to manage all-resources in compartment Dev\n\n# BOM: específico\nAllow group Devs to read instance-family in compartment Dev\nAllow group Devs to manage volume-family in compartment Dev\nAllow group Devs to read virtual-network-family in compartment Dev\n```\n\n**3. Resource-specific:**\n```\nAllow group DBAs to manage db-systems in compartment Prod\n  where resource.id = '<specific-db-ocid>'\n```\n\n**4. Review periódico:**\n- Audit logs mensais\n- Remova acesso não usado\n- Documente exceções\n\n**Trade-off:** Mais granularidade = mais complexidade", system))
    
    examples.append(create_example("security-iam-basics", cat, "advanced",
        "Como federar com Azure AD?",
        "Federação com Azure AD:\n\n**1. No Azure AD:**\n- Crie Enterprise Application\n- Configure SAML\n- Download metadata XML\n\n**2. No OCI:**\n```bash\noci iam identity-provider create \\\n  --compartment-id <tenancy-ocid> \\\n  --name AzureAD \\\n  --protocol-type SAML2 \\\n  --metadata-url https://login.microsoftonline.com/<tenant>/federationmetadata/2007-06/federationmetadata.xml\n```\n\n**3. Mapeie grupos:**\n```\nAzure AD Group \"OCI-Admins\" → OCI Group \"Admins\"\n```\n\n**4. Policy no OCI:**\n```\nAllow group Admins to manage all-resources in tenancy\n```\n\n**5. Teste login:**\n- Users logam via Azure AD SSO\n- Tokens SAML válidos no OCI\n\n**Vantagens:**\n- SSO centralizado\n- Provisionamento automático\n- Offboarding no Azure remove acesso OCI", system))
    
    return examples

# ============ SECURITY POLICIES ============
def generate_security_policies():
    examples = []
    system = "You are an OCI security specialist with expertise in IAM policies. Provide technical guidance on policy syntax, conditions, and best practices."
    cat = "security/policies"
    
    # Beginner (3)
    examples.append(create_example("security-policies", cat, "beginner",
        "O que são policies no OCI?",
        "Policies são regras que definem quem pode fazer o quê no OCI.\n\n**Sintaxe:**\n```\nAllow <group> to <verb> <resource-type> in <location>\n```\n\n**Exemplos:**\n```\nAllow group Admins to manage all-resources in tenancy\nAllow group Developers to manage instance-family in compartment Dev\nAllow group DBAs to read database-family in compartment Prod\n```\n\n**Verbos:**\n- read: visualizar\n- use: usar (inspecionar + ações)\n- manage: CRUD completo\n\n**Recursos:**\n- instance-family: instâncias, images, volumes\n- virtual-network-family: VCNs, subnets, security lists\n- database-family: databases, backups\n\nDocs: https://docs.oracle.com/en-us/iaas/Content/Identity/Concepts/policies.htm", system))
    
    examples.append(create_example("security-policies", cat, "beginner",
        "Como criar uma policy?",
        "Criando policy:\n\n**Via Console:**\n1. Identity & Security → Policies\n2. 'Create Policy'\n3. Selecione compartment\n4. Digite statement:\n   ```\n   Allow group Developers to manage instance-family in compartment Dev\n   ```\n5. Create\n\n**Via CLI:**\n```bash\noci iam policy create \\\n  --compartment-id <compartment-ocid> \\\n  --name dev-compute-policy \\\n  --statements '[\"Allow group Developers to manage instance-family in compartment Dev\"]'\n```\n\n**Best Practices:**\n- Names descritivos\n- Statements em linhas separadas\n- Teste com usuário de teste\n\n[CHECK DOCS] Limites de policies por compartment.", system))
    
    examples.append(create_example("security-policies", cat, "beginner",
        "Qual a diferença entre read, use e manage?",
        "Níveis de permissão:\n\n**READ:**\n- Listar recursos\n- Ver detalhes\n- Sem modificações\n```\nAllow group Auditors to read instance-family in tenancy\n```\n\n**USE:**\n- Tudo do READ +\n- Start/stop instâncias\n- Attach/detach volumes\n- Console access\n```\nAllow group Operators to use instance-family in compartment Prod\n```\n\n**MANAGE:**\n- Tudo do USE +\n- Create/delete\n- Update configurações\n```\nAllow group Admins to manage instance-family in compartment Dev\n```\n\n**Hierarquia:** manage > use > read\n\n**Use case:**\n- Devs: use (dev/test)\n- Ops: use (prod)\n- Admins: manage (tudo)", system))
    
    # Intermediate (5)
    examples.append(create_example("security-policies", cat, "intermediate",
        "Como escrever policy para VCN?",
        "Policies para VCN:\n\n**Leitura (network team):**\n```\nAllow group NetworkAdmins to read virtual-network-family in tenancy\n```\n\n**Gerenciamento completo:**\n```\nAllow group NetworkAdmins to manage virtual-network-family in compartment Shared\n```\n\n**Específico por recurso:**\n```\nAllow group NetworkAdmins to manage vcns in compartment Shared\nAllow group NetworkAdmins to manage subnets in compartment Shared\nAllow group NetworkAdmins to manage security-lists in compartment Shared\n```\n\n**Cross-compartment:**\n```\nAllow group NetworkAdmins to read virtual-network-family in compartment Prod\nAllow group NetworkAdmins to manage virtual-network-family in compartment Shared\n```\n\n**DRG (Dynamic Routing Gateway):**\n```\nAllow group NetworkAdmins to manage drg-family in tenancy\n```", system))
    
    examples.append(create_example("security-policies", cat, "intermediate",
        "Como permitir acesso a Object Storage?",
        "Policies para Object Storage:\n\n**Acesso a buckets específicos:**\n```\nAllow group AppTeam to read buckets in compartment Prod\n  where target.bucket.name='app-data'\nAllow group AppTeam to manage objects in compartment Prod\n  where target.bucket.name='app-data'\n```\n\n**Acesso por prefixo:**\n```\nAllow group DataTeam to manage objects in compartment Data\n  where target.object.name.startsWith('team-a/')\n```\n\n**Verbos:**\n- read: listar buckets, ver metadata\n- use: download de objetos\n- manage: CRUD completo\n\n**Exemplo completo:**\n```\nAllow group BackupTeam to read buckets in tenancy\nAllow group BackupTeam to manage objects in tenancy\n  where target.object.name.startsWith('backups/')\n```\n\nDocs: https://docs.oracle.com/en-us/iaas/Content/Identity/Concepts/commonpolicies.htm#Object_Storage", system))
    
    examples.append(create_example("security-policies", cat, "intermediate",
        "Como criar policy para Load Balancer?",
        "Policies para Load Balancer:\n\n**Gerenciamento completo:**\n```\nAllow group LBAdmins to manage load-balancers in compartment Prod\n```\n\n**Apenas leitura:**\n```\nAllow group Auditors to read load-balancers in tenancy\n```\n\n**Específico:**\n```\nAllow group LBAdmins to manage load-balancers in compartment Prod\nAllow group LBAdmins to manage backend-sets in compartment Prod\nAllow group LBAdmins to manage certificates in compartment Prod\n```\n\n**Network resources relacionados:**\n```\nAllow group LBAdmins to use virtual-network-family in compartment Prod\n  where target.resource.type='subnet'\n```\n\n**Cross-compartment:**\n```\nAllow group LBAdmins to manage load-balancers in compartment Shared\nAllow group LBAdmins to read virtual-network-family in compartment Prod\n```", system))
    
    examples.append(create_example("security-policies", cat, "intermediate",
        "Como usar condições em policies?",
        "Condições em policies:\n\n**Por tag:**\n```\nAllow group Devs to manage instance-family in compartment Dev\n  where ALL {request.resource.tags.Environment = 'dev'}\n```\n\n**Por tempo:**\n```\nAllow group Contractors to use instance-family in compartment Dev\n  where request.time < '2024-12-31T23:59:59Z'\n```\n\n**Por MFA:**\n```\nAllow group Admins to manage all-resources in tenancy\n  where request.auth.type='mfa'\n```\n\n**Por IP:**\n```\nAllow group RemoteWorkers to use instance-family in compartment Prod\n  where request.source.ip='203.0.113.0/24'\n```\n\n**Combinando:**\n```\nAllow group Devs to manage instance-family in compartment Dev\n  where ALL {\n    request.resource.tags.Environment = 'dev',\n    request.auth.type = 'mfa'\n  }\n```\n\n**Operadores:** ALL (AND), ANY (OR)", system))
    
    examples.append(create_example("security-policies", cat, "intermediate",
        "Como debugar policy que não funciona?",
        "Debug de policies:\n\n**1. Policy Analyzer (Console):**\n- Identity → Policies → Policy Analyzer\n- Simule usuário + ação\n- Veja se policy permite/nega\n\n**2. Verifique hierarquia:**\n- Policies em múltiplos compartments?\n- Herança pode bloquear\n\n**3. Sintaxe:**\n```bash\noci iam policy list --compartment-id <ocid>\noci iam policy get --policy-id <ocid>\n```\n\n**4. Common issues:**\n- Group name errado\n- Compartment errado\n- Verbo insuficiente (read vs use)\n- Resource-type incorreto\n\n**5. Audit logs:**\n```bash\noci audit event list --query \"?data.resourceName=='<resource>'\"\n```\n\n**6. Teste com usuário do grupo afetado", system))
    
    # Advanced (2)
    examples.append(create_example("security-policies", cat, "advanced",
        "Como implementar políticas de tagging obrigatório?",
        "Tagging obrigatório com policies:\n\n**1. Crie tag schema:**\n```bash\noci iam tag-namespace create \\\n  --compartment-id <tenancy-ocid> \\\n  --name Production \\\n  --description \"Production tags\"\n\noci iam tag create \\\n  --tag-namespace-id <namespace-ocid> \\\n  --name CostCenter \\\n  --description \"Cost center code\"\n```\n\n**2. Policy para exigir tag:**\n```\nAllow group Admins to manage instance-family in tenancy\n  where ALL {request.resource.tags.Production.CostCenter = 'defined'}\n\nDeny group AllUsers to manage instance-family in tenancy\n  where ANY {request.resource.tags.Production.CostCenter = 'undefined'}\n```\n\n**3. Validação:**\n- Criação sem tag → negado\n- Criação com tag → permitido\n\n**Limitação:** Nem todos recursos suportam tag enforcement\n\n**Alternativa:** Automation via Functions para remediar recursos sem tag.", system))
    
    examples.append(create_example("security-policies", cat, "advanced",
        "Como criar política multi-tenancy?",
        "Políticas multi-tenancy:\n\n**Cenário:** MSP gerencia múltiplas tenancies\n\n**1. Federation setup:**\n- Identity Provider central\n- Groups mapeados por tenancy\n\n**2. Policy por tenancy:**\n```\nAllow group MSP-Admins to manage all-resources in tenancy\n  where request.tenant.name='TenantA'\n\nAllow group MSP-Admins to manage all-resources in tenancy\n  where request.tenant.name='TenantB'\n```\n\n**3. Cross-tenancy access:**\n```\nAllow group CentralOps to read metrics in tenancy\n  where request.tenant.id in ['<tenancy-a>','<tenancy-b>']\n```\n\n**4. Resource isolation:**\n```\nAllow group TenantA-Devs to manage instance-family in tenancy\n  where ALL {\n    request.tenant.name = 'TenantA',\n    request.resource.compartment.name = 'TenantA-Prod'\n  }\n```\n\n**Best Practice:** Use Organizations + federation para escala", system))
    
    return examples

# Continue with more security categories...
# (Dynamic Groups, Federation, Vault, Encryption, Cloud Guard, WAF)

def generate_security_dynamic_groups():
    examples = []
    system = "You are an OCI security specialist with expertise in Dynamic Groups. Provide technical guidance on rules, matching, and use cases."
    cat = "security/dynamic-groups"
    
    # Beginner (3)
    examples.append(create_example("security-dynamic-groups", cat, "beginner",
        "O que são Dynamic Groups?",
        "Dynamic Groups são grupos que contêm recursos (não usuários) baseados em regras de matching.\n\n**Diferença de grupos normais:**\n- Grupos normais: contêm usuários\n- Dynamic Groups: contêm recursos (instâncias, functions)\n\n**Casos de uso:**\n- Instâncias acessando outros serviços OCI\n- Functions acessando Vault\n- Recursos de um compartment específico\n\n**Exemplo de regra:**\n```\nALL {instance.compartment.id = '<compartment-ocid>'}\n```\n\n**Vantagem:** Não precisa gerenciar usuários manualmente\n\nDocs: https://docs.oracle.com/en-us/iaas/Content/Identity/Concepts/dynamicgroups.htm", system))
    
    examples.append(create_example("security-dynamic-groups", cat, "beginner",
        "Como criar um Dynamic Group?",
        "Criando Dynamic Group:\n\n**Via Console:**\n1. Identity & Security → Dynamic Groups\n2. 'Create Dynamic Group'\n3. Configure:\n   - Name\n   - Description\n   - Matching Rules\n4. Create\n\n**Via CLI:**\n```bash\noci iam dynamic-group create \\\n  --compartment-id <tenancy-ocid> \\\n  --name \"ProdInstances\" \\\n  --description \"All instances in Prod\" \\\n  --matching-rules \"ALL {instance.compartment.id = '<prod-ocid>'}\"\n```\n\n**Tipos de recursos:**\n- instance\n- fnfunc (Functions)\n- apigateway\n- oceinstance\n\n[CHECK DOCS] Tipos suportados variam.", system))
    
    examples.append(create_example("security-dynamic-groups", cat, "beginner",
        "Qual a sintaxe de Matching Rules?",
        "Sintaxe de Matching Rules:\n\n**Estrutura básica:**\n```\nALL {<condition>}\nANY {<condition1>, <condition2>}\n```\n\n**Condições comuns:**\n```\ninstance.compartment.id = '<ocid>'\ninstance.id = '<ocid>'\ninstance.tag.value = 'prod'\nfnfunc.compartment.id = '<ocid>'\n```\n\n**Operadores:**\n- `=` igual\n- `!=` diferente\n- `.value` para tags\n\n**Exemplos:**\n```\nALL {instance.compartment.id = '<prod-ocid>'}\nANY {instance.id = '<ocid1>', instance.id = '<ocid2>'}\nALL {instance.tag.value.Production.Environment = 'prod'}\n```", system))
    
    # Intermediate (5)
    examples.append(create_example("security-dynamic-groups", cat, "intermediate",
        "Como usar Dynamic Groups com Instance Principal?",
        "Instance Principal com Dynamic Groups:\n\n**1. Crie Dynamic Group:**\n```\nALL {instance.compartment.id = '<compartment-ocid>'}\n```\n\n**2. Crie Policy:**\n```\nAllow dynamic-group ProdInstances to read object-family in compartment Prod\n```\n\n**3. Na instância (SDK Python):**\n```python\nimport oci\n\n# Usa instance principal automaticamente\nconfig = oci.config.from_file('~/.oci/config', 'DEFAULT')\n# Ou use instance principal provider\nfrom oci.auth import principals\nprovider = principals.InstancePrincipalsSecurityTokenProvider()\nobject_storage = oci.object_storage.ObjectStorageClient(config={}, provider=provider)\n```\n\n**4. Teste:**\n```bash\ncurl -H \"Authorization: Bearer $(curl -X GET http://169.254.169.254/opc/v1/instance/identity/token)\" https://objectstorage.<region>.oraclecloud.com\n```\n\n**Vantagem:** Sem credentials hardcoded", system))
    
    examples.append(create_example("security-dynamic-groups", cat, "intermediate",
        "Como criar regra para Functions?",
        "Dynamic Groups para Functions:\n\n**Regra básica:**\n```\nALL {resource.type = 'fnfunc', resource.compartment.id = '<compartment-ocid>'}\n```\n\n**Ou por function específica:**\n```\nANY {\n  resource.id = '<function-ocid-1>',\n  resource.id = '<function-ocid-2>'\n}\n```\n\n**Policy para acessar Vault:**\n```\nAllow dynamic-group MyFunctions to read secret-family in compartment Prod\n```\n\n**Na function:**\n```python\nimport oci\n\ndef handler(ctx, data):\n    # Instance principal automático\n    vault = oci.vault.VaultClient()\n    secret = vault.get_secret(secret_id='<ocid>')\n    return {'status': 'success'}\n```\n\n**Use case:** Functions acessando secrets, databases, outros serviços", system))
    
    examples.append(create_example("security-dynamic-groups", cat, "intermediate",
        "Como usar tags em Matching Rules?",
        "Dynamic Groups com tags:\n\n**Regra por tag:**\n```\nALL {\n  resource.type = 'instance',\n  resource.tag.value.Production.Environment = 'prod'\n}\n```\n\n**Múltiplas tags:**\n```\nALL {\n  resource.type = 'instance',\n  resource.tag.value.Production.Environment = 'prod',\n  resource.tag.value.Production.Team = 'devops'\n}\n```\n\n**ANY com tags:**\n```\nANY {\n  resource.tag.value.Production.Environment = 'prod',\n  resource.tag.value.Production.Environment = 'staging'\n}\n```\n\n**Requisitos:**\n- Tags devem ser defined tags (não free-form)\n- Tag namespace deve existir\n- Recursos devem estar taggeados\n\n**Best Practice:** Use tags para organização flexível", system))
    
    examples.append(create_example("security-dynamic-groups", cat, "intermediate",
        "Como debugar Dynamic Group que não funciona?",
        "Debug de Dynamic Groups:\n\n**1. Verifique matching:**\n```bash\noci iam dynamic-group get --dynamic-group-id <ocid>\n# Veja matching rule\n```\n\n**2. Teste regra no Console:**\n- Dynamic Groups → Test Matching Rule\n- Insira resource OCID\n- Veja se match\n\n**3. Verifique recursos:**\n```bash\noci compute instance list --compartment-id <ocid>\n# Confirme recursos existem\n```\n\n**4. Common issues:**\n- OCID errado na regra\n- Tipo de recurso errado (instance vs fnfunc)\n- Tag não aplicada\n- Policy não criada\n\n**5. Verifique policies:**\n```\nAllow dynamic-group MyGroup to ...\n```\n\n**6. Audit logs:**\n```bash\noci audit event list --query \"?data.identity.callerType=='InstancePrincipal'\"\n```", system))
    
    examples.append(create_example("security-dynamic-groups", cat, "intermediate",
        "Como criar Dynamic Group para OKE?",
        "Dynamic Groups para OKE:\n\n**Para worker nodes:**\n```\nALL {\n  resource.type = 'instance',\n  resource.compartment.id = '<compartment-ocid>',\n  resource.tag.value.OKE.Cluster = '<cluster-name>'\n}\n```\n\n**Para OKE cluster:**\n```\nALL {resource.type = 'okecluster', resource.id = '<cluster-ocid>'}\n```\n\n**Policy para OKE acessar outros serviços:**\n```\nAllow dynamic-group OKEWorkers to read object-family in compartment Prod\nAllow dynamic-group OKECluster to manage virtual-network-family in compartment Shared\n```\n\n**Use case:**\n- Pods acessando Object Storage\n- OKE criando Load Balancers\n- Cluster acessando Vault\n\n**Nota:** OKE usa service accounts para fine-grained access", system))
    
    # Advanced (2)
    examples.append(create_example("security-dynamic-groups", cat, "advanced",
        "Como implementar acesso cross-compartment?",
        "Acesso cross-compartment com Dynamic Groups:\n\n**Cenário:** Instâncias em Dev acessam Database em Prod\n\n**1. Dynamic Group em Dev:**\n```\nALL {instance.compartment.id = '<dev-ocid>'}\n```\n\n**2. Policy em Prod:**\n```\nAllow dynamic-group DevInstances to read database-family in compartment Prod\n```\n\n**3. Na aplicação:**\n```python\nimport oci\n\nprovider = principals.InstancePrincipalsSecurityTokenProvider()\ndb = oci.database.DatabaseClient(config={}, provider=provider)\n# Acessa database em Prod\n```\n\n**Segurança:**\n- Least privilege (só read)\n- Audit via CloudTrail\n- Network security (VCN peering, security lists)\n\n**Best Practice:** Documente todos acessos cross-compartment", system))
    
    examples.append(create_example("security-dynamic-groups", cat, "advanced",
        "Como migrar IAM Roles (AWS) para Dynamic Groups?",
        "Migração IAM Roles → Dynamic Groups:\n\n**1. Mapeamento:**\n- IAM Role → Dynamic Group + Policy\n- IAM Instance Profile → Instance Principal\n- Trust Policy → Matching Rule\n\n**2. Exemplo AWS:**\n```json\n{\n  \"Version\": \"2012-10-17\",\n  \"Statement\": [{\n    \"Effect\": \"Allow\",\n    \"Principal\": {\"Service\": \"ec2.amazonaws.com\"},\n    \"Action\": \"sts:AssumeRole\"\n  }]\n}\n```\n\n**3. Equivalente OCI:**\n```\nALL {resource.type = 'instance', resource.compartment.id = '<ocid>'}\n```\n\n**4. Policy:**\n```\nAllow dynamic-group MyInstances to manage object-family in tenancy\n```\n\n**5. Na instância:**\n- AWS: IMDSv2 → STS AssumeRole\n- OCI: Instance Principal automático\n\n**Diferenças:**\n- OCI é mais simples\n- Menos configuração manual\n- Sem rotação de credentials", system))
    
    return examples

def generate_security_federation():
    examples = []
    system = "You are an OCI security specialist with expertise in federation and SSO. Provide technical guidance on SAML, OIDC, and identity providers."
    cat = "security/federation"
    
    # Beginner (3)
    examples.append(create_example("security-federation", cat, "beginner",
        "O que é federação de identidade no OCI?",
        "Federação de identidade permite usar provedores externos (Azure AD, Okta, etc.) para autenticação no OCI.\n\n**Benefícios:**\n- SSO (Single Sign-On)\n- Gerenciamento centralizado de usuários\n- MFA no provedor\n- Offboarding automático\n\n**Protocolos suportados:**\n- SAML 2.0 (mais comum)\n- OIDC (OpenID Connect)\n\n**Fluxo SAML:**\n1. Usuário acessa OCI Console\n2. Redirecionado para IdP\n3. Autentica no IdP\n4. IdP retorna assertion SAML\n5. OCI concede acesso\n\nDocs: https://docs.oracle.com/en-us/iaas/Content/Identity/Concepts/federation.htm", system))
    
    examples.append(create_example("security-federation", cat, "beginner",
        "Quais Identity Providers são suportados?",
        "Identity Providers suportados:\n\n**Enterprise:**\n- Microsoft Active Directory (via ADFS)\n- Azure Active Directory\n- Okta\n- Ping Identity\n- OneLogin\n\n**Oracle:**\n- Oracle IDCS (Identity Cloud Service)\n\n**Open Source:**\n- Keycloak\n- Shibboleth\n\n**Requisitos:**\n- Suporte a SAML 2.0\n- Ou OIDC para federation mais moderna\n\n**Recomendação:**\n- Azure AD: comum em empresas Microsoft\n- Okta: multi-cloud\n- IDCS: ecossistema Oracle\n\n[CHECK DOCS] Verifique compatibilidade de versão.", system))
    
    examples.append(create_example("security-federation", cat, "beginner",
        "Como configurar federação com Azure AD?",
        "Configurando federação Azure AD → OCI:\n\n**1. No Azure AD:**\n- Enterprise Applications → New Application\n- 'Non-gallery application'\n- Nome: OCI Federation\n\n**2. Configure SAML:**\n- Single sign-on → SAML\n- Download Federation Metadata XML\n\n**3. No OCI:**\n```bash\noci iam identity-provider create \\\n  --compartment-id <tenancy-ocid> \\\n  --name AzureAD \\\n  --protocol-type SAML2 \\\n  --metadata-url <azure-metadata-url>\n```\n\n**4. Mapeie grupos:**\n- Azure AD Groups → OCI Groups\n\n**5. Teste login via Console OCI", system))
    
    # Intermediate (5)
    examples.append(create_example("security-federation", cat, "intermediate",
        "Como mapear grupos do IdP para OCI?",
        "Mapeamento de grupos:\n\n**1. No Azure AD:**\n- Crie grupos (OCI-Admins, OCI-Developers)\n- Add usuários aos grupos\n\n**2. No OCI:**\n```bash\n# Crie grupos OCI\noci iam group create \\\n  --compartment-id <tenancy-ocid> \\\n  --name OCI-Admins\n\n# Mapeie (via Console ou CLI)\noci iam identity-provider-and-group-mapping create \\\n  --identity-provider-id <idp-ocid> \\\n  --idp-group-name \"OCI-Admins\" \\\n  --group-id <oci-group-ocid>\n```\n\n**3. Policies:**\n```\nAllow group OCI-Admins to manage all-resources in tenancy\n```\n\n**Fluxo:**\n- User loga no Azure AD\n- Azure retorna grupos no assertion SAML\n- OCI mapeia para grupos locais\n- Usuário herda policies dos grupos", system))
    
    examples.append(create_example("security-federation", cat, "intermediate",
        "Como configurar SSO direto para Console?",
        "SSO direto para OCI Console:\n\n**1. No IdP (Azure AD):**\n- Configure Enterprise Application\n- SAML Single Sign-On\n- Reply URL: https://idcs-<region>.identity.oraclecloud.com\n\n**2. No OCI:**\n- Identity → Federation → Identity Providers\n- Configure metadata\n- Enable federation\n\n**3. URL de login:**\n```\nhttps://cloud.oracle.com/?tenant=<tenant-name>\n```\n\n**4. Usuários:**\n- Acessam via portal do IdP\n- Ou URL direta do OCI\n- Redirecionados para IdP automaticamente\n\n**Session timeout:**\n- Configure no IdP\n- Default OCI: 12 horas\n\n**Best Practice:** Force MFA no IdP", system))
    
    examples.append(create_example("security-federation", cat, "intermediate",
        "Como usar OIDC para federation?",
        "Federação com OIDC:\n\n**OIDC vs SAML:**\n- OIDC: mais moderno, baseado em JSON/REST\n- SAML: mais maduro, XML-based\n\n**Configuração OIDC:**\n```bash\noci iam identity-provider create \\\n  --compartment-id <tenancy-ocid> \\\n  --name MyOIDC \\\n  --protocol-type OIDC \\\n  --description \"OIDC Provider\" \\\n  --claims \"email,groups\"\n```\n\n**Endpoints necessários:**\n- Authorization endpoint\n- Token endpoint\n- JWKS URI (chaves públicas)\n\n**Fluxo:**\n1. Redirect para IdP\n2. User autentica\n3. IdP retorna ID Token + Access Token\n4. OCI valida token\n5. Concede acesso\n\n**Use case:** Aplicações modernas, APIs", system))
    
    examples.append(create_example("security-federation", cat, "intermediate",
        "Como configurar federação para CLI/SDK?",
        "Federação para CLI/SDK:\n\n**1. OCI CLI com SAML:**\n```bash\noci login sso --profile azure-ad\n# Abre browser para autenticação\n# Token válido por [MUTABLE] 1 hora\n```\n\n**2. SDK Python:**\n```python\nfrom oci.auth import token\n\ntoken_provider = token.SecurityTokenProvider()\nconfig = oci.config.from_file(token_provider=token_provider)\n```\n\n**3. Renovação automática:**\n- Tokens expiram\n- Re-autentique periodicamente\n- Use refresh tokens se suportado\n\n**Limitações:**\n- Menos comum que Instance Principal\n- Requer interação do usuário\n- Melhor para desenvolvimento\n\n**Produção:** Use Instance Principal ou Resource Principal", system))
    
    examples.append(create_example("security-federation", cat, "intermediate",
        "Como debugar problemas de federação?",
        "Debug de federação:\n\n**1. Verifique Identity Provider:**\n```bash\noci iam identity-provider get --identity-provider-id <ocid>\n```\n\n**2. Audit logs:**\n```bash\noci audit event list --query \"?data.eventName=='identity.login'\"\n```\n\n**3. Common issues:**\n- Clock skew (sincronize relógios)\n- Certificate expirado\n- Claims não mapeados\n- Groups não encontrados\n\n**4. No IdP:**\n- Verifique logs de autenticação\n- Valide assertion SAML\n- Teste com ferramenta SAML tracer\n\n**5. SAML tracer (browser extension):**\n- Capture assertion\n- Verifique attributes\n- Valide signature\n\n**6. OCI Console:**\n- Identity → Audit\n- Veja tentativas de login", system))
    
    # Advanced (2)
    examples.append(create_example("security-federation", cat, "advanced",
        "Como implementar federação multi-cloud?",
        "Federação multi-cloud:\n\n**Cenário:** Usuários acessam OCI, AWS, Azure com mesmo login\n\n**1. IdP central (Okta/Azure AD):**\n- Configure aplicações para cada cloud\n- Mapeie grupos consistentes\n\n**2. OCI:**\n```\nAllow group Cloud-Admins to manage all-resources in tenancy\n```\n\n**3. AWS:**\n- SAML Role → Cloud-Admins\n- Trust relationship com IdP\n\n**4. Azure:**\n- Enterprise App → OCI\n- Role assignments\n\n**5. Mapeamento de grupos:**\n```\nOkta Group \"Cloud-Admins\"\n  → OCI Group \"Cloud-Admins\"\n  → AWS Role \"Cloud-Admins\"\n  → Azure RBAC \"Contributor\"\n```\n\n**Benefícios:**\n- SSO único\n- Gerenciamento centralizado\n- Compliance unificado", system))
    
    examples.append(create_example("security-federation", cat, "advanced",
        "Como migrar de SAML para OIDC?",
        "Migração SAML → OIDC:\n\n**1. Avalie impacto:**\n- Aplicações suportam OIDC?\n- Claims necessários\n- Grupos/roles mapeamento\n\n**2. Configure OIDC em paralelo:**\n```bash\noci iam identity-provider create \\\n  --protocol-type OIDC \\\n  --name MyIdP-OIDC\n```\n\n**3. Teste com usuários piloto:**\n- Grupo limitado\n- Valide acesso\n- Colete feedback\n\n**4. Migre gradualmente:**\n- Comunique mudança\n- Atualize documentação\n- Treine usuários\n\n**5. Deprecie SAML:**\n- Mantenha como fallback\n- Remova após confirmação\n\n**Benefícios OIDC:**\n- Mais leve (JSON vs XML)\n- Melhor para mobile/APIs\n- Suporte nativo em frameworks modernos", system))
    
    return examples

def generate_security_vault_secrets():
    examples = []
    system = "You are an OCI security specialist with expertise in Vault service. Provide technical guidance on secrets management, rotation, and access control."
    cat = "security/vault-secrets"
    
    # Beginner (3)
    examples.append(create_example("security-vault-secrets", cat, "beginner",
        "O que é OCI Vault?",
        "OCI Vault é um serviço gerenciado para gerenciar secrets e chaves de criptografia.\n\n**Componentes:**\n- Vault: container lógico\n- Secrets: passwords, API keys, connection strings\n- Keys: chaves de criptografia (symmetric/asymmetric)\n\n**Casos de uso:**\n- Secrets de database\n- API keys\n- Certificados TLS\n- Chaves de criptografia\n\n**Benefícios:**\n- Centralizado\n- Auditado\n- Rotação automática\n- Integration com outros serviços OCI\n\n**Diferença AWS:** Similar ao AWS Secrets Manager + KMS\n\n[MUTABLE] Preços por vault e operações.\n\nDocs: https://docs.oracle.com/en-us/iaas/Content/KeyManagement/", system))
    
    examples.append(create_example("security-vault-secrets", cat, "beginner",
        "Como criar um Vault?",
        "Criando Vault:\n\n**Via Console:**\n1. Identity & Security → Vault\n2. 'Create Vault'\n3. Configure:\n   - Compartment\n   - Name\n   - Protection mode (HSM ou Software)\n4. Create\n\n**Via CLI:**\n```bash\noci kms management vault create \\\n  --compartment-id <ocid> \\\n  --display-name prod-vault \\\n  --vault-type DEFAULT\n```\n\n**Protection modes:**\n- HSM: hardware, FIPS 140-2 Level 3\n- Software: mais econômico\n\n**Tipos de Vault:**\n- DEFAULT: secrets + keys\n- VIRTUAL_PRIVATE: isolamento adicional\n\n[CHECK DOCS] Limites de vaults por compartment.", system))
    
    examples.append(create_example("security-vault-secrets", cat, "beginner",
        "Como criar um secret?",
        "Criando secret:\n\n**Via Console:**\n1. Vault → Secrets\n2. 'Create Secret'\n3. Configure:\n   - Name\n   - Secret value\n   - Encryption key (opcional)\n4. Create\n\n**Via CLI:**\n```bash\noci kms secret create \\\n  --vault-id <vault-ocid> \\\n  --key-id <key-ocid> \\\n  --secret-name db-password \\\n  --secret-content '{\"content\": \"MyS3cr3tP@ss\"}'\n```\n\n**Best Practices:**\n- Names descritivos\n- Use encryption key dedicada\n- Enable versioning\n- Configure rotation\n\n**Acesso:** Via policies e dynamic groups", system))
    
    # Intermediate (5)
    examples.append(create_example("security-vault-secrets", cat, "intermediate",
        "Como ler secrets via SDK?",
        "Lendo secrets via SDK:\n\n**Python:**\n```python\nimport oci\nfrom oci.key_management import KmsSecretClient\n\n# Config\nconfig = oci.config.from_file()\nsecret_client = KmsSecretClient(config, service_endpoint='<vault-endpoint>')\n\n# Read secret\nsecret = secret_client.get_secret(secret_id='<secret-ocid>')\npassword = secret.data.secret_content.content\n\n# Use secret\nconnect_to_db(password=secret)\n```\n\n**Node.js:**\n```javascript\nconst secret = await secretClient.getSecret({\n  secretId: '<secret-ocid>'\n});\nconst password = secret.data.secretContent.content;\n```\n\n**Policy necessária:**\n```\nAllow group MyApp to read secret-family in compartment Prod\n```\n\n**Best Practice:** Cache secrets em memória (não em disco)", system))
    
    examples.append(create_example("security-vault-secrets", cat, "intermediate",
        "Como configurar rotação automática?",
        "Rotação automática de secrets:\n\n**Via Console:**\n1. Secret → Rotation\n2. 'Create Rotation Schedule'\n3. Configure:\n   - Rotation interval (30, 60, 90 dias)\n   - Next rotation time\n4. Save\n\n**Via CLI:**\n```bash\noci kms secret create-rotation-schedule \\\n  --secret-id <secret-ocid> \\\n  --rotation-period P30D \\\n  --next-rotation-time 2024-04-01T00:00:00Z\n```\n\n**Rotação manual:**\n```bash\noci kms secret rotate \\\n  --secret-id <secret-ocid>\n```\n\n**Versions:**\n- Cada rotação cria nova version\n- Version atual é default\n- Versions antigas permanecem (audit)\n\n**Best Practice:** Rotação de 30-90 dias para passwords", system))
    
    examples.append(create_example("security-vault-secrets", cat, "intermediate",
        "Como integrar Vault com Functions?",
        "Integração Functions + Vault:\n\n**1. Dynamic Group para Functions:**\n```\nALL {resource.type = 'fnfunc', resource.compartment.id = '<ocid>'}\n```\n\n**2. Policy:**\n```\nAllow dynamic-group MyFunctions to read secret-family in compartment Prod\n```\n\n**3. Function code:**\n```python\nimport oci\n\ndef handler(ctx, data):\n    config = oci.config.from_file()\n    secret_client = oci.vault.VaultClient(config)\n    \n    secret = secret_client.get_secret(secret_id='<ocid>')\n    password = secret.data.secret_content.content\n    \n    # Use password\n    return {'status': 'connected'}\n```\n\n**Vantagem:** Secrets não hardcoded no código\n\n**Security:** Instance Principal + least privilege", system))
    
    examples.append(create_example("security-vault-secrets", cat, "intermediate",
        "Como versionar secrets?",
        "Versionamento de secrets:\n\n**Automático (com rotação):**\n- Cada rotação cria nova version\n- Version numbering: 1, 2, 3...\n\n**Manual:**\n```bash\noci kms secret version create \\\n  --secret-id <secret-ocid> \\\n  --secret-content '{\"content\": \"NewPassword123\"}'\n```\n\n**Listar versions:**\n```bash\noci kms secret version list --secret-id <secret-ocid>\n```\n\n**Rollback para version anterior:**\n```bash\noci kms secret update \\\n  --secret-id <secret-ocid> \\\n  --current-version-id <version-ocid>\n```\n\n**Use cases:**\n- Rollback após problema\n- A/B testing de credentials\n- Audit trail\n\n**Retention:** [CHECK DOCS] Versions permanecem até delete manual", system))
    
    examples.append(create_example("security-vault-secrets", cat, "intermediate",
        "Como auditar acesso a secrets?",
        "Auditoria de acesso a secrets:\n\n**Audit logs:**\n```bash\noci audit event list \\\n  --compartment-id <ocid> \\\n  --query \"?data.resourceName=='secret-get'\"\n```\n\n**O que é auditado:**\n- Get secret\n- Create/update secret\n- Delete secret\n- Rotation events\n\n**Exemplo de log:**\n```json\n{\n  \"eventName\": \"GetSecret\",\n  \"identity\": {\n    \"userPrincipalName\": \"app-user\",\n    \"callerType\": \"InstancePrincipal\"\n  },\n  \"data\": {\n    \"resourceName\": \"db-password\"\n  }\n}\n```\n\n**Alertas:**\n- Configure Events para acesso não autorizado\n- Notifique via Email/Slack\n\n**Best Practice:** Review logs periodicamente", system))
    
    # Advanced (2)
    examples.append(create_example("security-vault-secrets", cat, "advanced",
        "Como implementar secret sharing entre compartments?",
        "Secret sharing cross-compartment:\n\n**Cenário:** Secret em Prod, acesso de Dev\n\n**1. Vault em Prod:**\n```bash\noci kms secret create \\\n  --vault-id <prod-vault-ocid> \\\n  --secret-name shared-api-key\n```\n\n**2. Policy em Prod:**\n```\nAllow group DevTeam to read secret-family in compartment Prod\n  where target.secret.id = '<secret-ocid>'\n```\n\n**3. Em Dev (application):**\n```python\nconfig = oci.config.from_file()\nsecret_client = oci.vault.VaultClient(\n    config,\n    service_endpoint='<prod-vault-endpoint>'\n)\nsecret = secret_client.get_secret(secret_id='<secret-ocid>')\n```\n\n**Segurança:**\n- Least privilege (só read)\n- Audit de acesso\n- Network security (VCN peering se privado)\n\n**Alternativa:** Replicate secret em Dev", system))
    
    examples.append(create_example("security-vault-secrets", cat, "advanced",
        "Como migrar AWS Secrets Manager para OCI Vault?",
        "Migração Secrets Manager → OCI Vault:\n\n**1. Exporte secrets AWS:**\n```bash\naws secretsmanager list-secrets\naws secretsmanager get-secret-value --secret-id my-secret\n```\n\n**2. Crie Vault no OCI:**\n```bash\noci kms management vault create \\\n  --compartment-id <ocid> \\\n  --display-name migrated-vault\n```\n\n**3. Migre secrets:**\n```python\nimport boto3\nimport oci\n\n# AWS\naws = boto3.client('secretsmanager')\nsecret = aws.get_secret_value(SecretId='my-secret')\n\n# OCI\noci_client = oci.vault.VaultClient(oci_config)\noci_client.create_secret({\n    'vault_id': vault_ocid,\n    'secret_name': 'my-secret',\n    'secret_content': {'content': secret['SecretString']}\n})\n```\n\n**4. Atualize aplicações:**\n- AWS SDK → OCI SDK\n- Update policies\n\n**Diferenças:**\n- OCI Vault unifica secrets + keys\n- Rotação similar\n- Pricing diferente", system))
    
    return examples

# Main execution
def main():
    generators = {
        "security-iam-basics": generate_security_iam_basics,
        "security-policies": generate_security_policies,
        "security-dynamic-groups": generate_security_dynamic_groups,
        "security-federation": generate_security_federation,
        "security-vault-secrets": generate_security_vault_secrets,
    }
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    for category, generator in generators.items():
        examples = generator()
        write_jsonl(f"{category}.jsonl", examples)
    
    print(f"\nTotal: {len(generators)} files generated")

if __name__ == "__main__":
    main()
