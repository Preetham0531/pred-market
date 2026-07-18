# Backend Implementation Spec

This document defines the backend implementation plan for Pred-Market V1. It covers modules, service boundaries, request flows, transaction boundaries, background jobs, API groups, testing, and build order.

This is planning documentation only. It does not create backend code or database migrations.

## 1. Backend Goal

Pred-Market V1 backend must support a user-to-user prediction market exchange.

Core product rule:

```text
Users trade contracts against other users.
The platform matches compatible orders.
The platform does not take directional risk.
Every fill is fully collateralized.
```

Primary engineering goal:

```text
Financial correctness before feature breadth.
```

V1 implementation assumptions:

```text
Python + FastAPI
Pydantic
SQLAlchemy 2.x
Alembic
PostgreSQL
Redis for cache/realtime support only
modular monolith
integer minor units for money
limit orders only
no market orders
no naked shorting
no leverage
no fees initially
admin-controlled market resolution
maker-checker approval for settlement
```

## 2. Backend Architecture

Recommended structure:

```text
backend/
  app/
    main.py
    api/
    core/
    db/
    modules/
    jobs/
    tests/
```

Suggested module folders:

```text
auth
users
wallets
ledger
markets
outcomes
orders
matching
trades
positions
collateral
resolution
settlement
admin
audit
notifications
analytics
risk
```

Architecture style:

```text
API layer -> service layer -> repository/database layer
```

Rules:

```text
API handlers should not contain business logic.
Services own business rules.
Repositories own database reads/writes.
Database transactions wrap financial workflows.
PostgreSQL is the source of truth.
Redis never becomes source of truth for money, orders, trades, or positions.
```

## 3. Module Responsibilities

### Auth Module

Responsibilities:

```text
register user
login user
issue access token
refresh token
role checks
admin checks
session/token revocation if needed
```

V1 roles:

```text
USER
ADMIN
CHECKER
MARKET_CREATOR
```

### Users Module

Responsibilities:

```text
user profile
user status
eligibility state
KYC state placeholder
jurisdiction state placeholder
account suspension
```

User statuses:

```text
ACTIVE
SUSPENDED
CLOSED
PENDING_REVIEW
```

### Wallets Module

Responsibilities:

```text
available cash balance
locked cash balance
wallet row locking
deposit placeholder
withdrawal placeholder
cash lock for buy orders
cash release on cancel
cash movement into market collateral on fill
settlement credit
void refund
wallet reconciliation
```

Wallet service must never allow:

```text
available_balance_minor < 0
locked_balance_minor < 0
```

### Ledger Module

Responsibilities:

```text
double-entry ledger transaction creation
ledger account management
ledger balancing validation
event idempotency
ledger-to-wallet reconciliation
ledger-to-collateral reconciliation
audit-readable money history
```

Every money movement must create a balanced ledger transaction.

### Markets Module

Responsibilities:

```text
market creation draft
market suggestion intake
market approval
market lifecycle state
market close scheduling
market metadata
market rule versioning
category and risk classification
```

Market lifecycle:

```text
DRAFT
REVIEW
APPROVED
OPEN
PAUSED
CLOSED
PENDING_RESOLUTION
DISPUTED
RESOLVED
VOIDED
ARCHIVED
```

### Outcomes Module

Responsibilities:

```text
YES/NO outcomes
multiple-choice outcomes
range outcome boundaries
threshold metadata
conditional metadata
combo leg metadata
outcome status
outcome validation
```

Outcome rules:

```text
binary markets must have YES and NO
multiple-choice markets must be mutually exclusive and exhaustive
range markets must be gapless and non-overlapping
threshold markets must define operator and exact source
conditional markets must define condition and failed-condition policy
combo markets must define legs and operator
```

### Orders Module

Responsibilities:

```text
validate order request
enforce market is OPEN
enforce tick size
enforce min/max quantity
lock cash for buy orders
lock shares for sell orders
create order
cancel order
release unfilled locks
dispatch matching
```

V1 order types:

```text
LIMIT_BUY
LIMIT_SELL
CANCEL
```

Binary early V1 can expose:

```text
BUY_YES
BUY_NO
CANCEL
```

### Matching Module

Responsibilities:

```text
select compatible resting orders
apply price-time priority
create fills
update order filled quantities
move locked cash into collateral
update positions
write ledger entries through LedgerService
publish order book events
```

Binary strict matching:

```text
incoming YES at Y matches resting NO at P - Y
incoming NO at N matches resting YES at P - N
```

Multiple-choice matching:

```text
one order book per outcome
buy matches lowest sell price <= buy limit
sell matches highest buy price >= sell limit
seller must own unlocked shares
```

### Trades Module

Responsibilities:

```text
trade/fill records
buyer and seller references
price and quantity
trade source order references
trade audit history
trade feed for frontend and analytics
```

Trades are immutable after creation.

### Positions Module

Responsibilities:

```text
increase positions on buys
decrease positions on sells
lock shares for sell orders
release locked shares on cancel
calculate average entry price
track realized and unrealized PnL inputs
mark positions settled
```

Positions must never go negative unless a future shorting module explicitly supports it.

### Collateral Module

Responsibilities:

```text
market collateral pool accounting
collateral increase on fills
collateral decrease on settlement or void
collateral reconciliation
maximum payout liability checks
```

Collateral invariant:

```text
market_collateral >= maximum_possible_payout_liability
```

### Resolution Module

Responsibilities:

```text
oracle evidence capture
candidate result calculation
admin resolver submission
checker approval
dispute flagging
resolution audit trail
```

Resolution output:

```text
YES
NO
outcome_id
VOID
PENDING
```

### Settlement Module

Responsibilities:

```text
close market
cancel open orders
release unfilled locks
read approved resolution
calculate payouts
write settlement ledger transactions
credit winning users
refund voided users
mark market RESOLVED or VOIDED
mark positions final
idempotency protection
```

Settlement must be safe to retry.

### Admin Module

Responsibilities:

```text
market approval
market rejection
market pause
market reopen
market close
oracle evidence review
resolution proposal
resolution checker approval
void decision
user suspension
manual adjustment request
audit inspection
```

Every admin action must write an audit log.

### Audit Module

Responsibilities:

```text
admin action logs
automated decision logs
before/after state capture
request ID capture
actor ID capture
immutable audit trail
```

### Notifications Module

Responsibilities:

```text
order filled
order partially filled
order cancelled
market closed
market resolved
settlement credited
market disputed
wallet event
```

### Analytics Module

Responsibilities:

```text
price history rollups
volume rollups
open interest
category volume
user exposure snapshots
market liquidity snapshots
```

Analytics must not mutate trading source-of-truth records.

### Risk Module

Responsibilities:

```text
restricted category checks
user eligibility checks
self-trade detection
wash-trade signal collection
exposure limits
suspicious activity alerts
```

## 4. Service Boundary Rules

Use these service ownership rules:

```text
WalletService owns wallet balances.
LedgerService owns ledger entries.
OrderService owns order validation, creation, and cancellation.
MatchingService owns fill creation and matching loops.
PositionService owns position quantity changes.
CollateralService owns market collateral balances.
SettlementService owns final payout and void workflows.
AdminService owns admin commands and approvals.
AuditService records all sensitive actions.
```

Services should communicate through explicit method calls, not by directly mutating another module's tables.

Example:

```text
OrderService.place_order()
  calls WalletService.lock_cash()
  creates order
  calls MatchingService.match_order()
```

MatchingService should not directly change wallet balances without going through ledger/wallet methods.

## 5. Request Flow: Place Binary Buy Order

Flow:

```text
1. API receives POST /orders.
2. Auth identifies user.
3. OrderService validates idempotency key.
4. OrderService loads market and outcome.
5. Validate market.status == OPEN.
6. Validate order side, price, tick size, and quantity.
7. Calculate required cash = price_minor * quantity.
8. Begin database transaction.
9. Lock wallet row with SELECT FOR UPDATE.
10. WalletService moves cash from available to locked.
11. LedgerService writes ORDER_LOCK transaction.
12. OrderService creates order as OPEN.
13. MatchingService finds compatible resting orders.
14. MatchingService creates fills until incoming order is filled or no compatible liquidity remains.
15. For each fill, locked cash moves into collateral.
16. PositionService increases positions.
17. LedgerService writes trade collateral entries.
18. Order statuses are updated.
19. Transaction commits.
20. Realtime events publish order book and fill updates.
```

Rollback rule:

```text
If any step inside the transaction fails, wallet, order, trade, position, collateral, and ledger writes all roll back together.
```

## 6. Request Flow: Cancel Order

Flow:

```text
1. API receives POST /orders/{id}/cancel.
2. Auth identifies user.
3. OrderService loads order.
4. Validate order belongs to user or admin has permission.
5. Validate order.status is OPEN or PARTIALLY_FILLED.
6. Begin transaction.
7. Lock order row.
8. Lock wallet or position row depending on locked asset.
9. Set remaining quantity to cancelled.
10. Release remaining locked cash or shares.
11. LedgerService writes ORDER_RELEASE transaction if cash is released.
12. Mark order CANCELLED or PARTIALLY_CANCELLED.
13. Commit.
14. Publish order book update.
```

## 7. Request Flow: Close Market

Flow:

```text
1. Scheduled job or admin command triggers close.
2. MarketService locks market row.
3. Validate market.status is OPEN or PAUSED.
4. Set market.status = CLOSED.
5. Cancel all open orders.
6. Release locked cash and shares.
7. Publish market closed event.
8. Queue resolution workflow.
```

## 8. Request Flow: Resolve And Settle Market

Flow:

```text
1. Oracle evidence is captured.
2. ResolutionService calculates candidate outcome if automation can do so.
3. Admin resolver proposes outcome.
4. Checker approves outcome.
5. SettlementService starts settlement with idempotency key.
6. Lock market row.
7. Validate market.status is PENDING_RESOLUTION or CLOSED.
8. Cancel any remaining open orders.
9. Calculate winning positions or void refunds.
10. Validate payout <= collateral.
11. Write balanced settlement ledger entries.
12. Credit user wallets.
13. Mark positions SETTLED or VOIDED.
14. Mark market RESOLVED or VOIDED.
15. Record settlement batch.
16. Commit.
17. Publish settlement notifications.
```

Settlement must not depend on platform profit.

## 9. API Groups

Initial REST groups:

```text
/auth
/users
/wallet
/markets
/orders
/trades
/positions
/settlement
/admin
/analytics
```

Initial WebSocket streams:

```text
/ws/markets/{market_id}/order-book
/ws/markets/{market_id}/trades
/ws/users/{user_id}/orders
/ws/users/{user_id}/wallet
/ws/users/{user_id}/notifications
```

API response rules:

```text
return integer minor units for money
include currency
include timestamps in ISO 8601 UTC
include stable IDs
include status fields
do not expose internal ledger account IDs unless admin endpoint
```

## 10. Background Jobs

V1 background jobs:

```text
market_close_job
oracle_poll_job
resolution_candidate_job
settlement_job
notification_dispatch_job
analytics_rollup_job
wallet_reconciliation_job
ledger_reconciliation_job
stale_order_book_snapshot_job
```

V1 scheduler:

```text
APScheduler or FastAPI background task runner for early development.
Move to Celery/RQ when job volume grows.
```

Job requirements:

```text
idempotent execution
retry with bounded attempts
structured logs
failure audit record for financial jobs
alert on repeated failure
```

## 11. Transaction And Locking Rules

Use PostgreSQL transactions for:

```text
order placement
order cancellation
matching fills
wallet movements
position movements
collateral movements
market close
settlement
void refunds
manual adjustments
```

Use row-level locks for:

```text
wallet rows being debited or credited
order rows being filled or cancelled
position rows being locked, released, increased, or decreased
market row during close and settlement
collateral pool row during fills and settlement
settlement batch row during retry
```

Use idempotency keys for:

```text
order placement
cancel order
deposit callback
withdrawal request
settlement execution
void refund
manual adjustment
```

## 12. Error Handling

Errors should be explicit and user-safe.

Examples:

```text
INSUFFICIENT_FUNDS
INSUFFICIENT_POSITION
MARKET_NOT_OPEN
MARKET_CLOSED
PRICE_OUT_OF_RANGE
INVALID_TICK_SIZE
QUANTITY_OUT_OF_RANGE
ORDER_ALREADY_FINAL
ORDER_NOT_FOUND
SELF_TRADE_BLOCKED
SETTLEMENT_ALREADY_COMPLETE
RESOLUTION_NOT_APPROVED
```

Do not expose raw database errors to users.

## 13. Observability

Log fields:

```text
request_id
user_id
admin_user_id
market_id
order_id
trade_id
settlement_id
ledger_transaction_id
event_type
status
error_code
```

Critical alerts:

```text
negative balance attempt
ledger imbalance
wallet-ledger mismatch
collateral mismatch
settlement retry failure
market stuck in PENDING_RESOLUTION
order matching exception
database transaction rollback spike
```

## 14. Testing Requirements

Required test groups:

```text
unit tests for pure validation logic
service tests for wallet, ledger, orders, matching, settlement
database transaction tests with PostgreSQL
API tests with httpx
idempotency tests
concurrency tests
reconciliation tests
```

Must-pass backend invariants:

```text
wallet balances never go negative
positions never go negative
filled_quantity never exceeds quantity
orders do not fill after close
cash locks before buy fills
shares lock before sell fills
ledger transactions always balance
collateral covers maximum payout
settlement can be retried without double credit
void refund can be retried without double refund
admin resolution writes audit record
```

## 15. Build Order

Recommended backend build order:

```text
1. Project scaffold and config.
2. Database connection and Alembic migrations.
3. Users and auth skeleton.
4. Wallet and ledger accounts.
5. Deposit test helper for local development.
6. Markets and outcomes.
7. Binary YES/NO market validation.
8. Order placement and cash locking.
9. Order cancellation and cash release.
10. Binary matching engine.
11. Trades and positions.
12. Collateral pool accounting.
13. Market close job.
14. Oracle evidence records.
15. Admin resolution proposal and checker approval.
16. Settlement and void handling.
17. API endpoints for frontend.
18. WebSocket order book and fill updates.
19. Analytics rollups.
20. Admin operations endpoints.
```

Do not build advanced market types before binary financial correctness is proven.

## 16. Out Of Scope For Early V1

Do not implement initially:

```text
market orders
naked shorting
leverage
fees
automated real-money settlement without checker approval
pre-settlement complete-set redemption
cross-market margining
external payment provider production integration
mobile app
microservices
```

## 17. Handoff Checklist

Backend implementation can start when these are ready:

```text
database schema spec approved
wallet and ledger spec approved
binary matching rules approved
settlement and void policy approved
admin resolution workflow approved
local Docker Compose plan approved
test database strategy approved
```

