# OCI Specialist LLM - Model Comparison Report

**Date:** 2026-04-04 08:38
**Progress:** 50/9,940 examples (0.5%)
**Evaluation Set:** 50 examples across 1 categories

## Executive Summary

| Metric | Base Model | Fine-Tuned Model | Improvement |
|--------|-----------|-----------------|-------------|
| **Overall Score** | **3.96/5** | **3.90/5** | **-0.06 (-1.5%)** |
| Technical Correctness | 3.16 | 3.56 | +0.40 |
| Depth | 4.11 | 3.74 | -0.36 |
| Structure | 4.17 | 4.08 | -0.09 |
| Hallucination (lower=better) | 5.00 | 5.00 | +0.00 |
| Clarity | 3.37 | 3.12 | -0.25 |

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
| compute/custom-images | 3.96 | 3.90 | -0.06 |

## Score Distribution

| Score Range | Base Count | Fine-Tuned Count |
|-------------|-----------|-----------------|
| 1-2 | 0 | 0 |
| 2-3 | 0 | 0 |
| 3-4 | 31 | 37 |
| 4-5 | 19 | 13 |

## Key Findings

1. **Overall Improvement:** -0.06 points (-1.5%)
2. **Best Category Improvement:** compute/custom-images (+-0.06)
3. **Worst Category:** compute/custom-images (3.90)

## Methodology

- **Scoring Rubric:** 6 criteria (1-5 scale): Technical Correctness, Depth, Structure, Hallucination (inverse), Clarity, Overall
- **Evaluation Set:** 50 examples from eval.jsonl, stratified across 1 OCI categories
- **Base Model:** mlx-community/Llama-3.2-3B-Instruct-4bit
- **Fine-Tuned Model:** LoRA adapters from cycle-3-v3 (merged), LR=5e-6, 466 iterations
- **Dataset:** 9,940 unique examples, 71 categories, 140 per category
