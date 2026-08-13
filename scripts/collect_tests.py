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

TEST_SUFFIXES = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".java", ".kt", ".go", ".rs", ".rb", ".php", ".cs",
}

FRAMEWORK_PATTERNS: dict[str, re.Pattern[str]] = {
    "pytest": re.compile(r"\bpytest\b|def\s+test_"),
    "unittest": re.compile(r"\bunittest\b|TestCase"),
    "jest/vitest": re.compile(r"\b(?:jest|vitest|describe|expect)\b"),
    "mocha": re.compile(r"\b(?:mocha|chai)\b"),
    "playwright": re.compile(r"\bplaywright\b|@playwright/test"),
    "cypress": re.compile(r"\bcypress\b|cy\."),
    "junit": re.compile(r"\b(?:org\.junit|@Test)\b"),
    "go-test": re.compile(r"\bfunc\s+Test[A-Z]\w*\s*\("),
    "rust-test": re.compile(r"#\[(?:tokio::)?test\]"),
}

ASSERTION_PATTERN = re.compile(
    r"\bassert\b|assert[A-Z]\w*\s*\(|\bexpect\s*\(|\bshould\b|"
    r"\brequire\.\w+\s*\(|\bassert\.\w+\s*\("
)


def looks_like_test(path: Path, root: Path) -> bool:
    if path.suffix.lower() not in TEST_SUFFIXES:
        return False
    relative_parts = [part.lower() for part in path.relative_to(root).parts]
    name = path.name.lower()
    return (
        any(part in {"test", "tests", "testing", "__tests__", "e2e", "spec", "specs"} for part in relative_parts)
        or name.startswith("test_") or name.endswith("_test.py") or ".test." in name
        or ".spec." in name or name.endswith("_test.go") or name.endswith("test.java")
    )


def python_test_stats(text: str) -> dict[str, int | bool]:
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return {"test_cases": 0, "assertions": 0, "syntax_error": True}
    test_cases = 0
    assertions = 0
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test"):
            test_cases += 1
        if isinstance(node, ast.Assert):
            assertions += 1
        if isinstance(node, ast.Call):
            func = node.func
            name = ""
            if isinstance(func, ast.Name):
                name = func.id
            elif isinstance(func, ast.Attribute):
                name = func.attr
            if name.startswith("assert"):
                assertions += 1
    return {"test_cases": test_cases, "assertions": assertions, "syntax_error": False}


def generic_test_stats(text: str) -> dict[str, int | bool]:
    cases = len(re.findall(r"\b(?:test|it)\s*\(", text)) + len(re.findall(r"@Test\b", text))
    assertions = len(ASSERTION_PATTERN.findall(text))
    return {"test_cases": cases, "assertions": assertions, "syntax_error": False}


def collect(root: Path | str) -> dict[str, Any]:
    root_path = resolve_root(root)
    frameworks: Counter[str] = Counter()
    test_files: list[dict[str, Any]] = []
    suspicious: list[dict[str, str]] = []
    for path in iter_text_files(root_path):
        if not looks_like_test(path, root_path):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for framework, pattern in FRAMEWORK_PATTERNS.items():
            if pattern.search(text):
                frameworks[framework] += 1
        stats = python_test_stats(text) if path.suffix.lower() == ".py" else generic_test_stats(text)
        line_count = text.count("\n") + 1 if text else 0
        relative = relative_posix(path, root_path)
        entry = {"path": relative, "language_extension": path.suffix.lower(), "lines": line_count, **stats}
        test_files.append(entry)
        if line_count <= 5:
            suspicious.append({
                "path": relative, "signal": "very_small_test_file",
                "reason": "Test file has five or fewer lines.",
            })
        if int(stats["test_cases"]) > 0 and int(stats["assertions"]) == 0:
            suspicious.append({
                "path": relative, "signal": "tests_without_detected_assertions",
                "reason": "Detected test cases but no assertion-like constructs.",
            })
    return {
        "collector": "collect_tests",
        "root": str(root_path),
        "summary": {
            "test_file_count": len(test_files),
            "detected_test_cases": sum(int(item["test_cases"]) for item in test_files),
            "detected_assertions": sum(int(item["assertions"]) for item in test_files),
            "frameworks": [{"name": name, "files": count} for name, count in frameworks.most_common()],
        },
        "test_files": sorted(test_files, key=lambda item: item["path"]),
        "suspicious_signals": suspicious,
        "limitations": [
            "Assertion detection is heuristic and cannot prove semantic test quality.",
            "Generated tests, parameterized cases, and framework-specific assertions may be undercounted.",
            "Coverage is unknown unless a real coverage tool is executed.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Inventory tests and weak-test signals.")
    parser.add_argument("root", nargs="?", default=".", type=Path)
    parser.add_argument("-o", "--output", type=Path)
    args = parser.parse_args()
    result = collect(args.root)
    if args.output:
        write_json(args.output, result)
        print(f"Wrote test inventory to {args.output}")
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
