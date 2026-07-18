# Prediction Market Types End-to-End Documentation

This document defines the market types Pred-Market may support, how each one works, the variables required, matching and settlement logic, edge cases, test cases, platform rules, compliance gates, and user-facing terms.

This is a product and engineering planning document. It is not legal advice. Real-money prediction markets can trigger gambling, exchange, derivatives, payments, tax, KYC/AML, data protection, advertising, and consumer-protection rules. A qualified lawyer must approve jurisdiction-specific launch plans before users trade real money.

For an implementation-facing V1 spec focused only on buyable discrete contract products, see [Six Buyable Contract Market Types](six_buyable_contract_market_types.md).

## 1. Market Types Covered

```text
1. Binary YES/NO market
2. Multiple-choice market
3. Range market
4. Threshold market
5. Conditional market
6. Combo / parlay-style market
7. Scalar market
```

## 2. Universal Product Model

Pred-Market should be designed as:

```text
an exchange-style prediction market
```

not:

```text
a sportsbook that takes directional risk
```

Core exchange principle:

```text
Users trade against other users.
The platform matches orders.
The platform does not choose winners for profit.
The platform does not take the opposite side unless explicitly acting as a disclosed market maker under approved policy.
```

## 3. Universal Entities

Core entities:

```text
User
Wallet
Market
Outcome
Contract
Order
Order Book
Trade / Fill
Position
Collateral Pool
Ledger Entry
Settlement
Oracle Evidence
Audit Log
Dispute
Notification
```

For binary markets:

```text
outcomes = YES / NO
```

For multiple-choice and range markets:

```text
outcomes = a fixed exhaustive outcome set
```

For scalar markets:

```text
outcome = numeric settlement value mapped to payout formula
```

## 4. Universal Money Rules

Use integer minor units.

Example:

```text
₹100.00 = 10000 paise
```

Never use floating-point values for:

```text
prices
payouts
fees
wallet balances
settlement amounts
collateral
```

Use:

```text
integer amount_minor
```

Every trade must be fully collateralized.

Core invariant:

```text
platform_collateral >= maximum_possible_payout_liability
```

No user wallet may go negative.

No position quantity may go negative unless the system explicitly supports shorting. V1 should not support naked shorting.

## 5. Universal Market Lifecycle

Recommended lifecycle:

```text
DRAFT
REVIEW
APPROVED
OPEN
PAUSED
CLOSED
PENDING_RESOLUTION
DISPUTED
RESOLVED
VOIDED
ARCHIVED
```

Lifecycle rules:

```text
1. Only APPROVED markets can open.
2. Only OPEN markets accept new orders.
3. PAUSED markets reject new orders.
4. CLOSED markets reject new orders.
5. PENDING_RESOLUTION markets reject orders and await evidence.
6. RESOLVED markets cannot trade.
7. VOIDED markets cannot trade.
8. ARCHIVED markets are read-only.
```

## 6. Universal Order Rules

V1 order types:

```text
LIMIT_BUY
LIMIT_SELL
CANCEL
```

Recommended not in first V1:

```text
MARKET_BUY
MARKET_SELL
NAKED_SHORT
LEVERAGED_POSITION
```

Order validation:

```text
market.status == OPEN
user.status == ACTIVE
user is allowed in jurisdiction
user passes required KYC/AML state
price > 0
price <= payout
price respects tick_size
quantity >= min_quantity
quantity <= max_quantity
buy has sufficient available cash
sell has sufficient available shares
```

Order priority:

```text
price priority first
time priority second
```

For buy orders:

```text
higher price has better priority
```

For sell orders:

```text
lower price has better priority
```

For equal price:

```text
earlier created_at fills first
```

## 7. Universal Settlement Rules

Settlement must be:

```text
objective
auditable
idempotent
based on predefined market rules
backed by oracle evidence
```

Settlement must not:

```text
depend on platform profit
change after execution except through formal incident process
pay more than collateral
pay losing outcomes
double-pay repeated settlement calls
```

Settlement workflow:

```text
1. Close market.
2. Cancel open orders.
3. Release locked cash and locked shares.
4. Capture oracle evidence.
5. Determine final outcome/value.
6. Calculate payouts.
7. Write ledger entries.
8. Credit users.
9. Mark positions final.
10. Mark market resolved or voided.
11. Notify users.
12. Archive after dispute window.
```

## 8. Universal Edge Cases

Every market type must handle:

```text
ambiguous wording
bad resolution source
late official correction
event cancellation
event postponement
market close while matching
duplicate order submission
self-trade
partial fill
cancel during matching
wallet lock mismatch
position lock mismatch
settlement retry
admin mistake
oracle outage
Redis/WebSocket outage
database rollback
user suspension
jurisdiction restriction
dispute
void
rounding
fees
tax reporting
```

## 9. Universal Compliance And Regulation Gates

Pred-Market must not launch real-money trading until these gates are cleared:

```text
1. Jurisdiction legal review.
2. Market category approval policy.
3. KYC/AML policy.
4. Age and residency controls.
5. Payment provider approval.
6. Data protection policy.
7. User risk disclosures.
8. Terms and conditions.
9. Market manipulation policy.
10. Dispute and void policy.
11. Tax reporting review.
12. Records/audit retention policy.
```

Compliance design requirements:

```text
block restricted jurisdictions
block restricted users
record user consent to terms
record market rule version at order time
record oracle source and evidence
record all admin actions
detect self-trading and wash trading
detect suspicious multi-account behavior
support account freeze without deleting ledger records
support legally required reports
```

## 10. Regulatory Reference Points

These are reference points for compliance planning, not final legal conclusions.

United States:

```text
CFTC materials describe event contracts and prediction markets.
CFTC Rule 40.11 and related materials identify categories of event contracts that may be prohibited or contrary to public interest, including activities such as terrorism, assassination, war, gaming, or unlawful activities.
```

India:

```text
Real-money markets may implicate online gaming, gambling/betting, payments, KYC/AML, tax, consumer protection, and data protection rules.
RBI KYC directions are relevant if the platform or partners are regulated entities or perform covered financial flows.
The Digital Personal Data Protection Act, 2023 is relevant to personal data handling.
MeitY online gaming/intermediary materials are relevant to online real-money game/intermediary analysis.
```

Required policy:

```text
Before launch, legal counsel must classify each market type and each market category by jurisdiction.
```

Do not list markets referencing:

```text
death
terrorism
assassination
war
crime commission
illegal activity
personal tragedy
private individuals without approval
minors
medical diagnosis of named people
court outcomes where prohibited
elections where prohibited
securities/commodities where licensing is required and not obtained
sports/gaming where prohibited
```

## 11. Market Type 1: Binary YES/NO

### 11.1 Definition

A binary market has exactly two mutually exclusive outcomes:

```text
YES
NO
```

Example:

```text
Will Bitcoin be above $100,000 on Dec 31?
```

### 11.2 Variables

```text
P = payout
Y = YES price
N = NO price
Q = quantity
T = close time
R = resolution rule
```

### 11.3 Core Invariant

```text
YES price + NO price = payout
```

Example:

```text
P = ₹100
Y = ₹40
N = ₹60

₹40 + ₹60 = ₹100
```

For quantity:

```text
(Y × Q) + (N × Q) = P × Q
```

### 11.4 Workflow

```text
1. Admin defines market question.
2. Admin defines YES condition.
3. Admin defines NO condition.
4. Admin defines payout, tick size, close time, and resolution source.
5. Market opens.
6. Users place YES/NO buy orders.
7. Matching engine pairs compatible YES and NO orders.
8. Funds are locked and moved to collateral.
9. Users hold YES or NO positions.
10. Market closes.
11. Oracle evidence is captured.
12. Outcome resolves YES, NO, or VOID.
13. Winning side receives payout.
14. Losing side receives zero.
```

### 11.5 Matching

For strict V1 complementary matching:

```text
incoming YES @ Y matches NO @ (P - Y)
incoming NO @ N matches YES @ (P - N)
```

Example:

```text
Payout = ₹100
Buy YES @ ₹40
Required NO = ₹60
```

### 11.6 Settlement

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
refund according to void policy
```

### 11.7 Edge Cases

```text
ambiguous YES condition
ambiguous NO condition
YES and NO both true
YES and NO both false
event cancelled
oracle unavailable
late result correction
user places order after close
partial fill
cancelled remainder
settlement retry
fees affecting displayed probability
```

### 11.8 Test Cases

```text
1. YES @ 40 matches NO @ 60 when payout is 100.
2. YES @ 40 does not match NO @ 50.
3. Partial YES quantity matches multiple NO orders.
4. Filled quantity never exceeds order quantity.
5. Wallet cannot go negative.
6. Cancelled order releases locked funds.
7. Closed market rejects new order.
8. YES settlement pays only YES holders.
9. NO settlement pays only NO holders.
10. Repeated settlement does not double pay.
11. VOID uses configured refund policy.
12. Oracle evidence is required before resolution.
```

## 12. Market Type 2: Multiple-Choice

### 12.1 Definition

A multiple-choice market has more than two outcomes, and exactly one outcome wins.

Example:

```text
Who will win the tournament?

India
Australia
England
Other
```

### 12.2 Variables

```text
P = payout
O = set of outcomes
n = number of outcomes
o_i = individual outcome
p_i = price of outcome i
Q = quantity
```

### 12.3 Outcome Rules

Outcomes must be:

```text
mutually exclusive
collectively exhaustive
```

Meaning:

```text
only one outcome can win
one outcome must be able to win
```

### 12.4 Core Invariant

For a complete outcome set:

```text
p_1 + p_2 + ... + p_n = P
```

Example:

```text
India ₹40
Australia ₹30
England ₹20
Other ₹10

Total = ₹100
```

### 12.5 Complete Set Model

A complete set contains one share of every outcome.

Example:

```text
1 India
1 Australia
1 England
1 Other
```

Collateral:

```text
₹100
```

because exactly one share will pay.

### 12.6 Workflow

```text
1. Admin defines market question.
2. Admin defines all outcome choices.
3. Admin confirms no overlaps.
4. Admin confirms outcome set is exhaustive.
5. Admin defines Other precisely if used.
6. Market opens.
7. Complete sets can be minted with full collateral.
8. Users trade individual outcome shares.
9. Each outcome has its own order book.
10. Users can buy outcome shares.
11. Users can sell only owned outcome shares.
12. Market closes.
13. Open orders are cancelled.
14. Winning outcome is selected.
15. Winning holders are paid.
16. Losing shares expire at zero.
```

### 12.7 Matching

Recommended first implementation:

```text
normal per-outcome order books
```

Example India book:

```text
Bids:
₹40 × 100
₹39 × 200

Asks:
₹42 × 100
₹43 × 200
```

Buy matching:

```text
buy order matches lowest sell price <= buy limit
```

Sell matching:

```text
sell order matches highest buy price >= sell limit
```

Advanced later:

```text
n-way complete-set combinatorial matching
```

### 12.8 Settlement

Example:

```text
Australia wins.
```

Settlement:

```text
Australia shares pay P
India, England, Other pay 0
```

### 12.9 Edge Cases

```text
overlapping outcomes
missing Other
ambiguous Other
duplicate outcomes
outcome added after market opens
outcome removed after market opens
joint winners
participant withdrawal
complete set collateral mismatch
unequal issued share quantities
void refund policy
liquidity fragmented across outcomes
```

### 12.10 Test Cases

```text
1. Overlapping outcomes are rejected.
2. Missing exhaustive bucket is rejected.
3. Duplicate outcome is rejected.
4. Complete set mint creates equal shares for all outcomes.
5. Mint fails without full payout collateral.
6. User cannot sell more shares than owned.
7. Buy order locks cash.
8. Sell order locks shares.
9. Cancel buy releases cash.
10. Cancel sell releases shares.
11. Settlement pays only winning outcome.
12. Losing outcomes expire at zero.
13. Settlement cannot execute if issued quantities are unequal.
14. VOID uses configured refund formula.
```

## 13. Market Type 3: Range

### 13.1 Definition

A range market asks where a numeric value will fall.

Example:

```text
What will CPI be?

Below 2%
2% to 3%
3% to 4%
Above 4%
```

It is a special multiple-choice market where each outcome is a numeric interval.

### 13.2 Variables

```text
V = final observed value
P = payout
R_i = range outcome i
lower_i = lower bound
upper_i = upper bound
inclusive_lower_i = true/false
inclusive_upper_i = true/false
source = data source
observation_time = time value is measured
```

### 13.3 Range Boundary Rules

Ranges must be:

```text
non-overlapping
gapless
precisely bounded
```

Bad:

```text
2% to 3%
3% to 4%
```

because exact `3.0%` is ambiguous unless inclusivity is defined.

Good:

```text
V < 2.0%
2.0% <= V < 3.0%
3.0% <= V < 4.0%
V >= 4.0%
```

### 13.4 Workflow

```text
1. Admin defines numeric question.
2. Admin defines official data source.
3. Admin defines observation date/time.
4. Admin defines units and rounding.
5. Admin defines non-overlapping ranges.
6. Admin validates ranges cover every possible value.
7. Market opens.
8. Users trade range outcome shares.
9. Market closes before observation.
10. Official value is captured.
11. System maps value to exactly one range.
12. Winning range pays payout.
13. Other ranges expire at zero.
```

### 13.5 Settlement

Example:

```text
Final CPI = 3.2%
```

Ranges:

```text
V < 2.0%
2.0% <= V < 3.0%
3.0% <= V < 4.0%
V >= 4.0%
```

Winning range:

```text
3.0% <= V < 4.0%
```

### 13.6 Edge Cases

```text
value exactly on boundary
source revises value later
source publishes preliminary and final values
source unavailable
unit mismatch
rounding mismatch
negative value
out-of-range value
all ranges not exhaustive
two ranges overlap
observation timezone unclear
```

### 13.7 Test Cases

```text
1. V = 1.99 maps to Below 2%.
2. V = 2.00 maps to 2%-3% if lower bound is inclusive.
3. V = 3.00 maps to 3%-4% if lower bound is inclusive.
4. V = 4.00 maps to Above 4% if upper range is inclusive.
5. Overlapping ranges are rejected.
6. Gap between ranges is rejected.
7. Missing upper catch-all is rejected.
8. Missing lower catch-all is rejected.
9. Source unavailable moves market to PENDING_RESOLUTION.
10. Revised value follows predefined correction policy.
11. Settlement pays only mapped range.
12. Boundary tests use integer/scaled numeric representation.
```

## 14. Market Type 4: Threshold

### 14.1 Definition

A threshold market asks whether a value crosses a cutoff.

Example:

```text
Will Bitcoin be above $100,000 on Dec 31?
```

This is usually a binary YES/NO market.

### 14.2 Variables

```text
V = observed value
T = threshold
P = payout
operator = >, >=, <, <=
source = official data source
observation_time = exact measurement time
```

### 14.3 Settlement Formula

Example:

```text
YES wins if BTC price > $100,000.
NO wins if BTC price <= $100,000.
```

If the question says:

```text
above
```

then equality does not count.

If the question says:

```text
at or above
```

then equality counts.

### 14.4 Workflow

```text
1. Admin defines threshold question.
2. Admin defines value source.
3. Admin defines threshold.
4. Admin defines comparison operator.
5. Admin defines observation time and timezone.
6. Market opens as binary YES/NO.
7. Users trade.
8. Market closes before observation.
9. Source value is captured.
10. System compares value to threshold.
11. YES or NO wins.
```

### 14.5 Edge Cases

```text
value equals threshold
price source outage
multiple exchanges show different values
timezone ambiguity
intraday high vs close price confusion
asset redenomination
source revises historical value
flash crash/manipulated print
stablecoin/depeg conversion issue
```

### 14.6 Test Cases

```text
1. V > T resolves YES for above market.
2. V = T resolves NO for above market.
3. V >= T resolves YES for at-or-above market.
4. V < T resolves YES for below market.
5. Missing source value blocks settlement.
6. Wrong timezone fixture fails validation.
7. Close price and intraday high are not interchangeable.
8. Settlement is idempotent.
9. Oracle evidence is stored.
10. Late correction follows policy.
```

## 15. Market Type 5: Conditional

### 15.1 Definition

A conditional market depends on another event happening first.

Example:

```text
If Team A reaches the final, will they win?
```

There are two parts:

```text
C = condition event
Q = main question
```

### 15.2 Variables

```text
C = condition
Q = question
P = payout
condition_source = source for C
question_source = source for Q
condition_status = TRUE/FALSE/UNKNOWN
question_status = TRUE/FALSE/UNKNOWN
```

### 15.3 Settlement Logic

Recommended policy:

```text
If C is false:
    market voids

If C is true and Q is true:
    YES wins

If C is true and Q is false:
    NO wins
```

Example:

```text
Condition: Team A reaches final.
Question: Team A wins final.
```

Outcomes:

```text
Team A reaches final and wins -> YES
Team A reaches final and loses -> NO
Team A does not reach final -> VOID
```

### 15.4 Workflow

```text
1. Admin defines condition.
2. Admin defines main question.
3. Admin defines what happens if condition fails.
4. Admin defines evidence sources for both.
5. Market opens.
6. Users trade YES/NO.
7. Condition is evaluated.
8. If condition false, market voids.
9. If condition true, main question is evaluated.
10. YES/NO settlement occurs.
```

### 15.5 Edge Cases

```text
condition never occurs
condition occurs but main event cancelled
condition source differs from question source
condition disputed
condition resolved after main event
condition becomes impossible before close
partial tournament format change
void policy unclear
```

### 15.6 Test Cases

```text
1. C false voids market.
2. C true and Q true resolves YES.
3. C true and Q false resolves NO.
4. C unknown blocks settlement.
5. Q unknown blocks settlement after C true.
6. Condition evidence is stored separately from question evidence.
7. Failed condition uses void refund policy.
8. Settlement retry does not double refund.
9. Market cannot resolve YES/NO if C is false.
10. Admin cannot skip condition evaluation.
```

## 16. Market Type 6: Combo / Parlay-Style

### 16.1 Definition

A combo market combines two or more legs into one contract.

Example:

```text
Will both X and Y happen?
```

YES wins only if all required legs happen.

### 16.2 Variables

```text
L = set of legs
n = number of legs
l_i = individual leg
status_i = TRUE/FALSE/VOID/UNKNOWN
P = payout
combo_operator = ALL / ANY / EXACTLY_K
```

V1 should start with:

```text
ALL
```

Meaning:

```text
YES wins if every leg is true.
NO wins if at least one leg is false.
```

### 16.3 Truth Table

For two legs:

```text
X true, Y true   -> YES
X true, Y false  -> NO
X false, Y true  -> NO
X false, Y false -> NO
```

### 16.4 Workflow

```text
1. Admin defines each leg.
2. Admin defines source and close time for each leg.
3. Admin defines operator, usually ALL.
4. Admin defines void handling for each leg.
5. Market opens as binary YES/NO.
6. Users trade.
7. Each leg resolves independently.
8. Combo engine evaluates final truth table.
9. YES/NO settles.
```

### 16.5 Void Policy

Recommended V1:

```text
If any leg voids, the entire combo market voids.
```

Alternative later:

```text
remove void leg and reprice combo
```

Not recommended for early V1 because it is confusing and legally sensitive.

### 16.6 Edge Cases

```text
one leg voids
one leg delayed
legs have different close times
leg source unavailable
one leg resolved then corrected
correlated legs
duplicate legs
conflicting legs
impossible combo
same event appears twice
user misunderstands all-or-nothing payout
```

### 16.7 Test Cases

```text
1. All legs true resolves YES.
2. Any leg false resolves NO.
3. Any leg void resolves VOID under V1 policy.
4. Unknown leg blocks settlement.
5. Duplicate leg is rejected.
6. Impossible combo is rejected.
7. Conflicting legs are rejected.
8. Late leg correction follows policy.
9. Combo settlement stores evidence for every leg.
10. Settlement is idempotent.
```

## 17. Market Type 7: Scalar

### 17.1 Definition

A scalar market pays according to a numeric value, not just one winning bucket.

Example:

```text
What will CPI be?

Lower bound = 0%
Upper bound = 10%
Payout = ₹100
```

If final CPI is 5%, payout may be ₹50.

### 17.2 Variables

```text
V = final observed value
L = lower bound
U = upper bound
P = maximum payout
payoff_formula = function(V, L, U, P)
source = official source
observation_time = exact time
rounding_policy = numeric rounding rule
```

### 17.3 Linear Payoff Formula

For a linear scalar market:

```text
if V <= L:
    payout = 0

if V >= U:
    payout = P

if L < V < U:
    payout = ((V - L) / (U - L)) × P
```

Example:

```text
L = 0%
U = 10%
P = ₹100
V = 5%

payout = ((5 - 0) / (10 - 0)) × 100 = ₹50
```

### 17.4 Opposite Side

The opposite side receives:

```text
P - scalar_payout
```

Example:

```text
scalar payout = ₹50
opposite payout = ₹50
```

If V = 8%:

```text
scalar payout = ₹80
opposite payout = ₹20
```

### 17.5 Workflow

```text
1. Admin defines numeric variable.
2. Admin defines lower and upper bounds.
3. Admin defines payoff formula.
4. Admin defines source, units, and observation time.
5. Market opens.
6. Users trade scalar exposure.
7. Market closes.
8. Final value is captured.
9. Payout is calculated by formula.
10. Settlement distributes proportional payout.
```

### 17.6 Edge Cases

```text
value below lower bound
value above upper bound
value exactly equals lower bound
value exactly equals upper bound
rounding fractional payout
source revision
unit mismatch
negative values
formula bug
users misunderstand proportional payout
```

### 17.7 Test Cases

```text
1. V <= L pays 0 to scalar side.
2. V >= U pays full payout to scalar side.
3. V halfway pays 50% payout.
4. Opposite side receives P - scalar_payout.
5. Payout never below 0.
6. Payout never above P.
7. Rounding policy is deterministic.
8. Unit mismatch blocks settlement.
9. Formula version is stored with market.
10. Settlement is idempotent.
```

### 17.8 V1 Recommendation

Scalar markets are advanced.

Recommended:

```text
Do not implement scalar markets until binary, range, and multiple-choice markets are stable.
```

Reason:

```text
payouts are continuous/proportional
rounding risk is higher
users may misunderstand payoff
testing must be stronger
```

## 18. Platform Market Creation Rules

Every market must define:

```text
market title
market description
market type
outcome set or payoff formula
payout amount
tick size
minimum quantity
maximum quantity
close time
timezone
resolution source
evidence requirements
void policy
dispute window
fee policy
jurisdiction availability
risk category
admin approver
```

Market wording must be:

```text
objective
testable
time-bound
source-bound
non-overlapping
non-misleading
```

Market wording must not depend on:

```text
private opinion
platform discretion
unverifiable events
secret information
ambiguous terminology
```

## 19. Prohibited Market Rules

Pred-Market should prohibit or require senior legal approval for markets involving:

```text
death
terrorism
assassination
war
crime
illegal activity
personal injury
named private individuals
minors
medical diagnosis of named persons
sexual content
personal financial distress
court cases where prohibited
elections where prohibited
sports/gaming where prohibited
securities/commodities where licensing is required
market manipulation targets
events controlled by a trader
```

## 20. Admin Approval Checklist

Before a market opens:

```text
1. Question is objective.
2. Outcomes are clear.
3. Outcome set is exhaustive when needed.
4. Outcomes do not overlap.
5. Boundary rules are explicit.
6. Observation time is explicit.
7. Timezone is explicit.
8. Resolution source is authoritative.
9. Void policy is explicit.
10. Dispute policy is explicit.
11. Jurisdiction/legal approval exists.
12. Market does not violate prohibited category rules.
13. Payout, tick size, and quantity limits are set.
14. Risk limit is set.
15. Admin approver is recorded.
```

## 21. Core Test Matrix Across All Markets

Universal tests:

```text
1. Market cannot open without approved status.
2. Order cannot be placed on closed market.
3. Order cannot be placed by restricted user.
4. Order cannot be placed with insufficient funds.
5. Sell order cannot exceed owned available shares.
6. Price must respect tick size.
7. Quantity must respect min/max limits.
8. Partial fills update orders correctly.
9. Cancels release locked assets.
10. Self-trade prevention works.
11. Duplicate request idempotency works.
12. Wallet cannot go negative.
13. Position cannot go negative.
14. Ledger balances for every transaction.
15. Settlement cannot double pay.
16. Oracle evidence is required.
17. Admin action is audited.
18. Void uses configured policy.
19. Dispute status blocks archive.
20. Redis outage does not corrupt source-of-truth data.
```

## 22. Rules And Regulations Operating Policy

This section defines internal operating rules. Legal counsel must convert these into jurisdiction-specific legal terms.

### 22.1 User Eligibility

Users must:

```text
be legally permitted to trade
meet minimum age requirements
pass required KYC checks
not be located in restricted jurisdictions
not be sanctioned or blocked
not use multiple accounts to evade limits
```

### 22.2 Market Integrity

Users must not:

```text
manipulate markets
self-trade to create fake volume
wash trade
use multiple accounts abusively
trade on platform-confidential information
submit fraudulent evidence
interfere with settlement sources
abuse APIs
```

### 22.3 Risk Limits

The platform should enforce:

```text
per-user order limits
per-user market exposure limits
daily deposit limits
daily withdrawal limits
market-level open interest limits
market-level loss/liability limits
category-level limits
velocity limits
```

### 22.4 KYC/AML

Required controls:

```text
identity verification when required
sanctions screening when required
transaction monitoring
suspicious activity review
source-of-funds checks for high-risk users
record retention
withdrawal holds where required
```

### 22.5 Data Protection

Required controls:

```text
collect only necessary personal data
state lawful purpose/consent basis
protect sensitive data
encrypt secrets
limit staff access
log admin access
support user rights where required
define retention periods
handle breach notifications
```

### 22.6 Responsible Trading

Recommended controls:

```text
risk warnings
deposit limits
loss limits
cool-off periods
self-exclusion
account closure
no misleading odds language
clear settlement rules
clear fee display
```

## 23. Terms And Conditions Template

This is a product template, not final legal text.

### 23.1 Acceptance

```text
By using Pred-Market, the user agrees to the platform terms, market rules, privacy policy, risk disclosures, fee schedule, and jurisdiction restrictions.
```

### 23.2 Eligibility

```text
The user must be of legal age, legally permitted to use the platform, pass required verification, and not be located in a restricted jurisdiction.
```

### 23.3 No Investment Advice

```text
Market prices are user-generated and do not represent financial, legal, tax, investment, or betting advice from the platform.
```

### 23.4 Risk Disclosure

```text
Users can lose the full amount committed to a position.
Markets may be illiquid.
Displayed probabilities are estimates based on prices.
Prices may move rapidly.
Settlement may be delayed by disputes or source issues.
Void rules may produce gains or losses compared with trade price.
```

### 23.5 Market Rules Are Binding

```text
Each market has specific rules, outcome definitions, close time, resolution source, and void policy. The user is responsible for reviewing those rules before trading.
```

### 23.6 Orders And Matching

```text
Orders are matched according to platform rules.
Limit orders may fill fully, partially, or not at all.
Open orders may be cancelled by the user before fill unless restricted by platform status or compliance action.
The platform may cancel orders during market halt, close, void, or incident response.
```

### 23.7 Settlement

```text
Settlement is based on the market's predefined resolution source and rules.
The platform may delay settlement for evidence collection, dispute review, technical issues, or compliance review.
```

### 23.8 Voids

```text
The platform may void a market according to the market's void policy if the event cannot be resolved fairly, the event is cancelled, the market was incorrectly specified, or required data is unavailable.
```

### 23.9 Prohibited Conduct

```text
Users may not manipulate markets, create false volume, self-trade abusively, use multiple accounts to evade controls, submit false information, abuse APIs, or violate applicable law.
```

### 23.10 Account Restrictions

```text
The platform may suspend, restrict, freeze, or close accounts when required by law, compliance policy, fraud controls, market integrity rules, or risk controls.
```

### 23.11 Fees

```text
All fees must be disclosed before order submission or settlement. The platform may charge trading, withdrawal, or settlement fees only as stated in the active fee schedule.
```

### 23.12 Data And Privacy

```text
The platform collects and processes user data according to the privacy policy and applicable data protection law.
```

### 23.13 Disputes

```text
Users may dispute settlement during the stated dispute window. The platform's dispute process, evidence standard, and final decision process must be documented.
```

### 23.14 Taxes

```text
Users are responsible for understanding and paying taxes applicable to their activity, unless the platform is legally required to withhold or report.
```

## 24. Implementation Priority

Recommended build order:

```text
1. Binary YES/NO market.
2. Wallet and double-entry ledger.
3. Limit orders.
4. Matching engine.
5. Positions.
6. Settlement and voids.
7. Admin resolution.
8. Multiple-choice complete-set model.
9. Range markets as multiple-choice intervals.
10. Threshold markets as binary templates.
11. Conditional markets with void-on-condition-false.
12. Combo markets with all-legs-true logic.
13. Scalar markets last.
```

Do not implement complex market types until:

```text
binary accounting is proven
settlement is idempotent
void handling is tested
admin audit trail exists
legal/compliance policy is approved
```

## 25. Final Architecture Principle

All market types should reduce to a small number of settlement primitives:

```text
1. binary winner pays
2. one-of-many winner pays
3. numeric range maps to one-of-many winner
4. threshold maps to binary winner
5. condition maps to binary winner or void
6. combo maps to binary truth table or void
7. scalar maps numeric value to payout formula
```

The safest engineering strategy:

```text
Build the accounting, collateral, order, position, and settlement engine once.
Then express each market type as a strict rule template on top of that engine.
```

## 26. Reference Sources For Compliance Planning

Reviewed reference points:

```text
CFTC - Understanding Prediction Markets and Event Contracts
CFTC - Contracts & Products, event contract references and Rule 40.11 discussion
CFTC - 2026 notice/proposal materials concerning event contracts
RBI - Master Direction: Know Your Customer Direction, 2016, updated through 2025
Reserve Bank of India KYC FAQs, June 2025
Government of India Gazette - Digital Personal Data Protection Act, 2023
MeitY - Information Technology Intermediary Guidelines and Digital Media Ethics Code Rules materials, including online gaming intermediary references
MeitY - online gaming / online money game related official materials
```
