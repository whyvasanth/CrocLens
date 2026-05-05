export type ConfidenceLevel = "low" | "medium" | "high";
export type RiskLevel = "low" | "medium" | "high";
export type AssetDetailCategory = "stock_etf" | "crypto" | "real_estate" | "debt" | "retirement";
export type MetricTone = "green" | "gold" | "blue" | "coral" | "neutral";

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

export interface DashboardApiData {
  actionPlan: ActionPlanResponse;
  assets: AssetResponse[];
  portfolio: PortfolioSummaryResponse;
}
