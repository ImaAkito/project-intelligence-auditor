#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from audit_utils import bounded, load_json, normalize_effort, write_json

PHASE_THRESHOLDS = ((24.0, "NOW"), (13.0, "NEXT"), (7.0, "LATER"))


def numeric(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def leverage_score(item: dict[str, Any]) -> float:
    impact = bounded(numeric(item.get("impact"), 50.0))
    risk_reduction = bounded(numeric(item.get("risk_reduction"), 0.0))
    unlocks = item.get("unlocks", [])
    unlock_score = min(len(unlocks) * 15.0, 100.0) if isinstance(unlocks, list) else bounded(numeric(unlocks))
    critical_path = 100.0 if item.get("critical_path") is True else 0.0
    confidence = bounded(numeric(item.get("confidence"), 70.0)) / 100.0
    effort = normalize_effort(item.get("effort"))
    gross_value = 0.50 * impact + 0.25 * risk_reduction + 0.15 * unlock_score + 0.10 * critical_path
    return round((gross_value * (0.65 + 0.35 * confidence)) / effort, 2)


def phase_for(score: float, item: dict[str, Any]) -> str:
    if item.get("recommended_timing") in {"REMOVE", "DEFER", "OPTIONAL"}:
        return str(item["recommended_timing"])
    if item.get("do_not_build") is True:
        return "DEFER"
    for threshold, phase in PHASE_THRESHOLDS:
        if score >= threshold:
            return phase
    return "DEFER"


def rank_recommendations(data: dict[str, Any]) -> list[dict[str, Any]]:
    recommendations = data.get("recommendations", [])
    if not isinstance(recommendations, list):
        raise ValueError("'recommendations' must be a list")
    ranked: list[dict[str, Any]] = []
    for index, recommendation in enumerate(recommendations):
        if not isinstance(recommendation, dict):
            continue
        item = dict(recommendation)
        item["leverage_score"] = leverage_score(item)
        item["phase"] = phase_for(item["leverage_score"], item)
        item["_original_order"] = index
        ranked.append(item)
    order = {"NOW": 0, "NEXT": 1, "LATER": 2, "OPTIONAL": 3, "DEFER": 4, "REMOVE": 5}
    ranked.sort(key=lambda item: (order.get(item["phase"], 6), -item["leverage_score"], item["_original_order"]))
    for item in ranked:
        item.pop("_original_order", None)
    return ranked


def apply(data: dict[str, Any]) -> dict[str, Any]:
    data = dict(data)
    ranked = rank_recommendations(data)
    data["recommendations"] = ranked
    data["action_plan"] = {
        "top_actions": [item["id"] for item in ranked if item["phase"] == "NOW"][:7],
        "highest_leverage_action": next(
            (item["id"] for item in ranked if item["phase"] == "NOW"),
            ranked[0]["id"] if ranked else None,
        ),
        "phases": {
            phase: [item["id"] for item in ranked if item["phase"] == phase]
            for phase in ("NOW", "NEXT", "LATER", "OPTIONAL", "DEFER", "REMOVE")
        },
        "method": (
            "Deterministic leverage heuristic using impact, risk reduction, unlocks, "
            "critical-path status, confidence, and normalized effort."
        ),
    }
    return data


def main() -> int:
    parser = argparse.ArgumentParser(description="Rank audit recommendations by deterministic leverage.")
    parser.add_argument("input", type=Path)
    parser.add_argument("-o", "--output", type=Path)
    args = parser.parse_args()
    result = apply(load_json(args.input))
    output = args.output or args.input
    write_json(output, result)
    print(json.dumps(result["action_plan"], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
