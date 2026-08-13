# Architecture Inference Reference

Architecture inference exists to produce an evidence-backed starting graph, not to replace architectural review.

## What the deterministic collector may infer

`scripts/infer_architecture.py` currently inspects static Python and JavaScript/TypeScript imports and produces:

- module candidates;
- dependency edges;
- import occurrence counts;
- source evidence for each edge;
- fan-in and fan-out;
- normalized structural centrality;
- strongly connected components as cycle candidates;
- high-connectivity hotspot candidates.

The output is collector evidence. Codex must still inspect responsibilities and runtime behavior before turning a structural signal into a defect, bottleneck, or critical-path claim.

## Dependency direction

An edge:

`A -> B`

means code in module `A` statically imports or references module `B` through a supported import form.

It does not mean:

- the runtime integration was executed successfully;
- the dependency is required on every path;
- the imported code is reachable;
- the architectural boundary is desirable;
- the modules communicate only through that dependency.

## Evidence strength

A static internal import is normally E2 evidence for the existence of a code-level dependency.

Do not promote it to E3 integration evidence unless a reproducible execution, integration test, trace, benchmark, or equivalent behavior-level validation demonstrates the interaction.

## Cycle review

A static dependency cycle is a review candidate. Before classifying it as technical debt, determine whether it is:

- a real runtime cycle;
- an intentional mutually recursive/package-level design;
- generated or type-only coupling;
- test-only coupling;
- a false positive caused by alias resolution.

When confirmed, record why the cycle matters: deployment coupling, initialization risk, change amplification, test difficulty, or another concrete consequence.

## Hotspot review

High fan-in can mean a healthy shared abstraction or a dangerous concentration point. High fan-out can mean orchestration or excessive knowledge.

Do not call a hotspot a bottleneck based on degree alone. Corroborate with at least one of:

- change churn;
- failure history;
- test gaps;
- performance data;
- ownership concentration;
- critical-path position;
- repeated regression evidence.

## Missing dependency classes

Static import analysis can miss:

- reflection and dynamic loading;
- dependency injection configured outside source imports;
- HTTP/RPC boundaries;
- queues, topics, event buses, and pub/sub;
- shared database coupling;
- files/object storage used as integration boundaries;
- shell subprocesses;
- generated code;
- plugin registries;
- runtime service discovery;
- hardware/firmware links.

Codex should supplement the graph with evidence from configuration, deployment files, API definitions, schemas, message contracts, and runtime validation.
