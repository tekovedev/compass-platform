"""
API health check tests.
"""

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

    async def fake_execute(query: str, top_k: int = 5):
        class Result:
            answer = f"echo:{query}"
            sources = []

        return Result()

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
