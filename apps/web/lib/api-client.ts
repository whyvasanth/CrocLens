import type {
  AccountCreateRequest,
  AccountLoginRequest,
  AccountSessionResponse,
  ActionPlanResponse,
  AgentRegistryResponse,
  AssistantRequest,
  AssistantResponse,
  AssetDetailCardResponse,
  AssetDetailResponse,
  AssetResponse,
  DataExportResponse,
  DataFreshnessResponse,
  DeleteDataResponse,
  DecisionJournalCreateRequest,
  DecisionJournalEntryResponse,
  DecisionJournalResponse,
  EvaluationMetricsResponse,
  AgentAIRequest,
  FinalAIResponse,
  MarketNewsImpactResponse,
  NormalizedDataPointResponse,
  OnboardingOptionsResponse,
  OnboardingProfileRequest,
  OnboardingProfileResponse,
  PriceHistoryResponse,
  PortfolioSummaryResponse,
  PrivacySettingsRequest,
  PrivacySettingsResponse,
  ProviderStatusResponse,
  RetirementPlanResponse,
  SecurityStatusResponse,
  TechnicalIndicatorSetResponse,
  TaxInsightResponse,
  WatchlistCreateRequest,
  WatchlistItemResponse,
  WatchlistResponse
} from "@/types/api";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_CROCLENS_API_URL ?? "http://127.0.0.1:8000";

async function requestJson<T>(path: string, signal?: AbortSignal): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      Accept: "application/json"
    },
    signal
  });

  if (!response.ok) {
    throw new Error(`CrocLens API returned ${response.status} for ${path}`);
  }

  return response.json() as Promise<T>;
}

async function postJson<TResponse, TRequest>(path: string, body: TRequest, signal?: AbortSignal): Promise<TResponse> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    body: JSON.stringify(body),
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json"
    },
    method: "POST",
    signal
  });

  if (!response.ok) {
    throw new Error(`CrocLens API returned ${response.status} for ${path}`);
  }

  return response.json() as Promise<TResponse>;
}

export function getApiBaseUrl() {
  return API_BASE_URL;
}

export function getPortfolioSummary(signal?: AbortSignal) {
  return requestJson<PortfolioSummaryResponse>("/api/v1/portfolio/summary", signal);
}

export function getAssets(signal?: AbortSignal) {
  return requestJson<AssetResponse[]>("/api/v1/assets", signal);
}

export function getAssetDetailCards(signal?: AbortSignal) {
  return requestJson<AssetDetailCardResponse[]>("/api/v1/assets/detail-cards", signal);
}

export function getAssetDetail(assetId: string, signal?: AbortSignal) {
  return requestJson<AssetDetailResponse>(`/api/v1/assets/${assetId}/detail`, signal);
}

export function getActionPlan(signal?: AbortSignal) {
  return requestJson<ActionPlanResponse>("/api/v1/action-plans", signal);
}

export function getOnboardingOptions(signal?: AbortSignal) {
  return requestJson<OnboardingOptionsResponse>("/api/v1/onboarding/options", signal);
}

export function submitOnboardingProfile(profile: OnboardingProfileRequest, signal?: AbortSignal) {
  return postJson<OnboardingProfileResponse, OnboardingProfileRequest>("/api/v1/onboarding/profile", profile, signal);
}

export function createAccount(request: AccountCreateRequest, signal?: AbortSignal) {
  return postJson<AccountSessionResponse, AccountCreateRequest>("/api/v1/auth/signup", request, signal);
}

export function loginAccount(request: AccountLoginRequest, signal?: AbortSignal) {
  return postJson<AccountSessionResponse, AccountLoginRequest>("/api/v1/auth/login", request, signal);
}

export function askAssistant(request: AssistantRequest, signal?: AbortSignal) {
  return postJson<AssistantResponse, AssistantRequest>("/api/v1/ai/assistant", request, signal);
}

export function getAgentRegistry(signal?: AbortSignal) {
  return requestJson<AgentRegistryResponse>("/api/v1/ai/agents", signal);
}

export function chatWithAgent(request: AgentAIRequest, signal?: AbortSignal) {
  return postJson<FinalAIResponse, AgentAIRequest>("/api/v1/ai/chat", request, signal);
}

export function generateAgentActionPlan(request: AgentAIRequest, signal?: AbortSignal) {
  return postJson<FinalAIResponse, AgentAIRequest>("/api/v1/ai/action-plan", request, signal);
}

export function explainAssetWithAgent(request: AgentAIRequest, signal?: AbortSignal) {
  return postJson<FinalAIResponse, AgentAIRequest>("/api/v1/ai/explain-asset", request, signal);
}

export function reviewPortfolioWithAgent(request: AgentAIRequest, signal?: AbortSignal) {
  return postJson<FinalAIResponse, AgentAIRequest>("/api/v1/ai/portfolio-review", request, signal);
}

async function putJson<TResponse, TRequest>(path: string, body: TRequest, signal?: AbortSignal): Promise<TResponse> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    body: JSON.stringify(body),
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json"
    },
    method: "PUT",
    signal
  });

  if (!response.ok) {
    throw new Error(`CrocLens API returned ${response.status} for ${path}`);
  }

  return response.json() as Promise<TResponse>;
}

async function deleteJson<TResponse>(path: string, signal?: AbortSignal): Promise<TResponse> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      Accept: "application/json"
    },
    method: "DELETE",
    signal
  });

  if (!response.ok) {
    throw new Error(`CrocLens API returned ${response.status} for ${path}`);
  }

  return response.json() as Promise<TResponse>;
}

export function getMarketNewsImpact(signal?: AbortSignal) {
  return requestJson<MarketNewsImpactResponse>("/api/v1/market-news/impact-summary", signal);
}

export function getDataProviders(signal?: AbortSignal) {
  return requestJson<ProviderStatusResponse[]>("/api/v1/data/providers", signal);
}

export function getDataFreshness(signal?: AbortSignal) {
  return requestJson<DataFreshnessResponse>("/api/v1/data/freshness", signal);
}

export function getMarketPrice(symbol: string, signal?: AbortSignal) {
  return requestJson<NormalizedDataPointResponse>(`/api/v1/market/price/${symbol}`, signal);
}

export function getMarketHistory(symbol: string, signal?: AbortSignal) {
  return requestJson<PriceHistoryResponse>(`/api/v1/market/history/${symbol}`, signal);
}

export function getMarketIndicators(symbol: string, signal?: AbortSignal) {
  return requestJson<TechnicalIndicatorSetResponse>(`/api/v1/market/indicators/${symbol}`, signal);
}

export function getCryptoPrice(coinId: string, signal?: AbortSignal) {
  return requestJson<NormalizedDataPointResponse>(`/api/v1/crypto/price/${coinId}`, signal);
}

export function getMacroSeries(seriesId: string, signal?: AbortSignal) {
  return requestJson<NormalizedDataPointResponse>(`/api/v1/macro/series/${seriesId}`, signal);
}

export function getTreasuryRates(signal?: AbortSignal) {
  return requestJson<NormalizedDataPointResponse>("/api/v1/rates/treasury", signal);
}

export function getTaxInsights(signal?: AbortSignal) {
  return requestJson<TaxInsightResponse>("/api/v1/tax/insights", signal);
}

export function getRetirementPlan(signal?: AbortSignal) {
  return requestJson<RetirementPlanResponse>("/api/v1/retirement/plan", signal);
}

export function getDecisionJournal(signal?: AbortSignal) {
  return requestJson<DecisionJournalResponse>("/api/v1/journal/entries", signal);
}

export function createDecisionJournalEntry(entry: DecisionJournalCreateRequest, signal?: AbortSignal) {
  return postJson<DecisionJournalEntryResponse, DecisionJournalCreateRequest>("/api/v1/journal/entries", entry, signal);
}

export function getWatchlist(signal?: AbortSignal) {
  return requestJson<WatchlistResponse>("/api/v1/watchlist", signal);
}

export function createWatchlistItem(item: WatchlistCreateRequest, signal?: AbortSignal) {
  return postJson<WatchlistItemResponse, WatchlistCreateRequest>("/api/v1/watchlist", item, signal);
}

export function getSecurityStatus(signal?: AbortSignal) {
  return requestJson<SecurityStatusResponse>("/api/v1/security/status", signal);
}

export function getPrivacySettings(signal?: AbortSignal) {
  return requestJson<PrivacySettingsResponse>("/api/v1/privacy/settings", signal);
}

export function updatePrivacySettings(settings: PrivacySettingsRequest, signal?: AbortSignal) {
  return putJson<PrivacySettingsResponse, PrivacySettingsRequest>("/api/v1/privacy/settings", settings, signal);
}

export function getDataExport(signal?: AbortSignal) {
  return requestJson<DataExportResponse>("/api/v1/privacy/export", signal);
}

export function deleteDataPreview(signal?: AbortSignal) {
  return deleteJson<DeleteDataResponse>("/api/v1/privacy/data", signal);
}

export function getEvaluationMetrics(signal?: AbortSignal) {
  return requestJson<EvaluationMetricsResponse>("/api/v1/evaluation/metrics", signal);
}
