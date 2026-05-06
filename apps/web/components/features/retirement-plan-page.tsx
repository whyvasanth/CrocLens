"use client";

import { useEffect, useState } from "react";
import { RefreshCw, TrendingUp } from "lucide-react";
import { AppShell } from "@/components/dashboard/app-shell";
import { DashboardHeader } from "@/components/dashboard/dashboard-header";
import { Card, Pill, SectionTitle } from "@/components/dashboard/ui";
import { getRetirementPlan } from "@/lib/api-client";
import { formatCurrency, formatPercent } from "@/lib/formatters";
import type { RetirementPlanResponse } from "@/types/api";

export function RetirementPlanPage() {
  const [data, setData] = useState<RetirementPlanResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  async function loadPlan(signal?: AbortSignal) {
    setIsLoading(true);
    setError(null);
    try {
      setData(await getRetirementPlan(signal));
    } catch (caught) {
      if (caught instanceof DOMException && caught.name === "AbortError") return;
      setError("CrocLens could not load the retirement plan.");
    } finally {
      if (!signal?.aborted) setIsLoading(false);
    }
  }

  useEffect(() => {
    const controller = new AbortController();
    void loadPlan(controller.signal);
    return () => controller.abort();
  }, []);

  return (
    <AppShell>
      {({ openGuide, openSidebar }) => (
        <div className="mx-auto max-w-[1180px] space-y-5">
          <DashboardHeader
            description="Understand retirement progress, employer match, and contribution scenarios with clear assumptions."
            onAskClick={openGuide}
            onMenuClick={openSidebar}
            title="Retirement Planner"
          />

          {error ? (
            <Card className="border-rose-200 bg-rose-50">
              <div className="flex items-center justify-between gap-4">
                <p className="text-sm font-semibold text-rose-900">{error}</p>
                <button
                  className="inline-flex min-h-10 items-center gap-2 rounded-lg bg-white px-4 text-sm font-semibold text-rose-900"
                  onClick={() => void loadPlan()}
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
                eyebrow="Progress"
                title={isLoading ? "Loading retirement plan" : data?.headline ?? "Retirement plan"}
                action={<Pill tone="green">{formatPercent(data?.progress_percent ?? 0)} funded</Pill>}
              />
              <p className="text-sm leading-6 text-stone-600">{data?.beginner_summary}</p>
              <div className="mt-5 h-3 rounded-full bg-stone-100">
                <div
                  className="h-3 rounded-full bg-croc-moss"
                  style={{ width: `${Math.min(data?.progress_percent ?? 0, 100)}%` }}
                />
              </div>
              <div className="mt-5 grid gap-3 sm:grid-cols-2">
                {data?.accounts.map((account) => (
                  <div className="rounded-lg border border-emerald-900/10 bg-croc-cream p-4" key={account.id}>
                    <p className="text-xs font-semibold uppercase text-croc-moss">{account.account_type}</p>
                    <p className="mt-2 text-2xl font-bold text-croc-ink">
                      {formatCurrency(account.current_balance)}
                    </p>
                    <p className="mt-2 text-sm leading-6 text-stone-600">{account.investment_mix_summary}</p>
                  </div>
                ))}
              </div>
            </Card>

            <div className="space-y-5">
              <Card>
                <SectionTitle eyebrow="Employer match" title="Sample match explanation" />
                <p className="text-sm font-semibold text-croc-ink">{data?.employer_match.formula}</p>
                <p className="mt-2 text-sm leading-6 text-stone-600">{data?.employer_match.beginner_explanation}</p>
                <p className="mt-4 text-2xl font-bold text-croc-moss">
                  {formatCurrency(data?.employer_match.estimated_annual_match ?? 0)}
                </p>
              </Card>

              <Card>
                <SectionTitle eyebrow="Scenarios" title="Contribution comparison" />
                <div className="space-y-3">
                  {data?.scenarios.map((scenario) => (
                    <div className="rounded-lg border border-emerald-900/10 p-3" key={scenario.id}>
                      <div className="flex items-start gap-3">
                        <span className="grid h-10 w-10 shrink-0 place-items-center rounded-lg bg-croc-mint text-croc-moss">
                          <TrendingUp className="h-5 w-5" />
                        </span>
                        <div>
                          <p className="text-sm font-bold text-croc-ink">{scenario.label}</p>
                          <p className="mt-1 text-sm text-stone-600">
                            {formatCurrency(scenario.projected_balance_at_65)} projected at 65
                          </p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </Card>
            </div>
          </div>
        </div>
      )}
    </AppShell>
  );
}
