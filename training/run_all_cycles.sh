#!/bin/bash
# training/run_all_cycles.sh
# Orquestra treinamento - padrão é 1 ciclo (cycle-1)
#
# Uso:
#   bash training/run_all_cycles.sh           # roda apenas cycle-1 (padrão)
#   bash training/run_all_cycles.sh --fresh  # limpa e roda cycle-1 do zero
#   bash training/run_all_cycles.sh 3         # roda até cycle-3 (se necessário)
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Parse arguments
FRESH=""
START_CYCLE=1
MAX_CYCLE=1
for arg in "$@"; do
    if [ "$arg" = "--fresh" ]; then
        FRESH="--fresh"
    elif [[ "$arg" =~ ^[0-9]+$ ]]; then
        MAX_CYCLE="$arg"
    fi
done

# Se nao passou CYCLE via env, usa cycle-1
if [ -z "$CYCLE" ]; then
    CYCLE="cycle-1"
fi

mkdir -p "outputs/logs"

# Clean outputs if --fresh
if [ -n "$FRESH" ]; then
    echo "[fresh] Cleaning outputs..."
    for dir in outputs/${CYCLE} outputs/logs outputs/benchmarks outputs/merged-model; do
        if [ -d "$dir" ]; then
            rm -rf "$dir"
            echo "[fresh] Cleaned: $dir"
        fi
    done
    echo "[fresh] Starting fresh with single cycle."
    echo ""
fi

echo "============================================"
echo "OCI Specialist LLM - Training (Single Cycle)"
echo "============================================"
echo "Cycle: $CYCLE"
echo "============================================"
echo ""

# Source config
ENV_FILE="${PROJECT_DIR}/config/${CYCLE}.env"
if [ ! -f "$ENV_FILE" ]; then
    echo "ERROR: Config not found: $ENV_FILE"
    exit 1
fi
source "$ENV_FILE"

echo "Configuration:"
echo "  LR: $LEARNING_RATE"
echo "  Iters: $ITERS"
echo "  Rank: $LORA_RANK"
echo "  Seq Length: $MAX_SEQ_LENGTH"
echo ""

CYCLE="$CYCLE" python "${SCRIPT_DIR}/train_mlx_tune.py" $FRESH
