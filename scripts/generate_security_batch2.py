#!/usr/bin/env python3
"""
Generate JSONL files for remaining Security categories and Migration categories.
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

# ============ SECURITY VAULT KEYS ============
def generate_security_vault_keys():
    examples = []
    system = "You are an OCI security specialist with expertise in Vault and Key Management. Provide technical guidance on encryption keys, HSM, and key lifecycle."
    cat = "security/vault-keys"
    
    # Beginner (3)
    examples.append(create_example("security-vault-keys", cat, "beginner",
        "O que são chaves de criptografia no OCI Vault?",
        "Chaves de criptografia no OCI Vault são usadas para proteger dados via criptografia.\n\n**Tipos de chaves:**\n- Symmetric (AES): mesma chave para encrypt/decrypt\n- Asymmetric (RSA): par de chaves (pública/privada)\n\n**Protection modes:**\n- HSM: hardware (FIPS 140-2 Level 3)\n- Software: mais econômico\n\n**Casos de uso:**\n- Encrypt Object Storage\n- Encrypt Block Volumes\n- Encrypt databases\n- Application-level encryption\n\n**Key versions:**\n- Cada key tem múltiplas versions\n- Version atual é usada por default\n- Versions antigas para decrypt histórico\n\n[MUTABLE] Preços por key e operações.\n\nDocs: https://docs.oracle.com/en-us/iaas/Content/KeyManagement/", system))
    
    examples.append(create_example("security-vault-keys", cat, "beginner",
        "Como criar uma chave no Vault?",
        "Criando chave de criptografia:\n\n**Via Console:**\n1. Identity & Security → Vault\n2. Selecione Vault → Keys\n3. 'Create Key'\n4. Configure:\n   - Name\n   - Protection mode (HSM/Software)\n   - Algorithm (AES, RSA)\n   - Key shape (size)\n5. Create\n\n**Via CLI:**\n```bash\noci kms management key create \\\n  --vault-id <vault-ocid> \\\n  --display-name prod-key \\\n  --key-shape '{\"algorithm\": \"AES\", \"length\": 32}' \\\n  --protection-mode HSM\n```\n\n**Algorithms:**\n- AES: 256-bit (symmetric)\n- RSA: 2048, 3072, 4096 (asymmetric)\n\n[CHECK DOCS] Limites de chaves por vault.", system))
    
    examples.append(create_example("security-vault-keys", cat, "beginner",
        "Qual a diferença entre HSM e Software?",
        "HSM vs Software protection:\n\n**HSM (Hardware Security Module):**\n- Hardware dedicado\n- FIPS 140-2 Level 3 certified\n- Mais seguro (chaves nunca saem do HSM)\n- Mais caro\n- Compliance: PCI-DSS, HIPAA\n\n**Software:**\n- Criptografia em software\n- FIPS 140-2 Level 1\n- Mais econômico\n- Performance boa para maioria dos casos\n\n**Quando usar HSM:**\n- Requisitos de compliance\n- Dados altamente sensíveis\n- Indústria financeira/governo\n\n**Quando usar Software:**\n- Desenvolvimento/testes\n- Cargas menos críticas\n- Orçamento limitado\n\n[MUTABLE] HSM custa ~10x mais que software.", system))
    
    # Intermediate (5)
    examples.append(create_example("security-vault-keys", cat, "intermediate",
        "Como usar chaves para encrypt Object Storage?",
        "Encrypt Object Storage com Vault:\n\n**1. Crie chave no Vault:**\n```bash\noci kms management key create \\\n  --vault-id <vault-ocid> \\\n  --display-name object-storage-key\n```\n\n**2. Policy:**\n```\nAllow group ObjectAdmins to use key-delegate in compartment Prod\n```\n\n**3. Upload com encryption:**\n```bash\noci os object put \\\n  --namespace <namespace> \\\n  --bucket-name my-bucket \\\n  --object-name sensitive.pdf \\\n  --file sensitive.pdf \\\n  --kms-key-id <key-ocid>\n```\n\n**4. Download (decrypt automático):**\n```bash\noci os object get \\\n  --namespace <namespace> \\\n  --bucket-name my-bucket \\\n  --object-name sensitive.pdf \\\n  --file decrypted.pdf\n```\n\n**Server-side encryption:** Automático com chave gerenciada pelo cliente (CMK)", system))
    
    examples.append(create_example("security-vault-keys", cat, "intermediate",
        "Como fazer rotação de chaves?",
        "Rotação de chaves:\n\n**Automática (recomendado):**\n```bash\noci kms management create-key-rotation-schedule \\\n  --key-id <key-ocid> \\\n  --rotation-period P90D \\\n  --next-rotation-time 2024-04-01T00:00:00Z\n```\n\n**Manual:**\n```bash\noci kms management key version create \\\n  --key-id <key-ocid> \\\n  --key-version-meta '{\"version_number\": 2}'\n```\n\n**Via Console:**\n1. Key Details → Create Key Version\n2. Aguarde criação\n3. Nova version se torna ativa\n\n**Impacto:**\n- Dados novos: encrypt com nova version\n- Dados antigos: decrypt com version original\n- OCI gerencia versions automaticamente\n\n**Best Practice:** Rotação de 90 dias para compliance", system))
    
    examples.append(create_example("security-vault-keys", cat, "intermediate",
        "Como encrypt dados na aplicação?",
        "Encrypt na aplicação (SDK Python):\n\n```python\nimport oci\nfrom oci.key_management import KmsCryptoClient\n\n# Config\nconfig = oci.config.from_file()\ncrypto_client = KmsCryptoClient(config, service_endpoint='<vault-endpoint>')\n\n# Encrypt\ndata = b'sensitive data'\nencrypted = crypto_client.encrypt(\n    key_id='<key-ocid>',\n    plaintext=data\n)\nprint(f\"Encrypted: {encrypted.data.ciphertext}\")\n\n# Decrypt\ndecrypted = crypto_client.decrypt(\n    key_id='<key-ocid>',\n    ciphertext=encrypted.data.ciphertext\n)\nprint(f\"Decrypted: {decrypted.data.plaintext}\")\n```\n\n**Policy necessária:**\n```\nAllow group MyApp to use key-delegate in compartment Prod\n```\n\n**Best Practices:**\n- Encrypt antes de persistir\n- Cache em memória (não em disco)\n- Rotate keys periodicamente", system))
    
    examples.append(create_example("security-vault-keys", cat, "intermediate",
        "Como auditar uso de chaves?",
        "Auditoria de uso de chaves:\n\n**Audit logs:**\n```bash\noci audit event list \\\n  --compartment-id <ocid> \\\n  --query \"?data.resourceName=='key-decrypt'\"\n```\n\n**Eventos auditados:**\n- Encrypt\n- Decrypt\n- Create key version\n- Delete key\n- Schedule key deletion\n\n**Exemplo de log:**\n```json\n{\n  \"eventName\": \"Decrypt\",\n  \"identity\": {\n    \"userPrincipalName\": \"app-user\",\n    \"callerType\": \"InstancePrincipal\"\n  },\n  \"data\": {\n    \"resourceName\": \"prod-key\",\n    \"keyId\": \"<ocid>\"\n  }\n}\n```\n\n**Alertas:**\n- Events Service → notificações\n- Accessos fora do horário\n- Volume anormal de decrypts\n\n**Compliance:** Logs retidos no Audit Service", system))
    
    examples.append(create_example("security-vault-keys", cat, "intermediate",
        "Como compartilhar chaves entre compartments?",
        "Compartilhamento cross-compartment:\n\n**Cenário:** Chave em Prod, uso em Dev\n\n**1. Policy em Prod:**\n```\nAllow group DevTeam to use key-delegate in compartment Prod\n  where target.key.id = '<key-ocid>'\n```\n\n**2. Na aplicação (Dev):**\n```python\nconfig = oci.config.from_file()\ncrypto_client = KmsCryptoClient(\n    config,\n    service_endpoint='<prod-vault-endpoint>'\n)\n\nencrypted = crypto_client.encrypt(\n    key_id='<key-ocid>',\n    plaintext=data\n)\n```\n\n**Segurança:**\n- Least privilege (só use, não manage)\n- Audit de acesso\n- Network security\n\n**Alternativa:** Replicate key em Dev", system))
    
    # Advanced (2)
    examples.append(create_example("security-vault-keys", cat, "advanced",
        "Como implementar envelope encryption?",
        "Envelope encryption:\n\n**Conceito:**\n- Data Key (DK): encrypt dados\n- Master Key (MK): encrypt DK\n- MK fica no Vault, DK na memória\n\n**Implementação:**\n```python\nimport oci\n\ncrypto = KmsCryptoClient(config)\n\n# 1. Generate data key\ndk_response = crypto.generate_data_key(\n    key_id='<master-key-ocid>',\n    shape={'algorithm': 'AES', 'length': 32}\n)\ndata_key = dk_response.data.plaintext  # Em memória\nencrypted_dk = dk_response.data.ciphertext  # Persiste\n\n# 2. Encrypt dados com data key\nfrom cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes\ncipher = Cipher(algorithms.AES(data_key), modes.GCM(nonce))\nencryptor = cipher.encryptor()\nciphertext = encryptor.update(data) + encryptor.finalize()\n\n# 3. Persiste: encrypted_dk + ciphertext + nonce\n# 4. Para decrypt: decrypt DK com Vault, depois decrypt dados\n```\n\n**Vantagens:**\n- Menos chamadas ao Vault\n- Mais performance\n- Chave de dados nunca persiste", system))
    
    examples.append(create_example("security-vault-keys", cat, "advanced",
        "Como migrar AWS KMS para OCI Vault?",
        "Migração KMS → OCI Vault:\n\n**1. Exporte chaves AWS:**\n```bash\naws kms list-keys\naws kms describe-key --key-id <id>\n# Chaves não exportáveis diretamente\n# Re-encrypt com nova chave OCI\n```\n\n**2. Crie Vault no OCI:**\n```bash\noci kms management vault create \\\n  --compartment-id <ocid> \\\n  --display-name migrated-vault\n```\n\n**3. Re-encrypt dados:**\n```python\nimport boto3\nimport oci\n\n# AWS KMS\naws_kms = boto3.client('kms')\n\n# OCI Vault\noci_crypto = oci.key_management.KmsCryptoClient(oci_config)\n\n# Para cada dado:\n# 1. Decrypt com AWS KMS\nplain = aws_kms.decrypt(CiphertextBlob=encrypted)\n\n# 2. Encrypt com OCI Vault\nenc = oci_crypto.encrypt(\n    key_id=oci_key_ocid,\n    plaintext=plain['Plaintext']\n)\n```\n\n**4. Atualize aplicações:**\n- AWS SDK → OCI SDK\n- Update IAM → OCI Policies\n\n**Diferenças:**\n- OCI Vault unifica secrets + keys\n- HSM similar\n- API diferente", system))
    
    return examples

# ============ SECURITY ENCRYPTION ============
def generate_security_encryption():
    examples = []
    system = "You are an OCI security specialist with expertise in encryption. Provide technical guidance on encryption at rest, in transit, and best practices."
    cat = "security/encryption"
    
    # Beginner (3)
    examples.append(create_example("security-encryption", cat, "beginner",
        "Como funciona encryption no OCI?",
        "Encryption no OCI é implementada em múltiplas camadas:\n\n**Encryption at rest:**\n- Block Volumes: AES-256 automático\n- Object Storage: server-side encryption\n- Databases: Transparent Data Encryption (TDE)\n- File Storage: encryption automático\n\n**Encryption in transit:**\n- TLS 1.2+ para todas as APIs\n- HTTPS para Console\n- SSH para instâncias\n- IPSec para VPN/FastConnect\n\n**Chaves:**\n- Oracle-managed: default (transparente)\n- Customer-managed: Vault (controle total)\n\n**Default:** Todos dados encryptados sem ação necessária\n\nDocs: https://docs.oracle.com/en-us/iaas/Content/Security/", system))
    
    examples.append(create_example("security-encryption", cat, "beginner",
        "O que é TDE (Transparent Data Encryption)?",
        "TDE (Transparent Data Encryption):\n\n**O que é:**\n- Encryption automático de databases Oracle\n- Encrypt datafiles, backups, logs\n- Transparente para aplicações\n\n**Como funciona:**\n```\nAplicação → SQL → Database\n              ↓\n         TDE encrypt/decrypt\n              ↓\n         Datafiles (encrypted)\n```\n\n**Algorithms:**\n- AES-256 (recomendado)\n- AES-128\n- 3DES168 (legado)\n\n**Chaves:**\n- Wallet local (on-premises)\n- OCI Vault (cloud, recomendado)\n\n**Performance:** Impacto mínimo (<5%)\n\n**Compliance:** PCI-DSS, HIPAA, SOX", system))
    
    examples.append(create_example("security-encryption", cat, "beginner",
        "Como habilitar encryption em Block Volume?",
        "Encryption em Block Volumes:\n\n**Default (Oracle-managed):**\n- Automático, sem configuração\n- AES-256\n- Chaves gerenciadas pela Oracle\n\n**Customer-managed (Vault):**\n\n**Via Console:**\n1. Block Storage → Create Volume\n2. Encryption → 'Customer-managed key'\n3. Selecione chave do Vault\n4. Create\n\n**Via CLI:**\n```bash\noci bv volume create \\\n  --compartment-id <ocid> \\\n  --availability-domain <AD> \\\n  --size-in-gbs 100 \\\n  --kms-key-id <key-ocid>\n```\n\n**Vantagens:**\n- Controle das chaves\n- Rotação própria\n- Audit de acesso\n\n[MUTABLE] Vault tem custo adicional.", system))
    
    # Intermediate (5)
    examples.append(create_example("security-encryption", cat, "intermediate",
        "Como configurar encryption in transit?",
        "Encryption in transit:\n\n**TLS para APIs:**\n- Automático (HTTPS)\n- TLS 1.2 mínimo\n- Cipher suites fortes\n\n**SSH para instâncias:**\n```bash\n# Gere chaves fortes\nssh-keygen -t ed25519 -a 100\n\n# Configure SSH server\nPermitRootLogin no\nPasswordAuthentication no\nPubkeyAuthentication yes\n```\n\n**Load Balancer:**\n```bash\noci lb certificate create \\\n  --load-balancer-id <ocid> \\\n  --certificate-name my-cert \\\n  --ca-certificate file://ca.pem \\\n  --public-certificate file://cert.pem \\\n  --private-key file://key.pem\n```\n\n**FastConnect:**\n- IPSec tunnel\n- MACsec (camada física)\n\n**Best Practice:** TLS 1.3 quando disponível", system))
    
    examples.append(create_example("security-encryption", cat, "intermediate",
        "Como usar encryption com Object Storage?",
        "Encryption com Object Storage:\n\n**Server-side (default):**\n- Automático\n- Oracle-managed keys\n- Transparente\n\n**Customer-managed keys:**\n```bash\noci os object put \\\n  --namespace <ns> \\\n  --bucket my-bucket \\\n  --object sensitive.txt \\\n  --file sensitive.txt \\\n  --kms-key-id <key-ocid>\n```\n\n**Client-side encryption:**\n```python\nfrom cryptography.fernet import Fernet\n\n# Generate key\nkey = Fernet.generate_key()\nf = Fernet(key)\n\n# Encrypt before upload\nwith open('file.txt', 'rb') as file:\n    encrypted = f.encrypt(file.read())\n\n# Upload encrypted\noci os object put(..., upload_data=encrypted)\n\n# Download and decrypt\ndecrypted = f.decrypt(encrypted)\n```\n\n**Use case:** Client-side para controle total", system))
    
    examples.append(create_example("security-encryption", cat, "intermediate",
        "Como gerenciar chaves de encryption?",
        "Gerenciamento de chaves:\n\n**Lifecycle:**\n1. Create\n2. Enable (default)\n3. Rotate (periódico)\n4. Disable (quando não usar)\n5. Schedule deletion\n6. Delete\n\n**Rotação:**\n```bash\noci kms management key version create \\\n  --key-id <ocid>\n\n# Ou automática\noci kms management create-key-rotation-schedule \\\n  --key-id <ocid> \\\n  --rotation-period P90D\n```\n\n**Deletion:**\n```bash\noci kms management key schedule-deletion \\\n  --key-id <ocid> \\\n  --time-of-deletion 2024-12-31T23:59:59Z\n```\n\n**Best Practices:**\n- Rotação de 90 dias\n- Separe chaves por ambiente\n- Audit acesso\n- Backup de chaves críticas", system))
    
    examples.append(create_example("security-encryption", cat, "intermediate",
        "Como auditar operações de encryption?",
        "Auditoria de encryption:\n\n**Audit logs:**\n```bash\noci audit event list \\\n  --query \"?data.resourceName=='key-decrypt'\"\n```\n\n**Eventos:**\n- Encrypt/Decrypt\n- Key create/delete\n- Key rotation\n- Access a secrets\n\n**Cloud Guard:**\n- Detecta anomalias\n- Chaves não rotacionadas\n- Acesso incomum\n\n**Exemplo de query:**\n```sql\n-- No Logging\nSELECT json_value(data, '$.resourceName') as resource,\n       json_value(identity, '$.userPrincipalName') as user\nFROM audit_logs\nWHERE event_name = 'Decrypt'\n  AND time > TIMESTAMP '-1 day';\n```\n\n**Alertas:**\n- Events Service → notificações\n- Slack/Email/PagerDuty", system))
    
    examples.append(create_example("security-encryption", cat, "intermediate",
        "Qual o impacto de performance da encryption?",
        "Impacto de performance:\n\n**Block Volumes:**\n- Oracle-managed: <1% impacto\n- Customer-managed: 2-5% impacto\n- Hardware encryption: mínimo\n\n**Object Storage:**\n- Server-side: <1% impacto\n- Client-side: depende do client\n\n**Database TDE:**\n- TDE habilitado: 3-7% impacto\n- Com HSM: 5-10% impacto\n- Cache reduz impacto\n\n**Network (TLS):**\n- TLS 1.2: 2-3% impacto\n- TLS 1.3: 1-2% impacto\n- Hardware offload: mínimo\n\n**Otimização:**\n- Use HSM para cargas críticas\n- Cache chaves em memória\n- Batch operations\n\n**Trade-off:** Segurança > Performance para dados sensíveis", system))
    
    # Advanced (2)
    examples.append(create_example("security-encryption", cat, "advanced",
        "Como implementar encryption de ponta-a-ponta?",
        "Encryption ponta-a-ponta:\n\n**Arquitetura:**\n```\nClient → Encrypt → OCI → Decrypt → Destino\n  ↓                        ↓\nChave do client        Chave do destino\n```\n\n**Implementação:**\n```python\n# Client-side\nfrom cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes\nimport os\n\n# Generate random key e nonce\nkey = os.urandom(32)  # AES-256\nnonce = os.urandom(12)  # GCM nonce\n\n# Encrypt\ncipher = Cipher(algorithms.AES(key), modes.GCM(nonce))\nencryptor = cipher.encryptor()\nciphertext = encryptor.update(data) + encryptor.finalize()\n\n# Send: nonce + ciphertext + tag\n# Chave enviada separadamente (ex: Vault)\n\n# Server-side (OCI)\n# Decrypt com chave do Vault\n# Re-encrypt para destino final\n```\n\n**Chaves:**\n- Client gera e controla\n- OCI não vê chave plaintext\n- Key exchange via Vault\n\n**Use case:** Dados altamente sensíveis, compliance rigoroso", system))
    
    examples.append(create_example("security-encryption", cat, "advanced",
        "Como migrar encryption de on-premises para OCI?",
        "Migração de encryption:\n\n**1. Inventário:**\n- Quais dados encryptados?\n- Quais algoritmos?\n- Onde estão as chaves?\n\n**2. Chaves on-premises:**\n- HSM local → OCI Vault HSM\n- Software → OCI Vault software\n- Exporte chaves (se possível)\n\n**3. Database TDE:**\n```sql\n-- On-premises\nADMINISTER KEY MANAGEMENT EXPORT KEYS\n  TO '/backup/tde_keys' \n  IDENTIFIED BY password;\n\n-- OCI\nADMINISTER KEY MANAGEMENT IMPORT KEYS\n  FROM 'oci://bucket@namespace/tde_keys'\n  IDENTIFIED BY password;\n```\n\n**4. Block Volumes:**\n- Migre dados\n- Re-encrypt com chaves OCI\n\n**5. Atualize aplicações:**\n- SDKs\n- Key management\n\n**Desafios:**\n- Chaves não exportáveis (alguns HSMs)\n- Re-encrypt necessário\n- Downtime planejado", system))
    
    return examples

# ============ SECURITY CLOUD GUARD ============
def generate_security_cloud_guard():
    examples = []
    system = "You are an OCI security specialist with expertise in Cloud Guard. Provide technical guidance on security monitoring, detection, and response."
    cat = "security/cloud-guard"
    
    # Beginner (3)
    examples.append(create_example("security-cloud-guard", cat, "beginner",
        "O que é OCI Cloud Guard?",
        "Cloud Guard é o serviço de segurança contínua e monitoring do OCI.\n\n**Funcionalidades:**\n- Detecção de ameaças\n- Monitoramento de configuração\n- Resposta automatizada\n- Security scoring\n\n**Componentes:**\n- Detectors: detectam problemas\n- Responders: ações automáticas\n- Targets: recursos monitorados\n- Recipes: regras de detecção\n\n**Casos de uso:**\n- Security buckets públicos\n- Instâncias sem patch\n- IAM policies permissivas\n- Network exposure\n\n**Diferença AWS:** Similar ao AWS Security Hub + GuardDuty\n\n[MUTABLE] Preços por eventos processados.\n\nDocs: https://docs.oracle.com/en-us/iaas/Content/CloudGuard/", system))
    
    examples.append(create_example("security-cloud-guard", cat, "beginner",
        "Como habilitar Cloud Guard?",
        "Habilitando Cloud Guard:\n\n**Via Console:**\n1. Security & Compliance → Cloud Guard\n2. 'Enable Cloud Guard'\n3. Configure:\n   - Compartment target\n   - Recipes (default ou custom)\n4. Enable\n\n**Via CLI:**\n```bash\noci cloud-guard configuration set \\\n  --compartment-id <ocid> \\\n  --is-enabled true\n```\n\n**Targets:**\n- Tenancy (tudo)\n- Compartment específico\n- Recursos específicos\n\n**Recipes:**\n- Security Recipes (default)\n- Activity Recipes\n- Custom recipes\n\n**Próximos passos:** Configure responders para ação automática", system))
    
    examples.append(create_example("security-cloud-guard", cat, "beginner",
        "O que são Security Zones?",
        "Security Zones:\n\n**O que é:**\n- Compartments com políticas de segurança reforçadas\n- Impede configurações inseguras\n- Enforcement automático\n\n**Restrições:**\n- Sem buckets públicos\n- Sem security lists permissivas\n- Encryption obrigatória\n- MFA para acesso\n\n**Como funciona:**\n```\nTentativa de criar recurso\n         ↓\nSecurity Zone valida\n         ↓\nPermite (seguro) ou Nega (inseguro)\n```\n\n**Via Console:**\n1. Security & Compliance → Security Zones\n2. 'Create Security Zone'\n3. Selecione compartment\n4. Enable\n\n**Diferença Cloud Guard:**\n- Security Zones: previne (antes)\n- Cloud Guard: detecta (depois)", system))
    
    # Intermediate (5)
    examples.append(create_example("security-cloud-guard", cat, "intermediate",
        "Como configurar detectors custom?",
        "Detectors custom:\n\n**Via Console:**\n1. Cloud Guard → Detectors\n2. 'Create Detector'\n3. Configure:\n   - Name\n   - Resource type\n   - Condition\n   - Risk level\n4. Create\n\n**Exemplo - Bucket público:**\n```json\n{\n  \"name\": \"Public Bucket Detector\",\n  \"resourceType\": \"OBJECT_STORAGE_BUCKET\",\n  \"condition\": \"isPublic == true\",\n  \"riskLevel\": \"HIGH\"\n}\n```\n\n**Via CLI:**\n```bash\noci cloud-guard detector create \\\n  --compartment-id <ocid> \\\n  --display-name \"My Detector\" \\\n  --resource-type OBJECT_STORAGE_BUCKET \\\n  --condition '{\"field\": \"isPublic\", \"operator\": \"equals\", \"value\": true}'\n```\n\n**Trigger:** Quando condição é verdadeira → problema detectado", system))
    
    examples.append(create_example("security-cloud-guard", cat, "intermediate",
        "Como configurar responders automáticos?",
        "Responders automáticos:\n\n**Tipos:**\n- Function: executa código\n- Security Zone: aplica políticas\n- Notification: envia alerta\n\n**Exemplo - Auto-remediate bucket público:**\n\n**1. Crie Function:**\n```python\ndef handler(ctx, data):\n    # Make bucket private\n    bucket = data['resourceName']\n    oci os bucket update --public-access disabled\n```\n\n**2. Configure Responder:**\n```bash\noci cloud-guard responder create \\\n  --compartment-id <ocid> \\\n  --display-name \"Make Private\" \\\n  --type FUNCTION \\\n  --function-id <function-ocid> \\\n  --detector-id <detector-ocid>\n```\n\n**Fluxo:**\n1. Detector encontra bucket público\n2. Trigger responder\n3. Function torna bucket privado\n4. Problema resolvido\n\n**Use cases:** Auto-remediation de security issues", system))
    
    examples.append(create_example("security-cloud-guard", cat, "intermediate",
        "Como interpretar Security Score?",
        "Security Score:\n\n**O que é:**\n- Nota de 0-100 da segurança\n- Baseado em problemas detectados\n- Maior = mais seguro\n\n**Cálculo:**\n```\nScore = 100 - (soma de riscos)\n\nRisco CRITICAL: -20 pontos\nRisco HIGH: -10 pontos\nRisco MEDIUM: -5 pontos\nRisco LOW: -1 ponto\n```\n\n**Via Console:**\n- Cloud Guard → Overview\n- Score por compartment\n- Trend histórico\n\n**Melhorando score:**\n1. Resolva problemas CRITICAL primeiro\n2. Habilite responders automáticos\n3. Revise configurações\n4. Monitore continuamente\n\n**Benchmark:**\n- 80-100: Excelente\n- 60-79: Bom\n- 40-59: Atenção\n- <40: Crítico", system))
    
    examples.append(create_example("security-cloud-guard", cat, "intermediate",
        "Como integrar Cloud Guard com Notifications?",
        "Integração com Notifications:\n\n**1. Crie Topic:**\n```bash\noci ons topic create \\\n  --compartment-id <ocid> \\\n  --name security-alerts\n```\n\n**2. Add Subscription:**\n```bash\noci ons subscription create \\\n  --topic-id <topic-ocid> \\\n  --protocol EMAIL \\\n  --endpoint security@empresa.com\n```\n\n**3. Cloud Guard → Notifications:**\n```bash\noci cloud-guard responder create \\\n  --type NOTIFICATION \\\n  --topic-id <topic-ocid> \\\n  --detector-id <detector-ocid>\n```\n\n**4. Events Service (alternativa):**\n```json\n{\n  \"eventType\": \"com.oraclecloud.cloudguard.problem\",\n  \"action\": {\n    \"type\": \"ONS\",\n    \"topicId\": \"<topic-ocid>\"\n  }\n}\n```\n\n**Canais:** Email, Slack, PagerDuty, SMS", system))
    
    examples.append(create_example("security-cloud-guard", cat, "intermediate",
        "Como criar receitas (recipes) custom?",
        "Receitas custom:\n\n**O que é:**\n- Coleção de regras de detecção\n- Aplicadas a targets\n- Reutilizáveis\n\n**Via Console:**\n1. Cloud Guard → Recipes\n2. 'Create Recipe'\n3. Add rules:\n   - Resource type\n   - Condition\n   - Risk level\n4. Save\n\n**Exemplo - Security Recipe:**\n```json\n{\n  \"name\": \"My Security Recipe\",\n  \"rules\": [\n    {\n      \"name\": \"Public Bucket\",\n      \"resourceType\": \"OBJECT_STORAGE_BUCKET\",\n      \"condition\": \"isPublic == true\",\n      \"riskLevel\": \"HIGH\"\n    },\n    {\n      \"name\": \"Unencrypted Volume\",\n      \"resourceType\": \"BLOCK_VOLUME\",\n      \"condition\": \"isEncrypted == false\",\n      \"riskLevel\": \"MEDIUM\"\n    }\n  ]\n}\n```\n\n**Apply recipe:**\n- Target → Attach recipe", system))
    
    # Advanced (2)
    examples.append(create_example("security-cloud-guard", cat, "advanced",
        "Como implementar auto-remediation avançada?",
        "Auto-remediation avançada:\n\n**Cenário:** Múltiplas ações condicionais\n\n**1. Function complexa:**\n```python\ndef handler(ctx, data):\n    problem = data['problem']\n    \n    if problem['riskLevel'] == 'CRITICAL':\n        # Ação imediata\n        remediate_critical(problem)\n        notify_security_team(problem)\n    elif problem['riskLevel'] == 'HIGH':\n        # Ação após aprovação\n        request_approval(problem)\n    else:\n        # Apenas notifica\n        notify_ops(problem)\n\ndef remediate_critical(problem):\n    # Lógica específica por tipo\n    if problem['resourceType'] == 'INSTANCE':\n        stop_instance(problem['resourceId'])\n    elif problem['resourceType'] == 'BUCKET':\n        make_private(problem['resourceId'])\n```\n\n**2. Approvals:**\n- Integration com ServiceNow/Jira\n- humano no loop para ações críticas\n\n**3. Rollback:**\n- Se remediation falhar\n- Notifica e reverte", system))
    
    examples.append(create_example("security-cloud-guard", cat, "advanced",
        "Como integrar com SIEM externo?",
        "Integração com SIEM:\n\n**Opção 1 - Streaming:**\n```bash\noci cloud-guard configuration set \\\n  --compartment-id <ocid> \\\n  --streaming-stream-id <stream-ocid>\n```\n\n**Logs vão para:**\n- Splunk\n- ELK Stack\n- QRadar\n- ArcSight\n\n**Opção 2 - Object Storage:**\n```bash\noci cloud-guard configuration set \\\n  --compartment-id <ocid> \\\n  --log-bucket security-logs\n```\n\n**SIEM ingere:**\n- Logs do Object Storage\n- Via S3 API ou OCI SDK\n\n**Opção 3 - API:**\n```python\n# SIEM consulta Cloud Guard API\nproblems = cloud_guard.list_problems(\n    compartment_id=ocid,\n    time_greater_than=last_hour\n)\n```\n\n**Schema:**\n- Common Event Format (CEF)\n- JSON custom\n- Mapeie campos do SIEM", system))
    
    return examples

# ============ SECURITY WAF ============
def generate_security_waf():
    examples = []
    system = "You are an OCI security specialist with expertise in Web Application Firewall (WAF). Provide technical guidance on WAF policies, rules, and protection."
    cat = "security/waf"
    
    # Beginner (3)
    examples.append(create_example("security-waf", cat, "beginner",
        "O que é OCI WAF?",
        "WAF (Web Application Firewall) protege aplicações web de ataques.\n\n**Proteções:**\n- OWASP Top 10\n- SQL Injection\n- Cross-Site Scripting (XSS)\n- DDoS layer 7\n- Bots maliciosos\n\n**Componentes:**\n- WAF Policy: regras de proteção\n- Rules: condições de bloqueio\n- Address Lists: IPs permitidos/bloqueados\n\n**Casos de uso:**\n- Aplicações web públicas\n- APIs REST/SOAP\n- E-commerce\n- Portais\n\n**Diferença AWS:** Similar ao AWS WAF\n\n**Deployment:**\n- Na frente do Load Balancer\n- Ou direto no backend\n\n[MUTABLE] Preços por policy e requests.\n\nDocs: https://docs.oracle.com/en-us/iaas/Content/WAF/", system))
    
    examples.append(create_example("security-waf", cat, "beginner",
        "Como criar uma WAF Policy?",
        "Criando WAF Policy:\n\n**Via Console:**\n1. Networking → Web Application Firewall\n2. 'Create WAF Policy'\n3. Configure:\n   - Compartment\n   - Name\n   - Compartment do Load Balancer\n4. Add rules (OWASP default)\n5. Associate com Load Balancer\n\n**Via CLI:**\n```bash\noci waas waf-policy create \\\n  --compartment-id <ocid> \\\n  --display-name my-waf \\\n  --load-balancer-id <lb-ocid>\n```\n\n**Regras default:**\n- OWASP Top 10 habilitado\n- Block mode (pode causar falsos positivos)\n- Comece em detect mode\n\n**Próximos passos:**\n- Monitore logs\n- Ajuste regras\n- Mude para block", system))
    
    examples.append(create_example("security-waf", cat, "beginner",
        "O que é OWASP Top 10?",
        "OWASP Top 10:\n\n**O que é:**\n- Lista das 10 vulnerabilidades web mais críticas\n- Mantida pela OWASP Foundation\n- WAF protege contra todas\n\n**Top 10 (2021):**\n1. Broken Access Control\n2. Cryptographic Failures\n3. Injection (SQL, NoSQL)\n4. Insecure Design\n5. Security Misconfiguration\n6. Vulnerable Components\n7. Authentication Failures\n8. Software/Data Integrity\n9. Logging Failures\n10. SSRF\n\n**WAF protege:**\n- #3 Injection: SQL injection, XSS\n- #5 Misconfiguration: headers inseguros\n- #8 SSRF: request forging\n\n**Complementa:** WAF não substitui secure coding", system))
    
    # Intermediate (5)
    examples.append(create_example("security-waf", cat, "intermediate",
        "Como configurar regras custom?",
        "Regras custom:\n\n**Via Console:**\n1. WAF Policy → Rules\n2. 'Create Rule'\n3. Configure:\n   - Name\n   - Action (Allow/Block/Captcha)\n   - Condition\n4. Save\n\n**Exemplo - Block IP:**\n```bash\noci waas waf-policy create-rule \\\n  --waf-policy-id <ocid> \\\n  --display-name \"Block Bad IPs\" \\\n  --action BLOCK \\\n  --condition 'client_ip in \"192.168.1.0/24\"'\n```\n\n**Exemplo - Block User-Agent:**\n```json\n{\n  \"name\": \"Block Bad Bots\",\n  \"action\": \"BLOCK\",\n  \"condition\": \"user_agent contains 'badbot'\"\n}\n```\n\n**Exemplo - Rate limiting:**\n```json\n{\n  \"name\": \"Rate Limit API\",\n  \"action\": \"BLOCK\",\n  \"condition\": \"request_rate > 100/minute\",\n  \"path\": \"/api/*\"\n}\n```\n\n**Order:** Regras avaliadas em ordem (primeiro match wins)", system))
    
    examples.append(create_example("security-waf", cat, "intermediate",
        "Como configurar address lists?",
        "Address Lists:\n\n**O que é:**\n- Listas de IPs/CIDRs\n- Allow lists (permitidos)\n- Block lists (bloqueados)\n\n**Criar lista:**\n```bash\noci waas address-list create \\\n  --compartment-id <ocid> \\\n  --display-name \"Blocked IPs\" \\\n  --addresses '[\"192.168.1.0/24\", \"10.0.0.1\"]'\n```\n\n**Usar na regra:**\n```json\n{\n  \"name\": \"Block List\",\n  \"action\": \"BLOCK\",\n  \"condition\": \"client_ip in \\\"<address-list-id>\\\"\"\n}\n```\n\n**Use cases:**\n- Block países (geo-IP)\n- Allow escritório\n- Block ataques conhecidos\n- Rate limit por IP\n\n**Update:**\n```bash\noci waas address-list update \\\n  --address-list-id <ocid> \\\n  --addresses '[\"new-ip/32\"]'\n```", system))
    
    examples.append(create_example("security-waf", cat, "intermediate",
        "Como monitorar ataques com WAF logs?",
        "WAF Logs:\n\n**Configurar Logging:**\n```bash\noci waas waf-policy update \\\n  --waf-policy-id <ocid> \\\n  --log-config '{\n    \"isLoggingEnabled\": true,\n    \"logBucket\": \"waf-logs\"\n  }'\n```\n\n**Logs incluem:**\n- Timestamp\n- Source IP\n- Request URL\n- Rule matched\n- Action taken\n\n**Query:**\n```bash\noci logging log-entry list \\\n  --compartment-id <ocid> \\\n  --log-id <waf-log-ocid> \\\n  --search-text \"BLOCK\"\n```\n\n**Dashboard:**\n- Requests bloqueados\n- Top IPs atacantes\n- Top rules acionadas\n- Trends\n\n**Alertas:**\n- Pico de blocks\n- Novo padrão de ataque\n- Falsos positivos", system))
    
    examples.append(create_example("security-waf", cat, "intermediate",
        "Como configurar Captcha?",
        "Captcha no WAF:\n\n**Quando usar:**\n- Suspeita de bot\n- Rate limiting excedido\n- Comportamento anômalo\n\n**Configurar:**\n```json\n{\n  \"name\": \"Captcha for API\",\n  \"action\": \"CAPTCHA\",\n  \"condition\": \"request_rate > 50/minute\",\n  \"path\": \"/api/*\"\n}\n```\n\n**Fluxo:**\n1. Request detectado como bot\n2. WAF retorna desafio Captcha\n3. Usuário resolve Captcha\n4. Request liberado\n5. Token válido por período\n\n**Tipos:**\n- Image-based (selecionar imagens)\n- Checkbox (\"não sou robô\")\n- Invisible (análise de comportamento)\n\n**Best Practice:** Captcha antes de Block (evita falsos positivos)", system))
    
    examples.append(create_example("security-waf", cat, "intermediate",
        "Como proteger APIs REST?",
        "Protegendo APIs REST:\n\n**1. Rate Limiting:**\n```json\n{\n  \"name\": \"API Rate Limit\",\n  \"action\": \"BLOCK\",\n  \"condition\": \"request_rate > 100/minute\",\n  \"path\": \"/api/*\"\n}\n```\n\n**2. Validação de schema:**\n```json\n{\n  \"name\": \"Validate JSON\",\n  \"action\": \"BLOCK\",\n  \"condition\": \"content_type != 'application/json'\",\n  \"method\": \"POST\"\n}\n```\n\n**3. Authentication:**\n- WAF valida JWT\n- Ou passa para backend\n\n**4. Input validation:**\n- SQL injection\n- XSS\n- Path traversal\n\n**5. DDoS protection:**\n- Block IPs com volume anormal\n- Geo-blocking se necessário\n\n**Exemplo completo:**\n```bash\noci waas waf-policy create \\\n  --display-name \"API WAF\" \\\n  --rules '[rate_limit, jwt_auth, sql_injection]'\n```", system))
    
    # Advanced (2)
    examples.append(create_example("security-waf", cat, "advanced",
        "Como implementar WAF dinâmico com Functions?",
        "WAF dinâmico com Functions:\n\n**Cenário:** Decisões complexas de segurança\n\n**1. WAF → Function:**\n```json\n{\n  \"name\": \"Dynamic Decision\",\n  \"action\": \"REDIRECT_TO_FUNCTION\",\n  \"functionId\": \"<function-ocid>\"\n}\n```\n\n**2. Function analisa:**\n```python\ndef handler(ctx, data):\n    request = data['request']\n    \n    # Análise complexa\n    if is_suspicious(request):\n        # Consulta threat intelligence\n        if is_known_attacker(request['ip']):\n            return {'action': 'BLOCK'}\n        else:\n            return {'action': 'CAPTCHA'}\n    \n    return {'action': 'ALLOW'}\n```\n\n**3. Integrações:**\n- Threat intelligence APIs\n- Machine learning models\n- Behavioral analysis\n\n**Vantagem:** Lógica custom complexa\n\n**Desvantagem:** Latência adicional", system))
    
    examples.append(create_example("security-waf", cat, "advanced",
        "Como migrar AWS WAF para OCI WAF?",
        "Migração AWS WAF → OCI WAF:\n\n**1. Exporte AWS WAF:**\n```bash\naws wafv2 list-web-acls\naws wafv2 get-web-acl --name my-waf\n```\n\n**2. Mapeamento:**\n- Web ACL → WAF Policy\n- Rules → WAF Rules\n- IP Sets → Address Lists\n- Byte Match Sets → Rule conditions\n\n**3. Converta regras:**\n```yaml\n# AWS\n- Name: SQLInjection\n  Action: BLOCK\n  Statement:\n    SqliMatchStatement: {}\n\n# OCI\n{\n  \"name\": \"SQL Injection\",\n  \"action\": \"BLOCK\",\n  \"condition\": \"sql_injection_detected == true\"\n}\n```\n\n**4. migre Address Lists:**\n- Exporte IP sets\n- Importe como OCI Address Lists\n\n**5. Teste:**\n- Detect mode primeiro\n- Valide regras\n- Mude para block\n\n**Diferenças:**\n- OCI mais simples\n- Menos regras predefinidas\n- Custom rules similares", system))
    
    return examples

# Main execution
def main():
    generators = {
        "security-vault-keys": generate_security_vault_keys,
        "security-encryption": generate_security_encryption,
        "security-cloud-guard": generate_security_cloud_guard,
        "security-waf": generate_security_waf,
    }
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    for category, generator in generators.items():
        examples = generator()
        write_jsonl(f"{category}.jsonl", examples)
    
    print(f"\nTotal: {len(generators)} files generated")

if __name__ == "__main__":
    main()
