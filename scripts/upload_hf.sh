#!/bin/bash

# HuggingFace Upload Script for OCI Copilot Jr
# Dataset: otavio-lemos/oci-copilot-jr-dataset
# Model: otavio-lemos/oci-copilot-jr

set -e

HF_USERNAME="otavio-lemos"
DATASET_NAME="oci-copilot-jr-dataset"
MODEL_NAME="oci-copilot-jr"

echo "========================================"
echo "OCI Copilot Jr - HF Upload Script"
echo "========================================"

# Check if logged in to HF
echo "[1/5] Verifying HuggingFace login..."
huggingface-cli whoami || { echo "ERROR: Not logged in. Run 'huggingface-cli login' first."; exit 1; }

# Upload Dataset
echo "[2/5] Uploading dataset: ${HF_USERNAME}/${DATASET_NAME}"
echo "  - data/train.jsonl"
echo "  - data/valid.jsonl"
echo "  - data/eval.jsonl"
echo "  - docs/huggingface/dataset-card.md"

huggingface-cli upload \
    ${HF_USERNAME}/${DATASET_NAME} \
    data/train.jsonl \
    data/valid.jsonl \
    data/eval.jsonl \
    docs/huggingface/dataset-card.md \
    --repo-type dataset \
    --commit-message "Initial upload: OCI Copilot Jr Dataset (13,196 examples)"

echo "✓ Dataset uploaded successfully!"

# Check if adapters exist (model training complete)
if [ -d "outputs/cycle-1/adapters" ]; then
    echo "[3/5] Uploading LoRA adapters: ${HF_USERNAME}/${MODEL_NAME}"
    huggingface-cli upload \
        ${HF_USERNAME}/${MODEL_NAME} \
        outputs/cycle-1/adapters/ \
        --repo-type model \
        --commit-message "LoRA adapters from Cycle 1 training"
    echo "✓ Adapters uploaded successfully!"
else
    echo "[3/5] Skipping adapters (not found - training not complete)"
fi

# Check if GGUF exists
if [ -d "outputs/cycle-1/gguf" ]; then
    echo "[4/5] Uploading quantized model (GGUF): ${HF_USERNAME}/${MODEL_NAME}"
    huggingface-cli upload \
        ${HF_USERNAME}/${MODEL_NAME} \
        outputs/cycle-1/gguf/ \
        --repo-type model \
        --commit-message "Quantized GGUF model (Q4_K_M)"
    echo "✓ GGUF model uploaded successfully!"
else
    echo "[4/5] Skipping GGUF (not found)"
fi

# Upload Model Card
echo "[5/5] Updating model card: ${HF_USERNAME}/${MODEL_NAME}"
huggingface-cli upload \
    ${HF_USERNAME}/${MODEL_NAME} \
    docs/huggingface/model-card.md \
    --repo-type model \
    --commit-message "Model card with benchmark results"

echo "✓ Model card updated!"

echo ""
echo "========================================"
echo "Upload complete!"
echo "========================================"
echo "Dataset: https://huggingface.co/datasets/${HF_USERNAME}/${DATASET_NAME}"
echo "Model:   https://huggingface.co/${HF_USERNAME}/${MODEL_NAME}"
echo "========================================"