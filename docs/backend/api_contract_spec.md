# API Contract Spec

This document defines the Pred-Market V1 REST and WebSocket API contract for frontend/backend integration. It covers `/markets`, `/orders`, `/trades`, `/positions`, `/wallet`, `/admin`, and realtime order book updates.

## Beginner-First Trading Addendum

Market list and detail responses include:

```json
{
  "quote": {
    "yes_bid": 63,
    "yes_ask": 65,
    "no_bid": 35,
    "no_ask": 37,
    "last_trade": 65,
    "spread": 2
  }
}
```

`GET /markets/{market_id}/order-book` returns `market_id`, monotonic `sequence`, `updated_at`, `quote`, and anonymous aggregated `yes_bids`/`no_bids`. Seeded `order_book_json` and `recent_trades_json` are compatibility data only and are never served as live fallbacks.

Quick trades remain `POST /orders` limit orders. Clients submit `outcome_id`, `side=BUY`, the current executable ask as `price_minor`, and `floor(budget / ask)` as `quantity`.

Order status meaning is exact:

- `OPEN`: waiting for another order.
- `PARTIALLY_FILLED`: some quantity filled and the remainder is open.
- `FILLED`: completed and reflected in positions.
- `CANCELLED` or `PARTIALLY_CANCELLED`: remaining quantity was cancelled and locks were released.

Public WebSocket events are `order_book.snapshot`, `trade.created`, `ticker.updated`, and `heartbeat`. An order-book subscription receives an immediate full snapshot. Full snapshots follow order creation, fill, cancellation, and simulated-liquidity replenishment. Redis pub/sub fans out the transactional outbox across backend instances.

This is planning documentation only. It does not create backend code.

## 1. API Goals

The API must support:

```text
market discovery
market detail
order placement
order cancellation
trade feed
positions and portfolio
wallet and ledger
admin review and resolution
realtime order book updates
realtime user order/fill notifications
```

Core API rules:

```text
REST for snapshots and commands
WebSockets for realtime updates
PostgreSQL remains source of truth
WebSocket clients can resync through REST
all money values use integer minor units
timestamps use ISO 8601 UTC
commands use idempotency keys
```

## 2. Common Conventions

Base path:

```text
/api/v1
```

Authentication:

```text
Authorization: Bearer <access_token>
```

Idempotency for commands:

```text
Idempotency-Key: <unique-client-generated-key>
```

Request ID:

```text
X-Request-ID: <optional-client-request-id>
```

Money shape:

```json
{
  "amount_minor": 10000,
  "currency": "INR"
}
```

Error shape:

```json
{
  "error": {
    "code": "INSUFFICIENT_FUNDS",
    "message": "Available balance is not sufficient for this order.",
    "request_id": "req_123",
    "details": {}
  }
}
```

Pagination:

```json
{
  "items": [],
  "next_cursor": "cursor_or_null"
}
```

## 3. Common Status Codes

Use:

```text
200 OK for successful reads and idempotent command replay
201 Created for newly created command resources
202 Accepted for async jobs
400 Bad Request for validation failures
401 Unauthorized for missing/invalid auth
403 Forbidden for eligibility or role failure
404 Not Found for missing resources
409 Conflict for state conflicts or idempotency mismatch
422 Unprocessable Entity for domain validation errors
429 Too Many Requests for rate limits
500 Internal Server Error for unexpected failures
```

## 4. Market APIs

### GET /markets

Purpose:

```text
market discovery list
```

Query parameters:

```text
category
market_type
status
close_before
close_after
min_volume_24h
max_spread
watchlisted
has_position
sort
cursor
limit
```

Response:

```json
{
  "items": [
    {
      "id": "market_uuid",
      "title": "Will India beat Australia in the next T20 final?",
      "category": {
        "slug": "sports",
        "name": "Sports"
      },
      "market_type": "BINARY",
      "status": "OPEN",
      "currency": "INR",
      "payout_amount_minor": 10000,
      "close_time": "2026-07-18T13:00:00Z",
      "primary_outcome_price_minor": 5600,
      "implied_probability_bps": 5600,
      "volume_24h_minor": 210000000,
      "liquidity_depth_minor": 340000000,
      "spread_minor": 200,
      "watchlisted": true,
      "has_position": true
    }
  ],
  "next_cursor": null
}
```

### GET /markets/{market_id}

Purpose:

```text
market detail page snapshot
```

Response:

```json
{
  "id": "market_uuid",
  "title": "Will India beat Australia in the next T20 final?",
  "description": "Market description.",
  "category": {
    "slug": "sports",
    "name": "Sports"
  },
  "market_type": "BINARY",
  "status": "OPEN",
  "currency": "INR",
  "payout_amount_minor": 10000,
  "tick_size_minor": 100,
  "min_quantity": 1,
  "max_quantity": 10000,
  "open_time": "2026-07-01T04:30:00Z",
  "close_time": "2026-07-18T13:00:00Z",
  "resolution_source": "Official tournament result",
  "resolution_rule": "YES resolves if India is official winner.",
  "void_policy": "Refund original matched cost if voided.",
  "outcomes": [
    {
      "id": "outcome_yes_uuid",
      "code": "YES",
      "label": "YES",
      "best_bid_minor": 5500,
      "best_ask_minor": null,
      "last_price_minor": 5600,
      "implied_probability_bps": 5600
    }
  ],
  "analytics": {
    "volume_24h_minor": 210000000,
    "total_volume_minor": 1840000000,
    "open_interest": 18400,
    "spread_minor": 200,
    "trader_count": 1842,
    "computed_at": "2026-07-09T08:00:00Z",
    "is_stale": false
  }
}
```

### GET /markets/{market_id}/order-book

Query parameters:

```text
outcome_id optional
depth default 20
```

Response:

```json
{
  "market_id": "market_uuid",
  "sequence": 1024,
  "generated_at": "2026-07-09T08:00:00Z",
  "outcomes": [
    {
      "outcome_id": "outcome_yes_uuid",
      "bids": [
        {
          "price_minor": 5500,
          "quantity": 420,
          "order_count": 3
        }
      ],
      "asks": []
    }
  ]
}
```

For binary complementary V1:

```text
YES and NO buy books may be displayed instead of bid/ask share books.
```

### GET /markets/{market_id}/price-history

Query parameters:

```text
outcome_id
interval=1m|5m|1h|1d
from
to
```

Response:

```json
{
  "market_id": "market_uuid",
  "outcome_id": "outcome_yes_uuid",
  "interval": "5m",
  "points": [
    {
      "time": "2026-07-09T08:00:00Z",
      "price_minor": 5600,
      "implied_probability_bps": 5600,
      "volume_minor": 1250000,
      "open_interest": 18400
    }
  ]
}
```

## 5. Order APIs

### POST /orders

Headers:

```text
Idempotency-Key required
```

Request:

```json
{
  "market_id": "market_uuid",
  "outcome_id": "outcome_yes_uuid",
  "side": "BUY",
  "price_minor": 5600,
  "quantity": 10
}
```

Response:

```json
{
  "order": {
    "id": "order_uuid",
    "market_id": "market_uuid",
    "outcome_id": "outcome_yes_uuid",
    "side": "BUY",
    "price_minor": 5600,
    "quantity": 10,
    "filled_quantity": 4,
    "remaining_quantity": 6,
    "status": "PARTIALLY_FILLED",
    "locked_cash_minor": 33600,
    "created_at": "2026-07-09T08:00:00Z"
  },
  "fills": [
    {
      "trade_id": "trade_uuid",
      "price_minor": 5600,
      "quantity": 4,
      "created_at": "2026-07-09T08:00:01Z"
    }
  ]
}
```

Validation errors:

```text
MARKET_NOT_OPEN
PRICE_OUT_OF_RANGE
INVALID_TICK_SIZE
QUANTITY_OUT_OF_RANGE
INSUFFICIENT_FUNDS
INSUFFICIENT_POSITION
SELF_TRADE_BLOCKED
```

### GET /orders

Query parameters:

```text
status
market_id
cursor
limit
```

Response:

```json
{
  "items": [
    {
      "id": "order_uuid",
      "market_id": "market_uuid",
      "market_title": "Will India beat Australia?",
      "outcome_label": "YES",
      "side": "BUY",
      "price_minor": 5600,
      "quantity": 10,
      "filled_quantity": 4,
      "remaining_quantity": 6,
      "status": "PARTIALLY_FILLED",
      "created_at": "2026-07-09T08:00:00Z"
    }
  ],
  "next_cursor": null
}
```

### GET /orders/{order_id}

Returns one order plus fill history.

### POST /orders/{order_id}/cancel

Headers:

```text
Idempotency-Key required
```

Response:

```json
{
  "order": {
    "id": "order_uuid",
    "status": "PARTIALLY_CANCELLED",
    "filled_quantity": 4,
    "cancelled_quantity": 6,
    "remaining_quantity": 0,
    "released_cash_minor": 33600,
    "cancelled_at": "2026-07-09T08:05:00Z"
  }
}
```

## 6. Trade APIs

### GET /trades

Query parameters:

```text
market_id
outcome_id
user_only
cursor
limit
```

Response:

```json
{
  "items": [
    {
      "id": "trade_uuid",
      "market_id": "market_uuid",
      "outcome_id": "outcome_yes_uuid",
      "outcome_label": "YES",
      "price_minor": 5600,
      "quantity": 4,
      "created_at": "2026-07-09T08:00:01Z"
    }
  ],
  "next_cursor": null
}
```

Normal users see anonymized public trade feed. Admin endpoints can expose user/order references.

## 7. Position APIs

### GET /positions

Query parameters:

```text
status
market_id
category
cursor
limit
```

Response:

```json
{
  "items": [
    {
      "market_id": "market_uuid",
      "market_title": "Will India beat Australia?",
      "outcome_id": "outcome_yes_uuid",
      "outcome_label": "YES",
      "quantity": 120,
      "locked_quantity": 0,
      "average_entry_price_minor": 4700,
      "current_price_minor": 5600,
      "cost_basis_minor": 564000,
      "current_value_minor": 672000,
      "max_payout_minor": 1200000,
      "unrealized_pnl_minor": 108000,
      "status": "OPEN"
    }
  ],
  "next_cursor": null
}
```

### GET /portfolio

Response:

```json
{
  "available_cash_minor": 8422000,
  "locked_cash_minor": 973000,
  "current_position_value_minor": 672000,
  "unrealized_pnl_minor": 108000,
  "realized_pnl_minor": 0,
  "max_payout_minor": 1200000,
  "category_exposure": [
    {
      "category_slug": "sports",
      "exposure_minor": 672000
    }
  ],
  "computed_at": "2026-07-09T08:00:00Z",
  "is_stale": false
}
```

## 8. Wallet APIs

### GET /wallet

Response:

```json
{
  "currency": "INR",
  "available_balance_minor": 8422000,
  "locked_balance_minor": 973000,
  "total_balance_minor": 9395000,
  "updated_at": "2026-07-09T08:00:00Z"
}
```

### GET /wallet/ledger

Query parameters:

```text
type
cursor
limit
```

Response:

```json
{
  "items": [
    {
      "id": "ledger_transaction_uuid",
      "type": "ORDER_LOCK",
      "amount_minor": -56000,
      "currency": "INR",
      "reference_type": "ORDER",
      "reference_id": "order_uuid",
      "created_at": "2026-07-09T08:00:00Z"
    }
  ],
  "next_cursor": null
}
```

### POST /wallet/test-deposit

Development-only endpoint.

Headers:

```text
Idempotency-Key required
```

Request:

```json
{
  "amount_minor": 100000,
  "currency": "INR"
}
```

Production payment APIs are out of scope for early V1.

## 9. Admin APIs

Admin endpoints require admin role.

### GET /admin/markets/review

Returns market approval queue.

### POST /admin/markets/{market_id}/approve

Headers:

```text
Idempotency-Key required
```

Request:

```json
{
  "reason": "Source and rule reviewed."
}
```

### POST /admin/markets/{market_id}/pause

Request:

```json
{
  "reason": "Source outage under review."
}
```

### POST /admin/markets/{market_id}/close

Closes market and cancels open orders.

### POST /admin/markets/{market_id}/evidence

Request:

```json
{
  "source_name": "Official source",
  "source_url": "https://example.com/result",
  "captured_value": "YES",
  "raw_payload_json": {}
}
```

### POST /admin/markets/{market_id}/resolution-proposals

Request:

```json
{
  "resolution_type": "OUTCOME",
  "proposed_outcome_id": "outcome_uuid",
  "oracle_evidence_id": "evidence_uuid",
  "reason": "Official source confirms outcome."
}
```

### POST /admin/resolution-proposals/{proposal_id}/approve

Checker endpoint.

Rules:

```text
checker cannot be proposal creator
```

### POST /admin/markets/{market_id}/settle

Headers:

```text
Idempotency-Key required
```

Response:

```json
{
  "settlement_id": "settlement_uuid",
  "status": "COMPLETE",
  "total_payout_minor": 1200000,
  "total_refund_minor": 0,
  "completed_at": "2026-07-09T09:00:00Z"
}
```

### GET /admin/audit-logs

Query parameters:

```text
entity_type
entity_id
actor_user_id
action
cursor
limit
```

## 10. WebSocket API

Base path:

```text
/ws/v1
```

Authentication:

```text
Bearer token in connection auth payload or query token for early local dev only
```

Event envelope:

```json
{
  "event_id": "event_uuid",
  "event_type": "order_book.updated",
  "sequence": 1025,
  "market_id": "market_uuid",
  "created_at": "2026-07-09T08:00:00Z",
  "payload": {}
}
```

Client message:

```json
{
  "type": "subscribe",
  "channel": "market.order_book",
  "market_id": "market_uuid"
}
```

Server ack:

```json
{
  "type": "subscribed",
  "channel": "market.order_book",
  "market_id": "market_uuid",
  "snapshot_sequence": 1024
}
```

## 11. WebSocket Channels

Market public channels:

```text
market.order_book.{market_id}
market.trades.{market_id}
market.ticker.{market_id}
market.status.{market_id}
```

Private user channels:

```text
user.orders
user.positions
user.wallet
user.notifications
```

Admin channels:

```text
admin.review_queue
admin.risk_alerts
admin.settlement_status
```

## 12. Order Book Events

Snapshot event:

```json
{
  "event_type": "order_book.snapshot",
  "sequence": 1024,
  "payload": {
    "market_id": "market_uuid",
    "outcomes": [
      {
        "outcome_id": "outcome_yes_uuid",
        "bids": [
          {
            "price_minor": 5500,
            "quantity": 420,
            "order_count": 3
          }
        ],
        "asks": []
      }
    ]
  }
}
```

Delta event:

```json
{
  "event_type": "order_book.updated",
  "sequence": 1025,
  "payload": {
    "market_id": "market_uuid",
    "changes": [
      {
        "outcome_id": "outcome_yes_uuid",
        "side": "BUY",
        "price_minor": 5500,
        "quantity": 390,
        "order_count": 2
      }
    ]
  }
}
```

Resync rule:

```text
if client detects sequence gap, fetch GET /markets/{market_id}/order-book
```

## 13. Trade Events

```json
{
  "event_type": "trade.executed",
  "sequence": 2048,
  "payload": {
    "trade_id": "trade_uuid",
    "market_id": "market_uuid",
    "outcome_id": "outcome_yes_uuid",
    "price_minor": 5600,
    "quantity": 4,
    "created_at": "2026-07-09T08:00:01Z"
  }
}
```

## 14. Private User Events

Order update:

```json
{
  "event_type": "user.order.updated",
  "payload": {
    "order_id": "order_uuid",
    "status": "PARTIALLY_FILLED",
    "filled_quantity": 4,
    "remaining_quantity": 6
  }
}
```

Wallet update:

```json
{
  "event_type": "user.wallet.updated",
  "payload": {
    "available_balance_minor": 8422000,
    "locked_balance_minor": 973000,
    "currency": "INR"
  }
}
```

Position update:

```json
{
  "event_type": "user.position.updated",
  "payload": {
    "market_id": "market_uuid",
    "outcome_id": "outcome_yes_uuid",
    "quantity": 120,
    "average_entry_price_minor": 4700
  }
}
```

## 15. API Security And Eligibility

Before command endpoints:

```text
authenticate user
check user status
check market status
check jurisdiction/category eligibility
check KYC state if real money
check wallet freeze/restriction
check rate limit
validate idempotency key
```

Admin endpoints:

```text
require admin/checker role
write audit log
require reason for sensitive action
maker-checker for resolution and settlement
```

## 16. Rate Limits

Suggested early limits:

```text
order placement: per-user and per-market limit
cancel order: per-user limit
market list reads: generous cacheable limit
WebSocket subscriptions: max markets per user connection
admin commands: low limit plus audit
```

Exact limits should be configurable.

## 17. Versioning

Version all public APIs:

```text
/api/v1
/ws/v1
```

Breaking changes require:

```text
new version
migration notice
frontend compatibility plan
```

## 18. Required Contract Tests

REST tests:

```text
GET /markets returns discovery fields
GET /markets/{id} returns outcomes and analytics
POST /orders requires idempotency key
POST /orders locks cash and may return fills
POST /orders duplicate key returns same result
POST /orders/{id}/cancel releases remainder
GET /positions returns portfolio-ready data
GET /wallet returns available and locked balances
admin resolution requires checker role
settlement endpoint is idempotent
```

WebSocket tests:

```text
connect authenticated user
subscribe market order book
receive snapshot then deltas
sequence gap triggers REST resync
trade event emitted after fill
private order update sent only to owner
wallet update sent only to owner
admin events require admin role
```

Error tests:

```text
invalid token returns 401
restricted user returns 403
market closed returns 422
insufficient funds returns 422
idempotency mismatch returns 409
admin self-approval returns 403 or 422
```

## 19. Out Of Scope For V1

Do not expose initially:

```text
market orders
advanced order types
public user identities in trade feed
production payment provider APIs
tax forms
external market-making APIs
third-party developer API keys
GraphQL
```
