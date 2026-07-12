# Enterprise Deployment Roadmap

## Purpose

This roadmap describes how to adapt the Regulated AI Agent Platform from a production-shaped reference implementation into a company-operated system for one approved business workflow. It is not a claim that the repository can be deployed unchanged into a regulated production environment.

The recommended first use case is a compliance knowledge and case-note assistant. An authenticated employee asks questions against approved procedures, receives source-bound answers, and can prepare a regulated case note. The write is executed only after policy evaluation and independent human approval.

## Target Workflow

```text
Employee signs in through corporate identity
→ retrieves approved compliance knowledge
→ receives an answer with citations
→ prepares a regulated case note
→ policy engine requires approval
→ an independent reviewer evaluates the evidence
→ scoped backend adapter writes to the CRM
→ execution is verified and exported as audit evidence
```

The pilot should define measurable outcomes before implementation:

- reduction in case-handling time,
- citation correctness and answer acceptance rate,
- percentage of unsafe or unsupported requests blocked,
- approval turnaround time,
- number of manual corrections,
- operational error and incident rates.

## Enterprise Integrations

Replace local fixtures and mock operations with narrowly scoped adapters for the company's approved systems.

| Capability | Typical integration | Required controls |
| --- | --- | --- |
| Corporate knowledge | SharePoint, Confluence, or document management system | classification, malware/PII/injection scanning, approval, review date, retirement |
| Customer or case data | Dynamics, Salesforce, ServiceNow, or internal CRM | least-privilege scopes, field allowlist, timeout, idempotency, audit, processing restrictions |
| Model access | Azure OpenAI, OpenAI API, or approved private inference | model allowlist, data-classification policy, residency, token/cost limits, telemetry |
| Identity | Microsoft Entra ID, Okta, or another OIDC provider | SSO, MFA, group-to-role mapping, service principals, access reviews |
| Security operations | SIEM and incident-management platform | outbox consumer, alert routing, immutable evidence, correlation IDs |

The agent must not receive a shell, a database password, or unrestricted integration credentials. It requests a named backend tool; the backend authenticates the actor, checks tenant and scope, evaluates policy, invokes the adapter, redacts the result, and records evidence.

## Identity and Access Management

Human access should use corporate OIDC/OAuth rather than user-supplied operator identifiers. Service-to-service clients can use the secured `/api/v1` surface with rotated credentials or workload identity.

Recommended roles:

| Role | Responsibility |
| --- | --- |
| Viewer / auditor | Read approved state and audit evidence. |
| Operator | Run permitted workflows and create review requests. |
| Approver | Decide regulated operations after reviewing evidence. |
| Privacy officer | Operate data-subject and retention workflows. |
| Model-risk reviewer | Evaluate and approve model or policy changes. |
| Platform administrator | Operate infrastructure and integrations without automatic access to regulated business data. |

Enforce maker-checker separation for critical actions. A person who drafts a policy change or requests a regulated write should not approve the same action. Approvals should expire and be bound to an exact payload digest.

## Durable Platform Foundation

Before production use:

- replace SQLite with PostgreSQL and managed schema migrations,
- apply `tenant_id` to business records and enforce PostgreSQL Row-Level Security where appropriate,
- use managed Redis with TLS and explicit failover behavior,
- move replay, evaluation, evidence generation, and large imports to durable workers and queues,
- implement transactional outbox processing with retry and dead-letter handling,
- store secrets in the deployment platform's secret manager,
- centralize logs, traces, metrics, and audit evidence,
- test backup, point-in-time recovery, restore, and disaster-recovery procedures.

The application should expose readiness separately from liveness and should degrade safely when Redis, the model provider, or an enterprise integration is unavailable.

## Operating Model and Ownership

Every production agent and control requires named ownership.

| Area | Accountable owner |
| --- | --- |
| Business workflow and outcomes | Business process owner |
| Agent behavior and policies | AI Governance |
| Model selection and evaluation | Model Risk |
| Source documents and review dates | Knowledge owner |
| Personal data and retention | Privacy / Data Protection |
| Security monitoring and incidents | Security Operations |
| Runtime reliability and deployment | Platform Engineering / SRE |
| Access groups and service identities | IAM team |

Define alert routes, response SLAs, suspension authority, reactivation authority, evidence retention, legal escalation, and regulator/customer notification procedures before production traffic is enabled.

## Observability and Evidence

Propagate one correlation ID through the API gateway, FastAPI request, lifecycle transition, worker job, enterprise adapter, outbox event, and audit evidence. Export OpenTelemetry traces, service metrics, structured logs, and security events to company-controlled systems.

Critical evidence should record:

- authenticated actor and tenant,
- policy and model versions,
- source citations and data classifications,
- requested and executed tool payload digests,
- approval actor, comment, and timestamp,
- lifecycle transitions and guard results,
- integration response and verification outcome,
- declared retention or deletion treatment.

## Security and Compliance Gates

Complete the following before regulated production use:

- deployment-specific threat model and abuse-case review,
- privacy impact assessment where personal data is processed,
- model-risk assessment and documented acceptance criteria,
- penetration test and remediation review,
- dependency, container, secret, and infrastructure scanning,
- egress allowlist, network policy, TLS, gateway limits, and key rotation,
- incident response and agent kill-switch exercises,
- data retention, legal hold, deletion, and immutable-audit procedures,
- evidence that cross-tenant and privilege-escalation tests pass.

## Rollout Plan

### Phase 1: Offline evaluation

- use synthetic or approved test data,
- establish security, quality, latency, and cost baselines,
- run adversarial evaluations and policy replay,
- block all external writes.

### Phase 2: Read-only sandbox

- enable corporate SSO,
- connect one approved knowledge source,
- expose one read-only enterprise tool,
- verify citations, access boundaries, telemetry, and support procedures.

### Phase 3: Shadow and internal pilot

- compare proposed answers or actions without affecting source systems,
- pilot with a named internal group,
- measure corrections, approval load, false blocks, and unsupported requests,
- review incidents and update policies through replay.

### Phase 4: Controlled write canary

- enable one regulated write behind maker-checker approval,
- limit users, tenants, volume, and operating hours,
- require idempotency and execution verification,
- maintain a tested rollback and immediate suspension path.

### Phase 5: Production expansion

- expand only after agreed SLOs and risk gates are met,
- perform periodic access, policy, model, knowledge, and retention reviews,
- rehearse incident response and recovery,
- treat every new tool or data source as a reviewed capability change.

## Production Readiness Exit Criteria

A deployment is ready for regulated production only when:

- the workflow, users, data, integrations, owners, and success metrics are explicitly defined,
- corporate identity and least-privilege authorization are enforced,
- production data is isolated by tenant and protected throughout storage and transit,
- durable state, queues, telemetry, backup, restore, and rollback have been tested,
- critical transitions enforce separation of duties and payload-bound approvals,
- the security, privacy, compliance, model-risk, and operational owners have approved the release,
- the pilot has met its quality, safety, reliability, cost, and response-time thresholds.

The implementation should begin with one narrow workflow and expand by adding reviewed capabilities, not by granting a general-purpose agent broader infrastructure access.
