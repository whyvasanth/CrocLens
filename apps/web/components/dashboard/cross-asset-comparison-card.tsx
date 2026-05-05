"use client";

import { ArrowDownRight, ArrowRight, ArrowUpRight } from "lucide-react";
import {
  Line,
  LineChart,
  ResponsiveContainer
} from "recharts";
import { comparisonAssets } from "@/lib/mock-dashboard-data";
import { Card, SectionTitle } from "@/components/dashboard/ui";

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

export function CrossAssetComparisonCard() {
  return (
    <Card>
      <SectionTitle
        eyebrow="Cross-asset comparison"
        title="What is moving in your world"
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
        {comparisonAssets.map((asset) => {
          const Icon = directionIcon[asset.direction];
          const chartData = asset.sparkline.map((value, index) => ({ index, value }));

          return (
            <article key={asset.symbol} className="rounded-lg border border-emerald-900/10 bg-white p-3">
              <div className="flex items-start justify-between gap-2">
                <div>
                  <h3 className="font-bold text-croc-ink">{asset.symbol}</h3>
                  <p className="mt-1 text-xs text-stone-500">{asset.name}</p>
                </div>
                <span className={`inline-flex items-center gap-1 text-xs font-bold ${directionClass[asset.direction]}`}>
                  <Icon className="h-3.5 w-3.5" />
                  {asset.change}
                </span>
              </div>
              <div className="mt-3 h-14">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={chartData}>
                    <Line
                      type="monotone"
                      dataKey="value"
                      stroke={asset.direction === "down" ? "#e11d48" : "#0d5c49"}
                      strokeWidth={2}
                      dot={false}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
              <p className="mt-2 text-sm font-semibold text-croc-ink">{asset.price}</p>
              <p className="mt-1 text-xs text-stone-500">vs previous close</p>
            </article>
          );
        })}
      </div>
    </Card>
  );
}
