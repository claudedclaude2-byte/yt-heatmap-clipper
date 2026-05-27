# Skill: Batch Scan

Quick market pulse across all instruments. Run anytime.

## Usage

```
/batch-scan
```

Optional: `/batch-scan crypto` (BTC, ETH only) or `/batch-scan futures` (NQ, ES, GC, CL)

## Steps

1. `tv_health_check`.
2. Run `batch_run` across target symbols with `delay_ms: 2500`:
   ```
   batch_run(
     symbols: ["CME_MINI:NQ1!", "CME_MINI:ES1!", "COMEX:GC1!", "NYMEX:CL1!", "BITSTAMP:BTCUSD"],
     action: "screenshot",
     delay_ms: 2500
   )
   ```
3. Read each screenshot — classify ribbon state:
   - BULLISH (all 4 EMAs stacked long)
   - BEARISH (all 4 EMAs stacked short)
   - NEUTRAL (mixed/choppy)
   - WATCH (just flipped — may trigger soon)
4. Output a table:
   | Symbol | Ribbon | ADX | Volume | Signal |
   |--------|--------|-----|--------|--------|
5. Highlight any WATCH setups — these become alerts.
6. Save report to `signals/YYYY-MM-DD_HH-MM_batch-scan.md`.

## Model

Use **Haiku 4.5** for bulk screenshot analysis — fast and cheap.
Switch to Sonnet only if a WATCH setup needs deeper signal evaluation.

## Subagent Pattern

For a fast scan while you work on something else:
```
"Spin off a subagent to run /batch-scan and report back — I'll keep working on the Pine Script fix."
```
