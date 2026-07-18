# Phase 7-8 Realtime, Analytics, And Frontend Integration Plan

## Summary

Phases 7-8 connect the simulated trading backend to the frontend and add V1 realtime/analytics foundations. The implementation remains simulated funds only and uses direct browser-to-FastAPI calls through `NEXT_PUBLIC_API_BASE_URL`.

## Phase 7 Backend Scope

- Add analytics rollups for markets, categories, and users.
- Add realtime event outbox rows for wallet, order, trade, position, market, admin, and settlement changes.
- Add WebSocket endpoint `WS /ws/v1`.
- Add public market channels and private user/admin channels.
- Store WebSocket tickets in Redis with a local development fallback.
- Compute order book from live open orders with seeded data fallback.

## Phase 8 Frontend Scope

- Keep mock mode behind `NEXT_PUBLIC_USE_MOCK_DATA=true`.
- Use FastAPI when `NEXT_PUBLIC_USE_MOCK_DATA=false`.
- Map backend `snake_case` DTOs into frontend `camelCase` view models.
- Wire auth, market reads, category reads, market detail, wallet, orders, portfolio, admin queue, suggestion submission, trade ticket, and realtime invalidation.
- Preserve the calm terminal visual direction and current responsive layouts.

## Acceptance Criteria

- Backend tests pass for analytics, realtime events, WebSocket auth, wallet, orders, matching, and settlement.
- Alembic upgrades apply through phase 7.
- Frontend typecheck, lint, and production build pass.
- Mock mode remains usable.
- Real mode can sign in with seeded users and read/write FastAPI state.

## Defaults

- WebSocket fanout is process-local for V1.
- DB realtime event outbox is source of record.
- Redis is used for WebSocket tickets when available.
- No real payments, KYC, AML, mobile app, or production multi-worker fanout is included.
