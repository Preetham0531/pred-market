"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { ChevronRight } from "lucide-react";
import { useCategories, useMarket } from "@/lib/api-hooks";
import { slugToLabel } from "@/lib/utils";

type Crumb = {
  label: string;
  href?: string;
};

function buildCrumbs(pathname: string, marketTitle?: string, marketCategorySlug?: string, marketSubcategory?: string, categoryName?: string): Crumb[] {
  if (pathname === "/") return [{ label: "Markets", href: "/markets" }];
  if (pathname === "/markets") return [{ label: "Markets" }];
  if (pathname === "/markets/suggest") {
    return [
      { label: "Markets", href: "/markets" },
      { label: "Suggest market" },
      { label: "Resolution rules" }
    ];
  }
  if (pathname.startsWith("/markets/")) {
    const id = pathname.split("/")[2];
    return [
      { label: "Markets", href: "/markets" },
      ...(categoryName && marketCategorySlug ? [{ label: categoryName, href: `/categories/${marketCategorySlug}` }] : []),
      ...(marketSubcategory ? [{ label: marketSubcategory }] : []),
      { label: marketTitle ?? slugToLabel(id) }
    ];
  }
  if (pathname.startsWith("/categories/")) {
    const slug = pathname.split("/")[2];
    return [
      { label: "Markets", href: "/markets" },
      { label: categoryName ?? slugToLabel(slug) }
    ];
  }
  if (pathname === "/admin") {
    return [
      { label: "Admin" },
      { label: "Market review" },
      { label: "Pending approval" }
    ];
  }
  if (pathname.startsWith("/admin/markets/")) {
    return [
      { label: "Admin", href: "/admin" },
      { label: "Market review", href: "/admin" },
      { label: "Review detail" }
    ];
  }

  const label = slugToLabel(pathname.replace("/", ""));
  return [{ label }];
}

export function Breadcrumbs() {
  const pathname = usePathname();
  const marketId = pathname.startsWith("/markets/") && pathname !== "/markets/suggest" ? pathname.split("/")[2] : "";
  const categorySlug = pathname.startsWith("/categories/") ? pathname.split("/")[2] : "";
  const { data: market } = useMarket(marketId);
  const { data: categories = [] } = useCategories();
  const category = categories.find((item) => item.slug === (market?.categorySlug ?? categorySlug));
  const crumbs = buildCrumbs(pathname, market?.title, market?.categorySlug, market?.subcategory, category?.name);
  const mobileCrumbs = crumbs.length > 1 ? [crumbs[0], crumbs[crumbs.length - 1]] : crumbs;

  return (
    <nav aria-label="Breadcrumb" className="min-w-0">
      <ol className="hidden min-w-0 items-center gap-1 text-xs text-[var(--muted)] sm:flex">
        {crumbs.map((crumb, index) => {
          const isLast = index === crumbs.length - 1;

          return (
            <li key={`${crumb.label}-${index}`} className="flex min-w-0 items-center gap-1">
              {index > 0 ? <ChevronRight className="h-3.5 w-3.5 shrink-0" /> : null}
              {crumb.href && !isLast ? (
                <Link className="truncate hover:text-[var(--foreground)]" href={crumb.href}>
                  {crumb.label}
                </Link>
              ) : (
                <span className="truncate text-[var(--foreground)]">{crumb.label}</span>
              )}
            </li>
          );
        })}
      </ol>
      <ol className="flex min-w-0 items-center gap-1 text-xs text-[var(--muted)] sm:hidden">
        {mobileCrumbs.map((crumb, index) => {
          const isLast = index === mobileCrumbs.length - 1;

          return (
            <li key={`${crumb.label}-mobile-${index}`} className="flex min-w-0 items-center gap-1">
              {index > 0 ? <ChevronRight className="h-3.5 w-3.5 shrink-0" /> : null}
              {crumb.href && !isLast ? (
                <Link className="shrink-0 hover:text-[var(--foreground)]" href={crumb.href}>
                  {crumb.label}
                </Link>
              ) : (
                <span className="truncate text-[var(--foreground)]">{crumb.label}</span>
              )}
            </li>
          );
        })}
      </ol>
    </nav>
  );
}
