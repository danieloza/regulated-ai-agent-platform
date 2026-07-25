# ADR 0013: Governed Code Assurance Adapter

## Status

Accepted

## Context

Static-analysis output is insufficient for a regulated AI release decision unless each finding is attributable to an immutable revision, remediation preserves separation of duties, and validation covers the exact release candidate. Giving the governance service a shell, repository write token, or autonomous patch authority would create a new path from untrusted scanner output to executable code.

## Decision

The platform implements a governed evidence adapter rather than an embedded autonomous scanner. It accepts an allowlisted repository identifier, a full commit SHA, and a fixed scanner profile. Portfolio mode imports deterministic SARIF-shaped fixtures; a production adapter would submit signed results from isolated CI.

Findings are normalized, integrity-digested, and associated with a modeled Security Twin path. Remediation remains `approval_required` with maker-checker separation. The platform never clones the repository, invokes a shell, applies a patch, or deploys. A candidate becomes Release Assurance eligible only after external build, test, and security-evaluation evidence is attached.

## Consequences

- Scanner evidence, approvals, validation results, and the candidate commit share one auditable lifecycle.
- Arbitrary repository URLs, file paths, scanner commands, and unknown request fields are rejected.
- Automated findings cannot directly change application code or production controls.
- Release Assurance fails closed when code evidence or independent approval is missing.
- Portfolio mode demonstrates the contract without paid scanner or CI infrastructure.
- Scanner execution, artifact signing, repository checkout, and delivery remain external responsibilities.
- Deterministic fixtures do not establish production scanner precision or recall.

## Operational Notes

Production adapters should authenticate CI workloads, accept signed size-limited SARIF, verify artifact provenance, and isolate scanner execution outside the API process. Monitor import failures, approval latency, validation failures, idempotency conflicts, and release blockers. Migration `a7d3f8c19e42` adds the durable code-assurance run store.
