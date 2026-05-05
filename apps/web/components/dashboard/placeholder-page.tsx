"use client";

import { ArrowRight, CheckCircle2, Construction, Lightbulb } from "lucide-react";
import { AppShell } from "@/components/dashboard/app-shell";
import { DashboardHeader } from "@/components/dashboard/dashboard-header";
import { Card, Pill, SectionTitle } from "@/components/dashboard/ui";
import type { ProductPageConfig } from "@/lib/page-config";

interface PlaceholderPageProps {
  config: ProductPageConfig;
}

export function PlaceholderPage({ config }: PlaceholderPageProps) {
  return (
    <AppShell>
      {({ openGuide, openSidebar }) => (
        <div className="mx-auto max-w-[1180px] space-y-5">
          <DashboardHeader
            description={config.description}
            onAskClick={openGuide}
            onMenuClick={openSidebar}
            title={config.title}
          />

          <div className="grid gap-5 lg:grid-cols-[minmax(0,1.35fr)_minmax(320px,0.85fr)]">
            <Card>
              <SectionTitle
                eyebrow={config.stage}
                title="What will live here"
                action={<Pill tone="green">Planned slice</Pill>}
              />
              <div className="grid gap-3 sm:grid-cols-2">
                {config.focusAreas.map((area) => (
                  <div
                    className="flex min-h-20 gap-3 rounded-lg border border-emerald-900/10 bg-croc-cream p-4"
                    key={area}
                  >
                    <CheckCircle2 className="mt-0.5 h-5 w-5 shrink-0 text-croc-moss" />
                    <p className="text-sm font-medium leading-6 text-croc-ink">{area}</p>
                  </div>
                ))}
              </div>
            </Card>

            <div className="space-y-5">
              <Card>
                <SectionTitle eyebrow="Build status" title="Coming in a later vertical slice" />
                <div className="flex gap-3">
                  <span className="grid h-11 w-11 shrink-0 place-items-center rounded-lg bg-croc-mint text-croc-moss">
                    <Construction className="h-5 w-5" />
                  </span>
                  <div>
                    <p className="text-sm leading-6 text-stone-600">{config.nextMilestone}</p>
                    <button
                      className="mt-4 inline-flex min-h-10 items-center gap-2 rounded-lg bg-croc-emerald px-4 text-sm font-semibold text-white"
                      onClick={openGuide}
                      suppressHydrationWarning
                      type="button"
                    >
                      Ask Croc Guide
                      <ArrowRight className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              </Card>

              <Card>
                <SectionTitle eyebrow="Beginner note" title="Plain-language explanation" />
                <div className="flex gap-3">
                  <span className="grid h-11 w-11 shrink-0 place-items-center rounded-lg bg-amber-100 text-amber-800">
                    <Lightbulb className="h-5 w-5" />
                  </span>
                  <p className="text-sm leading-6 text-stone-600">{config.beginnerNote}</p>
                </div>
              </Card>
            </div>
          </div>
        </div>
      )}
    </AppShell>
  );
}
