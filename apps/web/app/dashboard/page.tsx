import { AppHeader } from "@/components/app-header";
import { AssetSearch } from "@/components/asset-search";
import { PortfolioSummary } from "@/components/portfolio-summary";

export default function DashboardPage() {
  return (
    <main className="min-h-screen bg-croc-cream">
      <AppHeader />
      <section className="mx-auto max-w-6xl px-5 py-8">
        <div className="rounded-2xl border border-emerald-900/10 bg-white p-6 shadow-card">
          <p className="text-sm font-semibold uppercase text-croc-moss">Dashboard</p>
          <h1 className="mt-2 text-3xl font-bold text-croc-ink md:text-5xl">Research a stock or ETF.</h1>
          <p className="mt-3 max-w-2xl text-stone-600">
            Enter a ticker to see latest available price data, a simple chart, and Croc Guide's beginner explanation.
          </p>
          <div className="mt-6 max-w-2xl">
            <AssetSearch autoFocus />
          </div>
        </div>

        <div className="mt-6">
          <PortfolioSummary />
        </div>
      </section>
    </main>
  );
}
