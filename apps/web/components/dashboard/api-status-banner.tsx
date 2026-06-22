import { AlertCircle, CheckCircle2, Loader2, RefreshCw } from "lucide-react";
import { getApiBaseUrl } from "@/lib/api-client";

interface ApiStatusBannerProps {
  error: string | null;
  isLoading: boolean;
  onRetry: () => void;
}

export function ApiStatusBanner({ error, isLoading, onRetry }: ApiStatusBannerProps) {
  if (isLoading) {
    return (
      <div className="flex items-center gap-3 rounded-lg border border-emerald-900/10 bg-white/80 px-4 py-3 text-sm text-stone-700 shadow-card">
        <Loader2 className="h-4 w-4 animate-spin text-croc-moss" />
        Loading dashboard data from the CrocLens API...
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col gap-3 rounded-lg border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-900 shadow-card sm:flex-row sm:items-center sm:justify-between">
        <div className="flex gap-3">
          <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
          <div>
            <p className="font-semibold">Backend connection issue</p>
            <p className="mt-1 leading-6">
              Start FastAPI at <span className="font-semibold">{getApiBaseUrl()}</span> and keep the Next.js BFF running. {error}
            </p>
          </div>
        </div>
        <button
          className="inline-flex min-h-10 items-center justify-center gap-2 rounded-lg bg-white px-3 font-semibold text-rose-900"
          onClick={onRetry}
          suppressHydrationWarning
          type="button"
        >
          <RefreshCw className="h-4 w-4" />
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="flex items-center gap-3 rounded-lg border border-emerald-900/10 bg-white/80 px-4 py-3 text-sm text-stone-700 shadow-card">
      <CheckCircle2 className="h-4 w-4 text-croc-moss" />
      Connected through the CrocLens BFF to <span className="font-semibold text-croc-moss">{getApiBaseUrl()}</span>
    </div>
  );
}
