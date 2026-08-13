from __future__ import annotations

from pathlib import Path

import bootstrap_audit
import detect_project_profile
import generate_audit_plan
import run_collectors


def write_pyproject(root: Path, dependencies: list[str]) -> None:
    rendered = ",\n".join(f'  "{dependency}"' for dependency in dependencies)
    (root / "pyproject.toml").write_text(
        "[project]\n"
        'name = "fixture"\n'
        'version = "0.0.0"\n'
        "dependencies = [\n"
        f"{rendered}\n"
        "]\n",
        encoding="utf-8",
    )


def profile_by_id(result: dict, profile_id: str) -> dict:
    return next(item for item in result["profiles"] if item["id"] == profile_id)


def test_ml_medical_profile_routes_specialized_reviews(tmp_path: Path) -> None:
    write_pyproject(tmp_path, ["torch>=2", "monai>=1", "pydicom>=3"])
    (tmp_path / "train.py").write_text("print('train')\n", encoding="utf-8")

    result = detect_project_profile.detect(tmp_path)

    assert "machine_learning" in result["applicable_profiles"]
    assert "medical_healthcare" in result["applicable_profiles"]
    assert "references/ml-audit.md" in result["recommended_references"]
    assert "references/medical-audit.md" in result["recommended_references"]
    assert "ml_production" in result["recommended_readiness_gates"]
    assert "clinical" in result["recommended_readiness_gates"]
    assert profile_by_id(result, "medical_healthcare")["confidence"] > 50


def test_hardware_profile_routes_hardware_and_integration_gates(tmp_path: Path) -> None:
    (tmp_path / "platformio.ini").write_text("[env:board]\nplatform = native\n", encoding="utf-8")
    firmware = tmp_path / "firmware"
    firmware.mkdir()
    (firmware / "main.ino").write_text("void setup() {}\nvoid loop() {}\n", encoding="utf-8")

    result = detect_project_profile.detect(tmp_path)

    assert "hardware_embedded" in result["applicable_profiles"]
    assert "references/hardware-audit.md" in result["recommended_references"]
    assert "hardware" in result["recommended_readiness_gates"]
    assert "system_integration" in result["recommended_readiness_gates"]


def test_research_plan_preserves_research_production_separation(tmp_path: Path) -> None:
    write_pyproject(tmp_path, ["scipy>=1.13", "statsmodels>=0.14"])
    experiments = tmp_path / "experiments"
    experiments.mkdir()
    (experiments / "run.py").write_text("print('experiment')\n", encoding="utf-8")

    profile = detect_project_profile.detect(tmp_path)
    plan = generate_audit_plan.build_plan(profile)

    assert "research" in plan["applicable_profiles"]
    assert "research" in plan["readiness_gates"]
    assert "publication" in plan["readiness_gates"]
    assert "production" in plan["readiness_gates"]
    domain_phase = next(phase for phase in plan["phases"] if phase["id"] == "domain-reviews")
    assert any(review["profile"] == "research" for review in domain_phase["reviews"])
    validation_phase = next(phase for phase in plan["phases"] if phase["id"] == "behavior-validation")
    assert "Do not assume a test command" in validation_phase["note"]


def test_discovery_and_bootstrap_carry_profile_routing(tmp_path: Path) -> None:
    write_pyproject(tmp_path, ["fastapi>=0.115"])
    api = tmp_path / "api"
    api.mkdir()
    (api / "main.py").write_text("from fastapi import FastAPI\napp = FastAPI()\n", encoding="utf-8")

    discovery = run_collectors.run(tmp_path)
    assert discovery["collectors"]["project_profile"]["status"] == "ok"

    audit = bootstrap_audit.bootstrap(discovery)
    assert audit["metadata"]["auditor_version"] == "0.5.0"
    assert "web_backend" in audit["project_profile"]["applicable_profiles"]
    assert "commercial" in audit["project_profile"]["recommended_readiness_gates"]
    assert "scale" in audit["project_profile"]["recommended_readiness_gates"]
    assert audit["scores"]["clinical_readiness"] is None
