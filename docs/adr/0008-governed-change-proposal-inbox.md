# ADR 0008: Governed Change Proposal Inbox

## Status

Accepted

## Context

Policy replays, knowledge contradictions, adversarial-evaluation gaps, approval backlogs, and runtime risk signals can indicate that a platform control should change. Treating those signals as dashboard-only observations leaves no accountable path from evidence to evaluation and release planning. Allowing an LLM or autonomous agent to apply the change would create a larger control failure: the same system being governed would be able to expand or alter its own authority.

The platform needs a persistent intermediate object that captures why a change is being considered, what it could affect, how it will be evaluated, who must approve it, and how it can be rolled back.

## Decision

The platform synthesizes deterministic, evidence-backed change proposals from existing auditable signals. Each proposal records:

- a stable source fingerprint and source references;
- the affected component, controls, and historical runs;
- confidence and evidence-completeness measures;
- a current-versus-candidate diff;
- an evaluation plan, accountable owner, and required approvals;
- controlled rollout stages and a rollback contract;
- the human decision and operator rationale.

Proposal detection is idempotent. Re-running detection refreshes non-terminal evidence without resetting accepted or dismissed decisions.

The workflow supports assignment, requesting more evidence, dismissal, and acceptance for release. `accept_for_release` creates a release-handoff manifest only. It does not update policy, publish knowledge, deploy a model, execute a tool, or otherwise mutate runtime behavior.

Local endpoints support the operator console. The `/api/v1` surface adds tenant authorization, role separation, mandatory idempotency keys, actor attribution, and outbox events. Detection requires an `operator`; final decisions require an `approver`.

## Consequences

- Platform signals become an accountable change-governance workflow instead of disconnected alerts.
- Reviewers can inspect provenance, blast radius, expected risk reduction, and rollback before accepting a release candidate.
- Stable fingerprints prevent duplicate proposals when detection runs repeatedly.
- Terminal decisions remain durable and are not overwritten by later detection.
- The model or detection layer cannot authorize or execute its own recommendation.
- Proposal quality depends on the quality and coverage of the underlying deterministic signals.
- A release orchestrator, corporate approval system, and deployment controller are still required to execute an accepted handoff in a company environment.
- Confidence and expected-risk-reduction values are decision-support metadata, not guarantees.

## Operational Notes

Persist proposals in PostgreSQL for shared deployments and apply schema changes through reviewed migrations. Restrict enterprise detection to operator identities and decisions to approvers using corporate IAM. Send outbox events to the approved workflow or event bus, monitor proposal age and evidence gaps, and retain decision records with the relevant audit policy.

Before enabling a release integration, verify that the downstream system validates the manifest digest, checks every required approval, enforces separation of duties, supports canary and rollback, and cannot interpret `accepted_for_release` as permission to deploy automatically.
