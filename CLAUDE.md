# Thunder Trader — Claude Code Project Context

> Read this file at the start of every session. It replaces re-explaining the stack.

## What This Project Is

Two connected systems:
1. **TradingView MCP Server** — lets Claude Code control TradingView Desktop via Chrome DevTools Protocol. Write Pine Script, scan markets, run replay backtests — all from the terminal.
2. **Thunder Trader Bot** — 7-agent consensus trading bot (local machine, Kraken exchange, XBT/USDT). Code lives locally; paste logs here for analysis.

## Repo Structure

```
pine/
  momentum_ribbon_pro.pine   ← Main indicator — load on every chart
rules/
  entry_rules.json           ← READ before every trading decision
prompts/
  01-morning-scan.md         ← Run 09:25 EST daily
  02-signal-check.md         ← Run when TradingView alert fires
  03-batch-scan.md           ← Quick market pulse anytime
  subagent-patterns.md       ← How to parallelize work with subagents
  voice-thinking-template.md ← Mobile voice mode template
scripts/
  replay_backtest.md         ← Validate strategy before live trading
  restore.sh                 ← Restore from backup
backups/                     ← Timestamped snapshots before any changes
.claude/
  settings.json              ← Model, permissions, memory config
  styles/
    skeptical-senior-eng.md  ← Custom pushback persona
  commands/                  ← Slash command skills
artifacts/
  trading-signal-generator.html  ← Standalone Claude API signal tool
```

## Stack

| Layer | Tech |
|-------|------|
| Language | TypeScript (Node 20) |
| MCP SDK | `@modelcontextprotocol/sdk` |
| CDP client | `puppeteer-core` |
| TV control | Chrome DevTools Protocol → TradingView Desktop |
| Pine Script | v5 — EMA ribbon + ADX + volume + session filters |
| PDF output | `pdfkit` |
| Bot exchange | Kraken WebSocket (local machine) |
| Bot ML model | NeoQuasar/Kronos-small (HuggingFace) |

## MCP Tool Reference

```
tv_health_check()                          → verify CDP connection first, always
chart_set_symbol(symbol)                   → switch active chart
chart_set_timeframe(timeframe)             → "1", "5", "D", etc.
chart_set_type(type)                       → "Candles", "Heikin-Ashi"
chart_scroll_to_date(date)                 → "YYYY-MM-DD"
pane_set_symbol(index, symbol)             → multi-pane layout
quote_get(symbol?)                         → read live price
capture_screenshot(region, filename)       → save PNG to ./screenshots/
batch_run(symbols[], action, delay_ms)     → loop: set symbol → action → delay
ui_open_panel(panel, action)               → open Pine editor ("pine-editor", "open")
pine_set_source(code)                      → inject Pine Script into editor
pine_smart_compile()                       → compile + add to chart, return errors
replay_start(date)                         → enter replay mode at date
replay_status()                            → current bar, open position P&L
replay_step(bars?)                         → advance N bars (default 1)
replay_trade(action)                       → "buy" | "sell" | "close"
replay_stop()                              → exit replay, return to live
watchlist_add(symbol)                      → partially working (DOM fragile)
```

## Non-Negotiable Trading Rules

1. Read `rules/entry_rules.json` before every decision.
2. Never place real trades during morning scan or batch scan — analysis only.
3. All 5 gates must pass for APPROVED signal:
   - EMA full stack flip (this bar or last 2)
   - ADX ≥ 22
   - Volume ≥ 1.4× 20-bar average
   - In session (09:30–15:45 EST for futures)
   - 1H ribbon agrees with 5m ribbon
4. Daily hard stop: 3% drawdown → halt all trading.
5. Max 3 trades per day.
6. No trades during FOMC, NFP, CPI.
7. Minimum 50-trade backtest before live — expectancy must be > 0.3R.

## Standard Workflow

```
09:25 EST  → /morning-scan
alert fires → /signal-check SYMBOL DIRECTION PRICE
anytime     → /batch-scan
before change → cp -r . backups/$(date +%Y-%m-%d_%H-%M)_pre-[desc]
```

## Model Selection Guide (use the right model for the task)

| Task | Model | Why |
|------|-------|-----|
| Morning scan, signal check, batch scan | **Sonnet 4.6** | Fast, 80% as capable, default |
| Pine Script architecture, strategy redesign | **Opus 4.7** | Complex reasoning needed |
| Bulk log analysis, 200+ candles, batch PDFs | **Haiku 4.5** | Don't waste Opus tokens |
| Thunder Trader bug diagnosis (deep) | **Opus 4.7** | Multi-file reasoning |

Default to Sonnet. Switch to Opus only for gnarly architectural decisions.
Use Haiku for batch work — it's genuinely good at it.

## Subagent Pattern (Tip 10 — parallelize work)

Spin off subagents for independent tasks so you can keep coding:
```
"Spin off a subagent to screenshot all 4 instruments while I fix the Pine compile error"
"Run the batch scan subagent in the background while I diagnose the Kronos bug"
```
See `prompts/subagent-patterns.md` for ready-to-paste subagent prompts.

## EMA Ribbon Parameters

Default 8/13/21/34 — works on 5-min futures (NQ, ES) and daily crypto.
- Slower markets (Gold, Oil): 13/21/34/55
- Faster/crypto (BTC 1-min): 5/8/13/21
- Daily swing: 10/20/50/100

Never change EMA lengths without re-running the backtest.

## Thunder Trader Bot — Known Bugs (2026-05-16)

**BUG 1 — R:R hardcoded at 1.39, blocks ALL trades** ← fix this first
- TP = SL × 1.389 every bar; min R:R requirement = 2.0 → no trade ever executes
- Fix: use next structural S/R for TP, or lower min_rr to 1.5

**BUG 2 — Agent dropout kills quorum**
- DIVERGENCE + WHALE agents crash after asyncio `ConnectionResetError` (WinError 10054)
- `too_few_agents(2<3)` blocks 20 of 32 candles
- Fix: coroutine health monitor with auto-restart

**BUG 3 — Kronos bullish bias on bearish days**
- Predicted positive returns on 30/32 candles during -1.8% BTC session
- Fix: audit `kronos_predict()` for sign error or `abs()` call on output

**BUG 4 — score=-0.991 sentinel value**
- Hardcoded fallback when <3 agents respond; corrupts analytics

**BUG 5 — vol=0.0 feed dropout** — no guard clause at 09:45 candle

**BUG 6 — Kelly floor hardcoded at 0.57** — same value every bar

## Backup Protocol

```bash
cp -r . backups/$(date +%Y-%m-%d_%H-%M)_pre-[description]
git add . && git commit -m "backup: before [description]"
```

## Claude.ai Web Tips (not Claude Code CLI)

- **Memory** (Tip 3): On by default — Claude reads past chats. Turn off in Settings if unwanted.
- **Search past chats** (Tip 4): Ask "what was the Pine Script fix we landed on Tuesday?" — it finds it.
- **Voice mode** (Tip 7): Walk through a problem, use `prompts/voice-thinking-template.md` structure.

## DO NOT

- Run live order execution without completing `scripts/replay_backtest.md` first
- Change EMA lengths without re-running the backtest
- Skip HTF alignment check (5m alone is not enough)
- Use `git add -A` — stage specific files only
- Trade on a live account until 50-trade backtest shows expectancy > 0.3R
