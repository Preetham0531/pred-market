"use client";

import { MarketCard } from "@/components/market-card";
import { MarketTable } from "@/components/market-table";
import { ApiModeHint, DataState } from "@/components/ui/data-state";
import { useCategories, useWatchlistData } from "@/lib/api-hooks";

export default function WatchlistPage() {
  const { data: watchlistData, isLoading, error } = useWatchlistData();
  const { data: categories = [] } = useCategories();
  const watchlist = watchlistData?.items ?? [];

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-2xl font-semibold">Watchlist</h1>
        <p className="mt-1 text-sm text-[var(--muted)]">Markets saved for monitoring probability movement, close time, and liquidity.</p>
      </div>
      {error ? (
        <div className="space-y-3">
          <DataState
            title="Watchlist could not be loaded"
            message="Saved markets require a signed-in backend session. Sign in as a trader, or switch to mock mode for a visual preview."
            tone="error"
            badge="Auth required"
          />
          <ApiModeHint />
        </div>
      ) : isLoading ? (
        <div className="border-y border-[var(--border)] py-6 text-sm text-[var(--muted)]">Loading saved markets...</div>
      ) : watchlist.length ? (
        <>
          <div className="lg:hidden">
            {watchlist.map((market) => (
              <MarketCard key={market.id} market={market} categories={categories} />
            ))}
          </div>
          <div className="hidden lg:block">
            <MarketTable markets={watchlist} categories={categories} />
          </div>
        </>
      ) : (
        <DataState
          title="No saved markets yet"
          message="Use the exchange board to find contracts worth monitoring, then return here for a focused watchlist."
          actionLabel="Open exchange board"
          actionHref="/markets"
          tone="empty"
        />
      )}
    </div>
  );
}
