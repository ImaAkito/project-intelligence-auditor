#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from audit_utils import load_json, write_json
from evaluate_golden_audit import CHECKERS


def resolve_under(root: Path, value: Any) -> Path:
    path = Path(str(value))
    return path if path.is_absolute() else root / path


def validate(root: Path, manifest_path: Path) -> dict[str, Any]:
    manifest = load_json(manifest_path)
    cases = manifest.get("cases", []) if isinstance(manifest, dict) else []
    if not isinstance(cases, list):
        raise ValueError("challenge manifest 'cases' must be a list")

    issues: list[dict[str, str]] = []
    case_summaries: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    total_checks = 0

    for index, raw in enumerate(cases):
        if not isinstance(raw, dict):
            issues.append({"case": f"index:{index}", "issue": "case must be an object"})
            continue
        case_id = str(raw.get("id", "")).strip()
        if not case_id:
            issues.append({"case": f"index:{index}", "issue": "missing case id"})
            continue
        if case_id in seen_ids:
            issues.append({"case": case_id, "issue": "duplicate case id"})
        seen_ids.add(case_id)

        fixture = resolve_under(root, raw.get("fixture", ""))
        golden_path = resolve_under(root, raw.get("golden", ""))
        fixture_files = 0
        if not fixture.is_dir():
            issues.append({"case": case_id, "issue": f"fixture directory missing: {fixture}"})
        else:
            fixture_files = sum(1 for path in fixture.rglob("*") if path.is_file())
            if fixture_files == 0:
                issues.append({"case": case_id, "issue": "fixture directory is empty"})

        check_count = 0
        critical_count = 0
        if not golden_path.is_file():
            issues.append({"case": case_id, "issue": f"golden file missing: {golden_path}"})
        else:
            golden = load_json(golden_path)
            if str(golden.get("id", "")) != case_id:
                issues.append(
                    {
                        "case": case_id,
                        "issue": f"golden id mismatch: {golden.get('id')!r}",
                    }
                )
            checks = golden.get("checks", [])
            if not isinstance(checks, list) or not checks:
                issues.append({"case": case_id, "issue": "golden checks must be a non-empty list"})
            else:
                check_count = len(checks)
                total_checks += check_count
                for check_index, check in enumerate(checks):
                    if not isinstance(check, dict):
                        issues.append(
                            {
                                "case": case_id,
                                "issue": f"check {check_index} must be an object",
                            }
                        )
                        continue
                    check_type = str(check.get("type", ""))
                    if check_type not in CHECKERS:
                        issues.append(
                            {
                                "case": case_id,
                                "issue": f"unknown golden check type: {check_type!r}",
                            }
                        )
                    if check.get("critical") is True:
                        critical_count += 1
                if critical_count == 0:
                    issues.append(
                        {
                            "case": case_id,
                            "issue": "semantic challenge must include at least one critical check",
                        }
                    )

        case_summaries.append(
            {
                "id": case_id,
                "domain": raw.get("domain"),
                "fixture_files": fixture_files,
                "checks": check_count,
                "critical_checks": critical_count,
            }
        )

    return {
        "version": manifest.get("version"),
        "case_count": len(case_summaries),
        "check_count": total_checks,
        "issue_count": len(issues),
        "issues": issues,
        "cases": case_summaries,
        "valid": len(issues) == 0,
        "interpretation": [
            "Corpus validation checks structure and evaluator compatibility, not semantic audit accuracy.",
            "A semantic challenge becomes useful only after an independently produced audit is compared with its reviewed golden expectations.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the semantic challenge corpus contract.")
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--manifest", type=Path, default=Path("challenges/manifest.json"))
    parser.add_argument("-o", "--output", type=Path)
    args = parser.parse_args()

    root = args.root.resolve()
    manifest = args.manifest if args.manifest.is_absolute() else root / args.manifest
    result = validate(root, manifest)
    if args.output:
        write_json(args.output, result)
    print(json.dumps({"valid": result["valid"], "cases": result["case_count"], "checks": result["check_count"], "issues": result["issue_count"]}, indent=2))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
