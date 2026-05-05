import { Check, ChevronRight } from "lucide-react";
import { actionItems } from "@/lib/mock-dashboard-data";
import { Card, Pill, SectionTitle } from "@/components/dashboard/ui";

const priorityTone = {
  High: "coral",
  Medium: "gold",
  Low: "green"
} as const;

export function ActionPlanCard() {
  return (
    <Card>
      <SectionTitle eyebrow="AI action plan" title="Consider reviewing next" />
      <div className="space-y-3">
        {actionItems.map((item) => (
          <div key={item.title} className="flex gap-3">
            <span
              className={
                item.isDone
                  ? "mt-1 grid h-7 w-7 shrink-0 place-items-center rounded-full bg-croc-moss text-white"
                  : "mt-1 h-7 w-7 shrink-0 rounded-full border border-stone-300 bg-white"
              }
            >
              {item.isDone ? <Check className="h-4 w-4" /> : null}
            </span>
            <div className="min-w-0 flex-1 border-b border-emerald-900/10 pb-3 last:border-0">
              <div className="flex items-start justify-between gap-3">
                <h3 className="font-semibold text-croc-ink">{item.title}</h3>
                <Pill tone={priorityTone[item.priority]}>{item.priority}</Pill>
              </div>
              <p className="mt-1 text-sm leading-6 text-stone-600">{item.body}</p>
            </div>
          </div>
        ))}
      </div>
      <button className="mt-5 flex min-h-11 w-full items-center justify-center gap-2 rounded-lg bg-croc-mint px-4 text-sm font-semibold text-croc-moss transition hover:bg-croc-lime/70">
        Go to Action Plans
        <ChevronRight className="h-4 w-4" />
      </button>
    </Card>
  );
}
