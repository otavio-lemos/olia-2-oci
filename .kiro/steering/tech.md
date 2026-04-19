# Tech — OCI Specialist LLM

## Stack Principal

| Componente | Tecnologia |
|-----------|----------|
| **LLM Base** | Qwen 2.5 Coder 7B Instruct (4-bit) |
| **Fine-tuning** | MLX-Tune (Apple Silicon) |
| **Loop** | LoRA (rank 32, BF16) |
| **Orquestração** | LangGraph + LangChain |
| **UI** | Chainlit |
| **API Backend** | FastAPI |
| **RAG Dense** | FAISS |
| **RAG Sparse** | Rank-BM25 |
| **Embeddings** | Sentence-Transformers |
| **Linguagem** | Python 3.12 |

## Decisões de Arquitetura

- **Inferência Local**: Sem dependência de APIs externas (privacidade, custo)
- **RAG Híbrido**: Combinação de busca semântica + lexical para melhor recall
- **Pipeline Offline**: Índices RAG gerados offline para economia de RAM
- **HITL (Human-in-the-loop)**: Interface Chainlit com aprovação humana para comandos destrutivos

## Convenções de Código

- **Imports**: Relative imports dentro de módulos (`from rag.tools import ...`)
- **Configuração**: Arquivos YAML em `config/`
- **Outputs**: Timestamps em nomes de arquivos (`cycle-1/benchmarks/*.png`)
- **Testes**: pytest em `tests/`

## Estrutura de Diretórios

```
scripts/      # Pipeline de geração, treino, avaliação
rag/          # Componentes RAG e UI
training/     # Treinamento MLX
config/       # Configurações YAML
outputs/      # Modelos, adapters, benchmarks
data/         # Datasets curados
tests/        # Testes pytest
```