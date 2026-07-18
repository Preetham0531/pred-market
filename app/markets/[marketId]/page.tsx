"use client";

import { useParams } from "next/navigation";
import Link from "next/link";
import { ArrowDownRight, ArrowUpRight, Clock, ExternalLink, ShieldCheck } from "lucide-react";
import { OrderBook } from "@/components/order-book";
import { ProbabilityChart } from "@/components/probability-chart";
import { StatusBadge } from "@/components/status-badge";
import { TradeTicket } from "@/components/trade-ticket";
import { Badge } from "@/components/ui/badge";
import { buttonVariants } from "@/components/ui/button";
import { ApiModeHint, DataState } from "@/components/ui/data-state";
import { MarketCard } from "@/components/market-card";
import { useCategories, useMarket, useMarketAnalytics, useMarkets } from "@/lib/api-hooks";
import { useMarketRealtime } from "@/lib/realtime";
import { formatCompact, signedPercent } from "@/lib/utils";

function MarketDetailSkeleton() {
  return (
    <div className="grid gap-5 pb-24 xl:grid-cols-[minmax(0,1fr)_360px] xl:pb-0" aria-busy="true">
      <div className="min-w-0 space-y-4">
        <section className="exchange-panel rounded-md p-4">
          <div className="animate-pulse space-y-4">
            <div className="flex gap-2">
              <div className="exchange-skeleton h-6 w-16 rounded" />
              <div className="exchange-skeleton h-6 w-24 rounded" />
            </div>
            <div className="exchange-skeleton h-8 max-w-3xl rounded" />
            <div className="exchange-skeleton h-4 max-w-xl rounded" />
          </div>
        </section>
        <div className="exchange-skeleton h-[360px] rounded-md" />
        <div className="exchange-skeleton h-[230px] rounded-md" />
      </div>
      <aside className="exchange-skeleton hidden h-[520px] rounded-md xl:block" />
    </div>
  );
}

export default function MarketDetailPage() {
  const params = useParams<{ marketId: string }>();
  const marketId = params.marketId;
  const { data: market, isLoading, error } = useMarket(marketId);
  const { data: analytics } = useMarketAnalytics(marketId);
  const { data: categories = [] } = useCategories();
  const { data: markets = [] } = useMarkets();
  const realtime = useMarketRealtime(marketId);

  if (isLoading) {
    return <MarketDetailSkeleton />;
  }

  if (error || !market) {
    return (
      <div className="mx-auto max-w-3xl space-y-3">
        <DataState
          title="Market could not be loaded"
          message="The contract may have moved, the market API may be unavailable, or the local backend may not be seeded."
          actionLabel="Retry market"
          onAction={() => window.location.reload()}
          tone="error"
          badge="Unavailable"
        />
        <div className="flex flex-wrap gap-2">
          <Link href="/markets" className={buttonVariants({ variant: "secondary" })}>
            Back to markets
          </Link>
        </div>
        <ApiModeHint />
      </div>
    );
  }

  const category = categories.find((item) => item.slug === market.categorySlug);
  const relatedMarkets = markets
    .filter((item) => item.categorySlug === market.categorySlug && item.id !== market.id)
    .slice(0, 2);
  const tradingState =
    market.status === "Open"
      ? "Trading open"
      : market.status === "Closing soon"
        ? "Close-time risk active"
        : market.status;

  return (
    <div className="grid gap-5 pb-24 xl:grid-cols-[minmax(0,1fr)_360px] xl:pb-0">
      <div className="flex min-w-0 flex-col gap-4">
        <section className="order-1 pb-3">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div className="min-w-0">
              <div className="mb-2 flex flex-wrap items-center gap-2">
                <StatusBadge status={market.status} />
                <Badge>{market.marketType}</Badge>
                {category ? <Badge tone="blue">{category.name}</Badge> : null}
                <Badge tone={market.status === "Open" ? "neutral" : "brass"}>{tradingState}</Badge>
                <Badge tone={realtime.stale || analytics?.isStale ? "brass" : realtime.connected ? "green" : realtime.reconnecting ? "brass" : "blue"}>
                  {realtime.stale || analytics?.isStale ? "Stale" : realtime.connected ? "Live" : realtime.reconnecting ? "Reconnecting" : "Realtime ready"}
                </Badge>
              </div>
              <h1 className="max-w-4xl text-2xl font-semibold leading-tight text-balance">{market.title}</h1>
              <div className="mt-3 flex flex-wrap gap-x-4 gap-y-2 text-sm text-[var(--muted)]">
                <span className="flex items-center gap-1.5">
                  <Clock className="h-4 w-4" />
                  Closes {market.closeTime}
                </span>
                <span className="flex items-center gap-1.5">
                  <ShieldCheck className="h-4 w-4" />
                  Source: {market.source}
                </span>
                <a className="flex items-center gap-1.5 font-medium text-[var(--primary-strong)] hover:underline" href="#rules-evidence">
                  <ExternalLink className="h-4 w-4" />
                  Rules and evidence
                </a>
              </div>
              <div className="mt-4 hidden gap-0 overflow-hidden rounded-md bg-[var(--surface-raised)]/42 text-xs sm:grid sm:grid-cols-4">
                <div className="px-3 py-2">
                  <div className="text-[var(--muted)]">Close</div>
                  <div className="mt-0.5 font-medium text-[var(--foreground)]">{market.closeTime}</div>
                </div>
                <div className="border-l border-[color-mix(in_srgb,var(--border)_42%,transparent)] px-3 py-2">
                  <div className="text-[var(--muted)]">Spread</div>
                  <div className="numeric mt-0.5 font-medium text-[var(--foreground)]">{(analytics?.spread ?? market.spread) || 0} pts</div>
                </div>
                <div className="border-l border-[color-mix(in_srgb,var(--border)_42%,transparent)] px-3 py-2">
                  <div className="text-[var(--muted)]">Liquidity</div>
                  <div className="numeric mt-0.5 font-medium text-[var(--foreground)]">{formatCompact(analytics?.liquidityDepth ?? market.liquidity)}</div>
                </div>
                <div className="border-l border-[color-mix(in_srgb,var(--border)_42%,transparent)] px-3 py-2">
                  <div className="text-[var(--muted)]">24h move</div>
                  <div className={market.change24h >= 0 ? "numeric mt-0.5 font-medium text-[var(--green-text)]" : "numeric mt-0.5 font-medium text-[var(--red-text)]"}>
                    {signedPercent(market.change24h)}
                  </div>
                </div>
              </div>
              <div className="mt-3 hidden text-xs leading-5 text-[var(--blue-text)] sm:block">
                Confirm the source and resolution rule before placing a limit order. V1 uses simulated funds only.
              </div>
            </div>
            <div className="min-w-[150px] px-1 py-1 text-right">
              <div className="numeric text-3xl font-semibold">{market.probability}</div>
              <div className="text-xs text-[var(--muted)]">YES price</div>
              <div className={market.change24h >= 0 ? "mt-1 inline-flex items-center gap-1 text-sm font-medium text-[var(--green-text)]" : "mt-1 inline-flex items-center gap-1 text-sm font-medium text-[var(--red-text)]"}>
                {market.change24h >= 0 ? <ArrowUpRight className="h-4 w-4" /> : <ArrowDownRight className="h-4 w-4" />}
                {signedPercent(market.change24h)} 24h
              </div>
            </div>
          </div>
        </section>

        <div className="order-2 md:order-2">
          <ProbabilityChart data={market.priceHistory} sourceLabel={`Source: ${market.source}`} closeTime={market.closeTime} status={market.status} />
        </div>
        <div className="order-4">
          <OrderBook market={market} />
        </div>

        <section className="order-5 grid gap-4 lg:grid-cols-[minmax(0,0.9fr)_minmax(0,1.1fr)]">
          <div id="rules-evidence" className="scroll-mt-24 rounded-md bg-[var(--surface)]/38 p-3">
            <div className="flex items-center justify-between">
              <h2 className="text-sm font-semibold">Recent trades</h2>
              <Badge tone="blue">Live tape</Badge>
            </div>
            <div className="exchange-table-header mt-3 grid grid-cols-4 px-2 py-2">
              <span>Time</span>
              <span>Outcome</span>
              <span className="text-right">Price</span>
              <span className="text-right">Qty</span>
            </div>
            <div className="space-y-1">
              {market.recentTrades.length ? market.recentTrades.map((trade) => (
                <div key={`${trade.time}-${trade.price}-${trade.quantity}`} className="grid min-h-9 grid-cols-4 items-center rounded-md px-2 text-sm hover:bg-[var(--surface-muted)]/60">
                  <span className="text-[var(--muted)]">{trade.time}</span>
                  <span>{trade.outcome}</span>
                  <span className="numeric text-right">{trade.price}</span>
                  <span className="numeric text-right">{trade.quantity}</span>
                </div>
              )) : <div className="py-4 text-sm text-[var(--muted)]">No trades yet.</div>}
            </div>
          </div>

          <div className="rounded-md bg-[var(--surface)]/38 p-3">
            <div className="flex items-center justify-between">
              <h2 className="text-sm font-semibold">Rules and evidence</h2>
              <Badge tone="brass">Resolution source</Badge>
            </div>
            <p className="mt-3 text-sm leading-6 text-[var(--muted)]">{market.ruleSummary}</p>
            <div className="mt-3 space-y-2">
              {market.riskNotes.map((note) => (
                <div key={note} className="rounded-md bg-[var(--surface-muted)]/42 px-3 py-2 text-sm text-[var(--foreground)]">
                  {note}
                </div>
              ))}
            </div>
          </div>
        </section>

        {relatedMarkets.length > 0 ? (
          <section className="order-6">
            <h2 className="mb-3 text-sm font-semibold">Related markets</h2>
            <div className="grid gap-3 lg:grid-cols-2">
              {relatedMarkets.map((item) => (
                <MarketCard key={item.id} market={item} categories={categories} compact />
              ))}
            </div>
          </section>
        ) : null}
      </div>

      <TradeTicket market={market} />
    </div>
  );
}
