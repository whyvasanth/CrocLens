export type ConfidenceLevel = "low" | "medium" | "high";
export type RiskLevel = "low" | "medium" | "high";
export type AssetDetailCategory = "stock_etf" | "crypto" | "real_estate" | "debt" | "retirement";
export type AssistantIntent = "portfolio" | "debt" | "retirement" | "tax" | "market" | "risk" | "education" | "safety";
export type AgentRole =
  | "intent_router"
  | "portfolio_analyst"
  | "cross_asset_comparison"
  | "stock_etf_research"
  | "crypto_research"
  | "real_estate_insight"
  | "news_impact"
  | "tax_aware"
  | "retirement_planner"
  | "debt_liability_coach"
  | "action_plan"
  | "decision_journal_feedback"
  | "safety_compliance_guardrail";
export type AgentStatus = "planned" | "used" | "skipped";
export type MetricTone = "green" | "gold" | "blue" | "coral" | "neutral";
export type EmployerMatchStatus = "yes" | "no" | "not_sure" | "not_applicable";
export type IncomeRange = "under_50k" | "50k_100k" | "100k_200k" | "over_200k" | "prefer_not";
export type InvestmentExperience = "new" | "some" | "experienced";
export type PrimaryGoal = "learn" | "build_wealth" | "retirement" | "debt_payoff" | "home" | "emergency_fund";
export type RiskToleranceInput = "low" | "medium" | "high";
export type TimeHorizon = "short" | "medium" | "long";

export interface SourceMetadata {
  name: string;
  freshness: string;
  as_of: string | null;
}

export interface AllocationItem {
  asset_class: string;
  percent: number;
  market_value: number;
}

export interface ScoreItem {
  label: string;
  value: number;
  explanation: string;
  formula: string;
}

export interface DebtImpact {
  debt_to_asset_percent: number;
  total_liabilities: number;
  explanation: string;
}

export interface PortfolioSummaryResponse {
  user_name: string;
  total_assets: number;
  total_liabilities: number;
  net_worth: number;
  allocation: AllocationItem[];
  debt_impact: DebtImpact;
  scores: ScoreItem[];
  sources: SourceMetadata[];
  educational_disclaimer: string;
}

export interface AssetResponse {
  id: string;
  symbol: string;
  name: string;
  asset_type: string;
  current_price: number | null;
  market_value: number;
  allocation_percent: number;
  risk_level: RiskLevel;
  beginner_explanation: string;
  source: SourceMetadata;
}

export interface AssetDetailMetric {
  label: string;
  value: string;
  explanation: string;
  tone: MetricTone;
}

export interface AssetDetailCardResponse {
  id: string;
  symbol: string;
  name: string;
  category: AssetDetailCategory;
  asset_type: string;
  current_value: number;
  risk_level: RiskLevel;
  summary: string;
}

export interface AssetDetailResponse {
  id: string;
  symbol: string;
  name: string;
  category: AssetDetailCategory;
  asset_type: string;
  current_value: number;
  allocation_percent: number;
  risk_level: RiskLevel;
  portfolio_role: string;
  headline: string;
  what_this_is: string;
  why_it_matters: string;
  risk_explanation: string;
  liquidity_explanation: string;
  tax_complexity_explanation: string;
  income_potential_explanation: string;
  what_to_watch: string[];
  beginner_takeaway: string;
  safe_next_steps: string[];
  key_metrics: AssetDetailMetric[];
  confidence: ConfidenceLevel;
  data_limitations: string[];
  source: SourceMetadata;
  educational_disclaimer: string;
}

export interface ActionPlanItemResponse {
  id: string;
  title: string;
  description: string;
  priority: "low" | "medium" | "high";
  status: "suggested" | "in_progress" | "completed";
  safe_wording_note: string;
}

export interface ActionPlanResponse {
  plan_id: string;
  items: ActionPlanItemResponse[];
  confidence: ConfidenceLevel;
  data_limitations: string[];
  educational_disclaimer: string;
}

export interface ManualAssetEntry {
  asset_class: string;
  label: string;
  estimated_value: number;
}

export interface OnboardingProfileRequest {
  investment_experience: InvestmentExperience;
  primary_goal: PrimaryGoal;
  risk_tolerance: RiskToleranceInput;
  time_horizon: TimeHorizon;
  income_range: IncomeRange;
  emergency_cash_months: number;
  has_retirement_account: boolean;
  employer_match: EmployerMatchStatus;
  retirement_contribution_percent: number | null;
  has_mortgage: boolean;
  has_student_loans: boolean;
  has_credit_card_debt: boolean;
  has_high_interest_debt: boolean;
  manual_assets: ManualAssetEntry[];
}

export interface OnboardingProfileResponse {
  profile_id: string;
  risk_profile: string;
  risk_score: number;
  summary: string;
  personalization_notes: string[];
  recommended_first_steps: string[];
  confidence: ConfidenceLevel;
  data_limitations: string[];
  source: SourceMetadata;
  educational_disclaimer: string;
}

export interface OnboardingOptionsResponse {
  investment_experience: InvestmentExperience[];
  primary_goal: PrimaryGoal[];
  risk_tolerance: RiskToleranceInput[];
  time_horizon: TimeHorizon[];
  income_range: IncomeRange[];
  employer_match: EmployerMatchStatus[];
}

export interface AccountCreateRequest {
  display_name: string;
  email: string;
  password: string;
  onboarding_profile: OnboardingProfileRequest;
}

export interface AccountLoginRequest {
  email: string;
  password: string;
}

export interface AccountUserResponse {
  id: string;
  display_name: string;
  email: string;
  beginner_mode_enabled: boolean;
  created_at: string;
}

export interface AccountSessionResponse {
  user: AccountUserResponse;
  onboarding_profile: OnboardingProfileResponse | null;
  session_token: string;
  token_type: "local_session" | "mock_session";
  expires_in_minutes: number;
  next_path: string;
  confidence: ConfidenceLevel;
  data_limitations: string[];
  sources: SourceMetadata[];
  security_note: string;
}

export interface LogoutResponse {
  status: "logged_out";
}

export interface AssistantRequest {
  question: string;
  beginner_mode: boolean;
  include_prompt_debug?: boolean;
}

export interface AssistantPromptContext {
  prompt_version: string;
  intent: AssistantIntent;
  system_rules: string[];
  context_summary: string;
  user_question: string;
}

export interface AssistantSafetyCheck {
  passed: boolean;
  flags: string[];
  rewritten_question: string | null;
}

export interface AgentTraceStep {
  agent: AgentRole;
  title: string;
  status: AgentStatus;
  input_summary: string;
  output_summary: string;
  tools_used: string[];
}

export interface AgentRegistryItem {
  agent: AgentRole;
  title: string;
  purpose: string;
  uses_tools: boolean;
  current_status: "implemented" | "stubbed";
}

export interface AgentRegistryResponse {
  agents: AgentRegistryItem[];
  orchestration_note: string;
}

export interface AssistantResponse {
  intent: AssistantIntent;
  summary: string;
  beginner_explanation: string;
  suggested_next_steps: string[];
  confidence: ConfidenceLevel;
  data_limitations: string[];
  sources: SourceMetadata[];
  safety: AssistantSafetyCheck;
  agent_trace: AgentTraceStep[];
  prompt_context: AssistantPromptContext | null;
  safety_disclaimer: string;
}

export interface NewsArticleResponse {
  id: string;
  title: string;
  source_name: string;
  published_at: string;
  summary: string;
  topic: string;
  affected_asset_classes: string[];
  source_url: string | null;
  confidence: ConfidenceLevel;
  data_limitations: string[];
}

export interface HoldingImpactResponse {
  holding_id: string;
  symbol: string;
  name: string;
  asset_type: string;
  impact_direction: "positive" | "negative" | "mixed" | "neutral";
  impact_level: "low" | "medium" | "high";
  why_it_matters: string;
  what_to_watch: string[];
}

export interface MarketNewsImpactResponse {
  headline: string;
  beginner_summary: string;
  portfolio_exposure_summary: string;
  articles: NewsArticleResponse[];
  affected_holdings: HoldingImpactResponse[];
  suggested_questions: string[];
  confidence: ConfidenceLevel;
  data_limitations: string[];
  sources: SourceMetadata[];
  educational_disclaimer: string;
}

export interface TaxLotResponse {
  id: string;
  symbol: string;
  asset_name: string;
  quantity: number;
  purchase_date: string;
  cost_basis: number;
  current_value: number;
  unrealized_gain_loss: number;
  holding_period_days: number;
  holding_term: "short_term" | "long_term";
  beginner_explanation: string;
}

export interface TaxOpportunityResponse {
  id: string;
  symbol: string;
  title: string;
  estimated_unrealized_loss: number;
  explanation: string;
  safe_next_steps: string[];
}

export interface TaxInsightResponse {
  headline: string;
  beginner_summary: string;
  total_unrealized_gain: number;
  total_unrealized_loss: number;
  tax_lots: TaxLotResponse[];
  harvesting_opportunities: TaxOpportunityResponse[];
  short_term_vs_long_term_explanation: string;
  wash_sale_warning: string;
  confidence: ConfidenceLevel;
  data_limitations: string[];
  sources: SourceMetadata[];
  educational_disclaimer: string;
}

export interface RetirementAccountResponse {
  id: string;
  account_type: string;
  provider_name: string;
  current_balance: number;
  contribution_percent: number;
  annual_contribution_estimate: number;
  investment_mix_summary: string;
}

export interface EmployerMatchResponse {
  has_match: boolean;
  formula: string;
  estimated_annual_match: number;
  beginner_explanation: string;
}

export interface RetirementScenarioResponse {
  id: string;
  label: string;
  contribution_percent: number;
  estimated_annual_employee_contribution: number;
  estimated_annual_employer_match: number;
  projected_balance_at_65: number;
  assumptions: string[];
}

export interface RetirementPlanResponse {
  headline: string;
  progress_percent: number;
  target_retirement_balance: number;
  current_retirement_balance: number;
  accounts: RetirementAccountResponse[];
  employer_match: EmployerMatchResponse;
  scenarios: RetirementScenarioResponse[];
  beginner_summary: string;
  suggested_reviews: string[];
  confidence: ConfidenceLevel;
  data_limitations: string[];
  sources: SourceMetadata[];
  educational_disclaimer: string;
}

export type DecisionType =
  | "buy"
  | "sell"
  | "hold"
  | "watch"
  | "rebalance"
  | "debt_payoff"
  | "retirement_contribution_change";

export interface DecisionJournalEntryResponse {
  id: string;
  decision_type: DecisionType;
  title: string;
  asset_symbol: string | null;
  reason: string;
  expected_outcome: string;
  risk_considered: string;
  review_date: string;
  created_at: string;
  status: "open" | "reviewed";
  feedback_summary: string;
}

export interface DecisionJournalCreateRequest {
  decision_type: DecisionType;
  title: string;
  asset_symbol: string | null;
  reason: string;
  expected_outcome: string;
  risk_considered: string;
  review_date: string;
}

export interface DecisionJournalResponse {
  entries: DecisionJournalEntryResponse[];
  feedback_prompts: string[];
  beginner_summary: string;
  confidence: ConfidenceLevel;
  data_limitations: string[];
  sources: SourceMetadata[];
  educational_disclaimer: string;
}

export type WatchlistAssetType = "stock" | "etf" | "crypto" | "real_estate_market" | "bond" | "treasury" | "other";

export interface WatchlistItemResponse {
  id: string;
  symbol: string;
  name: string;
  asset_type: WatchlistAssetType;
  why_watching: string;
  ai_summary: string;
  risk_notes: string[];
  opportunity_notes: string[];
  source: SourceMetadata;
  confidence: ConfidenceLevel;
  data_limitations: string[];
}

export interface WatchlistCreateRequest {
  symbol: string;
  name: string;
  asset_type: WatchlistAssetType;
  why_watching: string;
}

export interface WatchlistResponse {
  items: WatchlistItemResponse[];
  beginner_summary: string;
  safe_research_prompts: string[];
  confidence: ConfidenceLevel;
  data_limitations: string[];
  sources: SourceMetadata[];
  educational_disclaimer: string;
}

export interface SecurityStatusResponse {
  api_version: string;
  authentication_status: string;
  rate_limit_per_minute: number;
  security_headers_enabled: string[];
  cors_origins: string[];
  logging_summary: string;
  prompt_injection_guardrails: string[];
  data_rights: string[];
}

export interface PrivacySettingsRequest {
  beginner_mode_enabled: boolean;
  store_assistant_history: boolean;
  allow_product_analytics: boolean;
  allow_external_integrations: boolean;
  data_retention_days: number;
}

export interface PrivacySettingsResponse extends PrivacySettingsRequest {
  profile_id: string;
  explanation: string;
  updated_at: string;
}

export interface DataExportResponse {
  export_id: string;
  generated_at: string;
  sections: string[];
  record_counts: Record<string, number>;
  delivery_note: string;
  data_limitations: string[];
  sources: SourceMetadata[];
}

export interface DeleteDataResponse {
  request_id: string;
  status: "preview_only" | "completed";
  deleted_sections: string[];
  explanation: string;
  data_limitations: string[];
}

export type EvaluationMetricCategory = "product" | "ai_safety" | "data_quality" | "reliability";
export type EvaluationMetricStatus = "healthy" | "watch" | "needs_attention";
export type EvaluationMetricDirection = "higher_is_better" | "lower_is_better";

export interface EvaluationMetricResponse {
  id: string;
  label: string;
  category: EvaluationMetricCategory;
  value: number;
  unit: string;
  target: string;
  direction: EvaluationMetricDirection;
  status: EvaluationMetricStatus;
  sample_size: number;
  beginner_explanation: string;
  how_measured: string;
  limitations: string[];
}

export interface EvaluationMetricsResponse {
  headline: string;
  beginner_summary: string;
  metrics: EvaluationMetricResponse[];
  quality_checks: string[];
  recommended_reviews: string[];
  confidence: ConfidenceLevel;
  data_limitations: string[];
  sources: SourceMetadata[];
  educational_disclaimer: string;
}

export interface DashboardApiData {
  actionPlan: ActionPlanResponse;
  assets: AssetResponse[];
  portfolio: PortfolioSummaryResponse;
}
