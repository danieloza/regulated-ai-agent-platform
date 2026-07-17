# API Examples

The examples assume the backend is available at `http://127.0.0.1:8000`. Identifiers and timestamps are representative and will differ between requests. Responses are shortened where the endpoint also returns a full audit trail or citation detail.

## Health Check

```bash
curl -s http://127.0.0.1:8000/api/health
```

```json
{
  "status": "ok",
  "time": "2026-07-10T10:30:00.000000+00:00"
}
```

## Assistant Query

```bash
curl -s -X POST http://127.0.0.1:8000/api/assistant/query \
  -H "Content-Type: application/json" \
  -d '{"question":"How should AI assistants answer questions from approved sources?","user_id":"operator.demo"}'
```

```json
{
  "run_id": "run_8d12f4a908",
  "policy": {
    "decision": "allowed",
    "reason": "Read-only source-bound workflow.",
    "matches": []
  },
  "answer": "AI assistants must answer only from approved sources.",
  "citations": [
    {
      "chunk_id": 1,
      "document_id": 1,
      "title": "AI Assistant Governance Policy",
      "content": "AI assistants must answer only from approved sources...",
      "score": 0.731
    }
  ],
  "workflow_trace": [
    "classify_request",
    "retrieve_context",
    "policy_check",
    "tool_call",
    "final_answer"
  ],
  "audit": ["..."]
}
```

If no approved source meets the retrieval threshold, `answer` is `I don't know based on the approved sources.` and `citations` is empty.

## Document Upload

Upload a UTF-8 text file with the multipart endpoint:

```bash
curl -s -X POST http://127.0.0.1:8000/api/documents/upload \
  -F "file=@governance-note.txt;type=text/plain"
```

```json
{
  "id": 5,
  "risk_label": "clean",
  "policy": {
    "decision": "allowed",
    "reason": "Read-only source-bound workflow.",
    "matches": []
  }
}
```

The same ingestion path is available as JSON at `POST /api/documents` with `{"title":"...","content":"..."}`.

## Prompt Injection Attack Run

```bash
curl -s -X POST http://127.0.0.1:8000/api/prompt-attacks/ignore-instructions/run
```

```json
{
  "run_id": "attack_19ac3f22b1",
  "policy": {
    "decision": "denied",
    "reason": "Prompt-injection or secret-exfiltration request matched policy.",
    "matches": [
      "ignore (all )?(previous|system|developer) instructions",
      "reveal .*password",
      "database password"
    ]
  },
  "answer": "Request denied by policy engine.",
  "citations": [],
  "attack": {
    "id": "ignore-instructions",
    "name": "Instruction Override",
    "expected_decision": "denied"
  },
  "passed": true
}
```

## Read-Only Tool Call

```bash
curl -s -X POST http://127.0.0.1:8000/api/tools/get_customer_summary \
  -H "Content-Type: application/json" \
  -d '{"user_id":"operator.demo","payload":{"customer_id":"cus-1042"}}'
```

```json
{
  "decision": "allowed",
  "result": {
    "id": "cus-1042",
    "name": "Anna Kowalska",
    "segment": "Private Banking",
    "risk_score": 0.18,
    "note": "Mortgage review, prefers secure inbox contact."
  }
}
```

## Regulated Tool Call Requiring Approval

```bash
curl -s -X POST http://127.0.0.1:8000/api/tools/create_case_note \
  -H "Content-Type: application/json" \
  -d '{"user_id":"operator.demo","payload":{"customer_id":"cus-1042","note":"KYC review requested"}}'
```

```json
{
  "decision": "approval_required",
  "approval": {
    "id": "appr_711e52bc2a",
    "run_id": "tool_5f8ed761bc",
    "tool_name": "create_case_note",
    "payload": {
      "customer_id": "cus-1042",
      "note": "KYC review requested"
    },
    "status": "pending",
    "created_at": "2026-07-10T10:32:00.000000"
  }
}
```

## Approval Decision

Use the approval identifier returned by the regulated tool call:

```bash
curl -s -X POST http://127.0.0.1:8000/api/approvals/appr_711e52bc2a/decision \
  -H "Content-Type: application/json" \
  -d '{"status":"approved","operator_id":"reviewer.01","comment":"Verified against the KYC case."}'
```

```json
{
  "id": "appr_711e52bc2a",
  "run_id": "tool_5f8ed761bc",
  "tool_name": "create_case_note",
  "payload": {
    "customer_id": "cus-1042",
    "note": "KYC review requested"
  },
  "status": "approved",
  "created_at": "2026-07-10T10:32:00.000000"
}
```

Valid decision statuses are `approved`, `denied`, and `more_info`. This endpoint records the decision; the current implementation does not execute the proposed write after approval.

## Run Details

```bash
curl -s http://127.0.0.1:8000/api/runs/run_8d12f4a908
```

```json
{
  "run_id": "run_8d12f4a908",
  "question": "How should AI assistants answer questions from approved sources?",
  "policy": {
    "decision": "allowed",
    "reason": "Read-only source-bound workflow.",
    "matches": []
  },
  "answer": "AI assistants must answer only from approved sources.",
  "citations": ["..."],
  "workflow_trace": [
    "classify_request",
    "retrieve_context",
    "policy_check",
    "tool_call",
    "final_answer"
  ],
  "tool_calls": [],
  "audit": ["..."],
  "approvals": []
}
```

Tool calls use their returned `approval.run_id` when run details are needed.

## Ledger: Unsafe Read-Modify-Write

```bash
curl -s -X POST http://127.0.0.1:8000/api/ledger/bad-credit \
  -H "Content-Type: application/json" \
  -d '{"account_id":"acc-001","amount":25}'
```

```json
{
  "pattern": "read_modify_write",
  "before": 1000,
  "balance": 1025,
  "warning": "Unsafe under concurrent requests."
}
```

## Ledger: Atomic Update

```bash
curl -s -X POST http://127.0.0.1:8000/api/ledger/good-credit \
  -H "Content-Type: application/json" \
  -d '{"account_id":"acc-001","amount":25}'
```

```json
{
  "pattern": "atomic_update",
  "balance": 1050,
  "sql": "UPDATE accounts SET balance = balance + :amount WHERE id = :account_id RETURNING balance"
}
```

Ledger balances depend on prior calls. Use `POST /api/ledger/reset` to restore `acc-001` to `1000` before a repeatable comparison.

## Infrastructure Status

```bash
curl -s http://127.0.0.1:8000/api/infra
```

```json
{
  "runtime": "kubernetes-ready",
  "database": {
    "mode": "sqlite",
    "url_configured": false
  },
  "redis": {
    "mode": "memory",
    "connected": false,
    "url": null
  },
  "capabilities": [
    "distributed tool rate limiting",
    "stateless backend replicas",
    "readiness and liveness probes",
    "configurable REDIS_URL"
  ]
}
```

In Compose, a healthy Redis connection reports `{"mode":"redis","connected":true,"url":"redis://redis:6379/0"}`. Do not expose infrastructure status publicly without considering whether its deployment metadata is appropriate for that audience.

## Governance Lifecycle

Read the connected onboarding, runtime, incident, and policy-improvement state:

```bash
curl -s http://127.0.0.1:8000/api/lifecycle
```

Apply only the `next_action.id` returned by that response. Out-of-order transitions return `409 Conflict`.

```bash
curl -s -X POST http://127.0.0.1:8000/api/lifecycle/transition \
  -H "Content-Type: application/json" \
  -d '{"action":"evaluate_agent","agent_id":"agent_customer_copilot","operator_id":"governance.reviewer","notes":"Onboarding controls reviewed."}'
```

The response contains the managed agent, linked incident and policy change, progress across all four loops, the next permitted action, and lifecycle audit evidence.

## Data-Subject Lifecycle

```bash
curl -s http://127.0.0.1:8000/api/data-subject
```

Execute only the returned `next_action.id`:

```bash
curl -s -X POST http://127.0.0.1:8000/api/data-subject/transition \
  -H "Content-Type: application/json" \
  -d '{"action":"export_data","request_id":"dsr_customer_1042","operator_id":"privacy.reviewer","notes":"Identity and request scope verified."}'
```

Once processing is restricted, customer read and regulated-write tools return `403`. Completion evidence is available from `GET /api/data-subject/{request_id}/evidence`.

## Control Lifecycle Matrix

```bash
curl -s http://127.0.0.1:8000/api/control-lifecycles
```

Advance one cost, model, approval, or knowledge loop using its returned `next_action.id`:

```bash
curl -s -X POST http://127.0.0.1:8000/api/control-lifecycles/transition \
  -H "Content-Type: application/json" \
  -d '{"kind":"model","action":"evaluate_model","operator_id":"model-risk.reviewer","notes":"Candidate passed the governed evaluation suite."}'
```

The API rejects skipped and repeated transitions with `409 Conflict` and records domain evidence plus a platform audit event for every accepted transition.

## Enterprise API v1

The `/api/v1` surface requires a credential, tenant context, and role. Store only SHA-256 credential digests in `ENTERPRISE_API_CREDENTIALS`; inject the JSON through a secret manager.

```bash
curl -s http://127.0.0.1:8000/api/v1/capabilities \
  -H "Authorization: Bearer $ENTERPRISE_API_KEY" \
  -H "X-Tenant-ID: demo"
```

Versioned lifecycle mutation with replay-safe idempotency:

```bash
curl -s -X POST http://127.0.0.1:8000/api/v1/control-lifecycles/transitions \
  -H "Authorization: Bearer $ENTERPRISE_API_KEY" \
  -H "X-Tenant-ID: demo" \
  -H "Idempotency-Key: model-evaluation-20260712-001" \
  -H "Content-Type: application/json" \
  -d '{"kind":"model","action":"evaluate_model","notes":"Candidate passed governed evaluation."}'
```

The same key and payload return the stored response with `idempotency_replayed: true`. Reusing the key with a different payload returns `409`. Audit endpoints support `limit`, `offset`, and optional `event_type`; outbox access requires `admin`.

## Knowledge Control Center

Read the explainable health controls, action queue, sources, claims, candidate changes, and releases:

```bash
curl -s http://127.0.0.1:8000/api/knowledge/overview
```

Register an immutable source and compile candidate claims:

```bash
curl -s -X POST http://127.0.0.1:8000/api/knowledge/sources \
  -H "Content-Type: application/json" \
  -d '{
    "title":"Customer Communication Standard 2026",
    "content":"Customer communications must use approved templates and cite the governing policy before regulated guidance is provided.",
    "classification":"internal",
    "owner":"Knowledge Governance",
    "source_type":"standard",
    "review_days":365
  }'
```

The response contains the immutable source metadata and a `pending_review` change. Injection or secret-bearing content is registered as `quarantined` and produces no candidate claims.

Replay a candidate against historical runs:

```bash
curl -s -X POST http://127.0.0.1:8000/api/knowledge/replay \
  -H "Content-Type: application/json" \
  -d '{"change_id":"kchg_retention_2026","limit":100}'
```

Approve and publish after reviewing provenance, contradictions, and replay evidence:

```bash
curl -s -X POST http://127.0.0.1:8000/api/knowledge/changes/kchg_retention_2026/decision \
  -H "Content-Type: application/json" \
  -d '{
    "decision":"approved",
    "operator_id":"knowledge.reviewer",
    "comment":"Reviewed source provenance, contradiction impact, and historical replay evidence."
  }'
```

High-risk approvals require a substantive comment. Approval supersedes contradicted claims, indexes the approved source, and returns a release version plus SHA-256 integrity digest.

## Secure Context Vault

The local workstation credential is documented in [Governed LLM Wiki](knowledge-governance.md). For any shared environment, configure a password hash and master secret or replace this flow with corporate step-up MFA.

Unlock a ten-minute context session:

```bash
curl -s -X POST http://127.0.0.1:8000/api/knowledge/secure-context/unlock \
  -H "Content-Type: application/json" \
  -d '{"password":"replace-with-configured-password","operator_id":"operator.demo"}'
```

Use the returned token to create encrypted supplemental context:

```bash
curl -s -X POST http://127.0.0.1:8000/api/knowledge/secure-context \
  -H "Content-Type: application/json" \
  -H "X-Secure-Context-Token: $SECURE_CONTEXT_TOKEN" \
  -d '{
    "content":"Customer identity was verified by Compliance Operations for this investigation.",
    "purpose":"Compliance investigation",
    "scope":"current_run",
    "classification":"confidential",
    "expires_hours":1,
    "model_access":true
  }'
```

Attach the returned context ID to a governed run:

```bash
curl -s -X POST http://127.0.0.1:8000/api/assistant/query \
  -H "Content-Type: application/json" \
  -H "X-Secure-Context-Token: $SECURE_CONTEXT_TOKEN" \
  -d '{
    "question":"How should approved sources be used?",
    "user_id":"operator.demo",
    "secure_context_id":"ctx_replace_me"
  }'
```

A `current_run` context cannot be reused. The run audit contains purpose, scope, classification, model-access state, and digest but not plaintext content.

Enterprise clients use the authenticated, tenant-bound knowledge surface:

```bash
curl -s http://127.0.0.1:8000/api/v1/knowledge/claims?limit=50 \
  -H "Authorization: Bearer $ENTERPRISE_API_KEY" \
  -H "X-Tenant-ID: demo"
```

Source ingestion requires the `operator` role and an idempotency key. The outbox event contains identifiers, classification, status, and content hash rather than source plaintext.

```bash
curl -s -X POST http://127.0.0.1:8000/api/v1/knowledge/sources \
  -H "Authorization: Bearer $ENTERPRISE_API_KEY" \
  -H "X-Tenant-ID: demo" \
  -H "Idempotency-Key: source-ingest-20260717-001" \
  -H "Content-Type: application/json" \
  -d '{
    "title":"Customer Communication Standard 2026",
    "content":"Customer communications must use approved templates before regulated guidance is provided.",
    "classification":"internal",
    "owner":"Knowledge Governance",
    "source_type":"standard",
    "review_days":365
  }'
```

Replay requires the `operator` role and an idempotency key:

```bash
curl -s -X POST http://127.0.0.1:8000/api/v1/knowledge/replays \
  -H "Authorization: Bearer $ENTERPRISE_API_KEY" \
  -H "X-Tenant-ID: demo" \
  -H "Idempotency-Key: retention-replay-20260717-001" \
  -H "Content-Type: application/json" \
  -d '{"change_id":"kchg_retention_2026","limit":100}'
```

Knowledge decisions require the `approver` role and also produce an integration outbox event.
