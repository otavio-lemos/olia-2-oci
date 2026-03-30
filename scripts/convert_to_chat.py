#!/usr/bin/env python3
"""Convert Q&A JSONL to chat format JSONL."""

import json
import sys
from pathlib import Path

SYSTEM_PROMPT = """Você é um arquiteto especialista em OCI, migração multicloud e modernização on-premises. Seja técnico, objetivo e não invente serviços inexistentes. Sempre inclua passos, riscos e alternativas quando aplicável."""


def convert_to_chat(qa_file: Path) -> list:
    results = []
    with open(qa_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                qa = json.loads(line)
                chat = {
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": qa.get("question", "")},
                        {"role": "assistant", "content": qa.get("answer", "")},
                    ],
                    "metadata": {
                        "category": qa.get("category", "unknown"),
                        "difficulty": qa.get("difficulty", "intermediate"),
                        "source": qa.get("source", "generated"),
                    },
                }
                results.append(chat)
    return results


def save_chat_format(examples: list, output_file: Path):
    with open(output_file, "w", encoding="utf-8") as f:
        for ex in examples:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")


def main():
    curated_dir = Path("data/curated")
    output_dir = Path("data/curated")

    for jsonl_file in curated_dir.glob("*.jsonl"):
        print(f"Processing {jsonl_file.name}...")
        examples = convert_to_chat(jsonl_file)

        output_name = jsonl_file.stem + "-chat.jsonl"
        output_path = output_dir / output_name

        save_chat_format(examples, output_path)
        print(f"  Saved {len(examples)} examples to {output_name}")

        # Also save as the original for build_dataset.py
        backup_name = jsonl_file.stem + "-orig.jsonl"
        backup_path = output_dir / backup_name
        with open(backup_path, "w", encoding="utf-8") as f:
            for line in open(jsonl_file, "r"):
                if line.strip():
                    f.write(line)


if __name__ == "__main__":
    main()
