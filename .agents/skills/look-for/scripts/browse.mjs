#!/usr/bin/env node
// browse.mjs — opens one URL in headless Chrome/Edge and prints what a person would see as JSON:
// title, final URL, visible text, links, JSON-LD blocks, and a `status`: ok | login-prompt | empty | blocked.
// It never tries to get past a login wall, captcha or bot filter: it reports them so the caller can ask the human.
//
// Usage: node browse.mjs <url> [--out file.json] [--wait 2500] [--scroll 4] [--profile dir] [--headed] [--browser path]
//   --wait     ms to let the page settle after load (default 2500)
//   --scroll   times to scroll to the bottom so lazy-loaded listings render (default 3)
//   --profile  persistent browser profile dir; sessions the human logged into survive between runs
//   --headed   visible window, for the human to log in or solve a captcha by hand; add --hold 90 to keep it open
// No dependencies: Node 22+ (global WebSocket) and Chrome or Edge installed. Exit 0 = page read (ok or login-prompt), 1 = empty or blocked, 2 = bad usage or no browser.

import { spawn, spawnSync } from 'node:child_process';
import { existsSync, readFileSync, writeFileSync, mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

const args = process.argv.slice(2);
const flag = (name) => { const i = args.indexOf(name); if (i < 0) return false; args.splice(i, 1); return true; };
const opt = (name, def) => { const i = args.indexOf(name); return i >= 0 ? args.splice(i, 2)[1] : def; };
const headed = flag('--headed');
const out = opt('--out', null);
const wait = Number(opt('--wait', 2500));
const scrolls = Number(opt('--scroll', 3));
const hold = Number(opt('--hold', 0));
const profileArg = opt('--profile', null);
const browserArg = opt('--browser', process.env.CHROME_PATH ?? null);
const url = args[0];
if (!/^https?:\/\//.test(url ?? '') || ![wait, scrolls, hold].every(Number.isFinite)) {
  console.error('Usage: node browse.mjs <url> [--out file.json] [--wait 2500] [--scroll 3] [--profile dir] [--headed] [--hold sec]');
  process.exit(2);
}

function findBrowser() {
  if (browserArg) return browserArg;
  const env = process.env;
  const c = {
    win32: [`${env.PROGRAMFILES}\\Google\\Chrome\\Application\\chrome.exe`, `${env['PROGRAMFILES(X86)']}\\Google\\Chrome\\Application\\chrome.exe`,
      `${env.LOCALAPPDATA}\\Google\\Chrome\\Application\\chrome.exe`, `${env.PROGRAMFILES}\\Microsoft\\Edge\\Application\\msedge.exe`,
      `${env['PROGRAMFILES(X86)']}\\Microsoft\\Edge\\Application\\msedge.exe`],
    darwin: ['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge'],
  }[process.platform];
  if (c) return c.find((p) => p && existsSync(p)) ?? null;
  for (const bin of ['google-chrome', 'google-chrome-stable', 'chromium', 'chromium-browser', 'microsoft-edge']) {
    const r = spawnSync('which', [bin], { encoding: 'utf8' }); if (r.status === 0) return r.stdout.trim();
  }
  return null;
}
const browser = findBrowser();
if (!browser) { console.error('No Chrome or Edge found. Pass --browser <path> or set CHROME_PATH.'); process.exit(2); }

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const tmp = mkdtempSync(join(tmpdir(), 'look-for-'));
const profile = profileArg ?? join(tmp, 'profile');
const proc = spawn(browser, [
  `--user-data-dir=${profile}`, '--remote-debugging-port=0', '--no-first-run', '--no-default-browser-check',
  '--lang=es-CL', '--window-size=1366,900', ...(headed ? [] : ['--headless=new']), 'about:blank',
], { stdio: 'ignore' });
const cleanup = () => { try { proc.kill(); } catch {} setTimeout(() => { try { rmSync(tmp, { recursive: true, force: true }); } catch {} }, 500); };

try {
  let port = null;
  for (let i = 0; i < 100 && !port; i++) {
    await sleep(200);
    try { port = readFileSync(join(profile, 'DevToolsActivePort'), 'utf8').split('\n')[0]; } catch {}
  }
  if (!port) throw new Error('Browser did not open its debugging port.');
  const targets = await (await fetch(`http://127.0.0.1:${port}/json`)).json();
  const page = targets.find((t) => t.type === 'page');
  const ws = new WebSocket(page.webSocketDebuggerUrl);
  await new Promise((res, rej) => { ws.onopen = res; ws.onerror = rej; });
  let id = 0; const pending = new Map(); const events = [];
  ws.onmessage = (m) => {
    const d = JSON.parse(m.data);
    if (d.id && pending.has(d.id)) { pending.get(d.id)(d); pending.delete(d.id); } else events.push(d.method);
  };
  const send = (method, params = {}) => new Promise((res) => { const i = ++id; pending.set(i, res); ws.send(JSON.stringify({ id: i, method, params })); });
  const evaluate = async (expression) => (await send('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true })).result?.result?.value;

  await send('Page.enable');
  const ua = (await send('Browser.getVersion')).result.userAgent.replace('HeadlessChrome', 'Chrome');
  await send('Network.setUserAgentOverride', { userAgent: ua, acceptLanguage: 'es-CL,es;q=0.9,en;q=0.8' });
  await send('Page.navigate', { url });
  for (let i = 0; i < 60 && !events.includes('Page.loadEventFired'); i++) await sleep(500);
  await sleep(wait);
  for (let i = 0; i < scrolls; i++) { await evaluate('window.scrollTo(0, document.body.scrollHeight)'); await sleep(1200); }
  if (headed && hold > 0) await sleep(hold * 1000);

  const result = await evaluate(`(() => {
    const clean = (s) => (s || '').replace(/\\s+/g, ' ').trim();
    const seen = new Set(), links = [];
    for (const a of document.querySelectorAll('a[href]')) {
      const href = a.href, text = clean(a.innerText).slice(0, 200);
      if (!/^https?:/.test(href) || seen.has(href)) continue;
      seen.add(href); links.push({ href, text });
    }
    const text = clean(document.body ? document.body.innerText : '');
    const ldjson = [...document.querySelectorAll('script[type="application/ld+json"]')].map((s) => s.textContent.trim().slice(0, 20000));
    const gate = /iniciar sesi[oó]n|inicia sesi[oó]n|log in to|you must log in|captcha|no soy un robot|verify you are human|acceso denegado|access denied/i;
    const loginPrompt = links.some((l) => /\\/login|\\/signin|iniciar-sesion/i.test(l.href)) && /iniciar sesi[oó]n|inicia sesi[oó]n|log in/i.test(text);
    const blocked = /login|checkpoint|captcha|account-verification/i.test(location.href) || (text.length < 1500 && gate.test(text));
    // status: ok | empty (page served nothing, typical of bot filtering) | blocked (wall or captcha) | login-prompt (page loads but listings may sit behind login)
    const status = blocked ? 'blocked' : text.length < 200 ? 'empty' : loginPrompt ? 'login-prompt' : 'ok';
    return { url: location.href, title: document.title, status, blocked: status === 'blocked' || status === 'empty', textLength: text.length, text: text.slice(0, 60000), links: links.slice(0, 400), ldjson };
  })()`);
  ws.close();
  const json = JSON.stringify(result, null, 2);
  if (out) writeFileSync(out, json); else console.log(json);
  if (out) console.error(`${result.status.toUpperCase()} ${result.title} | ${result.textLength} chars, ${result.links.length} links -> ${out}`);
  cleanup();
  process.exit(result.blocked ? 1 : 0);
} catch (e) {
  console.error(String(e?.message ?? e));
  cleanup();
  process.exit(2);
}
