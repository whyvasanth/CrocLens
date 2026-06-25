import Link from "next/link";

export function AppHeader() {
  return (
    <header className="border-b border-emerald-900/10 bg-white/85 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-5 py-4">
        <Link className="flex items-center gap-3" href="/" aria-label="CrocLens home">
          <span className="grid h-11 w-11 place-items-center rounded-xl bg-croc-lime text-xl font-bold text-white">
            C
          </span>
          <span>
            <span className="block text-lg font-bold text-croc-ink">CrocLens</span>
            <span className="block text-xs text-stone-600">See your money clearly.</span>
          </span>
        </Link>
        <nav className="flex items-center gap-2 text-sm font-semibold">
          <Link className="rounded-lg px-3 py-2 text-croc-moss hover:bg-croc-mint" href="/dashboard">
            Dashboard
          </Link>
        </nav>
      </div>
    </header>
  );
}
