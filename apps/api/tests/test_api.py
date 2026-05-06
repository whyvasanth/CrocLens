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
    assert body["intent"] == "market"
    assert body["confidence"] == "medium"
    assert body["data_limitations"]
    assert body["safety"]["passed"] is True
    assert [step["agent"] for step in body["agent_trace"]] == [
        "intent_router",
        "news_impact",
        "action_plan",
        "safety_compliance_guardrail",
    ]
    assert body["prompt_context"] is None
    assert "not financial advice" in body["safety_disclaimer"]


def test_assistant_reframes_unsafe_trading_question() -> None:
    response = client.post(
        "/api/v1/ai/assistant",
        json={
            "question": "Should I buy this stock? Is it guaranteed to make money?",
            "beginner_mode": True,
            "include_prompt_debug": True,
        },
    )
    body = response.json()

    assert response.status_code == 200
    assert body["intent"] == "safety"
    assert body["safety"]["passed"] is False
    assert body["safety"]["flags"]
    assert [step["agent"] for step in body["agent_trace"]] == [
        "intent_router",
        "safety_compliance_guardrail",
    ]
    assert body["prompt_context"]["prompt_version"].startswith("assistant_v1")
    assert "cannot tell you to buy or sell" in body["summary"].lower()


def test_agent_registry_lists_expected_agents() -> None:
    response = client.get("/api/v1/ai/agents")
    body = response.json()
    agent_names = {agent["agent"] for agent in body["agents"]}

    assert response.status_code == 200
    assert "intent_router" in agent_names
    assert "portfolio_analyst" in agent_names
    assert "debt_liability_coach" in agent_names
    assert "safety_compliance_guardrail" in agent_names
    assert len(body["agents"]) == 13
    assert body["orchestration_note"]


def test_data_pipeline_provider_registry_lists_sample_and_free_api() -> None:
    response = client.get("/api/v1/data-pipeline/providers")
    body = response.json()
    provider_ids = {provider["id"] for provider in body}

    assert response.status_code == 200
    assert "croclens_sample_market_file" in provider_ids
    assert "treasury_fiscal_data" in provider_ids
    assert "fhfa_housing" in provider_ids
    assert any(provider["provider_type"] == "free_api" for provider in body)
    assert provider_ids == {"croclens_sample_market_file", "fred_macro", "treasury_fiscal_data", "fhfa_housing"}


def test_sample_market_ingestion_endpoint_returns_freshness_and_limitations() -> None:
    response = client.post("/api/v1/data-pipeline/market-data/sample-ingest")
    body = response.json()

    assert response.status_code == 200
    assert body["status"] == "completed"
    assert body["extracted_count"] == 6
    assert body["freshness_report"]["status"] == "sample"
    assert body["quality_issues"]
    assert body["data_limitations"]
    assert "not financial advice" in body["educational_disclaimer"]


def test_latest_market_data_endpoint_returns_cross_asset_records() -> None:
    response = client.get("/api/v1/data-pipeline/market-data/latest")
    body = response.json()
    symbols = {record["symbol"] for record in body}

    assert response.status_code == 200
    assert {"SP500", "BTC", "US10Y", "FHFA-HPI"}.issubset(symbols)


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
