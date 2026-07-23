# Contributing

Thank you for improving the Regulated AI Agent Platform. Contributions should
preserve the repository's core purpose: demonstrating auditable, controlled AI
agent behavior with production-shaped engineering practices.

## Before You Start

- Use an issue for non-trivial changes so the intended behavior and control
  impact can be discussed before implementation.
- Report suspected vulnerabilities through the process in
  [SECURITY.md](SECURITY.md), not through a public issue.
- Keep changes focused. Avoid combining unrelated refactors, generated
  artifacts, dependency updates, and product behavior in one pull request.
- Never commit credentials, tokens, private data, local environment files, or
  workstation-specific paths.

## Development Setup

The backend requires Python 3.12. The frontend CI build uses Node.js 22.

```powershell
git clone https://github.com/danieloza/regulated-ai-agent-platform.git
cd regulated-ai-agent-platform

cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"

cd ..\frontend
npm ci
```

For the full local runtime and optional Redis/PostgreSQL profiles, follow
[README.md](README.md) and
[docs/operations-checklist.md](docs/operations-checklist.md).

## Engineering Expectations

Changes must preserve these security and governance invariants:

- the agent receives no shell access, raw secrets, or direct database
  credentials;
- tool execution remains scoped, policy-checked, tenant-bound where applicable,
  and auditable;
- retrieved content is treated as untrusted data and cannot override policy;
- source-bound answers retain citations and safe uncertainty behavior;
- regulated writes remain approval-gated unless a reviewed policy change
  explicitly proves otherwise;
- approval, policy, identity, and delivery controls fail closed;
- sensitive values and personal data are not written to logs or audit exports.

When changing persistent models, include an Alembic migration and describe
upgrade, compatibility, and rollback considerations. Do not edit generated
build output or committed evidence artifacts unless the change explicitly
requires refreshing them.

## Validation

Run the checks relevant to the change before opening a pull request. The normal
baseline is:

```powershell
cd backend
python -m pytest

cd ..\frontend
npm ci
npm run build

cd ..
docker compose config --quiet
docker compose --profile postgres config --quiet
git diff --check
```

Security-sensitive changes should also add or update regression cases in
`backend/tests/` or `backend/evals/security_cases.json`. Changes affecting the
operator experience should include an updated screenshot or a short description
of the browser validation performed.

## Pull Requests

A pull request should:

- explain the problem and the selected engineering tradeoff;
- identify policy, identity, tenant, approval, audit, data, and operational
  effects;
- include tests for new behavior and regressions;
- document new configuration without committing real values;
- update API examples, ADRs, operations guidance, or the threat model when their
  contracts change;
- update [CHANGELOG.md](CHANGELOG.md) for significant user-visible,
  security-relevant, or operational changes.

Approval of a pull request means the change is suitable for this reference
implementation. It does not certify the change for a regulated production
environment.

## Commit Style

Use concise, imperative commit messages, for example:

```text
Add governed policy replay
Harden approval payload validation
Document PostgreSQL migration workflow
```

By contributing, you agree that your contribution is licensed under the
repository's [MIT License](LICENSE).
