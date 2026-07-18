import Link from "next/link";
import { ArrowDownRight, ArrowUpRight, Clock, Droplets, Star } from "lucide-react";
import { IdentityIcon } from "@/components/identity-icon";
import { ProbabilityPill } from "@/components/probability-pill";
import { StatusBadge } from "@/components/status-badge";
import { getMarketIdentity, getOutcomeIdentity } from "@/lib/market-identities";
import type { Category, Market } from "@/lib/mock-data";
import { cn, formatCompact, signedPercent } from "@/lib/utils";

type MarketTableProps = {
  markets: Market[];
  categories?: Category[];
};

const tableGrid = "md:grid-cols-[minmax(360px,1fr)_92px_84px_126px_78px_132px]";

export function MarketTable({ markets, categories = [] }: MarketTableProps) {
  return (
    <div className="exchange-unified-table overflow-hidden">
      <div className={cn("exchange-table-header hidden gap-4 px-2 py-2 md:grid", tableGrid)}>
        <div>Market</div>
        <div className="text-right">YES price</div>
        <div className="text-right">24h</div>
        <div className="text-right">Volume / liq</div>
        <div className="text-right">Spread</div>
        <div>Close</div>
      </div>
      <div className="space-y-1">
        {markets.map((market) => {
          const category = categories.find((item) => item.slug === market.categorySlug);
          const isPositive = market.change24h >= 0;

          return (
            <Link
              href={`/markets/${market.id}`}
              key={market.id}
              className={cn(
                "exchange-live-row grid min-h-[76px] gap-4 rounded-md px-2 py-3 text-sm transition hover:bg-[color-mix(in_srgb,var(--surface-muted)_42%,transparent)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--ring)] md:items-center",
                tableGrid
              )}
            >
              <div className="min-w-0">
                <div className="flex min-w-0 items-center gap-2">
                  <IdentityIcon identity={getMarketIdentity(market, category)} size="sm" />
                  {market.watchlisted ? <Star className="h-4 w-4 fill-[var(--brass)] text-[var(--brass)]" /> : null}
                  <span className="truncate font-medium">{market.title}</span>
                  <StatusBadge status={market.status} />
                </div>
                <div className="mt-1 flex min-w-0 flex-wrap gap-x-2 gap-y-0.5 text-xs text-[var(--muted)]">
                  <span>{category?.shortName}</span>
                  <span>{market.marketType}</span>
                  <span>{market.subcategory}</span>
                  <span className="truncate">Source: {market.source}</span>
                </div>
                <div className="mt-2 grid gap-1 sm:grid-cols-2">
                  {market.outcomes.slice(0, 2).map((outcome) => (
                    <div key={outcome.label} className="min-w-0">
                      <div className="flex items-center justify-between gap-2 text-xs">
                        <span className="flex min-w-0 items-center gap-2 text-[var(--foreground)]">
                          <IdentityIcon identity={getOutcomeIdentity(market, outcome, category)} size="sm" className="h-5 w-5" />
                          <span className="truncate">{getOutcomeIdentity(market, outcome, category).label}</span>
                        </span>
                        <span className="numeric shrink-0 text-[var(--muted)]">{outcome.probability}%</span>
                      </div>
                      <div className="mt-1 h-1 overflow-hidden rounded-full bg-[var(--surface-muted)]">
                        <div
                          className={outcome.label.toUpperCase() === "NO" ? "exchange-bar-fill h-full rounded-full bg-[var(--red-border)] shadow-[0_0_10px_rgba(239,68,68,0.25)]" : "exchange-bar-fill h-full rounded-full bg-[var(--green-border)] shadow-[0_0_10px_rgba(34,197,94,0.25)]"}
                          style={{ width: `${Math.max(6, outcome.probability)}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
              <div className="flex justify-end">
                <ProbabilityPill label="YES" probability={market.probability} compact className="h-8 min-w-14 px-2" />
              </div>
              <div
                className={cn(
                  "inline-flex items-center justify-end gap-1 text-xs font-medium",
                  isPositive ? "text-[var(--green-text)]" : "text-[var(--red-text)]"
                )}
              >
                {isPositive ? <ArrowUpRight className="h-3.5 w-3.5" /> : <ArrowDownRight className="h-3.5 w-3.5" />}
                {signedPercent(market.change24h)}
              </div>
              <div className="numeric text-right text-xs text-[var(--muted)]">
                <div className="flex items-center justify-end gap-1">
                  <Droplets className="h-3.5 w-3.5" />
                  {formatCompact(market.volume24h)}
                </div>
                <div className="mt-1">{formatCompact(market.liquidity)} liq</div>
              </div>
              <div className="numeric text-right text-xs text-[var(--muted)]">{market.spread} pts</div>
              <div className="flex min-w-0 items-center gap-1 text-xs text-[var(--muted)]">
                <Clock className="h-3.5 w-3.5 shrink-0" />
                <span className="truncate">{market.closeTime}</span>
              </div>
            </Link>
          );
        })}
      </div>
    </div>
  );
}
