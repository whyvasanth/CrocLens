"use client";

import { FormEvent, useEffect, useState } from "react";
import { NotebookPen, RefreshCw } from "lucide-react";
import { AppShell } from "@/components/dashboard/app-shell";
import { DashboardHeader } from "@/components/dashboard/dashboard-header";
import { Card, Pill, SectionTitle } from "@/components/dashboard/ui";
import { createDecisionJournalEntry, getDecisionJournal } from "@/lib/api-client";
import type { DecisionJournalCreateRequest, DecisionJournalEntryResponse, DecisionJournalResponse, DecisionType } from "@/types/api";

const initialForm: DecisionJournalCreateRequest = {
  decision_type: "watch",
  title: "",
  asset_symbol: "",
  reason: "",
  expected_outcome: "",
  risk_considered: "",
  review_date: "2026-08-01"
};

export function DecisionJournalPage() {
  const [data, setData] = useState<DecisionJournalResponse | null>(null);
  const [previewEntry, setPreviewEntry] = useState<DecisionJournalEntryResponse | null>(null);
  const [form, setForm] = useState<DecisionJournalCreateRequest>(initialForm);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  async function loadJournal(signal?: AbortSignal) {
    setIsLoading(true);
    setError(null);
    try {
      setData(await getDecisionJournal(signal));
    } catch (caught) {
      if (caught instanceof DOMException && caught.name === "AbortError") return;
      setError("CrocLens could not load the decision journal.");
    } finally {
      if (!signal?.aborted) setIsLoading(false);
    }
  }

  useEffect(() => {
    const controller = new AbortController();
    void loadJournal(controller.signal);
    return () => controller.abort();
  }, []);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    try {
      const created = await createDecisionJournalEntry({
        ...form,
        asset_symbol: form.asset_symbol?.trim() ? form.asset_symbol : null
      });
      setPreviewEntry(created);
    } catch {
      setError("Check that every journal field has enough detail.");
    }
  }

  return (
    <AppShell>
      {({ openGuide, openSidebar }) => (
        <div className="mx-auto max-w-[1180px] space-y-5">
          <DashboardHeader
            description="Record the reason, expected outcome, risk, and review date before judging a decision."
            onAskClick={openGuide}
            onMenuClick={openSidebar}
            title="Decision Journal"
          />

          <div className="grid gap-5 lg:grid-cols-[minmax(0,1.1fr)_minmax(360px,0.9fr)]">
            <Card>
              <SectionTitle
                eyebrow="Learning loop"
                title={isLoading ? "Loading journal" : "Recorded decisions"}
                action={<Pill tone="blue">Process over outcome</Pill>}
              />
              <p className="text-sm leading-6 text-stone-600">{data?.beginner_summary}</p>
              <div className="mt-5 space-y-3">
                {[...(data?.entries ?? []), ...(previewEntry ? [previewEntry] : [])].map((entry) => (
                  <div className="rounded-lg border border-emerald-900/10 p-4" key={entry.id}>
                    <div className="flex flex-wrap items-start justify-between gap-3">
                      <div>
                        <p className="font-bold text-croc-ink">{entry.title}</p>
                        <p className="text-xs font-semibold uppercase text-croc-moss">{entry.decision_type.replaceAll("_", " ")}</p>
                      </div>
                      <Pill tone="green">{entry.status}</Pill>
                    </div>
                    <p className="mt-3 text-sm leading-6 text-stone-600">{entry.feedback_summary}</p>
                  </div>
                ))}
              </div>
            </Card>

            <Card>
              <SectionTitle eyebrow="New entry" title="Write the decision before acting" />
              <form className="space-y-3" onSubmit={onSubmit}>
                <select
                  className="min-h-11 w-full rounded-lg border border-emerald-900/10 px-3 text-sm"
                  onChange={(event) => setForm((current) => ({ ...current, decision_type: event.target.value as DecisionType }))}
                  value={form.decision_type}
                >
                  <option value="watch">Watch</option>
                  <option value="hold">Hold</option>
                  <option value="rebalance">Rebalance</option>
                  <option value="debt_payoff">Debt payoff</option>
                  <option value="retirement_contribution_change">Retirement change</option>
                </select>
                <input
                  className="min-h-11 w-full rounded-lg border border-emerald-900/10 px-3 text-sm"
                  onChange={(event) => setForm((current) => ({ ...current, title: event.target.value }))}
                  placeholder="Decision title"
                  value={form.title}
                />
                <input
                  className="min-h-11 w-full rounded-lg border border-emerald-900/10 px-3 text-sm"
                  onChange={(event) => setForm((current) => ({ ...current, asset_symbol: event.target.value }))}
                  placeholder="Symbol or topic"
                  value={form.asset_symbol ?? ""}
                />
                {(["reason", "expected_outcome", "risk_considered"] as const).map((field) => (
                  <textarea
                    className="min-h-24 w-full rounded-lg border border-emerald-900/10 p-3 text-sm"
                    key={field}
                    onChange={(event) => setForm((current) => ({ ...current, [field]: event.target.value }))}
                    placeholder={field.replaceAll("_", " ")}
                    value={form[field]}
                  />
                ))}
                <input
                  className="min-h-11 w-full rounded-lg border border-emerald-900/10 px-3 text-sm"
                  onChange={(event) => setForm((current) => ({ ...current, review_date: event.target.value }))}
                  type="date"
                  value={form.review_date}
                />
                <button
                  className="inline-flex min-h-11 w-full items-center justify-center gap-2 rounded-lg bg-croc-emerald px-4 text-sm font-semibold text-white"
                  suppressHydrationWarning
                  type="submit"
                >
                  <NotebookPen className="h-4 w-4" />
                  Preview feedback
                </button>
                {error ? (
                  <button
                    className="inline-flex min-h-10 w-full items-center justify-center gap-2 rounded-lg bg-rose-50 px-4 text-sm font-semibold text-rose-900"
                    onClick={() => void loadJournal()}
                    suppressHydrationWarning
                    type="button"
                  >
                    <RefreshCw className="h-4 w-4" />
                    {error}
                  </button>
                ) : null}
              </form>
            </Card>
          </div>
        </div>
      )}
    </AppShell>
  );
}
