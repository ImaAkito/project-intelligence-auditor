#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import collect_dependencies
import scan_repository
from audit_utils import iter_files, relative_posix, resolve_root, write_json

PROFILE_DEPENDENCIES: dict[str, dict[str, float]] = {
    "web_frontend": {
        "react": 35,
        "next": 35,
        "vue": 35,
        "svelte": 35,
        "@angular/core": 35,
        "vite": 20,
        "astro": 30,
    },
    "web_backend": {
        "fastapi": 35,
        "flask": 35,
        "django": 35,
        "express": 35,
        "@nestjs/core": 35,
        "spring-boot": 35,
        "gin-gonic/gin": 35,
        "actix-web": 35,
    },
    "machine_learning": {
        "torch": 35,
        "tensorflow": 35,
        "keras": 30,
        "scikit-learn": 30,
        "xgboost": 30,
        "lightgbm": 30,
        "transformers": 35,
        "ultralytics": 35,
        "mlflow": 20,
        "onnxruntime": 20,
    },
    "medical_healthcare": {
        "pydicom": 45,
        "nibabel": 45,
        "monai": 50,
        "highdicom": 50,
        "wfdb": 45,
        "pynetdicom": 50,
        "dicomweb-client": 45,
    },
    "research": {
        "scipy": 18,
        "statsmodels": 25,
        "sympy": 20,
        "jax": 25,
        "jupyter": 20,
        "papermill": 20,
    },
    "data_engineering": {
        "pandas": 20,
        "polars": 25,
        "duckdb": 25,
        "sqlalchemy": 20,
        "alembic": 20,
        "pyspark": 35,
        "apache-airflow": 35,
        "dbt-core": 35,
    },
    "desktop": {
        "pyqt5": 40,
        "pyqt6": 40,
        "pyside6": 40,
        "electron": 40,
        "tauri": 40,
    },
    "mobile": {
        "react-native": 40,
        "flutter": 40,
        "expo": 35,
    },
    "devops_infrastructure": {
        "kubernetes": 20,
        "docker": 15,
        "terraform": 30,
        "pulumi": 30,
    },
}

PROFILE_FILE_SUFFIXES: dict[str, dict[str, float]] = {
    "medical_healthcare": {
        ".dcm": 45,
        ".nii": 40,
        ".mha": 35,
        ".mhd": 35,
        ".nrrd": 35,
        ".edf": 35,
    },
    "hardware_embedded": {
        ".kicad_sch": 50,
        ".kicad_pcb": 50,
        ".sch": 30,
        ".brd": 30,
        ".ino": 45,
        ".sv": 35,
        ".vhd": 35,
        ".vhdl": 35,
    },
    "research": {
        ".ipynb": 18,
        ".tex": 18,
    },
}

PROFILE_FILENAMES: dict[str, dict[str, float]] = {
    "devops_infrastructure": {
        "Dockerfile": 25,
        "docker-compose.yml": 20,
        "docker-compose.yaml": 20,
        "terraform.tf": 35,
        "Pulumi.yaml": 35,
        "Chart.yaml": 25,
    },
    "hardware_embedded": {
        "platformio.ini": 45,
        "west.yml": 35,
        "prj.conf": 30,
    },
    "research": {
        "CITATION.cff": 20,
    },
}

PROFILE_DIRECTORY_HINTS: dict[str, dict[str, float]] = {
    "machine_learning": {
        "models": 12,
        "training": 15,
        "checkpoints": 12,
    },
    "research": {
        "experiments": 18,
        "notebooks": 18,
        "paper": 18,
    },
    "web_frontend": {
        "frontend": 18,
        "web": 10,
        "ui": 10,
    },
    "web_backend": {
        "backend": 18,
        "api": 14,
        "server": 12,
    },
    "hardware_embedded": {
        "firmware": 25,
        "pcb": 25,
        "hardware": 20,
    },
}

REFERENCE_ROUTING: dict[str, list[str]] = {
    "machine_learning": ["references/ml-audit.md"],
    "medical_healthcare": ["references/medical-audit.md"],
    "research": ["references/research-audit.md"],
    "hardware_embedded": ["references/hardware-audit.md"],
}

GATE_ROUTING: dict[str, list[str]] = {
    "machine_learning": ["ml_production"],
    "medical_healthcare": ["clinical"],
    "research": ["research", "publication"],
    "hardware_embedded": ["hardware", "system_integration"],
    "web_backend": ["scale"],
}


def add_signal(
    buckets: dict[str, list[dict[str, Any]]],
    profile: str,
    *,
    kind: str,
    value: str,
    weight: float,
    source: str | None = None,
) -> None:
    buckets[profile].append(
        {
            "kind": kind,
            "value": value,
            "weight": float(weight),
            "source": source,
        }
    )


def collect_file_signals(root: Path, buckets: dict[str, list[dict[str, Any]]]) -> None:
    for path in iter_files(root, max_bytes=None):
        relative = relative_posix(path, root)
        suffix = path.suffix.lower()
        name = path.name
        for profile, suffixes in PROFILE_FILE_SUFFIXES.items():
            if suffix in suffixes:
                add_signal(
                    buckets,
                    profile,
                    kind="file_suffix",
                    value=suffix,
                    weight=suffixes[suffix],
                    source=relative,
                )
        for profile, names in PROFILE_FILENAMES.items():
            if name in names:
                add_signal(
                    buckets,
                    profile,
                    kind="filename",
                    value=name,
                    weight=names[name],
                    source=relative,
                )


def collect_directory_signals(root: Path, buckets: dict[str, list[dict[str, Any]]]) -> None:
    seen: set[tuple[str, str]] = set()
    for path in root.rglob("*"):
        if not path.is_dir():
            continue
        name = path.name.lower()
        for profile, names in PROFILE_DIRECTORY_HINTS.items():
            if name not in names or (profile, name) in seen:
                continue
            seen.add((profile, name))
            add_signal(
                buckets,
                profile,
                kind="directory",
                value=name,
                weight=names[name],
                source=relative_posix(path, root),
            )


def profile_score(signals: list[dict[str, Any]]) -> float:
    # Repeated weak hints have diminishing value. Strong explicit ecosystem signals dominate.
    ordered = sorted((float(item["weight"]) for item in signals), reverse=True)
    score = 0.0
    attenuation = 1.0
    for weight in ordered:
        score += weight * attenuation
        attenuation *= 0.72
    return min(100.0, round(score, 2))


def profile_confidence(score: float, signal_count: int) -> float:
    if signal_count <= 0:
        return 0.0
    diversity_bonus = min(15.0, max(0, signal_count - 1) * 3.0)
    return min(95.0, round(25.0 + score * 0.58 + diversity_bonus, 2))


def detect(root: Path | str) -> dict[str, Any]:
    root_path = resolve_root(root)
    inventory = scan_repository.scan(root_path)
    dependencies = collect_dependencies.collect(root_path)
    buckets: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for dependency in dependencies.get("dependencies", []):
        if not isinstance(dependency, dict):
            continue
        name = str(dependency.get("name", "")).lower()
        for profile, mapping in PROFILE_DEPENDENCIES.items():
            if name in mapping:
                add_signal(
                    buckets,
                    profile,
                    kind="dependency",
                    value=name,
                    weight=mapping[name],
                    source=dependency.get("manifest"),
                )

    collect_file_signals(root_path, buckets)
    collect_directory_signals(root_path, buckets)

    profiles: list[dict[str, Any]] = []
    all_profiles = sorted(
        set(PROFILE_DEPENDENCIES)
        | set(PROFILE_FILE_SUFFIXES)
        | set(PROFILE_FILENAMES)
        | set(PROFILE_DIRECTORY_HINTS)
    )
    for profile in all_profiles:
        signals = buckets.get(profile, [])
        score = profile_score(signals)
        profiles.append(
            {
                "id": profile,
                "score": score,
                "confidence": profile_confidence(score, len(signals)),
                "applicable": score >= 35.0,
                "signals": sorted(
                    signals,
                    key=lambda item: (-float(item["weight"]), str(item.get("source") or "")),
                )[:20],
            }
        )

    applicable = [item["id"] for item in profiles if item["applicable"]]
    perspectives = ["engineering", "architecture", "qa_validation"]
    references = [
        "references/evidence-model.md",
        "references/scoring-model.md",
        "references/architecture-audit.md",
        "references/readiness-gates.md",
    ]
    readiness_gates = ["prototype", "mvp", "production"]

    if any(profile in applicable for profile in {"web_backend", "web_frontend", "desktop", "mobile"}):
        perspectives.extend(["security", "product", "commercial"])
        readiness_gates.append("commercial")
        references.extend(["references/security-audit.md", "references/product-audit.md", "references/commercialization-audit.md"])
    if "machine_learning" in applicable:
        perspectives.append("ai_ml")
    if "medical_healthcare" in applicable:
        perspectives.append("medical_healthcare")
    if "research" in applicable:
        perspectives.append("research")
    if "hardware_embedded" in applicable:
        perspectives.append("hardware_embedded_robotics")

    for profile in applicable:
        references.extend(REFERENCE_ROUTING.get(profile, []))
        readiness_gates.extend(GATE_ROUTING.get(profile, []))

    def unique(values: list[str]) -> list[str]:
        return list(dict.fromkeys(values))

    return {
        "collector": "detect_project_profile",
        "root": str(root_path),
        "profiles": sorted(profiles, key=lambda item: (-float(item["score"]), item["id"])),
        "applicable_profiles": applicable,
        "recommended_perspectives": unique(perspectives),
        "recommended_references": unique(references),
        "recommended_readiness_gates": unique(readiness_gates),
        "repository_signals": {
            "file_count": inventory.get("file_count"),
            "manifests": inventory.get("manifests", []),
            "unique_dependency_count": dependencies.get("unique_dependency_count"),
        },
        "limitations": [
            "Project profiles are deterministic routing hints, not semantic project classification.",
            "Absence of a profile signal does not prove that a domain perspective is irrelevant.",
            "Directory names and dependencies can be misleading; Codex must confirm applicability from project intent and source context.",
            "Medical, commercial, safety, and regulatory conclusions must never be inferred from this profile alone.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Detect deterministic project-profile routing hints.")
    parser.add_argument("root", nargs="?", default=".", type=Path)
    parser.add_argument("-o", "--output", type=Path)
    args = parser.parse_args()
    result = detect(args.root)
    if args.output:
        write_json(args.output, result)
        print(f"Wrote project profile to {args.output}")
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
