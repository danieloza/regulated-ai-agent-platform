from __future__ import annotations

import hashlib
import hmac
import json
import os
from dataclasses import dataclass
from typing import Callable
from urllib.parse import urlparse

import jwt
from fastapi import Depends, Header, HTTPException
from jwt import PyJWKClient, PyJWKSet


ROLE_LEVEL = {"viewer": 10, "operator": 20, "approver": 30, "admin": 40}


@dataclass(frozen=True)
class EnterprisePrincipal:
    subject: str
    role: str
    tenant_id: str
    key_fingerprint: str
    auth_method: str = "api_key"
    assurance_level: str = "workload"
    groups: tuple[str, ...] = ()


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


def _json_environment(name: str, default):
    raw = os.getenv(name, "")
    if not raw:
        return default
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=503, detail=f"{name} configuration is invalid.") from exc


def _oidc_signing_key(token: str):
    static_jwks = _json_environment("OIDC_JWKS_JSON", None)
    if static_jwks:
        try:
            key_set = PyJWKSet.from_dict(static_jwks)
            key_id = jwt.get_unverified_header(token).get("kid")
        except (jwt.PyJWTError, KeyError, TypeError, ValueError) as exc:
            raise HTTPException(status_code=401, detail="OIDC token header or signing-key set is invalid.") from exc
        for key in key_set.keys:
            if key.key_id == key_id:
                return key.key
        raise HTTPException(status_code=401, detail="OIDC signing key is not trusted.")

    jwks_url = os.getenv("OIDC_JWKS_URL", "").strip()
    if not jwks_url:
        raise HTTPException(status_code=503, detail="OIDC signing keys are not configured.")
    parsed = urlparse(jwks_url)
    app_env = os.getenv("APP_ENV", "development").lower()
    is_local_dev = app_env != "production" and parsed.hostname in {"127.0.0.1", "localhost"}
    if parsed.scheme != "https" and not (is_local_dev and parsed.scheme == "http"):
        raise HTTPException(status_code=503, detail="OIDC JWKS URL must use HTTPS outside local development.")
    try:
        return PyJWKClient(jwks_url, cache_keys=True, timeout=5).get_signing_key_from_jwt(token).key
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=401, detail="OIDC signing key could not be resolved.") from exc


def _role_from_claims(claims: dict) -> tuple[str, tuple[str, ...]]:
    groups_claim = os.getenv("OIDC_GROUPS_CLAIM", "groups")
    raw_groups = claims.get(groups_claim, [])
    groups = tuple(str(item) for item in (raw_groups if isinstance(raw_groups, list) else [raw_groups]) if item)
    mapping = _json_environment("OIDC_GROUP_ROLE_MAP", {})
    mapped_roles = [str(mapping[group]) for group in groups if group in mapping and str(mapping[group]) in ROLE_LEVEL]

    roles_claim = os.getenv("OIDC_ROLES_CLAIM", "roles")
    raw_roles = claims.get(roles_claim, [])
    direct_roles = [str(item) for item in (raw_roles if isinstance(raw_roles, list) else [raw_roles]) if str(item) in ROLE_LEVEL]
    candidates = mapped_roles + direct_roles
    if not candidates:
        raise HTTPException(status_code=403, detail="OIDC identity is not mapped to an enterprise role.")
    return max(candidates, key=lambda role: ROLE_LEVEL[role]), groups


def _assurance_from_claims(claims: dict) -> str:
    acr = str(claims.get("acr", "")).lower()
    raw_amr = claims.get("amr", [])
    amr = {str(item).lower() for item in (raw_amr if isinstance(raw_amr, list) else [raw_amr])}
    if "mfa" in amr or "aal2" in acr or "multi-factor" in acr:
        return "aal2"
    return "aal1"


def _authenticate_oidc(token: str, tenant_id: str) -> EnterprisePrincipal:
    issuer = os.getenv("OIDC_ISSUER", "").strip()
    audience = os.getenv("OIDC_AUDIENCE", "").strip()
    if not issuer or not audience:
        raise HTTPException(status_code=503, detail="OIDC issuer and audience are not configured.")
    allowed_algorithms = [
        item.strip()
        for item in os.getenv("OIDC_ALLOWED_ALGORITHMS", "RS256").split(",")
        if item.strip() in {"RS256", "RS384", "RS512", "ES256", "ES384", "ES512"}
    ]
    if not allowed_algorithms:
        raise HTTPException(status_code=503, detail="OIDC algorithm allowlist is invalid.")
    try:
        claims = jwt.decode(
            token,
            _oidc_signing_key(token),
            algorithms=allowed_algorithms,
            audience=audience,
            issuer=issuer,
            options={"require": ["exp", "iat", "sub"]},
            leeway=30,
        )
    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(status_code=401, detail="OIDC token has expired.", headers={"WWW-Authenticate": "Bearer"}) from exc
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=401, detail="OIDC token validation failed.", headers={"WWW-Authenticate": "Bearer"}) from exc

    tenant_claim = os.getenv("OIDC_TENANT_CLAIM", "tenant_ids")
    raw_tenants = claims.get(tenant_claim, [])
    tenants = {str(item) for item in (raw_tenants if isinstance(raw_tenants, list) else [raw_tenants]) if item}
    if tenant_id not in tenants:
        raise HTTPException(status_code=403, detail="OIDC identity is not authorized for this tenant.")
    role, groups = _role_from_claims(claims)
    return EnterprisePrincipal(
        subject=str(claims["sub"]),
        role=role,
        tenant_id=tenant_id,
        key_fingerprint=api_key_digest(token)[:12],
        auth_method="oidc",
        assurance_level=_assurance_from_claims(claims),
        groups=groups,
    )


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

    if authorization and authorization.lower().startswith("bearer ") and key.count(".") == 2 and os.getenv("OIDC_ISSUER"):
        return _authenticate_oidc(key, x_tenant_id)

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
                auth_method="api_key",
                assurance_level="workload",
            )
    raise HTTPException(status_code=401, detail="Invalid enterprise API credential.", headers={"WWW-Authenticate": "Bearer"})


def require_role(minimum_role: str) -> Callable:
    minimum = ROLE_LEVEL[minimum_role]

    def dependency(principal: EnterprisePrincipal = Depends(authenticate_enterprise)) -> EnterprisePrincipal:
        if ROLE_LEVEL[principal.role] < minimum:
            raise HTTPException(status_code=403, detail=f"Role {minimum_role} or higher is required.")
        return principal

    return dependency
