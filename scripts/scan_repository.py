#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Iterable

IGNORED_DIRS = {
    ".git", ".hg", ".svn", "node_modules", ".venv", "venv", "env", "dist", "build",
    "coverage", "htmlcov", ".next", ".cache", ".pytest_cache", ".mypy_cache", ".ruff_cache"
}

MANIFEST_NAMES = {
    "pyproject.toml", "requirements.txt", "package.json", "package-lock.json", "pnpm-lock.yaml",
    "yarn.lock", "Cargo.toml", "go.mod", "pom.xml", "build.gradle", "build.gradle.kts",
    "Dockerfile", "docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml"
}

TEST_MARKERS = ("test_", "_test.", ".spec.", ".test.")


def iter_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in IGNORED_DIRS for part in path.parts):
            continue
        yield path


def classify(path: Path) -> str:
    name = path.name.lower()
    parts = {part.lower() for part in path.parts}
    if path.name in MANIFEST_NAMES:
        return "manifest"
    if ".github" in parts and "workflows" in parts:
        return "ci"
    if any(marker in name for marker in TEST_MARKERS) or "tests" in parts or "test" in parts:
        return "test"
    if name.startswith("readme") or path.suffix.lower() in {".md", ".rst"}:
        return "documentation"
    if path.suffix.lower() in {".ipynb"}:
        return "notebook"
    if path.suffix.lower() in {".yaml", ".yml", ".toml", ".ini", ".cfg", ".json"}:
        return "configuration"
    if path.suffix.lower() in {
        ".py", ".js", ".jsx", ".ts", ".tsx", ".java", ".kt", ".go", ".rs", ".c", ".cpp",
        ".cc", ".h", ".hpp", ".cs", ".php", ".rb", ".swift", ".scala", ".vue", ".svelte"
    }:
        return "source"
    return "other"


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect a deterministic repository inventory for auditing.")
    parser.add_argument("root", nargs="?", default=".", type=Path)
    parser.add_argument("-o", "--output", type=Path)
    args = parser.parse_args()

    root = args.root.resolve()
    files = list(iter_files(root))
    by_extension = Counter(path.suffix.lower() or "<none>" for path in files)
    by_kind = Counter(classify(path.relative_to(root)) for path in files)

    top_level = sorted(
        path.name for path in root.iterdir()
        if path.name not in IGNORED_DIRS
    )

    payload = {
        "root": str(root),
        "file_count": len(files),
        "top_level": top_level,
        "by_kind": dict(sorted(by_kind.items())),
        "by_extension": dict(sorted(by_extension.items(), key=lambda item: (-item[1], item[0]))),
        "manifests": sorted(path.relative_to(root).as_posix() for path in files if path.name in MANIFEST_NAMES),
        "tests": sorted(path.relative_to(root).as_posix() for path in files if classify(path.relative_to(root)) == "test"),
        "documentation": sorted(path.relative_to(root).as_posix() for path in files if classify(path.relative_to(root)) == "documentation"),
        "ci": sorted(path.relative_to(root).as_posix() for path in files if classify(path.relative_to(root)) == "ci"),
    }

    rendered = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
        print(f"Wrote repository inventory to {args.output}")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
