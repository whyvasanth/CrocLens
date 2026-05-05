"use client";

import { useEffect } from "react";
import { clsx } from "clsx";
import {
  Bell,
  ChevronRight,
  Lightbulb,
  MoreHorizontal,
  Send,
  ShieldCheck,
  Star,
  X
} from "lucide-react";
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

interface CrocGuidePanelProps {
  isOpen: boolean;
  onClose: () => void;
}

export function CrocGuidePanel({ isOpen, onClose }: CrocGuidePanelProps) {
  useEffect(() => {
    if (!isOpen) {
      return;
    }

    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        onClose();
      }
    };

    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [isOpen, onClose]);

  return (
    <>
      <div
        className={clsx(
          "fixed inset-0 z-40 bg-croc-ink/35 backdrop-blur-sm transition-opacity",
          isOpen ? "opacity-100" : "pointer-events-none opacity-0"
        )}
        onClick={onClose}
      />
      <aside
        aria-label="Croc Guide assistant drawer"
        aria-hidden={!isOpen}
        className={clsx(
          "fixed inset-y-0 right-0 z-50 flex w-full max-w-[430px] flex-col border-l border-emerald-900/10 bg-white shadow-2xl transition-transform duration-300",
          isOpen ? "translate-x-0" : "translate-x-full"
        )}
      >
        <div className="flex items-center justify-between gap-3 border-b border-emerald-900/10 p-5">
          <div>
            <h2 className="text-lg font-bold text-croc-ink">Your Croc Guide</h2>
            <p className="mt-1 text-xs text-stone-500">Friendly AI assistant</p>
          </div>
          <div className="flex items-center gap-2">
            <Pill tone="green">AI Assistant</Pill>
            <button
              aria-label="More Croc Guide options"
              className="grid h-9 w-9 place-items-center rounded-lg hover:bg-stone-100"
              suppressHydrationWarning
              type="button"
            >
              <MoreHorizontal className="h-4 w-4" />
            </button>
            <button
              aria-label="Close Croc Guide"
              className="grid h-9 w-9 place-items-center rounded-lg bg-stone-100 text-croc-ink hover:bg-stone-200"
              onClick={onClose}
              suppressHydrationWarning
              type="button"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        </div>

        <div className="min-h-0 flex-1 overflow-y-auto p-5">
          <div className="grid place-items-center rounded-lg bg-gradient-to-b from-croc-mint to-white pb-3 pt-5">
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
        </div>

        <form className="flex gap-2 border-t border-emerald-900/10 bg-white p-4">
          <input
            aria-label="Ask CrocLens"
            className="h-11 min-w-0 flex-1 rounded-lg border border-emerald-900/10 bg-white px-3 text-sm text-croc-ink placeholder:text-stone-500 focus:outline-none"
            placeholder="Ask me anything about your money..."
            suppressHydrationWarning
          />
          <button
            aria-label="Send question"
            className="grid h-11 w-11 shrink-0 place-items-center rounded-full bg-croc-emerald text-white transition hover:bg-croc-moss"
            suppressHydrationWarning
            type="button"
          >
            <Send className="h-4 w-4" />
          </button>
        </form>
      </aside>
    </>
  );
}
