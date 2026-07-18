"use client";

import { useParams } from "next/navigation";
import { useState } from "react";
import { CategoryNavigation } from "@/components/category-navigation";
import { CategoryIcon } from "@/components/category-3d-icon";
import { MarketCard } from "@/components/market-card";
import { MarketTable } from "@/components/market-table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ApiModeHint, DataSkeleton, DataState } from "@/components/ui/data-state";
import { useCategories, useCategory, useMarkets } from "@/lib/api-hooks";
import { cn } from "@/lib/utils";

export default function CategoryPage() {
  const params = useParams<{ categorySlug: string }>();
  const categorySlug = params.categorySlug;
  const [subcategory, setSubcategory] = useState("all");
  const { data: category, isLoading, error } = useCategory(categorySlug);
  const { data: categories = [] } = useCategories();
  const { data: markets = [] } = useMarkets();

  if (isLoading) {
    return (
      <div className="space-y-5">
        <section className="border-b border-[var(--border)] pb-5" aria-busy="true">
          <div className="flex items-start justify-between gap-4">
            <div className="w-full max-w-3xl space-y-3">
              <div className="exchange-skeleton h-6 w-44 rounded" />
              <div className="exchange-skeleton h-8 w-64 rounded" />
              <div className="exchange-skeleton h-4 w-full rounded" />
              <div className="exchange-skeleton h-4 w-2/3 rounded" />
            </div>
            <div className="exchange-skeleton h-16 w-16 rounded-md" />
          </div>
        </section>
        <DataSkeleton rows={4} />
      </div>
    );
  }

  if (error || !category) {
    return (
      <div className="mx-auto max-w-3xl space-y-3">
        <DataState
          title="Category could not be loaded"
          message="The category dashboard needs category metrics and market data before it can show movers, liquidity, and subcategory filters."
          actionLabel="Retry category"
          onAction={() => window.location.reload()}
          tone="error"
          badge="Unavailable"
        />
        <ApiModeHint />
      </div>
    );
  }

  const categoryMarkets = markets.filter((market) => market.categorySlug === category.slug);
  const subcategoryCounter = new Map<string, number>();
  categoryMarkets.forEach((market) => {
    subcategoryCounter.set(market.subcategory, (subcategoryCounter.get(market.subcategory) ?? 0) + 1);
  });
  const subcategoryCounts = [...subcategoryCounter.entries()].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]));
  const filteredMarkets = subcategory === "all" ? categoryMarkets : categoryMarkets.filter((market) => market.subcategory === subcategory);
  return (
    <div className="space-y-5">
      <CategoryNavigation categories={categories} marketsCount={markets.length} />

      <section className="border-b border-[var(--border)] pb-5">
        <div className="flex items-start justify-between gap-4">
          <div>
            <div className="mb-2 flex items-center gap-2">
              <Badge tone={category.risk === "LOW" ? "green" : category.risk === "MEDIUM" ? "blue" : "brass"}>{category.risk} risk</Badge>
              <Badge>{category.focus.join(" / ")}</Badge>
            </div>
            <h1 className="text-2xl font-semibold">{category.name}</h1>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-[var(--muted)]">{category.description}</p>
          </div>
          <CategoryIcon category={category} size="lg" />
        </div>
      </section>

      <div className="exchange-category-rail -mx-4 flex gap-1 overflow-x-auto px-4 pb-2 lg:hidden">
        <Button variant={subcategory === "all" ? "primary" : "secondary"} size="sm" onClick={() => setSubcategory("all")}>
          All
        </Button>
        {subcategoryCounts.map(([label, count]) => (
          <Button key={label} variant={subcategory === label ? "primary" : "secondary"} size="sm" onClick={() => setSubcategory(label)}>
            {label} ({count})
          </Button>
        ))}
      </div>

      <div className="grid gap-5 lg:grid-cols-[220px_1fr]">
        <aside className="hidden border-r border-[var(--border)] pr-4 lg:block lg:self-start">
          <div className="mb-3 flex items-center justify-between gap-2 text-sm">
            <h2 className="text-sm font-semibold">Subcategories</h2>
            <Badge tone="blue">{filteredMarkets.length}</Badge>
          </div>
          <div className="space-y-1">
            <button
              type="button"
              onClick={() => setSubcategory("all")}
              className={cn(
                "flex w-full items-center justify-between rounded-md px-2 py-2 text-left text-sm transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--ring)]",
                subcategory === "all" ? "bg-[var(--primary-soft)] text-[var(--primary-strong)]" : "text-[var(--muted)] hover:bg-[var(--surface-muted)] hover:text-[var(--foreground)]"
              )}
            >
              <span>All markets</span>
              <span className="numeric text-xs">{categoryMarkets.length}</span>
            </button>
            {subcategoryCounts.map(([label, count]) => (
              <button
                key={label}
                type="button"
                onClick={() => setSubcategory(label)}
                className={cn(
                  "flex w-full items-center justify-between rounded-md px-2 py-2 text-left text-sm transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--ring)]",
                  subcategory === label ? "bg-[var(--primary-soft)] text-[var(--primary-strong)]" : "text-[var(--muted)] hover:bg-[var(--surface-muted)] hover:text-[var(--foreground)]"
                )}
              >
                <span className="truncate">{label}</span>
                <span className="numeric ml-2 text-xs">{count}</span>
              </button>
            ))}
          </div>
        </aside>

        <div className="min-w-0 space-y-5">
          <section className="xl:hidden">
            <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
              <div>
                <h2 className="text-sm font-semibold">Active contracts</h2>
                <p className="mt-1 text-xs text-[var(--muted)]">Rows show outcomes, source, close time, spread, and liquidity.</p>
              </div>
              <Badge tone="green">{filteredMarkets.length} visible</Badge>
            </div>
            {filteredMarkets.length ? (
              <div className="xl:hidden">
                {filteredMarkets.map((market) => (
                <MarketCard key={market.id} market={market} categories={categories} compact />
                ))}
              </div>
            ) : (
              <DataState
                title="No markets in this subcategory yet"
                message="Choose another subcategory or return to all markets to compare the full category board."
                actionLabel="Show all markets"
                onAction={() => setSubcategory("all")}
                tone="empty"
              />
            )}
          </section>

          <section className="hidden xl:block">
            <div className="mb-3 flex items-center justify-between">
              <h2 className="text-sm font-semibold">Comparison table</h2>
              <span className="text-xs text-[var(--muted)]">Includes active, paused, and closing markets</span>
            </div>
            {filteredMarkets.length ? <MarketTable markets={filteredMarkets} categories={categories} /> : <div className="border-y border-[var(--border)] py-6 text-sm text-[var(--muted)]">No markets in this category yet.</div>}
          </section>
        </div>
      </div>
    </div>
  );
}
