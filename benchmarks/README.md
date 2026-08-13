# Project Intelligence Auditor Benchmarks

This directory contains deterministic synthetic fixtures used to regression-test the auditor itself.

The goal is not to claim that a synthetic suite measures the full quality of an LLM-driven project audit. It checks narrower, reproducible contracts such as:

- module discovery signals;
- static architecture edges;
- cycle detection;
- dependency extraction;
- false-completion signal collection;
- weak-test signals;
- technical-debt markers.

Run the suite from the auditor repository root:

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

## What a 100% score means

A 100% fixture score means the current deterministic collectors satisfied every declared expectation in `manifest.json`.

It does **not** mean:

- the auditor understands arbitrary repositories perfectly;
- semantic architecture reconstruction is solved;
- the LLM will always assign correct module boundaries or criticality;
- completion/readiness scores are correct on real projects;
- false positives or false negatives are absent outside these fixtures.

The benchmark suite should grow whenever a real audit reveals a reproducible deterministic failure mode.
