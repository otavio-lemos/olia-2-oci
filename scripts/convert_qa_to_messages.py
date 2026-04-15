#!/usr/bin/env python3
"""
Convert new Q/A format to messages format for MLX-Tune training.

Input format (new):
  {"question": "...", "answer": "...", "metadata": {"category": "...", "difficulty": "..."}}

Output format (messages):
  {"messages": [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}], "metadata": {...}}

Usage:
  python scripts/convert_qa_to_messages.py --input data/all_curated.jsonl --output data/all_curated_messages.jsonl
"""

import json
import argparse
import re
from pathlib import Path
from typing import Dict, Any, List


SYSTEM_PROMPT = """Você é um especialista em Oracle Cloud Infrastructure (OCI). 
Forneça respostas técnicas precisas em Português do Brasil.
Sempre inclua passos específicos, comandos CLI quando aplicável, e referências à documentação oficial.
Use [MUTABLE] para preços e [CHECK DOCS] para limites de serviço."""


def clean_answer(answer: str) -> str:
    """Clean and format answer text."""
    # Remove excessive whitespace
    answer = re.sub(r"\n\n\n+", "\n\n", answer)
    answer = answer.strip()
    return answer


def convert_example(example: Dict[str, Any]) -> Dict[str, Any]:
    """Convert Q/A format to messages format."""
    question = example.get("question", "")
    answer = example.get("answer", "")
    metadata = example.get("metadata", {})

    # Clean answer
    answer = clean_answer(answer)

    # Normalize difficulty to lowercase
    if "difficulty" in metadata and metadata["difficulty"]:
        metadata["difficulty"] = metadata["difficulty"].lower()

    # Normalize persona to lowercase
    if "persona" in metadata and metadata["persona"]:
        metadata["persona"] = metadata["persona"].lower()

    # Ensure metadata has required fields for validation
    if "source" not in metadata:
        metadata["source"] = "generated"
    if "category" not in metadata:
        metadata["category"] = "unknown"
    if "difficulty" not in metadata:
        metadata["difficulty"] = "intermediate"

    # Create messages format
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question},
        {"role": "assistant", "content": answer},
    ]

    return {"messages": messages, "metadata": metadata}


def load_qa_examples(input_path: Path) -> List[Dict[str, Any]]:
    """Load examples from Q/A format JSONL."""
    examples = []
    with open(input_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                try:
                    ex = json.loads(line)
                    if isinstance(ex, dict) and "question" in ex and "answer" in ex:
                        examples.append(ex)
                except json.JSONDecodeError:
                    continue
    return examples


def save_messages_examples(examples: List[Dict[str, Any]], output_path: Path):
    """Save examples in messages format to JSONL."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        for ex in examples:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Convert Q/A format to messages format"
    )
    parser.add_argument("--input", "-i", required=True, help="Input JSONL (Q/A format)")
    parser.add_argument(
        "--output", "-o", required=True, help="Output JSONL (messages format)"
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}")
        return 1

    print(f"Loading examples from {input_path}...")
    examples = load_qa_examples(input_path)
    print(f"Loaded {len(examples)} examples")

    print("Converting to messages format...")
    converted = [convert_example(ex) for ex in examples]
    print(f"Converted {len(converted)} examples")

    print(f"Saving to {output_path}...")
    save_messages_examples(converted, output_path)
    print(f"✅ Done! Output: {output_path}")

    # Show sample
    if converted:
        print("\n--- Sample output ---")
        sample = converted[0]
        print(f"Messages count: {len(sample['messages'])}")
        print(f"Metadata: {sample['metadata']}")

    return 0


if __name__ == "__main__":
    exit(main())
