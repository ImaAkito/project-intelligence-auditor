# Project Intelligence Command Center — Dashboard Specification

The dashboard is an investigative interface for the audit, not a decorative report.

## Data contract

Use `.project-audit/audit.json` as the source of truth. Do not duplicate scores in UI constants.

When history exists, trajectory should be read from `history.trajectory`.

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
- deltas versus previous snapshots when available.

A readiness score should also expose its evidence coverage/state when structured readiness-gate data exists.

### Module Intelligence

Present modules by completion, quality, risk, criticality, confidence, and status.

Selecting a module should reveal:

- responsibility;
- dependencies and consumers;
- evidence;
- tests;
- technical debt;
- blockers;
- recommendations;
- score breakdown.

### Architecture / Dependency Map

Visualize module relationships and distinguish when data exists:

- critical path;
- unfinished nodes;
- bottlenecks;
- high-risk nodes;
- experimental/legacy/dead components;
- static dependency cycles;
- high fan-in/fan-out structural hotspots.

Static import edges must not be visually described as verified runtime integration.

### Readiness

For every structured readiness gate show:

- score when sufficiently evidenced;
- assessed score;
- evidence coverage;
- confidence;
- lower/upper score bounds;
- state;
- hard blockers;
- missing critical evidence;
- individual criteria on drill-down.

Do not render an unknown gate as `0%`.

### Development Directions

Show alternative product/research directions. For each direction display applicable fields such as:

- direction score;
- reuse percentage;
- development effort;
- commercial potential;
- risk;
- time to MVP;
- time to revenue;
- recommendation status.

### Roadmap / What Should I Do Now?

Support:

- NOW;
- NEXT;
- LATER;
- OPTIONAL;
- DEFER;
- REMOVE.

The immediate view should emphasize only the highest-leverage next actions, ideally 3–7. For each show:

- why now;
- impact;
- effort;
- dependencies;
- what it unlocks;
- definition of done;
- leverage score as a prioritization aid.

### Risk Matrix

Plot probability × impact. Selecting a risk should reveal evidence and mitigation.

### Trajectory

When multiple comparable snapshots exist, show:

- latest value;
- latest delta;
- approximate points per 30 days;
- direction;
- R-squared when available;
- historical series;
- descriptive ETA only when emitted by the trajectory tool;
- regressions.

Label trajectory as descriptive. Never make a trend line look like a committed delivery schedule.

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

### Evidence Explorer

Allow drill-down:

Project → System → Module → Component → Finding → Evidence.

Each important score should be explainable from this view.

## Perspective switching

When enough audit data exists, perspectives may include:

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
- charts that imply more precision than evidence supports;
- hardcoded numbers;
- inaccessible hover-only interactions.

## Confidence and uncertainty

Do not visually equate a score with certainty.

Examples:

```text
Completion 72%
Confidence 91%
```

or for readiness:

```text
MVP readiness 72%
Evidence coverage 78%
Possible range 61–84%
```

If a readiness point score is withheld because coverage is too low, show the interval/coverage instead of inventing a point estimate.

## History

When prior snapshots exist, surface:

- score deltas;
- regressions;
- closed/new risks;
- blocker changes;
- technical debt movement;
- module movement;
- methodology/version changes.

Do not treat positive completion delta as automatically healthy if quality or confidence fell.

## Validation

Before declaring the dashboard complete, run applicable build/lint/tests and inspect major views using browser automation when available. Check responsiveness, console errors, navigation, overflow, misleading visual encodings, and whether missing data is represented as unknown rather than zero.
