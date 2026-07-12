# Regulated AI Agent Platform

[![CI](https://github.com/danieloza/regulated-ai-agent-platform/actions/workflows/ci.yml/badge.svg)](https://github.com/danieloza/regulated-ai-agent-platform/actions/workflows/ci.yml)
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

Backend platform for safe AI assistants in banking, medical, legal, and enterprise environments.

This is not a chatbot with PDF.

It is a platform for controlling AI agents in regulated environments. It shows how an AI assistant can answer from business documents while staying behind controlled APIs, policy checks, audit logs, scoped tools, human approvals, PII redaction, and deterministic backend safeguards.

The goal is to demonstrate the engineering layer around AI agents: RAG, governance, security, auditability, approval workflows, race-condition-safe writes, Redis-backed rate limits, Docker, Kubernetes, and security tests.

## What It Demonstrates

- Secure RAG assistant with source-bound answers and citations.
- Prompt-injection lab with runnable attack scenarios and expected policy outcomes.
- Agent tool gateway where the agent has no shell, secrets, or direct database credentials.
- Policy engine decisions: `allowed`, `denied`, and `approval_required`.
- Policy Replay & Diff for comparing historical runs and security evals against current or stricter candidate policy behavior before rollout.
- Explainable risk scoring with low, medium, and high bands, weighted factors, and an operator review queue.
- Redacted audit Evidence Pack export in JSON, Markdown, and PDF with policy version, timestamps, citations, approvals, and an integrity digest.
- Controlled Governance Registry imports from a validated Excel template, with staged diffs, explicit apply, ownership metadata, and no implicit deletions.
- Closed-loop Governance Lifecycle connecting agent onboarding, runtime risk detection, incident containment, policy replay, approval, rollout, and reactivation through guarded state transitions.
- Data-subject request lifecycle with pseudonymous discovery, integrity-digested export, verified correction, enforced processing restriction, eligible-data anonymization, retention exceptions, and completion proof.
- Shared Control Lifecycle Matrix for cost governance, model changes, human approvals, and governed knowledge, with 21 ordered transitions and domain-specific evidence.
- Versioned enterprise API surface under `/api/v1` with SHA-256 API credentials, tenant boundaries, RBAC, idempotent mutations, pagination, actor attribution, and integration outbox events.
- Human approval workflow with approve, deny, more-info, operator comments, and audit records.
- Audit timeline with PII redaction and run-details drill-down.
- Document upload/indexing UI for TXT-style governance notes.
- Financial ledger race-condition demo with unsafe and atomic update variants.
- LangGraph workflow with explicit nodes for classify, retrieval, policy, tool call, approval, and final answer.
- Redis-backed distributed rate limiting for tool calls, with memory fallback for local development.
- Docker Compose and Kubernetes manifests for a cluster-ready deployment story.
- Security eval suite for benign requests, prompt-injection attempts, secret exfiltration, shell access, and regulated writes.
- Premium operator dashboard built with React and Vite.

## Stack

Python, FastAPI, SQLAlchemy, Pydantic, SQLite, LangGraph, Redis, deterministic mock embeddings, React, Vite, lucide-react, Docker, Kubernetes, pytest.

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
npm install
npm run dev -- --port 5173
```

Open:

```text
http://127.0.0.1:5173
```

## 2-Minute Demo Path

Use this flow when presenting the project in an interview:

1. Open the dashboard and show that the app is not a generic PDF chatbot: it has RAG, policy, tools, approvals, audit, ledger, Redis, Docker, and Kubernetes surfaces.
2. Go to `Prompt Injection Lab` and run the instruction-override attack. Show the `denied` policy decision and the audit event.
3. Open `Run Details` for that run. Walk through the question, policy decision, retrieval/tool trace, audit timeline, and final answer.
4. Upload or inspect a malicious document that says to ignore instructions or reveal secrets. Ask a question that retrieves it and show that the answer remains safe/source-bound.
5. Go to `Tool Gateway` and call a read-only tool such as `get_customer_summary`. Then call a regulated write such as `create_case_note` and show `approval_required`.
6. Go to `Approvals`, add an operator comment, and approve/deny/request more information. Show that the decision is recorded in the run/audit timeline.
7. Go to `Ledger Demo` and compare unsafe read-modify-write with the atomic SQL update:

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
docker compose --profile postgres up --build
```

Without `DATABASE_URL`, the backend uses SQLite for a zero-config demo.
Production deployments should use PostgreSQL, managed Redis, and secrets injected from the deployment platform. This repo includes `.env.example`; real secrets should stay in local environment variables, CI/CD secret stores, or Kubernetes Secrets managed outside source control.
The Compose PostgreSQL profile has a `dev-only-change-me` fallback so `docker compose config` works from a clean checkout; replace it for any real environment.

## Demo

![Regulated AI Agent Platform demo](docs/demo.gif)

## Screenshots

### Operator Dashboard

![Operator Dashboard](docs/screenshots/01-dashboard.png)

### Run Details

![Run Details](docs/screenshots/02-run-details.png)

### Tool Gateway

![Tool Gateway](docs/screenshots/03-tool-gateway.png)

### Prompt Injection Lab

![Prompt Injection Lab](docs/screenshots/04-prompt-lab.png)

### Approvals

![Approvals](docs/screenshots/05-approvals.png)

## Architecture

```mermaid
flowchart LR
  User["Operator / Recruiter"] --> UI["React Operator Console"]
  UI --> API["FastAPI Backend"]
  API --> Policy["Policy Engine"]
  API --> RAG["Secure RAG Pipeline"]
  API --> Tools["Scoped Tool Gateway"]
  API --> Approvals["Human Approval Workflow"]
  API --> Audit["Audit Trail"]
  API --> Ledger["Ledger Demo"]
  Tools --> Redis["Redis Rate Limit Store"]
  API --> DB[("SQLite default / PostgreSQL-ready")]
  RAG --> DB
  Audit --> DB
  Approvals --> DB
  Ledger --> DB
  Policy --> Evals["Security Evals"]
```

## Kubernetes

Manifests live in `k8s/` and include:

- backend deployment with two replicas,
- Redis deployment and service,
- frontend nginx deployment,
- readiness/liveness probes,
- resource requests/limits,
- backend HPA,
- ConfigMap/Secret split,
- non-root security contexts for app pods.

```powershell
docker build -t regulated-ai-agent-platform-backend:latest .\backend
docker build -t regulated-ai-agent-platform-frontend:latest .\frontend
kubectl apply -f .\k8s
kubectl -n regulated-ai get pods,svc,hpa
```

## Security Notes

- Threat model: [docs/threat-model.md](docs/threat-model.md)
- Production limitations: [docs/production-limitations.md](docs/production-limitations.md)

## Engineering Notes

- Architecture decisions: [docs/adr](docs/adr)
- API examples: [docs/api-examples.md](docs/api-examples.md)
- Operations checklist: [docs/operations-checklist.md](docs/operations-checklist.md)
- Threat model: [docs/threat-model.md](docs/threat-model.md)
- Production limitations: [docs/production-limitations.md](docs/production-limitations.md)

## Interview Talking Points

The architecture intentionally prevents common AI-agent failure modes. Prompt-injection text can be retrieved as a document chunk, but it cannot grant new permissions because tools are exposed only through scoped backend endpoints. Regulated writes go through `approval_required`, every decision is audited, and PII is redacted before it reaches the operator timeline.

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
