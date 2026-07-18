# Kalshi Reference Pattern Extraction

This document extracts reusable product patterns from the SkillUI Pred-Market and Kalshi reference outputs. It is not a visual cloning brief.

Generated inputs:

- Pred-Market extraction: `pred-market-design/DESIGN.md`
- Kalshi reference extraction: `design-references/kalshi-reference-design/DESIGN.md`
- Kalshi supporting references: `design-references/kalshi-reference-design/references/`
- Kalshi screenshots: `design-references/kalshi-reference-design/screens/`

## Extraction Notes

The Kalshi reference was generated with:

```bash
skillui --url https://kalshi.com --mode ultra --screens 8 --out ./design-references --name kalshi-reference
```

The first run degraded because Playwright was unavailable to SkillUI. Playwright and Chromium were installed, then the command was rerun successfully. The final extraction captured computed colors, two font families, seven scroll frames, page screenshots, state screenshots, and keyframes. Top-level component detection remained limited, so this brief uses the generated DOM pattern references and screenshots rather than treating the Kalshi component inventory as complete.

## Do Not Copy

Do not copy Kalshi brand identity, colors, fonts, logos, assets, icons, copy, exact card layouts, exact spacing, exact nav labels, or exact page composition.

Pred-Market must keep its own source of truth:

- Calm light exchange terminal.
- Inter as the UI family.
- Muted green, slate, brass, red, off-white, and neutral surfaces from the Pred-Market design system.
- 4px spacing rhythm, 6-8px radius, compact tables, Lucide icons, restrained motion.
- Serious trading language: trade, order, contract, position, exposure, source, evidence, settlement.

## Reusable Patterns

### Density

Reusable pattern: high-density scanning should place more market decision data in the first viewport without making every module equal weight.

Adaptation for Pred-Market:

- Keep the table as the primary discovery surface for desktop.
- Use compact market cards only for featured movers, category pages, and mobile discovery.
- Limit top summary strips to decision-driving metrics: volume, open markets, liquidity, spread, closing soon, and biggest mover.
- Avoid large marketing sections inside authenticated or trading surfaces.
- Keep vertical gaps tight inside cards and rows; reserve larger gaps for major workspace boundaries.

### Hierarchy

Reusable pattern: market hierarchy should be clear in one scan:

- Market category or source context.
- Contract title.
- Close time or live status.
- Two strongest outcomes.
- Probability or price.
- Volume/liquidity.
- Related market count or spread.

Adaptation for Pred-Market:

- Discovery rows should prioritize title, source, status, close time, YES price, 24h move, volume, spread, and liquidity.
- Category dashboards should pair a left subcategory rail with a dense active-market area.
- Status labels must distinguish open, closing soon, paused, pending resolution, and settled.
- Source/evidence confidence belongs in discovery rows, not only on market detail pages.

### Market Cards

Reusable pattern: compact cards can work when each card behaves like a small order-analysis object rather than a decorative tile.

Adaptation for Pred-Market cards:

- Header: category, source, status, close time.
- Body: contract title with two visible outcomes.
- Outcome rows: label, probability/price, compact depth or spread cue, small directional bar.
- Footer: 24h volume, liquidity, market count or outcome count, watchlist state.
- Use cards for mobile, category pages, related markets, and movers. Do not replace the desktop market table with a card wall.

Do not copy Kalshi flag/team imagery or sports-card composition directly. Pred-Market should use its own category icons and source labels.

### Trade Panels

Reusable pattern: the trade panel should stay close to the market list/detail context and expose the order decision before submission.

Adaptation for Pred-Market:

- Desktop: sticky right trade ticket on market detail.
- Mobile: bottom action bar opens a bottom sheet.
- Controls: outcome selector, limit price, quantity, available balance, estimated cost, max payout, max loss, fee, implied probability.
- States: unauthenticated, invalid input, insufficient balance, preview ready, submitting, accepted, partial fill, rejected.
- Keep V1 limit-order-only behavior explicit.
- Add clear source/rule reminder near the ticket when close-time or settlement risk is material.

Do not introduce real-money deposit language into V1 trading surfaces. Keep simulated funds wording until payments/KYC are approved.

### Navigation

Reusable pattern: prediction-market navigation benefits from two layers:

- Global product nav for major workspaces.
- Category/subcategory rail or chips for market browsing.

Adaptation for Pred-Market:

- Keep the existing sidebar, top bar, breadcrumbs, command search, wallet/profile, and mobile bottom nav.
- On category pages, use a left subcategory rail on desktop and horizontal chips on mobile.
- On discovery, place search and category filters early on mobile.
- Keep filters close to the market list: category, status, close time, volume, liquidity, spread, watchlisted, and has position.
- Use clear reset/empty/error states so users can recover from over-filtering.

### Chart Treatment

Reusable pattern: charts should support trading decisions through context, not decoration.

Adaptation for Pred-Market:

- Probability chart remains the main visual on market detail.
- Add timeframe controls, volume context, and source/evidence markers.
- Keep chart surfaces flat and bordered, with restrained color.
- Pair chart states with text: loading, empty, stale, live, paused, closed.
- Avoid cinematic scroll motion or marketing-style chart animation inside the trading cockpit.

### Interaction And Motion

Reusable pattern: interactions should be fast, subtle, and state-driven.

Adaptation for Pred-Market:

- Use 150-250ms transitions for hover, focus, tabs, row updates, bottom sheets, and confirmations.
- Prefer background, border, opacity, and subtle transform changes.
- Preserve visible focus outlines and keyboard access.
- Respect `prefers-reduced-motion`.
- Do not adopt cinematic homepage scroll effects inside exchange workflows.

## Pred-Market Implementation Backlog

Use this backlog only when improving frontend surfaces. It is not a requirement to copy Kalshi pages.

1. Market discovery
   - Keep the desktop table primary.
   - Add optional compact card mode for mobile and category pages.
   - Add source/evidence text in rows.
   - Strengthen active filter chips and reset actions.

2. Category dashboards
   - Add left subcategory rail on desktop.
   - Add category chips on mobile.
   - Show top movers, closing soon, liquidity, and risk notices without burying the market list.

3. Market detail
   - Keep chart, order book, recent trades, rules/evidence, and trade ticket visible in one cockpit.
   - Make source/rule confidence visible near the header and ticket.
   - Keep order-book row heights stable during live updates.

4. Trade ticket
   - Preserve preview-before-submit.
   - Show invalid, unauthenticated, insufficient, accepted, partial, and rejected states.
   - Keep mobile bottom sheet reachable without covering critical market context.

5. Motion and polish
   - Use short state transitions only.
   - Add live-update highlights to rows and order-book levels.
   - Avoid decorative motion and scroll storytelling in trading surfaces.

## Acceptance Criteria For Future UI Work

- The UI still reads as Pred-Market, not Kalshi.
- Colors, typography, radius, and tone come from Pred-Market design docs.
- Market browsing improves scan speed and decision clarity.
- Trading actions remain careful, explicit, and auditable.
- Source, rules, and settlement confidence are visible before trading.
- Mobile users can search/filter/open a market without fighting the layout.
