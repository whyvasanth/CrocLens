import { ArrowDownRight, ArrowRight, ArrowUpRight } from "lucide-react";
import { metricCards } from "@/lib/mock-dashboard-data";
import { Card } from "@/components/dashboard/ui";

const trendIcons = {
  up: ArrowUpRight,
  down: ArrowDownRight,
  flat: ArrowRight
};

const trendClasses = {
  up: "text-croc-moss bg-croc-mint",
  down: "text-sky-800 bg-sky-100",
  flat: "text-stone-700 bg-stone-100"
};

export function MetricCards() {
  return (
    <div className="grid gap-4 md:grid-cols-3">
      {metricCards.map((metric) => {
        const Icon = trendIcons[metric.direction];

        return (
          <Card key={metric.label}>
            <div className="flex items-start justify-between gap-3">
              <div>
                <p className="text-sm font-medium text-stone-600">{metric.label}</p>
                <p className="mt-2 text-2xl font-bold text-croc-ink">{metric.value}</p>
              </div>
              <span
                className={`grid h-9 w-9 place-items-center rounded-lg ${trendClasses[metric.direction]}`}
              >
                <Icon className="h-4 w-4" />
              </span>
            </div>
            <p className="mt-3 text-sm text-stone-600">{metric.helper}</p>
            <p className="mt-4 text-sm font-semibold text-croc-moss">{metric.trend}</p>
          </Card>
        );
      })}
    </div>
  );
}

