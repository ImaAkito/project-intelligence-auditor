from __future__ import annotations

from pathlib import Path

import check_audit_integrity
import evaluate_benchmarks
import evaluate_golden_audit
from audit_utils import load_json

ROOT = Path(__file__).resolve().parents[1]


def test_synthetic_benchmark_suite_meets_declared_contract() -> None:
    result = evaluate_benchmarks.evaluate(ROOT, ROOT / "benchmarks" / "manifest.json")
    assert result["case_count"] == 4
    assert result["failed_checks"] == 0
    assert result["suite_score"] == 100.0


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
            {"type": "module_classification", "module_id": "core", "expected": "critical_path"},
            {"type": "module_evidence_level", "module_id": "core", "minimum": "E3"},
            {"type": "readiness_state", "gate": "mvp", "expected": "ready"},
            {"type": "readiness_state", "gate": "production", "expected": "blocked"},
            {"type": "recommendation_presence", "id": "rec-integration-tests"},
        ],
    }
    result = evaluate_golden_audit.evaluate(audit, golden)
    assert result["score"] == 100.0
    assert result["failed"] == 0
