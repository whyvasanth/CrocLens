import { Database, RefreshCw, ShieldCheck } from "lucide-react";
import { Card, Pill, SectionTitle } from "@/components/dashboard/ui";
import type {
  DataFreshnessResponse,
  NormalizedDataPointResponse,
  ProviderStatusResponse
} from "@/types/api";

interface ProviderStatusCardProps {
  dataFreshness: DataFreshnessResponse | null;
  isLoading: boolean;
  marketData: NormalizedDataPointResponse[];
  providers: ProviderStatusResponse[];
}

export function ProviderStatusCard({
  dataFreshness,
  isLoading,
  marketData,
  providers
}: ProviderStatusCardProps) {
  const configuredCount = providers.filter((provider) => provider.configured).length;
  const fallbackProvider = providers.find((provider) => provider.id === "croclens_sample_fallback");
  const visibleProviders = providers
    .filter((provider) => provider.id !== "croclens_sample_fallback")
    .slice(0, 5);
  const latestObservations = marketData.slice(0, 4);

  return (
    <Card>
      <SectionTitle
        eyebrow="Data provider layer"
        title="Free-first data routing"
        action={<Pill tone={fallbackProvider ? "green" : "gold"}>{dataFreshness?.mode ?? "mock_or_live"}</Pill>}
      />
      <div className="grid gap-3 md:grid-cols-3">
        <StatusMetric
          icon={Database}
          label="Providers tracked"
          value={providers.length ? String(providers.length) : isLoading ? "Loading" : "0"}
        />
        <StatusMetric
          icon={ShieldCheck}
          label="Configured now"
          value={providers.length ? String(configuredCount) : isLoading ? "Loading" : "0"}
        />
        <StatusMetric
          icon={RefreshCw}
          label="Fallback"
          value={fallbackProvider ? "Ready" : "Unavailable"}
        />
      </div>
      <div className="mt-4 flex flex-wrap gap-2">
        {visibleProviders.map((provider) => (
          <Pill
            key={provider.id}
            tone={provider.health === "configured" ? "green" : provider.health === "unconfigured" ? "gold" : "neutral"}
          >
            {provider.name}: {provider.health.replace("_", " ")}
          </Pill>
        ))}
      </div>
      <div className="mt-5 rounded-lg border border-emerald-900/10 bg-white p-4">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <div>
            <p className="text-xs font-semibold uppercase text-croc-moss">Latest provider output</p>
            <p className="mt-1 text-sm text-stone-500">
              Normalized observations fetched for the dashboard.
            </p>
          </div>
          <Pill tone={latestObservations.length ? "green" : "gold"}>
            {latestObservations.length ? `${latestObservations.length} data points` : "Waiting"}
          </Pill>
        </div>
        <div className="mt-4 grid gap-3 lg:grid-cols-4">
          {latestObservations.length ? (
            latestObservations.map((point) => (
              <ProviderObservation key={`${point.provider}-${point.symbol_or_series_id}`} point={point} />
            ))
          ) : (
            <p className="rounded-lg bg-croc-cream p-3 text-sm text-stone-500 lg:col-span-4">
              {isLoading
                ? "Loading provider output..."
                : "No provider output has loaded yet. Start the FastAPI backend, then refresh the dashboard."}
            </p>
          )}
        </div>
      </div>
      <p className="mt-4 text-xs leading-5 text-stone-500">
        Live provider failures fall back to sample data. Missing API keys are expected in local development.
      </p>
    </Card>
  );
}

interface StatusMetricProps {
  icon: typeof Database;
  label: string;
  value: string;
}

function StatusMetric({ icon: Icon, label, value }: StatusMetricProps) {
  return (
    <div className="flex items-center gap-3 rounded-lg border border-emerald-900/10 bg-croc-cream p-3">
      <span className="grid h-10 w-10 shrink-0 place-items-center rounded-lg bg-croc-mint text-croc-moss">
        <Icon className="h-4 w-4" />
      </span>
      <div>
        <p className="text-xs text-stone-500">{label}</p>
        <p className="mt-1 text-sm font-bold text-croc-ink">{value}</p>
      </div>
    </div>
  );
}

interface ProviderObservationProps {
  point: NormalizedDataPointResponse;
}

function ProviderObservation({ point }: ProviderObservationProps) {
  const isFallback = point.provider === "croclens_sample_fallback";

  return (
    <div className="rounded-lg border border-emerald-900/10 bg-croc-cream p-3">
      <div className="flex items-start justify-between gap-2">
        <div className="min-w-0">
          <p className="truncate text-sm font-semibold text-croc-ink">{labelForPoint(point)}</p>
          <p className="mt-1 truncate text-xs text-stone-500">{point.symbol_or_series_id}</p>
        </div>
        <Pill tone={isFallback ? "gold" : "green"}>{isFallback ? "sample" : "provider"}</Pill>
      </div>
      <p className="mt-3 text-xl font-bold text-croc-ink">{formatProviderValue(point)}</p>
      <p className="mt-2 truncate text-xs text-stone-500">
        {point.provider} | {point.freshness}
      </p>
    </div>
  );
}

function labelForPoint(point: NormalizedDataPointResponse) {
  const labels: Record<string, string> = {
    AGG: "Bond ETF",
    bitcoin: "Bitcoin",
    CPIAUCSL: "Inflation index",
    VOO: "S&P 500 ETF"
  };

  return labels[point.symbol_or_series_id] ?? point.symbol_or_series_id;
}

function formatProviderValue(point: NormalizedDataPointResponse) {
  if (point.currency) {
    return new Intl.NumberFormat("en-US", {
      currency: point.currency,
      maximumFractionDigits: 2,
      style: "currency"
    }).format(point.value);
  }

  if (point.source_type === "treasury_rates") {
    return `${point.value.toFixed(2)}%`;
  }

  return new Intl.NumberFormat("en-US", { maximumFractionDigits: 2 }).format(point.value);
}
