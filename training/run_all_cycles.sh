#!/bin/bash
# Auto-detects and runs ALL cycles that exist in config/
#
# Usage:
#   bash training/run_all_cycles.sh --fresh  # runs all cycles
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

FRESH=""
for arg in "$@"; do
    if [ "$arg" = "--fresh" ]; then
        FRESH="--fresh"
    fi
done

cd "$PROJECT_DIR"

# Find all cycle configs
CYCLES=$(ls config/cycle-*.env 2>/dev/null | sed 's|config/cycle-||' | sed 's|\.env||' | sort -V)

if [ -z "$CYCLES" ]; then
    echo "ERROR: No cycle configs found in config/"
    exit 1
fi

echo "============================================"
echo "OCI Specialist LLM - Auto Training"
echo "Found cycles: $CYCLES"
echo "============================================"

source venv/bin/activate

# Run each cycle in order
for CYCLE in $CYCLES; do
    echo ""
    echo "=== CICLO: $CYCLE ==="
    
    if [ -n "$FRESH" ]; then
        rm -rf outputs/$CYCLE
    fi
    
    CYCLE=$CYCLE python training/train_mlx_tune.py
done

echo ""
echo "============================================"
echo "✓ ALL CYCLES COMPLETE: $CYCLES"
echo "============================================"