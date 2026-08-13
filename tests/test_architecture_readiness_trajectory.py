from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

import bootstrap_audit
import build_dashboard
import compare_snapshots
import forecast_trajectory
import infer_architecture
import score_readiness


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_architecture_inference_detects_internal_edges_and_cycle(tmp_path: Path) -> None:
    write(tmp_path / "api" / "__init__.py", "")
    write(tmp_path / "api" / "routes.py", "from core.service import run\n")
    write(tmp_path / "core" / "__init__.py", "")
    write(
        tmp_path / "core" / "service.py",
        "from data.repo import load\n\ndef run():\n    return load()\n",
    )
    write(tmp_path / "data" / "__init__.py", "")
    write(
        tmp_path / "data" / "repo.py",
        "from core.service import run\n\ndef load():\n    return 1\n",
    )
    write(tmp_path / "tests" / "test_service.py", "from core.service import run\n")

    result = infer_architecture.infer(tmp_path)
    pairs = {(edge["from"], edge["to"]) for edge in result["edges"]}

    assert ("api", "core") in pairs
    assert ("core", "data") in pairs
    assert ("data", "core") in pairs
    assert ["core", "data"] in result["cycles"]
    assert all(node["id"] != "tests" for node in result["nodes"])


def test_architecture_inference_expands_src_container(tmp_path: Path) -> None:
    write(tmp_path / "src" / "api" / "routes.py", "from core.service import run\n")
    write(tmp_path / "src" / "core" / "service.py", "def run():\n    return 1\n")

    result = infer_architecture.infer(tmp_path)
    node_ids = {node["id"] for node in result["nodes"]}

    assert "src-api" in node_ids
    assert "src-core" in node_ids


def test_readiness_gate_reports_bounds_and_coverage_without_inventing_score() -> None:
    gate = {
        "threshold": 75,
        "minimum_coverage": 0.75,
        "criteria": [
            {
                "id": "workflow",
                "status": "pass",
                "weight": 3,
                "confidence": 0.9,
                "critical": True,
            },
            {"id": "validation", "status": "partial", "weight": 2, "confidence": 0.8},
            {"id": "deployment", "status": "unknown", "weight": 5, "critical": True},
        ],
    }
    evaluation = score_readiness.evaluate_gate(gate)

    assert evaluation["coverage"] == 50.0
    assert evaluation["score"] is None
    assert evaluation["lower_bound"] == 40.0
    assert evaluation["upper_bound"] == 90.0
    assert evaluation["state"] == "insufficient_evidence"
    assert evaluation["critical_unknowns"] == ["deployment"]


def test_readiness_gate_critical_failure_blocks_gate() -> None:
    gate = {
        "threshold": 70,
        "minimum_coverage": 0.5,
        "criteria": [
            {"id": "core", "status": "pass", "weight": 4, "critical": True},
            {"id": "security", "status": "fail", "weight": 2, "critical": True},
        ],
    }
    evaluation = score_readiness.evaluate_gate(gate)

    assert evaluation["score"] == 66.67
    assert evaluation["blocked"] is True
    assert evaluation["state"] == "blocked"
    assert evaluation["critical_failures"] == ["security"]


def make_snapshot(day: int, completion: float, module_completion: float) -> dict:
    timestamp = datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(days=day)
    return {
        "metadata": {"generated_at": timestamp.isoformat()},
        "scores": {"estimated_completion": completion},
        "modules": [
            {"id": "core", "completion": module_completion, "quality": module_completion - 5}
        ],
    }


def test_trajectory_forecast_requires_three_points_for_eta() -> None:
    snapshots = [
        make_snapshot(0, 50, 45),
        make_snapshot(30, 60, 55),
        make_snapshot(60, 70, 65),
    ]
    result = forecast_trajectory.analyze(snapshots, target=80)
    trend = result["score_trends"]["estimated_completion"]

    assert trend["direction"] == "improving"
    assert 9.0 <= trend["delta_per_30d"] <= 11.0
    assert trend["r2"] == 1.0
    assert trend["eta_days"] is not None
    assert "core" in result["module_trends"]


def test_trajectory_does_not_emit_eta_for_two_points() -> None:
    result = forecast_trajectory.analyze(
        [make_snapshot(0, 40, 40), make_snapshot(30, 60, 60)],
        target=80,
    )
    trend = result["score_trends"]["estimated_completion"]
    assert trend["eta_days"] is None
    assert trend["eta_timestamp"] is None


def test_bootstrap_uses_architecture_edges_as_evidence() -> None:
    discovery = {
        "metadata": {"root": "/tmp/demo"},
        "collectors": {
            "modules": {
                "status": "ok",
                "result": {
                    "module_candidates": [
                        {"id": "api", "name": "api", "path": "api", "role_hint": "backend"},
                        {"id": "core", "name": "core", "path": "core", "role_hint": "module"},
                    ]
                },
            },
            "architecture": {
                "status": "ok",
                "result": {
                    "nodes": [
                        {
                            "id": "api",
                            "name": "api",
                            "path": "api",
                            "dependencies": ["core"],
                            "consumers": [],
                        },
                        {
                            "id": "core",
                            "name": "core",
                            "path": "core",
                            "dependencies": [],
                            "consumers": ["api"],
                        },
                    ],
                    "edges": [
                        {
                            "from": "api",
                            "to": "core",
                            "kind": "static_import",
                            "confidence": 0.95,
                            "occurrences": 2,
                            "evidence": [
                                {
                                    "path": "api/routes.py",
                                    "line": 3,
                                    "declaration": "core.service",
                                }
                            ],
                        }
                    ],
                    "cycles": [],
                    "hotspots": [{"module_id": "core", "centrality": 1.0}],
                    "limitations": ["static only"],
                },
            },
        },
    }
    audit = bootstrap_audit.bootstrap(discovery, project_name="Demo")

    assert audit["modules"][0]["completion"] is None
    assert audit["dependency_edges"][0]["from"] == "api"
    assert audit["dependency_edges"][0]["evidence_ids"] == ["ev-arch-0001"]
    assert audit["evidence"][0]["level"] == "E2"
    assert audit["architecture_analysis"]["hotspots"][0]["module_id"] == "core"


def test_snapshot_comparison_tracks_debt_bottlenecks_and_methodology_change() -> None:
    old = {
        "metadata": {"auditor_version": "0.2.0"},
        "scores": {"estimated_completion": 70},
        "modules": [
            {
                "id": "core",
                "completion": 70,
                "quality": 80,
                "classification": "critical_path",
            }
        ],
        "risks": [{"id": "r1"}],
        "technical_debt": [{"id": "d1"}],
        "bottlenecks": [{"id": "b1"}],
        "readiness_gates": {
            "mvp": {
                "evaluation": {
                    "score": 65,
                    "coverage": 80,
                    "confidence": 75,
                    "state": "nearly_ready",
                }
            }
        },
    }
    new = {
        "metadata": {"auditor_version": "0.3.0"},
        "scores": {"estimated_completion": 75},
        "modules": [
            {
                "id": "core",
                "completion": 75,
                "quality": 78,
                "classification": "critical_path",
            }
        ],
        "risks": [{"id": "r2"}],
        "technical_debt": [{"id": "d2"}],
        "bottlenecks": [],
        "readiness_gates": {
            "mvp": {
                "evaluation": {
                    "score": 74,
                    "coverage": 100,
                    "confidence": 90,
                    "state": "ready",
                }
            }
        },
    }
    result = compare_snapshots.compare(old, new)

    assert result["score_deltas"]["estimated_completion"] == 5.0
    assert result["closed_risks"] == ["r1"]
    assert result["new_risks"] == ["r2"]
    assert result["resolved_technical_debt"] == ["d1"]
    assert result["new_technical_debt"] == ["d2"]
    assert result["resolved_bottlenecks"] == ["b1"]
    assert result["readiness_gate_changes"]["mvp"]["state_changed"] is True
    assert result["methodology"]["changed"] is True


def test_dashboard_exposes_readiness_and_trajectory_views() -> None:
    audit = {
        "metadata": {
            "generated_at": "2026-01-01T00:00:00+00:00",
            "auditor_version": "0.3.0",
        },
        "project": {"name": "Demo"},
        "scores": {"mvp_readiness": 72, "confidence": 80},
        "modules": [],
        "risks": [],
        "recommendations": [],
        "evidence": [],
        "directions": [],
        "readiness_gates": {
            "mvp": {
                "evaluation": {
                    "score": 72,
                    "coverage": 90,
                    "confidence": 80,
                    "assessed_score": 72,
                    "lower_bound": 65,
                    "upper_bound": 82,
                    "state": "nearly_ready",
                    "critical_failures": [],
                    "critical_unknowns": [],
                }
            }
        },
        "history": {
            "trajectory": {
                "score_trends": {
                    "mvp_readiness": {
                        "latest_value": 72,
                        "latest_delta": 5,
                        "delta_per_30d": 4.5,
                        "r2": 0.8,
                        "target": 80,
                        "eta_days": 50,
                        "series": [
                            {"timestamp": "2026-01-01T00:00:00+00:00", "value": 60},
                            {"timestamp": "2026-02-01T00:00:00+00:00", "value": 72},
                        ],
                    }
                }
            }
        },
    }
    html = build_dashboard.render(audit)
    assert "Readiness gates" in html
    assert "Project trajectory" in html
    assert "Critical evidence missing" in html
    assert "mvp_readiness" in html
