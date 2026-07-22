import type { Category, CategoryRisk, ChartPoint, Market, OrderLevel, Position, UserOrder, WalletEntry } from "@/lib/mock-data";
import type { SessionUser, UserRole } from "@/lib/auth-session";

export type BackendUser = {
  id: string;
  email: string;
  display_name: string | null;
  status: string;
  roles: string[];
  email_verified_at: string | null;
  kyc_status: string;
  jurisdiction_code: string | null;
};

export type BackendImpersonation = {
  active: boolean;
  session_id: string;
  mode: "READ_ONLY";
  actor_user_id: string;
  target_user_id: string;
  started_at: string;
};

export type BackendAuthMe = {
  user: BackendUser;
  actor: BackendUser;
  impersonation: BackendImpersonation | null;
  mfa: BackendMfaStatus;
};

export type BackendMfaStatus = {
  enrolled: boolean;
  required: boolean;
  verified_for_session: boolean;
  factor_id: string | null;
  recovery_codes_remaining: number;
};

export type BackendCategory = {
  slug: string;
  name: string;
  short_name: string;
  description: string;
  active_markets: number;
  volume_24h: number;
  total_volume: number;
  risk: CategoryRisk;
  icon_tone: Category["iconTone"];
  focus: string[];
};

type BackendOutcome = {
  id?: string;
  label: string;
  price: number;
  probability: number;
};

export type BackendMarket = {
  id: string;
  title: string;
  category_slug: string;
  subcategory: string;
  market_type: Market["marketType"];
  status: string;
  close_time: string;
  source: string;
  rule_summary: string;
  probability: number;
  change_24h: number;
  volume_24h: number;
  total_volume: number;
  liquidity: number;
  spread: number;
  traders: number;
  outcomes: BackendOutcome[];
  risk_notes: string[];
  price_history?: ChartPoint[];
  order_book?: {
    yes_bids?: OrderLevel[];
    no_bids?: OrderLevel[];
  };
  recent_trades?: Array<{ time: string; outcome: string; price: number; quantity: number }>;
  watchlisted?: boolean;
  has_position?: boolean;
};

export type BackendOrder = {
  id: string;
  user_id: string;
  market_id: string;
  outcome_id: string;
  outcome: string;
  side: "BUY" | "SELL";
  price_minor: number;
  quantity: number;
  filled_quantity: number;
  cancelled_quantity: number;
  remaining_quantity: number;
  locked_cash_minor: number;
  locked_shares: number;
  status: string;
  created_at: string;
};

export type BackendAdminReview = {
  id: string;
  suggestion_id: string | null;
  draft_id?: string | null;
  market_id: string | null;
  title: string;
  category: string;
  status: string;
  risk: CategoryRisk;
  submitted_by: string;
  created_at: string;
  resolved_at: string | null;
};

export type AdminReview = {
  id: string;
  suggestionId: string | null;
  draftId: string | null;
  marketId: string | null;
  title: string;
  category: string;
  status: string;
  risk: CategoryRisk;
  submittedBy: string;
  createdAt: string;
  resolvedAt: string | null;
};

export type BackendDataSource = {
  id: string;
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
  status: string;
  health_status: string;
  last_checked_at: string | null;
  config: Record<string, unknown>;
  notes: string | null;
  created_at: string;
  updated_at: string;
};

export type DataSource = {
  id: string;
  name: string;
  provider: string;
  sourceType: string;
  categorySlug: string;
  baseUrl: string;
  licenseStatus: string;
  automationLevel: number;
  refreshSchedule: string;
  settlementEligible: boolean;
  discoveryEligible: boolean;
  status: string;
  healthStatus: string;
  lastCheckedAt: string | null;
  config: Record<string, unknown>;
  notes: string | null;
  createdAt: string;
  updatedAt: string;
};

export type BackendSourceEvent = {
  id: string;
  data_source_id: string;
  category_slug: string;
  title: string;
  url: string | null;
  published_at: string | null;
  source_timestamp: string | null;
  content_hash: string;
  dedupe_key: string;
  credibility_score: number;
  ingestion_status: string;
  ingested_at: string;
  created_at: string;
};

export type SourceEvent = {
  id: string;
  dataSourceId: string;
  categorySlug: string;
  title: string;
  url: string | null;
  publishedAt: string | null;
  sourceTimestamp: string | null;
  contentHash: string;
  dedupeKey: string;
  credibilityScore: number;
  ingestionStatus: string;
  ingestedAt: string;
  createdAt: string;
};

export type BackendMarketDraftEvidence = {
  id: string;
  source_event_id: string | null;
  data_source_id: string | null;
  title: string;
  url: string | null;
  evidence_type: string;
  snapshot: Record<string, unknown>;
  created_at: string;
};

export type BackendMarketDraft = {
  id: string;
  origin: "AI" | "ADMIN" | "TRADER" | string;
  created_by_user_id: string | null;
  suggestion_id: string | null;
  listed_market_id: string | null;
  category_slug: string;
  subcategory: string;
  market_type: string;
  question: string;
  outcomes: string[];
  close_time: string;
  source: string;
  resolution_rule: string;
  void_policy: string;
  settlement_source_id: string | null;
  discovery_source_id: string | null;
  status: string;
  checks: Record<string, { passed?: boolean; detail?: string }>;
  risk_flags: string[];
  ai_rationale: string | null;
  confidence_score: number | null;
  admin_notes: string | null;
  evidence: BackendMarketDraftEvidence[];
  created_at: string;
  updated_at: string;
};

export type MarketDraft = {
  id: string;
  origin: string;
  createdByUserId: string | null;
  suggestionId: string | null;
  listedMarketId: string | null;
  categorySlug: string;
  subcategory: string;
  marketType: string;
  question: string;
  outcomes: string[];
  closeTime: string;
  source: string;
  resolutionRule: string;
  voidPolicy: string;
  settlementSourceId: string | null;
  discoverySourceId: string | null;
  status: string;
  checks: Record<string, { passed?: boolean; detail?: string }>;
  riskFlags: string[];
  aiRationale: string | null;
  confidenceScore: number | null;
  adminNotes: string | null;
  evidence: Array<{
    id: string;
    sourceEventId: string | null;
    dataSourceId: string | null;
    title: string;
    url: string | null;
    evidenceType: string;
    snapshot: Record<string, unknown>;
    createdAt: string;
  }>;
  createdAt: string;
  updatedAt: string;
};

export type BackendMarketAnalytics = {
  market_id: string;
  outcome_metrics: Array<Record<string, unknown>>;
  best_bid: number | null;
  best_ask: number | null;
  last_trade: number | null;
  spread: number | null;
  volume_24h: number;
  total_volume: number;
  open_interest: number;
  liquidity_depth: number;
  price_change_24h: number;
  computed_at: string;
  is_stale: boolean;
};

export type MarketAnalytics = {
  marketId: string;
  outcomeMetrics: Array<Record<string, unknown>>;
  bestBid: number | null;
  bestAsk: number | null;
  lastTrade: number | null;
  spread: number | null;
  volume24h: number;
  totalVolume: number;
  openInterest: number;
  liquidityDepth: number;
  priceChange24h: number;
  computedAt: string;
  isStale: boolean;
};

export type BackendCategoryAnalytics = {
  category_slug: string;
  active_markets: number;
  volume_24h: number;
  top_markets: Array<Record<string, unknown>>;
  top_movers: Array<Record<string, unknown>>;
  average_spread: number | null;
  liquidity_depth: number;
  risk_alerts: string[];
  computed_at: string;
  is_stale: boolean;
};

export type CategoryAnalytics = {
  categorySlug: string;
  activeMarkets: number;
  volume24h: number;
  topMarkets: Array<Record<string, unknown>>;
  topMovers: Array<Record<string, unknown>>;
  averageSpread: number | null;
  liquidityDepth: number;
  riskAlerts: string[];
  computedAt: string;
  isStale: boolean;
};

export type BackendUserAnalytics = {
  user_id: string;
  available_cash: number;
  locked_cash: number;
  positions: Array<Record<string, unknown>>;
  category_exposure: Array<{ category_slug?: string; category?: string; exposure?: number; exposure_minor?: number }>;
  market_exposure: Array<Record<string, unknown>>;
  unrealized_pnl: number;
  realized_pnl: number;
  max_payout: number;
  max_loss: number;
  computed_at: string;
  is_stale: boolean;
};

export type UserAnalytics = {
  userId: string;
  availableCash: number;
  lockedCash: number;
  positions: Array<Record<string, unknown>>;
  categoryExposure: Array<{ categorySlug: string; exposure: number }>;
  marketExposure: Array<Record<string, unknown>>;
  unrealizedPnl: number;
  realizedPnl: number;
  maxPayout: number;
  maxLoss: number;
  computedAt: string;
  isStale: boolean;
};

export type BackendPosition = {
  id: string;
  market_id: string;
  outcome_id: string;
  outcome: string;
  quantity: number;
  locked_quantity: number;
  average_entry_price_minor: number;
  realized_pnl_minor: number;
  status: string;
};

export type BackendLedgerEntry = {
  id: string;
  transaction_id: string;
  account_type: string;
  side: string;
  amount_minor: number;
  currency: string;
  created_at: string;
};

export function mapUser(user: BackendUser, walletBalance = 0, mfa?: BackendMfaStatus): SessionUser {
  const resolvedMfa = mfa ?? {
    enrolled: false,
    required: false,
    verified_for_session: false,
    factor_id: null,
    recovery_codes_remaining: 0
  };
  return {
    id: user.id,
    email: user.email,
    displayName: user.display_name || user.email.split("@")[0],
    roles: user.roles as UserRole[],
    emailVerified: Boolean(user.email_verified_at),
    mfaVerified: resolvedMfa.verified_for_session,
    mfa: {
      enrolled: resolvedMfa.enrolled,
      required: resolvedMfa.required,
      verifiedForSession: resolvedMfa.verified_for_session,
      factorId: resolvedMfa.factor_id,
      recoveryCodesRemaining: resolvedMfa.recovery_codes_remaining
    },
    walletBalance,
    expiresAt: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString()
  };
}

export function mapAuthMe(payload: BackendAuthMe, walletBalance = 0): SessionUser {
  const user = mapUser(payload.user, walletBalance, payload.mfa);
  const actor = mapUser(payload.actor, walletBalance, payload.mfa);
  return {
    ...user,
    actor,
    impersonation: payload.impersonation
      ? {
          active: payload.impersonation.active,
          sessionId: payload.impersonation.session_id,
          mode: payload.impersonation.mode,
          actorUserId: payload.impersonation.actor_user_id,
          targetUserId: payload.impersonation.target_user_id,
          startedAt: payload.impersonation.started_at
        }
      : null
  };
}

export function mapCategory(category: BackendCategory): Category {
  return {
    slug: category.slug,
    name: category.name,
    shortName: category.short_name,
    description: category.description,
    activeMarkets: category.active_markets,
    volume24h: category.volume_24h,
    totalVolume: category.total_volume,
    risk: category.risk,
    iconTone: category.icon_tone,
    focus: category.focus
  };
}

export function mapMarket(market: BackendMarket): Market {
  return {
    id: market.id,
    title: market.title,
    categorySlug: market.category_slug,
    subcategory: market.subcategory,
    marketType: market.market_type,
    status: mapStatus(market.status),
    closeTime: market.close_time,
    source: market.source,
    ruleSummary: market.rule_summary,
    probability: market.probability,
    change24h: market.change_24h,
    volume24h: market.volume_24h,
    totalVolume: market.total_volume,
    liquidity: market.liquidity,
    spread: market.spread,
    traders: market.traders,
    watchlisted: Boolean(market.watchlisted),
    hasPosition: Boolean(market.has_position),
    outcomes: market.outcomes.map((outcome) => ({ id: outcome.id, label: outcome.label, price: outcome.price, probability: outcome.probability })),
    priceHistory: market.price_history || [],
    orderBook: {
      yesBids: market.order_book?.yes_bids || [],
      noBids: market.order_book?.no_bids || []
    },
    recentTrades: market.recent_trades || [],
    riskNotes: market.risk_notes
  };
}

export function mapOrder(order: BackendOrder): UserOrder {
  return {
    id: order.id,
    marketId: order.market_id,
    side: order.side === "BUY" ? "Buy" : "Sell",
    outcome: order.outcome,
    price: order.price_minor,
    quantity: order.quantity,
    filled: order.filled_quantity,
    status: order.status === "CANCELLED" || order.status === "PARTIALLY_CANCELLED" ? "Cancelled" : order.status === "FILLED" ? "Filled" : "Open",
    createdAt: order.created_at
  };
}

export function mapPosition(position: BackendPosition): Position {
  return {
    marketId: position.market_id,
    outcome: position.outcome,
    quantity: position.quantity,
    averageEntry: position.average_entry_price_minor,
    currentPrice: position.average_entry_price_minor,
    maxPayout: position.quantity * 100
  };
}

export function mapLedgerEntry(entry: BackendLedgerEntry): WalletEntry {
  const signedAmount = entry.side === "DEBIT" ? -entry.amount_minor : entry.amount_minor;
  return {
    id: entry.id,
    type: mapLedgerType(entry),
    amount: signedAmount,
    status: "Complete",
    createdAt: entry.created_at
  };
}

export function mapAdminReview(review: BackendAdminReview): AdminReview {
  return {
    id: review.id,
    suggestionId: review.suggestion_id,
    draftId: review.draft_id ?? null,
    marketId: review.market_id,
    title: review.title,
    category: review.category,
    status: review.status,
    risk: review.risk,
    submittedBy: review.submitted_by,
    createdAt: review.created_at,
    resolvedAt: review.resolved_at
  };
}

export function mapDataSource(source: BackendDataSource): DataSource {
  return {
    id: source.id,
    name: source.name,
    provider: source.provider,
    sourceType: source.source_type,
    categorySlug: source.category_slug,
    baseUrl: source.base_url,
    licenseStatus: source.license_status,
    automationLevel: source.automation_level,
    refreshSchedule: source.refresh_schedule,
    settlementEligible: source.settlement_eligible,
    discoveryEligible: source.discovery_eligible,
    status: source.status,
    healthStatus: source.health_status,
    lastCheckedAt: source.last_checked_at,
    config: source.config,
    notes: source.notes,
    createdAt: source.created_at,
    updatedAt: source.updated_at
  };
}

export function mapSourceEvent(event: BackendSourceEvent): SourceEvent {
  return {
    id: event.id,
    dataSourceId: event.data_source_id,
    categorySlug: event.category_slug,
    title: event.title,
    url: event.url,
    publishedAt: event.published_at,
    sourceTimestamp: event.source_timestamp,
    contentHash: event.content_hash,
    dedupeKey: event.dedupe_key,
    credibilityScore: event.credibility_score,
    ingestionStatus: event.ingestion_status,
    ingestedAt: event.ingested_at,
    createdAt: event.created_at
  };
}

export function mapMarketDraft(draft: BackendMarketDraft): MarketDraft {
  return {
    id: draft.id,
    origin: draft.origin,
    createdByUserId: draft.created_by_user_id,
    suggestionId: draft.suggestion_id,
    listedMarketId: draft.listed_market_id,
    categorySlug: draft.category_slug,
    subcategory: draft.subcategory,
    marketType: draft.market_type,
    question: draft.question,
    outcomes: draft.outcomes,
    closeTime: draft.close_time,
    source: draft.source,
    resolutionRule: draft.resolution_rule,
    voidPolicy: draft.void_policy,
    settlementSourceId: draft.settlement_source_id,
    discoverySourceId: draft.discovery_source_id,
    status: draft.status,
    checks: draft.checks,
    riskFlags: draft.risk_flags,
    aiRationale: draft.ai_rationale,
    confidenceScore: draft.confidence_score,
    adminNotes: draft.admin_notes,
    evidence: draft.evidence.map((item) => ({
      id: item.id,
      sourceEventId: item.source_event_id,
      dataSourceId: item.data_source_id,
      title: item.title,
      url: item.url,
      evidenceType: item.evidence_type,
      snapshot: item.snapshot,
      createdAt: item.created_at
    })),
    createdAt: draft.created_at,
    updatedAt: draft.updated_at
  };
}

export function mapMarketAnalytics(analytics: BackendMarketAnalytics): MarketAnalytics {
  return {
    marketId: analytics.market_id,
    outcomeMetrics: analytics.outcome_metrics,
    bestBid: analytics.best_bid,
    bestAsk: analytics.best_ask,
    lastTrade: analytics.last_trade,
    spread: analytics.spread,
    volume24h: analytics.volume_24h,
    totalVolume: analytics.total_volume,
    openInterest: analytics.open_interest,
    liquidityDepth: analytics.liquidity_depth,
    priceChange24h: analytics.price_change_24h,
    computedAt: analytics.computed_at,
    isStale: analytics.is_stale
  };
}

export function mapCategoryAnalytics(analytics: BackendCategoryAnalytics): CategoryAnalytics {
  return {
    categorySlug: analytics.category_slug,
    activeMarkets: analytics.active_markets,
    volume24h: analytics.volume_24h,
    topMarkets: analytics.top_markets,
    topMovers: analytics.top_movers,
    averageSpread: analytics.average_spread,
    liquidityDepth: analytics.liquidity_depth,
    riskAlerts: analytics.risk_alerts,
    computedAt: analytics.computed_at,
    isStale: analytics.is_stale
  };
}

export function mapUserAnalytics(analytics: BackendUserAnalytics): UserAnalytics {
  return {
    userId: analytics.user_id,
    availableCash: analytics.available_cash,
    lockedCash: analytics.locked_cash,
    positions: analytics.positions,
    categoryExposure: analytics.category_exposure.map((item) => ({
      categorySlug: item.category_slug ?? item.category ?? "unknown",
      exposure: item.exposure_minor ?? item.exposure ?? 0
    })),
    marketExposure: analytics.market_exposure,
    unrealizedPnl: analytics.unrealized_pnl,
    realizedPnl: analytics.realized_pnl,
    maxPayout: analytics.max_payout,
    maxLoss: analytics.max_loss,
    computedAt: analytics.computed_at,
    isStale: analytics.is_stale
  };
}

function mapStatus(status: string): Market["status"] {
  if (status === "PAUSED") return "Paused";
  if (status === "PENDING_RESOLUTION" || status === "CLOSED") return "Pending resolution";
  return "Open";
}

function mapLedgerType(entry: BackendLedgerEntry): WalletEntry["type"] {
  if (entry.account_type.includes("LOCKED")) return entry.side === "DEBIT" ? "Order release" : "Order lock";
  if (entry.account_type.includes("COLLATERAL")) return "Trade collateral";
  if (entry.account_type === "USER_AVAILABLE_CASH" && entry.side === "DEBIT") return "Order lock";
  return "Deposit";
}
