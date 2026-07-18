# Settlement And Resolution Spec

This document defines Pred-Market V1 market close, oracle evidence, resolution, maker-checker approval, voids, disputes, retries, admin override, and payout calculations.

This is planning documentation only. It does not create backend code or database migrations.

## 1. Settlement Goal

Settlement must be:

```text
objective
auditable
idempotent
fully collateralized
based on predefined market rules
approved through maker-checker workflow
safe under retry
```

Settlement must never:

```text
pay more than collateral
pay losing outcomes
depend on platform profit
change market rules after trading
double-credit repeated retries
hide admin override
```

## 2. Market Lifecycle

Supported statuses:

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

Settlement-related transitions:

```text
OPEN -> CLOSED
CLOSED -> PENDING_RESOLUTION
PENDING_RESOLUTION -> RESOLVED
PENDING_RESOLUTION -> VOIDED
PENDING_RESOLUTION -> DISPUTED
DISPUTED -> RESOLVED
DISPUTED -> VOIDED
RESOLVED -> ARCHIVED
VOIDED -> ARCHIVED
```

No trading allowed in:

```text
CLOSED
PENDING_RESOLUTION
DISPUTED
RESOLVED
VOIDED
ARCHIVED
```

## 3. Market Close

Market close can be triggered by:

```text
scheduled close job
admin close action
incident response
compliance action
```

Standard close flow:

```text
1. Lock market row.
2. Validate market.status is OPEN or PAUSED.
3. Set market.status = CLOSED.
4. Cancel all open and partially filled orders.
5. Release unfilled locked cash and locked shares.
6. Write ORDER_RELEASE ledger transactions.
7. Create audit log.
8. Publish market.closed event.
9. Queue evidence capture or resolution candidate job.
```

Close idempotency:

```text
calling close again returns current CLOSED/PENDING/RESOLVED/VOIDED state
no second order release occurs
```

## 4. Oracle Evidence

Oracle evidence is any source material used to determine outcome.

Evidence record must include:

```text
market_id
source_name
source_url
captured_value
captured_at
raw_payload_json
evidence_hash
created_by_user_id or system actor
created_at
```

Evidence capture rules:

```text
capture raw source response where legally allowed
store normalized value separately
store source timestamp and ingestion timestamp separately
never overwrite evidence
new evidence creates new record
```

Evidence source order:

```text
primary source
predefined backup source
manual admin evidence only if policy allows
```

## 5. Candidate Resolution

Automation may calculate candidate result.

Candidate outputs:

```text
YES
NO
outcome_id
VOID
PENDING
```

Candidate resolution does not settle market.

Candidate flow:

```text
1. Load market rule version.
2. Load approved evidence.
3. Apply market type resolver.
4. Store candidate result and reasoning.
5. Send to admin resolver queue.
```

Candidate result should include:

```text
result
confidence
normalized_value
rule_version
evidence_id
reason
warnings
```

## 6. Maker-Checker Approval

Maker:

```text
admin user who proposes resolution
```

Checker:

```text
different admin/checker user who approves resolution
```

Rules:

```text
maker_user_id != checker_user_id
maker must provide reason
checker must review evidence
approval writes audit log
approval freezes resolution for settlement
```

Resolution proposal statuses:

```text
PENDING
APPROVED
REJECTED
SUPERSEDED
```

Settlement can start only when:

```text
resolution_proposal.status == APPROVED
```

## 7. Resolution By Market Type

### Binary

Outputs:

```text
YES
NO
VOID
PENDING
```

YES wins:

```text
YES holders receive payout * quantity
NO holders receive zero
```

NO wins:

```text
NO holders receive payout * quantity
YES holders receive zero
```

### Threshold

Formula:

```text
observed_value operator threshold_value
true -> YES
false -> NO
```

Operator rules:

```text
above -> >
at or above -> >=
below -> <
at or below -> <=
```

### Multiple-Choice

Output:

```text
winning outcome_id
```

Settlement:

```text
winning outcome holders receive payout * quantity
all other outcome holders receive zero
```

### Range

Formula:

```text
map observed numeric value to exactly one range outcome
```

If value maps to zero or multiple outcomes:

```text
block settlement and require admin review
```

### Conditional

Recommended V1 policy:

```text
condition false -> VOID
condition true and question true -> YES
condition true and question false -> NO
condition unknown -> PENDING
```

### Combo

Recommended V1 operator:

```text
ALL
```

Truth table:

```text
all legs true -> YES
any leg false -> NO
any leg unknown -> PENDING
any leg void -> VOID
```

## 8. Payout Calculations

Binary payout:

```text
payout_minor = market.payout_amount_minor * winning_position.quantity
```

Multiple-choice payout:

```text
payout_minor = market.payout_amount_minor * winning_outcome_position.quantity
```

Void refund:

```text
refund_minor = original_matched_cost_minor
```

Total payout validation:

```text
sum(settlement_items.amount_minor) <= available_market_collateral_minor
```

No fees initially:

```text
fee_minor = 0
```

If fees are later introduced:

```text
fee policy must be included in market rule version before order placement
```

## 9. Settlement Execution

Settlement flow:

```text
1. Receive settlement command with idempotency key.
2. Validate approved resolution exists.
3. Begin transaction.
4. Lock market row.
5. Lock settlement row or create one.
6. Validate settlement not already complete.
7. Cancel any remaining open orders.
8. Lock collateral pool row.
9. Load affected positions.
10. Calculate settlement items.
11. Validate total payout/refund <= collateral.
12. Lock user wallet rows in deterministic order.
13. Credit user available balances.
14. Debit market collateral ledger account.
15. Credit user available cash ledger accounts.
16. Mark settlement items complete.
17. Mark positions SETTLED or VOIDED.
18. Mark market RESOLVED or VOIDED.
19. Commit.
20. Publish settlement events.
```

Post-commit:

```text
notify users
update analytics
archive after dispute window
```

## 10. Idempotency And Retries

Settlement idempotency key:

```text
settlement:{market_id}:{resolution_proposal_id}
```

Retry behavior:

```text
if settlement COMPLETE -> return existing result
if settlement PROCESSING and stale -> admin review required
if settlement FAILED before ledger commit -> retry allowed
if partial commit uncertainty exists -> block and require reconciliation
```

Settlement item uniqueness:

```text
UNIQUE(settlement_id, user_id, position_id, item_type)
```

This prevents double payout for same position in same settlement.

## 11. Void Handling

Default V1 void policy:

```text
refund original matched cost
release open order locks
no fees initially
```

Void triggers:

```text
source unavailable and no backup
market wording impossible
event cancelled under rule
condition false for conditional market
combo leg void under V1 policy
range cannot map observed value
admin/legal/compliance void decision
```

Void flow:

```text
1. Approved VOID resolution proposal exists.
2. Cancel open orders.
3. Release unfilled locks.
4. Calculate original matched cost per holder.
5. Validate refund <= collateral.
6. Credit users.
7. Mark positions VOIDED.
8. Mark market VOIDED.
9. Write audit and ledger entries.
```

## 12. Disputes

Dispute can be opened by:

```text
admin
compliance
system anomaly
eligible user during dispute window if product supports it
```

Dispute statuses:

```text
OPEN
UNDER_REVIEW
RESOLVED
REJECTED
ESCALATED
```

Dispute effects:

```text
market.status = DISPUTED
settlement blocked if not complete
withdrawals of disputed settlement credits may be held if policy requires
additional evidence can be attached
final decision requires maker-checker approval
```

Default V1:

```text
settlement approval should happen after evidence review
post-settlement disputes require incident process, not automatic reversal
```

## 13. Admin Override

Admin override is high-risk.

Allowed only for:

```text
source outage
source correction before settlement
market wording error
compliance/legal action
incident response
technical data extraction failure
```

Required fields:

```text
admin_user_id
checker_user_id
override_type
reason
evidence_ids
before_state
after_state
created_at
```

Rules:

```text
maker-checker required
audit log required
cannot override to benefit platform PnL
cannot override after settlement without incident workflow
```

## 14. Reconciliation

Before settlement:

```text
market closed
no open orders remain
open order locks released
collateral pool matches ledger
positions are non-negative
winning liability <= collateral
approved resolution exists
```

After settlement:

```text
settlement_items total equals settlement total
wallet credits equal ledger credits
collateral debit equals user credits/refunds
positions marked final
market marked final
analytics updated or queued
```

If reconciliation fails:

```text
block settlement
mark settlement FAILED
alert operations
require admin review
do not auto-adjust silently
```

## 15. Events

Publish after commit:

```text
market.closed
orders.cancelled_for_close
evidence.captured
resolution.proposed
resolution.approved
settlement.started
settlement.completed
settlement.failed
market.resolved
market.voided
dispute.opened
```

Private user events:

```text
position.settled
wallet.settlement_credit
wallet.void_refund
notification.created
```

## 16. Required Tests

Market close tests:

```text
close blocks new orders
close cancels open orders
close releases buy locks
close releases sell locks
close is idempotent
```

Resolution tests:

```text
binary YES resolves YES holders
binary NO resolves NO holders
threshold equality follows operator
range maps boundary correctly
conditional false voids
combo any false resolves NO
combo any void voids
maker cannot approve own proposal
resolution requires evidence
```

Settlement tests:

```text
payout credits winners only
losers receive zero
void refunds original matched cost
settlement cannot exceed collateral
duplicate settlement does not double credit
failed pre-commit settlement can retry
post-commit uncertainty blocks auto-retry
ledger balances after settlement
wallet reconciliation passes
positions become SETTLED or VOIDED
```

Dispute/admin tests:

```text
disputed market blocks settlement
admin override requires checker
override writes audit log
source substitution records reason
void decision requires maker-checker
```

## 17. Out Of Scope For V1

Do not implement initially:

```text
automatic real-money settlement without checker approval
settlement reversal after finalization
partial combo repricing after void leg
fee deduction
tax withholding
cross-market net settlement
external arbitration workflow
```

