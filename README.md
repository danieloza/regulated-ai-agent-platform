# Regulated AI Agent Platform

[![CI](https://github.com/danieloza/regulated-ai-agent-platform/actions/workflows/ci.yml/badge.svg)](https://github.com/danieloza/regulated-ai-agent-platform/actions/workflows/ci.yml)
[![Supply Chain](https://github.com/danieloza/regulated-ai-agent-platform/actions/workflows/supply-chain.yml/badge.svg)](https://github.com/danieloza/regulated-ai-agent-platform/actions/workflows/supply-chain.yml)
![Python 3.12](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-D71F00?style=for-the-badge)
![LangGraph](https://img.shields.io/badge/LangGraph-Workflow-1C3C3C?style=for-the-badge)
![Redis](https://img.shields.io/badge/Redis-Rate%20Limits-DC382D?style=for-the-badge&logo=redis&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Kubernetes](https://img.shields.io/badge/Kubernetes-Ready-326CE5?style=for-the-badge&logo=kubernetes&logoColor=white)
![Security Evals](https://img.shields.io/badge/Security%20Evals-Passing-2E7D32?style=for-the-badge)
![Audit Ready](https://img.shields.io/badge/Audit-Ready-0F766E?style=for-the-badge)
![License MIT](https://img.shields.io/badge/License-MIT-111827?style=for-the-badge)

[Overview](#what-it-demonstrates) · [Demo](#demo) · [Screenshots](#screenshots) · [Architecture](#architecture) · [API](docs/api-examples.md) · [Release Notes](CHANGELOG.md) · [Security](docs/threat-model.md) · [Roadmap](docs/enterprise-deployment-roadmap.md)

Backend platform for safe AI assistants in banking, medical, legal, and enterprise environments.

This is not a chatbot with PDF.

It is a governance and operations control plane for AI agents in regulated environments. It combines source-bound RAG and scoped execution with closed-loop governance, privacy operations, policy replay, audit evidence, and a secured enterprise API surface.

The goal is to demonstrate the engineering layer around AI agents: RAG, governance, security, auditability, approval workflows, race-condition-safe writes, Redis-backed rate limits, Docker, Kubernetes, and security tests.

## What It Demonstrates

- Secure RAG assistant with source-bound answers and citations.
- Governed LLM Wiki with immutable sources, compiled claims, contradiction detection, knowledge diffs, historical impact replay, approval-gated publication, and versioned releases.
- Knowledge Control Center with explainable health controls, operator review queue, claim provenance, source freshness, release lineage, and premium responsive UX.
- Controlled Obsidian Vault Connector with allowlisted Markdown scanning, persisted Preview Diff, drift-safe apply, `Open in Obsidian` deep links, and a knowledge governance graph.
- Secure Context Vault with encrypted supplemental context, short-lived step-up access, scope and TTL controls, single-run consumption, secret/injection scans, and metadata-only audit evidence.
- Prompt-injection lab with runnable attack scenarios and expected policy outcomes.
- Agent Security Twin with deterministic attack-path reconstruction, modeled blast-radius diff, approval-gated sandbox containment, verification replay, and integrity-digested evidence export.
- Agent tool gateway where the agent has no shell, secrets, or direct database credentials.
- Policy engine decisions: `allowed`, `denied`, and `approval_required`.
- Policy Replay & Diff for comparing historical runs and security evals against current or stricter candidate policy behavior before rollout.
- Governed Change Proposal Inbox that converts policy replay, knowledge contradictions, security-eval gaps, and approval signals into persistent, evidence-backed proposals with explicit ownership, evaluation, approval, rollout, and rollback contracts.
- Explainable risk scoring with low, medium, and high bands, weighted factors, and an operator review queue.
- Redacted audit Evidence Pack export in JSON, Markdown, and PDF with policy version, timestamps, citations, approvals, and an integrity digest.
- Controlled Governance Registry imports from a validated Excel template, with staged diffs, explicit apply, ownership metadata, and no implicit deletions.
- Closed-loop Governance Lifecycle connecting agent onboarding, runtime risk detection, incident containment, policy replay, approval, rollout, and reactivation through guarded state transitions.
- Data-subject request lifecycle with pseudonymous discovery, integrity-digested export, verified correction, enforced processing restriction, eligible-data anonymization, retention exceptions, and completion proof.
- Shared Control Lifecycle Matrix for cost governance, model changes, human approvals, and governed knowledge, with 21 ordered transitions and domain-specific evidence.
- Versioned enterprise API surface under `/api/v1` with SHA-256 API credentials, tenant boundaries, RBAC, idempotent mutations, pagination, actor attribution, and integration outbox events.
- Enterprise Identity & Trust Plane with strict OIDC JWT validation, group-to-role mapping, AAL2 step-up, tenant-aware authorization, maker-checker approval, payload digest binding, and incident-scoped break-glass access.
- Durable approved-delivery workflow with PostgreSQL/Alembic persistence, idempotency, HMAC integrity, retry/dead-letter evidence, and a fixed case-management adapter that defaults to non-writing sandbox mode.
- Operational telemetry with correlation-aware structured logs, dependency-aware readiness, separate liveness, Prometheus request/latency metrics, and explicit delivery SLO evidence.
- Supply-chain gates for dependency review, Python and npm audits, CycloneDX SBOM artifacts, commit-pinned container scanning, and Dependabot update proposals.
- Human approval workflow with approve, deny, more-info, operator comments, and audit records.
- Audit timeline with PII redaction and run-details drill-down.
- Document upload/indexing UI for TXT-style governance notes.
- Financial ledger race-condition demo with unsafe and atomic update variants.
- LangGraph workflow with explicit nodes for classify, retrieval, policy, tool call, approval, and final answer.
- Redis-backed distributed rate limiting for tool calls, with memory fallback for local development.
- Docker Compose and Kubernetes manifests for a cluster-ready deployment story.
- Security eval suite for benign requests, prompt-injection attempts, secret exfiltration, shell access, and regulated writes.
- Premium operator dashboard built with React and Vite.

## Governance Lifecycle Coverage

| Lifecycle | Controlled flow | Operational outcome |
| --- | --- | --- |
| Agent governance | Register → Evaluate → Activate → Detect → Contain → Improve | An incident can drive a replayed policy change, controlled rollout, and safe reactivation. |
| Data subject | Discover → Export → Correct → Restrict → Delete → Prove | Subject rights are fulfilled with pseudonymous references, enforced processing restrictions, and completion evidence. |
| Cost governance | Budget → Allocate → Track → Alert → Throttle → Optimize | Forecast overruns produce explicit throttling and model-routing evidence. |
| Model change | Propose → Evaluate → Shadow → Canary → Promote → Monitor | Candidate models progress through measured rollout stages instead of direct replacement. |
| Human approval | Request → Assign → Review → Decide → Execute → Verify | Execution is bound to reviewed evidence and verified against the approved scope. |
| Knowledge | Ingest → Classify → Scan → Approve → Index → Review → Retire | Sources are scanned, approved, versioned, reviewed, and removed from retrieval when retired. |

## Stack

Python, FastAPI, SQLAlchemy, Pydantic, PostgreSQL/SQLite, Alembic, LangGraph, Redis, Prometheus, deterministic mock embeddings, React, Vite, lucide-react, Docker, Kubernetes, pytest.

## Enterprise API v1

The versioned `/api/v1` surface is separate from the local/demo endpoints used by the operator UI. It adds:

- strict OIDC JWT validation for workforce identity plus SHA-256 API credentials for bounded workloads, with no raw bearer token stored by the application,
- issuer, audience, signing-key, expiry, tenant, group/role, and MFA-assurance enforcement,
- role hierarchy: `viewer`, `operator`, `approver`, and `admin`,
- explicit `X-Tenant-ID` authorization and resource-tenant boundaries,
- mandatory `Idempotency-Key` headers for mutations,
- paginated lifecycle, audit, and outbox resources,
- paginated knowledge sources, claims, changes, and releases with RBAC-gated replay and approval decisions,
- governed change-proposal detection and review with operator/approver role separation, idempotent decisions, and a non-executing release handoff,
- tenant-bound Security Twin simulation, containment approval, replay verification, and evidence APIs with idempotent mutations,
- payload-bound maker-checker approvals, durable integration deliveries, and incident-scoped break-glass grants,
- authenticated actor attribution and pending integration outbox events.

Enterprise credentials are disabled by default. Configure the corporate issuer/JWKS or inject `ENTERPRISE_API_CREDENTIALS` through a secret manager using [API examples](docs/api-examples.md); do not commit raw keys or JWTs.

```bash
curl -s http://127.0.0.1:8000/api/v1/capabilities \
  -H "Authorization: Bearer $ENTERPRISE_API_KEY" \
  -H "X-Tenant-ID: demo"
```

Mutation example:

```bash
curl -s -X POST http://127.0.0.1:8000/api/v1/control-lifecycles/transitions \
  -H "Authorization: Bearer $ENTERPRISE_API_KEY" \
  -H "X-Tenant-ID: demo" \
  -H "Idempotency-Key: model-evaluation-20260712-001" \
  -H "Content-Type: application/json" \
  -d '{"kind":"model","action":"evaluate_model","notes":"Candidate passed governed evaluation."}'
```

## License

MIT. See [LICENSE](LICENSE).

## Run Locally

Terminal 1 - backend:

```powershell
git clone https://github.com/danieloza/regulated-ai-agent-platform.git
cd regulated-ai-agent-platform/backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .[dev]
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Terminal 2 - frontend:

```powershell
cd regulated-ai-agent-platform/frontend
npm ci
npm run dev -- --port 5173
```

Open:

```text
http://127.0.0.1:5173
```

## Guided Demo Path

Use this flow when presenting the project in an interview:

1. Click `Demo presentation` and select the client or HR story. The guide focuses the relevant control and explains the evidence to show.
2. Open `Identity & Trust`. Evaluate Alex Morgan's AAL2 access, create a case-note request, approve it independently as Marta Chen, queue the exact payload, then dispatch it into verified sandbox evidence.
3. Emphasize that the browser displays identity context while `/api/v1` validates OIDC, tenant, role, assurance, payload digest, and maker-checker separation server-side.
4. Open `Governance Lifecycle`. Advance onboarding, simulate a high-risk signal, and show that the only permitted next action is incident triage.
5. Continue through containment, mitigation, policy draft, security replay, approval, and rollout. Show the evidence timeline and safe agent reactivation.
6. Open `Data Subject Requests`. Show pseudonymous discovery, integrity-digested export, tool-level processing restriction, anonymization, and completion proof.
7. Open `Control Lifecycle Matrix`. Compare cost, model change, human approval, and knowledge governance as separate guarded loops using one lifecycle engine.
8. Open `Knowledge Control Center`. Scan the bundled Obsidian vault, inspect the persisted Preview Diff, and apply it to the human review queue.
9. Open `Governance graph` to trace note-to-source-to-claim lineage, then review the five-to-seven-year retention contradiction and historical impact replay.
10. Unlock `Secure Context Vault`, attach confidential context to one run, and show that the audit records only its metadata and integrity digest.
11. Go to `Prompt Injection Lab`, run an instruction-override attack, and inspect the denied run with risk factors and audit evidence.
12. Open `Security Twin`. Compare the current tool-scope boundary with an overprivileged candidate, inspect the `0 -> 18` modeled blast-radius diff, approve a sandbox containment plan, and replay it until the path is proven broken.
13. Use `Tool Gateway` to compare an allowed read with a regulated write that becomes `approval_required`.
14. Open `Change Proposal Inbox`. Detect proposals, inspect the evidence and component diff, then show that `Accept for release` creates a controlled handoff without applying a runtime change.
15. Show `/api/v1` OIDC/workload authentication, tenant context, RBAC, idempotency replay, durable delivery, and the generated integration outbox event.
16. Go to `Ledger Demo` and compare unsafe read-modify-write with the atomic SQL update:

```sql
UPDATE accounts
SET balance = balance + :amount
WHERE id = :account_id
RETURNING balance;
```

The core message: the assistant can work with business data, but it cannot bypass policy, call arbitrary infrastructure, expose secrets, or make regulated writes without approval.

## Run With Redis

```powershell
git clone https://github.com/danieloza/regulated-ai-agent-platform.git
cd regulated-ai-agent-platform
docker compose up --build
```

Open:

```text
http://127.0.0.1:5173
```

The backend uses `REDIS_URL=redis://redis:6379/0` inside Compose. Without Redis it falls back to in-memory rate limiting, which keeps local development simple.

PostgreSQL-ready mode:

```powershell
cd regulated-ai-agent-platform
$env:POSTGRES_PASSWORD="replace-with-local-dev-password"
$env:DATABASE_URL="postgresql+psycopg://regulated_ai:regulated_ai_dev@postgres:5432/regulated_ai"
docker compose --profile postgres up -d postgres redis
docker compose --profile postgres run --rm migrate
docker compose up --build backend frontend
```

Without `DATABASE_URL`, the backend uses SQLite for a zero-config demo.
Production deployments should use PostgreSQL, managed Redis, and secrets injected from the deployment platform. This repo includes `.env.example`; real secrets should stay in local environment variables, CI/CD secret stores, or Kubernetes Secrets managed outside source control.
The Compose PostgreSQL profile has a `dev-only-change-me` fallback so `docker compose config` works from a clean checkout; replace it for any real environment.

## Path to Enterprise Deployment

This repository provides a production-shaped governance architecture, but a company deployment must be adapted to one specific operating environment and business workflow.

The recommended path is:

1. Select one measurable business process with named business and technical owners.
2. Connect approved enterprise systems through scoped, audited adapters rather than exposing credentials to the agent.
3. Replace demo identities with corporate OIDC/SSO, group-based RBAC, MFA, and service principals.
4. Move runtime state to PostgreSQL, managed Redis, durable workers/queues, centralized telemetry, and tested backup/restore procedures.
5. Assign business, data, model, security, privacy, knowledge, and platform ownership with escalation SLAs.
6. Roll out through offline evaluation, read-only sandbox, shadow mode, internal pilot, and controlled canary stages.

A practical first deployment would be a compliance knowledge and case-note assistant connected to corporate identity, an approved document repository, and a controlled CRM write workflow.

See [Enterprise Deployment Roadmap](docs/enterprise-deployment-roadmap.md) for the target operating model, pilot definition, integration requirements, rollout gates, and production-readiness criteria.

## Demo

![Regulated AI Agent Platform demo](docs/demo.gif)

The guided client and HR stories now include the Enterprise Identity & Trust Plane: OIDC/AAL2 evidence, server-side authorization, independent approval, payload-bound delivery, and verification. They continue through source-bound RAG, adversarial testing, attack-path analysis, lifecycle controls, governed knowledge, and release handoffs without granting the agent runtime authority.

## Screenshots

### Operator Console

![Operator Console](docs/screenshots/01-dashboard.png)

### Governance Lifecycle

![Governance Lifecycle](docs/screenshots/02-governance-lifecycle.png)

### Control Lifecycle Matrix

![Control Lifecycle Matrix](docs/screenshots/03-control-lifecycle-matrix.png)

### Knowledge Control Center

![Knowledge Control Center](docs/screenshots/04-knowledge-control-center.png)

### Policy Replay & Diff

![Policy Replay and Diff](docs/screenshots/05-policy-replay.png)

### Governed Change Proposal Inbox

![Governed Change Proposal Inbox](docs/screenshots/06-change-proposal-inbox.png)

### Agent Security Twin

![Agent Security Twin](docs/screenshots/07-agent-security-twin.png)

### Enterprise Identity & Trust Plane

![Enterprise Identity and Trust Plane](docs/screenshots/08-enterprise-identity-trust-plane.png)

## Architecture

```mermaid
flowchart LR
  Operator["Operator"] --> UI["React Operator Console"]
  IdP["Corporate OIDC / JWKS"] --> Gateway["/api/v1 Identity + Tenant + AAL + RBAC"]
  Workload["Scoped Workload Credential"] --> Gateway
  Client["Enterprise API Client"] --> Gateway
  UI --> API["FastAPI Control Plane"]
  Gateway --> API
  API --> Lifecycles["Governance Lifecycle Engine"]
  API --> Knowledge["Governed Knowledge Compiler"]
  Obsidian["Allowlisted Obsidian Markdown Vault"] --> Knowledge
  API --> Context["Secure Context Vault"]
  API --> Policy["Policy Engine"]
  API --> RAG["Secure RAG Pipeline"]
  API --> Tools["Scoped Tool Gateway"]
  API --> Approvals["Human Approval Workflow"]
  API --> Trust["Identity Decisions + Payload-bound Approval"]
  Trust --> Delivery["Durable Integration Delivery"]
  Delivery --> CaseSystem["Fixed Case-management Adapter"]
  API --> Twin["Agent Security Twin"]
  API --> Proposals["Governed Change Proposal Inbox"]
  API --> Audit["Audit Trail"]
  API --> Ledger["Ledger Demo"]
  API --> Outbox["Integration Outbox"]
  Tools --> Redis["Redis Rate Limit Store"]
  API --> DB[("SQLite local / PostgreSQL target")]
  Migrations["Alembic Migration Job"] --> DB
  RAG --> DB
  Audit --> DB
  Approvals --> DB
  Trust --> DB
  Delivery --> DB
  Ledger --> DB
  Lifecycles --> DB
  Knowledge --> DB
  Context --> DB
  Proposals --> DB
  Twin --> DB
  Knowledge --> RAG
  Outbox --> DB
  Policy --> Evals["Security Evals"]
  Policy --> Proposals
  Knowledge --> Proposals
  Approvals --> Proposals
  Evals --> Proposals
  Proposals --> Outbox
  Policy --> Twin
  Tools --> Twin
  Approvals --> Twin
  Twin --> Audit
  Twin --> Outbox
```

## Kubernetes

Manifests live in `k8s/` and include:

- backend deployment with two replicas,
- Redis deployment and service,
- frontend nginx deployment,
- readiness/liveness probes,
- an Alembic migration Job for PostgreSQL schema rollout,
- resource requests/limits,
- backend HPA,
- ConfigMap/Secret split for IAM, database, and integration settings,
- non-root security contexts for app pods.

```powershell
docker build -t regulated-ai-agent-platform-backend:latest .\backend
docker build -t regulated-ai-agent-platform-frontend:latest .\frontend
kubectl apply -f .\k8s\namespace.yaml
kubectl apply -f .\k8s\configmap.yaml -f .\k8s\secret.yaml -f .\k8s\redis.yaml
kubectl apply -f .\k8s\migration-job.yaml
kubectl -n regulated-ai wait --for=condition=complete job/backend-schema-migration --timeout=180s
kubectl apply -f .\k8s\backend.yaml -f .\k8s\frontend.yaml -f .\k8s\hpa.yaml
kubectl -n regulated-ai get pods,svc,hpa
```

## Security Notes

- Threat model: [docs/threat-model.md](docs/threat-model.md)
- Production limitations: [docs/production-limitations.md](docs/production-limitations.md)

## Engineering Notes

- Release notes: [CHANGELOG.md](CHANGELOG.md)
- Architecture decisions: [docs/adr](docs/adr)
- Governed change proposals: [ADR 0008](docs/adr/0008-governed-change-proposal-inbox.md)
- Agent Security Twin: [ADR 0009](docs/adr/0009-agent-security-twin.md)
- Enterprise Identity and Trust Plane: [ADR 0010](docs/adr/0010-enterprise-identity-and-trust-plane.md)
- Durable approved delivery: [ADR 0011](docs/adr/0011-durable-approved-delivery.md)
- Governed LLM Wiki and Secure Context: [docs/knowledge-governance.md](docs/knowledge-governance.md)
- API examples: [docs/api-examples.md](docs/api-examples.md)
- Operations checklist: [docs/operations-checklist.md](docs/operations-checklist.md)
- Enterprise deployment roadmap: [docs/enterprise-deployment-roadmap.md](docs/enterprise-deployment-roadmap.md)
- Threat model: [docs/threat-model.md](docs/threat-model.md)
- Production limitations: [docs/production-limitations.md](docs/production-limitations.md)

## Interview Talking Points

The architecture intentionally prevents common AI-agent failure modes. Prompt-injection text can be retrieved as a document chunk, but it cannot grant new permissions because tools are exposed only through scoped backend endpoints. Regulated writes go through `approval_required`, every decision is audited, and PII is redacted before it reaches the operator timeline.

The identity boundary applies the same principle to people and workloads. OIDC proves the workforce subject and MFA assurance, tenant/group mappings establish effective authority, maker-checker prevents self-approval, and the approved payload digest is revalidated before a durable case-management delivery can be dispatched.

Redis is used where it matters operationally: distributed rate limiting across multiple backend replicas. That lets the backend scale in Kubernetes without each pod having an isolated rate-limit counter.

The security evals live in `backend/evals/security_cases.json` and are enforced by pytest. This makes prompt-injection and regulated-write behavior regression-testable instead of only demo-driven.

The ledger module demonstrates why backend correctness still matters in AI products. The unsafe endpoint performs read-modify-write. The safe endpoint uses:

```sql
UPDATE accounts
SET balance = balance + :amount
WHERE id = :account_id
RETURNING balance;
```

## Related Projects

This repository is the main end-to-end regulated AI platform in my portfolio. Related projects explore adjacent parts of the same problem space:

- [Agentic Governance Intelligence Platform](https://github.com/danieloza/agentic-governance-intelligence-platform) - broader agent governance and observability platform.
- [MCP Security Gateway](https://github.com/danieloza/mcp-security-gateway) - focused security gateway for MCP/tool execution.
- [Danex RAG Service](https://github.com/danieloza/danex-rag-service) - focused hybrid RAG API with ingestion, citations, and SQL-backed answers.

## LinkedIn Description

Built a regulated AI agent platform for enterprise environments, focused on safe RAG, controlled tool access, prompt-injection resistance, audit logs, approval workflows, Redis-backed rate limits, Kubernetes deployment patterns, and deterministic backend safeguards.

The project demonstrates how AI assistants can work with sensitive business data without exposing secrets, direct database credentials or unrestricted shell access.

Full post draft: [docs/linkedin-post.md](docs/linkedin-post.md).
