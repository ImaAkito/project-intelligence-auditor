# Project Intelligence Auditor

## Purpose

Perform a repository-wide, evidence-based audit of a software, AI/ML, research, medical, hardware, embedded, robotics, or hybrid project. Produce objective project intelligence rather than a narrative code review.

The audit must distinguish:

- completion;
- quality;
- readiness;
- confidence;
- evidence strength.

Never invent precision. If evidence is weak, lower confidence or mark the metric unknown.

## Operating modes

Use all applicable modes:

- Engineering
- Architecture
- QA / Validation
- DevOps / SRE
- Security
- Product
- Commercial / Due Diligence
- Research
- AI / ML
- Medical
- Hardware / Embedded / Robotics

## Required workflow

### 1. Discover project intent

Inspect repository structure, README files, AGENTS.md, manifests, configuration, CI/CD, source code, tests, examples, notebooks, scripts, deployment files, TODO/FIXME/HACK markers, mocks, stubs, feature flags, disabled code, generated outputs, and Git history when available.

Recover:

- project mission;
- target users;
- core workflow;
- expected output;
- current demonstrated output;
- inferred intended end state.

Mark inferred requirements explicitly.

### 2. Build the system map

Model the repository as:

Project → Subsystem → Module → Component.

Do not equate directory boundaries with architectural boundaries.

For every module record:

- responsibility;
- dependencies;
- consumers;
- criticality;
- implementation state;
- validation state;
- quality;
- risks;
- blockers;
- evidence references.

Classify every major element as one of:

- critical_path;
- important;
- optional;
- experimental;
- legacy;
- dead;
- unknown.

### 3. Collect evidence

Use the evidence model in `references/evidence-model.md`.

Evidence levels:

- E0: no evidence;
- E1: intent-only evidence such as TODO, roadmap, comment, issue;
- E2: implementation exists but is unverified;
- E3: implementation is demonstrated by a reproducible execution, test, benchmark, or verified result;
- E4: implementation is independently corroborated by multiple strong sources.

README claims alone cannot exceed E1 unless corroborated.

### 4. Detect false completion

Search for:

- stubs;
- mocks;
- placeholder returns;
- hardcoded success states;
- empty tests;
- tests without meaningful assertions;
- disabled validation;
- silent exception suppression;
- demo-only code paths;
- frontend without backend integration;
- API surface without functional implementation;
- unused alternative implementations;
- TODOs hidden behind completed-looking UI;
- training/inference preprocessing drift;
- schema or migration drift.

Use `scripts/detect_false_completion.py` as an objective signal collector. Treat its output as evidence candidates, not final truth.

### 5. Validate safely

When feasible, run existing project checks:

- tests;
- lint;
- formatting checks;
- type checking;
- builds;
- dependency audits;
- smoke tests;
- sample inference;
- benchmark scripts.

Do not run destructive operations, mutate production data, publish artifacts, expose secrets, or use production credentials.

For each validation classify the result as:

- tested_pass;
- tested_fail;
- unable_to_test;
- not_applicable.

### 6. Score modules

Use the deterministic scoring model in `references/scoring-model.md` and `scripts/calculate_scores.py`.

Never let an LLM directly invent the final aggregate score.

For each module produce at least:

- implementation;
- integration;
- validation;
- documentation;
- operational_readiness;
- completion;
- quality;
- criticality;
- confidence;
- evidence_level.

### 7. Score the project

Produce at least:

- confirmed_completion;
- estimated_completion;
- project_health;
- prototype_readiness;
- mvp_readiness;
- commercial_readiness;
- production_readiness;
- scale_readiness;
- confidence.

Where applicable also produce:

- research_readiness;
- publication_readiness;
- ml_production_readiness;
- clinical_readiness;
- hardware_readiness;
- system_integration_readiness;
- TRL 1–9.

### 8. Audit architecture and technical debt

Identify:

- bottlenecks;
- cyclic dependencies;
- excessive coupling;
- god modules;
- hidden state;
- duplicate logic;
- weak boundaries;
- single points of failure;
- premature abstractions;
- missing abstractions;
- scalability limits;
- dependency concentration;
- documentation drift;
- reproducibility gaps;
- onboarding risk.

Create a technical debt register with severity, impact, effort, dependencies, and timing.

### 9. Audit risks

Create a risk register using:

Probability 1–5 × Impact 1–5.

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

### 10. Analyze product directions

Do not assume a single future trajectory.

Evaluate applicable directions such as:

- research tool;
- standalone application;
- SaaS;
- API;
- SDK;
- enterprise product;
- platform;
- open-source core + commercial layer;
- hardware product;
- medical device;
- data product;
- AI service;
- white-label;
- B2B;
- B2C;
- B2B2C.

For every serious direction estimate:

- technical fit;
- reuse of current work;
- additional development;
- differentiation;
- defensibility;
- commercial complexity;
- risk;
- time to MVP;
- time to revenue;
- strategic value.

### 11. Commercial audit

Use `references/commercialization-audit.md`.

Distinguish:

Technology Readiness ≠ Product Readiness ≠ Market Readiness ≠ Commercial Readiness ≠ Operational Readiness.

Analyze:

- problem severity;
- ICP clarity;
- value proposition;
- differentiation;
- technical/data/workflow moat;
- deployment complexity;
- support burden;
- pricing hypotheses;
- cost structure;
- market accessibility;
- regulatory barriers;
- IP potential;
- time to revenue;
- scalability.

Create explicit gap lists:

- Technology → Product;
- Product → Commercial;
- Commercial → Scale.

### 12. Domain-specific audit

If AI/ML is present, read `references/ml-audit.md`.

If medical/healthcare is present, read `references/medical-audit.md`.

If hardware/embedded/robotics is present, read `references/hardware-audit.md`.

If research is present, assess experimental validity, reproducibility, baselines, ablation, external validation, statistical design, novelty, and publication readiness.

### 13. Prioritize work

Build a roadmap using:

- NOW;
- NEXT;
- LATER;
- OPTIONAL;
- DEFER;
- REMOVE.

For each action include:

- priority;
- impact;
- effort;
- risk reduction;
- dependencies;
- unlocks;
- definition of done;
- evidence required for completion.

Identify:

- top 5 highest-leverage actions;
- current project bottleneck;
- best single two-week investment;
- STOP DOING / DEFER items.

### 14. Define the next version

Provide a concrete next-version scope with:

- included work;
- excluded work;
- acceptance criteria;
- quality gates;
- measurable completion conditions.

### 15. Produce audit artifacts

Create or update:

- `PROJECT_AUDIT.md`;
- `PROJECT_ROADMAP.md`;
- `PROJECT_COMMERCIALIZATION.md`;
- `.project-audit/audit.json`;
- `.project-audit/history/<timestamp>.json` when history is retained.

Validate the JSON against `schema/audit.schema.json` or the project-adapted equivalent.

### 16. Compare with history

If prior snapshots exist, calculate:

- completion delta;
- health delta;
- readiness deltas;
- closed risks;
- new risks;
- resolved blockers;
- new blockers;
- module progress;
- regressions;
- technical debt delta.

Use `scripts/compare_snapshots.py`.

### 17. Build or update the Project Command Center

Follow `references/dashboard-spec.md`.

Prefer the target project's existing frontend stack. Do not add another frontend framework without a strong reason.

The dashboard must read structured audit data rather than duplicate hardcoded scores.

Required views:

- Executive overview;
- Module intelligence;
- Architecture / dependency map;
- Development directions;
- Roadmap;
- Risk matrix;
- Commercialization;
- What Should I Do Now?;
- Evidence Explorer;
- historical changes when snapshots exist.

Use progressive disclosure:

Project → System → Module → Component → Finding → Evidence.

### 18. Validate the dashboard

Run applicable build/lint/tests and, if browser tooling is available, inspect the rendered UI for:

- broken navigation;
- console errors;
- overflow;
- poor responsive behavior;
- inaccessible controls;
- unreadable hierarchy;
- misleading data representations.

Do not stop immediately after generating files.

## Final response format

Keep the final chat response short. Report:

1. Project Completion.
2. Project Health.
3. MVP Readiness.
4. Production Readiness.
5. Commercial Readiness.
6. Confidence.
7. Main bottleneck.
8. Most promising direction.
9. Next three actions.
10. Audit/dashboard files created or updated.
11. How to run the dashboard.

Detailed reasoning belongs in the generated artifacts, not the final chat message.

## Safety and integrity constraints

- Never expose discovered secrets in reports.
- Never claim external validation that was not performed.
- Never silently convert unknown values into zeros.
- Never count code volume as completion.
- Never count a UI mock as a working workflow.
- Never count a test file as validation unless the tests are meaningful.
- Never upgrade a README claim into implementation evidence without corroboration.
- Never perform broad product refactoring during an audit unless explicitly requested.
