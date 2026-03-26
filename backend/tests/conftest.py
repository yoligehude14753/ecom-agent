"""
Shared test configuration for EcomAgent.

Fixtures and markers available to all test suites.
"""
from __future__ import annotations

import os
import pytest


# ─── Environment setup (runs before any test imports app modules) ─────────────

def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers",
        "real_llm: tests that call a real LLM via API (skipped in CI, run locally with -m real_llm)",
    )
    config.addinivalue_line(
        "markers",
        "acceptance: user-facing acceptance tests (tests/acceptance/)",
    )
    config.addinivalue_line(
        "markers",
        "eval: model quality evaluation tests (tests/eval/)",
    )


# ─── Shared env defaults (applied before any app import) ─────────────────────

@pytest.fixture(autouse=True, scope="session")
def _set_test_env():
    """Set safe test defaults for all env vars the app needs."""
    defaults = {
        "DATABASE_URL": "sqlite+aiosqlite:///./test_shared.db",
        "REDIS_URL": "redis://localhost:6379/0",
        "CELERY_BROKER_URL": "redis://localhost:6379/0",
        "CELERY_RESULT_BACKEND": "redis://localhost:6379/1",
        "SECRET_KEY": "test-secret-shared",
        "LLM_PROVIDER": "openai",
        "OPENAI_API_KEY": "sk-test-shared",
    }
    for key, value in defaults.items():
        os.environ.setdefault(key, value)


# ─── FastAPI test client (shared across unit + acceptance tests) ──────────────

@pytest.fixture(scope="session")
def app():
    """Return the FastAPI app instance."""
    from app.main import app as fastapi_app
    return fastapi_app


@pytest.fixture(scope="session")
def client(app):
    """Return a reusable TestClient for the whole test session."""
    from fastapi.testclient import TestClient
    return TestClient(app, raise_server_exceptions=False)


# ─── Real LLM fixture (local dev only, never runs in CI) ─────────────────────

@pytest.fixture
def real_llm_provider():
    """
    Returns a real LLM provider using yunwu API (local dev only).

    To use: mark your test with @pytest.mark.real_llm and request this fixture.
    Requires .env.dev with OPENAI_BASE_URL=https://yunwu.ai/v1 and a valid OPENAI_API_KEY.

    Skips automatically if OPENAI_API_KEY is a test placeholder.
    """
    api_key = os.environ.get("OPENAI_API_KEY", "")
    base_url = os.environ.get("OPENAI_BASE_URL", "")

    if api_key.startswith("sk-test") or not api_key:
        pytest.skip("Skipping real LLM test: no valid API key (set OPENAI_API_KEY in .env.dev)")

    from app.ai.providers.openai_provider import OpenAIProvider
    model = os.environ.get("OPENAI_MODEL", "gpt-4o")
    return OpenAIProvider(api_key=api_key, base_url=base_url or None, model=model)
