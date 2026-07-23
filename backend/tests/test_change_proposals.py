import hashlib
import json

import pytest
from fastapi.testclient import TestClient

from app.main import ChangeProposal, EnterpriseIdempotencyRecord, EnterpriseOutboxEvent, SessionLocal, app


@pytest.fixture()
def proposal_client():
    def reset() -> None:
        with SessionLocal() as session:
            session.query(ChangeProposal).delete()
            session.query(EnterpriseIdempotencyRecord).delete()
            session.query(EnterpriseOutboxEvent).filter(
                EnterpriseOutboxEvent.event_type.like("enterprise.change-proposal%")
            ).delete(synchronize_session=False)
            session.commit()

    reset()
    with TestClient(app) as client:
        yield client
    reset()


def test_change_proposal_detection_is_persistent_and_idempotent(proposal_client):
    with SessionLocal() as session:
        session.query(ChangeProposal).delete()
        session.commit()

    first = proposal_client.post(
        "/api/change-proposals/detect",
        json={"operator_id": "governance.tester"},
    )
    assert first.status_code == 200, first.text
    payload = first.json()
    assert payload["detection"]["created"] == 4
    assert payload["metrics"]["open"] == 4
    assert payload["metrics"]["high_priority"] == 2
    assert payload["operating_mode"]["execution"] == "not_executed"
    assert {item["source_type"] for item in payload["proposals"]} == {
        "policy_replay",
        "knowledge_change",
        "security_eval",
        "approval_queue",
    }
    fingerprints = {item["fingerprint"] for item in payload["proposals"]}

    replay = proposal_client.post(
        "/api/change-proposals/detect",
        json={"operator_id": "governance.tester"},
    )
    assert replay.status_code == 200
    assert replay.json()["detection"]["created"] == 0
    assert {item["fingerprint"] for item in replay.json()["proposals"]} == fingerprints


def test_change_proposal_acceptance_creates_handoff_without_runtime_execution(proposal_client):
    listing = proposal_client.get("/api/change-proposals").json()
    proposal = next(item for item in listing["proposals"] if item["source_type"] == "policy_replay")

    missing_rationale = proposal_client.post(
        f"/api/change-proposals/{proposal['id']}/decision",
        json={"action": "accept_for_release", "operator_id": "risk.approver", "comment": "short"},
    )
    assert missing_rationale.status_code == 422

    accepted = proposal_client.post(
        f"/api/change-proposals/{proposal['id']}/decision",
        json={
            "action": "accept_for_release",
            "operator_id": "risk.approver",
            "comment": "Replay evidence and rollback controls reviewed for release planning.",
            "owner": "AI Governance",
        },
    )
    assert accepted.status_code == 200, accepted.text
    payload = accepted.json()
    assert payload["proposal"]["status"] == "accepted_for_release"
    assert payload["proposal"]["execution_state"] == "not_executed"
    assert payload["runtime_change_applied"] is False
    assert payload["release_handoff"]["state"] == "awaiting_release_pipeline"
    assert payload["release_handoff"]["execution_state"] == "not_executed"

    refresh = proposal_client.post(
        "/api/change-proposals/detect",
        json={"operator_id": "governance.tester"},
    )
    preserved = next(item for item in refresh.json()["proposals"] if item["id"] == proposal["id"])
    assert preserved["status"] == "accepted_for_release"
    assert refresh.json()["detection"]["preserved"] == 1


def test_change_proposal_filters_and_evidence_contract(proposal_client):
    response = proposal_client.get("/api/change-proposals?source_type=knowledge_change&status=new")
    assert response.status_code == 200
    proposals = response.json()["proposals"]
    assert len(proposals) == 1
    proposal = proposals[0]
    assert proposal["affected_runs"] >= 18
    assert proposal["proposed_diff"]["current"] != proposal["proposed_diff"]["candidate"]
    assert proposal["evaluation_plan"]
    assert proposal["required_approvals"]
    assert proposal["rollback_plan"]
    assert all("state" in item for item in proposal["evidence"])


def test_enterprise_change_proposal_api_enforces_rbac_and_idempotency(proposal_client, monkeypatch):
    credentials = [
        {
            "subject": "proposal.viewer",
            "sha256": hashlib.sha256(b"proposal-viewer-key").hexdigest(),
            "role": "viewer",
            "tenants": ["demo"],
        },
        {
            "subject": "proposal.operator",
            "sha256": hashlib.sha256(b"proposal-operator-key").hexdigest(),
            "role": "operator",
            "tenants": ["demo"],
        },
        {
            "subject": "proposal.approver",
            "sha256": hashlib.sha256(b"proposal-approver-key").hexdigest(),
            "role": "approver",
            "tenants": ["demo"],
        },
    ]
    monkeypatch.setenv("ENTERPRISE_API_CREDENTIALS", json.dumps(credentials))
    monkeypatch.setenv("ENTERPRISE_RESOURCE_TENANT", "demo")
    viewer = {"X-API-Key": "proposal-viewer-key", "X-Tenant-ID": "demo"}
    operator = {"X-API-Key": "proposal-operator-key", "X-Tenant-ID": "demo"}
    approver = {"X-API-Key": "proposal-approver-key", "X-Tenant-ID": "demo"}

    listing = proposal_client.get("/api/v1/change-proposals?limit=2", headers=viewer)
    assert listing.status_code == 200
    assert listing.json()["pagination"]["total"] == 4
    assert len(listing.json()["data"]) == 2

    denied = proposal_client.post(
        "/api/v1/change-proposals/detect",
        headers={**viewer, "Idempotency-Key": "proposal-detect-viewer"},
    )
    assert denied.status_code == 403

    detected = proposal_client.post(
        "/api/v1/change-proposals/detect",
        headers={**operator, "Idempotency-Key": "proposal-detect-001"},
    )
    assert detected.status_code == 200
    assert detected.json()["enterprise_meta"]["idempotency_replayed"] is False
    replayed = proposal_client.post(
        "/api/v1/change-proposals/detect",
        headers={**operator, "Idempotency-Key": "proposal-detect-001"},
    )
    assert replayed.status_code == 200
    assert replayed.json()["enterprise_meta"]["idempotency_replayed"] is True

    proposal_id = listing.json()["data"][0]["id"]
    decision = proposal_client.post(
        f"/api/v1/change-proposals/{proposal_id}/decisions",
        headers={**approver, "Idempotency-Key": "proposal-decision-001"},
        json={
            "action": "request_evidence",
            "comment": "Additional operational baseline evidence is required before release.",
            "owner": "AI Governance",
        },
    )
    assert decision.status_code == 200, decision.text
    assert decision.json()["proposal"]["status"] == "needs_evidence"
    assert decision.json()["proposal"]["execution_state"] == "not_executed"
