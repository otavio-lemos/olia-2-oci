# Exemplo: Prompt Completo para Geração

Este é o prompt completo para gerar exemplos da categoria `oci-core/compute`.

---

```
Você é um especialista em Oracle Cloud Infrastructure (OCI) e deve gerar exemplos de training para um modelo de LLM fino-tuned.

## Formato de Saída

Gere EXATAMENTE um JSON por linha (JSONL), com este formato:

{"messages": [{"role": "system", "content": "Você é um arquiteto especialista em Oracle Cloud Infrastructure (OCI). Forneça respostas técnicas precisas, específicas e práticas sempre que possível."}, {"role": "user", "content": "SUA_PERGUNTA_AQUI"}, {"role": "assistant", "content": "SUA_RESPOSTA_AQUI"}], "metadata": {"category": "CATEGORIA_AQUI", "difficulty": "beginner|intermediate|advanced", "source": "generated"}}

## Regras Obrigatórias

1. **NUNCA copie documentação OCI verbatim** - reescreva com suas palavras
2. **NUNCA invente serviços Oracle inexistentes** - use apenas serviços reais
3. **NUNCA use preços sem marcar como [MUTABLE]** - preços mudam frequentemente
4. **NUNCA use limites/quotas sem marcar como [CHECK DOCS]** - variam por região
5. **NUNCA crie exemplos vagos** - seja específico com passos
6. **NUNCA pule riscos/justificativas em arquiteturas** - explique trade-offs

## Conteúdo Obrigatório

1. **Sempre marque conteúdo mutável**: [MUTABLE] para preços, [CHECK DOCS] para limites
2. **Sempre use terminologia OCI correta**: Compartment (não "folder"), VCN (não "virtual network")
3. **Sempre inclua contexto multi-cloud quando relevante**: AWS/Azure/GCP equivalente
4. **Sempre referencie documentação quando relevante**: https://docs.oracle.com/...

## Categoria a Gerar

oci-core/compute

## Tópicos para esta Categoria

- Instance creation and management
- Shape selection (VM.Standard2, VM.Standard.E4, VM.Optimized3, Ampere A1)
- Instance pools and auto-scaling
- Custom images
- Boot volumes
- HPC instances

## Distribuição de Dificuldade

- beginner: 30%
- intermediate: 50%
- advanced: 20%

## Exemplos de Perguntas

### Beginner
Como criar uma instância de compute no OCI?

### Intermediate
Como configurar um instance pool com auto-scaling no OCI?

### Advanced
Como criar uma arquitetura de alta disponibilidade com instance pool e load balancer?

## Gere 5-10 exemplos

Cada exemplo deve:
- Ser uma linha JSONL completa
- Ter difficulty diferente (mix de beginner/intermediate/advanced)
- Coverir diferentes tópicos da categoria
- Ser tecnicamente preciso e específico
```

---

## Resultado Esperado (resposta do LLM)

Uma resposta como esta (múltiplas linhas, uma por exemplo):

```jsonl
{"messages": [{"role": "system", "content": "Você é um arquiteto especialista em Oracle Cloud Infrastructure (OCI). Forneça respostas técnicas precisas, específicas e práticas sempre que possível."}, {"role": "user", "content": "Como criar uma instância de compute no OCI?"}, {"role": "assistant", "content": "Para criar uma instância no OCI:\n\n1. No Console, vá para Compute > Instances\n2. Clique em 'Create Instance'\n3. Selecione o compartment\n4. Escolha a imagem (Oracle Linux, Ubuntu, Windows)\n5. Selecione o shape (VM.Standard2.1, VM.Standard.E4.Flex, etc)\n6. Configure rede (VCN existente ou criar nova)\n7. Adicione SSH keys\n8. Clique em Create\n\nShape recomendado: VM.Standard.E4.Flex para general purpose. Para ARM, use Ampere A1.\n\nCusto estimado: [MUTABLE - verifique preços atuais]"}], "metadata": {"category": "oci-core/compute", "difficulty": "beginner", "source": "generated"}}
{"messages": [{"role": "system", "content": "Você é um arquiteto especialista em Oracle Cloud Infrastructure (OCI). Forneça respostas técnicas precisas, específicas e práticas sempre que possível."}, {"role": "user", "content": "Como configurar um instance pool com auto-scaling no OCI?"}, {"role": "assistant", "content": "Para configurar instance pool com auto-scaling:\n\n1. Compute > Instance Pools > Create Instance Pool\n2. Configure:\n   - Nome e compartment\n   - Instance configuration (template)\n   - Number of instances inicial\n3. Configure Auto-scaling:\n   - Create scaling policy\n   - Choose metric: CPU or memory utilization\n   - Set threshold (ex: scale out >70%, scale in <30%)\n   - Set min/max instances\n4. Configure Load Balancer (opcional)\n\nImportante: O instance pool requer uma Instance Configuration pré-definida com todos os recursos (VCN, subnet, shape, image)."}], "metadata": {"category": "oci-core/compute", "difficulty": "intermediate", "source": "generated"}}
...
```

---

## Como Salvar

Copie a resposta do LLM e salve em:
```
data/curated/oci-core/compute-001.jsonl
```

Uma linha = um exemplo. Você pode ter 5-10 exemplos por arquivo.
