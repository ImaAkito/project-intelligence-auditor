# Project Intelligence Auditor Benchmarks

This directory contains deterministic synthetic fixtures and reviewed-expectation examples used to regression-test the auditor itself.

The goal is not to claim that a synthetic suite measures the full quality of an LLM-driven project audit. It checks narrower, reproducible contracts such as:

- module discovery signals;
- static architecture edges;
- cycle detection;
- dependency extraction;
- false-completion signal collection;
- weak-test signals;
- technical-debt markers.

Run the deterministic suite from the auditor repository root:

```bash
python scripts/evaluate_benchmarks.py \
  --manifest benchmarks/manifest.json \
  --minimum-score 100 \
  -o /tmp/pia-benchmark.json \
  --markdown /tmp/pia-benchmark.md
```

## Fixtures

- `layered_python` — clean API -> core -> storage dependency chain with a meaningful unit test.
- `cyclic_python` — intentional static dependency cycle.
- `false_completion` — hardcoded success, unimplemented behavior, mocked-service marker, TODO debt, and an assertion-free test.
- `js_monorepo` — `apps/` + `packages/` layout with a cross-package TypeScript import and dependency declarations.

## What a 100% fixture score means

A 100% fixture score means the current deterministic collectors satisfied every declared expectation in `manifest.json`.

It does **not** mean:

- the auditor understands arbitrary repositories perfectly;
- semantic architecture reconstruction is solved;
- the LLM will always assign correct module boundaries or criticality;
- completion/readiness scores are correct on real projects;
- false positives or false negatives are absent outside these fixtures.

The fixture suite should grow whenever a real audit reveals a reproducible deterministic failure mode.

## Human-reviewed golden audits

Deterministic fixtures cannot adequately test semantic conclusions such as critical-path classification, readiness interpretation, or whether an overall completion estimate is plausible.

For reviewed audit expectations, use:

```bash
python scripts/evaluate_golden_audit.py \
  AUDIT.json \
  GOLDEN.json \
  --minimum-score 100 \
  -o /tmp/golden-evaluation.json
```

`golden-example.json` demonstrates the format.

Prefer broad, independently reviewed expectations such as:

- a score lies in a reasonable range;
- a known core module is classified as critical path;
- production readiness remains blocked by a known hard gate;
- a specific material risk is present;
- evidence strength is at least or at most a reviewed level;
- a high-leverage recommendation is surfaced.

Avoid exact percentage goldens unless the number follows from a deterministic calculation whose inputs are themselves part of the golden contract.

A real-project golden should ideally be reviewed independently from the audit output being evaluated. This reduces the risk of simply encoding the auditor's own answer as the expected answer.
