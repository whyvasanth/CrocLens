"use client";

import { useEffect, useState } from "react";
import { CheckCircle2, RefreshCw, RotateCcw, Sparkles, XCircle } from "lucide-react";
import { AppShell } from "@/components/dashboard/app-shell";
import { DashboardHeader } from "@/components/dashboard/dashboard-header";
import { Card, Pill, SectionTitle } from "@/components/dashboard/ui";
import {
  completeActionPlanItem,
  dismissActionPlanItem,
  generateActionPlan,
  getActionPlan,
  reopenActionPlanItem
} from "@/lib/api-client";
import type { ActionPlanResponse } from "@/types/api";

export function ActionPlansPage() {
  const [data, setData] = useState<ActionPlanResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);

  async function loadPlan(signal?: AbortSignal) {
    setIsLoading(true);
    setError(null);
    try {
      setData(await getActionPlan(signal));
    } catch (caught) {
      if (caught instanceof DOMException && caught.name === "AbortError") return;
      setError("CrocLens could not load action plans.");
    } finally {
      if (!signal?.aborted) setIsLoading(false);
    }
  }

  useEffect(() => {
    const controller = new AbortController();
    void loadPlan(controller.signal);
    return () => controller.abort();
  }, []);

  async function runAction(action: () => Promise<unknown>) {
    setIsSaving(true);
    setError(null);
    try {
      await action();
      await loadPlan();
    } catch {
      setError("CrocLens could not update that action item.");
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <AppShell>
      {({ account, openGuide, openSidebar }) => (
        <div className="mx-auto max-w-[1180px] space-y-5">
          <DashboardHeader
            description="Turn your saved records into beginner-friendly review steps without direct buy or sell advice."
            onAskClick={openGuide}
            onMenuClick={openSidebar}
            title="Action Plans"
          />

          {error ? (
            <Card className="border-rose-200 bg-rose-50">
              <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
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

          <div className="grid gap-5 lg:grid-cols-[minmax(0,1.2fr)_minmax(320px,0.8fr)]">
            <Card>
              <SectionTitle
                eyebrow="Review queue"
                title={isLoading ? "Loading action plan" : account ? "Saved review items" : "Demo review items"}
                action={<Pill tone={account ? "green" : "gold"}>{account ? "Saved" : "Demo"}</Pill>}
              />
              <div className="space-y-3">
                {data?.items.map((item) => (
                  <article className="rounded-lg border border-emerald-900/10 bg-white p-4" key={item.id}>
                    <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
                      <div>
                        <div className="flex flex-wrap items-center gap-2">
                          <h2 className="font-bold text-croc-ink">{item.title}</h2>
                          <Pill tone={item.priority === "high" ? "coral" : item.priority === "medium" ? "gold" : "green"}>
                            {item.priority}
                          </Pill>
                          <Pill tone={item.status === "completed" ? "green" : "neutral"}>{item.status}</Pill>
                        </div>
                        <p className="mt-2 text-sm leading-6 text-stone-600">{item.description}</p>
                        <p className="mt-2 text-xs leading-5 text-stone-500">{item.safe_wording_note}</p>
                      </div>
                      {account ? (
                        <div className="flex flex-wrap gap-2">
                          {item.status === "completed" ? (
                            <button
                              className="inline-flex min-h-10 items-center gap-2 rounded-lg border border-emerald-900/10 px-3 text-sm font-semibold text-croc-moss"
                              disabled={isSaving}
                              onClick={() => void runAction(() => reopenActionPlanItem(item.id))}
                              suppressHydrationWarning
                              type="button"
                            >
                              <RotateCcw className="h-4 w-4" />
                              Reopen
                            </button>
                          ) : (
                            <button
                              className="inline-flex min-h-10 items-center gap-2 rounded-lg bg-croc-emerald px-3 text-sm font-semibold text-white"
                              disabled={isSaving}
                              onClick={() => void runAction(() => completeActionPlanItem(item.id))}
                              suppressHydrationWarning
                              type="button"
                            >
                              <CheckCircle2 className="h-4 w-4" />
                              Complete
                            </button>
                          )}
                          <button
                            className="inline-flex min-h-10 items-center gap-2 rounded-lg border border-emerald-900/10 px-3 text-sm font-semibold text-stone-600"
                            disabled={isSaving}
                            onClick={() => void runAction(() => dismissActionPlanItem(item.id))}
                            suppressHydrationWarning
                            type="button"
                          >
                            <XCircle className="h-4 w-4" />
                            Dismiss
                          </button>
                        </div>
                      ) : null}
                    </div>
                  </article>
                ))}
              </div>
            </Card>

            <div className="space-y-5">
              <Card>
                <SectionTitle eyebrow="Generate" title="Refresh review ideas" />
                <p className="text-sm leading-6 text-stone-600">
                  {account
                    ? "CrocLens generates review prompts from your saved assets, debts, and data freshness labels."
                    : "Demo visitors can preview sample action plans. Sign in to save and update your own review items."}
                </p>
                <button
                  className="mt-4 inline-flex min-h-11 w-full items-center justify-center gap-2 rounded-lg bg-croc-emerald px-4 text-sm font-semibold text-white"
                  disabled={isSaving}
                  onClick={() => void runAction(() => generateActionPlan())}
                  suppressHydrationWarning
                  type="button"
                >
                  <Sparkles className="h-4 w-4" />
                  Generate action plan
                </button>
              </Card>

              <Card>
                <SectionTitle eyebrow="Safety" title="Review, do not blindly follow" />
                <p className="text-sm leading-6 text-stone-600">
                  {data?.educational_disclaimer} CrocLens action items use “consider,” “review,” and “research” language because this product is educational software.
                </p>
                <div className="mt-4 space-y-2">
                  {data?.data_limitations.map((limitation) => (
                    <p className="rounded-lg bg-croc-cream p-3 text-xs leading-5 text-stone-600" key={limitation}>
                      {limitation}
                    </p>
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
