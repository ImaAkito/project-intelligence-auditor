# Adaptive Audit Routing

Project Intelligence Auditor should not apply every domain checklist to every repository. The audit should remain broad enough to catch cross-cutting risks while routing deeper review effort toward the domains actually supported by repository evidence and project intent.

`detect_project_profile.py` provides deterministic routing hints. `generate_audit_plan.py` converts those hints into an initial audit plan.

## What routing is for

Routing decides which specialized perspectives deserve deeper inspection, for example:

- AI/ML;
- medical/healthcare;
- research;
- hardware/embedded;
- web product;
- commercial/product review;
- scale/operations.

It can also recommend relevant readiness gates and reference files.

Routing is not a project taxonomy and does not decide final readiness.

## Evidence sources

The deterministic profile detector can use weak-to-strong signals such as:

- declared dependencies;
- project manifests;
- domain-specific file types;
- recognizable tooling/configuration files;
- repository directory structure.

Signals are weighted and combined with diminishing returns. A repeated weak hint should not outweigh one strong explicit ecosystem signal indefinitely.

## Required interpretation

A detected profile means "inspect this perspective", not "the project definitely belongs to this domain".

Examples:

- `pydicom` should trigger medical/data-workflow review, but does not prove the software is a regulated medical device;
- `torch` should trigger ML review, but does not prove ML is on the critical user path;
- a `firmware/` directory should trigger embedded review, but may be a legacy experiment;
- React should trigger frontend/product integration review, but does not imply a commercial product;
- notebooks should increase research-review relevance, but do not prove publication intent.

Codex must confirm project intent, critical path, and actual use before assigning domain-specific readiness scores.

## Base versus conditional perspectives

Always retain the base perspectives:

- engineering;
- architecture;
- QA/validation;
- evidence calibration;
- general prototype/MVP/production readiness where meaningful.

Conditionally deepen:

- security/product/commercial review for user-facing applications and services;
- ML production review for material model pipelines;
- clinical/medical review when medical data, clinical workflow, or intended use is material;
- research/publication review for experiment-driven projects;
- hardware/system-integration review for embedded or physical-system projects;
- scale review when a backend/service architecture is material.

## Unknown and conflicting routing

Do not force one profile when multiple profiles apply. Hybrid projects are normal.

Examples include:

- medical AI + web application;
- research ML + production API;
- hardware + embedded firmware + cloud service;
- data engineering + commercial SaaS.

When profile signals conflict with stated project intent, record the discrepancy and inspect the source context. Repository structure may be stale, experimental, or legacy.

If the detector emits no specialized profile, do not conclude that specialized review is impossible. Domain evidence can be semantic rather than syntactic.

## Adaptive plan generation

Generate an initial plan with:

```bash
python scripts/generate_audit_plan.py .
```

This writes:

```text
.project-audit/audit-plan.json
.project-audit/AUDIT_PLAN.md
```

The plan should contain:

- base audit phases;
- detected profiles;
- recommended perspectives;
- relevant reference files;
- readiness gates to consider;
- conditional domain review focuses;
- deterministic commands that are safe for the auditor itself.

Project-native validation commands still require repository-specific inspection. Do not invent `pytest`, `npm test`, deployment, model inference, hardware flashing, or other commands solely from a detected ecosystem.

## Scoring integrity

Project-profile scores are routing confidence, not project completion, quality, or readiness. Never copy profile scores into the canonical project scorecard.

A profile can be high-confidence while all corresponding readiness gates remain low or unknown.

## Safety-sensitive domains

Medical, regulatory, security, hardware-safety, financial, and other high-impact conclusions require direct evidence and contextual review. Project-profile detection must never be used as the sole basis for a safety or regulatory statement.

## Evaluation

Routing should be regression-tested with synthetic fixtures where the intended signal is explicit. When a routing failure causes a semantic audit failure, preserve both layers when useful:

1. a deterministic fixture for the missed routing signal;
2. a semantic challenge for the incorrect high-level audit conclusion.
