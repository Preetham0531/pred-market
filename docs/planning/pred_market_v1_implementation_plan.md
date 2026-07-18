# Pred-Market V1 Implementation Plan

This document defines the implementation plan for moving Pred-Market from the current Next.js mock frontend into a working V1 exchange-style prediction market platform.

V1 default:

```text
simulated funds only
```

Real deposits, withdrawals, KYC vendor integration, AML operations, and jurisdiction-specific legal launch are later phases.

## 1. Implementation Goal

Build a serious prediction market product where users can:

```text
create an account
sign in securely
browse public markets
suggest markets for admin approval
trade limit orders using simulated funds
track orders, positions, wallet ledger, and analytics
receive realtime order book and trade updates
view transparent resolution rules and evidence
```

The platform should behave like:

```text
an exchange-style contract trading terminal
```

not:

```text
a sportsbook
a casino
a bookmaker
a marketing landing page
```

## 2. Current Repository State

Current implemented state:

```text
Next.js App Router frontend
TypeScript
Tailwind CSS
calm terminal visual direction
mock market/category/order/wallet/admin data
market discovery page
category dashboard pages
market detail pages
trade ticket UI
portfolio page
orders page
wallet page
market suggestion flow
admin review queue
```

Current documentation state:

```text
backend implementation spec
database schema spec
wallet and double-entry ledger spec
order matching engine spec
settlement and resolution spec
API contract spec
frontend design system spec
category rulebooks
analytics data model spec
compliance and risk policy spec
```

Major missing production pieces:

```text
FastAPI backend package
PostgreSQL migrations
Redis setup
real authentication service
server-side RBAC
wallet ledger implementation
matching engine implementation
settlement workers
WebSocket server
production API integration in frontend
automated test suite
deployment configuration
```

## 3. Architecture Decision

Use:

```text
Next.js frontend
FastAPI modular monolith backend
PostgreSQL source of truth
Redis for sessions, rate limiting, hot book snapshots, and pub/sub
```

Do not split into microservices in V1.

Reason:

```text
wallet, ledger, orders, matching, positions, and settlement need tight transaction boundaries
```

Internal backend modules:

```text
auth
users
markets
market_suggestions
wallets
ledger
orders
matching
trades
positions
settlement
admin
risk
analytics
notifications
realtime
audit
```

## 4. Build Order

The backend and frontend should be built in this dependency order:

```text
auth
users
markets
wallet/ledger
orders/matching
positions
settlement
analytics
admin
frontend API integration
```

This order is mandatory because:

```text
orders require authenticated users
orders require available balance
matching requires valid locked funds or locked shares
positions require trades
settlement requires positions and collateral
analytics requires stable events and rollups
admin requires market, settlement, and audit workflows
```

## 5. Phase 1: Backend Scaffold

Create a backend package:

```text
backend/
  app/
    main.py
    core/
    api/
    modules/
    db/
    tests/
  alembic/
  pyproject.toml
  Dockerfile
```

Create local infrastructure:

```text
docker-compose.yml
PostgreSQL
Redis
backend env file example
frontend env file example
```

Required backend endpoints:

```text
GET /health
GET /api/v1/health
GET /api/v1/version
```

Acceptance criteria:

```text
backend starts locally
PostgreSQL connects
Redis connects
OpenAPI docs load
health endpoint returns ok
pytest runs
```

## 6. Phase 2: Auth And Users

Implement the auth system defined in:

```text
docs/backend/auth_and_session_spec.md
```

Required endpoints:

```text
POST /api/v1/auth/sign-up
POST /api/v1/auth/sign-in
POST /api/v1/auth/sign-out
POST /api/v1/auth/refresh
GET /api/v1/auth/me
POST /api/v1/auth/verify-email/request
POST /api/v1/auth/verify-email/confirm
POST /api/v1/auth/password-reset/request
POST /api/v1/auth/password-reset/confirm
POST /api/v1/auth/ws-ticket
```

Required user fields:

```text
email
display_name
status
roles
email_verified_at
kyc_status
jurisdiction_code
failed_login_count
locked_until
last_login_at
```

Acceptance criteria:

```text
users can sign up
users can sign in
users can sign out
sessions refresh safely
invalid credentials are rejected
admin role gates admin APIs
auth actions create audit logs
```

## 7. Phase 3: Markets And Suggestions

Implement public market read APIs first:

```text
GET /api/v1/markets
GET /api/v1/markets/{market_id}
GET /api/v1/markets/{market_id}/order-book
GET /api/v1/markets/{market_id}/price-history
GET /api/v1/categories/{category_slug}
```

Implement market suggestion flow:

```text
POST /api/v1/market-suggestions
GET /api/v1/market-suggestions/{suggestion_id}
```

Implement admin approval:

```text
GET /api/v1/admin/markets/review
POST /api/v1/admin/markets/{market_id}/approve
POST /api/v1/admin/markets/{market_id}/pause
```

Acceptance criteria:

```text
public users can browse approved markets
signed-in users can suggest markets
suggestions run policy checks
admins can approve or reject suggestions
all admin actions are audited
```

## 8. Phase 4: Simulated Wallet And Ledger

Implement wallet and ledger from:

```text
docs/backend/wallet_double_entry_ledger_spec.md
```

V1 wallet mode:

```text
simulated only
```

Required endpoints:

```text
GET /api/v1/wallet
GET /api/v1/wallet/ledger
POST /api/v1/wallet/test-deposit
```

Do not implement real:

```text
deposits
withdrawals
payment provider webhooks
bank transfer reconciliation
```

Acceptance criteria:

```text
test deposits create balanced ledger transactions
wallet available balance cannot go negative
order locks reduce available balance
releases restore available balance
ledger entries are immutable
reconciliation checks pass
```

## 9. Phase 5: Orders, Matching, Trades, Positions

Implement order matching from:

```text
docs/backend/order_matching_engine_spec.md
```

V1 order rules:

```text
limit orders only
no market orders
price-time priority
partial fills allowed
self-trade blocked by default
idempotency required for order commands
```

Required endpoints:

```text
POST /api/v1/orders
GET /api/v1/orders
GET /api/v1/orders/{order_id}
POST /api/v1/orders/{order_id}/cancel
GET /api/v1/trades
GET /api/v1/positions
GET /api/v1/portfolio
```

Acceptance criteria:

```text
binary YES/NO orders match correctly
multiple-choice outcome books match correctly
partial fills update remaining quantity
cancellations release locked funds
trades update positions
positions reconcile to trades
```

## 10. Phase 6: Settlement And Resolution

Implement settlement from:

```text
docs/backend/settlement_resolution_spec.md
```

Required admin endpoints:

```text
POST /api/v1/admin/markets/{market_id}/close
POST /api/v1/admin/markets/{market_id}/evidence
POST /api/v1/admin/markets/{market_id}/resolution-proposals
POST /api/v1/admin/resolution-proposals/{proposal_id}/approve
POST /api/v1/admin/markets/{market_id}/settle
```

Required controls:

```text
maker-checker approval
admin self-approval blocked
oracle evidence stored before settlement
void policy supported
settlement retries idempotent
audit logs for all sensitive actions
```

Acceptance criteria:

```text
closed markets reject new orders
winning contracts receive payout
losing contracts receive zero
void markets refund collateral
settlement can be retried safely
admin override is audited
```

## 11. Phase 7: Realtime And Analytics

Implement WebSocket events:

```text
order_book.snapshot
order_book.delta
trade.created
order.updated
position.updated
wallet.updated
market.status_changed
notification.created
```

Implement analytics rollups from:

```text
docs/analytics/analytics_data_model_spec.md
```

Acceptance criteria:

```text
market pages update order book without refresh
trade ticket reflects user order state
portfolio updates after fills
wallet updates after locks and releases
charts have loading, empty, stale, and live states
```

## 12. Phase 8: Frontend API Integration

Replace frontend mock data gradually:

```text
auth first
public markets
market detail
order book and trades
wallet
orders
positions and portfolio
admin queue
analytics
```

Frontend environment flags:

```text
NEXT_PUBLIC_API_BASE_URL
NEXT_PUBLIC_USE_MOCK_DATA
```

Rules:

```text
mock data may exist only behind development flag
no localStorage auth tokens
use HttpOnly cookies for browser sessions
show loading, empty, error, stale, and unauthorized states
```

## 13. Local Development Workflow

Frontend:

```bash
npm install
NEXT_PUBLIC_API_BASE_URL=http://localhost:8010
NEXT_PUBLIC_USE_MOCK_DATA=false
npm run dev
npm run typecheck
npm run lint
npm run build
```

Backend:

```bash
cd backend
uv sync
DATABASE_URL=postgresql+psycopg://pred_market:pred_market@localhost:5433/pred_market uv run alembic upgrade head
DATABASE_URL=postgresql+psycopg://pred_market:pred_market@localhost:5433/pred_market uv run python -m app.seed.dev
uv run pytest
DATABASE_URL=postgresql+psycopg://pred_market:pred_market@localhost:5433/pred_market uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8010
```

Infrastructure:

```bash
docker compose up -d postgres redis
```

Local ports:

```text
frontend: http://localhost:3000
backend: http://localhost:8010
postgres host port: 5433
redis host port: 6379
```

## 14. Testing Requirements

Backend tests:

```text
auth sign-up/sign-in/sign-out/refresh
duplicate email
password reset expiry
email verification
admin role enforcement
wallet no-negative-balance
ledger balancing
order matching
partial fills
cancellation release
self-trade rejection
settlement payout
void refund
idempotent retries
WebSocket event shape
```

Frontend tests:

```text
auth route redirects
sign-in and sign-up forms
market discovery filters
trade ticket calculations
order preview and submit states
order cancellation state
wallet simulated deposit state
admin review navigation
mobile navigation
keyboard navigation
reduced-motion mode
```

## 15. Launch Checklist

Before V1 simulated launch:

```text
all protected routes require session
admin routes require admin role
all money movements use double-entry ledger
all order commands are idempotent
all admin actions are audited
all settlement actions are retry-safe
frontend has no dead navigation
mock data flag is explicit
system can be reset for test environment
```

Before any real-money launch:

```text
lawyer approves jurisdiction strategy
KYC/AML provider is integrated
payment provider is integrated
withdrawal operations are documented
tax/reporting assumptions are documented
fraud monitoring is live
data protection review is complete
incident response plan is approved
```
