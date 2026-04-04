# OCI Specialist LLM - Model Comparison Report

**Date:** 2026-04-04 09:44
**Progress:** 150/9,940 examples (1.5%)
**Evaluation Set:** 150 examples across 2 categories

## Executive Summary

| Metric | Base Model | Fine-Tuned Model | Improvement |
|--------|-----------|-----------------|-------------|
| **Overall Score** | **3.96/5** | **3.88/5** | **-0.08 (-2.1%)** |
| Technical Correctness | 3.14 | 3.54 | +0.40 |
| Depth | 4.13 | 3.72 | -0.41 |
| Structure | 4.19 | 4.04 | -0.15 |
| Hallucination (lower=better) | 5.00 | 5.00 | +0.00 |
| Clarity | 3.34 | 3.10 | -0.25 |

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
| compute/instances | 3.95 | 3.85 | -0.10 |

## Score Distribution

| Score Range | Base Count | Fine-Tuned Count |
|-------------|-----------|-----------------|
| 1-2 | 0 | 0 |
| 2-3 | 0 | 0 |
| 3-4 | 89 | 113 |
| 4-5 | 61 | 37 |

## Key Findings

1. **Overall Improvement:** -0.08 points (-2.1%)
2. **Best Category Improvement:** compute/custom-images (+-0.07)
3. **Worst Category:** compute/instances (3.85)

## Methodology

- **Scoring Rubric:** 6 criteria (1-5 scale): Technical Correctness, Depth, Structure, Hallucination (inverse), Clarity, Overall
- **Evaluation Set:** 150 examples from eval.jsonl, stratified across 2 OCI categories
- **Base Model:** mlx-community/Llama-3.2-3B-Instruct-4bit
- **Fine-Tuned Model:** LoRA adapters from cycle-3-v3 (merged), LR=5e-6, 466 iterations
- **Dataset:** 9,940 unique examples, 71 categories, 140 per category
