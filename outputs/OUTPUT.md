# Outputs

## Hugging Face Integration

### Model Repository
- **URL**: https://huggingface.co/otavio-lemos/oci-copilot-jr
- **Files**:
  - `model-Q4_K_M.gguf` - Quantized Q4 version (~4.6GB)
  - `model-fp16.gguf` - FP16 version (~15GB)
  - `eval_results.json` - Evaluation results

### Dataset Repository
- **URL**: https://huggingface.co/datasets/otavio-lemos/oci-copilot-jr-dataset
- **Files**:
  - `train.jsonl` - 9,897 examples
  - `valid.jsonl` - 1,979 examples
  - `eval.jsonl` - 1,320 examples

---

## Training Results (Cycle 1)

| Metric | Base Model | Fine-Tuned | Delta |
|--------|-------------|------------|-------|
| technical_correctness | 3.67 | 4.51 | +0.84 |
| depth | 3.11 | 3.93 | +0.82 |
| structure | 3.47 | 4.45 | +0.98 |
| hallucination | 3.23 | 3.95 | +0.72 |
| clarity | 3.07 | 3.06 | -0.01 |
| **Overall** | **3.31** | **3.98** | **+0.67** |

### External Judge (Llama 3.1 8B)

| Metric | Base Model | Fine-Tuned | Delta |
|--------|-------------|------------|-------|
| **Overall** | **4.01** | **4.40** | **+0.40** |

### Top Improvements
1. **governance/tagging**: +2.20
2. **security/posture-management**: +2.24
3. **terraform/state**: +2.00

---

## Configuration

| Parameter | Value |
|-----------|-------|
| MODEL | mlx-community/Qwen2.5-Coder-7B-Instruct-4bit |
| Iters | 2475 |
| Batch | 1 |
| Grad Accum | 4 |
| Num Layers | 16 |
| Max Seq | 1024 |
| BF16 | true |
| LoRA Rank | 32 |
| Learning Rate | 1e-4 |