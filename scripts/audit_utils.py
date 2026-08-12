#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Iterable, Iterator

DEFAULT_IGNORED_DIRS = {
    ".git", ".hg", ".svn", ".idea", ".vscode", ".mypy_cache", ".pytest_cache",
    ".ruff_cache", ".tox", ".nox", "__pycache__", "node_modules", "vendor", "dist",
    "build", "target", "coverage", ".coverage", ".venv", "venv", "env", ".project-audit",
}

TEXT_EXTENSIONS = {
    ".c", ".cc", ".cpp", ".cxx", ".h", ".hpp", ".cs", ".css", ".dart", ".go",
    ".gradle", ".graphql", ".hbs", ".html", ".ini", ".java", ".js", ".json", ".jsx",
    ".kt", ".kts", ".md", ".mjs", ".php", ".properties", ".proto", ".py", ".rb",
    ".rs", ".rst", ".scala", ".scss", ".sh", ".sql", ".svelte", ".swift", ".toml",
    ".ts", ".tsx", ".vue", ".xml", ".yaml", ".yml",
}


def resolve_root(root: Path | str) -> Path:
    path = Path(root).expanduser().resolve()
    if not path.exists():
        raise FileNotFoundError(f"Repository root does not exist: {path}")
    if not path.is_dir():
        raise NotADirectoryError(f"Repository root is not a directory: {path}")
    return path


def relative_posix(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def should_ignore(path: Path, root: Path, ignored_dirs: set[str] | None = None) -> bool:
    ignored = DEFAULT_IGNORED_DIRS if ignored_dirs is None else ignored_dirs
    try:
        relative = path.resolve().relative_to(root.resolve())
    except ValueError:
        return True
    return any(part in ignored for part in relative.parts)


def iter_files(
    root: Path | str,
    *,
    extensions: set[str] | None = None,
    max_bytes: int | None = 2_000_000,
    ignored_dirs: set[str] | None = None,
) -> Iterator[Path]:
    root_path = resolve_root(root)
    ignored = DEFAULT_IGNORED_DIRS if ignored_dirs is None else ignored_dirs
    for current, dirs, files in os.walk(root_path):
        current_path = Path(current)
        dirs[:] = [
            name for name in dirs
            if name not in ignored and not should_ignore(current_path / name, root_path, ignored)
        ]
        for filename in files:
            path = current_path / filename
            if should_ignore(path, root_path, ignored):
                continue
            if extensions is not None and path.suffix.lower() not in extensions:
                continue
            if max_bytes is not None:
                try:
                    if path.stat().st_size > max_bytes:
                        continue
                except OSError:
                    continue
            yield path


def iter_text_files(
    root: Path | str,
    *,
    max_bytes: int = 2_000_000,
    ignored_dirs: set[str] | None = None,
) -> Iterator[Path]:
    yield from iter_files(
        root, extensions=TEXT_EXTENSIONS, max_bytes=max_bytes, ignored_dirs=ignored_dirs
    )


def read_text(path: Path, *, max_chars: int | None = None) -> str:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = path.read_text(encoding="utf-8", errors="replace")
    return text[:max_chars] if max_chars is not None else text


def write_json(path: Path | str, data: Any) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2, sort_keys=False)
        handle.write("\n")
    return output


def load_json(path: Path | str) -> Any:
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def bounded(value: float, lower: float = 0.0, upper: float = 100.0) -> float:
    return max(lower, min(upper, value))


def normalize_effort(value: str | int | float | None) -> float:
    if value is None:
        return 3.0
    if isinstance(value, (int, float)):
        return max(1.0, min(5.0, float(value)))
    lookup = {
        "xs": 1.0, "tiny": 1.0, "trivial": 1.0, "s": 1.5, "small": 1.5, "low": 1.5,
        "m": 2.5, "medium": 2.5, "moderate": 2.5, "l": 3.5, "large": 3.5, "high": 3.5,
        "xl": 4.5, "very_large": 4.5, "very large": 4.5, "huge": 5.0,
    }
    return lookup.get(str(value).strip().lower(), 3.0)


def unique_preserve_order(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result
