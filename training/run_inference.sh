#!/bin/bash
set -e

BASE_MODEL=${BASE_MODEL:-"mlx-community/Llama-3.2-3B-Instruct-4bit"}
ADAPTER_DIR=${ADAPTER_DIR:-"outputs/adapters"}
MAX_TOKENS=${MAX_TOKENS:-512}
TEMPERATURE=${TEMPERATURE:-0.7}

SYSTEM_PROMPT="You are an Oracle Cloud Infrastructure (OCI) specialist. You provide accurate, practical guidance on OCI services, architecture, migration, and troubleshooting."

EXAMPLE_PROMPTS=(
    "How do I create a VCN with private subnets in OCI?"
    "What's the equivalent of AWS S3 in OCI and how do I migrate?"
    "How do I configure IAM policies for cross-compartment access?"
    "What's the process to migrate an EC2 instance to OCI Compute?"
)

echo "=========================================="
echo "OCI Specialist LLM - Inference Test"
echo "=========================================="
echo "Base Model: $BASE_MODEL"
echo "Adapter: $ADAPTER_DIR"
echo "=========================================="

for prompt in "${EXAMPLE_PROMPTS[@]}"; do
    echo ""
    echo "=========================================="
    echo "Prompt: $prompt"
    echo "=========================================="
    
    if [ -d "$ADAPTER_DIR" ]; then
        python -m mlx_lm.generate \
            --model "$BASE_MODEL" \
            --adapter-path "$ADAPTER_DIR" \
            --prompt "$SYSTEM_PROMPT\n\nUser: $prompt\nAssistant:" \
            --max-tokens "$MAX_TOKENS" \
            --temp "$TEMPERATURE"
    else
        echo "No adapter found, using base model"
        python -m mlx_lm.generate \
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
