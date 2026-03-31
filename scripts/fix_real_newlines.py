#!/usr/bin/env python3
"""
Fix files with real newlines in JSON strings.
The LLM outputs actual line breaks instead of \n escape sequences.
"""

import json
import re
from pathlib import Path
from typing import Optional

CURATED_DIR = Path("data/curated")


def fix_real_newlines_in_content(line: str) -> Optional[str]:
    """
    Find the content field and escape real newlines within it.
    """
    line = line.strip()
    if not line:
        return None

    try:
        # First try: direct parse (might work if already fixed)
        json.loads(line)
        return line
    except:
        pass

    # The problem: real newlines in the assistant content
    # Pattern: find "content": "..." and escape newlines inside

    # Strategy: Reconstruct the JSON by finding the structure
    # {"messages": [...{"role": "assistant", "content": "ACTUAL CONTENT"}, ...], "metadata": {...}}

    # Find the position of "content": " for the assistant role
    # and the position of }, "metadata" or }, ]}

    # Let's try a different approach: use regex to find and fix

    # Match the assistant content - from '"content": "' to next major delimiter
    # But this is complex because content can have quotes

    # Simpler: let's try to escape all newlines in the line first
    # Then see if it parses

    # Actually, let me try parsing character by character
    result = []
    i = 0
    in_string = False
    escape_next = False

    while i < len(line):
        char = line[i]

        if escape_next:
            result.append(char)
            escape_next = False
            i += 1
            continue

        if char == "\\" and in_string:
            result.append(char)
            escape_next = True
            i += 1
            continue

        if char == '"' and not escape_next:
            # Toggle string mode
            in_string = not in_string
            result.append(char)
            i += 1
            continue

        if char == "\n" and in_string:
            # Replace real newline with escaped \n
            result.append("\\n")
            i += 1
            continue

        if char == "\r":
            i += 1
            continue

        result.append(char)
        i += 1

    fixed_line = "".join(result)

    # Try to parse
    try:
        data = json.loads(fixed_line)
        return json.dumps(data, ensure_ascii=False)
    except json.JSONDecodeError as e:
        pass

    return None


def add_metadata(line: str, filename: str) -> Optional[str]:
    """Add metadata if missing"""
    try:
        data = json.loads(line)

        if "metadata" not in data:
            base = filename.replace(".jsonl", "")
            parts = base.split("-")
            if len(parts) >= 2:
                topic = "-".join(parts[:-1])
                category_map = {
                    "compute-custom-images": "compute/custom-images",
                    "compute-instances": "compute/instances",
                    "compute-scaling": "compute/scaling",
                    "container-instances": "container/instances",
                    "container-oke": "container/oke",
                    "database-autonomous": "database/autonomous",
                    "database-autonomous-json": "database/autonomous-json",
                    "database-exadata": "database/exadata",
                    "database-mysql": "database/mysql",
                    "database-nosql": "database/nosql",
                    "database-postgresql": "database/postgresql",
                    "lb-load-balancer": "lb/load-balancer",
                    "networking-connectivity": "networking/connectivity",
                    "networking-security": "networking/security",
                    "networking-vcn": "networking/vcn",
                    "observability-apm": "observability/apm",
                    "observability-logging": "observability/logging",
                    "observability-monitoring": "observability/monitoring",
                    "observability-stack-monitoring": "observability/stack-monitoring",
                    "security-cloud-guard": "security/cloud-guard",
                    "security-dynamic-groups": "security/dynamic-groups",
                    "security-encryption": "security/encryption",
                    "security-federation": "security/federation",
                    "security-iam-basics": "security/iam-basics",
                    "security-policies": "security/policies",
                    "security-vault-keys": "security/vault-keys",
                    "security-vault-secrets": "security/vault-secrets",
                    "security-waf": "security/waf",
                    "serverless-api-gateway": "serverless/api-gateway",
                    "serverless-functions": "serverless/functions",
                    "storage-block": "storage/block",
                    "storage-file": "storage/file",
                    "storage-object": "storage/object",
                    "terraform-compute": "terraform/compute",
                    "terraform-database": "terraform/database",
                    "terraform-load-balancer": "terraform/load-balancer",
                    "terraform-networking": "terraform/networking",
                    "terraform-provider": "terraform/provider",
                    "terraform-storage": "terraform/storage",
                }
                category = category_map.get(topic, f"unknown/{topic}")
            else:
                category = "unknown/unknown"

            data["metadata"] = {
                "category": category,
                "difficulty": "intermediate",
                "source": "generated",
            }
            return json.dumps(data, ensure_ascii=False)

        return line

    except:
        return None


def process_file(filepath: Path) -> dict:
    """Process a single JSONL file"""
    filename = filepath.name
    lines = []
    stats = {"fixed": 0, "error": 0}

    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            # Try to fix real newlines
            fixed = fix_real_newlines_in_content(line)

            if fixed:
                # Try to add metadata
                with_metadata = add_metadata(fixed, filename)
                if with_metadata:
                    try:
                        # Verify final JSON is valid
                        json.loads(with_metadata)
                        lines.append(with_metadata)
                        stats["fixed"] += 1
                    except:
                        stats["error"] += 1
                        print(f"  ERROR: Final JSON invalid: {filename}")
                else:
                    stats["error"] += 1
                    print(f"  ERROR: Could not add metadata: {filename}")
            else:
                stats["error"] += 1
                print(f"  ERROR: Could not fix: {filename}")

    # Write fixed file
    if stats["fixed"] > 0:
        with open(filepath, "w", encoding="utf-8") as f:
            for line in lines:
                f.write(line + "\n")
        print(f"  ✅ Fixed: {stats['fixed']} entries")
    else:
        print(f"  ⚠️  Could not fix: {filepath.name}")

    return stats


def main():
    print("=" * 60)
    print("Fix Real Newlines in JSONL Files")
    print("=" * 60)

    if not CURATED_DIR.exists():
        print(f"Error: {CURATED_DIR} not found")
        return

    jsonl_files = sorted(CURATED_DIR.glob("*.jsonl"))
    print(f"\nFound {len(jsonl_files)} JSONL files\n")

    total_stats = {"fixed": 0, "error": 0}

    for filepath in jsonl_files:
        print(f"Processing: {filepath.name}")
        stats = process_file(filepath)
        for k, v in stats.items():
            total_stats[k] += v

    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"Total files: {len(jsonl_files)}")
    print(f"Fixed entries: {total_stats['fixed']}")
    print(f"Error entries: {total_stats['error']}")


if __name__ == "__main__":
    main()
