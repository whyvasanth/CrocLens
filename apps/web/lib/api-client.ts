import type {
  ActionPlanResponse,
  AssetDetailCardResponse,
  AssetDetailResponse,
  AssetResponse,
  PortfolioSummaryResponse
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
