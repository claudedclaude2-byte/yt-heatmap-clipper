# Thunder Trader — Claude Code Instructions

This project uses the `tradesdontlie/tradingview-mcp` MCP server to control
TradingView Desktop via Chrome DevTools Protocol.

## MCP Server Setup

Make sure TradingView Desktop is running with:
```
--remote-debugging-port=9222
```

Verify connection always by running `tv_health_check` first.

## Project Structure

```
pine/
  momentum_ribbon_pro.pine   ← The main indicator (load this on every chart)
rules/
  entry_rules.json           ← Entry rules — READ THIS before every decision
prompts/
  01-morning-scan.md         ← Run at 09:25 EST daily
  02-signal-check.md         ← Run when TradingView alert fires
  03-batch-scan.md           ← Run anytime for quick market pulse
scripts/
  replay_backtest.md         ← Validate strategy before live trading
backups/                     ← Timestamped snapshots before any changes
```

## Rules You Must Follow (non-negotiable)

1. **Always read `rules/entry_rules.json` before making any trading decision.**
2. **Never place a real trade during morning scan or batch scan — analysis only.**
3. **All 5 gates must pass for a signal to be APPROVED:**
   - EMA full stack flip (ribbon flipped THIS bar or last 2 bars)
   - ADX ≥ 22 on the signal timeframe
   - Volume ≥ 1.4× 20-bar average
   - In session (09:30–15:45 EST for futures)
   - 1H ribbon agrees with 5m ribbon direction
4. **Daily hard stop: if 3% drawdown hit, halt all trading for the day.**
5. **Max 3 trades per day.**
6. **Save every signal screenshot to `signals/` folder with timestamp.**

## Indicator: Momentum Ribbon Pro

The Pine Script in `pine/momentum_ribbon_pro.pine` is the upgraded version
of the 4-EMA ribbon from the tradesdontlie video. Key improvements:

- **ADX gate**: only fires when market is trending (ADX ≥ 22)
- **Volume filter**: signal bar must have volume ≥ 1.4× average
- **Session filter**: ignores signals outside RTH (configurable)
- **ATR stop lines**: shows stop placement on chart automatically
- **Entry signals**: triangle shapes only on ribbon FLIP (not every bar)
- **Info table**: live ADX/volume/session status in top-right corner
- **4 alert conditions**: long, short, and two "watch" alerts for low-ADX flips

To load it:
```
tradingview → ui_open_panel(panel: "pine-editor", action: "open")
tradingview → pine_set_source(code: [contents of pine/momentum_ribbon_pro.pine])
tradingview → pine_smart_compile()
```

## EMA Lengths — When to Change

Default 8/13/21/34 works well on 5-min futures (NQ, ES) and daily crypto.
Consider adjusting:
- **Slower markets (Gold, Oil)**: try 13/21/34/55
- **Faster/crypto (BTC 1-min)**: try 5/8/13/21
- **Daily swing trading**: try 10/20/50/100 (standard institutional set)

## Standard Morning Workflow

```
09:25 EST → run prompts/01-morning-scan.md
09:30 EST → market opens, read the brief, watch flagged setups
Alert fires → run prompts/02-signal-check.md with signal details
Signal approved → execute per the approved entry/stop/target
End of day → review trades, note what worked and what didn't
```

## Backup Protocol

Before making ANY code change to the Pine Script or rules:
```bash
cp -r . backups/$(date +%Y-%m-%d_%H-%M)_pre-[description]
git add . && git commit -m "backup: before [description]"
```

To revert to a backup:
```bash
cp backups/2026-05-16_pre-implementation/PLAN.md .
# or restore entire state:
git checkout [commit-hash]
```

## DO NOT

- Run live order execution without completing the replay backtest protocol first
- Change EMA lengths without re-running the backtest with new parameters
- Skip the HTF alignment check (5m alone is not enough)
- Trade during FOMC, NFP, CPI — mark as NO TRADE in the morning scan
- Use this on a live account until 50-trade backtest shows expectancy > 0.3R

---

## Thunder Trader Bot (Local Machine)

Separate Python bot running on user's desktop. Connects to Kraken via WebSocket.
Code lives locally — NOT in this repo. Logs can be pasted here for analysis.

### Architecture
- **7-agent consensus network**: BB, PATTERN, DIVERGENCE, MOMENTUM, TREND, WHALE, KRONOS
- **Kronos ML model**: NeoQuasar/Kronos-small + NeoQuasar/Kronos-Tokenizer-base (HuggingFace)
- **Minimum agents for quorum**: 3 of 7 must respond
- **Position sizing**: Kelly criterion (currently hardcoded floor=0.57)
- **Exchange**: Kraken, pair XBT/USDT, paper trading mode
- **Timeframe**: 15-minute candles

### Known Bugs (diagnosed from logs, 2026-05-16)

**BUG 1 — R:R hardcoded at 1.39, blocks ALL trades** ← fix this first
- TP = SL × 1.389 on every bar (not a structural level)
- Min R:R requirement = 2.0 → no trade can ever execute
- SL calculated from upper Bollinger Band which drifts upward while price falls
- Fix: set TP to next structural support/resistance, OR lower min_rr to 1.5

**BUG 2 — Agent dropout kills quorum**
- DIVERGENCE + WHALE agents silent all session after asyncio crash at 05:40
- Windows `_ProactorBasePipeTransport` / `ConnectionResetError [WinError 10054]`
- `too_few_agents(2<3)` blocked 20 of 32 candles
- Fix: coroutine health monitor, auto-restart dead agents

**BUG 3 — Kronos bullish bias on bearish day**
- Predicted positive returns on 30/32 candles during -1.8% BTC session
- Likely sign error or abs() call in prediction pipeline
- Fix: audit kronos_predict() for negation or abs() on output

**BUG 4 — score=-0.991 is a sentinel value**
- Appears exactly 11 times — hardcoded fallback when <3 agents respond
- Not a real consensus calculation, corrupts analytics

**BUG 5 — vol=0.0 data feed dropout**
- Seen at 09:45 candle — no guard clause

**BUG 6 — Kelly floor hardcoded at 0.57**
- Same value every bar regardless of market conditions

### Missed Trades (2026-05-16)
- 06:45 SHORT (BB+PATTERN+MOMENTUM, score -2.226) — price dropped $1,204 after
- 08:30, 08:45, 09:00 — three consecutive SHORTs blocked by R:R bug
- 12:15 — volume 10× normal, price +$300 recovery after

### To Fix — Share These Code Sections
Paste these directly into chat for Claude to fix:
1. The TP calculation function (the one producing 1.389× ratio)
2. The agent runner / asyncio task setup
3. `kronos_predict()` or wherever the model output is processed
4. The quorum / consensus scoring function
