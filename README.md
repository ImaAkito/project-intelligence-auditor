# Project Intelligence Auditor

Evidence-based Codex skill for technical, product, research, commercial, and readiness auditing of software projects with deterministic scoring and an interactive Project Intelligence Command Center.

## What it does

Project Intelligence Auditor turns a repository into a structured, evidence-backed project intelligence snapshot. It separates completion from quality, readiness, and audit confidence; reconstructs module boundaries and code-level dependencies; detects false completion; tracks technical debt and risk; evaluates product and commercialization paths; ranks high-leverage work; and compares project state across audit snapshots.

The tool is designed around one rule: **important numbers should come from explicit evidence and deterministic calculations, not from an LLM guessing a percentage.**

The workflow is:

1. collect repository evidence;
2. infer module and architecture candidates;
3. review project intent, critical path, and semantic completeness;
4. validate behavior safely;
5. score module completion/quality from evidence-backed inputs;
6. evaluate explicit readiness gates with coverage and uncertainty intervals;
7. analyze product, research, commercial, security, and domain-specific risks;
8. rank high-leverage actions;
9. compare history and estimate descriptive trajectory when enough snapshots exist;
10. render the Project Intelligence Command Center.

## Core principles

- Evidence before opinion.
- Completion is not quality.
- Quality is not readiness.
- Readiness is not confidence.
- Unknown evidence stays visible instead of silently becoming zero.
- Critical-path modules weigh more than optional polish.
- README claims do not count as implementation evidence unless code/tests/results support them.
- Static imports prove code-level dependency existence, not successful runtime integration.
- Git activity is an activity signal, not proof of progress.
- Mocks, stubs, hardcoded outputs, empty tests, dead paths, and demo-only flows are false-completion candidates until reviewed in context.

## Repository layout

```text
SKILL.md
references/
  scoring-model.md
  evidence-model.md
  architecture-audit.md
  architecture-inference.md
  readiness-gates.md
  trajectory-analysis.md
  product-audit.md
  commercialization-audit.md
  research-audit.md
  security-audit.md
  ml-audit.md
  medical-audit.md
  hardware-audit.md
  dashboard-spec.md
scripts/
  run_collectors.py
  scan_repository.py
  discover_modules.py
  infer_architecture.py
  collect_dependencies.py
  collect_tests.py
  analyze_git_history.py
  detect_false_completion.py
  detect_technical_debt.py
  bootstrap_audit.py
  calculate_scores.py
  score_readiness.py
  plan_actions.py
  compare_snapshots.py
  forecast_trajectory.py
  validate_audit.py
  build_dashboard.py
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

A target project should receive:

```text
.project-audit/
  discovery.json
  audit.json
  PROJECT_COMMAND_CENTER.html
  history/
    <timestamp>.json
PROJECT_AUDIT.md
PROJECT_ROADMAP.md
PROJECT_COMMERCIALIZATION.md
```

`audit.json` is the canonical structured source. The dashboard reads it directly rather than duplicating hand-maintained scores.

## Deterministic workflow

Run repository discovery:

```bash
python scripts/run_collectors.py . -o .project-audit/discovery.json
```

Bootstrap an unscored audit skeleton:

```bash
python scripts/bootstrap_audit.py .project-audit/discovery.json \
  -o .project-audit/audit.json
```

After Codex reviews evidence and fills module scoring inputs:

```bash
python scripts/calculate_scores.py .project-audit/audit.json
```

After Codex defines structured readiness criteria:

```bash
python scripts/score_readiness.py .project-audit/audit.json
```

Rank recommendations:

```bash
python scripts/plan_actions.py .project-audit/audit.json
```

Validate the canonical snapshot:

```bash
python scripts/validate_audit.py .project-audit/audit.json
```

Build the standalone Project Intelligence Command Center:

```bash
python scripts/build_dashboard.py .project-audit/audit.json \
  -o .project-audit/PROJECT_COMMAND_CENTER.html
```

Compare two snapshots:

```bash
python scripts/compare_snapshots.py OLD.json NEW.json
```

With three or more comparable snapshots, attach descriptive trajectory analysis:

```bash
python scripts/forecast_trajectory.py \
  --history-dir .project-audit/history \
  --update-audit .project-audit/audit.json
```

The forecast is intentionally conservative: target ETA is omitted unless there are at least three observations, positive trend, and sufficient linear fit. Even when emitted, it is labeled descriptive rather than a delivery promise.

## Project Command Center

The built-in standalone dashboard currently exposes:

- executive project state;
- module health and drill-down;
- dependency graph;
- static dependency cycles and hotspots;
- readiness gates with evidence coverage and score intervals;
- risk matrix;
- highest-leverage actions;
- project trajectory;
- commercialization and development directions;
- evidence explorer.

## Quick start with Codex

Install this repository as a Codex skill or make it available to Codex, then run:

```text
Run the Project Intelligence Auditor on this repository. Perform a full evidence-based audit, execute safe validation checks, generate a new audit snapshot, compare it with previous snapshots if present, evaluate readiness gates, and build or update the Project Intelligence Command Center. Do not change product behavior except where minimal audit tooling is required.
```

For the full operating procedure, evidence model, scoring rules, domain-specific reviews, and dashboard contract, see `SKILL.md` and `references/`.

## Status

Current development line: **v0.3**.

v0.3 adds static architecture inference, evidence-backed dependency bootstrapping, structured readiness scoring with uncertainty bounds, richer snapshot comparison, descriptive trajectory analysis, and expanded Command Center views.

The project is intentionally being developed against real audit use cases rather than treating repository metrics as a proxy for project quality.

## License

MIT.
