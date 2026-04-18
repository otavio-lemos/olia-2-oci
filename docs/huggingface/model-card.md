---
library_name: mlx
license: mit
model_name: OCI Copilot Jr
language:
- pt-BR
tags:
- oracle-cloud-infrastructure
- oci
- fine-tuning
- lorawan
- apple-silicon
- mlx
---

# Model Card: otavio-lemos/oci-copilot-jr

## Overview

**OCI Copilot Jr** is a fine-tuned Large Language Model specialized in Oracle Cloud Infrastructure (OCI) operations. Built on Qwen 2.5 Coder 7B Instruct and fine-tuned using LoRA on Apple Silicon (M3 Pro).

| Attribute | Value |
|-----------|-------|
| **Base Model** | Qwen2.5-Coder-7B-Instruct-4bit |
| **Fine-tuning Method** | LoRA (Rank 32, Alpha 64) |
| **Framework** | MLX-Tune 0.4.18 |
| **Hardware** | Apple Silicon M3 Pro (18GB) |
| **Training Date** | April 2026 |

## Training Configuration

```python
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
  "bf16": true,
  "gradient_checkpointing": true
}
```

### Dataset

- **Training**: 9,897 examples (75%)
- **Validation**: 1,979 examples (15%)
- **Evaluation**: 1,320 examples (10%)
- **Total**: 13,196 examples
- **Language**: Brazilian Portuguese (PT-BR)
- **Categories**: 88 OCI domains

## Benchmark Results (Cycle 1)

Evaluation on 200 samples comparing base model vs fine-tuned:

| Metric | Base Model | Fine-Tuned | Delta |
|--------|------------|------------|-------|
| Technical Correctness | 3.40 | 3.40 | +0.00 |
| Depth | 2.60 | 2.60 | +0.00 |
| Structure | 4.00 | 4.44 | +0.45 |
| Hallucination | 3.58 | 4.68 | **+1.10** |
| Clarity | 3.50 | 3.37 | -0.13 |
| **Overall** | **3.42** | **3.70** | **+0.28** |

### Top Performance Gains by Category

| Rank | Category | Delta |
|------|----------|-------|
| 1 | Troubleshooting Connectivity | +0.66 |
| 2 | Troubleshooting Storage | +0.66 |
| 3 | FinOps Cost-Optimization | +0.60 |
| 4 | DevOps Secrets | +0.50 |
| 5 | Security Encryption | +0.50 |

## Usage

### MLX (Apple Silicon - Recommended)

```bash
mlx_lm.server --model mlx-community/Qwen2.5-Coder-7B-Instruct-4bit --adapter outputs/cycle-1/adapters
```

### Ollama

```bash
# Create Modelfile
cat > Modelfile << 'EOF'
FROM ./oci-copilot-jr-Q4_K_M.gguf
PARAMETER temperature 0.1
PARAMETER top_p 0.9
PARAMETER top_k 40
SYSTEM Você é um especialista em OCI (Oracle Cloud Infrastructure).
EOF

ollama create oci-copilot-jr -f Modelfile
```

### llama.cpp

```bash
llama-server -m oci-copilot-jr-Q4_K_M.gguf --port 8080
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

## Limitations

- **Language**: Optimized for Brazilian Portuguese (PT-BR)
- **Scope**: Operational guidance — OCI CLI commands, Terraform snippets, step-by-step procedures, risk validation, and troubleshooting runbooks
- **Training**: Single-cycle LoRA (may improve with more cycles)
- **Knowledge**: Based on OCI documentation up to April 2026

## Citation

```bibtex
@model{lemos_2026_oci_copilot_jr,
  author    = {Otavio Lemos},
  title     = {OCI Copilot Jr},
  year      = {2026},
  publisher = {HuggingFace},
  url       = {https://huggingface.co/otavio-lemos/oci-copilot-jr}
}
```

## License

MIT License - See [LICENSE](https://github.com/otavio-lemos/olia-2-oci/blob/main/LICENSE)

---

*Fine-tuned on Apple Silicon M3 Pro using MLX-Tune*