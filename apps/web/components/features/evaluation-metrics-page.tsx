"use client";

import { useEffect, useMemo, useState } from "react";
import { AlertCircle, BarChart3, CheckCircle2, RefreshCw, ShieldCheck, TrendingUp } from "lucide-react";
import { AppShell } from "@/components/dashboard/app-shell";
import { DashboardHeader } from "@/components/dashboard/dashboard-header";
import { Card, Pill, SectionTitle } from "@/components/dashboard/ui";
import { getEvaluationMetrics } from "@/lib/api-client";
import type {
  EvaluationMetricCategory,
  EvaluationMetricResponse,
  EvaluationMetricStatus,
  EvaluationMetricsResponse
} from "@/types/api";

const categoryLabels: Record<EvaluationMetricCategory, string> = {
  ai_safety: "AI safety",
  data_quality: "Data quality",
  product: "Product",
  reliability: "Reliability"
};

const statusTone: Record<EvaluationMetricStatus, "green" | "gold" | "coral"> = {
  healthy: "green",
  needs_attention: "coral",
  watch: "gold"
};

function formatMetricValue(metric: EvaluationMetricResponse) {
  if (metric.unit === "percent") return `${metric.value.toFixed(metric.value % 1 === 0 ? 0 : 1)}%`;
  if (metric.unit === "milliseconds") return `${Math.round(metric.value)} ms`;
  if (metric.unit === "out_of_5") return `${metric.value.toFixed(1)} / 5`;
  return `${metric.value}`;
}

function progressWidth(metric: EvaluationMetricResponse) {
  if (metric.unit === "percent") return Math.min(100, Math.max(0, metric.value));
  if (metric.unit === "out_of_5") return Math.min(100, Math.max(0, (metric.value / 5) * 100));
  if (metric.unit === "milliseconds") return Math.min(100, Math.max(8, 100 - metric.value / 5));
  return Math.min(100, Math.max(8, metric.value));
}

export function EvaluationMetricsPage() {
  const [data, setData] = useState<EvaluationMetricsResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  async function loadMetrics(signal?: AbortSignal) {
    setIsLoading(true);
    setError(null);
    try {
      const response = await getEvaluationMetrics(signal);
      setData(response);
    } catch (caught) {
      if (caught instanceof DOMException && caught.name === "AbortError") return;
      setError("CrocLens could not load evaluation metrics.");
    } finally {
      if (!signal?.aborted) setIsLoading(false);
    }
  }

  useEffect(() => {
    const controller = new AbortController();
    void loadMetrics(controller.signal);
    return () => controller.abort();
  }, []);

  const groupedMetrics = useMemo(() => {
    const groups: Record<EvaluationMetricCategory, EvaluationMetricResponse[]> = {
      ai_safety: [],
      data_quality: [],
      product: [],
      reliability: []
    };

    for (const metric of data?.metrics ?? []) {
      groups[metric.category].push(metric);
    }

    return groups;
  }, [data]);

  const watchCount = data?.metrics.filter((metric) => metric.status !== "healthy").length ?? 0;

  return (
    <AppShell>
      {({ openGuide, openSidebar }) => (
        <div className="mx-auto max-w-[1180px] space-y-5">
          <DashboardHeader
            description="Track whether CrocLens is useful, clear, safe, fresh, and reliable before adding more AI."
            onAskClick={openGuide}
            onMenuClick={openSidebar}
            title="Evaluation Metrics"
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
                  onClick={() => void loadMetrics()}
                  suppressHydrationWarning
                  type="button"
                >
                  <RefreshCw className="h-4 w-4" />
                  Retry
                </button>
              </div>
            </Card>
          ) : null}

          <div className="grid gap-5 lg:grid-cols-[minmax(0,1.15fr)_minmax(320px,0.85fr)]">
            <Card>
              <SectionTitle
                eyebrow="Internal product scorecard"
                title={isLoading ? "Loading evaluation metrics" : data?.headline ?? "Evaluation metrics"}
                action={<Pill tone={watchCount > 0 ? "gold" : "green"}>{watchCount} watch items</Pill>}
              />
              <p className="text-sm leading-6 text-stone-600">
                {data?.beginner_summary ??
                  "CrocLens is preparing a local scorecard for product quality, AI safety, data quality, and reliability."}
              </p>

              <div className="mt-5 grid gap-3 sm:grid-cols-3">
                <div className="rounded-lg bg-croc-cream p-4">
                  <div className="flex items-center gap-2 text-croc-moss">
                    <TrendingUp className="h-4 w-4" />
                    <p className="text-xs font-semibold uppercase">Tracked metrics</p>
                  </div>
                  <p className="mt-2 text-2xl font-bold text-croc-ink">{data?.metrics.length ?? "--"}</p>
                </div>
                <div className="rounded-lg bg-croc-mint p-4">
                  <div className="flex items-center gap-2 text-croc-moss">
                    <ShieldCheck className="h-4 w-4" />
                    <p className="text-xs font-semibold uppercase">AI safety</p>
                  </div>
                  <p className="mt-2 text-2xl font-bold text-croc-ink">
                    {data ? formatMetricValue(data.metrics.find((metric) => metric.id === "unsafe_recommendation_rate")!) : "--"}
                  </p>
                </div>
                <div className="rounded-lg bg-sky-50 p-4">
                  <div className="flex items-center gap-2 text-sky-800">
                    <BarChart3 className="h-4 w-4" />
                    <p className="text-xs font-semibold uppercase">Confidence</p>
                  </div>
                  <p className="mt-2 text-2xl font-bold capitalize text-croc-ink">{data?.confidence ?? "--"}</p>
                </div>
              </div>
            </Card>

            <Card>
              <SectionTitle eyebrow="Quality gates" title="Before production" action={<Pill tone="blue">Free-only</Pill>} />
              <div className="space-y-3">
                {data?.quality_checks.map((check) => (
                  <div className="flex gap-3 rounded-lg border border-emerald-900/10 p-3" key={check}>
                    <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-croc-moss" />
                    <p className="text-sm leading-6 text-stone-600">{check}</p>
                  </div>
                )) ?? <p className="text-sm text-stone-600">Loading quality checks...</p>}
              </div>
            </Card>
          </div>

          <div className="grid gap-5 xl:grid-cols-2">
            {(Object.keys(groupedMetrics) as EvaluationMetricCategory[]).map((category) => (
              <Card key={category}>
                <SectionTitle eyebrow={categoryLabels[category]} title={`${categoryLabels[category]} metrics`} />
                <div className="space-y-3">
                  {groupedMetrics[category].map((metric) => (
                    <div className="rounded-lg border border-emerald-900/10 p-4" key={metric.id}>
                      <div className="flex flex-wrap items-start justify-between gap-3">
                        <div>
                          <p className="text-sm font-bold text-croc-ink">{metric.label}</p>
                          <p className="mt-1 text-sm leading-6 text-stone-600">{metric.beginner_explanation}</p>
                        </div>
                        <div className="text-right">
                          <p className="text-xl font-bold text-croc-ink">{formatMetricValue(metric)}</p>
                          <Pill tone={statusTone[metric.status]}>{metric.status.replace("_", " ")}</Pill>
                        </div>
                      </div>
                      <div className="mt-3 h-2 rounded-full bg-stone-100">
                        <div
                          className="h-2 rounded-full bg-croc-moss"
                          style={{ width: `${progressWidth(metric)}%` }}
                        />
                      </div>
                      <div className="mt-3 grid gap-2 text-xs leading-5 text-stone-500 sm:grid-cols-2">
                        <p>Target: {metric.target}</p>
                        <p>Sample size: {metric.sample_size}</p>
                        <p className="sm:col-span-2">Measured by: {metric.how_measured}</p>
                      </div>
                    </div>
                  ))}
                  {!isLoading && groupedMetrics[category].length === 0 ? (
                    <p className="text-sm text-stone-600">No metrics yet for this category.</p>
                  ) : null}
                </div>
              </Card>
            ))}
          </div>

          <div className="grid gap-5 lg:grid-cols-2">
            <Card>
              <SectionTitle eyebrow="Recommended reviews" title="What to inspect next" />
              <ul className="space-y-2 text-sm leading-6 text-stone-600">
                {data?.recommended_reviews.map((review) => <li key={review}>{review}</li>) ?? null}
              </ul>
            </Card>
            <Card>
              <SectionTitle eyebrow="Limitations" title="What this does not prove" />
              <ul className="space-y-2 text-sm leading-6 text-stone-600">
                {data?.data_limitations.map((limitation) => <li key={limitation}>{limitation}</li>) ?? null}
              </ul>
              <p className="mt-4 text-xs leading-5 text-stone-500">{data?.educational_disclaimer}</p>
            </Card>
          </div>
        </div>
      )}
    </AppShell>
  );
}
