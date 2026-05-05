"use client";

import { useState } from "react";
import { ActionPlanCard } from "@/components/dashboard/action-plan-card";
import { CrossAssetComparisonCard } from "@/components/dashboard/cross-asset-comparison-card";
import { CrocGuidePanel } from "@/components/dashboard/croc-guide-panel";
import { DashboardHeader } from "@/components/dashboard/dashboard-header";
import { MarketSnapshot } from "@/components/dashboard/market-snapshot";
import { PortfolioChart } from "@/components/dashboard/portfolio-chart";
import { RetirementCard, TaxInsightCard } from "@/components/dashboard/insight-cards";
import { Sidebar } from "@/components/dashboard/sidebar";

export function DashboardShell() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isGuideOpen, setIsGuideOpen] = useState(false);

  return (
    <div className="min-h-screen bg-croc-emerald lg:flex">
      <Sidebar isOpen={isSidebarOpen} onClose={() => setIsSidebarOpen(false)} />
      <main className="min-w-0 flex-1 bg-croc-cream p-4 md:p-6 lg:rounded-l-[28px] lg:p-7">
        <div className="mx-auto max-w-[1220px] space-y-5">
          <DashboardHeader
            onAskClick={() => setIsGuideOpen(true)}
            onMenuClick={() => setIsSidebarOpen(true)}
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
      </main>
      <CrocGuidePanel isOpen={isGuideOpen} onClose={() => setIsGuideOpen(false)} />
    </div>
  );
}
