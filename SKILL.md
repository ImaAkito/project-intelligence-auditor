---
name: project-intelligence-auditor
description: Evidence-based technical, product, research, and commercial audit of a repository with deterministic scoring, risk and roadmap analysis, history tracking, and an interactive Project Command Center.
---

# Project Intelligence Auditor

Use this skill when the user wants to know the actual state of a project: what exists, what works, what is missing, how good the implementation is, how close it is to prototype/MVP/production/commercial readiness, which direction is strongest, and what work has the highest leverage.

The output is project intelligence, not a narrative code review.

## Core invariants

Keep these concepts separate:

- **Completion** — how much of the intended capability exists.
- **Confirmed completion** — how much completion is supported by strong evidence.
- **Quality** — how well the existing implementation is engineered.
- **Readiness** — whether the system satisfies the gates for a target state such as MVP or production.
- **Confidence** — how reliable the audit itself is.
- **Evidence strength** — how strongly a specific claim is supported.

Do not manufacture precision. Unknown values stay unknown. Missing evidence lowers confidence rather than silently becoming zero.

Do not infer readiness from code volume, commit count, number of files, UI polish, README claims, or a passing happy-path demo alone.

## Evidence model

Read `references/evidence-model.md` before scoring.

Use:

- **E0** — no evidence.
- **E1** — intent-only evidence: roadmap, issue, TODO, comment, design note, README claim.
- **E2** — implementation exists but behavior is not verified.
- **E3** — behavior is demonstrated by a reproducible test, execution, benchmark, trace, or validated output.
- **E4** — multiple independent strong sources corroborate the behavior.

README claims alone cannot exceed E1 unless corroborated.

Every material score or conclusion should be traceable to evidence IDs or explicit limitations.

## Audit perspectives

Apply all perspectives that are relevant:

- Engineering
- Architecture
- QA / Validation
- DevOps / SRE
- Security
- Product
- Commercial / Due Diligence
- Research
- AI / ML
- Medical / Healthcare
- Hardware / Embedded / Robotics

Do not force a domain perspective that does not apply.

## Execution workflow

### Phase 0 — Establish scope and safety

Read repository-level instructions such as `AGENTS.md` first.

Identify:

- repository root;
- current branch and commit when available;
- whether this is a monorepo;
- whether generated/vendor directories exist;
- whether the project can be executed safely;
- whether credentials, production services, hardware, paid APIs, or destructive migrations might be involved.

Do not expose secrets in reports. Do not use production credentials. Do not mutate production data. Do not publish or deploy unless the user separately requests it.

### Phase 1 — Run deterministic discovery

When Python is available, run the collector suite before deep model-assisted conclusions:

```bash
python scripts/run_collectors.py . -o .project-audit/discovery.json
```

This collects repository inventory, module candidates, dependency declarations, test signals, false-completion candidates, technical-debt candidates, and Git-history signals.

Collector results are **evidence candidates**, not automatic defects or final architectural truth.

If a collector fails, continue the audit using the remaining evidence and record the failure under limitations.

When starting a new audit snapshot, optionally bootstrap the JSON skeleton:

```bash
python scripts/bootstrap_audit.py .project-audit/discovery.json \
  -o .project-audit/audit.json
```

The bootstrap intentionally leaves scores null.

### Phase 2 — Recover project intent

Inspect source code and documentation, not only README.

Recover and distinguish:

- project mission;
- target users;
- primary problem;
- core user workflow;
- expected outputs;
- currently demonstrated outputs;
- inferred intended end state;
- declared MVP scope when present;
- inferred requirements needed for a coherent product.

Mark inferred requirements explicitly.

If official scope is ambiguous, do not pretend it is known. Record competing interpretations if they materially change the audit.

### Phase 3 — Build the actual system map

Model the project as:

Project → Subsystem → Module → Component.

Directory names are only discovery hints. Merge or split module candidates according to responsibility and dependency boundaries.

For each module record at least:

- id and name;
- responsibility;
- path(s);
- dependencies and consumers;
- classification;
- criticality;
- implementation;
- integration;
- validation;
- documentation;
- operational readiness;
- quality;
- confidence;
- evidence level;
- evidence IDs;
- risks;
- blockers.

Classify major modules as:

- `critical_path`
- `important`
- `optional`
- `experimental`
- `legacy`
- `dead`
- `unknown`

Build `dependency_edges` when dependencies can be established.

Identify the **critical path** for the primary user outcome. Missing critical-path capability must influence readiness more strongly than optional polish.

### Phase 4 — Detect false completion

Use deterministic signals from `scripts/detect_false_completion.py` and inspect the surrounding code before confirming a finding.

Look for semantic incompleteness such as:

- stubs and placeholders;
- mocked production paths;
- hardcoded success or outputs;
- UI without backend integration;
- API surfaces without meaningful behavior;
- tests that execute but assert nothing important;
- disabled validation or authentication;
- silent exception suppression;
- demo-only paths presented as product capability;
- unused implementations;
- TODOs hidden behind completed-looking UI;
- schema/migration drift;
- training/inference preprocessing drift;
- configuration options that are not wired into execution;
- documentation that describes removed or unfinished behavior.

A heuristic match is not itself a defect. Confirm context first.

### Phase 5 — Validate behavior safely

Run existing project checks when feasible:

- unit tests;
- integration tests;
- end-to-end tests;
- lint;
- formatting checks;
- type checking;
- builds;
- smoke tests;
- dependency/security audits already configured in the project;
- sample inference;
- benchmark scripts;
- reproducibility scripts.

Record each run in `validation_runs` with:

- command or action;
- status: `tested_pass`, `tested_fail`, `unable_to_test`, or `not_applicable`;
- relevant output summary;
- environment constraints;
- evidence IDs.

A passing build does not prove the product workflow works.

### Phase 6 — Audit architecture, debt, dependencies, and maintainability

Read:

- `references/architecture-audit.md`
- `references/security-audit.md`
- `references/readiness-gates.md`

Use `scripts/detect_technical_debt.py` as a signal collector.

Assess:

- boundaries and cohesion;
- coupling and cycles;
- state ownership;
- duplicate logic;
- god modules;
- single points of failure;
- hidden state;
- premature and missing abstractions;
- scalability bottlenecks;
- error handling;
- observability;
- configuration;
- dependency concentration;
- dependency/version drift;
- reproducibility;
- onboarding readiness;
- bus-factor signals;
- documentation drift.

Create a technical-debt register. Do not convert every TODO into debt automatically.

### Phase 7 — Apply domain-specific reviews

If AI/ML is material, read `references/ml-audit.md`.

If medical/healthcare is material, read `references/medical-audit.md`.

If hardware/embedded/robotics is material, read `references/hardware-audit.md`.

If the project is research-driven, read `references/research-audit.md`.

Keep domain readiness separate from general software completion.

Examples:

- working inference ≠ production ML readiness;
- good internal validation ≠ clinical readiness;
- a PCB layout ≠ manufacturable hardware;
- promising experiment ≠ publication readiness.

### Phase 8 — Score modules deterministically

Read `references/scoring-model.md`.

For every scored module, fill evidence-backed input dimensions before calculating aggregates:

- implementation;
- integration;
- validation;
- documentation;
- operational_readiness;
- quality;
- confidence;
- evidence_level;
- classification / criticality;
- dependency factor when justified;
- user-value factor when justified.

Then run:

```bash
python scripts/calculate_scores.py .project-audit/audit.json
```

Do not manually overwrite deterministic aggregate values merely to make them "look right." If the result is misleading, correct the underlying module inputs or scoring model assumptions and document why.

### Phase 9 — Evaluate readiness gates

Evaluate applicable states independently:

- Prototype Ready
- MVP Ready
- Commercial Ready
- Production Ready
- Scale Ready

Where relevant also evaluate:

- Research Readiness
- Publication Readiness
- ML Production Readiness
- Clinical Readiness
- Hardware Readiness
- System Integration Readiness
- Technology Readiness Level (TRL 1–9)

A readiness score should reflect gate satisfaction, not simply mirror completion.

For every target state list:

- satisfied gates;
- unsatisfied gates;
- unknown gates;
- blockers;
- required evidence.

### Phase 10 — Product and commercialization audit

Read:

- `references/product-audit.md`
- `references/commercialization-audit.md`

Distinguish:

Technology Readiness ≠ Product Readiness ≠ Market Readiness ≠ Commercial Readiness ≠ Operational Readiness.

Analyze:

- problem severity;
- target user and ICP clarity;
- value proposition;
- workflow fit;
- differentiation;
- technical moat;
- data moat;
- workflow moat;
- switching cost;
- deployment complexity;
- support burden;
- pricing hypotheses;
- cost structure;
- time to first revenue;
- regulatory/legal barriers;
- IP potential;
- scalability.

If current market facts, competitors, prices, regulations, or standards are needed and fresh external research is unavailable, mark those claims unverified rather than relying on stale memory.

Create explicit gap maps:

- Technology → Product
- Product → Commercial
- Commercial → Scale

### Phase 11 — Analyze alternative development directions

Do not assume the current trajectory is optimal.

Evaluate only plausible directions, for example:

- research tool;
- standalone application;
- SaaS;
- enterprise product;
- API;
- SDK;
- platform;
- open-source core + commercial layer;
- hardware product;
- medical device;
- data product;
- AI service;
- white-label;
- B2B / B2C / B2B2C.

For each serious direction record:

- technical fit;
- reuse of existing work;
- additional development;
- differentiation;
- defensibility;
- commercial complexity;
- time to MVP;
- time to revenue;
- risk;
- strategic value;
- direction score;
- major unknowns.

When useful, create contrasting scenarios such as fastest credible MVP, technically strongest product, and commercially strongest direction.

### Phase 12 — Adversarial project review

Ask:

- What could kill this project technically?
- What assumption is carrying the most unvalidated risk?
- What appears complete but is not?
- Which subsystem could invalidate the rest of the roadmap?
- What is being overengineered?
- What work should be stopped or deferred?
- What would an external CTO, reviewer, customer, investor, regulator, or acquirer challenge first?

Record concrete evidence and uncertainty.

### Phase 13 — Build the risk register

For each material risk use Probability 1–5 × Impact 1–5.

Cover applicable categories:

- technical;
- architecture;
- security;
- performance;
- data;
- ML;
- scientific;
- product;
- market;
- commercial;
- legal;
- regulatory;
- operational;
- team;
- vendor;
- supply chain.

Record mitigation and evidence.

### Phase 14 — Prioritize highest-leverage work

Recommendations should include when applicable:

- impact 0–100;
- effort;
- risk reduction 0–100;
- critical-path status;
- confidence;
- dependencies;
- unlocks;
- definition of done;
- evidence required for completion;
- rationale.

Then run:

```bash
python scripts/plan_actions.py .project-audit/audit.json
```

Use the result to create:

- NOW
- NEXT
- LATER
- OPTIONAL
- DEFER
- REMOVE

Identify top immediate actions, one highest-leverage action, best single two-week investment, and STOP DOING / DEFER items.

The deterministic leverage score is a prioritization aid, not a substitute for context.

### Phase 15 — Define the next version

Provide a concrete next-version scope with included work, excluded work, acceptance criteria, quality gates, and measurable completion conditions.

Avoid a roadmap made of dozens of equal-priority tasks.

### Phase 16 — Save and compare snapshots

Produce or update:

- `PROJECT_AUDIT.md`
- `PROJECT_ROADMAP.md`
- `PROJECT_COMMERCIALIZATION.md`
- `.project-audit/audit.json`
- `.project-audit/history/<timestamp>.json` when history is retained

If an older snapshot exists, run:

```bash
python scripts/compare_snapshots.py OLD.json NEW.json
```

Track completion delta, health delta, readiness deltas, module progress, new and closed risks, new and resolved blockers, technical-debt delta, and regressions.

Do not interpret velocity as positive merely because many files changed.

### Phase 17 — Validate the audit schema

Run:

```bash
python scripts/validate_audit.py .project-audit/audit.json
```

Resolve schema errors before presenting the audit.

### Phase 18 — Build the Project Command Center

Read `references/dashboard-spec.md`.

If the target project already has a suitable frontend stack, prefer integrating the dashboard there.

If it does not, or a self-contained artifact is preferable, use the built-in static dashboard generator:

```bash
python scripts/build_dashboard.py .project-audit/audit.json \
  -o .project-audit/PROJECT_COMMAND_CENTER.html
```

The dashboard must read structured audit data and expose evidence behind scores.

Required information architecture:

- Executive overview
- Module intelligence
- Architecture / dependency graph
- Risk matrix
- What Should I Do Now?
- Development directions
- Commercialization
- Evidence Explorer
- history/deltas when available

Use progressive disclosure:

Project → System → Module → Component → Finding → Evidence.

Do not hardcode scores separately from the audit JSON.

### Phase 19 — Validate the dashboard and artifacts

At minimum:

- confirm the audit JSON validates;
- confirm the dashboard is generated;
- inspect the resulting HTML or app build for obvious rendering issues;
- run existing lint/build/tests for any dashboard code you changed;
- use browser tooling when available to inspect navigation, responsiveness, console errors, and overflow.

Do not stop immediately after file generation.

## Required audit artifacts

The canonical machine-readable source is `.project-audit/audit.json`.

`PROJECT_AUDIT.md` should begin with a concise executive summary answering what the project is, where it is now, how complete it is, how strong the evidence is, what is working well, what is weak, what the main bottleneck is, what should happen next, and whether commercialization is plausible.

Detailed claims must remain traceable to evidence.

## Final response

Keep the final chat response compact. Report:

1. Project Completion.
2. Project Health.
3. MVP Readiness.
4. Production Readiness.
5. Commercial Readiness.
6. Confidence.
7. Main bottleneck.
8. Most promising direction.
9. Next three actions.
10. Audit/dashboard artifacts created or updated.
11. How to open or run the dashboard.
12. Important limitations that materially affect confidence.

Detailed analysis belongs in the audit artifacts.

## Safety and integrity

- Never reveal discovered secrets.
- Never claim a validation, benchmark, clinical result, customer fact, market fact, or external test that was not actually verified.
- Never silently convert unknown values into zero.
- Never count source volume as completion.
- Never count UI polish as workflow completion.
- Never count a test file as meaningful validation merely because it exists.
- Never upgrade README claims into implementation evidence without corroboration.
- Never treat heuristic scanner findings as proven defects without contextual review.
- Never perform broad refactoring of the audited product unless the user explicitly requests implementation work in addition to auditing.
