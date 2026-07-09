from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


def test_openapi_documents_required_routes() -> None:
    client = TestClient(app)
    schema = client.get("/openapi.json").json()

    assert "/api/v1/roadmap" in schema["paths"]
    assert "/api/v1/project" in schema["paths"]
    assert "/api/v1/chat" in schema["paths"]
    assert "/api/v1/progress" in schema["paths"]


def test_root_health_endpoint() -> None:
    client = TestClient(app)
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
