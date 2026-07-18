# Pred-Market V1 Tech Stack And Database Plan

This document records the recommended technology stack, database design direction, and implementation foundation for Pred-Market V1. No code or database setup is created here; this is planning documentation only.

## 1. Product Type

Pred-Market V1 is a binary prediction market exchange.

It should support:

```text
- user accounts
- wallets
- market creation/suggestion
- admin market approval
- YES/NO binary contracts
- order book trading
- user-to-user matching
- fully collateralized trades
- position tracking
- market close
- outcome resolution
- settlement and payouts
- audit logs
- admin controls
```

The most important business rule:

```text
Pred-Market V1 is an exchange, not a sportsbook.
```

The platform should match users against other users. It should not take directional risk against users.

## 2. Recommended Stack

### Backend

Recommended:

```text
Python + FastAPI
```

Why:

```text
- Fast to build V1 APIs
- Good async support
- Excellent OpenAPI documentation generation
- Easy to test
- Works well with PostgreSQL
- Python is good for future analytics, risk scoring, and market simulations
```

Alternative:

```text
Node.js + NestJS
```

Why not first choice for this project:

```text
- Good backend framework, but Python gives better future flexibility for analytics and simulations.
```

Decision:

```text
Use Python + FastAPI for V1.
```

## 3. Database

Recommended:

```text
PostgreSQL
```

Why PostgreSQL:

```text
- strong transactions
- row-level locking
- reliable relational constraints
- good indexing
- supports JSONB for flexible metadata
- mature migration tooling
- excellent fit for wallets, orders, trades, positions, and ledgers
```

This product needs correctness more than raw speed at V1.

Critical financial operations need ACID transactions:

```text
- lock user funds
- match orders
- create trades
- update positions
- write ledger entries
- settle markets
```

Decision:

```text
Use PostgreSQL as the primary database.
```

## 4. ORM And Migrations

Recommended:

```text
SQLAlchemy 2.x + Alembic
```

Why:

```text
- mature Python ORM
- supports explicit transactions
- works well with PostgreSQL
- Alembic is the standard migration tool
- good control over schema and queries
```

Decision:

```text
Use SQLAlchemy for models and Alembic for migrations.
```

## 5. API Layer

Recommended:

```text
FastAPI
Pydantic
Uvicorn
```

Responsibilities:

```text
- validate request payloads
- expose REST APIs
- generate OpenAPI docs
- authenticate users
- route commands to services
- return market/order/position/wallet data
```

Initial API groups:

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
```

## 6. Realtime Layer

For V1, start simple.

Recommended:

```text
FastAPI WebSockets
```

Use for:

```text
- order book updates
- trade/fill updates
- market price updates
- settlement notifications
```

Later upgrade path:

```text
Redis Pub/Sub
Kafka
NATS
```

Decision:

```text
Use simple WebSockets first, design events so they can later move to Redis/Kafka.
```

## 7. Cache And Queues

Recommended for V1:

```text
Redis
```

Use Redis for:

```text
- sessions or token denylist if needed
- hot order book snapshots
- rate limiting
- lightweight pub/sub
- background job coordination
```

Do not make Redis the source of truth for orders/trades/wallets.

Source of truth:

```text
PostgreSQL
```

Cache:

```text
Redis
```

## 8. Background Jobs

Recommended:

```text
Celery + Redis
```

or simpler V1:

```text
FastAPI background tasks / APScheduler
```

Use background jobs for:

```text
- market close jobs
- oracle polling
- settlement execution
- notification sending
- reconciliation checks
- analytics rollups
```

Decision:

```text
Start with simple scheduled/background jobs.
Move to Celery/RQ when job volume grows.
```

## 9. Authentication

Recommended V1:

```text
Email/password or passwordless login
JWT access tokens
refresh tokens
```

Later:

```text
OAuth
2FA
device trust
KYC provider integration
```

Core auth requirements:

```text
- user identity
- admin role
- market creator role if needed
- market maker role if needed
```

## 10. Frontend

Recommended:

```text
Next.js + TypeScript
```

Why:

```text
- strong React ecosystem
- good routing and server rendering
- good developer experience
- easy dashboard/admin UI
- works well with REST/WebSocket APIs
```

UI areas:

```text
- market discovery
- market detail page
- YES/NO trade ticket
- order book display
- user portfolio
- wallet page
- transaction history
- admin review console
```

Decision:

```text
Use Next.js + TypeScript when frontend begins.
```

## 11. Matching Engine Placement

For V1, keep the matching engine inside the backend service.

Recommended:

```text
FastAPI service layer + PostgreSQL transactions
```

Why:

```text
- simpler
- easier to debug
- easier to keep wallet/order/trade updates atomic
- enough for V1
```

Later upgrade:

```text
separate matching-engine service
event-driven architecture
in-memory order books with persisted event log
```

Decision:

```text
Start monolith-first, but keep matching logic isolated in its own module/service.
```

## 12. Architecture Style

Recommended V1 architecture:

```text
Modular monolith
```

Not microservices at first.

Why:

```text
- faster to build
- fewer deployment problems
- easier database transactions
- easier local development
- easier debugging
```

Internal modules:

```text
auth
users
wallets
markets
contracts
orders
matching
trades
positions
ledger
settlement
admin
notifications
risk
```

Future split candidates:

```text
matching service
market data service
settlement service
notification service
analytics service
```

## 13. Core Database Tables

Minimum V1 tables:

```text
users
wallets
markets
contracts
orders
trades
positions
ledger_entries
market_rules
oracle_evidence
settlements
audit_logs
notifications
```

Important table relationships:

```text
users -> wallets
users -> orders
users -> positions
markets -> contracts
markets -> orders
markets -> trades
markets -> settlements
orders -> trades
trades -> ledger_entries
markets -> oracle_evidence
```

## 14. Database Design Principles

Use integer minor units for money.

Example:

```text
₹100.00 = 10000 paise
```

Do not store money as floating-point numbers.

Use:

```text
integer amount_minor
```

or:

```text
NUMERIC(20, 4)
```

Recommended V1:

```text
Store money as integer minor units.
```

Examples:

```text
payout_amount = 10000
yes_price = 4000
no_price = 6000
```

Meaning:

```text
payout = ₹100.00
YES price = ₹40.00
NO price = ₹60.00
```

## 15. Critical Database Constraints

Important constraints:

```text
orders.price > 0
orders.quantity > 0
orders.filled_quantity <= orders.quantity
contracts.payout_amount > 0
wallets.available_balance >= 0
wallets.locked_balance >= 0
trades.yes_price + trades.no_price = trades.payout_amount
trades.quantity > 0
```

Some constraints may be enforced in application logic plus tests if database-level checks are awkward.

But the most important invariant must always hold:

```text
YES price + NO price = payout
```

## 16. Transaction Boundaries

These operations must be transactional:

```text
- place order and lock funds
- match orders
- create trade
- update positions
- update wallet balances
- write ledger entries
- cancel order and release funds
- settle market
```

Example transaction:

```text
BEGIN
  lock user wallet row
  validate available balance
  move funds from available to locked
  create order
  try matching
  create trades
  update positions
  write ledger entries
COMMIT
```

If anything fails:

```text
ROLLBACK
```

## 17. Locking Strategy

V1 can use PostgreSQL row-level locks.

Use locks when touching:

```text
- wallet rows
- order rows involved in matching
- market row during settlement
```

Likely patterns:

```text
SELECT ... FOR UPDATE
```

Use idempotency keys for order placement and settlement calls.

## 18. Matching Rule For V1

Strict matching:

```text
incoming YES at price Y matches resting NO at price N only if:
Y + N = payout
```

Incoming NO at price N matches resting YES at price Y only if:

```text
N + Y = payout
```

Priority:

```text
1. compatible price
2. earliest created_at
```

This is enough for the first implementation.

## 19. Services To Build

Recommended backend services/modules:

```text
UserService
AuthService
WalletService
MarketService
ContractService
OrderService
MatchingService
TradeService
PositionService
LedgerService
SettlementService
NotificationService
RiskService
AdminService
```

Most important early services:

```text
WalletService
OrderService
MatchingService
LedgerService
PositionService
SettlementService
```

## 20. Testing Strategy

Core testing should focus on financial correctness.

Test types:

```text
unit tests
service tests
database transaction tests
API tests
settlement tests
property/invariant tests
```

Must-test invariants:

```text
- no negative wallet balances
- matched YES + NO equals payout
- settlement pays exactly the winning liability
- cancelled orders release funds
- partial fills update quantities correctly
- repeated settlement call does not double pay
```

Recommended testing tools:

```text
pytest
pytest-asyncio
httpx
factory_boy
testcontainers or dockerized PostgreSQL
```

## 21. Local Development Setup

When implementation starts, use:

```text
Docker Compose
```

Services:

```text
backend
postgres
redis
frontend
```

Useful local tools:

```text
pgAdmin or TablePlus
RedisInsight
Makefile
ruff
pytest
alembic
```

## 22. Deployment Direction

V1 deployment can be simple:

```text
Backend: containerized FastAPI app
Database: managed PostgreSQL
Cache: managed Redis
Frontend: Vercel or containerized Next.js
Object storage: S3-compatible storage
```

Possible platforms:

```text
Render
Fly.io
Railway
AWS
GCP
DigitalOcean
```

For serious money movement, prefer:

```text
AWS/GCP with managed PostgreSQL and strong observability
```

## 23. Observability

Need from early V1:

```text
structured logs
request IDs
trade IDs
order IDs
audit logs
error tracking
metrics
```

Recommended:

```text
Sentry for errors
OpenTelemetry later
Prometheus/Grafana later
```

Critical alerts:

```text
- wallet balance mismatch
- failed settlement
- order matching exception
- negative balance attempt
- database transaction failure
- market stuck in pending resolution
```

## 24. Admin And Operations

Admin console must support:

```text
- approve/reject markets
- pause markets
- close markets
- add oracle evidence
- resolve outcome
- inspect orders/trades
- inspect user wallet ledger
- handle disputes
```

Admin actions must be audited.

Audit entry should include:

```text
admin_user_id
action
entity_type
entity_id
before_state
after_state
created_at
```

## 25. Recommended Build Order

Do not start with the frontend.

Recommended build order:

```text
1. Database schema
2. Wallet and ledger
3. Market and contract model
4. Limit orders
5. Matching engine
6. Positions
7. Settlement
8. Admin resolution
9. API endpoints
10. Realtime order book updates
11. Frontend market page
12. Trade ticket
13. Portfolio/wallet page
14. Admin console
```

Reason:

```text
The hardest part is financial correctness, not UI.
```

## 26. Final Stack Decision

Recommended final V1 stack:

```text
Backend:
Python, FastAPI, Pydantic, SQLAlchemy, Alembic

Database:
PostgreSQL

Cache/Realtime Support:
Redis

Background Jobs:
Start simple, later Celery/RQ if needed

Frontend:
Next.js, TypeScript

Testing:
pytest, httpx, testcontainers/dockerized Postgres

Dev Environment:
Docker Compose

Observability:
Structured logs, Sentry, audit logs
```

Core architectural decision:

```text
Build a modular monolith first.
Keep matching, wallet, ledger, and settlement logic isolated and heavily tested.
```

