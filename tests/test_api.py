from fastapi.testclient import TestClient

from harness.api.main import app


def test_api_health_and_root():
    client = TestClient(app)
    root = client.get("/")
    health = client.get("/health")
    assert root.status_code == 200
    assert root.json()["name"] == "Agent Harness Pro"
    assert health.status_code == 200
    assert health.json()["status"] == "ok"


def test_nextjs_cors_preflight():
    client = TestClient(app)
    response = client.options(
        "/chat",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"


def test_dashboard_stats_shape(monkeypatch):
    class EmptyRunStore:
        def list_runs(self, limit=50):
            return []

    monkeypatch.setattr("harness.api.main.RunStore", EmptyRunStore)
    client = TestClient(app)
    response = client.get("/stats")
    assert response.status_code == 200
    assert response.json() == {
        "total_runs": 0,
        "completed_runs": 0,
        "failed_runs": 0,
        "success_rate": 0,
        "average_latency_ms": 0,
        "average_score": 0,
        "recent_runs": [],
    }
