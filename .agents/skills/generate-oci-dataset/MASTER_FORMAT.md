# OCI Dataset Generation - Output Format

## CRITICAL: JSONL FORMAT

**ONE JSON object per line** - no arrays, no wrapping.

```
{"messages": [...], "metadata": {...}}
{"messages": [...], "metadata": {...}}
```

### JSON Escaping Rules

| Character | Escape as |
|-----------|------------|
| `"` (quote) | `\"` |
| `\` (backslash) | `\\` |
| newline | `\n` |
| tab | `\t` |

### Correct vs Incorrect

```python
# CORRECT - escaped newlines:
{"assistant": "content": "1. Step one\n2. Step two"}

# WRONG - real newlines break JSON:
{"assistant": "content": "1. Step one
2. Step two"}
```

```python
# CORRECT - escaped quotes:
{"assistant": "content": "Use the \"Create\" button"}

# WRONG - unescaped quotes break JSON:
{"assistant": "content": "Use the "Create" button"}
```

```python
# CORRECT - escaped backslashes:
{"assistant": "content": "C:\\Users\\admin"}

# WRONG - unescaped backslash:
{"assistant": "content": "C:\Users\admin"}
```

## METADATA (REQUIRED)

Every JSON object MUST include:

```json
"metadata": {
  "category": "CATEGORY/SUBCATEGORY",
  "difficulty": "beginner|intermediate|advanced",
  "source": "generated"
}
```

## QUALITY RULES

### NEVER (these break training):
- Copy OCI documentation verbatim
- Invent non-existent Oracle services
- Use prices without [MUTABLE] tag
- Use limits without [CHECK DOCS] tag
- Give vague advice ("use best practices")
- Skip trade-offs in architecture

### ALWAYS:
- Paraphrase in your own words
- Use correct OCI terminology
- Include specific steps with resource names
- Mark mutable content: [MUTABLE] for prices, [CHECK DOCS] for limits
- Reference: https://docs.oracle.com/en-us/iaas/Content/...
