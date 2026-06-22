"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { AlertCircle, ArrowDownRight, ArrowRight, ArrowUpRight, RefreshCw } from "lucide-react";
import { getMarketSnapshot } from "@/lib/api-client";
import { formatCurrency } from "@/lib/formatters";
import { Card, Pill, SectionTitle } from "@/components/dashboard/ui";
import type { MarketSnapshotResponse } from "@/types/api";

const icons = {
  up: ArrowUpRight,
  down: ArrowDownRight,
  flat: ArrowRight
};

const classes = {
  up: "bg-croc-mint text-croc-moss",
  down: "bg-rose-100 text-rose-800",
  flat: "bg-amber-100 text-amber-800"
};

function formatMarketValue(value: number, unit: string, currency: string | null) {
  if (currency === "USD") {
    return formatCurrency(value);
  }

  if (unit === "%") {
    return `${value.toFixed(2)}%`;
  }

  return `${value.toLocaleString()}${unit ? ` ${unit}` : ""}`;
}

export function MarketSnapshot() {
  const [data, setData] = useState<MarketSnapshotResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    const controller = new AbortController();
    setIsLoading(true);
    setError(null);

    getMarketSnapshot(controller.signal)
      .then(setData)
      .catch((caught) => {
        if (controller.signal.aborted) {
          return;
        }

        setError(caught instanceof Error ? caught.message : "Market context is unavailable right now.");
      })
      .finally(() => {
        if (!controller.signal.aborted) {
          setIsLoading(false);
        }
      });

    return () => controller.abort();
  }, [reloadKey]);

  return (
    <Card>
      <SectionTitle
        eyebrow="Market snapshot"
        title="Latest available context"
        action={<Link href="/market-news" className="text-sm font-semibold text-croc-moss">View more</Link>}
      />

      {isLoading ? (
        <div className="space-y-3" aria-live="polite">
          {[0, 1, 2, 3].map((item) => (
            <div className="flex items-center gap-3" key={item}>
              <span className="h-10 w-10 animate-pulse rounded-full bg-stone-100" />
              <div className="min-w-0 flex-1 space-y-2">
                <div className="h-5 w-32 animate-pulse rounded-md bg-stone-100" />
                <div className="h-4 w-48 animate-pulse rounded-md bg-stone-100" />
              </div>
              <div className="h-8 w-20 animate-pulse rounded-md bg-stone-100" />
            </div>
          ))}
        </div>
      ) : error ? (
        <div className="rounded-lg border border-rose-200 bg-rose-50 p-4" role="status">
          <div className="flex gap-3">
            <AlertCircle className="mt-0.5 h-4 w-4 shrink-0 text-rose-700" />
            <div className="min-w-0 flex-1">
              <p className="text-sm font-semibold text-rose-900">Market context could not load</p>
              <p className="mt-1 text-sm leading-6 text-rose-800">{error}</p>
            </div>
          </div>
          <button
            className="mt-3 inline-flex min-h-10 items-center gap-2 rounded-lg bg-white px-3 text-sm font-semibold text-rose-900"
            onClick={() => setReloadKey((key) => key + 1)}
            suppressHydrationWarning
            type="button"
          >
            <RefreshCw className="h-4 w-4" />
            Retry
          </button>
        </div>
      ) : data?.items.length ? (
        <>
          <div className="mb-3 flex flex-wrap gap-2">
            <Pill tone={data.is_sample_data ? "gold" : data.data_quality === "stale" ? "gold" : "green"}>
              {data.is_sample_data ? "Demo market data" : data.data_quality}
            </Pill>
            <Pill tone="neutral">{data.provider_status}</Pill>
          </div>
          <div className="divide-y divide-emerald-900/10">
            {data.items.map((item) => {
              const direction =
                item.change_percent === null
                  ? "flat"
                  : item.change_percent > 0
                    ? "up"
                    : item.change_percent < 0
                      ? "down"
                      : "flat";
              const Icon = icons[direction];
              const changeLabel =
                item.change_percent === null
                  ? "No recent change"
                  : `${item.change_percent > 0 ? "+" : ""}${item.change_percent.toFixed(2)}%`;

              return (
                <div key={`${item.symbol}-${item.metric_type}`} className="flex items-center gap-3 py-3 first:pt-0 last:pb-0">
                  <span
                    className={`grid h-10 w-10 shrink-0 place-items-center rounded-full ${classes[direction]}`}
                    aria-hidden="true"
                  >
                    <Icon className="h-4 w-4" />
                  </span>
                  <div className="min-w-0 flex-1">
                    <p className="font-semibold text-croc-ink">{item.name}</p>
                    <p className="mt-1 truncate text-xs text-stone-500">
                      {item.is_stale ? "Stale data" : item.is_sample_data ? "Demo data" : "Latest provider data"} from {item.source_name}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="font-semibold text-croc-ink">
                      {formatMarketValue(item.value, item.unit, item.currency)}
                    </p>
                    <p
                      className={
                        direction === "down"
                          ? "mt-1 text-sm font-semibold text-rose-600"
                          : "mt-1 text-sm font-semibold text-croc-moss"
                      }
                    >
                      <span className="sr-only">{direction === "down" ? "Down " : direction === "up" ? "Up " : ""}</span>
                      {changeLabel}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
          <p className="mt-4 text-xs leading-5 text-stone-500">
            {data.data_limitations[0]} {data.educational_disclaimer}
          </p>
        </>
      ) : (
        <div className="rounded-lg border border-emerald-900/10 bg-croc-cream p-4" role="status">
          <p className="text-sm font-semibold text-croc-ink">No market context available</p>
          <p className="mt-2 text-sm leading-6 text-stone-600">
            CrocLens could not load a market snapshot. No sample data was substituted for a failed live provider.
          </p>
        </div>
      )}
    </Card>
  );
}
