# Subagent Patterns for Thunder Trader

Subagents let you parallelize work — spin one off and keep coding.
Most people never use this. It's the move.

## Pattern 1 — Background Batch Scan

While you fix a Pine Script bug or review logs:
```
"Spin off a subagent to run the batch scan across NQ, ES, GC, CL, and BTC.
Use the /batch-scan skill. Report results when done — I'll keep working."
```

## Pattern 2 — Parallel Instrument Analysis

Four subagents, four instruments at once:
```
"Spawn 4 subagents in parallel:
- Agent 1: screenshot and classify NQ1! 5m ribbon
- Agent 2: screenshot and classify ES1! 5m ribbon
- Agent 3: screenshot and classify GC1! 5m ribbon
- Agent 4: screenshot and classify CL1! 5m ribbon
Each should run tv_health_check first. Report ribbon state for each."
```

## Pattern 3 — Test Suite While Coding

```
"Spin off a subagent to run the replay backtest on March 2026 data
while I work on the Kronos bug fix. Use /backtest NQ1! 2026-03-01 2026-03-31."
```

## Pattern 4 — Log Analysis + Code Fix in Parallel

```
"Two subagents:
- Agent A: analyze the Thunder Trader log I pasted — count missed trades,
  identify which bug caused each miss, output a tally by bug number.
- Agent B: read kronos_predict() and look for any abs() call or sign
  negation on the model output — report line numbers.
I'll work on the R:R fix."
```

## Pattern 5 — Morning Scan + Crypto Scan

```
"Run two subagents:
- Agent 1: /morning-scan (futures — NQ, ES, GC, CL)
- Agent 2: check BTC and ETH daily ribbon on Bitstamp,
  report if either is in a full-stack bullish or bearish state.
Both in parallel."
```

## When NOT to Use Subagents

- Tasks that need each other's output (do those sequentially)
- Simple one-step operations (just run them directly)
- When you need to read a screenshot before deciding next action

## Model for Subagents

- Batch/scan subagents → **Haiku 4.5**
- Analysis subagents → **Sonnet 4.6**
- Architectural subagents → **Opus 4.7**
