# DESIGN.md

## Metadata

- Product: Pred-Market
- Platform: Web
- Register: Product UI
- Framework: Next.js App Router, React, TypeScript, Tailwind CSS 4
- Design intent: calm professional prediction exchange terminal

## Visual Theme

Pred-Market uses a restrained graphite-grey exchange terminal theme. The background is softened dark graphite, primary surfaces are dark grey panels, and secondary surfaces are muted steel-grey layers. The interface should feel quiet, data-dense, and operational without feeling green, blacked-out, or neon. Visual interest comes from charts, tables, market state, and carefully used category icons, not decorative backgrounds.

Avoid loud gradients, neon colors, purple-blue AI styling, casino/sportsbook cues, generic blue SaaS dominance, wellness typography, or gallery-like page layouts.

## Color Tokens

Use the existing CSS variables in `app/globals.css` as the source of truth.

```css
--background: #1d2023;
--foreground: #f0f2f3;
--muted: #aeb5ba;
--surface: #272b2f;
--surface-muted: #30353a;
--surface-raised: #23272b;
--border: #444b52;
--border-strong: #586169;

--primary: #7f8a93;
--primary-strong: #d7dde1;
--primary-soft: #373d43;
--primary-border: #68737d;
--ring: rgba(174, 181, 186, 0.28);

--green-soft: #2f3840;
--green-border: #647280;
--green-text: #c4d0d8;

--blue-soft: #2d3640;
--blue-border: #617283;
--blue-text: #c3d4e0;

--brass: #c59a38;
--brass-soft: #3a3425;
--brass-border: #8a784a;
--brass-text: #e0cc8d;

--red-soft: #3d2523;
--red-border: #894b44;
--red-text: #e28a80;
--danger: #b4584f;
--danger-strong: #cf6d63;
```

### Color Roles

- Primary steel-grey: primary actions, selected navigation, selected category, and neutral focus state.
- Slate blue-grey: neutral information, evidence/source state, secondary metrics, portfolio max payout.
- Brass: caution, closing soon, pending review, authentication-required notices.
- Soft red: risk, rejection, negative movement, cancelled state, destructive action.
- Neutral dark surfaces: all panels, tables, filters, tickets, drawers, admin queues.

Color must never be the only state channel. Pair it with labels, icons, signs, or status text.

## Typography

Use Inter as the single UI family. Product screens do not use display fonts or decorative pairings.

```text
Primary: Inter
Fallback: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif
Numeric: tabular numbers via `.numeric`
Monospace IDs: ui-monospace stack via `.mono-numeric`
```

Recommended sizes:

- Page heading: 24-28px, semibold, tight line height.
- Section heading: 14-16px, semibold.
- Body/table text: 13-15px.
- Metric labels: 11px uppercase, 0.06em tracking.
- Buttons/inputs: 13-14px.
- IDs/order refs: 12px monospace.

Do not use viewport-scaled type. Do not use negative tracking.

## Layout

Pred-Market is an app shell, not a landing page.

- Desktop: fixed left sidebar, sticky top bar, breadcrumbs, command search, wallet/profile controls.
- Mobile: compressed breadcrumbs, bottom navigation, mobile category chips, trade ticket bottom sheet.
- Main content: dense but readable, with 4px/8px spacing rhythm.
- Radius: 6px for controls and 8px maximum for cards/modals.
- Panels: one-level framed tools only; do not nest cards inside cards.
- Tables: stable row heights, compact headers, tabular numbers, hover state, no layout shift during realtime updates.

Use `.exchange-panel` for framed product surfaces and `.exchange-table-header` for dense table headers.

## Core Components

### Market Discovery

Market discovery should behave like an exchange board:

- Top metrics: 24h volume, open markets, average spread, biggest mover, deepest book, tightest spread.
- Left filter rail on desktop; mobile category chips.
- Category tape for sector scanning.
- Highlight cards only for movers or special markets.
- Full market table as the primary browsing surface.

### Market Detail

Market detail is the trading cockpit:

- Header: status, type, category, title, close time, source, rules/evidence, YES price, 24h movement.
- Metrics: 24h volume, total volume, liquidity, spread.
- Chart: deterministic probability chart with volume context and source-event markers.
- Market depth: YES/NO order book with best YES, YES ask, spread, quantities, totals.
- Lower workspace: recent trades, rules/evidence, risk notes, related markets.

### Trade Ticket

The trade ticket must feel careful and explicit:

- Segmented YES/NO selector.
- Limit price and quantity inputs.
- Available balance, estimated cost, max payout, max loss, implied probability, fee.
- Preview before submit.
- States: unauthenticated, insufficient balance, submitting, accepted, partial fill, rejected.
- Desktop sticky side panel; mobile bottom action bar and bottom sheet.

### Portfolio, Orders, Wallet, Admin

- Portfolio: exposure, open positions, PnL, average entry, current price, max payout, scenario outcomes.
- Orders: open/filled/cancelled states, cancel action, stable table rows.
- Wallet: simulated funds only, available/locked/total, ledger, test deposit.
- Admin: review queue, risk status, automation checks, maker-checker language, evidence clarity.

## Motion

Motion is subtle and state-driven only.

- Use 150-250ms transitions for hover, focus, tabs, drawers, and confirmation states.
- Do not animate layout properties unless necessary.
- No decorative floating animations or choreographed page-load sequences.
- Respect `prefers-reduced-motion`.

## Icons And Assets

- Use Lucide for functional UI icons.
- Use restrained 3D category icons only for category identity and empty states.
- Do not use emoji as UI icons.
- Do not use hand-drawn SVG illustrations as placeholders.

## Accessibility

- Minimum WCAG AA contrast.
- Visible focus states on all interactive elements.
- Screen-reader labels for icon-only buttons.
- Keyboard-operable dialogs, menus, filters, and trade ticket.
- Reduced-motion mode honored.
- Tables and charts must have readable labels and not rely on color alone.

## Implementation Notes

- Keep `NEXT_PUBLIC_USE_MOCK_DATA` behavior intact.
- No backend API changes are implied by the design system.
- Keep the UI serious: trade, order, contract, position, exposure, settlement; avoid bet/gamble language.
