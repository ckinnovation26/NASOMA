"""Smoke test — l'endpoint /health doit répondre 200."""

from fastapi.testclient import TestClient


def test_health_endpoint(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert "version" in body
    assert "env" in body


def test_api_v1_root(client: TestClient) -> None:
    response = client.get("/api/v1/")
    assert response.status_code == 200
    assert response.json()["api"] == "nasoma"
