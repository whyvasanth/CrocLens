import Link from "next/link";
import { ArrowRight, BarChart3, Search, ShieldCheck } from "lucide-react";
import { AppHeader } from "@/components/app-header";
import { AssetSearch } from "@/components/asset-search";

export default function HomePage() {
  return (
    <main className="min-h-screen bg-croc-cream">
      <AppHeader />
      <section className="mx-auto grid max-w-6xl gap-8 px-5 py-10 lg:grid-cols-[1fr_0.85fr] lg:items-center lg:py-16">
        <div>
          <p className="inline-flex rounded-full bg-croc-mint px-3 py-2 text-sm font-semibold text-croc-moss">
            See your money clearly.
          </p>
          <h1 className="mt-5 max-w-3xl text-4xl font-bold leading-tight text-croc-ink md:text-6xl">
            A simple stock and ETF dashboard for beginner investors.
          </h1>
          <p className="mt-5 max-w-2xl text-lg leading-8 text-stone-600">
            Search a ticker, review the latest available yfinance data, and let Croc Guide explain the numbers in plain language.
          </p>
          <div className="mt-7 max-w-xl">
            <AssetSearch autoFocus />
          </div>
          <div className="mt-6 flex flex-wrap gap-3">
            <Link
              className="inline-flex min-h-11 items-center gap-2 rounded-lg bg-croc-emerald px-4 text-sm font-semibold text-white"
              href="/dashboard"
            >
              Open Dashboard
              <ArrowRight className="h-4 w-4" />
            </Link>
          </div>
          <p className="mt-5 text-sm leading-6 text-stone-500">
            Educational information only. CrocLens does not provide financial advice or buy/sell recommendations.
          </p>
        </div>

        <div className="rounded-2xl border border-emerald-900/10 bg-white p-5 shadow-card">
          <div className="rounded-xl bg-[radial-gradient(circle_at_top_left,#0b7a5c,#052f28_60%,#03231e)] p-5 text-white">
            <div className="flex items-center justify-between gap-4">
              <div>
                <p className="text-sm text-emerald-100">Demo portfolio</p>
                <p className="mt-2 text-3xl font-bold">$2,728.70</p>
                <p className="mt-1 text-sm text-emerald-100">Sample ETF allocation for learning.</p>
              </div>
              <BarChart3 className="h-10 w-10 text-croc-lime" />
            </div>
          </div>
          <div className="mt-4 grid gap-3 sm:grid-cols-3">
            {[
              { icon: Search, label: "Search", text: "Stocks and ETFs" },
              { icon: BarChart3, label: "Chart", text: "Simple history" },
              { icon: ShieldCheck, label: "Safety", text: "Educational only" }
            ].map(({ icon: Icon, label, text }) => (
              <div className="rounded-xl border border-emerald-900/10 bg-croc-cream p-4" key={label}>
                <Icon className="h-5 w-5 text-croc-moss" />
                <p className="mt-3 font-semibold text-croc-ink">{label}</p>
                <p className="mt-1 text-sm text-stone-600">{text}</p>
              </div>
            ))}
          </div>
        </div>
      </section>
    </main>
  );
}
