from __future__ import annotations

from pathlib import Path

import bootstrap_audit
import run_collectors


def test_collector_suite_and_bootstrap(tmp_path: Path) -> None:
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "app.py").write_text("def main():\n    return 1\n")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_app.py").write_text("def test_main():\n    assert 1 == 1\n")

    discovery = run_collectors.run(tmp_path)

    assert discovery["failed_collectors"] == []
    assert discovery["collectors"]["repository"]["status"] == "ok"
    assert discovery["collectors"]["modules"]["status"] == "ok"

    audit = bootstrap_audit.bootstrap(discovery, project_name="Demo")
    assert audit["project"]["name"] == "Demo"
    assert audit["scores"]["estimated_completion"] is None
    assert len(audit["modules"]) >= 1
