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

export interface DashboardApiData {
  actionPlan: ActionPlanResponse;
  assets: AssetResponse[];
  portfolio: PortfolioSummaryResponse;
}
