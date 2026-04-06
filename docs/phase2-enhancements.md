# Phase 2 Enhancements Documentation

## Overview
This document details the performance, quality, and reporting enhancements implemented in Phase 2.

## Performance Improvements

### Async Data Pipeline (`scripts/performance/async_pipeline.py`)
- Prefetching during GPU compute
- Reduces data loading bottlenecks
- Usage: `python scripts/performance/async_pipeline.py --input data/train.jsonl --info`

### Dynamic Batch Sizing (`scripts/performance/dynamic_batcher.py`)
- Auto-tunes batch size based on sequence length distribution
- Optimal memory utilization on Apple Silicon
- Usage: `python scripts/performance/dynamic_batcher.py --input data/train.jsonl --recommend`

### Evaluation Response Cache (`scripts/performance/eval_cache.py`)
- LRU cache for base model responses
- Avoids redundant inference
- Usage: `python scripts/performance/eval_cache.py --stats`

## Quality Enhancements

### Semantic Scoring (`scripts/quality/semantic_scorer.py`)
- Embedding-based similarity for hallucination detection
- Uses sentence-transformers (paraphrase-MiniLM-L6-v2)
- Better correlation with human judgments
- Usage: `python scripts/quality/semantic_scorer.py --reference ref.txt --generated gen.txt`

### Factual Consistency Checker (`scripts/quality/factual_checker.py`)
- Validates OCI shapes, regions, CLI commands
- Detects cross-cloud references (AWS/Azure/GCP)
- Detects fake OCI services
- Usage: `python scripts/quality/factual_checker.py --text "response to check"`

## Reporting Improvements

### Automated HTML Reports (`scripts/reporting/report_generator.py`)
- Interactive dashboards with filtering
- Category and difficulty breakdowns
- Visual charts and graphs
- Usage: `python scripts/reporting/report_generator.py --results results.json --output report.html`

### Base vs FT Comparison (`scripts/reporting/comparison_dashboard.py`)
- Side-by-side performance comparison
- Statistical analysis
- Category-wise improvement metrics
- Usage: `python scripts/reporting/comparison_dashboard.py --base base.json --ft ft.json --output comparison.html`

## Usage

### Running Enhanced Evaluation
```bash
python scripts/evaluate_model.py --fresh "mlx-community/Llama-3.2-3B-Instruct-4bit" "outputs/merged-model" data/eval.jsonl outputs/benchmarks
```

### Generating Reports
```bash
python scripts/reporting/report_generator.py --results outputs/benchmarks/eval-ft-results-final.json --output outputs/benchmarks/report.html
```

### Comparison Dashboard
```bash
python scripts/reporting/comparison_dashboard.py --base outputs/benchmarks/eval-base-results-final.json --ft outputs/benchmarks/eval-ft-results-final.json --output outputs/benchmarks/comparison.html
```

## Backward Compatibility
All Phase 2 enhancements are opt-in. The original pipeline remains unchanged.

## Dependencies
- sentence-transformers==5.3.0
- scikit-learn==1.8.0