import { AssetDetailShell } from "@/components/asset-detail/asset-detail-shell";

interface AssetDetailPageProps {
  params: Promise<{
    assetId: string;
  }>;
}

export default async function AssetDetailPage({ params }: AssetDetailPageProps) {
  const { assetId } = await params;

  return <AssetDetailShell assetId={assetId} />;
}
