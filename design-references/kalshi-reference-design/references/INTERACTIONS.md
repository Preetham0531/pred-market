# Interaction Reference

> Micro-interactions extracted from live DOM. Recreate these exactly for authentic feel.

## Coverage

| Component Type | Count | States Captured |
|----------------|-------|----------------|
| Button | 3 | default, hover, focus |
| Link | 3 | default, hover, focus |
| Input | 1 | default, hover, focus |

## Transition System

These transition declarations were extracted from interactive elements:

```css
transition: color 0.15s cubic-bezier(0.4, 0, 0.2, 1), background-color 0.15s cubic-bezier(0.4, 0, 0.2, 1), border-color 0.15s cubic-bezier(0.4, 0, 0.2, 1), text-decoration-color 0.15s cubic-bezier(0.4, 0, 0.2, 1), fill 0.15s cubic-bezier(0.4, 0, 0.2, 1), stroke 0.15s cubic-bezier(0.4, 0, 0.2, 1);
transition: opacity 0.083s cubic-bezier(0.4, 0, 0.2, 1), background-color 0.083s cubic-bezier(0.4, 0, 0.2, 1), transform 0.167s cubic-bezier(0.4, 0, 0.2, 1);
transition: all;
transition: background-color 0.3s cubic-bezier(0.4, 0, 0.2, 1);
```

Apply these to all interactive elements. Never invent new durations or easings.

## Button Interactions

### Button 1 — `TRUST`

**States:**

- Default: `../screens/states/button-1-default.png`
- Hover: `../screens/states/button-1-hover.png`
- Focus: `../screens/states/button-1-focus.png`

**On hover:**

```css
/* background-color: rgba(0, 0, 0, 0) → */ background-color: rgba(128, 128, 128, 0.02);
```

**On focus:**

```css
/* outline: rgba(0, 0, 0, 0.9) none 3px → */ outline: rgb(0, 95, 204) auto 1px;
/* outline-color: rgba(0, 0, 0, 0.9) → */ outline-color: rgb(0, 95, 204);
```

**Transition:** `color 0.15s cubic-bezier(0.4, 0, 0.2, 1), background-color 0.15s cubic-bezier(0.4, 0, 0.2, 1), border-color 0.15s cubic-bezier(0.4, 0, 0.2, 1), text-decoration-color 0.15s cubic-bezier(0.4, 0, 0.2, 1), fill 0.15s cubic-bezier(0.4, 0, 0.2, 1), stroke 0.15s cubic-bezier(0.4, 0, 0.2, 1)`

### Button 2 — `button`

**States:**

- Default: `../screens/states/button-2-default.png`
- Hover: `../screens/states/button-2-hover.png`
- Focus: `../screens/states/button-2-focus.png`

**On focus:**

```css
/* outline: rgba(0, 0, 0, 0) solid 0px → */ outline: rgb(40, 204, 149) solid 2px;
/* outline-color: rgba(0, 0, 0, 0) → */ outline-color: rgb(40, 204, 149);
```

**Transition:** `opacity 0.083s cubic-bezier(0.4, 0, 0.2, 1), background-color 0.083s cubic-bezier(0.4, 0, 0.2, 1), transform 0.167s cubic-bezier(0.4, 0, 0.2, 1)`

### Button 3 — `Log in`

**States:**

- Default: `../screens/states/button-3-default.png`
- Hover: `../screens/states/button-3-hover.png`
- Focus: `../screens/states/button-3-focus.png`

**On hover:**

```css
/* background-color: rgba(0, 0, 0, 0) → */ background-color: rgba(0, 0, 0, 0.07);
/* opacity: 1 → */ opacity: 0.8;
```

**On focus:**

```css
/* outline: rgba(0, 0, 0, 0) solid 0px → */ outline: rgb(40, 204, 149) solid 2px;
/* outline-color: rgba(0, 0, 0, 0) → */ outline-color: rgb(40, 204, 149);
```

**Transition:** `opacity 0.083s cubic-bezier(0.4, 0, 0.2, 1), background-color 0.083s cubic-bezier(0.4, 0, 0.2, 1), transform 0.167s cubic-bezier(0.4, 0, 0.2, 1)`

## Link Interactions

### Link 1 — `a`

**States:**

- Default: `../screens/states/link-1-default.png`
- Hover: `../screens/states/link-1-hover.png`
- Focus: `../screens/states/link-1-focus.png`

**On focus:**

```css
/* outline: rgba(0, 0, 0, 0.9) none 3px → */ outline: rgb(0, 95, 204) auto 1px;
/* outline-color: rgba(0, 0, 0, 0.9) → */ outline-color: rgb(0, 95, 204);
```

**Transition:** `all`

### Link 2 — `MARKETS`

**States:**

- Default: `../screens/states/link-2-default.png`
- Hover: `../screens/states/link-2-hover.png`
- Focus: `../screens/states/link-2-focus.png`

**On focus:**

```css
/* outline: rgba(0, 0, 0, 0.9) none 3px → */ outline: rgb(0, 95, 204) auto 1px;
/* outline-color: rgba(0, 0, 0, 0.9) → */ outline-color: rgb(0, 95, 204);
```

**Transition:** `color 0.15s cubic-bezier(0.4, 0, 0.2, 1), background-color 0.15s cubic-bezier(0.4, 0, 0.2, 1), border-color 0.15s cubic-bezier(0.4, 0, 0.2, 1), text-decoration-color 0.15s cubic-bezier(0.4, 0, 0.2, 1), fill 0.15s cubic-bezier(0.4, 0, 0.2, 1), stroke 0.15s cubic-bezier(0.4, 0, 0.2, 1)`

### Link 3 — `PERPS`

**States:**

- Default: `../screens/states/link-3-default.png`
- Hover: `../screens/states/link-3-hover.png`
- Focus: `../screens/states/link-3-focus.png`

**On focus:**

```css
/* outline: rgba(0, 0, 0, 0.9) none 3px → */ outline: rgb(0, 95, 204) auto 1px;
/* outline-color: rgba(0, 0, 0, 0.9) → */ outline-color: rgb(0, 95, 204);
```

**Transition:** `color 0.15s cubic-bezier(0.4, 0, 0.2, 1), background-color 0.15s cubic-bezier(0.4, 0, 0.2, 1), border-color 0.15s cubic-bezier(0.4, 0, 0.2, 1), text-decoration-color 0.15s cubic-bezier(0.4, 0, 0.2, 1), fill 0.15s cubic-bezier(0.4, 0, 0.2, 1), stroke 0.15s cubic-bezier(0.4, 0, 0.2, 1)`

## Input Interactions

### Input 1 — `Trade on anything`

**States:**

- Default: `../screens/states/input-1-default.png`
- Hover: `../screens/states/input-1-hover.png`
- Focus: `../screens/states/input-1-focus.png`

**On focus:**

```css
/* background-color: rgba(0, 0, 0, 0.07) → */ background-color: rgba(255, 255, 255, 1);
/* outline: rgba(0, 0, 0, 0.9) none 3px → */ outline: rgb(10, 194, 133) solid 1px;
/* outline-color: rgba(0, 0, 0, 0.9) → */ outline-color: rgb(10, 194, 133);
```

**Transition:** `background-color 0.3s cubic-bezier(0.4, 0, 0.2, 1)`

## Interaction Rules

- Accent color `#28cc95` is used for focus rings, active states, and hover highlights
- Hover effects use **opacity** changes, not color shifts
- Hover effects include **color transitions** — use the extracted values, not approximations
- Focus states use **outline** (not box-shadow) — always match the extracted focus ring
- Transition durations in use: `0.15s`, `0.083s`, `0.167s`, `0.3s`
- Always respect `prefers-reduced-motion` — set all transitions to `0s` when enabled

