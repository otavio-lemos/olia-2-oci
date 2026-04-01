#!/bin/bash
# training/train_mlx_v2.sh
# Versão com suporte a resume de ciclo anterior e logging estruturado
#
# Uso:
#   CYCLE=cycle-1 bash training/train_mlx_v2.sh
#   CYCLE=cycle-2 bash training/train_mlx_v2.sh
#   CYCLE=cycle-3 bash training/train_mlx_v2.sh
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CYCLE=${CYCLE:-"cycle-1"}

source "${SCRIPT_DIR}/../config/${CYCLE}.env"

MODEL=${MODEL:-"mlx-community/Llama-3.2-3B-Instruct-4bit"}
TRAIN_DATA=${TRAIN_DATA:-"data/train.jsonl"}
VALID_DATA=${VALID_DATA:-"data/valid.jsonl"}
OUTPUT_DIR=${OUTPUT_DIR:-"outputs/${CYCLE}"}
PREV_ADAPTER=${PREV_ADAPTER:-""}
EPOCHS=${EPOCHS:-2}
BATCH_SIZE=${BATCH_SIZE:-1}
LEARNING_RATE=${LEARNING_RATE:-5e-5}
LORA_RANK=${LORA_RANK:-8}
LORA_ALPHA=${LORA_ALPHA:-16}
LORA_DROPOUT=${LORA_DROPOUT:-0.05}
GRADIENT_ACCUMULATION=${GRADIENT_ACCUMULATION:-4}

ITERS=${ITERS:-200}
MAX_SEQ_LENGTH=${MAX_SEQ_LENGTH:-1024}
NUM_LAYERS=${NUM_LAYERS:-16}

echo "=========================================="
echo "OCI Specialist LLM - MLX LoRA Training v2"
echo "=========================================="
echo "Cycle: $CYCLE"
echo "Model: $MODEL"
echo "Train: $TRAIN_DATA"
echo "Valid: $VALID_DATA"
echo "Output: $OUTPUT_DIR"
echo "Resume: ${PREV_ADAPTER:-(none, training from scratch)}"
echo "Epochs: $EPOCHS"
echo "Batch Size: $BATCH_SIZE"
echo "Learning Rate: $LEARNING_RATE"
echo "LoRA Rank: $LORA_RANK"
echo "Iters: $ITERS"
echo "Max Seq Length: $MAX_SEQ_LENGTH"
echo "=========================================="

mkdir -p "$OUTPUT_DIR"
mkdir -p "outputs/logs/$CYCLE"

export KMP_DUPLICATE_LIB_OK=TRUE

RESUME_FLAG=""
if [ -n "$PREV_ADAPTER" ] && [ -f "$PREV_ADAPTER" ]; then
    RESUME_FLAG="--resume-adapter-file $PREV_ADAPTER"
    echo "Resuming from: $PREV_ADAPTER"
elif [ -n "$PREV_ADAPTER" ]; then
    echo "WARNING: PREV_ADAPTER=$PREV_ADAPTER not found, training from scratch"
fi

CMD="python -m mlx_lm lora \
    --model \"$MODEL\" \
    --train \
    --data \"$(dirname "$TRAIN_DATA")\" \
    --fine-tune-type lora \
    --num-layers $NUM_LAYERS \
    --batch-size $BATCH_SIZE \
    --iters $ITERS \
    --learning-rate $LEARNING_RATE \
    --grad-accumulation-steps $GRADIENT_ACCUMULATION \
    --adapter-path \"$OUTPUT_DIR\" \
    --save-every 50 \
    --steps-per-report 10 \
    --steps-per-eval 50 \
    --max-seq-length $MAX_SEQ_LENGTH \
    $RESUME_FLAG"

echo ""
echo "Running training with logging..."
echo ""

python "${SCRIPT_DIR}/log_metrics.py" "$CYCLE" -- bash -c "$CMD"
EXIT_CODE=$?

echo ""
echo "=========================================="
if [ $EXIT_CODE -eq 0 ]; then
    echo "Training complete!"
else
    echo "Training FAILED (exit code $EXIT_CODE)"
fi
echo "Adapters saved to: $OUTPUT_DIR"
echo "Logs saved to: outputs/logs/$CYCLE/"
echo "=========================================="

exit $EXIT_CODE
