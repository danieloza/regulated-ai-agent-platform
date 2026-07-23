import json
import os
from pathlib import Path
import subprocess
import sys


BACKEND_ROOT = Path(__file__).resolve().parents[1]


def run_app_import(
    *,
    allowed_hosts: str | None,
    allowed_origins: str = "https://regulated-ai.example.test",
) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment["APP_ENV"] = "production"
    environment["ALLOWED_ORIGINS"] = allowed_origins
    if allowed_hosts is None:
        environment.pop("ALLOWED_HOSTS", None)
    else:
        environment["ALLOWED_HOSTS"] = allowed_hosts

    code = """
import json
from app.main import ALLOWED_HOSTS, app
print(json.dumps({
    "allowed_hosts": ALLOWED_HOSTS,
    "docs_url": app.docs_url,
    "redoc_url": app.redoc_url,
    "openapi_url": app.openapi_url,
}))
"""
    return subprocess.run(
        [sys.executable, "-c", code],
        cwd=BACKEND_ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )


def test_production_requires_explicit_host_allowlist():
    result = run_app_import(allowed_hosts=None)

    assert result.returncode != 0
    assert "ALLOWED_HOSTS must contain an explicit host allowlist in production." in result.stderr


def test_production_rejects_wildcard_cors_origin():
    result = run_app_import(
        allowed_hosts="regulated-ai.example.test",
        allowed_origins="*",
    )

    assert result.returncode != 0
    assert "ALLOWED_ORIGINS must contain an explicit origin allowlist in production." in result.stderr


def test_production_disables_interactive_api_docs():
    result = run_app_import(allowed_hosts="regulated-ai.example.test")

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout.strip())
    assert payload == {
        "allowed_hosts": ["regulated-ai.example.test"],
        "docs_url": None,
        "openapi_url": None,
        "redoc_url": None,
    }
