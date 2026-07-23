# ADR 0009: Deterministic Agent Security Twin

## Status

Accepted

## Context

Runtime risk scores and incident queues identify suspicious behavior, but they do not prove how an agent-originated attack could traverse knowledge, policy, tool scopes, approvals, tenant boundaries, and downstream systems. In a regulated environment, operators need to identify the exact control that stopped a path, estimate the exposure created by a candidate control failure, and verify that an approved containment action breaks the same path when replayed.

Using an LLM to invent attack-graph edges, infer production reachability, or authorize containment would make those conclusions non-reproducible and could grant the governed system authority over its own security controls.

## Decision

The platform implements a deterministic Agent Security Twin with four versioned scenarios:

- indirect prompt injection through retrieved knowledge;
- tool-scope escalation;
- approval bypass;
- cross-tenant access.

Each scenario defines its nodes, ordered edges, control points, modeled inventory, expected blocking step, applicable failure profile, and containment actions. The backend calculates `reached`, `blocked`, and `not_reachable` states without using model output. Blast-radius counts are explicitly labeled as scenario-modeled inventory rather than a live production scan.

Every simulation is persisted with the candidate profile, control evidence, operator identity, integrity digest, and runtime-execution state. Containment follows three separate transitions:

1. an operator prepares a sandbox-only plan;
2. an approver records an attributable decision and rationale;
3. an operator replays the original scenario to verify that the path is broken.

No Security Twin endpoint changes IAM, policies, credentials, connectors, tools, or business systems. The `/api/v1` surface adds tenant authorization, RBAC, mandatory idempotency keys, actor attribution, and integration outbox events.

## Consequences

- Operators can inspect the exact control that blocks an attack rather than relying only on a risk score.
- Candidate control failures produce a reproducible before/after blast-radius diff.
- Containment effectiveness is demonstrated through replay and included in an integrity-digested evidence pack.
- Human approval remains distinct from simulation, verification, and production rollout.
- Security scenarios become testable contracts for object authorization, least privilege, approvals, and defense in depth.
- Results are limited by the accuracy and coverage of the configured scenario inventory.
- Modeled record counts must not be represented as discovered production exposure.
- Production containment still requires corporate IAM, SOAR, secrets, connector, and release integrations outside this repository.

## Operational Notes

Persist simulations in PostgreSQL for shared deployments and evolve the schema through reviewed migrations. Restrict simulation and plan creation to security operators, decisions to approvers, and evidence access to authorized tenant viewers. Retain simulation, decision, verification, and outbox records under the applicable audit policy.

Before connecting containment to production systems, require an external workflow to revalidate the evidence digest, scope, separation of duties, target asset ownership, rollback, and maintenance window. Production adapters should use fixed destinations, narrow service identities, idempotent commands, and independent post-change verification. The Security Twin must remain unable to execute shell commands, construct arbitrary outbound requests, or receive infrastructure credentials.
