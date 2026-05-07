import json
import sys

import pytest

from app.data_providers.coingecko_provider import CoinGeckoProvider
from app.data_providers.errors import ProviderConfigurationError, ProviderUnavailableError
from app.data_providers.fred_provider import FredProvider
from app.data_providers.registry import DataProviderRegistry
from app.data_providers.yfinance_provider import YFinanceProvider


def test_provider_registry_reports_configured_and_fallback_providers() -> None:
    registry = DataProviderRegistry()
    statuses = registry.list_provider_statuses()
    ids = {status.id for status in statuses}

    assert "yfinance" in ids
    assert "fred" in ids
    assert "coingecko" in ids
    assert "croclens_sample_fallback" in ids
    assert all("paid" not in status.cost_note.lower() for status in statuses)


def test_provider_registry_falls_back_to_sample_when_primary_fails() -> None:
    registry = DataProviderRegistry()

    def fail_price(symbol: str):
        raise ProviderUnavailableError("forced test failure")

    registry.yfinance.get_market_price = fail_price
    registry.alpha_vantage.is_configured = lambda: False

    result = registry.get_market_price("VOO")

    assert result.provider == "croclens_sample_fallback"
    assert result.symbol_or_series_id == "VOO"
    assert result.value > 0
    assert result.fallback_chain[-1].provider == "croclens_sample_fallback"


def test_yfinance_provider_normalizes_price_response(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeTimestamp:
        def to_pydatetime(self):
            from datetime import UTC, datetime

            return datetime(2026, 5, 6, 20, 0, tzinfo=UTC)

    class FakeSeries:
        def dropna(self):
            return self

        @property
        def iloc(self):
            return self

        def __getitem__(self, index):
            return 123.45

    class FakeHistory:
        empty = False
        index = [FakeTimestamp()]

        def __getitem__(self, key):
            return FakeSeries()

    class FakeTicker:
        fast_info = {"last_price": 123.45, "currency": "USD"}

        def history(self, period: str):
            return FakeHistory()

    class FakeYFinance:
        @staticmethod
        def Ticker(symbol: str):
            return FakeTicker()

    monkeypatch.setitem(sys.modules, "yfinance", FakeYFinance)

    result = YFinanceProvider().get_market_price("aapl")

    assert result.provider == "yfinance"
    assert result.symbol_or_series_id == "AAPL"
    assert result.value == 123.45
    assert result.currency == "USD"
    assert result.confidence == "medium"
    assert result.limitations


def test_coingecko_provider_normalizes_public_price_response(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, traceback):
            return None

        def read(self):
            return json.dumps({"bitcoin": {"usd": 66421.35, "last_updated_at": 1778083200}}).encode("utf-8")

    monkeypatch.setattr("app.data_providers.coingecko_provider.urlopen", lambda request, timeout: FakeResponse())

    result = CoinGeckoProvider().get_crypto_price("bitcoin")

    assert result.provider == "coingecko"
    assert result.asset_type == "crypto"
    assert result.symbol_or_series_id == "bitcoin"
    assert result.value == 66421.35
    assert result.source_url.endswith("/bitcoin")


def test_fred_provider_requires_api_key() -> None:
    provider = FredProvider()

    assert provider.is_configured() is False
    with pytest.raises(ProviderConfigurationError):
        provider.get_macro_series("CPIAUCSL")
