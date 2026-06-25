"use client";

import { useEffect, useState } from "react";
import { ArrowDownRight, ArrowUpRight, RefreshCw } from "lucide-react";
import { getGuide, getHistory, getQuote } from "@/lib/api";
import { formatCurrency, formatNumber, formatPercent } from "@/lib/formatters";
import type { GuideResponse, MarketHistoryResponse, QuoteResponse } from "@/lib/types";
import { AssetSearch } from "./asset-search";
import { CrocGuide } from "./croc-guide";
import { PriceChart } from "./price-chart";

export function AssetSummary({ symbol }: { symbol: string }) {
  const [quote, setQuote] = useState<QuoteResponse | null>(null);
  const [history, setHistory] = useState<MarketHistoryResponse | null>(null);
  const [guide, setGuide] = useState<GuideResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;
    async function load() {
      setIsLoading(true);
      setError(null);
      try {
        const [quoteResponse, historyResponse, guideResponse] = await Promise.all([
          getQuote(symbol),
          getHistory(symbol, "6mo"),
          getGuide(symbol)
        ]);
        if (isMounted) {
          setQuote(quoteResponse);
          setHistory(historyResponse);
          setGuide(guideResponse);
        }
      } catch (caught) {
        if (isMounted) {
          setError(caught instanceof Error ? caught.message : "CrocLens could not load this asset.");
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    }
    load();
    return () => {
      isMounted = false;
    };
  }, [symbol]);

  if (isLoading) {
    return (
      <div className="rounded-2xl border border-emerald-900/10 bg-white p-6 shadow-card">
        <div className="flex items-center gap-3 text-croc-moss">
          <RefreshCw className="h-5 w-5 animate-spin" />
          <p className="font-semibold">Loading latest available market data...</p>
        </div>
      </div>
    );
  }

  if (error || !quote || !history || !guide) {
    return (
      <div className="space-y-5">
        <AssetSearch />
        <div className="rounded-2xl border border-rose-200 bg-rose-50 p-6 text-rose-800">
          <h1 className="text-xl font-bold">Asset could not load</h1>
          <p className="mt-2">{error ?? "No data was returned."}</p>
        </div>
      </div>
    );
  }

  const isPositive = (quote.change ?? 0) >= 0;
  const DirectionIcon = isPositive ? ArrowUpRight : ArrowDownRight;

  return (
    <div className="space-y-6">
      <AssetSearch />
      <section className="grid gap-5 lg:grid-cols-[1fr_0.7fr]">
        <div className="rounded-2xl border border-emerald-900/10 bg-white p-6 shadow-card">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div>
              <p className="text-sm font-semibold uppercase text-croc-moss">{quote.symbol}</p>
              <h1 className="mt-1 text-3xl font-bold text-croc-ink">{quote.name}</h1>
              <p className="mt-2 text-sm text-stone-500">Data as of {quote.data_as_of}. Source: {quote.provider}.</p>
            </div>
            <div className="text-right">
              <p className="text-4xl font-bold text-croc-ink">{formatCurrency(quote.price, quote.currency)}</p>
              <p className={`mt-2 inline-flex items-center gap-1 rounded-lg px-2 py-1 text-sm font-semibold ${isPositive ? "bg-croc-mint text-croc-moss" : "bg-rose-100 text-rose-700"}`}>
                <DirectionIcon className="h-4 w-4" />
                {quote.change === null ? "No change data" : `${formatCurrency(quote.change, quote.currency)} (${formatPercent(quote.change_percent)})`}
              </p>
            </div>
          </div>

          <div className="mt-6 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            <Stat label="Previous close" value={quote.previous_close ? formatCurrency(quote.previous_close, quote.currency) : "N/A"} />
            <Stat label="Day range" value={quote.day_low && quote.day_high ? `${formatCurrency(quote.day_low, quote.currency)} - ${formatCurrency(quote.day_high, quote.currency)}` : "N/A"} />
            <Stat label="Volume" value={quote.volume ? formatNumber(quote.volume) : "N/A"} />
            <Stat label="Market cap" value={quote.market_cap ? formatCurrency(quote.market_cap, quote.currency, true) : "N/A"} />
          </div>

          <div className="mt-6">
            <PriceChart points={history.points} />
          </div>
        </div>

        <CrocGuide guide={guide} />
      </section>
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-emerald-900/10 bg-croc-cream p-4">
      <p className="text-xs font-semibold uppercase text-stone-500">{label}</p>
      <p className="mt-2 font-bold text-croc-ink">{value}</p>
    </div>
  );
}
