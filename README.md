<!-- prettier-ignore -->
<div align="center">

# OCI Specialist LLM

Fine-tuning pipeline para um LLM especialista em OCI usando Apple Silicon, MLX e LoRA.

[![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.12-blue?style=flat-square&logo=python&logoColor=white)](https://www.python.org)
[![MLX](https://img.shields.io/badge/MLX-Apple%20Silicon-orange?style=flat-square)](https://mlx.ai)
[![Dataset](https://img.shields.io/badge/Dataset-710_examples-green?style=flat-square)](docs/taxonomy.md)

</div>

> **Idioma**: [PT-BR](#visao-geral) | [EN-US](#overview)

---

## Visão Geral {#visao-geral}

Este projeto constrói um LLM especializado em Oracle Cloud Infrastructure (OCI). O pipeline prioriza qualidade do dataset, baixo custo, validação rigorosa e segue regras de qualidade rigorosas para garantir respostas precisas e úteis.

O modelo foi projetado para ajudar com:
- Explicar serviços OCI, arquitetura e melhores práticas
- Solucionar problemas de cargas de trabalho OCI
- Guiar migração de AWS, Azure, GCP e on-premises para OCI
- Escrever configurações OCI Terraform
- Fornecer orientação de segurança e IAM

---

## Dataset

O dataset contém exemplos gerados via MASTER_PROMPT. Veja `docs/taxonomy.md` para todos os topics.

| Categoria | Topics |
|-----------|--------|
| OCI Core (compute, storage, networking, lb, database, container, serverless) | 20 |
| Security (iam-basics, policies, vault, encryption, cloud-guard, waf) | 9 |
| Migration (AWS/Azure/GCP/On-prem → OCI) | 14 |
| Terraform (provider, compute, storage, networking, lb, database, container, serverless, security, observability, devops, state) | 12 |
| Observability | 4 |
| Troubleshooting | 8 |
| DevOps | 4 |

> **Total: 71 topics × 10 exemplos = 710 exemplos**

### Formato dos Dados

Cada exemplo segue o formato OpenAI chat:

```json
{
  "messages": [
    {"role": "system", "content": "You are an OCI specialist..."},
    {"role": "user", "content": "How do I configure..."},
    {"role": "assistant", "content": "## Solution\n\n### Steps..."}
  ],
  "metadata": {"category": "compute/instances", "difficulty": "intermediate", "source": "generated"}
}
```

---

## Regras de Qualidade

Aplicamos regras de qualidade rigorosas para garantir precisão do dataset:

- **NUNCA** copiar documentação OCI verbatim
- **NUNCA** inventar serviços Oracle inexistentes
- **NUNCA** usar preços ou limites sem marcar como mutável
- **NUNCA** criar exemplos vagos como "usar melhores práticas"
- **NUNCA** gerar respostas arquiteturais sem passos, riscos ou justificativas

---

## Pré-requisitos

- **Apple Silicon Mac** (M1/M2/M3/M4) para treinamento MLX
- **Python 3.12** (recomendado via venv)

### Configurar Ambiente Virtual

```bash
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## Início Rápido

### Gerar Dados Curados

Use o **MASTER_PROMPT** com qualquer LLM externo (Gemini, GPT-4, Claude):

```bash
# Listar topics disponíveis
python scripts/generate_prompt.py --list

# Gerar prompt para um topic
python scripts/generate_prompt.py compute/instances
```

O prompt gerado deve ser enviado para um LLM, e o resultado salvo em `data/curated/[topic]-001.jsonl`.

### Pipeline Completo

```bash
# 1. Ativar ambiente virtual
source venv/bin/activate

# 2. Validar dataset
python3 scripts/validate_jsonl.py data/all_curated.jsonl --filter

# 3. Deduplicar
python3 scripts/dedupe_dataset.py data/all_curated.jsonl --remove

# 4. Criar splits (train/valid/eval)
python3 scripts/build_dataset_fixed.py -i data/all_curated.jsonl -o data/

# 5. Treinar modelo
source config/cycle-1.env && bash training/train_mlx.sh

# 6. Avaliar
python scripts/evaluate_model.py outputs/adapters data/eval.jsonl outputs/benchmarks
```

---

## Estrutura do Projeto

```
olia-2-oci/
├── AGENTS.md                      # Diretrizes do agente
├── README.md                      # Este arquivo
├── CONTRIBUTING.md                # Guia de contribuição
├── docs/                          # Documentação do projeto
│   ├── taxonomy.md               # Topics do dataset
│   ├── quality-rules.md          # Regras de qualidade
│   └── eval-rubric.md            # Critérios de avaliação
├── scripts/                      # Scripts de pipeline
│   ├── generate_prompt.py       # Gerar prompts para LLM
│   ├── validate_jsonl.py         # Validar formato JSONL
│   ├── dedupe_dataset.py         # Remover duplicatas
│   ├── build_dataset_fixed.py    # Criar splits train/valid/eval
│   └── evaluate_model.py         # Executar benchmarks
├── .agents/skills/               # Skills para geração de dados
│   └── generate-oci-dataset/
│       ├── MASTER_FORMAT.md
│       └── prompts/              # Prompts por topic
└── training/                     # Scripts de treinamento MLX
    ├── train_mlx.sh
    └── run_inference.sh
```

---

## Pipeline

1. **Documentação** → Escopo, taxonomia, regras de qualidade
2. **Geração de Dados** → MASTER_PROMPT + LLM externo → curated/
3. **Validação** → JSONL validator, deduplicação
4. **Construção do Dataset** → train (~75%), valid (~15%), eval (~10%)
5. **Treinamento** → Fine-tuning MLX LoRA no Apple Silicon
6. **Avaliação** → Benchmark comparing base vs fine-tuned

---

## Outputs

Após o treinamento:

- `outputs/adapters/` - Adaptadores LoRA treinados
- `outputs/benchmarks/` - Relatórios de avaliação
- `outputs/logs/` - Logs de treinamento

---

## Overview {#overview}

This project builds an LLM specialized in Oracle Cloud Infrastructure (OCI). The pipeline prioritizes dataset quality, low cost, rigorous validation, and follows strict quality rules to ensure accurate and helpful responses.

The model is designed to assist with:
- Explaining OCI services, architecture, and best practices
- Troubleshooting OCI workloads
- Guiding migration from AWS, Azure, GCP, and on-premises to OCI
- Writing OCI Terraform configurations
- Providing security and IAM guidance

---

## Dataset

The dataset contains examples generated via MASTER_PROMPT. See `docs/taxonomy.md` for all topics.

| Category | Topics |
|----------|--------|
| OCI Core (compute, storage, networking, lb, database, container, serverless) | 20 |
| Security (iam-basics, policies, vault, encryption, cloud-guard, waf) | 9 |
| Migration (AWS/Azure/GCP/On-prem → OCI) | 14 |
| Terraform (provider, compute, storage, networking, lb, database, container, serverless, security, observability, devops, state) | 12 |
| Observability | 4 |
| Troubleshooting | 8 |
| DevOps | 4 |

> **Total: 71 topics × 10 examples = 710 examples**

### Data Format

Each example follows the OpenAI chat format:

```json
{
  "messages": [
    {"role": "system", "content": "You are an OCI specialist..."},
    {"role": "user", "content": "How do I configure..."},
    {"role": "assistant", "content": "## Solution\n\n### Steps..."}
  ],
  "metadata": {"category": "compute/instances", "difficulty": "intermediate", "source": "generated"}
}
```

---

## Quality Rules

We enforce strict quality rules to ensure dataset accuracy:

- **NEVER** copy OCI documentation verbatim
- **NEVER** invent non-existent Oracle services
- **NEVER** use prices or limits without marking as mutable
- **NEVER** create vague examples like "use best practices"
- **NEVER** generate architectural responses without steps, risks, or justifications

---

## Prerequisites

- **Apple Silicon Mac** (M1/M2/M3/M4) for MLX training
- **Python 3.12** (recommended via venv)

### Setup Virtual Environment

```bash
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## Quick Start

### Generate Curated Data

Use **MASTER_PROMPT** with any external LLM (Gemini, GPT-4, Claude):

```bash
# List available topics
python scripts/generate_prompt.py --list

# Generate prompt for a topic
python scripts/generate_prompt.py compute/instances
```

The generated prompt should be sent to an LLM, and the result saved to `data/curated/[topic]-001.jsonl`.

### Complete Pipeline

```bash
# 1. Activate virtual environment
source venv/bin/activate

# 2. Validate dataset
python3 scripts/validate_jsonl.py data/all_curated.jsonl --filter

# 3. Deduplicate
python3 scripts/dedupe_dataset.py data/all_curated.jsonl --remove

# 4. Create splits (train/valid/eval)
python3 scripts/build_dataset_fixed.py -i data/all_curated.jsonl -o data/

# 5. Train model
source config/cycle-1.env && bash training/train_mlx.sh

# 6. Evaluate
python scripts/evaluate_model.py outputs/adapters data/eval.jsonl outputs/benchmarks
```

---

## Project Structure

```
olia-2-oci/
├── AGENTS.md                      # Agent guidelines
├── README.md                      # This file
├── CONTRIBUTING.md                # Contributing guide
├── docs/                          # Project documentation
│   ├── taxonomy.md               # Dataset topics
│   ├── quality-rules.md          # Quality rules
│   └── eval-rubric.md            # Evaluation criteria
├── scripts/                      # Pipeline scripts
│   ├── generate_prompt.py       # Generate prompts for LLM
│   ├── validate_jsonl.py         # Validate JSONL format
│   ├── dedupe_dataset.py         # Remove duplicates
│   ├── build_dataset_fixed.py    # Create train/valid/eval splits
│   └── evaluate_model.py         # Run benchmarks
├── .agents/skills/               # Data generation skills
│   └── generate-oci-dataset/
│       ├── MASTER_FORMAT.md
│       └── prompts/              # Prompts per topic
└── training/                     # MLX training scripts
    ├── train_mlx.sh
    └── run_inference.sh
```

---

## Pipeline

1. **Documentation** → Scope, taxonomy, quality rules
2. **Data Generation** → MASTER_PROMPT + external LLM → curated/
3. **Validation** → JSONL validator, deduplication
4. **Dataset Building** → train (~75%), valid (~15%), eval (~10%)
5. **Training** → MLX LoRA fine-tuning on Apple Silicon
6. **Evaluation** → Benchmark comparing base vs fine-tuned

---

## Outputs

After training:

- `outputs/adapters/` - Trained LoRA adapters
- `outputs/benchmarks/` - Evaluation reports
- `outputs/logs/` - Training logs