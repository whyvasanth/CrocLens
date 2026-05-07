from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


ProviderCapability = Literal[
    "market_price",
    "price_history",
    "company_profile",
    "company_filings",
    "technical_indicators",
    "crypto_price",
    "macro_series",
    "treasury_rates",
    "housing_index",
    "census_context",
    "security_mapping",
]
ProviderHealth = Literal["configured", "unconfigured", "fallback_only", "unavailable"]
SourceType = Literal[
    "sample",
    "market_price",
    "price_history",
    "technical_indicator",
    "crypto_price",
    "macro_series",
    "treasury_rates",
    "company_filing",
    "housing_index",
    "census_context",
    "security_mapping",
]
ProviderAssetType = Literal[
    "stock",
    "etf",
    "mutual_fund",
    "crypto",
    "macro",
    "treasury",
    "real_estate",
    "cash",
    "bond",
    "liability",
    "unknown",
]
ProviderConfidence = Literal["low", "medium", "high"]


class ProviderFallbackStep(BaseModel):
    provider: str
    status: Literal["used", "skipped", "failed"]
    reason: str


class NormalizedDataPoint(BaseModel):
    provider: str
    source_type: SourceType
    asset_type: ProviderAssetType
    symbol_or_series_id: str
    value: float
    currency: str | None = None
    as_of: datetime
    retrieved_at: datetime
    source_url: str | None = None
    freshness: str
    confidence: ProviderConfidence
    limitations: list[str]
    raw_payload: dict[str, Any] | None = None
    fallback_chain: list[ProviderFallbackStep] = Field(default_factory=list)


class PriceHistoryPoint(BaseModel):
    date: datetime
    open: float | None = None
    high: float | None = None
    low: float | None = None
    close: float
    volume: float | None = None


class PriceHistoryResponse(BaseModel):
    provider: str
    source_type: Literal["price_history"] = "price_history"
    asset_type: ProviderAssetType
    symbol_or_series_id: str
    currency: str | None = None
    as_of: datetime
    retrieved_at: datetime
    source_url: str | None = None
    freshness: str
    confidence: ProviderConfidence
    limitations: list[str]
    points: list[PriceHistoryPoint]
    raw_payload: dict[str, Any] | None = None
    fallback_chain: list[ProviderFallbackStep] = Field(default_factory=list)


class TechnicalIndicator(BaseModel):
    name: str
    value: float | None
    explanation: str


class TechnicalIndicatorResponse(BaseModel):
    provider: str
    source_type: Literal["technical_indicator"] = "technical_indicator"
    asset_type: ProviderAssetType
    symbol_or_series_id: str
    as_of: datetime
    retrieved_at: datetime
    freshness: str
    confidence: ProviderConfidence
    limitations: list[str]
    indicators: list[TechnicalIndicator]
    source_url: str | None = None
    fallback_chain: list[ProviderFallbackStep] = Field(default_factory=list)


class ProviderStatus(BaseModel):
    id: str
    name: str
    source_type: str
    capabilities: list[ProviderCapability]
    configured: bool
    health: ProviderHealth
    requires_api_key: bool
    cost_note: str
    limitations: list[str]


class DataFreshnessItem(BaseModel):
    provider: str
    status: ProviderHealth
    last_retrieved_at: datetime | None = None
    cache_ttl_seconds: int
    note: str


class DataFreshnessResponse(BaseModel):
    mode: str
    providers: list[DataFreshnessItem]
