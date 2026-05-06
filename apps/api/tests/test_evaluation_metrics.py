from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_evaluation_metrics_endpoint_groups_product_ai_data_and_reliability() -> None:
    response = client.get("/api/v1/evaluation/metrics")
    body = response.json()

    assert response.status_code == 200
    assert body["headline"]
    assert body["beginner_summary"]
    assert body["confidence"] == "medium"
    assert "not financial advice" in body["educational_disclaimer"]

    categories = {metric["category"] for metric in body["metrics"]}
    metric_ids = {metric["id"] for metric in body["metrics"]}

    assert categories == {"product", "ai_safety", "data_quality", "reliability"}
    assert {
        "onboarding_completion_rate",
        "portfolio_creation_rate",
        "action_plan_usage_rate",
        "ai_clarity_score",
        "hallucination_check_pass_rate",
        "unsafe_recommendation_rate",
        "data_freshness_coverage",
        "median_api_latency_ms",
        "api_error_rate",
    }.issubset(metric_ids)


def test_evaluation_metrics_have_targets_limitations_and_safe_ai_metric() -> None:
    response = client.get("/api/v1/evaluation/metrics")
    body = response.json()

    unsafe_rate = next(metric for metric in body["metrics"] if metric["id"] == "unsafe_recommendation_rate")

    assert unsafe_rate["value"] == 0.0
    assert unsafe_rate["direction"] == "lower_is_better"
    assert unsafe_rate["status"] == "healthy"
    assert all(metric["target"] for metric in body["metrics"])
    assert all(metric["how_measured"] for metric in body["metrics"])
    assert all(metric["limitations"] for metric in body["metrics"])
    assert body["quality_checks"]
    assert body["recommended_reviews"]
