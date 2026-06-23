import type {
  AccountCreateRequest,
  AccountLoginRequest,
  AccountUserResponse,
  ActionPlanResponse,
  ActionPlanStatusResponse,
  AgentRegistryResponse,
  AssistantRequest,
  AssistantResponse,
  AssetDetailCardResponse,
  AssetDetailResponse,
  AssetResponse,
  BrowserAccountSessionResponse,
  DataExportResponse,
  DeleteDataResponse,
  DecisionJournalCreateRequest,
  DecisionJournalEntryResponse,
  DecisionJournalResponse,
  DecisionJournalUpdateRequest,
  DeleteRecordResponse,
  EvaluationMetricsResponse,
  HoldingCreateRequest,
  HoldingResponse,
  HoldingUpdateRequest,
  LiabilityCreateRequest,
  LiabilityResponse,
  LiabilityUpdateRequest,
  LogoutResponse,
  MarketNewsImpactResponse,
  MarketSnapshotResponse,
  OnboardingOptionsResponse,
  OnboardingProfileRequest,
  OnboardingProfileResponse,
  PortfolioHistoryResponse,
  PortfolioRecordsResponse,
  PortfolioSummaryResponse,
  PrivacySettingsRequest,
  PrivacySettingsResponse,
  RetirementPlanResponse,
  RetirementAccountCreateRequest,
  RetirementAccountResponse,
  RetirementAccountUpdateRequest,
  SecurityStatusResponse,
  TaxInsightResponse,
  TaxLotCreateRequest,
  TaxLotResponse,
  TaxLotUpdateRequest,
  WatchlistCreateRequest,
  WatchlistItemResponse,
  WatchlistUpdateRequest,
  WatchlistResponse
} from "@/types/api";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ??
  process.env.NEXT_PUBLIC_CROCLENS_API_URL ??
  "http://localhost:8000";

function buildRequestUrl(path: string) {
  if (path.startsWith("/api/auth")) {
    return path;
  }

  if (path.startsWith("/api/v1")) {
    return `/api/backend${path}`;
  }

  return `${API_BASE_URL}${path}`;
}

async function requestJson<T>(path: string, signal?: AbortSignal): Promise<T> {
  const response = await fetch(buildRequestUrl(path), {
    headers: {
      Accept: "application/json"
    },
    signal
  });

  if (!response.ok) {
    throw new Error(await getApiErrorMessage(response, path));
  }

  return response.json() as Promise<T>;
}

async function postJson<TResponse, TRequest>(path: string, body: TRequest, signal?: AbortSignal): Promise<TResponse> {
  const response = await fetch(buildRequestUrl(path), {
    body: JSON.stringify(body),
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json"
    },
    method: "POST",
    signal
  });

  if (!response.ok) {
    throw new Error(await getApiErrorMessage(response, path));
  }

  return response.json() as Promise<TResponse>;
}

async function getApiErrorMessage(response: Response, path: string): Promise<string> {
  const fallback = `CrocLens API returned ${response.status} for ${path}`;

  try {
    const payload = (await response.clone().json()) as { detail?: unknown; message?: unknown };
    const detail = typeof payload.detail === "string" ? payload.detail : null;
    const message = typeof payload.message === "string" ? payload.message : null;
    return detail ?? message ?? fallback;
  } catch {
    try {
      const text = await response.clone().text();
      return text.trim() ? `${fallback}: ${text}` : fallback;
    } catch {
      return fallback;
    }
  }
}

export function getApiBaseUrl() {
  return API_BASE_URL;
}

export function getPortfolioSummary(signal?: AbortSignal) {
  return requestJson<PortfolioSummaryResponse>("/api/v1/portfolio/summary", signal);
}

export function getPortfolioRecords(signal?: AbortSignal) {
  return requestJson<PortfolioRecordsResponse>("/api/v1/portfolio/records", signal);
}

export function createHolding(request: HoldingCreateRequest, signal?: AbortSignal) {
  return postJson<HoldingResponse, HoldingCreateRequest>("/api/v1/portfolio/holdings", request, signal);
}

export function updateHolding(holdingId: string, request: HoldingUpdateRequest, signal?: AbortSignal) {
  return putJson<HoldingResponse, HoldingUpdateRequest>(`/api/v1/portfolio/holdings/${holdingId}`, request, signal);
}

export function deleteHolding(holdingId: string, signal?: AbortSignal) {
  return deleteJson<DeleteRecordResponse>(`/api/v1/portfolio/holdings/${holdingId}`, signal);
}

export function createLiability(request: LiabilityCreateRequest, signal?: AbortSignal) {
  return postJson<LiabilityResponse, LiabilityCreateRequest>("/api/v1/portfolio/liabilities", request, signal);
}

export function updateLiability(liabilityId: string, request: LiabilityUpdateRequest, signal?: AbortSignal) {
  return putJson<LiabilityResponse, LiabilityUpdateRequest>(`/api/v1/portfolio/liabilities/${liabilityId}`, request, signal);
}

export function deleteLiability(liabilityId: string, signal?: AbortSignal) {
  return deleteJson<DeleteRecordResponse>(`/api/v1/portfolio/liabilities/${liabilityId}`, signal);
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

export function generateActionPlan(signal?: AbortSignal) {
  return postJson<ActionPlanResponse, Record<string, never>>("/api/v1/action-plans/generate", {}, signal);
}

export function completeActionPlanItem(itemId: string, signal?: AbortSignal) {
  return postJson<ActionPlanStatusResponse, Record<string, never>>(`/api/v1/action-plans/items/${itemId}/complete`, {}, signal);
}

export function dismissActionPlanItem(itemId: string, signal?: AbortSignal) {
  return postJson<ActionPlanStatusResponse, Record<string, never>>(`/api/v1/action-plans/items/${itemId}/dismiss`, {}, signal);
}

export function reopenActionPlanItem(itemId: string, signal?: AbortSignal) {
  return postJson<ActionPlanStatusResponse, Record<string, never>>(`/api/v1/action-plans/items/${itemId}/reopen`, {}, signal);
}

export function getOnboardingOptions(signal?: AbortSignal) {
  return requestJson<OnboardingOptionsResponse>("/api/v1/onboarding/options", signal);
}

export function submitOnboardingProfile(profile: OnboardingProfileRequest, signal?: AbortSignal) {
  return postJson<OnboardingProfileResponse, OnboardingProfileRequest>("/api/v1/onboarding/profile", profile, signal);
}

export function createAccount(request: AccountCreateRequest, signal?: AbortSignal) {
  return postJson<BrowserAccountSessionResponse, AccountCreateRequest>("/api/auth/signup", request, signal);
}

export function loginAccount(request: AccountLoginRequest, signal?: AbortSignal) {
  return postJson<BrowserAccountSessionResponse, AccountLoginRequest>("/api/auth/login", request, signal);
}

export function getCurrentAccount(signal?: AbortSignal) {
  return requestJson<AccountUserResponse | null>("/api/auth/me", signal);
}

export function logoutAccount(signal?: AbortSignal) {
  return postJson<LogoutResponse, Record<string, never>>("/api/auth/logout", {}, signal);
}

export function askAssistant(request: AssistantRequest, signal?: AbortSignal) {
  return postJson<AssistantResponse, AssistantRequest>("/api/v1/ai/assistant", request, signal);
}

export function getAgentRegistry(signal?: AbortSignal) {
  return requestJson<AgentRegistryResponse>("/api/v1/ai/agents", signal);
}

async function putJson<TResponse, TRequest>(path: string, body: TRequest, signal?: AbortSignal): Promise<TResponse> {
  const response = await fetch(buildRequestUrl(path), {
    body: JSON.stringify(body),
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json"
    },
    method: "PUT",
    signal
  });

  if (!response.ok) {
    throw new Error(await getApiErrorMessage(response, path));
  }

  return response.json() as Promise<TResponse>;
}

async function deleteJson<TResponse>(path: string, signal?: AbortSignal): Promise<TResponse> {
  const response = await fetch(buildRequestUrl(path), {
    headers: {
      Accept: "application/json"
    },
    method: "DELETE",
    signal
  });

  if (!response.ok) {
    throw new Error(await getApiErrorMessage(response, path));
  }

  return response.json() as Promise<TResponse>;
}

export function getMarketNewsImpact(signal?: AbortSignal) {
  return requestJson<MarketNewsImpactResponse>("/api/v1/market-news/impact-summary", signal);
}

export function getMarketSnapshot(signal?: AbortSignal) {
  return requestJson<MarketSnapshotResponse>("/api/v1/market/snapshot", signal);
}

export function getPortfolioHistory(signal?: AbortSignal) {
  return requestJson<PortfolioHistoryResponse>("/api/v1/portfolio/history", signal);
}

export function getTaxInsights(signal?: AbortSignal) {
  return requestJson<TaxInsightResponse>("/api/v1/tax/insights", signal);
}

export function getRetirementPlan(signal?: AbortSignal) {
  return requestJson<RetirementPlanResponse>("/api/v1/retirement/plan", signal);
}

export function createRetirementAccount(request: RetirementAccountCreateRequest, signal?: AbortSignal) {
  return postJson<RetirementAccountResponse, RetirementAccountCreateRequest>("/api/v1/retirement/accounts", request, signal);
}

export function updateRetirementAccount(accountId: string, request: RetirementAccountUpdateRequest, signal?: AbortSignal) {
  return putJson<RetirementAccountResponse, RetirementAccountUpdateRequest>(`/api/v1/retirement/accounts/${accountId}`, request, signal);
}

export function deleteRetirementAccount(accountId: string, signal?: AbortSignal) {
  return deleteJson<DeleteRecordResponse>(`/api/v1/retirement/accounts/${accountId}`, signal);
}

export function getDecisionJournal(signal?: AbortSignal) {
  return requestJson<DecisionJournalResponse>("/api/v1/journal/entries", signal);
}

export function createDecisionJournalEntry(entry: DecisionJournalCreateRequest, signal?: AbortSignal) {
  return postJson<DecisionJournalEntryResponse, DecisionJournalCreateRequest>("/api/v1/journal/entries", entry, signal);
}

export function updateDecisionJournalEntry(entryId: string, entry: DecisionJournalUpdateRequest, signal?: AbortSignal) {
  return putJson<DecisionJournalEntryResponse, DecisionJournalUpdateRequest>(`/api/v1/journal/entries/${entryId}`, entry, signal);
}

export function deleteDecisionJournalEntry(entryId: string, signal?: AbortSignal) {
  return deleteJson<DeleteRecordResponse>(`/api/v1/journal/entries/${entryId}`, signal);
}

export function getWatchlist(signal?: AbortSignal) {
  return requestJson<WatchlistResponse>("/api/v1/watchlist", signal);
}

export function createWatchlistItem(item: WatchlistCreateRequest, signal?: AbortSignal) {
  return postJson<WatchlistItemResponse, WatchlistCreateRequest>("/api/v1/watchlist", item, signal);
}

export function updateWatchlistItem(itemId: string, item: WatchlistUpdateRequest, signal?: AbortSignal) {
  return putJson<WatchlistItemResponse, WatchlistUpdateRequest>(`/api/v1/watchlist/${itemId}`, item, signal);
}

export function deleteWatchlistItem(itemId: string, signal?: AbortSignal) {
  return deleteJson<DeleteRecordResponse>(`/api/v1/watchlist/${itemId}`, signal);
}

export function createTaxLot(request: TaxLotCreateRequest, signal?: AbortSignal) {
  return postJson<TaxLotResponse, TaxLotCreateRequest>("/api/v1/tax/lots", request, signal);
}

export function updateTaxLot(lotId: string, request: TaxLotUpdateRequest, signal?: AbortSignal) {
  return putJson<TaxLotResponse, TaxLotUpdateRequest>(`/api/v1/tax/lots/${lotId}`, request, signal);
}

export function deleteTaxLot(lotId: string, signal?: AbortSignal) {
  return deleteJson<DeleteRecordResponse>(`/api/v1/tax/lots/${lotId}`, signal);
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
