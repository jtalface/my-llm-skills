#!/usr/bin/env python3
"""
Daily Pre-Market Brief — Remote Runner
Runs on GitHub Actions every weekday at 7:40am ET (11:40 UTC).
Uses Claude API + Firecrawl + Composio (Gmail + Telegram).

Required GitHub Secrets:
  ANTHROPIC_API_KEY  - Anthropic API key
  COMPOSIO_API_KEY   - Composio API key (for Gmail + Telegram)
  FIRECRAWL_API_KEY  - Firecrawl API key (for web search)
"""

import os
import sys
import json
import requests
from datetime import datetime, timezone
from pathlib import Path

import anthropic
from firecrawl import FirecrawlApp

# ── Market Holiday Check (NYSE) ───────────────────────────────────────────────
# Update this list annually. Source: https://www.nyse.com/markets/hours-calendars
MARKET_HOLIDAYS = {
    # 2026
    "2026-01-01", "2026-01-19", "2026-02-16", "2026-04-03",
    "2026-05-25", "2026-06-19", "2026-07-03", "2026-09-07",
    "2026-11-26", "2026-12-25",
    # 2027
    "2027-01-01", "2027-01-18", "2027-02-15", "2027-03-26",
    "2027-05-31", "2027-06-18", "2027-07-05", "2027-09-06",
    "2027-11-25", "2027-12-24",
}

# Use ET time for holiday check (UTC-5/UTC-4)
from zoneinfo import ZoneInfo
et_now = datetime.now(ZoneInfo("America/New_York"))
today_str = et_now.strftime("%Y-%m-%d")
today_display = et_now.strftime("%A, %B %d, %Y")

if today_str in MARKET_HOLIDAYS:
    print(f"NYSE holiday today ({today_str}) — no brief sent.")
    sys.exit(0)

if et_now.weekday() >= 5:  # Saturday=5, Sunday=6
    print(f"Weekend ({today_str}) — no brief sent.")
    sys.exit(0)

print(f"Generating pre-market brief for {today_display}...")

# ── Initialize clients ────────────────────────────────────────────────────────
anthropic_client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
firecrawl = FirecrawlApp(api_key=os.environ["FIRECRAWL_API_KEY"])
COMPOSIO_API_KEY = os.environ["COMPOSIO_API_KEY"]
COMPOSIO_BASE = "https://backend.composio.dev/api/v1"

# ── Composio REST helper ──────────────────────────────────────────────────────
def composio_execute(action_slug: str, params: dict) -> dict:
    """Execute a Composio action via REST API."""
    resp = requests.post(
        f"{COMPOSIO_BASE}/actions/{action_slug}/execute",
        headers={
            "X-API-Key": COMPOSIO_API_KEY,
            "Content-Type": "application/json",
        },
        json={"input": params},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()

# ── Tool definitions for Claude ───────────────────────────────────────────────
TOOLS = [
    {
        "name": "firecrawl_search",
        "description": "Search the web for real-time market data, news, and financial information.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "num_results": {"type": "integer", "description": "Number of results (default 5)", "default": 5},
            },
            "required": ["query"],
        },
    },
    {
        "name": "web_fetch",
        "description": "Fetch and return the content of a specific URL as clean markdown text.",
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "URL to fetch"},
            },
            "required": ["url"],
        },
    },
    {
        "name": "send_gmail",
        "description": "Send the pre-market brief as an HTML email via Gmail.",
        "input_schema": {
            "type": "object",
            "properties": {
                "to": {"type": "string", "description": "Recipient email address"},
                "subject": {"type": "string", "description": "Email subject line"},
                "body": {"type": "string", "description": "HTML email body"},
                "is_html": {"type": "boolean", "description": "Whether body is HTML", "default": True},
            },
            "required": ["to", "subject", "body"],
        },
    },
    {
        "name": "send_telegram",
        "description": "Send the pre-market brief as a plain-text message via Telegram.",
        "input_schema": {
            "type": "object",
            "properties": {
                "message": {"type": "string", "description": "Plain-text message to send (max 4000 chars)"},
            },
            "required": ["message"],
        },
    },
]

# ── Tool handler ──────────────────────────────────────────────────────────────
def handle_tool(name: str, inp: dict) -> str:
    try:
        if name == "firecrawl_search":
            results = firecrawl.search(
                query=inp["query"],
                limit=inp.get("num_results", 5),
            )
            return json.dumps(results, default=str)[:12000]

        elif name == "web_fetch":
            result = firecrawl.scrape_url(inp["url"], formats=["markdown"])
            content = getattr(result, "markdown", None) or str(result)
            return content[:8000]

        elif name == "send_gmail":
            result = composio_execute(
                "GMAIL_SEND_EMAIL",
                {
                    "recipient_email": inp["to"],
                    "subject": inp["subject"],
                    "body": inp["body"],
                    "is_html": inp.get("is_html", True),
                },
            )
            print(f"  Gmail result: {result.get('successfull', result.get('success', '?'))}")
            return json.dumps(result)

        elif name == "send_telegram":
            msg = inp["message"]
            # Try TELEGRAM_SEND_MESSAGE first, fall back to TELEGRAM_SENDMESSAGE
            for action in ["TELEGRAM_SEND_MESSAGE", "TELEGRAM_SENDMESSAGE", "TELEGRAM_SEND_A_MESSAGE"]:
                try:
                    result = composio_execute(action, {"message": msg, "text": msg})
                    print(f"  Telegram ({action}) result: {result.get('successfull', result.get('success', '?'))}")
                    return json.dumps(result)
                except Exception as e:
                    print(f"  Telegram action {action} failed: {e}")
                    continue
            return json.dumps({"error": "All Telegram action slugs failed"})

        else:
            return json.dumps({"error": f"Unknown tool: {name}"})

    except Exception as e:
        print(f"  Tool {name} error: {e}")
        return json.dumps({"error": str(e)})

# ── Read the skill prompt ─────────────────────────────────────────────────────
skill_path = Path(__file__).parent / "SKILL.md"
skill_content = skill_path.read_text(encoding="utf-8")

prompt = f"""You are running in GitHub Actions (remote execution, no human present).
Today is {today_display}. Current time: approximately {et_now.strftime('%I:%M%p')} ET.
US pre-market has been open since 4:00am ET. Asian markets are closing, European markets are open.

You have access to these tools:
- firecrawl_search: Search the web for real-time data
- web_fetch: Fetch a specific URL
- send_gmail: Send the HTML brief to jtalface@gmail.com
- send_telegram: Send the plain-text brief via Telegram

Execute the following skill completely. Ignore any MCP-style tool references (mcp__...) in the skill — use the tools listed above instead.

{skill_content}"""

# ── Agentic loop ──────────────────────────────────────────────────────────────
messages = [{"role": "user", "content": prompt}]
MAX_ITERATIONS = 50  # safety cap

for i in range(MAX_ITERATIONS):
    print(f"Iteration {i + 1}...")

    response = anthropic_client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=8192,
        tools=TOOLS,
        messages=messages,
    )

    messages.append({"role": "assistant", "content": response.content})

    if response.stop_reason == "end_turn":
        print("✅ Brief completed and delivered.")
        sys.exit(0)

    if response.stop_reason == "tool_use":
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                print(f"  → {block.name}({json.dumps(block.input)[:120]}...)")
                result = handle_tool(block.name, block.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result,
                })
        messages.append({"role": "user", "content": tool_results})
    else:
        print(f"Unexpected stop reason: {response.stop_reason}")
        sys.exit(1)

print("⚠️  Hit max iterations limit.")
sys.exit(1)
