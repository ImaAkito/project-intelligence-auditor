# Scoring Model

The auditor keeps completion, quality, readiness, and confidence separate.

## Module completion

For each module, calculate normalized 0–100 sub-scores:

- implementation;
- integration;
- validation;
- documentation;
- operational_readiness.

Default weights:

```text
implementation          0.35
integration             0.25
validation              0.20
documentation           0.05
operational_readiness   0.15
```

Module Completion is the weighted mean of applicable dimensions. If a dimension is not applicable, renormalize the remaining weights. If a dimension is unknown, do not silently assign zero; preserve the unknown and lower confidence.

## Confirmed versus estimated completion

Confirmed Completion should only count evidence that reaches E3 or E4.

Estimated Completion may include E2 evidence but must be reported alongside confidence.

Suggested evidence multipliers for confirmed completion:

```text
E0 = 0.00
E1 = 0.10
E2 = 0.45
E3 = 0.85
E4 = 1.00
```

These multipliers are conservative by design.

## Module quality

Default quality dimensions:

- correctness: 0.18
- maintainability: 0.12
- architecture: 0.12
- test_quality: 0.12
- reliability: 0.10
- security: 0.08
- performance: 0.07
- observability: 0.06
- documentation: 0.05
- dependency_health: 0.04
- portability_reproducibility: 0.06

For domain-specific projects, add applicable dimensions and renormalize.

## Criticality

Criticality is 0–1 and should reflect:

- presence on the critical path;
- user value;
- dependency fan-out;
- failure impact;
- necessity for MVP.

Suggested base values:

```text
critical_path = 1.00
important     = 0.75
optional      = 0.35
experimental  = 0.20
legacy        = 0.15
dead          = 0.00
unknown       = 0.40
```

The auditor may adjust these values when evidence supports it.

## Project completion

Project completion is a criticality-weighted mean of module completion values.

A module weight may be computed as:

```text
weight = criticality × (0.45 + 0.25 × dependency_factor + 0.30 × user_value_factor)
```

where dependency_factor and user_value_factor are normalized to 0–1.

## Project health

Project Health is not completion. It should reflect the health of the engineering system.

Default dimensions:

- architecture: 0.13
- code_quality: 0.12
- testing: 0.13
- reliability: 0.10
- security: 0.09
- performance: 0.07
- maintainability: 0.10
- documentation: 0.06
- devops: 0.08
- observability: 0.06
- dependency_health: 0.06

Renormalize non-applicable dimensions.

## Readiness stages

Readiness scores should be independently calculated from stage-specific requirements rather than copied from completion.

Prototype Readiness emphasizes whether the core idea can be demonstrated.

MVP Readiness emphasizes whether the critical user workflow works end to end with acceptable reliability.

Commercial Readiness emphasizes target customer clarity, value proposition, supportability, legal/regulatory constraints, deployment, pricing hypotheses, and a credible route to first revenue.

Production Readiness emphasizes reliability, security, deployment, monitoring, failure handling, backups/recovery where applicable, reproducibility, and operational documentation.

Scale Readiness emphasizes architecture, performance, observability, automation, support burden, cost structure, and repeatability.

## Confidence

Project confidence is not simply the mean of module confidences. Critical-path uncertainty must weigh more heavily.

A suitable approximation is the criticality-weighted mean of module confidence, reduced by penalties for:

- untested critical-path modules;
- conflicting evidence;
- stale evidence;
- missing runtime access;
- inferred requirements that dominate the score.

## Score interpretation

Use score bands only as communication aids:

```text
90–100  strong
75–89   good but incomplete
60–74   material gaps
40–59   major gaps
20–39   weak readiness
0–19    mostly absent or unverified
```

Never imply that an 80 means “80% of all work hours are finished.” It is a structured readiness/completion estimate under the declared model.
