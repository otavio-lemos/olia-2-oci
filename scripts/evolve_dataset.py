#!/usr/bin/env python3
"""Evolve synthetic OCI examples into high-quality training data using Gemini Native SDK.

Usage:
    python scripts/evolve_dataset.py --file data/curated/compute-instances.jsonl --limit 10
"""

import argparse
import json
import logging
import os
import sys
import time
from pathlib import Path
from datetime import datetime, timezone

import yaml
import google.generativeai as genai

# Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

def load_config(path: Path) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)

class DatasetEvolver:
    def __init__(self, cfg: dict):
        provider = cfg["provider"]
        genai.configure(api_key=provider["api_key"])
        self.gen_cfg = cfg["generation"]
        self.output_dir = Path("data/evolved")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Modelo principal
        self.model_id = cfg["models"][0]["id"].replace("models/", "")
        self.model = genai.GenerativeModel(
            model_name=self.model_id,
            system_instruction="""Você é um Arquiteto Sênior de OCI. 
Sua tarefa é evoluir exemplos de treinamento sintéticos.
1. Melhore a redação para parecer natural e profissional.
2. Mantenha os comandos OCI CLI e referências técnicas exatas.
3. Adicione uma breve explicação do "porquê" da solução se estiver faltando.
4. Garanta que a resposta seja completa e útil para treinamento de IA.
5. Retorne APENAS um objeto JSON válido com 'question' e 'answer'."""
        )

    def evolve_example(self, raw_example: dict) -> dict | None:
        prompt = f"""Evolua o seguinte exemplo de treinamento OCI:
{json.dumps(raw_example, ensure_ascii=False)}

RETORNE APENAS O JSON:
{{
  "question": "pergunta evoluída",
  "answer": "resposta evoluída e detalhada"
}}"""
        
        for attempt in range(3):
            try:
                response = self.model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=4096,
                        temperature=0.7,
                        response_mime_type="application/json",
                    )
                )
                evolved = json.loads(response.text)
                
                # Monta o formato final de treino
                return {
                    "messages": [
                        {"role": "system", "content": "Você é um especialista sênior em Oracle Cloud Infrastructure (OCI)."},
                        {"role": "user", "content": evolved["question"]},
                        {"role": "assistant", "content": evolved["answer"]}
                    ],
                    "metadata": {
                        "original_category": raw_example.get("metadata", {}).get("category"),
                        "source": "evolved_synthetic",
                        "model": self.model_id,
                        "evolved_at": datetime.now(timezone.utc).isoformat()
                    }
                }
            except Exception as e:
                log.warning(f"Falha na evolução (tentativa {attempt+1}): {e}")
                time.sleep(2)
        return None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", type=Path, required=True, help="Arquivo .jsonl original")
    parser.add_argument("--limit", type=int, default=None, help="Limite de exemplos a processar")
    parser.add_argument("--config", type=Path, default=Path("config/llm_provider.yaml"))
    args = parser.parse_args()

    cfg = load_config(args.config)
    evolver = DatasetEvolver(cfg)
    
    out_file = Path("data/evolved") / args.file.name
    
    log.info(f"Evoluindo {args.file} -> {out_file}")
    
    count = 0
    with open(args.file, "r") as fin, open(out_file, "a") as fout:
        for line in fin:
            if args.limit and count >= args.limit:
                break
                
            raw = json.loads(line)
            evolved = evolver.evolve_example(raw)
            
            if evolved:
                fout.write(json.dumps(evolved, ensure_ascii=False) + "\n")
                fout.flush()
                count += 1
                print(f"\rProcessados: {count}", end="", flush=True)
            
            # Pequeno delay para respeitar RPM do Free Tier
            time.sleep(4)

    print(f"\nConcluído! {count} exemplos evoluídos.")

if __name__ == "__main__":
    main()
