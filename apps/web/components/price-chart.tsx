"use client";

import { Area, AreaChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { formatCurrency } from "@/lib/formatters";
import type { PricePoint } from "@/lib/types";

export function PriceChart({ points }: { points: PricePoint[] }) {
  if (!points.length) {
    return <div className="rounded-xl bg-croc-cream p-6 text-stone-600">No history available.</div>;
  }

  return (
    <div className="h-[320px] rounded-xl bg-croc-cream p-4">
      <ResponsiveContainer height="100%" width="100%">
        <AreaChart data={points} margin={{ bottom: 8, left: 0, right: 8, top: 12 }}>
          <defs>
            <linearGradient id="price" x1="0" x2="0" y1="0" y2="1">
              <stop offset="5%" stopColor="#0d5c49" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#0d5c49" stopOpacity={0.03} />
            </linearGradient>
          </defs>
          <XAxis dataKey="date" minTickGap={32} tick={{ fill: "#6b6760", fontSize: 12 }} tickLine={false} />
          <YAxis domain={["auto", "auto"]} tick={{ fill: "#6b6760", fontSize: 12 }} tickFormatter={(value) => `$${value}`} tickLine={false} width={56} />
          <Tooltip formatter={(value) => formatCurrency(Number(value), "USD")} labelClassName="text-croc-ink" />
          <Area dataKey="close" fill="url(#price)" stroke="#0d5c49" strokeWidth={3} type="monotone" />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
