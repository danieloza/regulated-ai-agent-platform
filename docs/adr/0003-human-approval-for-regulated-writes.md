# ADR 0003: Human Approval for Regulated Writes

## Status

Accepted

## Context

Writes to regulated records can create legal, financial, privacy, and customer-impacting consequences. Model intent is not sufficient authorization, and a prompt injection or ambiguous request must not directly mutate customer data. An operator needs a reviewable payload, an explicit decision, and a durable audit trail.

## Decision

Tools marked as regulated writes do not execute on the initial call. The gateway returns `approval_required`, stores the proposed tool name and payload, and assigns an approval and run identifier. An operator can submit `approved`, `denied`, or `more_info` with an operator identity and comment through the approval decision endpoint.

The decision is recorded as a `human_approval` audit event. In the current implementation, approval demonstrates the policy and audit state transition; it does not asynchronously execute the proposed write. Production integration must keep execution separate, idempotent, and bound to an approved immutable payload.

## Consequences

- Regulated mutations have a deliberate human checkpoint.
- Approval decisions, operator comments, payloads, and run history are reviewable.
- `more_info` supports investigation without treating uncertainty as authorization.
- The workflow adds latency and operational workload for reviewers.
- Approval queues require ownership, service-level objectives, escalation, and access control.
- A production executor must prevent payload substitution, replay, duplicate execution, and approval by an unauthorized or conflicted operator.

## Operational Notes

Monitor pending approval age and decision outcomes. Require authenticated operator identities and least-privilege approval roles in deployed environments. Before enabling a real write executor, add immutable payload hashes, idempotency keys, expiry, separation-of-duties rules where required, and a final audit event that identifies the resulting business record.
