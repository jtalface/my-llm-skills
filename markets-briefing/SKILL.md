---
name: markets-briefing
description: Generate and email a daily pre-market intelligence brief for Jose Alface covering US futures, AI/tech watchlist, global markets, economic calendar, and key trading signals. Trigger when user asks for the pre-market brief, morning briefing, or "run the markets skill". Also runs automatically each weekday at 4:40am PDT.
---

# Daily Pre-Market Snapshot Skill

## Overview

You are generating a **pre-market intelligence brief** for an active investor (Jose Alface, jtalface@gmail.com) focused on AI and technology stocks. The brief is delivered via Gmail **and Telegram** at 4:40am PDT (7:40am ET) every weekday.

**Tone rules — non-negotiable:**
- No PR language ("exciting", "innovative", etc.)
- Every data point needs a delta — not just where things are, but how they moved
- Flag anomalies explicitly with ⚠️
- Opinions allowed — when data points clearly somewhere, say it
- Every sentence must give a number, explain a why, or flag a risk. Cut anything else.

---

## Step 0 — Market Holiday Check

Before doing anything else, check if today is a US market holiday. The NYSE is closed on:
- New Year's Day (Jan 1), MLK Jr. Day (3rd Mon Jan), Presidents' Day (3rd Mon Feb)
- Good Friday (Friday before Easter), Memorial Day (last Mon May)
- Juneteenth (Jun 19), Independence Day (Jul 4), Labor Day (1st Mon Sep)
- Thanksgiving (4th Thu Nov), Christmas Day (Dec 25)

If today is a US market holiday, **do not send the email and exit**. If the holiday falls on a weekend, the market observes the nearest weekday — apply standard NYSE holiday rules.

---

## Step 1 — Data Gathering

Use `firecrawl_search` as your primary search tool and `web_fetch` for scraping specific pages. Run searches in parallel where possible.

### 1A. Futures & Macro Data
Scrape or search for current values of:
- **US Futures**: ES (S&P 500), NQ (Nasdaq 100), RTY (Russell 2000), YM (Dow) — level + change + %
- **VIX**: current level, 5-day trend direction, term structure (contango vs. backwardation if available)
- **Put/Call ratio**: previous day close
- **10-Year Treasury yield** and **2-Year Treasury yield** — level + direction
- **DXY** (Dollar Index) — level + % change
- **Gold** (XAU/USD or GLD) — level + %
- **WTI Crude** — level + %
- **Bitcoin** (BTC/USD) — level + %

**Sources**: Search "US futures pre-market [today's date]" and "VIX level today". Try fetching https://finviz.com/futures.ashx for live data.

### 1B. AI/Tech Watchlist Pre-Market Prices
For each of these tickers, search for the current pre-market price, % change, and volume vs. average:

```
AI INFRASTRUCTURE:   NVDA, AMD, AVGO, INTC, QCOM, MRVL, ARM
MEMORY/STORAGE:      MU, WDC, STX
SEMIS EQUIPMENT:     ASML, LRCX, AMAT, KLAC, ONTO, COHU
FOUNDRY/SUPPLY:      TSM
HYPERSCALERS:        MSFT, GOOGL, AMZN, META, ORCL
AI SOFTWARE/INFRA:   PLTR, SNOW, NET, CRWD, DDOG, SMCI
```

Search: "AI semiconductor stocks pre-market movers [today's date]". Focus on stocks moving >1% — those need a catalyst explanation.

For each mover (>1%), search specifically for: "[TICKER] pre-market [today's date] reason" to find the actual catalyst.

### 1C. Analyst Actions & News
Search for overnight analyst actions:
- "[watchlist tickers] upgrade downgrade price target [today's date]"
- "semiconductor AI stock analyst [today's date]"
- Check for any earnings reports from watchlist companies today (pre or post market)
- Product launches, export control news, government contracts, partnerships

### 1D. Global Markets
Search: "Asian markets overnight [today's date]" and "European markets [today's date]"
Get: Nikkei 225, Hang Seng, CSI 300/Shanghai, DAX, FTSE 100, Euro Stoxx 50 — level + % change

### 1E. Economic Calendar
Search: "US economic calendar [today's date] releases"
Key releases to flag: CPI, PPI, NFP, FOMC minutes/decision, ISM Manufacturing/Services, GDP, PCE, jobless claims
Get consensus estimates and prior values where available.

### 1F. Fed & Rates
Search: "CME FedWatch rate probability [today's date]" and "next FOMC meeting date"
Get: current Fed Funds rate, next FOMC date, implied cut/hike probability, any Fed speaker comments from yesterday/overnight.

### 1G. SOX & Sector Data
Search: "Philadelphia Semiconductor Index SOX [today's date]" and "S&P 500 sector performance yesterday"
Get: SOX level + %, SOXX ETF, top 2 and bottom 2 S&P sectors from yesterday's close.

### 1H. Earnings Radar (5-day window)
Search: "[watchlist tickers] earnings [this week's dates]"
Find any watchlist company reporting earnings in the next 5 trading days. Get: EPS estimate, revenue estimate, date, time (pre/post market).

---

## Step 2 — Compile the Brief

Using all gathered data, compose the brief following this exact structure. Use your judgment — if data for a subsection is unavailable or unreliable, omit it cleanly rather than pad with uncertainty.

### Email Subject Line
```
📊 Pre-Market Brief — [Weekday, Month Day] | NQ [±X.X%] | VIX [XX.X]
```

### HTML Email Body

Build a clean HTML email with:
- White background, dark text, 16px base font, max-width 680px centered
- Section headers in dark blue (#1a237e), bold, with a thin bottom border
- Numbers in **bold**, ▲ for positive moves (green #2e7d32), ▼ for negative (red #c62828)
- ⚠️ for anything anomalous or requiring attention
- Tables with light grey (#f5f5f5) alternating rows
- Clean, mobile-readable — no images, no external CSS dependencies

**SECTION 1 — MARKET PULSE**

Dashboard table of US Futures (ES, NQ, RTY, YM) with level, change, %. Flag any future down >0.5% or up >0.5% with context.

Risk Barometers block:
- VIX: level, 5-day trend, term structure note
- Put/Call ratio (prior day)

Macro Gauges block: 10Y yield, 2Y yield, DXY, Gold, WTI Crude, Bitcoin — each with level and % change. Flag anything outside normal range (VIX >25 = elevated, 10Y >4.8% = elevated, DXY >106 = strong).

**One-Line Market Mood** (bold, italic): One sentence synthesizing what these numbers collectively say about today's setup.

---

**SECTION 2 — AI/TECH WATCHLIST**

**2A. Pre-Market Movers**
List stocks moving >1% with: ticker, pre-market price, % change, volume vs. avg, and a one-sentence catalyst. Then: "Signal: [hold/fade]" based on catalyst quality and volume.

If fewer than 3 stocks are moving >1%, note the quietness: "Light pre-market activity — most names within 0.5% of prior close."

**2B. Key Catalysts Today**
- Earnings today: [Ticker] — consensus EPS $X, rev $Xb, focus: [specific metric market cares about]
- Analyst actions: [Bank] [upgraded/downgraded] [TICKER] from [X] to [Y], PT [old→new]. Weight: [major/minor bank]
- Product/regulatory/conference news

**2C. Sector Narrative**
3–5 sentences on what's driving the AI/semiconductor sector right now. What's the 2–4 week thesis? What is the market worried about? What's the next catalyst being waited on? Be specific — name the dynamic.

**2D. SOX & SOXX Watch**
SOX level + % + trend direction. SOXX ETF note. SOX vs. Nasdaq comparison (semis leading or lagging?).

---

**SECTION 3 — BROADER MARKET CONTEXT**

**3A. Overnight Global Markets**
Table: Market | Index | Level | % Change | Driver (only if US-relevant)
Rows: Japan/Nikkei, Hong Kong/Hang Seng, China/Shanghai, Germany/DAX, UK/FTSE, Europe/Euro Stoxx 50

**3B. Today's Economic Calendar**
Table of market-moving releases only: Time (ET) | Release | Estimate | Prior | Why It Matters
Rate the day: **[Low / Medium / High] impact day**. One sentence explaining.

**3C. Fed & Rate Environment**
2–3 sentences max. Current rate, next FOMC date + implied probability, any overnight shift. On quiet days: one sentence only.

**3D. Sector Rotation (Yesterday's Close)**
Top 2 sectors, bottom 2 sectors. One sentence: is money moving into defensives or growth?

---

**SECTION 4 — SIGNALS FOR ACTIVE MANAGEMENT**

**4A. Key Levels to Watch**
For NQ futures, NVDA, MU, SOX, and SPX (or whichever are most relevant today):
> **[Instrument]**: At $X. Support $Y ([basis]). Resistance $Z ([basis]). [One sentence on current positioning.]

**4B. Options Market Intelligence**
- NVDA implied volatility vs. 30-day average (elevated/normal/suppressed)
- Any unusual options activity on watchlist names (large sweeps from yesterday)
- Earnings IV crush warning if any watchlist name reports today

*(Skip 4C — institutional flow/dark pool data not reliably available)*

**4D. Today's Risk Assessment**
One paragraph, 3–4 sentences. What are the 2–3 biggest risks to the long AI/tech thesis specifically today? Name them, number them, be specific.

---

**SECTION 5 — EARNINGS RADAR**

Table (only show if watchlist companies have earnings in next 5 trading days):
Date | Ticker | Time | EPS Est. | Rev Est. | What to Watch

"What to Watch" must be the specific metric the market is focused on — not generic.

If no watchlist earnings in next 5 days, omit this section entirely.

---

**Footer**
Small grey text: "Pre-Market Brief | Generated [time] | Data sourced from public market data as of ~4:30am PDT | Not financial advice"

---

## Step 3 — Deliver: Gmail + Telegram

Run both deliveries. If one fails, still attempt the other.

### 3A. Gmail
Call `send_gmail` tool with:
- to: "jtalface@gmail.com"
- subject: [the subject line from Step 2]
- body: [the full HTML email body]
- is_html: true

### 3B. Telegram
Compose a plain-text Telegram version (under 4000 chars). Format:

```
📊 Pre-Market Brief — [Day, Date]

🔢 MARKET PULSE
• NQ: [level] [▲/▼X.X%]  ES: [level] [▲/▼X.X%]
• VIX: [level] ([trend])  Put/Call: [X.XX]
• 10Y: [X.XX%]  2Y: [X.XX%]  DXY: [X.X]
• Gold: $[X]  WTI: $[X]  BTC: $[X]

[One-Line Market Mood]

📱 AI/TECH MOVERS
[Movers >1%: TICKER ▲/▼X.X% — catalyst in one line]

📰 KEY CATALYSTS
[Analyst actions, earnings today, major news — bullets]

🌍 GLOBAL MARKETS
[Nikkei, Hang Seng, DAX, FTSE — one line each with %]

📅 ECON CALENDAR
[Market-moving releases — time, name, estimate]
[Impact: Low/Medium/High]

⚠️ RISKS TODAY
[2-3 specific risks numbered]

📆 EARNINGS RADAR
[Watchlist companies reporting this week, or omit if none]
```

Call `send_telegram` tool with:
- message: [the plain-text brief above]

---

## Quality Checklist

- [ ] Every number has a direction indicator (▲/▼ or +/-)
- [ ] Every pre-market mover has an actual catalyst (not "market conditions")
- [ ] Anomalies are flagged with ⚠️
- [ ] No sentences that are purely descriptive with no number, why, or risk
- [ ] Earnings radar only shows watchlist companies
- [ ] Risk assessment is specific to today, not generic
- [ ] Email renders cleanly in HTML (no broken tags)
