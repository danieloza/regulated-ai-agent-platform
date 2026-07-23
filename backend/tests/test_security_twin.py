import hashlib
import json

import pytest
from fastapi.testclient import TestClient

from app.main import (
    AuditEvent,
    EnterpriseIdempotencyRecord,
    EnterpriseOutboxEvent,
    SecurityTwinSimulation,
    SessionLocal,
    app,
)


@pytest.fixture()
def security_twin_client():
    with TestClient(app) as client:
        with SessionLocal() as session:
            session.query(SecurityTwinSimulation).delete()
            session.query(EnterpriseIdempotencyRecord).delete()
            session.query(EnterpriseOutboxEvent).filter(
                EnterpriseOutboxEvent.event_type.like("enterprise.security.%")
            ).delete(synchronize_session=False)
            session.query(AuditEvent).filter(
                AuditEvent.event_type.like("security_%")
            ).delete(synchronize_session=False)
            session.commit()
        yield client
        with SessionLocal() as session:
            session.query(SecurityTwinSimulation).delete()
            session.query(EnterpriseIdempotencyRecord).delete()
            session.query(EnterpriseOutboxEvent).filter(
                EnterpriseOutboxEvent.event_type.like("enterprise.security.%")
            ).delete(synchronize_session=False)
            session.commit()


def simulate(client, scenario_id, candidate_profile):
    response = client.post(
        "/api/security/attack-paths/simulate",
        json={
            "scenario_id": scenario_id,
            "candidate_profile": candidate_profile,
            "operator_id": "security.tester",
        },
    )
    assert response.status_code == 200, response.text
    return response.json()["simulation"]


def test_security_twin_detects_scope_escalation_and_blast_radius(security_twin_client):
    baseline = simulate(security_twin_client, "tool_scope_escalation", "current")
    candidate = simulate(
        security_twin_client,
        "tool_scope_escalation",
        "overprivileged_scope",
    )

    assert baseline["outcome"] == "blocked"
    assert baseline["blast_radius"]["candidate"]["reachable_records"] == 0
    assert candidate["outcome"] == "asset_reached"
    assert candidate["severity"] == "critical"
    assert candidate["blast_radius"]["candidate"]["reachable_records"] == 18
    assert candidate["blast_radius"]["diff"] == {"systems": 1, "records": 18}
    assert any(
        control["id"] == "SCOPE-03" and control["state"] == "bypassed"
        for control in candidate["controls"]
    )
    assert candidate["runtime_change_applied"] is False


def test_security_twin_containment_requires_approval_and_breaks_path(security_twin_client):
    simulation = simulate(
        security_twin_client,
        "approval_bypass",
        "approval_bypass",
    )

    premature = security_twin_client.post(
        f"/api/security/containments/{simulation['id']}/decision",
        json={
            "action": "approve",
            "operator_id": "security.approver",
            "comment": "Containment reviewed against the modeled attack path.",
        },
    )
    assert premature.status_code == 409

    planned = security_twin_client.post(
        f"/api/security/attack-paths/{simulation['id']}/containment-plan",
        json={"operator_id": "security.operator"},
    )
    assert planned.status_code == 200, planned.text
    assert planned.json()["simulation"]["containment_plan"]["state"] == "awaiting_approval"
    assert planned.json()["runtime_change_applied"] is False

    approved = security_twin_client.post(
        f"/api/security/containments/{simulation['id']}/decision",
        json={
            "action": "approve",
            "operator_id": "security.approver",
            "comment": "Sandbox actions are scoped, attributable, and ready for replay.",
        },
    )
    assert approved.status_code == 200, approved.text
    assert approved.json()["sandbox_containment_armed"] is True
    assert approved.json()["runtime_change_applied"] is False

    verified = security_twin_client.post(
        f"/api/security/attack-paths/{simulation['id']}/verify",
        json={"operator_id": "security.operator"},
    )
    assert verified.status_code == 200, verified.text
    payload = verified.json()
    assert payload["verification"]["effective"] is True
    assert payload["verification"]["path_broken"] is True
    assert payload["verification"]["before"]["reachable_records"] == 18
    assert payload["verification"]["after"]["reachable_records"] == 0
    assert payload["simulation"]["status"] == "verified"
    assert all(
        action["state"] == "verified"
        for action in payload["simulation"]["containment_plan"]["actions"]
    )

    evidence = security_twin_client.get(
        f"/api/security/attack-paths/{simulation['id']}/evidence"
    )
    assert evidence.status_code == 200
    assert evidence.json()["integrity"]["digest"] == payload["simulation"]["evidence_digest"]
    assert evidence.json()["simulation"]["runtime_change_applied"] is False


def test_cross_tenant_path_remains_unreachable_with_current_controls(security_twin_client):
    simulation = simulate(security_twin_client, "cross_tenant_access", "current")

    assert simulation["outcome"] == "blocked"
    assert simulation["blast_radius"]["candidate"]["reachable_records"] == 0
    tenant_control = next(
        control for control in simulation["controls"] if control["id"] == "TENANT-01"
    )
    assert tenant_control["state"] == "enforced"
    assert all(
        node["state"] != "reached"
        for node in simulation["nodes"]
        if node["type"] == "asset"
    )


def test_enterprise_security_twin_enforces_rbac_and_idempotency(
    security_twin_client,
    monkeypatch,
):
    credentials = [
        {
            "subject": "security.viewer",
            "sha256": hashlib.sha256(b"security-viewer-key").hexdigest(),
            "role": "viewer",
            "tenants": ["demo"],
        },
        {
            "subject": "security.operator",
            "sha256": hashlib.sha256(b"security-operator-key").hexdigest(),
            "role": "operator",
            "tenants": ["demo"],
        },
        {
            "subject": "security.approver",
            "sha256": hashlib.sha256(b"security-approver-key").hexdigest(),
            "role": "approver",
            "tenants": ["demo"],
        },
    ]
    monkeypatch.setenv("ENTERPRISE_API_CREDENTIALS", json.dumps(credentials))
    monkeypatch.setenv("ENTERPRISE_RESOURCE_TENANT", "demo")
    viewer = {"X-API-Key": "security-viewer-key", "X-Tenant-ID": "demo"}
    operator = {"X-API-Key": "security-operator-key", "X-Tenant-ID": "demo"}

    denied = security_twin_client.post(
        "/api/v1/security/attack-paths/simulate",
        headers={**viewer, "Idempotency-Key": "security-sim-viewer"},
        json={
            "scenario_id": "tool_scope_escalation",
            "candidate_profile": "overprivileged_scope",
        },
    )
    assert denied.status_code == 403

    request = {
        "scenario_id": "tool_scope_escalation",
        "candidate_profile": "overprivileged_scope",
    }
    first = security_twin_client.post(
        "/api/v1/security/attack-paths/simulate",
        headers={**operator, "Idempotency-Key": "security-sim-001"},
        json=request,
    )
    assert first.status_code == 200, first.text
    assert first.json()["enterprise_meta"]["idempotency_replayed"] is False
    assert first.json()["simulation"]["created_by"] == "security.operator"

    replayed = security_twin_client.post(
        "/api/v1/security/attack-paths/simulate",
        headers={**operator, "Idempotency-Key": "security-sim-001"},
        json=request,
    )
    assert replayed.status_code == 200
    assert replayed.json()["enterprise_meta"]["idempotency_replayed"] is True
    assert replayed.json()["simulation"]["id"] == first.json()["simulation"]["id"]

    listing = security_twin_client.get(
        "/api/v1/security/attack-paths",
        headers=viewer,
    )
    assert listing.status_code == 200
    assert listing.json()["pagination"]["total"] == 1
    assert listing.json()["tenant_id"] == "demo"
