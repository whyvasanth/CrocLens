"use client";

import { AppShell } from "@/components/dashboard/app-shell";
import { ActionPlanCard } from "@/components/dashboard/action-plan-card";
import { CrossAssetComparisonCard } from "@/components/dashboard/cross-asset-comparison-card";
import { DashboardHeader } from "@/components/dashboard/dashboard-header";
import { MarketSnapshot } from "@/components/dashboard/market-snapshot";
import { PortfolioChart } from "@/components/dashboard/portfolio-chart";
import { RetirementCard, TaxInsightCard } from "@/components/dashboard/insight-cards";

export function DashboardShell() {
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
          <div className="grid gap-5 xl:grid-cols-[minmax(0,1.45fr)_minmax(340px,0.9fr)]">
            <PortfolioChart />
            <MarketSnapshot />
          </div>
          <div className="grid gap-5 xl:grid-cols-[minmax(0,1.45fr)_minmax(340px,0.9fr)]">
            <CrossAssetComparisonCard />
            <ActionPlanCard />
          </div>
          <div className="grid gap-5 lg:grid-cols-2">
            <TaxInsightCard />
            <RetirementCard />
          </div>
        </div>
      )}
    </AppShell>
  );
}
