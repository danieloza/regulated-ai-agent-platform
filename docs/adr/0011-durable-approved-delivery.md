# ADR 0011: Durable Approved Delivery

## Status

Accepted

## Context

A human approval is not sufficient if the executed payload can differ from the reviewed payload, if a downstream timeout loses the operation, or if a retry creates duplicate regulated writes. Multi-replica deployment also requires shared database state and an explicit schema-change process.

## Decision

An approved action creates a durable integration-delivery record from the exact persisted payload. The platform revalidates its SHA-256 digest before queueing. Delivery uses an idempotency key, a fixed configured destination, an HMAC payload signature, bounded timeouts, disabled redirects, retry scheduling, terminal verification, and a dead-letter state.

When no case-management endpoint is configured, the adapter operates in deterministic sandbox mode and proves the delivery contract without making an external write.

SQLite remains the zero-configuration local default. PostgreSQL is the deployment target, and Alembic owns versioned schema changes. Kubernetes runs migrations as a bounded non-root Job before application rollout.

## Consequences

- Execution cannot silently drift from the payload approved by the reviewer.
- Delivery attempts and downstream response digests remain auditable.
- Idempotent retries reduce duplicate-write risk.
- Sandbox mode supports safe demonstrations and integration contract testing.
- PostgreSQL supports shared state across replicas; SQLite does not.
- The included delivery loop is synchronous and bounded. A production deployment should schedule due records through a managed worker/queue.
- Downstream API contracts, credentials, reconciliation, and availability remain deployment-specific responsibilities.

## Operational Notes

Configure `CASE_MANAGEMENT_API_URL` as a fixed HTTPS destination and inject a minimum 32-character `CASE_MANAGEMENT_SIGNING_SECRET`. Alert on `retry_pending`, `failed`, and `dead_letter` states, and reconcile verified delivery IDs with the downstream system.

Run `python -m alembic upgrade head` as a pre-deployment gate against PostgreSQL. Back up the database before destructive migrations, test restore and rollback procedures, and do not start a new application revision until the migration Job succeeds.
