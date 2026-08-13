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

Read `references/semantic-calibration.md` and use the challenge corpus under `challenges/`.

Evaluate dimensions separately.

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

## Layer 4 — Adversarial semantic challenge projects

Use `challenges/manifest.json` as the corpus index.

The corpus should intentionally contain projects that tempt the auditor into incorrect conclusions. Current v0.5 challenge families include:

- polished UI over demo/hardcoded backend behavior;
- ML evaluation with preprocessing leakage and patient-level split errors;
- medical AI with strong internal metrics but missing external/clinical validation;
- reproducible research artifact without production operations;
- technically competent developer tooling without customer/commercial evidence.

Validate corpus structure:

```bash
python scripts/validate_challenge_corpus.py
```

After independently running the auditor on every fixture and saving `<case-id>.json` outputs, evaluate:

```bash
python scripts/evaluate_challenge_corpus.py \
  .project-audit/challenge-results \
  --require-all \
  --minimum-score 80
```

The challenge evaluator supports broad numeric ranges, score relations, readiness-state sets, semantic text requirements, commercialization-field state checks, and critical checks.

A critical semantic failure must remain visible even when the weighted score is high.

Do not interpret the aggregate challenge score as universal audit accuracy.

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

A real-world fixture can have a human-reviewed `golden.json` containing ranges, relations, semantic requirements, or categorical expectations rather than exact percentages.

Prefer expectations such as:

- core module must be classified `critical_path`;
- production readiness must remain blocked while recovery is absent;
- research readiness should materially exceed production readiness for a research-only artifact;
- commercial readiness must remain low-confidence without customer evidence;
- a leakage or external-validation risk must be surfaced;
- completion should fall within a broad reviewed range.

Use `critical: true` for conclusions whose omission materially invalidates the audit. Critical failures are counted separately from the weighted score.

Avoid brittle goldens that assert an arbitrary exact percentage or require one preferred wording when several correct descriptions are possible.

## Benchmark governance

When a real audit exposes a reproducible deterministic bug:

1. reduce it to the smallest safe fixture;
2. add an expectation that fails before the fix;
3. implement the fix;
4. keep the fixture permanently as a regression case;
5. document what the fixture does and does not prove.

When a semantic failure is discovered:

1. isolate the reasoning trap;
2. remove confidential/project-specific details;
3. create a minimized challenge fixture;
4. write a reviewed golden contract using ranges/categories/relations;
5. mark truly decisive expectations as critical;
6. demonstrate the failure before changing the auditor;
7. improve instructions, tools, scoring, or references;
8. keep the challenge permanently.

This turns real audit mistakes into a growing semantic regression corpus instead of relying on anecdotal confidence.
