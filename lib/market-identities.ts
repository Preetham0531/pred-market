import type { Category, Market, Outcome } from "@/lib/mock-data";

export type MarketIdentity = {
  kind: "flag" | "category" | "entity" | "fallback";
  code?: string;
  src?: string;
  label: string;
};

const categoryIconSrc: Record<string, string> = {
  sports: "/icons/3d/sports.svg",
  politics: "/icons/3d/politics.svg",
  economics: "/icons/3d/economics.svg",
  "stocks-mutual-funds": "/icons/3d/stocks-mutual-funds.svg",
  financials: "/icons/3d/financials.svg",
  "weather-climate": "/icons/3d/weather-climate.svg",
  culture: "/icons/3d/culture.svg",
  "tech-science": "/icons/3d/tech-science.svg",
  mentions: "/icons/3d/mentions.svg",
  commodities: "/icons/3d/commodities.svg"
};

const outcomeIdentityMap: Record<string, Record<string, MarketIdentity>> = {
  "ind-aus-final": {
    YES: { kind: "flag", code: "in", src: "/icons/flags/in.svg", label: "India" },
    NO: { kind: "flag", code: "au", src: "/icons/flags/au.svg", label: "Australia" }
  }
};

const marketEntityMap: Record<string, MarketIdentity> = {
  "ai-model-release": { kind: "entity", src: "/icons/3d/tech-science.svg", label: "AI release" },
  "cpi-above-4": { kind: "entity", src: "/icons/3d/economics.svg", label: "Inflation" },
  "mumbai-rainfall-range": { kind: "entity", src: "/icons/3d/weather-climate.svg", label: "Rainfall" },
  "gold-above-2500": { kind: "entity", src: "/icons/3d/commodities.svg", label: "Gold" },
  "film-award-winner": { kind: "entity", src: "/icons/3d/culture.svg", label: "Awards" }
};

export function getCategoryIdentity(category?: Pick<Category, "slug" | "shortName"> | null): MarketIdentity {
  if (!category) return { kind: "fallback", src: "/icons/3d/market.svg", label: "Market" };
  return {
    kind: "category",
    src: categoryIconSrc[category.slug] ?? "/icons/3d/market.svg",
    label: category.shortName
  };
}

export function getMarketIdentity(market: Pick<Market, "id" | "categorySlug">, category?: Pick<Category, "slug" | "shortName"> | null): MarketIdentity {
  return marketEntityMap[market.id] ?? getCategoryIdentity(category ?? { slug: market.categorySlug, shortName: market.categorySlug });
}

export function getOutcomeIdentity(market: Pick<Market, "id" | "categorySlug">, outcome: Pick<Outcome, "label">, category?: Pick<Category, "slug" | "shortName"> | null): MarketIdentity {
  return outcomeIdentityMap[market.id]?.[outcome.label.toUpperCase()] ?? getMarketIdentity(market, category);
}
