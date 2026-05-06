"use client";

import { useEffect, useState } from "react";
import { AlertTriangle, Leaf, RefreshCw } from "lucide-react";
import { AppShell } from "@/components/dashboard/app-shell";
import { DashboardHeader } from "@/components/dashboard/dashboard-header";
import { Card, Pill, SectionTitle } from "@/components/dashboard/ui";
import { getTaxInsights } from "@/lib/api-client";
import { formatCurrency } from "@/lib/formatters";
import type { TaxInsightResponse } from "@/types/api";

export function TaxPlannerPage() {
  const [data, setData] = useState<TaxInsightResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  async function loadTaxInsights(signal?: AbortSignal) {
    setIsLoading(true);
    setError(null);
    try {
      setData(await getTaxInsights(signal));
    } catch (caught) {
      if (caught instanceof DOMException && caught.name === "AbortError") return;
      setError("CrocLens could not load tax insights.");
    } finally {
      if (!signal?.aborted) setIsLoading(false);
    }
  }

  useEffect(() => {
    const controller = new AbortController();
    void loadTaxInsights(controller.signal);
    return () => controller.abort();
  }, []);

  return (
    <AppShell>
      {({ openGuide, openSidebar }) => (
        <div className="mx-auto max-w-[1180px] space-y-5">
          <DashboardHeader
            description="Learn tax lots, holding periods, unrealized gains, and loss-harvesting concepts without tax advice."
            onAskClick={openGuide}
            onMenuClick={openSidebar}
            title="Tax Planner"
          />

          {error ? (
            <Card className="border-rose-200 bg-rose-50">
              <div className="flex items-center justify-between gap-4">
                <p className="text-sm font-semibold text-rose-900">{error}</p>
                <button
                  className="inline-flex min-h-10 items-center gap-2 rounded-lg bg-white px-4 text-sm font-semibold text-rose-900"
                  onClick={() => void loadTaxInsights()}
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
                eyebrow="Tax-aware insight"
                title={isLoading ? "Loading tax lots" : data?.headline ?? "Tax lots"}
                action={<Pill tone="gold">Educational</Pill>}
              />
              <p className="text-sm leading-6 text-stone-600">{data?.beginner_summary}</p>
              <div className="mt-5 grid gap-3 sm:grid-cols-2">
                <div className="rounded-lg bg-croc-mint p-4">
                  <p className="text-xs font-semibold uppercase text-croc-moss">Unrealized gains</p>
                  <p className="mt-2 text-2xl font-bold text-croc-ink">
                    {formatCurrency(data?.total_unrealized_gain ?? 0)}
                  </p>
                </div>
                <div className="rounded-lg bg-rose-50 p-4">
                  <p className="text-xs font-semibold uppercase text-rose-700">Unrealized losses</p>
                  <p className="mt-2 text-2xl font-bold text-croc-ink">
                    {formatCurrency(data?.total_unrealized_loss ?? 0)}
                  </p>
                </div>
              </div>
              <div className="mt-5 space-y-3">
                {data?.tax_lots.map((lot) => (
                  <div className="rounded-lg border border-emerald-900/10 p-4" key={lot.id}>
                    <div className="flex flex-wrap items-start justify-between gap-3">
                      <div>
                        <p className="font-bold text-croc-ink">{lot.symbol}</p>
                        <p className="text-sm text-stone-600">{lot.asset_name}</p>
                      </div>
                      <Pill tone={lot.holding_term === "long_term" ? "green" : "gold"}>
                        {lot.holding_term === "long_term" ? "Long-term" : "Short-term"}
                      </Pill>
                    </div>
                    <p className="mt-3 text-sm leading-6 text-stone-600">{lot.beginner_explanation}</p>
                  </div>
                ))}
              </div>
            </Card>

            <div className="space-y-5">
              <Card>
                <SectionTitle eyebrow="Loss review" title="Harvesting education" />
                <div className="space-y-3">
                  {data?.harvesting_opportunities.map((opportunity) => (
                    <div className="rounded-lg border border-emerald-900/10 p-3" key={opportunity.id}>
                      <div className="flex gap-3">
                        <span className="grid h-10 w-10 shrink-0 place-items-center rounded-lg bg-croc-mint text-croc-moss">
                          <Leaf className="h-5 w-5" />
                        </span>
                        <div>
                          <p className="text-sm font-bold text-croc-ink">{opportunity.title}</p>
                          <p className="mt-1 text-sm leading-6 text-stone-600">{opportunity.explanation}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </Card>

              <Card>
                <SectionTitle eyebrow="Guardrail" title="Wash-sale warning" />
                <div className="flex gap-3">
                  <AlertTriangle className="mt-1 h-5 w-5 shrink-0 text-amber-700" />
                  <p className="text-sm leading-6 text-stone-600">{data?.wash_sale_warning}</p>
                </div>
              </Card>
            </div>
          </div>
        </div>
      )}
    </AppShell>
  );
}
