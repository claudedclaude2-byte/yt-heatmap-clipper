import { mkdir } from 'node:fs/promises';
import { executeScript, getPage } from './client.js';

const SCREENSHOT_DIR = 'screenshots';

export async function setSymbol(symbol: string): Promise<void> {
  const page = await getPage();
  await page.keyboard.down('Control');
  await page.keyboard.press('KeyK');
  await page.keyboard.up('Control');
  await delay(300);
  await page.keyboard.type(symbol, { delay: 40 });
  await delay(500);
  await page.keyboard.press('Enter');
  await delay(800);
}

export async function setTimeframe(timeframe: string): Promise<void> {
  const page = await getPage();
  await page.keyboard.press('Escape');
  await delay(100);
  const btn = await page.$('[data-name="time-interval-button"]');
  if (!btn) throw new Error('Timeframe button not found in TradingView toolbar');
  await btn.click();
  await delay(200);
  await page.keyboard.type(timeframe);
  await page.keyboard.press('Enter');
  await delay(500);
}

export async function setChartType(chartType: 'Candles' | 'Heikin-Ashi' | 'Bars' | 'Line'): Promise<void> {
  await executeScript(`
    (() => {
      const chart = window.tvWidget?.activeChart?.();
      const typeMap = { Candles: 1, Bars: 0, 'Heikin-Ashi': 8, Line: 2 };
      chart?.setChartType(typeMap['${chartType}'] ?? 1);
    })()
  `);
  await delay(400);
}

export async function scrollToDate(date: string): Promise<void> {
  await executeScript(`
    (() => {
      const chart = window.tvWidget?.activeChart?.();
      if (!chart) throw new Error('TV chart API not accessible');
      const ts = new Date('${date}').getTime() / 1000;
      chart.setVisibleRange({ from: ts - 86400 * 30, to: ts + 86400 * 5 });
    })()
  `);
  await delay(600);
}

export async function setPaneSymbol(paneIndex: number, symbol: string): Promise<void> {
  await executeScript(`
    (() => {
      const chart = window.tvWidget?.activeChart?.();
      const pane = chart?.getPanes()?.[${paneIndex}];
      const series = pane?.getMainSourceId?.();
      if (series) chart?.setSymbol('${symbol}');
    })()
  `);
  await delay(600);
}

export async function getQuote(symbol?: string): Promise<{ price: number; symbol: string }> {
  if (symbol) await setSymbol(symbol);
  return executeScript<{ price: number; symbol: string }>(`
    (() => {
      const priceEl = document.querySelector(
        '[data-name="legend-series-item"] [class*="price"], .js-symbol-last'
      );
      const price = parseFloat(priceEl?.textContent?.replace(/,/g, '') ?? '0');
      const symEl = document.querySelector('[data-name="legend-series-item"] [class*="title"]');
      return { price, symbol: symEl?.textContent?.trim() ?? '' };
    })()
  `);
}

export async function openPineEditor(): Promise<void> {
  const page = await getPage();
  await page.keyboard.down('Alt');
  await page.keyboard.press('KeyP');
  await page.keyboard.up('Alt');
  await delay(900);
}

export async function setPineSource(code: string): Promise<void> {
  const page = await getPage();
  const editor = await page.$('.cm-content, .pine-editor-wrapper textarea');
  if (!editor) throw new Error('Pine editor not found — call openPineEditor() first');
  await editor.click();
  await page.keyboard.down('Control');
  await page.keyboard.press('KeyA');
  await page.keyboard.up('Control');
  // Type in chunks to avoid losing keystrokes on large scripts
  const chunkSize = 500;
  for (let i = 0; i < code.length; i += chunkSize) {
    await page.keyboard.type(code.slice(i, i + chunkSize));
  }
}

export interface CompileResult {
  success: boolean;
  error?: string;
}

export async function compileAndAdd(): Promise<CompileResult> {
  const page = await getPage();
  const addBtn = await page.$(
    '[data-name="add-button"], button[aria-label="Add to chart"], .tv-pine-editor__add-button'
  );
  if (!addBtn) throw new Error('Pine compile button not found — is the editor open?');
  await addBtn.click();
  await delay(1500);

  const errEl = await page.$('.pine-editor-error, [data-name="compile-errors"]');
  if (errEl) {
    const errorText = await errEl.evaluate(el => el.textContent ?? '');
    return { success: false, error: errorText.trim() };
  }
  return { success: true };
}

export async function captureScreenshot(filename: string): Promise<string> {
  await mkdir(SCREENSHOT_DIR, { recursive: true });
  const page = await getPage();
  const path = `${SCREENSHOT_DIR}/${filename}-${Date.now()}.png`;
  await page.screenshot({ path, fullPage: false });
  return path;
}

export async function batchRun(
  symbols: string[],
  action: 'screenshot',
  delayMs = 2500
): Promise<Record<string, string>> {
  const results: Record<string, string> = {};
  for (const sym of symbols) {
    await setSymbol(sym);
    await delay(delayMs);
    if (action === 'screenshot') {
      results[sym] = await captureScreenshot(sym.replace(/[^a-zA-Z0-9]/g, '_'));
    }
  }
  return results;
}

export interface ReplayStatus {
  timestamp: string;
  hasOpenPosition: boolean;
}

export async function replayStart(date: string): Promise<void> {
  await executeScript(`
    (() => {
      const chart = window.tvWidget?.activeChart?.();
      chart?.startReplayMode?.();
    })()
  `);
  await delay(800);
  await scrollToDate(date);
}

export async function replayStatus(): Promise<ReplayStatus> {
  return executeScript<ReplayStatus>(`
    (() => {
      const bar = document.querySelector('[data-name="replay-bar"] .timestamp');
      const pos = document.querySelector('[data-name="replay-position"]');
      return {
        timestamp: bar?.textContent?.trim() ?? '',
        hasOpenPosition: !!pos,
      };
    })()
  `);
}

export async function replayStep(bars = 1): Promise<void> {
  const page = await getPage();
  for (let i = 0; i < bars; i++) {
    await page.keyboard.press('ArrowRight');
    await delay(200);
  }
}

export async function replayTrade(action: 'buy' | 'sell' | 'close'): Promise<void> {
  const page = await getPage();
  const selector = action === 'buy'
    ? '[data-name="replay-buy-button"], button[aria-label="Buy"]'
    : action === 'sell'
    ? '[data-name="replay-sell-button"], button[aria-label="Sell"]'
    : '[data-name="replay-close-button"], button[aria-label="Close position"]';
  const btn = await page.$(selector);
  if (!btn) throw new Error(`Replay ${action} button not found — is replay mode active?`);
  await btn.click();
  await delay(400);
}

export async function replayStop(): Promise<void> {
  await executeScript(`
    (() => { window.tvWidget?.activeChart?.()?.stopReplayMode?.(); })()
  `);
  await delay(500);
}

function delay(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}
