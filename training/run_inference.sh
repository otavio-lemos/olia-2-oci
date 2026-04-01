#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
VENV_DIR="${PROJECT_DIR}/venv"

source "${VENV_DIR}/bin/activate"

BASE_MODEL=${BASE_MODEL:-"mlx-community/Llama-3.2-3B-Instruct-4bit"}
ADAPTER_DIR=${ADAPTER_DIR:-"outputs/cycle-2"}
MERGED_MODEL=${MERGED_MODEL:-"outputs/merged-model"}
MAX_TOKENS=${MAX_TOKENS:-512}
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
        mlx_lm.generate \
            --model "$MERGED_MODEL" \
            --prompt "$SYSTEM_PROMPT\n\nUser: $prompt\nAssistant:" \
            --max-tokens "$MAX_TOKENS" \
            --temp "$TEMPERATURE"
    elif [ -f "$ADAPTER_DIR/adapters.safetensors" ]; then
        echo "Using LoRA adapter..."
        mlx_lm.generate \
            --model "$BASE_MODEL" \
            --adapter-path "$ADAPTER_DIR" \
            --prompt "$SYSTEM_PROMPT\n\nUser: $prompt\nAssistant:" \
            --max-tokens "$MAX_TOKENS" \
            --temp "$TEMPERATURE"
    else
        echo "No adapter found, using base model"
        mlx_lm.generate \
            --model "$BASE_MODEL" \
            --prompt "$SYSTEM_PROMPT\n\nUser: $prompt\nAssistant:" \
            --max-tokens "$MAX_TOKENS" \
            --temp "$TEMPERATURE"
    fi
done

echo ""
echo "=========================================="
echo "Inference complete!"
echo "=========================================="
