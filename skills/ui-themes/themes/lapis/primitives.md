# Lapis — design primitives

Single-mode theme extracted from a product inbox app. Clean light SaaS: soft gray canvas, white surfaces, indigo accent.

**Preview:** [preview.png](preview.png)

**Name:** Lapis (indigo / blue stone). Alternatives considered: Lucid, Lattice, Loom.

## Vibe (one sentence)

A crisp product inbox UI — airy slate canvas, white cards, indigo actions, system-clear hierarchy.

## Source

- CSS vars observed on `:root`: `--accent #4f46e5`, `--accent-soft #eef0ff`, `--surface #ffffff`, `--fg-muted #526077`, body `#f5f6f8`

## Typography

| Role | Font |
|------|------|
| Display + UI | **Plus Jakarta Sans** (polished SaaS sans; the source app used system-ui) |
| Code | **IBM Plex Mono** |

## Color

| Token | Hex | Use |
|-------|-----|-----|
| `--bg` | `#f5f6f8` | Page canvas |
| `--bg-elevated` / `--bg-panel` | `#ffffff` | Header / cards |
| `--line` | `#e2e8f0` | Borders |
| `--text` | `#0f172a` | Primary text |
| `--muted` | `#526077` | Secondary (`--fg-muted`) |
| `--accent` | `#4f46e5` | Indigo CTA / active |
| `--accent-dim` | `#4338ca` | Hover / stronger indigo |
| `--accent-soft` | `#eef0ff` | Soft indigo wash |
| `--accent-ink` | `#ffffff` | On indigo buttons |
| `--danger` | `#dc2626` | Destructive |
| `--focus` | `#4f46e5` | Focus ring |

## Proportions

| Measure | Value |
|---------|-------|
| Panel radius | `0.75rem` |
| Control radius | `0.5rem` (pills often `999px`) |
| Base size | `16px` |

## Mode

**Single mode only** — no dark/light variants. Do not invent a dark sibling unless asked.

## Do

- Indigo sparingly: active nav, CTAs, unread accents, badges
- White surfaces on cool gray canvas
- Soft borders, generous whitespace

## Don’t

- Gold/luxury (lavish) or lime neon (lime-lab)
- Heavy shadows
- Forcing a dark mode
