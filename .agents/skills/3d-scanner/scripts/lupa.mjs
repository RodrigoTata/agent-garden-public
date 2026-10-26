#!/usr/bin/env node
// lupa.mjs — recorta y amplía una zona de una foto con una grilla rotulada en píxeles de la foto original.
// Las coordenadas que leas en la grilla son las que van a rectificar.mjs.
//
// Uso:  node lupa.mjs <foto.jpg|png|webp> [--zona x,y,ancho,alto] [--escala n] [--grilla px] [--out salida.png] [--browser ruta]
// Sin --zona muestra la foto completa reducida (sirve para ubicar zonas). Píxeles tal como está guardada la foto (sin rotación EXIF).
// Sin dependencias: Node 18+ y Chrome o Edge instalado.

import { spawnSync } from 'node:child_process';
import { existsSync, readFileSync, writeFileSync, mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, resolve, basename, extname } from 'node:path';
import { pathToFileURL } from 'node:url';

const args = process.argv.slice(2);
const opt = (name, def) => { const i = args.indexOf(name); return i >= 0 ? args.splice(i, 2)[1] : def; };
const zonaArg = opt('--zona', null);
const escalaArg = opt('--escala', null);
const grillaArg = opt('--grilla', null);
const outArg = opt('--out', null);
const browserArg = opt('--browser', process.env.CHROME_PATH ?? null);
const file = args[0];
if (!file || !existsSync(file)) { console.error('Uso: node lupa.mjs <foto> [--zona x,y,ancho,alto] [--escala n] [--grilla px] [--out salida.png]'); process.exit(2); }

function imageSize(buf) {
  if (buf.readUInt32BE(0) === 0x89504e47) return [buf.readUInt32BE(16), buf.readUInt32BE(20)];
  if (buf[0] === 0xff && buf[1] === 0xd8) {
    let i = 2;
    while (i + 9 < buf.length) {
      if (buf[i] !== 0xff) { i++; continue; }
      const m = buf[i + 1];
      if (m >= 0xc0 && m <= 0xcf && m !== 0xc4 && m !== 0xc8 && m !== 0xcc) return [buf.readUInt16BE(i + 7), buf.readUInt16BE(i + 5)];
      i += 2 + buf.readUInt16BE(i + 2);
    }
  }
  if (buf.toString('ascii', 0, 4) === 'RIFF' && buf.toString('ascii', 8, 12) === 'WEBP') {
    const t = buf.toString('ascii', 12, 16);
    if (t === 'VP8X') return [1 + buf.readUIntLE(24, 3), 1 + buf.readUIntLE(27, 3)];
    if (t === 'VP8 ') return [buf.readUInt16LE(26) & 0x3fff, buf.readUInt16LE(28) & 0x3fff];
    if (t === 'VP8L') { const b = buf.readUInt32LE(21); return [1 + (b & 0x3fff), 1 + ((b >>> 14) & 0x3fff)]; }
  }
  return null;
}

function findBrowser() {
  if (browserArg) return browserArg;
  const env = process.env;
  const c = {
    win32: [`${env.PROGRAMFILES}\\Google\\Chrome\\Application\\chrome.exe`, `${env['PROGRAMFILES(X86)']}\\Google\\Chrome\\Application\\chrome.exe`,
      `${env.LOCALAPPDATA}\\Google\\Chrome\\Application\\chrome.exe`, `${env['PROGRAMFILES(X86)']}\\Microsoft\\Edge\\Application\\msedge.exe`,
      `${env.PROGRAMFILES}\\Microsoft\\Edge\\Application\\msedge.exe`],
    darwin: ['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge'],
  }[process.platform];
  if (c) return c.find((p) => p && existsSync(p)) ?? null;
  for (const bin of ['google-chrome', 'google-chrome-stable', 'chromium', 'chromium-browser', 'microsoft-edge']) {
    const r = spawnSync('which', [bin], { encoding: 'utf8' }); if (r.status === 0) return r.stdout.trim();
  }
  return null;
}

const buf = readFileSync(file);
const size = imageSize(buf);
if (!size) { console.error('Formato no soportado: usa JPG, PNG o WebP.'); process.exit(2); }
const [iw, ih] = size;
let [x, y, w, h] = zonaArg ? zonaArg.split(',').map(Number) : [0, 0, iw, ih];
x = Math.max(0, x); y = Math.max(0, y); w = Math.min(w, iw - x); h = Math.min(h, ih - y);
if (![x, y, w, h].every(Number.isFinite) || w <= 0 || h <= 0) { console.error(`Zona fuera de la foto (${iw} × ${ih} px).`); process.exit(2); }
const escala = Number(escalaArg ?? Math.min(4, 1400 / Math.max(w, h)));
const grilla = Number(grillaArg ?? [10, 20, 40, 80, 160].find((g) => (Math.max(w, h) / g) <= 30) ?? 200);
const W = Math.round(w * escala), H = Math.round(h * escala);

const mime = buf.readUInt32BE(0) === 0x89504e47 ? 'image/png' : buf.toString('ascii', 8, 12) === 'WEBP' ? 'image/webp' : 'image/jpeg';
const html = `<!doctype html><meta charset="utf-8"><style>html,body{margin:0;background:#000;overflow:hidden}img{image-orientation:none}</style>
<canvas id="c" width="${W}" height="${H}"></canvas>
<script>
const img = new Image();
img.style.imageOrientation = 'none';
img.onload = () => {
  const g = document.getElementById('c').getContext('2d');
  g.imageSmoothingQuality = 'high';
  g.drawImage(img, ${x}, ${y}, ${w}, ${h}, 0, 0, ${W}, ${H});
  g.font = '12px Consolas, monospace'; g.lineWidth = 1;
  for (let v = Math.ceil(${x} / ${grilla}) * ${grilla}; v < ${x + w}; v += ${grilla}) {
    const p = Math.round((v - ${x}) * ${escala}) + 0.5;
    g.strokeStyle = 'rgba(0,255,255,.6)'; g.beginPath(); g.moveTo(p, 0); g.lineTo(p, ${H}); g.stroke();
    g.fillStyle = '#000'; g.fillRect(p + 1, 0, 34, 14); g.fillStyle = '#ff0'; g.fillText(v, p + 2, 11);
  }
  for (let v = Math.ceil(${y} / ${grilla}) * ${grilla}; v < ${y + h}; v += ${grilla}) {
    const p = Math.round((v - ${y}) * ${escala}) + 0.5;
    g.strokeStyle = 'rgba(0,255,255,.6)'; g.beginPath(); g.moveTo(0, p); g.lineTo(${W}, p); g.stroke();
    g.fillStyle = '#000'; g.fillRect(0, p + 1, 34, 14); g.fillStyle = '#ff0'; g.fillText(v, 2, p + 12);
  }
};
img.src = 'data:${mime};base64,${buf.toString('base64')}';
</script>`;

const browser = findBrowser();
if (!browser) { console.error('No encontré Chrome ni Edge. Indica la ruta con --browser o CHROME_PATH.'); process.exit(2); }
const tmp = mkdtempSync(join(tmpdir(), 'lupa-'));
const page = join(tmp, 'lupa.html'); writeFileSync(page, html);
const out = resolve(outArg ?? join(tmpdir(), `${basename(file, extname(file))}.lupa-${x}-${y}-${w}x${h}.png`));
const r = spawnSync(browser, ['--headless=new', '--disable-gpu', '--hide-scrollbars', '--force-device-scale-factor=1',
  `--window-size=${W},${H}`, '--virtual-time-budget=5000', `--user-data-dir=${join(tmp, 'perfil')}`,
  `--screenshot=${out}`, pathToFileURL(page).href], { encoding: 'utf8', timeout: 60000 });
try { rmSync(tmp, { recursive: true, force: true, maxRetries: 5, retryDelay: 200 }); } catch {}
if (!existsSync(out)) { console.error(`No se generó la captura.\n${r.stderr ?? ''}`); process.exit(1); }
console.log(`foto ${iw} × ${ih} px · zona ${x},${y},${w},${h} · escala ×${+escala.toFixed(2)} · grilla ${grilla} px`);
console.log(out);
