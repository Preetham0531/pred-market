# Phase 4-6 Backend Implementation Plan

## Summary

Phases 4-6 convert the Phase 1-3 backend foundation into a simulated-money trading backend. The scope is wallet/ledger, orders/matching/trades/positions, and admin-led settlement. Real deposits, withdrawals, KYC, live WebSockets, and production payment rails remain out of scope.

Implementation defaults:

- FastAPI modular monolith.
- PostgreSQL target schema with SQLite-compatible tests.
- SQLAlchemy 2 models and Alembic migrations.
- Simulated funds only.
- Limit orders only.
- Binary YES/NO matching uses complementary collateral: YES price + NO price must equal 100.
- Settlement requires maker-checker approval.

## Phase 4: Wallet And Double-Entry Ledger

### Build Scope

- Create `wallets` for every user.
- Create ledger accounts for:
  - user available cash
  - user locked cash
  - market collateral
  - external simulated deposit clearing
- Create balanced ledger transactions and entries.
- Add simulated test deposits.
- Lock available cash for buy orders.
- Release locked cash on cancellation.
- Move locked cash to market collateral after matched binary fills.
- Credit available cash from market collateral during settlement.

### Endpoints

- `GET /api/v1/wallet`
- `GET /api/v1/wallet/ledger`
- `POST /api/v1/wallet/test-deposit`

### Rules

- Wallet balances cannot go negative.
- Every ledger transaction must balance: total debits equal total credits.
- Mutating wallet endpoints should use `Idempotency-Key`.
- Test deposits are simulation-only and must never be reused for real payment behavior.

## Phase 5: Orders, Matching, Trades, Positions

### Build Scope

- Add orders, trades, and positions tables.
- Add limit order placement.
- Add order cancellation.
- Add binary complementary matching.
- Add same-outcome order book matching for non-binary markets.
- Add position creation and transfer logic.
- Add portfolio and trade read APIs.

### Endpoints

- `POST /api/v1/orders`
- `GET /api/v1/orders`
- `GET /api/v1/orders/{order_id}`
- `POST /api/v1/orders/{order_id}/cancel`
- `GET /api/v1/trades`
- `GET /api/v1/positions`
- `GET /api/v1/portfolio`

### Matching Rules

- Binary markets only match BUY YES against BUY NO when prices sum to 100.
- Matching is price-time priority.
- Partial fills are allowed.
- Self-trade matching is blocked.
- Buy orders lock cash at submitted limit price.
- Sell orders lock existing position quantity.
- Filled binary cash moves from user locked cash to market collateral.
- Filled same-outcome position transfers move buyer locked cash to seller available cash.

## Phase 6: Settlement And Resolution

### Build Scope

- Close markets.
- Cancel remaining open orders on close.
- Capture oracle/source evidence.
- Create resolution proposals.
- Approve proposals with maker-checker separation.
- Settle resolved or voided markets.
- Write audit logs for admin actions.

### Endpoints

- `POST /api/v1/admin/markets/{market_id}/close`
- `POST /api/v1/admin/markets/{market_id}/evidence`
- `POST /api/v1/admin/markets/{market_id}/resolution-proposals`
- `POST /api/v1/admin/resolution-proposals/{proposal_id}/approve`
- `POST /api/v1/admin/markets/{market_id}/settle`

### Settlement Rules

- Only closed markets can receive resolution proposals.
- A proposal can resolve to a winning outcome or void the market.
- The same admin cannot both propose and approve a resolution.
- Approved resolution is required before settlement.
- Resolved markets pay `100 * quantity` to positions on the winning outcome.
- Losing positions pay `0`.
- Voided markets refund `average_entry_price * quantity`.
- Settled positions move to `SETTLED` status with quantity zero and realized PnL recorded.

## Acceptance Criteria

- Wallet deposit writes a balanced ledger transaction.
- Reusing an idempotency key with the same deposit does not double-credit.
- Buy order placement locks cash.
- Order cancellation releases remaining locked cash.
- Complementary binary YES/NO orders match and create positions.
- Trade history includes both participants.
- Market close cancels remaining open orders.
- Evidence, proposal, approval, and settlement flows require admin/checker roles where appropriate.
- Maker-checker enforcement blocks self-approval.
- Settlement credits winning users and marks the market resolved.
- Alembic upgrades apply cleanly from an empty database.

## Implemented Files

- `backend/alembic/versions/0002_phase_4_6_trading.py`
- `backend/app/modules/wallets/`
- `backend/app/modules/orders/`
- `backend/app/modules/trades/`
- `backend/app/modules/positions/`
- `backend/app/modules/settlement/`
- `backend/tests/test_trading_wallet_orders_settlement.py`

## Out Of Scope For These Phases

- Real deposits and withdrawals.
- KYC/AML vendor integration.
- Payment processor reconciliation.
- WebSocket order book updates.
- Advanced matching worker isolation.
- Market maker APIs.
- Production-grade collateral risk engine.
- Dispute UI and public evidence review portal.
