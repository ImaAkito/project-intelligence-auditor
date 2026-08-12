# Architecture Audit

The architecture audit should reconstruct the system as it actually exists, then compare that with declared design intent.

## Reconstruct the architecture

Identify:

- entry points;
- services/processes;
- frontend/backend boundaries;
- APIs and protocols;
- data stores;
- queues/event paths;
- model-serving boundaries;
- external services;
- deployment units;
- shared libraries;
- configuration surfaces;
- critical runtime dependencies.

Build both a logical module map and, when possible, a runtime/deployment map.

## Review dimensions

Assess:

- cohesion;
- coupling;
- dependency direction;
- boundary clarity;
- cyclic dependencies;
- hidden shared state;
- duplicate business logic;
- god modules;
- single points of failure;
- error propagation;
- concurrency model;
- configuration sprawl;
- infrastructure leakage into domain code;
- portability;
- scalability constraints;
- testability;
- observability boundaries;
- migration/evolution difficulty.

## Drift

Compare documentation, diagrams, configuration, and implementation. Record architecture drift when:

- documented components no longer exist;
- runtime paths bypass the intended abstraction;
- experimental code became production-critical without redesign;
- duplicated implementations compete for ownership;
- boundaries changed without documentation;
- dependencies now point opposite the intended architecture.

## Critical path

Identify the minimum end-to-end chain required for the system's core user outcome. Weight architectural findings on this path more strongly than optional or decorative areas.

## Recommendations

For every major finding include:

- severity;
- impact;
- evidence;
- proposed change;
- effort;
- dependency/risk;
- timing.

Do not prescribe a rewrite when a bounded refactor solves the actual problem.
