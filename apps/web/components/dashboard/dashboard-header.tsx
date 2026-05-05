import { Menu, Sparkles } from "lucide-react";

interface DashboardHeaderProps {
  description: string;
  onAskClick: () => void;
  onMenuClick: () => void;
  title: string;
}

export function DashboardHeader({
  description,
  onAskClick,
  onMenuClick,
  title
}: DashboardHeaderProps) {
  return (
    <header className="flex flex-col gap-4 rounded-lg border border-emerald-900/10 bg-white/75 p-4 shadow-card backdrop-blur md:flex-row md:items-center md:justify-between md:p-5">
      <div className="flex items-start gap-3">
        <button
          aria-label="Open navigation"
          className="grid h-10 w-10 shrink-0 place-items-center rounded-lg border border-emerald-900/10 bg-white lg:hidden"
          onClick={onMenuClick}
          suppressHydrationWarning
          type="button"
        >
          <Menu className="h-5 w-5" />
        </button>
        <div>
          <h1 className="text-2xl font-bold text-croc-ink md:text-3xl">
            {title}
          </h1>
          <p className="mt-1 max-w-2xl text-sm leading-6 text-stone-600">
            {description}
          </p>
        </div>
      </div>

      <button
        className="inline-flex min-h-11 items-center justify-center gap-2 rounded-lg bg-croc-emerald px-5 text-sm font-semibold text-white shadow-card transition hover:bg-croc-moss"
        onClick={onAskClick}
        suppressHydrationWarning
        type="button"
      >
        <Sparkles className="h-4 w-4" />
        Ask CrocLens
      </button>
    </header>
  );
}
