"use client";

import { AppShell } from "@/components/dashboard/app-shell";
import { ActionPlanCard } from "@/components/dashboard/action-plan-card";
import { ApiStatusBanner } from "@/components/dashboard/api-status-banner";
import { CrossAssetComparisonCard } from "@/components/dashboard/cross-asset-comparison-card";
import { DashboardHeader } from "@/components/dashboard/dashboard-header";
import { MarketSnapshot } from "@/components/dashboard/market-snapshot";
import { PortfolioChart } from "@/components/dashboard/portfolio-chart";
import { RiskMeter } from "@/components/dashboard/risk-meter";
import { RetirementCard, TaxInsightCard } from "@/components/dashboard/insight-cards";
import { useDashboardData } from "@/hooks/use-dashboard-data";

export function DashboardShell() {
  const { data, error, isLoading, refetch } = useDashboardData();

  return (
    <AppShell>
      {({ openGuide, openSidebar }) => (
        <div className="mx-auto max-w-[1220px] space-y-5">
          <DashboardHeader
            description="Here is your whole-wealth snapshot and beginner-friendly money update for today."
            onAskClick={openGuide}
            onMenuClick={openSidebar}
            title="Good morning, Maya"
          />
          <ApiStatusBanner error={error} isLoading={isLoading} onRetry={refetch} />
          <div className="grid gap-5 xl:grid-cols-[minmax(0,1.45fr)_minmax(340px,0.9fr)]">
            <PortfolioChart
              isLoading={isLoading}
              portfolio={data?.portfolio ?? null}
            />
            <MarketSnapshot />
          </div>
          <div className="grid gap-5 xl:grid-cols-[minmax(0,1.45fr)_minmax(340px,0.9fr)]">
            <CrossAssetComparisonCard assets={data?.assets ?? []} isLoading={isLoading} />
            <ActionPlanCard actionPlan={data?.actionPlan ?? null} isLoading={isLoading} />
          </div>
          <div className="grid gap-5 xl:grid-cols-[minmax(0,1.2fr)_minmax(280px,0.8fr)]">
            <RiskMeter
              debtImpact={data?.portfolio.debt_impact ?? null}
              isLoading={isLoading}
              scores={data?.portfolio.scores ?? []}
            />
            <div className="grid gap-5">
              <TaxInsightCard />
              <RetirementCard />
            </div>
          </div>
        </div>
      )}
    </AppShell>
  );
}
