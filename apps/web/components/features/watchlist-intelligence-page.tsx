"use client";

import { FormEvent, useEffect, useState } from "react";
import { Bell, RefreshCw, ShieldAlert, Sparkles } from "lucide-react";
import { AppShell } from "@/components/dashboard/app-shell";
import { DashboardHeader } from "@/components/dashboard/dashboard-header";
import { Card, Pill, SectionTitle } from "@/components/dashboard/ui";
import { createWatchlistItem, getWatchlist } from "@/lib/api-client";
import type { WatchlistAssetType, WatchlistCreateRequest, WatchlistItemResponse, WatchlistResponse } from "@/types/api";

const initialForm: WatchlistCreateRequest = {
  symbol: "",
  name: "",
  asset_type: "etf",
  why_watching: ""
};

export function WatchlistIntelligencePage() {
  const [data, setData] = useState<WatchlistResponse | null>(null);
  const [previewItem, setPreviewItem] = useState<WatchlistItemResponse | null>(null);
  const [form, setForm] = useState<WatchlistCreateRequest>(initialForm);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  async function loadWatchlist(signal?: AbortSignal) {
    setIsLoading(true);
    setError(null);
    try {
      setData(await getWatchlist(signal));
    } catch (caught) {
      if (caught instanceof DOMException && caught.name === "AbortError") return;
      setError("CrocLens could not load watchlist intelligence.");
    } finally {
      if (!signal?.aborted) setIsLoading(false);
    }
  }

  useEffect(() => {
    const controller = new AbortController();
    void loadWatchlist(controller.signal);
    return () => controller.abort();
  }, []);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    try {
      setPreviewItem(await createWatchlistItem(form));
    } catch {
      setError("Add a symbol, name, and a clear reason you are watching it.");
    }
  }

  const items = [...(data?.items ?? []), ...(previewItem ? [previewItem] : [])];

  return (
    <AppShell>
      {({ openGuide, openSidebar }) => (
        <div className="mx-auto max-w-[1180px] space-y-5">
          <DashboardHeader
            description="Track assets, markets, and research reasons without treating the list as a buy signal."
            onAskClick={openGuide}
            onMenuClick={openSidebar}
            title="Watchlist Intelligence"
          />

          <div className="grid gap-5 lg:grid-cols-[minmax(0,1.15fr)_minmax(360px,0.85fr)]">
            <Card>
              <SectionTitle
                eyebrow="Research queue"
                title={isLoading ? "Loading watchlist" : "Items you are watching"}
                action={<Pill tone="green">Research only</Pill>}
              />
              <p className="text-sm leading-6 text-stone-600">{data?.beginner_summary}</p>
              <div className="mt-5 grid gap-3 sm:grid-cols-2">
                {items.map((item) => (
                  <div className="rounded-lg border border-emerald-900/10 p-4" key={item.id}>
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <p className="text-lg font-bold text-croc-ink">{item.symbol}</p>
                        <p className="text-sm text-stone-600">{item.name}</p>
                      </div>
                      <Pill tone="blue">{item.asset_type.replaceAll("_", " ")}</Pill>
                    </div>
                    <p className="mt-3 text-sm font-semibold text-croc-moss">{item.why_watching}</p>
                    <p className="mt-2 text-sm leading-6 text-stone-600">{item.ai_summary}</p>
                    <div className="mt-3 flex gap-2 text-xs font-semibold text-stone-600">
                      <ShieldAlert className="h-4 w-4 text-amber-700" />
                      {item.risk_notes[0]}
                    </div>
                  </div>
                ))}
              </div>
            </Card>

            <div className="space-y-5">
              <Card>
                <SectionTitle eyebrow="Add research item" title="Why are you watching it?" />
                <form className="space-y-3" onSubmit={onSubmit}>
                  <input
                    className="min-h-11 w-full rounded-lg border border-emerald-900/10 px-3 text-sm"
                    onChange={(event) => setForm((current) => ({ ...current, symbol: event.target.value }))}
                    placeholder="Symbol or market"
                    value={form.symbol}
                  />
                  <input
                    className="min-h-11 w-full rounded-lg border border-emerald-900/10 px-3 text-sm"
                    onChange={(event) => setForm((current) => ({ ...current, name: event.target.value }))}
                    placeholder="Name"
                    value={form.name}
                  />
                  <select
                    className="min-h-11 w-full rounded-lg border border-emerald-900/10 px-3 text-sm"
                    onChange={(event) => setForm((current) => ({ ...current, asset_type: event.target.value as WatchlistAssetType }))}
                    value={form.asset_type}
                  >
                    <option value="stock">Stock</option>
                    <option value="etf">ETF</option>
                    <option value="crypto">Crypto</option>
                    <option value="real_estate_market">Real estate market</option>
                    <option value="bond">Bond</option>
                    <option value="treasury">Treasury</option>
                    <option value="other">Other</option>
                  </select>
                  <textarea
                    className="min-h-28 w-full rounded-lg border border-emerald-900/10 p-3 text-sm"
                    onChange={(event) => setForm((current) => ({ ...current, why_watching: event.target.value }))}
                    placeholder="Why I am watching this"
                    value={form.why_watching}
                  />
                  <button
                    className="inline-flex min-h-11 w-full items-center justify-center gap-2 rounded-lg bg-croc-emerald px-4 text-sm font-semibold text-white"
                    suppressHydrationWarning
                    type="submit"
                  >
                    <Bell className="h-4 w-4" />
                    Preview watch note
                  </button>
                  {error ? (
                    <button
                      className="inline-flex min-h-10 w-full items-center justify-center gap-2 rounded-lg bg-rose-50 px-4 text-sm font-semibold text-rose-900"
                      onClick={() => void loadWatchlist()}
                      suppressHydrationWarning
                      type="button"
                    >
                      <RefreshCw className="h-4 w-4" />
                      {error}
                    </button>
                  ) : null}
                </form>
              </Card>

              <Card>
                <SectionTitle eyebrow="Research prompts" title="Before deciding" />
                <div className="space-y-3">
                  {data?.safe_research_prompts.map((prompt) => (
                    <div className="flex gap-3 rounded-lg bg-croc-cream p-3" key={prompt}>
                      <Sparkles className="mt-0.5 h-4 w-4 shrink-0 text-croc-moss" />
                      <p className="text-sm leading-6 text-stone-600">{prompt}</p>
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
