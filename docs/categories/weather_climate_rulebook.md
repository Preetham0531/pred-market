# Weather And Climate Category Rulebook

This document defines the V1 rulebook for weather and climate prediction markets.

This is planning documentation only. It is not legal advice. Weather and climate markets may still require market-category and jurisdiction review before real-money launch.

## 1. Category Status

Recommended V1 status:

```text
LOW to MEDIUM risk
Level 1 automation for market creation
Level 2 automation for station/source polling, close scheduling, and candidate settlement
manual admin approval before listing
manual maker-checker approval before settlement
```

Weather is a strong early automation category because official agencies often publish structured observations and forecasts.

## 2. Allowed Market Types

Recommended first market types:

```text
threshold
range
binary YES/NO
multiple-choice for named storm outcomes only after rules are mature
```

Avoid initially:

```text
life-threatening disaster casualty markets
private property damage markets
markets on named individuals
markets that incentivize harm
markets without precise location/station
```

## 3. Approved Source Hierarchy

Primary source:

```text
official national meteorological agency
official station observation
official climate data release
```

India source examples:

```text
India Meteorological Department (IMD)
IMD regional/station pages where available
official Ministry of Earth Sciences/IMD releases
```

Reference examples:

```text
IMD: https://mausam.imd.gov.in/
IMD Pune climate services: https://www.imdpune.gov.in/
```

Fallback source:

```text
approved government mirror
approved licensed weather data vendor
```

Do not use:

```text
user screenshots
social media posts
unofficial weather apps as sole settlement source
```

## 4. Supported Subcategories

Initial subcategories:

```text
temperature
rainfall
air quality if official source approved
storm landfall
wind speed
climate monthly/seasonal summaries
```

Each subcategory must define:

```text
station/location identifier
measurement period
unit
aggregation method
observation timestamp
source update time
rounding
correction policy
```

## 5. Market Templates

### Temperature Threshold

Template:

```text
Will [station/location] record temperature above [threshold] on [date/time period]?
```

Resolution:

```text
YES if official measurement > threshold
NO if official measurement <= threshold
```

Must define:

```text
maximum temperature
minimum temperature
hourly observation
daily average
```

### Rainfall Range

Template:

```text
What range will total rainfall at [station] fall into for [period]?
```

Ranges:

```text
non-overlapping
gapless
unit in mm
boundary inclusivity explicit
```

### Storm Landfall

Template:

```text
Will [named storm/system] make landfall in [region] before [deadline]?
```

Resolution:

```text
official agency landfall statement controls outcome
```

## 6. Market Wording Rules

Every weather/climate market must define:

```text
location
station ID if available
metric
unit
measurement period
aggregation method
official source
observation timezone
threshold or ranges
rounding policy
backup source if any
void policy
```

Bad wording:

```text
Will Mumbai have heavy rain?
Will it be very hot tomorrow?
Will the storm be bad?
```

Good wording:

```text
Will the official IMD station rainfall total for Mumbai Santacruz exceed 75 mm from 08:30 IST Jul 20 to 08:30 IST Jul 21?
```

## 7. Close Time Rules

Recommended:

```text
close before observation period starts
```

For intraday markets:

```text
close before the first observation window begins
```

Do not allow trading after:

```text
the measurement period has started unless market is explicitly designed as live and legally approved
```

V1 should not support live weather markets.

## 8. Settlement Rules

Settlement requires:

```text
official observation captured
station/location verified
raw value stored
normalized value stored
unit stored
source timestamp stored
admin resolver
checker approval
```

Correction policy:

```text
default V1: use first official final daily/period value if available
if source later corrects before settlement, use corrected official value
if source corrects after settlement, follow incident policy only
```

## 9. Void Policy

Default void triggers:

```text
station did not report
station permanently unavailable
official agency cancels or withdraws data
measurement period was incorrectly specified
unit/location ambiguity prevents settlement
backup source not defined and primary unavailable
```

Do not void merely because:

```text
weather was extreme
forecast was wrong
market price moved sharply
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
station outage
station relocation
missing hourly observation
delayed official daily value
unit conversion error
multiple nearby stations
rainfall trace value
exact threshold equality
storm name changed
landfall location disputed
official correction after initial publication
```

## 11. Automation Level

Allowed automation:

```text
station metadata validation
observation window scheduling
source polling
candidate value extraction
threshold/range candidate calculation
evidence snapshot
stale source alerts
analytics rollups
notifications
```

Human approval required:

```text
market approval
station/source approval
settlement approval
source substitution
void decision
dispute resolution
official correction decision
```

## 12. Required Tests

Test cases:

```text
market rejects missing station/location
market rejects missing unit
market rejects close time after observation start
threshold equality resolves correctly
range boundary maps correctly
station outage moves market to pending resolution or void path
unit conversion is deterministic
official correction before settlement is handled
settlement is idempotent
void refund is idempotent
```

