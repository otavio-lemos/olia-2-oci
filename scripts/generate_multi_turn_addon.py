def _generate_followup(category: str, answer: str, idx: int) -> tuple[str, str]:
    import random
    subcat = category.split("/")[1] if "/" in category else category
    main_cat = category.split("/")[0] if "/" in category else category
    
    # Decide type of follow up
    followup_types = ["troubleshooting", "security", "cost", "automation", "explanation", "limits"]
    
    # Use deterministic random based on idx and category so it's reproducible
    rng = random.Random(f"{category}_{idx}_followup")
    ftype = rng.choice(followup_types)
    
    user_q = ""
    asst_a = ""
    
    if ftype == "troubleshooting":
        user_q = f"Implementei isso, mas recebi um erro 'NotAuthorizedOrNotFound'. O que pode estar errado?"
        asst_a = f"Esse erro na OCI geralmente indica um problema de permissão do IAM ou que o recurso (como o OCID) está incorreto/em outro compartment.\n\nPara resolver:\n1. Verifique se a sua role/group possui uma policy como `Allow group <SeuGrupo> to manage {subcat.replace('-', ' ')} in compartment <SeuCompartment>`.\n2. Confirme se você está executando o comando na região (Region) correta.\n3. Valide se o OCID fornecido realmente existe e não foi excluído."
    elif ftype == "security":
        user_q = f"Quais as melhores práticas de segurança para proteger esse recurso?"
        asst_a = f"Para proteger seus recursos de {subcat.replace('-', ' ')} na OCI:\n\n- **Princípio do Menor Privilégio:** Crie policies restritas no IAM (ex: `use` ou `read` em vez de `manage` quando possível).\n- **Criptografia:** Utilize chaves gerenciadas pelo cliente (Customer Managed Keys) através do OCI Vault (KMS) ao invés de chaves gerenciadas pela Oracle.\n- **Rede:** Isole o acesso usando Network Security Groups (NSGs) e garanta que endpoints privados sejam usados ao invés de IPs públicos.\n- **Auditoria:** Ative os logs do OCI Audit e Cloud Guard para monitorar alterações na configuração."
    elif ftype == "cost":
        user_q = f"Como posso otimizar os custos associados a isso?"
        asst_a = f"Otimizar custos de {subcat.replace('-', ' ')} na Oracle Cloud envolve:\n\n1. **Dimensionamento Correto (Right-Sizing):** Monitore a utilização (CPU/Memória) via OCI Monitoring. Use instâncias Flex (ex: `VM.Standard.E4.Flex`) para alocar a quantidade exata de OCPUs necessárias.\n2. **Autoscaling:** Configure regras de auto-scaling para escalar horizonalmente em picos e diminuir a infraestrutura em momentos de ociosidade.\n3. **Ciclo de Vida:** Se envolver armazenamento, use políticas de Object Lifecycle Management para mover dados inativos para a camada Archive.\n4. **Tagging:** Aplique Cost-Tracking Tags para mapear os gastos por departamento ou projeto no Cost Analysis dashboard."
    elif ftype == "automation":
        user_q = f"Como eu poderia automatizar essa mesma configuração usando Terraform?"
        asst_a = f"Para automatizar a criação de recursos de {subcat.replace('-', ' ')} via OCI Terraform Provider, você usaria um bloco `resource` específico.\n\nExemplo da estrutura genérica:\n```hcl\nresource \"oci_{main_cat}_{subcat.replace('-', '_')}\" \"exemplo\" {{\n  compartment_id = var.compartment_id\n  display_name   = \"{subcat}-automatizado\"\n  # Atributos obrigatórios do recurso iriam aqui\n}}\n```\n\nAlém de definir o recurso, lembre-se de configurar o provider `oci` com a sua `tenancy_ocid`, `user_ocid`, `fingerprint`, `private_key_path` e `region`."
    elif ftype == "explanation":
        user_q = "Pode explicar detalhadamente como o OCI lida com a resiliência (High Availability) nesse caso?"
        asst_a = f"A Oracle Cloud Infrastructure foi projetada para Alta Disponibilidade (HA) através de Fault Domains (FDs) e Availability Domains (ADs).\n\nPara cenários envolvendo {subcat.replace('-', ' ')}:\n- **Availability Domains (ADs):** São data centers isolados dentro de uma mesma região. Distribuir a carga entre AD-1, AD-2 e AD-3 protege contra falhas físicas totais de um data center.\n- **Fault Domains (FDs):** Se a região possuir apenas um AD (ex: `sa-saopaulo-1`), você deve distribuir seus recursos entre os 3 Fault Domains lógicos (FD-1, FD-2, FD-3). Eles representam racks de servidores isolados energeticamente.\n- **Replicação:** Utilize os recursos nativos da OCI (como Block Volume Backups cruzados por região, ou replicação do Object Storage) para garantir a integridade em casos de Disaster Recovery (DR)."
    elif ftype == "limits":
        user_q = "Existe algum limite ou quota de serviço padrão (Service Limit) que eu deva me preocupar ao escalar?"
        asst_a = f"Sim, a OCI opera com Service Limits (limites de serviço rígidos por tenancy) e Compartment Quotas (políticas lógicas).\n\nAo escalar serviços como {subcat.replace('-', ' ')}:\n1. Acesse *Governance & Administration -> Limits, Quotas and Usage* no console para ver o uso atual.\n2. Verifique o limite padrão associado à sua região. Contas Trial (Always Free) têm limites muito estritos (ex: 2 VMs AMD, 4 OCPUs ARM).\n3. Caso atinja o limite, você deverá abrir uma solicitação de Service Limit Increase (aumento de limite) via Oracle Support através do próprio console, detalhando a justificativa de negócio.\n4. Proativamente, use *Compartment Quotas* para evitar que um departamento devore todos os limites de OCPUs ou armazenamento da tenancy inteira."

    return user_q, asst_a
