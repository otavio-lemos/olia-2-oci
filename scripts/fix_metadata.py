#!/usr/bin/env python3
"""
Validate and fix metadata in JSONL files.
Ensures all files have the required metadata field.
"""

import json
import os
import sys
import re
from pathlib import Path
from typing import Dict, List, Tuple

CURATED_DIR = Path("data/curated")

CATEGORY_MAP = {
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


def extract_category(filename: str) -> str:
    """Extract category from filename like compute-instances-001.jsonl"""
    base = filename.replace(".jsonl", "")
    parts = base.split("-")
    if len(parts) >= 2:
        topic = "-".join(parts[:-1])
        return CATEGORY_MAP.get(topic, f"unknown/{topic}")
    return "unknown/unknown"


def validate_jsonl_line(line: str, filename: str) -> Tuple[bool, str, Dict]:
    """Validate a single JSONL line"""
    try:
        data = json.loads(line)

        if "messages" not in data:
            return False, "Missing 'messages' field", data

        if "metadata" not in data:
            category = extract_category(filename)
            data["metadata"] = {
                "category": category,
                "difficulty": "intermediate",
                "source": "generated",
            }
            return True, "Added missing metadata", data

        metadata = data["metadata"]
        if "category" not in metadata:
            metadata["category"] = extract_category(filename)
        if "difficulty" not in metadata:
            metadata["difficulty"] = "intermediate"
        if "source" not in metadata:
            metadata["source"] = "generated"

        return True, "OK", data

    except json.JSONDecodeError as e:
        return False, f"Invalid JSON: {e}", None


def process_file(filepath: Path) -> Tuple[int, int, int]:
    """Process a single JSONL file"""
    valid_count = 0
    fixed_count = 0
    error_count = 0

    filename = filepath.name
    new_lines = []

    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            is_valid, message, data = validate_jsonl_line(line, filename)

            if data is None:
                error_count += 1
                print(f"  ERROR: {message}")
                continue

            if is_valid and message == "OK":
                valid_count += 1
                new_lines.append(line)
            elif is_valid and message == "Added missing metadata":
                fixed_count += 1
                new_lines.append(json.dumps(data, ensure_ascii=False))

    if fixed_count > 0:
        with open(filepath, "w", encoding="utf-8") as f:
            for line in new_lines:
                f.write(line + "\n")
        print(f"  Fixed {fixed_count} entries, kept {valid_count} valid")

    return valid_count, fixed_count, error_count


def main():
    print("=" * 60)
    print("JSONL Metadata Validator and Fixer")
    print("=" * 60)

    if not CURATED_DIR.exists():
        print(f"Error: {CURATED_DIR} not found")
        sys.exit(1)

    jsonl_files = sorted(CURATED_DIR.glob("*.jsonl"))
    print(f"\nFound {len(jsonl_files)} JSONL files\n")

    total_valid = 0
    total_fixed = 0
    total_errors = 0

    for filepath in jsonl_files:
        print(f"Processing: {filepath.name}")
        valid, fixed, errors = process_file(filepath)
        total_valid += valid
        total_fixed += fixed
        total_errors += errors

    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"Total files processed: {len(jsonl_files)}")
    print(f"Valid entries: {total_valid}")
    print(f"Fixed entries: {total_fixed}")
    print(f"Error entries: {total_errors}")

    if total_fixed > 0:
        print(f"\n✅ Fixed {total_fixed} entries")
    if total_errors > 0:
        print(f"\n⚠️  {total_errors} entries have errors")
    if total_fixed == 0 and total_errors == 0:
        print("\n✅ All files are valid!")


if __name__ == "__main__":
    main()
