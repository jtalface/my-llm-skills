# my-llm-skills

A personal collection of Claude AI skills — automated agents, digest bots, and productivity tools.

## Structure

Each skill lives in its own directory under `skills/`:

```
skills/
  <skill-name>/
    SKILL.md        # The skill definition (required)
    assets/         # Optional: images, templates, supporting files
    README.md       # Optional: longer docs for complex skills
```

Skills may also carry other supporting folders the skill reads at runtime, such as `ui-themes/themes/` or `auto-research/examples/`.

### What is a SKILL.md?

A `SKILL.md` file is a self-contained prompt that defines what a Claude skill does. It includes:
- YAML frontmatter with `name` and `description`
- Step-by-step instructions the agent follows when invoked
- Any configuration (delivery targets, formatting rules, etc.)

To install a skill locally, package it with the Claude skill-creator tool and double-click the resulting `.skill` file.

## Skills

| Skill | Description | Schedule |
|---|---|---|
| [atlas](skills/atlas/) | Institutional-grade buy-side equity research — 23-section report per company (financials, moat, DCF, risks, catalysts, memo) | On demand (`/atlas`) |
| [auto-research](skills/auto-research/) | Karpathy-style autoresearch loop — builds a benchmark for any target, then modifies, measures, and keeps or reverts until stopped | On demand (`/autoresearch`) |
| [markets-briefing](skills/markets-briefing/) | Daily pre-market brief — US futures, AI/tech watchlist, global markets, economic calendar, trading signals — delivered by email | Weekdays 4:40am PDT (GitHub Actions) |
| [ui-themes](skills/ui-themes/) | Catalog of reusable UI design themes (Lime Lab, Lavish, Lapis, Ledger) — list them with previews, then apply one's fonts, tokens, and components to a project | On demand (`/ui-themes`) |
| [worldcup-digest](skills/worldcup-digest/) | FIFA World Cup 2026 live snapshot — standings, schedule, news — delivered to Telegram + email | Daily 4am & 9pm PDT (cloud) |

## Adding a New Skill

1. Create a directory: `skills/<your-skill-name>/`
2. Write `SKILL.md` with the required frontmatter:
   ```markdown
   ---
   name: your-skill-name
   description: One-line description of what this skill does.
   ---

   Your skill prompt here...
   ```
3. Add it to the table above
4. Package and install: `python3 -m scripts.package_skill ~/.codex/skills/<skill-name>`
