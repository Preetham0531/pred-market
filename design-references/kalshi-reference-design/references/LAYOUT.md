# Layout Reference

> Auto-extracted from live DOM. Use this to understand how the site is structured spatially.

## Spacing System

**Base grid:** 4px

**Scale:** `2, 4, 6, 8, 12, 16, 24, 32, 80` px

| Spacing | Semantic Use |
|---------|-------------|
| 4px | Tight — within a component |
| 8px | Medium — between sibling items |
| 16px | Wide — between sections |
| 32px | Vast — major section breaks |

## Flex Layouts

| Element | Direction | Justify | Align | Gap | Children |
|---------|-----------|---------|-------|-----|----------|
| `div.flex.flex-col` | column | — | — | — | 3 |
| `div.flex.flex-1` | row | — | — | — | 1 |
| `nav.flex.min-h-7` | row | — | center | — | 2 |
| `div.pointer-events-auto.flex` | row | — | — | — | 1 |
| `div.flex.flex-col` | column | — | — | — | 2 |
| `div.flex.flex-col` | column | center | — | 4px | 2 |
| `div.px-3.sm:px-1` | row | — | — | — | 2 |
| `div.flex.justify-between` | row | space-between | — | — | 2 |
| `div.relative.flex` | row | — | center | — | 2 |
| `div.flex.items-center` | row | — | center | 8px | 2 |
| `div.flex.items-center` | row | end | center | 8px | 3 |
| `div.flex.flex-col` | column | — | — | 16px | 5 |
| `div.flex.flex-col` | column | — | — | 24px | 7 |
| `div.flex.gap-4` | row | — | — | 32px | 2 |
| `div.flex.flex-col` | column | — | — | 24px | 2 |

## Grid Layouts

| Element | Template Columns | Gap | Children |
|---------|-----------------|-----|----------|
| `div.grid.gap-3` | `276px 276px 276px 276px` | 24px | 4 |
| `div.flex-1.grid` | `267.328px 267.328px 267.344px` | 24px | 3 |

## Structural Containers

### `<nav>` (`nav.flex.min-h-7`)

```
display:          flex
flex-direction:   row
justify-content:  —
align-items:      center
children:         2
```

### `<footer>` (`footer.bg-fill-x60.dark:bg-surface-x20`)

```
display:          block
padding:          24px 16px 16px
children:         1
```

### `<footer>` (`footer.bg-fill-x60.dark:bg-surface-x20`)

```
display:          block
padding:          32px 16px 24px
children:         1
```

## Layout Rules

- **Container max-width:** `1320px` — always center with `margin: auto`
- Primary layout system: **Flexbox**
- Secondary layout system: **CSS Grid** (used for card grids and multi-column layouts)
- Every spacing value must be a multiple of **4px**
- Never use arbitrary margin/padding values outside the spacing scale

