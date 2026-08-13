# Auditor Evaluation Methodology

Project Intelligence Auditor must be evaluated at multiple layers. A single benchmark score is not sufficient because deterministic collection, semantic reasoning, scoring integrity, and usefulness are different capabilities.

## Layer 1 — Deterministic collector regression

Use `scripts/evaluate_benchmarks.py` against `benchmarks/manifest.json`.

This layer checks reproducible expectations such as static dependency detection, cycle detection, dependency extraction, false-completion signals, weak-test signals, and technical-debt markers.

A regression here is actionable because the expected signal is known in advance.

Do not interpret the fixture score as overall audit accuracy.

## Layer 2 — Audit artifact integrity

Use `scripts/check_audit_integrity.py AUDIT.json`.

This layer checks whether important structured claims are internally traceable and actionable:

- scored modules link to known evidence;
- dependency edges link to known evidence;
- risks link to evidence;
- assessed readiness criteria link to evidence and confidence;
- validation runs link to evidence;
- recommendations contain concrete action fields.

The resulting `integrity_coverage` measures structural traceability, not semantic truth.

## Layer 3 — Semantic audit evaluation

Real audit quality requires repositories where expected high-level conclusions are known or reviewed by a competent human.

Evaluate dimensions separately:

### Scope reconstruction

- Did the audit correctly identify the project's actual mission and core workflow?
- Were inferred requirements labeled as inferred?
- Did it avoid treating README claims as demonstrated behavior?

### Module decomposition

- Are module boundaries based on responsibility rather than only folders?
- Is the critical path plausible?
- Are legacy, experimental, optional, and dead areas distinguished correctly?

### Evidence calibration

- Are E0-E4 levels conservative?
- Are passing unit tests being over-promoted into end-to-end evidence?
- Are static imports kept at structural evidence rather than runtime proof?
- Are unknowns visible?

### Completion and quality calibration

- Does module completion reflect implementation, integration, validation, documentation, and operations separately?
- Does quality remain independent from completion?
- Do aggregate weights reflect user value and critical-path importance?

### Readiness calibration

- Are hard gates identified correctly?
- Are unavailable facts marked unknown rather than failed?
- Does insufficient evidence widen uncertainty or withhold a point estimate?
- Are research, ML, clinical, hardware, commercial, and production readiness kept distinct?

### Action usefulness

- Are the highest-leverage actions genuinely leverage points?
- Are STOP/DEFER recommendations present when appropriate?
- Does each major recommendation have a measurable definition of done?
- Would completing the recommendation materially change readiness, risk, or evidence quality?

### Commercial reasoning

- Are market claims separated from repository evidence?
- Are current external facts verified when tools are available?
- Is technical sophistication kept separate from customer value and willingness to pay?
- Are commercialization gaps explicit?

## Layer 4 — Adversarial benchmark projects

The evaluation corpus should intentionally include projects that tempt an auditor into incorrect conclusions:

- polished UI over mocked backend;
- many tests with weak assertions;
- large repository with little usable functionality;
- tiny repository with a complete narrow product;
- ML project with train/inference preprocessing drift;
- medical AI project with internal-only validation;
- project with excellent engineering but no product-market evidence;
- monorepo where folder names do not equal architectural boundaries;
- high commit velocity with declining quality;
- dormant project that is nevertheless technically complete.

These cases are more valuable than randomly sampling repositories because each targets a known failure mode.

## Layer 5 — Longitudinal consistency

For repeated audits of the same repository, verify that:

- unchanged evidence does not cause unexplained score jumps;
- methodology changes are recorded;
- a new test only increases the dimensions it actually supports;
- optional polish does not dominate critical-path progress;
- removed functionality can reduce completion;
- confidence can rise even when completion does not;
- scope changes are distinguished from implementation progress.

## Golden audit protocol

A real-world fixture can have a human-reviewed `golden.json` containing ranges or categorical expectations rather than exact percentages.

Prefer expectations such as:

- core module must be classified `critical_path`;
- production readiness must remain blocked while recovery is absent;
- commercial readiness must remain low-confidence without customer evidence;
- static dependency X -> Y must exist;
- finding Z must be surfaced;
- completion should fall within a broad reviewed range.

Avoid brittle goldens that assert an arbitrary exact percentage.

## Benchmark governance

When a real audit exposes a reproducible deterministic bug:

1. reduce it to the smallest safe fixture;
2. add an expectation that fails before the fix;
3. implement the fix;
4. keep the fixture permanently as a regression case;
5. document what the fixture does and does not prove.

When a semantic failure is discovered, add it to the human-reviewed challenge corpus instead of pretending a simple deterministic assertion can represent nuanced judgment.
