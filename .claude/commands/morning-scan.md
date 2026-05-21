# Skill: Morning Scan

Run this at 09:25 EST before the market opens.

## Steps

1. Run `tv_health_check` — abort if connection fails.
2. Read `rules/entry_rules.json` — confirm all 5 gates in memory.
3. Check macro calendar: is today FOMC, NFP, or CPI? If yes → mark NO TRADE and stop.
4. For each instrument (NQ1!, ES1!, GC1!, CL1!, BTCUSD):
   - `chart_set_symbol` → `chart_set_timeframe("D")` → `capture_screenshot`
   - Label: BULLISH / BEARISH / NEUTRAL based on daily ribbon
5. Switch to 1H for NQ1! and ES1! — confirm HTF ribbon direction.
6. Switch to 5m for NQ1! — note any pre-market ribbon state.
7. Generate morning brief:
   - Market bias (bull / bear / mixed)
   - Top 2 setups to watch with entry trigger
   - Key levels (yesterday HOD/LOD, overnight range)
   - Session notes
8. Save brief to `signals/YYYY-MM-DD_morning-brief.md`.

## Model

Use **Sonnet 4.6** — fast enough for this workflow.

## Example Invocation

```
/morning-scan
```

Or: "Run the morning scan for today."
