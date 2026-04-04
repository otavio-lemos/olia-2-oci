# OCI Specialist LLM - Model Comparison Report

**Date:** 2026-04-04 17:33
**Progress:** 250/9,940 examples (2.5%)
**Evaluation Set:** 250 examples across 9 categories

## Executive Summary

| Metric | Base Model | Fine-Tuned Model | Improvement |
|--------|-----------|-----------------|-------------|
| **Overall Score** | **3.98/5** | **3.93/5** | **-0.05 (-1.2%)** |
| Technical Correctness | 3.18 | 3.48 | +0.30 |
| Depth | 4.14 | 3.88 | -0.26 |
| Structure | 4.23 | 4.14 | -0.09 |
| Hallucination (lower=better) | 5.00 | 5.00 | -0.00 |
| Clarity | 3.35 | 3.16 | -0.18 |

## Training Metrics

| Cycle | Learning Rate | Iterations | Train Loss | Val Loss |
|-------|--------------|------------|------------|----------|
| cycle-1 | 3e-5 | 1864 | 0.074 | 0.070 |
| cycle-2 | 1e-5 | 932 | 0.056 | 0.056 |
| cycle-3 | 5e-6 | 466 | 0.039 | 0.053 |

**Best Model:** cycle-3 (lowest validation loss: 0.053)

## Category-by-Category Comparison

| Category | Base | Fine-Tuned | Delta |
|----------|------|------------|-------|
| compute/custom-images | 3.97 | 3.89 | -0.07 |
| compute/instances | 3.95 | 3.89 | -0.06 |
| database/mysql | 3.91 | 3.94 | +0.03 |
| devops/ci-cd | 4.05 | 3.99 | -0.06 |
| security/policies | 3.94 | 4.01 | +0.07 |
| security/vault-keys | 3.97 | 3.99 | +0.02 |
| terraform/container | 4.03 | 4.04 | +0.00 |
| terraform/networking | 4.12 | 4.02 | -0.10 |
| terraform/observability | 4.08 | 4.09 | +0.02 |

## Score Distribution

| Score Range | Base Count | Fine-Tuned Count |
|-------------|-----------|-----------------|
| 1-2 | 0 | 0 |
| 2-3 | 0 | 0 |
| 3-4 | 138 | 161 |
| 4-5 | 112 | 89 |

## Key Findings

1. **Overall Improvement:** -0.05 points (-1.2%)
2. **Best Category Improvement:** security/policies (+0.07)
3. **Worst Category:** compute/instances (3.89)

## Methodology

- **Scoring Rubric:** 6 criteria (1-5 scale): Technical Correctness, Depth, Structure, Hallucination (inverse), Clarity, Overall
- **Evaluation Set:** 250 examples from eval.jsonl, stratified across 9 OCI categories
- **Base Model:** mlx-community/Llama-3.2-3B-Instruct-4bit
- **Fine-Tuned Model:** LoRA adapters from cycle-3-v3 (merged), LR=5e-6, 466 iterations
- **Dataset:** 9,940 unique examples, 71 categories, 140 per category
