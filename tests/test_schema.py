from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator


def test_example_audit_matches_schema() -> None:
    root = Path(__file__).resolve().parents[1]
    schema = json.loads((root / "schema" / "audit.schema.json").read_text())
    example = json.loads((root / "examples" / "example-audit.json").read_text())

    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(example), key=lambda error: list(error.absolute_path))
    assert errors == []
