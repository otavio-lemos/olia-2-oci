# Plano de Migração: mlx-lm → mlx-tune

## Objetivo

Migrar o pipeline de treinamento de `mlx-lm` (CLI-based) para `mlx-tune` (Python API, Unsloth-compatible) para ganhar:
- **Performance**: Batched RL training, melhor gerenciamento de memória
- **Qualidade**: `train_on_responses_only()`, chat templates nativos, melhor controle de LoRA
- **Relatórios**: API programática para métricas, export direto para HuggingFace, GGUF nativo

## Contexto Atual

```
Atual: python -m mlx_lm lora -c config.yaml
Novo:  Python API via SFTTrainer (Unsloth-compatible)
```

## Análise de Impacto

### Arquivos a MODIFICAR

| Arquivo | Mudança | Complexidade |
|---------|---------|-------------|
| `requirements.txt` | `mlx-lm` → `mlx-tune` | Baixa |
| `training/train_mlx_v2.sh` | Reescrita completa para Python script | Alta |
| `training/log_metrics.py` | Adaptar para callback do SFTTrainer | Média |
| `training/export_adapter.sh` | Usar `model.save_pretrained_merged()` | Baixa |
| `training/run_inference.sh` | Usar `mlx_tune.generate()` ou `mlx_lm.generate` | Baixa |
| `training/run_all_cycles.sh` | Ajustar chamada do novo script | Baixa |

### Arquivos a MANTER (sem mudanças)

| Arquivo | Motivo |
|---------|--------|
| `config/cycle-1.env` | Mesmos hyperparâmetros funcionam |
| `config/cycle-2.env` | Mesmos hyperparâmetros funcionam |
| `config/cycle-3.env` | Mesmos hyperparâmetros funcionam |
| `data/*.jsonl` | Formato de dados compatível |
| `scripts/clean_dataset.py` | Independente do framework |
| `scripts/validate_content.py` | Independente do framework |
| `scripts/quality/*.py` | Independente do framework |
| `scripts/reporting/*.py` | Independente do framework |
| `scripts/performance/*.py` | Independente do framework |

## Plano de Execução

### Fase 1: Infraestrutura (requirements + novo script de treino)

#### 1.1 Atualizar `requirements.txt`

```diff
- mlx-lm==0.31.1
+ mlx-tune>=0.4.17
```

Manter `mlx==0.31.1` (dependência do mlx-tune).

#### 1.2 Criar `training/train_mlx_tune.py`

Novo script Python que substitui `train_mlx_v2.sh`. Usa a API Unsloth-compatible:

```python
#!/usr/bin/env python3
"""
Training script usando mlx-tune (Unsloth-compatible API).
Substitui: training/train_mlx_v2.sh + python -m mlx_lm lora

Uso: CYCLE=cycle-1 python training/train_mlx_tune.py
"""
import os
import json
from pathlib import Path
from dotenv import load_dotenv

from mlx_tune import FastLanguageModel, SFTTrainer, SFTConfig


def load_cycle_config(cycle_name):
    """Carrega config do cycle-N.env"""
    env_file = Path(__file__).parent.parent / "config" / f"{cycle_name}.env"
    config = {}
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                config[key.strip()] = value.strip().strip('"')
    return config


def load_dataset_jsonl(path):
    """Carrega dataset JSONL no formato esperado pelo mlx-tune"""
    import json
    from datasets import Dataset

    messages = []
    with open(path) as f:
        for line in f:
            data = json.loads(line)
            messages.append(data["messages"])

    return Dataset.from_dict({"messages": messages})


def main():
    cycle = os.environ.get("CYCLE", "cycle-1")
    cfg = load_cycle_config(cycle)

    # Parse config
    model_name = cfg.get("MODEL", "mlx-community/Llama-3.2-3B-Instruct-4bit")
    train_data = cfg.get("TRAIN_DATA", "data/train.jsonl")
    valid_data = cfg.get("VALID_DATA", "data/valid.jsonl")
    output_dir = cfg.get("OUTPUT_DIR", f"outputs/{cycle}")
    prev_adapter = cfg.get("PREV_ADAPTER", "")
    iters = int(cfg.get("ITERS", "2450"))
    max_seq_length = int(cfg.get("MAX_SEQ_LENGTH", "2048"))
    batch_size = int(cfg.get("BATCH_SIZE", "8"))
    lr = float(cfg.get("LEARNING_RATE", "3e-5"))
    rank = int(cfg.get("LORA_RANK", "16"))
    alpha = int(cfg.get("LORA_ALPHA", "32"))
    dropout = float(cfg.get("LORA_DROPOUT", "0.05"))
    grad_accum = int(cfg.get("GRADIENT_ACCUMULATION", "2"))

    print(f"=== OCI Specialist - mlx-tune Training ===")
    print(f"Cycle: {cycle}")
    print(f"Model: {model_name}")
    print(f"LR: {lr}, Iters: {iters}, Rank: {rank}")
    print(f"Batch: {batch_size}, Grad Accum: {grad_accum}")
    print(f"Max Seq: {max_seq_length}")
    print()

    # 1. Load model
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=model_name,
        max_seq_length=max_seq_length,
        load_in_4bit=True,
    )

    # 2. Add LoRA adapters (ou resume do ciclo anterior)
    if prev_adapter and Path(prev_adapter).exists():
        print(f"Resuming from: {prev_adapter}")
        # Carrega adapters anteriores e adiciona novos
        model = FastLanguageModel.from_pretrained(
            model_name=model_name,
            max_seq_length=max_seq_length,
            load_in_4bit=True,
            _adapters=[prev_adapter],  # Resume previous adapters
        )

    model = FastLanguageModel.get_peft_model(
        model,
        r=rank,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                        "gate_proj", "up_proj", "down_proj"],
        lora_alpha=alpha,
        lora_dropout=dropout,
        bias="none",
        use_gradient_checkpointing=True,
    )

    # 3. Load dataset
    train_dataset = load_dataset_jsonl(train_data)
    print(f"Train dataset: {len(train_dataset)} examples")

    # 4. Train
    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=train_dataset,
        args=SFTConfig(
            output_dir=output_dir,
            per_device_train_batch_size=batch_size,
            gradient_accumulation_steps=grad_accum,
            learning_rate=lr,
            max_steps=iters,
            logging_steps=10,
            save_steps=50,
            eval_steps=50,
            seed=42,
        ),
    )

    trainer.train()

    # 5. Save adapters
    model.save_pretrained(output_dir)
    print(f"Adapters saved to: {output_dir}")


if __name__ == "__main__":
    main()
```

#### 1.3 Atualizar `training/run_all_cycles.sh`

Mudar a chamada de `train_mlx_v2.sh` para `train_mlx_tune.py`:

```diff
- CYCLE="$CYCLE" bash "${SCRIPT_DIR}/train_mlx_v2.sh"
+ CYCLE="$CYCLE" python "${SCRIPT_DIR}/train_mlx_tune.py"
```

### Fase 2: Métricas e Logging

#### 2.1 Atualizar `training/log_metrics.py`

mlx-tune usa `logging_steps` nativo do SFTTrainer. As métricas são salvas automaticamente em `output_dir/runs/`. Podemos:

**Opção A** (Recomendada): Usar os logs nativos do SFTTrainer (TensorBoard-style)
**Opção B**: Manter wrapper atual mas adaptar parsing

Recomendo **Opção A** + script auxiliar para extrair métricas para CSV:

```python
# training/extract_metrics.py
"""Extrai métricas do training log do mlx-tune para CSV"""
import csv
import json
from pathlib import Path

def extract_metrics(cycle_name):
    output_dir = Path(f"outputs/{cycle_name}")
    # mlx-tune salva em runs/ directory
    runs_dir = output_dir / "runs"
    # ... parse para metrics.csv
```

### Fase 3: Export e Inference

#### 3.1 Atualizar `training/export_adapter.sh`

```diff
- python -m mlx_lm fuse \
-     --model "$BASE_MODEL" \
-     --adapter-path "$ADAPTER_DIR" \
-     --save-path "$MERGED_MODEL"
+ python -c "
+ from mlx_tune import FastLanguageModel
+ model, tokenizer = FastLanguageModel.from_pretrained('$BASE_MODEL')
+ model.save_pretrained_merged('$MERGED_MODEL', tokenizer)
+ "
```

#### 3.2 Atualizar `training/run_inference.sh`

Duas opções:

**Opção A**: Manter `mlx_lm.generate` (compatível, mlx-tune usa mlx-lm por baixo)
**Opção B**: Usar API do mlx-tune para inference

Recomendo **Opção A** para inference - é mais simples e funciona com adapters salvos.

### Fase 4: Melhorias Habilitadas pela Migração

Após a migração básica, habilitar features exclusivas do mlx-tune:

#### 4.1 `train_on_responses_only()`

Treinar apenas nas respostas do assistant (mais eficiente):

```python
from mlx_tune import train_on_responses_only

trainer = train_on_responses_only(
    trainer,
    instruction_part="<|start_header_id|>user<|end_header_id|>\n\n",
    response_part="<|start_header_id|>assistant<|end_header_id|>\n\n",
)
```

#### 4.2 Chat template nativo

```python
from mlx_tune import get_chat_template

tokenizer = get_chat_template(tokenizer, chat_template="llama-3")
```

#### 4.3 GGUF Export (para Ollama/llama.cpp)

```python
model.save_pretrained_gguf("outputs/oci-specialist-gguf", tokenizer)
```

#### 4.4 Push to HuggingFace Hub

```python
model.push_to_hub("seu-org/oci-specialist-lora")
```

## Ordem de Execução

1. ✅ Criar este plano
2. ⏳ Atualizar `requirements.txt`
3. ⏳ Criar `training/train_mlx_tune.py`
4. ⏳ Atualizar `training/run_all_cycles.sh`
5. ⏳ Atualizar `training/export_adapter.sh`
6. ⏳ Criar `training/extract_metrics.py`
7. ⏳ Testar com cycle-1 (ITERS=50 para validação rápida)
8. ⏳ Validar adapters gerados
9. ⏳ Habilitar `train_on_responses_only()`
10. ⏳ Atualizar README

## Riscos e Mitigações

| Risco | Probabilidade | Mitigação |
|-------|--------------|-----------|
| mlx-tune incompatível com Llama-3.2-3B-4bit | Baixa | Suportado oficialmente |
| Formato de dataset diferente | Baixa | JSONL com "messages" é compatível |
| Memory usage diferente | Média | Testar com ITERS=50 primeiro |
| Resume de ciclo anterior não funcionar | Média | Testar cycle-1 → cycle-2 explicitamente |
| Breaking changes em versões futuras | Baixa | Pin `mlx-tune>=0.4.17,<0.5.0` |

## Rollback

Se algo falhar:
1. Reverter `requirements.txt` para `mlx-lm==0.31.1`
2. `train_mlx_v2.sh` permanece no repo (não deletar até validação completa)
3. `pip install -r requirements.txt` restaura ambiente anterior

## Timeline Estimada

| Fase | Tempo |
|------|-------|
| Fase 1: Infraestrutura | 30 min |
| Fase 2: Métricas | 15 min |
| Fase 3: Export/Inference | 15 min |
| Fase 4: Melhorias | 20 min |
| Teste cycle-1 (50 iters) | 10 min |
| **Total** | **~90 min** |
