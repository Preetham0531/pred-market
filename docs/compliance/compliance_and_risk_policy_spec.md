# Compliance And Risk Policy Spec

This document defines the Pred-Market V1 compliance and risk policy assumptions for restricted categories, prohibited markets, KYC/AML, jurisdiction controls, user eligibility, and manipulation monitoring.

This is planning documentation only. It is not legal advice. A qualified lawyer must approve any real-money launch, jurisdiction strategy, category rules, user terms, and compliance program.

## 1. Policy Goal

Pred-Market should operate as:

```text
an exchange-style prediction market platform
```

not:

```text
a sportsbook that takes directional risk
```

Compliance design goal:

```text
block markets, users, and activity that the platform is not legally or operationally ready to support
```

## 2. Regulatory Reference Points

Reference points used for planning:

```text
CFTC event contract materials and Rule 40.11
RBI KYC Master Direction
India Digital Personal Data Protection Act, 2023
MeitY intermediary and online gaming materials
official data-source licensing requirements
jurisdiction-specific gambling, derivatives, securities, commodities, payments, tax, and consumer-protection rules
```

Important official references:

```text
CFTC contracts/products event contracts:
https://www.cftc.gov/IndustryOversight/ContractsProducts/index.htm

17 CFR 40.11:
https://www.law.cornell.edu/cfr/text/17/40.11

RBI Master Direction - Know Your Customer (KYC) Direction, 2016:
https://www.rbi.org.in/commonman/english/scripts/notification.aspx?id=2607

Digital Personal Data Protection Act, 2023 Gazette:
https://egazette.gov.in/WriteReadData/2023/247847.pdf

MeitY IT Intermediary Guidelines and Digital Media Ethics Code Rules materials:
https://www.meity.gov.in/
```

These references are not a legal conclusion.

## 3. Risk Levels

Every market category and market should have a risk level:

```text
LOW
MEDIUM
HIGH
RESTRICTED
PROHIBITED
```

Risk level controls:

```text
whether market can be listed
required approval level
required legal review
automation level
source requirements
user eligibility
exposure limits
monitoring intensity
dispute workflow
```

## 4. Category Risk Defaults

Initial category risk:

```text
sports: MEDIUM, jurisdiction review required
politics: RESTRICTED
economics: MEDIUM
stocks and mutual funds: RESTRICTED
financials: HIGH
weather / climate: LOW to MEDIUM
culture: MEDIUM
tech and science: MEDIUM
mentions / public attention: HIGH
commodities: HIGH
```

Launch recommendation:

```text
start with non-real-money or test-money markets until legal review is complete
prioritize weather/climate and economics for structured automation
apply stricter review to sports, commodities, financials, stocks, politics, and mentions
```

## 5. Prohibited Market Topics

Do not list markets involving:

```text
terrorism
assassination
war
death of named people
serious injury of named people
crime commission
illegal activity
personal tragedy
medical diagnosis of named people
private individuals without approval
minors
doxxing or private data exposure
harassment targets
self-harm
court outcomes where prohibited
elections where prohibited
sports/gaming where prohibited
securities/commodities where licensing is required and not obtained
markets designed to manipulate real-world harm
```

Additional prohibited construction:

```text
ambiguous outcome source
subjective resolution
no observation time
no settlement source
impossible or contradictory outcome set
market designed around rumors only
market likely to incentivize manipulation or abuse
```

## 6. Restricted Categories

Restricted categories require legal/compliance approval before real-money listing:

```text
politics
elections
sports in jurisdictions treating the product as gaming/betting
stocks
mutual funds
securities
commodities
financial instruments
interest rates
FX
mentions/public attention
court/legal outcomes
health/medical outcomes
```

Restricted category default:

```text
admin cannot self-approve
legal review required
market rule review required
enhanced monitoring required
settlement automation capped at Level 1
```

## 7. User Eligibility

Minimum requirements before real-money trading:

```text
legal age
accepted terms
accepted risk disclosures
not in restricted jurisdiction
not suspended
KYC state sufficient for product risk
payment method approved
no sanctions/watchlist block where applicable
```

User status:

```text
ACTIVE
PENDING_REVIEW
RESTRICTED
SUSPENDED
CLOSED
```

Eligibility checks before order placement:

```text
user.status == ACTIVE
market.status == OPEN
jurisdiction allowed for market category
KYC state sufficient
wallet not frozen
market not compliance locked
```

## 8. KYC And AML Assumptions

V1 planning assumptions:

```text
test-money mode can use lightweight identity
real-money mode requires KYC/AML policy
payment provider requirements may impose additional checks
high-risk users require enhanced due diligence
source-of-funds checks may be needed for high deposits/withdrawals
records must be retained according to legal policy
```

KYC states:

```text
NOT_STARTED
BASIC_PENDING
BASIC_VERIFIED
ENHANCED_PENDING
ENHANCED_VERIFIED
REJECTED
EXPIRED
```

AML/risk triggers:

```text
large deposit
rapid deposit then withdrawal
high-frequency trading in low-liquidity markets
self-trade attempts
multi-account signals
unusual category concentration
sanctions/watchlist match if applicable
chargeback or payment failure
manual admin flag
```

## 9. Jurisdiction Controls

Every user session and order should be evaluated for jurisdiction restrictions.

Signals:

```text
declared residence
KYC country
payment instrument country
IP country
device signals if legally permitted
VPN/proxy risk signal
```

Jurisdiction controls:

```text
block real-money trading in restricted locations
block category-specific markets where required
allow view-only mode where legally permitted
record jurisdiction decision at order time
record market rule version at order time
```

If signals conflict:

```text
use most restrictive interpretation
move user to PENDING_REVIEW if needed
```

## 10. Market Approval Workflow

Required checks before listing:

```text
category risk classification
jurisdiction availability
prohibited topic screen
duplicate market detection
source validation
resolution wording review
void policy review
manipulation risk review
data licensing review
legal review where required
admin approval
audit log
```

Approval levels:

```text
LOW: admin approval
MEDIUM: admin approval plus policy checklist
HIGH: senior admin/compliance approval
RESTRICTED: legal/compliance approval required
PROHIBITED: cannot list
```

## 11. Market Integrity Monitoring

Monitor:

```text
self-trading
wash trading
multi-account trading
price manipulation attempts
spoofing or layering signals
collusive trading groups
rapid order cancellations
trading immediately before source publication
unusual volume spikes
large trades in illiquid markets
category-level concentration
admin/user relationship conflicts
```

Actions:

```text
soft alert
enhanced monitoring
market pause
user trading restriction
wallet freeze
admin review
settlement delay
regulatory report if required
```

## 12. Account Restrictions And Freezes

Restriction types:

```text
view only
no new orders
cancel only
withdrawal hold
full wallet freeze
account suspension
account closure
```

Freeze rules:

```text
must have reason
must have actor or automated trigger
must write audit log
must preserve ledger records
must not delete user financial history
must have review path
```

## 13. Data Protection

Personal data controls:

```text
collect minimum necessary data
store consent and terms acceptance
separate KYC documents from trading data where possible
encrypt sensitive data at rest
restrict admin access
log admin access to sensitive records
support user rights process where legally required
define retention schedule
define breach response process
```

Do not expose:

```text
KYC data in normal admin tables
payment details beyond masked display
private user identifiers in public market data
precise user location
```

## 14. Risk Disclosures

Users should see clear disclosures:

```text
contracts can lose full cost
prices are not guarantees
markets may be illiquid
orders may fill partially or not at all
settlement depends on predefined source/rules
markets can be paused, voided, or disputed
withdrawals may be delayed by compliance review
```

Avoid promotional claims:

```text
guaranteed profit
safe returns
investment advice
sure outcome
risk-free trading
```

## 15. Admin And Maker-Checker Controls

Maker-checker required for:

```text
market approval in high/restricted categories
resolution approval
void decision
manual wallet adjustment
user freeze above threshold
source substitution
settlement retry after failure
```

Rules:

```text
maker and checker cannot be same user
reason is required
before/after state must be logged
evidence must be linked
```

## 16. Incident Response

Incident types:

```text
wrong market wording
wrong source
oracle outage
market manipulation
ledger mismatch
settlement error
data breach
payment provider issue
admin mistake
jurisdiction block failure
```

Incident workflow:

```text
detect
pause affected market/user action
preserve logs and evidence
assign owner
assess financial impact
decide correction/void/settlement delay
communicate to users if needed
write post-incident record
update controls
```

## 17. Audit Requirements

Audit logs required for:

```text
market creation
market approval/rejection
market pause/reopen
source changes
rule changes
resolution proposal
resolution approval
settlement execution
void decision
manual wallet adjustment
user restriction/freeze
admin sensitive data access
compliance override
```

Audit record:

```text
actor_user_id
actor_type
action
entity_type
entity_id
before_state
after_state
reason
request_id
created_at
```

## 18. Launch Gates

No real-money launch until:

```text
legal review completed
jurisdiction matrix approved
category matrix approved
KYC/AML policy approved
payment provider approval completed
data protection policy approved
terms and risk disclosures approved
market manipulation policy approved
dispute and void policy approved
tax/reporting review completed
records retention policy approved
incident response process tested
```

## 19. Required Tests And Controls

Required compliance tests:

```text
restricted user cannot trade
restricted jurisdiction cannot trade
restricted category blocks order
prohibited market cannot be approved
admin self-approval is rejected
market approval writes audit log
resolution approval writes audit log
manual adjustment requires reason
frozen wallet cannot withdraw
cancel-only restriction allows cancellation but blocks new orders
self-trade attempt is blocked or flagged
large suspicious activity creates alert
```

## 20. Default Policy Until Legal Approval

Until legal review is complete:

```text
frontend and backend should be treated as prototype/test environment
no production real-money trading
no public promise that categories are legally available
no direct user-created real-money market listing
no automated settlement without human checker
no restricted category launch
```

