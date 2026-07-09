# ADR 0001: Controlled Tool Gateway

## Status

Accepted

## Context

An AI assistant that can invoke arbitrary operating-system commands, use raw database credentials, or call unrestricted services can turn prompt injection into infrastructure access. Regulated workflows also require each business action to have an explicit permission boundary, policy outcome, rate limit, and audit record.

## Decision

The agent has no shell and receives no direct database password. All agent-accessible operations are named tools exposed by the FastAPI backend through `/api/tools/{tool_name}`. The gateway maintains an allowlist that maps each tool to a narrow scope and states whether human approval is required. It rejects unknown tools, applies a per-user and per-tool rate limit, and records the decision in the audit trail.

Read operations such as `get_customer_summary` execute through backend-owned database sessions. Regulated writes such as `create_case_note` stop at `approval_required` and create an approval record rather than mutating data immediately.

## Consequences

- Tool capabilities and scopes are explicit, reviewable, and regression-testable.
- Prompt or retrieved-document text cannot create new permissions or bypass the backend API.
- Database credentials remain within the backend runtime boundary.
- Every accepted, denied, or approval-gated tool request can be tied to a user and run.
- Adding a tool requires backend implementation, policy classification, tests, and operational limits.
- The current scope model is application-defined; a production deployment must bind authenticated identities and centrally managed authorization to these scopes.

## Operational Notes

Monitor tool decisions, rate-limit rejections, and approval volume by tool and user. Keep the allowlist small, validate payloads more narrowly as tools mature, and never expose generic command execution or arbitrary SQL as a tool. Rotate backend credentials through the deployment platform and verify that they are not present in agent prompts, frontend configuration, or audit metadata.
