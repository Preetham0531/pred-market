"use client";

import Link from "next/link";
import { DataState } from "@/components/ui/data-state";
import { useWatchlistData } from "@/lib/api-hooks";
import { formatCompact } from "@/lib/utils";

export default function WatchlistPage() {
  const { data, isLoading, error } = useWatchlistData();
  const markets = data?.items ?? [];

  return (
    <div className="mx-auto max-w-5xl space-y-5">
      <header>
        <h1 className="text-2xl font-semibold">Watchlist</h1>
        <p className="mt-1 text-sm text-[var(--muted)]">Markets you saved for later.</p>
      </header>
      {error ? (
        <DataState title="Watchlist could not be loaded" message="Try signing in again." tone="error" />
      ) : isLoading ? (
        <div className="border-y border-[var(--border)] py-6 text-sm text-[var(--muted)]">Loading saved markets...</div>
      ) : markets.length ? (
        <div className="divide-y divide-[var(--border)] border-y border-[var(--border)]">
          {markets.map((market) => (
            <Link key={market.id} href={`/markets/${market.id}`} className="grid gap-3 px-3 py-4 hover:bg-[var(--surface-muted)]/45 sm:grid-cols-[1fr_80px_80px_100px] sm:items-center">
              <div className="font-medium">{market.title.replace(/^Simulation:\s*/i, "")}</div>
              <div className="numeric text-sm font-semibold text-[var(--green-text)]">YES {market.quote?.yesAsk ?? "-"}</div>
              <div className="numeric text-sm font-semibold text-[var(--red-text)]">NO {market.quote?.noAsk ?? "-"}</div>
              <div className="numeric text-xs text-[var(--muted)]">{formatCompact(market.volume24h)} vol</div>
            </Link>
          ))}
        </div>
      ) : (
        <DataState title="No saved markets" message="Save markets you want to check again." actionLabel="Browse markets" actionHref="/" tone="empty" />
      )}
    </div>
  );
}
