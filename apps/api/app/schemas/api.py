from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


ConfidenceLevel = Literal["low", "medium", "high"]
TrendDirection = Literal["up", "down", "flat"]
AssetDetailCategory = Literal["stock_etf", "crypto", "real_estate", "debt", "retirement", "cash", "bond", "other"]
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
DataProviderKind = Literal["manual", "sample_file", "free_api"]
DataQualitySeverity = Literal["info", "warning", "error"]
FreshnessStatus = Literal["fresh", "stale", "sample", "unknown"]
MarketAssetClass = Literal["stock", "etf", "crypto", "treasury", "macro", "real_estate"]
MarketMetricType = Literal["price", "index_level", "yield", "rate", "housing_index"]
PipelineRunStatus = Literal["completed", "completed_with_warnings", "failed"]
ImpactDirection = Literal["positive", "negative", "mixed", "neutral"]
ImpactLevel = Literal["low", "medium", "high"]
HoldingTerm = Literal["short_term", "long_term"]
MarketPeriod = Literal["1M", "3M", "6M", "YTD", "1Y", "5Y", "ALL"]
MarketInterval = Literal["1d", "1wk", "1mo"]
ValuationMethod = Literal["provider_valued", "manually_valued", "stale_value", "unavailable_value"]
DecisionType = Literal[
    "buy",
    "sell",
    "hold",
    "watch",
    "rebalance",
    "debt_payoff",
    "retirement_contribution_change",
]
WatchlistAssetType = Literal["stock", "etf", "crypto", "real_estate_market", "bond", "treasury", "other"]
EvaluationMetricCategory = Literal["product", "ai_safety", "data_quality", "reliability"]
EvaluationMetricStatus = Literal["healthy", "watch", "needs_attention"]
EvaluationMetricDirection = Literal["higher_is_better", "lower_is_better"]


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


AssetTypeInput = Literal[
    "Stocks",
    "ETFs",
    "Mutual Funds",
    "Crypto",
    "Real Estate",
    "Cash",
    "Bonds",
    "Treasuries",
    "Retirement",
    "Other",
]
LiabilityTypeInput = Literal["Mortgage", "Student loan", "Credit card", "Auto loan", "Personal loan", "Other"]


class HoldingCreateRequest(BaseModel):
    symbol: str = Field(min_length=1, max_length=40)
    name: str = Field(min_length=2, max_length=255)
    asset_type: AssetTypeInput
    account_name: str | None = Field(default=None, max_length=120)
    quantity: float = Field(default=0, ge=0)
    cost_basis: float | None = Field(default=None, ge=0)
    market_value: float = Field(ge=0)
    as_of_date: str | None = None


class HoldingUpdateRequest(BaseModel):
    symbol: str | None = Field(default=None, min_length=1, max_length=40)
    name: str | None = Field(default=None, min_length=2, max_length=255)
    asset_type: AssetTypeInput | None = None
    account_name: str | None = Field(default=None, max_length=120)
    quantity: float | None = Field(default=None, ge=0)
    cost_basis: float | None = Field(default=None, ge=0)
    market_value: float | None = Field(default=None, ge=0)
    as_of_date: str | None = None


class HoldingResponse(BaseModel):
    id: str
    portfolio_id: str
    asset_id: str
    symbol: str
    name: str
    asset_type: str
    account_name: str | None
    quantity: float
    cost_basis: float | None
    market_value: float
    allocation_percent: float = Field(ge=0, le=100)
    as_of_date: str | None
    source: SourceMetadata


class LiabilityCreateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    liability_type: LiabilityTypeInput
    balance: float = Field(ge=0)
    interest_rate: float | None = Field(default=None, ge=0, le=1)
    minimum_payment: float | None = Field(default=None, ge=0)
    due_day: int | None = Field(default=None, ge=1, le=31)


class LiabilityUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=160)
    liability_type: LiabilityTypeInput | None = None
    balance: float | None = Field(default=None, ge=0)
    interest_rate: float | None = Field(default=None, ge=0, le=1)
    minimum_payment: float | None = Field(default=None, ge=0)
    due_day: int | None = Field(default=None, ge=1, le=31)


class LiabilityResponse(BaseModel):
    id: str
    name: str
    liability_type: str
    balance: float
    interest_rate: float | None
    minimum_payment: float | None
    due_day: int | None
    source: SourceMetadata


class PortfolioRecordsResponse(BaseModel):
    holdings: list[HoldingResponse]
    liabilities: list[LiabilityResponse]
    summary: PortfolioSummaryResponse


class DeleteRecordResponse(BaseModel):
    status: Literal["deleted"]
    id: str


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


class AccountCreateRequest(BaseModel):
    display_name: str = Field(min_length=2, max_length=80)
    email: str = Field(min_length=5, max_length=120)
    password: str = Field(min_length=8, max_length=120)
    onboarding_profile: OnboardingProfileRequest


class AccountLoginRequest(BaseModel):
    email: str = Field(min_length=5, max_length=120)
    password: str = Field(min_length=8, max_length=120)


class AccountUserResponse(BaseModel):
    id: str
    display_name: str
    email: str
    beginner_mode_enabled: bool
    created_at: str


class AccountSessionResponse(BaseModel):
    user: AccountUserResponse
    onboarding_profile: OnboardingProfileResponse | None = None
    session_token: str
    token_type: Literal["local_session", "mock_session"]
    expires_in_minutes: int = Field(ge=1)
    next_path: str
    confidence: ConfidenceLevel
    data_limitations: list[str]
    sources: list[SourceMetadata]
    security_note: str


class LogoutResponse(BaseModel):
    status: Literal["logged_out"]


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


class ActionPlanStatusResponse(BaseModel):
    item: ActionPlanItem
    action: Literal["completed", "dismissed", "reopened"]
    explanation: str


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


class MarketDataQualityMetadata(BaseModel):
    provider_status: str
    source_name: str
    source_url: str | None = None
    data_as_of: datetime | None = None
    retrieved_at: datetime | None = None
    is_stale: bool
    is_sample_data: bool
    data_quality: str
    confidence: ConfidenceLevel
    data_limitations: list[str]
    warning: str | None = None


class MarketQuoteResponse(MarketDataQualityMetadata):
    symbol: str
    name: str
    asset_type: str
    price: float | None = None
    currency: str | None = "USD"


class MarketHistoryPointResponse(BaseModel):
    observed_at: datetime
    close: float = Field(ge=0)
    source_name: str
    data_quality: str
    is_stale: bool


class MarketHistoryResponse(MarketDataQualityMetadata):
    symbol: str
    name: str
    asset_type: str
    period: MarketPeriod
    interval: MarketInterval
    currency: str | None = "USD"
    points: list[MarketHistoryPointResponse]


class MarketSnapshotItemResponse(MarketDataQualityMetadata):
    symbol: str
    name: str
    asset_class: str
    metric_type: str
    value: float
    unit: str
    currency: str | None = None
    change_percent: float | None = None


class MarketSnapshotResponse(BaseModel):
    items: list[MarketSnapshotItemResponse]
    provider_status: str
    is_sample_data: bool
    data_quality: str
    data_limitations: list[str]
    educational_disclaimer: str


class PortfolioHistoryPointResponse(BaseModel):
    snapshot_date: str
    total_assets: float
    total_liabilities: float
    net_worth: float
    source_name: str
    data_quality: str


class PortfolioHistoryResponse(BaseModel):
    points: list[PortfolioHistoryPointResponse]
    confidence: ConfidenceLevel
    data_limitations: list[str]
    educational_disclaimer: str


class PortfolioRefreshPricesResponse(BaseModel):
    status: Literal["completed", "completed_with_warnings"]
    provider_name: str | None
    counts: dict[str, int]
    valuation_counts: dict[ValuationMethod, int]
    snapshot: PortfolioHistoryPointResponse
    summary: PortfolioSummaryResponse
    warnings: list[str]
    confidence: ConfidenceLevel
    data_limitations: list[str]
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


class TaxLotCreateRequest(BaseModel):
    holding_id: str = Field(min_length=1, max_length=36)
    acquired_date: str
    quantity: float = Field(gt=0)
    cost_basis: float = Field(ge=0)
    account_tax_type: str = Field(default="taxable", min_length=3, max_length=60)


class TaxLotUpdateRequest(BaseModel):
    acquired_date: str | None = None
    quantity: float | None = Field(default=None, gt=0)
    cost_basis: float | None = Field(default=None, ge=0)
    account_tax_type: str | None = Field(default=None, min_length=3, max_length=60)


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


class RetirementAccountCreateRequest(BaseModel):
    account_type: str = Field(min_length=2, max_length=60)
    provider_name: str | None = Field(default=None, max_length=160)
    current_balance: float = Field(ge=0)
    contribution_percent: float | None = Field(default=None, ge=0, le=100)
    employer_match_percent: float | None = Field(default=None, ge=0, le=100)


class RetirementAccountUpdateRequest(BaseModel):
    account_type: str | None = Field(default=None, min_length=2, max_length=60)
    provider_name: str | None = Field(default=None, max_length=160)
    current_balance: float | None = Field(default=None, ge=0)
    contribution_percent: float | None = Field(default=None, ge=0, le=100)
    employer_match_percent: float | None = Field(default=None, ge=0, le=100)


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
    actual_outcome: str | None = None
    reflection: str | None = None


class DecisionJournalCreateRequest(BaseModel):
    decision_type: DecisionType
    title: str = Field(min_length=3, max_length=120)
    asset_symbol: str | None = Field(default=None, max_length=20)
    reason: str = Field(min_length=10, max_length=500)
    expected_outcome: str = Field(min_length=10, max_length=500)
    risk_considered: str = Field(min_length=10, max_length=500)
    review_date: str


class DecisionJournalUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=120)
    reason: str | None = Field(default=None, min_length=10, max_length=500)
    expected_outcome: str | None = Field(default=None, min_length=10, max_length=500)
    risk_considered: str | None = Field(default=None, min_length=10, max_length=500)
    review_date: str | None = None
    status: Literal["open", "reviewed"] | None = None
    actual_outcome: str | None = Field(default=None, max_length=500)
    reflection: str | None = Field(default=None, max_length=500)


class DecisionJournalResponse(BaseModel):
    entries: list[DecisionJournalEntryResponse]
    feedback_prompts: list[str]
    beginner_summary: str
    confidence: ConfidenceLevel
    data_limitations: list[str]
    sources: list[SourceMetadata]
    educational_disclaimer: str


class WatchlistItemResponse(BaseModel):
    id: str
    symbol: str
    name: str
    asset_type: WatchlistAssetType
    why_watching: str
    ai_summary: str
    risk_notes: list[str]
    opportunity_notes: list[str]
    source: SourceMetadata
    confidence: ConfidenceLevel
    data_limitations: list[str]


class WatchlistCreateRequest(BaseModel):
    symbol: str = Field(min_length=1, max_length=32)
    name: str = Field(min_length=2, max_length=120)
    asset_type: WatchlistAssetType
    why_watching: str = Field(min_length=10, max_length=500)


class WatchlistUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    why_watching: str | None = Field(default=None, min_length=10, max_length=500)
    notes: str | None = Field(default=None, max_length=500)


class WatchlistResponse(BaseModel):
    items: list[WatchlistItemResponse]
    beginner_summary: str
    safe_research_prompts: list[str]
    confidence: ConfidenceLevel
    data_limitations: list[str]
    sources: list[SourceMetadata]
    educational_disclaimer: str


class SecurityStatusResponse(BaseModel):
    api_version: str
    authentication_status: str
    rate_limit_per_minute: int = Field(ge=0)
    security_headers_enabled: list[str]
    cors_origins: list[str]
    logging_summary: str
    prompt_injection_guardrails: list[str]
    data_rights: list[str]


class PrivacySettingsRequest(BaseModel):
    beginner_mode_enabled: bool = True
    store_assistant_history: bool = False
    allow_product_analytics: bool = False
    allow_external_integrations: bool = False
    data_retention_days: int = Field(default=30, ge=1, le=365)


class PrivacySettingsResponse(PrivacySettingsRequest):
    profile_id: str
    explanation: str
    updated_at: str


class DataExportResponse(BaseModel):
    export_id: str
    generated_at: str
    sections: list[str]
    record_counts: dict[str, int]
    delivery_note: str
    data_limitations: list[str]
    sources: list[SourceMetadata]


class DeleteDataResponse(BaseModel):
    request_id: str
    status: Literal["preview_only", "completed"]
    deleted_sections: list[str]
    explanation: str
    data_limitations: list[str]


class EvaluationMetricResponse(BaseModel):
    id: str
    label: str
    category: EvaluationMetricCategory
    value: float = Field(ge=0)
    unit: str
    target: str
    direction: EvaluationMetricDirection
    status: EvaluationMetricStatus
    sample_size: int = Field(ge=0)
    beginner_explanation: str
    how_measured: str
    limitations: list[str]


class EvaluationMetricsResponse(BaseModel):
    headline: str
    beginner_summary: str
    metrics: list[EvaluationMetricResponse]
    quality_checks: list[str]
    recommended_reviews: list[str]
    confidence: ConfidenceLevel
    data_limitations: list[str]
    sources: list[SourceMetadata]
    educational_disclaimer: str
