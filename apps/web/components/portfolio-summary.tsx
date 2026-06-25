"use client";

import { useEffect, useState } from "react";
import { getDemoPortfolio } from "@/lib/api";
import { formatCurrency } from "@/lib/formatters";
import type { DemoPortfolioResponse } from "@/lib/types";

export function PortfolioSummary() {
  const [portfolio, setPortfolio] = useState<DemoPortfolioResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getDemoPortfolio()
      .then(setPortfolio)
      .catch((caught) => setError(caught instanceof Error ? caught.message : "Demo portfolio could not load."));
  }, []);

  if (error) {
    return <div className="rounded-2xl border border-rose-200 bg-rose-50 p-5 text-rose-800">{error}</div>;
  }

  if (!portfolio) {
    return <div className="rounded-2xl border border-emerald-900/10 bg-white p-5 shadow-card">Loading demo portfolio...</div>;
  }

  return (
    <section className="rounded-2xl border border-emerald-900/10 bg-white p-6 shadow-card">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="text-sm font-semibold uppercase text-croc-moss">Demo portfolio</p>
          <h2 className="mt-1 text-2xl font-bold text-croc-ink">{formatCurrency(portfolio.total_value, "USD")}</h2>
          <p className="mt-2 text-sm text-stone-600">Sample ETF allocation for learning. This is not your personal portfolio.</p>
        </div>
        <span className="rounded-lg bg-amber-100 px-3 py-2 text-sm font-semibold text-amber-800">Sample data</span>
      </div>
      <div className="mt-5 grid gap-3 md:grid-cols-3">
        {portfolio.holdings.map((holding) => (
          <article className="rounded-xl border border-emerald-900/10 bg-croc-cream p-4" key={holding.symbol}>
            <div className="flex items-start justify-between gap-3">
              <div>
                <h3 className="font-bold text-croc-ink">{holding.symbol}</h3>
                <p className="mt-1 text-sm text-stone-600">{holding.name}</p>
              </div>
              <p className="font-bold text-croc-moss">{holding.allocation_percent}%</p>
            </div>
            <p className="mt-3 text-sm text-stone-600">{holding.note}</p>
            <p className="mt-3 text-sm font-semibold text-croc-ink">{formatCurrency(holding.market_value, "USD")}</p>
          </article>
        ))}
      </div>
    </section>
  );
}
