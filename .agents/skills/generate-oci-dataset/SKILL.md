# Generate OCI Dataset Skill

## Purpose

Generate high-quality training examples for OCI Specialist LLM using online LLMs (Gemini, GPT-4, Claude, Perplexity).

## Context Files

Always read these files before generating:
- `docs/taxonomy.md` - Category hierarchy and topics
- `docs/quality-rules.md` - Quality guidelines
- `AGENTS.md` - Project overview

## Output Format

Each generated example must be saved as:

```
data/curated/[category]-[nnn].jsonl
```

With content (1 line = 1 JSON):
```json
{"messages": [{"role": "system", "content": "Você é um arquiteto especialista em OCI..."}, {"role": "user", "content": "pergunta"}, {"role": "assistant", "content": "resposta"}]}
```

## Generation Process

### 1. Select Category

Use taxonomy to select category. Example categories:
- oci-core/compute, oci-core/storage, oci-core/networking, oci-core/database
- oci-security/iam, oci-security/vault, oci-security/encryption
- oci-migration/aws-to-oci, oci-migration/azure-to-oci, oci-migration/gcp-to-oci, oci-migration/onprem-to-oci
- oci-terraform/provider, oci-terraform/resources
- oci-troubleshooting/connectivity, oci-troubleshooting/performance

### 2. Generate Prompt

Use prompts template from `prompts/[category].md` or create custom prompt based on:
- Category topic from taxonomy.md
- Quality rules from quality-rules.md
- Difficulty: beginner/intermediate/advanced

### 3. Send to LLM

Send prompt to online LLM (Gemini, GPT-4, etc.)

### 4. Validate Response

Check:
- [ ] No copied OCI docs verbatim
- [ ] No invented services
- [ ] Specific steps included
- [ ] Risks/alternatives mentioned
- [ ] Multi-cloud context when relevant

### 5. Save File

Save to `data/curated/[category]-[nnn].jsonl`

## Providers

Recommended online LLMs for generation:
- Google Gemini (gemini-2.0-flash)
- OpenAI GPT-4o
- Anthropic Claude 3.5
- Perplexity Sonar

## Quantity Guidelines

**10 examples per topic** (64 topics × 10 = 640 examples total)

Quick reference:
- compute: 3 topics (instances, scaling, custom-images)
- storage: 3 topics (block, object, file)
- networking: 3 topics (vcn, security, connectivity)
- lb: 1 topic (load-balancer)
- database: 6 topics (autonomous, autonomous-json, mysql, postgresql, nosql, exadata)
- container: 2 topics (oke, instances)
- serverless: 2 topics (functions, api-gateway)
- security: 9 topics (iam-basics, policies, dynamic-groups, federation, vault-secrets, vault-keys, encryption, cloud-guard, waf)
- migration: 12 topics (aws-compute, aws-storage, aws-database, azure-compute, azure-database, gcp-compute, gcp-storage, gcp-database, gcp-to-oci, onprem-vmware, onprem-database, data-transfer)
- terraform: 7 topics (provider, compute-storage, networking, iam, database, oke, state)
- observability: 4 topics (logging, monitoring, stack-monitoring, apm)
- troubleshooting: 8 topics (connectivity, performance, authentication, database, compute, storage, oke, functions)
- devops: 4 topics (ci-cd, resource-manager, artifacts, secrets)

## Quality Checklist

For each generated example, verify:
- [ ] Accurate OCI terminology
- [ ] Specific OCI resource names
- [ ] Concrete steps (not generic)
- [ ] Trade-offs explained
- [ ] Mutable content marked [MUTABLE] or [CHECK DOCS]
- [ ] No exact prices or limits
- [ ] Multi-cloud mapping when relevant
