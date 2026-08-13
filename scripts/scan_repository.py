#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

from audit_utils import iter_files, relative_posix, resolve_root, write_json

MANIFEST_NAMES = {
    "pyproject.toml", "requirements.txt", "package.json", "package-lock.json", "pnpm-lock.yaml",
    "yarn.lock", "Cargo.toml", "Cargo.lock", "go.mod", "go.sum", "pom.xml", "build.gradle",
    "build.gradle.kts", "Dockerfile", "docker-compose.yml", "docker-compose.yaml", "compose.yml",
    "compose.yaml", "Makefile", "CMakeLists.txt",
}

SOURCE_EXTENSIONS = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".java", ".kt", ".go", ".rs", ".c", ".cpp",
    ".cc", ".h", ".hpp", ".cs", ".php", ".rb", ".swift", ".scala", ".vue", ".svelte",
}
TEST_MARKERS = ("test_", "_test.", ".spec.", ".test.")


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
    if path.suffix.lower() == ".ipynb":
        return "notebook"
    if path.suffix.lower() in {".yaml", ".yml", ".toml", ".ini", ".cfg", ".json"}:
        return "configuration"
    if path.suffix.lower() in SOURCE_EXTENSIONS:
        return "source"
    return "other"


def scan(root: Path | str) -> dict[str, Any]:
    root_path = resolve_root(root)
    files = list(iter_files(root_path, max_bytes=None))
    by_extension = Counter(path.suffix.lower() or "<none>" for path in files)
    by_kind = Counter(classify(path.relative_to(root_path)) for path in files)
    top_level = sorted(
        path.name for path in root_path.iterdir() if path.name not in {".git", ".project-audit"}
    )
    return {
        "collector": "scan_repository",
        "root": str(root_path), "file_count": len(files), "top_level": top_level,
        "by_kind": dict(sorted(by_kind.items())),
        "by_extension": dict(sorted(by_extension.items(), key=lambda item: (-item[1], item[0]))),
        "manifests": sorted(relative_posix(path, root_path) for path in files if path.name in MANIFEST_NAMES),
        "tests": sorted(
            relative_posix(path, root_path) for path in files
            if classify(path.relative_to(root_path)) == "test"
        ),
        "documentation": sorted(
            relative_posix(path, root_path) for path in files
            if classify(path.relative_to(root_path)) == "documentation"
        ),
        "ci": sorted(
            relative_posix(path, root_path) for path in files
            if classify(path.relative_to(root_path)) == "ci"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect a deterministic repository inventory for auditing.")
    parser.add_argument("root", nargs="?", default=".", type=Path)
    parser.add_argument("-o", "--output", type=Path)
    args = parser.parse_args()
    payload = scan(args.root)
    if args.output:
        write_json(args.output, payload)
        print(f"Wrote repository inventory to {args.output}")
    else:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
