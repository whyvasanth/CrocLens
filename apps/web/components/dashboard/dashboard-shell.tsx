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
import Link from "next/link";

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
                  : "You are exploring a clearly labeled demo snapshot. Create an account to track your own records."
              }
              onAskClick={openGuide}
              onMenuClick={openSidebar}
              title={isAccountLoading ? "Loading your CrocLens dashboard" : `Good morning, ${firstName}`}
            />
            <ApiStatusBanner error={error} isLoading={isLoading} onRetry={refetch} />
            {!isSignedIn && !isAccountLoading ? (
              <section className="flex flex-col gap-3 rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-950 shadow-card md:flex-row md:items-center md:justify-between">
                <div>
                  <p className="font-semibold">Demo data</p>
                  <p className="mt-1 leading-6">
                    This sample dashboard is separate from real user accounts and does not save changes.
                  </p>
                </div>
                <div className="flex flex-wrap gap-2">
                  <Link className="inline-flex min-h-10 items-center rounded-lg bg-white px-3 font-semibold text-amber-950" href="/">
                    Exit demo
                  </Link>
                  <Link className="inline-flex min-h-10 items-center rounded-lg bg-croc-emerald px-3 font-semibold text-white" href="/signup">
                    Create your account
                  </Link>
                </div>
              </section>
            ) : null}
            <div className="grid gap-5 xl:grid-cols-[minmax(0,1.45fr)_minmax(340px,0.9fr)]">
              <PortfolioChart
                account={account}
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
