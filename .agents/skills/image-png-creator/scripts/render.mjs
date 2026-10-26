#!/usr/bin/env node
// render.mjs — convierte la fuente HTML de una imagen en PNG con un navegador sin ventana y revisa el resultado.
// Mide la altura real del contenido, detecta texto desbordado, piezas fuera del lienzo e imágenes rotas,
// y lista las líneas con números que quedaron en la imagen para cotejarlas con la ficha.
//
// Uso:  node render.mjs <fuente.html> [--out imagen.png] [--ancho 1000] [--alto px] [--escala 2] [--browser ruta]
//   --ancho   ancho del lienzo en px CSS (el body de la fuente debe medir lo mismo)
//   --alto    alto fijo (post, historia, banner); sin él la imagen toma la altura del contenido
//   --escala  densidad de píxeles: 2 = nítido para imprimir o hacer zoom
// Sin dependencias: Node 18+ y Chrome o Edge instalado. Sale con código 1 si el resultado es ROJO.

import { spawnSync } from 'node:child_process';
import { existsSync, readFileSync, writeFileSync, rmSync, mkdtempSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, resolve, dirname, basename } from 'node:path';
import { pathToFileURL } from 'node:url';

const args = process.argv.slice(2);
const opt = (name, def) => { const i = args.indexOf(name); return i >= 0 ? args.splice(i, 2)[1] : def; };
const outArg = opt('--out', null);
const ancho = Number(opt('--ancho', 1000));
const altoArg = opt('--alto', null);
const alto = altoArg === null ? null : Number(altoArg);
const escala = Number(opt('--escala', 2));
const browserArg = opt('--browser', process.env.CHROME_PATH ?? null);
const file = args[0];
if (!file || !existsSync(file) || ![ancho, escala, alto ?? 1].every((n) => Number.isFinite(n) && n > 0)) {
  console.error('Uso: node render.mjs <fuente.html> [--out imagen.png] [--ancho 1000] [--alto px] [--escala 2]');
  process.exit(2);
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
const browser = findBrowser();
if (!browser) { console.error('No encontré Chrome ni Edge. Pasa la ruta con --browser o CHROME_PATH.'); process.exit(2); }

// Script de medición: corre dentro de una copia temporal de la fuente, nunca en la imagen final.
// La barra de scroll se oculta para que el lienzo medido mida lo mismo que la captura.
const MEDIR = `<style>html{scrollbar-width:none}::-webkit-scrollbar{display:none}</style>
<script>addEventListener('load', () => (document.fonts ? document.fonts.ready : Promise.resolve()).then(() => {
  const W = window.innerWidth, txt = (el) => (el.innerText || el.textContent || '').trim().replace(/\\s+/g, ' ').slice(0, 70);
  const desbordes = new Set(), fuera = new Set(), rotas = [];
  for (const el of document.body.querySelectorAll('*')) {
    if (el.closest('svg') || ['SCRIPT', 'STYLE'].includes(el.tagName)) continue;
    const cs = getComputedStyle(el); if (cs.display === 'none' || cs.display === 'inline') continue;
    if (el.clientWidth > 0 && el.scrollWidth > el.clientWidth + 1) desbordes.add(txt(el));
    if (cs.overflow !== 'visible' && el.clientHeight > 0 && el.scrollHeight > el.clientHeight + 1) desbordes.add(txt(el));
    const b = el.getBoundingClientRect(); if (b.width && (b.right > W + 1 || b.left < -1)) fuera.add(txt(el) || el.tagName);
  }
  for (const img of document.images) if (!img.naturalWidth) rotas.push(img.getAttribute('src'));
  const r = { vw: innerWidth, vh: innerHeight, alto: Math.ceil(document.documentElement.scrollHeight), desbordes: [...desbordes], fuera: [...fuera], rotas, texto: document.body.innerText };
  const pre = document.createElement('pre'); pre.id = '__medida'; pre.hidden = true;
  pre.textContent = btoa(unescape(encodeURIComponent(JSON.stringify(r)))); document.body.appendChild(pre);
}));</script>`;

const src = resolve(file);
const out = resolve(outArg ?? src.replace(/\.html?$/i, '') + '.png');
const html = readFileSync(src, 'utf8');
const cierre = html.toLowerCase().lastIndexOf('</body>');
// La copia va junto a la fuente para que sus rutas relativas (imágenes, fuentes) sigan resolviendo.
const sonda = join(dirname(src), `.${basename(src)}.medir.html`);
writeFileSync(sonda, cierre >= 0 ? html.slice(0, cierre) + MEDIR + html.slice(cierre) : html + MEDIR);
const tmp = mkdtempSync(join(tmpdir(), 'png-'));
const base = ['--headless=new', '--disable-gpu', '--hide-scrollbars', '--virtual-time-budget=5000', `--user-data-dir=${join(tmp, 'perfil')}`];

// Con alto libre se mide en una ventana baja: scrollHeight nunca es menor que la ventana.
const objetivo = [ancho, alto ?? 100];
let medida, marco = [0, 0];
try {
  // En --dump-dom el navegador descuenta su marco de la ventana (unos 24 × 92 px): se calibra hasta que el lienzo calce.
  for (let intento = 0; intento < 3; intento++) {
    const r = spawnSync(browser, [...base, `--window-size=${objetivo[0] + marco[0]},${objetivo[1] + marco[1]}`, '--dump-dom',
      pathToFileURL(sonda).href], { encoding: 'utf8', timeout: 60000, maxBuffer: 64 * 1024 * 1024 });
    const m = /id="__medida"[^>]*>([A-Za-z0-9+/=]+)</.exec(r.stdout ?? '');
    if (!m) { console.error(`No pude medir la fuente.\n${r.stderr ?? ''}`); process.exit(1); }
    medida = JSON.parse(Buffer.from(m[1], 'base64').toString('utf8'));
    const calza = medida.vw === ancho && (alto === null || medida.vh === alto);
    if (calza) break;
    marco = [marco[0] + ancho - medida.vw, marco[1] + objetivo[1] - medida.vh];
  }
} finally {
  rmSync(sonda, { force: true });
}
if (medida.vw !== ancho) { console.error(`No pude calibrar el lienzo: mide ${medida.vw} px y debía medir ${ancho}.`); process.exit(1); }

const altoFinal = alto ?? medida.alto;
const s = spawnSync(browser, [...base, `--force-device-scale-factor=${escala}`, `--window-size=${ancho},${altoFinal}`,
  `--screenshot=${out}`, pathToFileURL(src).href], { encoding: 'utf8', timeout: 60000 });
try { rmSync(tmp, { recursive: true, force: true, maxRetries: 5, retryDelay: 200 }); } catch {}
if (!existsSync(out)) { console.error(`No se generó el PNG.\n${s.stderr ?? ''}`); process.exit(1); }

const png = readFileSync(out);
const [pw, ph] = [png.readUInt32BE(16), png.readUInt32BE(20)];
const avisos = [];
for (const t of medida.desbordes) avisos.push(`texto desbordado: "${t}"`);
for (const t of medida.fuera) avisos.push(`fuera del lienzo de ${ancho} px: "${t}"`);
for (const t of medida.rotas) avisos.push(`imagen rota: ${t}`);
if (alto !== null && medida.alto > alto) avisos.push(`el contenido mide ${medida.alto} px y el alto fijo es ${alto} px: se corta`);

console.log(`fuente  ${src}`);
console.log(`imagen  ${out} · ${pw} × ${ph} px (${ancho} × ${altoFinal} css × ${escala})`);
console.log(avisos.length ? avisos.map((a) => `⚠ ${a}`).join('\n') : '✓ sin desbordes, piezas fuera del lienzo ni imágenes rotas');
const conNumeros = [...new Set(medida.texto.split('\n').map((l) => l.trim()).filter((l) => /\d/.test(l) && !/^\d{1,2}$/.test(l)))]; // sin los números sueltos de los pasos
console.log(`líneas con números (${conNumeros.length}), cotéjalas con la ficha:`);
for (const l of conNumeros) console.log(`  · ${l}`);
console.log(avisos.length ? 'ROJO' : 'VERDE');
process.exit(avisos.length ? 1 : 0);
