#!/usr/bin/env python3
"""
Fix all escaping issues in JSONL files.
Handles: \\n -> \n, real newlines in strings, missing metadata.
"""

import json
from pathlib import Path
from typing import Optional

CURATED_DIR = Path("data/curated")


def fix_escaping(line: str) -> Optional[str]:
    """
    Fix multiple escaping issues:
    1. \\n (double backslash) -> \n (single)
    2. Real newlines in strings -> \n
    """
    line = line.strip()
    if not line:
        return None

    # First try direct parse
    try:
        json.loads(line)
        return line
    except:
        pass

    # Work on bytes level for more control
    result = []
    i = 0
    in_string = False
    escape_count = 0

    while i < len(line):
        char = line[i]

        if char == "\\" and not in_string:
            # Outside string - could be start of escape
            escape_count = 1
            result.append(char)
            i += 1
            continue
        elif char == "\\" and in_string:
            # Inside string - handle escaping
            if escape_count > 0:
                # Already have escape, this is second backslash
                escape_count += 1
                result.append(char)
                i += 1

                # Check what follows
                if i < len(line):
                    next_char = line[i]
                    if next_char == "n" and escape_count == 2:
                        # \\n -> replace with \n
                        result = result[:-3]  # remove \\n
                        result.append("\\n")  # add \n
                        escape_count = 0
                        i += 1  # skip the 'n'
                        continue
                    elif next_char == "\\" and escape_count >= 2:
                        # \\\ or more - normalize to \\
                        result = result[:-escape_count]
                        result.append("\\\\")
                        escape_count = 0
                        i += 1
                        continue
            else:
                escape_count = 1
                result.append(char)
                i += 1
            continue

        if char == '"' and (i == 0 or line[i - 1] != "\\"):
            # Quote not escaped
            in_string = not in_string
            escape_count = 0

        if char == "\n" and in_string:
            # Real newline in string - escape it
            result = result[:-1] if result and result[-1] == "\\" else result
            result.append("\\n")
            i += 1
            continue

        if char == "\r":
            i += 1
            continue

        result.append(char)
        i += 1

    fixed_line = "".join(result)

    try:
        data = json.loads(fixed_line)
        return json.dumps(data, ensure_ascii=False)
    except json.JSONDecodeError as e:
        # Try alternative: simpler fix - just replace all \\n with \n
        alt = line.replace("\\\\n", "\\n").replace("\\\\r", "")
        try:
            data = json.loads(alt)
            return json.dumps(data, ensure_ascii=False)
        except:
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

            # Try to fix escaping
            fixed = fix_escaping(line)

            if fixed:
                # Try to add metadata
                with_metadata = add_metadata(fixed, filename)
                if with_metadata:
                    try:
                        json.loads(with_metadata)
                        lines.append(with_metadata)
                        stats["fixed"] += 1
                    except:
                        stats["error"] += 1
                        print(f"  ERROR: Final invalid: {filename}")
                else:
                    stats["error"] += 1
            else:
                stats["error"] += 1
                if stats["error"] == 1:
                    print(f"  ERROR: Could not fix: {filename}")

    if stats["fixed"] > 0:
        with open(filepath, "w", encoding="utf-8") as f:
            for line in lines:
                f.write(line + "\n")
        if stats["error"] == 0:
            print(f"  ✅ Fixed: {stats['fixed']} entries")
        else:
            print(f"  ⚠️  Fixed {stats['fixed']}, errors {stats['error']}")

    return stats


def main():
    print("=" * 60)
    print("Universal JSONL Fixer")
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
