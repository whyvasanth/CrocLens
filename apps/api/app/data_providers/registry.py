from datetime import UTC, datetime, timedelta
from typing import Any, Callable

from app.core.config import settings
from app.data_providers.alpha_vantage_provider import AlphaVantageProvider
from app.data_providers.base import BaseDataProvider, utc_now
from app.data_providers.cache import InMemoryTTLCache
from app.data_providers.census_provider import CensusProvider
from app.data_providers.coingecko_provider import CoinGeckoProvider
from app.data_providers.errors import DataProviderError
from app.data_providers.fhfa_provider import FhfaProvider
from app.data_providers.fred_provider import FredProvider
from app.data_providers.openfigi_provider import OpenFigiProvider
from app.data_providers.schemas import (
    DataFreshnessItem,
    DataFreshnessResponse,
    NormalizedDataPoint,
    PriceHistoryPoint,
    PriceHistoryResponse,
    ProviderFallbackStep,
    ProviderStatus,
    TechnicalIndicatorResponse,
)
from app.data_providers.sec_edgar_provider import SecEdgarProvider
from app.data_providers.stockstats_provider import StockstatsProvider
from app.data_providers.treasury_provider import TreasuryProvider
from app.data_providers.yfinance_provider import YFinanceProvider


SAMPLE_LIMITATIONS = [
    "This is deterministic CrocLens sample data, not live market data.",
    "Use it for product development and education only.",
    "This is educational, not financial advice.",
]


class DataProviderRegistry:
    def __init__(self, cache_ttl_seconds: int | None = None) -> None:
        self.cache = InMemoryTTLCache(cache_ttl_seconds or settings.data_cache_ttl_seconds)
        self.yfinance = YFinanceProvider()
        self.alpha_vantage = AlphaVantageProvider()
        self.stockstats = StockstatsProvider()
        self.coingecko = CoinGeckoProvider()
        self.fred = FredProvider()
        self.treasury = TreasuryProvider()
        self.providers: list[BaseDataProvider] = [
            self.yfinance,
            self.alpha_vantage,
            SecEdgarProvider(),
            self.stockstats,
            self.coingecko,
            self.fred,
            self.treasury,
            FhfaProvider(),
            CensusProvider(),
            OpenFigiProvider(),
        ]

    def list_provider_statuses(self) -> list[ProviderStatus]:
        statuses = []
        for provider in self.providers:
            status = provider.status()
            if provider.provider_id in {"alpha_vantage", "fred"} and not status.configured:
                status.health = "unconfigured"
            elif provider.provider_id in {"sec_edgar"} and not status.configured:
                status.health = "unconfigured"
            statuses.append(status)
        statuses.append(
            ProviderStatus(
                id="croclens_sample_fallback",
                name="CrocLens sample fallback",
                source_type="sample",
                capabilities=[
                    "market_price",
                    "price_history",
                    "technical_indicators",
                    "crypto_price",
                    "macro_series",
                    "treasury_rates",
                    "housing_index",
                    "census_context",
                    "security_mapping",
                ],
                configured=True,
                health="fallback_only",
                requires_api_key=False,
                cost_note="Free local deterministic sample data.",
                limitations=SAMPLE_LIMITATIONS,
            )
        )
        return statuses

    def freshness(self) -> DataFreshnessResponse:
        keys = self.cache.last_retrieved_keys()
        return DataFreshnessResponse(
            mode=settings.data_provider_mode,
            providers=[
                DataFreshnessItem(
                    provider=status.id,
                    status=status.health,
                    last_retrieved_at=utc_now() if keys and status.id != "croclens_sample_fallback" else None,
                    cache_ttl_seconds=self.cache.ttl_seconds,
                    note=(
                        "Provider is available through the registry."
                        if status.configured
                        else "Provider needs an environment variable before live calls can run."
                    ),
                )
                for status in self.list_provider_statuses()
            ],
        )

    def get_market_price(self, symbol: str) -> NormalizedDataPoint:
        return self._cached(
            "market_price",
            {"symbol": symbol.upper()},
            lambda: self._route_with_fallback(
                [self.yfinance, self.alpha_vantage],
                lambda provider: provider.get_market_price(symbol),
                lambda chain: _sample_market_price(symbol, chain),
            ),
        )

    def get_price_history(self, symbol: str, period: str = "1mo") -> PriceHistoryResponse:
        return self._cached(
            "price_history",
            {"symbol": symbol.upper(), "period": period},
            lambda: self._route_with_fallback(
                [self.yfinance, self.alpha_vantage],
                lambda provider: provider.get_price_history(symbol, period),
                lambda chain: _sample_price_history(symbol, chain),
            ),
        )

    def get_technical_indicators(self, symbol: str) -> TechnicalIndicatorResponse:
        history = self.get_price_history(symbol)
        return self.stockstats.get_technical_indicators(history)

    def get_crypto_price(self, coin_id: str) -> NormalizedDataPoint:
        return self._cached(
            "crypto_price",
            {"coin_id": coin_id.lower()},
            lambda: self._route_with_fallback(
                [self.coingecko],
                lambda provider: provider.get_crypto_price(coin_id),
                lambda chain: _sample_crypto_price(coin_id, chain),
            ),
        )

    def get_macro_series(self, series_id: str) -> NormalizedDataPoint:
        return self._cached(
            "macro_series",
            {"series_id": series_id.upper()},
            lambda: self._route_with_fallback(
                [self.fred],
                lambda provider: provider.get_macro_series(series_id),
                lambda chain: _sample_macro_series(series_id, chain),
            ),
        )

    def get_treasury_rates(self) -> NormalizedDataPoint:
        return self._cached(
            "treasury_rates",
            {},
            lambda: self._route_with_fallback(
                [self.treasury],
                lambda provider: provider.get_treasury_rates(),
                lambda chain: _sample_treasury_rate(chain),
            ),
        )

    def _route_with_fallback(
        self,
        providers: list[BaseDataProvider],
        call: Callable[[BaseDataProvider], Any],
        sample_fallback: Callable[[list[ProviderFallbackStep]], Any],
    ) -> Any:
        chain: list[ProviderFallbackStep] = []
        if settings.data_provider_mode == "mock":
            chain.append(
                ProviderFallbackStep(
                    provider="croclens_sample_fallback",
                    status="used",
                    reason="DATA_PROVIDER_MODE=mock",
                )
            )
            return sample_fallback(chain)

        for provider in providers:
            if not provider.is_configured():
                chain.append(
                    ProviderFallbackStep(
                        provider=provider.provider_id,
                        status="skipped",
                        reason="provider is not configured",
                    )
                )
                continue

            try:
                result = call(provider)
                result.fallback_chain = chain + [
                    ProviderFallbackStep(provider=provider.provider_id, status="used", reason="primary route succeeded")
                ]
                return result
            except DataProviderError as exc:
                chain.append(
                    ProviderFallbackStep(provider=provider.provider_id, status="failed", reason=str(exc))
                )

        chain.append(
            ProviderFallbackStep(
                provider="croclens_sample_fallback",
                status="used",
                reason="all live providers were unavailable, unconfigured, or failed",
            )
        )
        return sample_fallback(chain)

    def _cached(self, method: str, params: dict[str, Any], factory: Callable[[], Any]) -> Any:
        key = f"{method}:{sorted(params.items())}"
        cached = self.cache.get(key)
        if cached is not None:
            return cached

        value = factory()
        self.cache.set(key, value)
        return value


def _sample_as_of(days_ago: int = 1) -> datetime:
    return datetime(2026, 5, 6, 20, 0, tzinfo=UTC) - timedelta(days=days_ago - 1)


def _sample_market_price(symbol: str, chain: list[ProviderFallbackStep]) -> NormalizedDataPoint:
    prices = {"AAPL": 187.42, "MSFT": 421.18, "VOO": 486.2, "VTI": 261.81, "AGG": 97.66}
    upper_symbol = symbol.upper()
    return NormalizedDataPoint(
        provider="croclens_sample_fallback",
        source_type="market_price",
        asset_type="etf" if upper_symbol in {"VOO", "VTI", "AGG"} else "stock",
        symbol_or_series_id=upper_symbol,
        value=prices.get(upper_symbol, 100.0),
        currency="USD",
        as_of=_sample_as_of(),
        retrieved_at=utc_now(),
        source_url=None,
        freshness="sample fallback",
        confidence="low",
        limitations=SAMPLE_LIMITATIONS,
        fallback_chain=chain,
    )


def _sample_price_history(symbol: str, chain: list[ProviderFallbackStep]) -> PriceHistoryResponse:
    base = _sample_market_price(symbol, chain).value
    points = [
        PriceHistoryPoint(
            date=_sample_as_of(6 - index),
            open=round(base * (0.96 + index * 0.006), 2),
            high=round(base * (0.98 + index * 0.006), 2),
            low=round(base * (0.95 + index * 0.006), 2),
            close=round(base * (0.97 + index * 0.006), 2),
            volume=1000000 + index * 25000,
        )
        for index in range(6)
    ]
    return PriceHistoryResponse(
        provider="croclens_sample_fallback",
        asset_type="stock",
        symbol_or_series_id=symbol.upper(),
        currency="USD",
        as_of=points[-1].date,
        retrieved_at=utc_now(),
        source_url=None,
        freshness="sample fallback",
        confidence="low",
        limitations=SAMPLE_LIMITATIONS,
        points=points,
        fallback_chain=chain,
    )


def _sample_crypto_price(coin_id: str, chain: list[ProviderFallbackStep]) -> NormalizedDataPoint:
    values = {"bitcoin": 66421.35, "ethereum": 3200.0}
    return NormalizedDataPoint(
        provider="croclens_sample_fallback",
        source_type="crypto_price",
        asset_type="crypto",
        symbol_or_series_id=coin_id.lower(),
        value=values.get(coin_id.lower(), 100.0),
        currency="USD",
        as_of=_sample_as_of(),
        retrieved_at=utc_now(),
        source_url=None,
        freshness="sample fallback",
        confidence="low",
        limitations=SAMPLE_LIMITATIONS,
        fallback_chain=chain,
    )


def _sample_macro_series(series_id: str, chain: list[ProviderFallbackStep]) -> NormalizedDataPoint:
    values = {"CPIAUCSL": 315.6, "UNRATE": 4.0, "MORTGAGE30US": 6.75}
    return NormalizedDataPoint(
        provider="croclens_sample_fallback",
        source_type="macro_series",
        asset_type="macro",
        symbol_or_series_id=series_id.upper(),
        value=values.get(series_id.upper(), 1.0),
        currency=None,
        as_of=_sample_as_of(30),
        retrieved_at=utc_now(),
        source_url=None,
        freshness="sample fallback",
        confidence="low",
        limitations=SAMPLE_LIMITATIONS,
        fallback_chain=chain,
    )


def _sample_treasury_rate(chain: list[ProviderFallbackStep]) -> NormalizedDataPoint:
    return NormalizedDataPoint(
        provider="croclens_sample_fallback",
        source_type="treasury_rates",
        asset_type="treasury",
        symbol_or_series_id="US10Y_SAMPLE",
        value=4.18,
        currency=None,
        as_of=_sample_as_of(),
        retrieved_at=utc_now(),
        source_url=None,
        freshness="sample fallback",
        confidence="low",
        limitations=SAMPLE_LIMITATIONS,
        fallback_chain=chain,
    )


_registry: DataProviderRegistry | None = None


def get_data_provider_registry() -> DataProviderRegistry:
    global _registry
    if _registry is None:
        _registry = DataProviderRegistry()
    return _registry
