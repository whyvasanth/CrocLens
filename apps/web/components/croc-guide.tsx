import { ShieldCheck } from "lucide-react";
import type { GuideResponse } from "@/lib/types";

export function CrocGuide({ guide }: { guide: GuideResponse }) {
  return (
    <aside className="rounded-2xl border border-emerald-900/10 bg-white p-6 shadow-card">
      <div className="flex items-start gap-3">
        <span className="grid h-12 w-12 shrink-0 place-items-center rounded-xl bg-croc-mint text-xl font-bold text-croc-moss">
          C
        </span>
        <div>
          <p className="text-sm font-semibold uppercase text-croc-moss">Croc Guide</p>
          <h2 className="mt-1 text-xl font-bold text-croc-ink">Beginner explanation</h2>
        </div>
      </div>
      <p className="mt-4 text-sm leading-6 text-stone-700">{guide.summary}</p>

      <div className="mt-5 space-y-3">
        {guide.observations.map((item) => (
          <p className="rounded-xl bg-croc-cream p-3 text-sm leading-6 text-stone-700" key={item}>{item}</p>
        ))}
      </div>

      <div className="mt-5 rounded-xl border border-emerald-900/10 p-4">
        <div className="flex items-center gap-2">
          <ShieldCheck className="h-4 w-4 text-croc-moss" />
          <p className="font-semibold text-croc-ink">What to keep in mind</p>
        </div>
        <ul className="mt-3 space-y-2 text-sm leading-6 text-stone-600">
          {guide.considerations.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </div>

      <p className="mt-4 text-xs leading-5 text-stone-500">{guide.educational_disclaimer}</p>
    </aside>
  );
}
