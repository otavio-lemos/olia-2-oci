# OCI Copilot Jr — Publicações

## HuggingFace Repositories

| Repositório | URL | Descrição |
|-------------|-----|----------|
| **Dataset** | https://huggingface.co/datasets/otavio-lemos/oci-copilot-jr-dataset | 13,196 exemplos (PT-BR) |
| **Modelo (LoRA)** | https://huggingface.co/otavio-lemos/oci-copilot-jr | Qwen2.5-Coder-7B + LoRA adapters |

## Como Usar

###Dataset (Python)
```python
from datasets import load_dataset
ds = load_dataset("otavio-lemos/oci-copilot-jr-dataset")
```

### Modelo (MLX)
```bash
mlx_lm.server --model mlx-community/Qwen2.5-Coder-7B-Instruct-4bit --adapter outputs/cycle-1/adapters
```

### Modelo (Ollama)
```bash
# Baixe o GGUF e crie Modelfile
ollama create oci-copilot-jr -f Modelfile
```