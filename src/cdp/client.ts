import puppeteer, { type Browser, type Page } from 'puppeteer-core';

const TV_DEBUG_URL = 'http://localhost:9222';
const TV_URL_PATTERN = /tradingview\.com/i;

export interface HealthCheckResult {
  connected: boolean;
  url: string;
  title: string;
  version?: string;
  error?: string;
}

let _browser: Browser | null = null;
let _page: Page | null = null;

export async function connect(): Promise<{ browser: Browser; page: Page }> {
  if (_browser && _page) {
    try {
      await _page.evaluate(() => true); // ping — throws if connection dropped
      return { browser: _browser, page: _page };
    } catch {
      _browser = null;
      _page = null;
    }
  }

  const browser = await puppeteer.connect({
    browserURL: TV_DEBUG_URL,
    defaultViewport: null,
  });

  const pages = await browser.pages();
  const tvPage = pages.find(p => TV_URL_PATTERN.test(p.url()));

  if (!tvPage) {
    await browser.disconnect();
    throw new Error(
      'No TradingView page found. ' +
      'Launch TradingView Desktop with --remote-debugging-port=9222'
    );
  }

  _browser = browser;
  _page = tvPage;

  browser.on('disconnected', () => {
    _browser = null;
    _page = null;
  });

  return { browser, page: tvPage };
}

export async function getPage(): Promise<Page> {
  const { page } = await connect();
  return page;
}

export async function executeScript<T>(js: string): Promise<T> {
  const page = await getPage();
  return page.evaluate(js) as Promise<T>;
}

export async function healthCheck(): Promise<HealthCheckResult> {
  try {
    const { page } = await connect();
    const url = page.url();
    const title = await page.title();
    const version = await page
      .evaluate(() => {
        const meta = document.querySelector('meta[name="version"]');
        return meta?.getAttribute('content') ?? undefined;
      })
      .catch(() => undefined);
    return { connected: true, url, title, version };
  } catch (err) {
    return {
      connected: false,
      url: '',
      title: '',
      error: err instanceof Error ? err.message : String(err),
    };
  }
}

// Run as script: `npm run health` or `tsx src/cdp/client.ts`
if (process.argv[1]?.endsWith('client.ts') || process.argv[1]?.endsWith('client.js')) {
  healthCheck().then(result => {
    console.log(JSON.stringify(result, null, 2));
    process.exit(result.connected ? 0 : 1);
  });
}
