from datetime import UTC, date, datetime
from decimal import Decimal
from typing import Any, Literal

from pydantic import BaseModel, Field

ConfidenceLevel = Literal["low", "medium", "high"]
DataQuality = Literal["live", "delayed", "cached", "stale", "sample", "unavailable", "unknown"]
ProviderStatus = Literal["healthy", "degraded", "unavailable", "disabled", "not_configured"]
ProviderCapability = Literal[
    "quote",
    "history",
    "profile",
    "dividends",
    "splits",
    "crypto_price",
    "macro_series",
    "treasury_rates",
    "sec_filings",
]


def utc_now() -> datetime:
    return datetime.now(tz=UTC)


class ProviderErrorDetails(BaseModel):
    code: str
    message: str
    retryable: bool = False


class ProviderHealth(BaseModel):
    provider_name: str
    display_name: str
    enabled: bool
    configured: bool
    provider_status: ProviderStatus
    capabilities: list[ProviderCapability]
    cache_ttl_seconds: int = Field(ge=0)
    stale_after_seconds: int = Field(ge=0)
    last_successful_request: datetime | None = None
    last_error: ProviderErrorDetails | None = None
    cache_status: dict[str, int] = Field(default_factory=dict)
    data_limitations: list[str]


class ProviderStatusResponse(BaseModel):
    mode: str
    providers: list[ProviderHealth]
    data_limitations: list[str]


class ProviderResult(BaseModel):
    provider_name: str
    provider_status: ProviderStatus
    is_sample_data: bool
    data_quality: DataQuality
    confidence: ConfidenceLevel
    data_as_of: datetime | None
    retrieved_at: datetime
    is_stale: bool
    source_url: str | None = None
    data_limitations: list[str]
    error: ProviderErrorDetails | None = None
    raw_payload: dict[str, Any] | None = None


class MarketQuote(ProviderResult):
    symbol: str
    asset_type: str
    price: Decimal | None = None
    currency: str | None = "USD"
    change_percent: Decimal | None = None


class MarketHistoryPoint(BaseModel):
    observed_at: datetime
    open: Decimal | None = None
    high: Decimal | None = None
    low: Decimal | None = None
    close: Decimal
    volume: Decimal | None = None


class MarketHistory(ProviderResult):
    symbol: str
    asset_type: str
    period: str
    interval: str
    currency: str | None = "USD"
    points: list[MarketHistoryPoint]


class CorporateActionEvent(BaseModel):
    observed_at: datetime
    value: Decimal


class CorporateAction(ProviderResult):
    symbol: str
    action_type: Literal["dividend", "split"]
    events: list[CorporateActionEvent]


class CompanyProfile(ProviderResult):
    symbol: str
    company_name: str | None = None
    exchange: str | None = None
    sector: str | None = None
    industry: str | None = None
    website: str | None = None


class EconomicObservation(ProviderResult):
    series_id: str
    label: str
    value: Decimal | None = None
    unit: str | None = None
    observation_date: date | None = None


class FilingSummary(ProviderResult):
    symbol: str
    cik: str | None = None
    filing_type: str | None = None
    filing_date: date | None = None
    accession_number: str | None = None
    filing_url: str | None = None
