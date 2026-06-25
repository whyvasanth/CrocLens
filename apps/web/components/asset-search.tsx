"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { Search } from "lucide-react";

export function AssetSearch({ autoFocus = false }: { autoFocus?: boolean }) {
  const router = useRouter();
  const [symbol, setSymbol] = useState("");
  const [error, setError] = useState<string | null>(null);

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const normalized = symbol.trim().toUpperCase();
    if (!/^[A-Z0-9.\-]{1,12}$/.test(normalized)) {
      setError("Enter a stock or ETF ticker, such as VTI or AAPL.");
      return;
    }
    router.push(`/assets/${encodeURIComponent(normalized)}`);
  }

  return (
    <form className="space-y-2" onSubmit={submit}>
      <div className="flex flex-col gap-3 rounded-xl border border-emerald-900/10 bg-white p-2 shadow-card sm:flex-row">
        <label className="sr-only" htmlFor="ticker-search">Ticker symbol</label>
        <input
          autoFocus={autoFocus}
          className="min-h-12 flex-1 rounded-lg bg-croc-cream px-4 text-base text-croc-ink outline-none"
          id="ticker-search"
          onChange={(event) => {
            setError(null);
            setSymbol(event.target.value);
          }}
          placeholder="Search ticker, e.g. VTI"
          value={symbol}
        />
        <button className="inline-flex min-h-12 items-center justify-center gap-2 rounded-lg bg-croc-emerald px-5 font-semibold text-white" type="submit">
          <Search className="h-4 w-4" />
          Search
        </button>
      </div>
      {error ? <p className="text-sm text-rose-700">{error}</p> : null}
    </form>
  );
}
