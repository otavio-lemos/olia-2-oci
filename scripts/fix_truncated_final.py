#!/usr/bin/env python3
"""Fix all remaining broken JSONL files."""

import json
from pathlib import Path

CURATED_DIR = Path("data/curated")


def get_category(filename: str) -> str:
    base = filename.replace(".jsonl", "")
    parts = base.split("-")
    if len(parts) >= 2:
        topic = "-".join(parts[:-1])
        cat_map = {
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
        return cat_map.get(topic, f"unknown/{topic}")
    return "unknown/unknown"


def fix_file(filepath: Path) -> bool:
    filename = filepath.name
    category = get_category(filename)
    md = json.dumps(
        {"category": category, "difficulty": "intermediate", "source": "generated"}
    )

    with open(filepath, "r", encoding="utf-8") as f:
        raw = f.read().strip()
    if not raw:
        return False

    # Fix double backslashes
    fixed = raw.replace("\\\\n", "\\n").replace("\\\\r", "")

    endings = [
        "]}], " + '"metadata": ' + md + "}",
        "]}], " + '"metadata": ' + md + "}",
        "]], " + '"metadata": ' + md + "}",
        "], " + '"metadata": ' + md + "}",
        ", " + '"metadata": ' + md + "}",
        ", " + '"metadata": ' + md,
        "",
    ]

    for end in endings:
        candidate = fixed + end
        try:
            data = json.loads(candidate)
            if "messages" in data:
                if "metadata" not in data:
                    data["metadata"] = {
                        "category": category,
                        "difficulty": "intermediate",
                        "source": "generated",
                    }
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(json.dumps(data, ensure_ascii=False) + "\n")
                return True
        except:
            continue

    # Try trimming
    for trim in range(1, 30):
        trimmed = fixed[:-trim]
        for end in endings:
            candidate = trimmed + end
            try:
                data = json.loads(candidate)
                if "messages" in data:
                    if "metadata" not in data:
                        data["metadata"] = {
                            "category": category,
                            "difficulty": "intermediate",
                            "source": "generated",
                        }
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(json.dumps(data, ensure_ascii=False) + "\n")
                    return True
            except:
                continue

    return False


def main():
    files = sorted(CURATED_DIR.glob("*.jsonl"))
    fixed, failed = 0, 0
    for f in files:
        if fix_file(f):
            fixed += 1
        else:
            failed += 1
            print(f"FAILED: {f.name}")
    print(f"\nFixed: {fixed}, Failed: {failed}, Total: {len(files)}")


if __name__ == "__main__":
    main()
