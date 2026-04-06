#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
VENV_DIR="${PROJECT_DIR}/venv"

source "${VENV_DIR}/bin/activate"

CYCLE=${CYCLE:-"cycle-3"}
source "${PROJECT_DIR}/config/${CYCLE}.env"

BASE_MODEL=${BASE_MODEL:-${MODEL:-"mlx-community/Meta-Llama-3.1-8B-Instruct-4bit"}}
ADAPTER_DIR=${ADAPTER_DIR:-${OUTPUT_DIR:-"outputs/${CYCLE}"}}
MERGED_MODEL=${MERGED_MODEL:-"outputs/merged-model"}
MAX_TOKENS=${MAX_TOKENS:-2048}
TEMPERATURE=${TEMPERATURE:-0.7}

SYSTEM_PROMPT="Você é um arquiteto especialista em Oracle Cloud Infrastructure (OCI). Forneça respostas técnicas precisas, específicas e práticas em português (Brasil)."

EXAMPLE_PROMPTS=(
    "Como criar uma VCN com subnets privadas no OCI?"
    "Qual o equivalente do AWS S3 no OCI e como migrar?"
    "Como configurar políticas IAM para acesso cross-compartment?"
    "Qual o processo para migrar uma instância EC2 para OCI Compute?"
)

echo "=========================================="
echo "OCI Specialist LLM - Inference Test"
echo "=========================================="
echo "Base Model: $BASE_MODEL"
echo "Adapter: $ADAPTER_DIR"
echo "Merged Model: $MERGED_MODEL"
echo "=========================================="

for prompt in "${EXAMPLE_PROMPTS[@]}"; do
    echo ""
    echo "=========================================="
    echo "Prompt: $prompt"
    echo "=========================================="

    if [ -d "$MERGED_MODEL" ]; then
        echo "Using merged model..."
        python -m mlx_lm.generate \
            --model "$MERGED_MODEL" \
            --prompt "$prompt" \
            --max-tokens "$MAX_TOKENS" \
            --temperature "$TEMPERATURE" \
            --system-prompt "$SYSTEM_PROMPT"
    elif [ -d "$ADAPTER_DIR" ] && [ -f "$ADAPTER_DIR/adapters.safetensors" ]; then
        echo "Using LoRA adapter..."
        python -m mlx_lm.generate \
            --model "$BASE_MODEL" \
            --adapter-path "$ADAPTER_DIR" \
            --prompt "$prompt" \
            --max-tokens "$MAX_TOKENS" \
            --temperature "$TEMPERATURE" \
            --system-prompt "$SYSTEM_PROMPT"
    else
        echo "No adapter found, using base model"
        python -m mlx_lm.generate \
            --model "$BASE_MODEL" \
            --prompt "$prompt" \
            --max-tokens "$MAX_TOKENS" \
            --temperature "$TEMPERATURE" \
            --system-prompt "$SYSTEM_PROMPT"
    fi
done

echo ""
echo "=========================================="
echo "Inference complete!"
echo "=========================================="
