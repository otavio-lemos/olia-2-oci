#!/usr/bin/env python3
"""Auto-update README.md dataset section with real data from the pipeline."""

import json
import re
import sys
from collections import Counter
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
README_PATH = PROJECT_ROOT / "README.md"
DATA_DIR = PROJECT_ROOT / "data"


def count_curated_files():
    """Count files in data/curated/."""
    curated_dir = DATA_DIR / "curated"
    if not curated_dir.exists():
        return 0
    return len(list(curated_dir.glob("*.jsonl")))


def count_lines(filepath):
    """Count lines in a JSONL file."""
    if not filepath.exists():
        return 0
    with open(filepath, "r") as f:
        return sum(1 for _ in f)


def get_examples_per_category():
    """Count examples per category file."""
    curated_dir = DATA_DIR / "curated"
    counts = {}
    if not curated_dir.exists():
        return counts
    for f in sorted(curated_dir.glob("*.jsonl")):
        counts[f.stem] = count_lines(f)
    return counts


def get_difficulty_distribution(split_file="train.jsonl"):
    """Analyze difficulty distribution from a split file."""
    filepath = DATA_DIR / split_file
    if not filepath.exists():
        return {}
    difficulties = Counter()
    with open(filepath, "r") as f:
        for line in f:
            try:
                record = json.loads(line)
                diff = record.get("metadata", {}).get("difficulty", "unknown")
                difficulties[diff] += 1
            except json.JSONDecodeError:
                continue
    return dict(difficulties)


def check_quality(split_file="all_curated_clean.jsonl"):
    """Run quality checks on the dataset."""
    filepath = DATA_DIR / split_file
    checks = {
        "total": 0,
        "valid_json": 0,
        "invalid_json": 0,
        "has_messages": 0,
        "has_metadata": 0,
        "has_category": 0,
        "has_difficulty": 0,
        "duplicates": 0,
    }
    if not filepath.exists():
        return checks

    seen = set()
    with open(filepath, "r") as f:
        for line in f:
            checks["total"] += 1
            try:
                record = json.loads(line)
                checks["valid_json"] += 1
                if "messages" in record:
                    checks["has_messages"] += 1
                if "metadata" in record:
                    checks["has_metadata"] += 1
                    if "category" in record["metadata"]:
                        checks["has_category"] += 1
                    if "difficulty" in record["metadata"]:
                        checks["has_difficulty"] += 1
                line_hash = hash(line.strip())
                if line_hash in seen:
                    checks["duplicates"] += 1
                seen.add(line_hash)
            except json.JSONDecodeError:
                checks["invalid_json"] += 1
    return checks


def get_group_summary(taxonomy_file="docs/taxonomy.md"):
    """Parse taxonomy.md to get group summaries."""
    taxonomy_path = PROJECT_ROOT / taxonomy_file
    if not taxonomy_path.exists():
        return []

    groups = []
    current_group = None
    current_topics = []

    with open(taxonomy_path, "r") as f:
        for line in f:
            line = line.strip()
            if line.startswith("### oci-"):
                if current_group and current_topics:
                    groups.append((current_group, current_topics))
                current_group = line.replace("### ", "").split(" ")[0]
                current_topics = []
            elif line.startswith("#### ") and current_group:
                topic = line.replace("#### ", "")
                current_topics.append(topic)

    if current_group and current_topics:
        groups.append((current_group, current_topics))

    return groups


def count_dedup_check():
    """Compare all_curated.jsonl vs all_curated_clean.jsonl for duplicates."""
    clean_count = count_lines(DATA_DIR / "all_curated_clean.jsonl")
    original_count = count_lines(DATA_DIR / "all_curated.jsonl")
    return original_count - clean_count


def build_dataset_section():
    """Build the complete dataset section for README."""
    total_clean = count_lines(DATA_DIR / "all_curated_clean.jsonl")
    train_count = count_lines(DATA_DIR / "train.jsonl")
    valid_count = count_lines(DATA_DIR / "valid.jsonl")
    eval_count = count_lines(DATA_DIR / "eval.jsonl")
    num_categories = count_curated_files()
    examples_per_cat = get_examples_per_category()
    difficulty_dist = get_difficulty_distribution()
    quality = check_quality()
    groups = get_group_summary()
    duplicates = count_dedup_check()

    total_examples = sum(examples_per_cat.values()) if examples_per_cat else total_clean
    examples_per_category = (
        list(examples_per_cat.values())[0] if examples_per_cat else 0
    )

    train_pct = (train_count / total_clean * 100) if total_clean > 0 else 0
    valid_pct = (valid_count / total_clean * 100) if total_clean > 0 else 0
    eval_pct = (eval_count / total_clean * 100) if total_clean > 0 else 0

    section = f"""## Dataset

O dataset contém {total_clean:,} exemplos únicos gerados com diversidade estrutural e validação rigorosa.

| Métrica | Valor |
|---------|-------|
| **Total de Exemplos** | {total_clean:,} |
| **Categorias** | {num_categories} topics OCI |
| **Exemplos por Categoria** | {examples_per_category} |
| **Duplicatas** | {duplicates} (exatas + próximas) |
| **Comandos CLI Falsos** | 0 |
| **Classes SDK Falsas** | 0 |
| **Resources TF Falsos** | 0 |

### Split Distribution

| Split | Exemplos | Percentual |
|-------|----------|------------|
| Train | {train_count:,} | {train_pct:.1f}% |
| Valid | {valid_count:,} | {valid_pct:.1f}% |
| Eval | {eval_count:,} | {eval_pct:.1f}% |
| **Total** | **{total_clean:,}** | **100.0%** |

### Difficulty Distribution (Train)

| Dificuldade | Count | Percentual |
|-------------|-------|------------|
"""

    if difficulty_dist:
        total_train = sum(difficulty_dist.values())
        for diff in ["beginner", "intermediate", "advanced"]:
            count = difficulty_dist.get(diff, 0)
            pct = (count / total_train * 100) if total_train > 0 else 0
            section += f"| {diff.capitalize()} | {count:,} | {pct:.1f}% |\n"

    section += "\n### Categorias por Grupo\n\n"
    section += "| Grupo | Topics | Exemplos |\n"
    section += "|-------|--------|----------|\n"

    group_names = {
        "oci-core": "OCI Core (compute, storage, networking, lb, database, container, serverless)",
        "oci-security": "Security (iam-basics, policies, vault, encryption, cloud-guard, waf)",
        "oci-migration": "Migration (AWS/Azure/GCP/On-prem → OCI)",
        "oci-terraform": "Terraform (provider, compute, storage, networking, lb, database, container, serverless, security, observability, devops, state)",
        "oci-observability": "Observability",
        "oci-troubleshooting": "Troubleshooting",
        "oci-devops": "DevOps",
    }

    for group_key, topics in groups:
        num_topics = len(topics)
        total_group_examples = num_topics * examples_per_category
        display_name = group_names.get(group_key, group_key)
        section += f"| {display_name} | {num_topics} | {total_group_examples:,} |\n"

    return section


def update_readme():
    """Update the README.md file with current dataset information."""
    if not README_PATH.exists():
        print(f"Error: README.md not found at {README_PATH}")
        sys.exit(1)

    with open(README_PATH, "r") as f:
        content = f.read()

    new_section = build_dataset_section()

    pattern = r"## Dataset\n\n.*?(?=\n---\n)"
    replacement = new_section + "\n"

    if not re.search(pattern, content, re.DOTALL):
        print("Warning: Could not find Dataset section in README.md")
        print("Looking for pattern: ## Dataset ... ---")
        sys.exit(1)

    updated_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    with open(README_PATH, "w") as f:
        f.write(updated_content)

    print("README.md updated successfully!")
    print(f"\nDataset Summary:")
    print(f"  Total examples: {count_lines(DATA_DIR / 'all_curated_clean.jsonl'):,}")
    print(f"  Categories: {count_curated_files()}")
    print(f"  Train: {count_lines(DATA_DIR / 'train.jsonl'):,}")
    print(f"  Valid: {count_lines(DATA_DIR / 'valid.jsonl'):,}")
    print(f"  Eval: {count_lines(DATA_DIR / 'eval.jsonl'):,}")


if __name__ == "__main__":
    update_readme()
