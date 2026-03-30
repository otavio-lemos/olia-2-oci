#!/usr/bin/env python3
import json
import os
import sys
from pathlib import Path

SYSTEM_PROMPT = "Você é um arquiteto especialista em OCI, migração multicloud e modernização on-premises. Seja técnico, objetivo e não invente serviços inexistentes. Sempre inclua passos, riscos e alternativas quando aplicável."


def convert_file(input_path, output_path):
    with open(input_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    converted = []
    stats = {"converted": 0, "skipped": 0, "errors": 0}

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if line.startswith("#"):
            converted.append(line + "\n")
            continue

        try:
            data = json.loads(line)

            if "messages" in data:
                converted.append(json.dumps(data, ensure_ascii=False) + "\n")
                stats["skipped"] += 1
                continue

            question = data.get("question", data.get("Q", ""))
            answer = data.get("answer", data.get("A", ""))

            if not question or not answer:
                stats["skipped"] += 1
                continue

            chat_format = {
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": question},
                    {"role": "assistant", "content": answer},
                ]
            }

            if "metadata" in data:
                chat_format["metadata"] = data["metadata"]

            converted.append(json.dumps(chat_format, ensure_ascii=False) + "\n")
            stats["converted"] += 1

        except json.JSONDecodeError:
            stats["errors"] += 1
            converted.append(line + "\n")

    with open(output_path, "w", encoding="utf-8") as f:
        f.writelines(converted)

    return stats


def main():
    input_dir = Path("data/curated")
    output_dir = Path("data/curated/fixed")
    output_dir.mkdir(parents=True, exist_ok=True)

    files = list(input_dir.glob("*.jsonl"))
    print(f"Found {len(files)} files to convert\n")

    total_stats = {"converted": 0, "skipped": 0, "errors": 0, "files": 0}

    for input_file in sorted(files):
        stats = convert_file(input_file, output_dir / input_file.name)
        total_stats["converted"] += stats["converted"]
        total_stats["skipped"] += stats["skipped"]
        total_stats["errors"] += stats["errors"]
        total_stats["files"] += 1

        status = "✓" if stats["errors"] == 0 else "⚠"
        print(
            f"{status} {input_file.name}: {stats['converted']} converted, {stats['skipped']} skipped, {stats['errors']} errors"
        )

    print(f"\n{'=' * 50}")
    print(f"TOTAL: {total_stats['files']} files")
    print(f"Converted: {total_stats['converted']} Q&A → chat")
    print(f"Skipped: {total_stats['skipped']} (already chat or empty)")
    print(f"Errors: {total_stats['errors']}")
    print(f"\nOutput: {output_dir}/")
    print(f"\nNext: python scripts/validate_jsonl.py {output_dir}/")


if __name__ == "__main__":
    main()
