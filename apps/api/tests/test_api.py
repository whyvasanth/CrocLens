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
    assert body["debt_impact"]["debt_to_asset_percent"] == 34.79
    assert len(body["scores"]) == 6
    assert all(score["formula"] for score in body["scores"])
    assert "not financial advice" in body["educational_disclaimer"]


def test_asset_not_found_returns_404() -> None:
    response = client.get("/api/v1/assets/missing")

    assert response.status_code == 404


def test_asset_detail_cards_include_debt_example() -> None:
    response = client.get("/api/v1/assets/detail-cards")
    body = response.json()

    assert response.status_code == 200
    assert any(item["category"] == "debt" for item in body)
    assert any(item["id"] == "asset_btc" for item in body)


def test_asset_detail_includes_beginner_fields_and_guardrails() -> None:
    response = client.get("/api/v1/assets/asset_btc/detail")
    body = response.json()

    assert response.status_code == 200
    assert body["category"] == "crypto"
    assert body["risk_level"] == "high"
    assert body["what_to_watch"]
    assert body["safe_next_steps"]
    assert body["data_limitations"]
    assert "not financial advice" in body["educational_disclaimer"]


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


def test_onboarding_options_are_available() -> None:
    response = client.get("/api/v1/onboarding/options")
    body = response.json()

    assert response.status_code == 200
    assert "new" in body["investment_experience"]
    assert "debt_payoff" in body["primary_goal"]


def test_onboarding_profile_returns_risk_profile_and_guardrails() -> None:
    response = client.post(
        "/api/v1/onboarding/profile",
        json={
            "investment_experience": "new",
            "primary_goal": "debt_payoff",
            "risk_tolerance": "medium",
            "time_horizon": "medium",
            "income_range": "50k_100k",
            "emergency_cash_months": 2,
            "has_retirement_account": True,
            "employer_match": "not_sure",
            "retirement_contribution_percent": 4,
            "has_mortgage": False,
            "has_student_loans": True,
            "has_credit_card_debt": True,
            "has_high_interest_debt": True,
            "manual_assets": [
                {
                    "asset_class": "Cash",
                    "label": "Emergency savings",
                    "estimated_value": 4500,
                }
            ],
        },
    )
    body = response.json()

    assert response.status_code == 200
    assert body["risk_profile"] == "Cautious Beginner"
    assert body["risk_score"] <= 40
    assert body["recommended_first_steps"]
    assert body["personalization_notes"]
    assert body["confidence"] == "medium"
    assert body["data_limitations"]
    assert "not financial advice" in body["educational_disclaimer"]
