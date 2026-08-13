#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Callable

from audit_utils import load_json, write_json

EVIDENCE_RANK = {"E0": 0, "E1": 1, "E2": 2, "E3": 3, "E4": 4}


def index_by_id(items: Any) -> dict[str, dict[str, Any]]:
    if not isinstance(items, list):
        return {}
    return {
        str(item["id"]): item
        for item in items
        if isinstance(item, dict) and item.get("id")
    }


def numeric_range(value: Any, check: dict[str, Any]) -> tuple[bool, str]:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return False, f"expected numeric value, actual={value!r}"
    minimum = check.get("min")
    maximum = check.get("max")
    passed = (minimum is None or number >= float(minimum)) and (maximum is None or number <= float(maximum))
    return passed, f"expected range {minimum!r}..{maximum!r}, actual={number}"


def check_score_range(audit: dict[str, Any], check: dict[str, Any]) -> tuple[bool, str]:
    key = str(check.get("key", ""))
    scores = audit.get("scores", {}) if isinstance(audit.get("scores"), dict) else {}
    passed, detail = numeric_range(scores.get(key), check)
    return passed, f"score {key}: {detail}"


def check_module_classification(audit: dict[str, Any], check: dict[str, Any]) -> tuple[bool, str]:
    module_id = str(check.get("module_id", ""))
    expected = str(check.get("expected", ""))
    module = index_by_id(audit.get("modules", [])).get(module_id)
    actual = None if module is None else module.get("classification")
    return actual == expected, f"module {module_id} classification: expected={expected!r}, actual={actual!r}"


def check_module_score_range(audit: dict[str, Any], check: dict[str, Any]) -> tuple[bool, str]:
    module_id = str(check.get("module_id", ""))
    key = str(check.get("key", "completion"))
    module = index_by_id(audit.get("modules", [])).get(module_id)
    value = None if module is None else module.get(key)
    passed, detail = numeric_range(value, check)
    return passed, f"module {module_id} {key}: {detail}"


def check_readiness_state(audit: dict[str, Any], check: dict[str, Any]) -> tuple[bool, str]:
    gate_name = str(check.get("gate", ""))
    expected = str(check.get("expected", ""))
    gates = audit.get("readiness_gates", {}) if isinstance(audit.get("readiness_gates"), dict) else {}
    gate = gates.get(gate_name, {}) if isinstance(gates.get(gate_name), dict) else {}
    evaluation = gate.get("evaluation", {}) if isinstance(gate.get("evaluation"), dict) else {}
    actual = evaluation.get("state")
    return actual == expected, f"readiness {gate_name}: expected state={expected!r}, actual={actual!r}"


def presence_check(items: Any, check: dict[str, Any], label: str) -> tuple[bool, str]:
    item_id = str(check.get("id", ""))
    present = item_id in index_by_id(items)
    expected = bool(check.get("present", True))
    return present == expected, f"{label} {item_id}: expected present={expected}, actual={present}"


def check_risk_presence(audit: dict[str, Any], check: dict[str, Any]) -> tuple[bool, str]:
    return presence_check(audit.get("risks", []), check, "risk")


def check_bottleneck_presence(audit: dict[str, Any], check: dict[str, Any]) -> tuple[bool, str]:
    return presence_check(audit.get("bottlenecks", []), check, "bottleneck")


def check_recommendation_presence(audit: dict[str, Any], check: dict[str, Any]) -> tuple[bool, str]:
    return presence_check(audit.get("recommendations", []), check, "recommendation")


def check_module_evidence_level(audit: dict[str, Any], check: dict[str, Any]) -> tuple[bool, str]:
    module_id = str(check.get("module_id", ""))
    minimum = str(check.get("minimum", "E0"))
    maximum = check.get("maximum")
    module = index_by_id(audit.get("modules", [])).get(module_id)
    actual = "E0" if module is None else str(module.get("evidence_level", "E0"))
    actual_rank = EVIDENCE_RANK.get(actual, -1)
    min_rank = EVIDENCE_RANK.get(minimum, 0)
    max_rank = EVIDENCE_RANK.get(str(maximum), 4) if maximum is not None else 4
    passed = min_rank <= actual_rank <= max_rank
    return passed, f"module {module_id} evidence: expected {minimum}..{maximum or 'E4'}, actual={actual}"


def check_limitation_contains(audit: dict[str, Any], check: dict[str, Any]) -> tuple[bool, str]:
    needle = str(check.get("text", "")).lower()
    limitations = audit.get("limitations", []) if isinstance(audit.get("limitations"), list) else []
    present = any(needle in str(item).lower() for item in limitations)
    expected = bool(check.get("present", True))
    return present == expected, f"limitation contains {needle!r}: expected present={expected}, actual={present}"


CHECKERS: dict[str, Callable[[dict[str, Any], dict[str, Any]], tuple[bool, str]]] = {
    "score_range": check_score_range,
    "module_classification": check_module_classification,
    "module_score_range": check_module_score_range,
    "readiness_state": check_readiness_state,
    "risk_presence": check_risk_presence,
    "bottleneck_presence": check_bottleneck_presence,
    "recommendation_presence": check_recommendation_presence,
    "module_evidence_level": check_module_evidence_level,
    "limitation_contains": check_limitation_contains,
}


def evaluate(audit: dict[str, Any], golden: dict[str, Any]) -> dict[str, Any]:
    checks = golden.get("checks", []) if isinstance(golden, dict) else []
    if not isinstance(checks, list):
        raise ValueError("golden 'checks' must be a list")

    rendered: list[dict[str, Any]] = []
    passed_weight = 0.0
    total_weight = 0.0
    for raw in checks:
        if not isinstance(raw, dict):
            continue
        check = dict(raw)
        check_type = str(check.get("type", ""))
        weight = max(0.0, float(check.get("weight", 1.0)))
        total_weight += weight
        checker = CHECKERS.get(check_type)
        if checker is None:
            passed = False
            detail = f"unknown golden check type: {check_type}"
        else:
            passed, detail = checker(audit, check)
        if passed:
            passed_weight += weight
        rendered.append({"type": check_type, "weight": weight, "passed": passed, "detail": detail})

    score = 100.0 if total_weight <= 0 else round(100.0 * passed_weight / total_weight, 2)
    return {
        "golden_id": golden.get("id"),
        "score": score,
        "passed": sum(1 for item in rendered if item["passed"]),
        "failed": sum(1 for item in rendered if not item["passed"]),
        "checks": rendered,
        "notes": golden.get("notes", []),
        "interpretation": [
            "Golden audit checks should encode human-reviewed ranges and categorical expectations rather than arbitrary exact percentages.",
            "Passing a golden file demonstrates agreement with that reviewed expectation set; it does not prove universal audit correctness.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare an audit snapshot against human-reviewed golden expectations.")
    parser.add_argument("audit", type=Path)
    parser.add_argument("golden", type=Path)
    parser.add_argument("-o", "--output", type=Path)
    parser.add_argument("--minimum-score", type=float, default=100.0)
    args = parser.parse_args()

    result = evaluate(load_json(args.audit), load_json(args.golden))
    if args.output:
        write_json(args.output, result)
    print(json.dumps({"score": result["score"], "passed": result["passed"], "failed": result["failed"]}, indent=2))
    return 0 if float(result["score"]) >= float(args.minimum_score) else 1


if __name__ == "__main__":
    raise SystemExit(main())
