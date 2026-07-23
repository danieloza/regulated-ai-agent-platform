# Changelog

This file records material platform changes for operators, reviewers, and integrators. It follows a Keep a Changelog-style structure and uses semantic versioning once a set of changes is published as a tagged release.

## Unreleased

No unreleased material changes.

## [0.1.0] - 2026-07-24

### Added

- Enterprise Identity & Trust Plane with strict OIDC JWT validation, issuer/audience/signing-key enforcement, tenant and group-to-role mapping, AAL2 step-up, and scoped workload credentials.
- Server-enforced access decisions, expiring payload-bound approvals, maker-checker separation, incident-scoped break-glass grants, and a premium operator evidence view.
- Durable approved-delivery state machine with a fixed case-management adapter, idempotency and HMAC integrity headers, bounded timeouts, retry/dead-letter evidence, and deterministic non-writing sandbox verification.
- PostgreSQL deployment path with an Alembic baseline, Compose migration service, and a non-root Kubernetes migration Job.
- Correlation-aware structured logs, dependency-aware readiness, separate liveness, and Prometheus request/latency metrics.
- Supply-chain workflow with dependency review, Python and npm audits, CycloneDX SBOM artifacts, commit-pinned container scanning, and Dependabot configuration.
- Governed Change Proposal Inbox for converting policy replay, knowledge contradiction, security-eval, and approval signals into persistent proposals with explicit ownership, evidence, evaluation, approval, rollout, and rollback contracts.
- Agent Security Twin for deterministic attack-path reconstruction, modeled blast-radius comparison, approval-gated sandbox containment, verification replay, and integrity-digested evidence export.
- Enterprise API resources for tenant-bound change proposals and Security Twin workflows with RBAC, idempotent mutations, actor attribution, and integration outbox events.
- Operator views and guided-demo steps for reviewing change proposals and demonstrating security containment.
- Tag-driven backend and frontend OCI image publication to GitHub Container Registry with embedded SBOMs, maximum-mode BuildKit provenance, and GitHub OIDC-signed build attestations.

### Changed

- GitHub Actions runners were upgraded to their current supported major versions and pinned to reviewed full commit SHAs.
- React and React DOM were updated from `19.2.7` to `19.2.8`.
- Kubernetes deployment examples now consume versioned `0.1.0` GHCR images instead of mutable local `latest` tags.
- Dependabot now groups compatible React runtime updates and defers unreviewed major upgrades for TypeScript, the Vite React plugin, and the icon library.

### Fixed

- Corrected cross-repository action pinning that referenced the checkout SHA for artifact upload and the artifact-upload SHA for dependency review.
- Added bounded job timeouts, cancellation of superseded CI runs, and explicit read-only repository permissions for validation workflows.

### Security

- OIDC tokens fail closed on invalid signature, algorithm, issuer, audience, expiry, tenant, or missing role mapping; raw tokens are fingerprinted and not persisted.
- Regulated writes require AAL2, independent approval, an unmodified payload digest, and a durable execution transition.
- Break-glass access is short-lived, incident-bound, scope-limited, audited, and cannot be self-approved.
- External delivery is disabled by default and cannot use caller-controlled destinations or redirects.
- Production startup requires an explicit host allowlist, disables interactive OpenAPI surfaces, and uses a non-credentialed least-privilege CORS policy.
- Containment plans remain non-executing until an authorized approval is recorded.
- Security Twin evidence binds simulations, approvals, replay verification, and export integrity to an auditable workflow.
- Candidate changes expose scope and blast-radius differences before release handoff.

### Documentation

- Added architecture decisions for enterprise identity/trust and durable approved delivery.
- Added OIDC, maker-checker, delivery, operational probe, migration, observability, and supply-chain guidance.
- Extended the guided client and HR presentation with identity architecture and payload-bound execution evidence.
- Added architecture decisions for governed change proposals and the Agent Security Twin.
- Extended API examples, operational guidance, production limitations, threat modeling, screenshots, and demo media for the new controls.

### Validation

- Backend test suite: 58 tests passed.
- Frontend production build completed successfully.
- Docker Compose configuration validated successfully.
- Alembic upgraded a fresh database to revision `48f2772be5c4 (head)` with no model/schema drift.
- Project-scoped Python dependency audit and npm audit reported no known vulnerabilities; backend and frontend CycloneDX generation completed.
- Browser validation completed at desktop, tablet, and mobile widths with the end-to-end maker-checker and verified-delivery workflow; no console warnings or errors were present.

## Release note policy

Every material platform patch should:

1. Add operator-relevant changes to `Unreleased`.
2. Separate capabilities, security changes, fixes, deprecations, and operational impact.
3. Move the completed entries into a dated version section when the patch is tagged.
4. Publish a GitHub Release that links to the versioned changelog entry and states validation evidence, migration requirements, and known limitations.
5. Avoid release claims that are not supported by completed tests or deployment evidence.

Small refactors, formatting-only changes, and generated artifacts do not require individual entries unless they affect operators, security posture, compatibility, or deployment behavior.

[Unreleased]: https://github.com/danieloza/regulated-ai-agent-platform/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/danieloza/regulated-ai-agent-platform/releases/tag/v0.1.0
