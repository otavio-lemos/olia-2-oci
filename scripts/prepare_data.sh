#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

# Use venv python
PYTHON="${PROJECT_DIR}/venv/bin/python"

if [ ! -d "data/curated" ]; then
    echo "ERROR: data/curated/ directory not found"
    exit 1
fi

echo "=== Step 1: Concatenate all curated files ==="
find data/curated -name "*.jsonl" -exec cat {} + > data/all_curated.jsonl
echo "Created: data/all_curated.jsonl ($(wc -l < data/all_curated.jsonl) lines)"

echo ""
echo "=== Step 2: Validate (structural) ==="
${PYTHON} scripts/validate_jsonl.py data/all_curated.jsonl

echo ""
echo "=== Step 3: Clean content (remove generic templates, wrong CLI, etc.) ==="
${PYTHON} scripts/clean_dataset.py --input data/all_curated.jsonl --output data/all_curated_clean.jsonl --all

echo ""
echo "=== Step 4: Deduplicate (embedding-based, semantic) ==="
${PYTHON} scripts/dedupe_embedding.py --input data/all_curated_clean.jsonl --output data/all_curated_semantic_dedup.jsonl --threshold 0.97 --question-threshold 0.97 --answer-threshold 0.97
if [ -f "data/all_curated_semantic_dedup.jsonl" ]; then
    echo "Deduplicated (semantic): $(wc -l < data/all_curated_semantic_dedup.jsonl) lines"
fi

echo ""
echo "=== Step 5: Build dataset splits ==="
${PYTHON} scripts/build_dataset_fixed.py -i data/all_curated_semantic_dedup.jsonl -o data/

echo ""
echo "=== Done! ==="
echo "Generated files:"
echo "  - data/train.jsonl ($(wc -l < data/train.jsonl) lines)"
echo "  - data/valid.jsonl ($(wc -l < data/valid.jsonl) lines)"
echo "  - data/eval.jsonl ($(wc -l < data/eval.jsonl) lines)"
