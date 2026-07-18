# Sports Category Rulebook

This document defines the V1 rulebook for sports prediction markets.

This is planning documentation only. It is not legal advice. Sports-related real-money contracts may be restricted or prohibited in some jurisdictions and must be legally reviewed before launch.

## 1. Category Status

Recommended V1 status:

```text
MEDIUM risk
Level 1 automation for market creation
Level 2 automation for event data ingestion and close scheduling
manual admin approval before listing
manual maker-checker approval before settlement
```

Sports can be operationally structured because official schedules and results often exist, but legal treatment may vary sharply by jurisdiction.

## 2. Allowed Market Types

Recommended first sports market types:

```text
binary YES/NO
threshold
multiple-choice tournament winner
range totals
combo only after binary correctness is proven
```

Avoid initially:

```text
player injury markets
disciplinary markets
medical/private-life markets
markets involving minors
markets that encourage harassment
markets based on unofficial rumors
```

## 3. Approved Source Hierarchy

Primary source preference:

```text
official league, federation, tournament, or governing body result page
```

Examples of source categories:

```text
ICC official fixtures/results for international cricket
BCCI official results for Indian cricket
FIFA or official competition site for football
Olympics official results for Olympic events
official league match center for domestic leagues
```

Fallback source:

```text
licensed sports data vendor approved by legal and data licensing review
```

Do not use:

```text
social media rumors
fan pages
unofficial score aggregators as sole settlement source
news articles unless source policy explicitly allows them
```

Reference examples:

```text
ICC fixtures/results: https://www.icc-cricket.com/fixtures-results
BCCI: https://www.bcci.tv/
Olympic results: https://www.olympics.com/en/olympic-games/olympic-results
```

## 4. Supported Sports Subcategories

Initial subcategories:

```text
cricket
football
tennis
motorsport
Olympic sports
tournament outrights
team season standings
```

Each subcategory needs:

```text
official source list
postponement policy
abandonment policy
tie/draw policy
walkover policy
settlement timing
```

## 5. Market Templates

### Match Winner

Template:

```text
Will [Team A] beat [Team B] in [match/event]?
```

Resolution:

```text
YES if Team A is official winner.
NO if Team A is not official winner.
VOID if the match is abandoned without official winner and void policy applies.
```

### Tournament Winner

Template:

```text
Who will win [tournament]?
```

Outcomes:

```text
listed teams/players
Other if exhaustive coverage requires it
```

Resolution:

```text
official tournament winner resolves winning outcome
```

### Points/Runs/Goals Threshold

Template:

```text
Will total [runs/goals/points] be above [threshold] in [match]?
```

Resolution:

```text
YES if official total > threshold
NO if official total <= threshold
```

Equality rule must be explicit.

### Range Total

Template:

```text
What range will total [runs/goals/points] fall into?
```

Ranges:

```text
non-overlapping
gapless
boundary inclusivity explicit
```

## 6. Market Wording Rules

Every sports market must define:

```text
event name
teams/players
competition
scheduled date/time
official source
close time
settlement statistic
tie/draw rule
postponement rule
abandonment rule
void policy
```

Bad wording:

```text
Will India perform well?
Will the match be exciting?
Will Player X dominate?
```

Good wording:

```text
Will India be declared the winner of the final by the official tournament source?
```

## 7. Close Time Rules

Recommended:

```text
close before scheduled match/event start
```

Do not allow trading after:

```text
official start
toss if toss changes market information materially
lineups if lineups materially affect the market and rules require earlier close
```

If event start changes:

```text
system may update close time before market closes
admin audit required
users must see updated close time
```

## 8. Settlement Rules

Settlement requires:

```text
official result
captured evidence
admin resolver
checker approval
settlement job
audit log
```

Settlement timing:

```text
wait until official result is final under market rules
do not settle from live score alone unless official source confirms final
```

Late correction policy:

```text
follow predefined market rule
default V1: ignore corrections after settlement finalization unless incident policy is triggered
```

## 9. Void Policy

Default void triggers:

```text
event cancelled and not rescheduled within defined window
event abandoned without official result
official source permanently unavailable and no backup source exists
market wording error makes settlement impossible
material participant identity error
```

Do not void merely because:

```text
market price moved sharply
popular team lost
result was unexpected
users misunderstood the market
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
draw/tie
super over or extra time
penalty shootout
walkover
disqualification
rain interruption
abandoned match
postponed match
venue change
team renamed
player withdrawal
incorrect official score later corrected
official source outage
```

## 11. Automation Level

Allowed automation:

```text
event calendar ingestion
duplicate market detection
scheduled close
official result polling
candidate settlement calculation
market analytics rollups
notifications
```

Human approval required:

```text
market approval
source approval
settlement approval
void decision
dispute resolution
legal/compliance exception
```

## 12. Required Tests

Test cases:

```text
market cannot open without official source
close time must be before event start
match winner resolves YES correctly
match winner resolves NO correctly
draw follows explicit rule
postponement follows defined window
abandoned match voids when no official result exists
official result evidence is stored
duplicate market is flagged
settlement is idempotent
void refund is idempotent
```

