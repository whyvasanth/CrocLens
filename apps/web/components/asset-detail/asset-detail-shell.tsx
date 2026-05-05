"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import {
  Activity,
  AlertTriangle,
  ArrowLeft,
  Banknote,
  Building2,
  CheckCircle2,
  Landmark,
  LineChart,
  RefreshCcw,
  Shield,
  WalletCards
} from "lucide-react";
import { AppShell } from "@/components/dashboard/app-shell";
import { DashboardHeader } from "@/components/dashboard/dashboard-header";
import { Card, Pill, SectionTitle } from "@/components/dashboard/ui";
import { getAssetDetail } from "@/lib/api-client";
import { formatCurrency } from "@/lib/formatters";
import type { AssetDetailCategory, AssetDetailResponse, RiskLevel } from "@/types/api";

interface AssetDetailShellProps {
  assetId: string;
}

const categoryLabel: Record<AssetDetailCategory, string> = {
  stock_etf: "Stock / ETF",
  crypto: "Crypto",
  real_estate: "Real estate",
  debt: "Debt / liability",
  retirement: "Retirement"
};

const categoryTone: Record<AssetDetailCategory, "green" | "gold" | "blue" | "coral" | "neutral"> = {
  stock_etf: "green",
  crypto: "coral",
  real_estate: "blue",
  debt: "gold",
  retirement: "green"
};

const riskTone: Record<RiskLevel, "green" | "gold" | "coral"> = {
  low: "green",
  medium: "gold",
  high: "coral"
};

const categoryIcon = {
  stock_etf: LineChart,
  crypto: Activity,
  real_estate: Building2,
  debt: Banknote,
  retirement: Landmark
};

function LoadingDetail() {
  return (
    <div className="grid gap-5 lg:grid-cols-[minmax(0,1.35fr)_minmax(320px,0.75fr)]">
      <Card className="min-h-[360px]">
        <div className="h-5 w-32 animate-pulse rounded-md bg-stone-100" />
        <div className="mt-6 h-12 w-64 animate-pulse rounded-md bg-stone-100" />
        <div className="mt-4 h-24 animate-pulse rounded-md bg-stone-100" />
      </Card>
      <Card>
        <div className="h-5 w-24 animate-pulse rounded-md bg-stone-100" />
        <div className="mt-5 space-y-3">
          {[0, 1, 2, 3].map((item) => (
            <div className="h-14 animate-pulse rounded-lg bg-stone-100" key={item} />
          ))}
        </div>
      </Card>
    </div>
  );
}

function DetailError({ message, onRetry }: { message: string; onRetry: () => void }) {
  return (
    <Card>
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex gap-3">
          <span className="grid h-11 w-11 shrink-0 place-items-center rounded-lg bg-rose-100 text-rose-700">
            <AlertTriangle className="h-5 w-5" />
          </span>
          <div>
            <h2 className="font-semibold text-croc-ink">Asset detail could not load</h2>
            <p className="mt-1 text-sm leading-6 text-stone-600">{message}</p>
          </div>
        </div>
        <button
          className="inline-flex min-h-10 items-center justify-center gap-2 rounded-lg bg-croc-emerald px-4 text-sm font-semibold text-white"
          onClick={onRetry}
          suppressHydrationWarning
          type="button"
        >
          <RefreshCcw className="h-4 w-4" />
          Retry
        </button>
      </div>
    </Card>
  );
}

export function AssetDetailShell({ assetId }: AssetDetailShellProps) {
  const [detail, setDetail] = useState<AssetDetailResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    const controller = new AbortController();
    setIsLoading(true);
    setError(null);

    getAssetDetail(assetId, controller.signal)
      .then(setDetail)
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
  }, [assetId, refreshKey]);

  const title = detail ? detail.name : "Asset detail";
  const description = detail
    ? detail.headline
    : "Review one asset, debt, or retirement account in beginner-friendly language.";

  const Icon = useMemo(() => {
    return detail ? categoryIcon[detail.category] : WalletCards;
  }, [detail]);

  return (
    <AppShell>
      {({ openGuide, openSidebar }) => (
        <div className="mx-auto max-w-[1180px] space-y-5">
          <DashboardHeader
            description={description}
            onAskClick={openGuide}
            onMenuClick={openSidebar}
            title={title}
          />

          <Link
            className="inline-flex min-h-10 items-center gap-2 rounded-lg border border-emerald-900/10 bg-white px-3 text-sm font-semibold text-croc-moss"
            href="/portfolio"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to portfolio
          </Link>

          {isLoading ? <LoadingDetail /> : null}
          {!isLoading && error ? (
            <DetailError message={error} onRetry={() => setRefreshKey((value) => value + 1)} />
          ) : null}

          {!isLoading && detail ? (
            <>
              <div className="grid gap-5 lg:grid-cols-[minmax(0,1.35fr)_minmax(320px,0.75fr)]">
                <Card className="overflow-hidden">
                  <div className="flex flex-col gap-5 md:flex-row md:items-start md:justify-between">
                    <div className="flex gap-4">
                      <span className="grid h-14 w-14 shrink-0 place-items-center rounded-lg bg-croc-mint text-croc-moss">
                        <Icon className="h-7 w-7" />
                      </span>
                      <div>
                        <div className="flex flex-wrap gap-2">
                          <Pill tone={categoryTone[detail.category]}>{categoryLabel[detail.category]}</Pill>
                          <Pill tone={riskTone[detail.risk_level]}>{detail.risk_level} risk</Pill>
                          <Pill tone="neutral">{detail.confidence} confidence</Pill>
                        </div>
                        <h2 className="mt-4 text-3xl font-bold text-croc-ink">{formatCurrency(detail.current_value)}</h2>
                        <p className="mt-2 max-w-2xl text-sm leading-6 text-stone-600">{detail.beginner_takeaway}</p>
                      </div>
                    </div>
                    <div className="rounded-lg border border-emerald-900/10 bg-croc-cream p-4 md:w-56">
                      <p className="text-xs font-semibold uppercase text-croc-moss">Portfolio role</p>
                      <p className="mt-2 text-sm leading-6 text-stone-700">{detail.portfolio_role}</p>
                    </div>
                  </div>
                </Card>

                <Card>
                  <SectionTitle eyebrow="Key metrics" title="What CrocLens is watching" />
                  <div className="space-y-3">
                    {detail.key_metrics.map((metric) => (
                      <div className="border-b border-emerald-900/10 pb-3 last:border-0 last:pb-0" key={metric.label}>
                        <div className="flex items-center justify-between gap-3">
                          <p className="text-sm font-semibold text-croc-ink">{metric.label}</p>
                          <Pill tone={metric.tone}>{metric.value}</Pill>
                        </div>
                        <p className="mt-1 text-xs leading-5 text-stone-500">{metric.explanation}</p>
                      </div>
                    ))}
                  </div>
                </Card>
              </div>

              <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
                {[
                  ["What this is", detail.what_this_is],
                  ["Why it matters", detail.why_it_matters],
                  ["Risk", detail.risk_explanation],
                  ["Liquidity", detail.liquidity_explanation],
                  ["Tax complexity", detail.tax_complexity_explanation],
                  ["Income potential", detail.income_potential_explanation]
                ].map(([label, body]) => (
                  <Card key={label}>
                    <SectionTitle title={label} />
                    <p className="text-sm leading-6 text-stone-600">{body}</p>
                  </Card>
                ))}
              </div>

              <div className="grid gap-5 lg:grid-cols-2">
                <Card>
                  <SectionTitle eyebrow="Beginner watchlist" title="What to watch" />
                  <div className="space-y-3">
                    {detail.what_to_watch.map((item) => (
                      <div className="flex gap-3" key={item}>
                        <span className="mt-1 h-2 w-2 shrink-0 rounded-full bg-croc-moss" />
                        <p className="text-sm leading-6 text-stone-600">{item}</p>
                      </div>
                    ))}
                  </div>
                </Card>

                <Card>
                  <SectionTitle eyebrow="Safe action language" title="Possible next steps" />
                  <div className="space-y-3">
                    {detail.safe_next_steps.map((item) => (
                      <div className="flex gap-3" key={item}>
                        <CheckCircle2 className="mt-0.5 h-5 w-5 shrink-0 text-croc-moss" />
                        <p className="text-sm leading-6 text-stone-600">{item}</p>
                      </div>
                    ))}
                  </div>
                  <div className="mt-5 rounded-lg border border-amber-200 bg-amber-50 p-4">
                    <div className="flex gap-3">
                      <Shield className="mt-0.5 h-5 w-5 shrink-0 text-amber-700" />
                      <div>
                        <p className="text-sm font-semibold text-croc-ink">{detail.educational_disclaimer}</p>
                        <p className="mt-1 text-xs leading-5 text-stone-600">
                          Limitations: {detail.data_limitations.join(" ")}
                        </p>
                        <p className="mt-1 text-xs leading-5 text-stone-500">
                          Source: {detail.source.name}. {detail.source.freshness}.
                        </p>
                      </div>
                    </div>
                  </div>
                </Card>
              </div>
            </>
          ) : null}
        </div>
      )}
    </AppShell>
  );
}
