"use client";

import { scoreItems } from "@/lib/mock-dashboard-data";
import { formatPercent } from "@/lib/formatters";
import { Card, SectionTitle } from "@/components/dashboard/ui";

export function RiskMeter() {
  return (
    <Card>
      <SectionTitle eyebrow="Scorecard" title="Wealth health signals" />
      <div className="space-y-5">
        {scoreItems.map((score) => (
          <div key={score.label}>
            <div className="flex items-center justify-between gap-3">
              <p className="font-semibold text-croc-ink">{score.label}</p>
              <p className="text-sm font-semibold text-croc-moss">
                {formatPercent(score.value)}
              </p>
            </div>
            <div className="mt-2 h-3 overflow-hidden rounded-sm bg-stone-100">
              <div
                className="h-full rounded-sm bg-croc-moss"
                style={{ width: `${score.value}%` }}
              />
            </div>
            <p className="mt-2 text-sm leading-6 text-stone-600">{score.description}</p>
          </div>
        ))}
      </div>
    </Card>
  );
}

