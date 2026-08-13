#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

from audit_utils import iter_text_files, relative_posix, resolve_root, write_json

MARKERS: dict[str, re.Pattern[str]] = {
    "TODO": re.compile(r"\bTODO\b", re.IGNORECASE),
    "FIXME": re.compile(r"\bFIXME\b", re.IGNORECASE),
    "HACK": re.compile(r"\bHACK\b", re.IGNORECASE),
    "XXX": re.compile(r"\bXXX\b"),
    "TEMPORARY": re.compile(r"\btemporary\b|\btemp workaround\b", re.IGNORECASE),
    "DEPRECATED": re.compile(r"\bdeprecated\b", re.IGNORECASE),
}
SEVERITY = {
    "TODO": "low", "FIXME": "medium", "HACK": "medium", "XXX": "medium",
    "TEMPORARY": "medium", "DEPRECATED": "low",
}


def python_complexity_signals(path: Path, text: str, root: Path) -> list[dict[str, Any]]:
    signals: list[dict[str, Any]] = []
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return signals
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        end_lineno = getattr(node, "end_lineno", None)
        if end_lineno is None:
            continue
        length = end_lineno - node.lineno + 1
        if isinstance(node, ast.ClassDef):
            threshold, kind = 350, "large_class"
        else:
            threshold, kind = 100, "large_function"
        if length >= threshold:
            signals.append({
                "category": "code", "signal": kind, "severity": "medium",
                "path": relative_posix(path, root), "line": node.lineno, "symbol": node.name,
                "details": f"{type(node).__name__} spans {length} lines.",
            })
    return signals


def collect(root: Path | str) -> dict[str, Any]:
    root_path = resolve_root(root)
    signals: list[dict[str, Any]] = []
    marker_counts: Counter[str] = Counter()
    large_files: list[dict[str, Any]] = []
    for path in iter_text_files(root_path):
        text = path.read_text(encoding="utf-8", errors="replace")
        relative = relative_posix(path, root_path)
        lines = text.splitlines()
        if len(lines) >= 1000:
            large_files.append({
                "category": "code", "signal": "large_file", "severity": "medium",
                "path": relative, "line_count": len(lines),
                "details": "Text/source file exceeds 1000 lines and should be reviewed for cohesion.",
            })
        for line_no, line in enumerate(lines, start=1):
            for marker, pattern in MARKERS.items():
                if not pattern.search(line):
                    continue
                marker_counts[marker] += 1
                snippet = line.strip()
                if len(snippet) > 240:
                    snippet = snippet[:237] + "..."
                signals.append({
                    "category": "code", "signal": f"marker:{marker.lower()}",
                    "severity": SEVERITY[marker], "path": relative, "line": line_no,
                    "details": snippet,
                })
        if path.suffix.lower() == ".py":
            signals.extend(python_complexity_signals(path, text, root_path))
    signals.extend(large_files)
    category_counts = Counter(item["signal"] for item in signals)
    return {
        "collector": "detect_technical_debt", "root": str(root_path),
        "summary": {
            "signal_count": len(signals), "marker_counts": dict(sorted(marker_counts.items())),
            "signal_counts": dict(sorted(category_counts.items())),
        },
        "signals": sorted(signals, key=lambda item: (item.get("path", ""), int(item.get("line", 0) or 0), item.get("signal", ""))),
        "limitations": [
            "Markers and size thresholds are triage signals, not proof of technical debt.",
            "This collector does not infer architectural debt without model-assisted repository reasoning.",
            "Large generated files should be excluded or marked not applicable by the auditor.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect technical-debt candidate signals.")
    parser.add_argument("root", nargs="?", default=".", type=Path)
    parser.add_argument("-o", "--output", type=Path)
    args = parser.parse_args()
    result = collect(args.root)
    if args.output:
        write_json(args.output, result)
        print(f"Wrote technical-debt signals to {args.output}")
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
