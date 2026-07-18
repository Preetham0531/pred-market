---
name: pred-market-design
description: Design system skill for pred-market. Activate when building UI components, pages, or any visual elements. Provides exact color tokens, typography scale, spacing grid, component patterns, and craft rules. Read references/DESIGN.md before writing any CSS or JSX.
---

# pred-market Design System

You are building UI for **pred-market**. Light-themed, neutral palette, sans-serif typography (sans-serif), compact density on a 4px grid, expressive motion.

## Design Philosophy

- **Layered depth** — use shadow tokens to create a sense of physical layering. Each elevation level has a specific shadow.
- **Solid colors only** — no gradients anywhere. Every surface is a single flat color.
- **Single typeface** — sans-serif carries all text. Hierarchy comes from size, weight, and color — never font mixing.
- **compact density** — 4px base grid. Every dimension is a multiple of 4.
- **neutral palette** — the color temperature runs neutral, matching the sans-serif typography.
- **Restrained accent** — `#b9cbd7` is the only pop of color. Used exclusively for CTAs, links, focus rings, and active states.
- **Expressive motion** — animations are an integral part of the experience. Use spring physics and layout animations.
- **Lucide icons** — use Lucide for all iconography. Do not mix icon libraries.

## Color System

### Core Palette

| Role | Token | Hex | Use |
|------|-------|-----|-----|
| Background | `--background` | `#f4f6f2` | Page/app background |
| Surface | `--surface` | `#e0efe6` | Cards, panels, modals |
| Text Primary | `--text-primary` | `#17201b` | Headings, body text |
| Text Muted | `--text-muted` | `#abcbb8` | Captions, placeholders |
| Accent | `--accent` | `#b9cbd7` | CTAs, links, focus rings |
| Border | `--border` | `#56645d` | Dividers, card borders |

### Status Colors

| Status | Hex | Use |
|--------|-----|-----|
| Success | `#1f6846` | Confirmations, positive trends |
| Warning | `#d7c17f` | Caution states, pending items |
| Danger | `#dbb3ac` | Errors, destructive actions |

### Extended Palette

- **border:** `#d8dfd5`
- **border-strong:** `#c4cfc0`
- **primary-strong:** `#164f35`

### CSS Variable Tokens

```css
--background: #f4f6f2;
--foreground: #17201b;
--muted: #56645d;
--surface-muted: #edf1eb;
--border: #d8dfd5;
--border-strong: #c4cfc0;
--primary: #1f6846;
--primary-strong: #164f35;
--primary-soft: #e0efe6;
--primary-border: #abcbb8;
--green-border: #afcfba;
--blue-border: #b9cbd7;
--brass-border: #d7c17f;
--red-border: #dbb3ac;
```

## Typography

### Font Stack

- **sans-serif** — Heading 1, Heading 2, Heading 3, Body, Caption

### Type Scale

| Role | Family | Size | Weight |
|------|--------|------|--------|
| Heading 1 | sans-serif | 48px / 3rem | 700 |
| Heading 2 | sans-serif | 32px / 2rem | 600 |
| Heading 3 | sans-serif | 24px / 1.5rem | 600 |
| Body | sans-serif | 16px / 1rem | 400 |
| Caption | sans-serif | 12px / 0.75rem | 400 |

### Typography Rules

- All text uses **sans-serif** — never add another font family
- Max 3-4 font sizes per screen
- Headings: weight 600-700, body: weight 400
- Use color and opacity for text hierarchy, not additional font sizes
- Line height: 1.5 for body, 1.2 for headings

## Spacing & Layout

### Base Grid: 4px

Every dimension (margin, padding, gap, width, height) must be a multiple of **4px**.

### Spacing Scale

`4, 8, 12, 16, 20, 24, 32, 40, 48, 64` px

### Spacing as Meaning

| Spacing | Use |
|---------|-----|
| 4-8px | Tight: related items (icon + label, avatar + name) |
| 12-16px | Medium: between groups within a section |
| 24-32px | Wide: between distinct sections |
| 48px+ | Vast: major page section breaks |

### Border Radius

Scale: `4px, 6px, 8px`
Default: `6px`

## Component Patterns

### Card

```css
.card {
  background: #e0efe6;
  border: 1px solid #56645d;
  border-radius: 6px;
  padding: 16px;
  box-shadow: var(--shadow-hairline);
}
```

```html
<div class="card">
  <h3>Card Title</h3>
  <p>Card content goes here.</p>
</div>
```

### Button

```css
/* Primary */
.btn-primary {
  background: #b9cbd7;
  color: #17201b;
  border-radius: 6px;
  padding: 8px 16px;
  font-weight: 500;
  transition: opacity 150ms ease;
}
.btn-primary:hover { opacity: 0.9; }

/* Ghost */
.btn-ghost {
  background: transparent;
  border: 1px solid #56645d;
  color: #17201b;
  border-radius: 6px;
  padding: 8px 16px;
}
```

```html
<button class="btn-primary">Get Started</button>
<button class="btn-ghost">Learn More</button>
```

### Input

```css
.input {
  background: #f4f6f2;
  border: 1px solid #56645d;
  border-radius: 6px;
  padding: 8px 12px;
  color: #17201b;
  font-size: 14px;
}
.input:focus { border-color: #b9cbd7; outline: none; }
```

```html
<input class="input" type="text" placeholder="Search..." />
```

### Badge / Chip

```css
.badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 8px;
  border-radius: 9999px;
  font-size: 12px;
  font-weight: 500;
  background: #e0efe6;
  color: #abcbb8;
}
```

```html
<span class="badge">New</span>
<span class="badge">Beta</span>
```

### Modal / Dialog

```css
.modal-backdrop { background: rgba(0, 0, 0, 0.6); }
.modal {
  background: #e0efe6;
  border: 1px solid #56645d;
  border-radius: 8px;
  padding: 24px;
  max-width: 480px;
  width: 90vw;
  box-shadow: var(--shadow-hairline);
}
```

```html
<div class="modal-backdrop">
  <div class="modal">
    <h2>Dialog Title</h2>
    <p>Dialog content.</p>
    <button class="btn-primary">Confirm</button>
    <button class="btn-ghost">Cancel</button>
  </div>
</div>
```

### Table

```css
.table { width: 100%; border-collapse: collapse; }
.table th {
  text-align: left;
  padding: 8px 12px;
  font-weight: 500;
  font-size: 12px;
  color: #abcbb8;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-bottom: 1px solid #56645d;
}
.table td {
  padding: 12px;
  border-bottom: 1px solid #56645d;
}
```

```html
<table class="table">
  <thead><tr><th>Name</th><th>Status</th><th>Date</th></tr></thead>
  <tbody>
    <tr><td>Item One</td><td>Active</td><td>Jan 1</td></tr>
    <tr><td>Item Two</td><td>Pending</td><td>Jan 2</td></tr>
  </tbody>
</table>
```

### Navigation

```css
.nav {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  border-bottom: 1px solid #56645d;
}
.nav-link {
  color: #abcbb8;
  padding: 8px 12px;
  border-radius: 6px;
  transition: color 150ms;
}
.nav-link:hover { color: #17201b; }
.nav-link.active { color: #b9cbd7; }
```

```html
<nav class="nav">
  <a href="/" class="nav-link active">Home</a>
  <a href="/about" class="nav-link">About</a>
  <a href="/pricing" class="nav-link">Pricing</a>
  <button class="btn-primary" style="margin-left: auto">Get Started</button>
</nav>
```

### Extracted Components

These components were found in the codebase:

**AppShell** (`components/app-shell.tsx`)
- Props: `variant`, `size`
- Styles: `bg-[var(--surface)]`, `border-r`, `px-3`, `text-sm`, `shadow-sm`

**AuthPanel** (`components/auth-panel.tsx`)
- Variants: `trader`, `admin`
- Props: `mode`
- Styles: `bg-[var(--primary-soft)]`, `rounded-md`, `mx-auto`, `text-sm`, `shadow-sm`

**Breadcrumbs** (`components/breadcrumbs.tsx`)
- Styles: `gap-1`, `text-xs`

**Category3dIcon** (`components/category-3d-icon.tsx`)
- Variants: `slug`, `iconTone`, `sm`, `md`, `shortName`, `lg`
- Props: `category`, `size`, `className`
- Styles: `bg-linear-to-br`, `rounded-md`, `text-white`, `drop-shadow`

**MarketCard** (`components/market-card.tsx`)
- Props: `market`, `compact`
- Styles: `bg-[var(--surface)]`, `rounded-md`, `p-3`, `line-clamp-2`

**MarketDiscovery** (`components/market-discovery.tsx`)
- Variants: `all`, `trending`
- Props: `label`, `value`
- Styles: `bg-[var(--red-soft)]`, `rounded-md`, `mx-auto`, `text-[var(--red-text)]`

**MarketTable** (`components/market-table.tsx`)
- Props: `markets`
- Styles: `rounded-md`, `px-3`, `text-sm`

**Metric** (`components/metric.tsx`)
- Variants: `neutral`, `green`, `red`, `blue`
- Props: `label`, `value`, `detail`, `tone`, `className`
- Styles: `rounded-md`, `mt-1`, `text-[11px]`

**OrderBook** (`components/order-book.tsx`)
- Variants: `green`, `red`
- Props: `market`, `price`, `quantity`, `empty`, `index`
- Styles: `bg-[var(--brass-soft)]`, `rounded-t-md`, `px-2`, `text-right`

**OrdersWorkspace** (`components/orders-workspace.tsx`)
- Props: `open`, `filled`, `cancelled`
- Styles: `bg-[var(--red-soft)]`, `rounded-md`, `space-y-5`, `text-2xl`

## Animation & Motion

This project uses **expressive motion**. Animations are part of the design language.

### Framer Motion

```tsx
// Standard enter animation
<motion.div
  initial={{ opacity: 0, y: 8 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.3, ease: "easeOut" }}
/>

// List stagger
const container = { hidden: {}, show: { transition: { staggerChildren: 0.05 } } }
const item = { hidden: { opacity: 0, y: 8 }, show: { opacity: 1, y: 0 } }
```

### CSS Animations

- `animate-spin`
- `animate-pulse`

### Motion Guidelines

- **Duration:** 150-300ms for micro-interactions, 300-500ms for page transitions
- **Easing:** `ease-out` for enters, `ease-in` for exits
- **Direction:** Elements enter from bottom/right, exit to top/left
- **Reduced motion:** Always respect `prefers-reduced-motion` — disable animations when set

## Depth & Elevation

### Shadow Tokens

- Raised (cards, buttons): `var(--shadow-hairline)`

## Anti-Patterns (Never Do)

- **No gradients** — solid colors only, everywhere
- **No blur effects** — no backdrop-blur, no filter: blur()
- **No zebra striping** — tables and lists use borders for separation
- **No invented colors** — every hex value must come from the palette above
- **No arbitrary spacing** — every dimension is a multiple of 4px
- **No extra fonts** — only sans-serif are allowed
- **No arbitrary border-radius** — use the scale: 4px, 6px, 8px
- **No opacity for disabled states** — use muted colors instead
- **No pill shapes** — this design doesn't use rounded-full / 9999px radius

## Workflow

1. **Read** `references/DESIGN.md` before writing any UI code
2. **Pick colors** from the Color System section — never invent new ones
3. **Set typography** — sans-serif only, using the type scale
4. **Build layout** on the 4px grid — check every margin, padding, gap
5. **Match components** to patterns above before creating new ones
6. **Apply elevation** — use shadow tokens
7. **Validate** — every value traces back to a design token. No magic numbers.

## Brand Spec

- **Brand color:** `#b9cbd7`
- **Brand typeface:** sans-serif

## Quick Reference

```
Background:     #f4f6f2
Surface:        #e0efe6
Text:           #17201b / #abcbb8
Accent:         #b9cbd7
Border:         #56645d
Font:           sans-serif
Spacing:        4px grid
Radius:         6px
Frameworks:     Tailwind CSS, React, Next.js
Icons:          Lucide
Components:     44 detected
```

## When to Trigger

Activate this skill when:
- Creating new components, pages, or visual elements for pred-market
- Writing CSS, Tailwind classes, styled-components, or inline styles
- Building page layouts, templates, or responsive designs
- Reviewing UI code for design consistency
- The user mentions "pred-market" design, style, UI, or theme
- Generating mockups, wireframes, or visual prototypes

---

# Full Reference Files

> Every output file is embedded below. Claude has full design system context from /skills alone.

## Design System Tokens (DESIGN.md)

# pred-market DESIGN.md

> Auto-generated design system — reverse-engineered via static analysis by skillui.
> Frameworks: Tailwind CSS 4.3.2 + React 19.2.7 + Next.js 16.2.10
> Colors: 12 · Fonts: 1 · Components: 44
> Icon library: Lucide · State: not detected
> Primary theme: light · Dark mode toggle: no · Motion: expressive

---

## 1. Visual Theme & Atmosphere

This is a **light-themed** interface with a neutral, approachable feel. The light background emphasizes content clarity. Typography uses **sans-serif** throughout — a clean, modern choice that maintains consistency. Spacing follows a **4px base grid** (compact density), with scale: 4, 8, 12, 16, 20, 24, 32, 40px. The accent color **#b9cbd7** anchors interactive elements (buttons, links, focus rings). Motion is expressive — spring physics, layout animations, and staggered reveals are part of the visual language.

---

## 2. Color Palette & Roles

| Token | Hex | Role | Use |
|---|---|---|---|
| background | `#f4f6f2` | background | Page background, darkest surface |
| primary-soft | `#e0efe6` | surface | Card and panel backgrounds |
| foreground | `#17201b` | text-primary | Headings and body text |
| primary-border | `#abcbb8` | text-muted | Captions, placeholders, secondary info |
| muted | `#56645d` | border | Dividers, card borders, outlines |
| blue-border | `#b9cbd7` | accent | CTAs, links, focus rings, active states |
| red-border | `#dbb3ac` | danger | Error states, destructive actions |
| primary | `#1f6846` | success | Success states, positive indicators |
| brass-border | `#d7c17f` | warning | Warning states, caution indicators |
| border | `#d8dfd5` | unknown | Palette color |
| border-strong | `#c4cfc0` | unknown | Palette color |
| primary-strong | `#164f35` | unknown | Palette color |

### CSS Variable Tokens

```css
--background: #f4f6f2;
--foreground: #17201b;
--muted: #56645d;
--surface-muted: #edf1eb;
--border: #d8dfd5;
--border-strong: #c4cfc0;
--primary: #1f6846;
--primary-strong: #164f35;
--primary-soft: #e0efe6;
--primary-border: #abcbb8;
--green-border: #afcfba;
--blue-border: #b9cbd7;
--brass-border: #d7c17f;
--red-border: #dbb3ac;
```


---

## 3. Typography Rules

**Font Stack:**
- **sans-serif** — Heading 1, Heading 2, Heading 3, Body, Caption

| Role | Font | Size | Weight |
|---|---|---|---|
| Heading 1 | sans-serif | 48px / 3rem | 700 |
| Heading 2 | sans-serif | 32px / 2rem | 600 |
| Heading 3 | sans-serif | 24px / 1.5rem | 600 |
| Body | sans-serif | 16px / 1rem | 400 |
| Caption | sans-serif | 12px / 0.75rem | 400 |

**Typographic Rules:**
- Use **sans-serif** for all text — do not mix font families
- Maintain consistent hierarchy: no more than 3-4 font sizes per screen
- Headings use bold (600-700), body uses regular (400)
- Line height: 1.5 for body text, 1.2 for headings
- Use color and opacity for secondary hierarchy, not additional font sizes


---

## 4. Component Stylings

### Layout (26)

**Category3dIcon** — `components/category-3d-icon.tsx`
- Variants: `slug`, `iconTone`, `sm`, `md`, `shortName`, `lg`
- Props: `category`, `size`, `className`
- Key Styles: `rounded-md`, `border-white/35`, `bg-linear-to-br`, `drop-shadow`

```tsx
<div
      className={cn(
        "relative grid shrink-0 place-items-center rounded-lg bg-linear-to-br shadow-[inset_0_1px_0_rgba(255,255,255,0.85
```

**MarketDiscovery** — `components/market-discovery.tsx`
- Variants: `all`, `trending`
- Props: `label`, `value`
- Key Styles: `rounded-md`, `border-[var(--border)]`, `bg-[var(--red-soft)]`, `mx-auto`, `text-base`, `font-semibold`, `pointer-events-none`
- State: useState

```tsx
<div className="exchange-panel mx-auto max-w-3xl rounded-md p-5" role="alert">
        <div className="flex items-start gap-3">
          <div className="grid h-10 w-10 shrink-0 place-items-center rounded-md bg-[var(--red-soft
```

**OrderBook** — `components/order-book.tsx`
- Variants: `green`, `red`
- Props: `market`, `price`, `quantity`, `empty`, `index`
- Key Styles: `rounded-t-md`, `border-x`, `bg-[var(--brass-soft)]`, `px-2`, `text-sm`, `font-semibold`

```tsx
<div>
      <div className="exchange-table-header grid grid-cols-[72px_1fr_1fr] rounded-t-md px-2 py-2">
        <span>{label}</span>
        <span className="text-right">Qty</span>
        <span className="text-right">Total</span>
      </div>
      <div className="overflow-hidden rounded-b-md border-x border-b border-[var(--border
```

**PortfolioExposureChart** — `components/portfolio-exposure-chart.tsx`
- Key Styles: `rounded-md`, `border-[var(--border)]`, `bg-[var(--surface-muted)]`, `p-3`, `text-sm`, `font-semibold`

```tsx
<div className="exchange-panel h-[260px] rounded-md p-3">
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-semibold">Exposure by category</h2>
        <span className="rounded-md border border-[var(--border
```

**ProbabilityChart** — `components/probability-chart.tsx`
- Props: `data`
- Key Styles: `rounded-md`, `border-[var(--border)]`, `bg-[var(--surface-muted)]`, `p-3`, `text-sm`, `font-semibold`, `cursor-pointer`
- State: useState

```tsx
<div className="exchange-panel rounded-md p-3">
      <div className="mb-3 flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-sm font-semibold">Probability history</h2>
          <p className="text-xs text-[var(--muted
```

**SuggestMarketFlow** — `components/suggest-market-flow.tsx`
- Variants: `Binary`, `Threshold`, `Conditional`
- Props: `category_slug`, `market_type`, `question`, `outcomes`, `source`, `resolution_rule`
- Key Styles: `rounded-md`, `border-[var(--border)]`, `bg-[var(--surface)]`, `p-6`, `text-sm`, `font-semibold`, `focus:ring-2`
- State: useState

```tsx
<div className="grid gap-5 lg:grid-cols-[280px_1fr]">
      <aside className="rounded-md border border-[var(--border
```

**Button** — `components/ui/button.tsx`
- Variants: `variant`, `primary`, `hover`, `secondary`, `ghost`, `danger`, `size`
- Props: `className`, `variant`, `size`
- Key Styles: `rounded-md`, `gap-2`, `text-sm`, `font-medium`, `cursor-pointer`

**WalletWorkspace** — `components/wallet-workspace.tsx`
- Key Styles: `rounded-md`, `border-[var(--red-border)]`, `bg-[var(--red-soft)]`, `space-y-5`, `text-2xl`, `font-semibold`
- State: useState

```tsx
<div className="space-y-5">
      <div>
        <h1 className="text-2xl font-semibold">Wallet</h1>
        <p className="mt-1 text-sm text-[var(--muted
```

*...and 18 more layout components.*

### Navigation (8)

**AppShell** — `components/app-shell.tsx`
- Props: `variant`, `size`
- Key Styles: `rounded-md`, `border-r`, `bg-[var(--surface)]`, `px-3`, `text-sm`, `font-semibold`, `shadow-sm`
- Animation: framer-motion, transition: {duration: 0.22, ease: "easeOut"}, animate: {opacity: 1, y: 0}
- State: useState

```tsx
<aside className="hidden h-dvh w-[264px] shrink-0 border-r border-[var(--border
```

**Breadcrumbs** — `components/breadcrumbs.tsx`
- Key Styles: `gap-1`, `text-xs`, `hover:text-[var(--foreground)]`

```tsx
<nav aria-label="Breadcrumb" className="min-w-0">
      <ol className="hidden min-w-0 items-center gap-1 text-xs text-[var(--muted
```

**MarketCard** — `components/market-card.tsx`
- Props: `market`, `compact`
- Key Styles: `rounded-md`, `border-[var(--border)]`, `bg-[var(--surface)]`, `p-3`, `text-sm`, `font-semibold`, `hover:border-[var(--primary-border)]`
- Animation: hover-transforms

```tsx
<Link
      href={`/markets/${market.id}`}
      className="group block rounded-md border border-[var(--border
```

**MarketTable** — `components/market-table.tsx`
- Props: `markets`
- Key Styles: `rounded-md`, `px-3`, `text-sm`, `font-medium`, `hover:bg-[var(--surface-muted)]`

```tsx
<div className="exchange-panel overflow-hidden rounded-md">
      <div className="exchange-table-header hidden grid-cols-[minmax(260px,1fr
```

**OrdersWorkspace** — `components/orders-workspace.tsx`
- Props: `open`, `filled`, `cancelled`
- Key Styles: `rounded-md`, `border-[var(--red-border)]`, `bg-[var(--red-soft)]`, `space-y-5`, `text-2xl`, `font-semibold`, `hover:text-[var(--primary-strong)]`
- State: useState

```tsx
<div className="space-y-5">
      <div>
        <h1 className="text-2xl font-semibold">Orders</h1>
        <p className="mt-1 text-sm text-[var(--muted
```

**TradeTicket** — `components/trade-ticket.tsx`
- Variants: `idle`, `submitting`, `accepted`, `rejected`, `partial`
- Props: `market`
- Key Styles: `rounded-md`, `border-[var(--border)]`, `bg-[var(--surface)]`, `mb-3`, `text-sm`, `font-semibold`, `shadow-lg`, `hover:bg-[var(--surface-muted)]`
- Animation: tw-animate-spin
- State: useState

```tsx
<>
      <div className="mb-3 flex items-center justify-between">
        <div>
          <h2 className="text-sm font-semibold">Trade ticket</h2>
          <p className="text-xs text-[var(--muted
```

**Tabs** — `components/ui/tabs.tsx`
- Key Styles: `rounded-md`, `border-[var(--border)]`, `bg-[var(--surface-muted)]`, `gap-1`, `text-xs`, `font-medium`

```tsx
<TabsPrimitive.List
      className={cn(
        "inline-flex h-9 items-center gap-1 rounded-md border border-[var(--border
```

**NotFound** — `app/not-found.tsx`
- Props: `variant`, `size`
- Key Styles: `rounded-md`, `border-[var(--border)]`, `bg-[var(--surface)]`, `mx-auto`, `text-2xl`, `font-semibold`

```tsx
<section className="mx-auto grid max-w-xl place-items-center rounded-md border border-[var(--border
```

### Data Display (3)

**Metric** — `components/metric.tsx`
- Variants: `neutral`, `green`, `red`, `blue`
- Props: `label`, `value`, `detail`, `tone`, `className`
- Key Styles: `rounded-md`, `mt-1`, `text-xs`, `font-semibold`

```tsx
<div className={cn("exchange-panel rounded-md p-3", className
```

**StatusBadge** — `components/status-badge.tsx`
- Props: `status`

**Badge** — `components/ui/badge.tsx`
- Variants: `neutral`, `green`, `blue`, `brass`, `red`
- Props: `children`, `tone`, `className`
- Key Styles: `rounded-md`, `px-2`, `text-xs`, `font-medium`

```tsx
<span
      className={cn(
        "inline-flex h-6 items-center rounded-md border px-2 text-xs font-medium",
        tones[tone],
        className
```

### Data Input (3)

**AuthPanel** — `components/auth-panel.tsx`
- Variants: `trader`, `admin`
- Props: `mode`
- Key Styles: `rounded-md`, `border-[var(--primary-border)]`, `bg-[var(--primary-soft)]`, `mx-auto`, `text-sm`, `font-medium`, `shadow-sm`, `hover:text-[var(--foreground)]`
- Animation: tw-animate-spin
- State: useState

```tsx
<section className="mx-auto grid min-h-dvh w-full max-w-6xl items-center gap-8 px-4 py-8 lg:grid-cols-[1fr_430px]">
      <div className="max-w-2xl">
        <div className="mb-6 inline-flex items-center gap-2 rounded-md border border-[var(--primary-border
```

**Input** — `components/ui/input.tsx`
- Key Styles: `rounded-md`, `border-[var(--border)]`, `bg-[var(--surface)]`, `px-3`, `text-sm`, `focus:border-[var(--primary)]`
- State: forwardRef

```tsx
<input
      type={type}
      className={cn(
        "h-9 w-full rounded-md border border-[var(--border
```

**Select** — `components/ui/select.tsx`
- Props: `value`, `onValueChange`, `options`, `label`, `className`
- Key Styles: `rounded-md`, `border-[var(--border)]`, `bg-[var(--surface)]`, `p-1`, `text-sm`, `shadow-xl`, `cursor-pointer`

```tsx
<SelectPrimitive.Root value={value} onValueChange={onValueChange}>
      <SelectPrimitive.Trigger
        aria-label={label}
        className={cn(
          "inline-flex h-9 w-full cursor-pointer items-center justify-between gap-2 rounded-md border border-[var(--border
```

### Feedback (2)

**Error** — `app/error.tsx`
- Key Styles: `rounded-md`, `border-[var(--red-border)]`, `bg-[var(--red-soft)]`, `mx-auto`, `text-2xl`, `font-semibold`

```tsx
<section className="mx-auto grid max-w-xl place-items-center rounded-md border border-[var(--red-border
```

**Loading** — `app/loading.tsx`
- Key Styles: `rounded-md`, `border-[var(--border)]`, `bg-[var(--surface-muted)]`, `space-y-4`
- Animation: tw-animate-pulse

```tsx
<div className="space-y-4">
      <div className="h-8 w-56 animate-pulse rounded-md bg-[var(--surface-muted
```

### Other (2)

**AuthProvider** — `components/auth-provider.tsx`
- Props: `email`, `password`
- State: useState, useContext

**Providers** — `components/providers.tsx`
- State: useState

```tsx
<QueryClientProvider client={queryClient}>
      <AuthProvider>
        <RealtimeBridge />
        {children}
      </AuthProvider>
    </QueryClientProvider>
```



---

## 5. Layout Principles

- **Base spacing unit:** 4px
- **Spacing scale:** 4, 8, 12, 16, 20, 24, 32, 40, 48, 64
- **Border radius:** 4px, 6px, 8px
- **Grid usage:** `grid-cols-5`, `grid-cols-2`, `grid-cols-3`
- **Container:** Tailwind `container` class with responsive padding

**Spacing as Meaning:**
| Spacing | Use |
|---|---|
| 4-8px | Tight: related items within a group |
| 12-16px | Medium: between groups |
| 24-32px | Wide: between sections |
| 48px+ | Vast: major section breaks |


---

## 6. Depth & Elevation

### Raised — cards, buttons, interactive elements

- `var(--shadow-hairline)`



---

## 7. Animation & Motion

This project uses **expressive motion**. Animations are an integral part of the experience.

### Framer Motion Patterns

```tsx
// Standard enter animation
<motion.div
  initial={{ opacity: 0, y: 8 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.3, ease: "easeOut" }}
/>

// List stagger
const container = {
  hidden: {},
  show: { transition: { staggerChildren: 0.05 } }
}
const item = {
  hidden: { opacity: 0, y: 8 },
  show: { opacity: 1, y: 0 }
}
```

### CSS Animations

- `@keyframes animate-spin`
- `@keyframes animate-pulse`

### Animated Components

- **AppShell**: framer-motion, transition: {duration: 0.22, ease: "easeOut"}, animate: {opacity: 1, y: 0}
- **AuthPanel**: tw-animate-spin
- **MarketCard**: hover-transforms
- **TradeTicket**: tw-animate-spin
- **Loading**: tw-animate-pulse

### Motion Guidelines

- Duration: 150-300ms for micro-interactions, 300-500ms for page transitions
- Easing: `ease-out` for enters, `ease-in` for exits
- Always respect `prefers-reduced-motion`


---

## 8. Do's and Don'ts

### Do's

- Use `#b9cbd7` for interactive elements (buttons, links, focus rings)
- Use `#f4f6f2` as the primary page background
- Use **sans-serif** for all UI text
- Follow the **4px** spacing grid for all margins, padding, and gaps
- Use the defined shadow tokens for elevation — see Section 6
- Use border-radius from the scale: 4px, 6px, 8px
- Reuse existing components from Section 4 before creating new ones
- Use **Lucide** for all icons

### Don'ts

- Don't introduce colors outside this palette — extend the design tokens first
- Don't mix font families — use sans-serif consistently
- Don't use arbitrary spacing values — stick to multiples of 4px
- Don't create custom box-shadow values outside the system tokens
- Don't use gradients — the design uses solid colors only
- Don't use arbitrary border-radius values — pick from the defined scale
- Don't duplicate component patterns — check Section 4 first
- Don't mix icon libraries — consistency matters
- Don't use backdrop-blur or blur effects

### Anti-Patterns (detected from codebase)

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
Background: #e0efe6
Border: 1px solid #56645d
Radius: 6px
Padding: 16px
Font: sans-serif
Use shadow tokens from Section 6.
```

### Build a Button

```
Primary: bg #b9cbd7, text white
Ghost: bg transparent, border #56645d
Padding: 8px 16px
Radius: 6px
Hover: opacity 0.9 or lighter shade
Focus: ring with #b9cbd7
```

### Build a Page Layout

```
Background: #f4f6f2
Max-width: 1280px, centered
Grid: 4px base
Responsive: mobile-first, breakpoints from Section 9
```

### Build a Stats Card

```
Surface: #e0efe6
Label: #abcbb8 (muted, 12px, uppercase)
Value: #17201b (primary, 24-32px, bold)
Status: use success/warning/danger from Section 2
```

### Build a Form

```
Input bg: #f4f6f2
Input border: 1px solid #56645d
Focus: border-color #b9cbd7
Label: #abcbb8 12px
Spacing: 16px between fields
Radius: 6px
```

### General Component

```
1. Read DESIGN.md Sections 2-6 for tokens
2. Colors: only from palette
3. Font: sans-serif, type scale from Section 3
4. Spacing: 4px grid
5. Components: match patterns from Section 4
6. Elevation: shadow tokens
```

