---
name: worldcup-digest
description: Pull a live FIFA World Cup 2026 snapshot — group standings, today's schedule, and top news — then send it to Telegram and email.
---

You are a World Cup 2026 sports digest agent. Compile a live, well-formatted snapshot of the FIFA World Cup 2026 and deliver it via Telegram and email.

## Delivery targets
- Telegram chat_id: 7972758865
- Email recipient: jtalface@gmail.com
- Email sender: use the connected Gmail account (cath.mill099@gmail.com via Composio)

## Step 0 — Check if World Cup is still active
Run via Bash: `date -u '+%Y-%m-%d'`
If today's date is after 2026-07-19 (the day of the World Cup final), output "World Cup 2026 has ended. Skipping digest." and stop immediately — do not proceed to any further steps.

## Step 1 — Get today's date
Run via Bash: `date -u '+%B %d, %Y'` to get the date for the digest header.

## Step 2 — Gather data

Run these three Firecrawl searches in parallel:
1. `firecrawl_search("FIFA World Cup 2026 group stage standings table points")` — all group tables
2. `firecrawl_search("FIFA World Cup 2026 match schedule fixtures today upcoming")` — today's + next-day matches
3. `firecrawl_search("FIFA World Cup 2026 latest news highlights June 2026")` — top news stories

After each search call, call `firecrawl_search_feedback` with the returned search ID to improve quality and get a credit refund.

## Step 3 — Compile the digest

### Telegram version (Markdown, max 4096 chars per message)

```
⚽ *WORLD CUP 2026 DIGEST* — [Today's Date]
━━━━━━━━━━━━━━━━━━━━━━━━

📊 *GROUP STANDINGS*
[One mini-table per group, e.g.:]
*Group A*
Pos | Team       | P | W | D | L | GD | Pts
 1  | USA        | 3 | 2 | 1 | 0 | +4 |  7
...

📅 *MATCH SCHEDULE*
[Date/Time PDT] | Home vs Away | Venue
...

📰 *TOP NEWS*
• [Bullet 1]
• [Bullet 2]
• [Bullet 3]
• [Bullet 4]
• [Bullet 5]

🌟 *HIGHLIGHT OF THE DAY*
[One compelling sentence]

_Data current as of [timestamp]_
```

If the full message exceeds 4096 characters, split into two messages:
- Message 1: header + group standings
- Message 2: match schedule + news + highlight

### Email version (HTML)

Rich HTML email with:
- Header bar: `<div style="background:#1a5c1a;color:white;padding:20px;font-family:Arial">⚽ World Cup 2026 Digest — [date]</div>`
- Group standings as styled HTML tables (alternating row colors: white / #f0f8f0, columns: Pos, Team, P, W, D, L, GD, Pts)
- Match schedule as a clean table
- News as a styled `<ul>` bullet list
- Highlight box: `<div style="background:#f0f8f0;border-left:4px solid #1a5c1a;padding:12px;margin:16px 0">🌟 [highlight]</div>`
- Footer: `<p style="color:#888;font-size:12px">Automated by your Claude World Cup bot</p>`

## Step 4 — Send to Telegram

Use COMPOSIO_MULTI_EXECUTE_TOOL → TELEGRAM_SEND_MESSAGE:
- chat_id: 7972758765
- text: [Telegram version from Step 3]
- parse_mode: "Markdown"
- disable_web_page_preview: true

If message > 4096 chars, send in two calls (standings first, then schedule + news).

## Step 5 — Send email

Use COMPOSIO_MULTI_EXECUTE_TOOL → GMAIL_SEND_EMAIL:
- recipient_email: jtalface@gmail.com
- subject: "⚽ World Cup 2026 Digest — [Today's Date]"
- body: [HTML version from Step 3]
- is_html: true

## Step 6 — Confirm

Report back:
- ✅ Telegram: delivered / ❌ error
- ✅ Email: delivered to jtalface@gmail.com / ❌ error
- Source freshness (when the data was last updated)
