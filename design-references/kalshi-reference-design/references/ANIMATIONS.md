# Animation Reference

> Cinematic motion design extracted from live DOM. Follow these specs exactly to recreate the experience.

## Motion Technology Stack

| Library | Type | Notes |
|---------|------|-------|
| **Web Animations API (12 active)** | animation |  |

## Scroll Journey

The page is **4,100px** tall. Each frame below shows what the user sees at that scroll depth.

> **Use these screenshots to understand WHAT animates, WHEN it animates, and HOW it moves.**

### 0% — Top / Hero
Scroll position: 0px

![Scroll 0%](../screens/scroll/scroll-000.png)

### 17% — Opening Section
Scroll position: 544px

![Scroll 17%](../screens/scroll/scroll-017.png)

### 33% — First Feature Section
Scroll position: 1,056px

![Scroll 33%](../screens/scroll/scroll-033.png)

### 50% — Mid-Page
Scroll position: 0px

![Scroll 50%](../screens/scroll/scroll-050.png)

### 67% — Lower Content
Scroll position: 0px

![Scroll 67%](../screens/scroll/scroll-067.png)

### 83% — Near Footer
Scroll position: 0px

![Scroll 83%](../screens/scroll/scroll-083.png)

### 100% — Bottom / Footer
Scroll position: 0px

![Scroll 100%](../screens/scroll/scroll-100.png)

## Scroll Animation Patterns

| Pattern | Library | Element Count | Duration | Delay | Easing |
|---------|---------|---------------|----------|-------|--------|
| parallax / sticky scroll | CSS | 1 | — | — | — |

### CSS Implementation

## CSS Keyframes (40 extracted)

### `@keyframes fadeIn`

Duration: `3s, 0.6s` · Easing: `linear, ease` · Delay: `0s, 0s` · Iteration: `1, 1` · Fill: `none, none`

Used by: `.animate-\[expandHeight_3s_linear\,fadeIn_0\.6s_ease\]`, `.animate-\[fadeIn_0\.1s_ease_forwards\]`, `.animate-\[fadeIn_0\.3s_ease-in-out\]`, `.animate-\[fadeIn_0\.3s_ease_0\.1s_forwards\,slideIntoPosition_0\.3s_ease_0\.1s_`

```css
@keyframes fadeIn {
  0% {
    opacity: 0;
  }
  100% {
    opacity: 1;
  }
}
```

> Opacity fade

### `@keyframes fadeOut`

Duration: `0.45s` · Easing: `cubic-bezier(0.66, 0, 0.34, 1)` · Delay: `0s` · Iteration: `1` · Fill: `none`

Used by: `.animate-fade-out`, `.data-\[state\=closed\]\:animate-\[fadeOut_0\.2s_ease\][data-state="closed"]`, `.data-\[state\=closed\]\:animate-quick-fade-out[data-state="closed"]`

```css
@keyframes fadeOut {
  0% {
    opacity: 1;
  }
  100% {
    opacity: 0;
  }
}
```

> Opacity fade

### `@keyframes hideshow`

Duration: `1.5s` · Easing: `ease` · Delay: `0s` · Iteration: `infinite` · Fill: `none`

Used by: `.animate-hideshow`, `.animate-hideshow-live`

```css
@keyframes hideshow {
  0% {
    opacity: 0.12;
  }
  30% {
    opacity: 1;
  }
  70% {
    opacity: 1;
  }
  100% {
    opacity: 0.12;
  }
}
```

> Opacity fade

### `@keyframes shimmerGradient`

Duration: `2s` · Easing: `linear` · Delay: `0s` · Iteration: `infinite` · Fill: `none`

Used by: `.animate-shimmer-gradient`, `.animate-skeleton-shimmer`

```css
@keyframes shimmerGradient {
  0% {
    background-position-x: 200%;
    background-position-y: 0px;
  }
  100% {
    background-position-x: -200%;
    background-position-y: 0px;
  }
}
```

> Background color/gradient shift · Background position (shimmer/scroll)

### `@keyframes shimmerGradient`

Duration: `2s` · Easing: `linear` · Delay: `0s` · Iteration: `infinite` · Fill: `none`

Used by: `.animate-shimmer-gradient`, `.animate-skeleton-shimmer`

```css
@keyframes shimmerGradient {
  0% {
    background-position-x: 200%;
    background-position-y: 0px;
  }
  100% {
    background-position-x: -200%;
    background-position-y: 0px;
  }
}
```

> Background color/gradient shift · Background position (shimmer/scroll)

### `@keyframes expandHeight`

Duration: `3s, 0.6s` · Easing: `linear, ease` · Delay: `0s, 0s` · Iteration: `1, 1` · Fill: `none, none`

Used by: `.animate-\[expandHeight_3s_linear\,fadeIn_0\.6s_ease\]`

```css
@keyframes expandHeight {
  0% {
    max-height: 0px;
  }
  100% {
    max-height: 1000px;
  }
}
```

> Dimension expand/collapse

### `@keyframes slideIntoPosition`

Duration: `0.3s, 0.3s` · Easing: `ease, ease` · Delay: `0.1s, 0.1s` · Iteration: `1, 1` · Fill: `forwards, forwards`

Used by: `.animate-\[fadeIn_0\.3s_ease_0\.1s_forwards\,slideIntoPosition_0\.3s_ease_0\.1s_`

```css
@keyframes slideIntoPosition {
  0% {
    transform: translateY(24px);
  }
  100% {
    transform: none;
  }
}
```

> Transform/motion animation

### `@keyframes heartbeat`

Duration: `3s` · Easing: `cubic-bezier(0.32, 0.93, 0.6, 1)` · Delay: `0s` · Iteration: `infinite` · Fill: `none`

Used by: `.animate-\[heartbeat_3s_cubic-bezier\(0\.32\,0\.93\,0\.60\,1\.00\)_infinite\]`

```css
@keyframes heartbeat {
  0% {
    stroke-width: 0;
    stroke-opacity: 1;
  }
  100% {
    stroke-width: 16px;
    stroke-opacity: 0;
  }
}
```

> Opacity fade · SVG stroke animation

### `@keyframes autoInsertPost`

Duration: `0.8s` · Easing: `ease-in-out` · Delay: `0s` · Iteration: `1` · Fill: `none`

Used by: `.animate-auto-insert-post`

```css
@keyframes autoInsertPost {
  0% {
    background-color: rgba(10, 194, 133, 0.12);
  }
  100% {
    background-color: rgba(0, 0, 0, 0);
  }
}
```

> Background color/gradient shift · Text color shift

### `@keyframes bounce`

Duration: `1s` · Easing: `ease` · Delay: `0s` · Iteration: `infinite` · Fill: `none`

Used by: `.animate-bounce`

```css
@keyframes bounce {
  0%, 100% {
    animation-timing-function: cubic-bezier(0.8, 0, 1, 1);
    transform: translateY(-25%);
  }
  50% {
    animation-timing-function: cubic-bezier(0, 0, 0.2, 1);
    transform: none;
  }
}
```

> Transform/motion animation

### `@keyframes slideLeft`

Duration: `0.3s` · Easing: `ease-in-out` · Delay: `0s` · Iteration: `1` · Fill: `none`

Used by: `.animate-bracket-slide-left`

```css
@keyframes slideLeft {
  0% {
    transform: translate(0px);
  }
  100% {
    transform: translate(-25%);
  }
}
```

> Transform/motion animation

### `@keyframes slideRight`

Duration: `0.3s` · Easing: `ease-in-out` · Delay: `0s` · Iteration: `1` · Fill: `none`

Used by: `.animate-bracket-slide-right`

```css
@keyframes slideRight {
  0% {
    transform: translate(-25%);
  }
  100% {
    transform: translate(0px);
  }
}
```

> Transform/motion animation

### `@keyframes expandGrid`

Duration: `80ms` · Easing: `ease-out` · Delay: `0s` · Iteration: `1` · Fill: `both`

Used by: `.animate-expand-grid`

```css
@keyframes expandGrid {
  0% {
    opacity: 0;
    grid-template-rows: 0fr;
  }
  100% {
    opacity: 1;
    grid-template-rows: 1fr;
  }
}
```

> Opacity fade

### `@keyframes grow`

Duration: `0.6s` · Easing: `ease` · Delay: `0s` · Iteration: `1` · Fill: `forwards`

Used by: `.animate-grow`

```css
@keyframes grow {
  0% {
    max-height: 88px;
  }
  100% {
    max-height: 800px;
  }
}
```

> Dimension expand/collapse

### `@keyframes heightContract`

Duration: `0.3s` · Easing: `ease-in-out` · Delay: `0s` · Iteration: `1` · Fill: `none`

Used by: `.animate-height-contract`

```css
@keyframes heightContract {
  0% {
    max-height: 100%;
  }
  100% {
    max-height: 50%;
  }
}
```

> Dimension expand/collapse

### `@keyframes liveBracketGradientShift`

Duration: `1.4s` · Easing: `ease-in-out` · Delay: `0s` · Iteration: `infinite` · Fill: `none`

Used by: `.animate-live-bracket-gradient`

```css
@keyframes liveBracketGradientShift {
  0% {
    background-color: rgba(217, 22, 22, 0.12);
  }
  50% {
    background-color: rgba(217, 22, 22, 0.5);
  }
  100% {
    background-color: rgba(217, 22, 22, 0.12);
  }
}
```

> Background color/gradient shift · Background position (shimmer/scroll)

### `@keyframes marquee`

Duration: `30s` · Easing: `linear` · Delay: `0s` · Iteration: `infinite` · Fill: `none`

Used by: `.animate-marquee`

```css
@keyframes marquee {
  0% {
    transform: translate(0px);
  }
  100% {
    transform: translate(-50%);
  }
}
```

> Transform/motion animation

### `@keyframes orderbookFlash`

Duration: `0.8s` · Easing: `ease` · Delay: `0s` · Iteration: `1` · Fill: `both`

Used by: `.animate-orderbook-flash`

```css
@keyframes orderbookFlash {
  0% {
    opacity: 0;
  }
  20% {
    opacity: 0.35;
  }
  100% {
    opacity: 0;
  }
}
```

> Opacity fade

### `@keyframes ping`

Duration: `1s` · Easing: `cubic-bezier(0, 0, 0.2, 1)` · Delay: `0s` · Iteration: `infinite` · Fill: `none`

Used by: `.animate-ping`

```css
@keyframes ping {
  75%, 100% {
    opacity: 0;
    transform: scale(2);
  }
}
```

> Fade + motion enter animation

### `@keyframes pulse`

Duration: `2s` · Easing: `cubic-bezier(0.4, 0, 0.6, 1)` · Delay: `0s` · Iteration: `infinite` · Fill: `none`

Used by: `.animate-pulse`

```css
@keyframes pulse {
  50% {
    opacity: 0.5;
  }
}
```

> Opacity fade

### `@keyframes rotate`

Duration: `0.8s` · Easing: `ease-in-out` · Delay: `0s` · Iteration: `1` · Fill: `none`

Used by: `.animate-rotate`

```css
@keyframes rotate {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}
```

> Transform/motion animation

### `@keyframes sheen`

Duration: `0.4s` · Easing: `ease-out` · Delay: `0s` · Iteration: `1` · Fill: `forwards`

Used by: `.animate-sheen`

```css
@keyframes sheen {
  0% {
    transform: translate(-100%);
  }
  100% {
    transform: translate(100%);
  }
}
```

> Transform/motion animation

### `@keyframes slideIn`

Duration: `0.35s` · Easing: `cubic-bezier(0.22, 1, 0.36, 1)` · Delay: `0s` · Iteration: `1` · Fill: `both`

Used by: `.animate-slide-in`

```css
@keyframes slideIn {
  0% {
    opacity: 0;
    transform: translateY(-30px);
  }
  100% {
    opacity: 1;
    transform: translateY(0px);
  }
}
```

> Fade + motion enter animation

### `@keyframes softFlashDown`

Duration: `59s` · Easing: `ease` · Delay: `0s` · Iteration: `1` · Fill: `none`

Used by: `.animate-soft-flash-down`

```css
@keyframes softFlashDown {
  0% {
    background-color: rgba(255, 82, 82, 0.15);
  }
  100% {
    background-color: rgba(0, 0, 0, 0);
  }
}
```

> Background color/gradient shift · Text color shift

### `@keyframes softFlashUp`

Duration: `59s` · Easing: `ease` · Delay: `0s` · Iteration: `1` · Fill: `none`

Used by: `.animate-soft-flash-up`

```css
@keyframes softFlashUp {
  0% {
    background-color: rgba(10, 194, 133, 0.15);
  }
  100% {
    background-color: rgba(0, 0, 0, 0);
  }
}
```

> Background color/gradient shift · Text color shift

### `@keyframes spin`

Duration: `1s` · Easing: `linear` · Delay: `0s` · Iteration: `infinite` · Fill: `none`

Used by: `.animate-spin`

```css
@keyframes spin {
  100% {
    transform: rotate(360deg);
  }
}
```

> Transform/motion animation

### `@keyframes collapsible-up`

Duration: `0.3s` · Easing: `ease-out` · Delay: `0s` · Iteration: `1` · Fill: `none`

Used by: `.data-\[state\=closed\]\:animate-collapsible-up[data-state="closed"]`

```css
@keyframes collapsible-up {
  0% {
    height: var(--radix-collapsible-content-height);
  }
  100% {
    height: 0px;
  }
}
```

> Dimension expand/collapse

### `@keyframes collapsible-down`

Duration: `0.3s` · Easing: `ease-out` · Delay: `0s` · Iteration: `1` · Fill: `none`

Used by: `.data-\[state\=open\]\:animate-collapsible-down[data-state="open"]`

```css
@keyframes collapsible-down {
  0% {
    height: 0px;
  }
  100% {
    height: var(--radix-collapsible-content-height);
  }
}
```

> Dimension expand/collapse

### `@keyframes chartRevealWipe`

Duration: `1.2s` · Easing: `cubic-bezier(0.66, 0, 0.34, 1)` · Delay: `0s` · Iteration: `1` · Fill: `forwards`

Used by: `.chart-reveal-wipe`

```css
@keyframes chartRevealWipe {
  0% {
    transform: scaleX(0);
  }
  100% {
    transform: scaleX(1);
  }
}
```

> Transform/motion animation

### `@keyframes swipe-out-left`

Used by: `[data-sonner-toast][data-swipe-out="true"][data-swipe-direction="left"]`

```css
@keyframes swipe-out-left {
  0% {
    transform: var(--y) translateX(var(--swipe-amount-x));
    opacity: 1;
  }
  100% {
    transform: var(--y) translateX(calc(var(--swipe-amount-x) - 100%));
    opacity: 0;
  }
}
```

> Fade + motion enter animation

### `@keyframes swipe-out-right`

Used by: `[data-sonner-toast][data-swipe-out="true"][data-swipe-direction="right"]`

```css
@keyframes swipe-out-right {
  0% {
    transform: var(--y) translateX(var(--swipe-amount-x));
    opacity: 1;
  }
  100% {
    transform: var(--y) translateX(calc(var(--swipe-amount-x) + 100%));
    opacity: 0;
  }
}
```

> Fade + motion enter animation

### `@keyframes swipe-out-up`

Used by: `[data-sonner-toast][data-swipe-out="true"][data-swipe-direction="up"]`

```css
@keyframes swipe-out-up {
  0% {
    transform: var(--y) translateY(var(--swipe-amount-y));
    opacity: 1;
  }
  100% {
    transform: var(--y) translateY(calc(var(--swipe-amount-y) - 100%));
    opacity: 0;
  }
}
```

> Fade + motion enter animation

### `@keyframes swipe-out-down`

Used by: `[data-sonner-toast][data-swipe-out="true"][data-swipe-direction="down"]`

```css
@keyframes swipe-out-down {
  0% {
    transform: var(--y) translateY(var(--swipe-amount-y));
    opacity: 1;
  }
  100% {
    transform: var(--y) translateY(calc(var(--swipe-amount-y) + 100%));
    opacity: 0;
  }
}
```

> Fade + motion enter animation

### `@keyframes sonner-fade-in`

Duration: `0.3s` · Easing: `ease` · Delay: `0s` · Iteration: `1` · Fill: `forwards`

Used by: `[data-sonner-toast][data-promise="true"] [data-icon] > svg`

```css
@keyframes sonner-fade-in {
  0% {
    opacity: 0;
    transform: scale(0.8);
  }
  100% {
    opacity: 1;
    transform: scale(1);
  }
}
```

> Fade + motion enter animation

### `@keyframes sonner-fade-out`

Duration: `0.2s` · Easing: `ease` · Delay: `0s` · Iteration: `1` · Fill: `forwards`

Used by: `.sonner-loading-wrapper[data-visible="false"]`

```css
@keyframes sonner-fade-out {
  0% {
    opacity: 1;
    transform: scale(1);
  }
  100% {
    opacity: 0;
    transform: scale(0.8);
  }
}
```

> Fade + motion enter animation

### `@keyframes sonner-spin`

Duration: `1.2s` · Easing: `linear` · Delay: `0s` · Iteration: `infinite` · Fill: `none`

Used by: `.sonner-loading-bar`

```css
@keyframes sonner-spin {
  0% {
    opacity: 1;
  }
  100% {
    opacity: 0.15;
  }
}
```

> Opacity fade

### `@keyframes bprogress-indeterminate-increase`

Duration: `2s` · Easing: `ease` · Delay: `0s` · Iteration: `infinite` · Fill: `none`

Used by: `.bprogress .indeterminate .inc`

```css
@keyframes bprogress-indeterminate-increase {
  0% {
    left: -5%;
    width: 5%;
  }
  100% {
    left: 130%;
    width: 100%;
  }
}
```

> Dimension expand/collapse

### `@keyframes bprogress-indeterminate-decrease`

Duration: `2s` · Easing: `ease` · Delay: `0.5s` · Iteration: `infinite` · Fill: `none`

Used by: `.bprogress .indeterminate .dec`

```css
@keyframes bprogress-indeterminate-decrease {
  0% {
    left: -80%;
    width: 80%;
  }
  100% {
    left: 110%;
    width: 10%;
  }
}
```

> Dimension expand/collapse

### `@keyframes bprogress-spinner`

```css
@keyframes bprogress-spinner {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}
```

> Transform/motion animation

### `@keyframes bprogress-spinner`

```css
@keyframes bprogress-spinner {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}
```

> Transform/motion animation

## Motion Tokens (CSS Variables)

### Duration Tokens

```css
--bprogress-spinner-animation-duration: 400ms;
```

## Global Transition Declarations

These `transition` values were extracted from CSS rules across the site:

```css
transition: transform 0.2s cubic-bezier(0.11, 0, 0.02, 0.99), --live-border-fallback 0.2s;
transition: transform 0.2s cubic-bezier(0.11, 0, 0.02, 0.99), border-color 0.2s;
transition: transform 0.4s;
transition: transform 0.4s, opacity 0.4s, height 0.4s, box-shadow 0.2s;
transition: opacity 0.4s, box-shadow 0.2s;
transition: opacity 0.1s, background 0.2s, border-color 0.2s;
transition: opacity 0.4s;
transition: transform 0.5s, opacity 0.2s;
transition: opacity 0.2s, transform 0.2s;
transition: fill 200ms cubic-bezier(0.4, 0, 0.2, 1);
transition: height 0.2s linear;
transition: width 0.3s linear;
```

## How to Recreate This Motion Design

### Step 1 — Install Dependencies

```bash
```

### Step 2 — Scroll-Reveal Pattern

Elements that animate into view follow this pattern:

```css
/* Initial hidden state */
.reveal {
  opacity: 0;
  transform: translateY(40px);
  transition: opacity 400ms cubic-bezier(0.4, 0, 0.2, 1),
              transform 400ms cubic-bezier(0.4, 0, 0.2, 1);
}
.reveal.visible {
  opacity: 1;
  transform: translateY(0);
}
```

### Step 3 — Key Motion Principles

- **Duration scale:** `400ms` · `0.2s` · `0.4s` — use these values, never invent new durations
- **Always add** `@media (prefers-reduced-motion: reduce) { * { animation-duration: 0.01ms !important; transition-duration: 0.01ms !important; } }`

### Step 4 — Scroll Journey Reference

Match what happens at each scroll position:

- **0%** (`0px`) → `screens/scroll/scroll-000.png`
- **17%** (`544px`) → `screens/scroll/scroll-017.png`
- **33%** (`1056px`) → `screens/scroll/scroll-033.png`
- **50%** (`0px`) → `screens/scroll/scroll-050.png`
- **67%** (`0px`) → `screens/scroll/scroll-067.png`
- **83%** (`0px`) → `screens/scroll/scroll-083.png`
- **100%** (`0px`) → `screens/scroll/scroll-100.png`

