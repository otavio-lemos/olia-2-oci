# OCI Specialist LLM - Model Comparison Report

**Date:** 2026-04-04 18:18
**Progress:** 400/9,940 examples (4.0%)
**Evaluation Set:** 400 examples across 19 categories

## Executive Summary

| Metric | Base Model | Fine-Tuned Model | Improvement |
|--------|-----------|-----------------|-------------|
| **Overall Score** | **3.97/5** | **3.95/5** | **-0.01 (-0.4%)** |
| Technical Correctness | 3.17 | 3.40 | +0.23 |
| Depth | 4.11 | 3.97 | -0.14 |
| Structure | 4.21 | 4.19 | -0.02 |
| Hallucination (lower=better) | 4.99 | 4.98 | -0.00 |
| Clarity | 3.35 | 3.22 | -0.13 |

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
| compute/custom-images | 3.97 | 3.92 | -0.04 |
| compute/instances | 3.95 | 3.89 | -0.06 |
| compute/scaling | 3.91 | 3.94 | +0.03 |
| container/instances | 3.89 | 4.00 | +0.11 |
| database/mysql | 3.91 | 3.94 | +0.03 |
| database/nosql | 3.96 | 3.93 | -0.03 |
| devops/ci-cd | 4.05 | 3.99 | -0.06 |
| migration/gcp-storage | 3.89 | 3.81 | -0.08 |
| observability/logging | 3.96 | 3.93 | -0.02 |
| security/policies | 3.94 | 4.01 | +0.07 |
| security/vault-keys | 3.97 | 3.99 | +0.02 |
| storage/object | 3.87 | 4.05 | +0.17 |
| terraform/container | 4.03 | 4.04 | +0.00 |
| terraform/devops | 4.04 | 4.14 | +0.10 |
| terraform/networking | 4.12 | 4.02 | -0.10 |
| terraform/observability | 4.04 | 4.10 | +0.05 |
| terraform/provider | 4.16 | 4.14 | -0.01 |
| troubleshooting/authentication | 3.87 | 3.85 | -0.02 |
| troubleshooting/storage | 3.88 | 3.82 | -0.06 |

## Score Distribution

| Score Range | Base Count | Fine-Tuned Count |
|-------------|-----------|-----------------|
| 1-2 | 0 | 0 |
| 2-3 | 0 | 0 |
| 3-4 | 234 | 244 |
| 4-5 | 166 | 156 |

## Key Findings

1. **Overall Improvement:** -0.01 points (-0.4%)
2. **Best Category Improvement:** storage/object (+0.17)
3. **Worst Category:** migration/gcp-storage (3.81)

## Methodology

- **Scoring Rubric:** 6 criteria (1-5 scale): Technical Correctness, Depth, Structure, Hallucination (inverse), Clarity, Overall
- **Evaluation Set:** 400 examples from eval.jsonl, stratified across 19 OCI categories
- **Base Model:** mlx-community/Llama-3.2-3B-Instruct-4bit
- **Fine-Tuned Model:** LoRA adapters from cycle-3-v3 (merged), LR=5e-6, 466 iterations
- **Dataset:** 9,940 unique examples, 71 categories, 140 per category
