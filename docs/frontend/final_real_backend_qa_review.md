# Final Real Backend QA Review

## Purpose

This artifact tracks the final Pred-Market V1 frontend completion pass against the real local FastAPI backend. The goal is not a new visual redesign; it is to verify that the renovated calm exchange-terminal UI works with seeded backend data, real auth cookies, persisted watchlists, wallet/order state, analytics endpoints, and WebSocket connection state.

## Local Runtime

Use this topology for real-backend QA:

```text
frontend: http://localhost:3000
backend: http://localhost:8010
postgres host port: 5433
redis host port: 6379
```

`localhost:8000` is intentionally not used for Pred-Market on the current machine because another Python app is bound to that port.

Frontend real mode:

```text
NEXT_PUBLIC_API_BASE_URL=http://localhost:8010
NEXT_PUBLIC_USE_MOCK_DATA=false
```

Mock mode remains available only for populated visual-preview review:

```text
NEXT_PUBLIC_USE_MOCK_DATA=true
```

## Startup Verification

Before visual QA, verify:

```bash
curl http://localhost:8010/api/v1/health
curl http://localhost:8010/api/v1/categories
curl http://localhost:8010/api/v1/markets
```

Then verify browser flows:

```text
sign in as trader@predmarket.dev
open wallet
add simulated funds
submit a YES limit order
cancel an open order
open portfolio and orders
sign in as admin@predmarket.dev
open admin queue and review detail
```

## Implemented Completion Items

- Frontend local API base now targets `http://localhost:8010`.
- Backend watchlist persistence is added through `GET /api/v1/watchlist`, `POST /api/v1/watchlist/{market_id}`, and `DELETE /api/v1/watchlist/{market_id}`.
- Admin review detail is available through `GET /api/v1/admin/markets/review/{review_id}`.
- Frontend API hooks now cover watchlist, market analytics, category analytics, user analytics, and admin market actions.
- Market cards, market tables, breadcrumbs, watchlist, and portfolio exposure no longer depend on static mock data in real mode.
- Market detail displays explicit realtime state: Live, Reconnecting, Stale, or Realtime ready.
- Portfolio current price, exposure, PnL, locked cash, and chart values now prefer real markets/user analytics when available.

## Visual Review Targets

Capture desktop `1440x900` and mobile `390x844` for:

```text
/markets
/categories/sports
/markets/ind-aus-final
/portfolio
/orders
/wallet
/admin
/markets/suggest
/sign-in
/watchlist
```

Captured screenshots are stored under:

```text
qa-screenshots/real-backend/
```

## Acceptance Checklist

- No unreadable buttons or overlapping text at desktop/mobile widths.
- Market discovery loads real backend markets when `NEXT_PUBLIC_USE_MOCK_DATA=false`.
- Signed-out protected routes redirect or show auth-required states without noisy blank screens.
- Trader can sign in, add simulated funds, submit/cancel a limit order, and see wallet/order/portfolio updates.
- Watchlist persists per user through the backend.
- Admin queue loads for admin role and denies non-admin users.
- Market detail shows chart, order book, recent trades, rules/evidence, related markets, sticky ticket, and realtime status.
- WebSocket connection failure is visible as reconnecting/stale rather than silent.
- Console has no unexpected errors; signed-out `401 /auth/me` probes are acceptable.

## Verification Results

Completed on July 10, 2026 against `http://localhost:8010` backend and `http://localhost:3002` frontend QA server.

Backend:

```text
alembic upgrade head: passed
seed dev data: passed
pytest: 25 passed, 1 Starlette/httpx deprecation warning
watchlist add/list: passed
admin review detail: passed
```

Frontend:

```text
npx impeccable detect app components: passed
npm run typecheck: passed
npm run lint: passed
npm run build: passed
```

Playwright real-backend QA:

```text
public routes: /markets, /categories/sports, /markets/ind-aus-final, /sign-in captured at desktop and mobile
trader routes: /watchlist, /portfolio, /orders, /wallet, /markets/suggest captured at desktop and mobile
admin routes: /admin and /admin/markets/{reviewId} captured at desktop and mobile
console: clean after signed-in route passes; signed-out /sign-in shows expected 401 /auth/me probe
```

Fixes made during QA:

```text
Next proxy now accepts backend-owned pm_refresh_token in real mode instead of requiring mock pm_session.
Wallet ledger filters duplicate accounting legs and labels available-cash debits as order locks.
Admin detail breadcrumbs now show Admin > Market review > Review detail instead of a raw path.
Mobile shell bottom padding increased for dense protected pages.
```

## Residual Risks

- Realtime fanout remains V1 process-local; the outbox keeps the design ready for Redis pub/sub or worker fanout later.
- V1 uses simulated funds only. Real money, KYC, AML, payments, withdrawals, and production compliance remain explicitly out of scope.
- Final human design approval still requires clicking through the local build after backend seeding.
