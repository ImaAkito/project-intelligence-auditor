#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import analyze_git_history
import collect_dependencies
import collect_tests
import detect_false_completion
import detect_technical_debt
import discover_modules
import scan_repository
from audit_utils import resolve_root, write_json

Collector = Callable[[Path], dict[str, Any]]


def safe_collect(name: str, collector: Collector, root: Path) -> dict[str, Any]:
    try:
        return {"status": "ok", "result": collector(root)}
    except Exception as exc:
        return {"status": "error", "error": f"{type(exc).__name__}: {exc}", "collector": name}


def run(root: Path | str) -> dict[str, Any]:
    root_path = resolve_root(root)
    collectors: list[tuple[str, Collector]] = [
        ("repository", scan_repository.scan),
        ("modules", discover_modules.discover),
        ("dependencies", collect_dependencies.collect),
        ("tests", collect_tests.collect),
        ("false_completion", detect_false_completion.scan),
        ("technical_debt", detect_technical_debt.collect),
        ("git_history", analyze_git_history.collect),
    ]
    results: dict[str, Any] = {}
    failures: list[str] = []
    for name, collector in collectors:
        outcome = safe_collect(name, collector, root_path)
        results[name] = outcome
        if outcome["status"] != "ok":
            failures.append(name)
    return {
        "metadata": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "root": str(root_path), "collector_suite": "project-intelligence-auditor",
        },
        "collectors": results, "failed_collectors": failures,
        "instructions": [
            "Treat collector output as evidence candidates, not final conclusions.",
            "Inspect source context before converting heuristic signals into audit findings.",
            "Do not derive completion percentages directly from file counts, TODO counts, or Git activity.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run deterministic Project Intelligence Auditor evidence collectors.")
    parser.add_argument("root", nargs="?", default=".", type=Path)
    parser.add_argument("-o", "--output", type=Path, default=Path(".project-audit/discovery.json"))
    args = parser.parse_args()
    result = run(args.root)
    output = args.output
    if not output.is_absolute():
        output = resolve_root(args.root) / output
    write_json(output, result)
    print(json.dumps({"output": str(output), "failed_collectors": result["failed_collectors"]}, indent=2))
    return 1 if result["failed_collectors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
