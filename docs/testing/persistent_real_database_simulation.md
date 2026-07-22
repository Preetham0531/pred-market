# Persistent Real-Database Trading Simulation

Completed on July 18, 2026 against:

```text
Frontend proxy: http://localhost:3000
FastAPI backend: http://127.0.0.1:8010
PostgreSQL: localhost:5433/pred_market
Redis: localhost:6379
```

## Purpose

This run persists the deterministic multi-user trading simulation in the local PostgreSQL database. Unlike the isolated pytest simulation, the resulting users, markets, orders, trades, positions, wallet balances, and settlement remain available to the frontend.

The development-only runner is:

```bash
cd backend
source .venv/bin/activate
python -m app.seed.simulation
```

It uses fixed user emails and idempotency keys, refuses non-PostgreSQL and non-development environments, executes product actions through the live FastAPI API, and verifies final records directly in PostgreSQL.

## Persisted Results

```text
Simulation users: 20
Simulation wallets: 20
Admin-issued markets: 6
Primary orders: 75
Negative-path order records: 4
Trades: 37
Positions: 74
Settlements: 1
Negative checks: 14
Realtime events for simulation markets: 387
Relevant audit events: 88
Ledger debits: 2,124,939
Ledger credits: 2,124,939
```

The ledger is balanced.

## Markets

Five simulation markets remain open and one is resolved:

```text
RESOLVED  Will Alpha Cricket Club win the persistent simulation final?
OPEN      Will Beta Football Club win the persistent simulation cup?
OPEN      Will the persistent simulation CPI release exceed 4 percent?
OPEN      Will persistent simulation rainfall exceed 20 millimetres?
OPEN      Will a public AI model launch in the persistent simulation window?
OPEN      Will the persistent simulation commodity benchmark exceed 2500?
```

## Users

```text
sim-user-01@predmarket.dev
...
sim-user-20@predmarket.dev
```

All simulation users use `StrongPass123` in local development and have the `USER` role. They are searchable through the admin Switch User View interface.

## Happy Paths Verified

- Twenty real user accounts and wallets were created.
- Each user received one idempotent simulated deposit.
- Six markets passed the admin draft pipeline and were listed.
- Thirty-six complementary YES/NO order pairs matched.
- One partial fill left a resting quantity in the order book.
- One unmatched order locked cash and cancellation released it.
- Market detail returned computed order-book levels and recent trades.
- Trades produced persistent positions and realtime events.
- One market closed, received evidence, passed maker-checker approval, and settled to YES.
- Winner payouts and loser zero-payout records were persisted.
- Analytics recomputation completed.
- Global ledger debit and credit totals remained equal.

## Negative Paths Verified

- Unauthenticated order rejected.
- Normal user blocked from admin draft creation.
- Duplicate market title flagged `NEEDS_CHANGES`.
- Draft without an approved settlement source blocked from approval.
- Price zero rejected.
- Price 100 rejected.
- Quantity zero rejected.
- Insufficient balance rejected.
- Non-owner cancellation rejected.
- Same-user complementary orders remained open and did not self-match.
- Repeated idempotency key returned the same order.
- Missing idempotency key rejected.
- Resolved/closed market rejected a new order.
- Trader suggestion created a draft but did not auto-list.

## Defects Found And Fixed

### Draft self-duplicate detection

Updating a `NEEDS_CHANGES` draft caused duplicate detection to compare the draft against itself, permanently blocking approval. Validation now excludes the current draft during update and approval, with regression coverage.

### PostgreSQL settlement key overflow

Settlement ledger idempotency keys and reference IDs could exceed their PostgreSQL column lengths for long market IDs. Settlement now uses a deterministic SHA-256 idempotency key and a bounded settlement/position reference. Regression assertions enforce the schema limits.

## Verification

```text
Backend pytest: 39 passed
Frontend TypeScript: passed
Frontend markets API: 6 persistent markets returned
Admin user search API: 20 simulation users returned
```

One existing Starlette/httpx deprecation warning remains; it does not affect simulation behavior.
