# Multiple-Choice Market End-to-End Workflow

This document explains the complete workflow for a multiple-choice prediction market in Pred-Market terms.

Example market:

```text
Who will win the tournament?

Outcomes:
- India
- Australia
- England
- Other
```

The purpose of this document is to define the product model, core variables, collateral logic, order workflow, matching workflow, position model, settlement flow, and implementation implications.

This is a study and planning document. It does not create code or database migrations.

## 1. Definition

A multiple-choice prediction market is a market with more than two possible outcomes where exactly one outcome resolves as the winner.

Example:

```text
Market:
Who will win the tournament?

Outcome set:
India / Australia / England / Other
```

At settlement:

```text
Only one outcome pays.
All other outcomes pay zero.
```

If India wins:

```text
India pays payout
Australia pays 0
England pays 0
Other pays 0
```

If Australia wins:

```text
India pays 0
Australia pays payout
England pays 0
Other pays 0
```

## 2. Required Outcome Rules

A valid multiple-choice market must have outcomes that are:

```text
1. Mutually exclusive
2. Collectively exhaustive
```

## 3. Mutually Exclusive Outcomes

Mutually exclusive means only one outcome can be true.

Valid:

```text
Who will win the tournament?

India
Australia
England
Other
```

Only one team can win the tournament.

Invalid:

```text
Who will win the tournament?

India
Asian team
Australia
Other
```

This is invalid because India is also an Asian team.

If India wins:

```text
India = true
Asian team = true
```

Two outcomes become true, so the market is broken.

## 4. Collectively Exhaustive Outcomes

Collectively exhaustive means the outcome list covers every possible result.

Bad outcome set:

```text
India
Australia
England
```

Problem:

```text
If South Africa wins, none of the listed outcomes is true.
```

Better outcome set:

```text
India
Australia
England
Other
```

Now the market can always resolve:

```text
If South Africa wins, Other wins.
```

## 5. Core Variables

For a multiple-choice market:

```text
P = payout per winning share
O = set of outcomes
n = number of outcomes
o_i = a specific outcome
p_i = price of outcome i
q = quantity of shares/contracts
C = complete set collateral
```

Example:

```text
P = ₹100
O = {India, Australia, England, Other}
n = 4
```

Prices:

```text
India price = ₹40
Australia price = ₹30
England price = ₹20
Other price = ₹10
```

## 6. Core Pricing Invariant

For a perfectly priced complete outcome set:

```text
sum(all outcome prices) = payout
```

Using variables:

```text
p_1 + p_2 + p_3 + ... + p_n = P
```

Example:

```text
India + Australia + England + Other = ₹100

₹40 + ₹30 + ₹20 + ₹10 = ₹100
```

This is the multiple-choice version of the binary invariant:

```text
YES + NO = payout
```

For multiple-choice:

```text
Outcome 1 + Outcome 2 + ... + Outcome n = payout
```

## 7. Probability Interpretation

Each outcome price can be interpreted as an implied probability.

Formula:

```text
implied probability = outcome price / payout
```

Example:

```text
Payout = ₹100
India price = ₹40

India implied probability = 40 / 100 = 40%
```

For the full market:

```text
India: ₹40 = 40%
Australia: ₹30 = 30%
England: ₹20 = 20%
Other: ₹10 = 10%
```

Total:

```text
40% + 30% + 20% + 10% = 100%
```

## 8. Contract Model

A multiple-choice market can be modeled as one market with many outcome contracts.

```text
Market:
Who will win the tournament?

Outcome contracts:
- India pays ₹100 if India wins
- Australia pays ₹100 if Australia wins
- England pays ₹100 if England wins
- Other pays ₹100 if any unlisted participant wins
```

Important:

```text
These are not independent binary markets.
```

They are linked outcome claims from the same mutually exclusive outcome set.

## 9. Complete Set Model

The cleanest collateral model is the complete set model.

For payout:

```text
P = ₹100
```

A complete set contains one share of every outcome:

```text
1 India share
1 Australia share
1 England share
1 Other share
```

The complete set is backed by:

```text
₹100 collateral
```

Why only ₹100?

Because exactly one outcome wins.

At settlement, only one share in the set pays:

```text
Winning share receives ₹100
Losing shares receive ₹0
```

So the system needs only:

```text
₹100 per complete set
```

not:

```text
₹100 × number_of_outcomes
```

## 10. Complete Set Minting

If a user deposits ₹100 into a market, the platform can mint one complete set:

```text
User deposits ₹100

System mints:
- 1 India
- 1 Australia
- 1 England
- 1 Other
```

The user can then sell individual outcome shares to other traders.

Example:

```text
User A mints complete set for ₹100.

User A sells:
- India at ₹40
- Australia at ₹30
- England at ₹20
- Other at ₹10
```

If all shares are sold, User A receives:

```text
₹40 + ₹30 + ₹20 + ₹10 = ₹100
```

User A has no remaining exposure.

The buyers now each hold outcome risk.

## 11. Buying One Outcome

Suppose User B buys:

```text
10 India shares at ₹40
```

Cost:

```text
10 × ₹40 = ₹400
```

If India wins:

```text
User B receives 10 × ₹100 = ₹1000
Profit = ₹1000 - ₹400 = ₹600
```

If any other outcome wins:

```text
User B receives ₹0
Loss = ₹400
```

## 12. Selling One Outcome

Selling an outcome means the user gives up that outcome share in exchange for cash.

Example:

```text
User A owns 10 India shares.
User A sells 10 India shares at ₹45.
```

User A receives:

```text
10 × ₹45 = ₹450
```

User A no longer receives payout if India wins for those 10 sold shares.

The buyer now owns the India upside.

## 13. Shorting An Outcome

Shorting an outcome is more complex than selling an owned share.

If a user wants to sell India without owning India shares, the platform must ensure the user can pay if India wins.

There are two ways to support this:

```text
1. Require the seller to own the India share before selling.
2. Allow synthetic shorting with collateral equal to payout - sale_price.
```

For V1 study, the safest model is:

```text
Users can sell only shares they already own.
```

This avoids undercollateralized short exposure.

Advanced versions can support shorting, but it requires stricter collateral and risk rules.

## 14. Order Book Model

A multiple-choice market has one order book per outcome.

Example:

```text
India order book
Australia order book
England order book
Other order book
```

Each outcome order book can have:

```text
bids = users who want to buy that outcome
asks = users who want to sell that outcome
```

Example India order book:

```text
Bids:
₹40 × 100
₹39 × 200

Asks:
₹42 × 150
₹43 × 100
```

The spread is:

```text
Best ask - best bid = ₹42 - ₹40 = ₹2
```

## 15. Order Types

Basic order types:

```text
LIMIT_BUY
LIMIT_SELL
CANCEL
```

Later:

```text
MARKET_BUY
MARKET_SELL
```

Market orders should require slippage limits because low-liquidity outcome markets can execute at bad prices.

## 16. Limit Buy Workflow

Example:

```text
User B wants to buy 10 India shares at ₹40.
```

Workflow:

```text
1. User selects market.
2. User selects outcome: India.
3. User selects action: BUY.
4. User enters price: ₹40.
5. User enters quantity: 10.
6. System calculates required funds: ₹400.
7. System validates market is open.
8. System validates price, quantity, tick size, and balance.
9. System locks ₹400 from user's wallet.
10. System tries to match against India sell orders at ₹40 or lower.
11. If matched, trade is created.
12. If partially matched, remaining quantity stays open.
13. If unmatched, order remains on the India bid book.
```

## 17. Limit Sell Workflow

Example:

```text
User A wants to sell 10 India shares at ₹45.
```

Workflow:

```text
1. User selects market.
2. User selects outcome: India.
3. User selects action: SELL.
4. User enters price: ₹45.
5. User enters quantity: 10.
6. System validates market is open.
7. System validates user owns at least 10 unlocked India shares.
8. System locks 10 India shares.
9. System tries to match against India buy orders at ₹45 or higher.
10. If matched, buyer receives India shares.
11. Seller receives cash.
12. If partially matched, remaining locked shares stay as an open sell order.
13. If unmatched, order remains on the India ask book.
```

## 18. Matching Rule For Outcome Order Books

For each outcome, matching can follow normal price-time priority.

For a buy order:

```text
Match against the lowest available sell price less than or equal to the buy limit.
```

For a sell order:

```text
Match against the highest available buy price greater than or equal to the sell limit.
```

Priority:

```text
1. Best price
2. Earliest created_at
```

Example:

```text
Incoming buy:
Buy 10 India at ₹45

Sell book:
₹42 × 3
₹43 × 4
₹46 × 10
```

Matches:

```text
3 shares at ₹42
4 shares at ₹43
```

The ₹46 sell order does not match because it is above the buyer's ₹45 limit.

Remaining buy quantity:

```text
3 shares
```

The remaining quantity can rest as a bid at ₹45 or cancel, depending on order settings.

## 19. Trade Record

Each matched fill should record:

```text
id
market_id
outcome_id
buy_order_id
sell_order_id
buyer_user_id
seller_user_id
price
quantity
created_at
```

Example:

```text
Market: Tournament winner
Outcome: India
Buyer: User B
Seller: User A
Price: ₹42
Quantity: 3
```

## 20. Position Model

Positions should track how many shares of each outcome a user owns.

Example:

```text
User B positions:
India: 10 shares
Australia: 0 shares
England: 0 shares
Other: 0 shares
```

Position fields:

```text
user_id
market_id
outcome_id
quantity
locked_quantity
average_entry_price
realized_pnl
created_at
updated_at
```

The `locked_quantity` is used when the user places sell orders.

Example:

```text
User owns 10 India shares.
User places sell order for 4 India shares.

quantity = 10
locked_quantity = 4
available_quantity = 6
```

## 21. Wallet Workflow

Buying shares locks cash.

Example:

```text
Buy 10 India at ₹40
Required cash = ₹400
```

Wallet update when order is placed:

```text
available_cash decreases by ₹400
locked_cash increases by ₹400
```

When order fills:

```text
locked_cash decreases by fill_cost
cash is transferred to seller
buyer receives shares
```

When order is cancelled:

```text
locked_cash for unfilled quantity is released
available_cash increases by released amount
```

Selling shares locks shares, not cash.

Example:

```text
Sell 10 India at ₹45
```

Position update when sell order is placed:

```text
available India shares decreases by 10
locked India shares increases by 10
```

When sell order fills:

```text
locked India shares decreases
buyer receives shares
seller receives cash
```

When sell order is cancelled:

```text
locked India shares are released
available India shares increases
```

## 22. Collateral Safety

The platform must always be able to pay winning shares.

In the complete set model:

```text
Every issued group of outcome shares is backed by payout collateral.
```

For one complete set:

```text
Collateral = ₹100

Issued:
1 India
1 Australia
1 England
1 Other
```

At settlement, exactly one share pays:

```text
1 winning share × ₹100 = ₹100
```

The collateral is sufficient.

Critical invariant:

```text
total_complete_sets_issued × payout = total_market_collateral
```

Another useful invariant:

```text
issued_quantity must be equal across all outcomes
```

Example:

```text
India issued = 100
Australia issued = 100
England issued = 100
Other issued = 100
```

This means there are:

```text
100 complete sets
```

Market collateral must be:

```text
100 × ₹100 = ₹10,000
```

## 23. Why Independent Binary Markets Are Dangerous

Do not model this as four unrelated binary markets:

```text
India YES/NO
Australia YES/NO
England YES/NO
Other YES/NO
```

That creates unnecessary complexity and can break the probability relationship between outcomes.

The linked multiple-choice model says:

```text
India + Australia + England + Other = ₹100
```

Independent binary markets would each have:

```text
India YES + India NO = ₹100
Australia YES + Australia NO = ₹100
England YES + England NO = ₹100
Other YES + Other NO = ₹100
```

That is not the clean model for a tournament winner market.

The better mental model:

```text
One market.
Many outcome shares.
Exactly one winner.
One collateral pool per complete set.
```

## 24. End-to-End Example

Market:

```text
Who will win the tournament?
```

Payout:

```text
₹100
```

Outcomes:

```text
India
Australia
England
Other
```

Initial complete set creation:

```text
User A deposits ₹100 collateral.
System mints:
- 1 India share
- 1 Australia share
- 1 England share
- 1 Other share
```

User A sells shares:

```text
India sold to User B for ₹40
Australia sold to User C for ₹30
England sold to User D for ₹20
Other sold to User E for ₹10
```

Total received by User A:

```text
₹40 + ₹30 + ₹20 + ₹10 = ₹100
```

Current holders:

```text
User B owns 1 India
User C owns 1 Australia
User D owns 1 England
User E owns 1 Other
```

Market resolves:

```text
Australia wins.
```

Settlement:

```text
User B receives ₹0
User C receives ₹100
User D receives ₹0
User E receives ₹0
```

Collateral used:

```text
₹100
```

System remains fully funded.

## 25. Market Lifecycle

Lifecycle:

```text
DRAFT
REVIEW
APPROVED
OPEN
PAUSED
CLOSED
PENDING_RESOLUTION
RESOLVED
VOIDED
ARCHIVED
```

Workflow:

```text
1. User or admin proposes market.
2. Platform defines exact question.
3. Platform defines all valid outcomes.
4. Platform confirms outcomes are mutually exclusive.
5. Platform confirms outcomes are collectively exhaustive.
6. Platform defines payout, tick size, close time, and resolution source.
7. Admin approves market.
8. Market opens.
9. Complete sets can be minted.
10. Users trade outcome shares.
11. Market reaches close time.
12. Trading stops.
13. Open orders are cancelled.
14. Locked cash and locked shares are released.
15. Oracle evidence is captured.
16. Admin or automated resolver selects winning outcome.
17. Winning outcome holders are paid.
18. Losing outcome holders receive zero.
19. Market is reconciled.
20. Market is archived.
```

## 26. Settlement Workflow

When the market closes:

```text
1. Stop accepting new orders.
2. Cancel all open buy orders.
3. Release locked cash from cancelled buy orders.
4. Cancel all open sell orders.
5. Release locked shares from cancelled sell orders.
6. Capture oracle evidence.
7. Select winning outcome.
8. Calculate payout for each holder of winning outcome.
9. Debit market collateral pool.
10. Credit winning users.
11. Mark losing outcome shares as expired.
12. Write settlement ledger entries.
13. Mark market as resolved.
14. Notify users.
```

Formula:

```text
user_payout = winning_outcome_quantity × payout
```

Example:

```text
User C owns 12 Australia shares.
Payout = ₹100.

User C receives:
12 × ₹100 = ₹1200
```

## 27. Void Workflow

A market may need to be voided if the question cannot be resolved fairly.

Examples:

```text
- tournament is cancelled
- rules were written incorrectly
- listed outcomes were not exhaustive
- official result is unavailable
- settlement source contradicts itself
```

Void policy must be defined before launch.

Common simple policy:

```text
All outstanding shares are redeemed pro-rata from the market collateral pool.
```

For a complete set model, one simple refund rule is:

```text
Each complete set is unwound at payout value.
```

But if shares have traded many times, refund policy becomes sensitive.

Pred-Market should not launch multiple-choice markets until the void policy is explicit.

## 28. Fees

Fees can be charged in several places:

```text
- trading fee on fills
- settlement fee on winnings
- withdrawal fee
```

For clean early design, start with:

```text
no fees in the core matching model
```

Then add fees after the no-fee accounting model is correct.

Fees affect:

```text
- implied probability
- user P&L
- ledger entries
- displayed odds
- settlement proceeds
```

## 29. Database Tables Needed

Multiple-choice markets require the binary model to be extended.

Core tables:

```text
markets
market_outcomes
orders
trades
positions
wallets
ledger_entries
market_collateral_pools
settlements
oracle_evidence
audit_logs
```

Important table changes:

```text
orders must reference outcome_id
trades must reference outcome_id
positions must reference outcome_id
settlement must reference winning_outcome_id
```

Suggested `market_outcomes` fields:

```text
id
market_id
name
description
display_order
status
created_at
updated_at
```

Suggested `market_collateral_pools` fields:

```text
id
market_id
payout_amount
complete_sets_issued
collateral_amount
created_at
updated_at
```

## 30. Critical Invariants

These rules must always hold:

```text
1. Exactly one outcome wins unless the market is voided.
2. Outcomes must be mutually exclusive.
3. Outcomes must be collectively exhaustive.
4. Each issued complete set must contain one share of every outcome.
5. Market collateral must equal complete_sets_issued × payout.
6. Issued share quantity must be equal across all outcomes.
7. A user cannot sell more shares than they own.
8. A user cannot buy without sufficient locked cash.
9. Filled quantity cannot exceed order quantity.
10. Cancelled buy orders must release locked cash.
11. Cancelled sell orders must release locked shares.
12. Settlement must be idempotent.
13. Losing outcome shares must not receive payout.
14. Winning outcome payout must not exceed market collateral.
15. All wallet, position, trade, and ledger updates must be transactional.
```

## 31. Risks And Hard Parts

Multiple-choice markets are harder than binary markets because:

```text
- there are more order books
- liquidity is split across outcomes
- complete set minting/redemption must be correct
- sell orders require share custody
- shorting requires more complex collateral
- void policy is more complex
- users may misunderstand Other
- outcome wording errors can break settlement
```

The most dangerous product errors are:

```text
- overlapping outcomes
- missing outcome bucket
- unclear Other definition
- weak resolution source
- allowing undercollateralized short selling
- settling more than one outcome as winner
```

## 32. End-to-End Edge Cases

This section defines the edge cases Pred-Market must handle before multiple-choice markets can safely launch.

The recommended V1 policy is conservative:

```text
- one market has many outcomes
- exactly one outcome wins
- outcomes must be mutually exclusive
- outcomes must be collectively exhaustive
- complete sets are fully collateralized
- users can sell only shares they already own
- no naked shorting
- no market orders initially
- no outcome changes after trading opens except through halt/void/admin process
```

## 33. Market Design Edge Cases

### 33.1 Overlapping Outcomes

Problem:

```text
Outcomes:
- India
- Asian team
- Australia
- Other
```

If India wins, both `India` and `Asian team` are true.

Required handling:

```text
Reject market before approval.
```

System rule:

```text
Do not allow trading until admin confirms exactly one outcome can win.
```

### 33.2 Missing Outcome

Problem:

```text
Outcomes:
- India
- Australia
- England
```

If South Africa wins, no listed outcome is true.

Required handling:

```text
Reject market unless an exhaustive bucket exists.
```

Usually add:

```text
Other
```

### 33.3 Ambiguous Other

Problem:

```text
Other
```

without definition.

Required handling:

```text
Define exactly what Other includes.
```

Example:

```text
Other means any tournament winner that is not India, Australia, or England.
```

### 33.4 Outcome Name Changes

Problem:

```text
Team name changes after market opens.
```

Required handling:

```text
Do not change the economic meaning of the outcome.
Allow only display-name correction with audit log.
```

Example:

```text
Old display: Team A
New display: Team A / official renamed team
Economic outcome remains the same.
```

### 33.5 Duplicate Outcomes

Problem:

```text
India
India
Australia
Other
```

Required handling:

```text
Reject at market review.
```

Database guard:

```text
unique(market_id, normalized_outcome_name)
```

### 33.6 Outcome Added After Trading Starts

Problem:

```text
Market opens with India/Australia/England/Other.
Later admin wants to add South Africa.
```

This changes all existing prices and positions.

Required V1 handling:

```text
Do not allow outcome additions after trading opens.
```

If the outcome list is materially wrong:

```text
halt market
cancel open orders
resolve through void policy
create a new corrected market
```

### 33.7 Outcome Removed After Trading Starts

Problem:

```text
An outcome is removed after users traded it.
```

Required V1 handling:

```text
Do not allow outcome removal after trading opens.
```

If removal is necessary because the market was invalid:

```text
halt and void
```

### 33.8 Event Cancelled Before Completion

Example:

```text
Tournament is cancelled.
```

Required handling:

```text
Use predefined void policy.
```

Do not improvise settlement after the fact.

### 33.9 Event Format Changes

Example:

```text
Tournament changes from knockout to league format.
```

Required handling:

```text
If the original resolution rule still clearly identifies one winner, continue.
If not, halt and use void/dispute process.
```

### 33.10 Joint Winners

Problem:

```text
Official result declares co-winners.
```

Multiple-choice markets require exactly one winner.

Required handling:

```text
Market rules must define tie/co-winner treatment before launch.
```

Possible policies:

```text
1. Official primary winner only.
2. Void if co-winners are declared.
3. Split payout across winning outcomes.
```

Recommended V1:

```text
Avoid split payout.
Use official single winner or void.
```

### 33.11 Dead Heat / Tie

Problem:

```text
Two outcomes tie under the data source.
```

Required V1 handling:

```text
Use explicit market rule.
If no explicit rule exists, halt and escalate to admin dispute review.
```

Recommended market design:

```text
Avoid markets where ties are likely unless tie is its own outcome.
```

### 33.12 Participant Withdraws

Example:

```text
England withdraws from tournament before close.
```

Required handling:

```text
Do not remove the England outcome.
Let market prices adjust.
England can still settle to zero if it does not win.
```

If withdrawal changes tournament validity:

```text
follow market-specific rules
```

## 34. Order Entry Edge Cases

### 34.1 Price Below Minimum

Problem:

```text
Buy India @ ₹0
```

Required handling:

```text
Reject order.
```

Rule:

```text
price >= tick_size
```

### 34.2 Price Above Payout

Problem:

```text
Buy India @ ₹120
Payout = ₹100
```

Required handling:

```text
Reject order.
```

Rule:

```text
price <= payout
```

Recommended stricter rule:

```text
price <= payout - tick_size
```

unless the system intentionally allows guaranteed-loss prices.

### 34.3 Invalid Tick Size

Problem:

```text
Tick size = ₹1
Order price = ₹40.25
```

Required handling:

```text
Reject order.
```

Rule:

```text
price % tick_size == 0
```

### 34.4 Quantity Below Minimum

Problem:

```text
Minimum quantity = 1
Order quantity = 0
```

Required handling:

```text
Reject order.
```

### 34.5 Quantity Above Maximum

Problem:

```text
Max order size = 1000
Order quantity = 10000
```

Required handling:

```text
Reject or require admin/market-maker permission.
```

### 34.6 Insufficient Cash For Buy

Problem:

```text
User tries to buy 10 India @ ₹40.
Required = ₹400.
Available cash = ₹300.
```

Required handling:

```text
Reject order.
Do not create partially funded order.
```

### 34.7 Insufficient Shares For Sell

Problem:

```text
User owns 5 India shares.
User tries to sell 10 India shares.
```

Required V1 handling:

```text
Reject order.
```

Reason:

```text
V1 does not allow naked shorting.
```

### 34.8 Selling Shares Already Locked

Problem:

```text
User owns 10 India shares.
User already has open sell order for 8 India shares.
User tries to sell 5 more India shares.
```

Available shares:

```text
10 - 8 = 2
```

Required handling:

```text
Reject order or allow only quantity 2 if user explicitly edits quantity.
```

Recommended V1:

```text
Reject with clear available quantity.
```

### 34.9 Order On Closed Market

Problem:

```text
Market status = CLOSED or PENDING_RESOLUTION.
User places order.
```

Required handling:

```text
Reject order.
```

### 34.10 Order On Paused Market

Problem:

```text
Risk team pauses market.
User places order.
```

Required handling:

```text
Reject new orders.
Allow cancellations unless the market is under legal/compliance lock.
```

### 34.11 Duplicate Order Submission

Problem:

```text
User clicks submit twice.
Network retries same request.
```

Required handling:

```text
Use idempotency key.
Process once.
Return same result for repeated request.
```

### 34.12 User Cancels During Matching

Problem:

```text
Cancel request arrives while order is being matched.
```

Required handling:

```text
Serialize through row locks or order state transition.
```

Valid final states:

```text
FILLED
PARTIALLY_FILLED_AND_CANCELLED
CANCELLED
```

Invalid final state:

```text
filled quantity greater than original quantity
```

### 34.13 Self-Trade

Problem:

```text
Same user has buy and sell orders that would match.
```

Required handling:

```text
Apply self-trade prevention.
```

Possible policies:

```text
1. Cancel newest order.
2. Cancel oldest order.
3. Decrement both orders without trade.
4. Allow only for approved market makers with surveillance.
```

Recommended V1:

```text
Cancel or reject the incoming order that would self-trade.
```

### 34.14 Restricted User

Problem:

```text
User is suspended, KYC-blocked, or jurisdiction-blocked.
```

Required handling:

```text
Reject new orders.
Allow withdrawal/cancellation according to compliance policy.
```

## 35. Matching Edge Cases

### 35.1 No Matching Sell Order

Example:

```text
Buy India @ ₹40.
Best India sell = ₹45.
```

Required handling:

```text
Order rests on book as bid at ₹40.
```

### 35.2 No Matching Buy Order

Example:

```text
Sell India @ ₹45.
Best India buy = ₹40.
```

Required handling:

```text
Order rests on book as ask at ₹45.
```

### 35.3 Partial Fill

Example:

```text
Buy India @ ₹45, qty 10.
Sell India @ ₹42, qty 3.
```

Required handling:

```text
Fill 3.
Remaining buy quantity = 7.
```

Remaining quantity:

```text
rests or cancels based on time-in-force
```

### 35.4 Multiple Price Levels

Example:

```text
Incoming buy India @ ₹45, qty 10.

Sell book:
₹42 × 3
₹43 × 4
₹45 × 10
```

Required handling:

```text
Match ₹42 first, then ₹43, then ₹45.
```

Reason:

```text
lowest sell price is best for buyer
```

### 35.5 Equal Price Priority

Example:

```text
Sell India @ ₹42 from User A at 10:00
Sell India @ ₹42 from User B at 10:05
```

Required handling:

```text
User A fills first.
```

Rule:

```text
price priority first
time priority second
```

### 35.6 Price Improvement

Example:

```text
Buyer limit = ₹45
Seller ask = ₹42
```

Possible execution prices:

```text
1. resting order price: ₹42
2. incoming order price: ₹45
3. midpoint or custom rule
```

Recommended V1:

```text
execute at resting order price
```

Reason:

```text
standard CLOB behavior and easier auditability
```

### 35.7 Locked Funds After Partial Fill

Example:

```text
Buy 10 India @ ₹45.
3 fill at ₹42.
```

Initially locked:

```text
10 × ₹45 = ₹450
```

Actual fill cost:

```text
3 × ₹42 = ₹126
```

Remaining lock needed:

```text
7 × ₹45 = ₹315
```

Excess release:

```text
₹450 - ₹126 - ₹315 = ₹9
```

Required handling:

```text
release price-improvement excess immediately or after order completion.
```

Recommended V1:

```text
release excess immediately after each fill.
```

### 35.8 Complete-Set Arbitrage Not Available

Problem:

```text
India + Australia + England + Other < ₹100
```

Example:

```text
₹35 + ₹25 + ₹20 + ₹10 = ₹90
```

This creates arbitrage if users can buy all outcomes for ₹90 and redeem a complete set for ₹100.

Required handling depends on whether redemption is enabled.

Recommended V1:

```text
Do not allow automatic complete-set redemption until it is deliberately designed.
```

If redemption is enabled:

```text
Allow user to buy full set and redeem for payout.
This helps force prices back toward ₹100.
```

### 35.9 Complete-Set Sum Above Payout

Problem:

```text
India + Australia + England + Other > ₹100
```

Example:

```text
₹45 + ₹35 + ₹25 + ₹15 = ₹120
```

This means the market is expensive across all outcomes.

Required handling:

```text
Allow prices if they come from normal order books.
Do not force displayed best prices to sum exactly to payout.
```

Reason:

```text
spreads, fees, and liquidity can make displayed prices deviate from payout.
```

### 35.10 N-Way Combination Matching Failure

If the advanced algorithm tries to combine buy orders across every outcome:

```text
India @ ₹40
Australia @ ₹30
England @ ₹20
Other @ ₹15
```

Sum:

```text
₹105
```

Required handling:

```text
No complete-set match.
Orders remain open.
```

Recommended V1:

```text
Avoid n-way matching initially.
Use complete-set minting plus per-outcome order books.
```

### 35.11 Liquidity Fragmentation

Problem:

```text
Many outcomes split liquidity thinly.
```

Required handling:

```text
show depth per outcome
show warning for wide spreads
support market maker tooling later
```

### 35.12 Dust Remainders

Problem:

```text
Partial fills leave tiny quantities below minimum tradable size.
```

Required handling:

```text
Define dust policy.
```

Recommended V1:

```text
If remaining quantity < min_quantity, cancel remainder and release funds/shares.
```

## 36. Complete Set And Collateral Edge Cases

### 36.1 Mint Without Full Payout Collateral

Problem:

```text
User tries to mint complete set with ₹90 when payout is ₹100.
```

Required handling:

```text
Reject mint.
```

### 36.2 Incomplete Set Minted

Problem:

```text
System mints India/Australia/England but misses Other.
```

Required handling:

```text
Rollback transaction.
No partial complete set may exist.
```

### 36.3 Unequal Issued Quantities

Problem:

```text
India issued = 100
Australia issued = 100
England issued = 100
Other issued = 99
```

Required handling:

```text
block settlement
trigger critical reconciliation alert
repair only through audited admin procedure
```

### 36.4 Collateral Pool Mismatch

Problem:

```text
complete_sets_issued = 100
payout = ₹100
required collateral = ₹10,000
actual collateral = ₹9,900
```

Required handling:

```text
halt market
block withdrawals from affected pool
trigger reconciliation incident
```

### 36.5 Redemption Of Full Set Before Settlement

If supported, user can redeem:

```text
1 India + 1 Australia + 1 England + 1 Other
```

for:

```text
₹100
```

Required handling:

```text
burn one share of every outcome
reduce complete_sets_issued by 1
release ₹100 collateral
```

Recommended V1:

```text
Do not support redemption until minting, trading, and settlement are tested.
```

### 36.6 User Owns Full Set Through Trading

Problem:

```text
User buys one share of every outcome from the market.
```

This is economically equivalent to holding a risk-free complete set.

Required handling:

```text
Allow holding.
Optional later: allow redemption.
```

### 36.7 Fees Break Exact Sum

Problem:

```text
Outcome prices sum to ₹100, but fees make total user cost ₹101.
```

Required handling:

```text
Display fees separately.
Do not treat user all-in cost as pure probability.
```

Recommended early model:

```text
no fees until accounting is proven
```

## 37. Settlement Edge Cases

### 37.1 Settlement Called Twice

Problem:

```text
Admin clicks resolve twice.
Background job retries.
```

Required handling:

```text
settlement must be idempotent
```

Rule:

```text
same settlement_id cannot pay twice
market cannot move RESOLVED -> RESOLVED with new payout
```

### 37.2 Wrong Outcome Selected

Problem:

```text
Admin accidentally resolves India instead of Australia.
```

Required handling:

```text
Use maker-checker approval before final settlement.
```

Recommended flow:

```text
1. admin proposes winning outcome
2. second admin approves
3. settlement executes
4. correction after execution requires formal incident process
```

### 37.3 Oracle Data Missing

Problem:

```text
Resolution source unavailable.
```

Required handling:

```text
move market to PENDING_RESOLUTION
do not settle
allow admin to attach evidence later
```

### 37.4 Conflicting Oracle Sources

Problem:

```text
Source A says India.
Source B says Australia.
```

Required handling:

```text
use market's predefined primary source
if primary source is ambiguous, escalate to dispute process
```

### 37.5 Result Later Corrected

Problem:

```text
Official source first says India, later corrects to Australia.
```

Required handling:

```text
market rules must define correction window.
```

Recommended V1:

```text
settle only after official final result and admin review
avoid instant settlement for high-risk markets
```

### 37.6 Market Closes While Orders Are Matching

Problem:

```text
Close job starts while matching transaction is active.
```

Required handling:

```text
use market row lock
serialize market close and matching
```

Valid behavior:

```text
orders accepted before close may finish if transaction began before close
or system may reject all orders whose final commit happens after close
```

Required product decision:

```text
choose one rule and enforce consistently.
```

Recommended V1:

```text
order must commit before close_time to be valid.
```

### 37.7 Open Orders At Settlement

Problem:

```text
Open buy/sell orders still exist when settlement starts.
```

Required handling:

```text
cancel all open orders first
release locked cash and shares
then settle positions
```

### 37.8 Locked Shares Included In Settlement

Problem:

```text
Winning shares are locked in an open sell order.
```

Required handling:

```text
cancel open sell order before settlement
release locked shares
then pay current owner
```

### 37.9 Losing Shares Not Expired

Problem:

```text
Losing shares remain active after settlement.
```

Required handling:

```text
mark all outcome positions final
winning outcome paid
losing outcomes expired at zero
```

### 37.10 Rounding Error

Problem:

```text
Fractional prices or fees cause rounding leftovers.
```

Required handling:

```text
use integer minor units
define rounding policy
send residual to fee/reconciliation account only if policy allows
```

Recommended V1:

```text
integer paise only
no fractional paise
```

## 38. Void And Dispute Edge Cases

### 38.1 Market Was Badly Worded

Problem:

```text
Question can be interpreted in multiple ways.
```

Required handling:

```text
halt
admin review
void if no objective resolution is possible
```

### 38.2 Outcome List Not Exhaustive

Problem:

```text
Unlisted participant wins and Other was not included.
```

Required handling:

```text
void market unless rules clearly cover the case.
```

### 38.3 Outcome List Overlaps

Problem:

```text
two outcomes are true
```

Required handling:

```text
void or apply predefined precedence rule.
```

Recommended V1:

```text
void if overlap reaches settlement.
```

### 38.4 Event Permanently Abandoned

Problem:

```text
tournament never finishes
```

Required handling:

```text
void after predefined waiting period
```

Example rule:

```text
If no official winner is declared within 30 days after scheduled end date, market voids.
```

### 38.5 Event Postponed

Problem:

```text
tournament delayed by 2 weeks
```

Required handling:

```text
market rules must define whether close/resolution moves with event.
```

Recommended:

```text
allow admin to update close_time before original close, with audit log and user notification.
```

### 38.6 User Disputes Resolution

Required handling:

```text
accept dispute during configured dispute window
freeze final withdrawal of disputed settlement if policy requires
record dispute evidence
admin resolves dispute
```

Recommended V1:

```text
manual dispute handling in admin console
```

### 38.7 Void Refund Formula

This must be decided before launch.

Possible policies:

```text
1. Refund current holders pro-rata by share count.
2. Refund original complete-set minters.
3. Redeem every outstanding share at equal value.
4. Use final pre-void mark price.
```

Recommended V1 policy for simplicity:

```text
If voided, each outstanding share receives payout / number_of_outcomes.
```

Example:

```text
Payout = ₹100
Outcomes = 4
Void refund per share = ₹25
```

Important consequence:

```text
This may create gains/losses versus traded prices.
Users must see this policy before trading.
```

## 39. Wallet And Ledger Edge Cases

### 39.1 Negative Balance Attempt

Required handling:

```text
database constraint and application validation block it
```

### 39.2 Ledger Does Not Balance

Problem:

```text
cash debit does not equal cash credit
```

Required handling:

```text
rollback transaction
raise critical alert
```

### 39.3 Trade Created But Position Not Updated

Required handling:

```text
trade, wallet, position, and ledger writes must be one transaction
```

### 39.4 Position Updated But Ledger Missing

Required handling:

```text
rollback transaction
```

### 39.5 Deposit Reversal

Problem:

```text
user deposits money, trades, then payment provider reverses deposit.
```

Required handling:

```text
do not credit trading balance until deposit is final or risk-approved
```

### 39.6 Withdrawal With Open Orders

Problem:

```text
user tries to withdraw cash locked in buy orders
```

Required handling:

```text
only available_cash can be withdrawn
locked_cash cannot be withdrawn
```

### 39.7 Settlement Payout While Withdrawal Pending

Required handling:

```text
serialize wallet updates
use wallet row lock
```

## 40. System And Concurrency Edge Cases

### 40.1 Two Buyers Hit Same Sell Order

Problem:

```text
two requests try to fill same sell order
```

Required handling:

```text
lock order row during matching
filled_quantity cannot exceed quantity
```

### 40.2 Two Sellers Sell Same Shares

Problem:

```text
same user submits two sell orders for same available shares
```

Required handling:

```text
lock position row
available_quantity cannot go negative
```

### 40.3 API Timeout After Successful Order

Problem:

```text
server commits order but client times out
```

Required handling:

```text
client retries with same idempotency key
server returns original committed result
```

### 40.4 Background Job Retry

Problem:

```text
settlement job fails halfway and retries
```

Required handling:

```text
settlement steps must be idempotent
each payout must have unique settlement ledger key
```

### 40.5 Redis Outage

Required handling:

```text
trading correctness must not depend on Redis
PostgreSQL remains source of truth
rebuild order book snapshots from database
```

### 40.6 WebSocket Missed Update

Required handling:

```text
client can resync order book through REST snapshot
events include monotonically increasing sequence numbers
```

### 40.7 Server Crash During Transaction

Required handling:

```text
database rollback handles uncommitted transaction
on restart, reconciliation job checks stuck orders/locks
```

## 41. Admin And Compliance Edge Cases

### 41.1 Admin Pauses Market

Required behavior:

```text
new orders rejected
matching stopped
cancellations allowed by default
state change audited
users notified
```

### 41.2 Admin Unpauses Market

Required behavior:

```text
market reopens only after risk reason is cleared
audit entry required
```

### 41.3 Admin Resolves Without Evidence

Required handling:

```text
block final settlement unless oracle evidence is attached
```

### 41.4 Admin Edits Resolution Source

Required V1 handling:

```text
do not allow resolution source changes after market opens
```

If absolutely necessary:

```text
halt market
notify users
require senior admin approval
audit before/after values
```

### 41.5 Suspicious Trading

Examples:

```text
self-trading
wash trading
multi-account manipulation
price spikes near settlement
```

Required handling:

```text
surveillance alerts
manual review
possible market pause
```

### 41.6 User Account Frozen

Required behavior:

```text
block new orders
cancel open orders if policy requires
do not delete positions
settlement still credits/debits according to legal policy
```

## 42. User Interface Edge Cases

### 42.1 User Misunderstands Other

Required UI:

```text
show exact Other definition next to outcome
```

### 42.2 Displayed Probabilities Do Not Sum To 100%

This can happen because:

```text
spreads
fees
stale books
low liquidity
different bid/ask sides
```

Required UI:

```text
do not promise displayed prices sum exactly to 100%
show bid/ask and last traded price separately
```

### 42.3 Low Liquidity

Required UI:

```text
show depth
show spread
warn when order may not fill
```

### 42.4 Stale Market Data

Required UI:

```text
show reconnecting/stale state
refresh from REST snapshot
do not submit orders against stale assumptions without final confirmation
```

### 42.5 User Places Bad Fat-Finger Order

Example:

```text
Buy India @ ₹90 when best ask is ₹40.
```

Required handling:

```text
show confirmation for orders far away from last price or best ask
```

Recommended V1:

```text
fat-finger price bands
```

## 43. Required Edge-Case Test Matrix

Before launch, tests should cover:

```text
1. overlapping outcomes rejected
2. missing Other rejected for non-exhaustive market
3. duplicate outcomes rejected
4. buy order with insufficient cash rejected
5. sell order with insufficient shares rejected
6. sell order cannot use already locked shares
7. partial buy fill updates cash, shares, order quantity
8. partial sell fill updates cash, shares, order quantity
9. cancel buy releases locked cash
10. cancel sell releases locked shares
11. self-trade prevention works
12. duplicate order request is idempotent
13. market close cancels open orders before settlement
14. settlement pays only winning outcome
15. settlement cannot pay twice
16. losing shares expire at zero
17. void pays according to explicit void formula
18. complete set mint creates equal outcome quantities
19. complete set mint cannot happen without full collateral
20. collateral pool equals complete_sets_issued × payout
21. database transaction rollback leaves no partial trade
22. two concurrent matches cannot overfill order
23. two concurrent sell orders cannot overlock shares
24. Redis outage does not affect source-of-truth balances
25. WebSocket resync recovers correct order book
```

## 44. Edge-Case Policy Decisions Still Required

These decisions must be finalized before coding multiple-choice markets:

```text
1. Are complete-set redemptions allowed before settlement?
2. What is the exact void refund formula?
3. What happens if official results are corrected after settlement?
4. Are co-winners voided or handled by predefined tie logic?
5. Are market orders allowed, or only limit orders?
6. Is price improvement executed at resting order price?
7. Are fees charged on trades, settlement, or both?
8. What is the dispute window?
9. Can admin extend close_time after market opens?
10. What self-trade prevention policy is used?
```

Recommended V1 answers:

```text
1. No pre-settlement redemption.
2. Void refund = payout / number_of_outcomes per outstanding share.
3. No correction after final settlement unless formal incident process.
4. Void co-winner markets unless tie rule exists.
5. Limit orders only.
6. Execute at resting order price.
7. No fees initially.
8. Manual dispute window, defined per market.
9. Only before original close_time, with audit and notification.
10. Reject incoming order that would self-trade.
```

## 45. Updated V1 Recommendation

For Pred-Market, multiple-choice markets should come after the binary YES/NO engine is correct.

Recommended implementation path:

```text
1. Build binary YES/NO markets first.
2. Build wallet, ledger, matching, positions, and settlement correctly.
3. Add outcome_id to generalize positions and orders.
4. Add complete set collateral model.
5. Add one order book per outcome.
6. Support complete-set minting.
7. Support limit buy orders.
8. Support limit sell orders only for owned shares.
9. Add cancellation with locked cash/share release.
10. Add market close and open-order cancellation.
11. Add admin-controlled settlement.
12. Add explicit void handling.
13. Add reconciliation jobs.
14. Add edge-case tests before frontend launch.
15. Add market maker tooling later to improve liquidity.
```

The safest first multiple-choice version:

```text
One market
Many mutually exclusive outcomes
Complete set collateral
Buy outcome shares
Sell only owned outcome shares
No naked shorts
No market orders initially
No pre-settlement complete-set redemption initially
No fees initially
Admin-controlled resolution
Maker-checker settlement approval
Explicit void formula
Idempotent settlement
Full audit trail
```

## 46. Final Mental Model

A multiple-choice market is:

```text
One question with many possible answers.
Exactly one answer wins.
Each answer is a tradable outcome share.
One complete set contains one share of every answer.
One complete set is backed by one payout amount.
The winning share receives the payout.
All losing shares expire at zero.
```

For the tournament example:

```text
India + Australia + England + Other = ₹100
```

This is the multiple-choice equivalent of:

```text
YES + NO = ₹100
```
