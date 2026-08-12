#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from audit_utils import iter_text_files, relative_posix, resolve_root, write_json

PATTERNS: list[tuple[str, re.Pattern[str], str]] = [
    ("todo", re.compile(r"\bTODO\b", re.IGNORECASE), "low"),
    ("fixme", re.compile(r"\bFIXME\b", re.IGNORECASE), "medium"),
    ("hack", re.compile(r"\bHACK\b", re.IGNORECASE), "medium"),
    ("not_implemented", re.compile(r"NotImplemented(?:Error)?|not\s+implemented", re.IGNORECASE), "high"),
    ("placeholder", re.compile(r"placeholder|stub(?:bed)?|dummy\s+(?:data|value|response)", re.IGNORECASE), "medium"),
    (
        "hardcoded_success",
        re.compile(
            r"return\s+(?:True|\{\s*[\"']success[\"']\s*:\s*True)|"
            r"status\s*=\s*[\"']success[\"']", re.IGNORECASE,
        ),
        "medium",
    ),
    ("silent_exception", re.compile(r"except(?:\s+(?:Exception|BaseException))?\s*:\s*(?:pass|continue)\b"), "high"),
    ("disabled_validation", re.compile(r"(?:skip|disable|bypass).{0,30}(?:validation|check|auth|security)", re.IGNORECASE), "high"),
    ("mock_marker", re.compile(r"\bmock(?:ed|ing)?\b|fake[_\- ]?(?:api|service|response|data)", re.IGNORECASE), "medium"),
]


@dataclass
class Finding:
    kind: str
    severity: str
    path: str
    line: int
    excerpt: str


def scan_file(root: Path, path: Path) -> list[Finding]:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    findings: list[Finding] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if not stripped:
            continue
        for kind, pattern, severity in PATTERNS:
            if pattern.search(line):
                findings.append(Finding(
                    kind=kind, severity=severity, path=relative_posix(path, root),
                    line=line_number, excerpt=stripped[:240],
                ))
    return findings


def scan(root: Path | str) -> dict[str, Any]:
    root_path = resolve_root(root)
    findings: list[Finding] = []
    for path in iter_text_files(root_path):
        findings.extend(scan_file(root_path, path))
    return {
        "collector": "detect_false_completion", "root": str(root_path),
        "count": len(findings), "findings": [asdict(item) for item in findings],
        "note": "These are evidence candidates, not automatic defects. Review them in context before scoring.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect potential false-completion signals.")
    parser.add_argument("root", nargs="?", default=".", type=Path)
    parser.add_argument("-o", "--output", type=Path)
    args = parser.parse_args()
    payload = scan(args.root)
    if args.output:
        write_json(args.output, payload)
        print(f"Wrote {payload['count']} findings to {args.output}")
    else:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
