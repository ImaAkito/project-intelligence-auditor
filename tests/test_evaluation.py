from __future__ import annotations

from pathlib import Path

import check_audit_integrity
import evaluate_benchmarks
import evaluate_golden_audit
import validate_challenge_corpus
from audit_utils import load_json

ROOT = Path(__file__).resolve().parents[1]


def test_synthetic_benchmark_suite_meets_declared_contract() -> None:
    result = evaluate_benchmarks.evaluate(ROOT, ROOT / "benchmarks" / "manifest.json")
    assert result["case_count"] == 4
    assert result["failed_checks"] == 0
    assert result["suite_score"] == 100.0


def test_semantic_challenge_corpus_is_structurally_valid() -> None:
    result = validate_challenge_corpus.validate(ROOT, ROOT / "challenges" / "manifest.json")
    assert result["case_count"] == 5
    assert result["check_count"] >= 25
    assert result["issue_count"] == 0
    assert result["valid"] is True


def test_example_audit_has_full_structural_integrity_coverage() -> None:
    audit = load_json(ROOT / "examples" / "example-audit.json")
    result = check_audit_integrity.calculate(audit)
    assert result["integrity_coverage"] == 100.0
    assert result["issue_count"] == 0


def test_integrity_checker_detects_untraceable_scored_module() -> None:
    audit = {
        "modules": [
            {
                "id": "core",
                "completion": 80,
                "quality": 70,
                "evidence_level": "E2",
                "evidence_ids": [],
            }
        ],
        "dependency_edges": [],
        "risks": [],
        "readiness_gates": {},
        "validation_runs": [],
        "recommendations": [],
        "evidence": [],
    }
    result = check_audit_integrity.calculate(audit)
    assert result["integrity_coverage"] == 0.0
    assert result["issue_count"] == 1
    assert result["issues"][0]["group"] == "module_traceability"


def test_golden_evaluator_prefers_ranges_and_categorical_expectations() -> None:
    audit = load_json(ROOT / "examples" / "example-audit.json")
    golden = {
        "id": "synthetic-reviewed-expectations",
        "checks": [
            {"type": "score_range", "key": "estimated_completion", "min": 60, "max": 75},
            {"type": "score_range", "key": "production_readiness", "min": 20, "max": 40},
            {
                "type": "module_classification",
                "module_id": "core",
                "expected": "critical_path",
            },
            {"type": "module_evidence_level", "module_id": "core", "minimum": "E3"},
            {"type": "readiness_state", "gate": "mvp", "expected": "ready"},
            {"type": "readiness_state", "gate": "production", "expected": "blocked"},
            {"type": "recommendation_presence", "id": "rec-integration-tests"},
        ],
    }
    result = evaluate_golden_audit.evaluate(audit, golden)
    assert result["score"] == 100.0
    assert result["failed"] == 0


def test_golden_evaluator_supports_relations_text_and_commercial_state() -> None:
    audit = {
        "scores": {
            "research_readiness": 82,
            "production_readiness": 34,
            "commercial_readiness": 28,
        },
        "readiness_gates": {
            "production": {"evaluation": {"state": "not_ready"}},
        },
        "risks": [
            {"id": "risk-deploy", "title": "Deployment path is not operationally validated"}
        ],
        "recommendations": [
            {"id": "rec-deploy", "title": "Add deployment and recovery validation"}
        ],
        "commercialization": {
            "time_to_revenue": None,
            "primary_blocker": "No customer evidence",
        },
    }
    golden = {
        "id": "semantic-demo",
        "checks": [
            {
                "type": "score_relation",
                "left": "research_readiness",
                "op": ">",
                "right": "production_readiness",
                "margin": 20,
                "critical": True,
            },
            {
                "type": "readiness_state_in",
                "gate": "production",
                "allowed": ["not_ready", "blocked"],
                "critical": True,
            },
            {"type": "item_text_contains", "section": "risks", "text": "deployment"},
            {
                "type": "commercialization_field",
                "key": "time_to_revenue",
                "state": "empty",
            },
        ],
    }
    result = evaluate_golden_audit.evaluate(audit, golden)
    assert result["score"] == 100.0
    assert result["critical_failed"] == 0


def test_golden_evaluator_exposes_critical_semantic_failure() -> None:
    audit = {
        "scores": {"clinical_readiness": 90},
        "readiness_gates": {"clinical": {"evaluation": {"state": "ready"}}},
        "risks": [],
    }
    golden = {
        "id": "clinical-gap",
        "checks": [
            {
                "type": "item_text_contains",
                "section": "risks",
                "text": "external validation",
                "critical": True,
                "weight": 5,
            },
            {
                "type": "score_range",
                "key": "clinical_readiness",
                "max": 50,
                "critical": True,
                "weight": 5,
            },
        ],
    }
    result = evaluate_golden_audit.evaluate(audit, golden)
    assert result["score"] == 0.0
    assert result["critical_failed"] == 2
