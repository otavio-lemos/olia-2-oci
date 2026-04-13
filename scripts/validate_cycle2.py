#!/usr/bin/env python3
"""Validate JSONL chat format for OCI dataset."""

import json
import sys
from pathlib import Path
from typing import List, Dict, Any

VALID_ROLES = {"system", "user", "assistant"}
MAX_ASSISTANT_MESSAGE_LENGTH = 8192
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


def validate_metadata(example: Dict[str, Any], line_num: int) -> List[str]:
    errors = []
    metadata = example.get("metadata")
    if metadata is None:
        errors.append(f"Line {line_num}: Missing 'metadata' field")
        return errors
    if not isinstance(metadata, dict):
        errors.append(f"Line {line_num}: 'metadata' must be a dict")
        return errors
    required_fields = ["category", "difficulty", "source"]
    for field in required_fields:
        if field not in metadata:
            errors.append(f"Line {line_num}: Missing metadata.{field}")
        elif not metadata[field] or not str(metadata[field]).strip():
            errors.append(f"Line {line_num}: Empty metadata.{field}")
    valid_difficulties = {"beginner", "intermediate", "advanced"}
    difficulty = metadata.get("difficulty", "")
    if difficulty and difficulty not in valid_difficulties:
        errors.append(
            f"Line {line_num}: Invalid metadata.difficulty '{difficulty}' "
            f"(must be one of {valid_difficulties})"
        )
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
        if msg["role"] == "assistant" and len(content) > MAX_ASSISTANT_MESSAGE_LENGTH:
            errors.append(
                f"Line {line_num}: Assistant message too long ({len(content)} chars)"
            )
        if msg["role"] == "user" and len(content) > MAX_USER_MESSAGE_LENGTH:
            errors.append(
                f"Line {line_num}: User message too long ({len(content)} chars)"
            )

    if roles_seen[0] != "system":
        errors.append(f"Line {line_num}: First message must be 'system'")

    if roles_seen[-1] != "assistant":
        errors.append(f"Line {line_num}: Last message must be 'assistant'")

    errors.extend(validate_metadata(example, line_num))

    return errors


def validate_file(filepath: Path) -> Dict[str, Any]:
    results = {"total": 0, "valid": 0, "errors": []}

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
        print("Usage: python validate_jsonl.py <file.jsonl> [--filter]")
        sys.exit(1)

    filepath = Path(sys.argv[1])
    filter_mode = "--filter" in sys.argv

    if not filepath.exists():
        print(f"Error: File not found: {filepath}")
        sys.exit(1)

    results = validate_file(filepath)

    print(f"\nValidation Results for {filepath}")
    print(f"=" * 50)
    print(f"Total examples: {results['total']}")
    print(f"Valid: {results['valid']}")
    print(f"Errors: {len(results['errors'])}")

    if filter_mode and results["errors"]:
        valid_examples = []
        error_lines = set()
        for err in results["errors"]:
            if "Line " in err:
                line_num = int(err.split("Line ")[1].split(":")[0])
                error_lines.add(line_num)

        with open(filepath, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                if line_num not in error_lines:
                    valid_examples.append(line)

        clean_path = filepath.parent / f"{filepath.stem}_valid{filepath.suffix}"
        with open(clean_path, "w", encoding="utf-8") as f:
            f.writelines(valid_examples)

        print(f"\n✓ Created filtered file: {clean_path}")
        print(f"  Removed {len(error_lines)} invalid examples")
        sys.exit(0)

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
