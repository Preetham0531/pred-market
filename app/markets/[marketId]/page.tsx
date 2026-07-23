"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect } from "react";
import { ArrowDownRight, ArrowUpRight, ChevronDown, Clock } from "lucide-react";
import { OrderBook } from "@/components/order-book";
import { ProbabilityChart } from "@/components/probability-chart";
import { TradeTicket } from "@/components/trade-ticket";
import { Badge } from "@/components/ui/badge";
import { buttonVariants } from "@/components/ui/button";
import { DataState } from "@/components/ui/data-state";
import { useCategories, useMarket } from "@/lib/api-hooks";
import { useMarketRealtime } from "@/lib/realtime";
import { formatCompact, signedPercent } from "@/lib/utils";

function MarketDetailSkeleton() {
  return (
    <div className="grid gap-5 pb-24 xl:grid-cols-[minmax(0,1fr)_360px] xl:pb-0" aria-busy="true">
      <div className="space-y-4">
        <div className="exchange-skeleton h-24 rounded-md" />
        <div className="exchange-skeleton h-[340px] rounded-md" />
        <div className="exchange-skeleton h-[260px] rounded-md" />
      </div>
      <div className="exchange-skeleton hidden h-[520px] rounded-md xl:block" />
    </div>
  );
}

export default function MarketDetailPage() {
  const params = useParams<{ marketId: string }>();
  const marketId = params.marketId;
  const marketQuery = useMarket(marketId);
  const refetchMarket = marketQuery.refetch;
  const { data: categories = [] } = useCategories();
  const realtime = useMarketRealtime(marketId);

  useEffect(() => {
    if (realtime.connected || !marketId) return;
    const timer = window.setInterval(() => void refetchMarket(), 5000);
    return () => window.clearInterval(timer);
  }, [marketId, realtime.connected, refetchMarket]);

  if (marketQuery.isLoading) return <MarketDetailSkeleton />;

  const market = marketQuery.data;
  if (marketQuery.error || !market) {
    return (
      <div className="mx-auto max-w-3xl space-y-3">
        <DataState
          title="Market could not be loaded"
          message="The market service is temporarily unavailable."
          actionLabel="Try again"
          onAction={() => window.location.reload()}
          tone="error"
        />
        <Link href="/" className={buttonVariants({ variant: "secondary" })}>Back to markets</Link>
      </div>
    );
  }

  const category = categories.find((item) => item.slug === market.categorySlug);
  const displayTitle = market.title.replace(/^Simulation:\s*/i, "");
  const spread = market.quote?.spread ?? market.spread;

  return (
    <div className="grid gap-5 pb-24 xl:grid-cols-[minmax(0,1fr)_360px] xl:pb-0">
      <div className="min-w-0 space-y-4">
        <header className="border-b border-[var(--border)] pb-4">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div className="min-w-0 max-w-4xl">
              <h1 className="text-2xl font-semibold leading-tight text-balance">{displayTitle}</h1>
              <div className="mt-2 flex items-center gap-2 text-sm text-[var(--muted)]">
                <Clock className="h-4 w-4 shrink-0" />
                <span>Closes {market.closeTime}</span>
                <span aria-hidden="true">·</span>
                <span className={realtime.stale ? "text-[var(--brass-text)]" : realtime.connected ? "text-[var(--green-text)]" : ""}>
                  {realtime.stale ? "Updating delayed" : realtime.connected ? "Connected" : "Connecting"}
                </span>
              </div>
            </div>
            <div className="text-right">
              <div className="numeric text-3xl font-semibold">{market.probability}%</div>
              <div className="text-xs text-[var(--muted)]">YES chance</div>
              <div className={market.change24h >= 0 ? "mt-1 flex items-center justify-end text-xs font-medium text-[var(--green-text)]" : "mt-1 flex items-center justify-end text-xs font-medium text-[var(--red-text)]"}>
                {market.change24h >= 0 ? <ArrowUpRight className="h-3.5 w-3.5" /> : <ArrowDownRight className="h-3.5 w-3.5" />}
                {signedPercent(market.change24h)} today
              </div>
            </div>
          </div>
        </header>

        <ProbabilityChart data={market.priceHistory} />

        <section className="grid border-y border-[var(--border)] sm:grid-cols-2">
          <div className="p-4 sm:border-r sm:border-[var(--border)]">
            <div className="text-xs text-[var(--muted)]">Spread</div>
            <div className="numeric mt-1 text-lg font-semibold">{spread ?? "-"} pts</div>
            <p className="mt-2 max-w-md text-xs leading-5 text-[var(--muted)]">
              The gap between the best buy and sell prices. A smaller spread usually means easier trading.
            </p>
          </div>
          <div className="border-t border-[var(--border)] p-4 sm:border-t-0">
            <div className="text-xs text-[var(--muted)]">24-hour volume</div>
            <div className="numeric mt-1 text-lg font-semibold">{formatCompact(market.volume24h)}</div>
            <p className="mt-2 text-xs leading-5 text-[var(--muted)]">Total value traded during the last 24 hours.</p>
          </div>
        </section>

        <OrderBook market={market} />

        <details className="group border-y border-[var(--border)]">
          <summary className="flex cursor-pointer list-none items-center justify-between py-4 text-sm font-semibold">
            How this market resolves
            <ChevronDown className="h-4 w-4 text-[var(--muted)] transition group-open:rotate-180" />
          </summary>
          <div className="space-y-4 pb-5 text-sm">
            <p className="leading-6 text-[var(--muted)]">{market.ruleSummary}</p>
            <dl className="grid gap-3 text-xs sm:grid-cols-2">
              <div><dt className="text-[var(--muted)]">Status</dt><dd className="mt-1 font-medium">{market.status}</dd></div>
              <div><dt className="text-[var(--muted)]">Market type</dt><dd className="mt-1 font-medium">{market.marketType}</dd></div>
              <div><dt className="text-[var(--muted)]">Category</dt><dd className="mt-1 font-medium">{category?.name ?? market.categorySlug}</dd></div>
              <div><dt className="text-[var(--muted)]">Close time</dt><dd className="mt-1 font-medium">{market.closeTime}</dd></div>
              <div className="sm:col-span-2"><dt className="text-[var(--muted)]">Resolution source</dt><dd className="mt-1 font-medium">{market.source}</dd></div>
            </dl>
            {market.riskNotes.length ? (
              <div>
                <div className="mb-2 text-xs font-medium text-[var(--muted)]">Important notes</div>
                <div className="flex flex-wrap gap-2">
                  {market.riskNotes.map((note) => <Badge key={note} tone="brass">{note}</Badge>)}
                </div>
              </div>
            ) : null}
          </div>
        </details>

        <details className="group border-b border-[var(--border)]">
          <summary className="flex cursor-pointer list-none items-center justify-between py-4 text-sm font-semibold">
            Recent trades
            <ChevronDown className="h-4 w-4 text-[var(--muted)] transition group-open:rotate-180" />
          </summary>
          <div className="pb-4">
            {market.recentTrades.length ? market.recentTrades.map((trade) => (
              <div key={`${trade.time}-${trade.price}-${trade.quantity}`} className="grid grid-cols-[1fr_70px_70px] border-t border-[var(--border)] py-2 text-xs">
                <span className="text-[var(--muted)]">{trade.outcome} · {trade.time}</span>
                <span className="numeric text-right">{trade.price}</span>
                <span className="numeric text-right">{trade.quantity}</span>
              </div>
            )) : <p className="text-sm text-[var(--muted)]">No completed trades yet.</p>}
          </div>
        </details>
      </div>

      <TradeTicket market={market} />
    </div>
  );
}
