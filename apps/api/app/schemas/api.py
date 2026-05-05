from typing import Literal

from pydantic import BaseModel, Field


ConfidenceLevel = Literal["low", "medium", "high"]
TrendDirection = Literal["up", "down", "flat"]


class SourceMetadata(BaseModel):
    name: str
    freshness: str
    as_of: str | None = None


class HealthResponse(BaseModel):
    status: Literal["ok"]
    service: str
    version: str


class AllocationItem(BaseModel):
    asset_class: str
    percent: float = Field(ge=0, le=100)
    market_value: float = Field(ge=0)


class DebtImpact(BaseModel):
    debt_to_asset_percent: float = Field(ge=0)
    total_liabilities: float = Field(ge=0)
    explanation: str


class ScoreItem(BaseModel):
    label: str
    value: int = Field(ge=0, le=100)
    explanation: str
    formula: str


class PortfolioSummaryResponse(BaseModel):
    user_name: str
    total_assets: float = Field(ge=0)
    total_liabilities: float = Field(ge=0)
    net_worth: float
    allocation: list[AllocationItem]
    debt_impact: DebtImpact
    scores: list[ScoreItem]
    sources: list[SourceMetadata]
    educational_disclaimer: str


class AssetResponse(BaseModel):
    id: str
    symbol: str
    name: str
    asset_type: str
    current_price: float | None = None
    market_value: float = Field(ge=0)
    allocation_percent: float = Field(ge=0, le=100)
    risk_level: Literal["low", "medium", "high"]
    beginner_explanation: str
    source: SourceMetadata


class ActionPlanItem(BaseModel):
    id: str
    title: str
    description: str
    priority: Literal["low", "medium", "high"]
    status: Literal["suggested", "in_progress", "completed"]
    safe_wording_note: str


class ActionPlanResponse(BaseModel):
    plan_id: str
    items: list[ActionPlanItem]
    confidence: ConfidenceLevel
    data_limitations: list[str]
    educational_disclaimer: str


class AssistantRequest(BaseModel):
    question: str = Field(min_length=3, max_length=500)
    beginner_mode: bool = True


class AssistantResponse(BaseModel):
    summary: str
    beginner_explanation: str
    suggested_next_steps: list[str]
    confidence: ConfidenceLevel
    data_limitations: list[str]
    sources: list[SourceMetadata]
    safety_disclaimer: str
