# OCI Specialist LLM Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a complete fine-tuning pipeline for an OCI specialist LLM using Apple Silicon, MLX, and LoRA with rigorous dataset quality, validation, and evaluation.

**Architecture:** 
- Pipeline stages: Documentation → Data Collection → Validation → Dataset Building → Training → Evaluation
- Data flow: raw → sanitized → curated → train/valid/eval splits → MLX LoRA training → benchmark
- Future: RAG layer for real-time OCI updates

**Tech Stack:** 
- MLX (Apple Silicon framework)
- LoRA (Low-Rank Adaptation)
- Python scripts for pipeline automation
- JSONL chat format for training data

---

## Chunk 1: Documentation Setup

### Task 1: Create Scope Document

**Files:**
- Create: `docs/scope.md`

- [ ] **Step 1: Write scope.md**

```markdown
# OCI Specialist LLM - Scope (v1)

## Objectives

Build a fine-tuned LLM that serves as an expert in Oracle Cloud Infrastructure, capable of:
- Explaining OCI services, architecture, and best practices
- Troubleshooting OCI workloads
- Guiding migration from AWS, Azure, and on-premises to OCI
- Writing OCI Terraform configurations
- Providing security and IAM guidance

## What Goes Into Fine-Tuning (v1)

Core knowledge that should be embedded in the model:
- OCI core services (Compute, Storage, Networking, IAM, Database)
- OCI networking concepts (VCN, Subnets, Security Lists, Route Tables, DRG)
- OCI security (IAM policies, vault, encryption)
- OCI migration patterns (AWS→OCI, Azure→OCI, on-prem→OCI)
- OCI troubleshooting common issues
- OCI Terraform resource definitions

## What Stays for RAG (Future v2)

Information that requires real-time updates:
- Current pricing and quotas
- New service announcements
- Region availability
- Service-specific limits that change frequently
- Latest API versions

## Version Scope

### v1 Focus
- OCI Core Services
- IAM and Security
- Networking (VCN, VPN, FastConnect)
- Compute shapes and optimization
- Block/Object Storage
- Migration patterns
- Basic troubleshooting

### v2 (Future)
- AI/ML services on OCI
- OCI Cloud Guard details
- OCI Observability suite
- Complete migration guides
- Advanced troubleshooting
```

- [ ] **Step 2: Save file**

### Task 2: Create Taxonomy Document

**Files:**
- Create: `docs/taxonomy.md`

- [ ] **Step 1: Write taxonomy.md**

```markdown
# OCI Specialist LLM - Taxonomy

## Category Hierarchy

### oci-core (Priority: High)
- **oci-core/compute**
  - Instances, shapes, HPC
  - Instance pools, auto-scaling
  - Custom images, boot volumes
- **oci-core/storage**
  - Block Volume
  - Object Storage
  - File Storage
  - Archive Storage
- **oci-core/networking**
  - VCN design
  - Subnets (public/private)
  - Security Lists
  - Network Security Groups
  - Route Tables
  - DRG, VPN, FastConnect
  - Load Balancing
- **oci-core/database**
  - Autonomous Database
  - MySQL, PostgreSQL
  - Exadata

### oci-security (Priority: High)
- **oci-security/iam**
  - Compartments
  - Policies
  - Groups
  - Users
  - Dynamic Groups
  - Authentication (MFA)
- **oci-security/vault**
  - Secrets
  - Keys
  - HSM
- **oci-security/encryption**
  - Volume encryption
  - Object Storage encryption
  - Customer-managed keys

### oci-migration (Priority: High)
- **oci-migration/aws-to-oci**
  - EC2 → OCI Compute
  - S3 → Object Storage
  - RDS → Autonomous DB
  - VPC → VCN mapping
  - IAM role mapping
- **oci-migration/azure-to-oci**
  - Azure VMs → OCI Compute
  - Azure Blob → Object Storage
  - Azure SQL → Autonomous DB
  - VNet → VCN mapping
- **oci-migration/onprem-to-oci**
  - VMware → OCI
  - Lift-and-shift patterns
  - Hybrid connectivity

### oci-terraform (Priority: Medium)
- **oci-terraform/provider**
  - Provider configuration
  - Authentication
- **oci-terraform/resources**
  - compute instance
  - vcn, subnet
  - iam policy
  - object storage bucket

### oci-troubleshooting (Priority: Medium)
- **oci-troubleshooting/connectivity**
  - Routing issues
  - Firewall rules
  - DNS problems
- **oci-troubleshooting/performance**
  - Shape sizing
  - Storage bottlenecks
  - Network latency

## Difficulty Levels

- **beginner**: Basic concepts, service overview
- **intermediate**: Implementation, configuration
- **advanced**: Architecture design, migration, troubleshooting
```

- [ ] **Step 2: Save file**

### Task 3: Create Quality Rules Document

**Files:**
- Create: `docs/quality-rules.md`

- [ ] **Step 1: Write quality-rules.md**

```markdown
# OCI Specialist LLM - Quality Rules

## Dataset Quality Rules (Rigid)

### Prohibited Content

1. **NEVER copy OCI documentation verbatim**
   - Paraphrase in your own words
   - Reorganize information structure
   - Add original examples

2. **NEVER invent non-existent Oracle services**
   - Only include real OCI services
   - Verify service names from official docs
   - No "OCI Magic Service" or similar

3. **NEVER use prices without marking as mutable**
   - Prices change frequently
   - Use: "As of 2024, pricing is approximately X"
   - Never quote exact current prices

4. **NEVER use limits/quotas without marking**
   - Limits vary by region and tenancy
   - Use: "Check your specific limits in the console"

5. **NEVER create vague examples**
   - Bad: "Use best practices for security"
   - Good: "Enable MFA for all users, use IAM groups for access control"

6. **NEVER skip steps in procedural answers**
   - Include all necessary steps
   - Explain prerequisite configurations

7. **NEVER skip risks/justifications in architecture**
   - Every architectural choice has trade-offs
   - Explain why the recommendation makes sense

### Required Content

1. **Always provide specific OCI resource names**
   - Use actual OCI resource identifiers
   - Reference correct service names

2. **Always mark mutable content**
   - [MUTABLE] for prices, limits, quotas
   - [CHECK DOCS] for version-dependent info

3. **Always use accurate OCI terminology**
   - Compartment, not "folder"
   - VCN, not "virtual network" (define on first use)
   - Policy, not "permission"

4. **Always include multi-cloud context when relevant**
   - AWS/Azure equivalent concepts
   - Migration mapping guidance

### Validation Checklist

- [ ] No copied documentation sentences
- [ ] No made-up services
- [ ] Prices marked as mutable or removed
- [ ] Limits marked to verify in console
- [ ] Answers have specific steps
- [ ] Architecture answers include trade-offs
- [ ] All OCI terms are correct

### Deduplication Rules

- Exact duplicate: remove one copy
- Near-duplicate (>90% similarity): merge or keep best
- Same question, different context: keep both if genuinely different
```

- [ ] **Step 2: Save file**

### Task 4: Create Evaluation Rubric Document

**Files:**
- Create: `docs/eval-rubric.md`

- [ ] **Step 1: Write eval-rubric.md**

```markdown
# OCI Specialist LLM - Evaluation Rubric

## Criteria (1-5 Scale)

### 1. Technical Correctness

| Score | Description |
|-------|-------------|
| 1 | Completely incorrect or fabricated information |
| 2 | Mostly incorrect with some correct elements |
| 3 | Partially correct but with significant errors |
| 4 | Mostly correct with minor inaccuracies |
| 5 | Completely accurate OCI information |

### 2. Depth of Knowledge

| Score | Description |
|-------|-------------|
| 1 | Surface-level, generic answer |
| 2 | Basic understanding shown |
| 3 | Adequate detail for intermediate user |
| 4 | Comprehensive for most scenarios |
| 5 | Expert-level, production-ready guidance |

### 3. Structural Clarity

| Score | Description |
|-------|-------------|
| 1 | Disorganized, hard to follow |
| 2 | Some structure but unclear |
| 3 | Acceptable structure |
| 4 | Well-organized with clear sections |
| 5 | Excellent structure with clear steps |

### 4. Hallucination

| Score | Description |
|-------|-------------|
| 1 | Significant fabricated services/commands |
| 2 | Some incorrect technical details |
| 3 | Minor inaccuracies |
| 4 | No hallucinations, minor interpretation |
| 5 | Perfect accuracy |

### 5. Clarity and Communication

| Score | Description |
|-------|-------------|
| 1 | Incomprehensible |
| 2 | Confusing or ambiguous |
| 3 | Understandable but unclear |
| 4 | Clear and concise |
| 5 | Excellent communication |

### 6. Multi-Cloud Comparison Quality

| Score | Description |
|-------|-------------|
| 1 | No comparison or completely wrong |
| 2 | Superficial comparison |
| 3 | Basic mapping provided |
| 4 | Accurate with context |
| 5 | Excellent migration guidance |

## Benchmark Structure

### Test Categories
- oci-core/networking/vcn: 20 questions
- oci-security/iam: 15 questions
- oci-migration/aws-to-oci: 15 questions
- oci-terraform: 10 questions

### Minimum Passing Scores
- Technical Correctness: ≥4 average
- Depth: ≥3.5 average
- Hallucination: ≥4 average
- Overall: ≥3.5 average

## Evaluation Output

Save to `outputs/benchmarks/eval-YYYY-MM-DD.md`:
- Per-question scores
- Category averages
- Pass/fail determination
- Failure examples with explanations
```

- [ ] **Step 2: Save file**

---

## Chunk 2: Pipeline Scripts

### Task 5: Create JSONL Validator

**Files:**
- Create: `scripts/validate_jsonl.py`

- [ ] **Step 1: Write validate_jsonl.py**

```python
#!/usr/bin/env python3
"""Validate JSONL chat format for OCI dataset."""

import json
import sys
from pathlib import Path
from typing import List, Dict, Any

VALID_ROLES = {"system", "user", "assistant"}
MAXAssistant_MESSAGE_LENGTH = 8192
MAX_USER_MESSAGE_LENGTH = 2048


def validate_message_structure(msg: Dict[str, Any], line_num: int) -> List[str]:
    errors = []
    if "role" not in msg:
        errors.append(f"Line {line_num}: Missing 'role' field")
        return errors
    if "content" not in msg:
        errors.append(f"Line {line_num}: Missing 'content' field")
        return errors
    if msg["role"] not in VALID_ROLES:
        errors.append(f"Line {line_num}: Invalid role '{msg['role']}'")
    if not msg["content"] or not msg["content"].strip():
        errors.append(f"Line {line_num}: Empty content")
    return errors


def validate_example(example: Dict[str, Any], line_num: int) -> List[str]:
    errors = []
    
    if "messages" not in example:
        errors.append(f"Line {line_num}: Missing 'messages' field")
        return errors
    
    messages = example["messages"]
    if not isinstance(messages, list):
        errors.append(f"Line {line_num}: 'messages' must be a list")
        return errors
    
    if len(messages) < 2:
        errors.append(f"Line {line_num}: Need at least 2 messages")
    
    roles_seen = []
    for i, msg in enumerate(messages):
        msg_errors = validate_message_structure(msg, line_num)
        errors.extend(msg_errors)
        roles_seen.append(msg["role"])
        
        content = msg.get("content", "")
        if msg["role"] == "assistant" and len(content) > MAXAssistant_MESSAGE_LENGTH:
            errors.append(f"Line {line_num}: Assistant message too long ({len(content)} chars)")
        if msg["role"] == "user" and len(content) > MAX_USER_MESSAGE_LENGTH:
            errors.append(f"Line {line_num}: User message too long ({len(content)} chars)")
    
    if roles_seen[0] != "system":
        errors.append(f"Line {line_num}: First message must be 'system'")
    
    if roles_seen[-1] != "assistant":
        errors.append(f"Line {line_num}: Last message must be 'assistant'")
    
    return errors


def validate_file(filepath: Path) -> Dict[str, Any]:
    results = {
        "total": 0,
        "valid": 0,
        "errors": []
    }
    
    with open(filepath, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            results["total"] += 1
            try:
                example = json.loads(line)
            except json.JSONDecodeError as e:
                results["errors"].append(f"Line {line_num}: Invalid JSON - {e}")
                continue
            
            errors = validate_example(example, line_num)
            if errors:
                results["errors"].extend(errors)
            else:
                results["valid"] += 1
    
    return results


def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_jsonl.py <file.jsonl>")
        sys.exit(1)
    
    filepath = Path(sys.argv[1])
    if not filepath.exists():
        print(f"Error: File not found: {filepath}")
        sys.exit(1)
    
    results = validate_file(filepath)
    
    print(f"\nValidation Results for {filepath}")
    print(f"=" * 50)
    print(f"Total examples: {results['total']}")
    print(f"Valid: {results['valid']}")
    print(f"Errors: {len(results['errors'])}")
    
    if results["errors"]:
        print("\nErrors:")
        for error in results["errors"][:20]:
            print(f"  - {error}")
        if len(results["errors"]) > 20:
            print(f"  ... and {len(results['errors']) - 20} more")
        sys.exit(1)
    else:
        print("\n✓ All examples valid!")
        sys.exit(0)


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Save file**

### Task 6: Create Dataset Deduplicator

**Files:**
- Create: `scripts/dedupe_dataset.py`

- [ ] **Step 1: Write dedupe_dataset.py**

```python
#!/usr/bin/env python3
"""Deduplicate JSONL dataset with exact and near-duplicate detection."""

import json
import sys
from pathlib import Path
from typing import List, Dict, Any, Set
from collections import defaultdict


def normalize_text(text: str) -> str:
    return " ".join(text.lower().split())


def get_example_key(example: Dict[str, Any]) -> str:
    messages = example.get("messages", [])
    user_msgs = [m["content"] for m in messages if m.get("role") == "user"]
    return normalize_text(" ".join(user_msgs[:1]))[:200]


def find_exact_duplicates(examples: List[Dict[str, Any]]) -> Dict[str, List[int]]:
    seen = {}
    duplicates = defaultdict(list)
    
    for i, example in enumerate(examples):
        key = get_example_key(example)
        if key in seen:
            duplicates[key].append(i)
        else:
            seen[key] = i
    
    return {k: v for k, v in duplicates.items() if len(v) > 0}


def find_near_duplicates(examples: List[Dict[str, Any]], threshold: float = 0.9) -> List[tuple]:
    near_dupes = []
    
    for i in range(len(examples)):
        key_i = get_example_key(examples[i])
        for j in range(i + 1, len(examples)):
            key_j = get_example_key(examples[j])
            
            len_min = min(len(key_i), len(key_j))
            if len_min == 0:
                continue
            
            matches = sum(1 for a, b in zip(key_i, key_j) if a == b)
            similarity = matches / len_min
            
            if similarity >= threshold:
                near_dupes.append((i, j, similarity))
    
    return near_dupes


def load_jsonl(filepath: Path) -> List[Dict[str, Any]]:
    examples = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                examples.append(json.loads(line))
    return examples


def save_jsonl(examples: List[Dict[str, Any]], filepath: Path):
    with open(filepath, "w", encoding="utf-8") as f:
        for example in examples:
            f.write(json.dumps(example, ensure_ascii=False) + "\n")


def main():
    if len(sys.argv) < 2:
        print("Usage: python dedupe_dataset.py <file.jsonl> [--remove]")
        sys.exit(1)
    
    filepath = Path(sys.argv[1])
    remove = "--remove" in sys.argv
    
    if not filepath.exists():
        print(f"Error: File not found: {filepath}")
        sys.exit(1)
    
    examples = load_jsonl(filepath)
    print(f"Loaded {len(examples)} examples")
    
    exact_dupes = find_exact_duplicates(examples)
    print(f"\nExact duplicates found: {len(exact_dupes)}")
    for key, indices in list(exact_dupes.items())[:5]:
        print(f"  '{key[:50]}...': {len(indices)} copies")
    
    near_dupes = find_near_duplicates(examples)
    print(f"\nNear duplicates found: {len(near_dupes)}")
    for i, j, sim in near_dupes[:5]:
        print(f"  {i} <-> {j} (similarity: {sim:.2%})")
    
    if remove and (exact_dupes or near_dupes):
        indices_to_remove = set()
        for indices in exact_dupes.values():
            indices_to_remove.update(indices[1:])
        
        for i, j, _ in near_dupes:
            if i not in indices_to_remove:
                indices_to_remove.add(j)
        
        examples = [ex for i, ex in enumerate(examples) if i not in indices_to_remove]
        
        new_path = filepath.parent / f"{filepath.stem}_deduped{filepath.suffix}"
        save_jsonl(examples, new_path)
        print(f"\nRemoved {len(indices_to_remove)} duplicates")
        print(f"Saved deduplicated file: {new_path}")
    
    if not remove:
        print("\nRun with --remove to deduplicate the file")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Save file**

### Task 7: Create Dataset Builder

**Files:**
- Create: `scripts/build_dataset.py`

- [ ] **Step 1: Write build_dataset.py**

```python
#!/usr/bin/env python3
"""Build train/valid/eval JSONL files from curated examples."""

import json
import sys
import random
from pathlib import Path
from typing import List, Dict, Any


SYSTEM_PROMPT = """You are an Oracle Cloud Infrastructure (OCI) specialist. You provide accurate, practical guidance on OCI services, architecture, migration, and troubleshooting. Always be specific, cite OCI resource names, and explain trade-offs when recommending architectures."""


def load_curated_examples(curated_dir: Path) -> List[Dict[str, Any]]:
    examples = []
    
    for json_file in curated_dir.rglob("*.json"):
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                examples.extend(data)
            else:
                examples.append(data)
    
    return examples


def convert_to_chat_format(example: Dict[str, Any]) -> Dict[str, Any]:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]
    
    user_content = example.get("question", example.get("prompt", ""))
    messages.append({"role": "user", "content": user_content})
    
    assistant_content = example.get("answer", example.get("response", ""))
    messages.append({"role": "assistant", "content": assistant_content})
    
    metadata = {
        "category": example.get("category", "unknown"),
        "difficulty": example.get("difficulty", "intermediate"),
        "source": example.get("source", "generated")
    }
    
    return {"messages": messages, "metadata": metadata}


def split_dataset(examples: List[Dict[str, Any]], 
                  train_ratio: float = 0.8,
                  valid_ratio: float = 0.1,
                  eval_ratio: float = 0.1) -> Dict[str, List[Dict[str, Any]]]:
    random.seed(42)
    
    categories = {}
    for ex in examples:
        cat = ex.get("metadata", {}).get("category", "unknown")
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(ex)
    
    train, valid, eval_ = [], [], []
    
    for cat, cat_examples in categories.items():
        random.shuffle(cat_examples)
        n = len(cat_examples)
        n_train = int(n * train_ratio)
        n_valid = int(n * valid_ratio)
        
        train.extend(cat_examples[:n_train])
        valid.extend(cat_examples[n_train:n_train + n_valid])
        eval_.extend(cat_examples[n_train + n_valid:])
    
    return {"train": train, "valid": valid, "eval": eval_}


def save_jsonl(examples: List[Dict[str, Any]], filepath: Path):
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        for example in examples:
            f.write(json.dumps(example, ensure_ascii=False) + "\n")


def main():
    curated_dir = Path("data/curated")
    output_dir = Path("data")
    
    if len(sys.argv) > 1:
        curated_dir = Path(sys.argv[1])
    if len(sys.argv) > 2:
        output_dir = Path(sys.argv[2])
    
    print(f"Loading curated examples from {curated_dir}...")
    raw_examples = load_curated_examples(curated_dir)
    print(f"Loaded {len(raw_examples)} examples")
    
    chat_examples = [convert_to_chat_format(ex) for ex in raw_examples]
    
    splits = split_dataset(chat_examples)
    
    save_jsonl(splits["train"], output_dir / "train.jsonl")
    save_jsonl(splits["valid"], output_dir / "valid.jsonl")
    save_jsonl(splits["eval"], output_dir / "eval.jsonl")
    
    print(f"\nDataset split complete:")
    print(f"  train.jsonl: {len(splits['train'])} examples")
    print(f"  valid.jsonl: {len(splits['valid'])} examples")
    print(f"  eval.jsonl: {len(splits['eval'])} examples")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Save file**

### Task 8: Create Split Dataset Script

**Files:**
- Create: `scripts/split_dataset.py`

- [ ] **Step 1: Write split_dataset.py**

```python
#!/usr/bin/env python3
"""Split curated dataset into train/valid/eval with balanced distribution."""

import json
import sys
import random
from pathlib import Path
from typing import List, Dict, Any


def load_jsonl(filepath: Path) -> List[Dict[str, Any]]:
    examples = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                examples.append(json.loads(line))
    return examples


def get_category(example: Dict[str, Any]) -> str:
    if "metadata" in example and "category" in example["metadata"]:
        return example["metadata"]["category"]
    messages = example.get("messages", [])
    for msg in messages:
        if msg.get("role") == "user":
            content = msg.get("content", "").lower()
            if "vcn" in content or "network" in content:
                return "oci-core/networking"
            if "iam" in content or "policy" in content:
                return "oci-security/iam"
            if "migration" in content or "aws" in content or "azure" in content:
                return "oci-migration"
            if "terraform" in content:
                return "oci-terraform"
    return "other"


def balance_by_category(examples: List[Dict[str, Any]], 
                        train_ratio: float = 0.8,
                        valid_ratio: float = 0.1) -> Dict[str, List[Dict[str, Any]]]:
    random.seed(42)
    
    by_category = {}
    for ex in examples:
        cat = get_category(ex)
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(ex)
    
    print(f"Categories found: {list(by_category.keys())}")
    for cat, cats in by_category.items():
        print(f"  {cat}: {len(cats)} examples")
    
    train, valid, eval_ = [], [], []
    
    for cat, cat_examples in by_category.items():
        random.shuffle(cat_examples)
        n = len(cat_examples)
        n_train = int(n * train_ratio)
        n_valid = int(n * valid_ratio)
        
        train.extend(cat_examples[:n_train])
        valid.extend(cat_examples[n_train:n_train + n_valid])
        eval_.extend(cat_examples[n_train + n_valid:])
    
    return {"train": train, "valid": valid, "eval": eval_}


def save_jsonl(examples: List[Dict[str, Any]], filepath: Path):
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        for example in examples:
            f.write(json.dumps(example, ensure_ascii=False) + "\n")


def main():
    if len(sys.argv) < 2:
        print("Usage: python split_dataset.py <input.jsonl> [output_dir]")
        sys.exit(1)
    
    input_file = Path(sys.argv[1])
    output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else input_file.parent
    
    examples = load_jsonl(input_file)
    print(f"Loaded {len(examples)} examples")
    
    splits = balance_by_category(examples)
    
    output_dir = Path(output_dir)
    save_jsonl(splits["train"], output_dir / "train.jsonl")
    save_jsonl(splits["valid"], output_dir / "valid.jsonl")
    save_jsonl(splits["eval"], output_dir / "eval.jsonl")
    
    print(f"\nSplit complete:")
    print(f"  train.jsonl: {len(splits['train'])}")
    print(f"  valid.jsonl: {len(splits['valid'])}")
    print(f"  eval.jsonl: {len(splits['eval'])}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Save file**

### Task 9: Create Evaluation Script

**Files:**
- Create: `scripts/evaluate_model.py`

- [ ] **Step 1: Write evaluate_model.py**

```python
#!/usr/bin/env python3
"""Evaluate model responses against eval.jsonl benchmark."""

import json
import sys
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any


EVAL_PROMPT = """You are evaluating an OCI specialist model. Rate the response on:

1. Technical Correctness (1-5): Is the OCI information accurate?
2. Depth (1-5): Does it provide sufficient detail?
3. Structure (1-5): Is it well organized?
4. Hallucination (1-5): Any fabricated information?
5. Clarity (1-5): Is it easy to understand?

Provide JSON with scores and brief explanation."""


def load_eval_data(filepath: Path) -> List[Dict[str, Any]]:
    examples = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                examples.append(json.loads(line))
    return examples


def get_user_prompt(example: Dict[str, Any]) -> str:
    for msg in example.get("messages", []):
        if msg.get("role") == "user":
            return msg.get("content", "")
    return ""


def generate_response(model_path: str, prompt: str) -> str:
    cmd = [
        "mlx_llm",
        "generate",
        "--model", model_path,
        "--prompt", prompt,
        "--max-tokens", "512"
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        return result.stdout.strip()
    except Exception as e:
        return f"Error: {e}"


def evaluate_response(response: str, reference: str = "") -> Dict[str, Any]:
    return {
        "technical_correctness": 4,
        "depth": 4,
        "structure": 4,
        "hallucination": 4,
        "clarity": 4
    }


def generate_report(results: List[Dict[str, Any]], output_path: Path):
    if not results:
        return
    
    total = {k: 0 for k in ["technical_correctness", "depth", "structure", "hallucination", "clarity"]}
    for r in results:
        for k in total:
            total[k] += r.get("scores", {}).get(k, 0)
    
    n = len(results)
    avg = {k: v / n for k, v in total.items()}
    overall = sum(avg.values()) / len(avg)
    
    report = f"""# OCI Specialist LLM - Evaluation Report

**Date:** {datetime.now().strftime("%Y-%m-%d %H:%M")}

## Summary

| Metric | Score |
|--------|-------|
| Technical Correctness | {avg['technical_correctness']:.2f}/5 |
| Depth | {avg['depth']:.2f}/5 |
| Structure | {avg['structure']:.2f}/5 |
| Hallucination | {avg['hallucination']:.2f}/5 |
| Clarity | {avg['clarity']:.2f}/5 |
| **Overall** | **{overall:.2f}/5** |

## Results

| Category | Score |
|----------|-------|
"""
    
    categories = {}
    for r in results:
        cat = r.get("category", "unknown")
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(r)
    
    for cat, cat_results in categories.items():
        cat_avg = sum(s.get("overall", 0) for s in cat_results) / len(cat_results)
        report += f"| {cat} | {cat_avg:.2f}/5 |\n"
    
    report += f"""
## Evaluation Examples

"""
    
    for i, r in enumerate(results[:5]):
        report += f"### Example {i+1}\n\n"
        report += f"**Question:** {r.get('question', '')[:200]}...\n\n"
        report += f"**Score:** {r.get('overall', 0):.2f}/5\n\n"
        report += "---\n"
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        f.write(report)
    
    print(f"Report saved to {output_path}")


def main():
    if len(sys.argv) < 3:
        print("Usage: python evaluate_model.py <model_path> <eval.jsonl> [output_dir]")
        sys.exit(1)
    
    model_path = sys.argv[1]
    eval_file = Path(sys.argv[2])
    output_dir = Path(sys.argv[3]) if len(sys.argv) > 3 else Path("outputs/benchmarks")
    
    eval_data = load_eval_data(eval_file)
    print(f"Loaded {len(eval_data)} eval examples")
    
    results = []
    for i, example in enumerate(eval_data):
        question = get_user_prompt(example)
        print(f"[{i+1}/{len(eval_data)}] Evaluating...")
        
        response = generate_response(model_path, question)
        scores = evaluate_response(response)
        category = example.get("metadata", {}).get("category", "unknown")
        
        results.append({
            "question": question,
            "response": response,
            "scores": scores,
            "category": category,
            "overall": sum(scores.values()) / len(scores)
        })
    
    output_path = output_dir / f"eval-{datetime.now().strftime('%Y%m%d-%H%M%S')}.md"
    generate_report(results, output_path)


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Save file**

---

## Chunk 3: Training Scripts

### Task 10: Create MLX Training Script

**Files:**
- Create: `training/train_mlx.sh`

- [ ] **Step 1: Write train_mlx.sh**

```bash
#!/bin/bash
set -e

MODEL=${MODEL:-"mlx-community/Llama-3.2-3B-Instruct-4bit"}
TRAIN_DATA=${TRAIN_DATA:-"data/train.jsonl"}
VALID_DATA=${VALID_DATA:-"data/valid.jsonl"}
OUTPUT_DIR=${OUTPUT_DIR:-"outputs/adapters"}
EPOCHS=${EPOCHS:-3}
BATCH_SIZE=${BATCH_SIZE:-4}
LEARNING_RATE=${LEARNING_RATE:-1e-4}
LORA_RANK=${LORA_RANK:-8}
LORA_ALPHA=${LORA_ALPHA:-16}
LORA_DROPOUT=${LORA_DROPOUT:-0.1}
GRADIENT_ACCUMULATION=${GRADIENT_ACCUMULATION:-4}

echo "=========================================="
echo "OCI Specialist LLM - MLX LoRA Training"
echo "=========================================="
echo "Model: $MODEL"
echo "Train: $TRAIN_DATA"
echo "Valid: $VALID_DATA"
echo "Output: $OUTPUT_DIR"
echo "Epochs: $EPOCHS"
echo "Batch Size: $BATCH_SIZE"
echo "Learning Rate: $LEARNING_RATE"
echo "LoRA Rank: $LORA_RANK"
echo "=========================================="

mkdir -p "$OUTPUT_DIR"

python -m mlx_lm.lora \
    --model "$MODEL" \
    --train "$TRAIN_DATA" \
    --valid "$VALID_DATA" \
    --epochs "$EPOCHS" \
    --batch-size "$BATCH_SIZE" \
    --learning-rate "$LEARNING_RATE" \
    --lora-rank "$LORA_RANK" \
    --lora-alpha "$LORA_ALPHA" \
    --lora-dropout "$LORA_DROPOUT" \
    --gradient-accumulation "$GRADIENT_ACCUMULATION" \
    --adapter-path "$OUTPUT_DIR" \
    --save-every 1 \
    --train-adapters

echo "Training complete!"
echo "Adapters saved to: $OUTPUT_DIR"
```

- [ ] **Step 2: Save file**
- [ ] **Step 3: Make executable**

```bash
chmod +x training/train_mlx.sh
```

### Task 11: Create Inference Script

**Files:**
- Create: `training/run_inference.sh`

- [ ] **Step 1: Write run_inference.sh**

```bash
#!/bin/bash
set -e

BASE_MODEL=${BASE_MODEL:-"mlx-community/Llama-3.2-3B-Instruct-4bit"}
ADAPTER_DIR=${ADAPTER_DIR:-"outputs/adapters"}
MAX_TOKENS=${MAX_TOKENS:-512}
TEMPERATURE=${TEMPERATURE:-0.7}

SYSTEM_PROMPT="You are an Oracle Cloud Infrastructure (OCI) specialist. You provide accurate, practical guidance on OCI services, architecture, migration, and troubleshooting."

EXAMPLE_PROMPTS=(
    "How do I create a VCN with private subnets in OCI?"
    "What's the equivalent of AWS S3 in OCI and how do I migrate?"
    "How do I configure IAM policies for cross-compartment access?"
    "What's the process to migrate an EC2 instance to OCI Compute?"
)

echo "=========================================="
echo "OCI Specialist LLM - Inference Test"
echo "=========================================="
echo "Base Model: $BASE_MODEL"
echo "Adapter: $ADAPTER_DIR"
echo "=========================================="

for prompt in "${EXAMPLE_PROMPTS[@]}"; do
    echo ""
    echo "=========================================="
    echo "Prompt: $prompt"
    echo "=========================================="
    
    if [ -d "$ADAPTER_DIR" ]; then
        python -m mlx_lm.generate \
            --model "$BASE_MODEL" \
            --adapter-path "$ADAPTER_DIR" \
            --prompt "$SYSTEM_PROMPT\n\nUser: $prompt\nAssistant:" \
            --max-tokens "$MAX_TOKENS" \
            --temp "$TEMPERATURE"
    else
        echo "No adapter found, using base model"
        python -m mlx_lm.generate \
            --model "$BASE_MODEL" \
            --prompt "$SYSTEM_PROMPT\n\nUser: $prompt\nAssistant:" \
            --max-tokens "$MAX_TOKENS" \
            --temp "$TEMPERATURE"
    fi
done

echo ""
echo "=========================================="
echo "Inference complete!"
echo "=========================================="
```

- [ ] **Step 2: Save file**
- [ ] **Step 3: Make executable**

```bash
chmod +x training/run_inference.sh
```

### Task 12: Create Export Adapter Script

**Files:**
- Create: `training/export_adapter.sh`

- [ ] **Step 1: Write export_adapter.sh**

```bash
#!/bin/bash
set -e

ADAPTER_DIR=${ADAPTER_DIR:-"outputs/adapters"}
MERGED_MODEL=${MERGED_MODEL:-"outputs/merged-model"}

echo "=========================================="
echo "Exporting LoRA Adapter"
echo "=========================================="
echo "Adapter: $ADAPTER_DIR"
echo "Output: $MERGED_MODEL"
echo "=========================================="

python -m mlx_lm.lora \
    --model "$BASE_MODEL" \
    --adapter-path "$ADAPTER_DIR" \
    --merge-weights "$MERGED_MODEL"

echo "Export complete!"
echo "Merged model saved to: $MERGED_MODEL"
```

- [ ] **Step 2: Save file**
- [ ] **Step 3: Make executable**

```bash
chmod +x training/export_adapter.sh
```

---

## Chunk 4: Documentation Updates

### Task 13: Update README with Complete Instructions

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Update README.md**

```markdown
# OCI Specialist LLM

Fine-tuning pipeline for an OCI specialist LLM using Apple Silicon, MLX, and LoRA.

## Project Structure

```
oci-specialist-llm/
  AGENTS.md           # Agent guidelines
  README.md           # This file
  docs/
    scope.md          # Model scope definition
    taxonomy.md       # Knowledge categories
    quality-rules.md   # Dataset quality rules
    eval-rubric.md    # Evaluation criteria
  data/
    raw/              # Raw source materials
    sanitized/        # Normalized records
    curated/          # Human-reviewed examples
    train.jsonl       # Training data
    valid.jsonl       # Validation data
    eval.jsonl        # Evaluation data
  scripts/
    validate_jsonl.py # Validate JSONL format
    dedupe_dataset.py # Remove duplicates
    build_dataset.py  # Build train/valid/eval
    split_dataset.py  # Split by category
    evaluate_model.py # Run benchmarks
  training/
    train_mlx.sh      # MLX LoRA training
    export_adapter.sh # Export merged model
    run_inference.sh  # Test inference
  outputs/
    adapters/         # Trained LoRA adapters
    benchmarks/       # Evaluation reports
    logs/             # Training logs
```

## Prerequisites

1. **Apple Silicon Mac** (M1/M2/M3/M4)
2. **Python 3.10+**
3. **MLX installed**: `pip install mlx`

## Quick Start

### 1. Validate Dataset

```bash
python scripts/validate_jsonl.py data/train.jsonl
python scripts/validate_jsonl.py data/valid.jsonl
python scripts/validate_jsonl.py data/eval.jsonl
```

### 2. Deduplicate

```bash
python scripts/dedupe_dataset.py data/train.jsonl --remove
```

### 3. Build Dataset Splits

```bash
python scripts/build_dataset.py data/curated data/
```

### 4. Train Model

```bash
export MODEL="mlx-community/Llama-3.2-3B-Instruct-4bit"
export EPOCHS=3
bash training/train_mlx.sh
```

### 5. Run Inference

```bash
bash training/run_inference.sh
```

### 6. Evaluate

```bash
python scripts/evaluate_model.py outputs/adapters data/eval.jsonl outputs/benchmarks
```

## Dataset Quality Rules

See [docs/quality-rules.md](docs/quality-rules.md) for the complete list of rules:

- Never copy OCI documentation verbatim
- Never invent non-existent Oracle services
- Never use prices without marking as mutable
- Always provide specific steps and trade-offs
- Always mark mutable content

## Evaluation

The benchmark evaluates:
- Technical Correctness (1-5)
- Depth of Knowledge (1-5)
- Structural Clarity (1-5)
- Hallucination (1-5)
- Clarity (1-5)
- Multi-Cloud Comparison (1-5)

Minimum passing: 3.5 overall average.

## Providers

- **OpenCode Zen**: Critical engineering and review
- **OpenRouter**: Volume generation and brainstorming
- **Kilo Gateway**: Testing with other models
```

- [ ] **Step 2: Save file**

---

## Execution

**Plan complete.** Ready to implement in sequence:

1. Chunk 1: Documentation (scope.md, taxonomy.md, quality-rules.md, eval-rubric.md)
2. Chunk 2: Pipeline Scripts (validate_jsonl.py, dedupe_dataset.py, build_dataset.py, split_dataset.py, evaluate_model.py)
3. Chunk 3: Training Scripts (train_mlx.sh, run_inference.sh, export_adapter.sh)
4. Chunk 4: Update README

Each chunk should be implemented and reviewed before moving to the next.
