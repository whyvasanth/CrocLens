from datetime import timedelta
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import get_provider_registry
from app.main import app
from app.providers.base import BaseProvider, ProviderRuntimeConfig
from app.providers.exceptions import ProviderMalformedResponseError, ProviderTimeoutError, ProviderUnavailableError
from app.providers.models import MarketHistory, MarketHistoryPoint, MarketQuote, utc_now

client = TestClient(app)


class FakeQuoteHistoryProvider(BaseProvider):
    name = "fake_market_provider"
    display_name = "Fake market provider"
    capabilities = ("quote", "history")

    def __init__(
        self,
        *,
        price: Decimal = Decimal("250.00"),
        fail_quote: bool = False,
        fail_history: bool = False,
        timeout_quote: bool = False,
        malformed_history: bool = False,
        stale_after_seconds: int = 900,
    ) -> None:
        super().__init__(
            enabled=True,
            configured=True,
            config=ProviderRuntimeConfig(
                timeout_seconds=5,
                retry_limit=1,
                cache_ttl_seconds=300,
                stale_after_seconds=stale_after_seconds,
                user_agent="CrocLens tests",
            ),
            data_limitations=["Fake provider used only in tests."],
        )
        self.price = price
        self.fail_quote = fail_quote
        self.fail_history = fail_history
        self.timeout_quote = timeout_quote
        self.malformed_history = malformed_history
        self.quote_calls = 0
        self.history_calls = 0

    async def get_quote(self, symbol: str) -> MarketQuote:
        self.quote_calls += 1
        if self.timeout_quote:
            raise ProviderTimeoutError("Provider timed out.")
        if self.fail_quote:
            raise ProviderUnavailableError("Provider failed.")
        now = utc_now()
        return MarketQuote(
            provider_name=self.name,
            provider_status="healthy",
            symbol=symbol.upper(),
            asset_type="etf",
            price=self.price,
            currency="USD",
            data_as_of=now,
            retrieved_at=now,
            is_stale=False,
            is_sample_data=False,
            data_quality="delayed",
            confidence="medium",
            source_url=f"https://example.test/{symbol}",
            data_limitations=["Fake provider used only in tests."],
        )

    async def get_history(self, symbol: str, period: str, interval: str) -> MarketHistory:
        self.history_calls += 1
        if self.fail_history:
            raise ProviderUnavailableError("Provider history failed.")
        if self.malformed_history:
            raise ProviderMalformedResponseError("History response was empty.")
        now = utc_now()
        return MarketHistory(
            provider_name=self.name,
            provider_status="healthy",
            symbol=symbol.upper(),
            asset_type="etf",
            period=period,
            interval=interval,
            currency="USD",
            points=[
                MarketHistoryPoint(observed_at=now - timedelta(days=1), close=Decimal("249.00")),
                MarketHistoryPoint(observed_at=now, close=self.price),
            ],
            data_as_of=now,
            retrieved_at=now,
            is_stale=False,
            is_sample_data=False,
            data_quality="delayed",
            confidence="medium",
            source_url=f"https://example.test/{symbol}/history",
            data_limitations=["Fake provider used only in tests."],
        )


class FakeProviderRegistry:
    def __init__(self, provider: BaseProvider | None) -> None:
        self.provider = provider

    def providers_for(self, capability: str) -> list[BaseProvider]:
        if self.provider is not None and self.provider.supports(capability):  # type: ignore[arg-type]
            return [self.provider]
        return []


@pytest.fixture
def override_provider_registry():
    providers: list[FakeQuoteHistoryProvider | None] = []

    def apply(provider: FakeQuoteHistoryProvider | None) -> FakeQuoteHistoryProvider | None:
        providers.append(provider)
        app.dependency_overrides[get_provider_registry] = lambda: FakeProviderRegistry(provider)
        return provider

    yield apply
    app.dependency_overrides.pop(get_provider_registry, None)


def test_market_snapshot_endpoint_labels_sample_data() -> None:
    response = client.get("/api/v1/market/snapshot")
    body = response.json()

    assert response.status_code == 200
    assert body["is_sample_data"] is True
    assert body["data_quality"] == "sample"
    assert body["items"]
    assert all(item["is_sample_data"] is True for item in body["items"])


def test_market_quote_endpoint_refreshes_and_reuses_fresh_cache(override_provider_registry) -> None:
    provider = override_provider_registry(FakeQuoteHistoryProvider(price=Decimal("251.25")))

    first = client.get("/api/v1/market/quotes/VTI")
    second = client.get("/api/v1/market/quotes/vti")

    assert first.status_code == 200
    assert first.json()["price"] == 251.25
    assert first.json()["is_sample_data"] is False
    assert first.json()["data_quality"] == "delayed"
    assert second.status_code == 200
    assert second.json()["price"] == 251.25
    assert provider.quote_calls == 1


def test_market_quote_rejects_malformed_symbol(override_provider_registry) -> None:
    override_provider_registry(FakeQuoteHistoryProvider())

    response = client.get("/api/v1/market/quotes/!!!")

    assert response.status_code == 422


def test_market_quote_returns_unavailable_on_timeout_without_sample_fallback(override_provider_registry) -> None:
    override_provider_registry(FakeQuoteHistoryProvider(timeout_quote=True))

    response = client.get("/api/v1/market/quotes/VTI")
    body = response.json()

    assert response.status_code == 200
    assert body["price"] is None
    assert body["provider_status"] == "unavailable"
    assert body["is_sample_data"] is False
    assert "did not substitute sample data" in body["data_limitations"][0]


def test_market_quote_returns_stale_cache_when_provider_fails(override_provider_registry) -> None:
    provider = override_provider_registry(FakeQuoteHistoryProvider(stale_after_seconds=0))
    first = client.get("/api/v1/market/quotes/VTI")
    provider.fail_quote = True

    second = client.get("/api/v1/market/quotes/VTI")
    body = second.json()

    assert first.status_code == 200
    assert second.status_code == 200
    assert body["price"] == 250.0
    assert body["is_stale"] is True
    assert body["warning"]
    assert provider.quote_calls == 2


def test_market_history_endpoint_persists_history_and_validates_period(override_provider_registry) -> None:
    provider = override_provider_registry(FakeQuoteHistoryProvider(price=Decimal("252.00")))

    response = client.get("/api/v1/market/history/VTI?period=1M&interval=1d")
    invalid = client.get("/api/v1/market/history/VTI?period=2Y&interval=1d")

    assert response.status_code == 200
    assert len(response.json()["points"]) == 2
    assert response.json()["points"][-1]["close"] == 252.0
    assert provider.history_calls == 1
    assert invalid.status_code == 422


def test_market_history_returns_empty_unavailable_without_fake_history(override_provider_registry) -> None:
    override_provider_registry(FakeQuoteHistoryProvider(malformed_history=True))

    response = client.get("/api/v1/market/history/VTI?period=1M&interval=1d")
    body = response.json()

    assert response.status_code == 200
    assert body["points"] == []
    assert body["provider_status"] == "unavailable"
    assert body["is_sample_data"] is False


def test_portfolio_refresh_prices_updates_public_holdings_and_preserves_manual_values(override_provider_registry) -> None:
    override_provider_registry(FakeQuoteHistoryProvider(price=Decimal("250.00")))
    token = _signup_user("refresh-owner@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    client.post(
        "/api/v1/portfolio/holdings",
        headers=headers,
        json={
            "symbol": "VTI",
            "name": "Total Stock Market ETF",
            "asset_type": "ETFs",
            "quantity": 5,
            "market_value": 100,
        },
    )
    client.post(
        "/api/v1/portfolio/holdings",
        headers=headers,
        json={
            "symbol": "CASH",
            "name": "Emergency cash",
            "asset_type": "Cash",
            "quantity": 0,
            "market_value": 500,
        },
    )

    response = client.post("/api/v1/portfolio/refresh-prices", headers=headers)
    body = response.json()

    assert response.status_code == 200
    assert body["summary"]["total_assets"] == 1750.0
    assert body["valuation_counts"]["provider_valued"] == 1
    assert body["valuation_counts"]["manually_valued"] == 1
    assert body["snapshot"]["net_worth"] == 1750.0
    assert body["data_limitations"]


def test_portfolio_history_is_user_specific(override_provider_registry) -> None:
    override_provider_registry(FakeQuoteHistoryProvider(price=Decimal("100.00")))
    owner_token = _signup_user("history-owner@example.com")
    other_token = _signup_user("history-other@example.com")
    owner_headers = {"Authorization": f"Bearer {owner_token}"}
    other_headers = {"Authorization": f"Bearer {other_token}"}
    client.post(
        "/api/v1/portfolio/holdings",
        headers=owner_headers,
        json={
            "symbol": "VTI",
            "name": "Total Stock Market ETF",
            "asset_type": "ETFs",
            "quantity": 1,
            "market_value": 100,
        },
    )
    client.post("/api/v1/portfolio/refresh-prices", headers=owner_headers)

    owner_history = client.get("/api/v1/portfolio/history", headers=owner_headers)
    other_history = client.get("/api/v1/portfolio/history", headers=other_headers)

    assert owner_history.status_code == 200
    assert len(owner_history.json()["points"]) == 1
    assert other_history.status_code == 200
    assert other_history.json()["points"] == []


def _signup_user(email: str) -> str:
    response = client.post(
        "/api/v1/auth/signup",
        json={
            "display_name": "Market Test User",
            "email": email,
            "password": "sample-pass-123",
            "onboarding_profile": {
                "investment_experience": "new",
                "primary_goal": "learn",
                "risk_tolerance": "medium",
                "time_horizon": "medium",
                "income_range": "prefer_not",
                "emergency_cash_months": 3,
                "has_retirement_account": False,
                "employer_match": "not_applicable",
                "retirement_contribution_percent": 0,
                "has_mortgage": False,
                "has_student_loans": False,
                "has_credit_card_debt": False,
                "has_high_interest_debt": False,
                "manual_assets": [],
            },
        },
    )
    assert response.status_code == 200
    return response.json()["session_token"]
