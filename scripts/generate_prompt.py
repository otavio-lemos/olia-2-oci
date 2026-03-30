#!/usr/bin/env python3
"""
Generate a ready-to-use prompt for LLM data generation.

Usage:
    python scripts/generate_prompt.py oci-core/compute
    python scripts/generate_prompt.py oci-security/iam
    python scripts/generate_prompt.py oci-migration/aws-to-oci
"""

import sys
import shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
TMP_DIR = PROJECT_ROOT / "tmp"
TMP_DIR.mkdir(exist_ok=True)

MASTER_PROMPT_PATH = (
    PROJECT_ROOT / ".agents/skills/generate-oci-dataset/MASTER_PROMPT.md"
)
TAXONOMY_PATH = PROJECT_ROOT / "docs/taxonomy.md"
QUALITY_RULES_PATH = PROJECT_ROOT / "docs/quality-rules.md"
PROMPTS_DIR = PROJECT_ROOT / ".agents/skills/generate-oci-dataset/prompts"


def get_category_from_taxonomy(taxonomy_path: Path, category: str) -> str:
    """Extract category section from taxonomy."""
    content = taxonomy_path.read_text()

    lines = content.split("\n")
    in_category = False
    category_lines = []
    category_prefix = f"#### {category}"

    for line in lines:
        if line.startswith("#### "):
            if in_category:
                break
            if category in line:
                in_category = True
                category_lines.append(line)
        elif in_category:
            if line.startswith("### ") or line.startswith("## "):
                break
            category_lines.append(line)

    return "\n".join(category_lines)


def get_category_prompt(prompts_dir: Path, category: str) -> str:
    """Read category-specific prompt."""
    category_file = prompts_dir / f"{category}.md"

    if not category_file.exists():
        print(f"Warning: Category prompt not found: {category_file}")
        print(f"Available categories in {prompts_dir}:")
        for f in sorted(prompts_dir.rglob("*.md")):
            print(f"  - {f.relative_to(prompts_dir)}")
        return ""

    return category_file.read_text()


def generate_prompt(category: str) -> str:
    """Generate the complete prompt for a category."""

    master_prompt = MASTER_PROMPT_PATH.read_text()
    quality_rules = QUALITY_RULES_PATH.read_text()
    category_info = get_category_from_taxonomy(TAXONOMY_PATH, category)
    category_prompt = get_category_prompt(PROMPTS_DIR, category)

    prompt = f"""{master_prompt}

---

## CATEGORY: {category}

### From Taxonomy (docs/taxonomy.md):

{category_info}

---

### Category-Specific Prompt (.agents/skills/generate-oci-dataset/prompts/{category}.md):

{category_prompt}

---

### Quality Rules (docs/quality-rules.md):

{quality_rules}

---

## TASK

Generate EXACTLY the number of examples specified in the taxonomy for category: {category}

Follow the format specified in MASTER_PROMPT above.
Apply the quality rules strictly.
Use the category topics and example questions as guidance.
"""

    return prompt


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)

    category = sys.argv[1]

    print(f"Generating prompt for category: {category}")

    prompt = generate_prompt(category)

    output_file = TMP_DIR / f"prompt_{category.replace('/', '-')}.md"
    output_file.write_text(prompt)

    print(f"\nPrompt saved to: {output_file}")
    print(f"\nTo use:")
    print(f"1. Copy the content above")
    print(f"2. Send to Gemini/GPT-4/Claude")
    print(f"3. Save results to: data/curated/{category}-001.jsonl")
    print(f"\n{'=' * 50}")
    print(f"\nPROMPT CONTENT:\n")
    print(prompt)


if __name__ == "__main__":
    main()
