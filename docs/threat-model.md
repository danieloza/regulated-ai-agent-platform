# Threat Model

This project models a regulated AI assistant that can answer from business documents and call a small set of controlled tools. The main security goal is to prevent the assistant from turning retrieved text or user prompts into uncontrolled infrastructure access, secret exposure, or unaudited regulated writes.

## Assets

- Business documents indexed for RAG.
- Customer summaries and operational case notes.
- Audit events, run details, approval decisions, and operator comments.
- Tool gateway scopes and rate-limit decisions.
- Runtime configuration, database connection strings, and deployment secrets.
- Ledger balances used in the race-condition demo.
- Immutable knowledge sources, derived claims, contradiction reviews, and published knowledge releases.
- Encrypted protected context, access tokens, content digests, purpose, scope, and expiration metadata.

## Trust Boundaries

| Boundary | Trusted side | Untrusted side | Control |
| --- | --- | --- | --- |
| User to API | FastAPI request validation and policy checks | Browser/user prompts | Pydantic models, policy classification, rate limits |
| Documents to RAG | Retrieval and source-bound answer code | Uploaded document text | Treat documents as untrusted data, require citations |
| Agent to tools | Tool gateway | Agent/tool request intent | Scope checks, Redis rate limits, audit events |
| Regulated write to operator | Approval workflow | Requested write payload | `approval_required`, operator decision, comment trail |
| App to infrastructure | Backend runtime | Secrets, shell, direct DB credentials | No shell tool, no secret-returning tools, env/K8s Secret split |
| Multiple replicas to rate limits | Redis | Per-process memory | Shared Redis counters for distributed enforcement |
| Sources to knowledge compiler | Approved review workflow | Untrusted source text and extraction output | Injection/secret scan, immutable source, diff, replay, approval gate |
| Protected context to run | Policy and scoped retrieval | Confidential operator-entered context | Step-up token, encryption, owner binding, TTL, single-run scope, metadata-only audit |

## Attacker Goals

- Prompt the assistant to ignore policy instructions.
- Place malicious instructions inside retrieved documents.
- Exfiltrate database passwords, API keys, or customer data.
- Trigger shell commands or direct database dumps.
- Abuse tool endpoints with excessive calls.
- Create regulated records without operator approval.
- Hide or bypass audit evidence.
- Exploit read-modify-write behavior in financial-style updates.
- Poison organizational knowledge through a malicious or misleading source.
- Publish a material knowledge change without expert review or hide its downstream impact.
- Steal, replay, or misuse protected context or its temporary access token.
- Place credentials in protected context so they reach a model provider or audit system.

## Mitigations

- Source-bound RAG: answers require retrieved citations, otherwise the assistant says it does not know.
- Documents are treated as untrusted data and cannot change system/tool policy.
- Prompt-injection and secret-exfiltration patterns are classified and denied.
- The agent has no shell and no direct database-password tool.
- Tool calls go through scoped backend endpoints with decisions: `allowed`, `denied`, or `approval_required`.
- Redis-backed rate limits are used for tool calls so limits work across backend replicas.
- Regulated write flows create pending approvals instead of directly mutating records.
- Approval decisions capture operator identity, status, and comment.
- Every meaningful action emits audit events and run details.
- PII redaction is applied before sensitive text appears in operator-facing audit summaries.
- Ledger safe path uses an atomic SQL update instead of read-modify-write.
- Security evals cover benign prompts, injection, secret exfiltration, tool abuse, and regulated writes.
- Knowledge sources are immutable, scanned, compiled into candidate claims, replayed, and explicitly approved before entering RAG.
- Contradicted claims are superseded through a versioned release rather than silently overwritten.
- Protected context uses scrypt step-up verification, signed short-lived access tokens, encryption at rest, owner binding, expiration, and single-run consumption.
- Secret-shaped and injection-shaped protected context is rejected; audit events store metadata and digest rather than plaintext.

## Residual Risks

- The current policy engine is deterministic and demo-oriented, not a complete enterprise DLP or IAM system.
- Mock embeddings are used for portability; production retrieval would need a hardened vector store and ingestion pipeline.
- Authentication is simplified for demo use; production should use OIDC/SAML, RBAC, tenant isolation, and session controls.
- SQLite is suitable for local demo only; production should use PostgreSQL with migrations, backups, encryption, and least-privilege users.
- Prompt-injection detection is regression-tested but not exhaustive. A production system should combine deterministic controls, model evals, red-team cases, monitoring, and incident response.
- Local claim extraction and contradiction detection are deterministic control-plane examples, not validated legal or clinical reasoning.
- The local Secure Context credential and application-managed encryption key are not substitutes for corporate MFA, KMS/HSM-backed keys, rotation, or privileged-access monitoring.

## Security Regression Scope

The pytest suite and `backend/evals/security_cases.json` are intentionally part of the threat model. They prevent the most important safety behavior from becoming only a manual demo:

- benign source-bound questions,
- prompt injection,
- malicious document retrieval,
- secret exfiltration,
- shell/tool abuse,
- approval-required regulated writes,
- PII redaction,
- unsafe vs atomic ledger behavior.
- quarantined knowledge sources, contradiction detection, replay-gated publication, and release integrity;
- protected-context authentication, encryption boundary, secret rejection, single-use scope, and metadata-only audit evidence.
