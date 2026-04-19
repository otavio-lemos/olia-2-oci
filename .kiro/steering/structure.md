# Structure — OCI Specialist LLM

## Organização do Projeto

O projeto segue uma estrutura modular organizada por responsabilidade:

```
ologia-2-oci/
├── scripts/           # Pipeline de dados, treino, avaliação
│   ├── generate_*.py   # Geração de dataset
│   ├── clean_*.py    # Limpeza e desduplicação
│   ├── merge_export.py # Merge LoRA + export GGUF
│   └── unified_evaluation*.py
├── rag/              # Sistema RAG + Interface
│   ├── api.py       # FastAPI backend
│   ├── orchestrator.py  # LangGraph agents
│   ├── app_chainlit.py # Chainlit UI
│   ├── dense_retriever.py   # FAISS
│   ├── sparse_retriever.py  # BM25
│   └── hybrid_retriever.py
├── training/         # Treinamento
│   └── train_mlx_tune.py
├── config/          # Configurações
│   ├── llm_provider*.yaml
│   └── oci-copilot-agents.yaml
├── outputs/         # Artefatos gerados
│   └── cycle-1/
│       ├── adapters/     # LoRA adapters
│       ├── safetensors/ # Modelos exportados
│       └── gguf/      # Versões quantizadas
├── data/           # Datasets curados
│   └── curated/*.jsonl
└── tests/          # Testes pytest
```

## Padrões de Import

- Módulos rag: `from rag.tools import ...`
- Módulos scripts: `from scripts.generate_v7_combined import ...` (quando usado como lib)

## Padrões de Nomenclatura

- **Arquivos de dados**: `{categoria}.jsonl` (ex: `troubleshooting-compute.jsonl`)
- **Outputs de ciclo**: `cycle-{n}/`
- **Scripts de avaliação**: `unified_evaluation_v{n}.py`

## Pipeline de Dados

1. **Geração**: `generate_v7_combined.py` → 88 categorias × 150 exemplos
2. **Preparação**: `prepare_data.sh` → valida, limpa, desduplica, split (75/15/10%)
3. **Treinamento**: `train_mlx_tune.py` → LoRA adapters
4. **Avaliação**: `unified_evaluation_v2.py` → métricas automáticas