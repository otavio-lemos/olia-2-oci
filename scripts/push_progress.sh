#!/bin/bash
# Push evaluation progress to GitHub for remote monitoring
# Usage: bash scripts/push_progress.sh

set -e

CHECKPOINT="outputs/benchmarks/eval-checkpoint.json"

if [ ! -f "$CHECKPOINT" ]; then
    echo "No checkpoint found. Run evaluation first."
    exit 1
fi

# Get progress from checkpoint
COMPLETED=$(python3 -c "import json; print(json.load(open('$CHECKPOINT'))['completed'])")
TIMESTAMP=$(python3 -c "import json; print(json.load(open('$CHECKPOINT'))['timestamp'])")

echo "=== OCI Specialist LLM - Evaluation Progress ==="
echo "Completed: $COMPLETED/9940 ($(( COMPLETED * 100 / 9940 ))%)"
echo "Timestamp: $TIMESTAMP"
echo ""

# Stage and commit progress
git add outputs/benchmarks/eval-checkpoint.json
git add outputs/benchmarks/eval-progress-*.md 2>/dev/null || true

git commit -m "chore: eval progress checkpoint - ${COMPLETED}/9940 ($(( COMPLETED * 100 / 9940 ))%) at ${TIMESTAMP}" || echo "No changes to commit"

# Push to GitHub
git push origin main

echo ""
echo "Progress pushed to GitHub!"
echo "View at: https://github.com/otavio-lemos/olia-2-oci/tree/main/outputs/benchmarks"
