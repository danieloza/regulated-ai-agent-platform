from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path, PurePosixPath
from urllib.parse import quote


WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|[^\]]+)?\]\]")
TAG_RE = re.compile(r"(?<!\w)#([a-zA-Z0-9_/-]+)")
ALLOWED_CLASSIFICATIONS = {"public", "internal", "confidential", "restricted"}
EXCLUDED_STATUSES = {"private", "draft", "personal"}


class ObsidianConnectorError(ValueError):
    pass


def connector_security_mode() -> str:
    if os.getenv("OBSIDIAN_ALLOWED_ROOTS", "").strip():
        return "configured"
    if os.getenv("APP_ENV", "development").casefold() in {"production", "prod"}:
        return "disabled"
    return "local_development"


def _allowed_roots(backend_root: Path) -> list[Path]:
    configured = [item.strip() for item in os.getenv("OBSIDIAN_ALLOWED_ROOTS", "").split(",") if item.strip()]
    if configured:
        roots = []
        for item in configured:
            candidate = Path(item)
            if not candidate.is_absolute():
                candidate = backend_root / candidate
            roots.append(candidate.resolve())
        return roots
    if connector_security_mode() == "local_development":
        return [(backend_root / "demo").resolve()]
    return []


def resolve_vault_path(vault_path: str, backend_root: Path) -> Path:
    if connector_security_mode() == "disabled":
        raise ObsidianConnectorError("Obsidian connector is disabled until OBSIDIAN_ALLOWED_ROOTS is configured.")
    candidate = Path(vault_path)
    if not candidate.is_absolute():
        candidate = backend_root / candidate
    if candidate.is_symlink():
        raise ObsidianConnectorError("Vault root cannot be a symbolic link.")
    try:
        resolved = candidate.resolve(strict=True)
    except FileNotFoundError as exc:
        raise ObsidianConnectorError("Vault path does not exist on the connector host.") from exc
    if not resolved.is_dir():
        raise ObsidianConnectorError("Vault path must resolve to a directory.")
    if not any(resolved == root or root in resolved.parents for root in _allowed_roots(backend_root)):
        raise ObsidianConnectorError("Vault path is outside the configured connector allowlist.")
    return resolved


def _parse_scalar(value: str):
    value = value.strip().strip('"').strip("'")
    if value.casefold() in {"true", "false"}:
        return value.casefold() == "true"
    if value.startswith("[") and value.endswith("]"):
        return [item.strip().strip('"').strip("'") for item in value[1:-1].split(",") if item.strip()]
    return value


def parse_frontmatter(raw: str) -> tuple[dict, str]:
    lines = raw.replace("\r\n", "\n").split("\n")
    if not lines or lines[0].strip() != "---":
        return {}, raw.strip()
    try:
        end = next(index for index, line in enumerate(lines[1:], start=1) if line.strip() == "---")
    except StopIteration:
        return {}, raw.strip()
    metadata: dict = {}
    current_list: str | None = None
    for line in lines[1:end]:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("- ") and current_list:
            metadata.setdefault(current_list, []).append(_parse_scalar(stripped[2:]))
            continue
        if ":" not in line:
            current_list = None
            continue
        key, value = line.split(":", 1)
        key = key.strip().casefold().replace("-", "_")
        parsed = _parse_scalar(value)
        metadata[key] = parsed if value.strip() else []
        current_list = key if not value.strip() else None
    return metadata, "\n".join(lines[end + 1 :]).strip()


def _normalize_list(value) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip().lstrip("#") for item in value if str(item).strip()]
    if isinstance(value, str):
        return [item.strip().lstrip("#") for item in value.split(",") if item.strip()]
    return []


def _validated_include_folders(include_folders: list[str]) -> list[PurePosixPath]:
    result = []
    for raw in include_folders:
        value = raw.strip().replace("\\", "/").strip("/")
        path = PurePosixPath(value)
        if not value or path.is_absolute() or ".." in path.parts or any(part.startswith(".") for part in path.parts):
            raise ObsidianConnectorError("Include folders must be safe vault-relative paths.")
        result.append(path)
    return result


def _is_included(relative_path: PurePosixPath, include_folders: list[PurePosixPath]) -> bool:
    if not include_folders:
        return True
    return any(relative_path == folder or folder in relative_path.parents for folder in include_folders)


def _note_title(metadata: dict, body: str, path: Path) -> str:
    if metadata.get("title"):
        return str(metadata["title"])[:240]
    for line in body.splitlines():
        if line.startswith("# "):
            return line[2:].strip()[:240]
    return path.stem.replace("-", " ").replace("_", " ")[:240]


def _obsidian_uri(vault_name: str, relative_path: str) -> str:
    return f"obsidian://open?vault={quote(vault_name, safe='')}&file={quote(relative_path, safe='')}"


def scan_obsidian_vault(
    vault_path: str,
    vault_name: str,
    backend_root: Path,
    include_folders: list[str] | None = None,
    required_tags: list[str] | None = None,
) -> dict:
    resolved = resolve_vault_path(vault_path, backend_root)
    include_paths = _validated_include_folders(include_folders or [])
    required = {item.casefold().lstrip("#") for item in (required_tags or []) if item.strip()}
    max_files = int(os.getenv("OBSIDIAN_MAX_FILES", "500"))
    max_file_bytes = int(os.getenv("OBSIDIAN_MAX_FILE_BYTES", str(256 * 1024)))
    max_total_bytes = int(os.getenv("OBSIDIAN_MAX_TOTAL_BYTES", str(10 * 1024 * 1024)))
    files: list[dict] = []
    skipped: list[dict] = []
    total_bytes = 0
    scanned_files = 0

    for path in sorted(resolved.rglob("*.md")):
        relative = path.relative_to(resolved)
        relative_posix = PurePosixPath(relative.as_posix())
        scanned_files += 1
        if scanned_files > max_files:
            skipped.append({"path": "[limit]", "reason": f"Vault file limit of {max_files} reached."})
            break
        if path.is_symlink() or any(part.startswith(".") for part in relative.parts):
            skipped.append({"path": relative.as_posix(), "reason": "Hidden paths and symbolic links are excluded."})
            continue
        if not _is_included(relative_posix, include_paths):
            continue
        size = path.stat().st_size
        if size > max_file_bytes or total_bytes + size > max_total_bytes:
            skipped.append({"path": relative.as_posix(), "reason": "Configured connector size limit exceeded."})
            continue
        try:
            raw = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            skipped.append({"path": relative.as_posix(), "reason": "Only UTF-8 Markdown notes are supported."})
            continue
        metadata, body = parse_frontmatter(raw)
        tags = {item.casefold() for item in _normalize_list(metadata.get("tags"))}
        tags.update(item.casefold() for item in TAG_RE.findall(body))
        status = str(metadata.get("status", "reviewable")).casefold()
        if metadata.get("publish") is False or status in EXCLUDED_STATUSES:
            skipped.append({"path": relative.as_posix(), "reason": "Note metadata excludes it from connector review."})
            continue
        if required and not required.issubset(tags):
            continue
        if len(body) < 30:
            skipped.append({"path": relative.as_posix(), "reason": "Note has insufficient reviewable content."})
            continue
        classification = str(metadata.get("classification", "internal")).casefold()
        if classification not in ALLOWED_CLASSIFICATIONS:
            classification = "internal"
        relative_value = relative.as_posix()
        content_hash = hashlib.sha256(body.encode("utf-8")).hexdigest()
        snapshot_hash = hashlib.sha256(raw.encode("utf-8")).hexdigest()
        links = sorted({item.strip() for item in WIKILINK_RE.findall(body) if item.strip()})
        files.append(
            {
                "relative_path": relative_value,
                "title": _note_title(metadata, body, path),
                "content": body,
                "content_hash": content_hash,
                "snapshot_hash": snapshot_hash,
                "size_bytes": size,
                "classification": classification,
                "owner": str(metadata.get("owner", "")).strip(),
                "source_type": str(metadata.get("source_type", "policy")).casefold(),
                "status": status,
                "policy_domain": str(metadata.get("policy_domain", "")).strip(),
                "review_due": str(metadata.get("review_due", "")).strip(),
                "tags": sorted(tags),
                "links": links,
                "obsidian_uri": _obsidian_uri(vault_name, relative_value),
                "excerpt": " ".join(body.split())[:220],
            }
        )
        total_bytes += size

    canonical = [{"path": item["relative_path"], "hash": item["snapshot_hash"]} for item in files]
    scan_digest = hashlib.sha256(json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return {
        "resolved_path": str(resolved),
        "files": files,
        "skipped": skipped,
        "scan_digest": scan_digest,
        "total_bytes": total_bytes,
    }
