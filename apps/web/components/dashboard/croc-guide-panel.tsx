"use client";

import { FormEvent, useEffect, useState } from "react";
import { clsx } from "clsx";
import {
  Bell,
  ChevronRight,
  Lightbulb,
  Loader2,
  MoreHorizontal,
  Send,
  ShieldCheck,
  Star,
  X
} from "lucide-react";
import { askAssistant } from "@/lib/api-client";
import { guideInsights, portfolioSummary } from "@/lib/mock-dashboard-data";
import { CrocMascot } from "@/components/dashboard/croc-mascot";
import { Pill } from "@/components/dashboard/ui";
import type { AssistantResponse } from "@/types/api";

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
  const [question, setQuestion] = useState("How does debt affect my net worth?");
  const [answer, setAnswer] = useState<AssistantResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

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

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const trimmedQuestion = question.trim();

    if (trimmedQuestion.length < 3) {
      setError("Ask CrocLens a question with at least three characters.");
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      const response = await askAssistant({
        question: trimmedQuestion,
        beginner_mode: true,
        include_prompt_debug: false
      });
      setAnswer(response);
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Unable to reach Croc Guide.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <>
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

          <div className="my-6 h-px bg-emerald-900/10" />

          <div className="space-y-3">
            <div className="flex items-center justify-between gap-3">
              <p className="font-semibold text-croc-ink">Latest Croc answer</p>
              {answer ? <Pill tone={answer.safety.passed ? "green" : "gold"}>{answer.intent}</Pill> : null}
            </div>

            {answer ? (
              <article className="rounded-lg border border-emerald-900/10 bg-croc-cream p-4">
                <div className="flex flex-wrap gap-2">
                  <Pill tone="green">{answer.confidence} confidence</Pill>
                  <Pill tone={answer.safety.passed ? "green" : "gold"}>
                    {answer.safety.passed ? "Safety passed" : "Safety reframed"}
                  </Pill>
                </div>
                <h3 className="mt-4 text-sm font-bold text-croc-ink">{answer.summary}</h3>
                <p className="mt-2 text-sm leading-6 text-stone-600">{answer.beginner_explanation}</p>
                <div className="mt-4 space-y-2">
                  {answer.suggested_next_steps.map((step) => (
                    <div className="flex gap-2" key={step}>
                      <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-croc-moss" />
                      <p className="text-xs leading-5 text-stone-600">{step}</p>
                    </div>
                  ))}
                </div>
                <p className="mt-4 text-xs leading-5 text-stone-500">
                  {answer.data_limitations[0]} {answer.safety_disclaimer}
                </p>
              </article>
            ) : (
              <div className="rounded-lg border border-emerald-900/10 bg-croc-cream p-4">
                <p className="text-sm leading-6 text-stone-600">
                  Ask about debt, retirement, risk, taxes, market moves, or how to read the dashboard.
                </p>
              </div>
            )}

            {answer?.agent_trace.length ? (
              <details className="rounded-lg border border-emerald-900/10 bg-white p-4">
                <summary className="flex cursor-pointer items-center justify-between gap-3">
                  <span className="text-sm font-semibold text-croc-ink">How CrocLens reached this</span>
                  <Pill tone="blue">{answer.agent_trace.length} checks</Pill>
                </summary>
                <div className="space-y-3">
                  {answer.agent_trace.map((step, index) => (
                    <div className="flex gap-3" key={`${step.agent}-${index}`}>
                      <span className="mt-1 grid h-6 w-6 shrink-0 place-items-center rounded-full bg-croc-mint text-xs font-bold text-croc-moss">
                        {index + 1}
                      </span>
                      <div className="min-w-0 flex-1 border-b border-emerald-900/10 pb-3 last:border-0 last:pb-0">
                        <div className="flex flex-wrap items-center gap-2">
                          <p className="text-xs font-bold text-croc-ink">{step.title}</p>
                          <Pill tone={step.status === "used" ? "green" : "neutral"}>{step.status}</Pill>
                        </div>
                        <p className="mt-1 text-xs leading-5 text-stone-600">{step.output_summary}</p>
                        {step.tools_used.length ? (
                          <p className="mt-1 text-[11px] leading-4 text-stone-500">
                            Tools: {step.tools_used.join(", ")}
                          </p>
                        ) : null}
                      </div>
                    </div>
                  ))}
                </div>
              </details>
            ) : null}

            {error ? (
              <p className="rounded-lg border border-rose-200 bg-rose-50 p-3 text-sm leading-6 text-rose-800">
                {error}
              </p>
            ) : null}
          </div>
        </div>

        <form className="flex gap-2 border-t border-emerald-900/10 bg-white p-4" onSubmit={handleSubmit}>
          <input
            aria-label="Ask CrocLens"
            className="h-11 min-w-0 flex-1 rounded-lg border border-emerald-900/10 bg-white px-3 text-sm text-croc-ink placeholder:text-stone-500 focus:outline-none"
            onChange={(event) => setQuestion(event.target.value)}
            placeholder="Ask me anything about your money..."
            suppressHydrationWarning
            value={question}
          />
          <button
            aria-label="Send question"
            disabled={isSubmitting}
            className="grid h-11 w-11 shrink-0 place-items-center rounded-full bg-croc-emerald text-white transition hover:bg-croc-moss"
            suppressHydrationWarning
            type="submit"
          >
            {isSubmitting ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
          </button>
        </form>
      </aside>
    </>
  );
}
