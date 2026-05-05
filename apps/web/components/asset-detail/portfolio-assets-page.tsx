"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Activity, ArrowRight, Banknote, Building2, Landmark, LineChart, RefreshCcw } from "lucide-react";
import { AppShell } from "@/components/dashboard/app-shell";
import { DashboardHeader } from "@/components/dashboard/dashboard-header";
import { Card, Pill, SectionTitle } from "@/components/dashboard/ui";
import { getAssetDetailCards } from "@/lib/api-client";
import { formatCurrency } from "@/lib/formatters";
import type { AssetDetailCardResponse, AssetDetailCategory, RiskLevel } from "@/types/api";

const categoryLabel: Record<AssetDetailCategory, string> = {
  stock_etf: "Stock / ETF",
  crypto: "Crypto",
  real_estate: "Real estate",
  debt: "Debt / liability",
  retirement: "Retirement"
};

const categoryIcon = {
  stock_etf: LineChart,
  crypto: Activity,
  real_estate: Building2,
  debt: Banknote,
  retirement: Landmark
};

const riskTone: Record<RiskLevel, "green" | "gold" | "coral"> = {
  low: "green",
  medium: "gold",
  high: "coral"
};

export function PortfolioAssetsPage() {
  const [items, setItems] = useState<AssetDetailCardResponse[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    const controller = new AbortController();
    setIsLoading(true);
    setError(null);

    getAssetDetailCards(controller.signal)
      .then(setItems)
      .catch((requestError: Error) => {
        if (!controller.signal.aborted) {
          setError(requestError.message);
        }
      })
      .finally(() => {
        if (!controller.signal.aborted) {
          setIsLoading(false);
        }
      });

    return () => controller.abort();
  }, [refreshKey]);

  return (
    <AppShell>
      {({ openGuide, openSidebar }) => (
        <div className="mx-auto max-w-[1180px] space-y-5">
          <DashboardHeader
            description="Open beginner-friendly detail pages for stocks, ETFs, crypto, real estate, debt, and retirement accounts."
            onAskClick={openGuide}
            onMenuClick={openSidebar}
            title="Portfolio"
          />

          <Card>
            <SectionTitle
              eyebrow="Phase 7"
              title="Your detail-ready wealth items"
              action={<Pill tone="green">API-backed</Pill>}
            />

            {isLoading ? (
              <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
                {[0, 1, 2, 3, 4, 5].map((item) => (
                  <div className="h-44 animate-pulse rounded-lg bg-stone-100" key={item} />
                ))}
              </div>
            ) : null}

            {!isLoading && error ? (
              <div className="flex flex-col gap-4 rounded-lg border border-rose-200 bg-rose-50 p-4 sm:flex-row sm:items-center sm:justify-between">
                <p className="text-sm leading-6 text-rose-800">{error}</p>
                <button
                  className="inline-flex min-h-10 items-center justify-center gap-2 rounded-lg bg-croc-emerald px-4 text-sm font-semibold text-white"
                  onClick={() => setRefreshKey((value) => value + 1)}
                  type="button"
                >
                  <RefreshCcw className="h-4 w-4" />
                  Retry
                </button>
              </div>
            ) : null}

            {!isLoading && !error ? (
              <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
                {items.map((item) => {
                  const Icon = categoryIcon[item.category];
                  return (
                    <Link
                      className="group flex min-h-48 flex-col justify-between rounded-lg border border-emerald-900/10 bg-croc-cream p-4 transition hover:-translate-y-0.5 hover:border-croc-moss hover:bg-white"
                      href={`/assets/${item.id}`}
                      key={item.id}
                    >
                      <div className="flex items-start justify-between gap-3">
                        <span className="grid h-11 w-11 shrink-0 place-items-center rounded-lg bg-white text-croc-moss shadow-sm">
                          <Icon className="h-5 w-5" />
                        </span>
                        <Pill tone={riskTone[item.risk_level]}>{item.risk_level} risk</Pill>
                      </div>
                      <div>
                        <div className="mt-5 flex items-end justify-between gap-3">
                          <div>
                            <p className="text-xs font-semibold uppercase text-croc-moss">
                              {categoryLabel[item.category]}
                            </p>
                            <h2 className="mt-1 text-lg font-bold text-croc-ink">{item.name}</h2>
                          </div>
                          <p className="text-base font-bold text-croc-ink">{formatCurrency(item.current_value)}</p>
                        </div>
                        <p className="mt-3 text-sm leading-6 text-stone-600">{item.summary}</p>
                      </div>
                      <span className="mt-4 inline-flex items-center gap-2 text-sm font-semibold text-croc-moss">
                        Open detail
                        <ArrowRight className="h-4 w-4 transition group-hover:translate-x-0.5" />
                      </span>
                    </Link>
                  );
                })}
              </div>
            ) : null}
          </Card>
        </div>
      )}
    </AppShell>
  );
}
