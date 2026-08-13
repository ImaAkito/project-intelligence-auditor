# AGENTS.md

## Repository mission

Project Intelligence Auditor is an evidence-driven Codex skill and deterministic support toolkit for understanding the real state of software, research, AI/ML, medical, hardware, and hybrid projects.

Changes to this repository must preserve the distinction between:

- completion;
- confirmed completion;
- quality;
- readiness;
- confidence;
- evidence strength;
- structural audit integrity;
- semantic calibration accuracy.

Do not collapse these concepts into one project score.

## Evidence rules

- Unknown is not zero.
- README/documentation claims alone are intent evidence unless corroborated.
- Static imports are structural/code-level evidence, not runtime integration proof.
- Heuristic scanner matches are candidates for review, not automatic defects.
- Passing tests support only the behavior actually exercised by those tests.
- Git activity is not project progress by itself.
- UI polish is not end-to-end completion.
- Internal ML/medical metrics do not automatically establish production or clinical readiness.
- Commercial claims require customer/market evidence rather than technical sophistication.

## Deterministic scoring

Do not hand-edit aggregate deterministic scores merely because they look surprising.

When a score appears wrong:

1. inspect the evidence;
2. inspect module boundaries and criticality;
3. inspect the input dimensions;
4. inspect gate definitions/weights;
5. change methodology only when the general rule is wrong;
6. add regression coverage for the corrected failure mode.

## Required validation for auditor changes

Run at minimum:

```bash
python scripts/validate_skill.py SKILL.md
python -m compileall scripts tests
pytest
python scripts/evaluate_benchmarks.py --manifest benchmarks/manifest.json --minimum-score 100
python scripts/validate_challenge_corpus.py --manifest challenges/manifest.json
python scripts/check_audit_integrity.py examples/example-audit.json --minimum-coverage 100
python scripts/evaluate_golden_audit.py examples/example-audit.json benchmarks/golden-example.json --minimum-score 100
python scripts/validate_audit.py examples/example-audit.json
python scripts/build_dashboard.py examples/example-audit.json -o /tmp/project-command-center.html
```

Use GitHub Actions as the final shared validation environment.

## Regression protocol

For a deterministic collector bug:

1. minimize the failing repository pattern;
2. add a fixture under `benchmarks/fixtures/`;
3. add a manifest expectation that fails before the fix;
4. fix the collector;
5. retain the fixture permanently.

For a semantic reasoning failure:

1. minimize the reasoning trap;
2. remove confidential/project-specific information;
3. add a fixture under `challenges/cases/<case>/fixture/`;
4. write a human-reviewed `golden.json` outside the fixture;
5. prefer ranges, relations, state sets, and semantic requirements over exact percentages;
6. mark decisive expectations `critical: true`;
7. run calibration blind so the auditor does not see the golden contract;
8. retain the case permanently after fixing the failure.

## Challenge integrity

Do not place `golden.json` inside a challenge `fixture/` directory.

The model being evaluated should receive the fixture repository and normal auditor instructions, not the answer contract.

Do not tune a fix only to one exact phrase in a golden file. Improve the underlying audit methodology so the conclusion generalizes.

## Safety

Do not add real credentials, private datasets, patient data, proprietary repository excerpts, or confidential user artifacts to benchmarks/challenges.

Reduce real-world failures to synthetic/minimized fixtures before committing them.

## Scope discipline

This repository is an auditor, not an automatic refactoring system. Changes should improve evidence collection, reasoning support, deterministic scoring, evaluation, reporting, or visualization.

Do not make audited projects mutate production data, deploy services, use production credentials, or perform destructive operations as part of an audit.

## Documentation

When adding a material capability:

- update the relevant reference file;
- update README status/capabilities when user-visible;
- update `SKILL.md` when the operating workflow changes;
- add or update tests;
- add deterministic or semantic regression coverage when applicable;
- bump the development version for a new development line.
