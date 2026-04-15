#!/usr/bin/env python3
"""Generate OCI training examples using LLM with Agentic Context.

This script evolves from generate_llm_v2.py by adding:
1. Technical Grounding: Injects real OCI CLI/SDK/Terraform metadata.
2. Structural Enforcement: Forces specific response types (Troubleshooting, Architecture, etc.).
3. Quality Rule Integration: Direct mapping from quality-rules.md to system prompts.
4. Rich Scenarios: Dynamic combination of Persona, Constraint, and Lifecycle.

Usage:
    python scripts/generate_llm_agentic.py --categories compute/instances
"""

import asyncio
import json
import logging
import os
import random
import re
import sys
import yaml
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, List, Dict

# Import technical grounding
try:
    from oci_technical_metadata import OCI_CLI_COMMANDS, OCI_PYTHON_SDK, OCI_TERRAFORM_RESOURCES
except ImportError:
    # If running from project root, adjust sys.path
    sys.path.append(str(Path(__file__).parent))
    from oci_technical_metadata import OCI_CLI_COMMANDS, OCI_PYTHON_SDK, OCI_TERRAFORM_RESOURCES

# Setup Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

# --- Paths ---
DOCS_DIR = Path("docs")
TAXONOMY_FILE = DOCS_DIR / "taxonomy.md"
QUALITY_FILE = DOCS_DIR / "quality-rules.md"
OUTPUT_DIR = Path("data/curated_llm")

# --- Constants for Diversity ---
COMPANIES = ["TechCorp Brasil", "DataFlow Solutions", "CloudNative Inc", "FinServe Digital", "RetailMax Online", "HealthTech Systems"]
PERSONAS = ["cloud architect", "platform engineer", "SRE", "security lead", "DBA", "FinOps analyst", "DevOps engineer"]
CONSTRAINTS = ["sem downtime", "com budget limitado", "ambiente legado", "multi-região", "mínimo privilégio"]
STRUCTURES = ["step_by_step", "troubleshooting", "architecture", "code_first", "best_practices", "cost_analysis", "migration"]

# --- Loaders ---

def load_taxonomy() -> Dict[str, Any]:
    if not TAXONOMY_FILE.exists(): return {}
    content = TAXONOMY_FILE.read_text()
    categories = re.findall(r"#### ([\w/.-]+)", content)
    return {cat: {} for cat in categories}

def load_quality_rules() -> str:
    if not QUALITY_FILE.exists(): return ""
    return QUALITY_FILE.read_text()

# --- LLM Client ---

class OCIAgentGenerator:
    def __init__(self, config_path: Path):
        with open(config_path) as f:
            self.config = yaml.safe_load(f)
        
        try:
            from openai import AsyncOpenAI
            self.client = AsyncOpenAI(
                api_key=self.config["provider"]["api_key"],
                base_url=self.config["provider"]["base_url"]
            )
        except ImportError:
            log.error("Dependência 'openai' não encontrada. Instale com: pip install openai")
            sys.exit(1)

    def _get_technical_grounding(self, category: str) -> str:
        cli = OCI_CLI_COMMANDS.get(category, {})
        sdk = OCI_PYTHON_SDK.get(category, {})
        tf = OCI_TERRAFORM_RESOURCES.get(category, "")
        
        grounding = []
        if cli: grounding.append(f"CLI Reference: {json.dumps(cli)}")
        if sdk: grounding.append(f"SDK Reference: {json.dumps(sdk)}")
        if tf: grounding.append(f"Terraform Resource: {tf}")
        
        return "\n".join(grounding)

    async def generate_batch(self, category: str, batch_size: int, rules: str) -> List[Dict]:
        structure = random.choice(STRUCTURES)
        persona = random.choice(PERSONAS)
        scenario = random.choice(COMPANIES)
        constraint = random.choice(CONSTRAINTS)
        grounding = self._get_technical_grounding(category)

        system_prompt = f"""Você é um AGENTE ESPECIALISTA EM OCI encarregado de gerar um dataset de treinamento.

=== REGRAS DE QUALIDADE (ESTRITAS) ===
{rules}

=== CONHECIMENTO TÉCNICO DE REFERÊNCIA ===
{grounding}

=== CONTEXTO DA GERAÇÃO ===
- Categoria OCI: {category}
- Estrutura de Resposta: {structure}
- Persona: {persona}
- Empresa: {scenario}
- Restrição: {constraint}

=== TAREFA ===
Gere {batch_size} exemplos. Cada 'answer' deve seguir a estrutura '{structure}' e ser técnica, exaustiva e correta.
AUTO-CRÍTICA: Antes de finalizar, valide se preços/limites estão marcados como [MUTABLE].

Retorne um JSON no formato:
{{
  "examples": [
    {{
      "question": "...",
      "answer": "...",
      "metadata": {{ "category": "{category}", "structure": "{structure}", "persona": "{persona}" }}
    }}
  ]
}}
"""

        try:
            response = await self.client.chat.completions.create(
                model=self.config["models"][0]["id"],
                messages=[{"role": "system", "content": system_prompt},
                          {"role": "user", "content": "Gere os exemplos agora."}],
                response_format={"type": "json_object"}
            )
            data = json.loads(response.choices[0].message.content)
            return data.get("examples", [])
        except Exception as e:
            log.error(f"Erro na geração: {e}")
            return []

async def main():
    config_path = Path("config/llm_provider.yaml")
    if not config_path.exists(): config_path = Path("config/llm_provider_genai.yaml")

    generator = OCIAgentGenerator(config_path)
    taxonomy = load_taxonomy()
    rules = load_quality_rules()
    
    categories = list(taxonomy.keys())
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    log.info(f"Agente pronto. Iniciando geração...")

    # Exemplo: Processar apenas as primeiras 2 categorias para teste
    for cat in categories[:2]:
        log.info(f"Agente trabalhando em: {cat}")
        batch = await generator.generate_batch(cat, 3, rules)
        
        if batch:
            file_name = cat.replace("/", "_") + ".jsonl"
            with open(OUTPUT_DIR / file_name, "a", encoding="utf-8") as f:
                for item in batch:
                    f.write(json.dumps(item, ensure_ascii=False) + "\n")
            log.info(f"  - {len(batch)} exemplos gerados com sucesso.")

if __name__ == "__main__":
    asyncio.run(main())
