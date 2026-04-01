#!/bin/bash
# training/run_all_cycles.sh
# Orquestra treinamento multi-ciclo sequencial com LR decrescente
#
# Cada ciclo continua do adapter do anterior:
#   cycle-1: from scratch, LR=5e-5, 200 iters
#   cycle-2: resume cycle-1, LR=1e-5, 100 iters
#   cycle-3: resume cycle-2, LR=5e-6, 50 iters
#
# Uso:
#   bash training/run_all_cycles.sh           # roda todos os ciclos
#   bash training/run_all_cycles.sh 2         # roda a partir do cycle-2
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
START_CYCLE=${1:-1}

CYCLES=("cycle-1" "cycle-2" "cycle-3")
ITERS_MAP=(200 100 50)

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

    ITERS="${ITERS_MAP[$i]}"

    echo ""
    echo "############################################"
    echo "# Starting $CYCLE (iters=$ITERS)"
    echo "############################################"
    echo ""

    # Verifica se adapter anterior existe para ciclos > 1
    if [ "$CYCLE_NUM" -gt 1 ]; then
        PREV_CYCLE="${CYCLES[$((i-1))]}"
        PREV_ADAPTER="outputs/${PREV_CYCLE}/adapters.safetensors"
        if [ ! -f "$PREV_ADAPTER" ]; then
            echo "ERROR: Previous adapter not found: $PREV_ADAPTER"
            echo "Cannot resume training. Aborting."
            exit 1
        fi
    fi

    CYCLE="$CYCLE" ITERS="$ITERS" bash "${SCRIPT_DIR}/train_mlx_v2.sh"
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
