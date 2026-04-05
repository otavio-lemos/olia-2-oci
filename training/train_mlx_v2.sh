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
ITERS=${ITERS:-200}
MAX_SEQ_LENGTH=${MAX_SEQ_LENGTH:-4096}
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
echo "Epochs: ${EPOCHS:-N/A}"
echo "Batch Size: ${BATCH_SIZE:-N/A}"
echo "Learning Rate: ${LEARNING_RATE:-N/A}"
echo "LoRA Rank: ${LORA_RANK:-N/A}"
echo "Iters: $ITERS"
echo "Max Seq Length: $MAX_SEQ_LENGTH"
echo "=========================================="

mkdir -p "$OUTPUT_DIR"
mkdir -p "outputs/logs/$CYCLE"

export KMP_DUPLICATE_LIB_OK=TRUE

# Generate YAML config for this cycle (mlx_lm requires lora_parameters via YAML config)
YAML_CONFIG="${OUTPUT_DIR}/train_config.yaml"
cat > "$YAML_CONFIG" <<YAML_EOF
model: $MODEL
train: true
fine_tune_type: lora
data: "$(dirname "$TRAIN_DATA")"
num_layers: $NUM_LAYERS
batch_size: $BATCH_SIZE
iters: $ITERS
learning_rate: $LEARNING_RATE
grad_accumulation_steps: $GRADIENT_ACCUMULATION
adapter_path: "$OUTPUT_DIR"
save_every: 50
steps_per_report: 10
steps_per_eval: 50
max_seq_length: $MAX_SEQ_LENGTH
lora_parameters:
  rank: ${LORA_RANK:-8}
  alpha: ${LORA_ALPHA:-16}
  dropout: ${LORA_DROPOUT:-0.05}
  scale: 2.0
YAML_EOF

echo "YAML config written to: $YAML_CONFIG"

RESUME_FLAG=""
if [ -n "$PREV_ADAPTER" ] && [ -f "$PREV_ADAPTER/adapters.safetensors" ]; then
    RESUME_FLAG="--resume-adapter-file $PREV_ADAPTER/adapters.safetensors"
    echo "Resuming from: $PREV_ADAPTER/adapters.safetensors"
elif [ -n "$PREV_ADAPTER" ] && [ -f "$PREV_ADAPTER" ]; then
    RESUME_FLAG="--resume-adapter-file $PREV_ADAPTER"
    echo "Resuming from: $PREV_ADAPTER"
elif [ -n "$PREV_ADAPTER" ]; then
    echo "WARNING: PREV_ADAPTER=$PREV_ADAPTER not found, training from scratch"
fi

CMD="python -m mlx_lm lora \
    -c \"$YAML_CONFIG\" \
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
