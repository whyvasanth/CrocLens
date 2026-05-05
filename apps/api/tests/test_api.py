from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_portfolio_summary_has_safety_disclaimer() -> None:
    response = client.get("/api/v1/portfolio/summary")
    body = response.json()

    assert response.status_code == 200
    assert body["net_worth"] == 214800.0
    assert "not financial advice" in body["educational_disclaimer"]


def test_asset_not_found_returns_404() -> None:
    response = client.get("/api/v1/assets/missing")

    assert response.status_code == 404


def test_assistant_response_includes_guardrail_fields() -> None:
    response = client.post(
        "/api/v1/ai/assistant",
        json={"question": "How does today's market affect me?", "beginner_mode": True},
    )
    body = response.json()

    assert response.status_code == 200
    assert body["confidence"] == "medium"
    assert body["data_limitations"]
    assert "not financial advice" in body["safety_disclaimer"]

