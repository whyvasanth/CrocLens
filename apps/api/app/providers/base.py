from __future__ import annotations

from dataclasses import dataclass
from typing import Awaitable, Callable

from app.providers.exceptions import ProviderCapabilityError, ProviderUnavailableError
from app.providers.cache import ProviderMemoryCache
from app.providers.models import (
    CompanyProfile,
    CorporateAction,
    EconomicObservation,
    FilingSummary,
    MarketHistory,
    MarketQuote,
    ProviderCapability,
    ProviderErrorDetails,
    ProviderHealth,
    utc_now,
)


@dataclass(frozen=True)
class ProviderRuntimeConfig:
    timeout_seconds: int
    retry_limit: int
    cache_ttl_seconds: int
    stale_after_seconds: int
    user_agent: str


class BaseProvider:
    name = "base"
    display_name = "Base provider"
    capabilities: tuple[ProviderCapability, ...] = ()

    def __init__(
        self,
        *,
        enabled: bool,
        configured: bool = True,
        config: ProviderRuntimeConfig,
        data_limitations: list[str],
    ) -> None:
        self.enabled = enabled
        self.configured = configured
        self.config = config
        self.data_limitations = data_limitations
        self.cache = ProviderMemoryCache(config.cache_ttl_seconds)
        self._last_successful_request = None
        self._last_error = None

    async def health_check(self) -> ProviderHealth:
        status = "healthy" if self.enabled and self.configured else "disabled"
        if self.enabled and not self.configured:
            status = "not_configured"

        return ProviderHealth(
            provider_name=self.name,
            display_name=self.display_name,
            enabled=self.enabled,
            configured=self.configured,
            provider_status=status,
            capabilities=list(self.capabilities),
            cache_ttl_seconds=self.config.cache_ttl_seconds,
            stale_after_seconds=self.config.stale_after_seconds,
            last_successful_request=self._last_successful_request,
            last_error=self._last_error,
            cache_status=self.cache.status(),
            data_limitations=self.data_limitations,
        )

    def supports(self, capability: ProviderCapability) -> bool:
        return capability in self.capabilities

    async def get_quote(self, symbol: str) -> MarketQuote:
        self._raise_unsupported("quote")

    async def get_history(self, symbol: str, period: str, interval: str) -> MarketHistory:
        self._raise_unsupported("history")

    async def get_profile(self, symbol: str) -> CompanyProfile:
        self._raise_unsupported("profile")

    async def get_dividends(self, symbol: str) -> CorporateAction:
        self._raise_unsupported("dividends")

    async def get_splits(self, symbol: str) -> CorporateAction:
        self._raise_unsupported("splits")

    async def get_crypto_price(self, coin_id: str) -> MarketQuote:
        self._raise_unsupported("crypto_price")

    async def get_macro_observation(self, series_id: str) -> EconomicObservation:
        self._raise_unsupported("macro_series")

    async def get_treasury_rates(self) -> list[EconomicObservation]:
        self._raise_unsupported("treasury_rates")

    async def get_filings(self, symbol: str) -> list[FilingSummary]:
        self._raise_unsupported("sec_filings")

    async def _call_sync(self, callback: Callable[[], object]) -> object:
        import asyncio

        return await asyncio.to_thread(callback)

    def _ensure_available(self) -> None:
        if not self.enabled:
            raise ProviderUnavailableError(f"{self.display_name} is disabled.")
        if not self.configured:
            raise ProviderUnavailableError(f"{self.display_name} is not configured.")

    def _record_success(self) -> None:
        self._last_successful_request = utc_now()
        self._last_error = None

    def _record_error(self, code: str, message: str, retryable: bool = True) -> None:
        self._last_error = ProviderErrorDetails(code=code, message=message, retryable=retryable)

    def _raise_unsupported(self, capability: ProviderCapability) -> None:
        raise ProviderCapabilityError(f"{self.display_name} does not support {capability}.")


ProviderFactory = Callable[[ProviderRuntimeConfig], BaseProvider]
