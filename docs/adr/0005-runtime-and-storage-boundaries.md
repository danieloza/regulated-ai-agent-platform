# ADR 0005: Runtime and Storage Boundaries

## Status

Accepted

## Context

The repository must support low-friction local evaluation while making the production scaling boundary explicit. A file-backed database is convenient for one process but does not provide shared durable state across replicas. Container and orchestration defaults also need to limit privilege and separate public configuration from sensitive values.

## Decision

SQLite is the zero-configuration local and development default. PostgreSQL is the production target and is selected through `DATABASE_URL`; it provides shared state for horizontally scaled backend replicas and the operational features expected for durable regulated records. Redis provides the shared rate-limit state.

The Docker images run as non-root users. Kubernetes manifests define non-root security contexts for application pods, HTTP readiness and liveness probes, resource requests and limits, and an HPA for the backend. Non-sensitive settings use a ConfigMap, while database connection material is referenced through a Secret.

The checked-in Secret and SQLite value are deployment examples only. A real environment must inject a PostgreSQL connection string from its secret-management system and must not run multiple writable backend replicas against pod-local SQLite files.

## Consequences

- Local development starts without provisioning an external database.
- PostgreSQL and Redis provide explicit shared-state targets for scaled deployments.
- Non-root containers and resource bounds reduce runtime blast radius.
- Probes and the HPA provide a baseline for Kubernetes health and scaling behavior.
- SQLite-to-PostgreSQL promotion requires environment configuration and schema migration discipline.
- The included manifests are a baseline; they do not provide production secret delivery, persistent PostgreSQL, network policy, TLS, backup, or disaster recovery.

## Operational Notes

Use SQLite only for a single local backend instance and disposable data. Before scaling the backend, configure PostgreSQL, test schema migrations, backups, restore procedures, connection pooling, and transaction semantics. Supply secrets through the cluster's secret manager, restrict network paths to PostgreSQL and Redis, verify probes and resource sizing under load, and monitor both shared stores as dependencies of the API.
