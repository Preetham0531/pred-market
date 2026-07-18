# Market Categories, Automation, And Analytics Plan

This document records the intended market categories for Pred-Market and the product requirement that category operations, data collection, and analytics should be automated wherever possible.

This is planning documentation only. It does not create backend code, database migrations, frontend screens, or automated jobs.

## 1. Market Categories

Pred-Market should support prediction markets across these top-level categories:

```text
1. Sports
2. Politics
3. Economics
4. Stocks and mutual funds
5. Financials
6. Weather / climate
7. Culture
8. Tech and science
9. Mentions / public attention
10. Commodities
```

Each category should have clear subcategories, approved data sources, resolution standards, risk controls, and analytics views.

## 2. Category Definitions

### Sports

Examples:

```text
match winners
tournament winners
player/team milestones
season standings
points, runs, goals, or medal thresholds
```

Primary requirements:

```text
official league or tournament data source
clear event start and close time
rules for postponement, cancellation, walkover, and abandoned games
sport-specific settlement rules
```

### Politics

Examples:

```text
election winners
approval ratings
policy outcomes
official appointments
legislative votes
```

Primary requirements:

```text
jurisdiction-specific legal review before launch
official election or government source where possible
clear rules for recounts, court challenges, and delayed certification
strong manipulation and misinformation monitoring
```

### Economics

Examples:

```text
inflation
GDP
unemployment
interest rates
currency reserves
central bank decisions
```

Primary requirements:

```text
official statistical or central bank sources
release calendar tracking
preliminary vs revised value policy
units and rounding rules
timezone and publication timestamp rules
```

### Stocks And Mutual Funds

Examples:

```text
stock price thresholds
index thresholds
mutual fund NAV thresholds
earnings-related outcomes
dividend or split events
```

Primary requirements:

```text
legal and licensing review before launch
approved market data vendor
corporate action handling
close price vs intraday price rules
NAV publication rules for mutual funds
restricted securities policy
```

### Financials

Examples:

```text
interest rates
bond yields
exchange rates
banking metrics
credit spreads
financial index levels
```

Primary requirements:

```text
approved financial data sources
instrument identifier standards
market holiday handling
rounding and decimal precision rules
regulatory classification review
```

### Weather / Climate

Examples:

```text
temperature thresholds
rainfall ranges
storm landfall
air quality
climate metric releases
```

Primary requirements:

```text
official weather agency source
station/location identifier
measurement period
unit conversion rules
delayed or corrected data policy
```

### Culture

Examples:

```text
award winners
box office milestones
music chart rankings
streaming rankings
festival results
public event outcomes
```

Primary requirements:

```text
official award, chart, or publisher source
clear observation window
category-specific tie handling
restricted personal/private-life policy
```

### Tech And Science

Examples:

```text
product launches
space mission milestones
AI model releases
scientific discovery announcements
benchmark thresholds
regulatory approval milestones
```

Primary requirements:

```text
official company, agency, journal, or regulator source
precise definition of what counts as launch, approval, release, or success
backup source policy
technical benchmark methodology
```

### Mentions / Public Attention

Examples:

```text
number of news mentions
social media mention thresholds
search trend thresholds
official ranking appearances
media coverage comparisons
```

Primary requirements:

```text
approved measurement provider
keyword and entity disambiguation rules
bot/spam filtering policy
time window definition
rate-limit and data outage handling
```

This category needs extra care because public attention data can be noisy, manipulated, or vendor-dependent.

### Commodities

Examples:

```text
gold price
crude oil price
natural gas price
agricultural commodity price
commodity inventory reports
```

Primary requirements:

```text
approved exchange or benchmark source
contract month or spot benchmark definition
settlement price vs intraday price rule
holiday and trading halt policy
unit and currency rules
```

## 3. Automation Requirement

The platform should automate as much of the market lifecycle as possible while keeping final controls auditable.

Automation should cover:

```text
market suggestion intake
category classification
prohibited-topic screening
duplicate market detection
source availability checks
event calendar ingestion
market close scheduling
oracle data collection
evidence capture
candidate outcome calculation
settlement job preparation
analytics rollups
risk alerts
user notifications
```

Human approval should still be required for:

```text
new category launch
high-risk market approval
final resolution of disputed markets
manual override of oracle data
void decisions
policy exceptions
legal/compliance exceptions
```

## 4. Automation Levels

Automation should be introduced in levels:

```text
Level 0: manual admin process
Level 1: system suggests, admin approves
Level 2: system executes low-risk actions, admin reviews exceptions
Level 3: system executes approved categories end-to-end with audit trails
```

Recommended V1 approach:

```text
Use Level 1 for most market creation and settlement workflows.
Use Level 2 only for low-risk data ingestion, analytics rollups, notifications, and routine close scheduling.
Do not use Level 3 for real-money settlement until legal, compliance, and operational controls are mature.
```

## 5. Data Source Model

Every category should have approved data sources before markets are listed.

Each data source record should define:

```text
source name
source type
official URL or vendor
covered categories
covered regions
data license status
refresh frequency
publication delay
historical availability
API reliability
backup source
correction policy
evidence capture method
```

Each market should store:

```text
primary source
backup source if allowed
source version or endpoint
observation time
value extraction rule
rounding rule
timezone
evidence snapshot
admin reviewer
```

## 6. Database Precision Requirements

The database should be designed for financial correctness and analytical clarity.

Core database principles:

```text
use integer minor units for money
use scaled integers for decimal measurements where possible
store raw source values separately from normalized values
store source timestamps and ingestion timestamps separately
never overwrite audit-critical records
version market rules
version resolution rules
record every admin action
record every automated decision
record every user-facing price point needed for charts
```

Important distinction:

```text
transaction tables protect correctness
analytics tables support understanding
```

The trading system should not depend on slow analytical queries. Analytics should be served from rollups, materialized views, or dedicated analytical tables.

## 7. Analytical Data Model

The analytics layer should help users understand markets quickly and form strategies.

Minimum market analytics:

```text
current best bid
current best ask
last traded price
24h price change
24h volume
total volume
open interest
spread
liquidity depth
number of traders
market close time
implied probability
price history
volume history
```

Minimum user analytics:

```text
open positions
average entry price
unrealized PnL
realized PnL
exposure by category
exposure by market
cash locked in orders
shares locked in sell orders
settlement history
win/loss history
```

Minimum category analytics:

```text
active markets
total volume
top markets by volume
top movers
new markets
markets closing soon
liquidity concentration
category-level risk alerts
```

## 8. User-Facing Analysis Experience

Users should not need to understand database internals to analyze markets.

Each market page should make these questions easy to answer:

```text
What is the market asking?
What has to happen for each outcome to win?
What is the current implied probability?
How has the probability moved over time?
How liquid is the market?
What is the spread?
How much volume traded recently?
When does the market close?
What source will settle the market?
What are the main risks or ambiguity points?
```

Each user portfolio page should make these questions easy to answer:

```text
Where is my money allocated?
Which categories am I exposed to?
Which markets can affect me soon?
What is my average entry price?
What happens if each outcome wins?
How much cash is locked?
How much can I lose?
How much can I gain?
```

## 9. Strategy-Oriented Views

The analytics product should support strategy without giving financial advice.

Useful views:

```text
watchlist
closing soon
high volume
low spread
large price movers
newly listed
category heatmap
probability trend chart
order book depth chart
portfolio exposure chart
market comparison table
```

Possible user filters:

```text
category
market type
close time
volume
liquidity
price range
probability range
spread
status
watchlisted markets
markets with open positions
```

## 10. Data Quality And Trust

Analytics must be precise enough that users can rely on them.

Required data quality controls:

```text
source ingestion health checks
duplicate event checks
stale data warnings
missing data warnings
outlier detection
timestamp consistency checks
price chart backfill checks
ledger-to-analytics reconciliation
daily volume reconciliation
open interest reconciliation
settlement payout reconciliation
```

User-facing trust indicators:

```text
last updated time
data source label
source evidence link
market rule version
settlement status
data delay notice
dispute status
void risk note where relevant
```

## 11. Risk And Compliance Controls By Category

Each category should have a risk level:

```text
LOW
MEDIUM
HIGH
RESTRICTED
PROHIBITED
```

Risk level should affect:

```text
whether market creation is allowed
whether admin approval is required
whether legal review is required
maximum exposure limits
settlement automation level
data source requirements
dispute process
user eligibility
```

High-risk categories such as politics, securities-related markets, and public attention markets should require stricter review before any real-money launch.

## 12. Reporting And Internal Analytics

Internal dashboards should track:

```text
daily active users
deposits and withdrawals
trading volume
fees if introduced later
market creation funnel
order fill rate
cancel rate
spread by category
liquidity by category
settlement time
dispute rate
void rate
oracle failure rate
suspicious trading alerts
user concentration risk
```

These analytics should support operations, compliance, liquidity planning, and product strategy.

## 13. Recommended Documentation Next Steps

Before coding, create separate category rulebooks for:

```text
sports
economics
weather / climate
commodities
```

These are the best first categories for structured automated resolution because they often have clear event calendars and official data sources.

Delay or apply stricter review to:

```text
politics
stocks and mutual funds
financials
mentions / public attention
```

These categories are more likely to involve legal, data licensing, manipulation, or regulatory risks.

