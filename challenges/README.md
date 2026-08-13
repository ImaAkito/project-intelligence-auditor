# Semantic Challenge Corpus

This corpus is for calibrating the model-assisted parts of Project Intelligence Auditor against deliberately tricky repositories.

The deterministic benchmark suite under `benchmarks/` answers questions such as "did the parser recover this import edge?". The semantic challenge corpus asks harder questions such as:

- did the audit notice that a polished UI is still backed by demo behavior?
- did it detect a scientifically invalid ML split rather than reward a high metric?
- did it keep clinical readiness separate from internal model performance?
- did it distinguish a strong research prototype from a production-ready product?
- did it avoid inventing commercial readiness when customer evidence is absent?

Each case contains:

```text
challenges/cases/<case>/
  fixture/        # repository presented to the auditor
  golden.json     # human-reviewed semantic expectations
```

The golden files intentionally prefer broad score ranges, score relations, categorical readiness states, required findings, and evidence expectations. They should not encode arbitrary exact percentages.

## Validate the corpus

```bash
python scripts/validate_challenge_corpus.py
```

This checks corpus structure and whether every golden check type is understood by the evaluator. It does not claim semantic accuracy.

## Run a calibration experiment

For every case, run Project Intelligence Auditor against the case's `fixture/` directory and save the resulting canonical audit as:

```text
.project-audit/challenge-results/<case-id>.json
```

Then evaluate all available results:

```bash
python scripts/evaluate_challenge_corpus.py \
  .project-audit/challenge-results \
  --require-all \
  --minimum-score 80 \
  -o .project-audit/challenge-evaluation.json \
  --markdown .project-audit/challenge-evaluation.md
```

A case can fail even with a high weighted score when a `critical` semantic expectation fails. This is intentional: missing a major leakage or clinical-readiness issue should not be hidden by many minor correct observations.

## Interpretation

A challenge score measures agreement with the reviewed expectations in this corpus. It is calibration evidence, not a universal accuracy claim.

When a real audit exposes a reproducible reasoning failure, add a minimized challenge case and a reviewed golden contract. Over time this corpus should become the main regression suite for the auditor's semantic judgment.
