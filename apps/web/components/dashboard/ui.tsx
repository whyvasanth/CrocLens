import { clsx } from "clsx";
import type { ReactNode } from "react";

interface CardProps {
  children: ReactNode;
  className?: string;
}

export function Card({ children, className }: CardProps) {
  return (
    <section
      className={clsx(
        "rounded-lg border border-emerald-900/10 bg-white/90 p-5 shadow-card backdrop-blur",
        className
      )}
    >
      {children}
    </section>
  );
}

interface SectionTitleProps {
  eyebrow?: string;
  title: string;
  action?: ReactNode;
}

export function SectionTitle({ eyebrow, title, action }: SectionTitleProps) {
  return (
    <div className="mb-4 flex items-start justify-between gap-4">
      <div>
        {eyebrow ? (
          <p className="text-xs font-semibold uppercase text-croc-moss">
            {eyebrow}
          </p>
        ) : null}
        <h2 className="mt-1 text-base font-semibold text-croc-ink">{title}</h2>
      </div>
      {action}
    </div>
  );
}

interface PillProps {
  children: ReactNode;
  tone?: "green" | "gold" | "blue" | "coral" | "neutral";
}

export function Pill({ children, tone = "neutral" }: PillProps) {
  const toneClass = {
    green: "bg-croc-mint text-croc-moss",
    gold: "bg-amber-100 text-amber-800",
    blue: "bg-sky-100 text-sky-800",
    coral: "bg-rose-100 text-rose-800",
    neutral: "bg-stone-100 text-stone-700"
  }[tone];

  return (
    <span
      className={clsx(
        "inline-flex min-h-7 items-center rounded-md px-2.5 text-xs font-semibold",
        toneClass
      )}
    >
      {children}
    </span>
  );
}

