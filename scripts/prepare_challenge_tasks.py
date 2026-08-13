#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from audit_utils import load_json

TASK_TEMPLATE = """# Project Intelligence Auditor semantic challenge: {case_id}

Audit only this fixture repository:

`{fixture}`

Use the normal Project Intelligence Auditor workflow. Treat the fixture as the project under review.

Requirements:

- do not inspect files outside the fixture for expected answers;
- do not inspect challenge golden contracts;
- recover project intent from the fixture itself;
- run safe deterministic discovery/validation when feasible;
- keep completion, quality, readiness, confidence, and evidence separate;
- apply relevant domain-specific review methodology;
- surface material risks and highest-leverage recommendations;
- preserve unknowns rather than inventing evidence;
- produce a canonical audit JSON compatible with the auditor schema.

Save the final canonical audit JSON to:

`{result_path}`

This is a blind calibration run. Do not optimize wording or scores for an expected answer contract.
"""


def resolve_under(root: Path, value: Any) -> Path:
    path = Path(str(value))
    return path if path.is_absolute() else root / path


def prepare(root: Path, manifest_path: Path, output_dir: Path, results_dir: Path) -> dict[str, Any]:
    manifest = load_json(manifest_path)
    cases = manifest.get("cases", []) if isinstance(manifest, dict) else []
    if not isinstance(cases, list):
        raise ValueError("challenge manifest 'cases' must be a list")

    output_dir.mkdir(parents=True, exist_ok=True)
    results_dir.mkdir(parents=True, exist_ok=True)
    written: list[dict[str, str]] = []

    for raw in cases:
        if not isinstance(raw, dict) or not raw.get("id"):
            continue
        case_id = str(raw["id"])
        fixture = resolve_under(root, raw.get("fixture", ""))
        result_path = results_dir / f"{case_id}.json"
        task_path = output_dir / f"{case_id}.md"
        task_path.write_text(
            TASK_TEMPLATE.format(
                case_id=case_id,
                fixture=fixture,
                result_path=result_path,
            ),
            encoding="utf-8",
        )
        written.append(
            {
                "id": case_id,
                "task": str(task_path),
                "fixture": str(fixture),
                "result": str(result_path),
            }
        )

    return {"task_count": len(written), "tasks": written}


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate blind semantic challenge task files.")
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--manifest", type=Path, default=Path("challenges/manifest.json"))
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(".project-audit/challenge-tasks"),
    )
    parser.add_argument(
        "--results-dir",
        type=Path,
        default=Path(".project-audit/challenge-results"),
    )
    args = parser.parse_args()

    root = args.root.resolve()
    manifest = args.manifest if args.manifest.is_absolute() else root / args.manifest
    output_dir = args.output_dir if args.output_dir.is_absolute() else root / args.output_dir
    results_dir = args.results_dir if args.results_dir.is_absolute() else root / args.results_dir
    result = prepare(root, manifest, output_dir, results_dir)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
