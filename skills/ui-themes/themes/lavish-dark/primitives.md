# Lavish Dark — design primitives

Extracted from a design ideation page (`data-theme="luxury"` / DaisyUI **luxury**). Near-black surfaces, champagne-gold type, white primary actions, soft large radii.

**Preview:** [preview.png](preview.png)

## Vibe (one sentence)

A dark luxury product UI: ink-black panels, warm gold copy, crisp white CTAs, and editorial serif headlines.

## Source

- DaisyUI 5 `luxury` theme (`data-theme="luxury"`)

## Typography

| Role | Font | Notes |
|------|------|-------|
| **Display / brand / H1–H2** | **Cormorant Garamond** | 600–700; editorial serif |
| **UI / body** | **DM Sans** | Clean product sans |
| **Code** | **IBM Plex Mono** | Technical snippets |

## Color (mapped to lime-lab token names)

| Token | Hex | DaisyUI source |
|-------|-----|----------------|
| `--bg` | `#09090b` | base-100 |
| `--bg-elevated` | `#171618` | base-200 |
| `--bg-panel` | `#1e1d1f` | base-300 |
| `--line` | `#2e2c31` | derived border |
| `--text` | `#dca54d` | base-content (champagne) |
| `--muted` | `#9a7a45` | softened gold |
| `--accent` | `#ffffff` | primary (CTA fill) |
| `--accent-ink` | `#161616` | primary-content |
| `--accent-dim` | `#ffe7a4` | neutral-content (pale gold) |
| `--danger` | `#ff6f6f` | error |
| `--focus` | `#67c6ff` | info |
| `--code` / `--brand-mark` | `#ffe7a4` | pale gold on dark |

## Proportions

| Measure | Value |
|---------|-------|
| Panel radius | `1rem` (DaisyUI `--radius-box`) |
| Control radius | `0.5rem` (`--radius-field`) |
| Base size | `15px` |
| Content max | `960px` |

## Do

- Gold text on near-black; white solid CTAs
- Larger radii than lime-lab
- Serif for titles, sans for UI chrome

## Don’t

- Neon lime / cyber accents
- Flat pure black with white body text (loses the luxury gold voice)
- Tiny 6–8px radii everywhere
