# Replay Backtest Protocol
# Use this to validate the Ribbon Pro strategy before trading live

---

You are running a structured replay backtest on {{SYMBOL}} on the 5-minute chart.

## Setup
1. Set symbol to {{SYMBOL}} (default: CME_MINI:NQ1!)
2. Set timeframe to 5 minutes
3. Make sure "Momentum Ribbon Pro" indicator is on the chart
4. Run `replay_start` at date: {{START_DATE}} (suggest: 3 months ago)

## Backtest Loop

Repeat until you reach today's date or 50 trades, whichever comes first:

For each bar:
1. `replay_step` — advance one bar
2. Check if a ribbon flip just occurred:
   - If YES: check ADX ≥ 22 and volume ≥ 1.4× average
   - If BOTH pass: record as a VALID SIGNAL
   - If either fails: record as a FILTERED SIGNAL (skipped)
3. If a valid signal was taken:
   - Track price from entry
   - Check if stop (1.5 ATR) or target (3×R) is hit first
   - Record result: WIN or LOSS
4. `replay_step` forward until the trade closes or reverses
5. Continue scanning for next signal

## Log Each Trade

Record in this format:
```
Trade #N
Date: [date]
Symbol: [symbol]
Direction: [LONG/SHORT]
Entry: [price]
Stop: [price] (1.5 ATR = [value])
Target: [price] (3R = [value])
Outcome: [WIN/LOSS/OPEN]
R earned: [+3.0 / -1.0]
ADX at entry: [value]
Volume ratio: [x.x× avg]
Notes: [anything notable about price action]
```

## Final Report

After 50 trades (or date reached), output:
```
BACKTEST RESULTS — {{SYMBOL}} 5m — {{START_DATE}} to {{END_DATE}}

Total signals fired:    [N]
Filtered (rules):       [N] ([%] of raw signals removed)
Trades taken:           [N]
Win rate:               [%]
Average winner:         +[R]R
Average loser:          -[R]R
Expectancy per trade:   [R]R
Max consecutive losses: [N]
Max drawdown:           [%]
Sharpe (approx):        [N]

VERDICT: [TRADE IT / NEEDS WORK / ABANDON]
Reason: [one sentence]
```

---
**This is paper trading only. No real orders.**
