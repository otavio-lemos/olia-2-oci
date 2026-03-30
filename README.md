<!-- prettier-ignore -->
<div align="center">

# OCI Specialist LLM

Pipeline de fine-tuning para um LLM especialista em OCI usando Apple Silicon, MLX e LoRA.

[![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.12-blue?style=flat-square&logo=python&logoColor=white)](https://www.python.org)
[![MLX](https://img.shields.io/badge/MLX-Apple%20Silicon-orange?style=flat-square)](https://mlx.ai)

</div>

> **Idioma / Language**: PT-BR | EN-US (padrão: PT-BR)

---

## Visão Geral

Este projeto constrói um LLM especializado em Oracle Cloud Infrastructure (OCI). O pipeline prioriza qualidade do dataset, baixo custo, validação rigorosa e segue regras de qualidade rigorosas para garantir respostas precisas e úteis.

> **Nota**: Esta é uma implementação de referência para construir um modelo especialista em OCI. O dataset atual é pequeno (~500 exemplos) para manter o treinamento rápido e barato no Apple Silicon. Para uso em produção, você deve escalar o dataset para 10.000+ exemplos seguindo as mesmas regras de qualidade e estrutura de taxonomia.

O modelo foi diseñado para ajudar com:
- Explicar serviços OCI, arquitetura e melhores práticas
- Solucionar problemas de cargas de trabalho OCI
- Guiar migração de AWS, Azure, GCP e on-premises para OCI
- Escrever configurações OCI Terraform
- Fornecer orientação de segurança e IAM

## Arquitetura

```
data/curated/      → exemplos revisados (gerados via MASTER_PROMPT)
data/TEMPLATE.jsonl → exemplo do formato correto
```

## Dataset

O dataset contém exemplos gerados via MASTER_PROMPT. Veja `docs/taxonomy.md` para todos os topics (71 topics disponíveis).

| Categoria | Exemplos |
|-----------|----------|
| OCI Core (compute, storage, networking, lb, database, container, serverless) | 20 topics |
| Security (iam-basics, policies, dynamic-groups, federation, vault, encryption, cloud-guard, waf) | 9 topics |
| Migration (AWS/Azure/GCP/On-prem → OCI) | 14 topics |
| Terraform (provider, compute, storage, networking, lb, database, container, serverless, security, observability, devops, state) | 12 topics |
| Observability (logging, monitoring, stack-monitoring, apm) | 4 topics |
| Troubleshooting (connectivity, performance, authentication, database, compute, storage, oke, functions) | 8 topics |
| DevOps (ci-cd, resource-manager, artifacts, secrets) | 4 topics |

**Total: 71 topics × 10 exemplos = 710 exemplos**

### Formato dos Dados

Cada exemplo segue o formato OpenAI chat:

```json
{
  "messages": [
    {"role": "system", "content": "You are an OCI specialist..."},
    {"role": "user", "content": "How do I configure..."},
    {"role": "assistant", "content": "## Solution\n\n### Steps..."}
  ],
  "metadata": {
    "category": "compute/instances",
    "difficulty": "intermediate",
    "source": "generated"
  }
}
```

## Regras de Qualidade

Aplicamos regras de qualidade rigorosas para garantir precisão do dataset:

- **NUNCA** copiar documentação OCI verbatim
- **NUNCA** inventar serviços Oracle inexistentes
- **NUNCA** usar preços ou limites sem marcar como mutável
- **NUNCA** criar exemplos vagos como "usar melhores práticas"
- **NUNCA** gerar respostas arquiteturais sem passos, riscos ou justificativas

## Pré-requisitos

- **Apple Silicon Mac** (M1/M2/M3/M4) para treinamento MLX
- **Python 3.12** (recomendado via venv)

### Configurar Ambiente Virtual

```bash
# Criar venv com Python 3.12
python3.12 -m venv venv

# Ativar
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

## Início Rápido

### 0. Gerar Dados Curados

Use o **MASTER_PROMPT** com qualquer LLM externo (Gemini, GPT-4, Claude, Perplexity):

```
.agents/skills/generate-oci-dataset/MASTER_FORMAT.md
├── docs/taxonomy.md              ← escolher topic
├── docs/quality-rules.md         ← regras de qualidade
└── .agents/skills/generate-oci-dataset/prompts/
    └── [topic].md                ← topic específico
```

#### Passo a Passo

1. **Escolha um topic** - veja `docs/taxonomy.md`

2. **Liste os topics disponíveis**:
   ```bash
   python scripts/generate_prompt.py --list
   ```

3. **Gere o prompt para um topic**:
   ```bash
   python scripts/generate_prompt.py compute/instances
   ```

4. **Envie para um LLM** (Gemini, GPT-4, Claude)

5. **Salve o resultado** em `data/curated/[topic]-001.jsonl`

#### Estrutura de Arquivos

```
data/
├── curated/                      # Exemplos gerados
│   └── compute/instances-001.jsonl
└── TEMPLATE.jsonl               # Exemplo do formato correto
```

#### Template (formato esperado)

```json
{"messages": [{"role": "system", "content": "You are an OCI specialist..."}, {"role": "user", "content": "Your question here"}, {"role": "assistant", "content": "Answer with steps, risks, alternatives, [MUTABLE] for prices, [CHECK DOCS] for limits"}], "metadata": {"category": "compute/instances", "difficulty": "beginner|intermediate|advanced", "source": "generated"}}
```

---

### 1. Ativar Ambiente Virtual

```bash
source venv/bin/activate
```

### 2. Concatenar todos os arquivos curados

```bash
# Cria um arquivo único com todos os exemplos de curated/
cat data/curated/*.jsonl > data/all_curated.jsonl
```

### 3. Validar Dataset

```bash
python3 scripts/validate_jsonl.py data/all_curated.jsonl --filter
mv data/all_curated_valid.jsonl data/all_curated.jsonl
```

### 4. Deduplicar

```bash
python3 scripts/dedupe_dataset.py data/all_curated.jsonl --remove
```

### 5. Criar Divisões do Dataset

O script lê `data/all_curated.jsonl` e gera:

- `data/train.jsonl` (~75%)
- `data/valid.jsonl` (~15%)
- `data/eval.jsonl` (~10%)

```bash
python3 scripts/build_dataset_fixed.py -i data/all_curated.jsonl -o data/
```

### 6. Treinar Modelo

```bash
source config/cycle-1.env && bash training/train_mlx.sh
```

Ou com parâmetros personalizados:
```bash
MODEL="mlx-community/Llama-3.2-3B-Instruct-4bit" EPOCHS=2 bash training/train_mlx.sh
```

> **Nota:** O script de treinamento define `KMP_DUPLICATE_LIB_OK=TRUE` para lidar com conflitos de OpenMP no macOS.

### 7. Executar Inferência

```bash
bash training/run_inference.sh
```

### 8. Avaliar

```bash
python scripts/evaluate_model.py outputs/adapters data/eval.jsonl outputs/benchmarks
```

## Rubrica de Avaliação

A avaliação verifica respostas em:

| Critério | Peso |
|----------|------|
| Correção Técnica | 1-5 |
| Profundidade do Conhecimento | 1-5 |
| Clareza Estrutural | 1-5 |
| Alucinação | 1-5 |
| Clareza | 1-5 |
| Comparação Multi-Cloud | 1-5 |

**Mínimo para passar**: 3.5 média geral.

## Estrutura do Projeto

```
olia-2-oci/
├── AGENTS.md                    # Diretrizes do agente
├── README.md                    # Este arquivo
├── CONTRIBUTING.md              # Guia de contribuição
├── requirements.txt             # Dependências Python
├── docs/
│   ├── scope.md                # Definição de escopo do modelo
│   ├── taxonomy.md             # Categorias de conhecimento
│   ├── quality-rules.md        # Regras de qualidade do dataset
│   └── eval-rubric.md          # Critérios de avaliação
├── data/
│   ├── curated/                # Exemplos revisados (gerados via MASTER_PROMPT)
│   └── TEMPLATE.jsonl          # Exemplo do formato correto
├── scripts/
│   ├── generate_prompt.py      # Gerar prompts para LLM
│   ├── validate_jsonl.py       # Validar formato JSONL
│   ├── dedupe_dataset.py       # Remover duplicatas
│   ├── build_dataset_fixed.py  # Criar splits train/valid/eval
│   └── evaluate_model.py        # Executar benchmarks
├── .agents/skills/
│   └── generate-oci-dataset/   # Prompts de geração
│       ├── MASTER_FORMAT.md
│       ├── SKILL.md
│       └── prompts/            # Prompts por topic
└── training/
    ├── train_mlx.sh            # Treinamento MLX LoRA
    ├── export_adapter.sh       # Exportar modelo mesclado
    └── run_inference.sh        # Testar inferência
```

## Artefatos de Saída

Após o treinamento, os seguintes artefatos são gerados:

- `outputs/adapters/` - Adaptadores LoRA treinados
- `outputs/benchmarks/` - Relatórios de avaliação
- `outputs/logs/` - Logs de treinamento

## Pipeline

1. **Documentação** → Escopo, taxonomia, regras de qualidade, rubrica de avaliação
2. **Geração de Dados** → Use MASTER_PROMPT com LLM externo → curated/[topic].jsonl
3. **Validação** → Validador JSONL, deduplicação
4. **Construção do Dataset** → Criar splits train/valid/eval
5. **Treinamento** → Fine-tuning MLX LoRA
6. **Avaliação** → Comparar base vs fine-tuned

## Licença

Este projeto é para fins educacionais e de pesquisa.