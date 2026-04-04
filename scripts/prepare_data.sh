#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

if [ ! -d "data/curated" ]; then
    echo "ERROR: data/curated/ directory not found"
    exit 1
fi

echo "=== Step 1: Concatenate all curated files ==="
find data/curated -name "*.jsonl" -exec cat {} + > data/all_curated.jsonl
echo "Created: data/all_curated.jsonl ($(wc -l < data/all_curated.jsonl) lines)"

echo ""
echo "=== Step 2: Validate ==="
python3 scripts/validate_jsonl.py data/all_curated.jsonl

echo ""
echo "=== Step 3: Deduplicate ==="
python3 scripts/dedupe_dataset.py data/all_curated.jsonl --remove
if [ -f "data/all_curated_deduped.jsonl" ]; then
    cp data/all_curated_deduped.jsonl data/all_curated_clean.jsonl
    echo "Deduplicated: $(wc -l < data/all_curated_clean.jsonl) lines"
else
    cp data/all_curated.jsonl data/all_curated_clean.jsonl
    echo "No duplicates found, using validated file: $(wc -l < data/all_curated_clean.jsonl) lines"
fi

echo ""
echo "=== Step 4: Build dataset splits ==="
python3 scripts/build_dataset_fixed.py -i data/all_curated_clean.jsonl -o data/

echo ""
echo "=== Done! ==="
echo "Generated files:"
echo "  - data/train.jsonl ($(wc -l < data/train.jsonl) lines)"
echo "  - data/valid.jsonl ($(wc -l < data/valid.jsonl) lines)"
echo "  - data/eval.jsonl ($(wc -l < data/eval.jsonl) lines)"
