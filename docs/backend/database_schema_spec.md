# Database Schema Spec

This document defines the recommended Pred-Market V1 PostgreSQL schema. It includes tables, columns, relationships, constraints, indexes, audit tables, and migration order.

This is planning documentation only. It does not create database migrations.

## 1. Schema Principles

Database goals:

```text
financial correctness
auditability
idempotency
clear relational constraints
safe settlement retries
analytics-friendly source data
```

Core decisions:

```text
PostgreSQL is the source of truth.
Use integer minor units for money.
Use UUID primary keys.
Use timestamptz for timestamps.
Use JSONB only for flexible metadata, not core money fields.
Do not physically delete financial records.
Use append-only records for ledger, trades, settlements, and audit logs.
```

Money convention:

```text
amount_minor BIGINT NOT NULL
currency CHAR(3) NOT NULL
```

Example:

```text
INR 100.00 = 10000 minor units
```

## 2. PostgreSQL Extensions

Recommended extensions:

```text
pgcrypto for gen_random_uuid()
btree_gin if JSONB search indexes are needed later
```

## 3. Core Enums

Recommended enum values can be implemented as PostgreSQL enums or constrained text fields.

```text
user_status:
ACTIVE, SUSPENDED, CLOSED, PENDING_REVIEW

user_role:
USER, ADMIN, CHECKER, MARKET_CREATOR

market_status:
DRAFT, REVIEW, APPROVED, OPEN, PAUSED, CLOSED,
PENDING_RESOLUTION, DISPUTED, RESOLVED, VOIDED, ARCHIVED

market_type:
BINARY, MULTIPLE_CHOICE, RANGE, THRESHOLD, CONDITIONAL, COMBO, SCALAR

outcome_status:
ACTIVE, INACTIVE, WINNER, LOSER, VOIDED

order_side:
BUY, SELL

order_status:
OPEN, PARTIALLY_FILLED, FILLED, CANCELLED, PARTIALLY_CANCELLED, REJECTED, EXPIRED

asset_type:
CASH, CONTRACT

trade_status:
EXECUTED, CANCELLED_BY_ADMIN

position_status:
OPEN, SETTLED, VOIDED

settlement_status:
PENDING, APPROVED, PROCESSING, COMPLETE, FAILED, VOIDED

ledger_entry_side:
DEBIT, CREDIT

ledger_transaction_type:
DEPOSIT, WITHDRAWAL, ORDER_LOCK, ORDER_RELEASE,
TRADE_COLLATERAL, POSITION_TRANSFER, SETTLEMENT_CREDIT,
VOID_REFUND, ADJUSTMENT
```

## 4. Users And Auth Tables

### users

Purpose:

```text
Stores platform user identity and status.
```

Columns:

```text
id UUID PRIMARY KEY
email CITEXT UNIQUE NOT NULL
password_hash TEXT NULL
display_name TEXT NULL
status user_status NOT NULL DEFAULT 'ACTIVE'
kyc_status TEXT NOT NULL DEFAULT 'NOT_STARTED'
jurisdiction_code TEXT NULL
created_at TIMESTAMPTZ NOT NULL DEFAULT now()
updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
```

Indexes:

```text
unique lower email through CITEXT
index status
index jurisdiction_code
```

### user_roles

Columns:

```text
id UUID PRIMARY KEY
user_id UUID NOT NULL REFERENCES users(id)
role user_role NOT NULL
created_at TIMESTAMPTZ NOT NULL DEFAULT now()
```

Constraints:

```text
UNIQUE(user_id, role)
```

### refresh_tokens

Columns:

```text
id UUID PRIMARY KEY
user_id UUID NOT NULL REFERENCES users(id)
token_hash TEXT NOT NULL UNIQUE
expires_at TIMESTAMPTZ NOT NULL
revoked_at TIMESTAMPTZ NULL
created_at TIMESTAMPTZ NOT NULL DEFAULT now()
```

## 5. Wallet And Ledger Tables

### wallets

Purpose:

```text
Stores fast user wallet balances. Ledger remains the audit source.
```

Columns:

```text
id UUID PRIMARY KEY
user_id UUID NOT NULL UNIQUE REFERENCES users(id)
currency CHAR(3) NOT NULL
available_balance_minor BIGINT NOT NULL DEFAULT 0
locked_balance_minor BIGINT NOT NULL DEFAULT 0
created_at TIMESTAMPTZ NOT NULL DEFAULT now()
updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
```

Constraints:

```text
available_balance_minor >= 0
locked_balance_minor >= 0
UNIQUE(user_id, currency)
```

Indexes:

```text
index user_id
```

### ledger_accounts

Purpose:

```text
Defines accounts used by double-entry ledger.
```

Columns:

```text
id UUID PRIMARY KEY
owner_type TEXT NOT NULL
owner_id UUID NULL
account_type TEXT NOT NULL
currency CHAR(3) NOT NULL
name TEXT NOT NULL
created_at TIMESTAMPTZ NOT NULL DEFAULT now()
```

Account examples:

```text
USER_AVAILABLE_CASH
USER_LOCKED_CASH
MARKET_COLLATERAL
PLATFORM_CLEARING
EXTERNAL_DEPOSIT_CLEARING
EXTERNAL_WITHDRAWAL_CLEARING
```

Constraints:

```text
UNIQUE(owner_type, owner_id, account_type, currency)
```

### ledger_transactions

Columns:

```text
id UUID PRIMARY KEY
transaction_type ledger_transaction_type NOT NULL
idempotency_key TEXT NULL UNIQUE
reference_type TEXT NULL
reference_id UUID NULL
description TEXT NULL
created_by_user_id UUID NULL REFERENCES users(id)
created_at TIMESTAMPTZ NOT NULL DEFAULT now()
```

Indexes:

```text
index transaction_type
index reference_type, reference_id
index created_at
```

### ledger_entries

Columns:

```text
id UUID PRIMARY KEY
ledger_transaction_id UUID NOT NULL REFERENCES ledger_transactions(id)
account_id UUID NOT NULL REFERENCES ledger_accounts(id)
side ledger_entry_side NOT NULL
amount_minor BIGINT NOT NULL
currency CHAR(3) NOT NULL
created_at TIMESTAMPTZ NOT NULL DEFAULT now()
```

Constraints:

```text
amount_minor > 0
```

Indexes:

```text
index ledger_transaction_id
index account_id
index created_at
```

Balance rule:

```text
For every ledger_transaction_id:
sum(debits.amount_minor) == sum(credits.amount_minor)
```

This may be enforced by application logic plus database tests because cross-row aggregate checks are awkward in simple constraints.

## 6. Category And Market Tables

### categories

Columns:

```text
id UUID PRIMARY KEY
slug TEXT NOT NULL UNIQUE
name TEXT NOT NULL
risk_level TEXT NOT NULL
status TEXT NOT NULL DEFAULT 'ACTIVE'
created_at TIMESTAMPTZ NOT NULL DEFAULT now()
updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
```

Seed categories:

```text
sports
politics
economics
stocks-mutual-funds
financials
weather-climate
culture
tech-science
mentions
commodities
```

### markets

Columns:

```text
id UUID PRIMARY KEY
category_id UUID NOT NULL REFERENCES categories(id)
market_type market_type NOT NULL
title TEXT NOT NULL
description TEXT NULL
status market_status NOT NULL DEFAULT 'DRAFT'
currency CHAR(3) NOT NULL
payout_amount_minor BIGINT NOT NULL
tick_size_minor BIGINT NOT NULL
min_quantity BIGINT NOT NULL
max_quantity BIGINT NOT NULL
open_time TIMESTAMPTZ NULL
close_time TIMESTAMPTZ NOT NULL
observation_time TIMESTAMPTZ NULL
timezone TEXT NOT NULL DEFAULT 'UTC'
resolution_source TEXT NOT NULL
resolution_rule TEXT NOT NULL
void_policy TEXT NOT NULL
dispute_window_seconds INTEGER NOT NULL DEFAULT 86400
metadata_json JSONB NOT NULL DEFAULT '{}'
created_by_user_id UUID NULL REFERENCES users(id)
approved_by_user_id UUID NULL REFERENCES users(id)
approved_at TIMESTAMPTZ NULL
created_at TIMESTAMPTZ NOT NULL DEFAULT now()
updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
```

Constraints:

```text
payout_amount_minor > 0
tick_size_minor > 0
min_quantity > 0
max_quantity >= min_quantity
close_time > open_time when open_time is not null
```

Indexes:

```text
index category_id
index market_type
index status
index close_time
GIN index metadata_json if needed later
```

### market_rules

Purpose:

```text
Stores immutable rule versions. Orders reference a rule version.
```

Columns:

```text
id UUID PRIMARY KEY
market_id UUID NOT NULL REFERENCES markets(id)
version INTEGER NOT NULL
rule_text TEXT NOT NULL
metadata_json JSONB NOT NULL DEFAULT '{}'
created_by_user_id UUID NULL REFERENCES users(id)
created_at TIMESTAMPTZ NOT NULL DEFAULT now()
```

Constraints:

```text
UNIQUE(market_id, version)
```

### outcomes

Columns:

```text
id UUID PRIMARY KEY
market_id UUID NOT NULL REFERENCES markets(id)
code TEXT NOT NULL
label TEXT NOT NULL
description TEXT NULL
display_order INTEGER NOT NULL
status outcome_status NOT NULL DEFAULT 'ACTIVE'
metadata_json JSONB NOT NULL DEFAULT '{}'
created_at TIMESTAMPTZ NOT NULL DEFAULT now()
updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
```

Constraints:

```text
UNIQUE(market_id, code)
UNIQUE(market_id, display_order)
```

Indexes:

```text
index market_id
index status
```

Binary market rule:

```text
exactly one YES outcome and one NO outcome
```

This should be enforced in application validation and tests.

## 7. Orders And Trades Tables

### orders

Columns:

```text
id UUID PRIMARY KEY
user_id UUID NOT NULL REFERENCES users(id)
market_id UUID NOT NULL REFERENCES markets(id)
outcome_id UUID NOT NULL REFERENCES outcomes(id)
market_rule_id UUID NOT NULL REFERENCES market_rules(id)
side order_side NOT NULL
price_minor BIGINT NOT NULL
quantity BIGINT NOT NULL
filled_quantity BIGINT NOT NULL DEFAULT 0
cancelled_quantity BIGINT NOT NULL DEFAULT 0
remaining_quantity BIGINT NOT NULL
locked_cash_minor BIGINT NOT NULL DEFAULT 0
locked_shares BIGINT NOT NULL DEFAULT 0
status order_status NOT NULL DEFAULT 'OPEN'
idempotency_key TEXT NULL UNIQUE
created_at TIMESTAMPTZ NOT NULL DEFAULT now()
updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
cancelled_at TIMESTAMPTZ NULL
```

Constraints:

```text
price_minor > 0
quantity > 0
filled_quantity >= 0
cancelled_quantity >= 0
remaining_quantity >= 0
filled_quantity + cancelled_quantity + remaining_quantity = quantity
locked_cash_minor >= 0
locked_shares >= 0
```

Indexes:

```text
index user_id, status
index market_id, outcome_id, side, status
index market_id, status, created_at
index price-time priority:
  BUY: market_id, outcome_id, side, status, price_minor DESC, created_at ASC
  SELL: market_id, outcome_id, side, status, price_minor ASC, created_at ASC
```

For binary strict complementary matching, also index:

```text
market_id, outcome_id, side, status, price_minor, created_at
```

### trades

Columns:

```text
id UUID PRIMARY KEY
market_id UUID NOT NULL REFERENCES markets(id)
outcome_id UUID NOT NULL REFERENCES outcomes(id)
buy_order_id UUID NOT NULL REFERENCES orders(id)
sell_order_id UUID NULL REFERENCES orders(id)
buyer_user_id UUID NOT NULL REFERENCES users(id)
seller_user_id UUID NULL REFERENCES users(id)
price_minor BIGINT NOT NULL
quantity BIGINT NOT NULL
payout_amount_minor BIGINT NOT NULL
status trade_status NOT NULL DEFAULT 'EXECUTED'
created_at TIMESTAMPTZ NOT NULL DEFAULT now()
```

Binary complementary V1 can store both sides:

```text
yes_order_id UUID NULL REFERENCES orders(id)
no_order_id UUID NULL REFERENCES orders(id)
yes_user_id UUID NULL REFERENCES users(id)
no_user_id UUID NULL REFERENCES users(id)
yes_price_minor BIGINT NULL
no_price_minor BIGINT NULL
```

Constraints:

```text
price_minor > 0
quantity > 0
payout_amount_minor > 0
for binary fills: yes_price_minor + no_price_minor = payout_amount_minor
```

Indexes:

```text
index market_id, created_at
index buyer_user_id, created_at
index seller_user_id, created_at
index buy_order_id
index sell_order_id
```

Trades should be append-only.

## 8. Positions Tables

### positions

Purpose:

```text
Tracks user share quantities per market outcome.
```

Columns:

```text
id UUID PRIMARY KEY
user_id UUID NOT NULL REFERENCES users(id)
market_id UUID NOT NULL REFERENCES markets(id)
outcome_id UUID NOT NULL REFERENCES outcomes(id)
quantity BIGINT NOT NULL DEFAULT 0
locked_quantity BIGINT NOT NULL DEFAULT 0
average_entry_price_minor BIGINT NOT NULL DEFAULT 0
realized_pnl_minor BIGINT NOT NULL DEFAULT 0
status position_status NOT NULL DEFAULT 'OPEN'
created_at TIMESTAMPTZ NOT NULL DEFAULT now()
updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
```

Constraints:

```text
quantity >= 0
locked_quantity >= 0
locked_quantity <= quantity
UNIQUE(user_id, market_id, outcome_id)
```

Indexes:

```text
index user_id, status
index market_id, outcome_id
```

### position_events

Purpose:

```text
Append-only position movement audit.
```

Columns:

```text
id UUID PRIMARY KEY
position_id UUID NOT NULL REFERENCES positions(id)
event_type TEXT NOT NULL
trade_id UUID NULL REFERENCES trades(id)
settlement_id UUID NULL
quantity_delta BIGINT NOT NULL
price_minor BIGINT NULL
created_at TIMESTAMPTZ NOT NULL DEFAULT now()
```

## 9. Collateral Tables

### market_collateral_pools

Columns:

```text
id UUID PRIMARY KEY
market_id UUID NOT NULL UNIQUE REFERENCES markets(id)
currency CHAR(3) NOT NULL
collateral_minor BIGINT NOT NULL DEFAULT 0
released_minor BIGINT NOT NULL DEFAULT 0
created_at TIMESTAMPTZ NOT NULL DEFAULT now()
updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
```

Constraints:

```text
collateral_minor >= 0
released_minor >= 0
released_minor <= collateral_minor
```

### collateral_events

Columns:

```text
id UUID PRIMARY KEY
market_id UUID NOT NULL REFERENCES markets(id)
trade_id UUID NULL REFERENCES trades(id)
settlement_id UUID NULL
event_type TEXT NOT NULL
amount_minor BIGINT NOT NULL
currency CHAR(3) NOT NULL
created_at TIMESTAMPTZ NOT NULL DEFAULT now()
```

Constraints:

```text
amount_minor > 0
```

## 10. Resolution And Settlement Tables

### oracle_evidence

Columns:

```text
id UUID PRIMARY KEY
market_id UUID NOT NULL REFERENCES markets(id)
source_name TEXT NOT NULL
source_url TEXT NULL
captured_value TEXT NULL
captured_at TIMESTAMPTZ NOT NULL
raw_payload_json JSONB NULL
evidence_hash TEXT NULL
created_by_user_id UUID NULL REFERENCES users(id)
created_at TIMESTAMPTZ NOT NULL DEFAULT now()
```

Indexes:

```text
index market_id, captured_at
```

### resolution_proposals

Columns:

```text
id UUID PRIMARY KEY
market_id UUID NOT NULL REFERENCES markets(id)
proposed_outcome_id UUID NULL REFERENCES outcomes(id)
resolution_value TEXT NULL
resolution_type TEXT NOT NULL
reason TEXT NOT NULL
oracle_evidence_id UUID NULL REFERENCES oracle_evidence(id)
proposed_by_user_id UUID NOT NULL REFERENCES users(id)
approved_by_user_id UUID NULL REFERENCES users(id)
status TEXT NOT NULL DEFAULT 'PENDING'
created_at TIMESTAMPTZ NOT NULL DEFAULT now()
approved_at TIMESTAMPTZ NULL
```

Constraints:

```text
proposed_by_user_id <> approved_by_user_id when approved_by_user_id is not null
```

### settlements

Columns:

```text
id UUID PRIMARY KEY
market_id UUID NOT NULL REFERENCES markets(id)
resolution_proposal_id UUID NOT NULL REFERENCES resolution_proposals(id)
status settlement_status NOT NULL DEFAULT 'PENDING'
idempotency_key TEXT NOT NULL UNIQUE
total_payout_minor BIGINT NOT NULL DEFAULT 0
total_refund_minor BIGINT NOT NULL DEFAULT 0
started_at TIMESTAMPTZ NULL
completed_at TIMESTAMPTZ NULL
error_message TEXT NULL
created_at TIMESTAMPTZ NOT NULL DEFAULT now()
updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
```

Constraints:

```text
total_payout_minor >= 0
total_refund_minor >= 0
UNIQUE(market_id) WHERE status = 'COMPLETE'
```

### settlement_items

Columns:

```text
id UUID PRIMARY KEY
settlement_id UUID NOT NULL REFERENCES settlements(id)
user_id UUID NOT NULL REFERENCES users(id)
position_id UUID NULL REFERENCES positions(id)
outcome_id UUID NULL REFERENCES outcomes(id)
item_type TEXT NOT NULL
quantity BIGINT NOT NULL DEFAULT 0
amount_minor BIGINT NOT NULL
currency CHAR(3) NOT NULL
ledger_transaction_id UUID NULL REFERENCES ledger_transactions(id)
created_at TIMESTAMPTZ NOT NULL DEFAULT now()
```

Constraints:

```text
quantity >= 0
amount_minor >= 0
UNIQUE(settlement_id, user_id, position_id, item_type)
```

## 11. Admin And Audit Tables

### audit_logs

Columns:

```text
id UUID PRIMARY KEY
actor_user_id UUID NULL REFERENCES users(id)
actor_type TEXT NOT NULL
action TEXT NOT NULL
entity_type TEXT NOT NULL
entity_id UUID NULL
request_id TEXT NULL
before_state_json JSONB NULL
after_state_json JSONB NULL
metadata_json JSONB NOT NULL DEFAULT '{}'
created_at TIMESTAMPTZ NOT NULL DEFAULT now()
```

Indexes:

```text
index actor_user_id, created_at
index entity_type, entity_id
index action
index created_at
```

### admin_reviews

Columns:

```text
id UUID PRIMARY KEY
entity_type TEXT NOT NULL
entity_id UUID NOT NULL
review_type TEXT NOT NULL
status TEXT NOT NULL DEFAULT 'PENDING'
assigned_to_user_id UUID NULL REFERENCES users(id)
decision_by_user_id UUID NULL REFERENCES users(id)
decision_reason TEXT NULL
created_at TIMESTAMPTZ NOT NULL DEFAULT now()
decided_at TIMESTAMPTZ NULL
```

## 12. Notifications And Analytics Tables

### notifications

Columns:

```text
id UUID PRIMARY KEY
user_id UUID NOT NULL REFERENCES users(id)
type TEXT NOT NULL
title TEXT NOT NULL
body TEXT NOT NULL
metadata_json JSONB NOT NULL DEFAULT '{}'
read_at TIMESTAMPTZ NULL
created_at TIMESTAMPTZ NOT NULL DEFAULT now()
```

Indexes:

```text
index user_id, read_at, created_at
```

### market_price_points

Purpose:

```text
Stores chartable price/probability snapshots.
```

Columns:

```text
id UUID PRIMARY KEY
market_id UUID NOT NULL REFERENCES markets(id)
outcome_id UUID NOT NULL REFERENCES outcomes(id)
price_minor BIGINT NOT NULL
volume_minor BIGINT NOT NULL DEFAULT 0
open_interest BIGINT NOT NULL DEFAULT 0
captured_at TIMESTAMPTZ NOT NULL
```

Indexes:

```text
index market_id, outcome_id, captured_at
```

### market_daily_rollups

Columns:

```text
id UUID PRIMARY KEY
market_id UUID NOT NULL REFERENCES markets(id)
rollup_date DATE NOT NULL
volume_minor BIGINT NOT NULL DEFAULT 0
trade_count BIGINT NOT NULL DEFAULT 0
unique_traders BIGINT NOT NULL DEFAULT 0
open_interest BIGINT NOT NULL DEFAULT 0
created_at TIMESTAMPTZ NOT NULL DEFAULT now()
updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
```

Constraints:

```text
UNIQUE(market_id, rollup_date)
```

## 13. Idempotency Table

### idempotency_keys

Columns:

```text
id UUID PRIMARY KEY
key TEXT NOT NULL UNIQUE
scope TEXT NOT NULL
request_hash TEXT NOT NULL
response_json JSONB NULL
status TEXT NOT NULL
created_by_user_id UUID NULL REFERENCES users(id)
created_at TIMESTAMPTZ NOT NULL DEFAULT now()
expires_at TIMESTAMPTZ NULL
```

Use for:

```text
order placement
order cancellation
deposit callback
withdrawal request
settlement execution
void refund
manual adjustment
```

## 14. Critical Constraints And Invariants

Database/application must enforce:

```text
wallet available balance >= 0
wallet locked balance >= 0
position quantity >= 0
position locked quantity <= quantity
order filled + cancelled + remaining = quantity
order price > 0
order quantity > 0
market payout > 0
tick size > 0
binary trade YES price + NO price = payout
settlement item uniqueness prevents double payout
one complete settlement per market
ledger transactions balance
```

Some invariants require application checks plus tests:

```text
exactly two outcomes for binary market
complete set outcome validation
range gapless validation
settlement payout <= market collateral
no order fill after market close
no admin self-approval for maker-checker flow
```

## 15. Migration Order

Recommended Alembic migration order:

```text
001_enable_extensions
002_create_enums
003_create_users_and_roles
004_create_wallets
005_create_ledger_accounts_transactions_entries
006_create_categories
007_create_markets_rules_outcomes
008_create_orders
009_create_trades
010_create_positions_and_position_events
011_create_collateral_pools_and_events
012_create_oracle_evidence
013_create_resolution_proposals
014_create_settlements_and_items
015_create_audit_and_admin_reviews
016_create_notifications
017_create_analytics_rollups
018_create_idempotency_keys
019_seed_categories
020_seed_system_ledger_accounts
```

## 16. Initial Seed Data

Seed categories:

```text
sports
politics
economics
stocks-mutual-funds
financials
weather-climate
culture
tech-science
mentions
commodities
```

Seed platform ledger accounts:

```text
PLATFORM_CLEARING
EXTERNAL_DEPOSIT_CLEARING
EXTERNAL_WITHDRAWAL_CLEARING
PLATFORM_ADJUSTMENT
```

Create market collateral ledger account when each market is approved or opened.

Create user wallet ledger accounts when user wallet is created:

```text
USER_AVAILABLE_CASH
USER_LOCKED_CASH
```

## 17. Indexing Notes

High-value query paths:

```text
market discovery by category/status/close_time
order book by market/outcome/side/status/price/created_at
user open orders
user positions
market recent trades
user ledger history
market settlement items
audit logs by entity
```

Do not over-index before real traffic. Start with correctness indexes, then tune from query plans.

## 18. Deletion Policy

Do not hard-delete:

```text
users with financial activity
wallets
ledger transactions
ledger entries
markets
orders
trades
positions
settlements
audit logs
oracle evidence
```

Use status fields and archival states.

