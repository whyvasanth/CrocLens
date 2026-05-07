import { ArrowDownRight, ArrowRight, ArrowUpRight } from "lucide-react";
import { marketSnapshot } from "@/lib/mock-dashboard-data";
import { Card, SectionTitle } from "@/components/dashboard/ui";
import type { MarketObservationResponse, TrendDirection } from "@/types/api";

interface MarketSnapshotProps {
  isLoading?: boolean;
  marketData: MarketObservationResponse[];
}

interface SnapshotDisplayItem {
  change: string;
  direction: TrendDirection;
  label: string;
  note: string;
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

export function MarketSnapshot({ isLoading = false, marketData }: MarketSnapshotProps) {
  const realDataItems = marketData.map(mapMarketObservationToSnapshotItem);
  const items = realDataItems.length > 0 ? realDataItems : marketSnapshot;
  const hasRealData = realDataItems.length > 0;
  const footer = hasRealData
    ? `Real public Treasury data as of ${formatShortDate(marketData[0].as_of)}`
    : "Sample fallback until a free public source is connected";

  return (
    <Card>
      <SectionTitle
        eyebrow="Market snapshot"
        title="Today at a glance"
        action={<a href="#" className="text-sm font-semibold text-croc-moss">View more</a>}
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
        {isLoading && !hasRealData ? "Loading public market context..." : footer}
      </p>
    </Card>
  );
}

function mapMarketObservationToSnapshotItem(record: MarketObservationResponse): SnapshotDisplayItem {
  return {
    change: formatObservationChange(record),
    direction: record.trend,
    label: record.name.replace(" Treasury Yield", ""),
    note: "Official Treasury yield curve context",
    value: formatObservationValue(record)
  };
}

function formatObservationValue(record: MarketObservationResponse) {
  if (record.unit === "percent" || record.metric_type === "yield" || record.metric_type === "rate") {
    return `${record.value.toFixed(2)}%`;
  }

  if (record.currency) {
    return new Intl.NumberFormat("en-US", {
      currency: record.currency,
      maximumFractionDigits: 2,
      style: "currency"
    }).format(record.value);
  }

  return new Intl.NumberFormat("en-US", { maximumFractionDigits: 2 }).format(record.value);
}

function formatObservationChange(record: MarketObservationResponse) {
  if (record.change_percent === null) {
    return "New";
  }

  if (record.change_percent === 0) {
    return "Flat";
  }

  const sign = record.change_percent > 0 ? "+" : "";

  if (record.unit === "percent" || record.metric_type === "yield" || record.metric_type === "rate") {
    return `${sign}${record.change_percent.toFixed(2)} pp`;
  }

  return `${sign}${record.change_percent.toFixed(2)}%`;
}

function formatShortDate(value: string) {
  return new Intl.DateTimeFormat("en-US", {
    day: "numeric",
    month: "short",
    timeZone: "UTC",
    year: "numeric"
  }).format(new Date(value));
}
