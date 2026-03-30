# OCI Specialist LLM - Quality Rules

## Dataset Quality Rules (Rigid)

### Prohibited Content

1. **NEVER copy OCI documentation verbatim**
   - Paraphrase in your own words
   - Reorganize information structure
   - Add original examples

2. **NEVER invent non-existent Oracle services**
   - Only include real OCI services
   - Verify service names from official docs
   - No "OCI Magic Service" or similar

3. **NEVER use prices without marking as mutable**
   - Prices change frequently
   - Use: "As of 2024, pricing is approximately X"
   - Never quote exact current prices

4. **NEVER use limits/quotas without marking**
   - Limits vary by region and tenancy
   - Use: "Check your specific limits in the console"

5. **NEVER create vague examples**
   - Bad: "Use best practices for security"
   - Good: "Enable MFA for all users, use IAM groups for access control"

6. **NEVER skip steps in procedural answers**
   - Include all necessary steps
   - Explain prerequisite configurations

7. **NEVER skip risks/justifications in architecture**
   - Every architectural choice has trade-offs
   - Explain why the recommendation makes sense

### Required Content

1. **Always provide specific OCI resource names**
   - Use actual OCI resource identifiers
   - Reference correct service names

2. **Always mark mutable content**
   - [MUTABLE] for prices, limits, quotas
   - [CHECK DOCS] for version-dependent info

3. **Always use accurate OCI terminology**
   - Compartment, not "folder"
   - VCN, not "virtual network" (define on first use)
   - Policy, not "permission"

4. **Always include multi-cloud context when relevant**
   - AWS/Azure equivalent concepts
   - Migration mapping guidance

### Validation Checklist

- [ ] No copied documentation sentences
- [ ] No made-up services
- [ ] Prices marked as mutable or removed
- [ ] Limits marked to verify in console
- [ ] Answers have specific steps
- [ ] Architecture answers include trade-offs
- [ ] All OCI terms are correct

### Deduplication Rules

- Exact duplicate: remove one copy
- Near-duplicate (>90% similarity): merge or keep best
- Same question, different context: keep both if genuinely different
