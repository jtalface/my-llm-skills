---
name: ui-themes
description: >-
  Lists and applies a personal catalog of reusable UI design themes (looks/templates). Use when
  the user asks to show looks, list themes, pick a design template, apply a
  theme, design primitives, lime-lab, lavish, lapis, ledger, or ui-themes.
---

# UI Themes

Personal catalog of design systems for Cursor, Claude Code CLI, and Claude Code app.

Install by copying or symlinking this folder into your agent's skills directory (e.g. `~/.claude/skills/ui-themes`, `~/.cursor/skills/ui-themes`).

## List & select (default when no theme id)

When the user says things like “show my looks”, “list themes”, `/ui-themes`, or “apply a theme” **without** an id:

1. Scan `themes/*/` (each folder name is a theme id).
2. Present a numbered picker with vibe + preview path.
3. For each theme, read the vibe from `themes/<id>/primitives.md`.
4. If `preview.png` exists, show/mention it.
5. **Stop and wait** for them to pick a number or id.
6. Then run **Apply** for that theme.

Do not apply a theme until they select one (unless they already named the id).

## Catalog

| ID | Vibe | Folder |
|----|------|--------|
| `lime-lab-dark` | Dark charcoal lab, lime accent, Syne + IBM Plex Mono | [themes/lime-lab-dark/](themes/lime-lab-dark/) |
| `lime-lab-light` | Soft green-white lab, lime CTAs, same type system | [themes/lime-lab-light/](themes/lime-lab-light/) |
| `lavish-dark` | DaisyUI luxury — ink black, champagne gold, white CTAs | [themes/lavish-dark/](themes/lavish-dark/) |
| `lavish-light` | Champagne paper, espresso type, dark CTAs, gold accents | [themes/lavish-light/](themes/lavish-light/) |
| `lapis` | Inbox SaaS — cool gray canvas, indigo accent (single mode) | [themes/lapis/](themes/lapis/) |
| `ledger-dark` | Warm editorial night — charcoal, violet, cream CTAs | [themes/ledger-dark/](themes/ledger-dark/) |
| `ledger-light` | Warm editorial — cream paper, ink CTAs, violet accent | [themes/ledger-light/](themes/ledger-light/) |

Keep this table in sync when adding themes. Prefer scanning `themes/` so new folders still appear even if the table lags.

**Aliases (legacy):**
- `lime-lab` / `lime-lab-darkmode` → `lime-lab-dark`
- `lime-lab-day` → `lime-lab-light`
- `ledger` → ask dark vs light (default `ledger-light`)

## How to invoke

| Goal | Say |
|------|-----|
| See all looks + pick | `/ui-themes` · “show my looks” · “list themes” |
| Apply one directly | “apply lime-lab-light” · `/ui-themes lime-lab-dark` |
| Add a new look | “add a ui-theme from this project” |

## Single-mode themes

Some looks have only one mode (e.g. `lapis`). Apply as `lapis` with no `-dark`/`-light` suffix. Do not invent a second mode unless asked.

## Apply

1. Read `themes/<id>/primitives.md`
2. Read `themes/<id>/tokens.css` and `themes/<id>/components.css`
3. Install into the target project:
   - Load fonts from primitives
   - Put `:root` tokens in global CSS
   - Reuse or adapt component classes; restyle existing UI with the same tokens
4. Follow that theme’s do/don’t rules exactly
5. Do **not** mix themes or fall back to generic AI UI (purple gradients, Inter-only, cream+terracotta) unless asked

## Adding a new theme

Create `themes/<new-id>/` with:

- `primitives.md` — vibe (first line after title), type, spacing, do/don’t
- `tokens.css` — CSS variables + base body
- `components.css` — reusable classes
- `preview.png` — optional screenshot (strongly recommended for the picker)

Add a row to the Catalog table above.
