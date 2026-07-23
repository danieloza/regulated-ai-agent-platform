# Production Limitations

This repository is designed as a production-shaped portfolio project, not a drop-in regulated production system. The architecture demonstrates the right control points, but a real banking, medical, legal, or enterprise deployment would need additional hardening.

## Current Demo Choices

- SQLite is the default database so the project runs locally without infrastructure.
- Embeddings are deterministic/mock-style for portability and repeatable tests.
- The local operator workflow includes explicit demo actors; the protected `/api/v1` boundary supports strict OIDC JWT validation and scoped workload API keys.
- The React console does not acquire corporate tokens or create an enterprise session. A deployed operator UI still needs the organization's authorization-code/PKCE or backend-for-frontend login pattern; actor-supplied Trust demo routes fail closed when `APP_ENV=production`.
- The policy engine is deterministic and intentionally readable.
- The dashboard is an operator demo console, not a full multi-tenant admin product.
- The governed knowledge compiler uses deterministic local claim extraction and conservative contradiction rules rather than an evaluated domain model.
- Secure Context uses a local step-up credential when deployment secrets are not configured; this mode is only for workstation development.
- The Obsidian connector scans an allowlisted local Markdown vault synchronously; the bundled vault is demonstration data.
- Change proposals are synthesized from deterministic project signals; confidence and expected-risk-reduction values are illustrative decision-support metadata.
- Security Twin attack paths and blast-radius counts come from deterministic scenario inventory; they do not discover live IAM, network, or data-catalog exposure.
- Kubernetes manifests show deployment patterns, probes, limits, ConfigMap/Secret split, and non-root containers, but they are not a complete platform baseline.
- The case-management adapter is deterministic and local until a fixed enterprise endpoint and signing secret are configured.
- Prometheus metrics and structured correlation logs are available, but no organization-specific dashboards, paging rules, or validated SLO history are bundled.

## Production Requirements

- Replace SQLite with PostgreSQL, backups, point-in-time recovery, and least-privilege database roles; apply the included Alembic migrations through a controlled release gate.
- Use managed Redis or a highly available Redis deployment for distributed rate limits.
- Connect the OIDC validation boundary to the corporate identity provider, group governance, access reviews, MFA policy, session revocation, and privileged-access process.
- Move all secrets to a secret manager or platform-native secret store, with rotation and audit.
- Connect correlation logs and Prometheus metrics to centralized tracing, dashboards, paging rules, and retention policies.
- Add model/provider governance if using external LLM APIs: data retention review, regional controls, vendor risk, and fallback behavior.
- Replace mock embeddings with a hardened retrieval pipeline, ingestion validation, document provenance, access control per document, and deletion workflows.
- Exercise Alembic migrations on production-like data and establish backup, compatibility, rollback, and ownership controls.
- Enforce the included dependency audits, CycloneDX SBOM, dependency review, and container scan; add image signing, provenance, and admission verification in the release platform.
- Add network policies, ingress TLS, WAF/API gateway controls, and environment-specific CORS.
- Add load, concurrency, and chaos testing for approval flows, rate limits, and ledger updates.
- Replace local knowledge compilation with an approved asynchronous extraction service, domain evaluation sets, expert review SLAs, and source-repository ACL synchronization.
- Replace Secure Context password step-up with corporate OIDC/MFA, managed encryption keys, rotation, retention enforcement, and role-separated reveal/revoke permissions.
- Run knowledge connectors as durable jobs against a controlled, read-only content replica; synchronize source ACLs, identities, retention holds, and deletion decisions from the system of record.
- Add connector scheduling, retries, dead-letter handling, malware/DLP inspection, capacity monitoring, and ownership for failed or stale syncs.
- Validate governance-graph inference against domain evaluation data before using inferred relationships for prioritization; keep authoritative lineage separate.
- Integrate accepted proposals with a corporate workflow and release controller that independently verifies manifest integrity, separation of duties, approvals, canary gates, observability, and rollback.
- Calibrate proposal ranking and risk-reduction estimates against representative operating data before using them for prioritization.
- Integrate Security Twin inventory with authoritative IAM entitlements, asset ownership, tenant metadata, connector scopes, data classification, and network-policy sources before using it for production exposure decisions.
- Keep production containment in a separate, human-authorized SOAR or release workflow with narrow service identities, fixed destinations, independent validation, rollback, and post-change verification.
- Run integration delivery through a managed queue/worker, connect the fixed adapter to an approved case-management sandbox, and establish downstream idempotency, reconciliation, retry, dead-letter, and incident ownership.
- Keep local `/api/trust/*` actor-supplied routes outside production ingress; production authorization must use `/api/v1/trust/*`.

## Intentional Scope

The project focuses on proving backend judgment around AI-agent safety:

- agents do not receive shell access,
- tools are scoped and audited,
- retrieved documents cannot override policy,
- regulated writes require approval,
- rate limits work across replicas,
- safety behavior is covered by tests.

That is the point of the repository: it is more than a "chat with PDF" demo, while still remaining small enough to run and explain during an interview.
