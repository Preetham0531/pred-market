"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import * as Dialog from "@radix-ui/react-dialog";
import { BriefcaseBusiness, Clock, Search, SlidersHorizontal, Star, X } from "lucide-react";
import { CategoryNavigation } from "@/components/category-navigation";
import { FeaturedMarketCard } from "@/components/featured-market-card";
import { MarketCard } from "@/components/market-card";
import { MarketTable } from "@/components/market-table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { ApiModeHint, DataSkeleton, DataState } from "@/components/ui/data-state";
import { useCategories, useMarkets } from "@/lib/api-hooks";
import { cn, formatCompact } from "@/lib/utils";

const sortOptions = [
  { label: "Trending", value: "trending" },
  { label: "Volume", value: "volume" },
  { label: "Closing soon", value: "closing-soon" },
  { label: "Newest", value: "newest" },
  { label: "Biggest movers", value: "movers" },
  { label: "Tightest spread", value: "spread" }
];

const statusOptions = [
  { label: "All statuses", value: "all" },
  { label: "Open", value: "Open" },
  { label: "Closing soon", value: "Closing soon" },
  { label: "Paused", value: "Paused" },
  { label: "Pending resolution", value: "Pending resolution" }
];

export function MarketDiscovery() {
  const [category, setCategory] = useState("all");
  const [status, setStatus] = useState("all");
  const [sort, setSort] = useState("trending");
  const [query, setQuery] = useState("");
  const [watchlistedOnly, setWatchlistedOnly] = useState(false);
  const [hasPositionOnly, setHasPositionOnly] = useState(false);
  const { data: markets = [], isLoading: marketsLoading, error: marketsError } = useMarkets();
  const { data: categories = [], isLoading: categoriesLoading } = useCategories();

  const filteredMarkets = useMemo(() => {
    const normalizedQuery = query.trim().toLowerCase();
    let next = markets.filter((market) => {
      const matchesCategory = category === "all" || market.categorySlug === category;
      const matchesStatus = status === "all" || market.status === status;
      const matchesQuery =
        normalizedQuery.length === 0 ||
        market.title.toLowerCase().includes(normalizedQuery) ||
        market.subcategory.toLowerCase().includes(normalizedQuery) ||
        market.source.toLowerCase().includes(normalizedQuery);
      const matchesWatchlist = !watchlistedOnly || market.watchlisted;
      const matchesPosition = !hasPositionOnly || market.hasPosition;
      return matchesCategory && matchesStatus && matchesQuery && matchesWatchlist && matchesPosition;
    });

    next = [...next].sort((a, b) => {
      if (sort === "volume") return b.volume24h - a.volume24h;
      if (sort === "movers") return Math.abs(b.change24h) - Math.abs(a.change24h);
      if (sort === "spread") return a.spread - b.spread;
      if (sort === "closing-soon") return a.closeTime.localeCompare(b.closeTime);
      return b.traders + b.volume24h / 10000 - (a.traders + a.volume24h / 10000);
    });

    return next;
  }, [category, hasPositionOnly, markets, query, sort, status, watchlistedOnly]);

  const loading = marketsLoading || categoriesLoading;
  const hasFilters = category !== "all" || status !== "all" || sort !== "trending" || query.trim().length > 0 || watchlistedOnly || hasPositionOnly;
  const activeFilterCount = [category !== "all", status !== "all", sort !== "trending", watchlistedOnly, hasPositionOnly].filter(Boolean).length;
  const sortLabel = sortOptions.find((item) => item.value === sort)?.label ?? "Trending";
  const selectedCategory = categories.find((item) => item.slug === category);
  const featuredMarket = filteredMarkets[0];
  const movers = [...filteredMarkets].sort((a, b) => Math.abs(b.change24h) - Math.abs(a.change24h)).slice(0, 3);
  const closingSoon = [...filteredMarkets].sort((a, b) => a.closeTime.localeCompare(b.closeTime)).slice(0, 3);
  const volumeLeaders = [...filteredMarkets].sort((a, b) => b.volume24h - a.volume24h).slice(0, 3);

  function resetFilters() {
    setCategory("all");
    setStatus("all");
    setSort("trending");
    setQuery("");
    setWatchlistedOnly(false);
    setHasPositionOnly(false);
  }

  if (marketsError) {
    return (
      <div className="mx-auto max-w-3xl space-y-3">
        <DataState
          title="Market data could not be loaded"
          message="The board is not showing aggregate volume, liquidity, or market counts because the backend request failed."
          actionLabel="Retry board"
          onAction={() => window.location.reload()}
          tone="error"
          badge="Data unavailable"
        />
        <ApiModeHint />
      </div>
    );
  }

  if (loading && markets.length === 0) {
    return (
      <div className="space-y-5">
        <div className="exchange-command-strip px-1 py-3">
          <div className="exchange-skeleton h-9 max-w-3xl rounded" />
        </div>
        <DataSkeleton rows={6} />
      </div>
    );
  }

  return (
    <div className="exchange-board space-y-5">
      <CategoryNavigation categories={categories} selectedCategory={category} onCategoryChange={setCategory} marketsCount={markets.length} />

      <header className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold tracking-normal">Markets</h1>
          <p className="mt-1 max-w-3xl text-sm text-[var(--muted)]">
            Scan contracts by source, liquidity, spread, movement, and close time.
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2 text-xs text-[var(--muted)]">
          <Badge tone="green">{loading ? "Loading" : `${filteredMarkets.length} markets`}</Badge>
          <Badge tone="blue">Sources visible</Badge>
          {hasFilters ? (
            <button type="button" className="font-medium text-[var(--primary-strong)] hover:underline" onClick={resetFilters}>
              Reset view
            </button>
          ) : null}
        </div>
      </header>

      <section className="exchange-command-strip -mx-4 px-4 py-2 lg:-mx-6 lg:px-6" aria-label="Market search">
        <div className="flex flex-col gap-3 md:flex-row md:items-center">
          <label className="block min-w-0 flex-1">
            <span className="sr-only">Search markets</span>
            <div className="group relative flex h-11 items-center border-b border-[color-mix(in_srgb,var(--border)_68%,transparent)] transition focus-within:border-[var(--primary-border)]">
              <Search className="pointer-events-none h-4 w-4 text-[var(--muted)]" />
              <Input
                className="h-10 border-0 bg-transparent px-3 shadow-none focus:border-transparent focus:ring-0"
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                placeholder="Search market, team, source"
              />
            </div>
          </label>

          <div className="flex flex-wrap items-center gap-2">
            <Select className="w-[164px] border-transparent bg-transparent px-0 text-[var(--primary-strong)] focus:ring-0" value={sort} onValueChange={setSort} options={sortOptions} label="Sort markets" />
            <Dialog.Root>
              <Dialog.Trigger asChild>
                <Button type="button" variant="ghost" className={cn("px-2", activeFilterCount > 0 ? "text-[var(--primary-strong)]" : "")}>
                  <SlidersHorizontal className="h-4 w-4" />
                  Filters
                  {activeFilterCount > 0 ? <span className="numeric rounded-full bg-[var(--primary-soft)] px-1.5 py-0.5 text-[11px]">{activeFilterCount}</span> : null}
                </Button>
              </Dialog.Trigger>
              <Dialog.Portal>
                <Dialog.Overlay className="fixed inset-0 z-50 bg-black/35" />
                <Dialog.Content className="fixed right-3 top-16 z-50 w-[min(390px,calc(100vw-24px))] rounded-lg bg-[var(--surface)] p-4 shadow-2xl ring-1 ring-[color-mix(in_srgb,var(--border)_70%,transparent)]">
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <Dialog.Title className="text-sm font-semibold">Board filters</Dialog.Title>
                      <Dialog.Description className="mt-1 text-xs leading-5 text-[var(--muted)]">
                        Narrow the board without giving permanent space to filters.
                      </Dialog.Description>
                    </div>
                    <Dialog.Close asChild>
                      <button className="grid h-8 w-8 place-items-center rounded-md text-[var(--muted)] transition hover:bg-[var(--surface-muted)] hover:text-[var(--foreground)]" aria-label="Close filters">
                        <X className="h-4 w-4" />
                      </button>
                    </Dialog.Close>
                  </div>

                  <div className="mt-4 grid gap-3">
                    <label className="block">
                      <span className="mb-1 block text-xs font-medium text-[var(--muted)]">Category</span>
                      <Select
                        className="bg-[var(--surface-raised)]"
                        value={category}
                        onValueChange={setCategory}
                        options={[{ label: "All categories", value: "all" }, ...categories.map((item) => ({ label: item.name, value: item.slug }))]}
                      />
                    </label>

                    <label className="block">
                      <span className="mb-1 block text-xs font-medium text-[var(--muted)]">Status</span>
                      <Select className="bg-[var(--surface-raised)]" value={status} onValueChange={setStatus} options={statusOptions} />
                    </label>

                    <div className="grid grid-cols-2 gap-2">
                      <label
                        className={cn(
                          "inline-flex h-10 items-center gap-2 rounded-md px-2.5 text-sm transition focus-within:ring-2 focus-within:ring-[var(--ring)]",
                          watchlistedOnly ? "bg-[var(--primary-soft)] text-[var(--primary-strong)]" : "bg-[var(--surface-raised)] text-[var(--muted)] hover:text-[var(--foreground)]"
                        )}
                      >
                        <input className="sr-only" type="checkbox" checked={watchlistedOnly} onChange={(event) => setWatchlistedOnly(event.target.checked)} />
                        <Star className="h-4 w-4" />
                        Watchlist
                      </label>
                      <label
                        className={cn(
                          "inline-flex h-10 items-center gap-2 rounded-md px-2.5 text-sm transition focus-within:ring-2 focus-within:ring-[var(--ring)]",
                          hasPositionOnly ? "bg-[var(--primary-soft)] text-[var(--primary-strong)]" : "bg-[var(--surface-raised)] text-[var(--muted)] hover:text-[var(--foreground)]"
                        )}
                      >
                        <input className="sr-only" type="checkbox" checked={hasPositionOnly} onChange={(event) => setHasPositionOnly(event.target.checked)} />
                        <BriefcaseBusiness className="h-4 w-4" />
                        Position
                      </label>
                    </div>

                    <div className="flex items-center justify-between pt-2">
                      <span className="text-xs text-[var(--muted)]">{filteredMarkets.length} visible markets</span>
                      <Button type="button" variant="ghost" onClick={resetFilters} disabled={!hasFilters}>
                        Reset
                      </Button>
                    </div>
                  </div>
                </Dialog.Content>
              </Dialog.Portal>
            </Dialog.Root>
          </div>
        </div>
      </section>

      <div className="flex flex-wrap items-center justify-between gap-2 text-sm text-[var(--muted)]">
        <div className="flex min-w-0 flex-wrap items-center gap-2">
          <span className="font-medium text-[var(--foreground)]">{sortLabel}</span>
          {selectedCategory ? <span>{selectedCategory.shortName}</span> : null}
          {status !== "all" ? <span>{status}</span> : null}
          {watchlistedOnly ? <span>Watchlist</span> : null}
          {hasPositionOnly ? <span>Positions</span> : null}
        </div>
        <div className="flex items-center gap-2 text-xs">
          <Clock className="h-3.5 w-3.5" />
          <span>Source, liquidity, spread, close time</span>
        </div>
      </div>

      {filteredMarkets.length ? (
        <div className="grid gap-6 2xl:grid-cols-[minmax(0,1fr)_320px]">
          <div className="min-w-0 space-y-5">
            {featuredMarket ? <FeaturedMarketCard market={featuredMarket} categories={categories} /> : null}
            <section className="md:hidden">
              {filteredMarkets.map((market) => (
                <MarketCard key={market.id} market={market} categories={categories} compact />
              ))}
            </section>
            <div className="hidden md:block">
              <MarketTable markets={filteredMarkets} categories={categories} />
            </div>
          </div>
          <aside className="hidden space-y-4 2xl:block">
            <MarketRail title="Biggest movers" markets={movers} />
            <MarketRail title="Closing soon" markets={closingSoon} />
            <MarketRail title="Volume leaders" markets={volumeLeaders} />
          </aside>
        </div>
      ) : (
        <div className="border-y border-[var(--border)] py-8 text-sm text-[var(--muted)]" role="status">
          <div className="font-medium text-[var(--foreground)]">{loading ? "Loading markets" : "No markets match this board view"}</div>
          <p className="mt-1">
            {loading
              ? "Market contracts, source labels, and liquidity are being prepared."
              : hasFilters
                ? "Clear filters to return to the full exchange board."
                : "No active contracts are available yet."}
          </p>
          {!loading && hasFilters ? (
            <Button className="mt-3" type="button" variant="secondary" onClick={resetFilters}>
              Reset filters
            </Button>
          ) : null}
        </div>
      )}
    </div>
  );
}

function MarketRail({ title, markets }: { title: string; markets: Array<{ id: string; title: string; probability: number; change24h: number; volume24h: number }> }) {
  return (
    <section className="rounded-md bg-[var(--surface)]/38 p-3">
      <h2 className="text-sm font-semibold">{title}</h2>
      <div className="mt-2 space-y-1">
        {markets.map((market) => (
          <Link key={market.id} href={`/markets/${market.id}`} className="block rounded-md px-2 py-2 text-sm transition hover:bg-[var(--surface-muted)]/56">
            <div className="line-clamp-2 font-medium">{market.title}</div>
            <div className="mt-1 flex items-center justify-between gap-2 text-xs text-[var(--muted)]">
              <span className="numeric">{market.probability}% YES</span>
              <span className={market.change24h >= 0 ? "numeric text-[var(--green-text)]" : "numeric text-[var(--red-text)]"}>{market.change24h >= 0 ? "+" : ""}{market.change24h.toFixed(1)}%</span>
            </div>
            <div className="numeric mt-0.5 text-xs text-[var(--muted)]">{formatCompact(market.volume24h)} vol</div>
          </Link>
        ))}
      </div>
    </section>
  );
}
