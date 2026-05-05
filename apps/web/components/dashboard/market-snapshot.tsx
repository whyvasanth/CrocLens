import { ArrowDownRight, ArrowRight, ArrowUpRight } from "lucide-react";
import { marketSnapshot } from "@/lib/mock-dashboard-data";
import { Card, SectionTitle } from "@/components/dashboard/ui";

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

export function MarketSnapshot() {
  return (
    <Card>
      <SectionTitle
        eyebrow="Market snapshot"
        title="Today at a glance"
        action={<a href="#" className="text-sm font-semibold text-croc-moss">View more</a>}
      />
      <div className="divide-y divide-emerald-900/10">
        {marketSnapshot.map((item) => {
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
      <p className="mt-4 text-xs text-stone-500">Data as of sample Phase 1 dataset</p>
    </Card>
  );
}
