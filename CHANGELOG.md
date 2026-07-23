# Changelog

This file records material platform changes for operators, reviewers, and integrators. It follows a Keep a Changelog-style structure and uses semantic versioning once a set of changes is published as a tagged release.

## Unreleased

### Added

- Governed Change Proposal Inbox for converting policy replay, knowledge contradiction, security-eval, and approval signals into persistent proposals with explicit ownership, evidence, evaluation, approval, rollout, and rollback contracts.
- Agent Security Twin for deterministic attack-path reconstruction, modeled blast-radius comparison, approval-gated sandbox containment, verification replay, and integrity-digested evidence export.
- Enterprise API resources for tenant-bound change proposals and Security Twin workflows with RBAC, idempotent mutations, actor attribution, and integration outbox events.
- Operator views and guided-demo steps for reviewing change proposals and demonstrating security containment.

### Security

- Containment plans remain non-executing until an authorized approval is recorded.
- Security Twin evidence binds simulations, approvals, replay verification, and export integrity to an auditable workflow.
- Candidate changes expose scope and blast-radius differences before release handoff.

### Documentation

- Added architecture decisions for governed change proposals and the Agent Security Twin.
- Extended API examples, operational guidance, production limitations, threat modeling, screenshots, and demo media for the new controls.

### Validation

- Backend test suite: 48 tests passed.
- Frontend production build completed successfully.
- Docker Compose configuration validated successfully.

## Release note policy

Every material platform patch should:

1. Add operator-relevant changes to `Unreleased`.
2. Separate capabilities, security changes, fixes, deprecations, and operational impact.
3. Move the completed entries into a dated version section when the patch is tagged.
4. Publish a GitHub Release that links to the versioned changelog entry and states validation evidence, migration requirements, and known limitations.
5. Avoid release claims that are not supported by completed tests or deployment evidence.

Small refactors, formatting-only changes, and generated artifacts do not require individual entries unless they affect operators, security posture, compatibility, or deployment behavior.
