import type { DemoPortfolioResponse, GuideResponse, MarketHistoryResponse, QuoteResponse } from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

export async function getQuote(symbol: string): Promise<QuoteResponse> {
  return getJson<QuoteResponse>(`/api/quote/${encodeURIComponent(symbol)}`);
}

export async function getHistory(symbol: string, period = "6mo"): Promise<MarketHistoryResponse> {
  return getJson<MarketHistoryResponse>(`/api/history/${encodeURIComponent(symbol)}?period=${period}`);
}

export async function getDemoPortfolio(): Promise<DemoPortfolioResponse> {
  return getJson<DemoPortfolioResponse>("/api/demo-portfolio");
}

export async function getGuide(symbol: string): Promise<GuideResponse> {
  return getJson<GuideResponse>(`/api/guide/${encodeURIComponent(symbol)}`);
}

async function getJson<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: { Accept: "application/json" },
    cache: "no-store"
  });
  if (!response.ok) {
    let message = `CrocLens API returned ${response.status}.`;
    try {
      const body = (await response.json()) as { detail?: string };
      if (body.detail) {
        message = body.detail;
      }
    } catch {
      // Keep the generic message if the API did not return JSON.
    }
    throw new Error(message);
  }
  return response.json() as Promise<T>;
}
