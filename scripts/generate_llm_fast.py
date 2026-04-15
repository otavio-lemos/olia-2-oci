#!/usr/bin/env python3
"""Generate OCI training examples with LLM intelligence + local speed.

Uses taxonomy.md as base, applies quality-rules.md, generates diverse examples
in parallel using opencode/minimax-m2.5-free.

Key optimizations:
- Parallel subprocess execution (not sequential)
- Batch generation (multiple examples per LLM call)
- Taxonomy-driven prompts (not hardcoded templates)
- Checkpoint resume support
"""

import asyncio
import json
import random
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Any

random.seed(42)

# ============================================================================
# CONFIG
# ============================================================================

MODEL = "opencode/minimax-m2.5-free"
TAXONOMY_FILE = Path("docs/taxonomy.md")
QUALITY_FILE = Path("docs/quality-rules.md")
OUTPUT_DIR = Path("data/curated")
CHECKPOINT_FILE = Path("data/checkpoint_llm.json")

BATCH_SIZE = 10  # Examples per LLM call
PARALLEL_WORKERS = 4  # Concurrent LLM calls (reduced to avoid rate limits)
TIMEOUT = 90  # Seconds per call (reduced)

# ============================================================================
# LOAD TAXONOMY & QUALITY RULES
# ============================================================================


def load_taxonomy() -> dict[str, dict]:
    """Parse taxonomy.md to get categories and hints."""
    if not TAXONOMY_FILE.exists():
        print(f"[WARN] {TAXONOMY_FILE} not found")
        return {}

    taxonomy = {}
    content = TAXONOMY_FILE.read_text()

    # Extract all categories (#### category/path)
    cat_pattern = re.compile(
        r"^####\s+([\w/.-]+)\s*\n(.*?)(?=^####|\Z)", re.MULTILINE | re.DOTALL
    )

    for match in cat_pattern.finditer(content):
        cat = match.group(1).strip()
        hints = match.group(2).strip()
        # Extract bullet points as hints
        bullet_pattern = re.compile(r"^\s*-\s*(.+)$", re.MULTILINE)
        hint_list = bullet_pattern.findall(hints)
        taxonomy[cat] = {"hints": hint_list, "raw": hints}

    print(f"[INFO] Loaded {len(taxonomy)} categories from taxonomy.md")
    return taxonomy


def load_quality_rules() -> str:
    """Load quality-rules.md for prompt injection."""
    if not QUALITY_FILE.exists():
        return ""
    return QUALITY_FILE.read_text()


# ============================================================================
# PROMPT BUILDERS
# ============================================================================

QUALITY_CONTEXT = """
## Quality Rules (MUST FOLLOW):
- NEVER copy OCI documentation verbatim - paraphrase in your own words
- NEVER invent non-existent Oracle services
- Mark mutable content with [MUTABLE] for prices, limits
- Use accurate OCI terminology: Compartment (not "folder"), VCN (define on first use)
- Include CLI commands and Python SDK examples when relevant
- Answer in Portuguese Brasileiro (PT-BR)
- Always include technical steps and justifications
"""

INTENT_TEMPLATES = [
    "como faço para {action}?",
    "qual a melhor forma de {action}?",
    "preciso {action} - como configuro?",
    "me ajude a {action}",
    "qual o processo para {action}?",
    "explique como {action}",
    "qual a diferença entre {action} e alternativa?",
    "quando devo usar {action}?",
]

DIFFICULTY_WEIGHTS = {"beginner": 0.3, "intermediate": 0.5, "advanced": 0.2}


def build_diverse_prompt(category: str, hints: list[str], batch_size: int) -> str:
    """Build a diverse prompt that avoids template repetition."""

    # Randomly select intent pattern
    action = category.replace("/", " ").replace("-", " ")
    intent = random.choice(INTENT_TEMPLATES).format(action=action)

    # Select random subset of hints for context
    selected_hints = random.sample(hints, min(4, len(hints))) if hints else []
    hints_str = (
        "\n".join(f"  - {h}" for h in selected_hints)
        if selected_hints
        else "  - Basic concepts"
    )

    return f"""Você é um especialista sênior em Oracle Cloud Infrastructure (OCI).
{QUALITY_CONTEXT}

Gere EXATAMENTE {batch_size} exemplos técnicos sobre: {category}

Contexto do tópico:
{hints_str}

IMPORTANTE: Responda APENAS com JSON válido, sem texto antes ou depois.
Formato obrigatório:
{{"examples": [{{"question": "pergunta técnica", "answer": "resposta com CLI/SDK", "difficulty": "beginner|intermediate|advanced"}}]}}

Não inclua markdown, não inclua explicações, apenas JSON."""


# ============================================================================
# LLM EXECUTION
# ============================================================================

call_lock = Lock()
active_calls = 0


def call_llm(prompt: str, timeout: int = TIMEOUT) -> str | None:
    """Call opencode CLI with minimax model - direct mode."""
    global active_calls

    cmd = [
        "opencode",
        "run",
        prompt,
        "--model",
        MODEL,
        "--format",
        "json",
        "--pure",  # Run without external plugins/skills for speed
    ]

    # Add system prompt to avoid tool usage
    full_prompt = f"You are a direct assistant. Answer the request immediately without using any tools or skills.\n\n{prompt}"
    cmd[2] = full_prompt

    with call_lock:
        active_calls += 1

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)

        if result.returncode == 0:
            # Extract text from JSON events
            for line in result.stdout.strip().split("\n"):
                try:
                    event = json.loads(line)
                    if event.get("type") == "text" and "part" in event:
                        text = event["part"].get("text", "")
                        if text:
                            return text
                except json.JSONDecodeError:
                    continue
        else:
            print(f"[WARN] opencode error: {result.stderr[:100]}", file=sys.stderr)

    except subprocess.TimeoutExpired:
        print("[WARN] opencode timeout", file=sys.stderr)
    except Exception as e:
        print(f"[WARN] opencode exception: {e}", file=sys.stderr)
    finally:
        with call_lock:
            active_calls -= 1

    return None


def parse_examples(raw: str) -> list[dict]:
    """Parse JSON examples from LLM output."""
    if not raw:
        return []

    content = raw.strip()

    # Extract JSON from markdown if present
    if "```" in content:
        match = re.search(r"```(?:json)?\s*(.*?)```", content, re.DOTALL)
        if match:
            content = match.group(1).strip()

    # Handle leading/trailing whitespace and newlines
    content = content.strip()

    try:
        data = json.loads(content)
        if isinstance(data, dict) and "examples" in data:
            return validate_examples(data["examples"])
        if isinstance(data, list):
            return validate_examples(data)
        # Handle direct object without wrapper
        if isinstance(data, dict) and "question" in data:
            return validate_examples([data])
    except json.JSONDecodeError as e:
        # Try to extract JSON from response
        try:
            # Find JSON object in content
            match = re.search(r"\{.*\}", content, re.DOTALL)
            if match:
                data = json.loads(match.group())
                if isinstance(data, dict) and "examples" in data:
                    return validate_examples(data["examples"])
                if isinstance(data, list):
                    return validate_examples(data)
        except:
            pass

    # Try flexible parsing
    items = []
    try:
        obj_matches = re.findall(r'\{[^{}]*"question"[^{}]*\}', content)
        for m in obj_matches:
            try:
                obj = json.loads(m)
                if "question" in obj:
                    items.append(obj)
            except:
                pass
    except:
        pass

    if items:
        return validate_examples(items)
    return []


def validate_examples(items: list) -> list[dict]:
    """Validate and normalize examples."""
    valid = []
    for item in items:
        if not isinstance(item, dict):
            continue
        q = str(item.get("question", "")).strip()
        a = str(item.get("answer", "")).strip()

        if len(q) >= 20 and len(a) >= 100:
            valid.append(
                {
                    "question": q,
                    "answer": a,
                    "difficulty": str(item.get("difficulty", "intermediate")).strip(),
                }
            )
    return valid


# ============================================================================
# GENERATION
# ============================================================================

checkpoint_data = {"total": 0, "per_category": {}}


def load_checkpoint() -> dict:
    """Load checkpoint file."""
    if CHECKPOINT_FILE.exists():
        try:
            with open(CHECKPOINT_FILE) as f:
                return json.load(f)
        except:
            pass
    return {"total": 0, "per_category": {}}


def save_checkpoint() -> None:
    """Save checkpoint file."""
    CHECKPOINT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CHECKPOINT_FILE, "w") as f:
        json.dump(checkpoint_data, f, indent=2)


def generate_batch(category: str, hints: list[str]) -> tuple[int, list[dict]]:
    """Generate a batch of examples for one category."""
    prompt = build_diverse_prompt(category, hints, BATCH_SIZE)

    raw = call_llm(prompt)
    if not raw:
        return 0, []

    examples = parse_examples(raw)
    return len(examples), examples


async def generate_category_worker(
    sem: asyncio.Semaphore, category: str, hints: list[str], target: int
) -> tuple[str, int]:
    """Async worker for parallel generation."""

    async def _generate():
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, generate_batch, category, hints)

    async with sem:
        generated = 0
        failures = 0

        while generated < target and failures < 5:
            count, examples = await _generate()

            if examples:
                # Save to file
                safe_name = category.replace("/", "_")
                out_file = OUTPUT_DIR / f"{safe_name}.jsonl"

                with open(out_file, "a") as f:
                    for ex in examples:
                        record = {
                            "messages": [
                                {
                                    "role": "system",
                                    "content": "Você é um especialista sênior em OCI. Responda em Português Brasileiro com comandos CLI e exemplos Python SDK.",
                                },
                                {"role": "user", "content": ex["question"]},
                                {"role": "assistant", "content": ex["answer"]},
                            ],
                            "metadata": {
                                "category": category,
                                "difficulty": ex["difficulty"],
                                "source": "llm_generate",
                                "model": MODEL,
                                "generated_at": datetime.now(timezone.utc).isoformat(),
                            },
                        }
                        f.write(json.dumps(record, ensure_ascii=False) + "\n")

                generated += count
                checkpoint_data["per_category"][category] = (
                    checkpoint_data["per_category"].get(category, 0) + count
                )
                checkpoint_data["total"] = sum(checkpoint_data["per_category"].values())
                failures = 0
            else:
                failures += 1
                await asyncio.sleep(2)

        return category, generated


async def main():
    global checkpoint_data

    # Load taxonomy
    taxonomy = load_taxonomy()
    if not taxonomy:
        print("[ERROR] No taxonomy loaded, exiting")
        sys.exit(1)

    # Load checkpoint
    checkpoint_data = load_checkpoint()
    print(f"[INFO] Resuming from: {checkpoint_data['total']} examples")

    # Prepare output
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Calculate work needed
    EXAMPLES_PER_CATEGORY = 180
    tasks = []

    for category, data in taxonomy.items():
        already = checkpoint_data["per_category"].get(category, 0)
        remaining = EXAMPLES_PER_CATEGORY - already

        if remaining > 0:
            batches_needed = (remaining + BATCH_SIZE - 1) // BATCH_SIZE
            for _ in range(batches_needed):
                tasks.append((category, data.get("hints", [])))

    print(f"[INFO] {len(tasks)} batches to generate across {len(taxonomy)} categories")
    print(f"[INFO] Using {PARALLEL_WORKERS} parallel workers")

    # Generate in parallel
    sem = asyncio.Semaphore(PARALLEL_WORKERS)

    async def worker(args):
        category, hints = args
        # Each worker generates one batch
        return await generate_category_worker(sem, category, hints, BATCH_SIZE)

    # Process in waves
    completed = 0
    total = len(tasks)

    while tasks:
        wave = tasks[:PARALLEL_WORKERS]
        tasks = tasks[PARALLEL_WORKERS:]

        results = await asyncio.gather(
            *[worker(t) for t in wave], return_exceptions=True
        )

        for r in results:
            if isinstance(r, Exception):
                print(f"[ERROR] {r}")
            else:
                cat, gen = r
                if gen > 0:
                    completed += 1
                    pct = (completed / total) * 100
                    print(
                        f"\rProgress: {completed}/{total} batches ({pct:.0f}%) | Total: {checkpoint_data['total']}",
                        end="",
                        flush=True,
                    )

        save_checkpoint()

    print()
    print(f"[DONE] Generated {checkpoint_data['total']} total examples")
    print(f"[DONE] Output: {OUTPUT_DIR}/")


if __name__ == "__main__":
    asyncio.run(main())
