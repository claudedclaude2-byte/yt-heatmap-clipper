# Skill: Pine Deploy

Deploy a Pine Script indicator to TradingView from the repo.

## Usage

```
/pine-deploy momentum_ribbon_pro
```

## Steps

1. `tv_health_check` — abort if disconnected.
2. Read `pine/[name].pine` — confirm file exists.
3. Backup current chart state:
   - `capture_screenshot(filename: "pre-deploy-backup")` → save to `backups/`
4. Open Pine editor:
   ```
   ui_open_panel(panel: "pine-editor", action: "open")
   ```
5. Inject source:
   ```
   pine_set_source(code: [contents of pine/[name].pine])
   ```
6. Compile:
   ```
   pine_smart_compile()
   ```
7. If compile errors → show full error, do NOT auto-fix without user confirmation.
8. If success → `capture_screenshot(filename: "post-deploy-[name]")` — confirm indicator is on chart.
9. Report: compile status, any warnings, screenshot path.

## Before Changing Any Pine Script

Always backup first:
```bash
cp pine/momentum_ribbon_pro.pine backups/$(date +%Y-%m-%d_%H-%M)_momentum_ribbon_pro.pine
```
