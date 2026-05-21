# Skill: Signal Check

Run when a TradingView alert fires. Pass symbol, direction, and price.

## Usage

```
/signal-check NQ1! LONG 21450
```

## Steps

1. `tv_health_check` — verify connected.
2. Load `rules/entry_rules.json` — check all 5 gates:
   - **Gate 1 — EMA flip**: did the ribbon flip THIS bar or in the last 2 bars?
   - **Gate 2 — ADX**: is ADX ≥ 22? Read from info table in screenshot.
   - **Gate 3 — Volume**: is volume ≥ 1.4× 20-bar average?
   - **Gate 4 — Session**: is time between 09:30–15:45 EST?
   - **Gate 5 — HTF**: does 1H ribbon agree with 5m direction?
3. `chart_set_symbol(SYMBOL)` → `chart_set_timeframe("5")` → `capture_screenshot`
4. Read screenshot — verify gates visually.
5. `chart_set_timeframe("60")` → `capture_screenshot` — verify 1H alignment.
6. If all 5 gates pass → output **APPROVED** with:
   - Entry price
   - Stop: below last swing low (long) or above last swing high (short)
   - Target: next structural level (NOT SL × 1.389)
   - R:R ratio — must be ≥ 1.5
7. If any gate fails → output **REJECTED** with which gate failed.
8. Save screenshot to `signals/YYYY-MM-DD_HH-MM_SYMBOL_DIRECTION.png`.

## Model

Use **Sonnet 4.6**.
