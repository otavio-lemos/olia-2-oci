#!/bin/bash
# Auto-detects and runs ALL cycles that exist in config/
#
# Usage:
#   bash training/run_cycles.sh --all            # runs all cycles
#   bash training/run_cycles.sh --all --fresh  # runs all cycles fresh
#   bash training/run_cycles.sh --cycle cycle-1   # runs specific cycle only
#   bash training/run_cycles.sh --cycle cycle-2 --fresh  # runs cycle-2 fresh
#   bash training/run_cycles.sh --help        # shows this help
set -e

show_help() {
    echo "OCI Specialist LLM - Auto Training"
    echo ""
    echo "Usage:"
    echo "  bash training/run_cycles.sh [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --help              Show this help message"
    echo "  --all              Run all cycles found in config/"
    echo "  --all --fresh      Run all cycles fresh"
    echo "  --cycle CYCLE      Run specific cycle only (e.g., --cycle cycle-1)"
    echo "  --cycle CYCLE --fresh  Run specific cycle fresh"
    echo ""
    echo "Examples:"
    echo "  bash training/run_cycles.sh --all"
    echo "  bash training/run_cycles.sh --all --fresh"
    echo "  bash training/run_cycles.sh --cycle cycle-1"
    echo "  bash training/run_cycles.sh --cycle cycle-2 --fresh"
    echo ""
    echo "Available cycles in config/:"
    ls config/cycle-*.env 2>/dev/null | sed 's|config/||' | sed 's|\.env||' | sort -V | awk '{print "  - " $0}'
    exit 0
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

FRESH=""
SELECTED_CYCLE=""
RUN_ALL=""

# Parse arguments
if [[ $# -eq 0 ]]; then
    show_help
fi

while [[ $# -gt 0 ]]; do
    case "$1" in
        --help|-h)
            show_help
            ;;
        --all)
            RUN_ALL="true"
            shift
            ;;
        --fresh)
            FRESH="true"
            shift
            ;;
        --cycle)
            SELECTED_CYCLE="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

cd "$PROJECT_DIR"

# Find all cycle configs or use selected one
if [ -n "$SELECTED_CYCLE" ]; then
    if [ ! -f "config/${SELECTED_CYCLE}.env" ]; then
        echo "ERROR: Config not found: config/${SELECTED_CYCLE}.env"
        exit 1
    fi
    CYCLES="$SELECTED_CYCLE"
elif [ -n "$RUN_ALL" ]; then
    CYCLES=$(ls config/cycle-*.env 2>/dev/null | sed 's|config/||' | sed 's|\.env||' | sort -V)
else
    show_help
fi

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
    
    # Salvar config usada para reproducibility
    OUTPUT_DIR="outputs/${CYCLE}"
    mkdir -p "${OUTPUT_DIR}/config"
    cp "config/${CYCLE}.env" "${OUTPUT_DIR}/config/${CYCLE}.env"
    echo "[config] Saved: ${OUTPUT_DIR}/config/${CYCLE}.env"
    
    CYCLE=$CYCLE caffeinate -i python training/train_mlx_tune.py
done

echo ""
echo "============================================"
echo "✓ ALL CYCLES COMPLETE: $CYCLES"
echo "============================================"