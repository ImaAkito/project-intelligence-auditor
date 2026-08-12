# Project Command Center — Dashboard Specification

The dashboard is an investigative interface for the audit, not a decorative report.

## Data contract

Use `.project-audit/audit.json` as the source of truth. Do not duplicate scores in UI constants.

## Required views

### Executive Overview
Show:

- Project Completion;
- Confirmed Completion;
- Project Health;
- MVP Readiness;
- Production Readiness;
- Commercial Readiness;
- Confidence;
- current stage;
- TRL when applicable;
- critical blockers;
- top recommended action;
- deltas versus the previous snapshot.

Every score should expose its evidence and uncertainty.

### Module Intelligence
Present modules by completion, quality, risk, criticality, confidence, and status.

Selecting a module should reveal:

- responsibility;
- dependencies;
- evidence;
- tests;
- technical debt;
- blockers;
- recommendations;
- score breakdown.

### Architecture / Dependency Map
Visualize module relationships and distinguish:

- critical path;
- unfinished nodes;
- bottlenecks;
- high-risk nodes;
- experimental/legacy/dead components.

### Development Directions
Show alternative product/research directions as a branching strategy map. For each direction display:

- direction score;
- reuse percentage;
- development effort;
- commercial potential;
- risk;
- time to MVP;
- recommendation status.

### Roadmap
Support stage filters such as:

- MVP;
- Production;
- Commercial;
- Scale;
- Research.

Use NOW / NEXT / LATER / OPTIONAL / DEFER / REMOVE.

### Risk Matrix
Plot probability × impact. Selecting a risk should reveal evidence and mitigation.

### Commercialization
Display:

- target users / ICP;
- value proposition;
- differentiation;
- moat hypotheses;
- monetization hypotheses;
- commercial blockers;
- route to first revenue;
- Technology → Product → Commercial → Scale gaps.

### What Should I Do Now?
Display only the highest-leverage next actions, ideally 3–7. For each show:

- why now;
- impact;
- effort;
- dependencies;
- what it unlocks;
- definition of done.

### Evidence Explorer
Allow drill-down:

Project → System → Module → Component → Finding → Evidence.

Each important score must be explainable from this view.

## Perspective switching

When enough audit data exists, allow the user to switch among:

- Engineering;
- Product;
- Research;
- Commercial;
- Investor / Due Diligence.

Perspective switching changes emphasis, not underlying facts.

## Visual design

The interface should feel like a project command center, not a generic admin template.

Prefer:

- strong hierarchy;
- compact but readable data density;
- progressive disclosure;
- restrained motion;
- meaningful transitions;
- keyboard-accessible controls;
- responsive layouts;
- dark mode when compatible with the host project.

Avoid:

- gratuitous gradient cards;
- excessive progress rings;
- animation without information value;
- charts that imply more precision than the audit supports;
- hardcoded numbers;
- inaccessible hover-only interactions.

## Confidence representation

Do not visually equate a score with certainty.

Examples:

```text
Completion 72%
Confidence 91%
```

or, when uncertainty is substantial:

```text
Estimated completion 72 ± 8%
```

## History

When prior snapshots exist, surface:

- score deltas;
- regressions;
- closed/new risks;
- blocker changes;
- technical debt movement;
- module velocity.

Do not treat a positive completion delta as automatically healthy if quality or confidence fell.

## Validation

Before declaring the dashboard complete, run applicable build/lint/tests and inspect major views using browser automation when available. Check responsiveness, console errors, navigation, overflow, and misleading visual encodings.
