import Link from "next/link";
import { ArrowDownRight, ArrowUpRight, Clock, Droplets, ShieldCheck, Users } from "lucide-react";
import { IdentityIcon } from "@/components/identity-icon";
import { ProbabilityPill } from "@/components/probability-pill";
import { StatusBadge } from "@/components/status-badge";
import { Badge } from "@/components/ui/badge";
import { getMarketIdentity, getOutcomeIdentity } from "@/lib/market-identities";
import type { Category, Market } from "@/lib/mock-data";
import { cn, formatCompact, signedPercent } from "@/lib/utils";

type MarketCardProps = {
  market: Market;
  categories?: Category[];
  compact?: boolean;
};

export function MarketCard({ market, categories = [], compact = false }: MarketCardProps) {
  const category = categories.find((item) => item.slug === market.categorySlug);
  const isPositive = market.change24h >= 0;
  const topOutcomes = market.outcomes.slice(0, 2);
  const maxOutcomeProbability = Math.max(...topOutcomes.map((item) => item.probability), 1);

  return (
    <Link
      href={`/markets/${market.id}`}
      className="exchange-flat-row group block rounded-md px-2 py-4 transition hover:bg-[color-mix(in_srgb,var(--surface-muted)_42%,transparent)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--ring)]"
    >
      <div className="flex gap-3">
        <IdentityIcon identity={getMarketIdentity(market, category)} size="sm" className="mt-0.5" />
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <StatusBadge status={market.status} />
            <Badge>{market.marketType}</Badge>
            {market.hasPosition ? <Badge tone="green">Position</Badge> : null}
          </div>
          <h3 className="mt-2 line-clamp-2 text-sm font-semibold leading-5 text-[var(--foreground)] group-hover:text-[var(--primary-strong)]">
            {market.title}
          </h3>
          <div className="mt-2 flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-[var(--muted)]">
            <span>{category?.shortName ?? market.categorySlug}</span>
            <span className="flex items-center gap-1">
              <Clock className="h-3.5 w-3.5" />
              {market.closeTime}
            </span>
            <span className="flex min-w-0 items-center gap-1">
              <ShieldCheck className="h-3.5 w-3.5 shrink-0" />
              <span className="truncate">Source: {market.source}</span>
            </span>
          </div>
        </div>
        <div className="text-right">
          <div className="numeric text-2xl font-semibold text-[var(--foreground)]">{market.probability}</div>
          <div className="text-xs text-[var(--muted)]">YES price</div>
          <div
            className={cn(
              "mt-1 inline-flex items-center gap-1 text-xs font-medium",
              isPositive ? "text-[var(--green-text)]" : "text-[var(--red-text)]"
            )}
          >
            {isPositive ? <ArrowUpRight className="h-3.5 w-3.5" /> : <ArrowDownRight className="h-3.5 w-3.5" />}
            {signedPercent(market.change24h)}
          </div>
        </div>
      </div>

      <div className="mt-3 space-y-2">
        {topOutcomes.map((outcome) => (
          <div key={outcome.label} className="grid grid-cols-[minmax(0,1fr)_52px] items-center gap-2 text-xs">
            <div className="min-w-0">
              <div className="flex items-center justify-between gap-2">
                <span className="flex min-w-0 items-center gap-2 text-[var(--foreground)]">
                  <IdentityIcon identity={getOutcomeIdentity(market, outcome, category)} size="sm" className="h-5 w-5" />
                  <span className="truncate">{getOutcomeIdentity(market, outcome, category).label}</span>
                </span>
                <span className="numeric shrink-0 text-[var(--muted)]">{outcome.price}</span>
              </div>
              <div className="mt-1 h-1 overflow-hidden rounded-full bg-[var(--surface-muted)]">
                <div
                  className={outcome.label.toUpperCase() === "NO" ? "exchange-bar-fill h-full rounded-full bg-[var(--red-border)] shadow-[0_0_12px_rgba(239,68,68,0.28)]" : "exchange-bar-fill h-full rounded-full bg-[var(--green-border)] shadow-[0_0_12px_rgba(34,197,94,0.28)]"}
                  style={{ width: `${Math.max(6, (outcome.probability / maxOutcomeProbability) * 100)}%` }}
                />
              </div>
            </div>
            <ProbabilityPill label={outcome.label} probability={outcome.probability} compact className="h-7 min-w-12 px-2" />
          </div>
        ))}
      </div>

      <div className="mt-3 grid grid-cols-3 gap-2 text-xs">
        <div>
          <div className="text-[var(--muted)]">24h volume</div>
          <div className="numeric mt-0.5 font-medium">{formatCompact(market.volume24h)}</div>
        </div>
        <div>
          <div className="flex items-center gap-1 text-[var(--muted)]">
            <Droplets className="h-3.5 w-3.5" />
            Liquidity
          </div>
          <div className="numeric mt-0.5 font-medium">{formatCompact(market.liquidity)}</div>
        </div>
        <div>
          <div className="text-[var(--muted)]">Spread</div>
          <div className="numeric mt-0.5 font-medium">{market.spread} pts</div>
        </div>
      </div>

      {!compact ? (
        <div className="mt-3 grid grid-cols-2 gap-2 text-xs">
          <div>
            <div className="text-[var(--muted)]">Total volume</div>
            <div className="numeric mt-0.5 font-medium">{formatCompact(market.totalVolume)}</div>
          </div>
          <div>
            <div className="flex items-center gap-1 text-[var(--muted)]">
              <Users className="h-3.5 w-3.5" />
              Traders
            </div>
            <div className="numeric mt-0.5 font-medium">{formatCompact(market.traders)}</div>
          </div>
        </div>
      ) : null}
    </Link>
  );
}
