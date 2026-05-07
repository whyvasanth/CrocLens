from datetime import UTC, datetime

from app.data_providers.errors import CapabilityNotSupportedError
from app.data_providers.schemas import (
    NormalizedDataPoint,
    PriceHistoryResponse,
    ProviderCapability,
    ProviderStatus,
    TechnicalIndicatorResponse,
)


def utc_now() -> datetime:
    return datetime.now(tz=UTC)


class BaseDataProvider:
    provider_id: str = "base"
    display_name: str = "Base Provider"
    source_type: str = "unknown"
    capabilities: list[ProviderCapability] = []
    requires_api_key: bool = False
    cost_note: str = "Unknown"
    limitations: list[str] = []

    def is_configured(self) -> bool:
        return not self.requires_api_key

    def status(self) -> ProviderStatus:
        configured = self.is_configured()
        return ProviderStatus(
            id=self.provider_id,
            name=self.display_name,
            source_type=self.source_type,
            capabilities=self.capabilities,
            configured=configured,
            health="configured" if configured else "unconfigured",
            requires_api_key=self.requires_api_key,
            cost_note=self.cost_note,
            limitations=self.limitations,
        )

    def get_market_price(self, symbol: str) -> NormalizedDataPoint:
        raise CapabilityNotSupportedError(f"{self.provider_id} does not support market prices.")

    def get_price_history(self, symbol: str, period: str = "1mo") -> PriceHistoryResponse:
        raise CapabilityNotSupportedError(f"{self.provider_id} does not support price history.")

    def get_technical_indicators(self, history: PriceHistoryResponse) -> TechnicalIndicatorResponse:
        raise CapabilityNotSupportedError(f"{self.provider_id} does not support technical indicators.")

    def get_crypto_price(self, coin_id: str) -> NormalizedDataPoint:
        raise CapabilityNotSupportedError(f"{self.provider_id} does not support crypto prices.")

    def get_macro_series(self, series_id: str) -> NormalizedDataPoint:
        raise CapabilityNotSupportedError(f"{self.provider_id} does not support macro series.")

    def get_treasury_rates(self) -> NormalizedDataPoint:
        raise CapabilityNotSupportedError(f"{self.provider_id} does not support Treasury rates.")
