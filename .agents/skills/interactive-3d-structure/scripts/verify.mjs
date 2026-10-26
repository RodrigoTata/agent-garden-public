#!/usr/bin/env node
// verify.mjs — abre un gemelo digital 3D en Chrome/Edge headless (escritorio y móvil)
// y dice VERDE o ROJO. Sin dependencias: Node 22+ (WebSocket nativo) y un Chrome o Edge instalado.
//
// Uso:  node verify.mjs <visor.html> [--out <carpeta>] [--timeout <ms>] [--browser <ruta>]
// Las capturas van a <temp del sistema>/gemelo3d-verify salvo que se indique --out.
// Sale con código 0 si queda VERDE, 1 si queda ROJO, 2 si no se pudo ejecutar.

import { spawn, spawnSync } from 'node:child_process';
import { existsSync, mkdtempSync, rmSync, writeFileSync, mkdirSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, resolve, basename, extname } from 'node:path';
import { pathToFileURL } from 'node:url';

const args = process.argv.slice(2);
const opt = (name, def) => { const i = args.indexOf(name); return i >= 0 ? args.splice(i, 2)[1] : def; };
const outDir = opt('--out', join(tmpdir(), 'gemelo3d-verify'));
const timeout = Number(opt('--timeout', 30000));
const browserArg = opt('--browser', process.env.CHROME_PATH ?? null);
const file = args[0];

if (!file || !existsSync(file)) { console.error('Uso: node verify.mjs <visor.html> [--out dir] [--timeout ms] [--browser ruta]'); process.exit(2); }
if (typeof WebSocket === 'undefined') { console.error('Se necesita Node 22 o superior (WebSocket nativo).'); process.exit(2); }

function findBrowser() {
  if (browserArg) return browserArg;
  const env = process.env;
  const candidates = {
    win32: [
      `${env['PROGRAMFILES']}\\Google\\Chrome\\Application\\chrome.exe`,
      `${env['PROGRAMFILES(X86)']}\\Google\\Chrome\\Application\\chrome.exe`,
      `${env['LOCALAPPDATA']}\\Google\\Chrome\\Application\\chrome.exe`,
      `${env['PROGRAMFILES(X86)']}\\Microsoft\\Edge\\Application\\msedge.exe`,
      `${env['PROGRAMFILES']}\\Microsoft\\Edge\\Application\\msedge.exe`,
    ],
    darwin: [
      '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
      '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge',
      '/Applications/Chromium.app/Contents/MacOS/Chromium',
    ],
  }[process.platform];
  if (candidates) return candidates.find((p) => p && existsSync(p)) ?? null;
  for (const bin of ['google-chrome', 'google-chrome-stable', 'chromium', 'chromium-browser', 'microsoft-edge']) {
    const r = spawnSync('which', [bin], { encoding: 'utf8' });
    if (r.status === 0) return r.stdout.trim();
  }
  return null;
}

const browser = findBrowser();
if (!browser) { console.error('No encontré Chrome ni Edge. Indica la ruta con --browser o CHROME_PATH.'); process.exit(2); }

const profile = mkdtempSync(join(tmpdir(), 'verify3d-'));
const proc = spawn(browser, [
  '--headless=new', '--remote-debugging-port=0', `--user-data-dir=${profile}`,
  '--no-first-run', '--no-default-browser-check', '--disable-extensions',
  '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist',
  '--window-size=1280,800', 'about:blank',
], { stdio: ['ignore', 'ignore', 'pipe'] });

function cleanup() {
  try { proc.kill(); } catch {}
  try { rmSync(profile, { recursive: true, force: true, maxRetries: 10, retryDelay: 200 }); } catch {}
}

const wsUrl = await new Promise((ok, ko) => {
  let buf = '';
  const t = setTimeout(() => ko(new Error('El navegador no abrió el puerto de depuración a tiempo.')), 15000);
  proc.stderr.on('data', (d) => {
    buf += d; const m = buf.match(/DevTools listening on (ws:\/\/\S+)/);
    if (m) { clearTimeout(t); ok(m[1]); }
  });
  proc.on('exit', (c) => ko(new Error(`El navegador terminó (código ${c}).`)));
}).catch((e) => { console.error(e.message); cleanup(); process.exit(2); });

// --- Cliente CDP mínimo ---
const ws = new WebSocket(wsUrl);
await new Promise((ok, ko) => { ws.onopen = ok; ws.onerror = () => ko(new Error('No pude conectar con el navegador.')); });
let nextId = 0; const pending = new Map(); const listeners = [];
ws.onmessage = (ev) => {
  const msg = JSON.parse(ev.data);
  if (msg.id !== undefined && pending.has(msg.id)) {
    const { ok, ko } = pending.get(msg.id); pending.delete(msg.id);
    msg.error ? ko(new Error(`${msg.error.message}`)) : ok(msg.result);
  } else if (msg.method) listeners.forEach((fn) => fn(msg));
};
const send = (method, params = {}, sessionId) => new Promise((ok, ko) => {
  const id = ++nextId; pending.set(id, { ok, ko });
  ws.send(JSON.stringify({ id, method, params, ...(sessionId ? { sessionId } : {}) }));
});

const { targetId } = await send('Target.createTarget', { url: 'about:blank' });
const { sessionId } = await send('Target.attachToTarget', { targetId, flatten: true });
const S = (m, p) => send(m, p, sessionId);

let errors = [], warnings = [];
listeners.push((m) => {
  if (m.sessionId !== sessionId) return;
  if (m.method === 'Runtime.exceptionThrown') {
    const d = m.params.exceptionDetails; errors.push(`excepción: ${d.exception?.description ?? d.text}`);
  } else if (m.method === 'Runtime.consoleAPICalled') {
    const text = m.params.args.map((a) => a.value ?? a.description ?? '').join(' ');
    if (m.params.type === 'error') errors.push(`console.error: ${text}`);
    else if (m.params.type === 'warning' || m.params.type === 'warn') warnings.push(text);
  } else if (m.method === 'Log.entryAdded') {
    const e = m.params.entry;
    if (e.level === 'error') errors.push(`${e.source}: ${e.text}${e.url ? ` (${e.url})` : ''}`);
  }
});
await S('Runtime.enable'); await S('Log.enable'); await S('Page.enable');

const url = pathToFileURL(resolve(file)).href;
const eval_ = async (expr) => (await S('Runtime.evaluate', { expression: expr, returnByValue: true, awaitPromise: true })).result?.value;
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function capture(nombre) {
  const shot = await S('Page.captureScreenshot', { format: 'png' });
  mkdirSync(outDir, { recursive: true });
  const path = join(outDir, `${basename(file, extname(file))}.verify-${nombre}.png`);
  writeFileSync(path, Buffer.from(shot.data, 'base64'));
  return path;
}

async function pass(nombre, metrics, interactuar = false) {
  errors = []; warnings = [];
  await S('Emulation.setDeviceMetricsOverride', metrics);
  await S('Emulation.setTouchEmulationEnabled', metrics.mobile ? { enabled: true, maxTouchPoints: 5 } : { enabled: false });
  await S('Page.navigate', { url });
  const t0 = Date.now(); let st = null;
  while (Date.now() - t0 < timeout) {
    await sleep(250);
    st = await eval_(`window.__viewer ? { ready: !!window.__viewer.ready, fallo: window.__viewer.fallo } : null`).catch(() => null);
    if (st?.ready || st?.fallo) break;
  }
  const r = { nombre, errores: [], avisos: [], test: null, captura: null, capturaInteraccion: null };
  if (!st) r.errores.push('el motor nunca arrancó (¿no cargó Three.js desde el CDN?)');
  else if (st.fallo) r.errores.push(`el visor mostró su pantalla de fallo: ${st.fallo}`);
  else if (!st.ready) r.errores.push(`el visor no quedó listo en ${timeout} ms`);
  if (st?.ready) {
    await sleep(700); // deja terminar la animación de cámara
    r.test = await eval_('window.__viewer.selfTest()').catch((e) => ({ ok: false, errores: [`selfTest falló: ${e.message}`] }));
    if (!r.test?.ok) {
      if (r.test?.errores?.length) r.errores.push(...r.test.errores.map((e) => `SPEC: ${e}`));
      if (r.test && r.test.piezas !== r.test.esperadas) r.errores.push(`piezas construidas ${r.test.piezas} de ${r.test.esperadas}`);
      if (r.test && r.test.cobertura < 0.02) r.errores.push(`el modelo casi no se ve en el encuadre (cobertura ${r.test.cobertura})`);
    }
    const overflow = await eval_('document.documentElement.scrollWidth - innerWidth');
    if (overflow > 1) r.errores.push(`hay scroll horizontal de ${overflow}px`);
    r.captura = await capture(nombre);
    if (interactuar) {
      // Recorre la interfaz completa: si algo lanza un error, aparece en la lista de errores.
      const out = await eval_(`(async () => {
        const wait = (ms) => new Promise((r) => setTimeout(r, ms));
        const click = (sel) => { const el = document.querySelector(sel); if (!el) throw new Error('falta ' + sel); el.click(); };
        click('[data-modo="rayos"]'); await wait(150);
        const ex = document.querySelector('#explota');
        if (ex && !document.querySelector('#explota-box').hidden) { ex.value = 100; ex.dispatchEvent(new Event('input')); }
        click('#b-tema'); await wait(150);
        const pieza = document.querySelector('#piezas button'); if (pieza) pieza.click();
        document.querySelector('#vistas .btn:nth-child(6)')?.click(); await wait(700);
        const png = window.__viewer.snapshot();
        window.dispatchEvent(new Event('beforeprint'));
        const hoja = !!document.querySelector('#print-sheet img');
        window.dispatchEvent(new Event('afterprint'));
        return { png: png.length, hoja, ficha: !document.querySelector('#ficha').hidden };
      })()`).catch((e) => ({ error: e.message }));
      if (out?.error) r.errores.push(`interacción: ${out.error}`);
      else {
        if (!(out?.png > 5000)) r.errores.push('la exportación PNG salió vacía');
        if (!out?.hoja) r.errores.push('la hoja de impresión no se generó');
        if (!out?.ficha) r.errores.push('la ficha de pieza no se abrió');
      }
      r.capturaInteraccion = await capture('interaccion');
      await eval_(`document.querySelector('#b-tema').click()`); // deja el tema como estaba
    }
  }
  r.errores.push(...errors.filter((e) => !e.startsWith('console.error: [SPEC]'))); // los [SPEC] ya vienen en selfTest
  r.avisos = [...new Set(warnings)];
  return r;
}

let results;
try {
  results = [
    await pass('escritorio', { width: 1280, height: 800, deviceScaleFactor: 1, mobile: false }, true),
    await pass('movil', { width: 390, height: 844, deviceScaleFactor: 2, mobile: true }),
  ];
} catch (e) {
  console.error(`No se pudo completar la verificación: ${e.message}`);
  await send('Browser.close').catch(() => {}); ws.close(); cleanup(); process.exit(2);
}
const version = (await send('Browser.getVersion').catch(() => null))?.product ?? basename(browser);
await send('Browser.close').catch(() => {});
ws.close(); cleanup();

console.log(`Archivo:   ${resolve(file)}`);
console.log(`Navegador: ${version} (headless, WebGL por SwiftShader)`);
for (const r of results) {
  const t = r.test;
  console.log(`\n[${r.nombre}] ${r.errores.length ? 'ROJO' : 'VERDE'}`);
  if (t) console.log(`  three r${t.three} · WebGL2 ${t.webgl2 ? 'sí' : 'no'} · piezas ${t.piezas}/${t.esperadas} · cobertura ${t.cobertura} · triángulos ${t.triangulos} · modelo ${t.medidas}`);
  for (const e of r.errores) console.log(`  ✗ ${e}`);
  for (const w of r.avisos) console.log(`  · aviso: ${w}`);
  if (r.captura) console.log(`  captura: ${r.captura}`);
  if (r.capturaInteraccion) console.log(`  captura tras interacción (rayos X, explosión, tema claro, planta, ficha): ${r.capturaInteraccion}`);
}
const green = results.every((r) => r.errores.length === 0);
console.log(`\n${green ? 'VERDE' : 'ROJO'}`);
process.exit(green ? 0 : 1);
