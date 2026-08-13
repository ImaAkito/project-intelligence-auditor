#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path

NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def parse_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        raise ValueError("SKILL.md must start with YAML front matter delimited by ---")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise ValueError("SKILL.md front matter is missing the closing ---")
    fields: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            raise ValueError(f"Invalid front matter line: {line!r}")
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip().strip("\"'")
    return fields


def validate(path: Path) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8")
    try:
        fields = parse_frontmatter(text)
    except ValueError as exc:
        return [str(exc)]
    name = fields.get("name", "")
    description = fields.get("description", "")
    if not name:
        errors.append("front matter requires 'name'")
    elif not NAME_PATTERN.fullmatch(name):
        errors.append("'name' should use lowercase letters, digits, and single hyphens")
    if not description:
        errors.append("front matter requires 'description'")
    elif len(description) > 1024:
        errors.append("'description' is unexpectedly long (>1024 characters)")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate basic Project Intelligence Auditor SKILL.md invariants.")
    parser.add_argument("path", nargs="?", type=Path, default=Path("SKILL.md"))
    args = parser.parse_args()
    errors = validate(args.path)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"{args.path} has valid required skill front matter.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
