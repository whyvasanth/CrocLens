import { Bell, ChevronRight, Lightbulb, Send, ShieldCheck, Star, MoreHorizontal } from "lucide-react";
import { guideInsights, portfolioSummary } from "@/lib/mock-dashboard-data";
import { CrocMascot } from "@/components/dashboard/croc-mascot";
import { Pill } from "@/components/dashboard/ui";

const insightStyles = {
  green: {
    icon: Lightbulb,
    className: "bg-croc-moss text-white",
    titleClass: "text-croc-moss"
  },
  gold: {
    icon: Star,
    className: "bg-amber-500 text-white",
    titleClass: "text-amber-700"
  },
  blue: {
    icon: ShieldCheck,
    className: "bg-sky-600 text-white",
    titleClass: "text-sky-700"
  }
};

export function CrocGuidePanel() {
  return (
    <aside className="rounded-lg border border-emerald-900/10 bg-white p-5 shadow-card xl:sticky xl:top-7 xl:max-h-[calc(100vh-3.5rem)] xl:overflow-auto">
      <div className="flex items-center justify-between gap-3">
        <div>
          <h2 className="text-lg font-bold text-croc-ink">Your Croc Guide</h2>
          <p className="mt-1 text-xs text-stone-500">Friendly AI assistant</p>
        </div>
        <div className="flex items-center gap-2">
          <Pill tone="green">AI Assistant</Pill>
          <button aria-label="More Croc Guide options" className="grid h-8 w-8 place-items-center rounded-lg hover:bg-stone-100">
            <MoreHorizontal className="h-4 w-4" />
          </button>
        </div>
      </div>

      <div className="mt-5 grid place-items-center rounded-lg bg-gradient-to-b from-croc-mint to-white pb-3 pt-5">
        <CrocMascot />
      </div>

      <div className="mt-5 space-y-3">
        {guideInsights.map((insight) => {
          const style = insightStyles[insight.tone];
          const Icon = style.icon;

          return (
            <article key={insight.title} className="flex items-center gap-3 rounded-lg border border-emerald-900/10 bg-white p-3 shadow-sm">
              <span className={`grid h-12 w-12 shrink-0 place-items-center rounded-lg ${style.className}`}>
                <Icon className="h-6 w-6" />
              </span>
              <div className="min-w-0 flex-1">
                <h3 className={`text-sm font-bold ${style.titleClass}`}>{insight.title}</h3>
                <p className="mt-1 text-sm leading-5 text-stone-600">{insight.body}</p>
              </div>
              <ChevronRight className="h-5 w-5 shrink-0 text-croc-moss" />
            </article>
          );
        })}
      </div>

      <div className="my-6 h-px bg-emerald-900/10" />

      <div>
        <div className="mb-3 flex items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <Bell className="h-4 w-4 text-croc-moss" />
            <p className="font-semibold text-croc-ink">Portfolio risk level</p>
          </div>
          <p className="text-sm font-semibold text-croc-moss">Moderate</p>
        </div>
        <div className="grid grid-cols-5 gap-1">
          {["bg-emerald-500", "bg-lime-500", "bg-yellow-400", "bg-orange-400", "bg-rose-500"].map((color, index) => (
            <div key={color} className={`h-3 rounded-sm ${color} ${index === 2 ? "ring-2 ring-croc-ink/20" : ""}`} />
          ))}
        </div>
        <p className="mt-3 text-sm leading-6 text-stone-600">
          {portfolioSummary.limitation}
        </p>
      </div>

      <form className="mt-6 flex gap-2 rounded-lg border border-emerald-900/10 bg-white p-2 shadow-sm">
        <input
          aria-label="Ask CrocLens"
          className="h-11 min-w-0 flex-1 border-0 bg-transparent px-2 text-sm text-croc-ink placeholder:text-stone-500 focus:outline-none"
          placeholder="Ask me anything about your money..."
        />
        <button
          aria-label="Send question"
          className="grid h-11 w-11 shrink-0 place-items-center rounded-full bg-croc-emerald text-white transition hover:bg-croc-moss"
          type="button"
        >
          <Send className="h-4 w-4" />
        </button>
      </form>
    </aside>
  );
}
