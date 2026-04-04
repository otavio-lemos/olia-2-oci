# OCI Specialist LLM - Model Comparison Report

**Date:** 2026-04-04 09:33
**Progress:** 100/9,940 examples (1.0%)
**Evaluation Set:** 100 examples across 1 categories

## Executive Summary

| Metric | Base Model | Fine-Tuned Model | Improvement |
|--------|-----------|-----------------|-------------|
| **Overall Score** | **3.97/5** | **3.90/5** | **-0.07 (-1.8%)** |
| Technical Correctness | 3.16 | 3.58 | +0.42 |
| Depth | 4.14 | 3.73 | -0.40 |
| Structure | 4.20 | 4.07 | -0.13 |
| Hallucination (lower=better) | 5.00 | 5.00 | +0.00 |
| Clarity | 3.35 | 3.10 | -0.25 |

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
| compute/custom-images | 3.97 | 3.90 | -0.07 |

## Score Distribution

| Score Range | Base Count | Fine-Tuned Count |
|-------------|-----------|-----------------|
| 1-2 | 0 | 0 |
| 2-3 | 0 | 0 |
| 3-4 | 59 | 72 |
| 4-5 | 41 | 28 |

## Key Findings

1. **Overall Improvement:** -0.07 points (-1.8%)
2. **Best Category Improvement:** compute/custom-images (+-0.07)
3. **Worst Category:** compute/custom-images (3.90)

## Methodology

- **Scoring Rubric:** 6 criteria (1-5 scale): Technical Correctness, Depth, Structure, Hallucination (inverse), Clarity, Overall
- **Evaluation Set:** 100 examples from eval.jsonl, stratified across 1 OCI categories
- **Base Model:** mlx-community/Llama-3.2-3B-Instruct-4bit
- **Fine-Tuned Model:** LoRA adapters from cycle-3-v3 (merged), LR=5e-6, 466 iterations
- **Dataset:** 9,940 unique examples, 71 categories, 140 per category
