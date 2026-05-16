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
