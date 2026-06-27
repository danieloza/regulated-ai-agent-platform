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
- Human approval workflow with approve, deny, more-info, operator comments, and audit records.
- Audit timeline with PII redaction and run-details drill-down.
- Document upload/indexing UI for TXT-style governance notes.
- Financial ledger race-condition demo with unsafe and atomic update variants.
- LangGraph workflow with explicit nodes for classify, retrieval, policy, tool call, approval, and final answer.
- Redis-backed distributed rate limiting for tool calls, with memory fallback for local development.
- Docker Compose and Kubernetes manifests for a cluster-ready deployment story.
- Security eval suite for benign requests, prompt-injection attempts, secret exfiltration, shell access, and regulated writes.
- Premium operator dashboard built with React and Vite.

## Portfolio Positioning

This is the flagship project in my AI governance/backend portfolio.

It connects the ideas from my earlier agent governance projects into one regulated, interview-ready platform: source-bound RAG, scoped tool access, policy enforcement, human approvals, auditability, Redis-backed rate limits, Docker, Kubernetes, and regression-tested security behavior.

## Stack

Python, FastAPI, SQLAlchemy, Pydantic, SQLite, LangGraph, Redis, deterministic mock embeddings, React, Vite, lucide-react, Docker, Kubernetes, pytest.

## License

MIT. See [LICENSE](LICENSE).

## Run Locally

Backend:

```powershell
cd C:\Users\syfsy\projekty\regulated-ai-agent-platform\backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .[dev]
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Frontend:

```powershell
cd C:\Users\syfsy\projekty\regulated-ai-agent-platform\frontend
npm install
npm run dev -- --port 5173
```

Open:

```text
http://127.0.0.1:5173
```

## Run With Redis

```powershell
cd C:\Users\syfsy\projekty\regulated-ai-agent-platform
docker compose up --build
```

Open:

```text
http://127.0.0.1:5173
```

The backend uses `REDIS_URL=redis://redis:6379/0` inside Compose. Without Redis it falls back to in-memory rate limiting, which keeps local development simple.

PostgreSQL-ready mode:

```powershell
cd C:\Users\syfsy\projekty\regulated-ai-agent-platform
$env:POSTGRES_PASSWORD="replace-with-local-dev-password"
$env:DATABASE_URL="postgresql+psycopg://regulated_ai:regulated_ai_dev@postgres:5432/regulated_ai"
docker compose --profile postgres up --build
```

Without `DATABASE_URL`, the backend uses SQLite for a zero-config demo.
Production deployments should use PostgreSQL, managed Redis, and secrets injected from the deployment platform. This repo includes `.env.example`; real secrets should stay in local environment variables, CI/CD secret stores, or Kubernetes Secrets managed outside source control.
The Compose PostgreSQL profile has a `dev-only-change-me` fallback so `docker compose config` works from a clean checkout; replace it for any real environment.

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
