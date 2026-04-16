# Dataset Quality Report

**Generated:** 2026-04-15
**Dataset:** data/curated_v5_dedup
**Total Categories:** 88

## Summary

| Intent | Categories Affected | Examples |
|--------|---------------------|----------|
| update | 62 | 1,937 |
| manage | 62 | 1,860 |
| describe | 14 | 2,520 |
| diagnose | 8 | 1,440 |
| analyze | 4 | 720 |

**All 88 categories have duplication issues.**

## Details

### Intents with 1 unique response (3%)

All standard intents (create, list, get, update, delete, manage) work correctly for most categories, but:

- **update**: 1/30-33 unique response (template genérico sem CLI específico)
- **manage**: 1/30-33 unique response (template genérico sem CLI específico)

### Intents with low diversity (11%)

- **describe** (migration): 20/180 unique
- **diagnose** (troubleshooting): 20/180 unique  
- **analyze** (finops): 20/180 unique

## Root Cause

The script `generate_v5_combined.py` uses:
1. Templates for each intent that don't incorporate contextual variables
2. CLI_COMMANDS dict but missing entries for "update" and "manage"
3. Same response generated regardless of company/project/constraint/lifecycle

## Fix Required

Modify `scripts/generate_v5_combined.py` to:
1. Add CLI_COMMANDS for update/manage intents
2. Add contextual variation (company, project, constraint, lifecycle)
3. Add template variations for diversity