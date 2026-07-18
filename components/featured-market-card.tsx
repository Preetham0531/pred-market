import Link from "next/link";
import { ArrowDownRight, ArrowUpRight, Clock, ShieldCheck } from "lucide-react";
import { IdentityIcon } from "@/components/identity-icon";
import { MiniProbabilityChart } from "@/components/mini-probability-chart";
import { ProbabilityPill } from "@/components/probability-pill";
import { StatusBadge } from "@/components/status-badge";
import { getMarketIdentity, getOutcomeIdentity } from "@/lib/market-identities";
import type { Category, Market } from "@/lib/mock-data";
import { cn, formatCompact, signedPercent } from "@/lib/utils";

type FeaturedMarketCardProps = {
  market: Market;
  categories?: Category[];
};

export function FeaturedMarketCard({ market, categories = [] }: FeaturedMarketCardProps) {
  const category = categories.find((item) => item.slug === market.categorySlug);
  const isPositive = market.change24h >= 0;
  const topOutcomes = market.outcomes.slice(0, 2);
  const chartData = market.priceHistory.length
    ? market.priceHistory
    : Array.from({ length: 7 }, (_, index) => {
        const progress = index / 6;
        const start = Math.max(1, Math.min(99, market.probability - market.change24h));
        return {
          time: `point-${index}`,
          value: Math.max(1, Math.min(99, Math.round(start + market.change24h * progress + Math.sin(index) * 1.4))),
          volume: Math.max(1, Math.round((market.volume24h / 7) * (0.72 + progress * 0.5)))
        };
      });

  return (
    <Link
      href={`/markets/${market.id}`}
      className="group block rounded-lg bg-[color-mix(in_srgb,var(--surface)_62%,transparent)] p-4 transition hover:bg-[color-mix(in_srgb,var(--surface-muted)_46%,transparent)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--ring)]"
    >
      <div className="grid gap-5 xl:grid-cols-[minmax(0,0.92fr)_minmax(360px,0.8fr)] xl:items-center">
        <div className="min-w-0">
          <div className="flex flex-wrap items-center gap-2">
            <IdentityIcon identity={getMarketIdentity(market, category)} size="md" />
            <span className="text-xs font-semibold text-[var(--muted)]">{category?.shortName ?? market.categorySlug}</span>
            <StatusBadge status={market.status} />
            <span
              className={cn(
                "numeric inline-flex items-center gap-1 text-xs font-semibold",
                isPositive ? "text-[var(--green-text)]" : "text-[var(--red-text)]"
              )}
            >
              {isPositive ? <ArrowUpRight className="h-3.5 w-3.5" /> : <ArrowDownRight className="h-3.5 w-3.5" />}
              {signedPercent(market.change24h)}
            </span>
          </div>

          <h2 className="mt-3 max-w-3xl text-2xl font-semibold leading-tight text-[var(--foreground)] group-hover:text-[var(--primary-strong)]">
            {market.title}
          </h2>

          <div className="mt-3 flex flex-wrap gap-x-4 gap-y-2 text-sm text-[var(--muted)]">
            <span className="flex items-center gap-1.5">
              <Clock className="h-4 w-4" />
              {market.closeTime}
            </span>
            <span className="flex items-center gap-1.5">
              <ShieldCheck className="h-4 w-4" />
              {market.source}
            </span>
            <span className="numeric">{formatCompact(market.volume24h)} 24h vol</span>
            <span className="numeric">{market.spread} pts spread</span>
          </div>

          <div className="mt-5 grid gap-2 sm:grid-cols-2">
            {topOutcomes.map((outcome) => (
              <div key={outcome.label} className="flex items-center justify-between gap-3 rounded-md bg-[var(--surface-raised)]/42 px-3 py-2">
                <div className="flex min-w-0 items-center gap-2">
                  <IdentityIcon identity={getOutcomeIdentity(market, outcome, category)} size="sm" />
                  <span className="truncate text-sm font-medium">{getOutcomeIdentity(market, outcome, category).label}</span>
                </div>
                <ProbabilityPill label={outcome.label} probability={outcome.probability} price={outcome.price} compact />
              </div>
            ))}
          </div>
        </div>

        <div className="min-h-40 rounded-md bg-[var(--surface-raised)]/36 p-3">
          <div className="mb-2 flex items-center justify-between gap-2 text-xs text-[var(--muted)]">
            <span>Probability movement</span>
            <span className="numeric font-semibold text-[var(--foreground)]">{market.probability}% YES</span>
          </div>
          <MiniProbabilityChart data={chartData} tone={isPositive ? "green" : "red"} height={150} />
        </div>
      </div>
    </Link>
  );
}
