export type CategoryRisk = "LOW" | "MEDIUM" | "HIGH" | "RESTRICTED";

export type Category = {
  slug: string;
  name: string;
  shortName: string;
  description: string;
  activeMarkets: number;
  volume24h: number;
  totalVolume: number;
  risk: CategoryRisk;
  iconTone: "green" | "blue" | "brass" | "red" | "violet" | "aqua";
  focus: string[];
};

export type Outcome = {
  id?: string;
  label: string;
  price: number;
  probability: number;
};

export type ChartPoint = {
  time: string;
  value: number;
  volume: number;
};

export type OrderLevel = {
  price: number;
  quantity: number;
};

export type Market = {
  id: string;
  title: string;
  categorySlug: string;
  subcategory: string;
  marketType: "Binary" | "Multiple-choice" | "Range" | "Threshold" | "Conditional" | "Combo";
  status: "Open" | "Paused" | "Closing soon" | "Pending resolution";
  closeTime: string;
  source: string;
  ruleSummary: string;
  probability: number;
  change24h: number;
  volume24h: number;
  totalVolume: number;
  liquidity: number;
  spread: number;
  quote?: {
    yesBid: number | null;
    yesAsk: number | null;
    noBid: number | null;
    noAsk: number | null;
    lastTrade: number | null;
    spread: number | null;
  };
  traders: number;
  watchlisted: boolean;
  hasPosition: boolean;
  outcomes: Outcome[];
  priceHistory: ChartPoint[];
  orderBook: {
    yesBids: OrderLevel[];
    noBids: OrderLevel[];
  };
  recentTrades: Array<{
    time: string;
    outcome: string;
    price: number;
    quantity: number;
  }>;
  riskNotes: string[];
};

export type Position = {
  marketId: string;
  outcome: string;
  quantity: number;
  averageEntry: number;
  currentPrice: number;
  maxPayout: number;
};

export type UserOrder = {
  id: string;
  marketId: string;
  side: "Buy" | "Sell";
  outcome: string;
  price: number;
  quantity: number;
  filled: number;
  remaining?: number;
  status: "Open" | "Partially filled" | "Filled" | "Cancelled";
  createdAt: string;
};

export type WalletEntry = {
  id: string;
  type: "Deposit" | "Order lock" | "Order release" | "Trade collateral" | "Settlement credit";
  amount: number;
  status: "Complete" | "Pending";
  createdAt: string;
};

export const categories: Category[] = [
  {
    slug: "sports",
    name: "Sports",
    shortName: "Sports",
    description: "Structured markets around matches, tournaments, milestones, and standings.",
    activeMarkets: 48,
    volume24h: 12400000,
    totalVolume: 188000000,
    risk: "MEDIUM",
    iconTone: "green",
    focus: ["Cricket", "Football", "Tennis", "Tournaments"]
  },
  {
    slug: "politics",
    name: "Politics",
    shortName: "Politics",
    description: "Election, policy, appointment, and public decision markets with strict review.",
    activeMarkets: 12,
    volume24h: 3200000,
    totalVolume: 91000000,
    risk: "RESTRICTED",
    iconTone: "blue",
    focus: ["Elections", "Policy", "Approval", "Appointments"]
  },
  {
    slug: "economics",
    name: "Economics",
    shortName: "Economics",
    description: "Macro releases, inflation, central bank decisions, and economic indicators.",
    activeMarkets: 34,
    volume24h: 9600000,
    totalVolume: 142000000,
    risk: "MEDIUM",
    iconTone: "brass",
    focus: ["Inflation", "GDP", "Jobs", "Rates"]
  },
  {
    slug: "stocks-mutual-funds",
    name: "Stocks and mutual funds",
    shortName: "Stocks",
    description: "Price thresholds, NAV outcomes, corporate actions, and earnings milestones.",
    activeMarkets: 20,
    volume24h: 7200000,
    totalVolume: 113000000,
    risk: "RESTRICTED",
    iconTone: "green",
    focus: ["Stocks", "Mutual funds", "NAV", "Earnings"]
  },
  {
    slug: "financials",
    name: "Financials",
    shortName: "Financials",
    description: "Rates, yields, FX, banking metrics, and financial index levels.",
    activeMarkets: 26,
    volume24h: 8100000,
    totalVolume: 128000000,
    risk: "HIGH",
    iconTone: "blue",
    focus: ["FX", "Yields", "Rates", "Banks"]
  },
  {
    slug: "weather-climate",
    name: "Weather / climate",
    shortName: "Weather",
    description: "Temperature, rainfall, climate data releases, air quality, and storm outcomes.",
    activeMarkets: 29,
    volume24h: 4100000,
    totalVolume: 68000000,
    risk: "LOW",
    iconTone: "aqua",
    focus: ["Temperature", "Rainfall", "AQI", "Storms"]
  },
  {
    slug: "culture",
    name: "Culture",
    shortName: "Culture",
    description: "Awards, box office, charts, streaming ranks, and public cultural events.",
    activeMarkets: 18,
    volume24h: 2600000,
    totalVolume: 41000000,
    risk: "MEDIUM",
    iconTone: "violet",
    focus: ["Awards", "Box office", "Charts", "Streaming"]
  },
  {
    slug: "tech-science",
    name: "Tech and science",
    shortName: "Tech",
    description: "Launches, space missions, AI releases, research milestones, and approvals.",
    activeMarkets: 31,
    volume24h: 6900000,
    totalVolume: 102000000,
    risk: "MEDIUM",
    iconTone: "blue",
    focus: ["AI", "Space", "Products", "Research"]
  },
  {
    slug: "mentions",
    name: "Mentions / public attention",
    shortName: "Mentions",
    description: "News, social, search, and ranking attention measured by approved providers.",
    activeMarkets: 15,
    volume24h: 1900000,
    totalVolume: 36000000,
    risk: "HIGH",
    iconTone: "red",
    focus: ["News", "Search", "Social", "Rankings"]
  },
  {
    slug: "commodities",
    name: "Commodities",
    shortName: "Commodities",
    description: "Gold, oil, gas, agricultural products, inventory reports, and benchmarks.",
    activeMarkets: 22,
    volume24h: 7800000,
    totalVolume: 119000000,
    risk: "HIGH",
    iconTone: "brass",
    focus: ["Gold", "Oil", "Gas", "Agriculture"]
  }
];

const historyA: ChartPoint[] = [
  { time: "2026-07-01", value: 41, volume: 1200 },
  { time: "2026-07-02", value: 43, volume: 1900 },
  { time: "2026-07-03", value: 45, volume: 2300 },
  { time: "2026-07-04", value: 44, volume: 1800 },
  { time: "2026-07-05", value: 48, volume: 3100 },
  { time: "2026-07-06", value: 51, volume: 4600 },
  { time: "2026-07-07", value: 49, volume: 3900 },
  { time: "2026-07-08", value: 53, volume: 5200 },
  { time: "2026-07-09", value: 56, volume: 6100 }
];

const historyB: ChartPoint[] = [
  { time: "2026-07-01", value: 62, volume: 2600 },
  { time: "2026-07-02", value: 60, volume: 2400 },
  { time: "2026-07-03", value: 58, volume: 2200 },
  { time: "2026-07-04", value: 59, volume: 2100 },
  { time: "2026-07-05", value: 57, volume: 2800 },
  { time: "2026-07-06", value: 55, volume: 3300 },
  { time: "2026-07-07", value: 52, volume: 4700 },
  { time: "2026-07-08", value: 51, volume: 4200 },
  { time: "2026-07-09", value: 49, volume: 3600 }
];

function createBinaryOutcomes(probability: number): Outcome[] {
  return [
    { label: "YES", price: probability, probability },
    { label: "NO", price: 100 - probability, probability: 100 - probability }
  ];
}

export const markets: Market[] = [
  {
    id: "ind-aus-final",
    title: "Will India beat Australia in the next T20 final?",
    categorySlug: "sports",
    subcategory: "Cricket",
    marketType: "Binary",
    status: "Open",
    closeTime: "Jul 18, 2026 18:30 IST",
    source: "Official tournament result",
    ruleSummary: "YES resolves if India is declared match winner by the official tournament source.",
    probability: 56,
    change24h: 3.8,
    volume24h: 2100000,
    totalVolume: 18400000,
    liquidity: 3400000,
    spread: 2,
    traders: 1842,
    watchlisted: true,
    hasPosition: true,
    outcomes: createBinaryOutcomes(56),
    priceHistory: historyA,
    orderBook: {
      yesBids: [
        { price: 55, quantity: 420 },
        { price: 54, quantity: 610 },
        { price: 53, quantity: 380 },
        { price: 52, quantity: 840 }
      ],
      noBids: [
        { price: 43, quantity: 360 },
        { price: 42, quantity: 520 },
        { price: 41, quantity: 680 },
        { price: 40, quantity: 770 }
      ]
    },
    recentTrades: [
      { time: "10:42", outcome: "YES", price: 56, quantity: 24 },
      { time: "10:39", outcome: "NO", price: 44, quantity: 18 },
      { time: "10:33", outcome: "YES", price: 55, quantity: 40 }
    ],
    riskNotes: ["Match postponement follows tournament void policy.", "Official result source is required."]
  },
  {
    id: "cpi-above-4",
    title: "Will India CPI be above 4.0% in the next release?",
    categorySlug: "economics",
    subcategory: "Inflation",
    marketType: "Threshold",
    status: "Open",
    closeTime: "Aug 12, 2026 16:30 IST",
    source: "MOSPI CPI release",
    ruleSummary: "YES resolves if the official CPI value is greater than 4.0%. Equality resolves NO.",
    probability: 49,
    change24h: -2.7,
    volume24h: 1600000,
    totalVolume: 12100000,
    liquidity: 2800000,
    spread: 3,
    traders: 931,
    watchlisted: true,
    hasPosition: false,
    outcomes: createBinaryOutcomes(49),
    priceHistory: historyB,
    orderBook: {
      yesBids: [
        { price: 48, quantity: 620 },
        { price: 47, quantity: 440 },
        { price: 46, quantity: 350 },
        { price: 45, quantity: 910 }
      ],
      noBids: [
        { price: 50, quantity: 510 },
        { price: 49, quantity: 360 },
        { price: 48, quantity: 790 },
        { price: 47, quantity: 420 }
      ]
    },
    recentTrades: [
      { time: "10:48", outcome: "NO", price: 51, quantity: 32 },
      { time: "10:41", outcome: "YES", price: 49, quantity: 16 },
      { time: "10:37", outcome: "NO", price: 50, quantity: 48 }
    ],
    riskNotes: ["Preliminary vs revised value follows market rule version.", "Exact 4.0% resolves NO."]
  },
  {
    id: "mumbai-rainfall-range",
    title: "Mumbai rainfall on Jul 20: which range will be recorded?",
    categorySlug: "weather-climate",
    subcategory: "Rainfall",
    marketType: "Range",
    status: "Open",
    closeTime: "Jul 20, 2026 06:00 IST",
    source: "Official weather station record",
    ruleSummary: "The official station rainfall total maps to exactly one predefined range.",
    probability: 34,
    change24h: 5.4,
    volume24h: 820000,
    totalVolume: 5400000,
    liquidity: 1180000,
    spread: 4,
    traders: 522,
    watchlisted: false,
    hasPosition: false,
    outcomes: [
      { label: "< 25 mm", price: 18, probability: 18 },
      { label: "25-75 mm", price: 34, probability: 34 },
      { label: "75-150 mm", price: 31, probability: 31 },
      { label: ">= 150 mm", price: 17, probability: 17 }
    ],
    priceHistory: historyA.map((point) => ({ ...point, value: point.value - 18 })),
    orderBook: {
      yesBids: [
        { price: 33, quantity: 210 },
        { price: 32, quantity: 360 },
        { price: 31, quantity: 190 },
        { price: 30, quantity: 420 }
      ],
      noBids: [
        { price: 64, quantity: 140 },
        { price: 63, quantity: 220 },
        { price: 62, quantity: 290 },
        { price: 61, quantity: 180 }
      ]
    },
    recentTrades: [
      { time: "10:31", outcome: "25-75 mm", price: 34, quantity: 11 },
      { time: "10:24", outcome: "75-150 mm", price: 31, quantity: 20 },
      { time: "10:18", outcome: "< 25 mm", price: 18, quantity: 15 }
    ],
    riskNotes: ["Station outage uses backup policy.", "Boundary inclusivity is defined in market rules."]
  },
  {
    id: "gold-above-2500",
    title: "Will gold close above USD 2,500 on the settlement date?",
    categorySlug: "commodities",
    subcategory: "Gold",
    marketType: "Threshold",
    status: "Closing soon",
    closeTime: "Jul 10, 2026 23:00 IST",
    source: "Approved benchmark close",
    ruleSummary: "YES resolves if the approved benchmark close is greater than USD 2,500.",
    probability: 61,
    change24h: 1.6,
    volume24h: 2400000,
    totalVolume: 17300000,
    liquidity: 3900000,
    spread: 2,
    traders: 1104,
    watchlisted: false,
    hasPosition: true,
    outcomes: createBinaryOutcomes(61),
    priceHistory: historyA.map((point) => ({ ...point, value: point.value + 5 })),
    orderBook: {
      yesBids: [
        { price: 60, quantity: 530 },
        { price: 59, quantity: 440 },
        { price: 58, quantity: 360 },
        { price: 57, quantity: 510 }
      ],
      noBids: [
        { price: 38, quantity: 410 },
        { price: 37, quantity: 390 },
        { price: 36, quantity: 260 },
        { price: 35, quantity: 680 }
      ]
    },
    recentTrades: [
      { time: "10:52", outcome: "YES", price: 61, quantity: 42 },
      { time: "10:45", outcome: "YES", price: 60, quantity: 19 },
      { time: "10:36", outcome: "NO", price: 39, quantity: 24 }
    ],
    riskNotes: ["Holiday close uses next valid benchmark date.", "Intraday prices do not settle this market."]
  },
  {
    id: "ai-model-release",
    title: "Will a frontier AI lab release a new public model before Sep 30?",
    categorySlug: "tech-science",
    subcategory: "AI",
    marketType: "Conditional",
    status: "Open",
    closeTime: "Sep 30, 2026 23:59 UTC",
    source: "Official lab announcements",
    ruleSummary: "YES requires a public model release from an approved frontier AI lab list.",
    probability: 64,
    change24h: 4.2,
    volume24h: 3100000,
    totalVolume: 22400000,
    liquidity: 4200000,
    spread: 3,
    traders: 2210,
    watchlisted: true,
    hasPosition: false,
    outcomes: createBinaryOutcomes(64),
    priceHistory: historyA.map((point) => ({ ...point, value: point.value + 8 })),
    orderBook: {
      yesBids: [
        { price: 63, quantity: 760 },
        { price: 62, quantity: 810 },
        { price: 61, quantity: 600 },
        { price: 60, quantity: 950 }
      ],
      noBids: [
        { price: 35, quantity: 420 },
        { price: 34, quantity: 620 },
        { price: 33, quantity: 530 },
        { price: 32, quantity: 470 }
      ]
    },
    recentTrades: [
      { time: "10:58", outcome: "YES", price: 64, quantity: 30 },
      { time: "10:55", outcome: "YES", price: 63, quantity: 52 },
      { time: "10:49", outcome: "NO", price: 36, quantity: 17 }
    ],
    riskNotes: ["Announcement must be official and public.", "Private beta releases do not count."]
  },
  {
    id: "film-award-winner",
    title: "Which film will win the national best picture award?",
    categorySlug: "culture",
    subcategory: "Awards",
    marketType: "Multiple-choice",
    status: "Open",
    closeTime: "Aug 28, 2026 20:00 IST",
    source: "Official award announcement",
    ruleSummary: "The officially announced winner resolves as the winning outcome.",
    probability: 38,
    change24h: -1.2,
    volume24h: 690000,
    totalVolume: 4200000,
    liquidity: 980000,
    spread: 5,
    traders: 388,
    watchlisted: false,
    hasPosition: false,
    outcomes: [
      { label: "Film A", price: 38, probability: 38 },
      { label: "Film B", price: 27, probability: 27 },
      { label: "Film C", price: 19, probability: 19 },
      { label: "Other", price: 16, probability: 16 }
    ],
    priceHistory: historyB.map((point) => ({ ...point, value: Math.max(18, point.value - 18) })),
    orderBook: {
      yesBids: [
        { price: 37, quantity: 140 },
        { price: 36, quantity: 210 },
        { price: 35, quantity: 170 },
        { price: 34, quantity: 260 }
      ],
      noBids: [
        { price: 61, quantity: 130 },
        { price: 60, quantity: 190 },
        { price: 59, quantity: 160 },
        { price: 58, quantity: 120 }
      ]
    },
    recentTrades: [
      { time: "09:52", outcome: "Film A", price: 38, quantity: 8 },
      { time: "09:44", outcome: "Film B", price: 27, quantity: 13 },
      { time: "09:18", outcome: "Other", price: 16, quantity: 12 }
    ],
    riskNotes: ["Tie policy follows official award treatment.", "Only listed official category counts."]
  }
];

export const positions: Position[] = [
  { marketId: "ind-aus-final", outcome: "YES", quantity: 120, averageEntry: 47, currentPrice: 56, maxPayout: 12000 },
  { marketId: "gold-above-2500", outcome: "YES", quantity: 80, averageEntry: 58, currentPrice: 61, maxPayout: 8000 }
];

export const userOrders: UserOrder[] = [
  { id: "ORD-1042", marketId: "ind-aus-final", side: "Buy", outcome: "YES", price: 55, quantity: 50, filled: 24, status: "Open", createdAt: "Jul 9, 10:42" },
  { id: "ORD-1038", marketId: "cpi-above-4", side: "Buy", outcome: "NO", price: 50, quantity: 30, filled: 30, status: "Filled", createdAt: "Jul 9, 09:18" },
  { id: "ORD-1024", marketId: "gold-above-2500", side: "Sell", outcome: "YES", price: 62, quantity: 20, filled: 0, status: "Open", createdAt: "Jul 8, 16:12" },
  { id: "ORD-1019", marketId: "ai-model-release", side: "Buy", outcome: "YES", price: 61, quantity: 12, filled: 0, status: "Cancelled", createdAt: "Jul 8, 12:03" }
];

export const walletEntries: WalletEntry[] = [
  { id: "LED-3009", type: "Deposit", amount: 50000, status: "Complete", createdAt: "Jul 9, 08:10" },
  { id: "LED-3008", type: "Order lock", amount: -2750, status: "Complete", createdAt: "Jul 9, 10:42" },
  { id: "LED-3007", type: "Trade collateral", amount: -1410, status: "Complete", createdAt: "Jul 9, 10:39" },
  { id: "LED-3006", type: "Order release", amount: 1220, status: "Complete", createdAt: "Jul 8, 17:05" },
  { id: "LED-3005", type: "Settlement credit", amount: 8000, status: "Pending", createdAt: "Jul 8, 15:22" }
];

export const adminQueue = [
  {
    id: "REV-221",
    title: "Will Bengaluru receive more than 20 mm rain tomorrow?",
    category: "Weather / climate",
    status: "Source check",
    risk: "LOW",
    submittedBy: "user_1829"
  },
  {
    id: "REV-220",
    title: "Will the next policy rate decision be a hold?",
    category: "Economics",
    status: "Resolution review",
    risk: "MEDIUM",
    submittedBy: "user_1041"
  },
  {
    id: "REV-219",
    title: "Will a listed stock close above its 52-week high?",
    category: "Stocks and mutual funds",
    status: "Legal review",
    risk: "RESTRICTED",
    submittedBy: "user_2810"
  }
];

export function getCategory(slug: string) {
  return categories.find((category) => category.slug === slug);
}

export function getMarket(id: string) {
  return markets.find((market) => market.id === id);
}

export function getMarketsByCategory(slug: string) {
  return markets.filter((market) => market.categorySlug === slug);
}
