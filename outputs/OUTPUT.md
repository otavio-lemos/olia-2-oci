# Outputs

## Pipeline de Treinamento

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Data Generation │ -> │   Training      │ -> │   Merge & Export │ -> │   Evaluation    │
│  generate_diverse │    │  mlx-tune LoRA  │    │  GGUF (Q4/FP16) │    │  unified_eval   │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
        │                      │                     │                      │
        v                      v                     v                      v
  data/curated/          outputs/cycle-1/      outputs/cycle-1/        outputs/cycle-1/
  (JSONL samples)       adapters/             gguf/                    benchmarks/
                        (LoRA weights)        (merged model)
```

## Estrutura de Diretórios

```
outputs/
├── cycle-1/
│   ├── adapters/          # LoRA adapters fine-tuned
│   ├── merged/            # Modelo mergeado (BF16)
│   ├── gguf/              # Modelos exportados (Q4/FP16)
│   ├── train.jsonl       # Dados de treino
│   ├── valid.jsonl        # Dados de validação
│   └── benchmarks/        # Resultados da avaliação
└── OUTPUT.md              # Este arquivo
```

## Modelos Disponíveis

Os modelos treinados e exportados estão disponíveis no Hugging Face Hub.