# Unified Evaluation Script - Design Spec

**Date**: 2026-04-10
**Project**: OCI Specialist LLM

## Overview

Unified evaluation script comparing Base Model vs Fine-Tuned Model with visualizations.

## Requirements

### Inputs
- Base model: MLX path or HuggingFace ID
- Fine-tuned adapters: cycle-N directory
- Eval data: data/eval.jsonl

### Modes
- `--mode base`: Evaluate base model only
- `--mode ft`: Evaluate FT only
- `--mode compare`: Both (default)

### Outputs
- JSON results cached
- Markdown comparison report
- 6 PNG visualizations

## Metrics (7)

| # | Metric | Range | Weight |
|---|--------|-------|--------|
| 1 | Technical Correctness | 1-5 | 25% |
| 2 | Depth | 1-5 | 15% |
| 3 | Structure | 1-5 | 15% |
| 4 | Hallucination | 1-5 (inverse) | 20% |
| 5 | Clarity | 1-5 | 10% |
| 6 | Semantic Similarity | 0-1 | 15% |
| 7 | Overall | 1-5 | 100% |

## Visualizations

1. `overall_comparison.png` - Bar chart (base vs ft per metric)
2. `score_distribution.png` - Histogram (score ranges)
3. `category_heatmap.png` - Heatmap (category × metric)
4. `difficulty_boxplot.png` - Boxplot (difficulty levels)
5. `radar_chart.png` - Radar (6 metrics)
6. `improvement_pie.png` - Pie (% better/worse/equal)

## Architecture

```
UnifiedEvaluator
├── load_models()
├── generate_response()
├── evaluate_single()
├── run_evaluation()
├── calculate_semantic_similarity()
├── create_visualizations()
└── generate_report()
```

## Acceptance Criteria

- [ ] Script runs with --cycle cycle-1 --mode compare
- [ ] Caches base and FT results separately
- [ ] Generates 6 PNG files
- [ ] Produces markdown table comparison
- [ ] Works without OCI credentials