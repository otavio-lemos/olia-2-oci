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

Basic execution (local):
- oci-core/*: 20-30 examples per subcategory
- oci-security/*: 15-20 examples per subcategory
- oci-migration/*: 15-20 examples per subcategory
- oci-terraform/*: 10-15 examples per subcategory
- oci-troubleshooting/*: 15-20 examples per subcategory

## Quality Checklist

For each generated example, verify:
- [ ] Accurate OCI terminology
- [ ] Specific OCI resource names
- [ ] Concrete steps (not generic)
- [ ] Trade-offs explained
- [ ] Mutable content marked [MUTABLE] or [CHECK DOCS]
- [ ] No exact prices or limits
- [ ] Multi-cloud mapping when relevant
