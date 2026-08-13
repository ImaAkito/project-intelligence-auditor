# Readiness Gates Reference

Readiness is not the same as completion. Evaluate every target state against explicit evidence-backed criteria.

Use criterion statuses:

- `pass`;
- `partial`;
- `fail`;
- `unknown`;
- `not_applicable`.

A criterion should include an ID, weight, confidence, whether it is critical, and evidence references.

## Structured gate format

Example:

```json
{
  "mvp": {
    "score_key": "mvp_readiness",
    "threshold": 75,
    "minimum_coverage": 0.7,
    "criteria": [
      {
        "id": "core-workflow",
        "title": "Core workflow is end-to-end",
        "status": "pass",
        "weight": 4,
        "confidence": 0.95,
        "critical": true,
        "evidence_ids": ["ev-core-integration"]
      },
      {
        "id": "failure-handling",
        "title": "Critical failure modes are handled",
        "status": "partial",
        "weight": 3,
        "confidence": 0.8,
        "critical": true,
        "evidence_ids": ["ev-failure-tests"]
      },
      {
        "id": "reproducible-setup",
        "status": "unknown",
        "weight": 2,
        "confidence": 0.0,
        "critical": false,
        "evidence_ids": []
      }
    ]
  }
}
```

Then run:

```bash
python scripts/score_readiness.py .project-audit/audit.json
```

## Deterministic scoring semantics

`score_readiness.py` separates four things:

- assessed score — weighted score over known criteria only;
- coverage — fraction of applicable criterion weight that is actually assessed;
- lower/upper bounds — explicit range produced by unresolved criteria;
- final gate score — emitted only when minimum coverage is reached.

Unknown criteria are not silently converted to zero. They widen the score interval and lower evidence coverage.

A failed critical criterion marks the gate `blocked` even if the numeric score is otherwise high.

A critical unknown marks the gate `critical_evidence_missing` once minimum coverage is sufficient.

## Prototype Ready

Typical criteria:

- primary technical hypothesis demonstrated;
- minimum end-to-end path executes;
- major assumptions are visible;
- output can be inspected;
- failure does not create unacceptable external impact.

A prototype may contain manual steps and weak operations.

## MVP Ready

Typical criteria:

- target user and problem are explicit;
- core workflow is end-to-end;
- critical-path components are integrated;
- basic failure handling exists;
- meaningful acceptance tests cover the core path;
- setup is reproducible enough for intended evaluators/users;
- no known critical blocker makes the main value proposition false.

MVP does not imply production robustness or market validation.

## Commercial Ready

Typical criteria:

- identifiable customer/ICP;
- value proposition tied to a real workflow;
- credible differentiation;
- deployment path understood;
- support burden understood;
- pricing/monetization hypothesis exists;
- legal/regulatory blockers identified;
- cost model is directionally understood;
- first-customer path is plausible.

Technical readiness alone cannot satisfy commercial readiness.

## Production Ready

Typical criteria:

- critical workflows are validated;
- error handling and rollback/recovery are adequate;
- observability exists;
- configuration and secrets are handled safely;
- security requirements are met for the context;
- data persistence/migrations are controlled when applicable;
- performance is measured against expected load;
- deployment is reproducible;
- operational ownership and failure response are understood;
- critical dependencies and infrastructure are supportable.

## Scale Ready

Typical criteria:

- measured scaling characteristics;
- bottlenecks identified and acceptable;
- capacity and cost model;
- operational automation;
- monitoring and alerting;
- multi-user/tenant/data isolation where required;
- backup/recovery or redundancy where required;
- support and deployment processes do not grow linearly with every customer.

## Research Ready

Typical criteria include a testable research question, valid experimental design, baseline, reproducibility, meaningful metrics, leakage/confounding controls, and uncertainty/error analysis.

## Publication Ready

Typical criteria include a scoped novelty claim, adequate baselines and ablations, reproducible results, appropriate statistical treatment, explicit limitations, evidence-matched conclusions, and regenerable figures/tables/results.

## ML Production Ready

Typical criteria include training/inference preprocessing consistency, versioned model artifacts, reproducible evaluation, representative validation, measured latency/resource requirements, monitoring/drift strategy, fallback/rollback behavior, and data/model lineage.

## Clinical Ready

Clinical readiness is context-dependent and must not be inferred from model accuracy alone. Potential criteria include intended use, clinically meaningful ground truth, patient-level splits, appropriate sensitivity/specificity and calibration, external validation, subgroup/domain-shift analysis, workflow integration, safety/error analysis, privacy/auditability, and an understood regulatory pathway.

## Hardware Ready

Potential criteria include schematic/PCB maturity, BOM/component availability, firmware, power/thermal considerations, mechanical integration, calibration, fault handling, prototype testing, manufacturability, and serviceability.
