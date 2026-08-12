#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import tomllib
from pathlib import Path
from typing import Any

from audit_utils import relative_posix, resolve_root, unique_preserve_order, write_json


def parse_requirement_name(requirement: str) -> str:
    value = requirement.strip()
    if not value or value.startswith(("#", "-r ", "--", "git+", "http://", "https://")):
        return ""
    value = re.split(r"[<>=!~;\[\s]", value, maxsplit=1)[0].strip()
    return value.lower().replace("_", "-")


def parse_requirements(path: Path) -> list[dict[str, str]]:
    result: list[dict[str, str]] = []
    for raw_line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw_line.strip()
        name = parse_requirement_name(line)
        if name:
            result.append({"name": name, "declaration": line, "scope": "runtime"})
    return result


def parse_pyproject(path: Path) -> list[dict[str, str]]:
    with path.open("rb") as handle:
        data = tomllib.load(handle)
    result: list[dict[str, str]] = []
    project = data.get("project", {})
    for declaration in project.get("dependencies", []) or []:
        name = parse_requirement_name(str(declaration))
        if name:
            result.append({"name": name, "declaration": str(declaration), "scope": "runtime"})
    optional = project.get("optional-dependencies", {}) or {}
    for group, dependencies in optional.items():
        for declaration in dependencies or []:
            name = parse_requirement_name(str(declaration))
            if name:
                result.append({
                    "name": name, "declaration": str(declaration), "scope": f"optional:{group}",
                })
    poetry = data.get("tool", {}).get("poetry", {})
    for name, declaration in (poetry.get("dependencies", {}) or {}).items():
        if name.lower() != "python":
            result.append({
                "name": name.lower().replace("_", "-"),
                "declaration": str(declaration), "scope": "runtime",
            })
    for group, group_data in (poetry.get("group", {}) or {}).items():
        for name, declaration in (group_data.get("dependencies", {}) or {}).items():
            result.append({
                "name": name.lower().replace("_", "-"),
                "declaration": str(declaration), "scope": f"group:{group}",
            })
    return result


def parse_package_json(path: Path) -> list[dict[str, str]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    result: list[dict[str, str]] = []
    scopes = {
        "dependencies": "runtime", "devDependencies": "dev", "peerDependencies": "peer",
        "optionalDependencies": "optional",
    }
    for key, scope in scopes.items():
        for name, version in (data.get(key, {}) or {}).items():
            result.append({"name": name, "declaration": str(version), "scope": scope})
    return result


def parse_cargo(path: Path) -> list[dict[str, str]]:
    with path.open("rb") as handle:
        data = tomllib.load(handle)
    result: list[dict[str, str]] = []
    for key, scope in (("dependencies", "runtime"), ("dev-dependencies", "dev"), ("build-dependencies", "build")):
        for name, declaration in (data.get(key, {}) or {}).items():
            result.append({"name": name, "declaration": str(declaration), "scope": scope})
    return result


def parse_go_mod(path: Path) -> list[dict[str, str]]:
    text = path.read_text(encoding="utf-8", errors="replace")
    result: list[dict[str, str]] = []
    in_block = False
    for raw in text.splitlines():
        line = raw.strip()
        if line == "require (":
            in_block = True
            continue
        if in_block and line == ")":
            in_block = False
            continue
        if line.startswith("require ") and not line.endswith("("):
            line = line[len("require "):].strip()
        elif not in_block:
            continue
        if not line or line.startswith("//"):
            continue
        fields = line.split()
        if fields:
            result.append({
                "name": fields[0],
                "declaration": " ".join(fields[1:]) if len(fields) > 1 else "",
                "scope": "runtime",
            })
    return result


PARSERS = {
    "pyproject.toml": parse_pyproject,
    "requirements.txt": parse_requirements,
    "package.json": parse_package_json,
    "Cargo.toml": parse_cargo,
    "go.mod": parse_go_mod,
}


def collect(root: Path | str) -> dict[str, Any]:
    root_path = resolve_root(root)
    manifests: list[dict[str, Any]] = []
    all_dependencies: list[dict[str, Any]] = []
    for path in sorted(root_path.rglob("*")):
        if not path.is_file() or path.name not in PARSERS:
            continue
        if any(part in {".git", "node_modules", ".venv", "venv", "dist", "build", "target"} for part in path.parts):
            continue
        parser = PARSERS[path.name]
        try:
            dependencies = parser(path)
            error = None
        except (OSError, ValueError, tomllib.TOMLDecodeError, json.JSONDecodeError) as exc:
            dependencies = []
            error = f"{type(exc).__name__}: {exc}"
        manifest_path = relative_posix(path, root_path)
        manifests.append({
            "path": manifest_path, "type": path.name,
            "dependency_count": len(dependencies), "error": error,
        })
        for dependency in dependencies:
            all_dependencies.append({**dependency, "manifest": manifest_path})

    by_name: dict[str, list[dict[str, Any]]] = {}
    for dependency in all_dependencies:
        by_name.setdefault(dependency["name"], []).append(dependency)
    duplicates = []
    for name, declarations in sorted(by_name.items()):
        manifests_for_name = unique_preserve_order(item["manifest"] for item in declarations)
        declarations_for_name = unique_preserve_order(item["declaration"] for item in declarations)
        if len(manifests_for_name) > 1 or len(declarations_for_name) > 1:
            duplicates.append({
                "name": name,
                "manifests": manifests_for_name,
                "declarations": declarations_for_name,
                "potential_version_drift": len(declarations_for_name) > 1,
            })
    return {
        "collector": "collect_dependencies",
        "root": str(root_path),
        "manifests": manifests,
        "dependencies": all_dependencies,
        "unique_dependency_count": len(by_name),
        "duplicate_declarations": duplicates,
        "limitations": [
            "This collector reads declarations only; it does not contact registries or infer current vulnerability status.",
            "Transitive dependency health requires ecosystem-specific lockfile or external audit tooling.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect declared dependencies from common manifests.")
    parser.add_argument("root", nargs="?", default=".", type=Path)
    parser.add_argument("-o", "--output", type=Path)
    args = parser.parse_args()
    result = collect(args.root)
    if args.output:
        write_json(args.output, result)
        print(f"Wrote dependency inventory to {args.output}")
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
