# Readiness Gates Reference

Readiness is not the same as completion. Evaluate each target state against explicit gates.

Use `pass`, `fail`, `unknown`, or `not_applicable` for each gate.

## Prototype Ready

Typical gates:

- primary technical hypothesis demonstrated;
- minimum end-to-end path executes;
- major assumptions are visible;
- output can be inspected;
- failure does not create unacceptable external impact.

A prototype may contain manual steps and weak operations.

## MVP Ready

Typical gates:

- target user and problem are explicit;
- core workflow is end-to-end;
- critical-path components are integrated;
- basic failure handling exists;
- meaningful acceptance tests cover the core path;
- setup is reproducible enough for intended evaluators/users;
- no known critical blocker makes the main value proposition false.

MVP does not imply production robustness or market validation.

## Commercial Ready

Typical gates:

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

Typical gates:

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

Typical gates:

- measured scaling characteristics;
- bottlenecks identified and acceptable;
- capacity and cost model;
- operational automation;
- monitoring and alerting;
- multi-user/tenant/data isolation where required;
- backup/recovery or redundancy where required;
- support and deployment processes do not grow linearly with every customer.

## Research Ready

Typical gates include a testable research question, valid experimental design, baseline, reproducibility, meaningful metrics, leakage/confounding controls, and uncertainty/error analysis.

## Publication Ready

Typical gates include a scoped novelty claim, adequate baselines and ablations, reproducible results, appropriate statistical treatment, explicit limitations, evidence-matched conclusions, and regenerable figures/tables/results.

## ML Production Ready

Typical gates include training/inference preprocessing consistency, versioned model artifacts, reproducible evaluation, representative validation, measured latency/resource requirements, monitoring/drift strategy, fallback/rollback behavior, and data/model lineage.

## Clinical Ready

Clinical readiness is context-dependent and must not be inferred from model accuracy alone. Potential gates include intended use, clinically meaningful ground truth, patient-level splits, appropriate sensitivity/specificity and calibration, external validation, subgroup/domain-shift analysis, workflow integration, safety/error analysis, privacy/auditability, and a understood regulatory pathway.

## Hardware Ready

Potential gates include schematic/PCB maturity, BOM/component availability, firmware, power/thermal considerations, mechanical integration, calibration, fault handling, prototype testing, manufacturability, and serviceability.

## Readiness scoring

Do not simply average unrelated gates if a failed gate is a hard blocker.

Classify gates as:

- hard gate;
- important gate;
- supporting gate.

A failed hard gate should cap readiness for that target state until resolved. Document any cap explicitly.
