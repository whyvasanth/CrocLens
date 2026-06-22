import { Check, ChevronRight } from "lucide-react";
import Link from "next/link";
import { Card, Pill, SectionTitle } from "@/components/dashboard/ui";
import type { ActionPlanResponse } from "@/types/api";

const priorityTone = {
  high: "coral",
  medium: "gold",
  low: "green"
} as const;

interface ActionPlanCardProps {
  actionPlan: ActionPlanResponse | null;
  isLoading: boolean;
}

export function ActionPlanCard({ actionPlan, isLoading }: ActionPlanCardProps) {
  return (
    <Card>
      <SectionTitle
        eyebrow="AI action plan"
        title="Consider reviewing next"
        action={actionPlan ? <Pill>{actionPlan.confidence} confidence</Pill> : null}
      />
      <div className="space-y-3">
        {isLoading
          ? [0, 1].map((item) => (
              <div className="flex gap-3" key={item}>
                <span className="mt-1 h-7 w-7 shrink-0 animate-pulse rounded-full bg-stone-100" />
                <div className="min-w-0 flex-1 space-y-2 pb-3">
                  <div className="h-5 w-44 animate-pulse rounded-md bg-stone-100" />
                  <div className="h-4 w-full animate-pulse rounded-md bg-stone-100" />
                </div>
              </div>
            ))
          : actionPlan?.items.map((item) => {
              const isDone = item.status === "completed";

              return (
                <div key={item.id} className="flex gap-3">
                  <span
                    className={
                      isDone
                        ? "mt-1 grid h-7 w-7 shrink-0 place-items-center rounded-full bg-croc-moss text-white"
                        : "mt-1 h-7 w-7 shrink-0 rounded-full border border-stone-300 bg-white"
                    }
                  >
                    {isDone ? <Check className="h-4 w-4" /> : null}
                  </span>
                  <div className="min-w-0 flex-1 border-b border-emerald-900/10 pb-3 last:border-0">
                    <div className="flex items-start justify-between gap-3">
                      <h3 className="font-semibold text-croc-ink">{item.title}</h3>
                      <Pill tone={priorityTone[item.priority]}>{item.priority}</Pill>
                    </div>
                    <p className="mt-1 text-sm leading-6 text-stone-600">{item.description}</p>
                  </div>
                </div>
              );
            })}
      </div>
      {!isLoading && actionPlan ? (
        <p className="mt-4 text-xs leading-5 text-stone-500">
          {actionPlan.educational_disclaimer} {actionPlan.data_limitations[0]}
        </p>
      ) : null}
      <Link
        href="/action-plans"
        className="mt-5 flex min-h-11 w-full items-center justify-center gap-2 rounded-lg bg-croc-mint px-4 text-sm font-semibold text-croc-moss transition hover:bg-croc-lime/70"
      >
        Go to Action Plans
        <ChevronRight className="h-4 w-4" />
      </Link>
    </Card>
  );
}
