# Semantic Calibration Reference

Semantic calibration evaluates whether Project Intelligence Auditor reaches defensible high-level conclusions when repository facts are ambiguous, misleading, or easy to overvalue.

This layer exists because deterministic collectors can be correct while the audit conclusion is still wrong.

## Calibration unit

A semantic challenge consists of:

- a minimized repository fixture;
- a written failure mode the case is designed to expose;
- a human-reviewed `golden.json` contract;
- an independently generated audit result;
- an evaluator report comparing the result with the golden expectations.

Use `challenges/manifest.json` as the corpus index.

## Golden contract design

Prefer robust expectations:

- broad score ranges;
- score relations such as Research Readiness > Production Readiness;
- readiness state sets;
- required risk/recommendation concepts expressed as text fragments;
- required evidence bounds;
- explicit empty/unknown commercialization fields when evidence is absent.

Avoid exact score targets unless the value is itself the output of a deterministic rule.

### Critical checks

Use `critical: true` for conclusions whose omission materially invalidates the audit, for example:

- missing known data leakage;
- declaring clinical readiness despite absent external validation;
- declaring a demo-only product MVP-ready;
- inventing customer validation;
- collapsing research readiness into production readiness.

Critical failures are counted separately from the weighted semantic score. A high average must not hide a major reasoning error.

## Current challenge families

### Polished mock product

Tests whether visual polish, README claims, and demo output are incorrectly counted as integrated product capability.

### ML leakage

Tests whether the auditor inspects evaluation design rather than trusting a high metric. Leakage, grouping, preprocessing order, and split semantics are material.

### Medical validation gap

Tests whether internal retrospective metrics are kept separate from clinical readiness, external validation, calibration, subgroup analysis, intended use, and regulatory evidence.

### Research versus production

Tests whether a reproducible research artifact can be judged strong for research while remaining weak for deployment and operations.

### Commercial evidence gap

Tests whether technical maturity is kept separate from ICP, customer discovery, pricing, sales motion, support burden, and route-to-revenue evidence.

## Running calibration

First validate corpus structure:

```bash
python scripts/validate_challenge_corpus.py
```

Run the auditor independently on every fixture and save canonical audit outputs to a results directory using `<case-id>.json`.

Then evaluate:

```bash
python scripts/evaluate_challenge_corpus.py \
  .project-audit/challenge-results \
  --require-all \
  --minimum-score 80 \
  -o .project-audit/challenge-evaluation.json \
  --markdown .project-audit/challenge-evaluation.md
```

## Interpreting results

Do not publish the aggregate challenge score as universal model accuracy.

Track at least:

- aggregate weighted agreement;
- critical semantic failures;
- per-domain scores;
- missing challenge results;
- regressions versus earlier auditor versions;
- recurring failure families.

A version is not semantically improved merely because its aggregate score increased. A new critical failure in a safety- or validity-sensitive domain can outweigh small gains elsewhere.

## Corpus evolution

When a real project audit reveals a reproducible semantic failure:

1. isolate the minimal facts that caused the reasoning failure;
2. remove confidential or project-specific details;
3. create a compact challenge fixture;
4. write a reviewed golden contract using ranges/categories rather than preferred exact scores;
5. demonstrate that the current auditor fails the challenge;
6. improve instructions/tooling/scoring;
7. keep the challenge permanently as a regression case.

The goal is an accumulating record of known reasoning traps, not a showcase of easy examples.
