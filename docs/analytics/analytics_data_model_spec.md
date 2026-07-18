# Analytics Data Model Spec

This document defines the analytics data model for Pred-Market V1: market analytics, user analytics, category analytics, rollups, chart data, open interest, liquidity, volume, and reconciliation.

This is planning documentation only. It does not create backend code or database migrations.

## 1. Analytics Goal

Analytics should help users:

```text
understand markets quickly
compare opportunities
track probability movement
evaluate liquidity
manage exposure
build strategies
avoid accidental risk
```

Analytics should help operations:

```text
monitor market health
detect suspicious activity
verify settlement correctness
track liquidity and volume
identify stale data
support compliance review
```

## 2. Core Principle

Separate:

```text
transaction source of truth
analytics read model
```

Transaction tables:

```text
wallets
ledger_entries
orders
trades
positions
settlements
```

Analytics tables:

```text
price points
rollups
snapshots
derived metrics
```

Analytics jobs must never mutate financial source-of-truth records.

## 3. Data Sources

Analytics source inputs:

```text
orders
trades
positions
wallets
ledger entries
market collateral
market status
oracle evidence
settlement items
category metadata
user events
```

Derived outputs:

```text
price history
volume history
order book depth
liquidity metrics
open interest
spread
category heatmaps
portfolio exposure
PnL inputs
market health indicators
```

## 4. Market Analytics

Minimum market metrics:

```text
current best bid
current best ask
last traded price
mid price
implied probability
spread
spread percentage
24h price change
24h volume
total volume
open interest
liquidity depth
number of traders
recent trade count
market close time
time to close
settlement source
data freshness
```

Market health metrics:

```text
stale order book age
last trade age
wide spread flag
thin liquidity flag
high cancellation rate flag
large price move flag
source data stale flag
```

## 5. User Analytics

Minimum user metrics:

```text
available cash
locked cash
open positions
position quantity
average entry price
current implied value
unrealized PnL
realized PnL
max payout
max loss
cash locked in orders
shares locked in sell orders
exposure by category
exposure by market
orders awaiting fill
settlement history
void refund history
```

User risk metrics:

```text
largest market exposure
largest category exposure
markets closing soon
correlated category exposure
restricted category exposure
high-risk market exposure
```

## 6. Category Analytics

Minimum category metrics:

```text
active markets
open markets
closing soon markets
24h volume
total volume
trade count
unique traders
average spread
median spread
liquidity depth
top markets by volume
top movers
new markets
risk alerts
void rate
dispute rate
settlement time
```

Category views:

```text
sports dashboard
economics dashboard
weather/climate dashboard
commodities dashboard
all-category heatmap
```

## 7. Price History Model

Store chart points per market outcome.

Recommended table:

```text
market_price_points
```

Fields:

```text
market_id
outcome_id
price_minor
implied_probability_bps
volume_minor
open_interest
best_bid_minor
best_ask_minor
spread_minor
captured_at
source_event_type
```

Probability basis points:

```text
10000 bps = 100.00%
5600 bps = 56.00%
```

Capture triggers:

```text
trade executed
best bid/ask changes
scheduled snapshot interval
market opens
market closes
market resolves
```

Recommended intervals:

```text
1 minute for active markets
5 minutes for normal open markets
1 hour for low-activity markets
final snapshot at close and settlement
```

## 8. Volume Model

Volume definitions:

```text
trade_volume_minor = price_minor * quantity
notional_payout_minor = payout_amount_minor * quantity
```

Display volume:

```text
V1 should display traded cost volume unless explicitly labeled otherwise.
```

Store both:

```text
traded_cost_volume_minor
notional_payout_volume_minor
```

Rollup windows:

```text
5 minute
1 hour
24 hour
daily
all time
```

## 9. Open Interest Model

Open interest means:

```text
number of unsettled matched contracts or shares outstanding
```

Binary open interest:

```text
sum matched YES quantity
which equals sum matched NO quantity
```

Multiple-choice open interest:

```text
sum outstanding outcome shares by outcome
complete-set consistency must be reconciled
```

Open interest should change when:

```text
new fills create positions
positions are sold/transferred
positions settle
positions void
complete sets are minted or redeemed if supported later
```

## 10. Liquidity Model

Liquidity depth:

```text
cash available at or near best prices
```

Suggested liquidity bands:

```text
within 1 price point
within 2 price points
within 5 price points
within 10 price points
```

For each market/outcome:

```text
bid_depth_quantity
ask_depth_quantity
bid_depth_minor
ask_depth_minor
spread_minor
spread_bps
```

Thin liquidity flag:

```text
depth within 5 points below configured category threshold
```

## 11. Order Book Analytics

Order book snapshot fields:

```text
market_id
outcome_id
side
price_minor
quantity
order_count
captured_at
```

Usage:

```text
depth chart
spread monitoring
liquidity scoring
market health alerts
```

Do not use order book snapshots as source of truth for open orders.

## 12. Portfolio Analytics

Portfolio snapshot fields:

```text
user_id
captured_at
available_cash_minor
locked_cash_minor
current_position_value_minor
max_payout_minor
max_loss_minor
unrealized_pnl_minor
realized_pnl_minor
category_exposure_json
market_exposure_json
```

Position value:

```text
quantity * current implied price
```

Max payout:

```text
quantity * payout_amount
```

Max loss:

```text
remaining cost basis at risk
```

## 13. Rollup Tables

Recommended rollups:

```text
market_minute_rollups
market_hourly_rollups
market_daily_rollups
category_daily_rollups
user_daily_portfolio_snapshots
order_book_snapshots
market_health_snapshots
```

Rollup fields:

```text
open_price_minor
high_price_minor
low_price_minor
close_price_minor
volume_minor
trade_count
unique_traders
open_interest
best_bid_minor
best_ask_minor
spread_minor
liquidity_depth_minor
```

## 14. Reconciliation

Analytics must reconcile against transaction tables.

Required checks:

```text
trade rollup volume equals trades table volume
open interest equals unsettled position quantities
market price last trade matches latest trade
wallet analytics equal wallet table
user PnL inputs match positions and trades
settlement analytics match settlement_items
category volume equals sum market volume
```

If reconciliation fails:

```text
mark analytics stale
hide or warn on affected metric
alert operations
do not auto-change financial source records
rerun rollup job after source issue is fixed
```

## 15. Freshness And Staleness

Every analytical response should include:

```text
computed_at
source_max_event_at
staleness_seconds
is_stale
```

User-facing stale indicators:

```text
Last updated [time]
Data delayed
Order book reconnecting
Chart backfill pending
Source evidence pending
```

## 16. API Responses

Market analytics response:

```text
market_id
outcome_metrics[]
best_bid
best_ask
last_trade
spread
volume_24h
total_volume
open_interest
liquidity_depth
price_change_24h
computed_at
is_stale
```

User analytics response:

```text
user_id
available_cash
locked_cash
positions[]
category_exposure[]
market_exposure[]
unrealized_pnl
realized_pnl
max_payout
max_loss
computed_at
is_stale
```

Category analytics response:

```text
category_id
active_markets
volume_24h
top_markets
top_movers
average_spread
liquidity_depth
risk_alerts
computed_at
is_stale
```

## 17. User-Facing Analytics Views

Required views:

```text
market page probability chart
market page volume chart
market page order book depth
market card key metrics
market table sorting
category dashboard
watchlist
portfolio exposure
orders page
wallet ledger
admin market health dashboard
```

Strategy views:

```text
closing soon
high volume
low spread
biggest movers
newly listed
has position
watchlisted
category heatmap
```

## 18. Testing Requirements

Required tests:

```text
price point created after trade
24h volume excludes older trades
open interest updates after fill
open interest clears after settlement
category rollup equals sum of markets
portfolio exposure equals positions
stale source marks analytics stale
analytics job is idempotent
rollup rerun does not double count
reconciliation detects forced mismatch
```

