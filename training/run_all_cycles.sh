#!/bin/bash
# Simple: run cycle-1, then cycle-2
# 
# Usage:
#   bash training/run_all_cycles.sh --fresh  # runs both cycles
set -e

FRESH=""
for arg in "$@"; do
    if [ "$arg" = "--fresh" ]; then
        FRESH="--fresh"
    fi
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

source venv/bin/activate

echo "=== CICLO 1 ==="
rm -rf outputs/cycle-1
python training/train_mlx_tune.py --cycle cycle-1 $FRESH

echo ""
echo "=== CICLO 2 (continuando do cycle-1) ==="
python training/train_mlx_tune.py --cycle cycle-2 --fresh

echo ""
echo "=== PRONTO! cycle-1 + cycle-2 ==="