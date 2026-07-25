import hashlib
import json

import pytest
from fastapi.testclient import TestClient

from app.main import (
    Base,
    CodeAssuranceRun,
    EnterpriseIdempotencyRecord,
    EnterpriseOutboxEvent,
    ReleaseAssuranceRun,
    SessionLocal,
    app,
    engine,
)


COMMIT_SHA = "a" * 40
ARTIFACT_DIGEST = "b" * 64


@pytest.fixture()
def code_assurance_client():
    Base.metadata.create_all(engine)

    def reset() -> None:
        with SessionLocal() as session:
            session.query(ReleaseAssuranceRun).delete()
            session.query(CodeAssuranceRun).delete()
            session.query(EnterpriseIdempotencyRecord).filter(
                EnterpriseIdempotencyRecord.route.like("%code-assurance%")
            ).delete(synchronize_session=False)
            session.query(EnterpriseOutboxEvent).filter(
                EnterpriseOutboxEvent.event_type.like("%code-assurance%")
            ).delete(synchronize_session=False)
            session.commit()

    reset()
    with TestClient(app) as client:
        reset()
        yield client
    reset()


def import_evidence(client):
    response = client.post(
        "/api/code-assurance/runs",
        json={
            "repository_id": "regulated-ai-agent-platform",
            "commit_sha": COMMIT_SHA,
            "scanner_profile": "guardrail-regression",
            "initiated_by": "code.operator",
        },
    )
    assert response.status_code == 200, response.text
    return response.json()["run"]


def test_code_assurance_binds_sarif_to_immutable_commit_and_never_mutates_repo(code_assurance_client):
    run = import_evidence(code_assurance_client)

    assert run["commit_sha"] == COMMIT_SHA
    assert run["sarif_summary"]["schema"] == "SARIF 2.1.0"
    assert run["sarif_summary"]["severity_counts"]["critical"] == 1
    assert run["status"] == "awaiting_remediation_approval"
    assert run["policy_decision"] == "approval_required"
    assert run["repository_cloned"] is False
    assert run["patch_applied"] is False
    assert run["runtime_change_applied"] is False
    assert len(run["evidence_digest"]) == 64


def test_code_assurance_requires_maker_checker_and_complete_validation(code_assurance_client):
    run = import_evidence(code_assurance_client)

    self_approval = code_assurance_client.post(
        f"/api/code-assurance/runs/{run['id']}/remediation-decision",
        json={
            "action": "approve",
            "operator_id": "code.operator",
            "comment": "I reviewed the proposed remediation and validation plan.",
        },
    )
    assert self_approval.status_code == 409

    premature = code_assurance_client.post(
        f"/api/code-assurance/runs/{run['id']}/validation-evidence",
        json={
            "operator_id": "release.operator",
            "artifact_digest": ARTIFACT_DIGEST,
            "build_passed": True,
            "tests_passed": True,
            "security_evals_passed": True,
            "test_count": 67,
        },
    )
    assert premature.status_code == 409

    approval = code_assurance_client.post(
        f"/api/code-assurance/runs/{run['id']}/remediation-decision",
        json={
            "action": "approve",
            "operator_id": "security.approver",
            "comment": "Independent review confirms the remediation scope and validation plan.",
        },
    )
    assert approval.status_code == 200, approval.text
    assert approval.json()["run"]["status"] == "approved_for_validation"
    assert approval.json()["run"]["patch_applied"] is False

    failed = code_assurance_client.post(
        f"/api/code-assurance/runs/{run['id']}/validation-evidence",
        json={
            "operator_id": "release.operator",
            "artifact_digest": ARTIFACT_DIGEST,
            "build_passed": True,
            "tests_passed": True,
            "security_evals_passed": False,
            "test_count": 67,
        },
    )
    assert failed.status_code == 200
    assert failed.json()["run"]["status"] == "validation_failed"
    assert failed.json()["release_gate_eligible"] is False


def test_validated_code_assurance_can_feed_release_gate(code_assurance_client):
    run = import_evidence(code_assurance_client)
    code_assurance_client.post(
        f"/api/code-assurance/runs/{run['id']}/remediation-decision",
        json={
            "action": "approve",
            "operator_id": "security.approver",
            "comment": "Independent review confirms the bounded remediation proposal.",
        },
    )
    validated = code_assurance_client.post(
        f"/api/code-assurance/runs/{run['id']}/validation-evidence",
        json={
            "operator_id": "release.operator",
            "artifact_digest": ARTIFACT_DIGEST,
            "build_passed": True,
            "tests_passed": True,
            "security_evals_passed": True,
            "test_count": 67,
        },
    )
    assert validated.status_code == 200
    assert validated.json()["run"]["status"] == "validated"

    gate = code_assurance_client.post(
        "/api/release-assurance/runs",
        json={"bundle_id": "code-assurance-v1", "initiated_by": "release.operator"},
    )
    assert gate.status_code == 200, gate.text
    assert gate.json()["run"]["gate_decision"] == "approval_required"
    assert not gate.json()["run"]["blockers"]


def test_code_assurance_contract_is_strict_and_enterprise_api_is_idempotent(code_assurance_client, monkeypatch):
    invalid = code_assurance_client.post(
        "/api/code-assurance/runs",
        json={
            "repository_id": "regulated-ai-agent-platform",
            "commit_sha": COMMIT_SHA,
            "scanner_profile": "guardrail-regression",
            "initiated_by": "code.operator",
            "repository_url": "https://untrusted.example/repository.git",
        },
    )
    assert invalid.status_code == 422

    credentials = [
        {
            "subject": "code.operator",
            "sha256": hashlib.sha256(b"code-operator-key").hexdigest(),
            "role": "operator",
            "tenants": ["demo"],
        }
    ]
    monkeypatch.setenv("ENTERPRISE_API_CREDENTIALS", json.dumps(credentials))
    monkeypatch.setenv("ENTERPRISE_RESOURCE_TENANT", "demo")
    headers = {
        "X-API-Key": "code-operator-key",
        "X-Tenant-ID": "demo",
        "Idempotency-Key": "code-import-001",
    }
    body = {
        "repository_id": "regulated-ai-agent-platform",
        "commit_sha": COMMIT_SHA,
        "scanner_profile": "guardrail-regression",
    }
    first = code_assurance_client.post("/api/v1/code-assurance/runs", headers=headers, json=body)
    assert first.status_code == 200, first.text
    replayed = code_assurance_client.post("/api/v1/code-assurance/runs", headers=headers, json=body)
    assert replayed.status_code == 200
    assert replayed.json()["enterprise_meta"]["idempotency_replayed"] is True
    assert replayed.json()["run"]["id"] == first.json()["run"]["id"]
