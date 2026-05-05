"use client";

import { ArrowDownRight, ArrowRight, ArrowUpRight } from "lucide-react";
import {
  Line,
  LineChart,
  ResponsiveContainer
} from "recharts";
import { Card, SectionTitle } from "@/components/dashboard/ui";
import { formatCurrency } from "@/lib/formatters";
import type { AssetResponse, RiskLevel } from "@/types/api";

const directionIcon = {
  up: ArrowUpRight,
  down: ArrowDownRight,
  flat: ArrowRight
};

const directionClass = {
  up: "text-croc-moss",
  down: "text-rose-600",
  flat: "text-amber-700"
};

const riskToDirection: Record<RiskLevel, "up" | "down" | "flat"> = {
  high: "down",
  medium: "flat",
  low: "up"
};

const sparklineByRisk: Record<RiskLevel, number[]> = {
  high: [70, 68, 71, 64, 67, 59, 62, 55, 58],
  medium: [42, 44, 43, 48, 47, 51, 50, 53, 55],
  low: [30, 31, 31, 32, 32, 33, 33, 34, 34]
};

interface CrossAssetComparisonCardProps {
  assets: AssetResponse[];
  isLoading: boolean;
}

export function CrossAssetComparisonCard({ assets, isLoading }: CrossAssetComparisonCardProps) {
  return (
    <Card>
      <SectionTitle
        eyebrow="Cross-asset comparison"
        title="API-backed tracked assets"
        action={<a href="#" className="text-sm font-semibold text-croc-moss">View more</a>}
      />
      <div className="mb-4 flex gap-6 border-b border-emerald-900/10 text-sm font-semibold text-stone-500">
        {["Stocks", "ETFs", "Crypto", "Bonds"].map((tab) => (
          <span
            key={tab}
            className={tab === "Stocks" ? "-mb-px border-b-2 border-croc-moss pb-3 text-croc-moss" : "pb-3"}
          >
            {tab}
          </span>
        ))}
      </div>
      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        {isLoading
          ? [0, 1, 2].map((item) => (
              <article key={item} className="rounded-lg border border-emerald-900/10 bg-white p-3">
                <div className="h-5 w-20 animate-pulse rounded-md bg-stone-100" />
                <div className="mt-2 h-4 w-32 animate-pulse rounded-md bg-stone-100" />
                <div className="mt-4 h-14 animate-pulse rounded-md bg-stone-100" />
                <div className="mt-3 h-5 w-24 animate-pulse rounded-md bg-stone-100" />
              </article>
            ))
          : assets.map((asset) => {
              const direction = riskToDirection[asset.risk_level];
              const Icon = directionIcon[direction];
              const chartData = sparklineByRisk[asset.risk_level].map((value, index) => ({ index, value }));
              const priceLabel =
                asset.current_price === null
                  ? formatCurrency(asset.market_value)
                  : formatCurrency(asset.current_price);

              return (
                <article key={asset.id} className="rounded-lg border border-emerald-900/10 bg-white p-3">
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <h3 className="font-bold text-croc-ink">{asset.symbol}</h3>
                      <p className="mt-1 text-xs text-stone-500">{asset.name}</p>
                    </div>
                    <span className={`inline-flex items-center gap-1 text-xs font-bold ${directionClass[direction]}`}>
                      <Icon className="h-3.5 w-3.5" />
                      {asset.risk_level} risk
                    </span>
                  </div>
                  <div className="mt-3 h-14">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={chartData}>
                        <Line
                          type="monotone"
                          dataKey="value"
                          stroke={direction === "down" ? "#e11d48" : "#0d5c49"}
                          strokeWidth={2}
                          dot={false}
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                  <p className="mt-2 text-sm font-semibold text-croc-ink">{priceLabel}</p>
                  <p className="mt-1 text-xs text-stone-500">{asset.allocation_percent}% allocation</p>
                </article>
              );
            })}
      </div>
      {!isLoading && assets.length === 0 ? (
        <p className="mt-4 text-sm leading-6 text-stone-600">
          No assets returned from the API yet. Start the FastAPI backend and retry.
        </p>
      ) : null}
    </Card>
  );
}
