#!/bin/bash
set -e

echo "=== Step 1: Concatenate all curated files ==="
cat data/curated/*.jsonl > data/all_curated.jsonl
echo "Created: data/all_curated.jsonl"

echo ""
echo "=== Step 2: Validate ==="
python3 scripts/validate_jsonl.py data/all_curated.jsonl

echo ""
echo "=== Step 3: Deduplicate ==="
python3 scripts/dedupe_dataset.py data/all_curated.jsonl --remove
mv data/all_curated_deduped.jsonl data/all_curated_clean.jsonl

echo ""
echo "=== Step 4: Build dataset splits ==="
python3 scripts/build_dataset_fixed.py -i data/all_curated_clean.jsonl -o data/

echo ""
echo "=== Done! ==="
echo "Generated files:"
echo "  - data/train.jsonl"
echo "  - data/valid.jsonl"
echo "  - data/eval.jsonl"
