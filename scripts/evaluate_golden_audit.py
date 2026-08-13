#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import operator
from pathlib import Path
from typing import Any, Callable

from audit_utils import load_json, write_json

EVIDENCE_RANK = {"E0": 0, "E1": 1, "E2": 2, "E3": 3, "E4": 4}
RELATIONS: dict[str, Callable[[float, float], bool]] = {
    ">": operator.gt,
    ">=": operator.ge,
    "<": operator.lt,
    "<=": operator.le,
    "==": operator.eq,
    "!=": operator.ne,
}


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
    passed = (minimum is None or number >= float(minimum)) and (
        maximum is None or number <= float(maximum)
    )
    return passed, f"expected range {minimum!r}..{maximum!r}, actual={number}"


def check_score_range(audit: dict[str, Any], check: dict[str, Any]) -> tuple[bool, str]:
    key = str(check.get("key", ""))
    scores = audit.get("scores", {}) if isinstance(audit.get("scores"), dict) else {}
    passed, detail = numeric_range(scores.get(key), check)
    return passed, f"score {key}: {detail}"


def check_score_relation(audit: dict[str, Any], check: dict[str, Any]) -> tuple[bool, str]:
    scores = audit.get("scores", {}) if isinstance(audit.get("scores"), dict) else {}
    left_key = str(check.get("left", ""))
    right_key = str(check.get("right", ""))
    relation = str(check.get("op", ">"))
    try:
        left = float(scores.get(left_key))
        right = float(scores.get(right_key))
    except (TypeError, ValueError):
        return False, f"score relation requires numeric {left_key!r} and {right_key!r}"
    margin = float(check.get("margin", 0.0))
    comparator = RELATIONS.get(relation)
    if comparator is None:
        return False, f"unknown score relation operator: {relation!r}"
    adjusted_right = right + margin if relation in {">", ">="} else right - margin
    passed = comparator(left, adjusted_right)
    return (
        passed,
        f"score relation: {left_key}={left} {relation} {right_key}={right} "
        f"with margin={margin}",
    )


def check_module_classification(audit: dict[str, Any], check: dict[str, Any]) -> tuple[bool, str]:
    module_id = str(check.get("module_id", ""))
    expected = str(check.get("expected", ""))
    module = index_by_id(audit.get("modules", [])).get(module_id)
    actual = None if module is None else module.get("classification")
    return actual == expected, (
        f"module {module_id} classification: expected={expected!r}, actual={actual!r}"
    )


def check_module_score_range(audit: dict[str, Any], check: dict[str, Any]) -> tuple[bool, str]:
    module_id = str(check.get("module_id", ""))
    key = str(check.get("key", "completion"))
    module = index_by_id(audit.get("modules", [])).get(module_id)
    value = None if module is None else module.get(key)
    passed, detail = numeric_range(value, check)
    return passed, f"module {module_id} {key}: {detail}"


def readiness_state(audit: dict[str, Any], gate_name: str) -> Any:
    gates = audit.get("readiness_gates", {}) if isinstance(audit.get("readiness_gates"), dict) else {}
    gate = gates.get(gate_name, {}) if isinstance(gates.get(gate_name), dict) else {}
    evaluation = gate.get("evaluation", {}) if isinstance(gate.get("evaluation"), dict) else {}
    return evaluation.get("state")


def check_readiness_state(audit: dict[str, Any], check: dict[str, Any]) -> tuple[bool, str]:
    gate_name = str(check.get("gate", ""))
    expected = str(check.get("expected", ""))
    actual = readiness_state(audit, gate_name)
    return actual == expected, (
        f"readiness {gate_name}: expected state={expected!r}, actual={actual!r}"
    )


def check_readiness_state_in(audit: dict[str, Any], check: dict[str, Any]) -> tuple[bool, str]:
    gate_name = str(check.get("gate", ""))
    allowed_raw = check.get("allowed", [])
    allowed = {str(item) for item in allowed_raw} if isinstance(allowed_raw, list) else set()
    actual = readiness_state(audit, gate_name)
    return actual in allowed, (
        f"readiness {gate_name}: allowed={sorted(allowed)!r}, actual={actual!r}"
    )


def presence_check(items: Any, check: dict[str, Any], label: str) -> tuple[bool, str]:
    item_id = str(check.get("id", ""))
    present = item_id in index_by_id(items)
    expected = bool(check.get("present", True))
    return present == expected, (
        f"{label} {item_id}: expected present={expected}, actual={present}"
    )


def check_risk_presence(audit: dict[str, Any], check: dict[str, Any]) -> tuple[bool, str]:
    return presence_check(audit.get("risks", []), check, "risk")


def check_bottleneck_presence(audit: dict[str, Any], check: dict[str, Any]) -> tuple[bool, str]:
    return presence_check(audit.get("bottlenecks", []), check, "bottleneck")


def check_recommendation_presence(audit: dict[str, Any], check: dict[str, Any]) -> tuple[bool, str]:
    return presence_check(audit.get("recommendations", []), check, "recommendation")


def item_texts(items: Any, fields: list[str]) -> list[str]:
    if not isinstance(items, list):
        return []
    rendered: list[str] = []
    for item in items:
        if isinstance(item, str):
            rendered.append(item)
        elif isinstance(item, dict):
            rendered.append(" ".join(str(item.get(field, "")) for field in fields))
    return rendered


def check_item_text_contains(audit: dict[str, Any], check: dict[str, Any]) -> tuple[bool, str]:
    section = str(check.get("section", ""))
    needle = str(check.get("text", "")).strip().lower()
    fields_raw = check.get(
        "fields",
        ["id", "title", "name", "description", "why", "mitigation", "rationale"],
    )
    fields = [str(item) for item in fields_raw] if isinstance(fields_raw, list) else []
    values = item_texts(audit.get(section, []), fields)
    present = any(needle in value.lower() for value in values)
    expected = bool(check.get("present", True))
    return present == expected, (
        f"section {section} contains {needle!r}: expected={expected}, actual={present}"
    )


def check_count_range(audit: dict[str, Any], check: dict[str, Any]) -> tuple[bool, str]:
    section = str(check.get("section", ""))
    items = audit.get(section, [])
    count = len(items) if isinstance(items, (list, dict)) else 0
    passed, detail = numeric_range(count, check)
    return passed, f"section {section} count: {detail}"


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
    return passed, (
        f"module {module_id} evidence: expected {minimum}..{maximum or 'E4'}, actual={actual}"
    )


def check_limitation_contains(audit: dict[str, Any], check: dict[str, Any]) -> tuple[bool, str]:
    needle = str(check.get("text", "")).lower()
    limitations = audit.get("limitations", []) if isinstance(audit.get("limitations"), list) else []
    present = any(needle in str(item).lower() for item in limitations)
    expected = bool(check.get("present", True))
    return present == expected, (
        f"limitation contains {needle!r}: expected present={expected}, actual={present}"
    )


def check_commercialization_field(audit: dict[str, Any], check: dict[str, Any]) -> tuple[bool, str]:
    commercial = audit.get("commercialization", {})
    commercial = commercial if isinstance(commercial, dict) else {}
    key = str(check.get("key", ""))
    value = commercial.get(key)
    state = str(check.get("state", "any"))
    contains = check.get("contains")

    if state == "missing":
        passed = key not in commercial or value is None
    elif state == "empty":
        passed = value in (None, "", [], {})
    elif state == "nonempty":
        passed = value not in (None, "", [], {})
    else:
        passed = True

    if passed and contains is not None:
        passed = str(contains).lower() in str(value).lower()
    return passed, (
        f"commercialization.{key}: state={state!r}, contains={contains!r}, actual={value!r}"
    )


CHECKERS: dict[str, Callable[[dict[str, Any], dict[str, Any]], tuple[bool, str]]] = {
    "score_range": check_score_range,
    "score_relation": check_score_relation,
    "module_classification": check_module_classification,
    "module_score_range": check_module_score_range,
    "readiness_state": check_readiness_state,
    "readiness_state_in": check_readiness_state_in,
    "risk_presence": check_risk_presence,
    "bottleneck_presence": check_bottleneck_presence,
    "recommendation_presence": check_recommendation_presence,
    "item_text_contains": check_item_text_contains,
    "count_range": check_count_range,
    "module_evidence_level": check_module_evidence_level,
    "limitation_contains": check_limitation_contains,
    "commercialization_field": check_commercialization_field,
}


def evaluate(audit: dict[str, Any], golden: dict[str, Any]) -> dict[str, Any]:
    checks = golden.get("checks", []) if isinstance(golden, dict) else []
    if not isinstance(checks, list):
        raise ValueError("golden 'checks' must be a list")

    rendered: list[dict[str, Any]] = []
    passed_weight = 0.0
    total_weight = 0.0
    critical_failed = 0
    for raw in checks:
        if not isinstance(raw, dict):
            continue
        check = dict(raw)
        check_type = str(check.get("type", ""))
        weight = max(0.0, float(check.get("weight", 1.0)))
        critical = check.get("critical") is True
        total_weight += weight
        checker = CHECKERS.get(check_type)
        if checker is None:
            passed = False
            detail = f"unknown golden check type: {check_type}"
        else:
            passed, detail = checker(audit, check)
        if passed:
            passed_weight += weight
        elif critical:
            critical_failed += 1
        rendered.append(
            {
                "type": check_type,
                "weight": weight,
                "critical": critical,
                "passed": passed,
                "detail": detail,
            }
        )

    score = 100.0 if total_weight <= 0 else round(100.0 * passed_weight / total_weight, 2)
    return {
        "golden_id": golden.get("id"),
        "score": score,
        "passed": sum(1 for item in rendered if item["passed"]),
        "failed": sum(1 for item in rendered if not item["passed"]),
        "critical_failed": critical_failed,
        "checks": rendered,
        "notes": golden.get("notes", []),
        "interpretation": [
            "Golden checks encode human-reviewed ranges, relations, and categorical expectations rather than arbitrary exact percentages.",
            "Critical checks represent semantic requirements whose failure should not be hidden by a high weighted average.",
            "Passing a golden file demonstrates agreement with that reviewed expectation set; it does not prove universal audit correctness.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compare an audit snapshot against human-reviewed golden expectations."
    )
    parser.add_argument("audit", type=Path)
    parser.add_argument("golden", type=Path)
    parser.add_argument("-o", "--output", type=Path)
    parser.add_argument("--minimum-score", type=float, default=100.0)
    parser.add_argument("--allow-critical-failures", action="store_true")
    args = parser.parse_args()

    result = evaluate(load_json(args.audit), load_json(args.golden))
    if args.output:
        write_json(args.output, result)
    print(
        json.dumps(
            {
                "score": result["score"],
                "passed": result["passed"],
                "failed": result["failed"],
                "critical_failed": result["critical_failed"],
            },
            indent=2,
        )
    )
    score_ok = float(result["score"]) >= float(args.minimum_score)
    critical_ok = args.allow_critical_failures or int(result["critical_failed"]) == 0
    return 0 if score_ok and critical_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
