import { ArrowDownRight, ArrowRight, ArrowUpRight } from "lucide-react";
import { marketSnapshot } from "@/lib/mock-dashboard-data";
import { Card, Pill, SectionTitle } from "@/components/dashboard/ui";
import type { NormalizedDataPointResponse } from "@/types/api";

interface MarketSnapshotProps {
  isLoading?: boolean;
  marketData?: NormalizedDataPointResponse[];
}

interface SnapshotItem {
  change: string;
  direction: "up" | "down" | "flat";
  label: string;
  note: string;
  provider: string;
  value: string;
}

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

export function MarketSnapshot({ isLoading = false, marketData = [] }: MarketSnapshotProps) {
  const providerItems = marketData.map(mapProviderPointToSnapshotItem);
  const items: SnapshotItem[] = providerItems.length
    ? providerItems
    : marketSnapshot.map((item) => ({
        ...item,
        provider: "frontend_sample"
      }));
  const isProviderBacked = providerItems.length > 0;

  return (
    <Card>
      <SectionTitle
        eyebrow={isProviderBacked ? "Provider-backed snapshot" : "Market snapshot"}
        title="Today at a glance"
        action={<Pill tone={isProviderBacked ? "green" : "gold"}>{isProviderBacked ? "API data" : "Sample"}</Pill>}
      />
      <div className="divide-y divide-emerald-900/10">
        {items.map((item) => {
          const Icon = icons[item.direction];

          return (
            <div key={item.label} className="flex items-center gap-3 py-3 first:pt-0 last:pb-0">
              <span
                className={`grid h-10 w-10 shrink-0 place-items-center rounded-full ${classes[item.direction]}`}
              >
                <Icon className="h-4 w-4" />
              </span>
              <div className="min-w-0 flex-1">
                <p className="font-semibold text-croc-ink">{item.label}</p>
                <p className="mt-1 truncate text-xs text-stone-500">{item.note}</p>
              </div>
              <div className="text-right">
                <p className="font-semibold text-croc-ink">{item.value}</p>
                <p
                  className={
                    item.direction === "down"
                      ? "mt-1 text-sm font-semibold text-rose-600"
                      : "mt-1 text-sm font-semibold text-croc-moss"
                  }
                >
                  {item.change}
                </p>
              </div>
            </div>
          );
        })}
      </div>
      <p className="mt-4 text-xs text-stone-500">
        {isLoading
          ? "Loading provider data..."
          : isProviderBacked
            ? "Provider layer data shown with live-or-sample fallback labels."
            : "Data as of sample Phase 1 dataset"}
      </p>
    </Card>
  );
}

function mapProviderPointToSnapshotItem(point: NormalizedDataPointResponse): SnapshotItem {
  return {
    change: point.provider === "croclens_sample_fallback" ? "Fallback" : point.confidence,
    direction: "flat",
    label: labelForPoint(point),
    note: `${point.provider} | ${point.freshness}`,
    provider: point.provider,
    value: formatProviderValue(point)
  };
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
