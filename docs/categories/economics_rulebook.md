# Economics Category Rulebook

This document defines the V1 rulebook for economics prediction markets.

This is planning documentation only. It is not legal advice. Economics markets can resemble financial, derivatives, or regulated event contracts in some jurisdictions and require legal review before real-money launch.

## 1. Category Status

Recommended V1 status:

```text
MEDIUM risk
Level 1 automation for market creation
Level 2 automation for release calendar ingestion, source polling, and candidate settlement
manual admin approval before listing
manual maker-checker approval before settlement
```

Economics is a good early category because official sources and release calendars often exist.

## 2. Allowed Market Types

Recommended first market types:

```text
threshold
range
binary YES/NO
multiple-choice for policy decision outcomes
```

Avoid initially:

```text
complex multi-indicator formulas
markets based only on forecasts
markets requiring proprietary licensed data without contract
markets where preliminary and final values are ambiguous
```

## 3. Approved Source Hierarchy

Primary source:

```text
official government statistical agency
central bank
official ministry release
```

India source examples:

```text
MoSPI for CPI, IIP, GDP and official statistical releases
RBI for monetary policy, rates, banking and financial stability releases
PIB only when it republishes or summarizes official government releases and market rule permits it
```

Reference examples:

```text
MoSPI CPI: https://www.mospi.gov.in/themes/product/9-consumer-price-index-cpi
MoSPI home: https://www.mospi.gov.in/
RBI press releases: https://rbi.org.in/Scripts/BS_PressreleaseDisplay.aspx
```

Fallback source:

```text
approved archival mirror or licensed data vendor
```

Fallback may be used only if the market rule names it before market opens.

## 4. Supported Subcategories

Initial subcategories:

```text
inflation
GDP
industrial production
unemployment/labour statistics
central bank policy rates
currency reserves
fiscal releases
```

Each subcategory must define:

```text
source agency
release calendar
data table or release title
unit
scale
rounding
revision policy
observation period
publication timestamp policy
```

## 5. Market Templates

### CPI Threshold

Template:

```text
Will [official CPI inflation value] be above [threshold] for [period]?
```

Resolution:

```text
YES if official value > threshold
NO if official value <= threshold
```

Equality rule:

```text
above means >
at or above means >=
below means <
at or below means <=
```

### Economic Range

Template:

```text
What range will [indicator] fall into for [period]?
```

Ranges:

```text
gapless
non-overlapping
boundary inclusivity explicit
```

### Policy Decision

Template:

```text
What will [central bank body] decide for [meeting date]?
```

Outcomes:

```text
raise
hold
cut
other if required
```

Resolution:

```text
official policy statement decides outcome
```

## 6. Market Wording Rules

Every economics market must define:

```text
indicator name
official source
release period
release date or meeting date
unit
scale
threshold or ranges
preliminary vs final policy
revision policy
timezone
fallback source if any
void policy
```

Bad wording:

```text
Will inflation be high?
Will the economy do well?
Will RBI surprise markets?
```

Good wording:

```text
Will the official all-India CPI year-on-year inflation rate for May 2026 published by MoSPI be greater than 4.0%?
```

## 7. Close Time Rules

Recommended:

```text
close before official scheduled release time
```

If no exact time exists:

```text
close at 00:00 local date of release or earlier conservative cutoff
```

Do not keep market open after:

```text
official release is published
embargo lifts
central bank decision is announced
credible official data leak is confirmed by admin policy
```

## 8. Settlement Rules

Settlement requires:

```text
official release captured
raw value stored
normalized value stored
source timestamp stored
ingestion timestamp stored
admin resolver
checker approval
```

Preliminary vs final:

```text
default V1: use first official release unless market explicitly says final revised value
```

Revision policy:

```text
ignore later revisions after settlement unless market explicitly references revised/final data
```

## 9. Void Policy

Default void triggers:

```text
official source permanently unavailable
indicator discontinued before release
methodology change makes market wording invalid
release cancelled without replacement
market wording references wrong period/source
value cannot be mapped because unit/scale was omitted
```

Do not void merely because:

```text
value is surprising
value is revised after settlement
market participants expected another source
```

Default refund:

```text
refund original matched cost
release open order locks
no fees initially
```

## 10. Edge Cases

Required handling:

```text
release delayed
release cancelled
preliminary value later revised
source republishes corrected PDF
data table differs from press summary
unit mismatch
seasonally adjusted vs unadjusted value
period mismatch
timezone ambiguity
source website outage
```

## 11. Automation Level

Allowed automation:

```text
release calendar ingestion
source polling
PDF/page evidence capture
numeric extraction candidate
threshold/range candidate calculation
stale data alerts
analytics rollups
notifications
```

Human approval required:

```text
market approval
source approval
final settlement
source substitution
void decision
dispute resolution
methodology-change decision
```

## 12. Required Tests

Test cases:

```text
market rejects missing source
market rejects missing period
threshold equality resolves correctly
range boundary maps correctly
wrong unit is rejected
preliminary value settles when rule says first release
revision ignored after final settlement by default
source outage moves market to pending resolution
methodology change requires admin review
settlement is idempotent
void refund is idempotent
```

