#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

TRACKED_SCORES = [
    "confirmed_completion",
    "estimated_completion",
    "project_health",
    "prototype_readiness",
    "mvp_readiness",
    "commercial_readiness",
    "production_readiness",
    "scale_readiness",
    "confidence",
]


def load(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def index_by_id(items: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    for item in items:
        item_id = item.get("id")
        if isinstance(item_id, str) and item_id:
            indexed[item_id] = item
    return indexed


def delta(old: Any, new: Any) -> float | None:
    if isinstance(old, (int, float)) and isinstance(new, (int, float)):
        return round(float(new) - float(old), 2)
    return None


def compare(old: dict[str, Any], new: dict[str, Any]) -> dict[str, Any]:
    old_scores = old.get("scores", {}) if isinstance(old.get("scores"), dict) else {}
    new_scores = new.get("scores", {}) if isinstance(new.get("scores"), dict) else {}

    score_deltas = {
        key: delta(old_scores.get(key), new_scores.get(key))
        for key in TRACKED_SCORES
        if old_scores.get(key) is not None or new_scores.get(key) is not None
    }

    old_modules = index_by_id(old.get("modules", []) if isinstance(old.get("modules"), list) else [])
    new_modules = index_by_id(new.get("modules", []) if isinstance(new.get("modules"), list) else [])
    module_changes: list[dict[str, Any]] = []
    for module_id in sorted(set(old_modules) | set(new_modules)):
        before = old_modules.get(module_id)
        after = new_modules.get(module_id)
        if before is None:
            module_changes.append({"id": module_id, "change": "added"})
            continue
        if after is None:
            module_changes.append({"id": module_id, "change": "removed"})
            continue
        completion_delta = delta(before.get("completion"), after.get("completion"))
        quality_delta = delta(before.get("quality"), after.get("quality"))
        confidence_delta = delta(before.get("confidence"), after.get("confidence"))
        if any(value not in (None, 0.0) for value in [completion_delta, quality_delta, confidence_delta]):
            module_changes.append({
                "id": module_id,
                "change": "updated",
                "completion_delta": completion_delta,
                "quality_delta": quality_delta,
                "confidence_delta": confidence_delta,
            })

    old_risks = index_by_id(old.get("risks", []) if isinstance(old.get("risks"), list) else [])
    new_risks = index_by_id(new.get("risks", []) if isinstance(new.get("risks"), list) else [])
    closed_risks = sorted(set(old_risks) - set(new_risks))
    new_risk_ids = sorted(set(new_risks) - set(old_risks))

    return {
        "score_deltas": score_deltas,
        "module_changes": module_changes,
        "closed_risks": closed_risks,
        "new_risks": new_risk_ids,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare two Project Intelligence Auditor snapshots.")
    parser.add_argument("old", type=Path)
    parser.add_argument("new", type=Path)
    parser.add_argument("-o", "--output", type=Path)
    args = parser.parse_args()

    result = compare(load(args.old), load(args.new))
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
        print(f"Wrote snapshot comparison to {args.output}")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
