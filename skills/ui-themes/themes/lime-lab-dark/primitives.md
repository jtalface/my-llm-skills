# Lime Lab Dark — design primitives

Dark developer-lab aesthetic from a coding playground app. High-contrast charcoal + electric lime. Monospace UI with bold display headings.

**Preview:** [preview.png](preview.png)

## Vibe (one sentence)

A technical workshop UI: calm dark green-black atmosphere, sharp lime actions, monospace density, and heavy display type for brand/titles.

## Typography (critical)

| Role | Font | Weight / notes |
|------|------|----------------|
| **Display / brand / H1–H2** | **Syne** | 600–800; tight tracking (`-0.02em` to `-0.03em`); large clamp sizes |
| **UI / body / code / inputs** | **IBM Plex Mono** | 400–600; default UI face — not Inter/system |

```html
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=Syne:wght@600;700;800&display=swap" rel="stylesheet" />
```

Or CSS:

```css
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=Syne:wght@600;700;800&display=swap');
```

**Rules**
- Body default = mono (`14px`, `line-height: 1.5`)
- Brand mark = accent color, uppercase, `letter-spacing: 0.12em`, ~0.75rem
- Section labels (panel titles) = uppercase muted mono, `letter-spacing: 0.08em`, ~0.8rem
- Never substitute Inter / Roboto / Arial as the primary face

## Color

| Token | Hex | Use |
|-------|-----|-----|
| `--bg` | `#0f1412` | Page base |
| `--bg-elevated` | `#171d1a` | Sidebar / chrome |
| `--bg-panel` | `#1c2420` | Cards / panels |
| `--line` | `#2a3530` | Borders |
| `--text` | `#e7efe9` | Primary text |
| `--muted` | `#8a9a91` | Secondary text |
| `--accent` | `#c8f542` | Primary CTA, brand mark, code highlights |
| `--accent-dim` | `#9bbb2e` | Softer accent |
| `--danger` | `#ff6b5a` | Destructive actions |
| `--focus` | `#7dd3c0` | Focus rings (cooler teal, not lime) |
| `--accent-ink` | `#10140f` | Text on lime buttons |

**Atmosphere** (not flat black):

```css
background:
  radial-gradient(1200px 600px at 10% -10%, #1a2a22 0%, transparent 55%),
  radial-gradient(900px 500px at 100% 0%, #1a2228 0%, transparent 50%),
  var(--bg);
```

## Proportions & layout

| Measure | Value |
|---------|-------|
| Radius (panels) | `10px` (`--radius`) |
| Radius (inputs/buttons) | `8px` |
| Pill radius | `999px` |
| Sidebar width | `minmax(240px, 300px)` |
| Main max content | ~`960px` |
| Base stack gap | `1rem` |
| Sidebar padding | `1.75rem 1.25rem` |
| Panel padding | `1rem 1.1rem` |
| Stack breakpoint | `860px` |

**Shell:** optional left nav + main. Brand: mark → huge Syne title → short muted tagline.

## Motion

- Transitions `140–160ms` ease on border/background/transform
- Enter: opacity + `translateY(8px)` ~`280ms`
- Primary hover: `translateY(-1px)` + slight brightness
- Nav hover: `translateX(2px)`
- Avoid glow stacks, bounce, long decorative motion

## Component patterns

1. **Primary button** — solid `--accent`, `--accent-ink` text  
2. **Ghost button** — transparent, `--line` border, `--text`  
3. **Danger button** — transparent, danger border/text  
4. **Panel** — `--bg-panel`, `1px` `--line`, `--radius`  
5. **Inputs** — `--bg` fill; focus ring with `--focus`  
6. **Stat pills** — small bordered capsules, muted text  
7. **Chips** — accent wash on panel bg  
8. **Inline code** — mono + `--accent` (muted for IDs)

## Do

- Lead with Syne for product/page name at hero scale when branding matters
- Keep UI chrome in IBM Plex Mono
- Use lime for actions + highlights, not large fills
- Prefer bordered panels over heavy shadows

## Don’t

- Purple / indigo gradient themes
- Warm cream + terracotta + default serif
- Inter/Roboto as main UI font
- Multi-layer shadows or neon glow everywhere
- Light mode unless explicitly requested

## Implementation checklist

- [ ] Fonts loaded (Syne + IBM Plex Mono)
- [ ] `:root` tokens from `tokens.css`
- [ ] Body uses mono + atmospheric background
- [ ] Display font on brand / major headings only
- [ ] Buttons: primary / ghost / danger
- [ ] Panels use token borders + radius
- [ ] Focus rings use `--focus`
- [ ] Mobile: single column under ~860px
