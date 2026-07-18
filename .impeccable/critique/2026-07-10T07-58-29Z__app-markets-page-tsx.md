---
target: /markets
total_score: 20
p0_count: 0
p1_count: 3
timestamp: 2026-07-10T07-58-29Z
slug: app-markets-page-tsx
---
Method: dual-agent (A: 019f4b02-4f1a-78c2-8866-559964592a7d / B: 019f4b02-6bb6-7e91-9c6a-7209f206b842)

## Design Health Score

| # | Heuristic | Score | Key Issue |
|---|-----------|-------|-----------|
| 1 | Visibility of System Status | 2 | Failed market data still rendered authoritative zero metrics. |
| 2 | Match System / Real World | 3 | Exchange language is strong; some copy felt internal. |
| 3 | User Control and Freedom | 2 | Filters lacked clear reset/recovery affordances. |
| 4 | Consistency and Standards | 3 | Tokens, shell, badges, and table structure are consistent. |
| 5 | Error Prevention | 2 | Users could over-filter into a blank board with little guidance. |
| 6 | Recognition Rather Than Recall | 2 | Source/resolution cues were too weak in discovery rows. |
| 7 | Flexibility and Efficiency | 2 | Desktop command menu helps, but mobile scanning started too late. |
| 8 | Aesthetic and Minimalist Design | 2 | Too many equally weighted modules competed with the table. |
| 9 | Error Recovery | 1 | Error state lacked a retry and did not suppress false metrics. |
| 10 | Help and Documentation | 1 | Contextual help for spread, source, rules, and simulated mode was limited. |
| **Total** | | **20/40** | **Acceptable, but fragile under real use.** |

## Anti-Patterns Verdict

The interface is mostly not AI slop. It preserves the calm exchange-terminal direction, with consistent Inter typography, restrained off-white surfaces, muted green primary state, compact tables, and institutional language. The main risk is generic dashboard sameness: metric tiles, category tape, featured cards, and table all carry similar weight.

Deterministic scan returned `[]`. Browser overlay flagged single-font and cream-palette issues, but those are false positives for Pred-Market because `DESIGN.md` explicitly defines Inter as the single UI family and a low-chroma off-white exchange background.

## Overall Impression

The `/markets` page has a solid product foundation, but the board needed stronger trust handling under backend failure, a more mobile-first scanning path, better filter recovery, and clearer source/resolution confidence before a user opens a contract.

## What's Working

- The shell, breadcrumbs, command search, wallet/profile controls, and mobile nav create a predictable trading workspace.
- The market table is directionally right for an exchange board, with probability, movement, volume, spread, close time, and status.
- The visual system aligns with the documented calm terminal direction and avoids casino/sportsbook cues.

## Priority Issues

**[P1] Error state undermines market trust**
Why it matters: A trading UI cannot show zero liquidity or zero markets as truth when the data request failed.
Fix: Make data failure own the page, suppress aggregate metrics and table, show retry/status context, and reserve "No markets match filters" for successful empty results.
Suggested command: `$impeccable harden`

**[P1] Mobile starts with the wrong task**
Why it matters: Mobile traders need search/category scanning immediately; six metric cards consumed the first viewport.
Fix: Move search and category chips above metrics on mobile, collapse metrics, and keep the board action in the thumb path.
Suggested command: `$impeccable adapt`

**[P1] Discovery lacks contract-resolution confidence**
Why it matters: Pred-Market's product principles require users to understand source/rules before strategy decisions.
Fix: Add source/resolution context directly to market rows or tooltips.
Suggested command: `$impeccable polish`

**[P2] Filter system has no recovery affordance**
Why it matters: Users can stack filters and get stranded in an unexplained blank board.
Fix: Add clear filters, active filter summary, and better empty-state guidance.
Suggested command: `$impeccable harden`

**[P2] Loaded state risks generic dashboard sameness**
Why it matters: The table should feel like the product, not one module among many.
Fix: Keep the table primary, use fewer board metrics on constrained screens, and reserve cards for true movers or alerts.
Suggested command: `$impeccable polish`

## Persona Red Flags

**Alex, power trader:** Ctrl-K exists, but filter reset, watchlist-only, and table navigation are not yet accelerated enough.

**Sam, accessibility-dependent user:** Dense mobile table rows can lose context when headers are hidden; dynamic status messages need ARIA announcements.

**Casey, distracted mobile user:** Search and category scanning must appear before summary metrics; bottom navigation should not obscure the next action.

**Pred-Market trader/operator:** The board must distinguish backend failure, empty inventory, permissions, and over-filtering.

## Minor Observations

- "Density 9" reads like a control but is static.
- "Filter state preserved locally" is implementation copy.
- Command search needs explicit empty states.

## Questions to Consider

- What would `/markets` look like if the table were treated as the primary product surface?
- Should a trader ever see aggregate metrics when the data request failed?
- Is category browsing more important than spread/liquidity scanning in the first 10 seconds?
