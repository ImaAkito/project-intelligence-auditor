from __future__ import annotations

import json
from pathlib import Path

import collect_dependencies
import collect_tests
import detect_technical_debt
import discover_modules
import scan_repository


def test_repository_and_module_discovery(tmp_path: Path) -> None:
    (tmp_path / "backend").mkdir()
    (tmp_path / "backend" / "api.py").write_text("def health():\n    return {'ok': True}\n")
    (tmp_path / "frontend").mkdir()
    (tmp_path / "frontend" / "app.tsx").write_text("export const App = () => null;\n")
    (tmp_path / "README.md").write_text("# Demo\n")

    inventory = scan_repository.scan(tmp_path)
    modules = discover_modules.discover(tmp_path)

    assert inventory["file_count"] == 3
    ids = {item["id"] for item in modules["module_candidates"]}
    assert {"backend", "frontend"} <= ids


def test_dependency_collection_handles_python_and_node(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname="demo"\nversion="0.1.0"\ndependencies=["httpx>=0.27"]\n'
    )
    (tmp_path / "package.json").write_text(
        json.dumps({"dependencies": {"react": "^19.0.0"}, "devDependencies": {"vitest": "^3.0.0"}})
    )

    result = collect_dependencies.collect(tmp_path)
    names = {item["name"] for item in result["dependencies"]}

    assert "httpx" in names
    assert "react" in names
    assert "vitest" in names


def test_test_collector_flags_test_without_assertions(tmp_path: Path) -> None:
    tests = tmp_path / "tests"
    tests.mkdir()
    (tests / "test_demo.py").write_text("def test_demo():\n    value = 1 + 1\n")

    result = collect_tests.collect(tmp_path)

    assert result["summary"]["test_file_count"] == 1
    assert any(
        item["signal"] == "tests_without_detected_assertions"
        for item in result["suspicious_signals"]
    )


def test_technical_debt_collector_finds_markers(tmp_path: Path) -> None:
    (tmp_path / "app.py").write_text("# TODO: replace temporary implementation\nx = 1\n")

    result = detect_technical_debt.collect(tmp_path)

    assert result["summary"]["marker_counts"]["TODO"] == 1
