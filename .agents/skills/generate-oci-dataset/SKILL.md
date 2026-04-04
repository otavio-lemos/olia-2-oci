# Generate OCI Dataset Skill

## Purpose

Generate high-quality training examples for OCI Specialist LLM using prompts.

## Context Files

Always read these files before generating:
- `docs/taxonomy.md` - Category hierarchy and topics
- `docs/quality-rules.md` - Quality guidelines
- `AGENTS.md` - Project overview

## Output Format

Each generated example must be saved as:

```
data/curated/[topic].jsonl
```

With content (1 line = 1 JSON):

**Each JSON object has EXACTLY 3 messages: system + user + assistant. NEVER put multiple user/assistant pairs in the same object.**

Correct format:
```json
{"messages": [{"role": "system", "content": "Você é um arquiteto especialista em OCI..."}, {"role": "user", "content": "pergunta"}, {"role": "assistant", "content": "resposta"}], "metadata": {"category": "topic/subtopic", "difficulty": "intermediate", "source": "generated"}}
```

WRONG format (multiple Q&A in one JSON - DO NOT DO THIS):
```json
{"messages": [{"role": "system", "content": "..."}, {"role": "user", "content": "pergunta 1"}, {"role": "assistant", "content": "resposta 1"}, {"role": "user", "content": "pergunta 2"}, {"role": "assistant", "content": "resposta 2"}], "metadata": {...}}
```

**Format: 1 file per topic with 140 lines (140 JSON objects, each with exactly 3 messages)**

## Generation Process

### 1. Select Category

Use taxonomy to select category. Example categories:
- oci-core/compute, oci-core/storage, oci-core/networking, oci-core/database
- oci-security/iam, oci-security/vault, oci-security/encryption
- oci-migration/aws-to-oci, oci-migration/azure-to-oci, oci-migration/gcp-to-oci, oci-migration/onprem-to-oci
- oci-terraform/provider, oci-terraform/resources
- oci-troubleshooting/connectivity, oci-troubleshooting/performance

### 2. Execute Prompt

Execute the generated prompt using your preferred method.

### 4. Validate Response

Check:
- [ ] **Exactly 3 messages per JSON object (system + 1 user + 1 assistant)**
- [ ] **No multiple user/assistant pairs in the same JSON object**
- [ ] **10 separate JSON objects (10 lines) per file**
- [ ] No copied OCI docs verbatim
- [ ] No invented services
- [ ] Specific steps included
- [ ] Risks/alternatives mentioned
- [ ] Multi-cloud context when relevant

### 5. Save File

Save to `data/curated/[topic].jsonl`

**Format: 1 file per topic with 140 examples each**

## Quantity Guidelines

**140 examples per topic** (71 topics × 140 = 9,940 examples total)

Quick reference:
- compute: 3 topics (instances, scaling, custom-images)
- storage: 3 topics (block, object, file)
- networking: 3 topics (vcn, security, connectivity)
- lb: 1 topic (load-balancer)
- database: 6 topics (autonomous, autonomous-json, mysql, postgresql, nosql, exadata)
- container: 2 topics (oke, instances)
- serverless: 2 topics (functions, api-gateway)
- security: 9 topics (iam-basics, policies, dynamic-groups, federation, vault-secrets, vault-keys, encryption, cloud-guard, waf)
- migration: 14 topics (aws-compute, aws-storage, aws-database, azure-compute, azure-storage, azure-database, gcp-compute, gcp-storage, gcp-database, onprem-compute, onprem-storage, onprem-vmware, onprem-database, data-transfer)
- terraform: 12 topics (provider, compute, storage, networking, load-balancer, database, container, serverless, security, observability, devops, state)
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
