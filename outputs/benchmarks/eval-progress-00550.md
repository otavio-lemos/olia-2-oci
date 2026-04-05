# OCI Specialist LLM - Model Comparison Report

**Date:** 2026-04-04 22:35
**Progress:** 550/994 examples (55.3%)
**Evaluation Set:** 550 examples across 30 categories

## Executive Summary

| Metric | Base Model | Fine-Tuned Model | Improvement |
|--------|-----------|-----------------|-------------|
| **Overall Score** | **3.96/5** | **3.96/5** | **-0.00 (-0.0%)** |
| Technical Correctness | 3.16 | 3.34 | +0.18 |
| Depth | 4.12 | 4.03 | -0.09 |
| Structure | 4.21 | 4.23 | +0.02 |
| Hallucination (lower=better) | 4.99 | 4.98 | -0.00 |
| Clarity | 3.35 | 3.23 | -0.11 |

## Training Metrics

| Cycle | Learning Rate | Iterations | Train Loss | Val Loss |
|-------|--------------|------------|------------|----------|
| cycle-1 | 3e-5 | 2485 | 0.062 | 0.073 |
| cycle-2 | 1e-5 | 2485 | 0.049 | 0.057 |

**Best Model:** cycle-2 (lowest validation loss: 0.057, minimal overfitting gap: 0.008)

## Category-by-Category Comparison

| Category | Base | Fine-Tuned | Delta |
|----------|------|------------|-------|
| compute/custom-images | 3.97 | 3.92 | -0.04 |
| compute/instances | 3.95 | 3.89 | -0.06 |
| compute/scaling | 3.91 | 3.94 | +0.03 |
| container/instances | 3.89 | 4.00 | +0.11 |
| database/autonomous-json | 4.04 | 4.02 | -0.02 |
| database/exadata | 3.94 | 3.98 | +0.04 |
| database/mysql | 3.91 | 3.94 | +0.03 |
| database/nosql | 3.96 | 3.93 | -0.03 |
| devops/ci-cd | 4.05 | 3.99 | -0.06 |
| devops/resource-manager | 3.91 | 3.99 | +0.07 |
| migration/aws-compute | 3.95 | 4.04 | +0.10 |
| migration/aws-database | 3.83 | 4.06 | +0.23 |
| migration/data-transfer | 3.98 | 3.93 | -0.04 |
| migration/gcp-storage | 3.89 | 3.81 | -0.08 |
| migration/onprem-compute | 3.96 | 3.90 | -0.06 |
| observability/logging | 3.96 | 3.93 | -0.02 |
| security/iam-basics | 4.07 | 3.99 | -0.08 |
| security/policies | 3.94 | 4.01 | +0.07 |
| security/vault-keys | 3.97 | 3.99 | +0.02 |
| serverless/api-gateway | 4.03 | 4.03 | +0.00 |
| storage/file | 3.89 | 3.92 | +0.03 |
| storage/object | 3.87 | 4.05 | +0.17 |
| terraform/container | 4.03 | 4.04 | +0.00 |
| terraform/devops | 4.04 | 4.14 | +0.10 |
| terraform/networking | 4.12 | 4.02 | -0.10 |
| terraform/observability | 4.04 | 4.10 | +0.05 |
| terraform/provider | 4.16 | 4.14 | -0.01 |
| terraform/state | 4.05 | 4.04 | -0.00 |
| troubleshooting/authentication | 3.85 | 3.92 | +0.07 |
| troubleshooting/storage | 3.88 | 3.82 | -0.06 |

## Score Distribution

| Score Range | Base Count | Fine-Tuned Count |
|-------------|-----------|-----------------|
| 1-2 | 0 | 0 |
| 2-3 | 0 | 0 |
| 3-4 | 326 | 322 |
| 4-5 | 224 | 228 |

## Key Findings

1. **Overall Improvement:** -0.00 points (-0.0%)
2. **Best Category Improvement:** migration/aws-database (+0.23)
3. **Worst Category:** migration/gcp-storage (3.81)

## Methodology

- **Scoring Rubric:** 6 criteria (1-5 scale): Technical Correctness, Depth, Structure, Hallucination (inverse), Clarity, Overall
- **Evaluation Set:** 550 examples from eval.jsonl, stratified across 30 OCI categories
- **Base Model:** mlx-community/Llama-3.2-3B-Instruct-4bit
- **Fine-Tuned Model:** LoRA adapters from cycle-2 (merged), LR=1e-5, 2485 iterations, rank=16
- **Dataset:** 9,940 unique examples, 71 categories, 140 per category
