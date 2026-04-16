# OCI Specialist LLM - Agent Guidelines

## Project Overview

This project builds a fine-tuned LLM specialist in Oracle Cloud Infrastructure (OCI) using Apple Silicon, MLX, and LoRA. The pipeline prioritizes dataset quality, low cost, and a robust RAG layer (OCI Copilot).

## Tech Stack

- **Hardware**: Apple Silicon M3 Pro (18GB unified memory)
- **Model**: Qwen 2.5 Coder 7B Instruct (4-bit)
- **Framework**: MLX-Tune 0.4.18
- **Orchestration**: LangGraph, Chainlit (UI)
- **Data**: JSONL chat format (PT-BR)

## Pipeline Stages

1. **Data Generation** → generate examples using prompts
2. **Validation** → JSONL validator, deduplication
3. **Training** → MLX-Tune LoRA fine-tuning (Single Cycle)
4. **Ingestion** → Offline document ingestion for RAG
5. **Deployment** → local inference via Chainlit UI

## Training Configuration (Cycle 1)

| Parameter | Value |
|-----------|-------|
| MODEL | mlx-community/Qwen2.5-Coder-7B-Instruct-4bit |
| Iters | 5556 |
| Batch | 1 |
| Grad Accum | 4 |
| Num Layers | 28 |
| Max Seq | 768 |
| BF16 | true |
| Grad Checkpointing | false |

### Expected Performance (M3 Pro 18GB)
- **Peak memory**: ~9.8 GB
- **Throughput**: ~150-165 tokens/sec
- **Duration**: ~2.5 hours

## Data Flow

```
data/curated/        → Generated topic-specific JSONL files
data/all_curated.jsonl → Concatenated and sanitized dataset
data/train.jsonl     → 11,112 examples (75%)
data/valid.jsonl     → 2,222 examples (15%)
data/eval.jsonl      → 1,483 examples (10%)
Total: 14,817 examples
```

## RAG Layer & Orchestration (OCI Copilot)

The project includes a multi-agent system acting as the **OCI Copilot**, optimized for local execution.

### Components
- **UI:** `rag/app_chainlit.py`. Features file attachments, streaming, and Human-in-the-loop (HITL) for safe CLI execution.
- **Orchestration:** `rag/orchestrator.py` (LangGraph). Manages state and logic between agents (Router, Specialists, Execution).
- **Ingestion:** `scripts/update_rag.py`. Offline processing to persist FAISS and BM25 indices to disk, ensuring memory efficiency during chat.

## Quality Rules

- **NEVER** copy documentation verbatim.
- **ALWAYS** include technical steps and justifications.
- **ALWAYS** validate JSONL structure before ingestion.
- **NEVER** allow autonomous execution of destructive OCI commands (HITL required).
