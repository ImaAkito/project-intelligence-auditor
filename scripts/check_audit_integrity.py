#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Callable

from audit_utils import load_json, write_json

GROUP_WEIGHTS = {
    "module_traceability": 30.0,
    "dependency_traceability": 15.0,
    "risk_traceability": 10.0,
    "readiness_traceability": 20.0,
    "validation_traceability": 10.0,
    "recommendation_actionability": 15.0,
}

SCORED_MODULE_FIELDS = (
    "implementation",
    "integration",
    "validation",
    "documentation",
    "operational_readiness",
    "completion",
    "confirmed_completion",
    "quality",
    "confidence",
)


def valid_ids(values: Any, evidence_ids: set[str]) -> tuple[bool, list[str]]:
    if not isinstance(values, list) or not values:
        return False, []
    ids = [str(value) for value in values if str(value)]
    unknown = [value for value in ids if value not in evidence_ids]
    return bool(ids) and not unknown, unknown


def scored_module(module: dict[str, Any]) -> bool:
    return any(module.get(key) is not None for key in SCORED_MODULE_FIELDS)


def evaluate_items(
    items: list[dict[str, Any]],
    predicate: Callable[[dict[str, Any]], tuple[bool, str | None]],
) -> tuple[int, int, list[str]]:
    passed = 0
    total = 0
    issues: list[str] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        total += 1
        ok, issue = predicate(item)
        if ok:
            passed += 1
        elif issue:
            issues.append(issue)
    return passed, total, issues


def calculate(data: dict[str, Any]) -> dict[str, Any]:
    evidence = data.get("evidence", []) if isinstance(data.get("evidence"), list) else []
    evidence_ids = {
        str(item.get("id"))
        for item in evidence
        if isinstance(item, dict) and item.get("id")
    }

    group_results: dict[str, dict[str, Any]] = {}
    issues: list[dict[str, str]] = []

    modules = [
        item for item in data.get("modules", [])
        if isinstance(item, dict) and scored_module(item)
    ]

    def module_check(item: dict[str, Any]) -> tuple[bool, str | None]:
        ok, unknown = valid_ids(item.get("evidence_ids"), evidence_ids)
        if not ok:
            name = item.get("id") or item.get("name") or "unknown"
            if unknown:
                return False, f"module {name} references unknown evidence IDs: {', '.join(unknown)}"
            return False, f"scored module {name} has no linked evidence"
        if str(item.get("evidence_level", "E0")) == "E0":
            return False, f"scored module {name} still declares E0 evidence"
        return True, None

    module_passed, module_total, module_issues = evaluate_items(modules, module_check)
    group_results["module_traceability"] = {"passed": module_passed, "total": module_total}
    issues.extend({"severity": "high", "group": "module_traceability", "message": message} for message in module_issues)

    edges = [item for item in data.get("dependency_edges", []) if isinstance(item, dict)]

    def edge_check(item: dict[str, Any]) -> tuple[bool, str | None]:
        ok, unknown = valid_ids(item.get("evidence_ids"), evidence_ids)
        label = f"{item.get('from', '?')} -> {item.get('to', '?')}"
        if unknown:
            return False, f"dependency edge {label} references unknown evidence IDs: {', '.join(unknown)}"
        if not ok:
            return False, f"dependency edge {label} has no linked evidence"
        return True, None

    edge_passed, edge_total, edge_issues = evaluate_items(edges, edge_check)
    group_results["dependency_traceability"] = {"passed": edge_passed, "total": edge_total}
    issues.extend({"severity": "medium", "group": "dependency_traceability", "message": message} for message in edge_issues)

    risks = [item for item in data.get("risks", []) if isinstance(item, dict)]

    def risk_check(item: dict[str, Any]) -> tuple[bool, str | None]:
        ok, unknown = valid_ids(item.get("evidence_ids"), evidence_ids)
        name = item.get("id") or item.get("title") or "unknown"
        if unknown:
            return False, f"risk {name} references unknown evidence IDs: {', '.join(unknown)}"
        if not ok:
            return False, f"risk {name} has no linked evidence"
        return True, None

    risk_passed, risk_total, risk_issues = evaluate_items(risks, risk_check)
    group_results["risk_traceability"] = {"passed": risk_passed, "total": risk_total}
    issues.extend({"severity": "medium", "group": "risk_traceability", "message": message} for message in risk_issues)

    readiness_criteria: list[dict[str, Any]] = []
    gates = data.get("readiness_gates", {})
    if isinstance(gates, dict):
        for gate_name, gate in gates.items():
            if not isinstance(gate, dict):
                continue
            criteria = gate.get("criteria", [])
            if not isinstance(criteria, list):
                continue
            for criterion in criteria:
                if not isinstance(criterion, dict):
                    continue
                status = str(criterion.get("status", "unknown")).lower()
                if status in {"pass", "partial", "fail"}:
                    readiness_criteria.append({**criterion, "_gate": str(gate_name)})

    def readiness_check(item: dict[str, Any]) -> tuple[bool, str | None]:
        ok, unknown = valid_ids(item.get("evidence_ids"), evidence_ids)
        label = f"{item.get('_gate', '?')}/{item.get('id', '?')}"
        if unknown:
            return False, f"readiness criterion {label} references unknown evidence IDs: {', '.join(unknown)}"
        if not ok:
            return False, f"assessed readiness criterion {label} has no linked evidence"
        confidence = item.get("confidence")
        if confidence is None:
            return False, f"assessed readiness criterion {label} has no confidence value"
        return True, None

    readiness_passed, readiness_total, readiness_issues = evaluate_items(readiness_criteria, readiness_check)
    group_results["readiness_traceability"] = {"passed": readiness_passed, "total": readiness_total}
    issues.extend({"severity": "high", "group": "readiness_traceability", "message": message} for message in readiness_issues)

    validations = [
        item for item in data.get("validation_runs", [])
        if isinstance(item, dict) and str(item.get("status")) != "not_applicable"
    ]

    def validation_check(item: dict[str, Any]) -> tuple[bool, str | None]:
        ok, unknown = valid_ids(item.get("evidence_ids"), evidence_ids)
        name = item.get("id") or item.get("action") or "unknown"
        if unknown:
            return False, f"validation run {name} references unknown evidence IDs: {', '.join(unknown)}"
        if not ok:
            return False, f"validation run {name} has no linked evidence"
        return True, None

    validation_passed, validation_total, validation_issues = evaluate_items(validations, validation_check)
    group_results["validation_traceability"] = {"passed": validation_passed, "total": validation_total}
    issues.extend({"severity": "medium", "group": "validation_traceability", "message": message} for message in validation_issues)

    recommendations = [item for item in data.get("recommendations", []) if isinstance(item, dict)]

    def recommendation_check(item: dict[str, Any]) -> tuple[bool, str | None]:
        required = ("title", "impact", "effort", "confidence", "definition_of_done", "why")
        missing = [key for key in required if item.get(key) in (None, "", [])]
        name = item.get("id") or item.get("title") or "unknown"
        if missing:
            return False, f"recommendation {name} is missing actionability fields: {', '.join(missing)}"
        return True, None

    rec_passed, rec_total, rec_issues = evaluate_items(recommendations, recommendation_check)
    group_results["recommendation_actionability"] = {"passed": rec_passed, "total": rec_total}
    issues.extend({"severity": "medium", "group": "recommendation_actionability", "message": message} for message in rec_issues)

    weighted_numerator = 0.0
    weighted_denominator = 0.0
    for group, weight in GROUP_WEIGHTS.items():
        result = group_results[group]
        total = int(result["total"])
        if total <= 0:
            result["coverage"] = None
            result["weight_used"] = 0.0
            continue
        coverage = 100.0 * int(result["passed"]) / total
        result["coverage"] = round(coverage, 2)
        result["weight_used"] = weight
        weighted_numerator += coverage * weight
        weighted_denominator += weight

    integrity_coverage = None if weighted_denominator <= 0 else round(weighted_numerator / weighted_denominator, 2)
    return {
        "integrity_coverage": integrity_coverage,
        "groups": group_results,
        "issue_count": len(issues),
        "issues": issues,
        "evidence_count": len(evidence_ids),
        "interpretation": [
            "Integrity coverage measures structural traceability and actionability of the audit artifact; it does not prove that the underlying judgments are semantically correct.",
            "A high score means important structured claims are linked and internally complete, not that the audited project itself is healthy or ready.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Check structural traceability and actionability of an audit snapshot.")
    parser.add_argument("audit", type=Path)
    parser.add_argument("-o", "--output", type=Path)
    parser.add_argument("--minimum-coverage", type=float, default=85.0)
    args = parser.parse_args()

    result = calculate(load_json(args.audit))
    if args.output:
        write_json(args.output, result)
    print(json.dumps({
        "integrity_coverage": result["integrity_coverage"],
        "issue_count": result["issue_count"],
    }, ensure_ascii=False, indent=2))
    coverage = result["integrity_coverage"]
    return 0 if coverage is not None and float(coverage) >= float(args.minimum_coverage) else 1


if __name__ == "__main__":
    raise SystemExit(main())
