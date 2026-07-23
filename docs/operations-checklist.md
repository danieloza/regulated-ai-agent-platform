# Operations Checklist

Use this checklist when moving from a local evaluation to a shared or deployed environment. The repository provides a production-shaped baseline, but environment-specific identity, secret management, persistence, and observability remain deployment responsibilities.

## Local Run

- [ ] Use Python 3.12 and Node.js 22.
- [ ] Create and activate a backend virtual environment, then install `pip install -e ".[dev]"` from `backend/`.
- [ ] Install frontend dependencies with `npm ci` from `frontend/`.
- [ ] Start the API on `127.0.0.1:8000` and the Vite frontend on `127.0.0.1:5173`.
- [ ] Confirm `GET /api/health` returns `status: ok` and the UI loads without API errors.
- [ ] Keep the default SQLite database limited to one local backend instance.

## Docker Compose

- [ ] Run `docker compose config --quiet` before starting services.
- [ ] Build and start with `docker compose up --build`.
- [ ] Confirm the Redis and backend health checks pass before validating the frontend.
- [ ] Inspect backend logs for structured request records and unexpected `500` responses.
- [ ] Replace the Compose PostgreSQL fallback password before using the `postgres` profile.
- [ ] Start PostgreSQL and Redis, run the one-off `migrate` service to completion, and only then start the backend/frontend services.
- [ ] Use named volumes intentionally and define a backup or disposal policy for their data.

## Redis and Rate Limits

- [ ] Set `REDIS_URL` to a Redis instance shared by every backend replica.
- [ ] Verify `GET /api/infra` reports `redis` and `connected: true` in shared environments.
- [ ] Alert if status changes to `memory_fallback`; that mode does not enforce a cluster-wide limit.
- [ ] Validate the eight-calls-per-user-and-tool, 60-second default against downstream capacity and abuse cases.
- [ ] Test `429` behavior, expiry, Redis restart, and calls distributed across multiple backend replicas.
- [ ] Restrict Redis network access and enable authentication and transport security where supported by the deployment.

## Database

- [ ] Use SQLite only for local, single-instance, disposable data.
- [ ] Configure PostgreSQL through `DATABASE_URL` before running multiple backend replicas.
- [ ] Provision a least-privilege database identity for the backend; do not expose its password to the agent or frontend.
- [ ] Run `python -m alembic upgrade head` against a restored staging copy before applying a migration to production.
- [ ] Require the Kubernetes migration Job to complete before rolling out the corresponding application image.
- [ ] Confirm `APP_ENV=production`; automatic schema creation and bundled demo-data seeding are disabled in that mode.
- [ ] Test connection limits, pooling, transaction behavior, backups, point-in-time recovery, and restore drills.
- [ ] Define retention and deletion rules for documents, approvals, and audit events.

## Secrets and Configuration

- [ ] Keep real secrets out of Git, images, frontend bundles, prompts, logs, and audit metadata.
- [ ] Inject database and Redis credentials from the environment's secret manager.
- [ ] Use ConfigMaps or equivalent only for non-sensitive configuration.
- [ ] Set `LOG_LEVEL`, `ALLOWED_ORIGINS`, `DATABASE_URL`, and `REDIS_URL` explicitly per environment.
- [ ] Rotate credentials and confirm the application reconnects without unsafe manual changes.
- [ ] Review `GET /api/infra` exposure because it can reveal runtime configuration metadata.

## Enterprise API

- [ ] Generate high-entropy API keys outside the repository and store only their SHA-256 digests in `ENTERPRISE_API_CREDENTIALS`.
- [ ] Inject credential configuration from a secret manager; replace the empty Compose/Kubernetes placeholder before enabling `/api/v1`.
- [ ] Assign the minimum role (`viewer`, `operator`, `approver`, or `admin`) and an explicit tenant allowlist to every service account.
- [ ] Rotate keys, remove revoked digests, and verify old credentials return `401`.
- [ ] Require unique `Idempotency-Key` values for every mutation and monitor `409` conflicts for client misuse.
- [ ] Drain pending outbox events into the approved SIEM, webhook relay, or event bus with retry and dead-letter handling.
- [ ] Apply gateway-level TLS, request-size limits, rate limits, IP policy, and credential abuse alerts before external exposure.
- [ ] Confirm audit and lifecycle pagination limits protect the database from unbounded reads.

## Enterprise Identity and Trust

- [ ] Configure `OIDC_ISSUER`, `OIDC_AUDIENCE`, and an HTTPS `OIDC_JWKS_URL` or secret-managed static JWKS.
- [ ] Keep `OIDC_ALLOWED_ALGORITHMS` restricted to the approved asymmetric signing algorithms.
- [ ] Map corporate groups to the minimum platform roles through `OIDC_GROUP_ROLE_MAP`; verify unmapped identities fail closed.
- [ ] Confirm the configured tenant claim includes only authorized tenant IDs and test cross-tenant requests.
- [ ] Require AAL2/MFA for regulated writes, approval decisions, policy release, and break-glass access.
- [ ] Verify the requester cannot approve the same payload and that a changed payload digest is rejected.
- [ ] Keep the local `/api/trust/*` demo routes behind a local-only or evaluation ingress; expose `/api/v1/trust/*` to enterprise clients.
- [ ] Alert on repeated JWT failures, tenant mismatches, MFA step-up failures, maker-checker violations, and active break-glass grants.
- [ ] Test identity-provider signing-key rotation, revoked sessions, expired tokens, and emergency access expiry.

## Durable Delivery and Integration

- [ ] Configure `CASE_MANAGEMENT_API_URL` as a fixed HTTPS destination; do not derive it from a request or model output.
- [ ] Inject a random `CASE_MANAGEMENT_SIGNING_SECRET` of at least 32 characters and rotate it with the downstream owner.
- [ ] Verify downstream processing is idempotent on the platform delivery ID and validates the payload digest and HMAC signature.
- [ ] Alert on `retry_pending`, `failed`, and `dead_letter`; define retry ownership and a manual replay procedure.
- [ ] Reconcile platform delivery IDs, payload digests, and response digests with the downstream case-management audit.
- [ ] Keep sandbox mode enabled until the downstream contract, network policy, credentials, and data classification are approved.
- [ ] Move due-delivery scheduling to the approved durable worker/queue before relying on unattended production retries.

## Observability and SLOs

- [ ] Scrape `/metrics` from every backend replica through an internal telemetry network.
- [ ] Preserve `X-Request-ID` and `X-Correlation-ID` across gateway, API, worker, and downstream integration logs.
- [ ] Dashboard request rate, error rate, latency, readiness, approval backlog, delivery age, retries, dead letters, and Redis fallback.
- [ ] Define measurable SLOs and alert thresholds; the UI's delivery SLO is a contract example until validated against operating data.
- [ ] Restrict `/metrics` and detailed health output from public ingress.
- [ ] Verify log, metric, and trace retention and access controls match audit and privacy requirements.

## Software Supply Chain

- [ ] Require CI, dependency review, `pip-audit`, `npm audit`, CycloneDX SBOM generation, and the pinned container scanner to pass.
- [ ] Review Dependabot pull requests with application tests and security ownership; do not auto-merge high-impact runtime changes.
- [ ] Publish SBOM artifacts with the release and retain the source revision, image digest, and scanner results.
- [ ] Pin release images by digest, sign them in the deployment pipeline, and verify signatures at admission.
- [ ] Keep GitHub Actions pinned to reviewed commits for security-sensitive jobs and review automation updates as code changes.
- [ ] Rebuild and rescan after base-image or critical dependency advisories.

## Governed Change Proposals

- [ ] Treat proposal detection as decision support; do not grant it policy, model, knowledge-publication, or deployment credentials.
- [ ] Restrict detection to operators and final proposal decisions to approvers through corporate IAM.
- [ ] Verify stable fingerprints prevent duplicates and repeated detection preserves accepted or dismissed decisions.
- [ ] Require a substantive rationale for evidence requests, dismissal, and release acceptance.
- [ ] Validate source references, blast radius, evaluation steps, required approvals, rollout stages, and rollback before acceptance.
- [ ] Confirm `accepted_for_release` creates only a release handoff and cannot mutate runtime state.
- [ ] Integrate outbox events with the approved workflow or event bus using retry and dead-letter handling.
- [ ] Alert on high-priority proposal age, incomplete evidence, missing owners, and stalled required approvals.
- [ ] Require the downstream release controller to verify the manifest digest and every approval independently.
- [ ] Test rollback in the target environment before enabling a proposal-driven release integration.

## Agent Security Twin

- [ ] Version and review scenario nodes, edges, blocking controls, modeled inventory, failure profiles, and containment actions as security-control changes.
- [ ] Keep scenario-modeled inventory visibly separate from live exposure or discovery data.
- [ ] Restrict simulation and containment planning to security operators, decisions to approvers, and evidence access to authorized tenant viewers.
- [ ] Require unique idempotency keys for enterprise simulations, plans, decisions, and verification replays.
- [ ] Confirm sandbox containment cannot call shell commands, construct arbitrary destinations, receive infrastructure credentials, or mutate runtime controls.
- [ ] Verify every containment records an owner, rationale, plan digest, decision, before/after path, and evidence digest.
- [ ] Send Security Twin outbox events to the approved SIEM, workflow, or SOAR integration with retry and dead-letter handling.
- [ ] Reconcile production inventory from IAM, CMDB, data catalog, connector registry, and network policy before using blast-radius results operationally.
- [ ] Require an external release workflow to revalidate separation of duties, scope, rollback, maintenance window, and post-change verification.

## Governed Knowledge and Secure Context

- [ ] Confirm every source has a business owner, classification, review date, integrity hash, and inherited access policy.
- [ ] Route prompt-injection and secret-bearing sources to quarantine and alert on attempted publication.
- [ ] Evaluate claim extraction and contradiction detection against representative domain documents before enabling automated compilation.
- [ ] Require historical replay and expert review for material or high-risk knowledge changes.
- [ ] Monitor stale-source SLAs, unresolved contradictions, pending-review age, replay failures, and release rollback events.
- [ ] Configure `SECURE_CONTEXT_MASTER_SECRET` and `SECURE_CONTEXT_PASSWORD_HASH` through a secret manager; never use the local credential in a shared environment.
- [ ] Set `APP_ENV=production` outside local development and verify missing or partial Secure Context configuration fails closed.
- [ ] Replace password step-up with corporate OIDC/MFA and role-separate create, reveal, approve, publish, and revoke actions.
- [ ] Test encryption-key rotation, context expiry, single-run consumption, emergency revocation, retention enforcement, and recovery procedures.
- [ ] Verify plaintext protected context does not appear in standard logs, traces, evidence exports, analytics, or error reports.
- [ ] Reject credentials and API keys from protected context and require references to the enterprise secrets vault.

## Obsidian Connector and Knowledge Graph

- [ ] Mount or replicate the approved Markdown vault on the backend host with read-only permissions.
- [ ] Set `OBSIDIAN_ALLOWED_ROOTS` to explicit server-side roots; verify production remains disabled when the setting is empty.
- [ ] Keep `.obsidian`, hidden content, symlinks, binaries, and oversized files outside the connector scope.
- [ ] Define included folders, required governance tags, source owner, classification, and review interval for each connector.
- [ ] Verify the persisted preview contains only expected new, modified, deleted, and excluded notes before apply.
- [ ] Confirm apply fails when the vault changes after preview and when the preview is older than 30 minutes.
- [ ] Confirm connector deletion creates a tombstone and retention-review action rather than deleting published knowledge.
- [ ] Restrict preview to `operator` and apply to `approver`; monitor connector scan and apply audit events.
- [ ] Confirm integration outbox payloads, logs, traces, and errors contain no Markdown plaintext.
- [ ] Treat `lexical_run_overlap` graph edges as inferred review signals, not authoritative lineage.
- [ ] Validate `obsidian://open` links on managed operator devices and document the fallback when the desktop app is unavailable.
- [ ] Operate the connector beside a controlled content replica or managed workspace; do not scan arbitrary employee local drives.

## CORS

- [ ] Replace localhost defaults with the exact deployed frontend origins.
- [ ] Avoid wildcard origins when credentials are enabled.
- [ ] Verify browser preflight and credential behavior from every supported origin.
- [ ] Confirm unapproved origins cannot call the API from a browser context.

## Kubernetes

- [ ] Replace example image tags with immutable, scanned image digests or release tags.
- [ ] Replace the placeholder `DATABASE_URL` with an externally managed PostgreSQL connection secret.
- [ ] Inject IAM, JWKS, and integration secrets through an external secret manager rather than committing values.
- [ ] Run and wait for `backend-schema-migration` before updating the backend Deployment.
- [ ] Confirm `/api/health/ready` reports the required Alembic revision; production readiness fails closed on schema drift.
- [ ] Confirm application containers run as non-root and do not require writable root filesystems.
- [ ] Verify readiness and liveness probes, resource requests and limits, and HPA behavior under load.
- [ ] Validate that the metrics pipeline required by the HPA is installed.
- [ ] Apply network policies that allow only required frontend, backend, PostgreSQL, and Redis flows.
- [ ] Configure TLS ingress, authentication, authorization, pod disruption budgets, and availability zones for the target environment.
- [ ] Confirm audit and application logs leave ephemeral pods and reach an access-controlled log store.

## Security Regression

- [ ] Run `python -m pytest` from `backend/`.
- [ ] Review changes to `backend/evals/security_cases.json` as security-control changes.
- [ ] Confirm prompt injection and secret-exfiltration requests remain `denied`.
- [ ] Confirm regulated writes remain `approval_required` and read-only tools remain scoped.
- [ ] Confirm malicious retrieved documents are treated as untrusted data and are not repeated as instructions.
- [ ] Confirm missing retrieval evidence produces the safe `I don't know` response.
- [ ] Confirm unsafe knowledge sources are quarantined, high-risk diffs require review comments, and only approved sources enter RAG.
- [ ] Confirm path traversal, symlinked roots, preview/apply drift, and direct connector publication are blocked.
- [ ] Confirm protected context cannot override policy, is owner-bound, expires, and produces metadata-only audit evidence.
- [ ] Confirm proposal detection cannot authorize or execute its own recommendation and terminal decisions are preserved.
- [ ] Confirm indirect injection, tool-scope escalation, approval bypass, and cross-tenant scenarios stop at their expected control under the current profile.
- [ ] Confirm wrong-issuer, wrong-audience, expired, unsigned, low-assurance, unmapped-role, and cross-tenant OIDC tokens fail closed.
- [ ] Confirm maker-checker, payload-digest, approval-expiry, delivery idempotency, bounded retry, and break-glass constraints.
- [ ] Confirm candidate control failures change only the applicable path and that modeled blast-radius counts remain explicitly labeled.
- [ ] Confirm containment cannot proceed without a prepared plan and substantive approver rationale.
- [ ] Confirm verification replay changes a reachable candidate path to blocked and preserves `runtime_change_applied: false`.
- [ ] Test PII redaction in audit summaries and operator comments.
- [ ] Add payload validation, authentication, authorization, and abuse tests before exposing the API beyond a controlled evaluation environment.

## Release and Readiness

- [ ] Run the backend tests, frontend build, and `docker compose config --quiet` from a clean checkout.
- [ ] Run the Alembic upgrade against a fresh database and confirm the current revision is `head`.
- [ ] Review dependency-audit, SBOM, dependency-review, and container-scan results.
- [ ] Review `git diff` and confirm no generated artifacts, local paths, credentials, or unrelated files are included.
- [ ] Record the application version, image digests, configuration revision, database migration, and rollback procedure.
- [ ] Validate health, assistant query, tool gateway, approval, run details, ledger, and infrastructure status in the target environment.
- [ ] Validate proposal detection, filtering, evidence inspection, RBAC, idempotent decisions, outbox delivery, and non-executing release handoff behavior.
- [ ] Validate Security Twin simulation, blast-radius diff, containment approval, verification replay, evidence export, RBAC, idempotency, and outbox delivery.
- [ ] Validate OIDC login, tenant/role mapping, MFA step-up, maker-checker approval, durable delivery, retry/dead-letter behavior, and downstream reconciliation.
- [ ] Define owners and alerts for API errors, latency, Redis degradation, database health, approval backlog, and rate-limit spikes.
- [ ] Review the threat model and production limitations for the intended data classification and exposure.
- [ ] Obtain the required security, privacy, compliance, and operational approvals before handling regulated production data.
