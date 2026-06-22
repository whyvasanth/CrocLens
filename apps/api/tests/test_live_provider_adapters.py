from decimal import Decimal

import pandas as pd
import pytest

from app.providers.base import ProviderRuntimeConfig
from app.providers.coingecko_provider import CoinGeckoProvider
from app.providers.fred_provider import FredProvider
from app.providers.sec_provider import SecProvider
from app.providers.treasury_provider import TreasuryProvider
from app.providers.yfinance_provider import YFinanceProvider


def runtime_config() -> ProviderRuntimeConfig:
    return ProviderRuntimeConfig(
        timeout_seconds=5,
        retry_limit=1,
        cache_ttl_seconds=300,
        stale_after_seconds=900,
        user_agent="CrocLens tests",
    )


class FakeYFinanceTicker:
    def __init__(self) -> None:
        self.fast_info = {
            "last_price": 250.25,
            "previous_close": 245.00,
            "currency": "USD",
        }
        self.info = {
            "quoteType": "ETF",
            "shortName": "Total Stock Market ETF",
            "longName": "Vanguard Total Stock Market ETF",
            "exchange": "NYSEARCA",
            "sector": None,
            "industry": None,
        }
        self.dividends = pd.Series([0.75], index=pd.to_datetime(["2026-03-15"]))
        self.splits = pd.Series([2], index=pd.to_datetime(["2026-01-01"]))

    def history(self, period: str, interval: str, auto_adjust: bool) -> pd.DataFrame:
        assert period == "1mo"
        assert interval == "1d"
        assert auto_adjust is False
        return pd.DataFrame(
            {
                "Open": [240.0, 242.0],
                "High": [251.0, 253.0],
                "Low": [239.0, 241.0],
                "Close": [250.0, 252.0],
                "Volume": [1000, 1200],
            },
            index=pd.to_datetime(["2026-06-20", "2026-06-21"]),
        )


@pytest.mark.anyio
async def test_yfinance_quote_history_and_cache_are_normalized() -> None:
    calls = {"ticker": 0}

    def ticker_factory(symbol: str) -> FakeYFinanceTicker:
        calls["ticker"] += 1
        assert symbol == "VTI"
        return FakeYFinanceTicker()

    provider = YFinanceProvider(enabled=True, config=runtime_config(), ticker_factory=ticker_factory)

    quote = await provider.get_quote("vti")
    cached_quote = await provider.get_quote("VTI")
    history = await provider.get_history("VTI", "1M", "1d")
    dividends = await provider.get_dividends("VTI")

    assert calls["ticker"] == 3
    assert quote is cached_quote
    assert quote.provider_name == "yfinance"
    assert quote.symbol == "VTI"
    assert quote.asset_type == "etf"
    assert quote.price == Decimal("250.25")
    assert quote.is_sample_data is False
    assert quote.data_quality == "delayed"
    assert len(history.points) == 2
    assert history.points[-1].close == Decimal("252.0")
    assert dividends.events[0].value == Decimal("0.75")


class FakeResponse:
    def __init__(self, *, json_payload: dict | None = None, text: str = "", status_code: int = 200) -> None:
        self._json_payload = json_payload or {}
        self.text = text
        self.status_code = status_code

    def json(self) -> dict:
        return self._json_payload


class FakeHttpClient:
    def __init__(self, responses: list[FakeResponse]) -> None:
        self.responses = responses
        self.calls: list[dict] = []

    async def get(self, url: str, **kwargs) -> FakeResponse:
        self.calls.append({"url": url, **kwargs})
        return self.responses.pop(0)


@pytest.mark.anyio
async def test_coingecko_public_price_response_is_normalized() -> None:
    client = FakeHttpClient(
        [
            FakeResponse(
                json_payload={
                    "bitcoin": {
                        "usd": 66421.35,
                        "usd_24h_change": -1.9,
                        "last_updated_at": 1782072000,
                    }
                }
            )
        ]
    )
    provider = CoinGeckoProvider(enabled=True, config=runtime_config(), client=client)

    quote = await provider.get_crypto_price("btc")

    assert quote.symbol == "bitcoin"
    assert quote.asset_type == "crypto"
    assert quote.price == Decimal("66421.35")
    assert quote.change_percent == Decimal("-1.9")
    assert quote.source_url.endswith("/bitcoin")
    assert quote.data_quality == "delayed"


@pytest.mark.anyio
async def test_fred_public_csv_response_is_normalized_without_api_key() -> None:
    client = FakeHttpClient(
        [
            FakeResponse(
                text=(
                    "observation_date,DGS10\n"
                    "2026-06-19,4.12\n"
                    "2026-06-20,.\n"
                    "2026-06-21,4.18\n"
                )
            )
        ]
    )
    provider = FredProvider(enabled=True, config=runtime_config(), client=client)

    observation = await provider.get_macro_observation("DGS10")

    assert observation.series_id == "DGS10"
    assert observation.value == Decimal("4.18")
    assert observation.unit == "percent"
    assert observation.source_url.endswith("/DGS10")
    assert observation.confidence == "high"


@pytest.mark.anyio
async def test_treasury_fiscal_data_response_is_normalized() -> None:
    client = FakeHttpClient(
        [
            FakeResponse(
                json_payload={
                    "data": [
                        {
                            "record_date": "2026-06-21",
                            "security_type_desc": "Treasury Bills",
                            "avg_interest_rate_amt": "4.251",
                        }
                    ]
                }
            )
        ]
    )
    provider = TreasuryProvider(enabled=True, config=runtime_config(), client=client)

    observations = await provider.get_treasury_rates()

    assert len(observations) == 1
    assert observations[0].series_id == "TREASURY_AVG_INTEREST_RATE"
    assert observations[0].value == Decimal("4.251")
    assert observations[0].provider_name == "treasury"


@pytest.mark.anyio
async def test_sec_edgar_profile_and_filings_use_configured_user_agent() -> None:
    client = FakeHttpClient(
        [
            FakeResponse(json_payload={"0": {"cik_str": 320193, "ticker": "AAPL", "title": "Apple Inc."}}),
            FakeResponse(
                json_payload={
                    "filings": {
                        "recent": {
                            "form": ["10-K"],
                            "filingDate": ["2026-01-30"],
                            "accessionNumber": ["0000320193-26-000001"],
                        }
                    }
                }
            ),
        ]
    )
    provider = SecProvider(
        enabled=True,
        user_agent="CrocLens tests contact@example.com",
        config=runtime_config(),
        client=client,
    )

    profile = await provider.get_profile("aapl")
    filings = await provider.get_filings("AAPL")

    assert profile.company_name == "Apple Inc."
    assert profile.confidence == "high"
    assert filings[0].filing_type == "10-K"
    assert filings[0].cik == "0000320193"
    assert "User-Agent" in client.calls[0]["headers"]
