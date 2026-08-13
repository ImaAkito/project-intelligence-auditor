# Evidence Model

The auditor uses evidence levels to separate repository intent from demonstrated capability.

## Levels

| Level | Meaning | Typical evidence |
|---|---|---|
| E0 | No evidence | Missing implementation and no stated intent |
| E1 | Intent only | TODO, roadmap, issue, comment, README claim |
| E2 | Implemented but unverified | Code path exists, configuration exists, interface exists |
| E3 | Reproducibly demonstrated | Passing meaningful test, successful build, executed sample, benchmark, verified runtime result |
| E4 | Independently corroborated | Multiple strong sources such as unit + integration + benchmark + documented production use |

## Rules

1. README text alone cannot exceed E1.
2. A file existing does not prove the feature works.
3. A test file does not count as validation unless the test exercises meaningful behavior and contains meaningful assertions.
4. Generated screenshots or static demos do not prove backend integration.
5. A benchmark result must identify the code/config/data version it represents before it can be treated as strong evidence.
6. When evidence conflicts, record the conflict and lower confidence.
7. Unknown is not zero. Unknown values should remain null/unknown and lower confidence.

## Evidence record

Each important claim should be traceable to a record with fields similar to:

```json
{
  "id": "ev-001",
  "kind": "test_result",
  "level": "E3",
  "claim": "MRI preprocessing pipeline completes on bundled sample",
  "source": "tests/test_preprocessing.py",
  "location": "test_end_to_end_preprocessing",
  "status": "verified",
  "confidence": 0.94,
  "notes": "Executed locally during audit"
}
```

## Confidence guidance

Confidence should reflect evidence density, consistency, freshness, and scope.

Suggested interpretation:

- 0.90–1.00: strong evidence across the relevant scope;
- 0.75–0.89: good evidence with limited gaps;
- 0.55–0.74: mixed evidence or important unverified assumptions;
- 0.30–0.54: sparse evidence;
- below 0.30: estimate is mostly speculative and should be treated as provisional.

A precise score with low confidence is misleading. Prefer ranges or clearly labeled estimates when uncertainty is high.
