# Commodities Category Rulebook

This document defines the V1 rulebook for commodities prediction markets.

This is planning documentation only. It is not legal advice. Commodity-linked markets may be regulated as derivatives, gaming, or financial products depending on jurisdiction and structure. Legal and data licensing review is required before real-money launch.

## 1. Category Status

Recommended V1 status:

```text
HIGH risk
Level 1 automation for market creation
Level 2 automation for source polling and analytics only
manual admin approval before listing
manual maker-checker approval before settlement
legal review required before launch
```

Commodities have clear price sources but higher regulatory and market-data licensing risk.

## 2. Allowed Market Types

Recommended first market types:

```text
threshold
range
binary YES/NO
```

Avoid initially:

```text
leveraged products
margin-like exposure
physical delivery references
complex spread contracts
multi-leg futures strategies
markets that mimic unlicensed derivatives too closely
```

## 3. Approved Source Hierarchy

Primary source:

```text
approved exchange settlement price
official benchmark administrator
licensed market data vendor
```

India source examples:

```text
MCX for listed Indian commodity derivatives information
NSE commodity derivatives where relevant
approved benchmark/vendor feed for global commodities
```

Reference examples:

```text
MCX: https://www.mcxindia.com/
NSE commodity derivatives: https://www.nseindia.com/market-data/commodity-derivatives
```

Do not use:

```text
broker app screenshots
unlicensed scraped price pages
social media price posts
unverified OTC quotes
```

## 4. Supported Subcategories

Initial subcategories:

```text
gold
silver
crude oil
natural gas
base metals
agricultural commodities only after source review
inventory reports only after source review
```

Each subcategory must define:

```text
exchange or benchmark
contract month or spot benchmark
settlement price vs close price
currency
unit
trading calendar
holiday policy
correction policy
data license status
```

## 5. Market Templates

### Price Threshold

Template:

```text
Will [commodity benchmark/contract] settle above [price] on [date]?
```

Resolution:

```text
YES if official settlement price > threshold
NO if official settlement price <= threshold
```

Must define:

```text
commodity
contract month or benchmark
exchange/source
settlement date
settlement price field
currency
unit
```

### Price Range

Template:

```text
What range will [commodity benchmark/contract] settlement price fall into on [date]?
```

Ranges:

```text
non-overlapping
gapless
currency/unit explicit
boundary inclusivity explicit
```

## 6. Market Wording Rules

Every commodities market must define:

```text
commodity
instrument or benchmark
contract month if futures
source/exchange
price field
settlement date
currency
unit
threshold or ranges
holiday policy
trading halt policy
correction policy
void policy
```

Bad wording:

```text
Will gold go up?
Will oil be expensive?
Will commodities rally?
```

Good wording:

```text
Will the official settlement price of [defined gold contract] on [exchange] for [contract month] be greater than [price] on [date]?
```

## 7. Close Time Rules

Recommended:

```text
close before relevant trading session starts on settlement date
```

Conservative alternative:

```text
close at end of prior trading day
```

Do not allow trading after:

```text
settlement price publication
trading halt that materially affects price discovery unless policy allows continued trading
```

## 8. Settlement Rules

Settlement requires:

```text
official settlement price captured
source page/vendor response archived
contract identifier verified
currency/unit verified
raw price stored
normalized price stored
admin resolver
checker approval
```

Correction policy:

```text
default V1: use official settlement price published by approved source at defined settlement time
if official correction occurs before settlement, use corrected value
if official correction occurs after settlement, follow incident policy only
```

## 9. Void Policy

Default void triggers:

```text
source unavailable and no backup exists
contract delisted before settlement
trading halted and no official settlement price is published
instrument specification changes materially
contract month was incorrectly defined
currency/unit ambiguity prevents settlement
data license issue prevents legal use of source
```

Do not void merely because:

```text
market was volatile
threshold was crossed intraday but settlement price differs
users expected spot price while market specified settlement price
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
holiday
early close
trading halt
limit up/down
contract expiry
contract rollover
negative price possibility for some commodities
currency conversion
unit conversion
official price correction
vendor outage
exchange outage
```

## 11. Automation Level

Allowed automation:

```text
instrument metadata validation
trading calendar ingestion
source polling
candidate price extraction
threshold/range candidate calculation
evidence capture
stale source alerts
analytics rollups
notifications
```

Human approval required:

```text
market approval
source/license approval
settlement approval
source substitution
void decision
dispute resolution
regulatory exception
```

## 12. Required Tests

Test cases:

```text
market rejects missing exchange/source
market rejects missing contract month when required
market rejects missing currency/unit
threshold equality resolves correctly
range boundary maps correctly
holiday uses defined policy
trading halt without settlement price follows void policy
official correction before settlement is handled
settlement is idempotent
void refund is idempotent
```

