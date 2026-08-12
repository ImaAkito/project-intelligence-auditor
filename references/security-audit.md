# Security Audit Reference

Use this reference for a non-destructive security review during a Project Intelligence Audit.

## Scope

The goal is to identify security readiness gaps and evidence, not to perform intrusive exploitation.

Review applicable areas:

- authentication;
- authorization;
- session management;
- secrets handling;
- input validation;
- file uploads;
- path traversal;
- injection;
- unsafe deserialization;
- SSRF;
- CORS;
- CSRF;
- sensitive logging;
- debug endpoints;
- tenant isolation;
- encryption in transit and at rest;
- key rotation;
- dependency vulnerabilities;
- container/runtime hardening;
- CI/CD credentials;
- update mechanisms;
- audit logging;
- rate limiting and abuse controls.

## Evidence strength

Examples:

- README says auth exists → E1.
- Auth middleware exists → E2.
- Authorization tests pass for allowed and denied cases → E3.
- Tests plus production/security review evidence → potentially E4.

Do not infer security from framework defaults without checking configuration.

## Secret handling

If a secret is discovered:

- do not copy it into reports;
- record only the file/path category and remediation need;
- avoid commands that print secret values;
- recommend rotation when exposure is credible.

## Dependency security

Prefer project-configured ecosystem tools when available, such as `pip-audit`, `npm audit`, `pnpm audit`, `cargo audit`, `govulncheck`, or configured security advisory tooling.

Do not install or run intrusive tools without considering environment constraints. A dependency declaration alone cannot establish that a vulnerability affects the deployed project.

## Severity

Use context-sensitive severity based on exploitability and impact.

A finding should record:

- asset;
- threat;
- attack precondition;
- affected boundary;
- evidence;
- impact;
- likelihood;
- mitigation;
- verification required.

## Production readiness blockers

Typical blockers can include absent authentication where required, authorization enforced only in UI, embedded credentials, committed secrets, unsafe file handling, sensitive logs, unauthenticated administrative endpoints, missing tenant isolation, critical dependency issues in exercised paths, or no rollback/incident visibility for a high-risk service.

Treat these as examples, not automatic findings.
