# Frontend Design System Spec

This document defines the Pred-Market frontend design system: colors, typography, spacing, components, icons, charts, tables, motion rules, responsive behavior, and accessibility standards.

This is planning documentation. It should guide implementation and review of the existing Next.js frontend prototype and future production UI.

## 1. Design Goal

Pred-Market should feel like:

```text
a calm professional trading terminal
```

not:

```text
a sportsbook
a flashy crypto casino
a marketing landing page
a loud consumer betting app
```

The interface should help users:

```text
scan markets quickly
understand contract rules
analyze probability movement
place limit orders carefully
manage positions
trust data freshness and settlement sources
```

Primary design values:

```text
calm
precise
readable
dense but not cramped
professional
low-distraction
analysis-first
```

## 2. Visual Direction

Default theme:

```text
restrained graphite-grey exchange terminal theme
softened dark graphite background
dark graphite panels and muted steel-grey secondary surfaces
steel-grey primary actions
slate blue-grey secondary information
muted brass attention/accent states
soft red risk/error states
```

Avoid:

```text
rainbow gradients
neon colors
bright purple/blue gradients
large decorative blobs
floating orb backgrounds
casino-style colors
oversized hero sections
landing-page layout for the app
```

The product should open directly into useful market discovery or the user workspace.

## 3. Color Tokens

Current frontend tokens:

```text
background: #1d2023
foreground: #f0f2f3
muted: #aeb5ba
surface: #272b2f
surface-muted: #30353a
surface-raised: #23272b
border: #444b52
border-strong: #586169

primary: #7f8a93
primary-strong: #d7dde1
primary-soft: #373d43
primary-border: #68737d
ring: rgba(174, 181, 186, 0.28)

green-soft: #2f3840
green-border: #647280
green-text: #c4d0d8

blue-soft: #2d3640
blue-border: #617283
blue-text: #c3d4e0

brass: #c59a38
brass-soft: #3a3425
brass-border: #8a784a
brass-text: #e0cc8d

red-soft: #3d2523
red-border: #894b44
red-text: #e28a80
danger: #b4584f
danger-strong: #cf6d63
```

Color usage:

```text
primary:
  main calls to action, active navigation, selected category

green:
  open markets, positive movement, successful checks, available balance

blue:
  neutral information, filled status, secondary metrics, source/evidence state

brass:
  attention, closing soon, pending review, caution without failure

red:
  risk, restriction, failure, negative movement, cancelled/rejected states
```

Do not use color alone to communicate state. Pair with text, icon, or status label.

## 4. Typography

Recommended font:

```text
Inter
fallback: system UI, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif
```

Typography rules:

```text
body text: 14px to 16px
table text: 13px to 14px
metric labels: 11px to 12px uppercase
page headings: 24px to 28px
section headings: 14px to 16px
button text: 12px to 14px
```

Do not scale font size with viewport width.

Letter spacing:

```text
normal for most text
small positive tracking only for uppercase metric labels
never use negative letter spacing
```

Line height:

```text
dense tables: 1.3 to 1.4
body paragraphs: 1.5 to 1.7
headings: 1.15 to 1.25
```

## 5. Spacing And Layout

Base spacing:

```text
4px atomic unit
8px compact gap
12px normal compact panel padding
16px standard page component gap
20px to 24px major section gap
```

Radius:

```text
4px for tiny controls
6px for buttons, inputs, badges, table rows
8px maximum for cards and modals
```

Do not use very rounded pill shapes unless representing a compact status badge.

Layout rules:

```text
left sidebar on desktop
top bar with breadcrumbs and search
mobile bottom navigation
content width uses available viewport
side panels should be sticky on desktop
cards are only for repeated items, widgets, modals, or framed tools
do not put cards inside cards
```

## 6. Navigation System

Desktop shell:

```text
left sidebar
top bar
breadcrumbs under or inside top bar
market search / command menu
notifications
wallet balance
profile
```

Mobile shell:

```text
top compressed breadcrumb
notifications/profile
bottom navigation
horizontal category chips where useful
```

Primary navigation:

```text
Markets
Watchlist
Portfolio
Orders
Wallet
Suggest
Admin
```

Breadcrumb pattern:

```text
Markets > Sports > Cricket > Market title
Markets > Suggest market > Resolution rules
Admin > Market review > Pending approval
```

Mobile breadcrumb should compress to:

```text
Markets > Current page
```

## 7. Core Components

### Buttons

Button variants:

```text
primary
secondary
ghost
danger
icon
```

Use primary buttons for:

```text
submit order
continue flow
approve action
save confirmed setup
```

Use secondary buttons for:

```text
preview
back
cancel non-destructive action
filter actions
```

Use danger buttons for:

```text
reject market
void market
suspend user
cancel high-risk process
```

### Inputs

Input types:

```text
text
search
number-like text input for money/quantity
select
textarea for rules
checkbox for binary filters
```

Input rules:

```text
always show labels
show unit/currency where relevant
validate before submit
do not rely on placeholder as label
```

### Badges

Badge types:

```text
market status
market type
category
risk level
position held
automation check status
```

Statuses:

```text
OPEN: green
CLOSING_SOON: brass
PENDING_RESOLUTION: blue
RESTRICTED: red
CANCELLED: red
FILLED: blue
```

### Metric Cards

Use for:

```text
24h volume
open markets
average spread
liquidity
total volume
available balance
locked balance
PnL
```

Metric card contents:

```text
label
primary value
optional detail
optional trend color
```

### Market Cards

Market cards must show:

```text
title
category
market type
status
primary probability/price
24h change
close time
24h volume
liquidity
trader count
position/watchlist indicators
```

### Trade Ticket

Trade ticket must show:

```text
outcome selector
limit price
quantity
estimated cost
max payout
max loss
implied probability
fee line, even if zero for V1
preview before submit
```

V1 rules:

```text
limit orders only
no market orders
no leverage
no naked shorting
```

## 8. Tables

Tables should be compact and scannable.

Common table types:

```text
market list
open orders
order history
recent trades
wallet ledger
positions
admin review queue
```

Table rules:

```text
sticky headers where useful
right-align numeric columns
use tabular numeric style if available
truncate long market titles with accessible full title
keep row height stable
support mobile stacked row layout
avoid horizontal overflow on mobile
```

## 9. Charts

Chart types:

```text
probability/price line or area chart
volume chart
order book depth chart
portfolio exposure bar chart
category heatmap
open interest trend
```

Chart rules:

```text
use muted grid lines
avoid heavy fills
use primary green for main YES/probability series
use red only for negative/risk series
show empty state
show loading state
show stale-data warning
show last updated timestamp
```

Chart axis rules:

```text
probability charts use 0 to 100 scale when practical
money values use formatted minor units
volume may use compact notation
timestamps use user's local display timezone but preserve UTC internally
```

## 10. Icons And 3D Assets

Functional icons:

```text
Lucide React
```

Use functional icons for:

```text
navigation
buttons
filters
notifications
wallet
orders
admin actions
chart controls
```

3D icons:

```text
limited accents only
category identity
empty states
onboarding moments
admin review illustrations if subtle
```

3D icon rules:

```text
do not place 3D icons on every button
do not animate 3D icons continuously
avoid loud gradients
verify commercial licensing before production
keep icons visually consistent across categories
```

Candidate sources:

```text
Streamline 3D
Icons8 3D Fluency
IconScout 3D
custom Spline assets if licensing and performance are acceptable
```

## 11. Motion Rules

Motion should be restrained.

Allowed:

```text
page fade/slide under 250ms
tab transitions
row update highlight
order book quantity flash
trade confirmation
modal open/close
filter panel open/close
```

Avoid:

```text
constant floating animations
large parallax sections
spinning objects
heavy 3D motion
distracting chart animation
motion that changes layout stability
```

Accessibility:

```text
respect prefers-reduced-motion
disable non-essential animations under reduced motion
```

## 12. Responsive Breakpoints

Recommended breakpoints:

```text
mobile: < 640px
tablet: 640px to 1023px
desktop: 1024px to 1439px
wide desktop: >= 1440px
```

Desktop:

```text
sidebar visible
top search visible
trade ticket sticky
filters in left column
tables use multi-column layout
```

Tablet:

```text
sidebar may collapse
trade ticket can stack below chart
tables reduce columns
filters can become panel
```

Mobile:

```text
bottom nav visible
sidebar hidden
top search hidden or moved to page
category filters become horizontal chips
tables become stacked rows
trade ticket appears below main market summary
no horizontal overflow
```

## 13. Accessibility Standards

Minimum requirements:

```text
keyboard navigation
visible focus states
semantic headings
button labels
icon button aria-labels
form labels
error text connected to fields
sufficient color contrast
do not use color alone for state
reduced motion support
screen-reader readable status updates
```

Interactive requirements:

```text
command menu opens and closes by keyboard
modals trap focus
escape closes modals
tabs are keyboard accessible
select controls are keyboard accessible
trade preview is reachable before submit
```

## 14. Content Language

Use exchange-style language:

```text
trade
contract
order
position
market
fill
settlement
payout
collateral
```

Avoid:

```text
bet
gamble
wager
jackpot
casino-style wins
guaranteed profit
sure outcome
```

Risk wording:

```text
clear
plain
non-alarmist
visible before order submission
```

## 15. Required QA

Before merging frontend UI changes:

```text
run typecheck
run lint
run production build
check desktop screenshot
check mobile screenshot
verify no horizontal overflow
verify key pages have breadcrumbs
verify text does not overlap
verify charts render nonblank
verify reduced motion does not break layout
```

Core pages for visual QA:

```text
/markets
/markets/[marketId]
/categories/[categorySlug]
/portfolio
/orders
/wallet
/markets/suggest
/admin
```
