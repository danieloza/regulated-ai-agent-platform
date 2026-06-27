# LinkedIn Post

I built a Regulated AI Agent Platform for enterprise environments.

This is not a chatbot with PDF.

It is a backend platform for controlling AI agents in regulated environments such as banking, legal, medical, and enterprise security.

The project demonstrates how an AI assistant can work with sensitive business data without exposing shell access, database passwords, unrestricted tools, or hidden secrets.

What it includes:

- source-bound RAG with citations and "I don't know" behavior,
- prompt-injection lab with malicious documents and attack scenarios,
- scoped agent tool gateway with Redis-backed rate limits,
- policy decisions: allowed, denied, approval_required,
- human approval workflow with operator comments,
- audit timeline and run details as the source of truth,
- PII redaction,
- financial ledger race-condition demo with unsafe vs atomic updates,
- LangGraph workflow,
- Docker Compose one-command local run,
- Kubernetes manifests with probes, limits, ConfigMap/Secret split,
- security evals and pytest coverage.

The main idea:

AI agents should not be trusted with direct infrastructure access.
They should operate through controlled APIs, policy checks, audit logs, scoped permissions, and approval workflows.

Stack:
Python, FastAPI, SQLAlchemy, Pydantic, SQLite/PostgreSQL-ready patterns, LangGraph, Redis, React, Vite, Docker, Kubernetes, pytest.

GitHub:
https://github.com/danieloza/regulated-ai-agent-platform

#AI #BackendEngineering #FastAPI #LangGraph #RAG #AISecurity #Governance #DevOps #Kubernetes #Redis
