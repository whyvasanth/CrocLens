from app.core.config import settings
from app.providers.base import BaseProvider, ProviderRuntimeConfig
from app.providers.coingecko_provider import CoinGeckoProvider
from app.providers.fred_provider import FredProvider
from app.providers.models import ProviderCapability, ProviderHealth, ProviderStatusResponse
from app.providers.sec_provider import SecProvider
from app.providers.treasury_provider import TreasuryProvider
from app.providers.yfinance_provider import YFinanceProvider


class ProviderRegistry:
    def __init__(self, providers: list[BaseProvider], mode: str) -> None:
        self.providers = {provider.name: provider for provider in providers}
        self.mode = mode

    def providers_for(self, capability: ProviderCapability) -> list[BaseProvider]:
        return [
            provider
            for provider in self.providers.values()
            if provider.enabled and provider.configured and provider.supports(capability)
        ]

    async def status(self) -> ProviderStatusResponse:
        provider_statuses = [await provider.health_check() for provider in self.providers.values()]
        return ProviderStatusResponse(
            mode=self.mode,
            providers=provider_statuses,
            data_limitations=[
                "Phase 21A reports provider readiness only; it does not fetch live market data yet.",
                "Provider failures must never be silently relabeled as sample or live data.",
                "Later phases will add persistence, stale-cache warnings, and live quote/history endpoints.",
            ],
        )

    async def health_for_provider(self, provider_name: str) -> ProviderHealth | None:
        provider = self.providers.get(provider_name)
        if provider is None:
            return None
        return await provider.health_check()


def build_runtime_config() -> ProviderRuntimeConfig:
    return ProviderRuntimeConfig(
        timeout_seconds=settings.market_provider_timeout_seconds,
        retry_limit=settings.market_provider_retry_limit,
        cache_ttl_seconds=settings.market_provider_cache_ttl_seconds,
        stale_after_seconds=settings.market_provider_stale_after_seconds,
        user_agent=settings.market_provider_user_agent,
    )


def build_default_provider_registry() -> ProviderRegistry:
    runtime_config = build_runtime_config()
    return ProviderRegistry(
        mode=settings.market_provider_mode,
        providers=[
            YFinanceProvider(enabled=settings.enable_yfinance_provider, config=runtime_config),
            CoinGeckoProvider(enabled=settings.enable_coingecko_provider, config=runtime_config),
            FredProvider(enabled=settings.enable_fred_provider, config=runtime_config),
            TreasuryProvider(enabled=settings.enable_treasury_provider, config=runtime_config),
            SecProvider(
                enabled=settings.enable_sec_provider,
                user_agent=settings.sec_edgar_user_agent,
                config=runtime_config,
            ),
        ],
    )
