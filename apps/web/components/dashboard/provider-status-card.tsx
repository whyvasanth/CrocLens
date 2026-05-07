import { Database, RefreshCw, ShieldCheck } from "lucide-react";
import { Card, Pill, SectionTitle } from "@/components/dashboard/ui";
import type { DataFreshnessResponse, ProviderStatusResponse } from "@/types/api";

interface ProviderStatusCardProps {
  dataFreshness: DataFreshnessResponse | null;
  isLoading: boolean;
  providers: ProviderStatusResponse[];
}

export function ProviderStatusCard({ dataFreshness, isLoading, providers }: ProviderStatusCardProps) {
  const configuredCount = providers.filter((provider) => provider.configured).length;
  const fallbackProvider = providers.find((provider) => provider.id === "croclens_sample_fallback");
  const visibleProviders = providers
    .filter((provider) => provider.id !== "croclens_sample_fallback")
    .slice(0, 5);

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
