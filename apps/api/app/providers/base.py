from __future__ import annotations

from dataclasses import dataclass
from typing import Awaitable, Callable

from app.providers.exceptions import ProviderCapabilityError, ProviderUnavailableError
from app.providers.models import (
    CompanyProfile,
    FilingSummary,
    MarketHistory,
    MarketQuote,
    ProviderCapability,
    ProviderHealth,
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

    def _raise_unsupported(self, capability: ProviderCapability) -> None:
        raise ProviderCapabilityError(f"{self.display_name} does not support {capability}.")


ProviderFactory = Callable[[ProviderRuntimeConfig], BaseProvider]
