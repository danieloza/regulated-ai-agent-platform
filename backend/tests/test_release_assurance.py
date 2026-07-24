import hashlib
import hmac
import json

import pytest
from fastapi.testclient import TestClient

import app.main as main_module
from app.main import (
    Base,
    EnterpriseIdempotencyRecord,
    EnterpriseOutboxEvent,
    ReleaseAssuranceRun,
    SessionLocal,
    app,
    engine,
)


@pytest.fixture()
def assurance_client():
    Base.metadata.create_all(engine)

    def reset() -> None:
        with SessionLocal() as session:
            session.query(ReleaseAssuranceRun).delete()
            session.query(EnterpriseIdempotencyRecord).filter(
                EnterpriseIdempotencyRecord.route.like("%release-assurance%")
            ).delete(synchronize_session=False)
            session.query(EnterpriseOutboxEvent).filter(
                EnterpriseOutboxEvent.event_type.like("enterprise.release-assurance%")
            ).delete(synchronize_session=False)
            session.commit()

    reset()
    with TestClient(app) as client:
        yield client
    reset()


def test_release_assurance_detects_blocking_control_regressions(assurance_client):
    response = assurance_client.post(
        "/api/release-assurance/runs",
        json={"bundle_id": "operations-fast-path", "initiated_by": "release.operator"},
    )
    assert response.status_code == 200, response.text
    run = response.json()["run"]

    assert run["status"] == "blocked"
    assert run["gate_decision"] == "no_go"
    assert run["readiness_score"] < 60
    assert run["blast_radius"]["reachable_records"] == 1042
    assert {item["id"] for item in run["blockers"]} >= {"POL-REPLAY-01", "HITL-04"}
    assert run["runtime_change_applied"] is False

    rejected_approval = assurance_client.post(
        f"/api/release-assurance/runs/{run['id']}/decision",
        json={
            "action": "approve",
            "operator_id": "risk.approver",
            "comment": "I reviewed the candidate and accept the modeled residual risk.",
        },
    )
    assert rejected_approval.status_code == 409


def test_release_assurance_requires_maker_checker_and_exports_attestation(assurance_client, monkeypatch):
    monkeypatch.setenv("RELEASE_ATTESTATION_KEY", "test-only-attestation-key")
    created = assurance_client.post(
        "/api/release-assurance/runs",
        json={"bundle_id": "guardrail-v2", "initiated_by": "release.operator"},
    )
    assert created.status_code == 200, created.text
    run = created.json()["run"]
    assert run["status"] == "awaiting_approval"
    assert run["gate_decision"] == "approval_required"
    assert not run["blockers"]

    self_approval = assurance_client.post(
        f"/api/release-assurance/runs/{run['id']}/decision",
        json={
            "action": "approve",
            "operator_id": "release.operator",
            "comment": "The evidence, rollback contract, and release controls have been reviewed.",
        },
    )
    assert self_approval.status_code == 409

    approved = assurance_client.post(
        f"/api/release-assurance/runs/{run['id']}/decision",
        json={
            "action": "approve",
            "operator_id": "risk.approver",
            "comment": "Independent review confirms the evidence, rollback contract, and release controls.",
        },
    )
    assert approved.status_code == 200, approved.text
    payload = approved.json()
    assert payload["run"]["status"] == "approved"
    assert payload["run"]["gate_decision"] == "go"
    assert payload["run"]["attestation_available"] is True
    assert payload["runtime_change_applied"] is False
    assert payload["attestation"]["execution"]["deployment_performed"] is False

    export = assurance_client.get(f"/api/release-assurance/runs/{run['id']}/attestation")
    assert export.status_code == 200
    assert export.headers["x-attestation-sha256"]
    assert export.json()["integrity"]["digest"] == payload["run"]["attestation_digest"]
    canonical_manifest = json.dumps(
        export.json()["certification_manifest"],
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    expected_digest = hmac.new(
        b"test-only-attestation-key",
        canonical_manifest.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    assert hmac.compare_digest(export.json()["integrity"]["digest"], expected_digest)


def test_release_assurance_payloads_are_strict(assurance_client):
    response = assurance_client.post(
        "/api/release-assurance/runs",
        json={
            "bundle_id": "guardrail-v2",
            "initiated_by": "release.operator",
            "unexpected_runtime_action": "deploy",
        },
    )
    assert response.status_code == 422


def test_production_attestation_fails_closed_without_strong_key_configuration(assurance_client, monkeypatch):
    monkeypatch.setattr(main_module, "IS_PRODUCTION", True)
    monkeypatch.delenv("RELEASE_ATTESTATION_KEY", raising=False)
    monkeypatch.delenv("RELEASE_ATTESTATION_KEY_ID", raising=False)
    created = assurance_client.post(
        "/api/release-assurance/runs",
        json={"bundle_id": "guardrail-v2", "initiated_by": "release.operator"},
    )
    run_id = created.json()["run"]["id"]
    decision = assurance_client.post(
        f"/api/release-assurance/runs/{run_id}/decision",
        json={
            "action": "approve",
            "operator_id": "risk.approver",
            "comment": "Independent reviewer verified the complete release evidence.",
        },
    )
    assert decision.status_code == 503
    refreshed = assurance_client.get(f"/api/release-assurance?run_id={run_id}").json()["selected"]
    assert refreshed["status"] == "awaiting_approval"
    assert refreshed["attestation_available"] is False


def test_enterprise_release_assurance_enforces_rbac_and_idempotency(assurance_client, monkeypatch):
    credentials = [
        {
            "subject": "release.viewer",
            "sha256": hashlib.sha256(b"release-viewer-key").hexdigest(),
            "role": "viewer",
            "tenants": ["demo"],
        },
        {
            "subject": "release.operator",
            "sha256": hashlib.sha256(b"release-operator-key").hexdigest(),
            "role": "operator",
            "tenants": ["demo"],
        },
        {
            "subject": "release.approver",
            "sha256": hashlib.sha256(b"release-approver-key").hexdigest(),
            "role": "approver",
            "tenants": ["demo"],
        },
    ]
    monkeypatch.setenv("ENTERPRISE_API_CREDENTIALS", json.dumps(credentials))
    monkeypatch.setenv("ENTERPRISE_RESOURCE_TENANT", "demo")
    monkeypatch.setenv("RELEASE_ATTESTATION_KEY", "test-only-attestation-key")
    viewer = {"X-API-Key": "release-viewer-key", "X-Tenant-ID": "demo"}
    operator = {"X-API-Key": "release-operator-key", "X-Tenant-ID": "demo"}
    approver = {"X-API-Key": "release-approver-key", "X-Tenant-ID": "demo"}

    denied = assurance_client.post(
        "/api/v1/release-assurance/runs",
        headers={**viewer, "Idempotency-Key": "release-cert-viewer"},
        json={"bundle_id": "guardrail-v2"},
    )
    assert denied.status_code == 403

    created = assurance_client.post(
        "/api/v1/release-assurance/runs",
        headers={**operator, "Idempotency-Key": "release-cert-001"},
        json={"bundle_id": "guardrail-v2"},
    )
    assert created.status_code == 200, created.text
    assert created.json()["enterprise_meta"]["idempotency_replayed"] is False
    run_id = created.json()["run"]["id"]

    replayed = assurance_client.post(
        "/api/v1/release-assurance/runs",
        headers={**operator, "Idempotency-Key": "release-cert-001"},
        json={"bundle_id": "guardrail-v2"},
    )
    assert replayed.status_code == 200
    assert replayed.json()["enterprise_meta"]["idempotency_replayed"] is True
    assert replayed.json()["run"]["id"] == run_id

    approved = assurance_client.post(
        f"/api/v1/release-assurance/runs/{run_id}/decisions",
        headers={**approver, "Idempotency-Key": "release-decision-001"},
        json={
            "action": "approve",
            "comment": "Independent enterprise reviewer verified the complete certification evidence.",
        },
    )
    assert approved.status_code == 200, approved.text
    assert approved.json()["run"]["gate_decision"] == "go"
    assert approved.json()["run"]["runtime_change_applied"] is False

    attestation = assurance_client.get(
        f"/api/v1/release-assurance/runs/{run_id}/attestation",
        headers=viewer,
    )
    assert attestation.status_code == 200
    assert attestation.json()["tenant_id"] == "demo"
    assert attestation.json()["execution"]["deployment_performed"] is False
