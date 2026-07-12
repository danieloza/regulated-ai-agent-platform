from __future__ import annotations

import hashlib
import hmac
import json
import os
from dataclasses import dataclass
from typing import Callable

from fastapi import Depends, Header, HTTPException


ROLE_LEVEL = {"viewer": 10, "operator": 20, "approver": 30, "admin": 40}


@dataclass(frozen=True)
class EnterprisePrincipal:
    subject: str
    role: str
    tenant_id: str
    key_fingerprint: str


def api_key_digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _configured_credentials() -> list[dict]:
    raw = os.getenv("ENTERPRISE_API_CREDENTIALS", "")
    if not raw:
        raise HTTPException(status_code=503, detail="Enterprise API credentials are not configured.")
    try:
        credentials = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=503, detail="Enterprise API credential configuration is invalid.") from exc
    if not isinstance(credentials, list):
        raise HTTPException(status_code=503, detail="Enterprise API credential configuration must be a list.")
    return credentials


def authenticate_enterprise(
    authorization: str | None = Header(default=None),
    x_api_key: str | None = Header(default=None),
    x_tenant_id: str | None = Header(default=None),
) -> EnterprisePrincipal:
    key = x_api_key
    if authorization and authorization.lower().startswith("bearer "):
        key = authorization[7:].strip()
    if not key:
        raise HTTPException(status_code=401, detail="Missing enterprise API credential.", headers={"WWW-Authenticate": "Bearer"})
    if not x_tenant_id:
        raise HTTPException(status_code=400, detail="X-Tenant-ID is required.")

    presented = api_key_digest(key)
    for credential in _configured_credentials():
        expected = str(credential.get("sha256", ""))
        role = str(credential.get("role", ""))
        tenants = credential.get("tenants", [])
        if expected and hmac.compare_digest(presented, expected):
            if role not in ROLE_LEVEL:
                raise HTTPException(status_code=503, detail="Enterprise API credential role is invalid.")
            if x_tenant_id not in tenants:
                raise HTTPException(status_code=403, detail="Credential is not authorized for this tenant.")
            return EnterprisePrincipal(
                subject=str(credential.get("subject", "service-account")),
                role=role,
                tenant_id=x_tenant_id,
                key_fingerprint=presented[:12],
            )
    raise HTTPException(status_code=401, detail="Invalid enterprise API credential.", headers={"WWW-Authenticate": "Bearer"})


def require_role(minimum_role: str) -> Callable:
    minimum = ROLE_LEVEL[minimum_role]

    def dependency(principal: EnterprisePrincipal = Depends(authenticate_enterprise)) -> EnterprisePrincipal:
        if ROLE_LEVEL[principal.role] < minimum:
            raise HTTPException(status_code=403, detail=f"Role {minimum_role} or higher is required.")
        return principal

    return dependency
