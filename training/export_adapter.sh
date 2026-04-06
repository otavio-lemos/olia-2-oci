#!/bin/bash
# training/export_adapter.sh
# Exporta adapter LoRA para modelo merged usando mlx-tune
#
# Uso:
#   CYCLE=cycle-3 bash training/export_adapter.sh
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

CYCLE=${CYCLE:-"cycle-3"}
source "${PROJECT_DIR}/config/${CYCLE}.env"

BASE_MODEL=${BASE_MODEL:-${MODEL:-"mlx-community/Meta-Llama-3.1-8B-Instruct-4bit"}}
ADAPTER_DIR=${ADAPTER_DIR:-${OUTPUT_DIR:-"outputs/${CYCLE}"}}
MERGED_MODEL=${MERGED_MODEL:-"outputs/merged-model"}

echo "=========================================="
echo "Exporting LoRA Adapter (mlx-tune)"
echo "=========================================="
echo "Cycle: $CYCLE"
echo "Base Model: $BASE_MODEL"
echo "Adapter: $ADAPTER_DIR"
echo "Output: $MERGED_MODEL"
echo "=========================================="

python -c "
from mlx_tune import FastLanguageModel

print('Loading base model...')
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name='${BASE_MODEL}',
    max_seq_length=${MAX_SEQ_LENGTH:-2048},
    load_in_4bit=True,
)

print('Loading adapters from: ${ADAPTER_DIR}')
model.load_adapter('${ADAPTER_DIR}/adapters.safetensors')

print('Saving merged model...')
model.save_pretrained_merged('${MERGED_MODEL}', tokenizer)

print('Export complete!')
print(f'Merged model saved to: ${MERGED_MODEL}')
"

echo ""
echo "=========================================="
echo "Export complete!"
echo "Merged model saved to: $MERGED_MODEL"
echo "=========================================="
