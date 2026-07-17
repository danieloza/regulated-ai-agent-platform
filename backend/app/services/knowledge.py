from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import re
import time
from datetime import UTC, datetime
from typing import Iterable

from cryptography.fernet import Fernet, InvalidToken


WORD_RE = re.compile(r"[a-zA-Z0-9_-]{2,}")
SENTENCE_RE = re.compile(r"(?<=[.!?])\s+|\n+")
SECRET_RE = re.compile(
    r"(?i)(?:api[_ -]?key|access[_ -]?token|client[_ -]?secret|password)\s*[:=]\s*[^\s,;]{6,}"
)
QUANTITY_RE = re.compile(r"\b(?:zero|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|\d+(?:\.\d+)?)\b", re.IGNORECASE)


def _tokens(value: str) -> set[str]:
    return {token.lower() for token in WORD_RE.findall(value)}


def _stable_id(prefix: str, value: str, length: int = 12) -> str:
    return f"{prefix}_{hashlib.sha256(value.encode('utf-8')).hexdigest()[:length]}"


def compile_claims(content: str, source_id: str, owner: str, limit: int = 10) -> list[dict]:
    """Compile reviewable claims without treating the source as executable instructions.

    The local implementation is intentionally deterministic. A company deployment can
    replace this extractor with an approved model while preserving the same review API.
    """
    claims: list[dict] = []
    seen: set[str] = set()
    for raw_sentence in SENTENCE_RE.split(content):
        statement = " ".join(raw_sentence.split()).strip(" -\t")
        if len(statement) < 28 or len(statement) > 600:
            continue
        normalized = statement.casefold().rstrip(".")
        if normalized in seen:
            continue
        seen.add(normalized)
        risk = "high" if any(term in normalized for term in ("must", "shall", "prohibited", "personal data", "retention")) else "medium"
        claims.append(
            {
                "id": _stable_id("clm", f"{source_id}:{normalized}"),
                "statement": statement,
                "normalized": normalized,
                "owner": owner,
                "risk": risk,
                "confidence": 0.94 if risk == "high" else 0.88,
                "source_excerpt": statement,
            }
        )
        if len(claims) >= limit:
            break
    return claims


def find_contradictions(candidate_claims: Iterable[dict], published_claims: Iterable[dict]) -> list[dict]:
    contradictions: list[dict] = []
    existing = list(published_claims)
    for candidate in candidate_claims:
        candidate_tokens = _tokens(candidate["statement"])
        candidate_numbers = {value.casefold() for value in QUANTITY_RE.findall(candidate["statement"])}
        candidate_modals = candidate_tokens & {"must", "shall", "may", "cannot", "prohibited", "optional"}
        for current in existing:
            current_tokens = _tokens(current["statement"])
            union = candidate_tokens | current_tokens
            overlap = len(candidate_tokens & current_tokens) / max(len(union), 1)
            if overlap < 0.32:
                continue
            current_numbers = {value.casefold() for value in QUANTITY_RE.findall(current["statement"])}
            current_modals = current_tokens & {"must", "shall", "may", "cannot", "prohibited", "optional"}
            numeric_conflict = bool(candidate_numbers and current_numbers and candidate_numbers != current_numbers)
            modal_conflict = bool(candidate_modals and current_modals and candidate_modals != current_modals)
            negation_conflict = ("not" in candidate_tokens) != ("not" in current_tokens)
            if numeric_conflict or modal_conflict or negation_conflict:
                contradictions.append(
                    {
                        "id": _stable_id("ctr", f"{candidate['id']}:{current['id']}"),
                        "candidate_claim_id": candidate["id"],
                        "published_claim_id": current["id"],
                        "candidate_statement": candidate["statement"],
                        "published_statement": current["statement"],
                        "reason": "numeric change" if numeric_conflict else "normative language changed" if modal_conflict else "negation changed",
                        "similarity": round(overlap, 2),
                        "severity": "high" if numeric_conflict or negation_conflict else "medium",
                    }
                )
    return contradictions


def contains_secret(value: str) -> bool:
    return bool(SECRET_RE.search(value))


def _b64url_encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


def _b64url_decode(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def _context_master_secret() -> str:
    return os.getenv("SECURE_CONTEXT_MASTER_SECRET") or "local-development-context-secret-change-me"


def context_security_mode() -> str:
    password_hash = bool(os.getenv("SECURE_CONTEXT_PASSWORD_HASH"))
    master_secret = bool(os.getenv("SECURE_CONTEXT_MASTER_SECRET"))
    if password_hash and master_secret:
        return "configured"
    if password_hash != master_secret:
        return "misconfigured"
    if os.getenv("APP_ENV", "development").casefold() in {"production", "prod"}:
        return "disabled"
    return "local_development"


def _derived_key(purpose: str) -> bytes:
    return hmac.new(_context_master_secret().encode("utf-8"), purpose.encode("utf-8"), hashlib.sha256).digest()


def hash_context_password(password: str, salt: bytes | None = None) -> str:
    salt = salt or os.urandom(16)
    digest = hashlib.scrypt(password.encode("utf-8"), salt=salt, n=2**14, r=8, p=1, dklen=32)
    return f"scrypt${_b64url_encode(salt)}${_b64url_encode(digest)}"


def verify_context_password(password: str) -> bool:
    if context_security_mode() in {"misconfigured", "disabled"}:
        return False
    configured = os.getenv("SECURE_CONTEXT_PASSWORD_HASH")
    encoded = configured or hash_context_password("knowledge-demo-access", salt=b"regulated-ai-dev")
    try:
        algorithm, salt_value, digest_value = encoded.split("$", 2)
        if algorithm != "scrypt":
            return False
        actual = hashlib.scrypt(
            password.encode("utf-8"),
            salt=_b64url_decode(salt_value),
            n=2**14,
            r=8,
            p=1,
            dklen=32,
        )
        return hmac.compare_digest(actual, _b64url_decode(digest_value))
    except (ValueError, TypeError):
        return False


def issue_context_token(subject: str, ttl_seconds: int = 600) -> tuple[str, datetime]:
    expires_at = int(time.time()) + ttl_seconds
    payload = _b64url_encode(json.dumps({"sub": subject, "exp": expires_at}, separators=(",", ":")).encode("utf-8"))
    signature = _b64url_encode(hmac.new(_derived_key("secure-context-access-token"), payload.encode("ascii"), hashlib.sha256).digest())
    return f"{payload}.{signature}", datetime.fromtimestamp(expires_at, UTC)


def verify_context_token(token: str | None) -> str | None:
    if not token:
        return None
    try:
        payload, signature = token.split(".", 1)
        expected = _b64url_encode(hmac.new(_derived_key("secure-context-access-token"), payload.encode("ascii"), hashlib.sha256).digest())
        if not hmac.compare_digest(signature, expected):
            return None
        data = json.loads(_b64url_decode(payload))
        if int(data["exp"]) < int(time.time()):
            return None
        return str(data["sub"])
    except (ValueError, KeyError, json.JSONDecodeError, UnicodeDecodeError):
        return None


def _fernet() -> Fernet:
    return Fernet(base64.urlsafe_b64encode(_derived_key("secure-context-encryption")))


def encrypt_context(content: str) -> str:
    return _fernet().encrypt(content.encode("utf-8")).decode("ascii")


def decrypt_context(ciphertext: str) -> str:
    try:
        return _fernet().decrypt(ciphertext.encode("ascii")).decode("utf-8")
    except (InvalidToken, UnicodeDecodeError) as exc:
        raise ValueError("Protected context could not be decrypted.") from exc
