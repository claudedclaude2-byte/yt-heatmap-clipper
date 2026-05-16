# TradingView MCP Automation — Full Video Analysis & Build Plan

## What the Video Shows

**Title overlay:** "Claude now automates TradingView via terminal to write Pine Script and scan markets in real-time"

**Source:** 54-second vertical (720×1280) social-media clip, published ~May 11 2025, by an account called "tradesdontlie."

It is a live screen recording — split-screen — with TradingView Desktop on the left and a Claude Code CLI terminal on the right. The Claude model running is **Opus 4.6** (visible in the status bar). "Bypass permissions on" is enabled, meaning every MCP tool call fires without a confirmation prompt.

---

## Scene-by-Scene Breakdown

| Time | Scene | MCP Calls Observed |
|------|-------|-------------------|
| 0–3s | NQ1! 1-min chart. Claude runs a health check and loads tools. | `tv_health_check` |
| 3–9s | Switches to BTCUSD 1-min. | `chart_set_symbol(symbol: "BTCUSD")` |
| 9–12s | BTCUSD switches to Daily Heikin-Ashi. Reads a screenshot. | `quote_get`, `capture_screenshot` |
| 12–18s | "Time travel" — scrolls to the 2024 Bitcoin halving date. | `chart_scroll_to_date(date: "2024-04-20")` |
| 18–21s | 4-pane layout: NQ1!, BTCUSD, ES1!, COMEX:GC1! + institutional watchlist panel. | `pane_set_symbol(index:1..3, symbol:…)` |
| 21–24s | Returns to NQ1! Daily, regular candles. | `chart_set_symbol("CME_MINI:NQ1!")`, `chart_set_timeframe("5")`, `chart_set_type("Candles")` |
| 24–27s | Switches to NQ1! 5-min. Opens Pine Script editor. | `ui_open_panel(panel:"pine-editor", action:"open")`, `pine_set_source` |
| 27–30s | "MCP Test Indicator" stub injected → compiles clean, zero warnings. | `pine_smart_compile` |
| 30–33s | Replaces stub with full "Claude's Live Momentum Ribbon" — 4-EMA ribbon. Compiles + screenshots. | `pine_smart_compile`, `capture_screenshot(filename:"claude_momentum_ribbon_live")` |
| 33–39s | Ribbon is live on chart. Batch-scans 4 contracts + screenshotting each. | `batch_run(symbols:["CME_MINI:NQ1!","CME_MINI:ES1!","COMEX:GC1!","NYMEX:CL1!"], action:"screenshot", delay_ms:2500)` |
| 39–42s | Enters Replay mode at 2026-03-28. Steps forward 5 bars. | `replay_start(date:"2026-03-28")`, `replay_status`, `replay_step` ×3 |
| 42–45s | Sees no open position → places a paper BUY on NQ1!. | `replay_trade(action:"buy")` |
| 45–48s | Steps forward more bars; ribbon shown turning bearish. | `replay_step` ×multiple |
| 48–51s | Tries to add NVDA to watchlist — gets an honest error. | `watchlist_add(symbol:"NVDA")` → `{"success":false,"error":"Add symbol button not found in watchlist panel"}` |
| 51–54s | Grand finale: NQ1! 1-min screenshot, then a recap capability table. | `chart_set_timeframe("1")`, `capture_screenshot(filename:"grand_finale_nq_1min")` |

---

## Is This Realistic?

**Yes — completely credible.** Evidence:

1. **CDP is a known technique.** TradingView runs in a Chromium-based desktop wrapper. Connecting to it via Chrome DevTools Protocol (CDP) is documented and used by many automation projects.
2. **MCP is real infrastructure.** Claude Code's MCP support (tool calls over JSON-RPC) is production-ready.
3. **The error is authentic.** A fake demo would not show `watchlist_add` returning a failure. This is the hallmark of a real live recording.
4. **Token counts are plausible.** Counters visible (2.4k–3.2k tokens per step) are in the right range for multi-tool agentic calls.
5. **Pine Script is syntactically correct.** The `ta.ema(close, lenN)` calls and `input.int()` pattern are proper Pine v5.
6. **"Bypass permissions on"** is a real Claude Code setting for autonomous agent workflows.
7. **The timing feels live.** The terminal shows genuine "thinking" labels (`Coalesceing…`, `Hyperspacing…`, `Percolating…`) and elapsed times — consistent with a real agentic loop.

---

## What Does It Trade?

This is **paper trading / demonstration only** — no real broker connection. But the instruments scanned are:

| Symbol | Instrument | Exchange |
|--------|-----------|----------|
| NQ1! | Nasdaq-100 E-mini Futures | CME MINI |
| ES1! | S&P 500 E-mini Futures | CME MINI |
| GC1! | Gold Futures | COMEX |
| CL1! | Crude Oil Futures | NYMEX |
| BTCUSD | Bitcoin vs USD | Bitstamp (spot ref) |

Primary focus for live replay simulation: **NQ1! (Nasdaq futures), 5-minute bars.**

---

## How Does It Trade? — The Strategy

**Indicator: "Claude's Live Momentum Ribbon"** (4-EMA stack)

```pinescript
//@version=5
indicator("Claude's Momentum Ribbon", overlay=true)
len1 = input.int(8,  "Fast EMA")
len2 = input.int(13, "Mid EMA")
len3 = input.int(21, "Slow EMA")
len4 = input.int(34, "Anchor EMA")

ema1 = ta.ema(close, len1)
ema2 = ta.ema(close, len2)
ema3 = ta.ema(close, len3)
ema4 = ta.ema(close, len4)

Bullish = ema1 > ema2 and ema2 > ema3 and ema3 > ema4
Bearish = ema1 < ema2 and ema2 < ema3 and ema3 < ema4

bgcolor(Bullish ? color.new(#2962FF, 90) : Bearish ? color.new(#ef5350, 90) : na)
```

**Signal logic:**
- **Long entry** → all 4 EMAs stacked bullishly (8 > 13 > 21 > 34)
- **Short/flat** → all 4 EMAs stacked bearishly (8 < 13 < 21 < 34)
- **No trade** → mixed/flat ribbon (EMAs intertwined)

**Execution in replay:**
Claude checks `replay_status` to confirm no open position, then fires `replay_trade(action:"buy")` when the ribbon is bullish. Steps bars with `replay_step` to observe price action.

---

## Architecture — How It Works

```
Claude Code CLI (terminal)
        │
        │  JSON-RPC over stdio/SSE
        ▼
TradingView MCP Server ("tradesdontlie" project)
        │
        │  Chrome DevTools Protocol (CDP)
        │  connects to TradingView Desktop app
        ▼
TradingView Desktop (Chromium-based)
        │
        ├── Chart manipulation  (symbol, timeframe, chart type, scroll)
        ├── Pine Script editor  (inject source, compile, add to chart)
        ├── Screenshot capture  (full region or cropped)
        ├── Replay mode         (start, step, place paper trades)
        ├── Multi-pane layout   (set each pane's symbol)
        └── Watchlist           (add symbols — partially working)
```

---

## Build Plan

### Goal
Build a working **TradingView MCP server** that lets Claude Code control TradingView Desktop from the terminal — matching the capabilities demonstrated in the video, plus a structured EMA-ribbon scanner with PDF report output.

---

### Phase 0 — Repo & Toolchain Setup

- [ ] Init Node.js (or Python) project with TypeScript
- [ ] Add MCP SDK (`@modelcontextprotocol/sdk`)
- [ ] Add `puppeteer-core` + CDP client (`chrome-remote-interface` or direct WS)
- [ ] Configure Claude Code's `.claude/settings.json` with `bypassPermissions: true` for MCP tools
- [ ] Write `CLAUDE.md` documenting every MCP tool for Claude's context

---

### Phase 1 — CDP Bridge to TradingView

**Files:** `src/cdp/client.ts`, `src/cdp/tradingview.ts`

- [ ] Launch TradingView Desktop with remote debugging port: `--remote-debugging-port=9222`
- [ ] Connect CDP, enumerate targets, attach to TradingView page target
- [ ] Implement `tv_health_check()` — verify connection, return version/status
- [ ] Abstract `executeScript(js: string)` for injecting arbitrary JS into the TV page

---

### Phase 2 — Core Chart Controls

**File:** `src/tools/chart.ts`

| Tool | Parameters | Implementation |
|------|-----------|----------------|
| `chart_set_symbol` | `symbol: string` | TV keyboard shortcut or search bar injection |
| `chart_set_timeframe` | `timeframe: string` | Click timeframe button in toolbar |
| `chart_set_type` | `chart_type: string` | Chart type dropdown |
| `chart_scroll_to_date` | `date: string` | TV's `chart.setVisibleRange()` via injected JS |
| `pane_set_symbol` | `index: number, symbol: string` | Multi-pane symbol change |
| `quote_get` | `symbol?: string` | Read price from TV data layer |

---

### Phase 3 — Screenshot & Visual Feedback Loop

**File:** `src/tools/screenshot.ts`

- [ ] `capture_screenshot(region, filename)` — CDP `Page.captureScreenshot`, save PNG to `./screenshots/`
- [ ] Return base64 or file path back to Claude so it can `Read` the image
- [ ] `batch_run(symbols[], action, delay_ms)` — loop: set symbol → action (screenshot) → delay

This is the core feedback mechanism: Claude writes Pine Script, compiles it, screenshots the result, reads the image, and decides next steps.

---

### Phase 4 — Pine Script Automation

**File:** `src/tools/pine.ts`

- [ ] `ui_open_panel(panel, action)` — open Pine Script editor via TV keyboard shortcut (`Alt+P` or menu)
- [ ] `pine_set_source(code)` — select-all in editor, paste source via CDP `Input.dispatchKeyEvent`
- [ ] `pine_smart_compile()` — click "Add to chart" button, poll for compile result, return error/success
- [ ] Cache last compiled source to detect no-op re-compiles

**The EMA Ribbon template** (Phase 4 deliverable): Claude generates custom Pine code at runtime based on user's strategy description.

---

### Phase 5 — Replay Mode (Paper Trading)

**File:** `src/tools/replay.ts`

- [ ] `replay_start(date)` — enter TradingView Replay mode, jump to date
- [ ] `replay_status()` — read current bar timestamp, open position P&L
- [ ] `replay_step(bars?)` — advance N bars (default 1)
- [ ] `replay_trade(action: "buy"|"sell"|"close")` — click the Buy/Sell button in replay panel
- [ ] `replay_stop()` — exit replay, return to live

---

### Phase 6 — Market Scanner Agent Loop

**File:** `src/agent/scanner.ts`

Claude-driven loop:
1. For each symbol in watchlist → `chart_set_symbol`, `capture_screenshot`
2. Claude reads each screenshot
3. Claude labels each as: `BULLISH | BEARISH | NEUTRAL` based on ribbon state
4. Aggregates results into a scan report
5. Generates PDF summary (use `pdfkit` or markdown → PDF)

---

### Phase 7 — Watchlist Management

**File:** `src/tools/watchlist.ts`

- [ ] `watchlist_add(symbol)` — find "Add symbol" button in watchlist panel (note: this failed in the video; needs DOM inspection to fix)
- [ ] `watchlist_list()` — read current watchlist symbols from TV page state

---

### Phase 8 — Claude Code Integration

**File:** `src/server.ts` (MCP entry point)

- [ ] Expose all tools via MCP SDK `server.tool(name, schema, handler)`
- [ ] Add `resources` for screenshot files so Claude can read them inline
- [ ] Write `.claude/settings.json` with MCP server registration and `bypassPermissions`
- [ ] Write `CLAUDE.md` with full tool reference + example prompts

---

### Milestone Summary

| Phase | Deliverable | Est. Effort |
|-------|------------|-------------|
| 0 | Repo + toolchain | 2h |
| 1 | CDP bridge + health check | 4h |
| 2 | Chart controls (6 tools) | 6h |
| 3 | Screenshot + batch_run | 4h |
| 4 | Pine Script automation | 6h |
| 5 | Replay paper trading | 6h |
| 6 | Scanner agent loop + PDF | 8h |
| 7 | Watchlist (DOM fix) | 3h |
| 8 | MCP server wiring | 4h |
| **Total** | | **~43h** |

---

### Tech Stack

| Layer | Choice | Reason |
|-------|--------|--------|
| Language | TypeScript (Node 20) | MCP SDK is TS-native; CDP libs are mature |
| MCP SDK | `@modelcontextprotocol/sdk` | Official SDK |
| CDP client | `puppeteer-core` | Battle-tested, handles WS reconnect |
| PDF | `pdfkit` | Lightweight, no headless browser needed |
| Testing | `vitest` + recorded CDP fixtures | Fast, no TV required for unit tests |

---

### Key Risks

1. **TradingView UI changes** — CDP selectors break when TV updates. Mitigation: use semantic JS access to TV's internal `chart` object rather than DOM clicking wherever possible.
2. **Replay mode fragility** — Buy/Sell buttons are only present during replay. Need guard to detect mode before calling replay tools.
3. **Rate limiting** — TV may throttle rapid symbol switches. The `delay_ms` param in `batch_run` is the safety valve.
4. **Pine compile errors** — Claude must handle compile error feedback and retry with corrected code.

---

### First Task to Start

```
Phase 1 — src/cdp/client.ts

1. `npm init -y && npm i @modelcontextprotocol/sdk puppeteer-core typescript tsx`
2. Launch TV Desktop: add `--remote-debugging-port=9222` to shortcut
3. Connect: `puppeteer.connect({ browserURL: "http://localhost:9222" })`
4. Find TradingView page target by URL pattern
5. Implement tv_health_check → return { connected: true, url, title }
6. Test from Claude Code: claude --mcp tradingview-mcp "run tv_health_check"
```
