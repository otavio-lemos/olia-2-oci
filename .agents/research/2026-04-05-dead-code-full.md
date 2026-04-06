# Dead Code Scan Report

**Date:** 2026-04-05
**Mode:** Full (hygiene)
**Files Scanned:** 11 Python + 3 shell scripts
**Language:** Python (adapted from Swift workflow)

---

## Summary

| Confidence | Count | Action |
|------------|-------|--------|
| HIGH | 12 | Safe to remove |
| MEDIUM | 2 | Verify before removing |

---

## Issue Rating Table

| # | Finding | Urgency | Risk: Fix | Risk: No Fix | ROI | Blast Radius | Fix Effort |
|---|---------|---------|-----------|-------------|-----|-------------|------------|
| 1 | `Set` import unused — `scripts/dedupe_dataset.py:7` (HIGH confidence) | ⚪ Low | ⚪ Low | ⚪ Low | 🟢 Good | ⚪ 1 file | Trivial |
| 2 | `json` import unused — `scripts/generate_prompt.py:11` (HIGH confidence) | ⚪ Low | ⚪ Low | ⚪ Low | 🟢 Good | ⚪ 1 file | Trivial |
| 3 | `hashlib` import unused — `scripts/generate_diverse_v2.py:18` (HIGH confidence) | ⚪ Low | ⚪ Low | ⚪ Low | 🟢 Good | ⚪ 1 file | Trivial |
| 4 | `Optional` import unused — `scripts/evaluate_model.py:11` (HIGH confidence) | ⚪ Low | ⚪ Low | ⚪ Low | 🟢 Good | ⚪ 1 file | Trivial |
| 5 | `subprocess` import unused — `scripts/evaluate_model.py:6` (HIGH confidence) | ⚪ Low | ⚪ Low | ⚪ Low | 🟢 Good | ⚪ 1 file | Trivial |
| 6 | `os` import unused — `scripts/update_readme_dataset.py:5` (HIGH confidence) | ⚪ Low | ⚪ Low | ⚪ Low | 🟢 Good | ⚪ 1 file | Trivial |
| 7 | `os` import unused — `training/log_metrics.py:14` (HIGH confidence) | ⚪ Low | ⚪ Low | ⚪ Low | 🟢 Good | ⚪ 1 file | Trivial |
| 8 | `load_checkpoint()` unused func — `scripts/evaluate_model.py:27` (HIGH confidence) | 🟢 Medium | ⚪ Low | 🟢 Medium | 🟠 Excellent | ⚪ 1 file | Trivial |
| 9 | `save_checkpoint()` unused func — `scripts/evaluate_model.py:39` (HIGH confidence) | 🟢 Medium | ⚪ Low | 🟢 Medium | 🟠 Excellent | ⚪ 1 file | Trivial |
| 10 | `get_category_distribution()` unused func — `scripts/update_readme_dataset.py:60` (HIGH confidence) | ⚪ Low | ⚪ Low | 🟢 Medium | 🟢 Good | ⚪ 1 file | Trivial |
| 11 | `mlx.core as mx` unused — `scripts/evaluate_model.py:13` (MEDIUM confidence, side-effect import) | ⚪ Low | 🟡 High | ⚪ Low | 🟡 Marginal | ⚪ 1 file | Trivial |
| 12 | `mlx.core as mx` unused — `scripts/evaluate_ft_only.py:12` (MEDIUM confidence, side-effect import) | ⚪ Low | 🟡 High | ⚪ Low | 🟡 Marginal | ⚪ 1 file | Trivial |
| 13 | `tmp/extract_base_cache.py` — one-off utility, already served purpose | ⚪ Low | ⚪ Low | 🟢 Medium | 🟢 Good | ⚪ 1 file | Trivial |
| 14 | `tmp/check_analysis.py` — one-off diagnostic, replaced by proper reports | ⚪ Low | ⚪ Low | 🟢 Medium | 🟢 Good | ⚪ 1 file | Trivial |

---

## Code Duplication Findings (Not dead code, but maintenance debt)

| # | Finding | Urgency | Risk: Fix | Risk: No Fix | ROI | Blast Radius | Fix Effort |
|---|---------|---------|-----------|-------------|-----|-------------|------------|
| 15 | **10 scoring functions duplicated** between `evaluate_model.py` (~300 lines) and `evaluate_ft_only.py` — identical logic for `score_technical_correctness`, `score_depth`, `score_structure`, `score_hallucination`, `score_clarity`, `evaluate_response`, `load_eval_data`, `format_eta`, `get_user_prompt`, `get_reference_answer` | 🟡 High | 🟡 High | 🟠 High | 🟠 Excellent | 🟢 2 files | Medium (extract to shared `scripts/eval_utils.py`) |
| 16 | **`SYSTEM_PROMPTS` dict duplicated** between `generate_prompt.py` (~70 lines) and `generate_diverse_v2.py` — 71 category keys, same content | 🟡 High | 🟡 High | 🟠 High | 🟠 Excellent | 🟢 2 files | Medium (extract to shared `scripts/prompts.py` or load from single source) |

---

## Detailed Findings

### HIGH Confidence — Unused Imports (Safe to Remove)

### 1. `Set` — unused import
**File:** `scripts/dedupe_dataset.py:7`

```python
from typing import List, Dict, Any, Set  # Set is never used
```

### 2. `json` — unused import
**File:** `scripts/generate_prompt.py:11`

```python
import json  # Never referenced — file uses only regex + text I/O
```

### 3. `hashlib` — unused import
**File:** `scripts/generate_diverse_v2.py:18`

```python
import hashlib  # No hashlib.* calls anywhere in 5451 lines
```

### 4. `Optional` — unused import
**File:** `scripts/evaluate_model.py:11`

```python
from typing import List, Dict, Any, Optional  # Optional never used
```

### 5. `subprocess` — unused import
**File:** `scripts/evaluate_model.py:6`

```python
import subprocess  # Never used — mlx_lm called directly
```

### 6. `os` — unused import
**File:** `scripts/update_readme_dataset.py:5`

```python
import os  # File uses pathlib.Path exclusively
```

### 7. `os` — unused import
**File:** `training/log_metrics.py:14`

```python
import os  # File uses pathlib.Path exclusively
```

### HIGH Confidence — Unused Functions (Safe to Remove)

### 8. `load_checkpoint()` — never called
**File:** `scripts/evaluate_model.py:27`

Defined but `main()` loads checkpoints directly from JSON (lines 701-712), bypassing this function entirely.

### 9. `save_checkpoint()` — never called
**File:** `scripts/evaluate_model.py:39`

Defined but `main()` saves results directly (lines 731, 761), bypassing this function.

### 10. `get_category_distribution()` — never called
**File:** `scripts/update_readme_dataset.py:60`

Defined but never called from anywhere in the codebase.

### MEDIUM Confidence — Verify Before Removing

### 11-12. `mlx.core as mx` — side-effect import
**Files:** `scripts/evaluate_model.py:13`, `scripts/evaluate_ft_only.py:12`

`mx` is never directly referenced but may be needed as a side-effect import for MLX GPU/memory initialization. Removing could cause subtle issues. Keep unless confirmed unnecessary by testing.

### One-off `tmp/` Scripts

### 13. `tmp/extract_base_cache.py`
One-time data extraction from old `eval-checkpoint.json` → `eval-base-results-final.json`. Already served its purpose.

### 14. `tmp/check_analysis.py`
One-time diagnostic script. Same analysis now done by `generate_difficulty_report` and `generate_comparison_report` in `evaluate_model.py`.

---

## Excluded (Known Safe)

| Symbol | Reason |
|--------|--------|
| All `main()` functions | Entry points via `if __name__ == "__main__"` |
| All scoring functions in `evaluate_ft_only.py` | Called by `evaluate_response` |
| All functions in `validate_jsonl.py`, `dedupe_dataset.py`, `build_dataset_fixed.py` | All called within their respective pipelines |
| `scripts/prepare_data.sh` | Main pipeline entry point, called manually |
| `scripts/push_training_progress.sh` | Manual utility, referenced in docs |
| `OCI_CLI_COMMANDS`, `OCI_PYTHON_SDK`, `OCI_TERRAFORM_RESOURCES` | All used by answer generation in `generate_diverse_v2.py` |
