import { AppHeader } from "@/components/app-header";
import { AssetSummary } from "@/components/asset-summary";

interface AssetPageProps {
  params: Promise<{
    symbol: string;
  }>;
}

export default async function AssetPage({ params }: AssetPageProps) {
  const { symbol } = await params;

  return (
    <main className="min-h-screen bg-croc-cream">
      <AppHeader />
      <section className="mx-auto max-w-6xl px-5 py-8">
        <AssetSummary symbol={symbol} />
      </section>
    </main>
  );
}
