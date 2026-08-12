# Project Intelligence Auditor

Evidence-based Codex skill and audit toolkit for understanding the real state of a software, AI/ML, research, medical, hardware, or hybrid project.

It combines model-assisted repository reasoning with deterministic evidence collectors, scoring, prioritization, snapshot comparison, and a self-contained interactive **Project Intelligence Command Center**.

## Why this exists

A repository can look "80% done" while the critical workflow is untested, the UI is wired to mocks, deployment is missing, or the commercial path is undefined.

Project Intelligence Auditor keeps separate:

- **Completion** — how much capability exists.
- **Confirmed completion** — how much is supported by strong evidence.
- **Quality** — how well the existing implementation is engineered.
- **Readiness** — whether target-state gates are satisfied.
- **Confidence** — how reliable the audit itself is.
- **Evidence strength** — why a claim should be believed.

The LLM is used for system understanding and contextual judgment. Aggregate completion scores are calculated by deterministic tooling from evidence-backed inputs.

## Current capabilities

The v0.2 toolchain includes:

- repository inventory;
- module-candidate discovery;
- dependency declaration inventory;
- test inventory and weak-test signals;
- false-completion signal detection;
- technical-debt signal collection;
- Git history, churn, velocity, hotspot, and author-concentration signals;
- evidence model E0–E4;
- deterministic module/project scoring;
- readiness-gate methodology;
- deterministic recommendation leverage ranking;
- audit snapshot schema validation;
- snapshot comparison;
- engineering, architecture, security, product, commercialization, research, ML, medical, and hardware audit references;
- standalone interactive Project Command Center generation.

## Repository layout

```text
SKILL.md
references/
  architecture-audit.md
  commercialization-audit.md
  dashboard-spec.md
  evidence-model.md
  hardware-audit.md
  medical-audit.md
  ml-audit.md
  product-audit.md
  readiness-gates.md
  research-audit.md
  scoring-model.md
  security-audit.md
scripts/
  audit_utils.py
  analyze_git_history.py
  bootstrap_audit.py
  build_dashboard.py
  calculate_scores.py
  collect_dependencies.py
  collect_tests.py
  compare_snapshots.py
  detect_false_completion.py
  detect_technical_debt.py
  discover_modules.py
  plan_actions.py
  run_collectors.py
  scan_repository.py
  validate_audit.py
  validate_skill.py
schema/
  audit.schema.json
templates/
  PROJECT_AUDIT.md
  PROJECT_ROADMAP.md
  PROJECT_COMMERCIALIZATION.md
examples/
  example-audit.json
tests/
```

## Quick start

Make this folder available to Codex as the `project-intelligence-auditor` skill and ask:

```text
Use the Project Intelligence Auditor skill.

Perform a full evidence-based audit of this repository. Run the deterministic
collectors first, verify the critical path, execute safe validation checks,
calculate deterministic scores, rank the highest-leverage work, preserve an
audit snapshot, and build the Project Intelligence Command Center.

Do not change product behavior unless I separately ask you to implement fixes.
```

The skill's `SKILL.md` contains the full operating workflow.

## Deterministic collector suite

From the target repository, with the auditor scripts available:

```bash
python scripts/run_collectors.py . -o .project-audit/discovery.json
```

The suite records evidence candidates in one discovery artifact.

It intentionally does **not** calculate completion from file counts, TODO counts, or Git activity.

Create an unscored audit skeleton:

```bash
python scripts/bootstrap_audit.py .project-audit/discovery.json \
  -o .project-audit/audit.json
```

Codex then reviews the repository in context, turns verified findings into evidence, defines the real modules and critical path, and fills the scoring inputs.

## Scoring

After module inputs have been evidence-backed:

```bash
python scripts/calculate_scores.py .project-audit/audit.json
```

Then rank recommendations:

```bash
python scripts/plan_actions.py .project-audit/audit.json
```

Validate the snapshot:

```bash
python scripts/validate_audit.py .project-audit/audit.json
```

## Project Intelligence Command Center

Generate a standalone interactive dashboard:

```bash
python scripts/build_dashboard.py .project-audit/audit.json \
  -o .project-audit/PROJECT_COMMAND_CENTER.html
```

Open the resulting HTML file in a browser.

The dashboard includes:

- executive readiness scores;
- bottleneck view;
- module health map;
- module drill-down;
- dependency graph;
- risk matrix;
- highest-leverage actions;
- commercialization view;
- development directions;
- evidence explorer.

It embeds the audit snapshot at generation time and has no runtime web dependency.

## Audit outputs

A fully audited target project should contain:

```text
.project-audit/
  discovery.json
  audit.json
  PROJECT_COMMAND_CENTER.html
  history/
PROJECT_AUDIT.md
PROJECT_ROADMAP.md
PROJECT_COMMERCIALIZATION.md
```

`audit.json` is the canonical machine-readable source of truth for the dashboard and derived reports.

## Historical comparison

Keep previous snapshots under `.project-audit/history/`, then compare:

```bash
python scripts/compare_snapshots.py OLD.json NEW.json
```

Use historical changes to detect progress, new risks, closed risks, regressions, and readiness movement. Activity itself is not treated as progress.

## Development

Install development dependencies:

```bash
python -m pip install -e '.[dev]'
```

Run:

```bash
python scripts/validate_skill.py SKILL.md
python -m compileall scripts tests
ruff check scripts tests
pytest
python scripts/validate_audit.py examples/example-audit.json
python scripts/build_dashboard.py examples/example-audit.json -o /tmp/project-command-center.html
```

## Design principles

- Evidence before opinion.
- Unknown is different from zero.
- Completion is different from quality.
- Readiness is gate-based.
- Critical-path gaps matter more than decorative gaps.
- README claims are not implementation proof.
- Heuristic scanner matches are not automatic defects.
- A passing unit test is not automatically end-to-end readiness.
- Commercial potential is evaluated separately from technical sophistication.
- Every important score should be explainable through evidence.

## Status

v0.2 is a usable foundation for real repository audits. The next development layers are deeper dependency/architecture inference, richer historical forecasting, browser-based dashboard validation, ecosystem-specific static-analysis adapters, and evaluation against real audit fixtures.

## License

MIT.
