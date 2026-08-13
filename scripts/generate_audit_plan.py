#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import detect_project_profile
from audit_utils import load_json, resolve_root, write_json


def build_plan(profile: dict[str, Any]) -> dict[str, Any]:
    profiles = profile.get("applicable_profiles", [])
    profiles = profiles if isinstance(profiles, list) else []
    perspectives = profile.get("recommended_perspectives", [])
    references = profile.get("recommended_references", [])
    gates = profile.get("recommended_readiness_gates", [])

    phases: list[dict[str, Any]] = [
        {
            "id": "scope-safety",
            "title": "Establish scope, instructions, and safe execution limits",
            "required": True,
            "outputs": ["repository scope", "execution constraints", "initial limitations"],
        },
        {
            "id": "deterministic-discovery",
            "title": "Run deterministic collectors and bootstrap the audit skeleton",
            "required": True,
            "commands": [
                "python scripts/run_collectors.py . -o .project-audit/discovery.json",
                "python scripts/bootstrap_audit.py .project-audit/discovery.json -o .project-audit/audit.json",
            ],
        },
        {
            "id": "intent-system-map",
            "title": "Recover project intent, system boundaries, modules, and critical path",
            "required": True,
            "outputs": ["mission", "target users", "core workflow", "module map", "critical path"],
        },
        {
            "id": "semantic-completeness",
            "title": "Review false completion, integration gaps, debt, architecture, and evidence quality",
            "required": True,
        },
        {
            "id": "behavior-validation",
            "title": "Run safe project-native validation and record validation_runs",
            "required": True,
            "note": "Choose commands from the audited repository. Do not assume a test command merely from language detection.",
        },
    ]

    domain_reviews: list[dict[str, Any]] = []
    if "machine_learning" in profiles:
        domain_reviews.append(
            {
                "profile": "machine_learning",
                "reference": "references/ml-audit.md",
                "focus": [
                    "data splits and leakage",
                    "train/inference preprocessing parity",
                    "representative validation",
                    "model/data lineage",
                    "latency/resources and monitoring",
                ],
            }
        )
    if "medical_healthcare" in profiles:
        domain_reviews.append(
            {
                "profile": "medical_healthcare",
                "reference": "references/medical-audit.md",
                "focus": [
                    "intended use",
                    "patient-level evaluation",
                    "external validation",
                    "calibration/subgroups/domain shift",
                    "clinical safety and regulatory evidence",
                ],
            }
        )
    if "research" in profiles:
        domain_reviews.append(
            {
                "profile": "research",
                "reference": "references/research-audit.md",
                "focus": [
                    "research question",
                    "baseline/ablation design",
                    "reproducibility",
                    "uncertainty/statistics",
                    "claim-to-evidence alignment",
                ],
            }
        )
    if "hardware_embedded" in profiles:
        domain_reviews.append(
            {
                "profile": "hardware_embedded",
                "reference": "references/hardware-audit.md",
                "focus": [
                    "schematic/PCB/firmware maturity",
                    "power/thermal/mechanical integration",
                    "calibration and fault handling",
                    "manufacturability",
                    "system integration testing",
                ],
            }
        )

    if domain_reviews:
        phases.append(
            {
                "id": "domain-reviews",
                "title": "Apply domain-specific reviews",
                "required": True,
                "reviews": domain_reviews,
            }
        )

    if any(profile_id in profiles for profile_id in {"web_frontend", "web_backend", "desktop", "mobile"}):
        phases.append(
            {
                "id": "product-commercial",
                "title": "Evaluate product workflow and commercialization evidence",
                "required": True,
                "references": [
                    "references/product-audit.md",
                    "references/commercialization-audit.md",
                ],
            }
        )

    phases.extend(
        [
            {
                "id": "scoring-readiness",
                "title": "Fill evidence-backed scoring inputs and evaluate applicable readiness gates",
                "required": True,
                "readiness_gates": gates,
                "commands": [
                    "python scripts/calculate_scores.py .project-audit/audit.json",
                    "python scripts/score_readiness.py .project-audit/audit.json",
                ],
            },
            {
                "id": "risks-actions",
                "title": "Build risk register, adversarial review, and highest-leverage action plan",
                "required": True,
                "commands": ["python scripts/plan_actions.py .project-audit/audit.json"],
            },
            {
                "id": "integrity-artifacts",
                "title": "Validate traceability/schema and build reports/dashboard",
                "required": True,
                "commands": [
                    "python scripts/check_audit_integrity.py .project-audit/audit.json --minimum-coverage 85 -o .project-audit/integrity.json",
                    "python scripts/validate_audit.py .project-audit/audit.json",
                    "python scripts/build_dashboard.py .project-audit/audit.json -o .project-audit/PROJECT_COMMAND_CENTER.html",
                ],
            },
        ]
    )

    return {
        "metadata": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "generator": "project-intelligence-auditor",
            "root": profile.get("root"),
        },
        "applicable_profiles": profiles,
        "perspectives": perspectives,
        "references": references,
        "readiness_gates": gates,
        "phases": phases,
        "routing_confidence": {
            item.get("id"): item.get("confidence")
            for item in profile.get("profiles", [])
            if isinstance(item, dict) and item.get("applicable") is True
        },
        "limitations": [
            "This plan is a routing aid generated from deterministic profile signals.",
            "Codex must confirm domain applicability from project intent and source context before scoring.",
            "The plan does not replace repository-specific AGENTS.md instructions or safe execution judgment.",
        ],
    }


def render_markdown(plan: dict[str, Any]) -> str:
    lines = [
        "# Adaptive Audit Plan",
        "",
        f"Profiles: {', '.join(plan.get('applicable_profiles', [])) or 'none detected'}",
        f"Perspectives: {', '.join(plan.get('perspectives', []))}",
        f"Readiness gates: {', '.join(plan.get('readiness_gates', []))}",
        "",
        "## Phases",
        "",
    ]
    for index, phase in enumerate(plan.get("phases", []), start=1):
        lines.append(f"### {index}. {phase.get('title', phase.get('id', 'Phase'))}")
        note = phase.get("note")
        if note:
            lines.append("")
            lines.append(str(note))
        commands = phase.get("commands", [])
        if isinstance(commands, list) and commands:
            lines.append("")
            lines.append("```bash")
            lines.extend(str(command) for command in commands)
            lines.append("```")
        reviews = phase.get("reviews", [])
        if isinstance(reviews, list):
            for review in reviews:
                if not isinstance(review, dict):
                    continue
                lines.append("")
                lines.append(f"- **{review.get('profile')}** — `{review.get('reference')}`")
                for focus in review.get("focus", []):
                    lines.append(f"  - {focus}")
        lines.append("")
    lines.extend(
        [
            "## Limitations",
            "",
            *[f"- {item}" for item in plan.get("limitations", [])],
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate an adaptive Project Intelligence audit plan.")
    parser.add_argument("root", nargs="?", default=".", type=Path)
    parser.add_argument("--profile", type=Path)
    parser.add_argument("-o", "--output", type=Path, default=Path(".project-audit/audit-plan.json"))
    parser.add_argument("--markdown", type=Path, default=Path(".project-audit/AUDIT_PLAN.md"))
    args = parser.parse_args()

    root = resolve_root(args.root)
    profile = load_json(args.profile) if args.profile else detect_project_profile.detect(root)
    plan = build_plan(profile)

    output = args.output if args.output.is_absolute() else root / args.output
    markdown = args.markdown if args.markdown.is_absolute() else root / args.markdown
    write_json(output, plan)
    markdown.parent.mkdir(parents=True, exist_ok=True)
    markdown.write_text(render_markdown(plan), encoding="utf-8")
    print(json.dumps({"output": str(output), "markdown": str(markdown), "profiles": plan["applicable_profiles"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
