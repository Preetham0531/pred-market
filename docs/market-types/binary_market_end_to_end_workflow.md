# Binary YES/NO Market End-to-End Workflow

This document defines the complete Binary YES/NO market model for Pred-Market: how it works, variables, pricing rules, order flow, matching, collateral, settlement, edge cases, test cases, operating rules, compliance gates, and user-facing terms.

This is a product and engineering planning document. It is not legal advice. Real-money prediction markets require jurisdiction-specific legal review before launch.

## 1. Definition

A binary prediction market asks a question with exactly two possible outcomes:

```text
YES
NO
```

Example:

```text
Will Bitcoin be above $100,000 on Dec 31?
```

Outcome meanings:

```text
YES = Bitcoin is above $100,000 at the defined observation time.
NO = Bitcoin is not above $100,000 at the defined observation time.
```

A binary market must be:

```text
objective
time-bound
source-bound
settleable as exactly YES or NO unless voided
```

## 2. Core Mental Model

Binary market:

```text
YES + NO = payout
```

Example:

```text
Payout = INR 100
YES price = INR 40
NO price = INR 60

INR 40 + INR 60 = INR 100
```

The platform is an exchange:

```text
users trade against users
platform matches compatible orders
platform does not take directional risk
```

## 3. Core Variables

```text
P = payout per winning contract
Y = YES price
N = NO price
Q = quantity
C = total collateral
T_close = market close time
T_obs = observation time
R = resolution rule
S = settlement source
```

Example:

```text
P = INR 100
Y = INR 40
N = INR 60
Q = 10
```

Collateral:

```text
C = P × Q
C = INR 100 × 10 = INR 1000
```

## 4. Fundamental Invariant

For every matched binary contract:

```text
Y + N = P
```

For quantity:

```text
(Y × Q) + (N × Q) = P × Q
```

Example:

```text
YES buyer pays INR 40 × 10 = INR 400
NO buyer pays INR 60 × 10 = INR 600

Total collateral = INR 1000
Maximum payout liability = INR 100 × 10 = INR 1000
```

This ensures the platform can always pay the winner.

## 5. Contract Definition

A binary contract must define:

```text
market title
YES condition
NO condition
payout amount
tick size
minimum quantity
maximum quantity
close time
observation time
timezone
resolution source
void policy
dispute window
fee policy
```

Example:

```text
Title:
Will Bitcoin be above $100,000 on Dec 31, 2026?

YES:
BTC/USD price is strictly greater than $100,000 at 23:59:59 UTC on Dec 31, 2026 according to the specified source.

NO:
BTC/USD price is less than or equal to $100,000 at that time.

Void:
If the specified source is permanently unavailable and no backup source is defined.
```

## 6. Valid Market Wording

Good binary market:

```text
Will BTC/USD be greater than $100,000 at 23:59:59 UTC on Dec 31, 2026 according to Source X?
```

Bad binary market:

```text
Will Bitcoin do well this year?
```

Why bad:

```text
"do well" is subjective
no threshold
no source
no observation time
```

## 7. YES And NO Must Be Complements

YES and NO must cover all non-void possibilities.

Good:

```text
YES = value > 100000
NO = value <= 100000
```

Bad:

```text
YES = India wins by more than 10 runs
NO = Australia wins
```

Problem:

```text
India could win by fewer than 10 runs.
That is neither YES nor NO.
```

Correct version:

```text
YES = India wins by more than 10 runs.
NO = India does not win by more than 10 runs.
```

## 8. Price And Probability

The price can be interpreted as implied probability:

```text
YES implied probability = YES price / payout
NO implied probability = NO price / payout
```

Example:

```text
YES price = INR 40
Payout = INR 100

YES implied probability = 40 / 100 = 40%
```

This is not a guarantee. Prices can be affected by:

```text
fees
spread
low liquidity
market manipulation attempts
user behavior
stale information
```

## 9. Order Model

Recommended V1 order actions:

```text
BUY_YES
BUY_NO
CANCEL
```

Later:

```text
SELL_YES
SELL_NO
MARKET_ORDER
```

For the simplest binary V1, a user expresses a view by buying YES or buying NO.

Example:

```text
User A buys YES @ INR 40, quantity 10.
User B buys NO @ INR 60, quantity 10.
```

These are compatible because:

```text
40 + 60 = 100
```

## 10. Limit Order Workflow

```text
1. User selects market.
2. User selects side: YES or NO.
3. User enters price.
4. User enters quantity.
5. System validates market is OPEN.
6. System validates user eligibility.
7. System validates price, tick size, and quantity.
8. System calculates required funds.
9. System locks funds.
10. System searches compatible opposite orders.
11. If compatible orders exist, trade is created.
12. If partially filled, remainder stays open.
13. If not filled, order stays in order book.
14. User receives order/fill notification.
```

Required funds:

```text
BUY_YES required = YES price × quantity
BUY_NO required = NO price × quantity
```

## 11. Matching Algorithm

Strict V1 matching:

```text
incoming YES @ Y matches resting NO @ (P - Y)
incoming NO @ N matches resting YES @ (P - N)
```

Example:

```text
Payout = INR 100
Incoming YES @ INR 40
Required NO = INR 60
```

Priority:

```text
1. compatible price
2. earliest created_at
```

This is deliberately simpler than a full professional CLOB.

Later CLOB model:

```text
support bids/asks for YES shares
support selling owned shares
support price improvement
support crossing orders
```

## 12. One-To-Many Matching

Example:

```text
Payout = INR 100
User A buys 10 YES @ INR 40
```

Compatible NO orders:

```text
User B buys 3 NO @ INR 60
User C buys 4 NO @ INR 60
User D buys 3 NO @ INR 60
```

Total:

```text
3 + 4 + 3 = 10
```

Result:

```text
User A gets 10 YES
User B gets 3 NO
User C gets 4 NO
User D gets 3 NO
```

Collateral:

```text
YES side: INR 40 × 10 = INR 400
NO side: INR 60 × 10 = INR 600
Total: INR 1000
```

## 13. Many-To-Many Matching

Example:

```text
YES orders:
A buys 4 YES @ INR 40
B buys 6 YES @ INR 40

NO orders:
C buys 3 NO @ INR 60
D buys 7 NO @ INR 60
```

Total YES quantity:

```text
10
```

Total NO quantity:

```text
10
```

Valid matched set:

```text
A owns 4 YES
B owns 6 YES
C owns 3 NO
D owns 7 NO
```

## 14. Invalid Price Stacking

Invalid:

```text
Payout = INR 100
A buys 10 YES @ INR 40
B buys 10 NO @ INR 30
C buys 10 NO @ INR 30
```

Although:

```text
40 + 30 + 30 = 100
```

this is invalid.

Reason:

```text
Each contract unit must pair one YES with one NO.
You cannot stack two NO buyers against one YES buyer.
```

If NO wins, both B and C would expect payout, causing undercollateralization.

## 15. Wallet And Collateral Workflow

When order is placed:

```text
available_balance decreases
locked_balance increases
```

When order fills:

```text
locked_balance decreases
trade collateral increases
position is created or increased
ledger entries are written
```

When order is cancelled:

```text
unfilled locked funds are released
available_balance increases
locked_balance decreases
```

No fill may occur without locked funds.

## 16. Position Model

Position fields:

```text
user_id
market_id
side
quantity
average_entry_price
realized_pnl
status
created_at
updated_at
```

Example:

```text
User A:
side = YES
quantity = 10
average_entry_price = INR 40
```

If YES wins:

```text
payout = INR 100 × 10 = INR 1000
profit = INR 1000 - INR 400 = INR 600
```

If NO wins:

```text
payout = INR 0
loss = INR 400
```

## 17. Ledger Model

Use double-entry accounting.

Ledger events:

```text
DEPOSIT
WITHDRAWAL
ORDER_LOCK
ORDER_RELEASE
TRADE_COLLATERAL
FEE_DEBIT
SETTLEMENT_CREDIT
VOID_REFUND
ADJUSTMENT
```

Required rule:

```text
Every transaction must balance.
```

Example trade:

```text
A locked INR 400 for YES.
B locked INR 600 for NO.
Trade moves INR 1000 into market collateral.
```

Settlement:

```text
If YES wins, collateral pays A.
If NO wins, collateral pays B.
```

## 18. Settlement Workflow

```text
1. Market reaches close time.
2. System stops accepting new orders.
3. Open orders are cancelled.
4. Locked funds for unfilled orders are released.
5. Oracle evidence is captured.
6. Admin or resolver determines YES, NO, or VOID.
7. Maker-checker approval confirms outcome.
8. Settlement job calculates payouts.
9. Winning users are credited.
10. Losing positions expire at zero.
11. Ledger entries are written.
12. Market is marked RESOLVED or VOIDED.
13. Users are notified.
14. Market is archived after dispute window.
```

## 19. Settlement Outcomes

If YES wins:

```text
YES holders receive P × quantity
NO holders receive 0
```

If NO wins:

```text
NO holders receive P × quantity
YES holders receive 0
```

If VOID:

```text
refund according to market void policy
```

Recommended V1 void policy:

```text
refund each holder's original matched cost, net of any already-disclosed non-refundable fee policy
```

Recommended early model:

```text
no fees
full refund of matched cost on void
```

## 20. Market Close Rules

Market close must define:

```text
close_time
timezone
whether orders must be received before close
whether orders must commit before close
```

Recommended V1:

```text
order must commit before close_time to be valid
```

When market closes:

```text
new orders rejected
matching stops
open orders cancelled
unfilled funds released
positions remain until settlement
```

## 21. Edge Cases

### 21.1 Ambiguous Question

Problem:

```text
Question can be interpreted multiple ways.
```

Required handling:

```text
reject during review
or halt and void if discovered after trading
```

### 21.2 YES And NO Not Exhaustive

Problem:

```text
possible result is neither YES nor NO
```

Required handling:

```text
reject market before approval
```

### 21.3 YES And NO Both True

Problem:

```text
bad wording makes both outcomes true
```

Required handling:

```text
halt and dispute review
void unless predefined precedence rule exists
```

### 21.4 Equality Boundary

Example:

```text
Will BTC be above $100,000?
Final value = exactly $100,000
```

Required handling:

```text
NO wins if wording says above
YES wins only if wording says at or above
```

### 21.5 Oracle Source Unavailable

Required handling:

```text
move to PENDING_RESOLUTION
use backup source only if predefined
void if no reliable source exists
```

### 21.6 Conflicting Sources

Required handling:

```text
use predefined primary source
do not choose source after outcome is known
```

### 21.7 Result Later Corrected

Required handling:

```text
market rules must define correction window
```

Recommended V1:

```text
settle after official final source is stable
post-settlement correction requires formal incident process
```

### 21.8 Event Cancelled

Required handling:

```text
use market-specific void policy
```

### 21.9 Event Postponed

Required handling:

```text
market rules define whether close/resolution moves with event
```

### 21.10 Duplicate Order Submission

Required handling:

```text
use idempotency key
process once
return same result on retry
```

### 21.11 Cancel During Matching

Required handling:

```text
lock order rows
valid final state is FILLED, CANCELLED, or PARTIALLY_FILLED_CANCELLED
```

### 21.12 Partial Fill

Required handling:

```text
filled quantity <= original quantity
remaining quantity rests or cancels according to order type
unfilled funds remain locked until cancel or expiry
```

### 21.13 Self-Trade

Required V1:

```text
reject incoming order that would self-trade
```

### 21.14 Restricted User

Required handling:

```text
block new orders
allow cancellation/withdrawal according to compliance policy
do not delete ledger records
```

### 21.15 Settlement Called Twice

Required handling:

```text
settlement must be idempotent
same market cannot pay twice
```

### 21.16 Wallet Mismatch

Required handling:

```text
halt affected market/user
run reconciliation
block settlement if collateral is insufficient
```

### 21.17 Rounding

Required handling:

```text
use integer minor units
no fractional paise
```

### 21.18 Fees

Fees affect:

```text
displayed probability
profit/loss
ledger entries
refund policy
```

Recommended V1:

```text
no fees until accounting is proven
```

## 22. Required Test Cases

### 22.1 Market Creation Tests

```text
1. Market cannot open without YES condition.
2. Market cannot open without NO condition.
3. Market cannot open without resolution source.
4. Market cannot open without close time.
5. Market cannot open if YES/NO are not complements.
6. Ambiguous wording requires rejection.
7. Equality boundary must be explicit for threshold markets.
```

### 22.2 Order Validation Tests

```text
1. Active user can place valid order.
2. Restricted user cannot place order.
3. Closed market rejects order.
4. Paused market rejects new order.
5. Price below tick rejected.
6. Price above payout rejected.
7. Invalid tick price rejected.
8. Quantity below minimum rejected.
9. Quantity above maximum rejected.
10. Insufficient funds rejected.
11. Duplicate request is idempotent.
```

### 22.3 Matching Tests

```text
1. YES @ 40 matches NO @ 60 when payout is 100.
2. YES @ 40 does not match NO @ 50.
3. NO @ 60 matches YES @ 40.
4. Earlier compatible order fills first.
5. Partial fill updates both orders.
6. Many NO orders can fill one YES order by quantity.
7. Many YES orders can fill one NO order by quantity.
8. Invalid price stacking is rejected.
9. Filled quantity cannot exceed order quantity.
10. Self-trade is prevented.
```

### 22.4 Wallet And Ledger Tests

```text
1. Buy YES locks correct funds.
2. Buy NO locks correct funds.
3. Fill moves locked funds into collateral.
4. Cancel releases unfilled locked funds.
5. Partial fill keeps correct remaining lock.
6. Wallet cannot go negative.
7. Ledger entries balance.
8. Trade, position, wallet, and ledger write atomically.
9. Rollback leaves no partial trade.
10. Reconciliation detects mismatch.
```

### 22.5 Settlement Tests

```text
1. YES win pays only YES holders.
2. NO win pays only NO holders.
3. Losing side receives zero.
4. Total settlement payout does not exceed collateral.
5. Open orders are cancelled before settlement.
6. Settlement requires oracle evidence.
7. Settlement requires admin approval.
8. Settlement is idempotent.
9. VOID refunds according to policy.
10. Market cannot trade after settlement.
```

### 22.6 Concurrency Tests

```text
1. Two incoming orders cannot overfill same resting order.
2. Cancel and match cannot both consume same quantity.
3. Market close and order placement serialize correctly.
4. Settlement retry does not duplicate ledger entries.
5. API timeout plus retry returns original order result.
6. Database crash rolls back uncommitted transaction.
```

## 23. Rules And Regulations Operating Policy

This section defines internal operating rules. Legal counsel must approve jurisdiction-specific versions before launch.

### 23.1 User Eligibility

Users must:

```text
be legally permitted to trade
meet minimum age requirements
pass required KYC checks
not be in restricted jurisdictions
not be sanctioned or blocked
not use multiple accounts to evade limits
```

### 23.2 Market Integrity

Users must not:

```text
self-trade
wash trade
manipulate prices
submit false information
use multiple accounts abusively
abuse APIs
interfere with settlement sources
trade in markets they can directly control unless allowed and disclosed
```

### 23.3 Prohibited Market Categories

Do not list markets involving:

```text
death
terrorism
assassination
war
crime
illegal activity
personal injury
minors
named private individuals without approval
medical diagnosis of named people
personal tragedy
events prohibited by local law
```

Markets involving:

```text
sports
elections
securities
commodities
macroeconomic data
court outcomes
public policy
```

require legal review before launch.

### 23.4 KYC/AML

Required controls:

```text
identity verification when required
sanctions screening
transaction monitoring
suspicious activity review
deposit and withdrawal controls
record retention
```

### 23.5 Data Protection

Required controls:

```text
collect only necessary personal data
protect user data
limit admin access
log admin access
support privacy rights where required
define retention period
handle breach notification duties
```

### 23.6 Responsible Trading

Recommended controls:

```text
risk warnings
deposit limits
loss limits
cool-off periods
self-exclusion
clear fees
clear odds/probability explanation
clear void policy
```

## 24. Terms And Conditions Template

This is a product template, not final legal text.

### 24.1 Acceptance

```text
By using Pred-Market, the user accepts platform terms, market rules, risk disclosures, fee schedule, privacy policy, and jurisdiction restrictions.
```

### 24.2 Eligibility

```text
The user must be legally eligible, of required age, verified when required, and not located in a restricted jurisdiction.
```

### 24.3 Market Rules

```text
Each market has its own question, YES condition, NO condition, close time, resolution source, void policy, and dispute window. The user is responsible for reviewing them before trading.
```

### 24.4 Risk Disclosure

```text
Users can lose the full amount committed to a position.
Prices are user-generated.
Displayed probabilities are estimates.
Markets may be illiquid.
Settlement may be delayed.
Void rules may produce different outcomes than expected.
```

### 24.5 Orders

```text
Limit orders may fill fully, partially, or not at all. The platform matches orders according to published rules and may cancel orders during halt, close, void, compliance action, or incident response.
```

### 24.6 Settlement

```text
Settlement is based on predefined market rules and resolution source. The platform may delay settlement for evidence collection, dispute review, technical issues, or compliance review.
```

### 24.7 Voids

```text
The platform may void a market according to the market's void policy if the event cannot be resolved fairly, the event is cancelled, the question is defective, or required data is unavailable.
```

### 24.8 Prohibited Conduct

```text
Users may not manipulate markets, self-trade, wash trade, evade limits, submit false information, abuse APIs, or violate applicable law.
```

### 24.9 Account Restrictions

```text
The platform may restrict, freeze, suspend, or close accounts when required by law, compliance policy, fraud controls, risk controls, or market integrity rules.
```

### 24.10 Fees

```text
Fees must be disclosed before trading or settlement. V1 may launch with no fees until accounting is proven.
```

### 24.11 Disputes

```text
Users may dispute settlement during the stated dispute window. Evidence standards and final decision process must be documented.
```

### 24.12 Taxes

```text
Users are responsible for applicable taxes unless the platform is legally required to withhold or report.
```

## 25. Admin Approval Checklist

Before opening a binary market:

```text
1. Question is objective.
2. YES condition is clear.
3. NO condition is exact complement of YES.
4. Equality/boundary case is defined.
5. Close time is defined.
6. Observation time is defined.
7. Timezone is defined.
8. Resolution source is authoritative.
9. Backup source policy is defined.
10. Void policy is defined.
11. Dispute window is defined.
12. Payout and tick size are defined.
13. Quantity limits are defined.
14. Jurisdiction review is complete.
15. Prohibited category check is complete.
16. Admin approval is audited.
```

## 26. V1 Recommendation

Safest binary V1:

```text
YES/NO only
limit orders only
strict complementary matching
no naked shorting
no market orders initially
no fees initially
integer minor units
fully collateralized fills
admin-controlled resolution
maker-checker settlement approval
explicit void policy
idempotent settlement
full audit trail
```

Build order:

```text
1. Market and contract model.
2. Wallet and ledger.
3. Limit order placement.
4. Fund locking.
5. Complementary matching.
6. Trade creation.
7. Position updates.
8. Cancellation.
9. Market close.
10. Oracle evidence.
11. Settlement.
12. Void handling.
13. Admin tools.
14. Reconciliation.
15. API endpoints.
16. Realtime order book updates.
```

## 27. Final Mental Model

Binary market:

```text
One question.
Two possible outcomes.
YES or NO wins.
YES price + NO price = payout.
Both sides fund the full payout together.
The winner receives payout.
The loser receives zero.
The platform matches users and keeps the market fully collateralized.
```

