#!/bin/bash
set -e

BASE_MODEL=${BASE_MODEL:-${MODEL:-"mlx-community/Llama-3.2-3B-Instruct-4bit"}}
ADAPTER_DIR=${ADAPTER_DIR:-${OUTPUT_DIR:-"outputs/adapters"}}
MERGED_MODEL=${MERGED_MODEL:-"outputs/merged-model"}

echo "=========================================="
echo "Exporting LoRA Adapter"
echo "=========================================="
echo "Adapter: $ADAPTER_DIR"
echo "Output: $MERGED_MODEL"
echo "=========================================="

python -m mlx_lm.lora \
    --model "$BASE_MODEL" \
    --adapter-path "$ADAPTER_DIR" \
    --merge-weights "$MERGED_MODEL"

echo "Export complete!"
echo "Merged model saved to: $MERGED_MODEL"
