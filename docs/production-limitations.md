# Production Limitations

This repository is designed as a production-shaped portfolio project, not a drop-in regulated production system. The architecture demonstrates the right control points, but a real banking, medical, legal, or enterprise deployment would need additional hardening.

## Current Demo Choices

- SQLite is the default database so the project runs locally without infrastructure.
- Embeddings are deterministic/mock-style for portability and repeatable tests.
- Authentication is simplified through demo user identifiers.
- The policy engine is deterministic and intentionally readable.
- The dashboard is an operator demo console, not a full multi-tenant admin product.
- The governed knowledge compiler uses deterministic local claim extraction and conservative contradiction rules rather than an evaluated domain model.
- Secure Context uses a local step-up credential when deployment secrets are not configured; this mode is only for workstation development.
- Kubernetes manifests show deployment patterns, probes, limits, ConfigMap/Secret split, and non-root containers, but they are not a complete platform baseline.

## Production Requirements

- Replace SQLite with PostgreSQL, migrations, backups, point-in-time recovery, and least-privilege database roles.
- Use managed Redis or a highly available Redis deployment for distributed rate limits.
- Add real authentication and authorization: OIDC/SAML, RBAC/ABAC, tenant boundaries, service accounts, and short-lived credentials.
- Move all secrets to a secret manager or platform-native secret store, with rotation and audit.
- Add complete request tracing, metrics, dashboards, alerting, and retention policies.
- Add model/provider governance if using external LLM APIs: data retention review, regional controls, vendor risk, and fallback behavior.
- Replace mock embeddings with a hardened retrieval pipeline, ingestion validation, document provenance, access control per document, and deletion workflows.
- Add database migrations through Alembic or equivalent.
- Add container image scanning, dependency scanning, SBOM generation, and signed images.
- Add network policies, ingress TLS, WAF/API gateway controls, and environment-specific CORS.
- Add load, concurrency, and chaos testing for approval flows, rate limits, and ledger updates.
- Replace local knowledge compilation with an approved asynchronous extraction service, domain evaluation sets, expert review SLAs, and source-repository ACL synchronization.
- Replace Secure Context password step-up with corporate OIDC/MFA, managed encryption keys, rotation, retention enforcement, and role-separated reveal/revoke permissions.

## Intentional Scope

The project focuses on proving backend judgment around AI-agent safety:

- agents do not receive shell access,
- tools are scoped and audited,
- retrieved documents cannot override policy,
- regulated writes require approval,
- rate limits work across replicas,
- safety behavior is covered by tests.

That is the point of the repository: it is more than a "chat with PDF" demo, while still remaining small enough to run and explain during an interview.
