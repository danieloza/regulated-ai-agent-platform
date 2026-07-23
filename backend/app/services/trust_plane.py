from __future__ import annotations

import hashlib
import hmac
import json
import os
from datetime import UTC, datetime
from urllib.parse import urlparse

import httpx


ROLE_LEVEL = {"viewer": 10, "operator": 20, "approver": 30, "admin": 40}
ASSURANCE_LEVEL = {"aal1": 10, "aal2": 20, "workload": 20}

ACTION_POLICIES = {
    "customer_summary.read": {
        "minimum_role": "viewer",
        "minimum_assurance": "aal1",
        "scope": "customer:read",
        "approval_required": False,
        "risk": "low",
    },
    "case_note.create": {
        "minimum_role": "operator",
        "minimum_assurance": "aal2",
        "scope": "case:write",
        "approval_required": True,
        "risk": "high",
    },
    "policy.release": {
        "minimum_role": "approver",
        "minimum_assurance": "aal2",
        "scope": "policy:release",
        "approval_required": True,
        "risk": "critical",
    },
    "identity.break_glass": {
        "minimum_role": "admin",
        "minimum_assurance": "aal2",
        "scope": "identity:break-glass",
        "approval_required": True,
        "risk": "critical",
    },
}


def canonical_digest(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def evaluate_access(
    *,
    subject: str,
    role: str,
    tenant_id: str,
    requested_tenant: str,
    assurance_level: str,
    groups: list[str],
    action: str,
    resource: str,
    payload: dict,
) -> dict:
    policy = ACTION_POLICIES[action]
    reasons = []
    checks = {
        "tenant_match": tenant_id == requested_tenant,
        "role_sufficient": ROLE_LEVEL.get(role, 0) >= ROLE_LEVEL[policy["minimum_role"]],
        "assurance_sufficient": ASSURANCE_LEVEL.get(assurance_level, 0) >= ASSURANCE_LEVEL[policy["minimum_assurance"]],
    }
    if not checks["tenant_match"]:
        reasons.append("tenant_boundary_mismatch")
    if not checks["role_sufficient"]:
        reasons.append("insufficient_role")
    if not checks["assurance_sufficient"]:
        reasons.append("step_up_mfa_required")

    if reasons:
        decision = "denied"
    elif policy["approval_required"]:
        decision = "approval_required"
        reasons.append("independent_approval_required")
    else:
        decision = "allowed"
        reasons.append("least_privilege_policy_satisfied")

    claims_projection = {
        "subject": subject,
        "role": role,
        "tenant_id": tenant_id,
        "assurance_level": assurance_level,
        "groups": sorted(groups),
    }
    return {
        "decision": decision,
        "reasons": reasons,
        "checks": checks,
        "policy": {**policy, "action": action},
        "subject": subject,
        "role": role,
        "tenant_id": requested_tenant,
        "assurance_level": assurance_level,
        "action": action,
        "resource": resource,
        "payload_digest": canonical_digest(payload),
        "claims_digest": canonical_digest(claims_projection),
        "evaluated_at": datetime.now(UTC).isoformat(),
    }


def integration_mode() -> dict:
    endpoint = os.getenv("CASE_MANAGEMENT_API_URL", "").strip()
    if not endpoint:
        return {
            "mode": "sandbox",
            "destination": "case-management-sandbox",
            "statement": "External execution is blocked; delivery verification is deterministic and local.",
        }
    parsed = urlparse(endpoint)
    app_env = os.getenv("APP_ENV", "development").lower()
    is_local_dev = app_env != "production" and parsed.hostname in {"127.0.0.1", "localhost"}
    if parsed.scheme != "https" and not (is_local_dev and parsed.scheme == "http"):
        return {
            "mode": "blocked",
            "destination": parsed.hostname or "invalid",
            "statement": "Configured integration endpoint is rejected because it does not meet transport policy.",
        }
    return {
        "mode": "configured",
        "destination": parsed.hostname or "case-management-api",
        "statement": "Fixed-destination delivery is enabled with idempotency, integrity signature, and bounded timeout.",
    }


def dispatch_case_management(delivery_id: str, payload: dict, payload_digest: str) -> dict:
    mode = integration_mode()
    if mode["mode"] == "sandbox":
        response = {
            "accepted": True,
            "external_write": False,
            "adapter": mode["destination"],
            "delivery_id": delivery_id,
            "payload_digest": payload_digest,
        }
        return {"status": "verified", "mode": "sandbox", "response_digest": canonical_digest(response), "response": response}
    if mode["mode"] == "blocked":
        return {"status": "failed", "mode": "blocked", "error": mode["statement"], "retryable": False}

    endpoint = os.environ["CASE_MANAGEMENT_API_URL"].strip()
    secret = os.getenv("CASE_MANAGEMENT_SIGNING_SECRET", "")
    if len(secret) < 32:
        return {
            "status": "failed",
            "mode": "configured",
            "error": "Integration signing secret is not configured with at least 32 characters.",
            "retryable": False,
        }
    signature = hmac.new(secret.encode("utf-8"), payload_digest.encode("ascii"), hashlib.sha256).hexdigest()
    try:
        response = httpx.post(
            endpoint,
            json=payload,
            headers={
                "Idempotency-Key": delivery_id,
                "X-Payload-Digest": payload_digest,
                "X-Payload-Signature": f"sha256={signature}",
            },
            timeout=httpx.Timeout(5.0, connect=2.0),
            follow_redirects=False,
        )
    except httpx.RequestError as exc:
        return {"status": "retry_pending", "mode": "configured", "error": exc.__class__.__name__, "retryable": True}
    if 200 <= response.status_code < 300:
        body = response.content[:65536]
        return {
            "status": "verified",
            "mode": "configured",
            "http_status": response.status_code,
            "response_digest": hashlib.sha256(body).hexdigest(),
        }
    return {
        "status": "retry_pending" if response.status_code >= 500 else "failed",
        "mode": "configured",
        "http_status": response.status_code,
        "error": "Downstream case-management adapter rejected the delivery.",
        "retryable": response.status_code >= 500,
    }
