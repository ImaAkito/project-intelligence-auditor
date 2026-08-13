---
name: project-intelligence-auditor
description: Evidence-based repository audit for technical, product, research, commercial, and readiness intelligence with deterministic scoring, history analysis, and an interactive Project Command Center.
---

# Project Intelligence Auditor

Use this skill when the user wants the actual state of a project: what exists, what works, what is missing, how good the implementation is, how close it is to prototype/MVP/production/commercial readiness, which development direction is strongest, and what work has the highest leverage.

The output is **project intelligence**, not a narrative code review.

## Core invariants

Keep these concepts separate:

- **Completion** — how much of the intended capability exists.
- **Confirmed completion** — how much completion is supported by strong evidence.
- **Quality** — how well the existing implementation is engineered.
- **Readiness** — whether explicit gates for a target state are satisfied.
- **Confidence** — how reliable the audit itself is.
- **Evidence strength** — how strongly a specific claim is supported.

Unknown evidence stays unknown. Do not manufacture precision.

Do not infer readiness from code volume, commit count, file count, UI polish, README claims, or one passing happy-path demo.

Aggregate scores must come from deterministic tooling after evidence-backed inputs have been filled. If the deterministic result looks wrong, inspect the evidence, weights, module boundaries, or assumptions instead of hand-editing the aggregate to a preferred number.

## Evidence model

Read `references/evidence-model.md` before scoring.

Use:

- **E0** — no evidence.
- **E1** — intent-only evidence: roadmap, issue, TODO, comment, design note, README claim.
- **E2** — implementation or structural evidence exists, but behavior is not verified.
- **E3** — behavior is demonstrated by reproducible execution, test, benchmark, trace, or validated output.
- **E4** — multiple independent strong sources corroborate the behavior.

README claims alone cannot exceed E1 unless corroborated.

Static internal imports normally support E2 dependency evidence. They do not prove successful runtime integration.

Every material score or conclusion should be traceable to evidence IDs or explicit limitations.

## Audit perspectives

Apply only the perspectives that materially fit the project:

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

## Required execution workflow

### Phase 0 — Establish scope and safety

Read repository instructions such as `AGENTS.md` first.

Identify:

- repository root;
- branch/commit when available;
- monorepo boundaries;
- generated/vendor directories;
- safe execution constraints;
- credentials, production services, hardware, paid APIs, destructive migrations, or external side effects.

Never expose secrets. Do not use production credentials or mutate production data. Do not deploy or publish unless separately requested.

### Phase 1 — Run deterministic discovery

When Python is available, begin with:

```bash
python scripts/run_collectors.py . -o .project-audit/discovery.json
```

The suite collects:

- repository inventory;
- module candidates;
- static architecture/dependency edges;
- dependency declarations;
- test signals;
- false-completion candidates;
- technical-debt candidates;
- Git-history signals.

Collector outputs are evidence candidates, not final defects or architectural truth.

If one collector fails, continue with the others and record the limitation.

Bootstrap the canonical audit skeleton:

```bash
python scripts/bootstrap_audit.py .project-audit/discovery.json \
  -o .project-audit/audit.json
```

The bootstrap intentionally leaves semantic scores null. It may populate static dependency edges and E2 dependency evidence.

### Phase 2 — Recover project intent

Inspect code and documentation, not only README.

Recover and distinguish:

- mission;
- target users;
- primary problem;
- core user workflow;
- expected outputs;
- demonstrated outputs;
- intended end state;
- declared MVP scope;
- inferred requirements needed for a coherent product.

Mark inferred requirements explicitly.

If scope is ambiguous and different interpretations change the score materially, record competing scope interpretations rather than pretending one is authoritative.

### Phase 3 — Build the actual system map

Read:

- `references/architecture-audit.md`
- `references/architecture-inference.md`

Model:

Project → Subsystem → Module → Component.

Directory names and deterministic module candidates are starting hints. Merge, split, or rename them based on responsibility and actual dependency boundaries.

For every material module record:

- id/name;
- responsibility;
- paths;
- dependencies;
- consumers;
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
- risks and blockers.

Classifications:

- `critical_path`
- `important`
- `optional`
- `experimental`
- `legacy`
- `dead`
- `unknown`

Identify the **critical path** for the primary user outcome.

Missing critical-path capability must influence project readiness more strongly than optional polish.

Review static cycles and hotspots from `architecture_analysis`. Do not call them defects based on graph degree alone.

### Phase 4 — Detect false completion

Use `scripts/detect_false_completion.py` and inspect surrounding context before confirming findings.

Look for semantic incompleteness:

- stubs/placeholders;
- mocked production paths;
- hardcoded success or outputs;
- UI without backend integration;
- API surfaces without meaningful behavior;
- tests that execute but assert nothing material;
- disabled validation/authentication;
- silent exception suppression;
- demo-only paths presented as product capability;
- unused implementations;
- TODOs hidden behind completed-looking UI;
- schema/migration drift;
- training/inference preprocessing drift;
- configuration options not wired into execution;
- docs describing removed or unfinished behavior.

A heuristic match is not itself a defect.

### Phase 5 — Validate behavior safely

Run existing checks when feasible:

- unit/integration/e2e tests;
- lint/format/type checks;
- builds;
- smoke tests;
- configured security/dependency audits;
- sample inference;
- benchmarks;
- reproducibility scripts.

Record each run in `validation_runs` with:

- action/command;
- `tested_pass`, `tested_fail`, `unable_to_test`, or `not_applicable`;
- summary;
- environment constraints;
- evidence IDs.

A passing build is not proof the product workflow works.

### Phase 6 — Audit architecture, debt, security, dependencies, and maintainability

Read:

- `references/architecture-audit.md`
- `references/security-audit.md`
- `references/readiness-gates.md`

Use deterministic collectors as signals, then inspect context.

Assess:

- boundaries/cohesion;
- coupling/cycles;
- state ownership;
- duplicate logic;
- god modules;
- single points of failure;
- hidden state;
- premature/missing abstractions;
- scalability bottlenecks;
- error handling;
- observability;
- configuration;
- dependency concentration/version drift;
- reproducibility;
- onboarding readiness;
- bus-factor signals;
- documentation drift.

Create a technical-debt register with severity, impact, effort, timing, dependencies, and evidence.

### Phase 7 — Apply domain-specific reviews

If AI/ML is material, read `references/ml-audit.md`.

If medical/healthcare is material, read `references/medical-audit.md`.

If hardware/embedded/robotics is material, read `references/hardware-audit.md`.

If research-driven, read `references/research-audit.md`.

Keep domain readiness separate from general software completion.

Examples:

- working inference ≠ production ML readiness;
- strong internal metrics ≠ clinical readiness;
- PCB layout ≠ manufacturable hardware;
- promising experiment ≠ publication readiness.

### Phase 8 — Score modules deterministically

Read `references/scoring-model.md`.

Fill evidence-backed module inputs first:

- implementation;
- integration;
- validation;
- documentation;
- operational_readiness;
- quality;
- confidence;
- evidence_level;
- classification/criticality;
- dependency factor when justified;
- user-value factor when justified.

Then run:

```bash
python scripts/calculate_scores.py .project-audit/audit.json
```

Do not manually replace deterministic aggregate values to make them look plausible.

### Phase 9 — Evaluate readiness gates explicitly

Read `references/readiness-gates.md`.

Evaluate applicable states independently:

- Prototype Ready
- MVP Ready
- Commercial Ready
- Production Ready
- Scale Ready

When relevant also evaluate:

- Research Readiness
- Publication Readiness
- ML Production Readiness
- Clinical Readiness
- Hardware Readiness
- System Integration Readiness
- TRL 1–9

For each readiness state, create structured criteria under `readiness_gates` with:

- id/title;
- `pass`, `partial`, `fail`, `unknown`, or `not_applicable`;
- weight;
- confidence;
- critical flag;
- evidence IDs;
- reason when useful.

Then run:

```bash
python scripts/score_readiness.py .project-audit/audit.json
```

The deterministic evaluator reports:

- assessed score;
- evidence coverage;
- lower/upper score bounds;
- final score only when minimum coverage is reached;
- hard blockers;
- missing critical evidence;
- readiness state.

Unknown criteria widen uncertainty instead of silently becoming zero.

### Phase 10 — Product and commercialization audit

Read:

- `references/product-audit.md`
- `references/commercialization-audit.md`

Distinguish:

Technology Readiness ≠ Product Readiness ≠ Market Readiness ≠ Commercial Readiness ≠ Operational Readiness.

Analyze:

- problem severity;
- target user/ICP clarity;
- value proposition/workflow fit;
- differentiation;
- technical/data/workflow moat;
- switching cost;
- deployment complexity;
- support burden;
- pricing hypotheses;
- cost structure;
- time to first revenue;
- regulatory/legal barriers;
- IP potential;
- scalability.

If current market facts, competitors, prices, regulations, standards, or customer facts require fresh external research and such research is unavailable, mark them unverified.

Create gap maps:

- Technology → Product
- Product → Commercial
- Commercial → Scale

### Phase 11 — Analyze alternative development directions

Do not assume the current trajectory is optimal.

Evaluate only plausible directions, such as:

- research tool;
- standalone application;
- SaaS;
- enterprise product;
- API/SDK;
- platform;
- open-source core + commercial layer;
- hardware product;
- medical device;
- data product;
- AI service;
- white-label;
- B2B/B2C/B2B2C.

For each serious direction record:

- technical fit;
- reuse of existing work;
- additional development;
- differentiation/defensibility;
- commercial complexity;
- time to MVP;
- time to revenue;
- risk;
- strategic value;
- direction score;
- major unknowns.

When useful, contrast fastest credible MVP, technically strongest product, and commercially strongest direction.

### Phase 12 — Adversarial project review

Ask:

- What could kill this project technically?
- Which assumption carries the most unvalidated risk?
- What appears complete but is not?
- Which subsystem could invalidate the roadmap?
- What is overengineered?
- What should be stopped or deferred?
- What would an external CTO, reviewer, customer, investor, regulator, or acquirer challenge first?

Tie answers to evidence and uncertainty.

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

Recommendations should contain when applicable:

- impact 0–100;
- effort;
- risk reduction 0–100;
- critical-path status;
- confidence;
- dependencies;
- unlocks;
- definition of done;
- evidence required;
- rationale.

Run:

```bash
python scripts/plan_actions.py .project-audit/audit.json
```

Use the result to form:

- NOW
- NEXT
- LATER
- OPTIONAL
- DEFER
- REMOVE

Identify:

- highest-leverage immediate actions;
- one best single two-week investment;
- STOP DOING / DEFER work.

The leverage score is a prioritization aid, not a replacement for context.

### Phase 15 — Define the next version

Define concrete scope with:

- included work;
- excluded work;
- acceptance criteria;
- quality gates;
- measurable completion conditions.

Avoid dozens of equal-priority roadmap items.

### Phase 16 — Save immutable snapshots and compare history

Produce/update:

- `PROJECT_AUDIT.md`
- `PROJECT_ROADMAP.md`
- `PROJECT_COMMERCIALIZATION.md`
- `.project-audit/audit.json`
- `.project-audit/history/<timestamp>.json`

When a prior comparable snapshot exists, run:

```bash
python scripts/compare_snapshots.py OLD.json NEW.json
```

Compare:

- score deltas;
- module changes;
- readiness state/coverage/confidence changes;
- opened/closed risks;
- new/resolved technical debt;
- new/resolved bottlenecks;
- regressions;
- scope changes;
- audit methodology version.

If audit versions differ, do not automatically interpret score delta as project progress.

### Phase 17 — Analyze trajectory when enough history exists

Read `references/trajectory-analysis.md`.

With at least three comparable snapshots, run:

```bash
python scripts/forecast_trajectory.py \
  --history-dir .project-audit/history \
  --update-audit .project-audit/audit.json
```

Trajectory is descriptive, not a delivery schedule.

Only surface an ETA when the tool emits one. Do not fabricate an ETA from two snapshots or weak/noisy trend data.

### Phase 18 — Validate the audit schema

Run:

```bash
python scripts/validate_audit.py .project-audit/audit.json
```

Resolve schema errors before presentation.

### Phase 19 — Build the Project Intelligence Command Center

Read `references/dashboard-spec.md`.

Prefer the audited project's existing frontend stack when appropriate. Otherwise build the standalone dashboard:

```bash
python scripts/build_dashboard.py .project-audit/audit.json \
  -o .project-audit/PROJECT_COMMAND_CENTER.html
```

The standalone dashboard exposes:

- Executive overview
- Module intelligence
- Architecture/dependency graph
- Static cycles/hotspots
- Readiness gates and uncertainty intervals
- Risk matrix
- What Should I Do Now?
- Project trajectory when history exists
- Development directions
- Commercialization
- Evidence Explorer

Use progressive disclosure:

Project → System → Module → Component → Finding → Evidence.

Do not hardcode audit scores separately from `audit.json`.

### Phase 20 — Validate artifacts

At minimum:

- audit JSON validates;
- dashboard generates;
- changed audit tooling compiles;
- auditor tests pass when available;
- dashboard output is inspected for obvious rendering defects;
- browser tooling is used when available for navigation, responsiveness, console errors, and overflow.

Do not stop immediately after file generation.

## Required artifacts

The canonical machine-readable source is `.project-audit/audit.json`.

`PROJECT_AUDIT.md` should begin with a concise executive summary covering:

- what the project is;
- where it is now;
- completion and evidence confidence;
- strongest parts;
- weakest parts;
- main bottleneck;
- highest-leverage next action;
- commercialization plausibility;
- material limitations.

Detailed claims remain traceable to evidence.

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
11. How to open/run the dashboard.
12. Important limitations that materially affect confidence.

Detailed analysis belongs in generated artifacts.

## Safety and integrity

- Never reveal discovered secrets.
- Never claim a validation, benchmark, clinical result, customer fact, market fact, or external test that was not actually verified.
- Never silently convert unknown values into zero.
- Never count source volume as completion.
- Never count UI polish as workflow completion.
- Never count a test file as meaningful validation merely because it exists.
- Never upgrade README claims into implementation evidence without corroboration.
- Never treat heuristic scanner findings as proven defects without contextual review.
- Never treat static import structure as verified runtime integration.
- Never present descriptive trajectory as a delivery commitment.
- Never perform broad refactoring of the audited product unless the user explicitly asks for implementation work in addition to auditing.
