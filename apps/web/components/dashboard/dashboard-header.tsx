import { Menu, Sparkles } from "lucide-react";

interface DashboardHeaderProps {
  onMenuClick: () => void;
}

export function DashboardHeader({ onMenuClick }: DashboardHeaderProps) {
  return (
    <header className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
      <div className="flex items-start gap-3">
        <button
          aria-label="Open navigation"
          className="grid h-10 w-10 shrink-0 place-items-center rounded-lg border border-emerald-900/10 bg-white lg:hidden"
          onClick={onMenuClick}
        >
          <Menu className="h-5 w-5" />
        </button>
        <div>
          <h1 className="text-3xl font-bold text-croc-ink md:text-4xl">
            Good morning, Maya!
          </h1>
          <p className="mt-2 text-sm leading-6 text-stone-600 md:text-base">
            Here is your whole-wealth snapshot and beginner-friendly money update for today.
          </p>
        </div>
      </div>

      <button className="inline-flex min-h-12 items-center justify-center gap-2 rounded-lg bg-croc-emerald px-5 text-sm font-semibold text-white shadow-card transition hover:bg-croc-moss">
        <Sparkles className="h-4 w-4" />
        Ask CrocLens
      </button>
    </header>
  );
}
