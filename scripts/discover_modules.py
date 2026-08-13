#!/usr/bin/env python3
from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path
from typing import Any

from audit_utils import iter_files, relative_posix, resolve_root, write_json

SOURCE_EXTENSIONS = {
    ".c", ".cc", ".cpp", ".cxx", ".cs", ".dart", ".go", ".java", ".js", ".jsx",
    ".kt", ".kts", ".php", ".py", ".rb", ".rs", ".scala", ".swift", ".ts", ".tsx",
    ".vue", ".svelte",
}

ROLE_HINTS: dict[str, tuple[str, ...]] = {
    "frontend": ("frontend", "web", "ui", "client", "app", "dashboard"),
    "backend": ("backend", "server", "api", "service", "services"),
    "ml": ("ml", "model", "models", "training", "train", "inference", "ai"),
    "data": ("data", "dataset", "datasets", "etl", "pipeline", "pipelines"),
    "database": ("db", "database", "migrations", "schema"),
    "infra": ("infra", "infrastructure", "deploy", "deployment", "terraform", "helm", "k8s"),
    "firmware": ("firmware", "embedded", "mcu"),
    "hardware": ("hardware", "pcb", "schematic", "electronics"),
    "tests": ("test", "tests", "qa", "e2e"),
    "docs": ("docs", "documentation"),
    "tools": ("scripts", "tools", "tooling", "cli"),
}

MANIFEST_NAMES = {
    "pyproject.toml", "requirements.txt", "package.json", "Cargo.toml", "go.mod", "pom.xml",
    "build.gradle", "build.gradle.kts", "composer.json",
}


def infer_role(name: str) -> str:
    lowered = name.lower()
    for role, hints in ROLE_HINTS.items():
        if lowered in hints or any(lowered.startswith(f"{hint}-") for hint in hints):
            return role
    return "module"


def is_probably_source_dir(path: Path) -> bool:
    if path.name.startswith("."):
        return False
    lowered = path.name.lower()
    return lowered not in {"assets", "static", "public", "images", "fixtures", "samples"}


def directory_stats(root: Path, directory: Path) -> dict[str, Any]:
    files = list(iter_files(directory, max_bytes=None))
    extensions = Counter(path.suffix.lower() or "<none>" for path in files)
    source_files = [path for path in files if path.suffix.lower() in SOURCE_EXTENSIONS]
    manifests = [path for path in files if path.name in MANIFEST_NAMES]
    test_files = [
        path for path in files
        if "test" in path.name.lower()
        or any(part.lower() in {"test", "tests", "e2e"} for part in path.parts)
    ]
    return {
        "path": relative_posix(directory, root),
        "file_count": len(files),
        "source_file_count": len(source_files),
        "test_file_count": len(test_files),
        "manifest_count": len(manifests),
        "top_extensions": [
            {"extension": extension, "count": count}
            for extension, count in extensions.most_common(8)
        ],
    }


def discover(root: Path | str) -> dict[str, Any]:
    root_path = resolve_root(root)
    top_dirs = [
        path for path in sorted(root_path.iterdir(), key=lambda item: item.name.lower())
        if path.is_dir() and is_probably_source_dir(path)
    ]
    candidates: list[dict[str, Any]] = []
    for directory in top_dirs:
        stats = directory_stats(root_path, directory)
        if stats["file_count"] == 0:
            continue
        role = infer_role(directory.name)
        significance = min(stats["source_file_count"], 20) * 2
        significance += min(stats["manifest_count"], 3) * 8
        significance += min(stats["test_file_count"], 10)
        if role not in {"module", "docs", "tests"}:
            significance += 10
        candidates.append({
            "id": directory.name.lower().replace(" ", "-").replace("_", "-"),
            "name": directory.name,
            "role_hint": role,
            "path": stats["path"],
            "significance_score": min(significance, 100),
            "stats": stats,
            "evidence": [{
                "kind": "directory", "path": stats["path"],
                "reason": "Top-level repository area with non-empty content",
            }],
        })

    root_files = [path for path in root_path.iterdir() if path.is_file()]
    root_manifests = [path.name for path in root_files if path.name in MANIFEST_NAMES]
    language_counter: Counter[str] = Counter()
    for path in iter_files(root_path, extensions=SOURCE_EXTENSIONS, max_bytes=None):
        language_counter[path.suffix.lower() or "<none>"] += 1

    return {
        "collector": "discover_modules",
        "root": str(root_path),
        "root_manifests": sorted(root_manifests),
        "language_signals": [
            {"extension": extension, "files": count}
            for extension, count in language_counter.most_common()
        ],
        "module_candidates": sorted(
            candidates, key=lambda item: (-item["significance_score"], item["path"])
        ),
        "notes": [
            "These are module candidates, not authoritative architectural boundaries.",
            "Codex must merge, split, or rename candidates after reading responsibilities and dependencies.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Discover evidence-backed module candidates.")
    parser.add_argument("root", nargs="?", default=".", type=Path)
    parser.add_argument("-o", "--output", type=Path)
    args = parser.parse_args()
    result = discover(args.root)
    if args.output:
        write_json(args.output, result)
        print(f"Wrote module discovery to {args.output}")
    else:
        import json
        print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
