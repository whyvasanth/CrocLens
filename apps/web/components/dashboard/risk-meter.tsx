"use client";

import { formatPercent } from "@/lib/formatters";
import { Card, SectionTitle } from "@/components/dashboard/ui";
import type { DebtImpact, ScoreItem } from "@/types/api";

interface RiskMeterProps {
  debtImpact: DebtImpact | null;
  isLoading: boolean;
  scores: ScoreItem[];
}

export function RiskMeter({ debtImpact, isLoading, scores }: RiskMeterProps) {
  return (
    <Card>
      <SectionTitle eyebrow="Calculated scorecard" title="Wealth health signals" />
      <div className="space-y-5">
        {isLoading
          ? [0, 1, 2, 3].map((item) => (
              <div key={item}>
                <div className="flex items-center justify-between gap-3">
                  <div className="h-5 w-32 animate-pulse rounded-md bg-stone-100" />
                  <div className="h-5 w-12 animate-pulse rounded-md bg-stone-100" />
                </div>
                <div className="mt-2 h-3 animate-pulse rounded-sm bg-stone-100" />
                <div className="mt-2 h-4 w-full animate-pulse rounded-md bg-stone-100" />
              </div>
            ))
          : scores.map((score) => (
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
                <p className="mt-2 text-sm leading-6 text-stone-600">{score.explanation}</p>
                <p className="mt-1 text-xs leading-5 text-stone-500">Formula: {score.formula}</p>
              </div>
            ))}
        {!isLoading && debtImpact ? (
          <div className="rounded-lg border border-emerald-900/10 bg-croc-cream p-4">
            <div className="flex items-center justify-between gap-3">
              <p className="font-semibold text-croc-ink">Debt impact</p>
              <p className="text-sm font-semibold text-croc-moss">
                {formatPercent(debtImpact.debt_to_asset_percent)}
              </p>
            </div>
            <p className="mt-2 text-sm leading-6 text-stone-600">{debtImpact.explanation}</p>
          </div>
        ) : null}
      </div>
    </Card>
  );
}
