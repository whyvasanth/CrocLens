"use client";

import { useEffect, useMemo, useState } from "react";
import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
} from "recharts";
import Link from "next/link";
import { AlertCircle, RefreshCw } from "lucide-react";
import { getPortfolioHistory } from "@/lib/api-client";
import { portfolioHistory } from "@/lib/mock-dashboard-data";
import { formatCompactCurrency, formatCurrency } from "@/lib/formatters";
import { Card, Pill, SectionTitle } from "@/components/dashboard/ui";
import type { AccountUserResponse, PortfolioHistoryResponse, PortfolioSummaryResponse } from "@/types/api";

const periods = ["1M", "3M", "6M", "YTD", "1Y", "All"] as const;
type ChartPeriod = (typeof periods)[number];

interface PortfolioChartProps {
  account: AccountUserResponse | null;
  isLoading: boolean;
  portfolio: PortfolioSummaryResponse | null;
}

interface ChartPoint {
  label: string;
  value: number;
  source: string;
  quality: string;
}

function formatDateLabel(value: string) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return date.toLocaleDateString("en-US", { month: "short", day: "numeric" });
}

function getDemoChartData(): ChartPoint[] {
  return portfolioHistory.map((point) => ({
    label: point.month,
    value: point.value,
    source: "CrocLens demo dataset",
    quality: "demo"
  }));
}

export function PortfolioChart({ account, isLoading, portfolio }: PortfolioChartProps) {
  const [period, setPeriod] = useState<ChartPeriod>("1M");
  const [history, setHistory] = useState<PortfolioHistoryResponse | null>(null);
  const [historyError, setHistoryError] = useState<string | null>(null);
  const [isHistoryLoading, setIsHistoryLoading] = useState(false);
  const [reloadKey, setReloadKey] = useState(0);
  const isSignedIn = Boolean(account);
  const netWorth = portfolio?.net_worth ?? 214_800;
  const totalAssets = portfolio?.total_assets ?? 329_400;
  const totalLiabilities = portfolio?.total_liabilities ?? 114_600;
  const sourceLabel = portfolio?.sources[0]?.freshness ?? "Demo data";
  const hasTrackedAssets = totalAssets > 0;

  useEffect(() => {
    if (!account) {
      setHistory(null);
      setHistoryError(null);
      setIsHistoryLoading(false);
      return;
    }

    const controller = new AbortController();
    setIsHistoryLoading(true);
    setHistoryError(null);

    getPortfolioHistory(controller.signal)
      .then(setHistory)
      .catch((caught) => {
        if (controller.signal.aborted) {
          return;
        }

        setHistoryError(caught instanceof Error ? caught.message : "Portfolio history could not load.");
      })
      .finally(() => {
        if (!controller.signal.aborted) {
          setIsHistoryLoading(false);
        }
      });

    return () => controller.abort();
  }, [account, reloadKey]);

  const chartData = useMemo<ChartPoint[]>(() => {
    if (!isSignedIn) {
      return getDemoChartData();
    }

    return (history?.points ?? []).map((point) => ({
      label: formatDateLabel(point.snapshot_date),
      value: point.net_worth,
      source: point.source_name,
      quality: point.data_quality
    }));
  }, [history?.points, isSignedIn]);

  return (
    <Card>
      <SectionTitle
        eyebrow="Portfolio overview"
        title="Net worth"
        action={
          <div className="hidden gap-2 text-xs font-semibold text-stone-600 sm:flex" aria-label="Net worth chart period">
            {periods.map((label) => (
              <button
                key={label}
                className={label === period ? "rounded-md border border-croc-moss px-2 py-1 text-croc-moss" : "rounded-md px-2 py-1 hover:bg-croc-mint"}
                onClick={() => setPeriod(label)}
                suppressHydrationWarning
                type="button"
              >
                {label}
              </button>
            ))}
          </div>
        }
      />
      {isLoading ? (
        <div className="mb-5 space-y-3">
          <div className="h-10 w-48 animate-pulse rounded-md bg-stone-100" />
          <div className="h-7 w-36 animate-pulse rounded-md bg-stone-100" />
        </div>
      ) : (
        <>
          <div className="mb-2 flex flex-wrap items-end gap-3">
            <p className="text-4xl font-bold text-croc-ink">{formatCurrency(netWorth)}</p>
            <Pill tone={isSignedIn ? "green" : "gold"}>{isSignedIn ? "Your records" : "Demo data"}</Pill>
          </div>
          <p className="mb-4 text-sm font-semibold text-croc-moss">
            {formatCurrency(totalAssets)} assets minus {formatCurrency(totalLiabilities)} liabilities
          </p>
        </>
      )}
      {!isLoading && !hasTrackedAssets ? (
        <div className="mb-4 rounded-lg border border-emerald-900/10 bg-croc-cream p-4">
          <p className="text-sm font-semibold text-croc-ink">Start with your first record</p>
          <p className="mt-2 text-sm leading-6 text-stone-600">
            Add cash, an ETF, a retirement balance, or a debt on the Portfolio page. CrocLens will calculate net worth from those records.
          </p>
          <Link href="/portfolio" className="mt-3 inline-flex text-sm font-semibold text-croc-moss">
            Open Portfolio
          </Link>
        </div>
      ) : null}

      {historyError ? (
        <div className="mb-4 rounded-lg border border-amber-200 bg-amber-50 p-4">
          <div className="flex gap-3">
            <AlertCircle className="mt-0.5 h-4 w-4 shrink-0 text-amber-700" />
            <div>
              <p className="text-sm font-semibold text-amber-900">History could not load</p>
              <p className="mt-1 text-sm leading-6 text-amber-800">{historyError}</p>
            </div>
          </div>
          <button
            className="mt-3 inline-flex min-h-10 items-center gap-2 rounded-lg bg-white px-3 text-sm font-semibold text-amber-900"
            onClick={() => setReloadKey((key) => key + 1)}
            suppressHydrationWarning
            type="button"
          >
            <RefreshCw className="h-4 w-4" />
            Retry history
          </button>
        </div>
      ) : null}

      {isHistoryLoading ? (
        <div className="grid h-72 place-items-center rounded-lg bg-croc-cream" aria-live="polite">
          <p className="text-sm font-semibold text-stone-600">Loading net worth history...</p>
        </div>
      ) : isSignedIn && chartData.length === 0 ? (
        <div className="grid h-72 place-items-center rounded-lg border border-emerald-900/10 bg-croc-cream p-6 text-center">
          <div>
            <p className="text-sm font-semibold text-croc-ink">No saved net worth history yet</p>
            <p className="mt-2 max-w-md text-sm leading-6 text-stone-600">
              Refresh prices or keep tracking your portfolio over time. CrocLens will show real saved snapshots here instead of drawing a fake trend line.
            </p>
            <Link href="/portfolio" className="mt-3 inline-flex text-sm font-semibold text-croc-moss">
              Review portfolio
            </Link>
          </div>
        </div>
      ) : (
        <div className="h-72">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={chartData} margin={{ left: 0, right: 8, top: 8, bottom: 0 }}>
              <defs>
                <linearGradient id="netWorthFill" x1="0" x2="0" y1="0" y2="1">
                  <stop offset="5%" stopColor="#0d5c49" stopOpacity={0.32} />
                  <stop offset="95%" stopColor="#0d5c49" stopOpacity={0.02} />
                </linearGradient>
              </defs>
              <CartesianGrid stroke="#e5eee9" vertical={false} />
              <XAxis
                dataKey="label"
                axisLine={false}
                tickLine={false}
                tick={{ fill: "#61716b", fontSize: 12 }}
              />
              <YAxis
                axisLine={false}
                tickLine={false}
                tick={{ fill: "#61716b", fontSize: 12 }}
                tickFormatter={formatCompactCurrency}
                width={58}
              />
              <Tooltip
                formatter={(value, _name, item) => [
                  `${formatCompactCurrency(Number(value))} (${item.payload.quality})`,
                  "Net worth"
                ]}
                labelFormatter={(label) => `${label} · ${chartData.find((point) => point.label === label)?.source ?? "Source unavailable"}`}
                contentStyle={{
                  borderRadius: 8,
                  border: "1px solid rgba(13, 92, 73, 0.16)",
                  boxShadow: "0 12px 30px rgba(16, 35, 31, 0.12)"
                }}
              />
              <Area
                type="monotone"
                dataKey="value"
                stroke="#0d5c49"
                strokeWidth={3}
                fill="url(#netWorthFill)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      )}
      <p className="mt-3 text-sm leading-6 text-stone-600">
        Beginner note: net worth is what you own minus what you owe.
      </p>
      <p className="mt-2 text-xs text-stone-500">
        Source: {isSignedIn ? sourceLabel : "Demo dataset"}. Selected view: {period}.
      </p>
    </Card>
  );
}
