# Model Card: otavio-lemos/oci-copilot-jr

## Overview

OCI Copilot Jr is a fine-tuned Large Language Model specialized in Oracle Cloud Infrastructure (OCI) operations. Built on Qwen 2.5 Coder 7B Instruct and fine-tuned using LoRA on Apple Silicon (M3 Pro).

| Attribute | Value |
| --- | --- |
| Base Model | Qwen2.5-Coder-7B-Instruct-4bit |
| Fine-tuning Method | LoRA (Rank 32, Alpha 64) |
| Framework | MLX-Tune 0.4.18 |
| Hardware | Apple Silicon M3 Pro (18GB) |
| Training Date | April 2026 |

## Training Configuration

```json
{
  "model": "mlx-community/Qwen2.5-Coder-7B-Instruct-4bit",
  "lora_rank": 32,
  "lora_alpha": 64,
  "lora_dropout": 0.05,
  "learning_rate": 1e-4,
  "batch_size": 1,
  "gradient_accumulation": 4,
  "num_layers": 16,
  "max_seq_length": 1024,
  "iters": 2475,
  "bf16": true
}
```

### Dataset

- Training: 9,897 examples (75%)
- Validation: 1,979 examples (15%)
- Evaluation: 1,320 examples (10%)
- Total: 13,196 examples
- Language: Portuguese (pt)
- Categories: 88 OCI domains

## Benchmark Results (Cycle 1 - 200 Samples)

| Metric | Base Model | Fine-Tuned | Delta |
| --- | --- | --- | --- |
| technical_correctness | 3.67 | 4.51 | +0.84 |
| depth | 3.11 | 3.93 | +0.82 |
| structure | 3.47 | 4.45 | +0.98 |
| hallucination | 3.23 | 3.95 | +0.72 |
| clarity | 3.07 | 3.06 | -0.01 |
| **Overall** | **3.31** | **3.98** | **+0.67** |

### External Judge (Llama 3.1 8B)

| Metric | Base Model | Fine-Tuned | Delta |
| --- | --- | --- | --- |
| **Overall** | **4.01** | **4.40** | **+0.40** |

### Top Performance Gains

| Rank | Category | Delta |
| --- | --- | --- |
| 1 | governance/tagging | +2.20 |
| 2 | security/posture-management | +2.24 |
| 3 | terraform/state | +2.00 |
| 4 | security/waf | +1.84 |
| 5 | troubleshooting/functions | +1.86 |

## Files

- `model-Q4_K_M.gguf` - Quantized Q4 version (4.6GB)
- `model-fp16.gguf` - FP16 version (~15GB)
- `safetensors/bf16/` - BF16 safetensors
- `safetensors-q4/` - Q4 safetensors

## Usage

### MLX (Apple Silicon)
```bash
mlx_lm.server --model mlx-community/Qwen2.5-Coder-7B-Instruct-4bit --adapter outputs/cycle-1/adapters
```

### llama.cpp
```bash
llama-server -m model-Q4_K_M.gguf --port 8080
```

## System Prompt

```
Você é um arquiteto e especialista experiente em OCI. Forneça orientações técnicas, profundas e definitivas com:
- Comandos OCI CLI reais
- Trechos de código Terraform
- Passos detalhados e justificação
- Restrições do cenário observadas
- Checklist de pré-requisitos
```

## License

MIT License