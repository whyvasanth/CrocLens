"use client";

import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
} from "recharts";
import { portfolioHistory } from "@/lib/mock-dashboard-data";
import { formatCompactCurrency, formatCurrency } from "@/lib/formatters";
import { Card, Pill, SectionTitle } from "@/components/dashboard/ui";
import type { PortfolioSummaryResponse } from "@/types/api";

interface PortfolioChartProps {
  isLoading: boolean;
  portfolio: PortfolioSummaryResponse | null;
}

export function PortfolioChart({ isLoading, portfolio }: PortfolioChartProps) {
  const netWorth = portfolio?.net_worth ?? 214_800;
  const totalAssets = portfolio?.total_assets ?? 329_400;
  const totalLiabilities = portfolio?.total_liabilities ?? 114_600;
  const sourceLabel = portfolio?.sources[0]?.freshness ?? "Static mock data";

  return (
    <Card>
      <SectionTitle
        eyebrow="Portfolio overview"
        title="Net worth"
        action={
          <div className="hidden gap-2 text-xs font-semibold text-stone-600 sm:flex">
            {["1M", "3M", "6M", "YTD", "1Y", "All"].map((label) => (
              <span
                key={label}
                className={label === "1M" ? "rounded-md border border-croc-moss px-2 py-1 text-croc-moss" : "px-2 py-1"}
              >
                {label}
              </span>
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
            <Pill tone="green">API-backed</Pill>
          </div>
          <p className="mb-4 text-sm font-semibold text-croc-moss">
            {formatCurrency(totalAssets)} assets minus {formatCurrency(totalLiabilities)} liabilities
          </p>
        </>
      )}
      <div className="h-72">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={portfolioHistory} margin={{ left: 0, right: 8, top: 8, bottom: 0 }}>
            <defs>
              <linearGradient id="netWorthFill" x1="0" x2="0" y1="0" y2="1">
                <stop offset="5%" stopColor="#0d5c49" stopOpacity={0.32} />
                <stop offset="95%" stopColor="#0d5c49" stopOpacity={0.02} />
              </linearGradient>
            </defs>
            <CartesianGrid stroke="#e5eee9" vertical={false} />
            <XAxis
              dataKey="month"
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
              formatter={(value) => [formatCompactCurrency(Number(value)), "Net worth"]}
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
      <p className="mt-3 text-sm leading-6 text-stone-600">
        Beginner note: net worth is what you own minus what you owe.
      </p>
      <p className="mt-2 text-xs text-stone-500">
        Source: {sourceLabel}. Trend line is still sample history until the backend adds time-series data.
      </p>
    </Card>
  );
}
