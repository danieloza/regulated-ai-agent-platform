# ADR 0004: Distributed Rate Limiting

## Status

Accepted

## Context

Tool calls can consume constrained services or amplify abusive agent behavior. Per-process counters do not provide a reliable limit when FastAPI runs across multiple workers or Kubernetes replicas because each process observes only its own traffic.

## Decision

The tool gateway uses Redis counters keyed by user, tool, and fixed time window. The first increment sets an expiry, allowing all backend replicas configured with the same `REDIS_URL` to enforce a shared limit. The current default is eight calls per user and tool per 60 seconds.

When Redis is not configured or cannot be reached, the application falls back to an in-memory limiter so local development remains available. Infrastructure status reports whether enforcement is using Redis, local memory, or memory fallback.

## Consequences

- A shared Redis deployment enforces limits consistently across backend replicas.
- Rate-limit keys are scoped enough to prevent one tool from consuming another tool's allowance.
- Redis expiry bounds key retention without a separate cleanup process.
- Fixed windows permit bursts around window boundaries.
- Memory fallback is process-local and therefore weaker in a multi-replica deployment.
- Redis availability and latency become part of the production control path.

## Operational Notes

Production environments should use managed or highly available Redis, alert on `memory_fallback`, and treat fallback as degraded control rather than normal operation. Validate limits against expected concurrency and downstream quotas. Tests should cover successful calls, `429` responses, key expiry, Redis failure, and behavior across more than one backend replica.
