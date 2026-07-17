# ADR 0006: Governed LLM Wiki and Protected Context

## Status

Accepted

## Context

Source-bound RAG can retrieve approved document chunks, but it does not maintain an explicit, versioned synthesis of what the organization currently considers valid knowledge. Reprocessing raw documents for every question also makes contradictions, stale claims, ownership gaps, and the impact of source changes difficult to review before rollout.

Operators may additionally need case-specific confidential context that must not become durable organizational knowledge. Treating this information as an ordinary prompt, document, or log field would weaken access control, retention, and evidence boundaries.

## Decision

The platform implements a governed knowledge compiler with separate records for immutable sources, derived claims, candidate changes, contradictions, historical replay results, and published releases.

New source content is treated as untrusted data. It is scanned before claim compilation. Prompt-injection or secret-bearing sources are retained as quarantined evidence but cannot enter the published knowledge layer. Safe candidate claims require an explicit operator decision. Approval creates a versioned release with an integrity digest and indexes the approved source into the source-bound RAG store.

The local compiler uses deterministic sentence extraction so behavior is explainable and testable without an external model. A company deployment can replace this extractor with an approved LLM or document-intelligence service while preserving the same immutable-source, diff, replay, approval, and release contracts.

Confidential supplemental information is stored separately in the Secure Context Vault. Access requires short-lived step-up authentication. Content is encrypted at rest, scoped, time-limited, audited without plaintext, and cannot override platform policy. A `current_run` context is single-use.

## Consequences

- Knowledge changes become reviewable artifacts instead of invisible index mutations.
- Claim-level provenance, ownership, freshness, contradiction state, and release version are visible to operators.
- Candidate changes can be replayed against historical runs before publication.
- Approved sources feed the existing RAG pipeline without granting the agent new tools or privileges.
- Confidential case context remains separate from the organizational source of truth.
- Secure context access and use add authentication, key-management, retention, and audit responsibilities.
- Deterministic local extraction is portable and testable but does not provide the semantic breadth of a governed production LLM compiler.
- The current contradiction detector is deliberately conservative and must be evaluated against domain-specific legal or clinical language before company use.

## Operational Notes

Production deployments must provide `SECURE_CONTEXT_MASTER_SECRET` and `SECURE_CONTEXT_PASSWORD_HASH` through a secret manager. The local credential exists only for zero-configuration development. Corporate deployments should replace password step-up with OIDC reauthentication or MFA and map reveal, create, revoke, approve, and publish actions to separate RBAC permissions.

PostgreSQL is the target store for durable knowledge and context state. Encryption keys require rotation and recovery procedures. Published releases, approvals, and context-access events require retention policies. The knowledge compiler should run asynchronously for large sources, and claim extraction quality, contradiction recall, replay coverage, and stale-source SLAs should be monitored.
