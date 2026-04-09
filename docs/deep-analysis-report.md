# RELATÓRIO: Análise Profunda do Projeto OCI Specialist LLM

## 1. Estado Atual do Projeto

### 1.1 Dataset (✅ CORRIGIDO)
- **Antes**: splits gerados de `all_curated.jsonl` (9,940 exemplos - sujo)
- **Depois**: splits gerados de `all_curated_clean.jsonl` (3,467 exemplos - limpo)
- **Resultado**: train=2583, valid=495, eval=325 (ratios corretos 75/15/10%)

### 1.2 Treinamento (⚠️ PARCIAL)
- Cycle-1: ✅ Concluído (200 iters, adapters salvos)
- Cycle-2: ✅ Concluído (100 iters, adapters salvos)
- Cycle-3: ❌ Não executado
- Cycle-4: ❌ Config existe mas não executado

### 1.3 Inferência (✅ FUNCIONAL)
Testado com cycle-1 adapter - funcionando normalmente.

---

## 2. PROBLEMAS IDENTIFICADOS

### 2.1 Dados Gerados - Problema de Qualidade
**PROBLEMA CRÍTICO**: Os exemplos gerados usam contexto de COMPUTE em TODAS as perguntas,independentemente da categoria.

**Exemplo do problema**:
```
User (categoria: security/dynamic-groups): 
  "Como criar Dynamic Groups OCI para TechCorp... [context: shape=VM.Standard.E4.Flex, 1OCPUs, 50GB, AD=AD-1, CIDR=10.0.0.0/16]"
```

Isso acontece porque:
1. O prompt de geração usa contexto de compute em TODOS os templates
2. O clean_dataset.py removeu o `[context: ...]` das perguntas
3. **MAS** as respostas ainda foram geradas pensando em compute shapes

### 2.2 Respostas Genéricas
As respostas foram geradas com templates fixos:
- "Passo 1: Preparacao"
- "Passo 2: Criacao"
- "Passo 3: Configuracao"
- "Passo 4: Validacao"

O clean_dataset.py removeu essas (ficou 0 com "Passo" depois da limpeza).

### 2.3 Falta de Documentação Official nos Dados
Os dados gerados não fazem referência à documentação oficial OCI de forma adequada.

---

## 3. ANÁLISE COMPARATIVA: Dados vs Documentação Oficial

### 3.1 OCI Compute Instance - Documentação Oficial
A documentação oficial diz para criar instância via:
- **Console**: Compute → Instances → Create Instance
- **CLI**: `oci compute instance launch --from-json <file.json>`
- **API**: `LaunchInstance`

A documentação cubre:
- Placement (AD, fault domain, capacity types)
- Image e Shape (AMD, Intel, Ampere, GPU, HPC)
- Networking (VCN, subnet, NSG, SSH keys)
- Storage (boot volume, block volumes)
- Management (cloud-init, tags)
- Security (Shielded, Confidential Computing)

### 3.2 OCI IAM Dynamic Groups - Documentação Oficial
Documentação: https://docs.oracle.com/iaas/Content/Identity/dynamicgroups/Working_with_Dynamic_Groups.htm

Conceitos importantes:
- Matching rules (instance.compartmentId, etc.)
- Resource OCIDs
- Policy attachment
- Group vs Dynamic Group distinction

### 3.3 OCI Terraform Provider
Documentação: https://registry.terraform.io/providers/oracle/oci/latest/docs/resources/core_instance

Recursos Covered:
- `oci_core_instance`
- `oci_core_vcn`
- `oci_core_subnet`
- `oci_database_autonomous_database`

---

## 4. RECOMENDAÇÕES DE CORREÇÃO

### 4.1 Para Novos Dados (Futuro)
1. **Separar prompts por categoria** - cada domínio (IAM, Compute, Database, etc.) deve ter seu próprio prompt template
2. **Incluir referências oficiais** - nos prompts, adicionar links como:
   - https://docs.oracle.com/iaas/Content/Compute/Tasks/launchinginstance.htm
   - https://docs.oracle.com/iaas/Content/Identity/dynamicgroups/Working_with_Dynamic_Groups.htm
3. **Remover contexto genérico** - não incluir shape/CIDR em perguntas de IAM

### 4.2 Para Dados Atuais (3,467 exemplos)
Os dados já foram limpos. Verificar se as respostas são relevantes.

### 4.3 Para Treinamento
1. Executar Cycle-3 (já configurado)
2. Adicionar validação de loss antes/depois
3. Documentar hiperparâmetros usados

---

## 5. PRÓXIMOS PASSOS RECOMENDADOS

1. **Verificar qualidade das respostas** do cycle-1/2 (fazer eval manual)
2. **Executar cycle-3** se os resultados anteriores forem aceitáveis
3. **Gerar novos dados** com prompts corrigidos (se necessário)
4. **Atualizar documentação** do projeto

---

## 6. Links de Referência

### Documentação Oficial OCI
- **Compute**: https://docs.oracle.com/iaas/Content/Compute/Concepts/computeoverview.htm
- **IAM**: https://docs.oracle.com/iaas/Content/Identity/overview.htm
- **Database**: https://docs.oracle.com/iaas/Content/Database/Concepts/dboverview.htm
- **Networking**: https://docs.oracle.com/iaas/Content/Network/Concepts/overview.htm
- **Terraform Provider**: https://registry.terraform.io/providers/oracle/oci/latest

### MLX/MLX-Tune
- **MLX Docs**: https://ml-explore.github.io/mlx/build/html/index.html
- **mlx-lm**: https://pypi.org/project/mlx-lm/
- **mlx-tune**: https://github.com/ARahim3/mlx-tune
- **mlx-lm lora CLI**: `mlx_lm lora --help`

---

*Relatório gerado em: 2026-04-08*