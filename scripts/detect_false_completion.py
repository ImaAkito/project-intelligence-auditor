#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

TEXT_EXTENSIONS = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".java", ".kt", ".kts", ".go", ".rs",
    ".c", ".cc", ".cpp", ".h", ".hpp", ".cs", ".php", ".rb", ".swift", ".scala",
    ".sh", ".bash", ".zsh", ".ps1", ".sql", ".yaml", ".yml", ".toml", ".json",
    ".md", ".rst", ".txt", ".html", ".css", ".scss", ".vue", ".svelte"
}

IGNORED_DIRS = {
    ".git", ".hg", ".svn", "node_modules", ".venv", "venv", "env", "dist", "build",
    "coverage", "htmlcov", ".next", ".cache", ".pytest_cache", ".mypy_cache", ".ruff_cache"
}

PATTERNS: list[tuple[str, re.Pattern[str], str]] = [
    ("todo", re.compile(r"\bTODO\b", re.IGNORECASE), "low"),
    ("fixme", re.compile(r"\bFIXME\b", re.IGNORECASE), "medium"),
    ("hack", re.compile(r"\bHACK\b", re.IGNORECASE), "medium"),
    ("not_implemented", re.compile(r"NotImplemented(?:Error)?|not\s+implemented", re.IGNORECASE), "high"),
    ("placeholder", re.compile(r"placeholder|stub(?:bed)?|dummy\s+(?:data|value|response)", re.IGNORECASE), "medium"),
    ("hardcoded_success", re.compile(r"return\s+(?:True|\{\s*[\"']success[\"']\s*:\s*True)|status\s*=\s*[\"']success[\"']", re.IGNORECASE), "medium"),
    ("silent_exception", re.compile(r"except(?:\s+Exception)?\s*:\s*(?:pass|continue)\b"), "high"),
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


def iter_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in IGNORED_DIRS for part in path.parts):
            continue
        if path.suffix.lower() in TEXT_EXTENSIONS or path.name in {"Dockerfile", "Makefile"}:
            yield path


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
                findings.append(
                    Finding(
                        kind=kind,
                        severity=severity,
                        path=path.relative_to(root).as_posix(),
                        line=line_number,
                        excerpt=stripped[:240],
                    )
                )
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect potential false-completion signals from a repository.")
    parser.add_argument("root", nargs="?", default=".", type=Path)
    parser.add_argument("-o", "--output", type=Path)
    args = parser.parse_args()

    root = args.root.resolve()
    findings: list[Finding] = []
    for path in iter_files(root):
        findings.extend(scan_file(root, path))

    payload = {
        "root": str(root),
        "count": len(findings),
        "findings": [asdict(item) for item in findings],
        "note": "These are evidence candidates, not automatic defects. Review them in context before scoring.",
    }

    rendered = json.dumps(payload, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
        print(f"Wrote {len(findings)} findings to {args.output}")
    else:
        print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
