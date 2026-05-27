import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { z } from 'zod';
import { healthCheck } from './cdp/client.js';
import {
  setSymbol,
  setTimeframe,
  setChartType,
  scrollToDate,
  getQuote,
  openPineEditor,
  setPineSource,
  compileAndAdd,
  captureScreenshot,
  batchRun,
  replayStart,
  replayStatus,
  replayStep,
  replayTrade,
  replayStop,
} from './cdp/tradingview.js';

const server = new McpServer({
  name: 'thunder-trader',
  version: '0.1.0',
});

server.tool('tv_health_check', 'Verify CDP connection to TradingView Desktop. Run this first.', {}, async () => {
  const result = await healthCheck();
  return { content: [{ type: 'text', text: JSON.stringify(result, null, 2) }] };
});

server.tool('chart_set_symbol', 'Switch the active chart to a symbol', {
  symbol: z.string().describe('e.g. CME_MINI:NQ1! or BTCUSD'),
}, async ({ symbol }) => {
  await setSymbol(symbol);
  return { content: [{ type: 'text', text: `Symbol set to ${symbol}` }] };
});

server.tool('chart_set_timeframe', 'Change chart timeframe', {
  timeframe: z.string().describe('1, 5, 15, 60, D, W'),
}, async ({ timeframe }) => {
  await setTimeframe(timeframe);
  return { content: [{ type: 'text', text: `Timeframe set to ${timeframe}` }] };
});

server.tool('chart_set_type', 'Change chart type', {
  chart_type: z.enum(['Candles', 'Heikin-Ashi', 'Bars', 'Line']),
}, async ({ chart_type }) => {
  await setChartType(chart_type);
  return { content: [{ type: 'text', text: `Chart type set to ${chart_type}` }] };
});

server.tool('chart_scroll_to_date', 'Scroll chart to a specific date', {
  date: z.string().describe('YYYY-MM-DD'),
}, async ({ date }) => {
  await scrollToDate(date);
  return { content: [{ type: 'text', text: `Scrolled to ${date}` }] };
});

server.tool('quote_get', 'Read current price from TradingView', {
  symbol: z.string().optional().describe('Switch to symbol before reading (optional)'),
}, async ({ symbol }) => {
  const quote = await getQuote(symbol);
  return { content: [{ type: 'text', text: JSON.stringify(quote) }] };
});

server.tool('ui_open_panel', 'Open a TradingView panel', {
  panel: z.enum(['pine-editor']),
  action: z.enum(['open']),
}, async () => {
  await openPineEditor();
  return { content: [{ type: 'text', text: 'Pine editor opened' }] };
});

server.tool('pine_set_source', 'Inject Pine Script source into the editor', {
  code: z.string().describe('Full Pine Script v5 source'),
}, async ({ code }) => {
  await setPineSource(code);
  return { content: [{ type: 'text', text: `Source injected (${code.length} chars)` }] };
});

server.tool('pine_smart_compile', 'Compile Pine Script and add to chart', {}, async () => {
  const result = await compileAndAdd();
  return { content: [{ type: 'text', text: JSON.stringify(result) }] };
});

server.tool('capture_screenshot', 'Take a screenshot of TradingView', {
  filename: z.string().describe('Base filename (no extension)'),
}, async ({ filename }) => {
  const path = await captureScreenshot(filename);
  return { content: [{ type: 'text', text: `Screenshot saved: ${path}` }] };
});

server.tool('batch_run', 'Loop through symbols: set symbol → action → delay', {
  symbols: z.array(z.string()),
  action: z.enum(['screenshot']),
  delay_ms: z.number().default(2500),
}, async ({ symbols, action, delay_ms }) => {
  const results = await batchRun(symbols, action, delay_ms);
  return { content: [{ type: 'text', text: JSON.stringify(results, null, 2) }] };
});

server.tool('replay_start', 'Enter TradingView Replay mode at a date', {
  date: z.string().describe('YYYY-MM-DD'),
}, async ({ date }) => {
  await replayStart(date);
  return { content: [{ type: 'text', text: `Replay started at ${date}` }] };
});

server.tool('replay_status', 'Get current replay bar timestamp and open position', {}, async () => {
  const status = await replayStatus();
  return { content: [{ type: 'text', text: JSON.stringify(status) }] };
});

server.tool('replay_step', 'Advance N bars in replay mode', {
  bars: z.number().default(1),
}, async ({ bars }) => {
  await replayStep(bars);
  return { content: [{ type: 'text', text: `Advanced ${bars} bar(s)` }] };
});

server.tool('replay_trade', 'Place a paper trade in replay mode', {
  action: z.enum(['buy', 'sell', 'close']),
}, async ({ action }) => {
  await replayTrade(action);
  return { content: [{ type: 'text', text: `Replay trade: ${action}` }] };
});

server.tool('replay_stop', 'Exit replay mode and return to live', {}, async () => {
  await replayStop();
  return { content: [{ type: 'text', text: 'Replay stopped' }] };
});

const transport = new StdioServerTransport();
await server.connect(transport);
