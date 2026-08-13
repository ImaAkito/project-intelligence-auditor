#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from audit_utils import load_json, write_json
from evaluate_golden_audit import evaluate


def resolve_under(root: Path, value: Any) -> Path:
    path = Path(str(value))
    return path if path.is_absolute() else root / path


def markdown_report(result: dict[str, Any]) -> str:
    lines = [
        "# Semantic Challenge Evaluation",
        "",
        f"- Aggregate score: **{result['aggregate_score']:.2f}%**",
        f"- Evaluated cases: **{result['evaluated_cases']} / {result['case_count']}**",
        f"- Critical failures: **{result['critical_failed']}**",
        f"- Missing result files: **{len(result['missing_cases'])}**",
        "",
        "| Case | Domain | Score | Critical failures | Status |",
        "|---|---|---:|---:|---|",
    ]
    for case in result["cases"]:
        score = "—" if case.get("score") is None else f"{case['score']:.2f}%"
        lines.append(
            f"| {case['id']} | {case.get('domain') or '—'} | {score} | "
            f"{case.get('critical_failed', 0)} | {case['status']} |"
        )
    lines.extend(
        [
            "",
            "> This score measures agreement with the reviewed challenge expectations. "
            "It is not a universal accuracy estimate for arbitrary repositories.",
            "",
        ]
    )
    return "\n".join(lines)


def evaluate_corpus(root: Path, manifest_path: Path, results_dir: Path) -> dict[str, Any]:
    manifest = load_json(manifest_path)
    cases = manifest.get("cases", []) if isinstance(manifest, dict) else []
    if not isinstance(cases, list):
        raise ValueError("challenge manifest 'cases' must be a list")

    rendered: list[dict[str, Any]] = []
    missing: list[str] = []
    weighted_score = 0.0
    total_weight = 0.0
    critical_failed = 0

    for raw in cases:
        if not isinstance(raw, dict):
            continue
        case_id = str(raw.get("id", ""))
        domain = raw.get("domain")
        weight = max(0.0, float(raw.get("weight", 1.0)))
        result_path = results_dir / f"{case_id}.json"
        golden_path = resolve_under(root, raw.get("golden", ""))

        if not result_path.is_file():
            missing.append(case_id)
            rendered.append(
                {
                    "id": case_id,
                    "domain": domain,
                    "weight": weight,
                    "status": "missing",
                    "score": None,
                    "critical_failed": 0,
                    "result": str(result_path),
                    "golden": str(golden_path),
                }
            )
            continue

        evaluation = evaluate(load_json(result_path), load_json(golden_path))
        score = float(evaluation["score"])
        total_weight += weight
        weighted_score += score * weight
        critical_failed += int(evaluation.get("critical_failed", 0))
        rendered.append(
            {
                "id": case_id,
                "domain": domain,
                "weight": weight,
                "status": "passed" if evaluation.get("critical_failed", 0) == 0 else "critical_failure",
                "score": score,
                "critical_failed": evaluation.get("critical_failed", 0),
                "passed_checks": evaluation.get("passed"),
                "failed_checks": evaluation.get("failed"),
                "result": str(result_path),
                "golden": str(golden_path),
                "evaluation": evaluation,
            }
        )

    aggregate = 0.0 if total_weight <= 0 else weighted_score / total_weight
    return {
        "version": manifest.get("version"),
        "case_count": len([item for item in cases if isinstance(item, dict)]),
        "evaluated_cases": len(rendered) - len(missing),
        "aggregate_score": round(aggregate, 2),
        "critical_failed": critical_failed,
        "missing_cases": missing,
        "cases": rendered,
        "interpretation": [
            "The aggregate score measures agreement with case-specific reviewed semantic expectations.",
            "Missing cases are reported separately and are not silently scored as zero.",
            "Critical semantic failures should block calibration acceptance even when the weighted average is high.",
            "Challenge results are calibration evidence, not a guarantee of correctness on unrelated repositories.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate Project Intelligence Auditor semantic challenge outputs.")
    parser.add_argument("results_dir", type=Path)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--manifest", type=Path, default=Path("challenges/manifest.json"))
    parser.add_argument("--minimum-score", type=float, default=80.0)
    parser.add_argument("--require-all", action="store_true")
    parser.add_argument("--allow-critical-failures", action="store_true")
    parser.add_argument("-o", "--output", type=Path)
    parser.add_argument("--markdown", type=Path)
    args = parser.parse_args()

    root = args.root.resolve()
    manifest = args.manifest if args.manifest.is_absolute() else root / args.manifest
    results_dir = args.results_dir if args.results_dir.is_absolute() else root / args.results_dir
    result = evaluate_corpus(root, manifest, results_dir)

    if args.output:
        write_json(args.output, result)
    if args.markdown:
        args.markdown.parent.mkdir(parents=True, exist_ok=True)
        args.markdown.write_text(markdown_report(result), encoding="utf-8")

    print(
        json.dumps(
            {
                "aggregate_score": result["aggregate_score"],
                "evaluated_cases": result["evaluated_cases"],
                "missing_cases": result["missing_cases"],
                "critical_failed": result["critical_failed"],
            },
            indent=2,
        )
    )
    score_ok = float(result["aggregate_score"]) >= float(args.minimum_score)
    coverage_ok = not args.require_all or not result["missing_cases"]
    critical_ok = args.allow_critical_failures or int(result["critical_failed"]) == 0
    return 0 if score_ok and coverage_ok and critical_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
