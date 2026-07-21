# Governed LLM Wiki

The Knowledge Control Center turns approved documents into a versioned, reviewable knowledge layer while preserving raw-source provenance.

## Control Model

```text
Immutable source
    -> injection and secret scan
    -> candidate claim compilation
    -> contradiction detection
    -> historical answer replay
    -> human review
    -> versioned knowledge release
    -> approved RAG index
```

Raw sources remain immutable. Claims are derived artifacts and never replace the original evidence. A published claim identifies its source, owner, classification, confidence, risk, effective date, review date, and release lineage.

## Knowledge Control Center

The operator dashboard includes:

- a health score decomposed into provenance, freshness, review coverage, and contradiction controls;
- an action queue ordered by knowledge risk and review deadline;
- source-to-release pipeline status;
- immutable source intake with classification and ownership;
- claim registry with source lineage;
- pull-request-style knowledge diffs;
- historical replay and impact analysis;
- versioned releases with approval actor and SHA-256 integrity digest;
- the Secure Context Vault for confidential, non-authoritative run context.

The health score is a transparent control aggregate, not a model-generated confidence score.

## Obsidian Vault Connector

Obsidian is an authoring workspace, not the production knowledge authority. The controlled connector scans an explicitly allowlisted Markdown vault, persists a reviewable change set, and only creates immutable sources and approval-gated knowledge changes after an operator applies that exact preview.

The connector workflow is:

```text
Allowlisted vault scope
    -> bounded Markdown scan
    -> persisted Preview Diff
    -> snapshot integrity recheck
    -> immutable source registration
    -> human review queue
    -> versioned release
```

The scanner excludes hidden folders including `.obsidian`, symlinks, non-UTF-8 files, oversized notes, and notes that do not match the configured folder and tag scope. In production, scanning is disabled until `OBSIDIAN_ALLOWED_ROOTS` is configured. A preview expires after 30 minutes, and apply fails if the vault digest changed after preview.

Deleting a note does not delete published knowledge. The connector records a tombstone and creates a retention-review action so an authorized reviewer can decide whether the corresponding source and claims should be retired. `Open in Obsidian` uses the official `obsidian://open` URI to return an operator to the original note without copying plaintext into the browser URL.

The included `backend/demo/obsidian-vault` is a local demonstration fixture. A deployed connector should run beside a controlled content replica or managed workspace, not scan arbitrary employee workstations.

## Knowledge Governance Graph

The governance graph traces connector, note, immutable source, candidate change, claim, release, and historical-run relationships. Persisted lineage such as `materialized_as`, `proposed_as`, and `published_as` is authoritative. `lexical_run_overlap` is explicitly marked as inferred and is not presented as proof of causality.

The UI includes both a visual network and an accessible relationship table. The graph helps an operator answer where a claim came from, which change proposed it, which release published it, and which historical runs may need review.

## Compiler Boundary

The repository uses deterministic local claim extraction to keep tests repeatable and avoid implying that an external model has been configured. The API boundary is designed so a deployment can introduce a governed extraction model without changing the review workflow.

A production compiler should add:

- asynchronous source processing and retry-safe jobs;
- document-type-specific parsers and OCR;
- structured claim schemas by domain;
- calibrated extraction confidence;
- semantic and rules-based contradiction detection;
- expert review queues;
- access control inherited from the source repository;
- model, prompt, and extractor version evidence.

## Secure Context Vault

Protected context is supplemental operational information. It is not an approved source and cannot override security controls, policy decisions, or approval requirements.

The local implementation provides:

- scrypt password verification;
- a signed ten-minute access token;
- Fernet encryption at rest;
- classification, purpose, scope, model-access flag, and expiration metadata;
- secret and prompt-injection rejection;
- owner-bound reveal and revoke operations;
- single-use behavior for `current_run` scope;
- audit events containing metadata and content digest, never plaintext.

For local development, the access password is `knowledge-demo-access`. Do not use this credential outside a local workstation.

Generate a deployment password hash from the backend directory:

```powershell
python -c "from app.services.knowledge import hash_context_password; print(hash_context_password('replace-with-strong-password'))"
```

Inject the result as `SECURE_CONTEXT_PASSWORD_HASH` and inject an independent high-entropy `SECURE_CONTEXT_MASTER_SECRET`. Enterprise deployments should replace the password endpoint with corporate SSO/MFA step-up and managed encryption keys.

The local credential is enabled only when both secure-context secrets are absent and `APP_ENV` is not `production`. Production and partially configured environments fail closed.

## Security Invariants

- Platform policy has higher precedence than protected context.
- Raw documents and protected context are untrusted input.
- Credentials and API keys must be referenced through a secrets manager, not stored in protected context.
- Standard audit logs and evidence packs contain context metadata and digest only.
- Publication requires a human decision; ingestion alone never changes production knowledge.
- A quarantined source cannot create claims or enter retrieval.
- Historical replay informs approval but does not automatically publish a candidate.
- Connector apply never publishes directly into RAG.
- Preview content remains server-side; API responses and integration events expose metadata, hashes, and redacted excerpts rather than raw note bodies.
- Authoritative graph lineage and inferred analytical relationships remain visibly distinct.

## Current Boundary

The feature demonstrates the control plane and persistence contracts. It is not a complete enterprise knowledge-management system. Production use requires corporate IAM, source-repository ACL synchronization, a controlled connector runner, PostgreSQL migrations, durable workers, key rotation, retention enforcement, deletion handling, expert ownership, and evaluated domain-specific extraction.
