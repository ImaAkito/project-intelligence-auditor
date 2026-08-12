# Project Intelligence Auditor

Evidence-based Codex skill for technical, product, research, and commercial auditing of software projects with an immersive intelligence dashboard.

## What it does

Project Intelligence Auditor turns a repository into a structured, evidence-backed project intelligence snapshot. It separates implementation from quality, readiness, and confidence; maps modules and dependencies; detects false completion; builds technical debt and risk registers; evaluates product and commercialization paths; and generates machine-readable audit data plus human-readable reports.

The intended workflow is:

1. scan the repository and collect objective evidence;
2. infer the system map and critical path;
3. classify evidence quality and confidence;
4. calculate module and project scores using deterministic scoring rules;
5. generate audit artifacts and roadmap recommendations;
6. compare with previous snapshots when available;
7. render or update an immersive Project Command Center.

## Core principles

- Evidence before opinion.
- Completion is not quality.
- Quality is not readiness.
- Readiness is not confidence.
- Critical-path modules weigh more than decorative or optional features.
- README claims do not count as implementation evidence unless code/tests/results support them.
- Mocks, stubs, hardcoded outputs, empty tests, dead paths, and demo-only flows reduce confirmed completion.
- Unverifiable conclusions must remain explicitly uncertain.

## Repository layout

```text
SKILL.md
references/
  scoring-model.md
  evidence-model.md
  architecture-audit.md
  product-audit.md
  commercialization-audit.md
  ml-audit.md
  medical-audit.md
  hardware-audit.md
  dashboard-spec.md
scripts/
  scan_repository.py
  detect_false_completion.py
  calculate_scores.py
  compare_snapshots.py
  validate_audit.py
schema/
  audit.schema.json
templates/
  PROJECT_AUDIT.md
  PROJECT_ROADMAP.md
  PROJECT_COMMERCIALIZATION.md
examples/
  example-audit.json
```

## Audit outputs

A target project should receive a `.project-audit/` directory containing at least:

```text
.project-audit/
  audit.json
  history/
PROJECT_AUDIT.md
PROJECT_ROADMAP.md
PROJECT_COMMERCIALIZATION.md
```

The dashboard should use `audit.json` as its source of truth instead of duplicating hand-maintained values in UI code.

## Quick start with Codex

Install this repository as a Codex skill or make it available to Codex, then run a task such as:

```text
Run the Project Intelligence Auditor on this repository. Perform a full evidence-based audit, execute safe validation checks, generate a new audit snapshot, compare it with previous snapshots if present, and build or update the immersive Project Command Center. Do not change product behavior except where minimal audit tooling is required.
```

For the full operating procedure, scoring rules, domain-specific audits, and dashboard contract, see `SKILL.md` and `references/`.

## Status

This repository currently contains the first public implementation of the audit methodology and deterministic helper scripts. The skill is designed to evolve through repeated use on real repositories.

## License

MIT.
