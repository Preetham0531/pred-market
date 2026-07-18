# Order Matching Engine Spec

This document defines the Pred-Market V1 order matching engine: binary YES/NO matching, multiple-choice order books, partial fills, cancellation, price-time priority, self-trade rules, idempotency, concurrency, and tests.

This is planning documentation only. It does not create backend code or database migrations.

## 1. Matching Goal

The matching engine must:

```text
match compatible user orders
never take platform directional risk
never fill without locked collateral or locked shares
preserve price-time priority
support partial fills
be safe under retries and concurrency
write auditable trades, ledger entries, positions, and collateral movements
```

V1 assumptions:

```text
limit orders only
no market orders
no naked shorting
no leverage
no fees initially
PostgreSQL is the source of truth
matching runs inside backend modular monolith
matching uses database transactions and row locks
```

## 2. Supported Market Types

V1 matching modes:

```text
BINARY_COMPLEMENTARY
OUTCOME_ORDER_BOOK
```

Market type mapping:

```text
BINARY -> BINARY_COMPLEMENTARY
THRESHOLD -> BINARY_COMPLEMENTARY
CONDITIONAL -> BINARY_COMPLEMENTARY
COMBO -> BINARY_COMPLEMENTARY
MULTIPLE_CHOICE -> OUTCOME_ORDER_BOOK
RANGE -> OUTCOME_ORDER_BOOK
```

Scalar markets are out of scope for early V1 matching.

## 3. Order Model

Core order fields:

```text
id
user_id
market_id
outcome_id
market_rule_id
side
price_minor
quantity
filled_quantity
cancelled_quantity
remaining_quantity
locked_cash_minor
locked_shares
status
idempotency_key
created_at
updated_at
cancelled_at
```

Order side:

```text
BUY
SELL
```

Order statuses:

```text
OPEN
PARTIALLY_FILLED
FILLED
CANCELLED
PARTIALLY_CANCELLED
REJECTED
EXPIRED
```

Core invariant:

```text
filled_quantity + cancelled_quantity + remaining_quantity = quantity
```

## 4. Pre-Match Validation

Before an order can enter matching:

```text
market.status == OPEN
market.close_time > now
user.status == ACTIVE
user passes jurisdiction and KYC checks
outcome.status == ACTIVE
price_minor > 0
price_minor <= payout_amount_minor
price_minor % tick_size_minor == 0
quantity >= min_quantity
quantity <= max_quantity
idempotency key is valid
```

For buy orders:

```text
wallet.available_balance_minor >= price_minor * quantity
cash is locked before matching starts
```

For sell orders:

```text
position.quantity - position.locked_quantity >= quantity
shares are locked before matching starts
```

## 5. Binary YES/NO Matching

Binary V1 uses strict complementary buy-side matching.

Invariant:

```text
YES price + NO price = payout
```

Incoming YES order:

```text
required NO price = payout - yes_price
match resting NO orders at required NO price
```

Incoming NO order:

```text
required YES price = payout - no_price
match resting YES orders at required YES price
```

Example:

```text
payout = 10000
incoming BUY YES at 4000
matches resting BUY NO at 6000
```

Do not match:

```text
YES 4000 with NO 5000
YES 4000 with two NO orders at 3000 each
YES and YES
NO and NO
orders from closed markets
orders without locked cash
```

## 6. Binary Matching Priority

Strict binary matching priority:

```text
1. exact compatible price
2. earliest created_at
3. stable order_id tiebreaker
```

Because compatible price is exact in strict V1, price improvement is not supported.

Later CLOB behavior can add:

```text
sell owned shares
crossing orders
price improvement
market orders
```

These are out of scope for early V1 binary.

## 7. Multiple-Choice And Range Order Books

Multiple-choice and range markets use one order book per outcome.

Buy matching:

```text
incoming BUY outcome at limit price P
matches lowest SELL orders for same outcome where sell_price <= P
```

Sell matching:

```text
incoming SELL outcome at limit price P
matches highest BUY orders for same outcome where buy_price >= P
```

Priority:

```text
BUY book: highest price first, then earliest created_at, then order_id
SELL book: lowest price first, then earliest created_at, then order_id
```

Seller rule:

```text
seller must own unlocked shares before placing sell order
```

No naked shorting in V1.

## 8. Fill Price Rules

For OUTCOME_ORDER_BOOK:

```text
fill price = resting order price
```

Reason:

```text
resting maker order defines available liquidity
incoming taker accepts price within limit
```

Examples:

```text
incoming BUY at 4500 matches resting SELL at 4200 -> fill price 4200
incoming SELL at 4200 matches resting BUY at 4500 -> fill price 4500
```

For BINARY_COMPLEMENTARY:

```text
fill uses both locked side prices:
YES price = yes_order.price_minor
NO price = no_order.price_minor
YES + NO must equal payout
```

## 9. Partial Fills

Fill quantity:

```text
fill_quantity = min(incoming.remaining_quantity, resting.remaining_quantity)
```

After fill:

```text
order.filled_quantity += fill_quantity
order.remaining_quantity -= fill_quantity
```

Status update:

```text
remaining_quantity == 0 -> FILLED
filled_quantity > 0 and remaining_quantity > 0 -> PARTIALLY_FILLED
filled_quantity == 0 and remaining_quantity > 0 -> OPEN
```

Partially filled orders may remain in the order book unless cancelled or expired.

## 10. Cash And Share Lock Handling

Buy order placement:

```text
lock price_minor * quantity cash
```

Buy fill:

```text
consume locked cash equal to fill_price * fill_quantity
```

If OUTCOME_ORDER_BOOK buyer gets price improvement:

```text
release difference between buyer limit and fill price for filled quantity
```

Example:

```text
buyer locks 4500 * 10
fills 10 at 4200
release 300 * 10
```

Sell order placement:

```text
lock quantity shares
```

Sell fill:

```text
transfer fill_quantity shares to buyer
reduce seller locked shares
credit seller available cash
```

Cancel unfilled remainder:

```text
buy order -> release unfilled locked cash
sell order -> release unfilled locked shares
```

## 11. Binary Fill Workflow

Flow:

```text
1. OrderService validates incoming order and locks cash.
2. MatchingService receives order_id.
3. Begin or join database transaction.
4. Lock market row if needed.
5. Lock incoming order row.
6. Query compatible resting orders by exact complementary price.
7. Lock resting order row.
8. Lock both user wallet rows in deterministic order.
9. Lock market collateral pool row.
10. Validate both orders are still fillable.
11. Calculate fill quantity.
12. Move both users' locked cash into market collateral.
13. Create trade record.
14. Increase YES and NO positions.
15. Create position events.
16. Create balanced ledger transaction.
17. Update order filled/remaining/status.
18. Continue until incoming order filled or no compatible resting order remains.
19. Commit.
20. Publish order book, trade, and user order events.
```

Required binary fill checks:

```text
yes_price + no_price == payout
both orders belong to same market
orders are opposite outcomes
both orders have locked cash
fill quantity > 0
market is still OPEN at fill time
```

## 12. Outcome Order Book Fill Workflow

Flow:

```text
1. OrderService validates incoming order and locks cash/shares.
2. MatchingService receives order_id.
3. Begin or join database transaction.
4. Lock incoming order row.
5. Query same-market same-outcome opposite-side resting orders.
6. Apply price-time priority.
7. Lock resting order row.
8. Lock affected wallet and position rows in deterministic order.
9. Validate both orders are still fillable.
10. Calculate fill quantity and fill price.
11. Move buyer locked cash to seller available cash.
12. Transfer shares from seller position to buyer position.
13. Release buyer price-improvement cash if applicable.
14. Create trade record.
15. Create position events.
16. Create balanced ledger transaction.
17. Update order filled/remaining/status.
18. Continue until incoming order filled or no crossing liquidity remains.
19. Commit.
20. Publish order book, trade, and user order events.
```

## 13. Cancellation Rules

User can cancel:

```text
own OPEN order
own PARTIALLY_FILLED order
```

Admin can cancel:

```text
orders in paused/closed/compliance-locked market
orders for suspended user
orders during incident response
```

Cancel flow:

```text
1. Load order.
2. Validate cancellable status.
3. Begin transaction.
4. Lock order row.
5. Re-check status.
6. Set cancelled_quantity += remaining_quantity.
7. Set remaining_quantity = 0.
8. Release locked cash or locked shares.
9. Write ledger ORDER_RELEASE for cash.
10. Mark status CANCELLED or PARTIALLY_CANCELLED.
11. Commit.
12. Publish order book and order status events.
```

Cancellation must be idempotent:

```text
second cancel call returns current final state
no second release happens
```

## 14. Self-Trade Rules

Default V1 policy:

```text
self-trade is blocked
```

Self-trade means:

```text
incoming order user_id == resting order user_id
```

When self-trade is detected:

```text
skip matching against own resting order
leave both orders open if otherwise valid
emit risk event SELF_TRADE_ATTEMPT
```

Do not automatically cancel either order unless risk policy requires it.

Future policy options:

```text
cancel newest
cancel oldest
decrement both
allow for disclosed market makers
```

Not supported in V1 without explicit policy review.

## 15. Idempotency

Required idempotency keys:

```text
place order
cancel order
admin cancel order
matching job retry if decoupled
```

Place order behavior:

```text
same key + same request hash -> return existing order result
same key + different request hash -> reject
```

Cancel behavior:

```text
same key + same request hash -> return existing cancel result
same key + different request hash -> reject
```

Trade creation idempotency:

```text
unique pair/fill guard should prevent duplicate fills for same order state
```

Recommended fill idempotency key:

```text
market_id + incoming_order_id + resting_order_id + incoming_filled_before + resting_filled_before
```

## 16. Concurrency And Locking

Use PostgreSQL row-level locks.

Lock order:

```text
1. market row if needed
2. collateral pool row if binary fill
3. order rows by UUID ascending
4. wallet rows by UUID ascending
5. position rows by UUID ascending
```

Use:

```text
SELECT ... FOR UPDATE
```

Matching query may use:

```text
FOR UPDATE SKIP LOCKED
```

Use `SKIP LOCKED` carefully:

```text
acceptable for high-throughput matching
must not violate price-time priority among unlocked eligible orders
must be covered by tests
```

Early V1 can avoid `SKIP LOCKED` until performance requires it.

## 17. Order Book Snapshots

Order book source:

```text
open orders in PostgreSQL
```

Redis may cache:

```text
best bid/ask
depth by price
recent trade feed
```

Redis cache must be rebuildable from PostgreSQL.

Snapshot fields:

```text
market_id
outcome_id
side
price_minor
quantity
order_count
last_sequence
generated_at
```

## 18. Realtime Events

Publish after commit only.

Events:

```text
order.created
order.partially_filled
order.filled
order.cancelled
trade.executed
order_book.updated
position.updated
wallet.updated
```

Event fields:

```text
event_id
event_type
sequence
market_id
user_id when private
payload
created_at
```

Clients must be able to resync with REST snapshot.

## 19. Failure Handling

If matching fails inside transaction:

```text
rollback all changes
return safe error
leave no partial wallet/position/ledger update
```

If event publish fails after commit:

```text
do not rollback financial transaction
write outbox event before commit
background dispatcher retries publish
```

Recommended:

```text
transactional outbox table for realtime/event publishing
```

## 20. Required Tests

Binary tests:

```text
YES 4000 matches NO 6000 when payout is 10000
YES 4000 does not match NO 5000
NO 6000 matches YES 4000
partial fill across multiple compatible orders
many-to-many fill preserves quantities
same-user compatible orders do not self-trade
market close prevents fill
locked cash moves to collateral
ledger balances after fill
positions increase correctly
duplicate place order idempotency does not double lock
duplicate matching retry does not double fill
```

Outcome order book tests:

```text
BUY matches lowest SELL at or below limit
SELL matches highest BUY at or above limit
resting price is fill price
price improvement releases buyer excess lock
seller cannot sell unowned shares
partial fill leaves remaining order open
cancel releases unfilled cash
cancel releases unfilled shares
duplicate cancel does not double release
price-time priority is preserved
```

Concurrency tests:

```text
two incoming orders cannot overfill same resting order
cancel during match cannot release already-filled lock
wallet never goes negative under concurrent orders
position never goes negative under concurrent sells
deadlock retry is safe only with idempotency
```

## 21. Out Of Scope For V1

Do not implement initially:

```text
market orders
stop orders
iceberg orders
post-only orders
time-in-force variants beyond default GTC
naked shorting
cross-market margin
automated market maker
platform market making
price improvement for binary complementary matching
```

