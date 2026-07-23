"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiRequest, USE_MOCK_DATA } from "@/lib/api-client";
import {
  mapAdminReview,
  mapCategory,
  mapCategoryAnalytics,
  mapDataSource,
  mapLedgerEntry,
  mapMarket,
  mapMarketAnalytics,
  mapMarketDraft,
  mapOrder,
  mapPosition,
  mapSourceEvent,
  mapUserAnalytics,
  type BackendAdminReview,
  type BackendCategory,
  type BackendCategoryAnalytics,
  type BackendDataSource,
  type BackendLedgerEntry,
  type BackendMarket,
  type BackendMarketAnalytics,
  type BackendMarketDraft,
  type BackendOrder,
  type BackendPosition,
  type BackendSourceEvent,
  type BackendUserAnalytics
} from "@/lib/api-mappers";
import { adminQueue, categories, getMarket, markets, positions, userOrders, walletEntries, type WalletEntry } from "@/lib/mock-data";

function mapMockAdminReview(item: (typeof adminQueue)[number]) {
  return {
    ...item,
    suggestionId: null,
    draftId: null,
    marketId: item.id === "REV-221" ? "blr-rain-20mm" : item.id === "REV-220" ? "rbi-rate-hold" : null,
    createdAt: "2026-07-10T09:00:00.000Z",
    resolvedAt: null
  };
}

const mockDataSources = [
  {
    id: "SRC-MOCK-SPORTS",
    name: "ICC official fixtures and results",
    provider: "ICC",
    sourceType: "OFFICIAL",
    categorySlug: "sports",
    baseUrl: "https://www.icc-cricket.com/fixtures-results",
    licenseStatus: "PUBLIC_OFFICIAL",
    automationLevel: 1,
    refreshSchedule: "DAILY",
    settlementEligible: true,
    discoveryEligible: true,
    status: "ACTIVE",
    healthStatus: "PASS",
    lastCheckedAt: new Date().toISOString(),
    config: {},
    notes: "Official sports source for mock review.",
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  },
  {
    id: "SRC-MOCK-GDELT",
    name: "GDELT global events",
    provider: "GDELT",
    sourceType: "NEWS_DISCOVERY",
    categorySlug: "tech-science",
    baseUrl: "https://www.gdeltproject.org/",
    licenseStatus: "DISCOVERY_ONLY",
    automationLevel: 1,
    refreshSchedule: "INTRADAY",
    settlementEligible: false,
    discoveryEligible: true,
    status: "ACTIVE",
    healthStatus: "UNKNOWN",
    lastCheckedAt: null,
    config: {},
    notes: "Discovery only.",
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  }
];

const mockSourceEvents = [
  {
    id: "EVS-MOCK-1",
    dataSourceId: "SRC-MOCK-GDELT",
    categorySlug: "tech-science",
    title: "Official technology/science announcement watch: frontier AI releases",
    url: "https://www.gdeltproject.org/",
    publishedAt: new Date().toISOString(),
    sourceTimestamp: new Date().toISOString(),
    contentHash: "mock",
    dedupeKey: "mock",
    credibilityScore: 70,
    ingestionStatus: "INGESTED",
    ingestedAt: new Date().toISOString(),
    createdAt: new Date().toISOString()
  }
];

const mockMarketDrafts = [
  {
    id: "DRF-MOCK-1",
    origin: "AI",
    createdByUserId: null,
    suggestionId: null,
    listedMarketId: null,
    categorySlug: "tech-science",
    subcategory: "AI candidate",
    marketType: "Binary",
    question: "Will a frontier AI lab release a new public model before October?",
    outcomes: ["YES", "NO"],
    closeTime: "Sep 30, 2026 23:59 UTC",
    source: "Official company announcement",
    resolutionRule: "YES resolves if an approved frontier lab publicly releases a qualifying model.",
    voidPolicy: "Void only if approved source is unavailable.",
    settlementSourceId: null,
    discoverySourceId: "SRC-MOCK-GDELT",
    status: "NEEDS_REVIEW",
    checks: {
      category_allowed: { passed: true, detail: "Category exists." },
      settlement_source_approved: { passed: false, detail: "Approved settlement source is required before listing." }
    },
    riskFlags: ["No approved settlement source is attached."],
    aiRationale: "Generated from discovery-source event and needs admin source confirmation.",
    confidenceScore: 78,
    adminNotes: null,
    evidence: [],
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  }
];

export function useMarkets(params: { category?: string; status?: string; q?: string } = {}) {
  return useQuery({
    queryKey: ["markets", params],
    queryFn: async () => {
      if (USE_MOCK_DATA) return markets;
      const search = new URLSearchParams();
      if (params.category && params.category !== "all") search.set("category", params.category);
      if (params.status && params.status !== "all") search.set("status", params.status.toUpperCase().replaceAll(" ", "_"));
      if (params.q) search.set("q", params.q);
      const suffix = search.size ? `?${search.toString()}` : "";
      const payload = await apiRequest<{ items: BackendMarket[] }>(`/api/v1/markets${suffix}`);
      return payload.items.map(mapMarket);
    }
  });
}

export function useMarket(marketId: string) {
  return useQuery({
    queryKey: ["market", marketId],
    enabled: Boolean(marketId),
    queryFn: async () => {
      if (USE_MOCK_DATA) return getMarket(marketId) ?? null;
      return mapMarket(await apiRequest<BackendMarket>(`/api/v1/markets/${marketId}`));
    }
  });
}

export function useMarketAnalytics(marketId: string) {
  return useQuery({
    queryKey: ["analytics", "market", marketId],
    enabled: Boolean(marketId),
    queryFn: async () => {
      if (USE_MOCK_DATA) {
        const market = getMarket(marketId);
        return {
          marketId,
          outcomeMetrics: market?.outcomes.map((outcome) => ({ outcome: outcome.label, probability: outcome.probability })) ?? [],
          bestBid: market?.orderBook.yesBids[0]?.price ?? null,
          bestAsk: market ? 100 - (market.orderBook.noBids[0]?.price ?? 0) : null,
          lastTrade: market?.recentTrades[0]?.price ?? null,
          spread: market?.spread ?? null,
          volume24h: market?.volume24h ?? 0,
          totalVolume: market?.totalVolume ?? 0,
          openInterest: market?.traders ?? 0,
          liquidityDepth: market?.liquidity ?? 0,
          priceChange24h: market?.change24h ?? 0,
          computedAt: new Date().toISOString(),
          isStale: false
        };
      }
      return mapMarketAnalytics(await apiRequest<BackendMarketAnalytics>(`/api/v1/analytics/markets/${marketId}`));
    }
  });
}

export function useCategories() {
  return useQuery({
    queryKey: ["categories"],
    queryFn: async () => {
      if (USE_MOCK_DATA) return categories;
      const payload = await apiRequest<{ items: BackendCategory[] }>("/api/v1/categories");
      return payload.items.map(mapCategory);
    }
  });
}

export function useCategory(categorySlug: string) {
  return useQuery({
    queryKey: ["category", categorySlug],
    queryFn: async () => {
      if (USE_MOCK_DATA) return categories.find((item) => item.slug === categorySlug) ?? null;
      return mapCategory(await apiRequest<BackendCategory>(`/api/v1/categories/${categorySlug}`));
    }
  });
}

export function useCategoryAnalytics(categorySlug: string) {
  return useQuery({
    queryKey: ["analytics", "category", categorySlug],
    enabled: Boolean(categorySlug),
    queryFn: async () => {
      if (USE_MOCK_DATA) {
        const categoryMarkets = markets.filter((item) => item.categorySlug === categorySlug);
        return {
          categorySlug,
          activeMarkets: categoryMarkets.length,
          volume24h: categoryMarkets.reduce((sum, item) => sum + item.volume24h, 0),
          topMarkets: categoryMarkets.slice(0, 3),
          topMovers: [...categoryMarkets].sort((a, b) => Math.abs(b.change24h) - Math.abs(a.change24h)).slice(0, 3),
          averageSpread: categoryMarkets.length ? categoryMarkets.reduce((sum, item) => sum + item.spread, 0) / categoryMarkets.length : null,
          liquidityDepth: categoryMarkets.reduce((sum, item) => sum + item.liquidity, 0),
          riskAlerts: [],
          computedAt: new Date().toISOString(),
          isStale: false
        };
      }
      return mapCategoryAnalytics(await apiRequest<BackendCategoryAnalytics>(`/api/v1/analytics/categories/${categorySlug}`));
    }
  });
}

export function usePortfolioData() {
  return useQuery({
    queryKey: ["portfolio"],
    queryFn: async () => {
      if (USE_MOCK_DATA) return { positions };
      const payload = await apiRequest<{ positions: BackendPosition[] }>("/api/v1/portfolio");
      return { ...payload, positions: payload.positions.map(mapPosition) };
    }
  });
}

export function useUserAnalytics() {
  return useQuery({
    queryKey: ["analytics", "user", "me"],
    queryFn: async () => {
      if (USE_MOCK_DATA) {
        const invested = positions.reduce((sum, position) => sum + position.averageEntry * position.quantity, 0);
        const currentValue = positions.reduce((sum, position) => sum + position.currentPrice * position.quantity, 0);
        return {
          userId: "mock-user",
          availableCash: 84220,
          lockedCash: 9730,
          positions: [],
          categoryExposure: [],
          marketExposure: [],
          unrealizedPnl: currentValue - invested,
          realizedPnl: 0,
          maxPayout: positions.reduce((sum, position) => sum + position.maxPayout, 0),
          maxLoss: invested,
          computedAt: new Date().toISOString(),
          isStale: false
        };
      }
      return mapUserAnalytics(await apiRequest<BackendUserAnalytics>("/api/v1/analytics/users/me"));
    }
  });
}

export function useOrdersData() {
  return useQuery({
    queryKey: ["orders"],
    queryFn: async () => {
      if (USE_MOCK_DATA) return { items: userOrders };
      const payload = await apiRequest<{ items: BackendOrder[] }>("/api/v1/orders");
      return { items: payload.items.map(mapOrder) };
    }
  });
}

export function useWalletData(enabled = true) {
  return useQuery({
    queryKey: ["wallet"],
    enabled,
    queryFn: async () => {
      if (USE_MOCK_DATA) {
        return {
          available: 84220,
          locked: 9730,
          entries: walletEntries as WalletEntry[]
        };
      }
      const [wallet, ledger] = await Promise.all([
        apiRequest<{ available: { amount_minor: number }; locked: { amount_minor: number }; total: { amount_minor: number } }>("/api/v1/wallet"),
        apiRequest<{ items: BackendLedgerEntry[] }>("/api/v1/wallet/ledger")
      ]);
      return {
        available: wallet.available.amount_minor,
        locked: wallet.locked.amount_minor,
        total: wallet.total.amount_minor,
        entries: ledger.items.filter((entry) => entry.account_type === "USER_AVAILABLE_CASH").map(mapLedgerEntry)
      };
    }
  });
}

export function useWatchlistData() {
  return useQuery({
    queryKey: ["watchlist"],
    queryFn: async () => {
      if (USE_MOCK_DATA) return { items: markets.filter((market) => market.watchlisted) };
      const payload = await apiRequest<{ items: BackendMarket[] }>("/api/v1/watchlist");
      return { items: payload.items.map((item) => ({ ...mapMarket(item), watchlisted: true })) };
    }
  });
}

export function useAddWatchlistItem() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (marketId: string) => apiRequest(`/api/v1/watchlist/${marketId}`, { method: "POST" }),
    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ["watchlist"] }),
        queryClient.invalidateQueries({ queryKey: ["markets"] })
      ]);
    }
  });
}

export function useRemoveWatchlistItem() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (marketId: string) => apiRequest(`/api/v1/watchlist/${marketId}`, { method: "DELETE" }),
    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ["watchlist"] }),
        queryClient.invalidateQueries({ queryKey: ["markets"] })
      ]);
    }
  });
}

export function useCreateOrder() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: { market_id: string; outcome_id?: string; outcome?: string; side: "BUY" | "SELL"; price_minor: number; quantity: number }) => {
      return apiRequest<BackendOrder>("/api/v1/orders", {
        method: "POST",
        body: JSON.stringify(payload),
        idempotencyKey: crypto.randomUUID()
      });
    },
    onSuccess: async (order) => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ["orders"] }),
        queryClient.invalidateQueries({ queryKey: ["wallet"] }),
        queryClient.invalidateQueries({ queryKey: ["portfolio"] }),
        queryClient.invalidateQueries({ queryKey: ["market", order.market_id] })
      ]);
    }
  });
}

export function useCancelOrder() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (orderId: string) => apiRequest<BackendOrder>(`/api/v1/orders/${orderId}/cancel`, { method: "POST" }),
    onSuccess: async (order) => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ["orders"] }),
        queryClient.invalidateQueries({ queryKey: ["wallet"] }),
        queryClient.invalidateQueries({ queryKey: ["market", order.market_id] })
      ]);
    }
  });
}

export function useTestDeposit() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (amountMinor: number) =>
      apiRequest("/api/v1/wallet/test-deposit", {
        method: "POST",
        body: JSON.stringify({ amount_minor: amountMinor, currency: "INR" }),
        idempotencyKey: crypto.randomUUID()
      }),
    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ["wallet"] }),
        queryClient.invalidateQueries({ queryKey: ["portfolio"] })
      ]);
    }
  });
}

export function useAdminReviews() {
  return useQuery({
    queryKey: ["admin-reviews"],
    queryFn: async () => {
      if (USE_MOCK_DATA) return adminQueue.map(mapMockAdminReview);
      const payload = await apiRequest<{ items: BackendAdminReview[] }>("/api/v1/admin/markets/review");
      return payload.items.map(mapAdminReview);
    }
  });
}

export function useAdminReview(reviewId: string) {
  return useQuery({
    queryKey: ["admin-review", reviewId],
    enabled: Boolean(reviewId),
    queryFn: async () => {
      if (USE_MOCK_DATA) {
        const item = adminQueue.find((review) => review.id === reviewId);
        return item ? mapMockAdminReview(item) : null;
      }
      return mapAdminReview(await apiRequest<BackendAdminReview>(`/api/v1/admin/markets/review/${reviewId}`));
    }
  });
}

export function useAdminDataSources(params: { categorySlug?: string } = {}) {
  return useQuery({
    queryKey: ["admin-data-sources", params],
    queryFn: async () => {
      if (USE_MOCK_DATA) return params.categorySlug ? mockDataSources.filter((item) => item.categorySlug === params.categorySlug) : mockDataSources;
      const search = new URLSearchParams();
      if (params.categorySlug) search.set("category_slug", params.categorySlug);
      const suffix = search.size ? `?${search.toString()}` : "";
      const payload = await apiRequest<{ items: BackendDataSource[] }>(`/api/v1/admin/data-sources${suffix}`);
      return payload.items.map(mapDataSource);
    }
  });
}

export function useAdminSourceEvents(params: { categorySlug?: string } = {}) {
  return useQuery({
    queryKey: ["admin-source-events", params],
    queryFn: async () => {
      if (USE_MOCK_DATA) return params.categorySlug ? mockSourceEvents.filter((item) => item.categorySlug === params.categorySlug) : mockSourceEvents;
      const search = new URLSearchParams();
      if (params.categorySlug) search.set("category_slug", params.categorySlug);
      const suffix = search.size ? `?${search.toString()}` : "";
      const payload = await apiRequest<{ items: BackendSourceEvent[] }>(`/api/v1/admin/source-events${suffix}`);
      return payload.items.map(mapSourceEvent);
    }
  });
}

export function useAdminMarketDrafts(params: { status?: string; origin?: string } = {}) {
  return useQuery({
    queryKey: ["admin-market-drafts", params],
    queryFn: async () => {
      if (USE_MOCK_DATA) return mockMarketDrafts.filter((item) => (!params.status || item.status === params.status) && (!params.origin || item.origin === params.origin));
      const search = new URLSearchParams();
      if (params.status) search.set("status", params.status);
      if (params.origin) search.set("origin", params.origin);
      const suffix = search.size ? `?${search.toString()}` : "";
      const payload = await apiRequest<{ items: BackendMarketDraft[] }>(`/api/v1/admin/market-drafts${suffix}`);
      return payload.items.map(mapMarketDraft);
    }
  });
}

export function useAdminCreateDataSource() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: {
      name: string;
      provider: string;
      source_type: string;
      category_slug: string;
      base_url: string;
      license_status: string;
      automation_level: number;
      refresh_schedule: string;
      settlement_eligible: boolean;
      discovery_eligible: boolean;
      notes?: string;
    }) => apiRequest<BackendDataSource>("/api/v1/admin/data-sources", { method: "POST", body: JSON.stringify(payload) }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["admin-data-sources"] });
    }
  });
}

export function useAdminRunIngestion() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: { source_id?: string; category_slug?: string; query?: string; limit?: number }) =>
      apiRequest<{ status: string; created_events: number; skipped_duplicates: number; items: BackendSourceEvent[] }>("/api/v1/admin/ingestion-runs", {
        method: "POST",
        body: JSON.stringify(payload)
      }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["admin-source-events"] });
    }
  });
}

export function useAdminGenerateAiDrafts() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: { source_event_id?: string; category_slug?: string; limit?: number }) =>
      apiRequest<{ status: string; created_drafts: number; items: BackendMarketDraft[] }>("/api/v1/admin/ai-market-generation/run", {
        method: "POST",
        body: JSON.stringify(payload)
      }),
    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ["admin-market-drafts"] }),
        queryClient.invalidateQueries({ queryKey: ["admin-reviews"] })
      ]);
    }
  });
}

export function useAdminCreateMarketDraft() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: {
      origin: "ADMIN";
      category_slug: string;
      subcategory: string;
      market_type: string;
      question: string;
      outcomes: string[];
      close_time: string;
      source: string;
      resolution_rule: string;
      void_policy: string;
      settlement_source_id?: string;
      discovery_source_id?: string;
      admin_notes?: string;
      list_immediately?: boolean;
    }) => apiRequest<BackendMarketDraft>("/api/v1/admin/market-drafts", { method: "POST", body: JSON.stringify(payload) }),
    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ["admin-market-drafts"] }),
        queryClient.invalidateQueries({ queryKey: ["admin-reviews"] }),
        queryClient.invalidateQueries({ queryKey: ["markets"] })
      ]);
    }
  });
}

export function useAdminMarketDraftAction(action: "approve" | "reject" | "list") {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (draftId: string) => apiRequest(`/api/v1/admin/market-drafts/${draftId}/${action}`, { method: "POST" }),
    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ["admin-market-drafts"] }),
        queryClient.invalidateQueries({ queryKey: ["admin-reviews"] }),
        queryClient.invalidateQueries({ queryKey: ["markets"] })
      ]);
    }
  });
}

export function useAdminMarketAction(action: "approve" | "pause") {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (marketId: string) => apiRequest(`/api/v1/admin/markets/${marketId}/${action}`, { method: "POST" }),
    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ["admin-reviews"] }),
        queryClient.invalidateQueries({ queryKey: ["markets"] })
      ]);
    }
  });
}

export function useSuggestMarket() {
  return useMutation({
    mutationFn: async (payload: { category_slug: string; market_type: string; question: string; outcomes: string[]; source: string; resolution_rule: string }) =>
      apiRequest("/api/v1/market-suggestions", {
        method: "POST",
        body: JSON.stringify(payload)
      })
  });
}
