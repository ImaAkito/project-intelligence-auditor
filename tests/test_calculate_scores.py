from __future__ import annotations

import importlib.util
from pathlib import Path


def load_module():
    path = Path(__file__).resolve().parents[1] / "scripts" / "calculate_scores.py"
    spec = importlib.util.spec_from_file_location("calculate_scores", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_module_completion_uses_declared_weights() -> None:
    scoring = load_module()
    module = {
        "implementation": 100,
        "integration": 80,
        "validation": 60,
        "documentation": 40,
        "operational_readiness": 20,
    }
    assert scoring.module_completion(module) == 72.0


def test_confirmed_completion_is_evidence_constrained() -> None:
    scoring = load_module()
    module = {
        "implementation": 100,
        "integration": 100,
        "validation": 100,
        "documentation": 100,
        "operational_readiness": 100,
        "evidence_level": "E2",
    }
    assert scoring.module_confirmed_completion(module) == 45.0


def test_unknown_dimensions_are_renormalized_not_zeroed() -> None:
    scoring = load_module()
    module = {
        "implementation": 100,
        "integration": None,
        "validation": None,
        "documentation": None,
        "operational_readiness": None,
    }
    assert scoring.module_completion(module) == 100.0


def test_project_weight_prefers_critical_modules() -> None:
    scoring = load_module()
    critical = {
        "classification": "critical_path",
        "dependency_factor": 0.5,
        "user_value_factor": 0.5,
    }
    optional = {
        "classification": "optional",
        "dependency_factor": 0.5,
        "user_value_factor": 0.5,
    }
    assert scoring.project_weight(critical) > scoring.project_weight(optional)


def test_calculate_populates_project_scores() -> None:
    scoring = load_module()
    payload = {
        "modules": [
            {
                "id": "core",
                "classification": "critical_path",
                "implementation": 80,
                "integration": 80,
                "validation": 80,
                "documentation": 80,
                "operational_readiness": 80,
                "quality": 70,
                "confidence": 90,
                "evidence_level": "E3",
            }
        ],
        "scores": {},
    }
    result = scoring.calculate(payload)
    assert result["scores"]["estimated_completion"] == 80.0
    assert result["scores"]["confirmed_completion"] == 68.0
    assert result["scores"]["project_health"] == 70.0
    assert result["scores"]["confidence"] == 90.0
