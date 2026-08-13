from __future__ import annotations

import build_dashboard
import plan_actions


def sample_audit() -> dict:
    return {
        "metadata": {"generated_at": "2026-08-13T00:00:00+00:00", "auditor_version": "0.2.0"},
        "project": {"name": "Demo", "mission": "Ship useful software"},
        "scores": {"estimated_completion": 65, "confidence": 80},
        "modules": [
            {
                "id": "core",
                "name": "Core",
                "classification": "critical_path",
                "completion": 70,
                "quality": 60,
                "confidence": 90,
                "dependencies": [],
                "evidence_ids": ["ev-1"],
            }
        ],
        "evidence": [{"id": "ev-1", "level": "E3", "claim": "Core test passes"}],
        "risks": [],
        "directions": [],
        "recommendations": [
            {
                "id": "a",
                "title": "Validate core flow",
                "impact": 90,
                "risk_reduction": 80,
                "effort": "small",
                "critical_path": True,
                "confidence": 90,
                "unlocks": ["MVP", "production"],
            },
            {
                "id": "b",
                "title": "Polish optional animation",
                "impact": 20,
                "risk_reduction": 0,
                "effort": "large",
                "confidence": 80,
            },
        ],
    }


def test_action_planner_prefers_high_leverage_work() -> None:
    result = plan_actions.apply(sample_audit())
    assert result["recommendations"][0]["id"] == "a"
    assert result["action_plan"]["highest_leverage_action"] == "a"
    assert result["recommendations"][0]["leverage_score"] > result["recommendations"][1]["leverage_score"]


def test_dashboard_embeds_audit_and_has_core_views() -> None:
    document = build_dashboard.render(sample_audit())
    assert "Project Intelligence Command Center" in document
    assert "What should I do now?" in document
    assert "Evidence explorer" in document
    assert '"name": "Demo"' in document
    assert "__AUDIT_DATA__" not in document
