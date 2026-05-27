# Skill: Replay Backtest

Validate the strategy in TradingView Replay mode before live trading.
See full protocol in `scripts/replay_backtest.md`.

## Usage

```
/backtest NQ1! 2026-03-01 2026-03-31
```

## Steps

1. `tv_health_check`.
2. Set symbol and timeframe:
   ```
   chart_set_symbol("CME_MINI:NQ1!")
   chart_set_timeframe("5")
   ```
3. Deploy ribbon indicator via `/pine-deploy momentum_ribbon_pro`.
4. Enter replay:
   ```
   replay_start(date: "[start-date]")
   ```
5. For each bar:
   - `replay_status()` — read open position and current ribbon state
   - `capture_screenshot()` — save for review
   - If ribbon flips and all 5 gates pass → `replay_trade(action: "buy"|"sell")`
   - If in position and ribbon reverses → `replay_trade(action: "close")`
   - `replay_step(1)`
6. After end date:
   - Count: total trades, wins, losses, avg R, max drawdown
   - **Pass criteria**: expectancy > 0.3R over ≥ 50 trades
   - If expectancy < 0.3R → do NOT use on live account
7. Save results to `signals/YYYY-MM-DD_backtest-[symbol]-[start]-[end].md`.

## Model

Use **Sonnet 4.6** for stepping through bars.
Use **Opus 4.7** only if diagnosing why a specific trade setup failed.
