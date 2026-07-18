# User-to-User Binary Prediction Market Model

This document defines the core model for a Kalshi/Polymarket-style binary prediction market. It focuses on the user-to-user exchange mechanism where traders buy YES/NO contracts from each other through an automated order book.

## 1. Main Synopsis

A binary prediction market lets users trade on the outcome of a future event.

Example:

```text
Will India win the 2026 World Cup?
```

The market has two possible outcomes:

```text
YES
NO
```

The platform defines a fixed payout per winning contract.

Example:

```text
Payout = ₹100
```

If YES wins:

```text
YES contracts pay ₹100 each
NO contracts pay ₹0
```

If NO wins:

```text
NO contracts pay ₹100 each
YES contracts pay ₹0
```

The platform does not act like a bookmaker. It does not manually take the opposite side of every user bet. Instead, the platform works like an exchange:

```text
Users place orders.
The matching engine matches compatible opposite orders.
Each completed trade is fully collateralized.
The winner is paid from the money locked during the trade.
```

This is called a:

```text
Binary prediction market
Event-contract exchange
User-to-user order book market
Fully collateralized YES/NO contract market
```

## 2. Core Entities

### 2.1 Market

A market is the event/question being traded.

Example:

```text
Will India win the 2026 World Cup?
```

A market should define:

```text
- title
- description
- category
- YES condition
- NO condition
- close time
- resolution source
- resolution rules
- status
```

Market statuses:

```text
DRAFT
UNDER_REVIEW
APPROVED
OPEN
PAUSED
CLOSED
PENDING_RESOLUTION
RESOLVED
VOIDED
ARCHIVED
```

### 2.2 Contract

A contract is the tradable instrument inside the market.

In a binary market, there are two sides:

```text
YES contract
NO contract
```

Each winning contract pays the fixed payout.

Example:

```text
1 YES contract pays ₹100 if YES wins.
1 NO contract pays ₹100 if NO wins.
```

### 2.3 Order

An order is a user instruction to buy a side at a price and quantity.

Example:

```text
User A wants to buy 10 YES contracts at ₹40 each.
```

Order fields:

```text
order_id
user_id
market_id
side: YES or NO
price
quantity
filled_quantity
remaining_quantity
order_type
status
created_at
updated_at
```

Order statuses:

```text
OPEN
PARTIALLY_FILLED
FILLED
CANCELLED
EXPIRED
REJECTED
```

### 2.4 Order Book

The order book stores open buy orders for YES and NO.

Example:

```text
YES orders:
A wants 10 YES at ₹40

NO orders:
B wants 10 NO at ₹60
```

The order book is not the same as the market.

Structure:

```text
Market
  -> Contract
      -> Order Book
          -> Open Orders
              -> Trades
```

### 2.5 Trade / Fill

A trade happens when compatible orders match.

Example:

```text
A buys 10 YES at ₹40
B buys 10 NO at ₹60
```

Because:

```text
₹40 + ₹60 = ₹100
```

The trade creates positions:

```text
A receives 10 YES contracts
B receives 10 NO contracts
```

### 2.6 Position

A position represents how many contracts a user owns in a market.

Example:

```text
A owns 10 YES contracts in Market X.
B owns 10 NO contracts in Market X.
```

Position fields:

```text
position_id
user_id
market_id
side
quantity
average_entry_price
realized_pnl
unrealized_pnl
```

### 2.7 Wallet

The wallet tracks user funds.

Wallet balances:

```text
available_balance
locked_balance
settled_balance
```

When a user places an order, some funds may be locked. When a trade completes, the funds become part of the fully collateralized payout pool.

### 2.8 Settlement

Settlement happens after the market outcome is known.

Example:

```text
Outcome = YES
```

Then:

```text
YES holders receive payout.
NO holders receive zero.
```

## 3. Core Variables

These are the important variables needed to reason about the model and later code it.

### 3.1 Payout

The fixed amount paid per winning contract.

Notation:

```text
P = payout
```

Example:

```text
P = ₹100
```

### 3.2 YES Price

The price a trader pays for one YES contract.

Notation:

```text
Y = YES price
```

Example:

```text
Y = ₹40
```

### 3.3 NO Price

The price a trader pays for one NO contract.

Notation:

```text
N = NO price
```

Example:

```text
N = ₹60
```

### 3.4 Quantity

Number of contracts being traded.

Notation:

```text
Q = quantity
```

Example:

```text
Q = 10 contracts
```

### 3.5 Total Cost

The amount a trader pays to enter a position.

For YES:

```text
YES cost = Y × Q
```

For NO:

```text
NO cost = N × Q
```

### 3.6 Total Payout Liability

The amount needed to pay the winner.

```text
Total payout liability = P × Q
```

Example:

```text
P = ₹100
Q = 10

Total payout liability = ₹100 × 10 = ₹1000
```

## 4. Fundamental Invariant

For every fully matched binary contract:

```text
YES price + NO price = payout
```

Using variables:

```text
Y + N = P
```

Example:

```text
Y = ₹40
N = ₹60
P = ₹100

₹40 + ₹60 = ₹100
```

This is the most important rule in the system.

It guarantees that the trade is fully funded.

For quantity Q:

```text
(Y × Q) + (N × Q) = P × Q
```

Example:

```text
Y = ₹40
N = ₹60
P = ₹100
Q = 10

(₹40 × 10) + (₹60 × 10) = ₹100 × 10
₹400 + ₹600 = ₹1000
```

## 5. Why This Rule Exists

The platform must always be able to pay the winner.

Example:

```text
Payout = ₹100
A buys 10 YES at ₹40
B buys 10 NO at ₹60
```

Money locked:

```text
A pays: 10 × ₹40 = ₹400
B pays: 10 × ₹60 = ₹600
Total locked = ₹1000
```

If YES wins:

```text
A receives 10 × ₹100 = ₹1000
B receives ₹0
```

If NO wins:

```text
B receives 10 × ₹100 = ₹1000
A receives ₹0
```

In both cases, the system has exactly enough money to pay the winner.

## 6. Invalid Price Stacking

This is invalid:

```text
A buys 10 YES at ₹40
B buys 10 NO at ₹30
C buys 10 NO at ₹30

₹40 + ₹30 + ₹30 = ₹100
```

This looks fully funded, but it is not valid because each contract must have:

```text
1 YES holder
1 NO holder
```

Not:

```text
1 YES holder
2 NO holders
```

Problem:

```text
A has 10 YES contracts.
B has 10 NO contracts.
C has 10 NO contracts.
```

If YES wins:

```text
A expects 10 × ₹100 = ₹1000
```

This works.

If NO wins:

```text
B expects 10 × ₹100 = ₹1000
C expects 10 × ₹100 = ₹1000

Total needed = ₹2000
```

But only ₹1000 was locked.

Therefore this model is invalid.

Correct rule:

```text
Each contract pair must be 1 YES + 1 NO.
Multiple users can split quantity, but they cannot stack prices.
```

## 7. Valid One-to-Many Matching

One trader can match against many traders by splitting quantity.

Example:

```text
Payout = ₹100
A buys 10 YES at ₹40
```

For A to match, NO must be:

```text
N = P - Y
N = ₹100 - ₹40
N = ₹60
```

Now:

```text
B buys 4 NO at ₹60
C buys 6 NO at ₹60
```

This is valid.

Final positions:

```text
A gets 10 YES
B gets 4 NO
C gets 6 NO
```

Money locked:

```text
A pays: 10 × ₹40 = ₹400
B pays: 4 × ₹60 = ₹240
C pays: 6 × ₹60 = ₹360

Total locked = ₹1000
```

If YES wins:

```text
A receives 10 × ₹100 = ₹1000
```

If NO wins:

```text
B receives 4 × ₹100 = ₹400
C receives 6 × ₹100 = ₹600

Total NO payout = ₹1000
```

This is fully funded in both outcomes.

## 8. Valid Many-to-Many Matching

Multiple YES traders can match with multiple NO traders.

Example:

```text
Payout = ₹100

YES orders:
A buys 4 YES at ₹40
B buys 6 YES at ₹40

NO orders:
C buys 3 NO at ₹60
D buys 7 NO at ₹60
```

Total YES quantity:

```text
4 + 6 = 10
```

Total NO quantity:

```text
3 + 7 = 10
```

Because:

```text
₹40 + ₹60 = ₹100
```

All orders can be matched.

Possible matching:

```text
A's 4 YES matches with C's 3 NO + 1 from D
B's 6 YES matches with D's remaining 6 NO
```

Final:

```text
A owns 4 YES
B owns 6 YES
C owns 3 NO
D owns 7 NO
```

## 9. Incomplete / Unmatched Orders

If prices do not satisfy the invariant, no trade happens.

Example:

```text
Payout = ₹100

A buys 10 YES at ₹40
B buys 10 NO at ₹30
```

Check:

```text
₹40 + ₹30 = ₹70
```

This is not enough.

So:

```text
A's order waits in the order book.
B's order waits in the order book.
No trade occurs.
```

A needs a NO order at:

```text
₹100 - ₹40 = ₹60
```

B needs a YES order at:

```text
₹100 - ₹30 = ₹70
```

## 10. Counterparty Selection

The user does not manually choose the counterparty.

The user chooses:

```text
- market
- side: YES or NO
- price
- quantity
- order type
```

The matching engine chooses the counterparty automatically using order book rules.

Typical rule:

```text
1. Best compatible price first
2. Earliest order first
```

This is called:

```text
price-time priority
```

## 11. Order Matching Logic

For a new YES order:

```text
required NO price = payout - YES price
```

For a new NO order:

```text
required YES price = payout - NO price
```

Example:

```text
Payout = ₹100
A buys YES at ₹40
```

Required NO:

```text
₹100 - ₹40 = ₹60
```

So A can match only with NO orders at ₹60.

Example:

```text
B buys NO at ₹30
C buys NO at ₹45
D buys NO at ₹60
```

Only D matches A.

## 12. Prices And Implied Probability

The price can be interpreted as an approximate market probability.

Example:

```text
Payout = ₹100
YES price = ₹40
NO price = ₹60
```

This roughly means:

```text
YES probability ≈ 40%
NO probability ≈ 60%
```

Formula:

```text
YES implied probability = YES price / payout
NO implied probability = NO price / payout
```

Example:

```text
YES probability = ₹40 / ₹100 = 40%
NO probability = ₹60 / ₹100 = 60%
```

This is not always a perfect probability because of:

```text
- fees
- bid/ask spread
- low liquidity
- trader behavior
- temporary market imbalance
```

## 13. Odds Display

The platform can show a simple odds-style UI while still using the exchange model internally.

Decimal odds:

```text
odds = payout / price
```

Example:

```text
Payout = ₹100
YES price = ₹40

YES odds = ₹100 / ₹40 = 2.5x
```

If user buys ₹40 worth of one YES contract and wins:

```text
Receives ₹100 total
Profit = ₹60
```

For NO:

```text
NO price = ₹60
NO odds = ₹100 / ₹60 = 1.67x
```

## 14. Sportsbook vs Exchange

### Sportsbook Model

In a sportsbook:

```text
User bets against the platform.
Platform sets odds.
Platform takes risk.
```

Example:

```text
User bets ₹100 at 1.5x.
If user wins, platform pays ₹150.
```

If too many users bet on the winning side, the platform may lose money.

### Exchange Model

In this prediction market model:

```text
User trades against another user.
Platform only matches compatible orders.
Platform does not take directional risk.
```

The platform earns through:

```text
- trading fees
- settlement fees
- spreads if acting as market maker, if allowed
```

The foundation for Pred-Market V1 should be the exchange model, not the sportsbook model.

## 15. Liquidity

A liquid market is one where traders can enter or exit quickly at fair prices without moving the price too much.

Good liquidity requires:

```text
- tight spread
- enough depth
- frequent trades
- low slippage
- easy exit
```

### 15.1 Spread

Spread is the gap between best available buy and sell prices.

Example:

```text
Best YES buyer: ₹40
Best YES seller: ₹42
Spread = ₹2
```

Tight spread means better liquidity.

### 15.2 Depth

Depth means how much quantity is available near the current price.

Good depth:

```text
YES buyers:
₹40 × 100 contracts
₹39 × 200 contracts

YES sellers:
₹41 × 100 contracts
₹42 × 200 contracts
```

Poor depth:

```text
YES buyers:
₹40 × 1 contract

YES sellers:
₹41 × 1 contract
```

### 15.3 Slippage

Slippage is the difference between expected price and actual average execution price.

Example:

```text
User expects to buy YES around ₹40.
Because depth is low, final average price becomes ₹48.
Slippage = ₹8.
```

## 16. Order Types For V1

Recommended V1 order types:

```text
LIMIT
MARKET
CANCEL
```

### 16.1 Limit Order

User specifies price and quantity.

Example:

```text
Buy 10 YES at ₹40.
```

The order executes only if compatible opposite orders exist.

### 16.2 Market Order

User wants immediate execution at the best available price.

For V1, market orders should be handled carefully because low liquidity can cause bad slippage.

Recommended safety:

```text
market order with max slippage limit
```

### 16.3 Cancel Order

User cancels an open unmatched or partially filled order.

Unfilled locked funds are released.

## 17. Core Matching Algorithm For V1

Basic flow:

```text
1. Receive order.
2. Validate user, market status, price, quantity, and balance.
3. Lock required funds.
4. Find compatible opposite orders.
5. Match by price-time priority.
6. Create trade/fill records.
7. Update positions.
8. Move money from locked balances into escrow/ledger.
9. Publish order book and fill events.
10. Keep any unfilled remainder open or cancel based on order type.
```

Pseudo-logic:

```text
if incoming.side == YES:
    required_opposite_price = payout - incoming.price
    match against NO orders at required_opposite_price

if incoming.side == NO:
    required_opposite_price = payout - incoming.price
    match against YES orders at required_opposite_price
```

For V1, use strict equality first:

```text
YES price + NO price == payout
```

Later versions can support more advanced order book mechanics.

## 18. Settlement Algorithm

When market closes:

```text
1. Stop accepting new orders.
2. Cancel remaining open orders.
3. Release funds locked for unfilled orders.
4. Fetch/record oracle evidence.
5. Resolve market as YES, NO, or VOID.
6. If YES:
      pay YES holders payout × quantity.
   If NO:
      pay NO holders payout × quantity.
   If VOID:
      refund users based on platform policy.
7. Mark market as resolved.
8. Write audit records.
9. Notify users.
```

## 19. Required Database Tables

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

### 19.1 users

```text
id
name
email
status
kyc_status
created_at
updated_at
```

### 19.2 wallets

```text
id
user_id
available_balance
locked_balance
created_at
updated_at
```

### 19.3 markets

```text
id
title
description
category
status
close_time
resolution_time
created_by
approved_by
created_at
updated_at
```

### 19.4 contracts

```text
id
market_id
payout
tick_size
min_quantity
max_quantity
yes_condition
no_condition
resolution_source
created_at
updated_at
```

### 19.5 orders

```text
id
user_id
market_id
side
price
quantity
filled_quantity
remaining_quantity
status
order_type
created_at
updated_at
```

### 19.6 trades

```text
id
market_id
yes_order_id
no_order_id
yes_user_id
no_user_id
yes_price
no_price
quantity
payout
created_at
```

### 19.7 positions

```text
id
user_id
market_id
side
quantity
average_entry_price
realized_pnl
created_at
updated_at
```

### 19.8 ledger_entries

Use double-entry accounting style.

```text
id
user_id
market_id
trade_id
entry_type
amount
balance_type
created_at
```

Entry types:

```text
DEPOSIT
WITHDRAWAL
ORDER_LOCK
ORDER_RELEASE
TRADE_DEBIT
TRADE_ESCROW
FEE_DEBIT
SETTLEMENT_CREDIT
VOID_REFUND
```

## 20. Critical System Invariants

These should be protected by code and tests.

```text
1. No order can be placed on a closed/resolved market.
2. No trade can happen unless YES price + NO price = payout.
3. No fill can happen without sufficient locked user funds.
4. Filled quantity cannot exceed order quantity.
5. A user wallet cannot go negative.
6. Every trade must create balanced ledger entries.
7. Total winning payout liability must equal escrowed collateral.
8. Settlement must be idempotent.
9. Cancelled order remainder must release locked funds.
10. Open orders must not participate in settlement.
```

## 21. Coding Foundation Needed

Before coding the full product, implement the core engine in this order:

```text
1. Market model
2. Contract model with payout
3. Wallet model
4. Limit order placement
5. Fund locking
6. Order book storage
7. Matching engine
8. Trade record creation
9. Position updates
10. Ledger entries
11. Order cancellation
12. Market close
13. Settlement
14. User notifications
15. Admin resolution tools
```

The first important milestone:

```text
Given:
Payout = ₹100
A buys 10 YES at ₹40
B buys 10 NO at ₹60

System should:
- validate both orders
- lock ₹400 from A
- lock ₹600 from B
- match 10 contracts
- create one trade
- create A's YES position
- create B's NO position
- store ₹1000 collateral
- settle correctly when YES or NO wins
```

## 22. Minimal V1 Matching Example

Input:

```text
Market payout = ₹100

Order 1:
User A buys 10 YES at ₹40

Order 2:
User B buys 10 NO at ₹60
```

Validation:

```text
₹40 + ₹60 = ₹100
```

Funds:

```text
A locks ₹400
B locks ₹600
```

Trade:

```text
quantity = 10
YES user = A
NO user = B
YES price = ₹40
NO price = ₹60
collateral = ₹1000
```

Settlement if YES wins:

```text
A receives ₹1000
B receives ₹0
A profit = ₹600
B loss = ₹600
```

Settlement if NO wins:

```text
B receives ₹1000
A receives ₹0
B profit = ₹400
A loss = ₹400
```

## 23. Final Mental Model

The whole system is built around this idea:

```text
The platform creates a market and defines the contract.
Users express opinions by placing YES/NO orders.
The matching engine pairs compatible orders.
Each matched contract is fully collateralized.
The final outcome determines which side receives the payout.
```

The most important formula:

```text
YES price + NO price = payout
```

The most important architecture choice:

```text
Pred-Market V1 is an exchange, not a sportsbook.
```

