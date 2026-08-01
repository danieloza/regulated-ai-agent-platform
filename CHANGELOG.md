# Changelog

This file records material platform changes for operators, reviewers, and integrators. It follows a Keep a Changelog-style structure and uses semantic versioning once a set of changes is published as a tagged release.

## Unreleased

### Added

- Contextual Focus Mode for the Interactive Governance Atlas, with camera centering, surrounding-context dimming, readable active-control evidence, explicit return to overview, and automatic step focus for Guided Story and Change Impact.
- Fullscreen Atlas presentation mode with keyboard navigation, focus return, responsive single-column fallback, and reduced-motion-safe behavior.
- Interactive Governance Atlas modes for controlled 2.5D exploration, five evidence-bound control stories, portfolio explanations, direct module navigation, and modeled approval-bypass blast-radius replay ending in a fail-closed `NO-GO`.
- Offline Architecture Intelligence in Knowledge Control Center, with a Graphify-derived system topology, searchable symbol drill-down, source evidence, confidence semantics, layer filters, accessible relationship data, and guided client and engineering presentation steps.
- Reproducible architecture-dataset compilation from an external Graphify node-link artifact into a sanitized, integrity-digested React asset.
- Governed Code Assurance control room with immutable commit binding, bounded SARIF normalization, Security Twin context, maker-checker remediation, external CI evidence, integrity export, and a `code-assurance-v1` Release Assurance gate.
- Tenant-bound `/api/v1/code-assurance` resources with RBAC, idempotent mutations, strict payloads, actor attribution, and outbox events.
- ADR 0013 and operator documentation for the scanner-adapter trust boundary.
- Adversarial Release Assurance War Room with persisted certification runs, a server-calculated control matrix, baseline-to-candidate diff, modeled blast radius, hard blocking findings, maker-checker GO / NO-GO decisions, and HMAC-SHA256 integrity attestations.
- Protected `/api/v1/release-assurance` resources with tenant enforcement, RBAC, idempotent certification and decision mutations, actor attribution, and outbox evidence.
- Safe and intentionally unsafe candidate bundles for demonstrating that approval removal produces a non-overridable `NO-GO` with modeled customer-record exposure.
- Guided client and engineering presentation steps, API examples, ADR 0012, operator screenshots, and updated demo media for adversarial release certification.
- A 59-second, watermark-free workflow explainer with offline English narration and a full-resolution README poster; reproducible production sources are isolated on the dedicated `media-production` branch.
- Native inline workflow video playback in the GitHub README, with the repository's free GitHub Pages endpoint retained as a full-resolution fallback.

### Changed

- Updated the guided client and HR presentation steps, README demo path, public Atlas screenshot, and animated demo to present the approval-boundary regression through the new contextual focus surface.
- Upgraded the architecture presentation step and public screenshot to demonstrate animated governance flows and release-impact reasoning while keeping the code-symbol evidence view available for engineering review.
- Reorganized the operator sidebar into compact, accessible control groups, bounded the Citations inventory behind an expandable evidence preview, and made guided-presentation panels collision-aware with a manual repositioning fallback.

### Security

- Focus and presentation behavior remain local React, SVG, and CSS state; the patch adds no remote renderer, analytics surface, repository authority, or runtime mutation.
- Atlas motion is implemented with the existing React, SVG and CSS surface; it adds no WebGL engine, remote animation package, runtime repository access or LLM dependency, and the candidate-impact story is explicitly modeled and non-mutating.
- Architecture evidence is rendered without remote JavaScript, runtime repository access, Graphify hooks, semantic extraction or LLM calls; absolute paths and control characters are removed before the generated dataset enters the frontend bundle.
- Code-assurance input is constrained to an allowlisted repository identifier, full commit SHA, and fixed scanner profile; the API exposes no arbitrary URL, path, command, clone, patch, or deployment surface.
- Remediation rejects self-approval, and release eligibility fails closed until build, tests, and security evaluations pass for an integrity-bound artifact.
- Production attestation fails closed when `RELEASE_ATTESTATION_KEY` is absent; signing key material is never returned to the client.
- Blocking control failures cannot be approved, and the initiating operator cannot approve the same certification run.
- An attestation explicitly authorizes only an external pipeline and never performs a deployment or runtime mutation.
- The frontend lockfile resolves PostCSS to `8.5.23`, removing the high-severity source-map path traversal advisory reported against versions through `8.5.17`.

### Operational impact

- Graphify remains an external development-time analyzer rather than an application dependency; operators regenerate the committed architecture dataset explicitly when architectural evidence needs to be refreshed.
- Production databases require migration `a7d3f8c19e42`.
- Deployments issuing attestations must inject and rotate `RELEASE_ATTESTATION_KEY` and publish a stable `RELEASE_ATTESTATION_KEY_ID`.
- Production code-scanner integrations require workload authentication, signed SARIF, authoritative artifact provenance, and isolated scanner execution.

### Validation

- Browser validation covered click-to-focus, automatic Guided Story and Change Impact camera transitions, `Back to full map`, fullscreen entry and `Escape` focus return, plus responsive presentation layouts at 1440 and 390 CSS pixels.
- Browser validation covered atlas exploration, governed-story playback, approval-bypass impact replay through blocking `NO-GO`, deep-link navigation to Release Assurance, symbol drill-down, and responsive layout at 1440 and 390 CSS pixels.
- Architecture generation produced an identical artifact on repeated runs, passed the local-path leakage scan, and was exercised in the browser across system-map, symbol-search, source-inspection, desktop, and 390-pixel responsive states.
- Backend test suite: 67 tests passed, including local, enterprise, integrity, fail-closed release assurance, and governed code-assurance contracts.
- Frontend production build, zero-high-severity npm audit, and Docker Compose configuration validation completed successfully.
- Alembic upgraded a fresh database to `a7d3f8c19e42 (head)` with no model/schema drift.
- Browser validation covered code-evidence import, maker-checker remediation, CI evidence, release-gate eligibility, safe GO, blocked NO-GO, and responsive layouts at 1440, 768, and 375 CSS pixels.

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
