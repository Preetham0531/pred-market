"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { ArrowDownRight, ArrowUpRight, Clock, Search } from "lucide-react";
import { Input } from "@/components/ui/input";
import { DataSkeleton, DataState } from "@/components/ui/data-state";
import { useCategories, useMarkets } from "@/lib/api-hooks";
import { cn, formatCompact, signedPercent } from "@/lib/utils";

function priceLabel(value: number | null | undefined) {
  return value == null ? "-" : `${value}`;
}

export function MarketDiscovery() {
  const [category, setCategory] = useState("all");
  const [query, setQuery] = useState("");
  const { data: markets = [], isLoading, error } = useMarkets();
  const { data: categories = [] } = useCategories();

  const visibleMarkets = useMemo(() => {
    const normalized = query.trim().toLowerCase();
    return markets.filter((market) => {
      const categoryMatch = category === "all" || market.categorySlug === category;
      const queryMatch = !normalized || market.title.toLowerCase().includes(normalized) || market.subcategory.toLowerCase().includes(normalized);
      return categoryMatch && queryMatch;
    });
  }, [category, markets, query]);

  if (error) {
    return (
      <DataState
        title="Markets are temporarily unavailable"
        message="The market service did not respond. Your account and funds are unchanged."
        actionLabel="Try again"
        onAction={() => window.location.reload()}
        tone="error"
      />
    );
  }

  return (
    <div className="mx-auto max-w-6xl">
      <header className="flex flex-col gap-4 border-b border-[var(--border)] pb-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <div className="mb-1 flex items-center gap-2 text-xs font-medium text-[var(--green-text)]">
            <span className="h-1.5 w-1.5 rounded-full bg-[var(--green-text)]" />
            Simulated funds
          </div>
          <h1 className="text-2xl font-semibold">Markets</h1>
        </div>
        <label className="relative block w-full sm:max-w-sm">
          <span className="sr-only">Filter markets</span>
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[var(--muted)]" />
          <Input className="pl-9" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Find a market" />
        </label>
      </header>

      <div className="-mx-1 flex gap-1 overflow-x-auto py-3" aria-label="Market categories">
        <button
          className={cn("h-8 shrink-0 rounded-md px-3 text-sm", category === "all" ? "bg-[var(--primary-soft)] font-medium text-[var(--primary-strong)]" : "text-[var(--muted)] hover:bg-[var(--surface-muted)]")}
          onClick={() => setCategory("all")}
        >
          All
        </button>
        {categories.map((item) => (
          <button
            key={item.slug}
            className={cn("h-8 shrink-0 rounded-md px-3 text-sm", category === item.slug ? "bg-[var(--primary-soft)] font-medium text-[var(--primary-strong)]" : "text-[var(--muted)] hover:bg-[var(--surface-muted)]")}
            onClick={() => setCategory(item.slug)}
          >
            {item.shortName}
          </button>
        ))}
      </div>

      {isLoading && !markets.length ? (
        <DataSkeleton rows={6} />
      ) : visibleMarkets.length ? (
        <section className="overflow-hidden border-y border-[var(--border)]" aria-label="Available markets">
          <div className="exchange-table-header hidden grid-cols-[minmax(280px,1fr)_88px_88px_86px_92px_88px_150px] gap-3 px-3 py-2 md:grid">
            <span>Market</span>
            <span className="text-right">YES</span>
            <span className="text-right">NO</span>
            <span className="text-right">24h</span>
            <span className="text-right">Volume</span>
            <span className="text-right">Spread</span>
            <span>Closes</span>
          </div>
          <div className="divide-y divide-[var(--border)]">
            {visibleMarkets.map((market) => {
              const positive = market.change24h >= 0;
              return (
                <Link
                  key={market.id}
                  href={`/markets/${market.id}`}
                  className="group block px-3 py-4 transition-colors hover:bg-[var(--surface-muted)]/45 md:grid md:min-h-[78px] md:grid-cols-[minmax(280px,1fr)_88px_88px_86px_92px_88px_150px] md:items-center md:gap-3 md:py-3"
                >
                  <div className="min-w-0">
                    <div className="font-medium leading-5 group-hover:text-[var(--primary-strong)]">{market.title.replace(/^Simulation:\s*/i, "")}</div>
                    <div className="mt-1 text-xs text-[var(--muted)]">{market.subcategory}</div>
                  </div>
                  <div className="mt-3 grid grid-cols-2 gap-2 md:contents">
                    <div className="numeric rounded-md border border-[var(--green-border)] bg-[var(--green-soft)] px-2 py-2 text-center text-sm font-semibold text-[var(--green-text)] md:text-right">
                      <span className="mr-1 md:hidden">YES</span>{priceLabel(market.quote?.yesAsk)}
                    </div>
                    <div className="numeric rounded-md border border-[var(--red-border)] bg-[var(--red-soft)] px-2 py-2 text-center text-sm font-semibold text-[var(--red-text)] md:text-right">
                      <span className="mr-1 md:hidden">NO</span>{priceLabel(market.quote?.noAsk)}
                    </div>
                  </div>
                  <div className={cn("mt-3 flex items-center text-xs font-medium md:mt-0 md:justify-end", positive ? "text-[var(--green-text)]" : "text-[var(--red-text)]")}>
                    {positive ? <ArrowUpRight className="h-3.5 w-3.5" /> : <ArrowDownRight className="h-3.5 w-3.5" />}
                    {signedPercent(market.change24h)}
                  </div>
                  <div className="numeric mt-2 text-xs text-[var(--muted)] md:mt-0 md:text-right">{formatCompact(market.volume24h)}</div>
                  <div className="numeric mt-1 text-xs text-[var(--muted)] md:mt-0 md:text-right">{market.quote?.spread ?? market.spread ?? "-"} pts</div>
                  <div className="mt-2 flex min-w-0 items-center gap-1.5 text-xs text-[var(--muted)] md:mt-0">
                    <Clock className="h-3.5 w-3.5 shrink-0" />
                    <span className="truncate">{market.closeTime}</span>
                  </div>
                </Link>
              );
            })}
          </div>
        </section>
      ) : (
        <div className="border-y border-[var(--border)] py-12 text-center">
          <div className="text-sm font-medium">No matching markets</div>
          <p className="mt-1 text-xs text-[var(--muted)]">Try another search or category.</p>
        </div>
      )}
    </div>
  );
}
