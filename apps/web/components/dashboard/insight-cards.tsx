import { Landmark, ReceiptText, ShieldAlert } from "lucide-react";
import { portfolioSummary, retirementProgress } from "@/lib/mock-dashboard-data";
import { Card, Pill, SectionTitle } from "@/components/dashboard/ui";

export function TaxInsightCard() {
  return (
    <Card>
      <SectionTitle eyebrow="Tax-aware insight" title="Holding period check" />
      <div className="grid gap-4 sm:grid-cols-[140px_1fr] sm:items-center">
        <div className="grid h-32 w-full place-items-center rounded-lg bg-croc-mint text-croc-moss">
          <ReceiptText className="h-12 w-12" />
        </div>
        <div>
          <p className="text-sm text-stone-600">Potential tax-aware review</p>
          <p className="mt-1 text-3xl font-bold text-croc-moss">$1,240</p>
          <p className="text-sm leading-6 text-stone-600">
            Some taxable holdings may be near a long-term holding period. Consider reviewing tax lots before making changes.
          </p>
          <div className="mt-3 flex flex-wrap gap-2">
            <Pill tone="gold">Educational</Pill>
            <Pill>{portfolioSummary.confidence} confidence</Pill>
          </div>
        </div>
      </div>
    </Card>
  );
}

export function RetirementCard() {
  const progress = Math.round((retirementProgress.current / retirementProgress.goal) * 100);

  return (
    <Card>
      <SectionTitle eyebrow="Retirement" title="401(k) progress" />
      <div className="grid gap-4 sm:grid-cols-[150px_1fr] sm:items-center">
        <div className="relative grid h-36 w-36 place-items-center rounded-full bg-croc-mint">
          <div
            className="absolute inset-0 rounded-full"
            style={{
              background: `conic-gradient(#0d5c49 ${progress * 3.6}deg, #e7efe9 0deg)`
            }}
          />
          <div className="relative grid h-24 w-24 place-items-center rounded-full bg-white text-center">
            <div>
              <p className="text-2xl font-bold text-croc-ink">{progress}%</p>
              <p className="text-xs text-stone-600">On track</p>
            </div>
          </div>
        </div>
        <div>
          <div className="flex items-center gap-2 text-croc-moss">
            <Landmark className="h-5 w-5" />
            <p className="text-sm font-semibold">{retirementProgress.contributionRate} contribution</p>
          </div>
          <p className="mt-3 text-3xl font-bold text-croc-ink">{progress}%</p>
          <p className="text-sm text-stone-600">of your current milestone</p>
          <p className="mt-3 text-sm leading-6 text-stone-600">{retirementProgress.matchStatus}</p>
        </div>
      </div>
    </Card>
  );
}

export function SafetyNoticeCard() {
  return (
    <Card className="bg-croc-ink text-white">
      <div className="flex gap-3">
        <span className="grid h-11 w-11 shrink-0 place-items-center rounded-lg bg-white/10 text-croc-lime">
          <ShieldAlert className="h-5 w-5" />
        </span>
        <div>
          <h2 className="font-semibold">Data limitations</h2>
          <p className="mt-2 text-sm leading-6 text-emerald-50">
            {portfolioSummary.limitation}
          </p>
        </div>
      </div>
    </Card>
  );
}
