# Project Intelligence Auditor

Evidence-based Codex skill for technical, product, research, commercial, and readiness auditing of software projects with deterministic scoring and an interactive Project Intelligence Command Center.

## What it does

Project Intelligence Auditor turns a repository into a structured, evidence-backed project intelligence snapshot. It separates completion from quality, readiness, and audit confidence; reconstructs module boundaries and code-level dependencies; detects false completion; tracks technical debt and risk; evaluates product and commercialization paths; ranks high-leverage work; compares project state across audit snapshots; and now regression-tests its own deterministic collectors against explicit benchmark fixtures.

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
9. check structural audit integrity and traceability;
10. compare history and estimate descriptive trajectory when enough snapshots exist;
11. render the Project Intelligence Command Center.

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
- The auditor itself must be regression-tested; a benchmark pass is evidence for a narrow collector contract, not proof of universal audit accuracy.

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
  evaluation-methodology.md
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
  check_audit_integrity.py
  evaluate_benchmarks.py
  validate_audit.py
  build_dashboard.py
benchmarks/
  manifest.json
  README.md
  fixtures/
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

Check structural traceability and actionability of the snapshot:

```bash
python scripts/check_audit_integrity.py \
  .project-audit/audit.json \
  --minimum-coverage 85 \
  -o .project-audit/integrity.json
```

`integrity_coverage` is intentionally narrow. It tells you whether scored modules, dependency edges, risks, assessed readiness gates, and validation runs are linked to known evidence and whether recommendations are actionable. It does not prove that the human/LLM judgments are correct.

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

## Self-evaluation benchmark suite

v0.4 adds an explicit dogfooding layer for the auditor itself.

Run:

```bash
python scripts/evaluate_benchmarks.py \
  --manifest benchmarks/manifest.json \
  --minimum-score 100 \
  -o /tmp/pia-benchmark.json \
  --markdown /tmp/pia-benchmark.md
```

The initial synthetic corpus covers:

- a clean layered Python service;
- an intentional static dependency cycle;
- a false-completion trap with hardcoded success, unimplemented behavior, mocked-service markers, TODO debt, and an assertion-free test;
- a JavaScript/TypeScript `apps/` + `packages/` monorepo with a cross-package import.

A 100% benchmark score means only that the deterministic collectors satisfied the declared expectations in these fixtures. It is not an overall accuracy claim for semantic project auditing. The evaluation methodology is documented in `references/evaluation-methodology.md`.

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
Run the Project Intelligence Auditor on this repository. Perform a full evidence-based audit, execute safe validation checks, generate a new audit snapshot, compare it with previous snapshots if present, evaluate readiness gates, verify audit integrity, and build or update the Project Intelligence Command Center. Do not change product behavior except where minimal audit tooling is required.
```

For the full operating procedure, evidence model, scoring rules, domain-specific reviews, evaluation methodology, and dashboard contract, see `SKILL.md` and `references/`.

## Status

Current development line: **v0.4**.

v0.4 adds self-evaluation: deterministic synthetic benchmark fixtures, a reusable benchmark harness, structural audit-integrity coverage, and an explicit multi-layer evaluation methodology. The purpose is to make failures of the auditor itself reproducible instead of continuously adding heuristics without measuring regressions.

The next layer is a human-reviewed real-world challenge corpus for semantic audit quality: projects where expected critical-path, readiness, false-completion, research/ML, and commercialization conclusions are reviewed independently rather than reduced to brittle exact percentages.

## License

MIT.
