"use client";

import { useCallback, useEffect, useState } from "react";
import {
  getActionPlan,
  getApiBaseUrl,
  getAssets,
  getCryptoPrice,
  getDataFreshness,
  getDataProviders,
  getMacroSeries,
  getMarketPrice,
  getPortfolioSummary
} from "@/lib/api-client";
import type { DashboardApiData, NormalizedDataPointResponse } from "@/types/api";

interface DashboardDataState {
  apiBaseUrl: string;
  data: DashboardApiData | null;
  error: string | null;
  isLoading: boolean;
  refetch: () => void;
}

export function useDashboardData(): DashboardDataState {
  const [data, setData] = useState<DashboardApiData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [reloadKey, setReloadKey] = useState(0);

  const refetch = useCallback(() => {
    setReloadKey((current) => current + 1);
  }, []);

  useEffect(() => {
    const controller = new AbortController();

    async function loadDashboardData() {
      setIsLoading(true);
      setError(null);

      try {
        const [
          portfolio,
          assets,
          actionPlan,
          providers,
          dataFreshness,
          vooPrice,
          aggPrice,
          bitcoinPrice,
          inflationSeries
        ] = await Promise.all([
          getPortfolioSummary(controller.signal),
          getAssets(controller.signal),
          getActionPlan(controller.signal),
          getDataProviders(controller.signal).catch(() => []),
          getDataFreshness(controller.signal).catch(() => null),
          getMarketPrice("VOO", controller.signal).catch(() => null),
          getMarketPrice("AGG", controller.signal).catch(() => null),
          getCryptoPrice("bitcoin", controller.signal).catch(() => null),
          getMacroSeries("CPIAUCSL", controller.signal).catch(() => null)
        ]);

        setData({
          actionPlan,
          assets,
          dataFreshness,
          marketData: [vooPrice, aggPrice, bitcoinPrice, inflationSeries].filter(isNormalizedDataPoint),
          portfolio,
          providers
        });
      } catch (err) {
        if (controller.signal.aborted) {
          return;
        }

        if (err instanceof DOMException && err.name === "AbortError") {
          return;
        }

        setError(err instanceof Error ? err.message : "Unable to load CrocLens API data.");
      } finally {
        if (!controller.signal.aborted) {
          setIsLoading(false);
        }
      }
    }

    loadDashboardData();

    return () => controller.abort();
  }, [reloadKey]);

  return {
    apiBaseUrl: getApiBaseUrl(),
    data,
    error,
    isLoading,
    refetch
  };
}

function isNormalizedDataPoint(
  item: NormalizedDataPointResponse | null
): item is NormalizedDataPointResponse {
  return item !== null;
}
