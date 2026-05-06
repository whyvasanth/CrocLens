from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


ConfidenceLevel = Literal["low", "medium", "high"]
TrendDirection = Literal["up", "down", "flat"]
AssetDetailCategory = Literal["stock_etf", "crypto", "real_estate", "debt", "retirement"]
AssistantIntent = Literal["portfolio", "debt", "retirement", "tax", "market", "risk", "education", "safety"]
AgentRole = Literal[
    "intent_router",
    "portfolio_analyst",
    "cross_asset_comparison",
    "stock_etf_research",
    "crypto_research",
    "real_estate_insight",
    "news_impact",
    "tax_aware",
    "retirement_planner",
    "debt_liability_coach",
    "action_plan",
    "decision_journal_feedback",
    "safety_compliance_guardrail",
]
AgentStatus = Literal["planned", "used", "skipped"]
MetricTone = Literal["green", "gold", "blue", "coral", "neutral"]
EmployerMatchStatus = Literal["yes", "no", "not_sure", "not_applicable"]
IncomeRange = Literal["under_50k", "50k_100k", "100k_200k", "over_200k", "prefer_not"]
InvestmentExperience = Literal["new", "some", "experienced"]
PrimaryGoal = Literal["learn", "build_wealth", "retirement", "debt_payoff", "home", "emergency_fund"]
RiskToleranceInput = Literal["low", "medium", "high"]
TimeHorizon = Literal["short", "medium", "long"]
DataProviderKind = Literal["manual", "sample_file", "free_api", "paid_optional"]
DataQualitySeverity = Literal["info", "warning", "error"]
FreshnessStatus = Literal["fresh", "stale", "sample", "unknown"]
MarketAssetClass = Literal["stock", "etf", "crypto", "treasury", "macro", "real_estate"]
MarketMetricType = Literal["price", "index_level", "yield", "rate", "housing_index"]
PipelineRunStatus = Literal["completed", "completed_with_warnings", "failed"]
ImpactDirection = Literal["positive", "negative", "mixed", "neutral"]
ImpactLevel = Literal["low", "medium", "high"]
HoldingTerm = Literal["short_term", "long_term"]
DecisionType = Literal[
    "buy",
    "sell",
    "hold",
    "watch",
    "rebalance",
    "debt_payoff",
    "retirement_contribution_change",
]


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


class AssetDetailMetric(BaseModel):
    label: str
    value: str
    explanation: str
    tone: MetricTone = "neutral"


class AssetDetailCard(BaseModel):
    id: str
    symbol: str
    name: str
    category: AssetDetailCategory
    asset_type: str
    current_value: float = Field(ge=0)
    risk_level: Literal["low", "medium", "high"]
    summary: str


class AssetDetailResponse(BaseModel):
    id: str
    symbol: str
    name: str
    category: AssetDetailCategory
    asset_type: str
    current_value: float = Field(ge=0)
    allocation_percent: float = Field(ge=0, le=100)
    risk_level: Literal["low", "medium", "high"]
    portfolio_role: str
    headline: str
    what_this_is: str
    why_it_matters: str
    risk_explanation: str
    liquidity_explanation: str
    tax_complexity_explanation: str
    income_potential_explanation: str
    what_to_watch: list[str]
    beginner_takeaway: str
    safe_next_steps: list[str]
    key_metrics: list[AssetDetailMetric]
    confidence: ConfidenceLevel
    data_limitations: list[str]
    source: SourceMetadata
    educational_disclaimer: str


class ManualAssetEntry(BaseModel):
    asset_class: str = Field(min_length=2, max_length=40)
    label: str = Field(min_length=2, max_length=80)
    estimated_value: float = Field(ge=0)


class OnboardingProfileRequest(BaseModel):
    investment_experience: InvestmentExperience
    primary_goal: PrimaryGoal
    risk_tolerance: RiskToleranceInput
    time_horizon: TimeHorizon
    income_range: IncomeRange
    emergency_cash_months: int = Field(ge=0, le=36)
    has_retirement_account: bool
    employer_match: EmployerMatchStatus
    retirement_contribution_percent: float | None = Field(default=None, ge=0, le=100)
    has_mortgage: bool
    has_student_loans: bool
    has_credit_card_debt: bool
    has_high_interest_debt: bool
    manual_assets: list[ManualAssetEntry] = Field(default_factory=list, max_length=12)


class OnboardingProfileResponse(BaseModel):
    profile_id: str
    risk_profile: str
    risk_score: int = Field(ge=0, le=100)
    summary: str
    personalization_notes: list[str]
    recommended_first_steps: list[str]
    confidence: ConfidenceLevel
    data_limitations: list[str]
    source: SourceMetadata
    educational_disclaimer: str


class OnboardingOptionsResponse(BaseModel):
    investment_experience: list[str]
    primary_goal: list[str]
    risk_tolerance: list[str]
    time_horizon: list[str]
    income_range: list[str]
    employer_match: list[str]


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
    include_prompt_debug: bool = False


class AssistantPromptContext(BaseModel):
    prompt_version: str
    intent: AssistantIntent
    system_rules: list[str]
    context_summary: str
    user_question: str


class AssistantSafetyCheck(BaseModel):
    passed: bool
    flags: list[str]
    rewritten_question: str | None = None


class AgentTraceStep(BaseModel):
    agent: AgentRole
    title: str
    status: AgentStatus
    input_summary: str
    output_summary: str
    tools_used: list[str] = Field(default_factory=list)


class AgentRegistryItem(BaseModel):
    agent: AgentRole
    title: str
    purpose: str
    uses_tools: bool
    current_status: Literal["implemented", "stubbed"]


class AgentRegistryResponse(BaseModel):
    agents: list[AgentRegistryItem]
    orchestration_note: str


class AssistantResponse(BaseModel):
    intent: AssistantIntent
    summary: str
    beginner_explanation: str
    suggested_next_steps: list[str]
    confidence: ConfidenceLevel
    data_limitations: list[str]
    sources: list[SourceMetadata]
    safety: AssistantSafetyCheck
    agent_trace: list[AgentTraceStep] = Field(default_factory=list)
    prompt_context: AssistantPromptContext | None = None
    safety_disclaimer: str


class DataProviderResponse(BaseModel):
    id: str
    name: str
    provider_type: DataProviderKind
    asset_classes: list[str]
    authentication: str
    cost_model: str
    current_use: str
    notes: list[str]


class DataQualityIssue(BaseModel):
    severity: DataQualitySeverity
    code: str
    message: str
    record_symbol: str | None = None


class DataFreshnessReport(BaseModel):
    status: FreshnessStatus
    as_of: datetime
    retrieved_at: datetime
    explanation: str


class MarketObservation(BaseModel):
    symbol: str = Field(min_length=1, max_length=32)
    name: str = Field(min_length=2, max_length=120)
    asset_class: MarketAssetClass
    metric_type: MarketMetricType
    value: float = Field(ge=0)
    unit: str = Field(min_length=1, max_length=40)
    currency: str | None = Field(default=None, max_length=8)
    change_percent: float | None = None
    trend: TrendDirection
    as_of: datetime
    retrieved_at: datetime
    source: SourceMetadata
    source_url: str | None = None
    data_limitations: list[str]


class SampleMarketDataFile(BaseModel):
    dataset_id: str
    generated_for: str
    source_name: str
    source_url: str | None = None
    provider_type: DataProviderKind
    as_of: datetime
    retrieved_at: datetime
    records: list[MarketObservation]


class MarketDataIngestionResponse(BaseModel):
    pipeline_name: str
    dataset_id: str
    provider: DataProviderResponse
    status: PipelineRunStatus
    extracted_count: int = Field(ge=0)
    accepted_count: int = Field(ge=0)
    rejected_count: int = Field(ge=0)
    freshness_report: DataFreshnessReport
    quality_issues: list[DataQualityIssue]
    records: list[MarketObservation]
    confidence: ConfidenceLevel
    data_limitations: list[str]
    sources: list[SourceMetadata]
    educational_disclaimer: str


class NewsArticleResponse(BaseModel):
    id: str
    title: str
    source_name: str
    published_at: str
    summary: str
    topic: str
    affected_asset_classes: list[str]
    source_url: str | None = None
    confidence: ConfidenceLevel
    data_limitations: list[str]


class HoldingImpactResponse(BaseModel):
    holding_id: str
    symbol: str
    name: str
    asset_type: str
    impact_direction: ImpactDirection
    impact_level: ImpactLevel
    why_it_matters: str
    what_to_watch: list[str]


class MarketNewsImpactResponse(BaseModel):
    headline: str
    beginner_summary: str
    portfolio_exposure_summary: str
    articles: list[NewsArticleResponse]
    affected_holdings: list[HoldingImpactResponse]
    suggested_questions: list[str]
    confidence: ConfidenceLevel
    data_limitations: list[str]
    sources: list[SourceMetadata]
    educational_disclaimer: str


class TaxLotResponse(BaseModel):
    id: str
    symbol: str
    asset_name: str
    quantity: float = Field(gt=0)
    purchase_date: str
    cost_basis: float = Field(ge=0)
    current_value: float = Field(ge=0)
    unrealized_gain_loss: float
    holding_period_days: int = Field(ge=0)
    holding_term: HoldingTerm
    beginner_explanation: str


class TaxOpportunityResponse(BaseModel):
    id: str
    symbol: str
    title: str
    estimated_unrealized_loss: float = Field(ge=0)
    explanation: str
    safe_next_steps: list[str]


class TaxInsightResponse(BaseModel):
    headline: str
    beginner_summary: str
    total_unrealized_gain: float
    total_unrealized_loss: float = Field(ge=0)
    tax_lots: list[TaxLotResponse]
    harvesting_opportunities: list[TaxOpportunityResponse]
    short_term_vs_long_term_explanation: str
    wash_sale_warning: str
    confidence: ConfidenceLevel
    data_limitations: list[str]
    sources: list[SourceMetadata]
    educational_disclaimer: str


class RetirementAccountResponse(BaseModel):
    id: str
    account_type: str
    provider_name: str
    current_balance: float = Field(ge=0)
    contribution_percent: float = Field(ge=0, le=100)
    annual_contribution_estimate: float = Field(ge=0)
    investment_mix_summary: str


class EmployerMatchResponse(BaseModel):
    has_match: bool
    formula: str
    estimated_annual_match: float = Field(ge=0)
    beginner_explanation: str


class RetirementScenarioResponse(BaseModel):
    id: str
    label: str
    contribution_percent: float = Field(ge=0, le=100)
    estimated_annual_employee_contribution: float = Field(ge=0)
    estimated_annual_employer_match: float = Field(ge=0)
    projected_balance_at_65: float = Field(ge=0)
    assumptions: list[str]


class RetirementPlanResponse(BaseModel):
    headline: str
    progress_percent: int = Field(ge=0, le=100)
    target_retirement_balance: float = Field(ge=0)
    current_retirement_balance: float = Field(ge=0)
    accounts: list[RetirementAccountResponse]
    employer_match: EmployerMatchResponse
    scenarios: list[RetirementScenarioResponse]
    beginner_summary: str
    suggested_reviews: list[str]
    confidence: ConfidenceLevel
    data_limitations: list[str]
    sources: list[SourceMetadata]
    educational_disclaimer: str


class DecisionJournalEntryResponse(BaseModel):
    id: str
    decision_type: DecisionType
    title: str
    asset_symbol: str | None = None
    reason: str
    expected_outcome: str
    risk_considered: str
    review_date: str
    created_at: str
    status: Literal["open", "reviewed"]
    feedback_summary: str


class DecisionJournalCreateRequest(BaseModel):
    decision_type: DecisionType
    title: str = Field(min_length=3, max_length=120)
    asset_symbol: str | None = Field(default=None, max_length=20)
    reason: str = Field(min_length=10, max_length=500)
    expected_outcome: str = Field(min_length=10, max_length=500)
    risk_considered: str = Field(min_length=10, max_length=500)
    review_date: str


class DecisionJournalResponse(BaseModel):
    entries: list[DecisionJournalEntryResponse]
    feedback_prompts: list[str]
    beginner_summary: str
    confidence: ConfidenceLevel
    data_limitations: list[str]
    sources: list[SourceMetadata]
    educational_disclaimer: str
