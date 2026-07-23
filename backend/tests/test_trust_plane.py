import base64
import hashlib
import json
from datetime import UTC, datetime, timedelta

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi.testclient import TestClient

from app.main import (
    AuditEvent,
    BreakGlassGrant,
    EnterpriseIdempotencyRecord,
    EnterpriseOutboxEvent,
    IdentityAccessDecision,
    IntegrationDelivery,
    SessionLocal,
    TrustApproval,
    app,
)


def actor(subject: str, role: str, assurance: str = "aal2", auth_method: str = "oidc") -> dict:
    return {
        "subject": subject,
        "role": role,
        "tenant_id": "demo",
        "auth_method": auth_method,
        "assurance_level": assurance,
        "groups": [f"{role.title()}-Group"],
    }


@pytest.fixture()
def trust_client():
    def reset() -> None:
        with SessionLocal() as session:
            session.query(IntegrationDelivery).delete()
            session.query(TrustApproval).delete()
            session.query(IdentityAccessDecision).delete()
            session.query(BreakGlassGrant).delete()
            session.query(EnterpriseIdempotencyRecord).delete()
            session.query(EnterpriseOutboxEvent).filter(
                EnterpriseOutboxEvent.event_type.like("enterprise.trust.%")
            ).delete(synchronize_session=False)
            session.query(AuditEvent).filter(
                AuditEvent.event_type.in_(
                    [
                        "identity_access_evaluated",
                        "trust_approval_requested",
                        "trust_approval_decided",
                        "integration_delivery_queued",
                        "integration_delivery_dispatched",
                        "break_glass_activated",
                    ]
                )
            ).delete(synchronize_session=False)
            session.commit()

    with TestClient(app) as client:
        reset()
        yield client
        reset()


def test_high_risk_access_requires_aal2_and_independent_approval(trust_client):
    denied = trust_client.post(
        "/api/trust/access-decisions/evaluate",
        json={
            "actor": actor("alex.morgan", "operator", assurance="aal1"),
            "requested_tenant": "demo",
            "action": "case_note.create",
            "resource": "customer/cus-1042/case-notes",
            "payload": {"customer_id": "cus-1042", "note": "KYC verified."},
            "correlation_id": "trace-aal1-denied",
        },
    )
    assert denied.status_code == 200
    assert denied.json()["decision"]["decision"] == "denied"
    assert "step_up_mfa_required" in denied.json()["decision"]["reasons"]

    created = trust_client.post(
        "/api/trust/approvals",
        json={
            "actor": actor("alex.morgan", "operator"),
            "action": "case_note.create",
            "resource": "customer/cus-1042/case-notes",
            "payload": {"customer_id": "cus-1042", "note": "KYC verified."},
            "correlation_id": "trace-maker-checker",
            "expires_minutes": 30,
        },
    )
    assert created.status_code == 200, created.text
    approval = created.json()["approval"]
    assert approval["status"] == "pending"
    assert len(approval["payload_digest"]) == 64

    self_approval = trust_client.post(
        f"/api/trust/approvals/{approval['id']}/decisions",
        json={
            "actor": actor("alex.morgan", "approver"),
            "decision": "approved",
            "expected_payload_digest": approval["payload_digest"],
            "comment": "Attempt to approve the same request should be blocked.",
        },
    )
    assert self_approval.status_code == 409
    assert "Maker-checker" in self_approval.json()["error"]["message"]

    wrong_digest = trust_client.post(
        f"/api/trust/approvals/{approval['id']}/decisions",
        json={
            "actor": actor("marta.chen", "approver"),
            "decision": "approved",
            "expected_payload_digest": "0" * 64,
            "comment": "The digest does not match the reviewed payload.",
        },
    )
    assert wrong_digest.status_code == 409

    approved = trust_client.post(
        f"/api/trust/approvals/{approval['id']}/decisions",
        json={
            "actor": actor("marta.chen", "approver"),
            "decision": "approved",
            "expected_payload_digest": approval["payload_digest"],
            "comment": "Independent review completed against the exact payload and destination.",
        },
    )
    assert approved.status_code == 200, approved.text
    assert approved.json()["approval"]["maker_checker"] is True


def test_approved_payload_enters_durable_delivery_and_verifies_in_sandbox(trust_client, monkeypatch):
    monkeypatch.delenv("CASE_MANAGEMENT_API_URL", raising=False)
    created = trust_client.post(
        "/api/trust/approvals",
        json={
            "actor": actor("alex.morgan", "operator"),
            "action": "case_note.create",
            "resource": "customer/cus-1042/case-notes",
            "payload": {"customer_id": "cus-1042", "note": "Verified KYC outcome."},
            "correlation_id": "trace-durable-delivery",
        },
    ).json()["approval"]
    trust_client.post(
        f"/api/trust/approvals/{created['id']}/decisions",
        json={
            "actor": actor("marta.chen", "approver"),
            "decision": "approved",
            "expected_payload_digest": created["payload_digest"],
            "comment": "Exact payload and business purpose independently reviewed.",
        },
    )

    queued = trust_client.post(
        f"/api/trust/approvals/{created['id']}/execute",
        json={
            "actor": actor("alex.morgan", "operator"),
            "expected_payload_digest": created["payload_digest"],
        },
    )
    assert queued.status_code == 200, queued.text
    delivery = queued.json()["delivery"]
    assert delivery["status"] == "queued"
    assert delivery["mode"] == "sandbox"

    repeated_queue = trust_client.post(
        f"/api/trust/approvals/{created['id']}/execute",
        json={
            "actor": actor("alex.morgan", "operator"),
            "expected_payload_digest": created["payload_digest"],
        },
    )
    assert repeated_queue.status_code == 200
    assert repeated_queue.json()["delivery"]["id"] == delivery["id"]

    dispatched = trust_client.post(
        f"/api/trust/deliveries/{delivery['id']}/dispatch",
        json={"actor": actor("integration.worker", "admin", assurance="workload", auth_method="api_key")},
    )
    assert dispatched.status_code == 200, dispatched.text
    result = dispatched.json()["delivery"]
    assert result["status"] == "verified"
    assert result["attempt_count"] == 1
    assert result["response_digest"]
    assert result["payload_digest"] == created["payload_digest"]

    overview = trust_client.get("/api/trust/overview").json()
    assert overview["metrics"]["maker_checker_percent"] == 100
    assert overview["metrics"]["verified_delivery_percent"] == 100
    assert overview["integration"]["mode"] == "sandbox"


def test_configured_case_management_adapter_sends_integrity_and_idempotency_headers(
    trust_client, monkeypatch
):
    monkeypatch.setenv("CASE_MANAGEMENT_API_URL", "https://cases.example.test/v1/case-notes")
    monkeypatch.setenv("CASE_MANAGEMENT_SIGNING_SECRET", "test-signing-secret-with-at-least-32-characters")
    captured: dict = {}

    class AcceptedResponse:
        status_code = 202
        content = b'{"accepted":true}'

    def fake_post(url, **kwargs):
        captured["url"] = url
        captured.update(kwargs)
        return AcceptedResponse()

    monkeypatch.setattr("app.services.trust_plane.httpx.post", fake_post)
    created = trust_client.post(
        "/api/trust/approvals",
        json={
            "actor": actor("alex.morgan", "operator"),
            "action": "case_note.create",
            "resource": "customer/cus-1042/case-notes",
            "payload": {"customer_id": "cus-1042", "note": "Approved downstream adapter test."},
            "correlation_id": "trace-configured-adapter",
        },
    ).json()["approval"]
    trust_client.post(
        f"/api/trust/approvals/{created['id']}/decisions",
        json={
            "actor": actor("marta.chen", "approver"),
            "decision": "approved",
            "expected_payload_digest": created["payload_digest"],
            "comment": "Verified the configured adapter payload and business purpose.",
        },
    )
    delivery = trust_client.post(
        f"/api/trust/approvals/{created['id']}/execute",
        json={
            "actor": actor("alex.morgan", "operator"),
            "expected_payload_digest": created["payload_digest"],
        },
    ).json()["delivery"]
    dispatched = trust_client.post(
        f"/api/trust/deliveries/{delivery['id']}/dispatch",
        json={"actor": actor("integration.worker", "admin", assurance="workload", auth_method="api_key")},
    )

    assert dispatched.status_code == 200, dispatched.text
    assert dispatched.json()["delivery"]["status"] == "verified"
    assert dispatched.json()["delivery"]["mode"] == "configured"
    assert captured["url"] == "https://cases.example.test/v1/case-notes"
    assert captured["headers"]["Idempotency-Key"] == delivery["id"]
    assert captured["headers"]["X-Payload-Digest"] == created["payload_digest"]
    assert captured["headers"]["X-Payload-Signature"].startswith("sha256=")
    assert captured["follow_redirects"] is False


def test_break_glass_is_short_lived_incident_bound_and_not_self_approved(trust_client):
    blocked = trust_client.post(
        "/api/trust/break-glass",
        json={
            "actor": actor("security.admin", "admin"),
            "subject": "security.admin",
            "incident_id": "INC-2026-0042",
            "scope": "case:read",
            "reason": "Emergency investigation requires temporary access to the affected case.",
            "duration_minutes": 15,
        },
    )
    assert blocked.status_code == 409

    granted = trust_client.post(
        "/api/trust/break-glass",
        json={
            "actor": actor("security.admin", "admin"),
            "subject": "incident.responder",
            "incident_id": "INC-2026-0042",
            "scope": "case:read",
            "reason": "Emergency investigation requires temporary read access to the affected case.",
            "duration_minutes": 15,
        },
    )
    assert granted.status_code == 200, granted.text
    grant = granted.json()["grant"]
    assert grant["status"] == "active"
    assert grant["approved_by"] == "security.admin"
    assert grant["subject"] == "incident.responder"


def b64url_uint(value: int) -> str:
    size = (value.bit_length() + 7) // 8
    return base64.urlsafe_b64encode(value.to_bytes(size, "big")).rstrip(b"=").decode("ascii")


def oidc_configuration(monkeypatch):
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public = private_key.public_key().public_numbers()
    monkeypatch.setenv("OIDC_ISSUER", "https://identity.example.test/tenant")
    monkeypatch.setenv("OIDC_AUDIENCE", "regulated-ai-api")
    monkeypatch.setenv(
        "OIDC_JWKS_JSON",
        json.dumps(
            {
                "keys": [
                    {
                        "kty": "RSA",
                        "kid": "test-key",
                        "use": "sig",
                        "alg": "RS256",
                        "n": b64url_uint(public.n),
                        "e": b64url_uint(public.e),
                    }
                ]
            }
        ),
    )
    monkeypatch.setenv(
        "OIDC_GROUP_ROLE_MAP",
        json.dumps({"AI-Operators": "operator", "Compliance-Approvers": "approver"}),
    )
    return private_key


def oidc_token(private_key, subject: str, group: str, audience: str = "regulated-ai-api") -> str:
    now = datetime.now(UTC)
    return jwt.encode(
        {
            "iss": "https://identity.example.test/tenant",
            "aud": audience,
            "sub": subject,
            "iat": now,
            "exp": now + timedelta(minutes=5),
            "tenant_ids": ["demo"],
            "groups": [group],
            "amr": ["pwd", "mfa"],
            "acr": "aal2",
        },
        private_key,
        algorithm="RS256",
        headers={"kid": "test-key"},
    )


def enterprise_headers(token: str, idempotency_key: str | None = None) -> dict:
    headers = {"Authorization": f"Bearer {token}", "X-Tenant-ID": "demo"}
    if idempotency_key:
        headers["Idempotency-Key"] = idempotency_key
    return headers


def test_oidc_tokens_are_strictly_validated_and_drive_enterprise_maker_checker(trust_client, monkeypatch):
    private_key = oidc_configuration(monkeypatch)
    maker_token = oidc_token(private_key, "alex.morgan", "AI-Operators")
    approver_token = oidc_token(private_key, "marta.chen", "Compliance-Approvers")

    capabilities = trust_client.get("/api/v1/capabilities", headers=enterprise_headers(maker_token))
    assert capabilities.status_code == 200, capabilities.text
    principal = capabilities.json()["principal"]
    assert principal["auth_method"] == "oidc"
    assert principal["assurance_level"] == "aal2"
    assert principal["role"] == "operator"

    invalid_audience = oidc_token(private_key, "alex.morgan", "AI-Operators", audience="another-api")
    rejected = trust_client.get("/api/v1/capabilities", headers=enterprise_headers(invalid_audience))
    assert rejected.status_code == 401

    cross_tenant_headers = enterprise_headers(maker_token)
    cross_tenant_headers["X-Tenant-ID"] = "another-tenant"
    cross_tenant = trust_client.get("/api/v1/capabilities", headers=cross_tenant_headers)
    assert cross_tenant.status_code == 403

    unmapped_token = oidc_token(private_key, "external.contractor", "Unmapped-Group")
    unmapped = trust_client.get("/api/v1/capabilities", headers=enterprise_headers(unmapped_token))
    assert unmapped.status_code == 403

    created = trust_client.post(
        "/api/v1/trust/approvals",
        headers=enterprise_headers(maker_token, "oidc-create-approval-001"),
        json={
            "action": "case_note.create",
            "resource": "customer/cus-1042/case-notes",
            "payload": {"customer_id": "cus-1042", "note": "OIDC-bound approval."},
            "correlation_id": "trace-oidc-approval",
        },
    )
    assert created.status_code == 200, created.text
    approval = created.json()["approval"]

    approved = trust_client.post(
        f"/api/v1/trust/approvals/{approval['id']}/decisions",
        headers=enterprise_headers(approver_token, "oidc-decide-approval-001"),
        json={
            "decision": "approved",
            "expected_payload_digest": approval["payload_digest"],
            "comment": "OIDC AAL2 reviewer verified the exact payload and separation of duties.",
        },
    )
    assert approved.status_code == 200, approved.text
    assert approved.json()["approval"]["approver_subject"] == "marta.chen"
    assert approved.json()["approval"]["maker_checker"] is True


def test_operational_health_and_metrics_are_machine_readable(trust_client, monkeypatch):
    assert trust_client.get("/api/health/live").json()["status"] == "alive"
    readiness = trust_client.get("/api/health/ready")
    assert readiness.status_code == 200
    assert readiness.json()["checks"]["database"] is True

    assert trust_client.get("/api/not-found/high-cardinality-value").status_code == 404
    metrics = trust_client.get("/metrics")
    assert metrics.status_code == 200
    assert "regulated_ai_http_requests_total" in metrics.text
    assert '__unmatched__' in metrics.text
    assert "high-cardinality-value" not in metrics.text
    assert metrics.headers["content-type"].startswith("text/plain")

    monkeypatch.setenv("APP_ENV", "production")
    missing_migration = trust_client.get("/api/health/ready")
    assert missing_migration.status_code == 503
    assert missing_migration.json()["checks"]["database"] is False
    monkeypatch.setenv("APP_ENV", "development")


def test_actor_supplied_trust_demo_routes_fail_closed_in_production(trust_client, monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    response = trust_client.get("/api/trust/overview")
    assert response.status_code == 404
    monkeypatch.setenv("APP_ENV", "development")
