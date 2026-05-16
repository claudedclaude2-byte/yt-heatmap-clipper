# On-Demand Multi-Instrument Batch Scan
# Run anytime during market hours for a quick market pulse

---

You are scanning multiple markets for ribbon alignment with quality filters.

## Instructions

Run `batch_run` across all instruments in `rules/entry_rules.json`:
```
symbols: ["CME_MINI:NQ1!", "CME_MINI:ES1!", "COMEX:GC1!", "NYMEX:CL1!", "BINANCE:BTCUSDT", "BINANCE:ETHUSDT"]
action: "screenshot"
delay_ms: 2500
timeframe: "5"
```

For each screenshot you read back, extract:
- Ribbon state: BULL / BEAR / NEUTRAL
- Approximate ADX (high / medium / low based on ribbon spread width)
- Is price near the ribbon (potential entry) or far from it (overextended)?
- Momentum: accelerating or stalling?

Then run a second `batch_run` on the same symbols but at **60-minute** timeframe for HTF context.

## Output Format

Print a rapid scan table:

| Symbol     | 5m State | 5m Momentum | 1H State | HTF Match? | Setup Quality |
|------------|----------|-------------|----------|------------|---------------|
| NQ1!       | BEAR     | Strong      | BEAR     | ✓ YES      | A-grade       |
| ES1!       | BEAR     | Stalling    | BULL     | ✗ NO       | Skip          |
| GC1!       | BULL     | Building    | BULL     | ✓ YES      | B-grade       |
| CL1!       | NEUTRAL  | —           | BEAR     | —          | Skip          |
| BTCUSDT    | BEAR     | Strong      | BEAR     | ✓ YES      | A-grade       |
| ETHUSDT    | NEUTRAL  | —           | BEAR     | —          | Watch         |

## Grading
- **A-grade**: Both TFs aligned + momentum strong + price near ribbon = watch for signal bar
- **B-grade**: Both TFs aligned + momentum building = on watchlist
- **Skip**: TFs disagree OR neutral → ignore completely
- **Watch**: One TF has setup forming, other unclear → monitor but don't trade yet

Do not place trades. Flag A-grade setups for `prompts/02-signal-check.md` verification.
