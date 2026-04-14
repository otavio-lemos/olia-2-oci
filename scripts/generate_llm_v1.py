#!/usr/bin/env python3
"""Generate OCI training examples using a real LLM via OpenRouter (or compatible).

Uso:
    python scripts/generate_llm_v1.py
    python scripts/generate_llm_v1.py --config config/llm_provider.yaml
    python scripts/generate_llm_v1.py --categories compute/instances networking/vcn
    python scripts/generate_llm_v1.py --resume          # continua de onde parou
    python scripts/generate_llm_v1.py --dry-run         # testa config sem gerar

Pré-requisitos:
    pip install openai pyyaml
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import random
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
# Constantes herdadas do generate_diverse_v2.py
# ---------------------------------------------------------------------------

CATEGORIES = [
    "compute/instances", "compute/scaling", "compute/custom-images",
    "storage/block", "storage/object", "storage/file",
    "networking/vcn", "networking/security", "networking/connectivity",
    "lb/load-balancer",
    "database/autonomous", "database/mysql", "database/postgresql",
    "database/nosql", "database/autonomous-json", "database/exadata",
    "container/oke", "container/instances",
    "serverless/functions", "serverless/api-gateway",
    "security/iam-basics", "security/policies", "security/dynamic-groups",
    "security/federation", "security/vault-secrets", "security/vault-keys",
    "security/encryption", "security/cloud-guard", "security/waf",
    "security/zero-trust", "security/posture-management",
    "migration/aws-compute", "migration/aws-storage", "migration/aws-database",
    "migration/azure-compute", "migration/azure-storage", "migration/azure-database",
    "migration/gcp-compute", "migration/gcp-storage", "migration/gcp-database",
    "migration/onprem-compute", "migration/onprem-storage",
    "migration/onprem-vmware", "migration/onprem-database", "migration/data-transfer",
    "terraform/provider", "terraform/compute", "terraform/storage",
    "terraform/networking", "terraform/load-balancer", "terraform/database",
    "terraform/container", "terraform/serverless", "terraform/security",
    "terraform/observability", "terraform/devops", "terraform/state",
    "observability/logging", "observability/monitoring",
    "observability/stack-monitoring", "observability/apm",
    "troubleshooting/connectivity", "troubleshooting/performance",
    "troubleshooting/authentication", "troubleshooting/database",
    "troubleshooting/compute", "troubleshooting/storage",
    "troubleshooting/oke", "troubleshooting/functions",
    "devops/ci-cd", "devops/resource-manager", "devops/artifacts", "devops/secrets",
    "governance/landing-zone", "governance/compartments", "governance/tagging",
    "governance/budgets-cost", "governance/policies-guardrails",
    "governance/compliance", "governance/audit-readiness",
    "governance/resource-discovery",
    "finops/cost-optimization", "finops/showback-chargeback",
    "finops/rightsizing", "finops/storage-tiering",
    "platform/backup-governance", "platform/sre-operations",
]

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
            f"  Edite o campo provider.api_key com sua chave do OpenRouter."
        )
        sys.exit(1)
    if not cfg.get("models"):
        log.error("Nenhum modelo configurado em 'models'.")
        sys.exit(1)


# ---------------------------------------------------------------------------
# Rotação de modelos com peso
# ---------------------------------------------------------------------------

class ModelRotator:
    """Round-robin ponderado entre modelos configurados."""

    def __init__(self, models: list[dict]):
        # Expande pela weight: [{id: A, weight: 2}, {id: B, weight: 1}] → [A, A, B]
        pool = []
        for m in models:
            pool.extend([m["id"]] * max(1, m.get("weight", 1)))
        random.shuffle(pool)
        self._cycle = cycle(pool)
        self._models = pool
        self._fail_counts: dict[str, int] = defaultdict(int)
        log.info(f"Modelos na rotação: {list(dict.fromkeys(pool))}")

    def next(self) -> str:
        return next(self._cycle)

    def mark_failure(self, model_id: str) -> None:
        self._fail_counts[model_id] += 1

    def stats(self) -> dict:
        return dict(self._fail_counts)


# ---------------------------------------------------------------------------
# Cliente OpenRouter
# ---------------------------------------------------------------------------

class OpenRouterClient:
    def __init__(self, cfg: dict):
        try:
            from openai import OpenAI
        except ImportError:
            log.error("Instale a dependência: pip install openai")
            sys.exit(1)

        provider = cfg["provider"]
        headers = cfg.get("http_headers", {})

        self.client = OpenAI(
            api_key=provider["api_key"],
            base_url=provider["base_url"],
            default_headers=headers,
        )
        self.gen_cfg = cfg["generation"]
        rl = cfg["rate_limit"]
        self.inter_delay = rl.get("inter_request_delay_seconds", 3.5)
        self.retry_attempts = rl.get("retry_attempts", 5)
        self.retry_delay = rl.get("retry_delay_seconds", 4)
        self._last_request_time: float = 0.0

    def _wait_rate_limit(self) -> None:
        elapsed = time.monotonic() - self._last_request_time
        wait = self.inter_delay - elapsed
        if wait > 0:
            time.sleep(wait)

    def call(self, model_id: str, system_prompt: str, user_prompt: str) -> str | None:
        """Chama o modelo e retorna o texto gerado, ou None em caso de falha."""
        self._wait_rate_limit()
        for attempt in range(1, self.retry_attempts + 1):
            try:
                self._last_request_time = time.monotonic()
                response = self.client.chat.completions.create(
                    model=model_id,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user",   "content": user_prompt},
                    ],
                    max_tokens=self.gen_cfg.get("max_tokens", 1500),
                    temperature=self.gen_cfg.get("temperature", 0.85),
                )
                return response.choices[0].message.content
            except Exception as exc:
                wait = self.retry_delay * (2 ** (attempt - 1))  # exponential backoff
                log.warning(
                    f"Tentativa {attempt}/{self.retry_attempts} falhou "
                    f"({model_id}): {exc}. Aguardando {wait:.0f}s..."
                )
                time.sleep(wait)
        return None


# ---------------------------------------------------------------------------
# Geração de prompts
# ---------------------------------------------------------------------------

SYSTEM_PROMPT_TEMPLATE = (
    "Você é um especialista sênior em Oracle Cloud Infrastructure (OCI). "
    "Responda SEMPRE em português brasileiro. "
    "Suas respostas devem incluir: comandos OCI CLI corretos, exemplos de código "
    "Python SDK ou Terraform quando relevante, boas práticas e considerações de segurança. "
    "Use formatação markdown com blocos de código. Seja técnico e preciso."
)


def build_user_prompt(category: str, difficulty: str) -> tuple[str, str]:
    """Gera um par (pergunta, prompt_completo) contextualizado."""
    company   = random.choice(COMPANIES)
    persona   = random.choice(PERSONAS)
    constraint = random.choice(CONSTRAINTS)
    lifecycle  = random.choice(LIFECYCLE_STAGES)
    intent    = random.choice(QUESTION_INTENTS)

    # Pergunta natural baseada na categoria
    service = category.split("/")[-1].replace("-", " ").replace("_", " ")
    domain  = category.split("/")[0]

    question = (
        f"Na {company}, sou {persona} responsável por {service} no ambiente de {lifecycle}. "
        f"Restrição: {constraint}. "
        f"Pergunta ({difficulty}): {intent} {service} na OCI de forma eficiente e segura?"
    )

    prompt = (
        f"{question}\n\n"
        f"Por favor, inclua na sua resposta:\n"
        f"1. Explicação do conceito e quando usar\n"
        f"2. Comando(s) OCI CLI completos e funcionais\n"
        f"3. Trecho de código Python SDK ou bloco Terraform (se aplicável)\n"
        f"4. Pelo menos uma boa prática ou ponto de atenção\n"
        f"Categoria OCI: {category} | Dificuldade: {difficulty}"
    )
    return question, prompt


def build_example(
    category: str,
    question: str,
    answer: str,
    model_id: str,
    difficulty: str,
) -> dict:
    """Monta o exemplo no formato JSONL do projeto."""
    # Deriva o system prompt por categoria (mesmo padrão do generate_diverse_v2.py)
    system_content = SYSTEM_PROMPT_TEMPLATE

    return {
        "messages": [
            {"role": "system",    "content": system_content},
            {"role": "user",      "content": question},
            {"role": "assistant", "content": answer},
        ],
        "metadata": {
            "category":   category,
            "difficulty": difficulty,
            "source":     "llm_generated",
            "model":      model_id,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        },
    }


# ---------------------------------------------------------------------------
# Checkpoint
# ---------------------------------------------------------------------------

class Checkpoint:
    def __init__(self, path: Path):
        self.path = path
        self._data: dict = self._load()

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

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "w") as f:
            json.dump(self._data, f, indent=2)

    def get_category_count(self, category: str) -> int:
        return self._data["per_category"].get(category, 0)

    def increment(self, category: str) -> None:
        self._data["per_category"][category] = self.get_category_count(category) + 1
        self._data["total_generated"] = sum(self._data["per_category"].values())

    @property
    def total(self) -> int:
        return self._data["total_generated"]

    def reset(self) -> None:
        self._data = {"total_generated": 0, "per_category": {}}
        if self.path.exists():
            self.path.unlink()
        log.info("Checkpoint resetado.")


# ---------------------------------------------------------------------------
# Pipeline principal
# ---------------------------------------------------------------------------

class DatasetGenerator:
    def __init__(self, cfg: dict, categories: list[str] | None = None):
        self.cfg        = cfg
        self.gen_cfg    = cfg["generation"]
        self.client     = OpenRouterClient(cfg)
        self.rotator    = ModelRotator(cfg["models"])
        self.output_dir = Path(self.gen_cfg["output_dir"])
        self.checkpoint = Checkpoint(Path(self.gen_cfg["checkpoint_file"]))
        self.categories = categories or CATEGORIES
        self.examples_per_cat = self.gen_cfg.get("examples_per_category", 15)
        self.checkpoint_every = self.gen_cfg.get("checkpoint_every", 50)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _output_file(self, category: str) -> Path:
        safe = category.replace("/", "_")
        return self.output_dir / f"{safe}.jsonl"

    def run(self, resume: bool = True) -> None:
        if not resume:
            self.checkpoint.reset()

        total_target = len(self.categories) * self.examples_per_cat
        log.info(
            f"Iniciando geração: {len(self.categories)} categorias × "
            f"{self.examples_per_cat} exemplos = {total_target} total.\n"
            f"  Já gerados (checkpoint): {self.checkpoint.total}"
        )

        generated_since_save = 0
        total_generated = 0
        total_failed = 0

        for category in self.categories:
            already = self.checkpoint.get_category_count(category)
            remaining = self.examples_per_cat - already
            if remaining <= 0:
                log.info(f"  [{category}] já completa ({already}/{self.examples_per_cat}), pulando.")
                total_generated += already
                continue

            log.info(f"  [{category}] gerando {remaining} exemplos (já tem {already})...")
            out_file = self._output_file(category)

            with open(out_file, "a", encoding="utf-8") as fout:
                for i in range(remaining):
                    difficulty = random.choice(DIFFICULTIES)
                    question, prompt = build_user_prompt(category, difficulty)
                    model_id = self.rotator.next()

                    answer = self.client.call(
                        model_id=model_id,
                        system_prompt=SYSTEM_PROMPT_TEMPLATE,
                        user_prompt=prompt,
                    )

                    if answer is None:
                        self.rotator.mark_failure(model_id)
                        total_failed += 1
                        log.warning(f"    Falha #{total_failed} em {category} ({model_id}), pulando exemplo.")
                        continue

                    example = build_example(category, question, answer, model_id, difficulty)
                    fout.write(json.dumps(example, ensure_ascii=False) + "\n")
                    fout.flush()

                    self.checkpoint.increment(category)
                    total_generated += 1
                    generated_since_save += 1

                    if generated_since_save >= self.checkpoint_every:
                        self.checkpoint.save()
                        generated_since_save = 0
                        log.info(
                            f"    Checkpoint salvo — total gerado até agora: "
                            f"{self.checkpoint.total}/{total_target}"
                        )

                    # Progress inline
                    pct = (self.checkpoint.total / total_target) * 100
                    print(
                        f"\r  Progresso: {self.checkpoint.total}/{total_target} "
                        f"({pct:.1f}%) | Falhas: {total_failed} | Modelo: {model_id[-30:]}   ",
                        end="",
                        flush=True,
                    )

        self.checkpoint.save()
        print()  # nova linha após progresso
        self._print_summary(total_generated, total_failed, total_target)

    def _print_summary(self, generated: int, failed: int, target: int) -> None:
        log.info("=" * 60)
        log.info("GERAÇÃO CONCLUÍDA")
        log.info("=" * 60)
        log.info(f"  Exemplos gerados : {generated}")
        log.info(f"  Falhas           : {failed}")
        log.info(f"  Meta             : {target}")
        log.info(f"  Taxa de sucesso  : {generated / max(generated + failed, 1) * 100:.1f}%")
        log.info(f"  Saída            : {self.output_dir}/")
        log.info("")
        log.info("Próximos passos:")
        log.info("  bash scripts/prepare_data.sh   # valida, limpa, deduplica e gera splits")
        if self.rotator.stats():
            log.info(f"  Falhas por modelo: {self.rotator.stats()}")


# ---------------------------------------------------------------------------
# Dry-run
# ---------------------------------------------------------------------------

def dry_run(cfg: dict) -> None:
    """Valida a config e testa 1 request real."""
    log.info("=== DRY RUN ===")
    log.info(f"  Provider  : {cfg['provider']['name']}")
    log.info(f"  Base URL  : {cfg['provider']['base_url']}")
    log.info(f"  Modelos   : {[m['id'] for m in cfg['models']]}")
    log.info(f"  Output dir: {cfg['generation']['output_dir']}")
    log.info(f"  Meta      : {cfg['generation']['target_examples']} exemplos")

    log.info("\nTestando 1 request real com o primeiro modelo...")
    client = OpenRouterClient(cfg)
    model_id = cfg["models"][0]["id"]
    result = client.call(
        model_id=model_id,
        system_prompt=SYSTEM_PROMPT_TEMPLATE,
        user_prompt="Explique em 2 frases o que é uma VCN na OCI.",
    )
    if result:
        log.info(f"  ✅ Request OK! Resposta ({len(result)} chars):\n{result[:300]}...")
    else:
        log.error("  ❌ Request falhou. Verifique sua API key e conexão.")
        sys.exit(1)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Gera dataset OCI via LLM (OpenRouter ou compatível)"
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
        help="Categorias específicas a gerar (ex: compute/instances networking/vcn)",
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
        help="Valida config e testa 1 request sem gerar dataset",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cfg  = load_config(args.config)

    if args.dry_run:
        dry_run(cfg)
        return

    generator = DatasetGenerator(
        cfg=cfg,
        categories=args.categories,
    )
    generator.run(resume=args.resume)


if __name__ == "__main__":
    main()
