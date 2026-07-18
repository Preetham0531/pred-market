# Frontend Completion Plan

This document defines the remaining frontend work needed to complete the Pred-Market V1 web product.

The current app is a Next.js prototype using mock data. The goal is to keep the calm professional trading terminal style while making every route navigable, analyzable, and ready for backend integration.

## 1. Frontend Goal

Users should be able to:

```text
browse markets without signing in
sign up and sign in
understand market rules and sources
preview and submit limit orders
track orders, positions, wallet, and ledger
suggest a market
review admin workflows when authorized
read charts and analytics without confusion
```

The product must remain:

```text
minimal
calm
professional
analysis-first
responsive
accessible
```

## 2. Route Completion

Public routes:

```text
/
/markets
/markets/[marketId]
/categories/[categorySlug]
/sign-in
/sign-up
/forgot-password
/reset-password
/verify-email
```

Signed-in routes:

```text
/watchlist
/portfolio
/orders
/wallet
/markets/suggest
/account/security
```

Admin routes:

```text
/admin
/admin/markets/[reviewId]
```

Expected behavior:

```text
signed-out users can browse public market data
signed-out users are redirected from private routes to sign-in
signed-in non-admin users are redirected away from admin
admin users can review admin routes
```

## 3. Auth UI

Auth pages:

```text
sign-in page
sign-up page
forgot-password page
reset-password page
verify-email page
account security page
```

Top bar states:

```text
signed out: Sign in and Create account
signed in: notifications, wallet balance, profile menu
admin: admin route available through sidebar and command menu
```

Auth implementation rule:

```text
frontend calls backend-owned /api/v1/auth endpoints
no localStorage tokens
browser session uses HttpOnly cookies
```

Temporary prototype rule:

```text
Next.js route handlers may simulate /api/v1/auth endpoints until FastAPI backend exists
the production owner remains FastAPI
```

## 4. Navigation

Global shell:

```text
desktop left sidebar
mobile bottom navigation
top bar search
breadcrumbs on inner pages
profile menu
notification drawer
```

Command menu:

```text
search markets
search categories
open portfolio
open suggest market
open admin review
```

Breadcrumb rules:

```text
market detail includes market and category context
category page starts from Markets
admin review pages start from Admin
mobile breadcrumbs stay compressed
```

## 5. Market Discovery

Market discovery must support:

```text
category filters
status filters
sort filters
search
watchlisted only
has position only
market cards
market table
category identity icons
```

Backend integration:

```text
GET /api/v1/markets
GET /api/v1/categories/{category_slug}
```

Required states:

```text
loading
empty
error
stale
live
```

## 6. Market Detail And Trading

Market detail must show:

```text
title
category
market type
status
close time
source
rules
probability chart
volume/liquidity/spread stats
order book
recent trades
evidence
related markets
```

Trade ticket must support:

```text
outcome selector
limit price input
quantity input
estimated cost
max payout
max loss
implied probability
fee placeholder
preview order
submit order
accepted state
rejected state
partial-fill state
```

V1 trading constraints:

```text
limit orders only
no market orders
no leverage
simulated funds only
```

## 7. Orders

Orders page must show:

```text
open orders
filled orders
cancelled orders
side
outcome
price
filled quantity
status
cancel action for open orders
```

Backend integration:

```text
GET /api/v1/orders
POST /api/v1/orders/{order_id}/cancel
```

UI rule:

```text
cancelling an order should update the row without layout shift
```

## 8. Wallet

Wallet page must show:

```text
available simulated balance
locked funds
total balance
ledger rows
simulated deposit flow
```

Backend integration:

```text
GET /api/v1/wallet
GET /api/v1/wallet/ledger
POST /api/v1/wallet/test-deposit
```

User copy must make clear:

```text
funds are simulated in V1
real deposits and withdrawals are disabled
```

## 9. Portfolio

Portfolio page must show:

```text
current value
invested capital
unrealized PnL
max payout
open positions
exposure chart
scenario payout table
```

Backend integration:

```text
GET /api/v1/positions
GET /api/v1/portfolio
```

Analytics rule:

```text
portfolio numbers must reconcile with trades and ledger events
```

## 10. Suggest Market

Suggestion flow steps:

```text
category
market type
question and outcomes
source and resolution rule
automation checks
submit for admin approval
```

Backend integration:

```text
POST /api/v1/market-suggestions
GET /api/v1/market-suggestions/{suggestion_id}
```

UI rule:

```text
users suggest markets; users do not directly list markets in V1
```

## 11. Admin

Admin must support:

```text
review queue
review detail page
automation checklist
market approval placeholder
request changes placeholder
reject placeholder
risk notices
maker-checker notes
```

Backend integration:

```text
GET /api/v1/admin/markets/review
POST /api/v1/admin/markets/{market_id}/approve
POST /api/v1/admin/markets/{market_id}/pause
POST /api/v1/admin/markets/{market_id}/evidence
POST /api/v1/admin/markets/{market_id}/resolution-proposals
POST /api/v1/admin/resolution-proposals/{proposal_id}/approve
POST /api/v1/admin/markets/{market_id}/settle
```

Admin UI rule:

```text
show controls only to authorized admin users
backend must enforce all permissions
```

## 12. API Integration

Add a typed API client with:

```text
base URL config
credentials include
JSON request/response handling
standard error shape
idempotency key support
mock-data flag
```

Use TanStack Query for:

```text
markets
categories
market detail
orders
wallet
portfolio
admin queue
```

Environment flags:

```text
NEXT_PUBLIC_API_BASE_URL
NEXT_PUBLIC_USE_MOCK_DATA
```

## 13. Realtime

Subscribe to:

```text
market order book updates
market trade updates
user order updates
user position updates
wallet updates
notifications
```

UI rules:

```text
stable row heights
no violent animations
no constant movement
respect prefers-reduced-motion
show live/stale state
```

## 14. Accessibility

Required checks:

```text
keyboard navigation
visible focus states
screen-reader labels for icon buttons
forms have labels
error states are text-visible
contrast is acceptable
reduced motion is respected
mobile text does not overlap
```

## 15. Visual QA

Required viewport checks:

```text
desktop
tablet
mobile
```

Required pages:

```text
markets
market detail
category
watchlist
portfolio
orders
wallet
suggest market
admin queue
admin review detail
sign in
sign up
account security
```

Visual rules:

```text
no rainbow gradients
no neon
no decorative orb backgrounds
no marketing hero page inside the app
no nested cards
cards only for repeated items and tool surfaces
calm palette stays intact
```

## 16. Completion Checklist

Frontend is complete for V1 when:

```text
all planned routes exist
all navigation links work
protected routes redirect correctly
auth UI exists
top bar has signed-in and signed-out states
command search is useful
trade ticket has all expected states
orders can be cancelled in prototype
wallet has simulated deposit flow
admin review detail exists
loading/error/not-found states exist
typed API client exists
mock-data flag is explicit
npm run typecheck passes
npm run lint passes
npm run build passes
```
