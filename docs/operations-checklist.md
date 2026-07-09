# Operations Checklist

Use this checklist when moving from a local evaluation to a shared or deployed environment. The repository provides a production-shaped baseline, but environment-specific identity, secret management, persistence, and observability remain deployment responsibilities.

## Local Run

- [ ] Use Python 3.12 and Node.js 22.
- [ ] Create and activate a backend virtual environment, then install `pip install -e ".[dev]"` from `backend/`.
- [ ] Install frontend dependencies with `npm install` from `frontend/`.
- [ ] Start the API on `127.0.0.1:8000` and the Vite frontend on `127.0.0.1:5173`.
- [ ] Confirm `GET /api/health` returns `status: ok` and the UI loads without API errors.
- [ ] Keep the default SQLite database limited to one local backend instance.

## Docker Compose

- [ ] Run `docker compose config --quiet` before starting services.
- [ ] Build and start with `docker compose up --build`.
- [ ] Confirm the Redis and backend health checks pass before validating the frontend.
- [ ] Inspect backend logs for structured request records and unexpected `500` responses.
- [ ] Replace the Compose PostgreSQL fallback password before using the `postgres` profile.
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
- [ ] Add a reviewed schema migration process before evolving persistent production data.
- [ ] Test connection limits, pooling, transaction behavior, backups, point-in-time recovery, and restore drills.
- [ ] Define retention and deletion rules for documents, approvals, and audit events.

## Secrets and Configuration

- [ ] Keep real secrets out of Git, images, frontend bundles, prompts, logs, and audit metadata.
- [ ] Inject database and Redis credentials from the environment's secret manager.
- [ ] Use ConfigMaps or equivalent only for non-sensitive configuration.
- [ ] Set `LOG_LEVEL`, `ALLOWED_ORIGINS`, `DATABASE_URL`, and `REDIS_URL` explicitly per environment.
- [ ] Rotate credentials and confirm the application reconnects without unsafe manual changes.
- [ ] Review `GET /api/infra` exposure because it can reveal runtime configuration metadata.

## CORS

- [ ] Replace localhost defaults with the exact deployed frontend origins.
- [ ] Avoid wildcard origins when credentials are enabled.
- [ ] Verify browser preflight and credential behavior from every supported origin.
- [ ] Confirm unapproved origins cannot call the API from a browser context.

## Kubernetes

- [ ] Replace example image tags with immutable, scanned image digests or release tags.
- [ ] Replace the example SQLite `DATABASE_URL` Secret with an externally managed PostgreSQL connection secret.
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
- [ ] Test PII redaction in audit summaries and operator comments.
- [ ] Add payload validation, authentication, authorization, and abuse tests before exposing the API beyond a controlled evaluation environment.

## Release and Readiness

- [ ] Run the backend tests, frontend build, and `docker compose config --quiet` from a clean checkout.
- [ ] Review `git diff` and confirm no generated artifacts, local paths, credentials, or unrelated files are included.
- [ ] Record the application version, image digests, configuration revision, database migration, and rollback procedure.
- [ ] Validate health, assistant query, tool gateway, approval, run details, ledger, and infrastructure status in the target environment.
- [ ] Define owners and alerts for API errors, latency, Redis degradation, database health, approval backlog, and rate-limit spikes.
- [ ] Review the threat model and production limitations for the intended data classification and exposure.
- [ ] Obtain the required security, privacy, compliance, and operational approvals before handling regulated production data.
