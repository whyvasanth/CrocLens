from datetime import UTC, datetime

from fastapi.testclient import TestClient

from app.main import app
from app.schemas import MarketHistoryResponse, PricePoint, QuoteResponse

client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "croclens-api"}


def test_quote_returns_simple_market_data(monkeypatch) -> None:
    async def fake_quote(symbol: str) -> QuoteResponse:
        return QuoteResponse(
            symbol=symbol,
            name="Vanguard Total Stock Market ETF",
            price=305.25,
            previous_close=302.0,
            change=3.25,
            change_percent=1.08,
            currency="USD",
            day_high=306.0,
            day_low=301.0,
            volume=1000,
            market_cap=None,
            data_as_of="2026-06-25",
            retrieved_at=datetime.now(tz=UTC).isoformat(),
            data_quality="latest_available",
            data_limitations=["test limitation"],
            beginner_explanation="VTI moved up versus the previous close.",
        )

    monkeypatch.setattr("app.main.get_quote", fake_quote)

    response = client.get("/api/quote/vti")
    body = response.json()

    assert response.status_code == 200
    assert body["symbol"] == "vti"
    assert body["price"] == 305.25
    assert body["provider"] == "yfinance"
    assert body["educational_disclaimer"]


def test_history_returns_points(monkeypatch) -> None:
    async def fake_history(symbol: str, period: str) -> MarketHistoryResponse:
        return MarketHistoryResponse(
            symbol=symbol,
            period=period,
            points=[
                PricePoint(date="2026-06-24", close=302.0),
                PricePoint(date="2026-06-25", close=305.25),
            ],
            data_quality="latest_available",
            data_limitations=["test limitation"],
        )

    monkeypatch.setattr("app.main.get_history", fake_history)

    response = client.get("/api/history/VTI?period=1mo")
    body = response.json()

    assert response.status_code == 200
    assert len(body["points"]) == 2


def test_invalid_symbol_returns_404(monkeypatch) -> None:
    from app.market_data import InvalidSymbolError

    async def fake_quote(_symbol: str) -> QuoteResponse:
        raise InvalidSymbolError("Enter a valid stock or ETF ticker, such as VTI or AAPL.")

    monkeypatch.setattr("app.main.get_quote", fake_quote)

    response = client.get("/api/quote/not-a-real-long-symbol")

    assert response.status_code == 404
    assert "valid stock or ETF ticker" in response.json()["detail"]


def test_demo_portfolio_is_labeled_sample_data() -> None:
    response = client.get("/api/demo-portfolio")
    body = response.json()

    assert response.status_code == 200
    assert body["is_sample_data"] is True
    assert body["total_value"] > 0
    assert {holding["symbol"] for holding in body["holdings"]} == {"VTI", "VXUS", "BND"}


def test_guide_uses_quote_without_advice(monkeypatch) -> None:
    async def fake_quote(symbol: str) -> QuoteResponse:
        return QuoteResponse(
            symbol=symbol,
            name="Apple Inc.",
            price=210.0,
            previous_close=200.0,
            change=10.0,
            change_percent=5.0,
            currency="USD",
            day_high=211.0,
            day_low=198.0,
            volume=1000,
            market_cap=3_000_000_000_000,
            data_as_of="2026-06-25",
            retrieved_at=datetime.now(tz=UTC).isoformat(),
            data_quality="latest_available",
            data_limitations=["test limitation"],
            beginner_explanation="Apple moved up.",
        )

    monkeypatch.setattr("app.main.get_quote", fake_quote)

    response = client.get("/api/guide/AAPL")
    body = response.json()

    assert response.status_code == 200
    combined = " ".join([body["summary"], *body["observations"], *body["considerations"]]).lower()
    assert "buy" not in combined
    assert "sell" not in combined
