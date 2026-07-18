# Market Data Source Catalog And AI Strategy

This document defines the data sectors, source policy, market issuing flows, and AI usage model for Pred-Market.

V1 rule: AI can suggest, summarize, classify, score, and explain. AI cannot list markets, settle markets, place trades, override admins, or become the settlement oracle.

## 1. Current Data Sectors

Pred-Market focuses on these top-level sectors:

```text
1. sports
2. politics
3. economics
4. stocks and mutual funds
5. financials
6. weather / climate
7. culture
8. tech and science
9. mentions / public attention
10. commodities
```

First-class automation focus:

```text
sports
economics
weather / climate
commodities
```

These have the clearest official-source and rulebook structure. Politics, stocks, financials, and mentions need stronger legal/licensing review before broad automation.

## 2. Source Policy

Pred-Market uses a two-tier source model.

### Discovery Sources

Discovery sources generate market ideas and alerts.

Examples:

```text
GDELT
NewsAPI
official RSS feeds
Media Cloud
Google Trends alpha
Wikimedia Analytics
vendor market-data APIs
licensed sports feeds
```

Discovery sources can create `source_events` and AI draft candidates, but they do not automatically settle markets.

### Settlement Sources

Settlement sources decide outcomes.

Examples:

```text
official league result page
official government statistical agency
official central bank release
official weather agency station record
official exchange settlement price
licensed benchmark provider
official company / regulator / journal announcement
official chart / award / publisher source
```

No market should be listed unless the admin has attached a settlement-approved source.

## 3. Source Catalog

### News And Internet Discovery

Use:

```text
GDELT
NewsAPI
official RSS feeds
Media Cloud
```

Purpose:

```text
discover candidate events
cluster stories
detect trend changes
find source URLs
create market drafts
monitor post-listing context
```

Settlement policy:

```text
news cannot settle by default
news may support evidence only when rule explicitly allows it
official source must be attached for listing
```

Research references:

```text
GDELT: https://www.gdeltproject.org/
NewsAPI: https://newsapi.org/docs
RSS 2.0: https://www.rssboard.org/rss-specification
Media Cloud: https://www.mediacloud.org/documentation/search-api-guide
```

### Sports

Use:

```text
official league / tournament pages
ICC fixtures and results
Sportradar
Football-Data.org
Cricsheet for analytics and backtesting
```

Settlement policy:

```text
official competition result page first
licensed vendor only after contract review
open historical datasets are not sole settlement sources
```

Research references:

```text
Sportradar: https://developer.sportradar.com/getting-started/docs/get-started
Football-Data.org: https://www.football-data.org/documentation/api
Cricsheet: https://cricsheet.org/
```

### Economics

Use:

```text
FRED
BLS
BEA
World Bank Indicators
country-specific official statistical agencies
central bank release pages
```

Settlement policy:

```text
official agency release controls outcome
market must specify preliminary vs revised value
market must specify unit, period, threshold, timezone, and rounding rule
```

Research references:

```text
FRED: https://fred.stlouisfed.org/docs/api/fred/
BLS: https://www.bls.gov/developers/home.htm
BEA: https://apps.bea.gov/api/signup/
World Bank: https://datahelpdesk.worldbank.org/knowledgebase/articles/889392-about-the-indicators-api-documentation
```

### Politics

Use:

```text
official election authority
official government portals
FEC OpenFEC for US campaign-finance data
official legislative vote sources
```

Settlement policy:

```text
manual/admin-first
jurisdiction review required
official certification or official vote record required
no rumor or poll-only settlement
```

Research references:

```text
OpenFEC: https://api.open.fec.gov/developers/
```

### Stocks, Mutual Funds, And Financials

Use:

```text
SEC EDGAR
Finnhub
Alpha Vantage
Nasdaq Data Link
licensed exchange/vendor feeds
official mutual fund NAV publisher
```

Settlement policy:

```text
official filing source for filing/corporate-action events
licensed market data source for prices
official NAV source for mutual funds
legal/licensing review required before real-money listing
```

Research references:

```text
SEC EDGAR: https://www.sec.gov/search-filings/edgar-application-programming-interfaces
Finnhub: https://finnhub.io/docs/api
Alpha Vantage: https://www.alphavantage.co/documentation/
Nasdaq Data Link: https://docs.data.nasdaq.com/
```

### Weather / Climate

Use:

```text
NOAA National Weather Service
NOAA NCEI / Climate Data Online
official national meteorological agencies
Open-Meteo for discovery/prototype only
```

Settlement policy:

```text
official station/location required
measurement period required
metric, unit, aggregation, timezone, and correction policy required
no casualty or private-damage markets
```

Research references:

```text
NWS API: https://www.weather.gov/documentation/services-web-api
NOAA CDO: https://www.ncdc.noaa.gov/cdo-web/webservices/getstarted
NCEI Access Data Service: https://www.ncei.noaa.gov/support/access-data-service-api-user-documentation
Open-Meteo: https://open-meteo.com/en/docs
```

### Culture

Use:

```text
official award pages
official chart publishers
TMDb for discovery and identity metadata
MusicBrainz for metadata
licensed box office/chart providers
```

Settlement policy:

```text
official award/chart/publisher source required
TMDb/MusicBrainz metadata does not settle award, chart, or revenue markets
```

Research references:

```text
TMDb: https://developer.themoviedb.org/docs/getting-started
MusicBrainz: https://musicbrainz.org/doc/MusicBrainz_API
```

### Tech And Science

Use:

```text
official company announcement pages
official agency pages
official regulator pages
journal publication pages
GDELT / RSS for discovery
```

Settlement policy:

```text
official publisher/source controls
rumors, leaks, and media speculation do not count unless rule says otherwise
market must define launch, release, approval, publication, benchmark, or mission success precisely
```

### Mentions / Public Attention

Use:

```text
Wikimedia Analytics API
Media Cloud
GDELT
Google Trends API alpha after access approval
licensed social/search measurement providers
```

Settlement policy:

```text
exact entity and keyword rules required
bot/spam policy required
time window required
provider outage policy required
avoid unofficial scraping as settlement source
```

Research references:

```text
Wikimedia Analytics: https://doc.wikimedia.org/generated-data-platform/aqs/analytics-api/reference/page-views.html
Google Trends API alpha: https://developers.google.com/search/apis/trends
Media Cloud: https://www.mediacloud.org/documentation/search-api-guide
```

### Commodities

Use:

```text
EIA Open Data
CME Group market data
Nasdaq Data Link
Alpha Vantage commodities data
licensed benchmark vendors
```

Settlement policy:

```text
official exchange settlement price or benchmark required
contract month / benchmark / currency / unit required
holiday and trading halt policy required
legal/licensing review required before real-money listing
```

Research references:

```text
EIA: https://www.eia.gov/opendata/
CME: https://www.cmegroup.com/market-data/market-data-api.html
Nasdaq Data Link: https://docs.data.nasdaq.com/
Alpha Vantage: https://www.alphavantage.co/documentation/
```

## 4. Market Issuing Flows

### Flow A: AI Creates Draft, Admin Approves

```text
1. Source registry defines approved discovery and settlement sources.
2. Ingestion job pulls or receives source data.
3. Raw source payload is stored as a source event.
4. System dedupes using source + dedupe key + content hash.
5. AI classifies event category and subcategory.
6. AI proposes market question, outcomes, close time, source, rule, void policy, and rationale.
7. Deterministic checks run:
   - category allowed
   - market type allowed
   - duplicate title
   - prohibited topic
   - source present
   - approved settlement source attached
   - close time valid
   - outcomes valid
   - resolution rule present
   - void policy present
   - AI rationale present
8. Draft enters admin queue.
9. Admin reviews source evidence, checks, risk flags, and AI rationale.
10. Admin edits or rejects draft if needed.
11. Admin approves only when checks pass.
12. Approved draft is listed as a real market.
13. Audit logs and realtime admin events are written.
```

### Flow B: Admin Directly Creates Market

```text
1. Admin opens market issuing workspace.
2. Admin selects category, market type, outcomes, source, rule, close time, and void policy.
3. Backend creates market draft with origin ADMIN.
4. Same deterministic checks run.
5. If checks pass and admin selected immediate listing, backend lists market.
6. If checks fail, draft remains NEEDS_CHANGES.
7. Every action writes audit logs.
```

### Flow C: Trader Suggests Market, Admin Approves

```text
1. Trader submits suggestion.
2. Backend stores market_suggestion for trader-facing history.
3. Backend creates linked market_draft with origin TRADER.
4. Deterministic checks run.
5. Draft enters admin review queue.
6. Admin edits source/rule/close time if needed.
7. Admin approves and lists only after checks pass.
8. Trader sees submitted / needs changes / approved / listed status.
```

## 5. AI Product Strategy

Use AI in these areas first:

```text
market candidate generation
source event summarization
duplicate / semantic similarity detection
market question rewriting
resolution-rule critique
void-policy suggestions
risk flagging
category/subcategory classification
evidence summarization for admins
user-facing market explainers
portfolio risk explanations
search and command-menu natural language parsing
```

Do not use AI for:

```text
placing orders
settlement finality
admin override
legal decisions
KYC/AML decisions without human review
price manipulation scoring without deterministic evidence
```

Recommended model integration pattern:

```text
source_events -> AI structured draft proposal -> deterministic validator -> market_drafts -> admin review
```

For OpenAI integration later, use structured outputs for schema-constrained market draft proposals, embeddings for semantic duplicate detection and source-event clustering, and evals to measure whether generated markets satisfy rulebook requirements.

Research references:

```text
OpenAI structured outputs: https://platform.openai.com/docs/guides/structured-outputs
OpenAI embeddings: https://platform.openai.com/docs/guides/embeddings
OpenAI evals: https://platform.openai.com/docs/guides/evals
```

## 6. Current Implementation State

Implemented:

```text
data_sources
source_events
market_drafts
market_draft_evidence
admin draft approval/rejection/listing APIs
deterministic local ingestion runs
deterministic AI draft generation from source events
admin issuing workspace
trader suggestions converted into market drafts
seeded source catalog across all ten sectors
```

Still future work:

```text
real provider fetchers and API-key management
OpenAI/LLM provider call
embedding-based duplicate detection
provider-specific parsers
scheduled ingestion workers
jurisdiction-specific politics controls
licensed market-data contracts
settlement oracle adapters
AI eval suite
```
