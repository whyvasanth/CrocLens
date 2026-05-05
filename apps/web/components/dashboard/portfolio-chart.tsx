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
import { formatCompactCurrency } from "@/lib/formatters";
import { Card, Pill, SectionTitle } from "@/components/dashboard/ui";

export function PortfolioChart() {
  return (
    <Card>
      <SectionTitle
        eyebrow="Portfolio overview"
        title="Total value"
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
      <div className="mb-2 flex flex-wrap items-end gap-3">
        <p className="text-3xl font-bold text-croc-ink">$214,800</p>
        <Pill tone="green">+2.1% this month</Pill>
      </div>
      <p className="mb-4 text-sm font-semibold text-croc-moss">+$4,200 estimated change</p>
      <div className="h-64">
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
        Beginner note: total value shows your tracked assets before subtracting liabilities.
      </p>
    </Card>
  );
}
