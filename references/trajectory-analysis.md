# Trajectory Analysis Reference

Trajectory analysis compares audit snapshots over time. It is intended to answer whether project state is improving, stagnating, regressing, or changing in scope.

## Preconditions

Before comparing snapshots, check:

- audit methodology/version;
- project scope;
- scoring weights;
- module boundaries;
- evidence policy;
- target definition.

A score delta after a methodology change is not automatically a project delta.

## Two-snapshot comparison

Use `scripts/compare_snapshots.py` for direct change detection:

- project score deltas;
- module additions/removals and score deltas;
- readiness gate state/coverage/confidence changes;
- opened/closed risks;
- new/resolved technical debt;
- new/resolved bottlenecks;
- regressions;
- methodology-change warning.

## Three or more snapshots

Use `scripts/forecast_trajectory.py` for descriptive trend estimation.

The current implementation uses simple linear regression over snapshot timestamps. It reports:

- latest value and latest delta;
- slope per day;
- approximate points per 30 days;
- direction;
- R-squared when defined;
- a descriptive target-crossing estimate only when evidence is strong enough.

## ETA policy

An ETA is emitted only when:

- at least three observations exist;
- slope is positive;
- R-squared is at least 0.35;
- the current value is still below the target.

Even then, the ETA is explicitly descriptive only. Do not present it as a delivery commitment or schedule.

## Regressions

A regression should trigger investigation, not automatic blame. Possible explanations include:

- actual product regression;
- newly discovered missing scope;
- stricter evidence classification;
- stronger tests exposing failure;
- module boundary changes;
- scoring methodology changes.

Prefer explanations that can be tied to repository evidence or validation results.

## Recommended storage

Keep immutable snapshots under:

`.project-audit/history/<timestamp>.json`

Attach the latest trajectory analysis under:

`history.trajectory`

in the current `.project-audit/audit.json` so the Project Command Center can render it.
