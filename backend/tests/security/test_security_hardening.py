from pathlib import Path
import importlib.util
import sys
import types

import pytest

from fastapi import WebSocketException, status


REPO_ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = REPO_ROOT / "backend"

SKIP_DIRS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "dist",
    "node_modules",
}
SKIP_SUFFIXES = {
    ".adapter",
    ".DS_Store",
    ".ico",
    ".jpg",
    ".jpeg",
    ".lock",
    ".pdf",
    ".pickle",
    ".png",
    ".svg",
    ".webp",
}


def iter_repo_text_files():
    for path in REPO_ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.suffix in SKIP_SUFFIXES:
            continue
        yield path


def load_module_from_path(module_name: str, path: Path):
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def load_config_module():
    return load_module_from_path(
        "security_test_config",
        BACKEND_ROOT / "src/memos/api/core/config.py",
    )


def load_yjs_router_module():
    for package_name in [
        "memos",
        "memos.api",
        "memos.api.core",
        "memos.api.routers",
        "memos.api.services",
    ]:
        sys.modules.setdefault(package_name, types.ModuleType(package_name))

    security_module = types.ModuleType("memos.api.core.security")
    security_module.verify_token = lambda token, token_type="access": None
    sys.modules["memos.api.core.security"] = security_module

    handler_module = types.ModuleType("memos.api.services.yjs_ws_handler")
    handler_module.yjs_ws_manager = types.SimpleNamespace()
    sys.modules["memos.api.services.yjs_ws_handler"] = handler_module

    return load_module_from_path(
        "security_test_yjs_router",
        BACKEND_ROOT / "src/memos/api/routers/yjs_router.py",
    )


def test_repository_does_not_contain_high_confidence_llm_api_keys():
    import re

    secret_pattern = re.compile(r"sk-[A-Za-z0-9][A-Za-z0-9_-]{16,}")
    findings: list[str] = []

    for path in iter_repo_text_files():
        text = path.read_text(encoding="utf-8", errors="ignore")
        for line_no, line in enumerate(text.splitlines(), start=1):
            if secret_pattern.search(line):
                redacted = secret_pattern.sub("sk-REDACTED", line)
                findings.append(f"{path.relative_to(REPO_ROOT)}:{line_no}:{redacted[:240]}")

    assert findings == []


def production_settings(**overrides):
    config = load_config_module()

    values = {
        "ENVIRONMENT": "production",
        "SECRET_KEY": "test-only-production-secret-key-with-enough-length",
        "POSTGRES_PASSWORD": "test-only-postgres-password",
        "REDIS_PASSWORD": "test-only-redis-password",
        "MONGODB_USERNAME": "test-only-mongo-user",
        "MONGODB_PASSWORD": "test-only-mongo-password",
        "MINIO_ACCESS_KEY": "test-only-minio-access",
        "MINIO_SECRET_KEY": "test-only-minio-secret",
        "BACKEND_CORS_ORIGINS": ["https://app.example.invalid"],
        "ALLOWED_HOSTS": ["app.example.invalid"],
    }
    values.update(overrides)
    return config.Settings(**values)


def test_production_rejects_default_secret_key():
    config = load_config_module()

    settings = production_settings(
        SECRET_KEY="your-super-secret-key-change-in-production",
    )

    with pytest.raises(RuntimeError, match="SECRET_KEY"):
        config.validate_security_settings(settings)


def test_production_rejects_wildcard_cors_origins():
    config = load_config_module()

    settings = production_settings(BACKEND_CORS_ORIGINS=["*"])

    with pytest.raises(RuntimeError, match="BACKEND_CORS_ORIGINS"):
        config.validate_security_settings(settings)


def test_production_rejects_weak_infrastructure_credentials():
    config = load_config_module()

    settings = production_settings(
        POSTGRES_PASSWORD="password",
        MINIO_ACCESS_KEY="minioadmin",
        MINIO_SECRET_KEY="minioadmin",
    )

    with pytest.raises(
        RuntimeError,
        match="POSTGRES_PASSWORD|MINIO_ACCESS_KEY|MINIO_SECRET_KEY",
    ):
        config.validate_security_settings(settings)


@pytest.mark.asyncio
async def test_yjs_websocket_auth_rejects_missing_token():
    yjs_router = load_yjs_router_module()

    with pytest.raises(WebSocketException) as exc_info:
        await yjs_router.authenticate_yjs_connection(token=None, room_name="work_1")

    assert exc_info.value.code == status.WS_1008_POLICY_VIOLATION


@pytest.mark.asyncio
async def test_yjs_websocket_auth_rejects_invalid_token():
    yjs_router = load_yjs_router_module()

    with pytest.raises(WebSocketException) as exc_info:
        await yjs_router.authenticate_yjs_connection(token="not-a-valid-jwt", room_name="work_1")

    assert exc_info.value.code == status.WS_1008_POLICY_VIOLATION
