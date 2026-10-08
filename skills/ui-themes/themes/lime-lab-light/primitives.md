# Lime Lab Light — design primitives

Light sibling of Lime Lab Dark. Same typography, proportions, and component patterns — inverted to white/soft green surfaces with lime CTAs.

**Preview:** [preview.png](preview.png)

## Vibe (one sentence)

A bright technical workshop UI: soft green-white atmosphere, sharp lime actions, monospace density, and heavy display type for brand/titles.

## Typography (critical)

Same as dark mode:

| Role | Font | Weight / notes |
|------|------|----------------|
| **Display / brand / H1–H2** | **Syne** | 600–800; tight tracking; large clamp sizes |
| **UI / body / code / inputs** | **IBM Plex Mono** | 400–600; default UI face |

```css
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=Syne:wght@600;700;800&display=swap');
```

## Color

| Token | Hex | Use |
|-------|-----|-----|
| `--bg` | `#f3f6f3` | Page base |
| `--bg-elevated` | `#e7eee8` | Sidebar / chrome |
| `--bg-panel` | `#ffffff` | Cards / panels |
| `--line` | `#c5d0c8` | Borders |
| `--text` | `#121816` | Primary text |
| `--muted` | `#5a6b62` | Secondary text |
| `--accent` | `#c8f542` | Primary CTA fills (with `--accent-ink`) |
| `--accent-dim` | `#5f7a12` | Links, code, readable accents on light |
| `--danger` | `#d94b3d` | Destructive actions |
| `--focus` | `#2a9d8f` | Focus rings |
| `--accent-ink` | `#10140f` | Text on lime buttons |

**Atmosphere:**

```css
background:
  radial-gradient(1200px 600px at 10% -10%, #dce8d8 0%, transparent 55%),
  radial-gradient(900px 500px at 100% 0%, #d8e4ea 0%, transparent 50%),
  var(--bg);
```

## Proportions, motion, components

Identical to `lime-lab-dark` — reuse the same spacing, radii, shell layout, button variants, and motion. Only tokens (and accent text color on light) change.

## Do

- Keep Syne + IBM Plex Mono
- Use bright lime for solid CTAs; use `--accent-dim` for text/links on white
- White panels with soft green page wash

## Don’t

- Flat pure `#fff` page with no atmosphere
- Purple / cream-terracotta defaults
- Inter as the UI font
- Reusing dark-mode neon lime as body text color (unreadable on white)

## Implementation checklist

- [ ] Fonts loaded
- [ ] Light `:root` tokens from `tokens.css`
- [ ] `components.css` (shared structure with dark)
- [ ] Code/links use `--accent-dim`
- [ ] Primary buttons still solid `--accent` + `--accent-ink`
