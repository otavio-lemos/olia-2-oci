#!/bin/bash
# Auto-detects and runs ALL cycles that exist in config/
# Each cycle continues from the MERGED model of previous cycle
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

# Track previous cycle for merging
PREV_CYCLE=""
BASE_MODEL="mlx-community/Meta-Llama-3.1-8B-Instruct-4bit"

# Run each cycle in order
for CYCLE in $CYCLES; do
    echo ""
    echo "=== CICLO: $CYCLE ==="
    
    # Clean if --fresh
    if [ -n "$FRESH" ]; then
        rm -rf outputs/$CYCLE
    fi
    
    # Load config for this cycle
    source config/${CYCLE}.env
    
    # Determine which model to use as base:
    # - If first cycle: use original base model
    # - If subsequent cycle: use merged model from previous cycle
    if [ -z "$PREV_CYCLE" ]; then
        # First cycle: use base model
        echo "Using base model: $BASE_MODEL"
    else
        # Subsequent cycle: use merged model from previous cycle
        MERGED_PREV="outputs/${PREV_CYCLE}/merged"
        if [ ! -d "$MERGED_PREV" ]; then
            echo "ERROR: Merged model from cycle $PREV_CYCLE not found at $MERGED_PREV"
            exit 1
        fi
        echo "Using merged model from previous cycle: $MERGED_PREV"
        BASE_MODEL="$MERGED_PREV"
    fi
    
    # Run training for this cycle
    CYCLE=$CYCLE python training/train_mlx_tune.py
    
    # After training, merge adapters with base model for next cycle
    echo ""
    echo "=== Merging adapters for cycle $CYCLE ==="
    
    CYCLE_NAME=$CYCLE python scripts/merge_export.py --cycle $CYCLE --quant q4 2>/dev/null || \
    echo "Note: merge_export failed or skipped (will try again later)"
    
    # Update PREV_CYCLE for next iteration
    PREV_CYCLE=$CYCLE
done

echo ""
echo "============================================"
echo "✓ ALL CYCLES COMPLETE: $CYCLES"
echo "============================================"