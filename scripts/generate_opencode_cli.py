#!/usr/bin/env python3
"""Generate OCI training examples using opencode CLI - HIGH PERFORMANCE VERSION.

Usage:
    python scripts/generate_opencode_cli.py --examples 180 --parallel 4 --batch 30
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Any

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

TAXONOMY_FILE = Path("docs/taxonomy.md")
QUALITY_FILE = Path("docs/quality-rules.md")
CHECKPOINT_FILE = Path("data/checkpoint_opencode.json")

session_lock = Lock()
current_session = None


def load_taxonomy() -> dict[str, dict]:
    if not TAXONOMY_FILE.exists():
        log.warning(f"taxonomy.md não encontrado: {TAXONOMY_FILE}")
        return {}
    taxonomy = {}
    with open(TAXONOMY_FILE) as f:
        content = f.read()
    cat_pattern = re.compile(r"^####\s+([\w/.-]+)", re.MULTILINE)
    categories = cat_pattern.findall(content)
    for cat in categories:
        taxonomy[cat] = {"hints": [], "docs_url": ""}
    log.info(f"taxonomy.md carregado: {len(taxonomy)} categorias")
    return taxonomy


def extract_text_from_json(output: str) -> str:
    for line in output.strip().split("\n"):
        try:
            event = json.loads(line)
            if event.get("type") == "text" and "part" in event:
                text = event["part"].get("text", "")
                if text:
                    return text
        except json.JSONDecodeError:
            continue
    return ""


def extract_session_id(output: str) -> str | None:
    for line in output.strip().split("\n"):
        try:
            event = json.loads(line)
            if "sessionID" in event:
                return event["sessionID"]
        except:
            continue
    return None


def call_opencode(
    prompt: str, timeout: int = 180, session_id: str = None
) -> tuple[str | None, str | None]:
    global current_session

    cmd = ["opencode", "run", f"{prompt}", "--format", "json"]

    with session_lock:
        if session_id and current_session == session_id:
            cmd.extend(["--session", session_id, "--continue"])
        elif current_session:
            cmd.extend(["--session", current_session, "--continue"])

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        if result.returncode == 0:
            new_session = extract_session_id(result.stdout)
            if new_session:
                with session_lock:
                    if current_session is None:
                        current_session = new_session
            return extract_text_from_json(result.stdout), new_session
        log.warning(
            f"opencode failed: {result.stderr[:200] if result.stderr else 'unknown'}"
        )
    except subprocess.TimeoutExpired:
        log.warning("opencode timeout")
    except Exception as e:
        log.warning(f"opencode error: {e}")
    return None, None


def parse_examples(raw: str, category: str) -> list[dict]:
    if not raw:
        return []
    content = raw.strip()
    if "```" in content:
        match = re.search(r"```(?:json)?\s*(.*?)```", content, re.DOTALL)
        if match:
            content = match.group(1).strip()
    try:
        data = json.loads(content)
        if isinstance(data, dict) and "examples" in data:
            return _validate(data["examples"])
        if isinstance(data, list):
            return _validate(data)
    except json.JSONDecodeError:
        pass

    # Parser flexível
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
        return _validate(items)
    return []


def _validate(items: list) -> list[dict]:
    valid = []
    for item in items:
        if not isinstance(item, dict):
            continue
        q = str(item.get("question", "")).strip()
        a = str(item.get("answer", "")).strip()
        if len(q) >= 20 and len(a) >= 50:
            valid.append(
                {
                    "question": q,
                    "answer": a,
                    "difficulty": str(item.get("difficulty", "intermediate")).strip(),
                }
            )
    return valid


SYSTEM_PROMPT = """Você é um OCI Specialist sênior. Responda em Português Brasileiro.
Inclua comandos OCI CLI e exemplos Python SDK quando relevante.
Responda APENAS com JSON válido sem markdown."""


def build_prompt(category: str, batch: int) -> str:
    return f"""{SYSTEM_PROMPT}

Gere {batch} exemplos técnicos sobre OCI: {category}.
Cada exemplo: question (pergunta técnica), answer (resposta com CLI/SDK), difficulty (beginner/intermediate/advanced).
Responda apenas com JSON:
{{"examples": [{{"question": "...", "answer": "...", "difficulty": "..."}}]}}"""


class Checkpoint:
    def __init__(self, path: Path):
        self.path = path
        self._data = self._load()
        self._lock = Lock()

    def _load(self) -> dict:
        if self.path.exists():
            try:
                with open(self.path) as f:
                    data = json.load(f)
                log.info(f"Checkpoint: {data.get('total_generated', 0)} exemplos")
                return data
            except Exception:
                pass
        return {"total_generated": 0, "per_category": {}}

    def save(self) -> None:
        with self._lock:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.path, "w") as f:
                json.dump(self._data, f, indent=2)

    def get_count(self, category: str) -> int:
        return self._data["per_category"].get(category, 0)

    def increment(self, category: str, count: int) -> None:
        with self._lock:
            self._data["per_category"][category] = self.get_count(category) + count
            self._data["total_generated"] = sum(self._data["per_category"].values())

    def reset(self) -> None:
        self._data = {"total_generated": 0, "per_category": {}}
        if self.path.exists():
            self.path.unlink()


def generate_batch(
    category: str, batch_size: int, checkpoint: Checkpoint, output_dir: Path
) -> tuple[int, int, str]:
    """Gera um batch de exemplos para uma categoria."""
    safe_name = category.replace("/", "_")
    out_file = output_dir / f"{safe_name}.jsonl"

    prompt = build_prompt(category, batch_size)
    raw, _ = call_opencode(prompt)

    if not raw:
        return 0, 1, category

    items = parse_examples(raw, category)
    if not items:
        return 0, 1, category

    saved = 0
    with open(out_file, "a") as fout:
        for item in items:
            ex = {
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": item["question"]},
                    {"role": "assistant", "content": item["answer"]},
                ],
                "metadata": {
                    "category": category,
                    "difficulty": item["difficulty"],
                    "source": "opencode",
                    "model": "minimax-m2.5-free",
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                },
            }
            fout.write(json.dumps(ex, ensure_ascii=False) + "\n")
            saved += 1

    return saved, 0, category


def generate_category_worker(args):
    """Worker para geração paralela de uma categoria."""
    category, examples_needed, batch_size, checkpoint, output_dir = args

    already = checkpoint.get_count(category)
    remaining = examples_needed - already
    if remaining <= 0:
        return category, 0, 0

    total_generated = 0
    total_failures = 0

    while remaining > 0 and total_failures < 5:
        saved, failed, _ = generate_batch(category, batch_size, checkpoint, output_dir)

        if saved > 0:
            checkpoint.increment(category, saved)
            total_generated += saved
            remaining -= saved
            total_failures = 0
        else:
            total_failures += 1
            time.sleep(2)

    return category, total_generated, total_failures


def main():
    parser = argparse.ArgumentParser(
        description="Gera dataset OCI via opencode CLI - ALTA PERFORMANCE"
    )
    parser.add_argument("--categories", "-c", nargs="*", help="Categorias específicas")
    parser.add_argument(
        "--examples", "-e", type=int, default=20, help="Exemplos por categoria"
    )
    parser.add_argument("--batch", "-b", type=int, default=30, help="Tamanho do batch")
    parser.add_argument(
        "--parallel", "-p", type=int, default=4, help=" workers paralelos"
    )
    parser.add_argument(
        "--output", "-o", default="data/curated", help="Diretório de saída"
    )
    parser.add_argument("--resume", action="store_true", default=True)
    parser.add_argument("--no-resume", action="store_false", dest="resume")
    args = parser.parse_args()

    taxonomy = load_taxonomy()
    categories = args.categories or list(taxonomy.keys())

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    checkpoint = Checkpoint(CHECKPOINT_FILE)
    if not args.resume:
        checkpoint.reset()

    total_target = len(categories) * args.examples
    log.info(
        f"Iniciando: {len(categories)} categorias x {args.examples} = {total_target} exemplos"
    )
    log.info(f"Workers paralelos: {args.parallel}, Batch: {args.batch}")
    log.info(f"Já gerados: {checkpoint._data['total_generated']}")

    # Prepara tarefas
    tasks = []
    for category in categories:
        already = checkpoint.get_count(category)
        remaining = args.examples - already
        if remaining > 0:
            tasks.append((category, args.examples, args.batch, checkpoint, output_dir))

    log.info(f"Tarefas a executar: {len(tasks)}")

    # Execução paralela
    with ThreadPoolExecutor(max_workers=args.parallel) as executor:
        futures = [executor.submit(generate_category_worker, task) for task in tasks]

        for future in as_completed(futures):
            try:
                cat, generated, failures = future.result()
                pct = (checkpoint._data["total_generated"] / total_target) * 100
                print(
                    f"\rProgresso: {checkpoint._data['total_generated']}/{total_target} ({pct:.1f}%) - {cat}: +{generated}",
                    end="",
                    flush=True,
                )
                checkpoint.save()
            except Exception as e:
                log.error(f"Erro: {e}")

    checkpoint.save()
    print()
    log.info(f"Concluído: {checkpoint._data['total_generated']} exemplos")
    log.info(f"Saída: {output_dir}/")


if __name__ == "__main__":
    main()
