#!/usr/bin/env python3
"""Generate OCI training examples using async parallel LLM calls via OpenRouter/Gemini.

v2: Paralelismo real com asyncio — múltiplas categorias e batches simultâneos.
Reduz tempo de ~2h para ~8-15min com max_concurrent=15.

Uso:
    python scripts/generate_llm_v2.py
    python scripts/generate_llm_v2.py --config config/llm_provider.yaml
    python scripts/generate_llm_v2.py --categories compute/instances networking/vcn
    python scripts/generate_llm_v2.py --resume          # continua de onde parou
    python scripts/generate_llm_v2.py --no-resume       # começa do zero
    python scripts/generate_llm_v2.py --dry-run         # testa config sem gerar
    python scripts/generate_llm_v2.py --concurrency 20  # ajusta concorrência

Pré-requisitos:
    pip install openai pyyaml
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import random
import re
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from itertools import cycle
from pathlib import Path
from typing import Any

import yaml

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

DOCS_DIR      = Path("docs")
TAXONOMY_FILE = DOCS_DIR / "taxonomy.md"
QUALITY_FILE  = DOCS_DIR / "quality-rules.md"

# ---------------------------------------------------------------------------
# Taxonomy
# ---------------------------------------------------------------------------

def load_taxonomy(path: Path = TAXONOMY_FILE) -> dict[str, dict]:
    if not path.exists():
        log.error(f"taxonomy.md não encontrado: {path}")
        sys.exit(1)

    taxonomy: dict[str, dict] = {}
    current_cat: str | None = None
    hints: list[str] = []
    docs_url: str = ""

    with open(path) as f:
        for line in f:
            line = line.rstrip()
            cat_match = re.match(r"^####\s+([\w/.-]+)", line)
            if cat_match:
                if current_cat:
                    taxonomy[current_cat] = {"hints": hints, "docs_url": docs_url}
                current_cat = cat_match.group(1)
                hints = []
                docs_url = ""
                continue
            if current_cat is None:
                continue
            docs_match = re.match(r"^-\s+\*\*Docs\*\*:\s+(https?://\S+)", line)
            if docs_match:
                docs_url = docs_match.group(1)
                continue
            hint_match = re.match(r"^-\s+(.+)", line)
            if hint_match:
                hints.append(hint_match.group(1))

    if current_cat:
        taxonomy[current_cat] = {"hints": hints, "docs_url": docs_url}

    log.info(f"taxonomy.md carregado: {len(taxonomy)} categorias.")
    return taxonomy

# ---------------------------------------------------------------------------
# Quality rules
# ---------------------------------------------------------------------------

PROHIBITED_MARKER = "### Prohibited Content"
REQUIRED_MARKER   = "### Required Content"
TEMPLATES_MARKER  = "### Response Templates"
VALIDATION_MARKER = "### Validation Checklist"


def load_quality_rules(path: Path = QUALITY_FILE) -> dict[str, str]:
    if not path.exists():
        log.error(f"quality-rules.md não encontrado: {path}")
        sys.exit(1)

    sections: dict[str, list[str]] = {
        "prohibited": [],
        "required":   [],
        "templates":  [],
    }
    current: str | None = None

    with open(path) as f:
        for line in f:
            stripped = line.rstrip()
            if PROHIBITED_MARKER in stripped:
                current = "prohibited"; continue
            if REQUIRED_MARKER in stripped:
                current = "required"; continue
            if TEMPLATES_MARKER in stripped:
                current = "templates"; continue
            if VALIDATION_MARKER in stripped:
                current = None; continue
            if current is not None:
                sections[current].append(stripped)

    log.info("quality-rules.md carregado.")
    return {k: "\n".join(v).strip() for k, v in sections.items()}


def build_system_prompt(quality: dict[str, str]) -> str:
    prohibited = quality.get("prohibited", "")
    required   = quality.get("required",   "")
    templates  = quality.get("templates",  "")
    return f"""Você é um especialista sênior em Oracle Cloud Infrastructure (OCI).
Responda SEMPRE em português brasileiro.
Suas respostas devem incluir: comandos OCI CLI corretos, exemplos de código Python SDK ou Terraform quando relevante, boas práticas e considerações de segurança.
Use formatação markdown com blocos de código. Seja técnico e preciso.

=== REGRAS DE QUALIDADE ===

--- PROIBIDO ---
{prohibited}

--- OBRIGATÓRIO ---
{required}

--- EXEMPLO DE RESPOSTA ADEQUADA ---
{templates}
"""

# ---------------------------------------------------------------------------
# Context constants
# ---------------------------------------------------------------------------

COMPANIES = [
    "TechCorp Brasil", "DataFlow Solutions", "CloudNative Inc",
    "FinServe Digital", "RetailMax Online", "HealthTech Systems",
    "EduPlatform Global", "LogiTrack Logistics", "MediaStream Pro",
    "AgriTech Innovations", "SecureBank Corp", "SmartCity IoT",
]

PERSONAS = [
    "cloud architect", "platform engineer", "SRE", "security lead",
    "DBA", "FinOps analyst", "DevOps engineer", "infrastructure engineer",
]

CONSTRAINTS = [
    "sem downtime", "com budget limitado", "com auditoria em 30 dias",
    "ambiente legado", "multi-região", "integração híbrida",
    "mínimo privilégio", "rollback em menos de 15 minutos",
]

LIFECYCLE_STAGES = [
    "greenfield", "brownfield", "produção estável",
    "incidente", "expansão", "migração",
]

DIFFICULTIES = ["beginner"] * 3 + ["intermediate"] * 5 + ["advanced"] * 2

QUESTION_INTENTS = [
    "como configurar", "qual a melhor prática para", "como solucionar",
    "como migrar", "como otimizar", "como monitorar", "como automatizar",
    "quais são os riscos de", "como auditar", "como escalar",
]

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

DEFAULT_CONFIG = Path("config/llm_provider.yaml")


def load_config(path: Path) -> dict:
    if not path.exists():
        log.error(
            f"Config não encontrado: {path}\n"
            f"  Execute: cp config/llm_provider.example.yaml config/llm_provider.yaml\n"
            f"  Depois edite o arquivo com sua API key."
        )
        sys.exit(1)
    with open(path) as f:
        cfg = yaml.safe_load(f)
    _validate_config(cfg, path)
    return cfg


def _validate_config(cfg: dict, path: Path) -> None:
    key = cfg.get("provider", {}).get("api_key", "")
    if "COLOQUE_SUA_KEY" in key or not key:
        log.error(
            f"API key não configurada em {path}.\n"
            f"  Edite o campo provider.api_key com sua chave."
        )
        sys.exit(1)
    if not cfg.get("models"):
        log.error("Nenhum modelo configurado em 'models'.")
        sys.exit(1)

# ---------------------------------------------------------------------------
# Model rotator (thread-safe via lock)
# ---------------------------------------------------------------------------

class ModelRotator:
    def __init__(self, models: list[dict]):
        pool = []
        for m in models:
            pool.extend([m["id"]] * max(1, m.get("weight", 1)))
        random.shuffle(pool)
        self._cycle   = cycle(pool)
        self._lock    = asyncio.Lock()
        self._fail_counts: dict[str, int] = defaultdict(int)
        log.info(f"Modelos na rotação: {list(dict.fromkeys(pool))}")

    async def next(self) -> str:
        async with self._lock:
            return next(self._cycle)

    def mark_failure(self, model_id: str) -> None:
        self._fail_counts[model_id] += 1

    def stats(self) -> dict:
        return dict(self._fail_counts)

# ---------------------------------------------------------------------------
# Async OpenRouter/Gemini client
# ---------------------------------------------------------------------------

class AsyncLLMClient:
    def __init__(self, cfg: dict, max_concurrent: int):
        try:
            from openai import AsyncOpenAI
        except ImportError:
            log.error("Instale a dependência: pip install openai")
            sys.exit(1)

        provider = cfg["provider"]
        headers  = cfg.get("http_headers", {})

        self.client = AsyncOpenAI(
            api_key=provider["api_key"],
            base_url=provider["base_url"],
            default_headers=headers,
        )
        self.gen_cfg        = cfg["generation"]
        self.semaphore      = asyncio.Semaphore(max_concurrent)
        rl                  = cfg["rate_limit"]
        self.retry_attempts = rl.get("retry_attempts", 5)
        self.retry_delay    = rl.get("retry_delay_seconds", 4)
        self._counters      = {"ok": 0, "fail": 0}
        self._lock          = asyncio.Lock()

    async def call(
        self,
        model_id: str,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int,
    ) -> str | None:
        async with self.semaphore:
            for attempt in range(1, self.retry_attempts + 1):
                try:
                    response = await self.client.chat.completions.create(
                        model=model_id,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user",   "content": user_prompt},
                        ],
                        max_tokens=max_tokens,
                        temperature=self.gen_cfg.get("temperature", 0.85),
                    )
                    async with self._lock:
                        self._counters["ok"] += 1
                    return response.choices[0].message.content
                except Exception as exc:
                    wait = self.retry_delay * (2 ** (attempt - 1))
                    log.warning(
                        f"Tentativa {attempt}/{self.retry_attempts} falhou "
                        f"({model_id}): {exc}. Aguardando {wait:.0f}s..."
                    )
                    await asyncio.sleep(wait)
            async with self._lock:
                self._counters["fail"] += 1
            return None

    @property
    def counters(self) -> dict:
        return dict(self._counters)

# ---------------------------------------------------------------------------
# Batch prompt builder (idêntico ao v1)
# ---------------------------------------------------------------------------

def build_batch_prompt(
    category: str,
    batch_size: int,
    taxonomy: dict[str, dict],
) -> str:
    service  = category.split("/")[-1].replace("-", " ").replace("_", " ")
    cat_info = taxonomy.get(category, {})
    hints    = cat_info.get("hints", [])
    docs_url = cat_info.get("docs_url", "")

    hints_block = ""
    if hints:
        hints_str   = "\n".join(f"  - {h}" for h in hints)
        hints_block = f"\nAspectos relevantes para esta categoria:\n{hints_str}\n"

    docs_block = ""
    if docs_url:
        docs_block = f"\nDocumentação oficial de referência: {docs_url}"

    contexts = []
    for _ in range(batch_size):
        company    = random.choice(COMPANIES)
        persona    = random.choice(PERSONAS)
        constraint = random.choice(CONSTRAINTS)
        lifecycle  = random.choice(LIFECYCLE_STAGES)
        intent     = random.choice(QUESTION_INTENTS)
        difficulty = random.choice(DIFFICULTIES)
        contexts.append(
            f"  - empresa={company}, persona={persona}, restrição={constraint}, "
            f"lifecycle={lifecycle}, intent='{intent}', difficulty={difficulty}"
        )

    contexts_str = "\n".join(contexts)

    return f"""Gere exatamente {batch_size} exemplos de treinamento sobre a categoria OCI: **{category}** ({service}).
{hints_block}{docs_block}

Cada exemplo deve ter uma pergunta técnica realista e uma resposta detalhada em português brasileiro.
Use os contextos abaixo para variar empresa, persona, restrição e dificuldade:
{contexts_str}

RETORNE SOMENTE um JSON array válido, sem texto antes ou depois, sem markdown code blocks, sem explicações.
Formato exato:
[
  {{
    "question": "pergunta completa e contextualizada aqui",
    "answer": "resposta técnica detalhada com CLI, código e boas práticas aqui",
    "difficulty": "beginner|intermediate|advanced"
  }},
  ...
]

Cada resposta deve incluir:
1. Explicação do conceito e quando usar
2. Comandos OCI CLI completos e funcionais
3. Trecho de código Python SDK ou bloco Terraform (se aplicável)
4. Pelo menos uma boa prática ou ponto de atenção
5. Riscos ou trade-offs da abordagem recomendada

Gere os {batch_size} exemplos agora:"""

# ---------------------------------------------------------------------------
# JSON parser (idêntico ao v1)
# ---------------------------------------------------------------------------

def parse_batch_response(raw: str, category: str) -> list[dict]:
    if not raw:
        return []

    cleaned = re.sub(r"```(?:json)?\s*", "", raw).strip()
    cleaned = re.sub(r"```\s*$", "", cleaned).strip()

    try:
        data = json.loads(cleaned)
        if isinstance(data, list):
            return _validate_items(data, category)
    except json.JSONDecodeError:
        pass

    bracket_match = re.search(r"(\[.*\])", cleaned, re.DOTALL)
    if bracket_match:
        try:
            data = json.loads(bracket_match.group(1))
            if isinstance(data, list):
                return _validate_items(data, category)
        except json.JSONDecodeError:
            pass

    items = []
    for obj_match in re.finditer(r"\{[^{}]*\"question\"[^{}]*\"answer\"[^{}]*\}", cleaned, re.DOTALL):
        try:
            obj = json.loads(obj_match.group(0))
            validated = _validate_items([obj], category)
            items.extend(validated)
        except json.JSONDecodeError:
            continue

    if items:
        log.warning(f"  [{category}] JSON malformado — recuperados {len(items)} via regex fallback.")
        return items

    log.warning(f"  [{category}] Falha total no parse. Raw (200 chars): {raw[:200]}")
    return []


def _validate_items(items: list, category: str) -> list[dict]:
    valid = []
    for item in items:
        if not isinstance(item, dict):
            continue
        q = str(item.get("question", "")).strip()
        a = str(item.get("answer",   "")).strip()
        if len(q) >= 20 and len(a) >= 50:
            valid.append({
                "question":   q,
                "answer":     a,
                "difficulty": str(item.get("difficulty", "intermediate")).strip(),
            })
    return valid


def build_example(
    category: str,
    question: str,
    answer: str,
    model_id: str,
    difficulty: str,
    system_prompt: str,
) -> dict:
    return {
        "messages": [
            {"role": "system",    "content": system_prompt},
            {"role": "user",      "content": question},
            {"role": "assistant", "content": answer},
        ],
        "metadata": {
            "category":     category,
            "difficulty":   difficulty,
            "source":       "llm_generated_v2",
            "model":        model_id,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        },
    }

# ---------------------------------------------------------------------------
# Checkpoint (thread-safe via asyncio.Lock)
# ---------------------------------------------------------------------------

class Checkpoint:
    def __init__(self, path: Path):
        self.path  = path
        self._data = self._load()
        self._lock = asyncio.Lock()

    def _load(self) -> dict:
        if self.path.exists():
            try:
                with open(self.path) as f:
                    data = json.load(f)
                log.info(f"Checkpoint carregado: {data.get('total_generated', 0)} exemplos já gerados.")
                return data
            except Exception:
                pass
        return {"total_generated": 0, "per_category": {}}

    async def save(self) -> None:
        async with self._lock:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.path, "w") as f:
                json.dump(self._data, f, indent=2)

    async def get_category_count(self, category: str) -> int:
        async with self._lock:
            return self._data["per_category"].get(category, 0)

    async def increment(self, category: str, count: int = 1) -> int:
        async with self._lock:
            prev = self._data["per_category"].get(category, 0)
            self._data["per_category"][category] = prev + count
            self._data["total_generated"] = sum(self._data["per_category"].values())
            return self._data["total_generated"]

    @property
    def total(self) -> int:
        return self._data["total_generated"]

    def reset(self) -> None:
        self._data = {"total_generated": 0, "per_category": {}}
        if self.path.exists():
            self.path.unlink()
        log.info("Checkpoint resetado.")

# ---------------------------------------------------------------------------
# Progress tracker
# ---------------------------------------------------------------------------

class Progress:
    def __init__(self, total: int):
        self.total         = total
        self.generated     = 0
        self.failed_batches = 0
        self._lock         = asyncio.Lock()
        self._start        = time.monotonic()

    async def add(self, count: int, failed: int = 0) -> None:
        async with self._lock:
            self.generated      += count
            self.failed_batches += failed
            elapsed = time.monotonic() - self._start
            rate    = self.generated / elapsed if elapsed > 0 else 0
            eta     = (self.total - self.generated) / rate if rate > 0 else 0
            pct     = (self.generated / self.total) * 100
            print(
                f"\r  Progresso: {self.generated}/{self.total} ({pct:.1f}%) "
                f"| {rate:.1f} ex/s | ETA: {eta/60:.1f}min "
                f"| Batches falhos: {self.failed_batches}   ",
                end="",
                flush=True,
            )

# ---------------------------------------------------------------------------
# Async Dataset Generator
# ---------------------------------------------------------------------------

class AsyncDatasetGenerator:
    def __init__(
        self,
        cfg: dict,
        taxonomy: dict[str, dict],
        system_prompt: str,
        categories: list[str] | None = None,
        max_concurrent: int | None = None,
    ):
        self.cfg           = cfg
        self.gen_cfg       = cfg["generation"]
        self.taxonomy      = taxonomy
        self.system_prompt = system_prompt
        self.categories    = categories or list(taxonomy.keys())
        self.output_dir    = Path(self.gen_cfg["output_dir"])
        self.checkpoint    = Checkpoint(Path(self.gen_cfg["checkpoint_file"]))

        self.examples_per_cat = self.gen_cfg.get("examples_per_category", 180)
        self.batch_size       = self.gen_cfg.get("batch_size", 60)
        self.checkpoint_every = self.gen_cfg.get("checkpoint_every", 60)
        self.max_failures     = self.gen_cfg.get("max_failures_per_batch", 5)
        self.max_tokens       = self.gen_cfg.get(
            "max_tokens", self.batch_size * 800 + 500
        )

        # concorrência: CLI arg > config > default 15
        rl = cfg["rate_limit"]
        self.max_concurrent = (
            max_concurrent
            or rl.get("max_concurrent", 15)
        )

        self.client  = AsyncLLMClient(cfg, self.max_concurrent)
        self.rotator = ModelRotator(cfg["models"])
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _output_file(self, category: str) -> Path:
        safe = category.replace("/", "_")
        return self.output_dir / f"{safe}.jsonl"

    async def _process_batch(
        self,
        category: str,
        batch_size: int,
        file_lock: asyncio.Lock,
        out_file: Path,
        progress: Progress,
        generated_since_save: list,  # mutable counter
    ) -> int:
        """Processa um único batch para uma categoria. Retorna exemplos salvos."""
        model_id = await self.rotator.next()
        prompt   = build_batch_prompt(category, batch_size, self.taxonomy)

        raw = await self.client.call(
            model_id=model_id,
            system_prompt=self.system_prompt,
            user_prompt=prompt,
            max_tokens=self.max_tokens,
        )

        if raw is None:
            self.rotator.mark_failure(model_id)
            await progress.add(0, failed=1)
            return 0

        items = parse_batch_response(raw, category)
        if not items:
            self.rotator.mark_failure(model_id)
            await progress.add(0, failed=1)
            return 0

        to_save = items[:batch_size]
        lines   = []
        for item in to_save:
            ex = build_example(
                category,
                item["question"],
                item["answer"],
                model_id,
                item["difficulty"],
                self.system_prompt,
            )
            lines.append(json.dumps(ex, ensure_ascii=False) + "\n")

        async with file_lock:
            with open(out_file, "a", encoding="utf-8") as fout:
                fout.writelines(lines)

        saved = len(to_save)
        total = await self.checkpoint.increment(category, saved)
        await progress.add(saved)

        # checkpoint periódico
        generated_since_save[0] += saved
        if generated_since_save[0] >= self.checkpoint_every:
            await self.checkpoint.save()
            generated_since_save[0] = 0

        log.debug(
            f"  [{category}] batch ok: {saved}/{batch_size} salvos "
            f"(total={total}, model={model_id.split('/')[-1]})"
        )
        return saved

    async def _process_category(self, category: str, progress: Progress) -> int:
        """Gera todos os batches de uma categoria em paralelo."""
        already   = await self.checkpoint.get_category_count(category)
        remaining = self.examples_per_cat - already

        if remaining <= 0:
            log.info(f"  [{category}] já completa ({already}/{self.examples_per_cat}), pulando.")
            return already

        log.info(
            f"  [{category}] gerando {remaining} exemplos "
            f"em batches de {self.batch_size}..."
        )

        out_file              = self._output_file(category)
        file_lock             = asyncio.Lock()
        generated_since_save  = [0]  # mutable para compartilhar entre coroutines
        consecutive_failures  = 0
        total_saved           = already

        # Divide em batches e processa com retry por categoria
        batches = []
        r = remaining
        while r > 0:
            batches.append(min(self.batch_size, r))
            r -= batches[-1]

        # Processa batches com controle de falhas consecutivas
        tasks = []
        for b in batches:
            tasks.append(
                self._process_batch(
                    category, b, file_lock, out_file, progress, generated_since_save
                )
            )

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for r in results:
            if isinstance(r, Exception):
                log.error(f"  [{category}] erro inesperado: {r}")
            elif isinstance(r, int):
                total_saved += r

        return total_saved

    async def run(self, resume: bool = True) -> None:
        if not resume:
            self.checkpoint.reset()

        total_target = len(self.categories) * self.examples_per_cat
        import math
        est_requests = math.ceil(
            max(0, total_target - self.checkpoint.total) / self.batch_size
        )

        log.info(
            f"\n{'='*60}\n"
            f"  GERAÇÃO ASYNC v2 — {self.max_concurrent} requests simultâneos\n"
            f"  {len(self.categories)} categorias × {self.examples_per_cat} exemplos = {total_target} total\n"
            f"  Requests estimados : ~{est_requests}\n"
            f"  max_tokens/request : {self.max_tokens}\n"
            f"  Já gerados         : {self.checkpoint.total}\n"
            f"{'='*60}"
        )

        progress = Progress(total_target)

        # Todas as categorias em paralelo (semáforo controla concorrência real)
        category_tasks = [
            self._process_category(cat, progress)
            for cat in self.categories
        ]
        await asyncio.gather(*category_tasks)

        await self.checkpoint.save()
        print()  # newline após progress bar

        elapsed = time.monotonic() - progress._start
        log.info("=" * 60)
        log.info("GERAÇÃO CONCLUÍDA")
        log.info("=" * 60)
        log.info(f"  Exemplos gerados  : {progress.generated}")
        log.info(f"  Batches falhos    : {progress.failed_batches}")
        log.info(f"  Meta              : {total_target}")
        log.info(f"  Taxa de sucesso   : {progress.generated / max(total_target, 1) * 100:.1f}%")
        log.info(f"  Tempo total       : {elapsed/60:.1f} min")
        log.info(f"  Throughput        : {progress.generated / elapsed:.1f} ex/s")
        log.info(f"  Saída             : {self.output_dir}/")
        if self.rotator.stats():
            log.info(f"  Falhas por modelo : {self.rotator.stats()}")
        log.info(f"  Stats client      : {self.client.counters}")
        log.info("")
        log.info("Próximos passos:")
        log.info("  bash scripts/prepare_data.sh   # valida, limpa, deduplica e gera splits")


# ---------------------------------------------------------------------------
# Dry-run
# ---------------------------------------------------------------------------

async def dry_run(cfg: dict, taxonomy: dict[str, dict], system_prompt: str, max_concurrent: int) -> None:
    gen        = cfg["generation"]
    batch_size = gen.get("batch_size", 60)
    max_tokens = gen.get("max_tokens", batch_size * 800 + 500)
    total      = len(taxonomy) * gen.get("examples_per_category", 180)
    import math
    est = math.ceil(total / batch_size)

    log.info("=== DRY RUN ===")
    log.info(f"  Provider          : {cfg['provider']['name']}")
    log.info(f"  Base URL          : {cfg['provider']['base_url']}")
    log.info(f"  Modelos           : {[m['id'] for m in cfg['models']]}")
    log.info(f"  max_concurrent    : {max_concurrent}")
    log.info(f"  Output dir        : {gen['output_dir']}")
    log.info(f"  Meta              : {total} exemplos")
    log.info(f"  Batch size        : {batch_size}")
    log.info(f"  max_tokens        : {max_tokens}")
    log.info(f"  Requests estimados: ~{est}")
    log.info(f"  Categorias        : {len(taxonomy)}")
    log.info(f"  Speedup estimado  : ~{max_concurrent}x vs sequencial")

    log.info("\nTestando 1 request real (batch de 2) com o primeiro modelo...")
    client   = AsyncLLMClient(cfg, max_concurrent)
    model_id = cfg["models"][0]["id"]

    test_category = list(taxonomy.keys())[0]
    prompt = build_batch_prompt(test_category, 2, taxonomy)
    raw    = await client.call(
        model_id=model_id,
        system_prompt=system_prompt,
        user_prompt=prompt,
        max_tokens=2000,
    )
    if raw:
        items = parse_batch_response(raw, test_category)
        log.info(f"  ✅ Request OK! {len(items)} exemplos extraídos do batch de teste.")
        if items:
            log.info(f"  Exemplo #1 question: {items[0]['question'][:120]}...")
    else:
        log.error("  ❌ Request falhou. Verifique sua API key e conexão.")
        sys.exit(1)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Gera dataset OCI via LLM em modo async paralelo (v2)"
    )
    parser.add_argument(
        "--config", "-c",
        type=Path,
        default=DEFAULT_CONFIG,
        help=f"Arquivo de configuração YAML (padrão: {DEFAULT_CONFIG})",
    )
    parser.add_argument(
        "--categories",
        nargs="+",
        metavar="CATEGORY",
        help="Categorias específicas (ex: compute/instances networking/vcn)",
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=None,
        help="Número de requests simultâneos (sobrescreve config rate_limit.max_concurrent)",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        default=True,
        help="Continua de onde parou usando o checkpoint (padrão: ativo)",
    )
    parser.add_argument(
        "--no-resume",
        action="store_false",
        dest="resume",
        help="Ignora checkpoint e começa do zero",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Valida config e testa 1 batch sem gerar dataset",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    taxonomy      = load_taxonomy()
    quality_rules = load_quality_rules()
    system_prompt = build_system_prompt(quality_rules)
    cfg           = load_config(args.config)

    max_concurrent = args.concurrency or cfg["rate_limit"].get("max_concurrent", 15)

    if args.dry_run:
        asyncio.run(dry_run(cfg, taxonomy, system_prompt, max_concurrent))
        return

    generator = AsyncDatasetGenerator(
        cfg=cfg,
        taxonomy=taxonomy,
        system_prompt=system_prompt,
        categories=args.categories,
        max_concurrent=max_concurrent,
    )
    asyncio.run(generator.run(resume=args.resume))


if __name__ == "__main__":
    main()
