---
library_name: transformers
license: mit
model_name: OCI Copilot Jr GGUF
language:
- pt
tags:
- oracle-cloud-infrastructure
- oci
- fine-tuning
- gguf
- quantization
- llama
ggufFilePaths:
- oci-copilot-jr-Q4_K_M.gguf
- oci-copilot-jr.fp16.gguf
base_model: otavio-lemos/oci-copilot-jr-safetensors
base_model_relation: quantized
---

# Model Card: otavio-lemos/oci-copilot-jr-gguf

## Overview

**OCI Copilot Jr GGUF** is a GGUF-quantized version of OCI Copilot Jr, specialized in Oracle Cloud Infrastructure (OCI) operations. Built on Qwen 2.5 Coder 7B Instruct and quantized using llama.cpp.

| Attribute | Value |
|-----------|-------|
| **Base Model** | Qwen2.5-Coder-7B-Instruct-4bit |
| **Quantization** | FP16, Q4_K_M |
| **Framework** | llama.cpp |
| **Conversion Date** | April 2026 |

## Variants

| File | Type | Size | Use Case |
|------|------|------|---------|
| oci-copilot-jr.fp16.gguf | FP16 | ~15 GB | High quality, GPU required |
| oci-copilot-jr-Q4_K_M.gguf | Q4_K_M | ~4.7 GB | CPU inference, low RAM |

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
|--------|------------|------------|-------|
| Technical Correctness | 3.67 | 4.51 | **+0.84** |
| Depth | 3.11 | 3.93 | **+0.82** |
| Structure | 3.47 | 4.45 | **+0.98** |
| Hallucination | 3.23 | 3.95 | **+0.72** |
| Clarity | 3.07 | 3.06 | -0.01 |
| **Overall** | **3.31** | **3.98** | **+0.67** |

### Top Performance Gains by Category

| Rank | Category | Delta |
|------|----------|-------|
| 1 | Security Posture Management | +2.24 |
| 2 | Governance Tagging | +2.20 |
| 3 | Terraform State | +2.00 |
| 4 | Troubleshooting Connectivity | +0.66 |
| 5 | Troubleshooting Storage | +0.66 |

### Benchmark Charts

![Comparison Chart](benchmarks/comparison_chart_20260418_220044.png)

![Category Chart](benchmarks/category_chart_20260418_220044.png)

## Usage

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
ollama run oci-copilot-jr
```

### llama.cpp

```bash
# FP16 (high quality)
llama-server -m oci-copilot-jr.fp16.gguf --port 8080 -c 4096

# Q4_K_M (recommended, low RAM)
llama-server -m oci-copilot-jr-Q4_K_M.gguf --port 8080 -c 4096
```

### LM Studio

Search for "oci-copilot-jr" in LM Studio and download the variant you need.

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
@model{lemos_2026_oci_copilot_jr_gguf,
  author    = {Otavio Lemos},
  title     = {OCI Copilot Jr GGUF},
  year      = {2026},
  publisher = {HuggingFace},
  url       = {https://huggingface.co/otavio-lemos/oci-copilot-jr-gguf}
}
```

## License

MIT License - See [LICENSE](https://github.com/otavio-lemos/olia-2-oci/blob/main/LICENSE)

---

*Fine-tuned on Apple Silicon M3 Pro using MLX-Tune, quantized with llama.cpp*