"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Flame } from "lucide-react";
import { IdentityIcon } from "@/components/identity-icon";
import { getCategoryIdentity } from "@/lib/market-identities";
import type { Category } from "@/lib/mock-data";
import { cn, formatCompact } from "@/lib/utils";

type CategoryNavigationProps = {
  categories: Category[];
  selectedCategory?: string;
  onCategoryChange?: (category: string) => void;
  marketsCount?: number;
};

export function CategoryNavigation({ categories, selectedCategory, onCategoryChange, marketsCount = 0 }: CategoryNavigationProps) {
  const pathname = usePathname();
  const activeSlug = selectedCategory ?? (pathname.startsWith("/categories/") ? pathname.split("/")[2] : "all");
  const itemClass = (active: boolean) =>
    cn(
      "inline-flex h-11 shrink-0 items-center gap-2 rounded-md px-2.5 text-sm font-medium transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--ring)]",
      active ? "bg-[var(--primary-soft)] text-[var(--primary-strong)]" : "text-[var(--muted)] hover:bg-[var(--surface-muted)]/64 hover:text-[var(--foreground)]"
    );

  const allButton = (
    <span className={itemClass(activeSlug === "all")}>
      <span className="grid h-7 w-7 place-items-center rounded-full bg-[var(--surface-muted)] text-[var(--primary-strong)]">
        <Flame className="h-3.5 w-3.5" />
      </span>
      Trending
      <span className="numeric text-xs text-[var(--muted)]">{formatCompact(marketsCount)}</span>
    </span>
  );

  return (
    <nav className="sticky top-[61px] z-[var(--z-sticky)] -mx-4 overflow-x-auto border-b border-[color-mix(in_srgb,var(--border)_45%,transparent)] bg-[color-mix(in_srgb,var(--background)_92%,transparent)] px-4 py-2 backdrop-blur lg:-mx-8 lg:px-8" aria-label="Market categories">
      <div className="mx-auto flex max-w-[1680px] gap-1">
        {onCategoryChange ? (
          <button type="button" onClick={() => onCategoryChange("all")}>
            {allButton}
          </button>
        ) : (
          <Link href="/markets">{allButton}</Link>
        )}
        {categories.map((category) => {
          const active = activeSlug === category.slug;
          const content = (
            <span className={itemClass(active)}>
              <IdentityIcon identity={getCategoryIdentity(category)} size="sm" />
              {category.shortName}
              <span className="numeric text-xs text-[var(--muted)]">{formatCompact(category.volume24h)}</span>
            </span>
          );

          return onCategoryChange ? (
            <button key={category.slug} type="button" onClick={() => onCategoryChange(category.slug)}>
              {content}
            </button>
          ) : (
            <Link key={category.slug} href={`/categories/${category.slug}`}>
              {content}
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
