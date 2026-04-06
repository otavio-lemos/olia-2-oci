#!/bin/bash
# training/run_all_cycles.sh
# Orquestra treinamento multi-ciclo sequencial com LR decrescente
#
# Cada ciclo continua do adapter do anterior (config em config/cycle-N.env):
#   cycle-1: from scratch, LR=3e-5, 2450 iters, rank=16, seq=2048
#   cycle-2: resume cycle-1, LR=1e-5, 2450 iters, rank=16, seq=2048
#   cycle-3: resume cycle-2, LR=5e-6, 500 iters, rank=16, seq=2048
#
# Uso:
#   bash training/run_all_cycles.sh           # roda todos os ciclos
#   bash training/run_all_cycles.sh 2         # roda a partir do cycle-2
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
START_CYCLE=${1:-1}

CYCLES=("cycle-1" "cycle-2" "cycle-3")

mkdir -p "outputs/logs"

echo "============================================"
echo "OCI Specialist LLM - Multi-Cycle Training"
echo "============================================"
echo "Starting from cycle: $START_CYCLE"
echo "Cycles to run: ${CYCLES[@]:$((START_CYCLE-1))}"
echo "============================================"
echo ""

for i in "${!CYCLES[@]}"; do
    CYCLE="${CYCLES[$i]}"
    CYCLE_NUM=$((i + 1))

    if [ "$CYCLE_NUM" -lt "$START_CYCLE" ]; then
        continue
    fi

    # Source config for this cycle — single source of truth
    ENV_FILE="${PROJECT_DIR}/config/${CYCLE}.env"
    if [ ! -f "$ENV_FILE" ]; then
        echo "ERROR: Config not found: $ENV_FILE"
        exit 1
    fi
    source "$ENV_FILE"

    echo ""
    echo "############################################"
    echo "# Starting $CYCLE"
    echo "#   LR: $LEARNING_RATE"
    echo "#   Iters: $ITERS"
    echo "#   Rank: $LORA_RANK"
    echo "#   Seq Length: $MAX_SEQ_LENGTH"
    echo "############################################"
    echo ""

    # Verify previous adapter exists for cycles > 1
    if [ "$CYCLE_NUM" -gt 1 ] && [ -n "${PREV_ADAPTER:-}" ]; then
        if [ ! -f "$PREV_ADAPTER" ]; then
            echo "ERROR: Previous adapter not found: $PREV_ADAPTER"
            echo "Cannot resume training. Aborting."
            exit 1
        fi
        echo "Resuming from: $PREV_ADAPTER"
    fi

    CYCLE="$CYCLE" bash "${SCRIPT_DIR}/train_mlx_v2.sh"
    EXIT_CODE=$?

    if [ $EXIT_CODE -ne 0 ]; then
        echo ""
        echo "ERROR: $CYCLE failed with exit code $EXIT_CODE"
        echo "Aborting multi-cycle training."
        exit $EXIT_CODE
    fi

    echo ""
    echo "$CYCLE completed successfully."
    echo ""
done

echo "============================================"
echo "All cycles completed!"
echo "============================================"
echo ""
echo "Results:"
for CYCLE in "${CYCLES[@]}"; do
    if [ -d "outputs/logs/$CYCLE" ]; then
        echo "  $CYCLE: outputs/logs/$CYCLE/metrics.csv"
    fi
done
echo ""
echo "Final adapter: outputs/cycle-3/adapters.safetensors"
