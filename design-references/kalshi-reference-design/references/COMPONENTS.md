# Component Reference

> Repeated DOM patterns detected by structural analysis. Each component appeared 3+ times.

## Detected Components

| Component | Category | Instances | Key Classes |
|-----------|----------|-----------|-------------|
| **Col Span Full** | card | 46× | `.col-span-full`, `.grid`, `.grid-cols-subgrid` |
| **Flex** | unknown | 44× | `.flex`, `.flex-1`, `.flex-col` |
| **Gap X 1** | unknown | 23× | `.gap-x-1`, `.gap-y-1.5`, `.grid` |
| **Flex** | card | 16× | `.flex`, `.gap-1.5`, `.items-center` |
| **Cursor Pointer** | card | 11× | `.cursor-pointer`, `.flex`, `.group` |
| **Duration 200** | unknown | 11× | `.duration-200`, `.font-kalshi-sans`, `.group-hover:opacity-100` |
| **!Translate X 0** | unknown | 7× | `.!translate-x-0`, `.absolute`, `.duration-300` |
| **Flex** | unknown | 7× | `.flex`, `.flex-col`, `.gap-2` |
| **Max W [Calc(100% 175px)]** | unknown | 7× | `.max-w-[calc(100%-175px)]`, `.no-underline`, `.text-text-x10` |
| **Flex** | card | 7× | `.flex`, `.font-kalshi-condensed`, `.items-center` |
| **Block** | unknown | 7× | `.block`, `.line-clamp-1`, `.truncate` |
| **Flex** | unknown | 7× | `.flex`, `.h-full`, `.no-underline` |
| **Flex** | unknown | 7× | `.flex`, `.flex-col`, `.gap-2` |
| **Flex** | unknown | 7× | `.flex`, `.flex-col`, `.justify-between` |
| **Flex** | unknown | 7× | `.flex`, `.flex-col`, `.gap-2` |
| **Bg Container X40** | unknown | 6× | `.bg-container-x40`, `.border`, `.border-solid` |
| **Font Kalshi Sans** | unknown | 5× | `.font-kalshi-sans`, `.text-text-x10`, `.typ-overline-x20` |
| **Div** | unknown | 4× |  |
| **Flex** | card | 3× | `.flex`, `.gap-0.75`, `.items-center` |
| **Gap 1.5** | card | 3× | `.gap-1.5`, `.inline-flex`, `.items-center` |

## Cards

### Col Span Full

**Instances found:** 46

**CSS classes:** `.col-span-full` `.grid` `.grid-cols-subgrid` `.items-center` `.min-h-4.5`

**HTML structure:**

```html
<div class="col-span-full grid grid-cols-subgrid items-center min-h-4.5"><div class="flex items-center gap-1.5 min-w-0"><div class="dark:hidden"><div aria-label="Alexander Zverev" class="flex items-center justify-center overflow-hidden transition-all shrink-0 size-4.5"><div style="background: transparent; display: flex; justify-content: center; align-items: center; width: 36px; min-width: 36px; height: 36px; border-radius: 6px;"><img alt="Alexander Zverev" fetchpriority="auto" loading="lazy" width="72" height="72" decoding="async" data-nimg="1" class="" srcset="/_next/image?url=%2Fcdn-images%2
```

**Base styles (from design tokens):**

```css
.col-span-full {
  border-radius: 16px;
  padding: 8px;
}```

### Flex

**Instances found:** 16

**CSS classes:** `.flex` `.gap-1.5` `.items-center` `.min-w-0`

**HTML structure:**

```html
<div class="flex items-center gap-1.5 min-w-0"><div class="dark:hidden"><div aria-label="Alexander Zverev" class="flex items-center justify-center overflow-hidden transition-all shrink-0 size-4.5"><div style="background: transparent; display: flex; justify-content: center; align-items: center; width: 36px; min-width: 36px; height: 36px; border-radius: 6px;"><img alt="Alexander Zverev" fetchpriority="auto" loading="lazy" width="72" height="72" decoding="async" data-nimg="1" class="" srcset="/_next/image?url=%2Fcdn-images%2Fstructured_targets%2FFLAG_DEU.webp&amp;w=96&amp;q=80 1x, /_next/image?ur
```

**Base styles (from design tokens):**

```css
.flex {
  border-radius: 16px;
  padding: 8px;
}```

### Cursor Pointer

**Instances found:** 11

**CSS classes:** `.cursor-pointer` `.flex` `.group` `.items-center` `.pb-0.5` `.pt-0.5`

**HTML structure:**

```html
<a class="group flex items-center pt-0.5 pb-0.5 cursor-pointer whitespace-nowrap text-text-x10" href="/category/elections"><span class="font-kalshi-sans typ-emphasis-x30 transition-opacity duration-200 opacity-50 group-hover:opacity-100">Elections</span></a>
```

**Base styles (from design tokens):**

```css
.cursor-pointer {
  border-radius: 16px;
  padding: 8px;
}```

### Flex

**Instances found:** 7

**CSS classes:** `.flex` `.font-kalshi-condensed` `.items-center` `.m-0` `.typ-headline-x20`

**HTML structure:**

```html
<h2 class="m-0 font-kalshi-condensed typ-headline-x20 flex items-center sm:min-h-10"><span class="block truncate line-clamp-1 sm:line-clamp-2 sm:whitespace-normal sm:text-clip">Fery vs Zverev</span></h2>
```

**Base styles (from design tokens):**

```css
.flex {
  border-radius: 16px;
  padding: 8px;
}```

### Flex

**Instances found:** 3

**CSS classes:** `.flex` `.gap-0.75` `.items-center` `.justify-center` `.min-h-4.5` `.px-2`

**HTML structure:**

```html
<a class="flex items-center justify-center min-h-4.5 px-2 rounded-x50 gap-0.75 hover:bg-fill-x60 transition-colors" href="/browse"><span class="font-kalshi-sans typ-overline-x20 text-text-x10">MARKETS</span></a>
```

**Base styles (from design tokens):**

```css
.flex {
  border-radius: 16px;
  padding: 8px;
}```

### Gap 1.5

**Instances found:** 3

**CSS classes:** `.gap-1.5` `.inline-flex` `.items-center` `.min-w-0`

**HTML structure:**

```html
<div class="inline-flex items-center gap-1.5 min-w-0"><div class="relative -left-px -top-px box-content flex size-3.5 shrink-0 items-center justify-center overflow-hidden rounded-x20 border border-stroke-x40"><div style="background: transparent; display: flex; justify-content: center; align-items: center; width: 28px; min-width: 28px; height: 28px; border-radius: 6px;"><img alt="" fetchpriority="auto" loading="lazy" width="56" height="56" decoding="async" data-nimg="1" class="" srcset="/_next/image?url=%2Fcdn-images%2Fseries-images-webp%2FKXATPMATCH.webp%3Fsize%3Dsm&amp;w=64&amp;q=80 1x, /_nex
```

**Base styles (from design tokens):**

```css
.gap-1.5 {
  border-radius: 16px;
  padding: 8px;
}```

## Other Components

### Flex

**Instances found:** 44

**CSS classes:** `.flex` `.flex-1` `.flex-col` `.gap-0.5` `.justify-center` `.min-w-0`

**HTML structure:**

```html
<div class="flex-1 min-w-0 flex flex-col gap-0.5 justify-center"><span class="font-kalshi-sans font-normal typ-body-x30 truncate">Alexander Zverev</span><div aria-valuemax="100" aria-valuemin="0" aria-valuenow="85" class="w-full overflow-hidden rounded-x50 h-[2px]" role="progressbar"><div class="relative h-full min-w-[4px] overflow-hidden rounded-x50 transition-[width] duration-300 ease-out" style="width: 85%; background-color: var(--green-x10);"></div></div></div>
```

**Base styles (from design tokens):**

```css
.flex {
  padding: 4px;
}```

### Gap X 1

**Instances found:** 23

**CSS classes:** `.gap-x-1` `.gap-y-1.5` `.grid` `.grid-cols-[1fr_auto_auto]` `.w-full`

**HTML structure:**

```html
<div class="grid grid-cols-[1fr_auto_auto] gap-x-1 gap-y-1.5 w-full"><div class="col-span-full grid grid-cols-subgrid items-center min-h-4.5"><div class="flex items-center gap-1.5 min-w-0"><div class="dark:hidden"><div aria-label="Alexander Zverev" class="flex items-center justify-center overflow-hidden transition-all shrink-0 size-4.5"><div style="background: transparent; display: flex; justify-content: center; align-items: center; width: 36px; min-width: 36px; height: 36px; border-radius: 6px;"><img alt="Alexander Zverev" fetchpriority="auto" loading="lazy" width="72" height="72" decoding="a
```

**Base styles (from design tokens):**

```css
.gap-x-1 {
  padding: 4px;
}```

### Duration 200

**Instances found:** 11

**CSS classes:** `.duration-200` `.font-kalshi-sans` `.group-hover:opacity-100` `.opacity-50` `.transition-opacity` `.typ-emphasis-x30`

**HTML structure:**

```html
<span class="font-kalshi-sans typ-emphasis-x30 transition-opacity duration-200 opacity-50 group-hover:opacity-100">Elections</span>
```

**Base styles (from design tokens):**

```css
.duration-200 {
  padding: 4px;
}```

### !Translate X 0

**Instances found:** 7

**CSS classes:** `.!translate-x-0` `.absolute` `.duration-300` `.ease-in-out` `.flex-1` `.flex-shrink-0`

**HTML structure:**

```html
<div class="jsx-66a68cb5d4c39b0d flex-shrink-0 w-full absolute top-0 left-0 transition-all duration-300 ease-in-out opacity-0 translate-x-full flex-1 h-full relative opacity-100 z-10 !translate-x-0"><div class="flex flex-col h-full gap-2 sm:gap-0"><div class="flex items-center justify-between gap-2 min-w-0 w-full"><a class="inline-flex items-center gap-1.5 min-w-0 no-underline stretched-link-action hover:opacity-75 transition-opacity" href="/category/sports/tennis/wimbledon-men-singles"><div class="inline-flex items-center gap-1.5 min-w-0"><div class="relative -left-px -top-px box-content flex
```

**Base styles (from design tokens):**

```css
.!translate-x-0 {
  padding: 4px;
}```

### Flex

**Instances found:** 7

**CSS classes:** `.flex` `.flex-col` `.gap-2` `.h-full`

**HTML structure:**

```html
<div class="flex flex-col h-full gap-2 sm:gap-0"><div class="flex items-center justify-between gap-2 min-w-0 w-full"><a class="inline-flex items-center gap-1.5 min-w-0 no-underline stretched-link-action hover:opacity-75 transition-opacity" href="/category/sports/tennis/wimbledon-men-singles"><div class="inline-flex items-center gap-1.5 min-w-0"><div class="relative -left-px -top-px box-content flex size-3.5 shrink-0 items-center justify-center overflow-hidden rounded-x20 border border-stroke-x40"><div style="background: transparent; display: flex; justify-content: center; align-items: center; 
```

**Base styles (from design tokens):**

```css
.flex {
  padding: 4px;
}```

### Max W [Calc(100% 175px)]

**Instances found:** 7

**CSS classes:** `.max-w-[calc(100%-175px)]` `.no-underline` `.text-text-x10`

**HTML structure:**

```html
<a class="no-underline text-text-x10 max-w-[calc(100%-175px)] sm:max-w-full" href="/markets/kxatpmatch/atp-tennis-match/kxatpmatch-26jul10ferzve"><h2 class="m-0 font-kalshi-condensed typ-headline-x20 flex items-center sm:min-h-10"><span class="block truncate line-clamp-1 sm:line-clamp-2 sm:whitespace-normal sm:text-clip">Fery vs Zverev</span></h2></a>
```

**Base styles (from design tokens):**

```css
.max-w-[calc(100%-175px)] {
  padding: 4px;
}```

### Block

**Instances found:** 7

**CSS classes:** `.block` `.line-clamp-1` `.truncate`

**HTML structure:**

```html
<span class="block truncate line-clamp-1 sm:line-clamp-2 sm:whitespace-normal sm:text-clip">Fery vs Zverev</span>
```

**Base styles (from design tokens):**

```css
.block {
  padding: 4px;
}```

### Flex

**Instances found:** 7

**CSS classes:** `.flex` `.h-full` `.no-underline` `.relative` `.text-text-x10` `.w-full`

**HTML structure:**

```html
<div class="relative flex w-full h-full no-underline text-text-x10"><div class="flex flex-col gap-2 w-full relative justify-between max-w-[360px] market-slide-content-wrapper"><div class="flex flex-col justify-between w-full"><div class="flex flex-col gap-2"><div class="flex items-center gap-1.5 w-full"><span class="font-kalshi-sans font-normal typ-body-x10 flex-1 min-w-0 text-text-x20">Market</span><span class="font-kalshi-sans font-normal typ-body-x10 min-w-4.5 text-right text-text-x20">Pays out</span><span class="font-kalshi-sans font-normal typ-body-x10 min-w-[80px] text-center text-text-x
```

**Base styles (from design tokens):**

```css
.flex {
  padding: 4px;
}```

### Flex

**Instances found:** 7

**CSS classes:** `.flex` `.flex-col` `.gap-2` `.justify-between` `.market-slide-content-wrapper` `.max-w-[360px]`

**HTML structure:**

```html
<div class="flex flex-col gap-2 w-full relative justify-between max-w-[360px] market-slide-content-wrapper"><div class="flex flex-col justify-between w-full"><div class="flex flex-col gap-2"><div class="flex items-center gap-1.5 w-full"><span class="font-kalshi-sans font-normal typ-body-x10 flex-1 min-w-0 text-text-x20">Market</span><span class="font-kalshi-sans font-normal typ-body-x10 min-w-4.5 text-right text-text-x20">Pays out</span><span class="font-kalshi-sans font-normal typ-body-x10 min-w-[80px] text-center text-text-x20">Odds</span></div><div class="grid grid-cols-[1fr_auto_auto] gap-
```

**Base styles (from design tokens):**

```css
.flex {
  padding: 4px;
}```

### Flex

**Instances found:** 7

**CSS classes:** `.flex` `.flex-col` `.justify-between` `.w-full`

**HTML structure:**

```html
<div class="flex flex-col justify-between w-full"><div class="flex flex-col gap-2"><div class="flex items-center gap-1.5 w-full"><span class="font-kalshi-sans font-normal typ-body-x10 flex-1 min-w-0 text-text-x20">Market</span><span class="font-kalshi-sans font-normal typ-body-x10 min-w-4.5 text-right text-text-x20">Pays out</span><span class="font-kalshi-sans font-normal typ-body-x10 min-w-[80px] text-center text-text-x20">Odds</span></div><div class="grid grid-cols-[1fr_auto_auto] gap-x-1 gap-y-1.5 w-full"><div class="col-span-full grid grid-cols-subgrid items-center min-h-4.5"><div class="f
```

**Base styles (from design tokens):**

```css
.flex {
  padding: 4px;
}```

### Flex

**Instances found:** 7

**CSS classes:** `.flex` `.flex-col` `.gap-2`

**HTML structure:**

```html
<div class="flex flex-col gap-2"><div class="flex items-center gap-1.5 w-full"><span class="font-kalshi-sans font-normal typ-body-x10 flex-1 min-w-0 text-text-x20">Market</span><span class="font-kalshi-sans font-normal typ-body-x10 min-w-4.5 text-right text-text-x20">Pays out</span><span class="font-kalshi-sans font-normal typ-body-x10 min-w-[80px] text-center text-text-x20">Odds</span></div><div class="grid grid-cols-[1fr_auto_auto] gap-x-1 gap-y-1.5 w-full"><div class="col-span-full grid grid-cols-subgrid items-center min-h-4.5"><div class="flex items-center gap-1.5 min-w-0"><div class="dark
```

**Base styles (from design tokens):**

```css
.flex {
  padding: 4px;
}```

### Bg Container X40

**Instances found:** 6

**CSS classes:** `.bg-container-x40` `.border` `.border-solid` `.border-stroke-x40` `.flex` `.flex-col`

**HTML structure:**

```html
<div class="jsx-66a68cb5d4c39b0d relative flex flex-col justify-between w-full gap-1 p-3 pb-2 overflow-hidden border border-solid market-slide-container bg-container-x40 border-stroke-x40 rounded-x40 sm:mt-2 sm:p-2" style="height: 26rem; touch-action: pan-y;"><div class="jsx-66a68cb5d4c39b0d relative flex flex-1 w-full"><div class="jsx-66a68cb5d4c39b0d flex-shrink-0 w-full absolute top-0 left-0 transition-all duration-300 ease-in-out opacity-0 translate-x-full flex-1 h-full relative opacity-100 z-10 !translate-x-0"><div class="flex flex-col h-full gap-2 sm:gap-0"><div class="flex items-center 
```

**Base styles (from design tokens):**

```css
.bg-container-x40 {
  padding: 4px;
}```

### Font Kalshi Sans

**Instances found:** 5

**CSS classes:** `.font-kalshi-sans` `.text-text-x10` `.typ-overline-x20`

**HTML structure:**

```html
<span class="font-kalshi-sans typ-overline-x20 text-text-x10">MARKETS</span>
```

**Base styles (from design tokens):**

```css
.font-kalshi-sans {
  padding: 4px;
}```

### Div

**Instances found:** 4

**HTML structure:**

```html
<div class="lg:hidden"><button type="button" id="radix-_r_1_" aria-haspopup="menu" aria-expanded="false" data-state="closed" class="appearance-none border-0 bg-transparent p-0 m-0 flex items-center justify-center min-h-4.5 px-2 rounded-x50 gap-0.75 hover:bg-container-x40 transition-colors cursor-pointer group"><span class="font-kalshi-sans typ-overline-x20 text-text-x10">TRUST</span><svg width="10" height="6" viewBox="0 0 10 6" fill="none" aria-hidden="true" class="text-text-x10 transition-transform group-data-[state=open]:rotate-180"><path d="M1 1L5 5L9 1" stroke="currentColor" stroke-width="
```

**Base styles (from design tokens):**

```css
.div {
  padding: 4px;
}```

## Component Rules

- Match class names exactly from the patterns above
- Each component instance must be visually identical to others of its type
- Do not add extra wrappers or change the DOM structure
- Use `#28cc95` for all interactive/active states

