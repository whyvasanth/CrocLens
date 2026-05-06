import type {
  ActionPlanResponse,
  AgentRegistryResponse,
  AssistantRequest,
  AssistantResponse,
  AssetDetailCardResponse,
  AssetDetailResponse,
  AssetResponse,
  DecisionJournalCreateRequest,
  DecisionJournalEntryResponse,
  DecisionJournalResponse,
  MarketNewsImpactResponse,
  OnboardingOptionsResponse,
  OnboardingProfileRequest,
  OnboardingProfileResponse,
  PortfolioSummaryResponse,
  RetirementPlanResponse,
  TaxInsightResponse
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

export function askAssistant(request: AssistantRequest, signal?: AbortSignal) {
  return postJson<AssistantResponse, AssistantRequest>("/api/v1/ai/assistant", request, signal);
}

export function getAgentRegistry(signal?: AbortSignal) {
  return requestJson<AgentRegistryResponse>("/api/v1/ai/agents", signal);
}

export function getMarketNewsImpact(signal?: AbortSignal) {
  return requestJson<MarketNewsImpactResponse>("/api/v1/market-news/impact-summary", signal);
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
