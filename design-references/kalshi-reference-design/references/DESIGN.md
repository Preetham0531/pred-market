# kalshi-reference DESIGN.md

> Auto-generated design system — reverse-engineered via static analysis by skillui.
> Frameworks: None detected
> Colors: 6 · Fonts: 2 · Components: 0
> Icon library: not detected · State: not detected
> Primary theme: dark · Dark mode toggle: no · Motion: none

## Visual Reference

**Match this design exactly** — study colors, fonts, spacing, and component shapes before writing any UI code.

![kalshi-reference Homepage](../screenshots/homepage.png)

---

## 1. Visual Theme & Atmosphere

This is a **dark-themed** interface with a flat, cool visual language. Elevation is achieved through color and border shifts rather than shadows — a clean, industrial aesthetic. Typography pairs **kalshiSans** for display/headings with **kalshiCondensed** for body text, creating clear visual hierarchy through type contrast. Spacing follows a **4px base grid** (compact density), with scale: 2, 4, 6, 8, 12, 16, 24, 32px. The accent color **#28cc95** anchors interactive elements (buttons, links, focus rings).

---

## 2. Color Palette & Roles

| Token | Hex | Role | Use |
|---|---|---|---|
| background | `#000000` | background | Page background, darkest surface |
| text-primary | `#ffffff` | text-primary | Headings and body text |
| accent | `#28cc95` | accent | CTAs, links, focus rings, active states |
| danger | `#d91616` | danger | Error states, destructive actions |
| success | `#0ac285` | success | Success states, positive indicators |
| info | `#265cff` | info | Informational highlights |

### CSS Variable Tokens

```css
--surface-foreground: #0000000d;
--surface-foreground-opaque: #f7f7f7;
--brand-primary: #28cc95;
--brand-secondary: #003221;
--bprogress-spinner-border-size: 2px;
```


---

## 3. Typography Rules

**Font Stack:**
- **kalshiCondensed** — Heading 1, Heading 2, Heading 3
- **kalshiSans** — Body, Caption

| Role | Font | Size | Weight |
|---|---|---|---|
| Heading 1 | kalshiCondensed | 48px / 3rem | 700 |
| Heading 2 | kalshiCondensed | 32px / 2rem | 600 |
| Heading 3 | kalshiCondensed | 24px / 1.5rem | 600 |
| Body | kalshiSans | 16px / 1rem | 400 |
| Caption | kalshiSans | 12px / 0.75rem | 400 |

**Typographic Rules:**
- Limit to 2 font families max per screen
- Use **kalshiCondensed** for body/UI text, **kalshiSans** for display/headings
- Maintain consistent hierarchy: no more than 3-4 font sizes per screen
- Headings use bold (600-700), body uses regular (400)
- Line height: 1.5 for body text, 1.2 for headings
- Use color and opacity for secondary hierarchy, not additional font sizes


---

## 4. Component Stylings

No components detected. Scan `src/components/` or `components/` to populate this section.

---

## 5. Layout Principles

- **Base spacing unit:** 4px
- **Spacing scale:** 2, 4, 6, 8, 12, 16, 24, 32, 80
- **Border radius:** 6px, 8px, 16px, 100px

**Spacing as Meaning:**
| Spacing | Use |
|---|---|
| 4-8px | Tight: related items within a group |
| 12-16px | Medium: between groups |
| 24-32px | Wide: between sections |
| 48px+ | Vast: major section breaks |


---

## 6. Depth & Elevation

No box-shadow values detected. The design uses a **flat visual style** — elevation is conveyed through background color shifts and borders rather than shadows.

**Elevation Strategy:**
| Level | Technique | Use |
|---|---|---|
| 0 — Base | Background color | Page background |
| 1 — Raised | Lighter surface + subtle border | Cards, panels |
| 2 — Floating | Even lighter surface + stronger border | Dropdowns, popovers |
| 3 — Overlay | Backdrop + modal surface | Modals, dialogs |


---

## 8. Do's and Don'ts

### Do's

- Use `#28cc95` for interactive elements (buttons, links, focus rings)
- Use `#000000` as the primary page background
- Pair **kalshiCondensed** (body) with **kalshiSans** (display) — these are the only allowed fonts
- Follow the **4px** spacing grid for all margins, padding, and gaps
- Use border and background shifts for elevation — not shadows
- Use border-radius from the scale: 6px, 8px, 16px, 100px

### Don'ts

- Don't introduce colors outside this palette — extend the design tokens first
- Don't introduce additional font families beyond kalshiCondensed and kalshiSans
- Don't use arbitrary spacing values — stick to multiples of 4px
- Don't add box-shadow — this design system uses flat elevation
- Don't use gradients — the design uses solid colors only
- Don't use arbitrary border-radius values — pick from the defined scale
- Don't use backdrop-blur or blur effects

### Anti-Patterns (detected from codebase)

- No box-shadow on any element
- No gradient backgrounds
- No blur or backdrop-blur effects
- No zebra striping on tables/lists


---

## 9. Responsive Behavior

No breakpoints detected. Consider adding responsive breakpoints to the design system.

---

## 10. Agent Prompt Guide

Use these as starting points when building new UI:

### Build a Card

```
Background: #000000
Border: 1px solid var(--border)
Radius: 16px
Padding: 16px
Font: kalshiCondensed
No shadows — use borders and surface colors for depth.
```

### Build a Button

```
Primary: bg #28cc95, text white
Ghost: bg transparent, border var(--border)
Padding: 8px 16px
Radius: 16px
Hover: opacity 0.9 or lighter shade
Focus: ring with #28cc95
```

### Build a Page Layout

```
Background: #000000
Max-width: 1280px, centered
Grid: 4px base
Responsive: mobile-first, breakpoints from Section 9
```

### Build a Stats Card

```
Surface: #000000
Label: var(--text-muted) (muted, 12px, uppercase)
Value: #ffffff (primary, 24-32px, bold)
Status: use success/warning/danger from Section 2
```

### Build a Form

```
Input bg: #000000
Input border: 1px solid var(--border)
Focus: border-color #28cc95
Label: var(--text-muted) 12px
Spacing: 16px between fields
Radius: 16px
```

### General Component

```
1. Read DESIGN.md Sections 2-6 for tokens
2. Colors: only from palette
3. Font: kalshiCondensed, type scale from Section 3
4. Spacing: 4px grid
5. Components: match patterns from Section 4
6. Elevation: flat, surface shifts
```
