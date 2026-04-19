---
library_name: mlx
license: mit
model_name: OCI Copilot Jr
language:
- pt
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
  "train_data": "data/train.jsonl",
  "valid_data": "data/valid.jsonl",
  "output_dir": "outputs/cycle-1",
  "batch_size": 1,
  "learning_rate": 1e-4,
  "lora_rank": 32,
  "lora_alpha": 64,
  "lora_dropout": 0.05,
  "gradient_accumulation": 4,
  "num_layers": 16,
  "target_modules": ["q_proj","k_proj","v_proj","o_proj","gate_proj","up_proj","down_proj"],
  "iters": 2475,
  "max_seq_length": 1024,
  "val_batches": 5,
  "eval_steps": 247,
  "logging_steps": 1,
  "save_steps": 247,
  "warmup_steps": 247,
  "gradient_checkpointing": false,
  "lr_scheduler": "cosine",
  "weight_decay": 0.01,
  "seed": 42,
  "gradient_clip_norm": 1.0,
  "bf16": true
}
```

### Dataset

- **Training**: 9,897 examples (75%)
- **Validation**: 1,979 examples (15%)
- **Evaluation**: 1,320 examples (10%)
- **Total**: 13,196 examples
- **Language**: Portuguese (pt)
- **Categories**: 88 OCI domains

## Benchmark Results (Cycle 1)

Evaluation on 200 samples comparing base model vs fine-tuned:

| Metric | Base Model | Fine-Tuned | Delta |
|--------|-------------|------------|-------|
| Technical Correctness | 3.67 | 4.51 | **+0.84** |
| Depth | 3.11 | 3.93 | **+0.82** |
| Structure | 3.47 | 4.45 | **+0.98** |
| Hallucination | 3.23 | 3.95 | **+0.72** |
| Clarity | 3.07 | 3.06 | -0.01 |
| **Overall** | **3.31** | **3.98** | **+0.67** |

### Top Performance Gains by Category

| Rank | Category | Delta |
|------|----------------------|-------|
| 1 | Security Posture Management | +2.24 |
| 2 | Governance Tagging | +2.20 |
| 3 | Terraform State | +2.00 |
| 4 | Troubleshooting Functions | +1.86 |
| 5 | Security WAF | +1.84 |

### Benchmark Charts

![Comparison Chart](comparison_chart_20260418_220044.png)

![Category Chart](category_chart_20260418_220044.png)

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