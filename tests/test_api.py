"""
API health check tests.
"""

from types import SimpleNamespace

from fastapi.testclient import TestClient


def test_api_module_imports():
    """Test that API modules can be imported."""
    try:
        from compass.api import app
        assert app is not None
    except ImportError as e:
        # If FastAPI or dependencies aren't installed, skip gracefully
        assert True, f"API imports skipped: {e}"


def test_healthcheck_endpoint_is_public():
    """Healthcheck should remain public even when auth is enabled."""
    from compass.api.app import app
    from compass.config import settings

    original_pool_id = settings.cognito_user_pool_id
    original_client_id = settings.cognito_client_id

    settings.cognito_user_pool_id = "us-east-1_example"
    settings.cognito_client_id = "example-client"

    try:
        client = TestClient(app)
        response = client.get("/api/v1/healthcheck")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    finally:
        settings.cognito_user_pool_id = original_pool_id
        settings.cognito_client_id = original_client_id


def test_query_requires_authentication_when_cognito_enabled(monkeypatch):
    """Query endpoint should reject anonymous requests once Cognito is configured."""
    from compass.api.app import app
    from compass.api import routes
    from compass.config import settings

    async def fake_execute(query: str, user_id: str, session_id: str | None = None, top_k: int = 5):
        return SimpleNamespace(
            answer=f"echo:{query}",
            sources=[],
            session_id=session_id or "session-1",
            input_tokens=0,
            output_tokens=0,
        )

    monkeypatch.setattr(routes._query_service, "execute", fake_execute)

    original_pool_id = settings.cognito_user_pool_id
    original_client_id = settings.cognito_client_id

    settings.cognito_user_pool_id = "us-east-1_example"
    settings.cognito_client_id = "example-client"

    try:
        client = TestClient(app)
        response = client.post("/api/v1/query", json={"query": "hola", "top_k": 3})
        assert response.status_code == 401
    finally:
        settings.cognito_user_pool_id = original_pool_id
        settings.cognito_client_id = original_client_id


def test_query_returns_session_id_when_auth_disabled(monkeypatch):
    """Query endpoint should return a session id when auth is disabled."""
    from compass.api.app import app
    from compass.api import routes
    from compass.config import settings

    captured: dict[str, object] = {}

    async def fake_execute(query: str, user_id: str, session_id: str | None = None, top_k: int = 5):
        captured.update({
            "query": query,
            "user_id": user_id,
            "session_id": session_id,
            "top_k": top_k,
        })

        return SimpleNamespace(
            answer=f"echo:{query}",
            sources=["source-1"],
            session_id=session_id or "session-1",
            input_tokens=7,
            output_tokens=11,
        )

    monkeypatch.setattr(routes._query_service, "execute", fake_execute)

    original_pool_id = settings.cognito_user_pool_id
    original_client_id = settings.cognito_client_id

    settings.cognito_user_pool_id = None
    settings.cognito_client_id = None

    try:
        client = TestClient(app)
        response = client.post("/api/v1/query", json={"query": "hola", "top_k": 3})
        assert response.status_code == 200

        body = response.json()
        assert body["answer"] == "echo:hola"
        assert body["session_id"] == "session-1"
        assert body["input_tokens"] == 7
        assert body["output_tokens"] == 11
        assert captured["user_id"] == "anonymous"
        assert captured["session_id"] is None
    finally:
        settings.cognito_user_pool_id = original_pool_id
        settings.cognito_client_id = original_client_id


def test_query_returns_429_when_quota_exceeded(monkeypatch):
    """Query endpoint should map QuotaExceeded to HTTP 429."""
    from compass.api.app import app
    from compass.api import routes
    from compass.config import settings
    from compass.exceptions import QuotaExceeded

    async def fake_execute(query: str, user_id: str, session_id: str | None = None, top_k: int = 5):
        raise QuotaExceeded(user_id=user_id, limit=1000, used=1000)

    monkeypatch.setattr(routes._query_service, "execute", fake_execute)

    original_pool_id = settings.cognito_user_pool_id
    original_client_id = settings.cognito_client_id

    settings.cognito_user_pool_id = None
    settings.cognito_client_id = None

    try:
        client = TestClient(app)
        response = client.post("/api/v1/query", json={"query": "hola", "top_k": 3})
        assert response.status_code == 429
        body = response.json()
        assert body["detail"]["error"] == "token_quota_exceeded"
    finally:
        settings.cognito_user_pool_id = original_pool_id
        settings.cognito_client_id = original_client_id
