#!/bin/bash
set -e

MODEL=${MODEL:-"mlx-community/Llama-3.2-3B-Instruct-4bit"}
TRAIN_DATA=${TRAIN_DATA:-"data/train.jsonl"}
VALID_DATA=${VALID_DATA:-"data/valid.jsonl"}
OUTPUT_DIR=${OUTPUT_DIR:-"outputs/adapters"}
EPOCHS=${EPOCHS:-3}
BATCH_SIZE=${BATCH_SIZE:-4}
LEARNING_RATE=${LEARNING_RATE:-1e-4}
LORA_RANK=${LORA_RANK:-8}
LORA_ALPHA=${LORA_ALPHA:-16}
LORA_DROPOUT=${LORA_DROPOUT:-0.1}
GRADIENT_ACCUMULATION=${GRADIENT_ACCUMULATION:-4}

echo "=========================================="
echo "OCI Specialist LLM - MLX LoRA Training"
echo "=========================================="
echo "Model: $MODEL"
echo "Train: $TRAIN_DATA"
echo "Valid: $VALID_DATA"
echo "Output: $OUTPUT_DIR"
echo "Epochs: $EPOCHS"
echo "Batch Size: $BATCH_SIZE"
echo "Learning Rate: $LEARNING_RATE"
echo "LoRA Rank: $LORA_RANK"
echo "=========================================="

mkdir -p "$OUTPUT_DIR"

export KMP_DUPLICATE_LIB_OK=TRUE

python -m mlx_lm.lora \
    --model "$MODEL" \
    --train "$TRAIN_DATA" \
    --valid "$VALID_DATA" \
    --epochs "$EPOCHS" \
    --batch-size "$BATCH_SIZE" \
    --learning-rate "$LEARNING_RATE" \
    --lora-rank "$LORA_RANK" \
    --lora-alpha "$LORA_ALPHA" \
    --lora-dropout "$LORA_DROPOUT" \
    --gradient-accumulation "$GRADIENT_ACCUMULATION" \
    --adapter-path "$OUTPUT_DIR" \
    --save-every 1 \
    --train-adapters

echo "Training complete!"
echo "Adapters saved to: $OUTPUT_DIR"
