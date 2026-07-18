# Wallet And Double-Entry Ledger Spec

This document defines the wallet and double-entry ledger model for Pred-Market V1. It covers deposits, locks, releases, trade collateral, settlement credits, void refunds, reconciliation, idempotency, and no-negative-balance rules.

This is planning documentation only. It does not create backend code or database migrations.

## 1. Goal

The wallet and ledger system must make every money movement:

```text
balanced
auditable
idempotent
reconcilable
safe under retry
safe under concurrency
```

Core rule:

```text
Wallet balances are fast operational balances.
Ledger entries are the audit trail.
```

No financial workflow is complete unless both wallet state and ledger state are correct.

## 2. Money Representation

Use integer minor units only.

Example:

```text
INR 100.00 = 10000
INR 40.00 = 4000
```

Never use floating point for:

```text
wallet balances
order prices
collateral
payouts
refunds
fees
ledger entries
```

## 3. Wallet Balances

Each user wallet stores:

```text
available_balance_minor
locked_balance_minor
currency
```

Definitions:

```text
available_balance_minor:
  cash the user can use for new orders or withdrawals

locked_balance_minor:
  cash reserved for open buy orders or pending financial operations
```

Wallet invariants:

```text
available_balance_minor >= 0
locked_balance_minor >= 0
available + locked must reconcile to user cash ledger accounts
```

All wallet debit/credit operations must lock the wallet row.

Recommended lock:

```text
SELECT wallet row FOR UPDATE
```

## 4. Ledger Model

Use double-entry accounting:

```text
Every ledger transaction has at least two ledger entries.
Total debits must equal total credits.
```

Ledger transaction:

```text
business event container
```

Ledger entry:

```text
debit or credit to one ledger account
```

Do not create unbalanced ledger transactions.

## 5. Ledger Accounts

Required account types:

```text
USER_AVAILABLE_CASH
USER_LOCKED_CASH
MARKET_COLLATERAL
PLATFORM_CLEARING
EXTERNAL_DEPOSIT_CLEARING
EXTERNAL_WITHDRAWAL_CLEARING
PLATFORM_ADJUSTMENT
```

Per-user accounts:

```text
USER_AVAILABLE_CASH for each user and currency
USER_LOCKED_CASH for each user and currency
```

Per-market accounts:

```text
MARKET_COLLATERAL for each market and currency
```

Platform accounts:

```text
EXTERNAL_DEPOSIT_CLEARING
EXTERNAL_WITHDRAWAL_CLEARING
PLATFORM_ADJUSTMENT
```

## 6. Balance Direction

Use one consistent accounting convention.

Recommended convention:

```text
User asset accounts increase with CREDIT.
User asset accounts decrease with DEBIT.
Platform liability/collateral accounts increase with CREDIT.
Platform liability/collateral accounts decrease with DEBIT.
```

The exact accounting convention can be implemented differently, but it must be consistent and documented in code.

The test requirement is simpler:

```text
For each ledger transaction:
sum(debits) == sum(credits)
```

## 7. Idempotency

Every external or retryable money event needs an idempotency key.

Required idempotency scopes:

```text
deposit
withdrawal
order_lock
order_release
trade_collateral
settlement_credit
void_refund
manual_adjustment
```

Idempotency behavior:

```text
same key + same request hash returns original result
same key + different request hash is rejected
completed event is never applied twice
failed event can be retried only if no irreversible entries were written
```

## 8. Deposit Flow

V1 development can use an admin/test deposit helper. Production needs payment provider integration later.

Deposit flow:

```text
1. Receive deposit event with idempotency key.
2. Validate user and currency.
3. Begin transaction.
4. Lock wallet row.
5. Create ledger transaction DEPOSIT.
6. Credit USER_AVAILABLE_CASH.
7. Debit EXTERNAL_DEPOSIT_CLEARING.
8. Increase wallet.available_balance_minor.
9. Commit.
10. Notify user.
```

Wallet effect:

```text
available += deposit_amount
locked unchanged
```

Ledger example:

```text
DEBIT  EXTERNAL_DEPOSIT_CLEARING 10000
CREDIT USER_AVAILABLE_CASH       10000
```

Required tests:

```text
deposit increases available balance
duplicate deposit idempotency key does not double credit
negative deposit rejected
unknown user rejected
ledger balances
```

## 9. Buy Order Cash Lock

When user places a buy order, cash must be locked before the order can rest or fill.

Required cash:

```text
required_cash_minor = price_minor * quantity
```

Flow:

```text
1. Validate order.
2. Begin transaction.
3. Lock wallet row.
4. Check available_balance_minor >= required_cash_minor.
5. Move available cash to locked cash.
6. Create ledger transaction ORDER_LOCK.
7. Create order with locked_cash_minor.
8. Continue to matching.
```

Wallet effect:

```text
available -= required_cash
locked += required_cash
```

Ledger example:

```text
DEBIT  USER_AVAILABLE_CASH 4000
CREDIT USER_LOCKED_CASH    4000
```

Required tests:

```text
insufficient available balance rejects order
available balance cannot go negative
locked balance increases exactly required cash
order is not created if wallet lock fails
ledger balances
```

## 10. Sell Order Share Lock

For sell orders, shares must be locked before order rests or fills.

V1 rule:

```text
Users can sell only shares they already own.
No naked shorting.
```

Flow:

```text
1. Validate sell order.
2. Begin transaction.
3. Lock position row.
4. Check position.quantity - position.locked_quantity >= sell_quantity.
5. Increase position.locked_quantity.
6. Create sell order with locked_shares.
7. Continue to matching.
```

No cash ledger entry is required just to lock shares, but create a position event.

Required tests:

```text
cannot sell more shares than owned
locked shares cannot exceed quantity
cancel releases locked shares
partial fill reduces locked shares correctly
```

## 11. Order Release Flow

When an unfilled buy order is cancelled, remaining locked cash is released.

Release amount:

```text
release_minor = remaining_quantity * price_minor
```

Flow:

```text
1. Begin transaction.
2. Lock order row.
3. Lock wallet row.
4. Validate order is cancellable.
5. Calculate unfilled locked amount.
6. Move locked cash back to available.
7. Create ledger transaction ORDER_RELEASE.
8. Update order status.
9. Commit.
```

Wallet effect:

```text
locked -= release_minor
available += release_minor
```

Ledger example:

```text
DEBIT  USER_LOCKED_CASH    4000
CREDIT USER_AVAILABLE_CASH 4000
```

Required tests:

```text
cancel releases only unfilled amount
cancel after full fill releases zero
double cancel does not double release
locked balance cannot go negative
ledger balances
```

## 12. Binary Trade Collateral Flow

Binary V1 strict match:

```text
YES price + NO price = payout
```

Example:

```text
payout = 10000
YES buyer locked 4000
NO buyer locked 6000
quantity = 1
total collateral = 10000
```

Flow:

```text
1. MatchingService finds compatible orders.
2. Lock both order rows.
3. Lock both wallet rows.
4. Lock market collateral pool row.
5. Decrease each user's locked cash by fill cost.
6. Increase market collateral by total fill collateral.
7. Create trade record.
8. Increase YES and NO positions.
9. Create ledger transaction TRADE_COLLATERAL.
10. Update filled quantities and order statuses.
```

Wallet effect:

```text
YES user locked -= yes_price * quantity
NO user locked -= no_price * quantity
available unchanged
```

Collateral effect:

```text
market_collateral += payout * quantity
```

Ledger example:

```text
DEBIT  YES_USER_LOCKED_CASH 4000
DEBIT  NO_USER_LOCKED_CASH  6000
CREDIT MARKET_COLLATERAL    10000
```

Required tests:

```text
YES + NO must equal payout
collateral increases by payout * quantity
locked cash decreases by exact filled cost
positions are created or increased
partial fills handle remaining locked cash
ledger balances
```

## 13. Multiple-Choice Trade Flow

Multiple-choice V1 uses owned outcome shares.

Buy/sell fill:

```text
buyer pays price * quantity
seller transfers owned shares
seller receives cash
buyer receives shares
```

Flow:

```text
1. Buyer cash is locked when buy order is placed.
2. Seller shares are locked when sell order is placed.
3. MatchingService finds compatible buy/sell orders for same outcome.
4. Lock buyer wallet, seller wallet, buyer position, seller position, and order rows.
5. Move buyer locked cash to seller available cash.
6. Move shares from seller position to buyer position.
7. Write ledger transaction POSITION_TRANSFER or TRADE_SETTLEMENT.
8. Write position events.
9. Update order fill quantities.
```

Ledger example:

```text
DEBIT  BUYER_LOCKED_CASH    4200
CREDIT SELLER_AVAILABLE_CASH 4200
```

Required tests:

```text
seller cannot sell unowned shares
buyer locked cash pays seller
seller available cash increases
buyer position increases
seller position decreases
ledger balances
```

## 14. Settlement Credit Flow

Binary settlement:

```text
winning holders receive payout * quantity
losing holders receive zero
```

Flow:

```text
1. SettlementService locks market row.
2. Lock market collateral pool row.
3. Load winning positions.
4. Calculate payout per user.
5. Validate total payout <= collateral.
6. For each winner, lock wallet row.
7. Credit user available balance.
8. Decrease/release market collateral.
9. Write settlement ledger transactions.
10. Mark settlement items complete.
11. Mark positions SETTLED.
12. Mark market RESOLVED.
```

Wallet effect:

```text
winner available += payout_amount
```

Collateral effect:

```text
market_collateral released += payout_amount
```

Ledger example:

```text
DEBIT  MARKET_COLLATERAL    10000
CREDIT USER_AVAILABLE_CASH  10000
```

Required tests:

```text
winner receives payout
loser receives zero
total payout does not exceed collateral
settlement is idempotent
settlement item uniqueness prevents double credit
ledger balances
```

## 15. Void Refund Flow

Recommended early V1 void policy:

```text
Refund each holder's original matched cost.
No fees initially.
```

For binary:

```text
YES buyer refund = yes_price * quantity
NO buyer refund = no_price * quantity
```

Flow:

```text
1. SettlementService locks market row.
2. Validate approved VOID resolution.
3. Cancel open orders and release remaining locks.
4. Load all matched position cost basis.
5. Calculate refund per user.
6. Validate total refund <= collateral.
7. Lock market collateral pool row.
8. Lock user wallet rows.
9. Credit user available balances.
10. Write VOID_REFUND ledger transactions.
11. Mark positions VOIDED.
12. Mark market VOIDED.
```

Ledger example:

```text
DEBIT  MARKET_COLLATERAL    4000
CREDIT USER_AVAILABLE_CASH  4000
```

Required tests:

```text
void refunds original matched cost
open order locks are released before refund
void refund does not pay more than collateral
void retry does not double refund
ledger balances
```

## 16. Withdrawal Flow

Production withdrawal should wait for payment provider design. For planning:

Flow:

```text
1. User requests withdrawal.
2. Validate available balance.
3. Begin transaction.
4. Lock wallet row.
5. Move available cash to withdrawal clearing or debit available.
6. Write WITHDRAWAL ledger transaction.
7. Create withdrawal record.
8. Payment provider executes transfer.
9. Mark withdrawal complete or failed.
```

No withdrawal should use locked funds.

Required tests:

```text
withdrawal cannot exceed available balance
locked balance is not withdrawable
failed withdrawal restores available balance if money did not leave
duplicate provider callback is idempotent
```

## 17. Manual Adjustment Flow

Manual adjustments are high-risk and admin-only.

Rules:

```text
requires admin role
requires reason
requires maker-checker approval above threshold
must write audit log
must write balanced ledger transaction
must update wallet only through WalletService
```

Ledger example for user credit:

```text
DEBIT  PLATFORM_ADJUSTMENT  1000
CREDIT USER_AVAILABLE_CASH  1000
```

Manual adjustment must never be used to hide ledger mismatch.

## 18. Reconciliation

Run reconciliation jobs regularly.

Wallet-ledger reconciliation:

```text
wallet.available_balance_minor == ledger balance of USER_AVAILABLE_CASH
wallet.locked_balance_minor == ledger balance of USER_LOCKED_CASH
```

Collateral reconciliation:

```text
market_collateral_pools.collateral_minor - released_minor
matches ledger balance of MARKET_COLLATERAL
```

Order lock reconciliation:

```text
sum(open order locked_cash_minor) == sum(user wallet locked amounts attributable to orders)
```

Settlement reconciliation:

```text
sum(settlement_items.amount_minor) == settlement total payout/refund
settlement total payout/refund <= collateral released
```

When reconciliation fails:

```text
create alert
pause affected market if needed
block settlement if collateral mismatch exists
require admin review
do not auto-adjust silently
```

## 19. Concurrency Rules

Use deterministic lock order to reduce deadlocks.

Recommended lock order:

```text
1. market row
2. collateral pool row
3. order rows by UUID ascending
4. wallet rows by UUID ascending
5. position rows by UUID ascending
```

For order placement, at minimum:

```text
lock wallet before debiting
lock order before filling or cancelling
lock position before changing share quantity
```

If deadlock occurs:

```text
rollback transaction
retry only if operation is idempotent
log retry count
alert if repeated
```

## 20. Event Types

Required ledger transaction types:

```text
DEPOSIT
WITHDRAWAL
ORDER_LOCK
ORDER_RELEASE
TRADE_COLLATERAL
POSITION_TRANSFER
SETTLEMENT_CREDIT
VOID_REFUND
ADJUSTMENT
```

Required wallet event statuses:

```text
PENDING
COMPLETE
FAILED
REVERSED
```

## 21. API Behavior

Wallet endpoints should expose:

```text
GET /wallet
GET /wallet/ledger
GET /wallet/reconciliation-status for admin only
POST /wallet/test-deposit for local/dev only
```

Response rules:

```text
show available balance
show locked balance
show currency
show recent ledger events
do not expose internal ledger account IDs to normal users
```

Admin endpoints may expose ledger transaction IDs and reconciliation detail.

## 22. Test Matrix

Minimum test cases:

```text
deposit creates balanced ledger and credits available
duplicate deposit does not double credit
buy order lock moves available to locked
insufficient funds rejects buy order
cancel buy order releases remaining locked cash
partial fill leaves correct remaining locked cash
binary fill moves both sides' locked cash to collateral
multiple-choice fill moves buyer cash to seller and shares to buyer
settlement credits winners only
void refunds original matched cost
settlement retry does not double credit
void retry does not double refund
wallet-ledger reconciliation passes after each workflow
forced imbalance is detected
concurrent orders cannot create negative balance
concurrent cancels cannot double release
```

## 23. Non-Negotiable Rules

Implementation must enforce:

```text
no wallet balance goes negative
no position goes negative
no unbalanced ledger transaction is committed
no fill occurs without locked cash or locked shares
no settlement pays more than collateral
no retry can double-credit a user
no manual adjustment happens without audit trail
no reconciliation failure is silently ignored
```

