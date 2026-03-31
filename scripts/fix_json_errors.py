#!/usr/bin/env python3
"""
Repair JSONL files with escaping issues.
Tries to fix common JSON formatting problems.
"""

import json
import re
import os
from pathlib import Path
from typing import Optional, Tuple

CURATED_DIR = Path("data/curated")


def try_fix_json(line: str, filename: str) -> Tuple[bool, Optional[str]]:
    """
    Try to fix common JSON escaping issues.
    Returns (success, fixed_line or None)
    """
    line = line.strip()
    if not line:
        return True, None

    try:
        # First try: direct parse
        json.loads(line)
        return True, None  # Already valid
    except json.JSONDecodeError:
        pass

    # Try to repair common issues

    # Issue 1: Missing comma after "content": "value"
    # Pattern: "content": "value" "role"
    pattern = r'("content":\s*"[^"]*)"(\s*"role")'
    fixed = re.sub(pattern, r"\1,\2", line)
    if try_parse(fixed):
        return True, fixed

    # Issue 2: Newline in string (not escaped)
    # This is hard to fix reliably - skip
    # Issue 3: Unescaped quotes in content
    # Skip - too complex to fix reliably

    # Issue 4: Multiple JSON objects - take first valid one
    # Try to extract first complete JSON
    lines = line.split("}{")
    if len(lines) > 1:
        for i in range(len(lines)):
            if i == 0:
                test = lines[i] + "}"
            elif i == len(lines) - 1:
                test = "{" + lines[i]
            else:
                test = "{" + lines[i] + "}"
            if try_parse(test):
                return True, test

    return False, None


def try_parse(s: str) -> bool:
    """Try to parse JSON"""
    try:
        json.loads(s)
        return True
    except:
        return False


def extract_and_fix(line: str) -> Optional[str]:
    """Extract and fix JSON from a potentially malformed line"""
    line = line.strip()
    if not line:
        return None

    # Try direct parse first
    if try_parse(line):
        return line

    # Try to find JSON pattern at start
    # Look for {"messages": ...}
    match = re.match(r"^\s*\{", line)
    if not match:
        return None

    # Try to extract valid JSON by finding matching braces
    depth = 0
    in_string = False
    escape_next = False

    for i, char in enumerate(line):
        if escape_next:
            escape_next = False
            continue

        if char == "\\" and in_string:
            escape_next = True
            continue

        if char == '"' and not escape_next:
            in_string = not in_string
            continue

        if not in_string:
            if char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    # Found complete JSON
                    potential = line[: i + 1]
                    if try_parse(potential):
                        return potential
                    break

    return None


def add_metadata(line: str, filename: str) -> Optional[str]:
    """Add metadata if missing"""
    try:
        data = json.loads(line)

        if "metadata" not in data:
            # Extract category from filename
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
    stats = {"valid": 0, "fixed": 0, "error": 0, "skipped": 0}

    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            # Try to extract and fix JSON
            fixed = extract_and_fix(line)

            if fixed:
                # Try to add metadata
                with_metadata = add_metadata(fixed, filename)
                if with_metadata:
                    # Verify final JSON is valid
                    if try_parse(with_metadata):
                        lines.append(with_metadata)
                        stats["fixed"] += 1
                    else:
                        stats["error"] += 1
                        print(f"  ERROR: Final JSON invalid: {filename}")
                else:
                    stats["error"] += 1
                    print(f"  ERROR: Could not add metadata: {filename}")
            else:
                stats["error"] += 1
                print(f"  ERROR: Could not extract JSON: {filename}")

    # Write fixed file
    if stats["fixed"] > 0 or stats["error"] == 0:
        with open(filepath, "w", encoding="utf-8") as f:
            for line in lines:
                f.write(line + "\n")
        print(f"  ✅ Fixed: {stats['fixed']} entries")
    else:
        print(f"  ⚠️  Could not fix: {filepath.name}")

    return stats


def main():
    print("=" * 60)
    print("JSONL Repair Tool - Fix escaping and metadata")
    print("=" * 60)

    if not CURATED_DIR.exists():
        print(f"Error: {CURATED_DIR} not found")
        return

    jsonl_files = sorted(CURATED_DIR.glob("*.jsonl"))
    print(f"\nFound {len(jsonl_files)} JSONL files\n")

    total_stats = {"valid": 0, "fixed": 0, "error": 0, "skipped": 0}

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

    if total_stats["fixed"] > 0:
        print(f"\n✅ Repaired {total_stats['fixed']} entries")
    if total_stats["error"] > 0:
        print(f"\n⚠️  {total_stats['error']} entries could not be repaired")
        print("   These files need to be regenerated")


if __name__ == "__main__":
    main()
