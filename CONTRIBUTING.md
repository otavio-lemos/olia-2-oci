# Contributing to OCI Specialist LLM

> **Language / Idioma**: EN-US | PT-BR (default: PT-BR)

---

## Fluxo Obrigatório

```
1. ABRIR ISSUE  → Descrever mudança proposta
2. APROVADA     → Mantenedor aprova o issue
3. FORK → PR    → Criar branch e PR linkando o issue
4. DESCRIÇÃO    → Explicar changes no PR
```

**PR sem issue linkada será rejeitado.**

---

## Issue: O que incluir

- **Tipo**: feature, bug, docs, dataset
- **Descrição**: O que precisa fazer e por quê
- **Escopo**: Qual(is) arquivo(s)/topic(s) afetado(s)
- **Checklist**: Como validar a mudança

### Labels

| Label | Uso |
|-------|-----|
| `feature` | Novo topic, script, funcionalidade |
| `bug` | Correção de bug |
| `docs` | Documentação |
| `dataset` | Adicionar/corrigir exemplos |
| `question` | Dúvida, não implementação |

---

## Pull Request

### Requisitos

- [ ] Issue linkada no PR
- [ ] Branch nomeada: `issue-{numero}-{descricao-curta}`
- [ ] Descrição clara do que foi mudado
- [ ] Screenshots/testes se aplicável
- [ ] Passar em lint/typecheck localmente

### Checklist de Revisão

- [ ] Código segue padrões do projeto
- [ ] Documentação atualizada se aplicável
- [ ] Testes incluídos (se nova funcionalidade)
- [ ] Sem secrets/credenciais
- [ ] Commits descritivos

---

## Diretrizes por Tipo

### Dataset/Prompts

- Usar `scripts/generate_prompt.py` para gerar template
- Seguir taxonomy em `docs/taxonomy.md`
- 10 exemplos por topic
- Validar com `python scripts/validate_jsonl.py`
- Incluir diagrama Mermaid se arquitetura

### Scripts/Terraform

- Python: seguir PEP 8, type hints
- Terraform: seguir HashiCorp style
- Testar localmente antes do PR

### Documentação

- Atualizar README se mudou pipeline
- Manter consistente com outros docs

---

## Dúvidas?

- Abra uma issue com label `question`
- Ou entre em contato pelo GitHub Discussions