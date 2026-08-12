#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from audit_utils import load_json, write_json


def bootstrap(discovery: dict[str, Any], project_name: str | None = None) -> dict[str, Any]:
    collectors = discovery.get("collectors", {})
    module_outcome = collectors.get("modules", {})
    module_result = module_outcome.get("result", {}) if isinstance(module_outcome, dict) else {}
    candidates = module_result.get("module_candidates", []) if isinstance(module_result, dict) else []
    modules = []
    for candidate in candidates:
        if not isinstance(candidate, dict):
            continue
        modules.append({
            "id": candidate.get("id") or candidate.get("name", "unknown").lower(),
            "name": candidate.get("name") or candidate.get("path") or "Unknown",
            "path": candidate.get("path"), "role_hint": candidate.get("role_hint"),
            "classification": "unknown", "implementation": None, "integration": None,
            "validation": None, "documentation": None, "operational_readiness": None,
            "completion": None, "confirmed_completion": None, "quality": None,
            "confidence": None, "criticality": None, "evidence_level": "E0",
            "dependencies": [], "evidence_ids": [], "status": "unreviewed",
        })
    root = discovery.get("metadata", {}).get("root")
    inferred_name = Path(root).name if root else "Unknown project"
    return {
        "metadata": {
            "generated_at": datetime.now(timezone.utc).isoformat(), "auditor_version": "0.2.0",
            "repository": root, "commit": None, "snapshot_kind": "bootstrap",
        },
        "project": {
            "name": project_name or inferred_name, "mission": None, "target_users": [],
            "current_stage": None, "trl": None, "scope_status": "unreviewed",
        },
        "scores": {
            "confirmed_completion": None, "estimated_completion": None, "project_health": None,
            "prototype_readiness": None, "mvp_readiness": None, "commercial_readiness": None,
            "production_readiness": None, "scale_readiness": None,
            "research_readiness": None, "confidence": None,
        },
        "modules": modules, "dependency_edges": [], "evidence": [], "validation_runs": [],
        "risks": [], "technical_debt": [], "directions": [], "recommendations": [],
        "limitations": [
            "This snapshot is a bootstrap generated from deterministic discovery only.",
            "Scores remain null until Codex reviews evidence and applies the audit methodology.",
        ],
        "history": {},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Create an unscored audit skeleton from discovery.json.")
    parser.add_argument("discovery", type=Path)
    parser.add_argument("-o", "--output", type=Path, default=Path(".project-audit/audit.json"))
    parser.add_argument("--project-name")
    args = parser.parse_args()
    result = bootstrap(load_json(args.discovery), project_name=args.project_name)
    write_json(args.output, result)
    print(json.dumps({"output": str(args.output), "module_count": len(result["modules"])}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
