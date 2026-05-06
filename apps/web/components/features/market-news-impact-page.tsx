"use client";

import { useEffect, useState } from "react";
import { AlertCircle, Newspaper, RefreshCw } from "lucide-react";
import { AppShell } from "@/components/dashboard/app-shell";
import { DashboardHeader } from "@/components/dashboard/dashboard-header";
import { Card, Pill, SectionTitle } from "@/components/dashboard/ui";
import { getMarketNewsImpact } from "@/lib/api-client";
import type { MarketNewsImpactResponse } from "@/types/api";

export function MarketNewsImpactPage() {
  const [data, setData] = useState<MarketNewsImpactResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  async function loadImpact(signal?: AbortSignal) {
    setIsLoading(true);
    setError(null);
    try {
      const response = await getMarketNewsImpact(signal);
      setData(response);
    } catch (caught) {
      if (caught instanceof DOMException && caught.name === "AbortError") return;
      setError("CrocLens could not load the market impact summary.");
    } finally {
      if (!signal?.aborted) setIsLoading(false);
    }
  }

  useEffect(() => {
    const controller = new AbortController();
    void loadImpact(controller.signal);
    return () => controller.abort();
  }, []);

  return (
    <AppShell>
      {({ openGuide, openSidebar }) => (
        <div className="mx-auto max-w-[1180px] space-y-5">
          <DashboardHeader
            description="See which sample headlines may touch your holdings, without turning news into trading instructions."
            onAskClick={openGuide}
            onMenuClick={openSidebar}
            title="Market News Impact"
          />

          {error ? (
            <Card className="border-rose-200 bg-rose-50">
              <div className="flex items-center justify-between gap-4">
                <div className="flex gap-3">
                  <AlertCircle className="mt-1 h-5 w-5 text-rose-700" />
                  <p className="text-sm font-semibold text-rose-900">{error}</p>
                </div>
                <button
                  className="inline-flex min-h-10 items-center gap-2 rounded-lg bg-white px-4 text-sm font-semibold text-rose-900"
                  onClick={() => void loadImpact()}
                  suppressHydrationWarning
                  type="button"
                >
                  <RefreshCw className="h-4 w-4" />
                  Retry
                </button>
              </div>
            </Card>
          ) : null}

          <div className="grid gap-5 lg:grid-cols-[minmax(0,1.25fr)_minmax(320px,0.75fr)]">
            <Card>
              <SectionTitle
                eyebrow="How does this affect me?"
                title={isLoading ? "Loading impact summary" : data?.headline ?? "Impact summary"}
                action={<Pill tone="green">Educational</Pill>}
              />
              <p className="text-sm leading-6 text-stone-600">
                {data?.beginner_summary ??
                  "CrocLens is preparing a beginner-friendly explanation using sample news and sample holdings."}
              </p>
              <div className="mt-5 grid gap-3 sm:grid-cols-2">
                {data?.affected_holdings.map((holding) => (
                  <div className="rounded-lg border border-emerald-900/10 bg-croc-cream p-4" key={holding.holding_id}>
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <p className="text-sm font-bold text-croc-ink">{holding.name}</p>
                        <p className="text-xs font-semibold uppercase text-croc-moss">{holding.asset_type}</p>
                      </div>
                      <Pill tone={holding.impact_level === "high" ? "coral" : "gold"}>{holding.impact_level}</Pill>
                    </div>
                    <p className="mt-3 text-sm leading-6 text-stone-600">{holding.why_it_matters}</p>
                  </div>
                ))}
              </div>
            </Card>

            <div className="space-y-5">
              <Card>
                <SectionTitle eyebrow="Sample headlines" title="News context" />
                <div className="space-y-3">
                  {data?.articles.map((article) => (
                    <div className="rounded-lg border border-emerald-900/10 p-3" key={article.id}>
                      <div className="flex gap-3">
                        <span className="grid h-10 w-10 shrink-0 place-items-center rounded-lg bg-croc-mint text-croc-moss">
                          <Newspaper className="h-5 w-5" />
                        </span>
                        <div>
                          <p className="text-sm font-bold text-croc-ink">{article.title}</p>
                          <p className="mt-1 text-sm leading-6 text-stone-600">{article.summary}</p>
                        </div>
                      </div>
                    </div>
                  )) ?? <p className="text-sm text-stone-600">Loading sample headlines...</p>}
                </div>
              </Card>

              <Card>
                <SectionTitle eyebrow="Safe next questions" title="Ask before acting" />
                <ul className="space-y-2 text-sm leading-6 text-stone-600">
                  {data?.suggested_questions.map((question) => <li key={question}>{question}</li>) ?? null}
                </ul>
                <p className="mt-4 text-xs leading-5 text-stone-500">{data?.educational_disclaimer}</p>
              </Card>
            </div>
          </div>
        </div>
      )}
    </AppShell>
  );
}
