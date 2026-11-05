from fastapi.testclient import TestClient

from recomendacoes_api.app import app


def test_health_returns_200_with_ok_status():
    response = TestClient(app).get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
