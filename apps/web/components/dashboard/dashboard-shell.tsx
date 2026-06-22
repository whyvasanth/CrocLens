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
      {({ account, isAccountLoading, openGuide, openSidebar }) => {
        const displayName = account?.display_name ?? "there";
        const firstName = displayName.split(" ")[0] || displayName;
        const isSignedIn = Boolean(account);

        return (
          <div className="mx-auto max-w-[1220px] space-y-5">
            <DashboardHeader
              description={
                isSignedIn
                  ? "Here is your latest financial snapshot and beginner-friendly money update."
                  : "Here is a sample whole-wealth snapshot. Log in to see your own persisted portfolio records."
              }
              onAskClick={openGuide}
              onMenuClick={openSidebar}
              title={isAccountLoading ? "Loading your CrocLens dashboard" : `Good morning, ${firstName}`}
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
        );
      }}
    </AppShell>
  );
}
