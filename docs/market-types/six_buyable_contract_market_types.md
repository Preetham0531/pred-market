# Six Buyable Contract Market Types

This document defines the six contract market types Pred-Market V1 can expose as buyable user-facing products.

The six types are:

```text
1. Binary YES/NO
2. Multiple-choice
3. Range
4. Threshold
5. Conditional
6. Combo / parlay-style
```

Scalar markets are intentionally excluded from this V1 buyable set. They require formula-based variable payouts instead of a single winning contract payout, so they should be treated as a later specialized payoff model.

## 1. Shared Product Rule

Pred-Market remains an exchange-style marketplace:

```text
Users buy contracts from other users.
The platform matches compatible orders.
The platform does not take directional risk.
Every fill is fully collateralized.
```

The default V1 constraints are:

```text
limit orders only
no market orders
no naked shorting
no leverage
no platform directional exposure
integer minor units only
admin-controlled resolution
maker-checker settlement approval
idempotent settlement
full audit trail
```

## 2. Shared Contract Shape

Every buyable contract type should be represented by a market plus one or more outcome contracts.

Required market fields:

```text
id
market_type
title
description
status
payout_amount_minor
currency
tick_size_minor
min_quantity
max_quantity
open_time
close_time
observation_time
timezone
resolution_source
resolution_rule
void_policy
dispute_window_seconds
created_by_admin_id
approved_by_admin_id
created_at
updated_at
```

Required outcome contract fields:

```text
id
market_id
code
label
description
display_order
status
metadata_json
created_at
updated_at
```

`metadata_json` stores type-specific parameters such as range boundaries, threshold operators, condition legs, or combo legs.

## 3. Shared Order Model

V1 order actions:

```text
BUY
SELL
CANCEL
```

For binary-style complementary markets, early V1 can support:

```text
BUY_YES
BUY_NO
CANCEL
```

For multi-outcome share markets:

```text
LIMIT_BUY outcome_id
LIMIT_SELL outcome_id
CANCEL
```

Shared order fields:

```text
id
user_id
market_id
outcome_id
side
price_minor
quantity
filled_quantity
remaining_quantity
status
time_in_force
created_at
updated_at
```

Shared validation:

```text
market.status == OPEN
outcome.status == ACTIVE
price_minor > 0
price_minor <= payout_amount_minor
price_minor respects tick_size_minor
quantity >= min_quantity
quantity <= max_quantity
buy orders lock cash
sell orders lock owned shares
orders after close are rejected
self-trade is blocked or explicitly handled by policy
```

## 4. Type 1: Binary YES/NO

Definition:

```text
A market with exactly two complementary outcomes: YES and NO.
```

Example:

```text
Will BTC/USD be above $100,000 at 23:59:59 UTC on Dec 31, 2026?
```

Outcome contracts:

```text
YES pays P if the condition is true.
NO pays P if the condition is false.
```

Buyable contract setup:

```text
market_type = BINARY
outcomes = YES, NO
payout = fixed amount, such as 10000 paise
```

Core invariant:

```text
YES price + NO price = payout
```

V1 matching:

```text
incoming BUY_YES @ Y matches resting BUY_NO @ P - Y
incoming BUY_NO @ N matches resting BUY_YES @ P - N
```

Settlement:

```text
YES result -> YES holders receive payout, NO holders receive zero
NO result -> NO holders receive payout, YES holders receive zero
VOID -> refund by void policy
```

Must-have tests:

```text
YES @ 40 matches NO @ 60 when payout is 100
YES @ 40 does not match NO @ 50
filled quantity cannot exceed order quantity
closed markets reject orders
settlement is idempotent
```

## 5. Type 2: Multiple-Choice

Definition:

```text
A market with more than two mutually exclusive and collectively exhaustive outcomes where exactly one outcome wins.
```

Example:

```text
Who will win the tournament?

India
Australia
England
Other
```

Buyable contract setup:

```text
market_type = MULTIPLE_CHOICE
one outcome contract per answer
exactly one outcome resolves winning
```

Core invariant for a complete set:

```text
sum(all outcome prices) = payout
```

V1 collateral model:

```text
Complete sets can be minted by locking one payout amount.
One complete set creates one share of every outcome.
Users can sell only outcome shares they own.
```

V1 matching:

```text
Each outcome has its own order book.
BUY outcome shares match SELL orders for the same outcome.
SELL requires owned unlocked shares.
```

Settlement:

```text
winning outcome holders receive payout
all other outcome holders receive zero
VOID refunds according to void policy
```

Must-have tests:

```text
duplicate outcomes are rejected
overlapping outcomes are rejected
missing exhaustive bucket is rejected
complete set mint creates equal shares for all outcomes
user cannot sell more shares than owned
settlement pays only the winning outcome
```

## 6. Type 3: Range

Definition:

```text
A numeric multiple-choice market where each outcome is a non-overlapping interval.
```

Example:

```text
What will CPI be?

V < 2.0%
2.0% <= V < 3.0%
3.0% <= V < 4.0%
V >= 4.0%
```

Buyable contract setup:

```text
market_type = RANGE
one outcome contract per interval
metadata_json stores lower bound, upper bound, and inclusivity
```

Required metadata per outcome:

```text
lower_value
upper_value
lower_inclusive
upper_inclusive
unit
scale
```

Validation:

```text
ranges must not overlap
ranges must not have gaps
boundary inclusivity must map every possible value to exactly one outcome
source, unit, rounding, and observation time must be explicit
```

V1 matching:

```text
Same as multiple-choice: one order book per range outcome.
```

Settlement:

```text
capture final numeric value
normalize using configured scale and rounding
map value to exactly one range
pay that range outcome
```

Must-have tests:

```text
exact lower boundary maps correctly
exact upper boundary maps correctly
overlap is rejected
gap is rejected
out-of-range value is impossible when catch-all ranges exist
source unavailable blocks settlement or voids by policy
```

## 7. Type 4: Threshold

Definition:

```text
A binary market where settlement depends on comparing a numeric observed value to a cutoff.
```

Example:

```text
Will BTC/USD be above $100,000 at the observation time?
```

Buyable contract setup:

```text
market_type = THRESHOLD
outcomes = YES, NO
metadata_json stores threshold value and comparison operator
```

Required metadata:

```text
observed_value_name
threshold_value
operator
unit
scale
source
observation_time
rounding_policy
```

Supported operators:

```text
>
>=
<
<=
```

V1 matching:

```text
Same as binary YES/NO complementary matching.
```

Settlement:

```text
evaluate observed value against threshold
true -> YES wins
false -> NO wins
```

Important wording rule:

```text
"above" means >
"at or above" means >=
"below" means <
"at or below" means <=
```

Must-have tests:

```text
equality resolves correctly for each operator
wrong unit is rejected
missing source value blocks settlement
timezone is respected
oracle evidence is stored
settlement is idempotent
```

## 8. Type 5: Conditional

Definition:

```text
A market where a condition must happen before the main YES/NO question can settle.
```

Example:

```text
If Team A reaches the final, will Team A win the final?
```

Buyable contract setup:

```text
market_type = CONDITIONAL
outcomes = YES, NO
metadata_json stores condition rule and main question rule
```

Required metadata:

```text
condition_description
condition_source
condition_observation_time
question_description
question_source
question_observation_time
failed_condition_policy
```

Recommended V1 failed condition policy:

```text
If condition is false, void the market.
```

V1 matching:

```text
Same as binary YES/NO complementary matching.
```

Settlement:

```text
condition false -> VOID
condition true and question true -> YES wins
condition true and question false -> NO wins
condition unknown -> remain PENDING_RESOLUTION
```

Must-have tests:

```text
false condition voids market
true condition plus true question resolves YES
true condition plus false question resolves NO
unknown condition blocks settlement
condition evidence and question evidence are stored separately
admin cannot resolve main question before condition evaluation
```

## 9. Type 6: Combo / Parlay-Style

Definition:

```text
A market combining two or more legs into one all-or-nothing contract.
```

Example:

```text
Will both India win the match and total runs exceed 300?
```

Buyable contract setup:

```text
market_type = COMBO
outcomes = YES, NO
metadata_json stores all legs and the combo operator
```

Required metadata:

```text
legs[]
legs[].description
legs[].source
legs[].observation_time
legs[].truth_rule
combo_operator
leg_void_policy
```

Recommended V1 operator:

```text
ALL
```

Truth table for `ALL`:

```text
all legs true -> YES wins
one or more legs false -> NO wins
one or more legs unknown -> remain PENDING_RESOLUTION
one or more legs void -> VOID under V1 policy
```

V1 matching:

```text
Same as binary YES/NO complementary matching.
```

Validation:

```text
duplicate legs are rejected
conflicting legs are rejected
impossible combos are rejected
each leg has its own objective source and observation time
```

Settlement:

```text
resolve every leg
apply combo operator
settle YES, NO, or VOID
store evidence for every leg
```

Must-have tests:

```text
all true resolves YES
any false resolves NO
any unknown blocks settlement
any void voids whole market under V1 policy
duplicate legs are rejected
impossible combo is rejected
settlement is idempotent
```

## 10. Recommended Build Order

Build the six types in this order:

```text
1. Binary YES/NO
2. Threshold
3. Multiple-choice
4. Range
5. Conditional
6. Combo / parlay-style
```

Reason:

```text
Threshold reuses binary mechanics.
Range reuses multiple-choice mechanics.
Conditional reuses binary mechanics plus a condition gate.
Combo reuses binary mechanics plus a multi-leg truth evaluator.
```

## 11. Minimal Backend Modules

The first backend implementation should isolate these modules:

```text
wallet
ledger
markets
outcomes
orders
matching
positions
collateral
resolution
settlement
audit
```

The market type logic should live behind two interfaces:

```text
validate_market_definition(market, outcomes)
resolve_market(market, evidence) -> YES | NO | outcome_id | VOID | PENDING
```

Matching should not know detailed market wording. It should only know:

```text
market_type
payout_amount_minor
outcome_id
side
price_minor
quantity
owned shares
locked cash
```

## 12. Non-Negotiable Invariants

Implementation must enforce:

```text
wallet balances never go negative
positions never go negative
orders never fill after close
filled quantity never exceeds order quantity
cash is locked before buy fills
shares are locked before sell fills
every fill writes balanced ledger entries
settlement pays no more than available collateral
settlement can be retried without double payment
admin resolution is audited
market rule version is recorded before first order
```

