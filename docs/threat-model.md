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
- Obsidian vault paths, Markdown notes, persisted sync previews, connector file lineage, and knowledge-graph relations.
- Change-proposal evidence, source fingerprints, operator rationale, release-handoff manifests, and rollback contracts.
- Security Twin scenarios, calculated attack paths, modeled blast radius, containment decisions, verification replays, and evidence digests.
- OIDC claims, role/group mappings, assurance level, access decisions, payload-bound approvals, break-glass grants, and correlation IDs.
- Durable integration deliveries, payload and response digests, retry state, and downstream signing material.

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
| Obsidian vault to connector | Allowlisted backend scanner | Local paths, Markdown, frontmatter, wiki links | Root allowlist, path containment, symlink rejection, file and vault limits, required tags |
| Preview to apply | Persisted preview digest | Vault content changing after review | Thirty-minute expiry, full rescan, digest comparison, immutable source registration |
| Graph to operator | Persisted provenance | Inferred lexical relationships | Explicit authoritative/inferred semantics and accessible adjacency view |
| Signal to change proposal | Human-authorized review workflow | Automated synthesis and incomplete evidence | Deterministic source rules, stable fingerprints, provenance, RBAC, substantive rationale, non-executing handoff |
| Security scenario to containment | Human-authorized sandbox workflow | Candidate control failure and attack-path hypothesis | Deterministic graph, fixed scenario inventory, operator/approver separation, idempotency, replay verification, no runtime credentials |
| Corporate identity to enterprise API | Trusted issuer, JWKS, tenant and group mappings | Bearer token and caller-supplied tenant | Signature, issuer, audience, expiry, algorithm, tenant, role, and assurance validation |
| Approval to execution | Persisted approved payload | Mutated or replayed execution request | Expiry, maker-checker separation, canonical digest comparison, durable state transition |
| Platform to case management | Fixed adapter and approved destination | Network failures and downstream response | HTTPS policy, HMAC digest signature, idempotency key, bounded timeout, no redirects, retry/dead-letter state |

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
- Escape the configured vault root, follow a symlink, or exhaust resources with a large Markdown tree.
- Change a note after preview but before apply to bypass operator review.
- Treat an inferred graph edge as authoritative provenance or delete published knowledge by deleting its source note.
- Manipulate a source signal to create a misleading change proposal or treat acceptance as permission to deploy.
- Exploit an overprivileged tool scope, forged approval, missing tenant check, or poisoned retrieval path to reach regulated assets.
- Treat scenario-modeled blast-radius counts as discovered production exposure or use sandbox containment as production authorization.
- Forge or replay an identity token, escalate a mapped group, cross a tenant boundary, or bypass MFA.
- Approve one's own action, change a payload after review, replay delivery, or abuse emergency access.
- Redirect the integration adapter, tamper with a downstream payload, or hide a failed delivery.

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
- The Obsidian connector is production-disabled without an explicit root allowlist and rejects roots or files that escape through path traversal or symlinks.
- Connector scans are bounded by file-count, file-size, and total-byte limits; hidden metadata and non-UTF-8 files are excluded.
- Apply rescans and compares the persisted digest, while expired previews require a new review.
- Connector deletion creates a tombstone and retention review; connector apply never directly publishes to RAG.
- Raw note bodies remain server-side and are omitted from preview responses and integration outbox projections.
- Governance graph edges distinguish persisted lineage from inferred lexical overlap.
- Change-proposal detection uses auditable deterministic inputs, stable fingerprints, explicit evidence completeness, and preserves terminal human decisions.
- Proposal decisions require attributed operators; enterprise acceptance requires an approver and idempotency key.
- Acceptance emits only a manifest-digested release handoff with `execution_state: not_executed`; it holds no deployment or runtime-mutation authority.
- Security Twin reachability is calculated from fixed, versioned scenario graphs and server-side control states; model output cannot add graph edges.
- Containment requires a persisted simulation, operator-prepared plan, separate approver decision, and replay verification.
- Security Twin containment is sandbox-only and cannot mutate IAM, policies, credentials, connectors, tools, or business systems.
- Evidence export includes the attack path, control states, modeled blast radius, decision, verification, and SHA-256 integrity digest.
- OIDC JWTs require a trusted asymmetric key, issuer, audience, expiry, issued-at, subject, tenant membership, and explicit role mapping; raw tokens are not persisted.
- High-risk actions require AAL2, and the API—not the browser—evaluates tenant, role, and assurance.
- Regulated approvals expire, prevent self-approval, and bind the reviewer decision and execution to the exact payload digest.
- Break-glass access requires an independent AAL2 administrator, incident reference, narrow scope, and short TTL.
- Integration deliveries persist state, preserve the approved payload, use idempotency and integrity headers, disable redirects, bound timeouts, and retain retry/dead-letter evidence.
- Request and correlation IDs are returned and written to structured logs; Prometheus exposes per-route request and latency telemetry.
- CI performs dependency review, Python and npm audits, CycloneDX SBOM generation, and a commit-pinned container vulnerability scan.

## Residual Risks

- The current policy engine is deterministic and demo-oriented, not a complete enterprise DLP or IAM system.
- Mock embeddings are used for portability; production retrieval would need a hardened vector store and ingestion pipeline.
- Local UI routes use explicit demo actors. Production must expose the protected OIDC/API-key surface and integrate corporate group lifecycle, session revocation, access reviews, and privileged-access monitoring.
- SQLite is suitable for local demo only; production should use PostgreSQL with the included Alembic baseline plus tested backups, encryption, rollback, and least-privilege users.
- Prompt-injection detection is regression-tested but not exhaustive. A production system should combine deterministic controls, model evals, red-team cases, monitoring, and incident response.
- Local claim extraction and contradiction detection are deterministic control-plane examples, not validated legal or clinical reasoning.
- The local Secure Context credential and application-managed encryption key are not substitutes for corporate MFA, KMS/HSM-backed keys, rotation, or privileged-access monitoring.
- The local connector scans a filesystem synchronously. Production requires a controlled content replica, inherited source ACLs, durable jobs, malware/DLP controls, and operational ownership.
- Proposal confidence and expected risk reduction are decision-support estimates. A production release controller must independently validate source evidence, approvals, manifest integrity, canary gates, and rollback.
- Security Twin inventory is scenario-modeled rather than discovered from live IAM and data catalogs. Production reachability requires authoritative identity, entitlement, connector, asset, and network integrations.
- The included fixed-destination adapter demonstrates a real delivery contract but is not connected to an organization's case-management system by default. Production needs a managed worker, downstream reconciliation, and operational ownership.
- Metrics are per-process and must be scraped across replicas; SLO targets are not proven until measured in the target environment.

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
- idempotent proposal detection, preserved terminal decisions, role-gated enterprise review, substantive rationale, and non-executing release handoffs.
- deterministic attack-path blocking, scope-escalation blast-radius detection, cross-tenant isolation, approval-gated containment, replay proof, stable evidence digests, and enterprise RBAC/idempotency.
- strict OIDC signature and claim validation, tenant and assurance checks, maker-checker separation, payload digest binding, approval expiry, and break-glass constraints.
- durable delivery queueing, sandbox verification, idempotent replay, bounded retry/dead-letter transitions, readiness checks, and machine-readable metrics.
