#!/bin/bash
# training/export_adapter.sh
# Exporta adapter LoRA para modelo merged usando mlx-tune
#
# Uso:
#   bash training/export_adapter.sh              # exporta cycle-1 (padrão)
#   CYCLE=cycle-2 bash training/export_adapter.sh # exporta cycle-2
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

CYCLE=${CYCLE:-"cycle-1"}

# Load config from outputs dir only (reproducibility)
if [ -f "${PROJECT_DIR}/outputs/${CYCLE}/config/${CYCLE}.env" ]; then
    source "${PROJECT_DIR}/outputs/${CYCLE}/config/${CYCLE}.env"
    echo "[config] Loaded from: outputs/${CYCLE}/config/${CYCLE}.env"
else
    echo "ERROR: Config not found: outputs/${CYCLE}/config/${CYCLE}.env"
    exit 1
fi

BASE_MODEL=${BASE_MODEL:-${MODEL:-"mlx-community/Qwen2.5-Coder-7B-Instruct-4bit"}}
ADAPTER_DIR=${ADAPTER_DIR:-${OUTPUT_DIR:-"outputs/${CYCLE}"}}
MERGED_MODEL=${MERGED_MODEL:-"outputs/${CYCLE}/merged"}
TARGET_MODULES=${TARGET_MODULES:-"q_proj,k_proj,v_proj,o_proj,gate_proj,up_proj,down_proj"}

export ADAPTER_CONFIG_PATH="${ADAPTER_DIR}/adapters/adapter_config.json"

generate_adapter_config() {
    if [ -f "$ADAPTER_CONFIG_PATH" ]; then
        echo "[adapter_config] Already exists: $ADAPTER_CONFIG_PATH"
        echo "[adapter_config] Skipping generation (use existing file)"
        return 0
    fi

    echo "[adapter_config] Generating from ${CYCLE}.env..."

    local rank=${LORA_RANK:-32}
    local alpha=${LORA_ALPHA:-64}
    local dropout=${LORA_DROPOUT:-0.05}
    local num_layers=${NUM_LAYERS:-32}
    local scale=$(echo "scale=4; $alpha / $rank" | bc)

    local keys=""
    IFS=',' read -ra MODS <<< "$TARGET_MODULES"
    for mod in "${MODS[@]}"; do
        case "$mod" in
            q_proj) keys+="\"self_attn.q_proj\", " ;;
            k_proj) keys+="\"self_attn.k_proj\", " ;;
            v_proj) keys+="\"self_attn.v_proj\", " ;;
            o_proj) keys+="\"self_attn.o_proj\", " ;;
            gate_proj) keys+="\"mlp.gate_proj\", " ;;
            up_proj) keys+="\"mlp.up_proj\", " ;;
            down_proj) keys+="\"mlp.down_proj\", " ;;
            *) keys+="\"$mod\", " ;;
        esac
    done
    keys="${keys%, }"

    cat > "$ADAPTER_CONFIG_PATH" << EOF
{
  "fine_tune_type": "lora",
  "num_layers": ${num_layers},
  "lora_parameters": {
    "rank": ${rank},
    "scale": ${scale},
    "dropout": ${dropout},
    "keys": [${keys}]
  }
}
EOF

    echo "[adapter_config] Created: $ADAPTER_CONFIG_PATH"
}

generate_adapter_config

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
adapter_dir = '${ADAPTER_DIR}/adapters'
if not __import__('pathlib').Path(adapter_dir).exists():
    adapter_dir = '${ADAPTER_DIR}'
model.load_adapter(adapter_dir)

print('Saving merged model...')
model.save_pretrained_merged('${MERGED_MODEL}', tokenizer)

print('Export complete!')
print(f'Merged model saved to: ${MERGED_MODEL}')
"

# Copy tokenizer files from base model if missing
echo "[tokenizer] Ensuring complete tokenizer files..."
BASE_MODEL_DIR=$(python -c "from huggingface_hub import snapshot_download; print(snapshot_download('${BASE_MODEL}', local_files_only=True))")

TOKENIZER_FILES="added_tokens.json special_tokens_map.json tokenizer.json tokenizer_config.json"
for f in $TOKENIZER_FILES; do
    if [ ! -f "${MERGED_MODEL}/${f}" ] && [ -f "${BASE_MODEL_DIR}/${f}" ]; then
        cp "${BASE_MODEL_DIR}/${f}" "${MERGED_MODEL}/${f}"
        echo "[tokenizer] Copied: ${f}"
    fi
done

echo ""
echo "=========================================="
echo "Export complete!"
echo "Merged model saved to: $MERGED_MODEL"
echo "=========================================="
