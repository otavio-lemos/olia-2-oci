# OCI Specialist LLM - Final Training Report

**Date:** 2026-04-03
**Model:** Llama-3.2-3B-Instruct-4bit (LoRA Fine-tuning via MLX)
**Hardware:** Apple Silicon (M-series)

---

## Executive Summary

| Metric | Value |
|--------|-------|
| **Dataset Size** | 9,940 unique examples |
| **Categories** | 71 OCI topics |
| **Examples per Category** | 140 |
| **Best Val Loss** | **0.114** (cycle-3) |
| **Best Train Loss** | **0.089** (cycle-3) |
| **Final Adapter** | `outputs/cycle-3/adapters.safetensors` |
| **Merged Model** | `outputs/merged-model/` (~1.8GB) |

---

## Training Results

| Cycle | Learning Rate | Iters | Val Loss | Train Loss | Notes |
|-------|--------------|-------|----------|------------|-------|
| cycle-1 | 5e-5 | 200 | 0.163 | 0.161 | From scratch |
| cycle-2 | 1e-5 | 200 | 0.119 | 0.104 | Resume cycle-1 |
| cycle-3 | 5e-6 | 200 | **0.114** | **0.089** | Resume cycle-2 (best) |

### Training Progression

```
Val Loss:  0.163 → 0.119 → 0.114  (30% improvement)
Train Loss: 0.161 → 0.104 → 0.089  (45% improvement)
```

The learning rate decay strategy (5e-5 → 1e-5 → 5e-6) with sequential resume training produced consistent improvement across all 3 cycles without overfitting.

---

## Dataset Statistics

### Split Distribution

| Split | Examples | Percentage |
|-------|----------|------------|
| Train | 7,455 | 75.0% |
| Valid | 1,491 | 15.0% |
| Eval | 994 | 10.0% |
| **Total** | **9,940** | **100%** |

### Difficulty Distribution (Train)

| Difficulty | Count | Percentage |
|------------|-------|------------|
| Beginner | 2,223 | 29.8% |
| Intermediate | 3,731 | 50.0% |
| Advanced | 1,501 | 20.1% |

### Category Coverage

All 71 OCI taxonomy categories covered with exactly 105 examples each in training split:

| Group | Topics | Examples |
|-------|--------|----------|
| oci-core | 20 | 2,100 |
| oci-security | 9 | 945 |
| oci-migration | 14 | 1,470 |
| oci-terraform | 12 | 1,260 |
| oci-observability | 4 | 420 |
| oci-troubleshooting | 8 | 840 |
| oci-devops | 4 | 420 |

---

## Data Quality

| Check | Status | Details |
|-------|--------|---------|
| Fake CLI Commands | ✅ PASS | 0 occurrences |
| Fake SDK Classes | ✅ PASS | 0 occurrences |
| Fake Terraform | ✅ PASS | 0 occurrences |
| JSON IAM Policies | ✅ PASS | 0 occurrences |
| "deletar" anglicism | ✅ PASS | 0 occurrences |
| Broken URLs | ✅ PASS | 0 occurrences |
| Format Validation | ✅ PASS | 100% valid JSONL |
| Duplicates | ✅ PASS | 0 exact, 0 near-duplicates |

---

## Training Configuration

| Parameter | Value |
|-----------|-------|
| Base Model | mlx-community/Llama-3.2-3B-Instruct-4bit |
| LoRA Rank | 8 |
| LoRA Alpha | 16 |
| LoRA Dropout | 0.05 |
| Num Layers | 16 |
| Batch Size | 1 |
| Gradient Accumulation | 4 |
| Max Seq Length | 1024 |
| Save Every | 50 steps |

---

## Pipeline Architecture

```
data/curated/*.jsonl (71 files × 140 examples)
    ↓
data/all_curated.jsonl (9,940 examples)
    ↓ validate → deduplicate → split
data/train.jsonl (7,455) | valid.jsonl (1,491) | eval.jsonl (994)
    ↓
Training: cycle-1 → cycle-2 → cycle-3 (LR decay, resume)
    ↓
outputs/cycle-3/adapters.safetensors (best adapter)
    ↓
outputs/merged-model/ (fused model for inference)
```

---

## Key Improvements Over Previous Runs

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Dataset Size | 495 | 9,940 | 20x |
| Val Loss (cycle-1) | 1.227 | 0.163 | 87% better |
| Val Loss (cycle-3) | 1.222 | 0.114 | 91% better |
| Fake Commands | ~808 | 0 | 100% fixed |
| "deletar" | 315 | 0 | 100% fixed |
| Duplicates | 699 | 0 | 100% fixed |

---

## Files Structure

```
config/
├── cycle-1.env          # LR=5e-5, from scratch
├── cycle-2.env          # LR=1e-5, resume cycle-1
└── cycle-3.env          # LR=5e-6, resume cycle-2

training/
├── train_mlx_v2.sh      # Training script with resume support
├── run_all_cycles.sh    # Multi-cycle orchestrator
├── export_adapter.sh    # Model fusion (mlx_lm fuse)
├── run_inference.sh     # Inference testing
└── log_metrics.py       # Metrics capture and CSV export

outputs/
├── cycle-1/             # Cycle 1 adapters
├── cycle-2/             # Cycle 2 adapters
├── cycle-3/             # Cycle 3 adapters (BEST)
│   ├── adapters.safetensors
│   └── 0000{050,100,150,200}_adapters.safetensors
├── merged-model/        # Fused model (~1.8GB)
├── logs/                # Training logs + metrics CSV
└── benchmarks/          # Evaluation reports

scripts/
├── generate_diverse_v2.py  # Dataset generator (9,940 examples)
├── validate_jsonl.py       # Format validation
├── dedupe_dataset.py       # Exact + near-duplicate removal
├── build_dataset_fixed.py  # Stratified split (75/15/10)
└── evaluate_model.py       # Model evaluation rubric
```

---

## Recommendations

1. **RAG Layer**: For factual accuracy on CLI commands, SDK classes, and Terraform resources, add a RAG layer to supplement the fine-tuned model with real-time documentation.

2. **Response Diversity**: Current dataset uses 8 response structures. Consider adding more variety (FAQ, decision trees, cost analysis, security hardening guides).

3. **Larger Model**: Consider fine-tuning Llama-3.1-8B for better reasoning capability on complex architectural scenarios.

4. **Human Evaluation**: Automated scoring captures syntax and structure, but human review of generated responses is needed for nuanced quality assessment.

5. **Continuous Training**: Pipeline supports adding new examples and retraining. Monitor OCI documentation updates and regenerate affected categories.
