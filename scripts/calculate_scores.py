#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Iterable

COMPLETION_WEIGHTS = {
    "implementation": 0.35,
    "integration": 0.25,
    "validation": 0.20,
    "documentation": 0.05,
    "operational_readiness": 0.15,
}

EVIDENCE_MULTIPLIERS = {
    "E0": 0.00,
    "E1": 0.10,
    "E2": 0.45,
    "E3": 0.85,
    "E4": 1.00,
}

BASE_CRITICALITY = {
    "critical_path": 1.00,
    "important": 0.75,
    "optional": 0.35,
    "experimental": 0.20,
    "legacy": 0.15,
    "dead": 0.00,
    "unknown": 0.40,
}


def clamp(value: float, lower: float = 0.0, upper: float = 100.0) -> float:
    return max(lower, min(upper, value))


def weighted_mean(values: dict[str, float | None], weights: dict[str, float]) -> float | None:
    pairs: list[tuple[float, float]] = []
    for key, weight in weights.items():
        value = values.get(key)
        if value is None:
            continue
        pairs.append((float(value), float(weight)))
    if not pairs:
        return None
    total_weight = sum(weight for _, weight in pairs)
    if total_weight <= 0:
        return None
    return sum(value * weight for value, weight in pairs) / total_weight


def module_completion(module: dict[str, Any]) -> float | None:
    values = {key: module.get(key) for key in COMPLETION_WEIGHTS}
    result = weighted_mean(values, COMPLETION_WEIGHTS)
    return None if result is None else round(clamp(result), 2)


def module_confirmed_completion(module: dict[str, Any]) -> float | None:
    estimated = module_completion(module)
    if estimated is None:
        return None
    evidence_level = str(module.get("evidence_level", "E0"))
    multiplier = EVIDENCE_MULTIPLIERS.get(evidence_level, 0.0)
    return round(clamp(estimated * multiplier), 2)


def resolve_criticality(module: dict[str, Any]) -> float:
    explicit = module.get("criticality")
    if explicit is not None:
        try:
            return max(0.0, min(1.0, float(explicit)))
        except (TypeError, ValueError):
            pass
    classification = str(module.get("classification", "unknown"))
    return BASE_CRITICALITY.get(classification, BASE_CRITICALITY["unknown"])


def project_weight(module: dict[str, Any]) -> float:
    criticality = resolve_criticality(module)
    dependency_factor = max(0.0, min(1.0, float(module.get("dependency_factor", 0.5))))
    user_value_factor = max(0.0, min(1.0, float(module.get("user_value_factor", 0.5))))
    return criticality * (0.45 + 0.25 * dependency_factor + 0.30 * user_value_factor)


def weighted_project_metric(modules: Iterable[dict[str, Any]], key: str) -> float | None:
    numerator = 0.0
    denominator = 0.0
    for module in modules:
        value = module.get(key)
        if value is None:
            continue
        weight = project_weight(module)
        if weight <= 0:
            continue
        numerator += float(value) * weight
        denominator += weight
    if denominator == 0:
        return None
    return round(clamp(numerator / denominator), 2)


def calculate(data: dict[str, Any]) -> dict[str, Any]:
    modules = data.setdefault("modules", [])
    if not isinstance(modules, list):
        raise ValueError("'modules' must be a list")

    for module in modules:
        if not isinstance(module, dict):
            raise ValueError("each module must be an object")
        module["completion"] = module_completion(module)
        module["confirmed_completion"] = module_confirmed_completion(module)
        module["resolved_criticality"] = round(resolve_criticality(module), 4)
        module["project_weight"] = round(project_weight(module), 4)

    scores = data.setdefault("scores", {})
    if not isinstance(scores, dict):
        raise ValueError("'scores' must be an object")

    scores["estimated_completion"] = weighted_project_metric(modules, "completion")
    scores["confirmed_completion"] = weighted_project_metric(modules, "confirmed_completion")
    scores["project_health"] = weighted_project_metric(modules, "quality")
    scores["confidence"] = weighted_project_metric(modules, "confidence")

    return data


def main() -> int:
    parser = argparse.ArgumentParser(description="Calculate deterministic Project Intelligence Auditor scores.")
    parser.add_argument("input", type=Path, help="Input audit JSON file")
    parser.add_argument("-o", "--output", type=Path, help="Output path. Defaults to overwriting input.")
    args = parser.parse_args()

    with args.input.open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    result = calculate(data)
    output_path = args.output or args.input
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2)
        handle.write("\n")

    print(f"Wrote calculated scores to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
