#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from jsonschema import Draft202012Validator


def load_json(path: Path) -> object:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a Project Intelligence Auditor JSON snapshot.")
    parser.add_argument("audit", type=Path)
    parser.add_argument(
        "--schema",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "schema" / "audit.schema.json",
    )
    args = parser.parse_args()

    schema = load_json(args.schema)
    audit = load_json(args.audit)
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(audit), key=lambda error: list(error.absolute_path))

    if errors:
        for error in errors:
            location = ".".join(str(part) for part in error.absolute_path) or "<root>"
            print(f"ERROR {location}: {error.message}")
        print(f"Validation failed with {len(errors)} error(s).")
        return 1

    print(f"Audit snapshot is valid against {args.schema}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
