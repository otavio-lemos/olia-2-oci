# Unified Evaluation Script Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Criar 1 único script Python que consolida todas as avaliações do projeto OCI Specialist LLM, gerando comparação base vs fine-tuned com gráficos e tabelas.

**Architecture:** Script monolítico com classes especializadas para cada componente (avaliação, scoring, similarity, reporting). Suporta modo teste (10 samples) e modo full (325 samples).

**Tech Stack:** Python 3.12, MLX-LM, sentence-transformers, matplotlib, seaborn

---

## Arquitetura do Script

```
scripts/unified_evaluation.py
├── UnifiedEvaluator (main class)
│   ├── load_models() - carrega base + FT
│   ├── run_evaluation() - executa eval
│   └── generate_report() - outputs
├── ScoringEngine (de eval_scoring.py)
│   └── evaluate_response()
├── SemanticScorer (embeddings)
│   └── cosine_similarity()
└── ReportGenerator
    ├── generate_comparison_report()
    ├── generate_difficulty_report()
    └── generate_charts()
```

---

## Dependencies

- [ ] **Step 1: Adicionar dependencies ao requirements.txt**

Arquivo: `requirements.txt`
Adicionar:
```
matplotlib>=3.8.0
seaborn>=0.13.0
```

---

## Task 1: Criar Script Base Estruturado

**Files:**
- Create: `scripts/unified_evaluation.py`

- [ ] **Step 1: Escrever a estrutura base do script**

```python
#!/usr/bin/env python3
"""Unified Evaluation Script for OCI Specialist LLM.

Consolida: base vs FT comparison, scoring, similarity semântica, relatórios com gráficos.
Modos: --test (10 samples), --full (325 samples)
"""

import argparse
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import random

import mlx.core as mx
from mlx_lm import load, generate
from mlx_lm.sample_utils import make_sampler

# Dependências opcionais
try:
    import numpy as np
    import matplotlib.pyplot as plt
    import seaborn as sns
    HAS_PLOTTING = True
except ImportError:
    HAS_PLOTTING = False


class UnifiedEvaluator:
    def __init__(
        self,
        base_model_id: str,
        adapter_path: str = "",
        merged_model_path: str = "",
    ):
        self.base_model_id = base_model_id
        self.adapter_path = adapter_path
        self.merged_model_path = merged_model_path
        self.model = None
        self.tokenizer = None
        self._loaded = False
    
    def load_model(self):
        """Carrega modelo base ou FT."""
        if self._loaded:
            return
        
        if self.merged_model_path:
            print(f"Loading merged model: {self.merged_model_path}")
            self.model, self.tokenizer = load(path_or_hf_repo=self.merged_model_path)
        else:
            print(f"Loading model: {self.base_model_id}")
            if self.adapter_path:
                print(f"  With adapter: {self.adapter_path}")
            self.model, self.tokenizer = load(
                path_or_hf_repo=self.base_model_id,
                adapter_path=self.adapter_path if self.adapter_path else None,
            )
        
        self.sampler = make_sampler(temp=0.5, top_p=0.9, min_p=0.0, top_k=50)
        self._loaded = True
        print("Model loaded successfully")
    
    def generate_response(
        self, prompt: str, system_prompt: str = "", max_tokens: int = 1024
    ) -> str:
        if not self._loaded:
            self.load_model()
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        prompt_tokens = self.tokenizer.apply_chat_template(
            messages, add_generation_prompt=True
        )
        
        start = time.time()
        response = generate(
            self.model,
            self.tokenizer,
            prompt=prompt_tokens,
            max_tokens=max_tokens,
            sampler=self.sampler,
            verbose=False,
        )
        elapsed = time.time() - start
        
        return response, elapsed


def main():
    parser = argparse.ArgumentParser(description="Unified OCI Specialist Evaluation")
    parser.add_argument("--base-model", required=True, help="Base model ID")
    parser.add_argument("--adapter", default="", help="LoRA adapter path")
    parser.add_argument("--merged", default="", help="Merged model path")
    parser.add_argument("--eval-file", default="data/eval.jsonl", help="Eval JSONL")
    parser.add_argument("--output-dir", default="outputs/benchmarks", help="Output dir")
    parser.add_argument("--mode", choices=["test", "full"], default="full", help="Eval mode")
    parser.add_argument("--test-samples", type=int, default=10, help="Test samples count")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    args = parser.parse_args()
    
    print("Unified Evaluation Script")
    print(f"Mode: {args.mode}")
    print(f"Base: {args.base_model}")
    print(f"Adapter: {args.adapter or 'None'}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run test para verificar estrutura**

Run: `python scripts/unified_evaluation.py --base-model test --adapter "" --eval-file data/eval.jsonl`
Expected: Help text output

---

## Task 2: Implementar Scoring Engine

**Files:**
- Modify: `scripts/unified_evaluation.py` - adicionar ScoringEngine class

- [ ] **Step 1: Copiar scoring functions do eval_scoring.py existente**

Implementar as funções de scoring:
- `score_technical_correctness(response, reference, category)`
- `score_depth(response, reference)`
- `score_structure(response)`
- `score_hallucination(response)`
- `score_clarity(response)`
- `evaluate_response(response, reference, category)` - retorna dict com todas as métricas

---

## Task 3: Implementar Semantic Scorer

**Files:**
- Modify: `scripts/unified_evaluation.py` - adicionar SemanticScorer class

- [ ] **Step 1: Implementar classe de similarity semântica**

```python
class SemanticScorer:
    def __init__(self, model_name: str = "sentence-transformers/paraphrase-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
        self.embedding_cache = {}
    
    def load_model(self):
        if self.model is None:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(self.model_name)
    
    def get_embedding(self, text: str):
        if text in self.embedding_cache:
            return self.embedding_cache[text]
        if self.model is None:
            self.load_model()
        embedding = self.model.encode(text, convert_to_numpy=True)
        self.embedding_cache[text] = embedding
        return embedding
    
    def cosine_similarity(self, a, b):
        import numpy as np
        a = a / (np.linalg.norm(a) + 1e-8)
        b = b / (np.linalg.norm(b) + 1e-8)
        return float(np.dot(a, b))
    
    def score(self, response: str, reference: str) -> float:
        resp_emb = self.get_embedding(response)
        ref_emb = self.get_embedding(reference)
        if resp_emb is None or ref_emb is None:
            return 0.5
        return self.cosine_similarity(resp_emb, ref_emb)
```

---

## Task 4: Implementar Report Generator

**Files:**
- Modify: `scripts/unified_evaluation.py` - adicionar ReportGenerator class

- [ ] **Step 1: Implementar generation de relatórios markdown**

```python
class ReportGenerator:
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
    
    def generate_comparison_report(
        self,
        base_results: List[Dict],
        ft_results: List[Dict],
        total_eval: int,
    ) -> Path:
        # Gera relatório markdown comparativo
        pass
    
    def generate_charts(
        self,
        base_results: List[Dict],
        ft_results: List[Dict],
    ) -> List[Path]:
        # Gera gráficos se HAS_PLOTTING=True
        pass
```

---

## Task 5: Implementar Main Evaluation Loop

**Files:**
- Modify: `scripts/unified_evaluation.py` - finalizar main()

- [ ] **Step 1: Implementar loop de avaliação completo**

- Carregar eval_data do JSONL
- Se modo test: amostrar 1 exemplo de cada categoria
- Para cada exemplo:
  - Gerar resposta com base model
  - Calcular scores (technical, depth, structure, hallucination, clarity)
  - Calcular semantic similarity
  - Salvar resultado
- Repetir para FT model
- Gerar relatório comparativo
- Gerar gráficos

---

## Task 6: Adicionar Test Mode

**Files:**
- Modify: `scripts/unified_evaluation.py`

- [ ] **Step 1: Implementar amostragem para modo teste**

```python
def get_test_samples(eval_data: List[Dict], n: int = 10, seed: int = 42) -> List[Dict]:
    """Retorna 1 exemplo de cada categoria, até n categorias."""
    random.seed(seed)
    
    # Agrupar por categoria
    by_category = {}
    for ex in eval_data:
        cat = ex.get("metadata", {}).get("category", "unknown")
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(ex)
    
    # Selecionar 1 de cada categoria (shuffle)
    samples = []
    for cat in random.sample(list(by_category.keys()), min(n, len(by_category))):
        samples.append(random.choice(by_category[cat]))
    
    return samples
```

---

## Task 7: Adicionar Gráficos

**Files:**
- Modify: `scripts/unified_evaluation.py` - adicionar funções de plotting

- [ ] **Step 1: Implementar radar chart comparativo**

```python
def plot_radar_comparison(base_scores: Dict, ft_scores: Dict, output_path: Path):
    """Radar chart comparativo base vs FT."""
    import matplotlib.pyplot as plt
    import numpy as np
    
    categories = list(base_scores.keys())
    N = len(categories)
    
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]
    
    ax = plt.subplot(111, polar=True)
    
    base_values = list(base_scores.values())
    base_values += base_values[:1]
    ax.plot(angles, base_values, 'o-', linewidth=2, label='Base')
    ax.fill(angles, base_values, alpha=0.25)
    
    ft_values = list(ft_scores.values())
    ft_values += ft_values[:1]
    ax.plot(angles, ft_values, 'o-', linewidth=2, label='FT')
    ax.fill(angles, ft_values, alpha=0.25)
    
    plt.xticks(angles[:-1], categories)
    plt.legend(loc='upper right')
    plt.savefig(output_path)
```

- [ ] **Step 2: Implementar bar chart por categoria**

- [ ] **Step 3: Implementar histogram distribution**

- [ ] **Step 4: Implementar heatmap categoria x métrica**

---

## Task 8: Adicionar Tabelas de Relatório

**Files:**
- Modify: `scripts/unified_evaluation.py` - expandir ReportGenerator

- [ ] **Step 1: Tabela Executive Summary**

| Metric | Base | FT | Delta | % |
|--------|------|-----|-------|---|

- [ ] **Step 2: Tabela por categoria**

- [ ] **Step 3: Tabela por dificuldade**

- [ ] **Step 4: Score distribution**

- [ ] **Step 5: Top/bottom categorias**

---

## Task 9: Testar Script em Modo Test

**Files:**
- Run: `scripts/unified_evaluation.py`

- [ ] **Step 1: Executar com 10 samples**

```bash
python scripts/unified_evaluation.py \
    --base-model mlx-community/Meta-Llama-3.1-8B-Instruct-4bit \
    --adapter outputs/cycle-1/adapters \
    --eval-file data/eval.jsonl \
    --mode test \
    --output-dir outputs/benchmarks
```

- [ ] **Step 2: Verificar outputs**

Expected:
- `outputs/benchmarks/unified_test_results.json`
- `outputs/benchmarks/unified_test_report.md`
- `outputs/benchmarks/test_charts/` (radar, bar, hist)

---

## Task 10: Executar Avaliação Completa

**Files:**
- Run: `scripts/unified_evaluation.py`

- [ ] **Step 1: Executar com todos os 325 samples**

```bash
python scripts/unified_evaluation.py \
    --base-model mlx-community/Meta-Llama-3.1-8B-Instruct-4bit \
    --adapter outputs/cycle-1/adapters \
    --eval-file data/eval.jsonl \
    --mode full \
    --output-dir outputs/benchmarks
```

- [ ] **Step 2: Verificar outputs finais**

Expected:
- `outputs/benchmarks/unified_base_results.json`
- `outputs/benchmarks/unified_ft_results.json`
- `outputs/benchmarks/unified_comparison_report.md`
- `outputs/benchmarks/unified_difficulty_report.md`
- `outputs/benchmarks/charts/` (6 gráficos)

---

## Cronograma de Tasks

| Task | Descrição | Estimativa |
|------|----------|------------|
| 1 | Script base estruturado | 15 min |
| 2 | Scoring Engine | 10 min |
| 3 | Semantic Scorer | 10 min |
| 4 | Report Generator | 15 min |
| 5 | Main Loop | 20 min |
| 6 | Test Mode | 5 min |
| 7 | Gráficos | 20 min |
| 8 | Tabelas | 10 min |
| 9 | Testar modo test | 10 min |
| 10 | Executar modo full (325 samples) | ~90 min |

**Total estimado:** ~3.5 hours (modo full com 325 exemplos)

**Dados reais eval.jsonl:**
- Total: 325 examples
- Categorias: 71 unique
- Difficulty: beginner (94), intermediate (170), advanced (61)
- Distribution: 2-8 examples por categoria